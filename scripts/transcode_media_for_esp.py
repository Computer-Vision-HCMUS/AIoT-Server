"""Create ESP32-friendly copies of the local MP3 media dataset.

The originals are preserved. Output is written under ``media-dataset/esp``
with the same music/podcast directory layout and is served automatically when
present. 22.05 kHz mono MP3 at 64 kbps is a good compromise between quality,
network stability and ESP32 decoding cost.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = ROOT / "media-dataset"
OUTPUT_DIR = DATASET_DIR / "esp"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Rebuild existing output files")
    args = parser.parse_args()

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise SystemExit("ffmpeg is required (already included in the Docker image).")

    sources = [
        path for path in DATASET_DIR.rglob("*.mp3")
        if OUTPUT_DIR not in path.parents
    ]
    for index, source in enumerate(sources, start=1):
        output = OUTPUT_DIR / source.relative_to(DATASET_DIR)
        if output.exists() and not args.force:
            continue
        output.parent.mkdir(parents=True, exist_ok=True)
        print(f"[{index}/{len(sources)}] {source.name}")
        subprocess.run(
            [
                ffmpeg, "-y", "-v", "error", "-i", str(source),
                "-vn", "-ac", "1", "-ar", "22050", "-c:a", "libmp3lame",
                "-b:a", "64k", "-map_metadata", "-1", str(output),
            ],
            check=True,
        )


if __name__ == "__main__":
    main()
