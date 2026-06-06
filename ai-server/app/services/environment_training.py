from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
import json

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from app.core.settings import get_settings
from app.schemas.prediction import InlineHistoryPoint
from app.services.environment_features import FEATURE_COLUMNS, build_feature_frame


ENV_ARTIFACT_NAME = "environment_bundle.joblib"
ENV_VERSION = "1.0.0"


@dataclass
class EnvironmentBundle:
    models: dict[str, Any]
    feature_columns: list[str]
    metrics: dict[str, Any]
    version: str


def _bool_to_float(value: Any) -> float:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return 0.0
    if isinstance(value, str):
        return 1.0 if value.strip().lower() in {"1", "true", "yes", "on"} else 0.0
    return 1.0 if bool(value) else 0.0


def load_environment_log_csv(csv_path: Path) -> pd.DataFrame:
    frame = pd.read_csv(csv_path)
    if "timestamp" not in frame.columns or "temperature" not in frame.columns or "humidity" not in frame.columns:
        raise ValueError("Environment log CSV must include timestamp, temperature, and humidity columns")
    frame["timestamp"] = pd.to_datetime(frame["timestamp"])
    frame["temperature"] = frame["temperature"].astype(float)
    frame["humidity"] = frame["humidity"].astype(float)
    if "room_id" not in frame.columns:
        frame["room_id"] = "ambient_zone_1"
    if "occupancy_ratio" not in frame.columns:
        if "bathroom_occupied" in frame.columns:
            frame["occupancy_ratio"] = frame["bathroom_occupied"].apply(_bool_to_float)
        else:
            frame["occupancy_ratio"] = 0.0
    if "fan_on" not in frame.columns:
        frame["fan_on"] = False
    if "rain_detected" not in frame.columns:
        frame["rain_detected"] = False
    if "outdoor_temp" not in frame.columns:
        frame["outdoor_temp"] = frame["temperature"].astype(float) + 1.5
    frame["fan_on"] = frame["fan_on"].apply(_bool_to_float).astype(bool)
    frame["rain_detected"] = frame["rain_detected"].apply(_bool_to_float).astype(bool)
    frame["occupancy_ratio"] = frame["occupancy_ratio"].astype(float).clip(0.0, 1.0)
    frame["outdoor_temp"] = frame["outdoor_temp"].astype(float)
    return frame[
        [
            "room_id",
            "timestamp",
            "temperature",
            "humidity",
            "occupancy_ratio",
            "fan_on",
            "rain_detected",
            "outdoor_temp",
        ]
    ].sort_values(["room_id", "timestamp"])


def generate_synthetic_histories(
    *,
    rooms: int = 8,
    days: int = 3,
    interval_minutes: int = 5,
) -> pd.DataFrame:
    rng = np.random.default_rng(get_settings().random_seed)
    periods = int((24 * 60 / interval_minutes) * days)
    start = datetime(2026, 1, 1, 0, 0, 0)
    records: list[dict[str, Any]] = []
    for room_idx in range(rooms):
        temp = 24.0 + rng.normal(0, 0.6)
        humidity = 56.0 + rng.normal(0, 3.0)
        for step in range(periods):
            timestamp = start + timedelta(minutes=step * interval_minutes)
            hour = timestamp.hour + timestamp.minute / 60.0
            outdoor = 28 + 4 * np.sin((2 * np.pi * hour) / 24.0) + rng.normal(0, 0.6)
            occupancy = 0.85 if 18 <= hour <= 23 else 0.35 if 6 <= hour <= 8 else 0.1
            fan_on = temp > 28.0 or (temp > 27.2 and occupancy > 0.6)
            rain_detected = bool((hour >= 15 and hour <= 17 and rng.random() > 0.72))
            temp = (
                temp
                + 0.10 * (outdoor - temp)
                + 0.55 * occupancy
                - 0.75 * float(fan_on)
                + rng.normal(0, 0.18)
            )
            humidity = (
                humidity
                + 0.07 * (67 - humidity)
                + 0.25 * occupancy
                + 0.55 * float(rain_detected)
                - 0.18 * float(fan_on)
                + rng.normal(0, 0.35)
            )
            records.append(
                {
                    "room_id": f"room-{room_idx+1}",
                    "timestamp": timestamp,
                    "temperature": round(float(temp), 3),
                    "humidity": round(float(humidity), 3),
                    "occupancy_ratio": round(float(occupancy), 3),
                    "fan_on": bool(fan_on),
                    "rain_detected": bool(rain_detected),
                    "outdoor_temp": round(float(outdoor), 3),
                }
            )
    return pd.DataFrame(records)


def prepare_training_frame(dataset_path: Path | None = None) -> tuple[pd.DataFrame, dict[str, Any]]:
    settings = get_settings()
    candidate_path = dataset_path or (settings.house_environment_csv if settings.house_environment_csv.exists() else None)
    if candidate_path and candidate_path.exists():
        frame = load_environment_log_csv(candidate_path)
        return frame, {
            "source": "house_log_csv",
            "path": str(candidate_path),
            "ambient_scope": "single_zone",
        }
    if settings.reference_environment_csv.exists():
        frame = load_environment_log_csv(settings.reference_environment_csv)
        return frame, {
            "source": "reference_log_csv",
            "path": str(settings.reference_environment_csv),
            "ambient_scope": "single_zone_reference",
        }
    return generate_synthetic_histories(rooms=1), {
        "source": "synthetic_bootstrap",
        "path": None,
        "ambient_scope": "single_zone_bootstrap",
    }


def build_supervised_dataset(
    frame: pd.DataFrame,
    *,
    history_window: int = 12,
    forecast_horizon_steps: int = 6,
) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    histories: list[list[InlineHistoryPoint]] = []
    temp_targets: list[float] = []
    humidity_targets: list[float] = []
    for _, room_frame in frame.groupby("room_id"):
        room_frame = room_frame.sort_values("timestamp").reset_index(drop=True)
        rows = [InlineHistoryPoint(**row) for row in room_frame.to_dict(orient="records")]
        for idx in range(history_window - 1, len(rows) - forecast_horizon_steps):
            history = rows[idx - history_window + 1 : idx + 1]
            target = rows[idx + forecast_horizon_steps]
            histories.append(history)
            temp_targets.append(target.temperature)
            humidity_targets.append(target.humidity)
    return build_feature_frame(histories), np.array(temp_targets), np.array(humidity_targets)


def _regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    return {
        "mae": round(float(mean_absolute_error(y_true, y_pred)), 4),
        "rmse": round(rmse, 4),
        "r2": round(float(r2_score(y_true, y_pred)), 4),
    }


def train_environment_bundle(dataset_path: Path | None = None) -> EnvironmentBundle:
    frame, dataset_meta = prepare_training_frame(dataset_path)
    features, y_temp, y_humidity = build_supervised_dataset(frame)
    split_idx = int(len(features) * 0.8)
    x_train = features.iloc[:split_idx]
    x_val = features.iloc[split_idx:]
    temp_train, temp_val = y_temp[:split_idx], y_temp[split_idx:]
    humidity_train, humidity_val = y_humidity[:split_idx], y_humidity[split_idx:]

    linear_temp = LinearRegression().fit(x_train, temp_train)
    linear_humidity = LinearRegression().fit(x_train, humidity_train)
    rf_temp = RandomForestRegressor(
        n_estimators=80,
        max_depth=8,
        min_samples_leaf=2,
        random_state=get_settings().random_seed,
    ).fit(x_train, temp_train)
    rf_humidity = RandomForestRegressor(
        n_estimators=80,
        max_depth=8,
        min_samples_leaf=2,
        random_state=get_settings().random_seed + 1,
    ).fit(x_train, humidity_train)

    persistence_temp = x_val["temp_current"].to_numpy()
    persistence_humidity = x_val["humidity_current"].to_numpy()

    metrics = {
        "temperature": {
            "persistence": _regression_metrics(temp_val, persistence_temp),
            "linear_regression": _regression_metrics(temp_val, linear_temp.predict(x_val)),
            "random_forest": _regression_metrics(temp_val, rf_temp.predict(x_val)),
        },
        "humidity": {
            "persistence": _regression_metrics(humidity_val, persistence_humidity),
            "linear_regression": _regression_metrics(humidity_val, linear_humidity.predict(x_val)),
            "random_forest": _regression_metrics(humidity_val, rf_humidity.predict(x_val)),
        },
        "dataset": {
            "source": dataset_meta["source"],
            "source_path": dataset_meta["path"],
            "ambient_scope": dataset_meta["ambient_scope"],
            "rows": int(len(features)),
            "train_rows": int(len(x_train)),
            "validation_rows": int(len(x_val)),
            "history_window_points": 12,
            "forecast_horizon_minutes": 30,
        },
    }
    return EnvironmentBundle(
        models={
            "linear_temp": linear_temp,
            "linear_humidity": linear_humidity,
            "rf_temp": rf_temp,
            "rf_humidity": rf_humidity,
        },
        feature_columns=list(FEATURE_COLUMNS),
        metrics=metrics,
        version=ENV_VERSION,
    )


def save_environment_bundle(bundle: EnvironmentBundle, target_dir: Path | None = None) -> Path:
    settings = get_settings()
    target = (target_dir or settings.artifacts_dir) / ENV_ARTIFACT_NAME
    payload = {
        "models": bundle.models,
        "feature_columns": bundle.feature_columns,
        "metrics": bundle.metrics,
        "version": bundle.version,
    }
    joblib.dump(payload, target)
    metrics_path = target.with_name("environment_metrics.json")
    metrics_path.write_text(json.dumps(bundle.metrics, indent=2), encoding="utf-8")
    model_card_path = target.with_name("environment_model_card.md")
    model_card_path.write_text(
        "\n".join(
            [
                "# Environment Forecast Model Card",
                "",
                f"- Version: {bundle.version}",
                "- Task: 30-minute indoor temperature/humidity forecasting",
                f"- Dataset source: {bundle.metrics.get('dataset', {}).get('source')}",
                "- Features: lag, slope, rolling stats, dew point proxy, cyclical hour, exogenous context",
                "- Production model: RandomForestRegressor",
                f"- Temperature RF metrics: {bundle.metrics.get('temperature', {}).get('random_forest', {})}",
                f"- Humidity RF metrics: {bundle.metrics.get('humidity', {}).get('random_forest', {})}",
            ]
        ),
        encoding="utf-8",
    )
    return target


def load_environment_bundle(target_dir: Path | None = None) -> EnvironmentBundle | None:
    settings = get_settings()
    target = (target_dir or settings.artifacts_dir) / ENV_ARTIFACT_NAME
    if not target.exists():
        return None
    payload = joblib.load(target)
    return EnvironmentBundle(
        models=dict(payload["models"]),
        feature_columns=list(payload.get("feature_columns", FEATURE_COLUMNS)),
        metrics=dict(payload.get("metrics", {})),
        version=str(payload.get("version", ENV_VERSION)),
    )


def ensure_environment_bundle() -> EnvironmentBundle:
    bundle = load_environment_bundle()
    if bundle is not None:
        return bundle
    bundle = train_environment_bundle()
    if get_settings().auto_bootstrap_models:
        save_environment_bundle(bundle)
    return bundle
