from __future__ import annotations

import argparse
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.settings import get_settings
from app.experiments.phobert_benchmark import (
    build_restoration_lexicon,
    load_scenario_dataset,
    records_for_view,
    train_phobert_slot,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Train and save the PhoBERT slot model for hybrid NLU")
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--batch-size", type=int, default=8)
    args = parser.parse_args()

    settings = get_settings()
    dataset = load_scenario_dataset()
    restoration_lexicon = build_restoration_lexicon(dataset.train_records)

    train_view = records_for_view(dataset.train_records, "clean", restoration_lexicon)
    val_view = records_for_view(dataset.val_records, "clean", restoration_lexicon)

    artifacts = train_phobert_slot(
        train_view,
        val_view,
        output_dir=settings.phobert_slot_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
    )
    trainer = artifacts["trainer"]
    tokenizer = artifacts["tokenizer"]

    settings.phobert_slot_dir.mkdir(parents=True, exist_ok=True)
    trainer.save_model(str(settings.phobert_slot_dir))
    tokenizer.save_pretrained(str(settings.phobert_slot_dir))
    (settings.phobert_slot_dir / "slot_metadata.json").write_text(
        json.dumps(
            {
                "label_list": artifacts["label_list"],
                "model_name": "vinai/phobert-base",
                "epochs": args.epochs,
                "batch_size": args.batch_size,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    settings.restoration_lexicon_path.write_text(
        json.dumps(restoration_lexicon, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Saved PhoBERT slot artifact to {settings.phobert_slot_dir}")


if __name__ == "__main__":
    main()
