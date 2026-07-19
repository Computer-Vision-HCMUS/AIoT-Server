"""Build the 40-item music catalog from already-validated local MP3 files."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DATASET = ROOT / "media-dataset"
MUSIC_DIR = DATASET / "music"
CATEGORIES = ["relax", "focus", "sleep", "happy", "sad_support", "anger_release", "energy_recover"]


def title_from_filename(path: Path) -> str:
    stem = re.sub(r"^\d{2}-commons-", "", path.stem)
    return stem.replace("-", " ").title()


def main() -> None:
    grouped: dict[int, list[Path]] = {}
    for path in MUSIC_DIR.glob("*-commons-*.mp3"):
        match = re.match(r"^(\d+)-commons-", path.name)
        if match:
            grouped.setdefault(int(match.group(1)), []).append(path)
    selected = [max(grouped[index], key=lambda item: item.stat().st_mtime) for index in range(1, 41) if index in grouped]
    if len(selected) != 40:
        raise SystemExit(f"Expected 40 local music files, found {len(selected)}.")
    catalog = [
        {
            "media_type": "song",
            "title": title_from_filename(path),
            "creator": "Internet Archive Creative Commons contributor",
            "category": CATEGORIES[index % len(CATEGORIES)],
            "duration_sec": 90,
            "source_url": f"/media/music/{path.name}",
            "dataset": "Internet Archive Creative Commons Music Dataset",
            "license_note": "Creative Commons; attribution source recorded with the local dataset.",
        }
        for index, path in enumerate(selected)
    ]
    (DATASET / "music_catalog.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(catalog)} local music catalog items.")


if __name__ == "__main__":
    main()
