from datetime import datetime, timezone

from app.database import SessionLocal
from app.models.device import Device
from app.models.smartclock import (
    GameScore,
    PomodoroSession,
    PresentationSession,
    SeminarRecording,
    SleepSession,
    StudySession,
)
from app.models.visiondrive import Trip
from app.seed import seed_database


def _register_smartclock(client, device_id="smartclock-test"):
    response = client.post(
        "/devices/register",
        json={"device_id": device_id, "device_type": "smartclock"},
    )
    assert response.status_code == 201
    body = response.json()
    return body["id"], {"Authorization": f"Bearer {body['device_token']}"}


def test_pomodoro_list_and_study_aggregation_use_minutes(client):
    _, headers = _register_smartclock(client)

    first = client.post(
        "/smartclock/pomodoro-sessions",
        headers=headers,
        json={
            "timestamp": "2026-06-01T08:00:00Z",
            "duration": 25,
            "session_type": "study",
        },
    )
    second = client.post(
        "/smartclock/pomodoro-sessions",
        headers=headers,
        json={
            "timestamp": "2026-06-01T08:30:00Z",
            "duration": 5,
            "session_type": "break",
        },
    )
    assert first.status_code == 201
    assert second.status_code == 201

    listed = client.get("/smartclock/pomodoro-sessions", headers=headers)
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [second.json()["id"], first.json()["id"]]

    study = client.post(
        "/smartclock/study-sessions",
        headers=headers,
        json={
            "start_time": "2026-06-01T08:00:00Z",
            "end_time": "2026-06-01T08:35:00Z",
            "status": "completed",
            "pomodoro_session_ids": [first.json()["id"], second.json()["id"]],
        },
    )
    assert study.status_code == 201
    body = study.json()
    assert body["focus_minutes"] == 25
    assert body["break_minutes"] == 5
    assert body["pomodoro_count"] == 1


def test_sleep_sensor_batch_rejects_completed_session(client):
    _, headers = _register_smartclock(client)

    created = client.post(
        "/smartclock/sleep-sessions",
        headers=headers,
        json={"start_time": "2026-06-01T22:00:00Z"},
    )
    assert created.status_code == 201
    session_id = created.json()["id"]

    ended = client.post(
        f"/smartclock/sleep-sessions/{session_id}/end",
        headers=headers,
        json={"end_time": "2026-06-02T06:00:00Z", "sleep_score": 88},
    )
    assert ended.status_code == 200

    batch = client.post(
        f"/smartclock/sleep-sessions/{session_id}/sensor-batches",
        headers=headers,
        json={
            "timestamp": "2026-06-02T01:00:00Z",
            "sound_level": 10,
            "light_level": 2,
        },
    )
    assert batch.status_code == 409


def test_dashboard_presentation_returns_recent_completed_sessions_sorted_ascending(client):
    device_id, headers = _register_smartclock(client)
    starts = [
        "2026-06-01T09:00:00Z",
        "2026-06-02T09:00:00Z",
        "2026-06-03T09:00:00Z",
    ]

    for index, start_time in enumerate(starts):
        created = client.post(
            "/smartclock/presentation-sessions",
            headers=headers,
            json={"start_time": start_time},
        )
        assert created.status_code == 201
        session_id = created.json()["id"]
        ended = client.post(
            f"/smartclock/presentation-sessions/{session_id}/end",
            headers=headers,
            json={
                "end_time": start_time.replace("09:00:00Z", "09:10:00Z"),
                "clarity_score": 70 + index,
                "speed_score": 80,
                "noise_score": 90,
                "confidence_score": 60,
            },
        )
        assert ended.status_code == 200

    response = client.get(f"/dashboard/presentation?device_id={device_id}&limit=2")
    assert response.status_code == 200
    body = response.json()
    assert [item["start_time"] for item in body] == [
        "2026-06-02T09:00:00",
        "2026-06-03T09:00:00",
    ]


def test_seed_database_contains_required_demo_shape():
    seed_database()
    db = SessionLocal()
    try:
        smartclocks = db.query(Device).filter(Device.device_type == "smartclock").count()
        visiondrives = db.query(Device).filter(Device.device_type == "visiondrive").count()

        assert smartclocks >= 2
        assert visiondrives >= 1
        assert db.query(PomodoroSession).count() >= 10
        assert db.query(StudySession).count() >= 3
        assert db.query(SleepSession).count() >= 3
        assert db.query(PresentationSession).count() >= 3
        assert db.query(SeminarRecording).count() >= 2
        assert db.query(GameScore).count() >= 5
        assert db.query(Trip).count() >= 3
    finally:
        db.close()
