from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.environment_training import save_environment_bundle, train_environment_bundle


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the environment forecast bundle")
    parser.add_argument("--csv", type=Path, default=None, help="Optional path to a house/reference environment log CSV")
    args = parser.parse_args()

    bundle = train_environment_bundle(dataset_path=args.csv)
    target = save_environment_bundle(bundle)
    print(f"Saved environment artifact to {target}")
    print(bundle.metrics)


if __name__ == "__main__":
    main()
