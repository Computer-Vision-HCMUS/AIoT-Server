"""Train and export the only deployed classifier: PerCom45 Random Forest."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import emlearn
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split

from percom45 import FEATURE_NAMES, FEATURE_SCHEMA_VERSION, extract_features

EMOTIONS = ("neutral", "calm", "happy", "sad", "angry", "fearful", "disgust", "surprised")


def parse_ravdess_file(path: Path) -> tuple[str, str]:
    parts = path.stem.split("-")
    if len(parts) != 7 or parts[0] != "03" or parts[1] != "01":
        raise ValueError(f"Not a RAVDESS speech filename: {path.name}")
    return EMOTIONS[int(parts[2]) - 1], parts[6]


def load_dataset(dataset: Path, cache: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if cache.exists():
        saved = np.load(cache, allow_pickle=False)
        return saved["features"], saved["labels"], saved["actors"]
    files = sorted(dataset.rglob("03-01-*.wav"))
    if len(files) != 1440:
        raise ValueError(f"Expected 1,440 RAVDESS speech WAV files; found {len(files)}")
    rows, labels, actors = [], [], []
    for path in files:
        label, actor = parse_ravdess_file(path)
        rows.append(extract_features(path).values)
        labels.append(label)
        actors.append(actor)
    features = np.stack(rows).astype(np.float32)
    label_values, actor_values = np.asarray(labels), np.asarray(actors)
    np.savez_compressed(cache, features=features, labels=label_values, actors=actor_values)
    return features, label_values, actor_values


def metrics(expected: np.ndarray, predicted: np.ndarray, labels: list[str]) -> dict[str, object]:
    return {
        "accuracy": float(accuracy_score(expected, predicted)),
        "macro_f1": float(f1_score(expected, predicted, average="macro")),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--cache", type=Path, default=Path("build/percom45_features.npz"))
    parser.add_argument("--header", type=Path, default=Path("include/classify.h"))
    parser.add_argument("--report", type=Path, default=Path("reports/train-metrics.json"))
    args = parser.parse_args()
    args.cache.parent.mkdir(parents=True, exist_ok=True)
    args.header.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    features, labels, actors = load_dataset(args.dataset, args.cache)
    class_labels = sorted(set(labels))
    label_to_index = {label: index for index, label in enumerate(class_labels)}
    encoded = np.asarray([label_to_index[label] for label in labels], dtype=np.int32)
    x_train, x_test, y_train, y_test = train_test_split(features, encoded, test_size=0.20, random_state=42, stratify=encoded)
    model = RandomForestClassifier(n_estimators=30, max_depth=10, class_weight="balanced", n_jobs=-1, random_state=42).fit(x_train, y_train)
    primary = metrics(y_test, model.predict(x_test), class_labels)
    held_out = np.isin(actors, ["21", "22", "23", "24"])
    actor_model = RandomForestClassifier(n_estimators=30, max_depth=10, class_weight="balanced", n_jobs=-1, random_state=42).fit(features[~held_out], encoded[~held_out])
    actor_test = metrics(encoded[held_out], actor_model.predict(features[held_out]), class_labels)
    emlearn.convert(model, method="inline", dtype="float").save(file=str(args.header), name="percom_rf")
    report = {
        "schema_version": FEATURE_SCHEMA_VERSION,
        "dataset": "RAVDESS audio-only speech",
        "sample_count": int(features.shape[0]),
        "feature_count": len(FEATURE_NAMES),
        "feature_names": FEATURE_NAMES,
        "labels": class_labels,
        "classifier": {"type": "RandomForestClassifier", "trees": 30, "max_depth": 10, "class_weight": "balanced", "seed": 42},
        "primary_evaluation": {"protocol": "stratified 80/20 holdout, seed 42", **primary},
        "actor_held_out_evaluation": {"actors": ["21", "22", "23", "24"], **actor_test},
        "class_distribution": dict(Counter(labels.tolist())),
    }
    args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"header": str(args.header), "report": str(args.report), **primary}, indent=2))


if __name__ == "__main__":
    main()
