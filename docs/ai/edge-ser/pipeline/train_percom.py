"""Train PerCom-style Random Forest and TFLite MLP models on RAVDESS-8."""

from __future__ import annotations

import argparse
import json
import random
import time
from collections import Counter
from pathlib import Path

import emlearn
import numpy as np
import tensorflow as tf
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split

from percom_features import FEATURE_NAMES, FEATURE_SCHEMA_VERSION, extract_features
from train_ravdess import EMOTIONS, parse_ravdess_file


def load_or_extract_dataset(
    dataset_root: Path, cache_path: Path
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if cache_path.exists():
        cached = np.load(cache_path, allow_pickle=False)
        return cached["features"], cached["labels"], cached["actors"]

    files = sorted(dataset_root.rglob("03-01-*.wav"))
    if len(files) < 1_000:
        raise ValueError(f"Expected 1,000+ RAVDESS speech files, found {len(files)}")
    rows, labels, actors = [], [], []
    # TensorFlow can configure NumPy to raise on harmless float32 underflow.
    # Librosa's STFT matrix multiplication legitimately produces values below
    # that threshold for quiet frames, so only suppress that condition here.
    error_settings = np.seterr(under="ignore")
    try:
        for index, path in enumerate(files, start=1):
            label, actor = parse_ravdess_file(path)
            rows.append(extract_features(path).values)
            labels.append(label)
            actors.append(actor)
            if index % 100 == 0:
                print(f"Extracted {index}/{len(files)} PerCom vectors")
    finally:
        np.seterr(**error_settings)
    features = np.stack(rows).astype(np.float32)
    label_values = np.asarray(labels)
    actor_values = np.asarray(actors)
    np.savez_compressed(
        cache_path, features=features, labels=label_values, actors=actor_values
    )
    return features, label_values, actor_values


def build_mlp(feature_count: int, class_count: int) -> tf.keras.Model:
    inputs = tf.keras.Input(shape=(feature_count,), name="percom_features")
    x = tf.keras.layers.Normalization(name="normalize")(inputs)
    x = tf.keras.layers.Dense(96, activation="relu")(x)
    x = tf.keras.layers.Dropout(0.20)(x)
    x = tf.keras.layers.Dense(48, activation="relu")(x)
    outputs = tf.keras.layers.Dense(class_count, activation="softmax", name="emotion")(x)
    return tf.keras.Model(inputs, outputs)


def evaluate_predictions(
    labels: np.ndarray, predictions: np.ndarray, class_labels: list[str]
) -> dict[str, object]:
    return {
        "accuracy": float(accuracy_score(labels, predictions)),
        "macro_f1": float(f1_score(labels, predictions, average="macro")),
        "classification_report": classification_report(
            labels,
            predictions,
            labels=list(range(len(class_labels))),
            target_names=class_labels,
            output_dict=True,
            zero_division=0,
        ),
    }


def tflite_predict(model_path: Path, features: np.ndarray) -> np.ndarray:
    interpreter = tf.lite.Interpreter(model_path=str(model_path))
    interpreter.allocate_tensors()
    input_info = interpreter.get_input_details()[0]
    output_info = interpreter.get_output_details()[0]
    predictions = []
    for feature_row in features:
        interpreter.set_tensor(
            input_info["index"], feature_row.reshape(1, -1).astype(np.float32)
        )
        interpreter.invoke()
        predictions.append(int(np.argmax(interpreter.get_tensor(output_info["index"])[0])))
    return np.asarray(predictions, dtype=np.int32)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("../models"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--test-size", type=float, default=0.20)
    parser.add_argument("--stress-test-actors", nargs="+", default=["21", "22", "23", "24"])
    args = parser.parse_args()

    random.seed(args.seed)
    np.random.seed(args.seed)
    tf.keras.utils.set_random_seed(args.seed)
    args.output.mkdir(parents=True, exist_ok=True)
    features, labels, actors = load_or_extract_dataset(
        args.dataset, args.output / "percom45_features.npz"
    )
    if features.shape[1] != len(FEATURE_NAMES):
        raise RuntimeError("Unexpected PerCom feature count")

    class_labels = sorted(set(labels))
    label_to_index = {label: index for index, label in enumerate(class_labels)}
    encoded = np.asarray([label_to_index[label] for label in labels], dtype=np.int32)
    x_train, x_test, y_train, y_test = train_test_split(
        features,
        encoded,
        test_size=args.test_size,
        random_state=args.seed,
        stratify=encoded,
    )

    started = time.perf_counter()
    random_forest = RandomForestClassifier(
        n_estimators=30,
        max_depth=10,
        class_weight="balanced",
        n_jobs=-1,
        random_state=args.seed,
    )
    random_forest.fit(x_train, y_train)
    rf_latency_ms = (time.perf_counter() - started) * 1000 / len(x_test)
    rf_metrics = evaluate_predictions(y_test, random_forest.predict(x_test), class_labels)
    if rf_metrics["accuracy"] <= 0.50:
        raise RuntimeError("PerCom Random Forest did not exceed 50% test accuracy")

    rf_header_path = args.output / "percom_rf.h"
    # Float thresholds preserve the Python feature scale. The default int16
    # export truncates low-amplitude features (RMS, ZCR, shimmer) and would
    # not be parity-compatible with the measured sklearn model.
    emlearn.convert(random_forest, method="inline", dtype="float").save(
        file=str(rf_header_path), name="percom_rf"
    )

    mlp = build_mlp(features.shape[1], len(class_labels))
    mlp.get_layer("normalize").adapt(x_train)
    mlp.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(),
        metrics=["accuracy"],
    )
    mlp.fit(
        x_train,
        y_train,
        validation_split=0.15,
        epochs=200,
        batch_size=32,
        verbose=2,
        callbacks=[
            tf.keras.callbacks.EarlyStopping(
                monitor="val_accuracy", patience=20, restore_best_weights=True
            )
        ],
    )
    keras_predictions = np.argmax(mlp.predict(x_test, verbose=0), axis=1)
    keras_metrics = evaluate_predictions(y_test, keras_predictions, class_labels)
    if keras_metrics["accuracy"] <= 0.50:
        raise RuntimeError("PerCom MLP did not exceed 50% test accuracy")

    tflite_path = args.output / "percom_mlp.tflite"
    converter = tf.lite.TFLiteConverter.from_keras_model(mlp)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_path.write_bytes(converter.convert())
    tflite_metrics = evaluate_predictions(
        y_test, tflite_predict(tflite_path, x_test), class_labels
    )
    if tflite_metrics["accuracy"] <= 0.50:
        raise RuntimeError("PerCom TFLite MLP did not exceed 50% test accuracy")

    actor_mask = np.isin(actors, args.stress_test_actors)
    actor_rf = RandomForestClassifier(
        n_estimators=30,
        max_depth=10,
        class_weight="balanced",
        n_jobs=-1,
        random_state=args.seed,
    )
    actor_rf.fit(features[~actor_mask], encoded[~actor_mask])
    actor_metrics = evaluate_predictions(
        encoded[actor_mask], actor_rf.predict(features[actor_mask]), class_labels
    )

    metadata = {
        "schema_version": FEATURE_SCHEMA_VERSION,
        "feature_names": FEATURE_NAMES,
        "feature_count": len(FEATURE_NAMES),
        "dataset": "RAVDESS audio-only speech",
        "sample_count": int(features.shape[0]),
        "labels": class_labels,
        "label_taxonomy_note": (
            "RAVDESS calm is retained as requested; this is an 8-label "
            "adaptation of the PerCom paper's 7-label taxonomy."
        ),
        "primary_evaluation": {
            "protocol": f"stratified random holdout {args.test_size:.0%}, seed {args.seed}",
            "test_samples": int(x_test.shape[0]),
        },
        "random_forest": {
            **rf_metrics,
            "mean_inference_latency_ms": rf_latency_ms,
            "header": rf_header_path.name,
            "header_size_bytes": rf_header_path.stat().st_size,
        },
        "keras_mlp": keras_metrics,
        "tflite_mlp": {**tflite_metrics, "model": tflite_path.name, "model_size_bytes": tflite_path.stat().st_size},
        "actor_held_out_stress_test": {
            "actors": args.stress_test_actors,
            **actor_metrics,
        },
        "class_distribution": dict(Counter(labels.tolist())),
    }
    (args.output / "percom45.metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
