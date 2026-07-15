"""Upload the 20-file MP3 demo dataset to Supabase Storage.

Usage:
    python scripts/upload_media_dataset.py --dataset-dir ./media-dataset

The dataset directory must contain:
    music/01-calm-morning-pad.mp3
    ...
    podcast/10-name-the-feeling.mp3
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import httpx

from app.config import settings
from app.seed import MEDIA_SEED


def _object_path(source_url: str) -> str:
    bucket = settings.SUPABASE_MEDIA_BUCKET
    marker = f"/{bucket}/"
    if marker in source_url:
        return source_url.split(marker, 1)[1]
    prefix = f"supabase://{bucket}/"
    if source_url.startswith(prefix):
        return source_url[len(prefix):]
    raise ValueError(f"Cannot derive object path from source_url={source_url!r}")


def expected_paths() -> list[str]:
    return [_object_path(item["source_url"]) for item in MEDIA_SEED]


def validate_dataset(dataset_dir: Path) -> list[tuple[Path, str]]:
    files: list[tuple[Path, str]] = []
    missing: list[str] = []
    for object_path in expected_paths():
        local_path = dataset_dir / object_path
        if not local_path.is_file():
            missing.append(object_path)
            continue
        files.append((local_path, object_path))
    if missing:
        joined = "\n".join(f"- {path}" for path in missing)
        raise SystemExit(f"Missing dataset MP3 files:\n{joined}")
    return files


def upload_file(client: httpx.Client, local_path: Path, object_path: str) -> None:
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        raise SystemExit("Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY before upload.")

    bucket = settings.SUPABASE_MEDIA_BUCKET
    url = (
        f"{settings.SUPABASE_URL.rstrip('/')}/storage/v1/object/"
        f"{bucket}/{object_path}"
    )
    headers = {
        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
        "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
        "Content-Type": "audio/mpeg",
        "x-upsert": "true",
    }
    with local_path.open("rb") as handle:
        response = client.post(url, headers=headers, content=handle)
    response.raise_for_status()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-dir", type=Path, required=True)
    args = parser.parse_args()

    os.environ.setdefault("SUPABASE_MEDIA_BUCKET", settings.SUPABASE_MEDIA_BUCKET)
    files = validate_dataset(args.dataset_dir)
    with httpx.Client(timeout=60.0) as client:
        for local_path, object_path in files:
            upload_file(client, local_path, object_path)
            print(f"uploaded {object_path}")
    print(f"Uploaded {len(files)} MP3 files to bucket {settings.SUPABASE_MEDIA_BUCKET}.")


if __name__ == "__main__":
    main()
