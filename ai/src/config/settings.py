"""
Configuration settings for Vietnamese NLP Intent Classification Server.
Loads configuration from environment variables.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Pydantic V2 configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        protected_namespaces=('settings_',)  # Avoid conflict with model_path
    )
    
    # API Configuration
    api_version: str = "v1"
    api_host: str = "0.0.0.0"
    api_port: int = 8001
    debug: bool = False
    
    # CORS Configuration
    cors_origins: str = "http://localhost:3000,https://smarthome.example.com"  # Comma-separated list
    cors_allow_credentials: bool = True
    cors_allow_methods: str = "GET,POST"
    cors_allow_headers: str = "Authorization,Content-Type"
    
    # JWT Authentication
    jwt_secret_key: str = "change-this-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60
    
    # Database Configuration
    database_url: str = "postgresql://user:password@localhost:5432/nlp_db"
    
    # Redis Cache Configuration
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl_seconds: int = 300
    
    # Model Configuration
    # NOTE: `model_path` is treated as a directory by the ML classifier.
    # Default points at the repo-provided PhoBERT model bundle.
    model_path: str = "models/phobert_intent_v1"
    onnx_model_path: str = "models/phobert_intent_v1/best_model.onnx"
    use_onnx: bool = True
    confidence_threshold: float = 0.7
    
    # Performance Configuration
    max_concurrent_requests: int = 50
    inference_timeout_seconds: int = 5
    rate_limit_per_minute: int = 60
    
    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "logs/nlp_server.log"
    log_rotation_days: int = 30
    log_format: str = "json"
    
    # Model Training Configuration
    batch_size: int = 32
    learning_rate: float = 2e-5
    num_epochs: int = 10
    warmup_steps: int = 500
    max_seq_length: int = 128
    
    # Data Augmentation
    augmentation_factor: int = 2
    use_paraphrase: bool = True
    use_synonym_replacement: bool = True
    use_typo_simulation: bool = True
    
    def get_cors_origins(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


# Global settings instance
settings = Settings()
