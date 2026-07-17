# AIoT-Server

FastAPI backend for **EmotiCare AIoT** Internet Service.

The server follows `docs/Spectification/EmotiCareAIoT/05_Internet Service.md`:

- Pair and authenticate Edge devices.
- Sync emotion sessions from Edge AI.
- Return TFT-ready recommendation, media, conversation, STT, and statistic payloads.
- Persist data in PostgreSQL with SQLAlchemy models and Alembic migrations.
- Integrate optional Gemini chat/reason generation and Whisper STT.
- Use Vercel for the FastAPI API and Supabase PostgreSQL + Storage for cloud demo data.

## Vercel deployment

Vercel detects the FastAPI `app` exported from `app/main.py`. Deploy this repo as
a Python/FastAPI project, then add the environment variables from `.env.example`
in the Vercel project settings.

Required cloud services:

- Supabase PostgreSQL for `DATABASE_URL`
- Supabase Storage bucket `media-demo` for the 10 music + 10 podcast demo files
- Gemini API key for AI chat/reason generation
- Whisper model setting for STT

```text
https://<your-vercel-project>.vercel.app
https://<your-vercel-project>.vercel.app/docs
```

Run migrations and seed from your machine against Supabase before testing:

```bash
alembic upgrade head
python -m app.seed
```

## Local setup

```bash
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

Local API:

```text
http://localhost:8000
http://localhost:8000/docs
```

Demo token:

```text
demo-emoticare-device-token-local-dev
```

Use it as:

```http
X-Device-Token: demo-emoticare-device-token-local-dev
```

## Core API flow

1. `POST /api/devices/pair`
2. `POST /api/emotion-sessions/sync`
3. `POST /api/recommendations/request`
4. `POST /api/media/recommendations`
5. `POST /api/conversations/respond`
6. `POST /api/feedback/activity` or `POST /api/feedback/media`
7. `GET /api/reports/tft-summary?period=daily`

Useful read/debug endpoints:

- `GET /api/emotion-sessions`
- `GET /api/recommendations`
- `GET /api/media/history`
- `GET /api/reports`

For detailed Postman examples, read `docs/api/POSTMAN_TESTING.md`.

For a browser-based ESP32 interaction simulator and API testing lab, read `docs/api/TESTING_SIMULATOR.md`.

## AI, Supabase, and Vercel setup

Copy `.env.example` to `.env`, then set:

```env
GEMINI_API_KEY=<google-ai-studio-api-key>
GEMINI_MODEL=gemini-2.5-flash
WHISPER_MODEL_SIZE=base
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<service-role-key>
SUPABASE_MEDIA_BUCKET=media-demo
CORS_ORIGINS=https://<your-frontend-domain>,http://localhost:3000,http://localhost:5173
```

New demo endpoints:

- `POST /api/stt/transcribe`
- `POST /api/recommendations/action`
- `POST /api/media/music/recommend`
- `POST /api/media/podcast/recommend`
- `GET /api/statistics/day`
- `GET /api/statistics/week`
- `GET /api/statistics/month`

Deployment, AI, and dataset details:

- `docs/deployment/SUPABASE_DEPLOYMENT.md`
- `docs/ai/cloud/gemini-whisper.md`
- `docs/datasets/MEDIA_DATASET.md`
