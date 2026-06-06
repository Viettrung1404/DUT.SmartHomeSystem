from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.datasets.smarthome_corpus import build_bootstrap_corpus, split_records, write_jsonl
from app.core.settings import get_settings
from app.services.nlp_training import save_nlp_bundle, train_nlp_bundle


def main() -> None:
    settings = get_settings()
    records = build_bootstrap_corpus()
    write_jsonl(settings.nlp_data_dir / "master.jsonl", records)
    for split_name, split_rows in split_records(records).items():
        write_jsonl(settings.nlp_data_dir / f"{split_name}.jsonl", split_rows)
    bundle = train_nlp_bundle()
    target = save_nlp_bundle(bundle)
    print(f"Saved NLP artifact to {target}")
    print(bundle.metrics)


if __name__ == "__main__":
    main()
