"""Build a small local EmotiCare catalog from downloaded FMA and podcast data.

The script copies 14 FMA Small tracks and downloads ten podcast episodes named
in the local Podcast Dataset CSV.  It stores audio under ``media-dataset`` and
writes a JSON catalog whose source URLs are local API paths only.

Run after FMA Small has fully downloaded and been extracted:
    python scripts/build_local_media_catalog.py
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DATASET = ROOT / "media-dataset"
SOURCE = DATASET / "source"
def _copy_music() -> list[dict]:
    catalog = DATASET / "music_catalog.json"
    if not catalog.is_file():
        raise SystemExit("Run scripts/generate_local_music_dataset.py first.")
    with catalog.open(encoding="utf-8-sig") as handle:
        return json.load(handle)


def _copy_podcasts() -> list[dict]:
    catalog = DATASET / "podcast_catalog.json"
    if not catalog.is_file():
        raise SystemExit("Run scripts/generate_local_podcast_dataset.ps1 first.")
    with catalog.open(encoding="utf-8-sig") as handle:
        return json.load(handle)


def main() -> None:
    catalog = _copy_music() + _copy_podcasts()
    with (DATASET / "catalog.json").open("w", encoding="utf-8") as handle:
        json.dump(catalog, handle, ensure_ascii=False, indent=2)
    print(f"Wrote {len(catalog)} local catalog items to {DATASET / 'catalog.json'}")


if __name__ == "__main__":
    main()
