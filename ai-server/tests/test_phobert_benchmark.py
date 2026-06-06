from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.experiments.phobert_benchmark import (
    build_restoration_lexicon,
    evaluate_restoration_quality,
    load_scenario_dataset,
    records_for_view,
    train_baseline_intent_model,
    train_slot_rule_baseline,
)


def test_restoration_lexicon_covers_core_tokens() -> None:
    dataset = load_scenario_dataset()
    lexicon = build_restoration_lexicon(dataset.train_records)
    assert "bat" in lexicon
    assert "phong" in lexicon
    assert dataset.restoration_coverage > 0.85


def test_records_for_view_support_clean_and_restored() -> None:
    dataset = load_scenario_dataset()
    lexicon = build_restoration_lexicon(dataset.train_records)
    clean_records = records_for_view(dataset.test_records[:5], "clean", lexicon)
    restored_records = records_for_view(dataset.test_records[:5], "restored", lexicon)
    assert len(clean_records) == len(restored_records) == 5
    assert all("text" in row for row in clean_records)


def test_baseline_bench_artifacts_build() -> None:
    dataset = load_scenario_dataset()
    sample_rows = []
    seen_per_intent = {}
    for row in dataset.train_records:
        intent = row["intent"]
        count = seen_per_intent.get(intent, 0)
        if count < 10:
            sample_rows.append(row)
            seen_per_intent[intent] = count + 1
        if len(seen_per_intent) == len(dataset.label_list) and all(value >= 10 for value in seen_per_intent.values()):
            break
    train_view = records_for_view(sample_rows, "clean", build_restoration_lexicon(dataset.train_records))
    intent_artifacts = train_baseline_intent_model(train_view)
    slot_artifacts = train_slot_rule_baseline(train_view)
    assert intent_artifacts.model_size_mb > 0
    assert slot_artifacts.max_phrase_len >= 1


def test_restoration_quality_dataframe() -> None:
    dataset = load_scenario_dataset()
    lexicon = build_restoration_lexicon(dataset.train_records)
    quality = evaluate_restoration_quality(dataset.test_records[:100], lexicon)
    assert not quality.empty
    assert 0.0 <= quality.iloc[0]["restoration_token_accuracy"] <= 1.0
