from __future__ import annotations

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.settings import get_settings
from app.datasets.smarthome_corpus import (
    build_bootstrap_corpus,
    corpus_summary,
    split_records,
    write_jsonl,
)


def main() -> None:
    settings = get_settings()
    records = build_bootstrap_corpus()
    splits = split_records(records)

    write_jsonl(settings.nlp_data_dir / "master.jsonl", records)
    for split_name, split_rows in splits.items():
        write_jsonl(settings.nlp_data_dir / f"{split_name}.jsonl", split_rows)
        bio_rows = [
            {
                "id": row["id"],
                "intent": row["intent"],
                "tokens": row["tokens"],
                "slot_tags": row["slot_tags"],
                "split_group": row["split_group"],
                "language_variant": row["language_variant"],
            }
            for row in split_rows
        ]
        write_jsonl(settings.nlp_data_dir / "bio" / f"{split_name}.jsonl", bio_rows)

    summary = corpus_summary(records)
    (settings.nlp_data_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Wrote NLP corpus to {settings.nlp_data_dir}")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
