"""Run the native audio -> RAVDESS-MFCC45 -> Random Forest pipeline."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", type=Path)
    parser.add_argument("--binary", type=Path, default=ROOT / "build" / "ser_pipeline.exe")
    parser.add_argument("--features", type=Path, default=ROOT / "build" / "features.json")
    args = parser.parse_args()

    args.features.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([str(args.binary), "extract", str(args.audio), str(args.features)], check=True)
    subprocess.run([str(args.binary), "classify", str(args.features)], check=True)
    print(json.dumps({"feature_file": str(args.features), "schema": "ravdess-mfcc45-v1"}))


if __name__ == "__main__":
    main()
