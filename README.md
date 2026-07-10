# AIoT-Server

FastAPI backend for **EmotiCare AIoT** Internet Service.

The server follows `docs/Spectification/EmotiCareAIoT/05_Internet Service.md`:

- Pair and authenticate Edge devices.
- Sync emotion sessions from Edge AI.
- Return TFT-ready recommendation, media, conversation, and report payloads.
- Persist data in PostgreSQL with SQLAlchemy models and Alembic migrations.

## Docker setup

```bash
docker compose up --build
```

The API is available at:

```text
http://localhost:8000
http://localhost:8000/docs
```

PostgreSQL is available at `localhost:5432`, and pgAdmin at:

```text
http://localhost:5050
```

Seed demo data:

```bash
docker compose exec api python -m app.seed
```

## Local setup

```bash
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
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
