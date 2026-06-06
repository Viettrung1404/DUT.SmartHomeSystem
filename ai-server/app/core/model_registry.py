from __future__ import annotations

from pathlib import Path

from app.core.settings import get_settings
from app.schemas.common import HealthModelStatus
from app.services.diacritic_restorer import VietnameseDiacriticRestorer
from app.services.environment_training import ENV_ARTIFACT_NAME, ensure_environment_bundle
from app.services.phobert_slot_model import PhoBERTSlotModel
from app.services.nlp_training import NLP_ARTIFACT_NAME, ensure_nlp_bundle


class ModelRegistry:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._nlp_bundle = None
        self._environment_bundle = None
        self._restorer = None
        self._slot_model = None

    def warmup(self) -> None:
        self._nlp_bundle = ensure_nlp_bundle()
        self._environment_bundle = ensure_environment_bundle()
        self._restorer = VietnameseDiacriticRestorer()
        self._slot_model = PhoBERTSlotModel()

    @property
    def nlp_bundle(self):
        if self._nlp_bundle is None:
            self._nlp_bundle = ensure_nlp_bundle()
        return self._nlp_bundle

    @property
    def environment_bundle(self):
        if self._environment_bundle is None:
            self._environment_bundle = ensure_environment_bundle()
        return self._environment_bundle

    @property
    def diacritic_restorer(self):
        if self._restorer is None:
            self._restorer = VietnameseDiacriticRestorer()
        return self._restorer

    @property
    def slot_model(self):
        if self._slot_model is None:
            self._slot_model = PhoBERTSlotModel()
        return self._slot_model

    def health_models(self) -> list[HealthModelStatus]:
        return [
            self._build_status("nlp", NLP_ARTIFACT_NAME, self.nlp_bundle.version, bool(self.nlp_bundle.metrics)),
            self._build_status(
                "environment",
                ENV_ARTIFACT_NAME,
                self.environment_bundle.version,
                bool(self.environment_bundle.metrics),
            ),
            self._build_status(
                "restoration",
                self.settings.restoration_lexicon_path.name,
                "1.0.0",
                self.diacritic_restorer.has_lexicon(),
            ),
            self._build_status(
                "phobert_slot",
                self.settings.phobert_slot_dir.name,
                "1.0.0",
                self.slot_model.available,
            ),
        ]

    def _build_status(self, name: str, artifact_name: str, version: str, metrics_available: bool) -> HealthModelStatus:
        artifact_path = self.settings.artifacts_dir / artifact_name
        status = "artifact_ready" if artifact_path.exists() else "bootstrapped_in_memory"
        return HealthModelStatus(
            name=name,
            artifact_present=artifact_path.exists(),
            version=version,
            status=status,
            metrics_available=metrics_available,
        )


registry = ModelRegistry()
