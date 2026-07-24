"""Compatibility facade for the current RAVDESS TFLite inference pipeline.

The old 45-feature Random Forest extractor is intentionally retired because its
training scaler and model source were unavailable. New callers should import
from ``edge-ser/pipeline`` directly; these functions preserve a simple API for
existing experiments.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import tensorflow as tf

PIPELINE_DIR = Path(__file__).resolve().parents[2] / "pipeline"
if str(PIPELINE_DIR) not in sys.path:
    sys.path.insert(0, str(PIPELINE_DIR))

from features import extract_features


def extract_features_for_prediction(file_path: str | Path) -> np.ndarray:
    """Return the model-ready 210-element float32 feature vector."""
    return extract_features(Path(file_path)).values


def predict_emotion(
    file_path: str | Path,
    model_path: str | Path,
    metadata_path: str | Path,
) -> dict[str, object]:
    """Decode MP3/WAV input, run TFLite, and return label/confidence/top-3."""
    features = extract_features_for_prediction(file_path)
    metadata = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    interpreter = tf.lite.Interpreter(model_path=str(model_path))
    interpreter.allocate_tensors()

    input_info = interpreter.get_input_details()[0]
    output_info = interpreter.get_output_details()[0]
    interpreter.set_tensor(
        input_info["index"], features.reshape(1, -1).astype(np.float32)
    )
    interpreter.invoke()
    probabilities = interpreter.get_tensor(output_info["index"])[0]
    ordering = np.argsort(probabilities)[::-1]
    labels = metadata["labels"]

    return {
        "emotion_label": labels[int(ordering[0])],
        "confidence_score": float(probabilities[ordering[0]]),
        "top_k_predictions": [
            {"label": labels[int(index)], "confidence": float(probabilities[index])}
            for index in ordering[:3]
        ],
    }
