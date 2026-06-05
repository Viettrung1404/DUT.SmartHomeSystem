"""
Unit tests for Scene Activation Intent Classification.

Tests the classification of scene activation intents (sleep, wake_up, movie, away, home)
using both rule-based and ML-based classifiers.

**Validates: Requirements 6.1-6.7**
"""

import pytest
from src.classifiers.rule_based import RuleBasedClassifier
from src.entities.entity_extractor import EntityExtractor


class TestSceneActivationRuleBased:
    """Unit tests for scene activation using rule-based classifier."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.classifier = RuleBasedClassifier()
        self.entity_extractor = EntityExtractor()
    
    # ========================================================================
    # SLEEP SCENE TESTS
    # ========================================================================
    
    def test_sleep_scene_basic(self):
        """Test basic sleep scene activation."""
        result = self.classifier.classify("đi ngủ")
        
        assert result is not None
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "sleep"
        assert result.confidence == 1.0
        assert result.classifier_type == "rule"
    
    def test_sleep_scene_with_goodnight(self):
        """Test sleep scene with 'chúc ngủ ngon'."""
        result = self.classifier.classify("chúc ngủ ngon")
        
        assert result is not None
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "sleep"
        assert result.confidence == 1.0
    
    def test_sleep_scene_with_preparation(self):
        """Test sleep scene with 'chuẩn bị ngủ'."""
        result = self.classifier.classify("chuẩn bị ngủ")
        
        assert result is not None
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "sleep"
        assert result.confidence == 1.0
    
    def test_sleep_scene_with_prefix(self):
        """Test sleep scene with prefix 'tôi muốn'."""
        result = self.classifier.classify("tôi muốn đi ngủ")
        
        assert result is not None
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "sleep"
        assert result.confidence == 1.0
    
    def test_sleep_scene_with_suffix(self):
        """Test sleep scene with suffix 'đi'."""
        result = self.classifier.classify("đi ngủ đi")
        
        assert result is not None
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "sleep"
        assert result.confidence == 1.0
    
    # ========================================================================
    # WAKE UP SCENE TESTS
    # ========================================================================
    
    def test_wake_up_scene_basic(self):
        """Test basic wake up scene activation."""
        result = self.classifier.classify("thức dậy")
        
        assert result is not None
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "wake_up"
        assert result.confidence == 1.0
        assert result.classifier_type == "rule"
    
    def test_wake_up_scene_morning(self):
        """Test wake up scene with 'buổi sáng'."""
        result = self.classifier.classify("buổi sáng")
        
        assert result is not None
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "wake_up"
        assert result.confidence == 1.0
    
    def test_wake_up_scene_good_morning(self):
        """Test wake up scene with 'chào buổi sáng'."""
        result = self.classifier.classify("chào buổi sáng")
        
        assert result is not None
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "wake_up"
        assert result.confidence == 1.0
    
    def test_wake_up_scene_with_prefix(self):
        """Test wake up scene with prefix 'tôi'."""
        result = self.classifier.classify("tôi thức dậy rồi")
        
        assert result is not None
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "wake_up"
        assert result.confidence == 1.0
    
    def test_wake_up_scene_with_suffix(self):
        """Test wake up scene with suffix 'nào'."""
        result = self.classifier.classify("chào buổi sáng nào")
        
        assert result is not None
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "wake_up"
        assert result.confidence == 1.0
    
    # ========================================================================
    # MOVIE SCENE TESTS
    # ========================================================================
    
    def test_movie_scene_basic(self):
        """Test basic movie scene activation."""
        result = self.classifier.classify("xem phim")
        
        assert result is not None
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "movie"
        assert result.confidence == 1.0
        assert result.classifier_type == "rule"
    
    def test_movie_scene_watch_tv(self):
        """Test movie scene with 'xem tv'."""
        result = self.classifier.classify("xem tv")
        
        assert result is not None
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "movie"
        assert result.confidence == 1.0
    
    def test_movie_scene_cinema(self):
        """Test movie scene with 'rạp chiếu phim'."""
        result = self.classifier.classify("rạp chiếu phim")
        
        assert result is not None
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "movie"
        assert result.confidence == 1.0
    
    def test_movie_scene_with_prefix(self):
        """Test movie scene with prefix 'tôi muốn'."""
        result = self.classifier.classify("tôi muốn xem phim")
        
        assert result is not None
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "movie"
        assert result.confidence == 1.0
    
    def test_movie_scene_with_suffix(self):
        """Test movie scene with suffix 'đi'."""
        result = self.classifier.classify("xem phim đi")
        
        assert result is not None
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "movie"
        assert result.confidence == 1.0
    
    def test_movie_scene_with_preparation(self):
        """Test movie scene with 'chuẩn bị'."""
        result = self.classifier.classify("chuẩn bị xem phim")
        
        assert result is not None
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "movie"
        assert result.confidence == 1.0
    
    # ========================================================================
    # AWAY SCENE TESTS
    # ========================================================================
    
    def test_away_scene_basic(self):
        """Test basic away scene activation."""
        result = self.classifier.classify("đi vắng")
        
        assert result is not None
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "away"
        assert result.confidence == 1.0
        assert result.classifier_type == "rule"
    
    def test_away_scene_go_out(self):
        """Test away scene with 'đi ra ngoài'."""
        result = self.classifier.classify("đi ra ngoài")
        
        assert result is not None
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "away"
        assert result.confidence == 1.0
    
    def test_away_scene_leave_home(self):
        """Test away scene with 'rời nhà'."""
        result = self.classifier.classify("rời nhà")
        
        assert result is not None
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "away"
        assert result.confidence == 1.0
    
    def test_away_scene_with_prefix(self):
        """Test away scene with prefix 'tôi'."""
        result = self.classifier.classify("tôi đi ra ngoài")
        
        assert result is not None
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "away"
        assert result.confidence == 1.0
    
    def test_away_scene_with_suffix(self):
        """Test away scene with suffix 'đi'."""
        result = self.classifier.classify("rời nhà đi")
        
        assert result is not None
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "away"
        assert result.confidence == 1.0
    
    # ========================================================================
    # HOME SCENE TESTS
    # ========================================================================
    
    def test_home_scene_basic(self):
        """Test basic home scene activation."""
        result = self.classifier.classify("về nhà")
        
        assert result is not None
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "home"
        assert result.confidence == 1.0
        assert result.classifier_type == "rule"
    
    def test_home_scene_already_home(self):
        """Test home scene with 'đã về'."""
        result = self.classifier.classify("đã về")
        
        assert result is not None
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "home"
        assert result.confidence == 1.0
    
    def test_home_scene_im_home(self):
        """Test home scene with 'tôi về rồi'."""
        result = self.classifier.classify("tôi về rồi")
        
        assert result is not None
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "home"
        assert result.confidence == 1.0
    
    def test_home_scene_with_prefix(self):
        """Test home scene with prefix 'tôi'."""
        result = self.classifier.classify("tôi về nhà rồi")
        
        assert result is not None
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "home"
        assert result.confidence == 1.0
    
    def test_home_scene_with_suffix(self):
        """Test home scene with suffix 'đi'."""
        result = self.classifier.classify("về nhà đi")
        
        assert result is not None
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "home"
        assert result.confidence == 1.0
    
    # ========================================================================
    # ENTITY EXTRACTION TESTS
    # ========================================================================
    
    def test_entity_extraction_sleep(self):
        """Test entity extraction for sleep scene."""
        entities = self.entity_extractor.extract("đi ngủ", "activate_scene")
        
        assert "scene_type" in entities
        assert entities["scene_type"] == "sleep"
    
    def test_entity_extraction_wake_up(self):
        """Test entity extraction for wake_up scene."""
        entities = self.entity_extractor.extract("thức dậy", "activate_scene")
        
        assert "scene_type" in entities
        assert entities["scene_type"] == "wake_up"
    
    def test_entity_extraction_movie(self):
        """Test entity extraction for movie scene."""
        entities = self.entity_extractor.extract("xem phim", "activate_scene")
        
        assert "scene_type" in entities
        assert entities["scene_type"] == "movie"
    
    def test_entity_extraction_away(self):
        """Test entity extraction for away scene."""
        entities = self.entity_extractor.extract("đi vắng", "activate_scene")
        
        assert "scene_type" in entities
        assert entities["scene_type"] == "away"
    
    def test_entity_extraction_home(self):
        """Test entity extraction for home scene."""
        entities = self.entity_extractor.extract("về nhà", "activate_scene")
        
        assert "scene_type" in entities
        assert entities["scene_type"] == "home"
    
    def test_entity_extraction_longest_match_first(self):
        """Test that longest match is used first (e.g., 'chào buổi sáng' before 'buổi sáng')."""
        entities = self.entity_extractor.extract("chào buổi sáng", "activate_scene")
        
        assert "scene_type" in entities
        assert entities["scene_type"] == "wake_up"
    
    # ========================================================================
    # NEGATIVE TESTS (Should NOT match scene activation)
    # ========================================================================
    
    def test_no_match_control_device(self):
        """Test that control device commands don't match scene activation."""
        result = self.classifier.classify("bật đèn")
        
        # Should match control_device, not activate_scene
        assert result is not None
        assert result.intent == "control_device"
        assert result.intent != "activate_scene"
    
    def test_no_match_environmental_comfort(self):
        """Test that environmental comfort doesn't match scene activation."""
        result = self.classifier.classify("nóng quá")
        
        # Should match environmental_comfort, not activate_scene
        assert result is not None
        assert result.intent == "environmental_comfort"
        assert result.intent != "activate_scene"
    
    def test_no_match_sensor_query(self):
        """Test that sensor queries don't match scene activation."""
        result = self.classifier.classify("nhiệt độ bao nhiêu")
        
        # Should match query_sensor, not activate_scene
        assert result is not None
        assert result.intent == "query_sensor"
        assert result.intent != "activate_scene"
    
    def test_no_match_arbitrary_text(self):
        """Test that arbitrary text doesn't match scene activation."""
        result = self.classifier.classify("xyz abc def")
        
        # Should return None (no match)
        assert result is None
    
    # ========================================================================
    # CASE INSENSITIVITY TESTS
    # ========================================================================
    
    def test_case_insensitive_uppercase(self):
        """Test that uppercase text is handled correctly."""
        result = self.classifier.classify("ĐI NGỦ")
        
        assert result is not None
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "sleep"
    
    def test_case_insensitive_mixed_case(self):
        """Test that mixed case text is handled correctly."""
        result = self.classifier.classify("Xem Phim")
        
        assert result is not None
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "movie"
    
    # ========================================================================
    # WHITESPACE HANDLING TESTS
    # ========================================================================
    
    def test_whitespace_leading(self):
        """Test that leading whitespace is handled correctly."""
        result = self.classifier.classify("   đi ngủ")
        
        assert result is not None
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "sleep"
    
    def test_whitespace_trailing(self):
        """Test that trailing whitespace is handled correctly."""
        result = self.classifier.classify("về nhà   ")
        
        assert result is not None
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "home"
    
    def test_whitespace_both(self):
        """Test that leading and trailing whitespace is handled correctly."""
        result = self.classifier.classify("   xem phim   ")
        
        assert result is not None
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "movie"
    
    # ========================================================================
    # COMPREHENSIVE COVERAGE TESTS
    # ========================================================================
    
    def test_all_scene_types_covered(self):
        """Test that all 5 scene types are properly classified."""
        test_cases = [
            ("đi ngủ", "sleep"),
            ("thức dậy", "wake_up"),
            ("xem phim", "movie"),
            ("đi vắng", "away"),
            ("về nhà", "home")
        ]
        
        for text, expected_scene_type in test_cases:
            result = self.classifier.classify(text)
            
            assert result is not None, f"Expected match for '{text}'"
            assert result.intent == "activate_scene", \
                f"Expected 'activate_scene' for '{text}', got '{result.intent}'"
            assert result.entities["scene_type"] == expected_scene_type, \
                f"Expected scene_type '{expected_scene_type}' for '{text}', got '{result.entities['scene_type']}'"
            assert result.confidence == 1.0
            assert result.classifier_type == "rule"
    
    def test_all_keywords_per_scene_type(self):
        """Test all keywords for each scene type."""
        test_cases = [
            # Sleep scene
            ("đi ngủ", "sleep"),
            ("chúc ngủ ngon", "sleep"),
            ("chuẩn bị ngủ", "sleep"),
            # Wake up scene
            ("thức dậy", "wake_up"),
            ("buổi sáng", "wake_up"),
            ("chào buổi sáng", "wake_up"),
            # Movie scene
            ("xem phim", "movie"),
            ("xem tv", "movie"),
            ("rạp chiếu phim", "movie"),
            # Away scene
            ("đi ra ngoài", "away"),
            ("rời nhà", "away"),
            ("đi vắng", "away"),
            # Home scene
            ("về nhà", "home"),
            ("đã về", "home"),
            ("tôi về rồi", "home")
        ]
        
        for text, expected_scene_type in test_cases:
            result = self.classifier.classify(text)
            
            assert result is not None, f"Expected match for '{text}'"
            assert result.intent == "activate_scene"
            assert result.entities["scene_type"] == expected_scene_type
