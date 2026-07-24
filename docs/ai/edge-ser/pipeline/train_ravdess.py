"""Train and export an actor-independent RAVDESS SER model as TFLite."""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from pathlib import Path

import numpy as np
import tensorflow as tf
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

from features import extract_features

EMOTIONS = {
    "01": "neutral",
    "02": "calm",
    "03": "happy",
    "04": "sad",
    "05": "angry",
    "06": "fearful",
    "07": "disgust",
    "08": "surprised",
}


def parse_ravdess_file(path: Path) -> tuple[str, str]:
    """Read emotion and actor from RAVDESS's seven-part filename."""
    parts = path.stem.split("-")
    if len(parts) != 7 or parts[0] != "03" or parts[1] != "01":
        raise ValueError(f"Not an audio-only RAVDESS speech file: {path.name}")
    return EMOTIONS[parts[2]], parts[6]


def collect_dataset(dataset_root: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    files = sorted(dataset_root.rglob("03-01-*.wav"))
    if len(files) < 1_000:
        raise ValueError(
            f"Expected about 1,440 RAVDESS speech files; found {len(files)} in {dataset_root}"
        )

    feature_rows: list[np.ndarray] = []
    labels: list[str] = []
    actors: list[str] = []
    for index, path in enumerate(files, start=1):
        label, actor = parse_ravdess_file(path)
        feature_rows.append(extract_features(path).values)
        labels.append(label)
        actors.append(actor)
        if index % 100 == 0:
            print(f"Extracted {index}/{len(files)} files")

    return (
        np.stack(feature_rows).astype(np.float32),
        np.asarray(labels),
        np.asarray(actors),
    )


def load_or_extract_dataset(
    dataset_root: Path, cache_path: Path
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if cache_path.exists():
        cached = np.load(cache_path, allow_pickle=False)
        print(f"Loaded cached features from {cache_path}")
        return cached["features"], cached["labels"], cached["actors"]

    features, labels, actors = collect_dataset(dataset_root)
    np.savez_compressed(
        cache_path, features=features, labels=labels, actors=actors
    )
    return features, labels, actors


def build_model(feature_count: int, class_count: int) -> tf.keras.Model:
    inputs = tf.keras.Input(shape=(feature_count,), name="acoustic_features")
    x = tf.keras.layers.Normalization(name="normalize")(inputs)
    x = tf.keras.layers.Dense(256, activation="relu")(x)
    x = tf.keras.layers.Dropout(0.25)(x)
    x = tf.keras.layers.Dense(128, activation="relu")(x)
    outputs = tf.keras.layers.Dense(class_count, activation="softmax", name="emotion")(x)
    return tf.keras.Model(inputs=inputs, outputs=outputs)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("../models"))
    parser.add_argument(
        "--evaluation",
        choices=["stratified", "actor"],
        default="stratified",
        help="Use a stratified random test split, or hold out entire actors.",
    )
    parser.add_argument(
        "--test-actors",
        nargs="+",
        default=["21", "22", "23", "24"],
        help="Actor IDs held out entirely when --evaluation=actor.",
    )
    parser.add_argument("--test-size", type=float, default=0.20)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    random.seed(args.seed)
    np.random.seed(args.seed)
    tf.keras.utils.set_random_seed(args.seed)
    args.output.mkdir(parents=True, exist_ok=True)

    cache_path = args.output / "ravdess_features.npz"
    features, labels, actors = load_or_extract_dataset(args.dataset, cache_path)
    class_labels = sorted(set(labels))
    label_to_index = {label: index for index, label in enumerate(class_labels)}
    encoded_labels = np.asarray([label_to_index[label] for label in labels], dtype=np.int32)

    if args.evaluation == "actor":
        test_mask = np.isin(actors, args.test_actors)
        if not test_mask.any() or test_mask.all():
            raise ValueError("The held-out actor split is empty or includes all data.")
        x_train, x_test = features[~test_mask], features[test_mask]
        y_train, y_test = encoded_labels[~test_mask], encoded_labels[test_mask]
        evaluation_description = f"actor-held-out: {', '.join(args.test_actors)}"
    else:
        x_train, x_test, y_train, y_test = train_test_split(
            features,
            encoded_labels,
            test_size=args.test_size,
            random_state=args.seed,
            stratify=encoded_labels,
        )
        evaluation_description = (
            f"stratified random holdout: {args.test_size:.0%}, seed {args.seed}"
        )

    model = build_model(features.shape[1], len(class_labels))
    normalizer = model.get_layer("normalize")
    normalizer.adapt(x_train)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(),
        metrics=["accuracy"],
    )
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_accuracy", patience=20, restore_best_weights=True
        )
    ]
    model.fit(
        x_train,
        y_train,
        validation_split=0.15,
        epochs=200,
        batch_size=32,
        verbose=2,
        callbacks=callbacks,
    )

    probabilities = model.predict(x_test, verbose=0)
    predictions = np.argmax(probabilities, axis=1)
    accuracy = float(accuracy_score(y_test, predictions))
    report = classification_report(
        y_test,
        predictions,
        labels=list(range(len(class_labels))),
        target_names=class_labels,
        output_dict=True,
        zero_division=0,
    )
    print(f"{evaluation_description} test accuracy: {accuracy:.4f}")
    if accuracy <= 0.50:
        raise RuntimeError(
            "Accuracy target not reached (>50%). Adjust features/model and rerun; "
            "do not publish this model."
        )

    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_path = args.output / "ravdess_ser.tflite"
    tflite_path.write_bytes(converter.convert())

    interpreter = tf.lite.Interpreter(model_path=str(tflite_path))
    interpreter.allocate_tensors()
    input_info = interpreter.get_input_details()[0]
    output_info = interpreter.get_output_details()[0]
    tflite_predictions = []
    for row in x_test:
        interpreter.set_tensor(input_info["index"], row.reshape(1, -1).astype(np.float32))
        interpreter.invoke()
        tflite_predictions.append(
            int(np.argmax(interpreter.get_tensor(output_info["index"])[0]))
        )
    tflite_accuracy = float(accuracy_score(y_test, tflite_predictions))
    print(f"TFLite test accuracy: {tflite_accuracy:.4f}")
    if tflite_accuracy <= 0.50:
        raise RuntimeError(
            "TFLite accuracy target not reached (>50%); do not publish this model."
        )

    metadata = {
        "dataset": "RAVDESS audio-only speech",
        "sample_count": int(features.shape[0]),
        "feature_count": int(features.shape[1]),
        "sample_rate_hz": 22050,
        "labels": class_labels,
        "evaluation_protocol": evaluation_description,
        "test_actors": args.test_actors if args.evaluation == "actor" else None,
        "test_samples": int(x_test.shape[0]),
        "test_accuracy": accuracy,
        "tflite_test_accuracy": tflite_accuracy,
        "class_distribution": dict(Counter(labels.tolist())),
        "classification_report": report,
        "tflite_model": tflite_path.name,
    }
    (args.output / "ravdess_ser.metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
