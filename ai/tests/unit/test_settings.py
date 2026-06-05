"""
Unit tests for configuration settings.
"""

import pytest
from pydantic import ValidationError
from src.config.settings import Settings


class TestSettings:
    """Test configuration settings loading and validation."""
    
    def test_settings_loads_with_defaults(self):
        """Test that settings can be loaded with default values."""
        settings = Settings()
        
        # API Configuration
        assert settings.api_version == "v1"
        assert settings.api_host == "0.0.0.0"
        assert settings.api_port == 8001
        assert settings.debug == False
        
        # JWT Authentication
        assert settings.jwt_secret_key is not None
        assert settings.jwt_algorithm == "HS256"
        assert settings.jwt_expiration_minutes == 60
        
        # Database Configuration
        assert settings.database_url is not None
        
        # Redis Cache Configuration
        assert settings.redis_url is not None
        assert settings.cache_ttl_seconds == 300
        
        # Model Configuration
        assert settings.model_path is not None
        assert settings.onnx_model_path is not None
        assert settings.use_onnx == True
        assert settings.confidence_threshold == 0.7
        
        # Performance Configuration
        assert settings.max_concurrent_requests == 50
        assert settings.inference_timeout_seconds == 5
        assert settings.rate_limit_per_minute == 60
        
        # Logging Configuration
        assert settings.log_level == "INFO"
        assert settings.log_file is not None
        assert settings.log_rotation_days == 30
        assert settings.log_format == "json"
    
    def test_settings_has_all_required_fields(self):
        """Test that all required configuration fields are present."""
        settings = Settings()
        
        # Check all required attributes exist
        required_fields = [
            # API
            'api_version', 'api_host', 'api_port', 'debug',
            # CORS
            'cors_origins', 'cors_allow_credentials', 'cors_allow_methods', 'cors_allow_headers',
            # JWT
            'jwt_secret_key', 'jwt_algorithm', 'jwt_expiration_minutes',
            # Database
            'database_url',
            # Redis
            'redis_url', 'cache_ttl_seconds',
            # Model
            'model_path', 'onnx_model_path', 'use_onnx', 'confidence_threshold',
            # Performance
            'max_concurrent_requests', 'inference_timeout_seconds', 'rate_limit_per_minute',
            # Logging
            'log_level', 'log_file', 'log_rotation_days', 'log_format',
            # Training
            'batch_size', 'learning_rate', 'num_epochs', 'warmup_steps', 'max_seq_length',
            # Augmentation
            'augmentation_factor', 'use_paraphrase', 'use_synonym_replacement', 'use_typo_simulation'
        ]
        
        for field in required_fields:
            assert hasattr(settings, field), f"Missing required field: {field}"
    
    def test_settings_types(self):
        """Test that settings have correct types."""
        settings = Settings()
        
        # String types
        assert isinstance(settings.api_version, str)
        assert isinstance(settings.jwt_secret_key, str)
        assert isinstance(settings.database_url, str)
        assert isinstance(settings.redis_url, str)
        
        # Integer types
        assert isinstance(settings.api_port, int)
        assert isinstance(settings.jwt_expiration_minutes, int)
        assert isinstance(settings.cache_ttl_seconds, int)
        assert isinstance(settings.max_concurrent_requests, int)
        
        # Float types
        assert isinstance(settings.confidence_threshold, float)
        assert isinstance(settings.learning_rate, float)
        
        # Boolean types
        assert isinstance(settings.debug, bool)
        assert isinstance(settings.use_onnx, bool)
        assert isinstance(settings.use_paraphrase, bool)
    
    def test_cors_origins_parsing(self):
        """Test that CORS origins are parsed correctly from comma-separated string."""
        settings = Settings()
        
        # Get parsed CORS origins
        origins = settings.get_cors_origins()
        
        # Should be a list
        assert isinstance(origins, list)
        
        # Should have at least one origin
        assert len(origins) > 0
        
        # Each origin should be a non-empty string
        for origin in origins:
            assert isinstance(origin, str)
            assert len(origin) > 0
