"""Check a native PerCom45 fixture against Python-derived reference features.

The native fixture format is intentionally plain JSON so it can be emitted by a
LibXtract-based ESP32/desktop probe without adding a JSON dependency to the
firmware.  It compares only primitives whose implementation details have been
matched. MFCC, spectral flux and spectral bandwidth are deliberately reported,
but never passed as numerically equivalent: their windowing/filter-bank
definitions must be benchmarked per LibXtract build.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from percom_features import FEATURE_NAMES, FEATURE_SCHEMA_VERSION, extract_features

# Exact / bounded-comparison candidates.  The remaining names are reported as
# "benchmark required"; adding them here requires a documented implementation match.
COMPARABLE_FEATURES = (
    "energy",
    "zero_crossing_rate",
    "pause_rate",
    "spectral_centroid",
    "spectral_rolloff",
    "spectral_flatness",
)
BENCHMARK_REQUIRED = (
    "f0",
    "f2",
    "jitter",
    "shimmer",
    "band_energy_ratio",
    "spectral_bandwidth",
    "spectral_flux",
    *(f"mfcc_{index}" for index in range(1, 14)),
    *(f"chroma_{index}" for index in range(1, 13)),
    *(f"spectral_contrast_{index}" for index in range(1, 8)),
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", type=Path)
    parser.add_argument("native_fixture", type=Path)
    parser.add_argument("--relative-tolerance", type=float, default=0.15)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    reference = extract_features(args.audio).values
    fixture = json.loads(args.native_fixture.read_text(encoding="utf-8"))
    if fixture.get("schema_version") != FEATURE_SCHEMA_VERSION:
        raise ValueError("Native fixture uses a different feature schema version")
    native_names = tuple(fixture.get("feature_names", FEATURE_NAMES))
    native_values = np.asarray(fixture.get("features", []), dtype=np.float64)
    if native_names != FEATURE_NAMES or native_values.shape != (len(FEATURE_NAMES),):
        raise ValueError("Native fixture must contain 45 PerCom values in schema order")

    index = {name: position for position, name in enumerate(FEATURE_NAMES)}
    comparisons = []
    for name in COMPARABLE_FEATURES:
        position = index[name]
        python_value = float(reference[position])
        native_value = float(native_values[position])
        relative_error = abs(native_value - python_value) / max(abs(python_value), 1e-8)
        comparisons.append(
            {
                "name": name,
                "python": python_value,
                "native": native_value,
                "relative_error": relative_error,
                "passes": relative_error <= args.relative_tolerance,
            }
        )
    result = {
        "schema_version": FEATURE_SCHEMA_VERSION,
        "comparable_features": comparisons,
        "all_comparable_features_pass": all(item["passes"] for item in comparisons),
        "benchmark_required": list(BENCHMARK_REQUIRED),
        "note": (
            "This does not claim numerical equivalence for MFCC, flux, or "
            "bandwidth. A LibXtract implementation must supply a fixture "
            "before this check can establish supported primitive parity."
        ),
    }
    serialized = json.dumps(result, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized + "\n", encoding="utf-8")
    print(serialized)
    if not result["all_comparable_features_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
