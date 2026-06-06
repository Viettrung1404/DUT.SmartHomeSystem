from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
import inspect
import pickle
import re
import time

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score

from app.core.settings import get_settings
from app.datasets.smarthome_corpus import TEST_SPLIT, TRAIN_SPLIT, VALIDATION_SPLIT, load_jsonl
from app.services.nlp_training import _build_classifier
from app.services.text_normalizer import normalize_text, strip_accents


TOKEN_PATTERN = re.compile(r"[0-9A-Za-zÀ-ỹà-ỹđĐ_]+", re.UNICODE)


@dataclass(frozen=True)
class ScenarioDataset:
    name: str
    train_records: list[dict]
    val_records: list[dict]
    test_records: list[dict]
    label_list: list[str]
    slot_labels: list[str]
    restoration_coverage: float


@dataclass(frozen=True)
class IntentArtifacts:
    classifier: object
    labels: list[str]
    model_size_mb: float


@dataclass(frozen=True)
class SlotBaselineArtifacts:
    phrase_lexicon: dict[tuple[str, ...], str]
    max_phrase_len: int
    model_size_mb: float


def _safe_tokenize_surface(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_PATTERN.findall(text)]


def _aligned_surface_tokens(record: dict) -> list[str]:
    normalized_tokens = [str(token) for token in record["tokens"]]
    surface_tokens = _safe_tokenize_surface(str(record["text"]))
    if len(surface_tokens) != len(normalized_tokens):
        return normalized_tokens
    for surface_token, normalized_token in zip(surface_tokens, normalized_tokens, strict=True):
        if normalize_text(surface_token) != normalized_token:
            return normalized_tokens
    return surface_tokens


def build_restoration_lexicon(records: Sequence[dict]) -> dict[str, str]:
    counts: dict[str, Counter[str]] = {}
    for record in records:
        normalized_tokens = [str(token) for token in record["tokens"]]
        surface_tokens = _aligned_surface_tokens(record)
        for normalized_token, surface_token in zip(normalized_tokens, surface_tokens, strict=True):
            if normalized_token == normalize_text(surface_token):
                counts.setdefault(normalized_token, Counter())[surface_token] += 1
    return {
        normalized_token: max(token_counts.items(), key=lambda item: (item[1], len(item[0]), item[0]))[0]
        for normalized_token, token_counts in counts.items()
    }


def restore_tokens(tokens: Sequence[str], lexicon: dict[str, str]) -> list[str]:
    return [lexicon.get(str(token), str(token)) for token in tokens]


def build_phrase_lexicon(records: Sequence[dict]) -> dict[tuple[str, ...], str]:
    phrase_counts: dict[tuple[str, ...], Counter[str]] = {}
    for record in records:
        tokens = [str(token) for token in record["tokens"]]
        slot_tags = [str(tag) for tag in record["slot_tags"]]
        idx = 0
        while idx < len(tokens):
            tag = slot_tags[idx]
            if not tag.startswith("B-"):
                idx += 1
                continue
            label = tag[2:]
            start = idx
            idx += 1
            while idx < len(tokens) and slot_tags[idx] == f"I-{label}":
                idx += 1
            span_tokens = tuple(tokens[start:idx])
            phrase_counts.setdefault(span_tokens, Counter())[label] += 1
    return {
        phrase: max(label_counts.items(), key=lambda item: item[1])[0]
        for phrase, label_counts in phrase_counts.items()
    }


def _slot_label_list(records: Sequence[dict]) -> list[str]:
    labels = sorted({str(tag) for record in records for tag in record["slot_tags"]})
    if "O" not in labels:
        labels.insert(0, "O")
    return labels


def load_scenario_dataset() -> ScenarioDataset:
    settings = get_settings()
    data_dir = settings.nlp_data_dir
    train_records = load_jsonl(data_dir / f"{TRAIN_SPLIT}.jsonl")
    val_records = load_jsonl(data_dir / f"{VALIDATION_SPLIT}.jsonl")
    test_records = load_jsonl(data_dir / f"{TEST_SPLIT}.jsonl")
    restoration_lexicon = build_restoration_lexicon(train_records)
    vocabulary = {str(token) for record in test_records for token in record["tokens"]}
    restored = sum(1 for token in vocabulary if token in restoration_lexicon)
    return ScenarioDataset(
        name="smarthome_vi_v1",
        train_records=train_records,
        val_records=val_records,
        test_records=test_records,
        label_list=sorted({str(record["intent"]) for record in train_records}),
        slot_labels=_slot_label_list(train_records + val_records + test_records),
        restoration_coverage=restored / max(1, len(vocabulary)),
    )


def records_for_view(records: Sequence[dict], scenario: str, lexicon: dict[str, str]) -> list[dict]:
    result: list[dict] = []
    for record in records:
        normalized_tokens = [str(token) for token in record["tokens"]]
        if scenario == "clean":
            view_tokens = _aligned_surface_tokens(record)
        elif scenario == "no_diacritic":
            view_tokens = normalized_tokens
        elif scenario == "restored":
            view_tokens = restore_tokens(normalized_tokens, lexicon)
        else:
            raise ValueError(f"Unsupported scenario: {scenario}")
        result.append(
            {
                "id": record["id"],
                "intent": record["intent"],
                "tokens": view_tokens,
                "slot_tags": [str(tag) for tag in record["slot_tags"]],
                "text": " ".join(view_tokens),
                "language_variant": record.get("language_variant", "unknown"),
            }
        )
    return result


def train_baseline_intent_model(train_records: Sequence[dict]) -> IntentArtifacts:
    texts = [normalize_text(" ".join(_aligned_surface_tokens(record))) for record in train_records]
    labels = [str(record["intent"]) for record in train_records]
    classifier = _build_classifier()
    classifier.fit(texts, labels)
    payload = {"pipeline": classifier, "labels": sorted(set(labels))}
    model_size_mb = len(pickle.dumps(payload)) / (1024 * 1024)
    return IntentArtifacts(classifier=classifier, labels=sorted(set(labels)), model_size_mb=round(model_size_mb, 3))


def evaluate_baseline_intent(
    artifacts: IntentArtifacts,
    records: Sequence[dict],
    scenario: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    texts = [normalize_text(record["text"]) for record in records]
    gold = [str(record["intent"]) for record in records]
    start = time.perf_counter()
    preds = list(artifacts.classifier.predict(texts))
    elapsed_ms = ((time.perf_counter() - start) * 1000.0) / max(1, len(texts))
    summary = pd.DataFrame(
        [
            {
                "model": "baseline_tfidf_lr",
                "scenario": scenario,
                "accuracy": round(float(accuracy_score(gold, preds)), 4),
                "macro_f1": round(float(f1_score(gold, preds, average="macro")), 4),
                "latency_ms_per_sample": round(float(elapsed_ms), 4),
                "model_size_mb": artifacts.model_size_mb,
            }
        ]
    )
    detailed = pd.DataFrame(classification_report(gold, preds, output_dict=True)).transpose().reset_index(names="label")
    return summary, detailed


def train_slot_rule_baseline(train_records: Sequence[dict]) -> SlotBaselineArtifacts:
    phrase_lexicon = build_phrase_lexicon(train_records)
    max_phrase_len = max((len(phrase) for phrase in phrase_lexicon), default=1)
    payload = {"phrase_lexicon": phrase_lexicon, "max_phrase_len": max_phrase_len}
    model_size_mb = len(pickle.dumps(payload)) / (1024 * 1024)
    return SlotBaselineArtifacts(
        phrase_lexicon=phrase_lexicon,
        max_phrase_len=max_phrase_len,
        model_size_mb=round(model_size_mb, 3),
    )


def predict_slot_tags_rule(tokens: Sequence[str], artifacts: SlotBaselineArtifacts) -> list[str]:
    normalized_tokens = [normalize_text(token) for token in tokens]
    tags = ["O"] * len(normalized_tokens)
    idx = 0
    while idx < len(normalized_tokens):
        matched = False
        for span_len in range(min(artifacts.max_phrase_len, len(normalized_tokens) - idx), 0, -1):
            phrase = tuple(normalized_tokens[idx : idx + span_len])
            label = artifacts.phrase_lexicon.get(phrase)
            if label is None:
                continue
            tags[idx] = f"B-{label}"
            for tag_idx in range(idx + 1, idx + span_len):
                tags[tag_idx] = f"I-{label}"
            idx += span_len
            matched = True
            break
        if not matched:
            idx += 1
    return tags


def slot_exact_match(gold_sequences: Sequence[Sequence[str]], pred_sequences: Sequence[Sequence[str]]) -> float:
    matches = sum(1 for gold, pred in zip(gold_sequences, pred_sequences, strict=True) if list(gold) == list(pred))
    return matches / max(1, len(gold_sequences))


def evaluate_slot_rule_baseline(
    artifacts: SlotBaselineArtifacts,
    records: Sequence[dict],
    scenario: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    try:
        from seqeval.metrics import classification_report as seqeval_report
        from seqeval.metrics import f1_score as seqeval_f1_score
    except ImportError as exc:
        raise RuntimeError("seqeval is required for slot evaluation") from exc

    gold_sequences = [list(record["slot_tags"]) for record in records]
    start = time.perf_counter()
    pred_sequences = [predict_slot_tags_rule(record["tokens"], artifacts) for record in records]
    elapsed_ms = ((time.perf_counter() - start) * 1000.0) / max(1, len(records))
    summary = pd.DataFrame(
        [
            {
                "model": "baseline_rule_slots",
                "scenario": scenario,
                "slot_f1": round(float(seqeval_f1_score(gold_sequences, pred_sequences)), 4),
                "exact_match": round(float(slot_exact_match(gold_sequences, pred_sequences)), 4),
                "latency_ms_per_sample": round(float(elapsed_ms), 4),
                "model_size_mb": artifacts.model_size_mb,
            }
        ]
    )
    detailed = pd.DataFrame(seqeval_report(gold_sequences, pred_sequences, output_dict=True)).transpose().reset_index(names="label")
    return summary, detailed


def intent_confusion(records: Sequence[dict], preds: Sequence[str], labels: Sequence[str]) -> pd.DataFrame:
    gold = [str(record["intent"]) for record in records]
    matrix = confusion_matrix(gold, preds, labels=list(labels))
    return pd.DataFrame(matrix, index=labels, columns=labels)


def train_phobert_intent(
    train_records: Sequence[dict],
    val_records: Sequence[dict],
    *,
    model_name: str = "vinai/phobert-base",
    output_dir: Path | None = None,
    epochs: int = 2,
    batch_size: int = 8,
):
    from datasets import Dataset
    import evaluate
    from transformers import (
        AutoModelForSequenceClassification,
        AutoTokenizer,
        DataCollatorWithPadding,
        Trainer,
        TrainingArguments,
    )

    label_list = sorted({str(record["intent"]) for record in train_records})
    label_to_id = {label: idx for idx, label in enumerate(label_list)}
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    def convert(records: Sequence[dict]) -> Dataset:
        return Dataset.from_dict(
            {
                "text": [str(record["text"]) for record in records],
                "label": [label_to_id[str(record["intent"])] for record in records],
            }
        )

    train_ds = convert(train_records)
    val_ds = convert(val_records)

    def tokenize(batch):
        return tokenizer(batch["text"], truncation=True, max_length=96)

    train_ds = train_ds.map(tokenize, batched=True)
    val_ds = val_ds.map(tokenize, batched=True)

    metric_accuracy = evaluate.load("accuracy")
    metric_f1 = evaluate.load("f1")

    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        preds = np.argmax(logits, axis=-1)
        accuracy = metric_accuracy.compute(predictions=preds, references=labels)["accuracy"]
        macro_f1 = metric_f1.compute(predictions=preds, references=labels, average="macro")["f1"]
        return {"accuracy": accuracy, "macro_f1": macro_f1}

    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=len(label_list),
        id2label={idx: label for label, idx in label_to_id.items()},
        label2id=label_to_id,
    )
    args_kwargs = {
        "output_dir": str(output_dir or (get_settings().artifacts_dir / "phobert_intent_tmp")),
        "per_device_train_batch_size": batch_size,
        "per_device_eval_batch_size": batch_size,
        "learning_rate": 2e-5,
        "num_train_epochs": epochs,
        "weight_decay": 0.01,
        "save_strategy": "no",
        "logging_strategy": "epoch",
        "report_to": [],
        "seed": get_settings().random_seed,
    }
    strategy_param = "eval_strategy" if "eval_strategy" in inspect.signature(TrainingArguments.__init__).parameters else "evaluation_strategy"
    args_kwargs[strategy_param] = "epoch"
    training_args = TrainingArguments(**args_kwargs)
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        processing_class=tokenizer,
        data_collator=DataCollatorWithPadding(tokenizer=tokenizer),
        compute_metrics=compute_metrics,
    )
    trainer.train()
    return {
        "trainer": trainer,
        "tokenizer": tokenizer,
        "label_list": label_list,
        "param_size_mb": round(model_parameter_size_mb(model), 3),
    }


def evaluate_phobert_intent(artifacts: dict, records: Sequence[dict], scenario: str) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    from datasets import Dataset

    trainer = artifacts["trainer"]
    tokenizer = artifacts["tokenizer"]

    eval_ds = Dataset.from_dict(
        {
            "text": [str(record["text"]) for record in records],
            "label": [artifacts["label_list"].index(str(record["intent"])) for record in records],
        }
    )
    eval_ds = eval_ds.map(lambda batch: tokenizer(batch["text"], truncation=True, max_length=96), batched=True)
    start = time.perf_counter()
    prediction = trainer.predict(eval_ds)
    elapsed_ms = ((time.perf_counter() - start) * 1000.0) / max(1, len(records))
    preds_idx = np.argmax(prediction.predictions, axis=-1)
    preds = [artifacts["label_list"][int(idx)] for idx in preds_idx]
    gold = [str(record["intent"]) for record in records]
    summary = pd.DataFrame(
        [
            {
                "model": "phobert_intent",
                "scenario": scenario,
                "accuracy": round(float(accuracy_score(gold, preds)), 4),
                "macro_f1": round(float(f1_score(gold, preds, average="macro")), 4),
                "latency_ms_per_sample": round(float(elapsed_ms), 4),
                "model_size_mb": artifacts["param_size_mb"],
            }
        ]
    )
    detailed = pd.DataFrame(classification_report(gold, preds, output_dict=True)).transpose().reset_index(names="label")
    return summary, detailed, preds


def train_phobert_slot(
    train_records: Sequence[dict],
    val_records: Sequence[dict],
    *,
    model_name: str = "vinai/phobert-base",
    output_dir: Path | None = None,
    epochs: int = 2,
    batch_size: int = 8,
):
    from datasets import Dataset
    import evaluate
    from transformers import (
        AutoModelForTokenClassification,
        AutoTokenizer,
        DataCollatorForTokenClassification,
        Trainer,
        TrainingArguments,
    )

    label_list = _slot_label_list(train_records + val_records)
    label_to_id = {label: idx for idx, label in enumerate(label_list)}
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    def convert(records: Sequence[dict]) -> Dataset:
        return Dataset.from_dict(
            {
                "tokens": [list(record["tokens"]) for record in records],
                "tags": [[label_to_id[str(tag)] for tag in record["slot_tags"]] for record in records],
            }
        )

    train_ds = convert(train_records)
    val_ds = convert(val_records)

    def encode_tokens_and_labels(tokens: Sequence[str], tag_ids: Sequence[int], max_length: int = 96) -> dict[str, list[int]]:
        input_ids = [tokenizer.cls_token_id]
        labels = [-100]
        for token, tag_id in zip(tokens, tag_ids, strict=True):
            piece_ids = tokenizer.convert_tokens_to_ids(tokenizer.tokenize(token))
            if not piece_ids:
                piece_ids = [tokenizer.unk_token_id]
            remaining = max_length - len(input_ids) - 1
            if remaining <= 0:
                break
            piece_ids = piece_ids[:remaining]
            input_ids.extend(piece_ids)
            labels.append(int(tag_id))
            labels.extend([-100] * (len(piece_ids) - 1))
        input_ids.append(tokenizer.sep_token_id)
        labels.append(-100)
        attention_mask = [1] * len(input_ids)
        return {"input_ids": input_ids, "attention_mask": attention_mask, "labels": labels}

    def tokenize_and_align(batch):
        rows = [encode_tokens_and_labels(tokens, tags) for tokens, tags in zip(batch["tokens"], batch["tags"], strict=True)]
        return {
            "input_ids": [row["input_ids"] for row in rows],
            "attention_mask": [row["attention_mask"] for row in rows],
            "labels": [row["labels"] for row in rows],
        }

    train_ds = train_ds.map(tokenize_and_align, batched=True)
    val_ds = val_ds.map(tokenize_and_align, batched=True)
    seqeval = evaluate.load("seqeval")

    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        preds = np.argmax(logits, axis=-1)
        pred_labels: list[list[str]] = []
        gold_labels: list[list[str]] = []
        for pred_row, gold_row in zip(preds, labels, strict=True):
            current_pred: list[str] = []
            current_gold: list[str] = []
            for pred_idx, gold_idx in zip(pred_row, gold_row, strict=True):
                if gold_idx == -100:
                    continue
                current_pred.append(label_list[int(pred_idx)])
                current_gold.append(label_list[int(gold_idx)])
            pred_labels.append(current_pred)
            gold_labels.append(current_gold)
        metrics = seqeval.compute(predictions=pred_labels, references=gold_labels)
        return {
            "slot_f1": metrics["overall_f1"],
            "slot_precision": metrics["overall_precision"],
            "slot_recall": metrics["overall_recall"],
        }

    model = AutoModelForTokenClassification.from_pretrained(
        model_name,
        num_labels=len(label_list),
        id2label={idx: label for label, idx in label_to_id.items()},
        label2id=label_to_id,
    )
    args_kwargs = {
        "output_dir": str(output_dir or (get_settings().artifacts_dir / "phobert_slot_tmp")),
        "per_device_train_batch_size": batch_size,
        "per_device_eval_batch_size": batch_size,
        "learning_rate": 2e-5,
        "num_train_epochs": epochs,
        "weight_decay": 0.01,
        "save_strategy": "no",
        "logging_strategy": "epoch",
        "report_to": [],
        "seed": get_settings().random_seed,
    }
    strategy_param = "eval_strategy" if "eval_strategy" in inspect.signature(TrainingArguments.__init__).parameters else "evaluation_strategy"
    args_kwargs[strategy_param] = "epoch"
    training_args = TrainingArguments(**args_kwargs)
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        processing_class=tokenizer,
        data_collator=DataCollatorForTokenClassification(tokenizer=tokenizer),
        compute_metrics=compute_metrics,
    )
    trainer.train()
    return {
        "trainer": trainer,
        "tokenizer": tokenizer,
        "label_list": label_list,
        "param_size_mb": round(model_parameter_size_mb(model), 3),
    }


def evaluate_phobert_slot(artifacts: dict, records: Sequence[dict], scenario: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    from datasets import Dataset
    from seqeval.metrics import classification_report as seqeval_report
    from seqeval.metrics import f1_score as seqeval_f1_score

    trainer = artifacts["trainer"]
    tokenizer = artifacts["tokenizer"]
    label_list = artifacts["label_list"]
    label_to_id = {label: idx for idx, label in enumerate(label_list)}

    ds = Dataset.from_dict(
        {
            "tokens": [list(record["tokens"]) for record in records],
            "tags": [[label_to_id[str(tag)] for tag in record["slot_tags"]] for record in records],
        }
    )

    def encode_tokens_and_labels(tokens: Sequence[str], tag_ids: Sequence[int], max_length: int = 96) -> dict[str, list[int]]:
        input_ids = [tokenizer.cls_token_id]
        labels = [-100]
        for token, tag_id in zip(tokens, tag_ids, strict=True):
            piece_ids = tokenizer.convert_tokens_to_ids(tokenizer.tokenize(token))
            if not piece_ids:
                piece_ids = [tokenizer.unk_token_id]
            remaining = max_length - len(input_ids) - 1
            if remaining <= 0:
                break
            piece_ids = piece_ids[:remaining]
            input_ids.extend(piece_ids)
            labels.append(int(tag_id))
            labels.extend([-100] * (len(piece_ids) - 1))
        input_ids.append(tokenizer.sep_token_id)
        labels.append(-100)
        attention_mask = [1] * len(input_ids)
        return {"input_ids": input_ids, "attention_mask": attention_mask, "labels": labels}

    def tokenize_and_align(batch):
        rows = [encode_tokens_and_labels(tokens, tags) for tokens, tags in zip(batch["tokens"], batch["tags"], strict=True)]
        return {
            "input_ids": [row["input_ids"] for row in rows],
            "attention_mask": [row["attention_mask"] for row in rows],
            "labels": [row["labels"] for row in rows],
        }

    ds = ds.map(tokenize_and_align, batched=True)
    start = time.perf_counter()
    prediction = trainer.predict(ds)
    elapsed_ms = ((time.perf_counter() - start) * 1000.0) / max(1, len(records))
    pred_ids = np.argmax(prediction.predictions, axis=-1)
    gold_sequences: list[list[str]] = []
    pred_sequences: list[list[str]] = []
    for pred_row, gold_row in zip(pred_ids, prediction.label_ids, strict=True):
        current_gold: list[str] = []
        current_pred: list[str] = []
        for pred_idx, gold_idx in zip(pred_row, gold_row, strict=True):
            if gold_idx == -100:
                continue
            current_gold.append(label_list[int(gold_idx)])
            current_pred.append(label_list[int(pred_idx)])
        gold_sequences.append(current_gold)
        pred_sequences.append(current_pred)
    summary = pd.DataFrame(
        [
            {
                "model": "phobert_slot",
                "scenario": scenario,
                "slot_f1": round(float(seqeval_f1_score(gold_sequences, pred_sequences)), 4),
                "exact_match": round(float(slot_exact_match(gold_sequences, pred_sequences)), 4),
                "latency_ms_per_sample": round(float(elapsed_ms), 4),
                "model_size_mb": artifacts["param_size_mb"],
            }
        ]
    )
    detailed = pd.DataFrame(seqeval_report(gold_sequences, pred_sequences, output_dict=True)).transpose().reset_index(names="label")
    return summary, detailed


def model_parameter_size_mb(model) -> float:
    total_bytes = 0
    for parameter in model.parameters():
        total_bytes += parameter.numel() * parameter.element_size()
    return total_bytes / (1024 * 1024)


def tokenizer_fragmentation(tokenizer, texts: Sequence[str]) -> pd.DataFrame:
    rows = []
    for text in texts:
        pieces = tokenizer.tokenize(text)
        rows.append(
            {
                "text": text,
                "pieces": pieces,
                "piece_count": len(pieces),
                "unk_count": sum(1 for piece in pieces if piece == "<unk>"),
            }
        )
    return pd.DataFrame(rows)


def evaluate_restoration_quality(records: Sequence[dict], lexicon: dict[str, str]) -> pd.DataFrame:
    rows = []
    correct = 0
    total = 0
    for record in records:
        gold_tokens = _aligned_surface_tokens(record)
        restored = restore_tokens(record["tokens"], lexicon)
        for normalized_token, gold_token, restored_token in zip(record["tokens"], gold_tokens, restored, strict=True):
            total += 1
            if strip_accents(gold_token).lower() != str(normalized_token):
                continue
            if gold_token == restored_token:
                correct += 1
    rows.append(
        {
            "restoration_token_accuracy": round(correct / max(1, total), 4),
            "covered_vocabulary_ratio": round(
                sum(1 for token in {str(token) for record in records for token in record["tokens"]} if token in lexicon)
                / max(1, len({str(token) for record in records for token in record["tokens"]})),
                4,
            ),
        }
    )
    return pd.DataFrame(rows)
