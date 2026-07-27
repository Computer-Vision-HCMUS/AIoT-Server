"""Train and export the only deployed classifier: PerCom45 Random Forest."""

from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split

EMOTIONS = ("neutral", "calm", "happy", "sad", "angry", "fearful", "disgust", "surprised")
FEATURE_SCHEMA_VERSION = "ravdess-mfcc45-v1"
FEATURE_NAMES = (
    *(f"mfcc_{index}" for index in range(1, 14)),
    *(f"mfcc_std_{index}" for index in range(1, 14)),
    *(f"chroma_{index}" for index in range(1, 13)),
    "rms", "zero_crossing_rate", "spectral_centroid", "spectral_bandwidth",
    "spectral_rolloff", "spectral_flatness", "spectral_contrast",
)
LOGGER = logging.getLogger("ravdess45")


def parse_ravdess_file(path: Path) -> tuple[str, str]:
    parts = path.stem.split("-")
    if len(parts) != 7 or parts[0] != "03" or parts[1] != "01":
        raise ValueError(f"Not a RAVDESS speech filename: {path.name}")
    return EMOTIONS[int(parts[2]) - 1], parts[6]


def extract_native(extractor: Path, path: Path) -> np.ndarray:
    """Extract with the exact C++ code deployed beside classify.h."""
    with tempfile.TemporaryDirectory(prefix="aiot-ser-") as temporary_directory:
        output = Path(temporary_directory) / "features.json"
        subprocess.run(
            [str(extractor), "extract", str(path), str(output)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
        values = np.asarray(json.loads(output.read_text(encoding="utf-8"))["features"], dtype=np.float32)
    if values.shape != (len(FEATURE_NAMES),) or not np.isfinite(values).all():
        raise ValueError(f"Native extractor did not produce 45 finite features for {path}")
    return values


def load_dataset(dataset: Path, cache: Path, workers: int, extractor: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if cache.exists():
        LOGGER.info("Nạp cache đặc trưng: %s", cache)
        saved = np.load(cache, allow_pickle=False)
        return saved["features"], saved["labels"], saved["actors"]
    files = sorted(dataset.rglob("03-01-*.wav"))
    if len(files) != 1440:
        raise ValueError(f"Expected 1,440 RAVDESS speech WAV files; found {len(files)}")
    def extract_row(path: Path) -> tuple[np.ndarray, str, str]:
        label, actor = parse_ravdess_file(path)
        return extract_native(extractor, path), label, actor

    rows, labels, actors = [], [], []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        for index, (values, label, actor) in enumerate(executor.map(extract_row, files), start=1):
            rows.append(values)
            labels.append(label)
            actors.append(actor)
            if index % 100 == 0:
                LOGGER.info("Đã trích xuất %d/%d file", index, len(files))
    features = np.stack(rows).astype(np.float32)
    label_values, actor_values = np.asarray(labels), np.asarray(actors)
    np.savez_compressed(cache, features=features, labels=label_values, actors=actor_values)
    LOGGER.info("Đã lưu cache %s với shape=%s", cache, features.shape)
    return features, label_values, actor_values


def metrics(expected: np.ndarray, predicted: np.ndarray, labels: list[str]) -> dict[str, object]:
    return {
        "accuracy": float(accuracy_score(expected, predicted)),
        "macro_f1": float(f1_score(expected, predicted, average="macro")),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--cache", type=Path, default=Path("build/ravdess_mfcc45_features.npz"))
    parser.add_argument("--header", type=Path, default=Path("include/classify.h"))
    parser.add_argument("--report", type=Path, default=Path("reports/train-metrics.json"))
    parser.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 1))
    parser.add_argument(
        "--extractor", type=Path, default=Path("build/ser_pipeline.exe"),
        help="Compiled native pipeline. Its extractor is used for both training and deployment.",
    )
    parser.add_argument(
        "--ffmpeg", type=Path,
        help="Optional ffmpeg executable; its directory is passed to the native extractor.",
    )
    parser.add_argument("--log-file", type=Path, default=Path("reports/train.log"))
    parser.add_argument(
        "--reference-exporter",
        type=Path,
        default=Path("tools/export_model.py"),
        help="Script emlearn được lấy từ repository tham khảo.",
    )
    args = parser.parse_args()
    args.log_file.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler(args.log_file, encoding="utf-8")],
    )
    args.cache.parent.mkdir(parents=True, exist_ok=True)
    args.header.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    if not args.extractor.is_file():
        raise FileNotFoundError(f"Build the native extractor first: {args.extractor}")
    if args.ffmpeg:
        if not args.ffmpeg.is_file():
            raise FileNotFoundError(f"ffmpeg executable not found: {args.ffmpeg}")
        os.environ["PATH"] = str(args.ffmpeg.parent) + os.pathsep + os.environ["PATH"]
    elif shutil.which("ffmpeg") is None:
        raise FileNotFoundError("ffmpeg is required; pass --ffmpeg <path-to-ffmpeg.exe>")
    features, labels, actors = load_dataset(args.dataset, args.cache, args.workers, args.extractor)
    LOGGER.info("Bắt đầu train Extra Trees với %d mẫu và %d đặc trưng", features.shape[0], features.shape[1])
    class_labels = sorted(set(labels))
    label_to_index = {label: index for index, label in enumerate(class_labels)}
    encoded = np.asarray([label_to_index[label] for label in labels], dtype=np.int32)
    x_train, x_test, y_train, y_test = train_test_split(features, encoded, test_size=0.20, random_state=42, stratify=encoded)
    model = ExtraTreesClassifier(n_estimators=100, max_depth=None, class_weight="balanced", n_jobs=-1, random_state=42).fit(x_train, y_train)
    primary = metrics(y_test, model.predict(x_test), class_labels)
    LOGGER.info("Holdout accuracy=%.4f macro_f1=%.4f", primary["accuracy"], primary["macro_f1"])
    held_out = np.isin(actors, ["21", "22", "23", "24"])
    actor_model = ExtraTreesClassifier(n_estimators=100, max_depth=None, class_weight="balanced", n_jobs=-1, random_state=42).fit(features[~held_out], encoded[~held_out])
    actor_test = metrics(encoded[held_out], actor_model.predict(features[held_out]), class_labels)
    LOGGER.info("Actor-held-out accuracy=%.4f macro_f1=%.4f", actor_test["accuracy"], actor_test["macro_f1"])
    model_path = args.cache.parent / "ExtraTreesClassifier.joblib"
    joblib.dump(model, model_path)
    LOGGER.info("Đã lưu model trung gian: %s", model_path)
    subprocess.run(
        [
            sys.executable,
            str(args.reference_exporter),
            str(model_path),
            "--output",
            str(args.header),
            "--name",
            "rf",
            "--dtype",
            "float",
        ],
        check=True,
    )
    LOGGER.info("Đã export classifier.h bằng %s", args.reference_exporter)
    report = {
        "schema_version": FEATURE_SCHEMA_VERSION,
        "dataset": "RAVDESS audio-only speech",
        "sample_count": int(features.shape[0]),
        "feature_count": len(FEATURE_NAMES),
        "feature_names": FEATURE_NAMES,
        "labels": class_labels,
        "classifier": {"type": "ExtraTreesClassifier", "trees": 100, "max_depth": None, "class_weight": "balanced", "seed": 42, "exporter": "tools/export_model.py + emlearn float"},
        "primary_evaluation": {"protocol": "stratified 80/20 holdout, seed 42", **primary},
        "actor_held_out_evaluation": {"actors": ["21", "22", "23", "24"], **actor_test},
        "class_distribution": dict(Counter(labels.tolist())),
    }
    args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    LOGGER.info("Đã ghi báo cáo: %s", args.report)
    print(json.dumps({"header": str(args.header), "report": str(args.report), **primary}, indent=2))


if __name__ == "__main__":
    main()
