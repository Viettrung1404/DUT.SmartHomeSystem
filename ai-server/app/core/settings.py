from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import os


class Settings:
    def __init__(self) -> None:
        base_dir = Path(__file__).resolve().parents[2]
        self.base_dir = base_dir
        self.app_dir = base_dir / "app"
        self.data_dir = base_dir / "data"
        self.artifacts_dir = base_dir / "artifacts"
        self.notebooks_dir = base_dir / "notebooks"
        self.default_locale = os.getenv("AI_SERVER_DEFAULT_LOCALE", "vi-VN")
        self.environment_horizon_minutes = int(os.getenv("AI_SERVER_ENV_HORIZON_MINUTES", "30"))
        self.environment_history_min_points = int(os.getenv("AI_SERVER_ENV_MIN_POINTS", "8"))
        self.database_url = os.getenv("AI_SERVER_DATABASE_URL") or os.getenv("DATABASE_URL")
        self.auto_bootstrap_models = os.getenv("AI_SERVER_AUTO_BOOTSTRAP", "1").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        self.random_seed = int(os.getenv("AI_SERVER_RANDOM_SEED", "42"))
        self.nlp_confidence_threshold = float(os.getenv("AI_SERVER_NLP_CONFIDENCE_THRESHOLD", "0.46"))
        self.nlp_oos_threshold = float(os.getenv("AI_SERVER_NLP_OOS_THRESHOLD", "0.38"))
        self.nlp_data_dir = self.data_dir / "nlp"
        self.environment_data_dir = self.data_dir / "environment"
        self.house_environment_csv = self.environment_data_dir / "house_ambient_log.csv"
        self.reference_environment_csv = self.environment_data_dir / "reference_environment_log.csv"
        self.restoration_lexicon_path = self.artifacts_dir / "diacritic_restoration_lexicon.json"
        self.phobert_slot_dir = self.artifacts_dir / "phobert_slot"
        self.enable_hybrid_slot_model = os.getenv("AI_SERVER_ENABLE_HYBRID_SLOT", "1").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.artifacts_dir.mkdir(parents=True, exist_ok=True)
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.nlp_data_dir.mkdir(parents=True, exist_ok=True)
    settings.environment_data_dir.mkdir(parents=True, exist_ok=True)
    settings.notebooks_dir.mkdir(parents=True, exist_ok=True)
    return settings
