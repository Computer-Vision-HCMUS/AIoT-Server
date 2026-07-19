"""Download a small local Creative Commons/Public Domain music dataset.

Internet Archive is used here because its public search endpoint exposes
licence metadata and downloadable audio files reliably in this environment.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from urllib.parse import quote

import httpx


ROOT = Path(__file__).resolve().parent.parent
DATASET = ROOT / "media-dataset"
MUSIC_DIR = DATASET / "music"
CATALOG = DATASET / "music_catalog.json"
ATTRIBUTION = DATASET / "music_attribution.json"
SEARCH_URL = "https://archive.org/advancedsearch.php"
METADATA_URL = "https://archive.org/metadata"
CATEGORIES = ["relax", "focus", "sleep", "happy", "sad_support", "anger_release", "energy_recover"]
MAX_SOURCE_BYTES = 16 * 1024 * 1024
TARGET_COUNT = 40


def _safe_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:55] or "track"


def _candidates(client: httpx.Client) -> list[dict]:
    response = client.get(
        SEARCH_URL,
        params={
            "q": 'collection:opensource_audio AND mediatype:audio AND licenseurl:*creativecommons* AND subject:music AND format:"VBR MP3"',
            "fl[]": ["identifier", "title", "creator", "licenseurl"], "rows": 100, "output": "json",
        },
    )
    response.raise_for_status()
    pages = response.json().get("response", {}).get("docs", [])
    items = []
    for page in pages:
        title = str(page.get("title", ""))
        if any(word in title.lower() for word in ("episode", "radio show", "podcast", "interview", "sermon")):
            continue
        identifier = str(page.get("identifier", ""))
        if not identifier:
            continue
        details = client.get(f"{METADATA_URL}/{quote(identifier, safe='')}")
        details.raise_for_status()
        files = details.json().get("files", [])
        audio = next((entry for entry in files if str(entry.get("name", "")).lower().endswith(".mp3") and entry.get("format") in {"VBR MP3", "128Kbps MP3", "64Kbps MP3", "MP3"}), None)
        if not audio:
            continue
        filename = str(audio["name"])
        items.append({
            "title": title or identifier, "identifier": identifier,
            "url": f"https://archive.org/download/{quote(identifier, safe='')}/{quote(filename)}",
            "license": page.get("licenseurl", "Creative Commons"),
            "artist": page.get("creator", "Internet Archive contributor"),
        })
        if len(items) == 50:
            break
    return items


def main() -> None:
    MUSIC_DIR.mkdir(parents=True, exist_ok=True)
    with httpx.Client(timeout=30.0, follow_redirects=True, headers={"User-Agent": "EmotiCare-AIoT-Dataset/1.0 (local research project)"}) as client:
        candidates = _candidates(client)
        if len(candidates) < TARGET_COUNT:
            raise SystemExit(f"Internet Archive did not return {TARGET_COUNT} compatible music files.")
        catalog, attribution = [], []
        for item in candidates:
            if len(catalog) == TARGET_COUNT:
                break
            index = len(catalog) + 1
            filename = f"{index:02d}-commons-{_safe_name(item['title'])}.mp3"
            original = MUSIC_DIR / f"{index:02d}-{_safe_name(str(item['identifier']))}.source"
            destination = MUSIC_DIR / filename
            if destination.is_file() and destination.stat().st_size > 100_000:
                category = CATEGORIES[(index - 1) % len(CATEGORIES)]
                catalog.append({
                    "media_type": "song", "title": item["title"], "creator": str(item["artist"]),
                    "category": category, "duration_sec": 90, "source_url": f"/media/music/{filename}",
                    "dataset": "Internet Archive Creative Commons Music Dataset", "license_note": item["license"],
                })
                attribution.append({**item, "local_file": filename})
                print(f"Reusing downloaded track: {item['title']}")
                continue
            try:
                with client.stream("GET", item["url"]) as response:
                    response.raise_for_status()
                    with original.open("wb") as handle:
                        written = 0
                        for chunk in response.iter_bytes():
                            remaining = MAX_SOURCE_BYTES - written
                            if remaining <= 0:
                                break
                            handle.write(chunk[:remaining])
                            written += len(chunk[:remaining])
                subprocess.run(
                    ["ffmpeg", "-y", "-i", str(original), "-t", "90", "-vn", "-codec:a", "libmp3lame", "-b:a", "128k", str(destination)],
                    check=True,
                    capture_output=True,
                )
            except (httpx.HTTPError, subprocess.CalledProcessError) as error:
                print(f"Skipping unavailable audio: {item['title']} ({error})")
                destination.unlink(missing_ok=True)
                continue
            finally:
                try:
                    original.unlink(missing_ok=True)
                except PermissionError:
                    # Antivirus/indexing can briefly hold a downloaded source on Windows.
                    # It is not referenced by the catalog and is safe to leave behind.
                    print(f"Keeping temporary source still in use: {original.name}")
            category = CATEGORIES[(index - 1) % len(CATEGORIES)]
            catalog.append({
                "media_type": "song", "title": item["title"], "creator": str(item["artist"]),
                "category": category, "duration_sec": 90, "source_url": f"/media/music/{filename}",
                "dataset": "Internet Archive Creative Commons Music Dataset", "license_note": item["license"],
            })
            attribution.append({**item, "local_file": filename})
    if len(catalog) < TARGET_COUNT:
        raise SystemExit(f"Only {len(catalog)} usable music files were downloaded.")
    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    ATTRIBUTION.write_text(json.dumps(attribution, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Downloaded {len(catalog)} licensed music tracks to {MUSIC_DIR}")


if __name__ == "__main__":
    main()
