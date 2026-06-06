from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
import math

import numpy as np
import pandas as pd

from app.schemas.prediction import InlineHistoryPoint


FEATURE_COLUMNS = [
    "temp_current",
    "humidity_current",
    "temp_lag_1",
    "temp_lag_2",
    "temp_lag_3",
    "temp_lag_6",
    "humidity_lag_1",
    "humidity_lag_2",
    "humidity_lag_3",
    "humidity_lag_6",
    "temp_slope_3",
    "temp_slope_6",
    "temp_slope_12",
    "humidity_slope_3",
    "humidity_slope_6",
    "humidity_slope_12",
    "temp_mean_3",
    "temp_mean_6",
    "temp_mean_12",
    "humidity_mean_3",
    "humidity_mean_6",
    "humidity_mean_12",
    "temp_std_6",
    "humidity_std_6",
    "temp_delta_12",
    "humidity_delta_12",
    "temp_humidity_interaction",
    "dew_point_proxy",
    "occupancy_ratio",
    "fan_on",
    "rain_detected",
    "outdoor_temp",
    "hour_sin",
    "hour_cos",
]


def _slope(values: np.ndarray) -> float:
    if len(values) < 2:
        return 0.0
    x = np.arange(len(values))
    coeffs = np.polyfit(x, values, 1)
    return float(coeffs[0])


def _value_at(values: Sequence[float], offset: int) -> float:
    idx = max(0, len(values) - offset)
    return float(values[idx])


def build_feature_row(history: list[InlineHistoryPoint]) -> dict[str, float]:
    frame = pd.DataFrame([point.model_dump() for point in history]).sort_values("timestamp")
    temps = frame["temperature"].astype(float).to_numpy()
    humidities = frame["humidity"].astype(float).to_numpy()
    occupancy = frame["occupancy_ratio"].astype(float).ffill().fillna(0.0).to_numpy()
    fan_on = frame["fan_on"].fillna(False).astype(int).to_numpy()
    rain = frame["rain_detected"].fillna(False).astype(int).to_numpy()
    outdoor = frame["outdoor_temp"].astype(float).ffill().fillna(temps[-1]).to_numpy()
    last_ts = pd.to_datetime(frame["timestamp"].iloc[-1]).to_pydatetime()

    temp_current = float(temps[-1])
    humidity_current = float(humidities[-1])
    dew_point_proxy = temp_current - ((100 - humidity_current) / 5.0)
    hour_decimal = last_ts.hour + (last_ts.minute / 60.0)
    angle = (2 * math.pi * hour_decimal) / 24.0

    row = {
        "temp_current": temp_current,
        "humidity_current": humidity_current,
        "temp_lag_1": _value_at(temps, 2),
        "temp_lag_2": _value_at(temps, 3),
        "temp_lag_3": _value_at(temps, 4),
        "temp_lag_6": _value_at(temps, min(7, len(temps))),
        "humidity_lag_1": _value_at(humidities, 2),
        "humidity_lag_2": _value_at(humidities, 3),
        "humidity_lag_3": _value_at(humidities, 4),
        "humidity_lag_6": _value_at(humidities, min(7, len(humidities))),
        "temp_slope_3": _slope(temps[-3:]),
        "temp_slope_6": _slope(temps[-6:]),
        "temp_slope_12": _slope(temps[-12:]),
        "humidity_slope_3": _slope(humidities[-3:]),
        "humidity_slope_6": _slope(humidities[-6:]),
        "humidity_slope_12": _slope(humidities[-12:]),
        "temp_mean_3": float(np.mean(temps[-3:])),
        "temp_mean_6": float(np.mean(temps[-6:])),
        "temp_mean_12": float(np.mean(temps[-12:])),
        "humidity_mean_3": float(np.mean(humidities[-3:])),
        "humidity_mean_6": float(np.mean(humidities[-6:])),
        "humidity_mean_12": float(np.mean(humidities[-12:])),
        "temp_std_6": float(np.std(temps[-6:])),
        "humidity_std_6": float(np.std(humidities[-6:])),
        "temp_delta_12": float(temps[-1] - temps[max(0, len(temps) - 12)]),
        "humidity_delta_12": float(humidities[-1] - humidities[max(0, len(humidities) - 12)]),
        "temp_humidity_interaction": float(temp_current * humidity_current),
        "dew_point_proxy": float(dew_point_proxy),
        "occupancy_ratio": float(occupancy[-1]),
        "fan_on": float(fan_on[-1]),
        "rain_detected": float(rain[-1]),
        "outdoor_temp": float(outdoor[-1]),
        "hour_sin": float(math.sin(angle)),
        "hour_cos": float(math.cos(angle)),
    }
    return row


def build_feature_frame(history_items: list[list[InlineHistoryPoint]]) -> pd.DataFrame:
    return pd.DataFrame([build_feature_row(history) for history in history_items], columns=FEATURE_COLUMNS)
