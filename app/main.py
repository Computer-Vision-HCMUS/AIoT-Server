"""
AIoT Backend Server — entry point.

Starts a FastAPI application that serves:
  - SmartClock (ESP32-S3): Pomodoro, Sleep, Seminar, Flappy Bird
  - VisionDriveAI (ESP32-CAM + IMU): Trip tracking, distraction detection

Run with:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

from app.routers import dashboard, devices, health, smartclock, visiondrive

# ─── FastAPI app ─────────────────────────────────────────────────────────────
app = FastAPI(
    title="AIoT Backend Server",
    description=(
        "Backend server for **SmartDesk Buddy** (SmartClock + VisionDriveAI).\n\n"
        "Receives data from ESP32 devices over WiFi, stores session logs and "
        "time-series sensor data, and provides REST API for devices and the web dashboard."
    ),
    version="0.1.0",
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


@app.get("/", tags=["Root"])
def root():
    return {
        "name": "AIoT Backend Server",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "postman_guide": "docs/api/POSTMAN_TESTING.md",
        "demo_tokens": {
            "smartclock": "dev-smartclock-token",
            "visiondrive": "dev-visiondrive-token",
        },
    }


# ─── Routers ──────────────────────────────────────────────────────────────────
app.include_router(health.router)
app.include_router(devices.router)
app.include_router(smartclock.router)
app.include_router(dashboard.router)
app.include_router(visiondrive.router)
