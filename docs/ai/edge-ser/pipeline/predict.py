"""Run a RAVDESS-trained TFLite SER model on an MP3/WAV input."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import tensorflow as tf

from features import extract_features


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="MP3/WAV/etc. accepted by ffmpeg/librosa")
    parser.add_argument(
        "--model",
        type=Path,
        default=Path("../models/ravdess_ser.tflite"),
    )
    parser.add_argument(
        "--metadata",
        type=Path,
        default=Path("../models/ravdess_ser.metadata.json"),
    )
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    feature_vector = extract_features(args.input)
    interpreter = tf.lite.Interpreter(model_path=str(args.model))
    interpreter.allocate_tensors()
    input_info = interpreter.get_input_details()[0]
    output_info = interpreter.get_output_details()[0]
    if input_info["shape"][-1] != feature_vector.values.size:
        raise RuntimeError(
            f"Model expects {input_info['shape'][-1]} features, got "
            f"{feature_vector.values.size}"
        )

    started = time.perf_counter()
    interpreter.set_tensor(
        input_info["index"], feature_vector.values.reshape(1, -1).astype(np.float32)
    )
    interpreter.invoke()
    probabilities = interpreter.get_tensor(output_info["index"])[0]
    latency_ms = (time.perf_counter() - started) * 1000
    ordering = np.argsort(probabilities)[::-1]
    labels = metadata["labels"]
    result = {
        "input": str(args.input),
        "emotion_label": labels[int(ordering[0])],
        "confidence_score": float(probabilities[ordering[0]]),
        "top_k_predictions": [
            {"label": labels[int(index)], "confidence": float(probabilities[index])}
            for index in ordering[:3]
        ],
        "sample_rate_hz": feature_vector.sample_rate_hz,
        "duration_seconds": feature_vector.duration_seconds,
        "feature_count": int(feature_vector.values.size),
        "inference_latency_ms": latency_ms,
    }
    serialized = json.dumps(result, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized + "\n", encoding="utf-8")
    print(serialized)


if __name__ == "__main__":
    main()
