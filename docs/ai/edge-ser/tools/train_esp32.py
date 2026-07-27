"""Export a size-bounded classifier for the standalone ESP32 SER component."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache", type=Path, default=Path("build/ravdess_mfcc45_features.npz"))
    parser.add_argument("--output", type=Path, default=Path("esp32/include/classify.h"))
    parser.add_argument("--trees", type=int, default=12)
    parser.add_argument("--depth", type=int, default=8)
    args = parser.parse_args()

    saved = np.load(args.cache, allow_pickle=False)
    labels = np.unique(saved["labels"])
    encoded = np.searchsorted(labels, saved["labels"])
    model = RandomForestClassifier(
        n_estimators=args.trees,
        max_depth=args.depth,
        class_weight="balanced",
        n_jobs=-1,
        random_state=42,
    ).fit(saved["features"], encoded)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    model_path = args.output.parent / "ser_esp32_model.joblib"
    joblib.dump(model, model_path)
    subprocess.run(
        [sys.executable, "tools/export_model.py", str(model_path), "--output", str(args.output), "--name", "rf", "--dtype", "float"],
        check=True,
    )
    print(f"exported {args.output} ({args.trees} trees, depth {args.depth})")


if __name__ == "__main__":
    main()
