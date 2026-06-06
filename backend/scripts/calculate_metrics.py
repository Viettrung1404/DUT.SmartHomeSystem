import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from pathlib import Path
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.apis.suggestions.service import SuggestionService

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:123456@localhost:5432/smarthome")

def main():
    engine = create_engine(DB_URL)
    with Session(engine) as session:
        # Lấy metrics cho 30 ngày qua
        metrics = SuggestionService.get_suggestion_dashboard_metrics(session, days=30)
        
        print("\n" + "="*60)
        print("  SMART HOME SUGGESTION ANALYTICS REPORT (LAST 30 DAYS)")
        print("="*60)
        
        print("\n[A] SUGGESTION METRICS")
        print(f"  Total Sent:             {metrics['sent_count']}")
        print(f"  Feedback Received:      {metrics['feedback']['total_feedback']}")
        print(f"    - Accepted:           {metrics['feedback']['accepted']}")
        print(f"    - Rejected:           {metrics['feedback']['rejected']}")
        print(f"    - Ignored:            {metrics['feedback']['ignored']}")
        
        print("\n[B] QUALITY METRICS")
        print(f"  Effective Accept Rate:  {metrics['effective_accept_rate']}% (accepted / feedback)")
        print(f"  Rejection Rate:         {metrics['rejection_rate']}%")
        print(f"  False Alert Rate:       {metrics['false_alert_rate']}% (rejected / sent)")
        
        print("\n[C] GUARDRAIL METRICS (SYSTEM PERFORMANCE)")
        print(f"  Cooldown Suppressions:  {metrics['cooldown_suppressions']} alerts saved")
        print(f"  Avg Suggestions/Day:    {metrics['avg_suggestions_per_day']}")
        
        print("\n[D] PATTERN EFFECTIVENESS (TOP ACCEPTED)")
        print(f"  {'Pattern Type':<18} | {'Sent':<5} | {'Acc':<5} | {'Rate':<6}")
        print(f"  {'-'*18}-+-{'-'*5}-+-{'-'*5}-+-{'-'*6}")
        for p in metrics['top_accepted_patterns']:
            print(f"  {p['pattern_type']:<18} | {p['sent']:>5} | {p['accepted']:>5} | {p['accept_rate']:>5.1f}%")

        if metrics['top_rejection_reasons']:
            print("\n[E] TOP REJECTION REASONS")
            for r in metrics['top_rejection_reasons']:
                print(f"  - {r['count']:>2}x: {r['reason']}")

        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
