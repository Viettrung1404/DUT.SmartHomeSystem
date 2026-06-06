from __future__ import annotations

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.environment_training import train_environment_bundle


def main() -> None:
    bundle = train_environment_bundle()
    print(json.dumps(bundle.metrics, indent=2))


if __name__ == "__main__":
    main()
