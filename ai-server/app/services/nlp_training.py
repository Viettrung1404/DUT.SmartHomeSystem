from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import FeatureUnion, Pipeline

from app.core.settings import get_settings
from app.datasets.nlp_seed import SEED_CORPUS
from app.datasets.smarthome_corpus import (
    TEST_SPLIT,
    TRAIN_SPLIT,
    VALIDATION_SPLIT,
    build_bootstrap_corpus,
    corpus_summary,
    load_jsonl,
)
from app.services.text_normalizer import normalize_text


NLP_ARTIFACT_NAME = "nlp_bundle.joblib"
NLP_VERSION = "1.0.0"


@dataclass
class NLPBundle:
    pipeline: Pipeline
    labels: list[str]
    metrics: dict[str, Any]
    version: str


def _build_classifier() -> Pipeline:
    vectorizers = FeatureUnion(
        [
            ("word_tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
            ("char_tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=1)),
        ]
    )
    return Pipeline(
        [
            ("features", vectorizers),
            (
                "clf",
                LogisticRegression(
                    max_iter=1200,
                    class_weight="balanced",
                    random_state=get_settings().random_seed,
                ),
            ),
        ]
    )


def _corpus_paths() -> dict[str, Path]:
    data_dir = get_settings().nlp_data_dir
    return {
        "master": data_dir / "master.jsonl",
        TRAIN_SPLIT: data_dir / f"{TRAIN_SPLIT}.jsonl",
        VALIDATION_SPLIT: data_dir / f"{VALIDATION_SPLIT}.jsonl",
        TEST_SPLIT: data_dir / f"{TEST_SPLIT}.jsonl",
    }


def build_training_rows() -> tuple[list[str], list[str]]:
    split_path = _corpus_paths()[TRAIN_SPLIT]
    if split_path.exists():
        records = load_jsonl(split_path)
        if records:
            return [str(record["normalized_text"]) for record in records], [str(record["intent"]) for record in records]
    texts: list[str] = []
    labels: list[str] = []
    for label, samples in SEED_CORPUS.items():
        for sample in samples:
            texts.append(normalize_text(sample))
            labels.append(label)
    return texts, labels


def _validation_rows() -> tuple[list[str], list[str]] | None:
    split_path = _corpus_paths()[VALIDATION_SPLIT]
    if not split_path.exists():
        return None
    records = load_jsonl(split_path)
    if not records:
        return None
    return [str(record["normalized_text"]) for record in records], [str(record["intent"]) for record in records]


def train_nlp_bundle() -> NLPBundle:
    texts, labels = build_training_rows()
    validation_rows = _validation_rows()
    if validation_rows is None:
        x_train, x_val, y_train, y_val = train_test_split(
            texts,
            labels,
            test_size=0.25,
            stratify=labels,
            random_state=get_settings().random_seed,
        )
        dataset_metrics: dict[str, Any] = {"source": "seed_fallback"}
    else:
        x_train, y_train = texts, labels
        x_val, y_val = validation_rows
        master_records = load_jsonl(_corpus_paths()["master"])
        if not master_records:
            master_records = build_bootstrap_corpus()
        dataset_metrics = corpus_summary(master_records)
        dataset_metrics["source"] = "jsonl_bootstrap"
    pipeline = _build_classifier()
    pipeline.fit(x_train, y_train)
    preds = pipeline.predict(x_val)
    metrics = {
        "accuracy": round(float(accuracy_score(y_val, preds)), 4),
        "macro_f1": round(float(f1_score(y_val, preds, average="macro")), 4),
        "train_size": int(len(x_train)),
        "validation_size": int(len(x_val)),
        "dataset": dataset_metrics,
    }
    return NLPBundle(
        pipeline=pipeline,
        labels=sorted(set(labels)),
        metrics=metrics,
        version=NLP_VERSION,
    )


def save_nlp_bundle(bundle: NLPBundle, target_dir: Path | None = None) -> Path:
    settings = get_settings()
    target = (target_dir or settings.artifacts_dir) / NLP_ARTIFACT_NAME
    payload: dict[str, Any] = {
        "pipeline": bundle.pipeline,
        "labels": bundle.labels,
        "metrics": bundle.metrics,
        "version": bundle.version,
    }
    joblib.dump(payload, target)
    metrics_path = target.with_name("nlp_metrics.json")
    metrics_path.write_text(json.dumps(bundle.metrics, indent=2), encoding="utf-8")
    model_card_path = target.with_name("nlp_model_card.md")
    model_card_path.write_text(
        "\n".join(
            [
                "# NLP Model Card",
                "",
                f"- Version: {bundle.version}",
                "- Task: Vietnamese task-oriented intent classification",
                "- Features: TF-IDF word n-grams + char n-grams",
                "- Classifier: Logistic Regression",
                f"- Accuracy: {bundle.metrics.get('accuracy')}",
                f"- Macro F1: {bundle.metrics.get('macro_f1')}",
                f"- Dataset source: {bundle.metrics.get('dataset', {}).get('source')}",
            ]
        ),
        encoding="utf-8",
    )
    return target


def load_nlp_bundle(target_dir: Path | None = None) -> NLPBundle | None:
    settings = get_settings()
    target = (target_dir or settings.artifacts_dir) / NLP_ARTIFACT_NAME
    if not target.exists():
        return None
    payload = joblib.load(target)
    return NLPBundle(
        pipeline=payload["pipeline"],
        labels=list(payload["labels"]),
        metrics=dict(payload.get("metrics", {})),
        version=str(payload.get("version", NLP_VERSION)),
    )


def ensure_nlp_bundle() -> NLPBundle:
    bundle = load_nlp_bundle()
    if bundle is not None:
        return bundle
    bundle = train_nlp_bundle()
    if get_settings().auto_bootstrap_models:
        save_nlp_bundle(bundle)
    return bundle
