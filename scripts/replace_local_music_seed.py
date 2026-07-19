"""Remove local music seed rows only, preserving all podcasts.

Run with ``--apply`` immediately before ``python -m app.seed`` after the
local music catalog has been replaced.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.config import settings


def _headers() -> dict[str, str]:
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        raise SystemExit("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required.")
    key = settings.SUPABASE_SERVICE_ROLE_KEY
    return {"Authorization": f"Bearer {key}", "apikey": key}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    base_url = settings.SUPABASE_URL.rstrip("/")
    filters = {"media_type": "eq.song", "source_url": "like./media/music/*", "select": "id,title,source_url"}
    with httpx.Client(timeout=60.0) as client:
        current = client.get(f"{base_url}/rest/v1/media_items", headers=_headers(), params=filters)
        current.raise_for_status()
        rows = current.json()
        print(f"Local music rows selected: {len(rows)}")
        for row in rows:
            print(f"- {row['title']} ({row['source_url']})")
        if not args.apply:
            print("Dry run only. Re-run with --apply to delete these music rows.")
            return
        deleted = client.delete(
            f"{base_url}/rest/v1/media_items",
            headers=_headers(),
            params={"media_type": "eq.song", "source_url": "like./media/music/*"},
        )
        deleted.raise_for_status()
    print("Deleted local music rows only; podcast rows were not touched.")


if __name__ == "__main__":
    main()
