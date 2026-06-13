# AIoT-Server

FastAPI backend for SmartClock and VisionDriveAI devices.

## Docker Setup (recommended)

```bash
docker compose up --build
```

The API is available at `http://localhost:8000`, Swagger docs at
`http://localhost:8000/docs`, PostgreSQL at `localhost:5432`, and pgAdmin at
`http://localhost:5050`.

To load mock data after the stack is running:

```bash
docker compose exec api python -m app.seed
```

## Local Setup (SQLite fallback or host Python)

```bash
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

API docs are available at `http://localhost:8000/docs`.

This project targets PostgreSQL for shared development, demos, and deployment.
SQLite remains supported as a lightweight local fallback by setting
`DATABASE_URL=sqlite:///./aiot.db`.

## Core Flow

1. Register a device with `POST /devices/register`.
2. Store the returned `device_token` on the ESP32 device.
3. Send authenticated requests with `Authorization: Bearer <device_token>` or `X-Device-Token`.

## Database

Schema changes are managed by Alembic migrations in `alembic/versions`.
Do not create production tables from application startup code.

For database architecture, migration, SQLite, PostgreSQL, Supabase, and pgAdmin notes, read `docs/database/DATABASE.md`.
For mock data and Postman requests, read `docs/api/POSTMAN_TESTING.md`.
