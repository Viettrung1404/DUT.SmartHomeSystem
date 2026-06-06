import os
import sys
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.apis.suggestions.service import SuggestionService
from src.entities.models import Home, User, UserPattern, SuggestionLog, SuggestionFeedbackLog, ActionType

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/smarthome")

def setup_mock_data(session: Session):
    # 1. Create a mock home and user if not exists
    home_id = uuid.uuid4()
    user_id = uuid.uuid4()
    
    # Using existing data or creating new
    # For testing, we'll just use random UUIDs and hope constraints pass or we mock them
    # Actually, it's better to use existing IDs from the DB to avoid FK errors
    
    home = session.query(Home).first()
    if not home:
        print("No home found in DB. Please run seed data first.")
        return None, None
    
    user = session.query(User).first()
    if not user:
        print("No user found in DB. Please run seed data first.")
        return None, None

    pattern = session.query(UserPattern).filter_by(home_id=home.id, user_id=user.id).first()
    if not pattern:
        print("No pattern found for user. Creating a mock one.")
        pattern = UserPattern(
            user_id=user.id,
            home_id=home.id,
            pattern_type="TIME_HABIT",
            pattern_data={"hour": 22, "days_of_week": [1,2,3]},
            confidence=0.9
        )
        session.add(pattern)
        session.commit()

    return home, user, pattern

def test_metrics_logic():
    engine = create_engine(DB_URL)
    with Session(engine) as session:
        home, user, pattern = setup_mock_data(session)
        if not home: return

        print(f"Testing with Home: {home.id}, User: {user.id}")

        # Test Case 1: Log a blocked decision (Cooldown)
        print("Test 1: Logging a blocked decision (Cooldown)...")
        SuggestionService.log_decision(
            session=session,
            pattern_id=pattern.id,
            home_id=str(home.id),
            user_id=str(user.id),
            decision_score=0.8,
            should_suggest=False,
            blocked_by="COOLDOWN",
            cooldown_signature="TIME_HABIT:light:unusual_hour",
            metadata_json={"reason": "Already suggested 10m ago"}
        )

        # Test Case 2: Log a suggested decision
        print("Test 2: Logging a successful decision...")
        SuggestionService.log_decision(
            session=session,
            pattern_id=pattern.id,
            home_id=str(home.id),
            user_id=str(user.id),
            decision_score=0.95,
            should_suggest=True,
            metadata_json={"priority_reason": ["hard_override_anomaly_high_energy_repeated"]}
        )

        # Test Case 3: Create a suggestion and feedback
        print("Test 3: Creating a suggestion and accepting it...")
        suggestion = SuggestionLog(
            user_id=user.id,
            pattern_id=pattern.id,
            action_type=ActionType.SCHEDULE,
            suggestion_text="Test Suggestion",
            suggestion_json={"explanation": {"cooldown_pass": True}},
            was_accepted=True
        )
        session.add(suggestion)
        session.commit()
        
        # Record feedback
        SuggestionService.record_suggestion_feedback(
            session=session,
            suggestion_id=suggestion.id,
            user_id=str(user.id),
            feedback_type="ACCEPT"
        )

        # Test Case 4: Verify Metrics
        print("Test 4: Verifying Dashboard Metrics...")
        metrics = SuggestionService.get_suggestion_dashboard_metrics(session, home_id=str(home.id), days=1)
        
        print("\n--- Metrics Results ---")
        print(f"Sent Count: {metrics['sent_count']}")
        print(f"Accepted: {metrics['feedback']['accepted']}")
        print(f"Cooldown Suppressions: {metrics['cooldown_suppressions']}")
        print(f"Effective Accept Rate: {metrics['effective_accept_rate']}%")
        
        assert metrics['sent_count'] >= 1
        assert metrics['feedback']['accepted'] >= 1
        assert metrics['cooldown_suppressions'] >= 1
        print("\n[SUCCESS] Metrics logic test PASSED!")

if __name__ == "__main__":
    try:
        test_metrics_logic()
    except Exception as e:
        print(f"[FAILED] Test failed: {e}")
        import traceback
        traceback.print_exc()
