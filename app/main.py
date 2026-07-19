"""
EmotiCare AIoT — Cloud API Server

Internet Service for the EmotiCare AIoT Edge Device.
Handles emotion session sync, recommendations, media, conversations,
feedback and TFT reports.

Run with:
    uvicorn app.main:app --reload
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routers import (
    conversations,
    device_config,
    devices,
    emotion_sessions,
    feedback,
    media,
    recommendations,
    reports,
    statistics,
    stt,
)

# ─── FastAPI app ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="EmotiCare AIoT — Cloud API",
    description=(
        "Cloud backend for **EmotiCare AIoT — Intelligent Emotional Companion**.\n\n"
        "Provides REST API for the Edge Device (ESP32-S3) to:\n"
        "- Pair and authenticate devices\n"
        "- Sync emotion sessions (idempotent)\n"
        "- Request activity and media recommendations\n"
        "- Trigger AI-assisted conversations with safety filter\n"
        "- Submit feedback for personalisation\n"
        "- Retrieve TFT-optimised emotion reports\n\n"
        "**Authentication:** Pass `X-Device-Token: <token>` header "
        "or `Authorization: Bearer <token>` on all endpoints except `/api/devices/pair`.\n\n"
        "**Quick start:** Use `/api/devices/pair` with `pairing_code = DEMO-001` to get a token, "
        "then use that token for all other endpoints."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

dataset_dir = Path(__file__).resolve().parent.parent / "media-dataset"
dataset_dir.mkdir(exist_ok=True)
app.mount("/media", StaticFiles(directory=dataset_dir), name="local-media")


@app.get("/", tags=["Root"])
def root():
    return {
        "name": "EmotiCare AIoT Cloud API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
        "quick_start": {
            "step_1": "POST /api/devices/pair  with body: {pairing_code: 'DEMO-001', device_name: 'My Device'}",
            "step_2": "Copy device_token from response",
            "step_3": "Use X-Device-Token header on all other endpoints",
        },
        "endpoints": {
            "pair_device":            "POST /api/devices/pair",
            "heartbeat":              "POST /api/devices/heartbeat",
            "sync_sessions":          "POST /api/emotion-sessions/sync",
            "list_sessions":          "GET  /api/emotion-sessions",
            "request_recommendation": "POST /api/recommendations/request",
            "list_recommendations":   "GET  /api/recommendations",
            "media_categories":       "GET  /api/media/categories",
            "media_recommendations":  "POST /api/media/recommendations",
            "media_history":          "GET  /api/media/history",
            "conversation":           "POST /api/conversations/respond",
            "stt":                    "POST /api/stt/transcribe",
            "feedback_activity":      "POST /api/feedback/activity",
            "feedback_media":         "POST /api/feedback/media",
            "tft_summary":            "GET  /api/reports/tft-summary",
            "statistic_day":          "GET  /api/statistics/day",
            "statistic_week":         "GET  /api/statistics/week",
            "statistic_month":        "GET  /api/statistics/month",
            "generate_report":        "POST /api/reports/generate",
            "list_reports":           "GET  /api/reports",
            "device_config":          "GET  /api/device-config",
        },
    }


# ─── Routers ──────────────────────────────────────────────────────────────────
app.include_router(devices.router)
app.include_router(emotion_sessions.router)
app.include_router(recommendations.router)
app.include_router(media.router)
app.include_router(conversations.router)
app.include_router(stt.router)
app.include_router(feedback.router)
app.include_router(reports.router)
app.include_router(statistics.router)
app.include_router(device_config.router)
