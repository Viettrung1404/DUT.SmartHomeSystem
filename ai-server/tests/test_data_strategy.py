from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.datasets.smarthome_corpus import CORE_INTENTS, build_bootstrap_corpus, corpus_summary, split_records
from app.services.environment_training import load_environment_log_csv, prepare_training_frame


def test_bootstrap_corpus_has_expected_size_and_intents() -> None:
    records = build_bootstrap_corpus()
    summary = corpus_summary(records)
    assert summary["rows"] >= 4200
    assert set(CORE_INTENTS).issubset(set(summary["intent_counts"]))
    assert summary["split_counts"]["train"] > summary["split_counts"]["test"]


def test_split_groups_do_not_change_split() -> None:
    records = build_bootstrap_corpus()
    grouped = {}
    for row in records:
        split = grouped.setdefault(row["split_group"], row["split"])
        assert split == row["split"]
    split_records(records)


def test_load_environment_log_csv_maps_optional_columns(tmp_path: Path) -> None:
    frame = pd.DataFrame(
        [
            {
                "timestamp": "2026-06-05T18:00:00",
                "temperature": 28.1,
                "humidity": 69.0,
                "bathroom_occupied": 1,
                "fan_on": 0,
                "rain_detected": 0,
            },
            {
                "timestamp": "2026-06-05T18:05:00",
                "temperature": 28.0,
                "humidity": 68.7,
                "bathroom_occupied": 0,
                "fan_on": 1,
                "rain_detected": 0,
            },
        ]
    )
    csv_path = tmp_path / "house_ambient_log.csv"
    frame.to_csv(csv_path, index=False)

    loaded = load_environment_log_csv(csv_path)
    assert list(loaded.columns) == [
        "room_id",
        "timestamp",
        "temperature",
        "humidity",
        "occupancy_ratio",
        "fan_on",
        "rain_detected",
        "outdoor_temp",
    ]
    assert loaded["occupancy_ratio"].iloc[0] == 1.0
    assert loaded["fan_on"].iloc[1]


def test_prepare_training_frame_prefers_given_path(tmp_path: Path) -> None:
    frame = pd.DataFrame(
        [
            {
                "timestamp": "2026-06-05T18:00:00",
                "temperature": 28.1,
                "humidity": 69.0,
            },
            {
                "timestamp": "2026-06-05T18:05:00",
                "temperature": 28.0,
                "humidity": 68.7,
            },
        ]
    )
    csv_path = tmp_path / "reference_environment_log.csv"
    frame.to_csv(csv_path, index=False)

    loaded, meta = prepare_training_frame(csv_path)
    assert meta["source"] == "house_log_csv"
    assert str(csv_path) == meta["path"]
    assert not loaded.empty
