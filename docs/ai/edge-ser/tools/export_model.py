"""Export the trained float Random Forest as the deployed C header."""

from __future__ import annotations

import argparse

import emlearn
import joblib


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("model")
    parser.add_argument("--output", required=True)
    parser.add_argument("--name", default="rf")
    parser.add_argument("--dtype", choices=("float",), default="float")
    args = parser.parse_args()
    emlearn.convert(joblib.load(args.model), method="inline", dtype="float").save(
        file=args.output, name=args.name
    )


if __name__ == "__main__":
    main()
