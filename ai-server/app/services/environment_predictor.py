from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from app.core.capabilities import CAPABILITY_NOTE
from app.core.settings import get_settings
from app.schemas.common import PredictionInterval, TopSignal
from app.schemas.prediction import PredictEnvironmentResponse
from app.services.db_adapter import SensorHistoryAdapter
from app.services.environment_features import build_feature_row
from app.services.environment_training import ensure_environment_bundle


class EnvironmentPredictor:
    def __init__(self) -> None:
        self.bundle = None
        self.db_adapter = SensorHistoryAdapter()

    def _bundle(self):
        if self.bundle is None:
            self.bundle = ensure_environment_bundle()
        return self.bundle

    def predict_from_request(self, request) -> PredictEnvironmentResponse:
        if request.inline_history:
            history = list(request.inline_history)
        else:
            history = self.db_adapter.load_inline_history(request.db_source)
        if len(history) < get_settings().environment_history_min_points:
            raise ValueError(
                f"Cần ít nhất {get_settings().environment_history_min_points} điểm lịch sử để dự báo ổn định"
            )

        feature_row = build_feature_row(history)
        bundle = self._bundle()
        frame = pd.DataFrame([feature_row], columns=bundle.feature_columns)

        rf_temp = bundle.models["rf_temp"]
        rf_humidity = bundle.models["rf_humidity"]
        feature_values = frame.to_numpy()
        temp_tree_preds = np.array([tree.predict(feature_values)[0] for tree in rf_temp.estimators_], dtype=float)
        humidity_tree_preds = np.array([tree.predict(feature_values)[0] for tree in rf_humidity.estimators_], dtype=float)

        temp_point = float(np.median(temp_tree_preds))
        humidity_point = float(np.median(humidity_tree_preds))
        temp_interval = PredictionInterval(
            lower=round(float(np.quantile(temp_tree_preds, 0.10)), 3),
            median=round(temp_point, 3),
            upper=round(float(np.quantile(temp_tree_preds, 0.90)), 3),
        )
        humidity_interval = PredictionInterval(
            lower=round(float(np.quantile(humidity_tree_preds, 0.10)), 3),
            median=round(humidity_point, 3),
            upper=round(float(np.quantile(humidity_tree_preds, 0.90)), 3),
        )
        comfort_proxy = self._comfort_proxy(temp_point, humidity_point)
        action_hint = self._action_hint(temp_point, humidity_point, feature_row)
        top_signals = self._top_signals(feature_row)

        return PredictEnvironmentResponse(
            temperature_next_30min=round(temp_point, 3),
            humidity_next_30min=round(humidity_point, 3),
            temperature_interval=temp_interval,
            humidity_interval=humidity_interval,
            comfort_proxy=comfort_proxy,
            comfort_note=CAPABILITY_NOTE,
            recommended_action_hint=action_hint,
            top_signals=top_signals,
            model_version=bundle.version,
            training_metrics=bundle.metrics,
        )

    def _top_signals(self, feature_row: dict[str, Any]) -> list[TopSignal]:
        bundle = self._bundle()
        rf_temp = bundle.models["rf_temp"]
        importance_pairs = sorted(
            zip(bundle.feature_columns, rf_temp.feature_importances_),
            key=lambda item: item[1],
            reverse=True,
        )
        return [
            TopSignal(
                feature=feature,
                importance=round(float(importance), 4),
                value=self._safe_float(feature_row.get(feature)),
            )
            for feature, importance in importance_pairs[:5]
        ]

    def _safe_float(self, value: Any) -> float | int | bool | None:
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float, np.number)):
            return round(float(value), 4)
        return None

    def _comfort_proxy(self, temperature: float, humidity: float) -> str:
        if 24.0 <= temperature <= 27.0 and 45.0 <= humidity <= 65.0:
            return "comfortable"
        if 27.0 < temperature <= 28.5 and humidity < 70.0:
            return "slightly_warm"
        if humidity >= 72.0 and temperature < 28.5:
            return "humid"
        if temperature >= 28.5:
            return "hot"
        return "uncomfortable"

    def _action_hint(self, temperature: float, humidity: float, feature_row: dict[str, Any]) -> str:
        if bool(feature_row.get("rain_detected", 0)):
            return "close_rain_servo"
        if temperature >= 28.5 and not bool(feature_row.get("fan_on", 0)):
            return "turn_on_fan"
        if humidity >= 72.0 and not bool(feature_row.get("rain_detected", 0)):
            return "open_window"
        return "no_action"
