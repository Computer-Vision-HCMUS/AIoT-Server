# Supabase Deployment Guide

This project uses Supabase for PostgreSQL and Storage, while the FastAPI API is
deployed on Vercel for Gemini, Whisper, recommendation, chat, and statistics.

## Architecture

```text
ESP32 / Swagger / Postman
        |
        v
Vercel FastAPI Function
        |
        +-- Gemini API
        +-- Whisper model on Python runtime
        +-- Supabase PostgreSQL
        +-- Supabase Storage bucket: media-demo
```

Supabase Edge Functions are not used for the main API. This keeps the university
demo simple: one FastAPI API on Vercel plus managed database/storage.

## Supabase Setup

1. Create a Supabase project.
2. Create a public or signed-access Storage bucket named `media-demo`.
3. Prepare dataset files under a local folder such as `./media-dataset`:

```text
music/01-calm-morning-pad.mp3
...
music/10-small-energy-rise.mp3
podcast/01-breathing-478.mp3
...
podcast/10-name-the-feeling.mp3
```

4. Set `.env`:

```env
DATABASE_URL=postgresql://postgres.<project-ref>:<db-password>@<pooler-host>:5432/postgres?sslmode=require
MIGRATION_DATABASE_URL=postgresql://postgres:<db-password>@db.<project-ref>.supabase.co:5432/postgres?sslmode=require
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<server-only-key>
SUPABASE_MEDIA_BUCKET=media-demo
```

5. Upload MP3 files, run migrations, and seed:

```bash
python scripts/upload_media_dataset.py --dataset-dir ./media-dataset
alembic upgrade head
python -m app.seed
```

Expected migration head:

```text
e003_drop_global_client_unique (head)
```

## Vercel FastAPI Hosting

Deploy this repository to Vercel. Vercel detects the `app` object exported from
`app/main.py`; `vercel.json` only configures the function duration.

Runtime requirements:

- Python runtime on Vercel
- environment variables from `.env.example`
- enough memory/time for `faster-whisper` model loading

## Demo Checklist

1. Open `/docs`.
2. Pair or seed a demo device.
3. Sync emotion sessions.
4. Call recommendation, chat, STT, media, and statistics endpoints.
5. Verify Supabase tables contain new rows.
6. Verify `media_items.source_url` points to `.mp3` objects in `media-demo`.
