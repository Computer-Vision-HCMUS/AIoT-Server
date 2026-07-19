"""Remove only the legacy EmotiCare demo media from Supabase.

The script is deliberately dry-run by default.  It targets objects declared by
the previous ``MEDIA_SEED`` and rows whose creator is ``EmotiCare Demo``; it
does not delete arbitrary bucket contents.

Usage:
    python scripts/refresh_supabase_media.py --apply
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings


LEGACY_PATHS = [
    *(f"music/{number:02d}-{name}.mp3" for number, name in [
        (1, "calm-morning-pad"), (2, "soft-rain-keys"),
        (3, "low-focus-pulse"), (4, "clean-study-loop"),
        (5, "night-breath-drone"), (6, "light-steps"),
        (7, "warm-smile-beat"), (8, "gentle-hold"),
        (9, "grounding-low-tone"), (10, "small-energy-rise"),
    ]),
    *(f"podcast/{number:02d}-{name}.mp3" for number, name in [
        (1, "breathing-478"), (2, "one-minute-pause"),
        (3, "start-focus"), (4, "prepare-rest"), (5, "keep-good-energy"),
        (6, "with-sadness"), (7, "kind-self-talk"),
        (8, "cool-down-anger"), (9, "energy-recover"),
        (10, "name-the-feeling"),
    ]),
]


def _headers() -> dict[str, str]:
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        raise SystemExit("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required.")
    key = settings.SUPABASE_SERVICE_ROLE_KEY
    return {"Authorization": f"Bearer {key}", "apikey": key}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="perform deletion; otherwise print targets")
    args = parser.parse_args()
    print("Legacy storage objects:")
    print("\n".join(f"- {path}" for path in LEGACY_PATHS))
    print("Legacy database rows: media_items where creator = 'EmotiCare Demo'")
    if not args.apply:
        print("Dry run only. Re-run with --apply after the new local catalog is ready.")
        return

    base_url = settings.SUPABASE_URL.rstrip("/")
    with httpx.Client(timeout=60.0) as client:
        storage = client.request(
            "DELETE",
            f"{base_url}/storage/v1/object/{settings.SUPABASE_MEDIA_BUCKET}",
            headers={**_headers(), "Content-Type": "application/json"},
            json={"prefixes": LEGACY_PATHS},
        )
        storage.raise_for_status()
        database = client.delete(
            f"{base_url}/rest/v1/media_items",
            headers=_headers(),
            params={"creator": "eq.EmotiCare Demo"},
        )
        database.raise_for_status()
    print("Deleted legacy demo objects and metadata rows.")


if __name__ == "__main__":
    main()
