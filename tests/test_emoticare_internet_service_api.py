import uuid
from datetime import datetime, timezone

from app.database import SessionLocal
from app.models.emoticare import (
    ActivityFeedback,
    ConversationRequest,
    Device,
    EmotionSession,
    MediaItem,
    MediaSelectionLog,
    RecommendationRequest,
    TftReport,
    User,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _create_user(pairing_code: str, *, consent_audio_storage: bool = False) -> str:
    user_id = str(uuid.uuid4())
    db = SessionLocal()
    try:
        db.add(
            User(
                id=user_id,
                name=f"User {pairing_code}",
                pairing_code=pairing_code,
                consent_audio_storage=consent_audio_storage,
                created_at=_now(),
                updated_at=_now(),
            )
        )
        db.commit()
    finally:
        db.close()
    return user_id


def _seed_media_items() -> list[str]:
    media_items = [
        {
            "media_type": "song",
            "category": "relax",
            "title": "Calm Water",
            "creator": "EmotiCare",
            "duration_sec": 180,
        },
        {
            "media_type": "podcast",
            "category": "relax",
            "title": "Slow Breathing",
            "creator": "EmotiCare",
            "duration_sec": 300,
        },
        {
            "media_type": "song",
            "category": "focus",
            "title": "Soft Focus",
            "creator": "EmotiCare",
            "duration_sec": 240,
        },
        {
            "media_type": "podcast",
            "category": "sad_support",
            "title": "Kind Words",
            "creator": "EmotiCare",
            "duration_sec": 360,
        },
    ]
    ids = []
    db = SessionLocal()
    try:
        for item in media_items:
            item_id = str(uuid.uuid4())
            ids.append(item_id)
            db.add(MediaItem(id=item_id, source_url=None, enabled=True, **item))
        db.commit()
    finally:
        db.close()
    return ids


def _pair_device(client, pairing_code: str) -> tuple[str, dict[str, str]]:
    response = client.post(
        "/api/devices/pair",
        json={
            "pairing_code": pairing_code,
            "device_name": f"Device {pairing_code}",
            "firmware_version": "1.0.0",
        },
    )
    assert response.status_code == 201
    body = response.json()
    return body["device_id"], {"X-Device-Token": body["device_token"]}


def _sync_session(
    client,
    headers: dict[str, str],
    client_session_id: str,
    emotion: str,
    *,
    confidence_score: float = 0.82,
):
    response = client.post(
        "/api/emotion-sessions/sync",
        headers=headers,
        json={
            "sessions": [
                {
                    "client_session_id": client_session_id,
                    "emotion_label": emotion,
                    "confidence_score": confidence_score,
                    "quality_flag": "clean",
                    "inference_latency_ms": 850,
                    "client_created_at": _now().isoformat(),
                }
            ]
        },
    )
    assert response.status_code == 200
    return response


def _create_flow(client, pairing_code: str, emotions: list[str], *, consent: bool = False):
    _seed_media_items()
    _create_user(pairing_code, consent_audio_storage=consent)
    device_id, headers = _pair_device(client, pairing_code)
    for index, emotion in enumerate(emotions, start=1):
        _sync_session(client, headers, f"{pairing_code.lower()}-session-{index}", emotion)
    first_session_id = _cloud_session_id(f"{pairing_code.lower()}-session-1", device_id)
    return device_id, headers, first_session_id


def _cloud_session_id(client_session_id: str, device_id: str) -> str:
    db = SessionLocal()
    try:
        session = (
            db.query(EmotionSession)
            .filter(
                EmotionSession.client_session_id == client_session_id,
                EmotionSession.device_id == device_id,
            )
            .one()
        )
        return session.id
    finally:
        db.close()


def test_device_pair_and_heartbeat_return_tft_ready_payload(client):
    _create_user("PAIR-001")
    device_id, headers = _pair_device(client, "PAIR-001")

    heartbeat = client.post(
        "/api/devices/heartbeat",
        headers=headers,
        json={"firmware_version": "1.0.1"},
    )

    assert heartbeat.status_code == 200
    assert heartbeat.json()["device_id"] == device_id
    assert heartbeat.json()["status"] == "online"
    assert heartbeat.json()["config_version"] == "emoticare-edge-config-v1"

    db = SessionLocal()
    try:
        device = db.query(Device).filter(Device.id == device_id).one()
        assert device.firmware_version == "1.0.1"
        assert device.device_token_hash != headers["X-Device-Token"]
    finally:
        db.close()


def test_emotion_sync_is_idempotent_per_device(client):
    _create_user("SYNC-001")
    first_device_id, first_headers = _pair_device(client, "SYNC-001")

    first = _sync_session(client, first_headers, "edge-session-001", "stressed")
    duplicate = _sync_session(client, first_headers, "edge-session-001", "stressed")

    assert first.json()["received_count"] == 1
    assert duplicate.json()["received_count"] == 0

    _create_user("SYNC-002")
    second_device_id, second_headers = _pair_device(client, "SYNC-002")
    same_client_id_other_device = _sync_session(
        client, second_headers, "edge-session-001", "happy"
    )

    assert same_client_id_other_device.json()["received_count"] == 1

    db = SessionLocal()
    try:
        assert (
            db.query(EmotionSession)
            .filter(EmotionSession.client_session_id == "edge-session-001")
            .count()
            == 2
        )
        assert first_device_id != second_device_id
    finally:
        db.close()


def test_recommendation_media_conversation_feedback_and_report_persist_to_tables(client):
    media_ids = _seed_media_items()
    _create_user("FLOW-001", consent_audio_storage=True)
    device_id, headers = _pair_device(client, "FLOW-001")

    for index, emotion in enumerate(["stressed", "sad", "neutral"], start=1):
        _sync_session(client, headers, f"flow-session-{index}", emotion)

    session_id = _cloud_session_id("flow-session-1", device_id)

    recommendation = client.post(
        "/api/recommendations/request",
        headers=headers,
        json={"session_id": session_id},
    )
    assert recommendation.status_code == 200
    assert 1 <= len(recommendation.json()["cards"]) <= 5
    assert all("reason" in card for card in recommendation.json()["cards"])

    activity_feedback = client.post(
        "/api/feedback/activity",
        headers=headers,
        json={
            "recommendation_id": recommendation.json()["recommendation_id"],
            "activity_type": "breathing",
            "selected": True,
            "feedback_score": 5,
        },
    )
    assert activity_feedback.status_code == 201

    categories = client.get("/api/media/categories", headers=headers)
    assert categories.status_code == 200
    assert len(categories.json()["categories"]) == 7

    media_recommendations = client.post(
        "/api/media/recommendations",
        headers=headers,
        json={
            "media_type": "both",
            "emotion_label": "stressed",
            "user_intent": "calm down",
        },
    )
    assert media_recommendations.status_code == 200
    assert media_recommendations.json()["cards"]

    media_feedback = client.post(
        "/api/feedback/media",
        headers=headers,
        json={
            "session_id": session_id,
            "media_item_id": media_ids[0],
            "user_intent": "calm down",
            "feedback_score": 4,
        },
    )
    assert media_feedback.status_code == 201

    conversation = client.post(
        "/api/conversations/respond",
        headers=headers,
        json={
            "session_id": session_id,
            "user_message": "toi thay cang thang nhung khong nguy hiem",
        },
    )
    assert conversation.status_code == 200
    assert conversation.json()["card"]["action_id"].startswith("conversation:")

    report = client.post(
        "/api/reports/generate",
        headers=headers,
        json={"period_type": "daily"},
    )
    assert report.status_code == 201
    assert report.json()["data_quality"] == "enough_data"
    assert any(card["action_id"] == "report:support_effectiveness" for card in report.json()["cards"])

    db = SessionLocal()
    try:
        assert db.query(EmotionSession).count() == 3
        assert db.query(RecommendationRequest).count() == 1
        assert db.query(ActivityFeedback).count() == 1
        assert db.query(MediaSelectionLog).count() == 1
        assert db.query(ConversationRequest).count() == 1
        assert db.query(TftReport).count() == 1
    finally:
        db.close()


def test_authenticated_list_endpoints_return_only_current_device_data(client):
    first_device_id, first_headers, first_session_id = _create_flow(
        client, "LIST-001", ["stressed", "sad", "neutral"], consent=True
    )
    second_device_id, second_headers, _ = _create_flow(
        client, "LIST-002", ["happy"], consent=False
    )

    reco = client.post(
        "/api/recommendations/request",
        headers=first_headers,
        json={"session_id": first_session_id},
    )
    assert reco.status_code == 200

    media_id = _seed_media_items()[0]
    assert client.post(
        "/api/feedback/media",
        headers=first_headers,
        json={
            "session_id": first_session_id,
            "media_item_id": media_id,
            "user_intent": "calm down",
            "feedback_score": 4,
        },
    ).status_code == 201
    assert client.post(
        "/api/reports/generate",
        headers=first_headers,
        json={"period_type": "daily"},
    ).status_code == 201

    sessions = client.get("/api/emotion-sessions", headers=first_headers)
    recommendations = client.get("/api/recommendations", headers=first_headers)
    media_history = client.get("/api/media/history", headers=first_headers)
    reports = client.get("/api/reports", headers=first_headers)

    assert sessions.status_code == 200
    assert recommendations.status_code == 200
    assert media_history.status_code == 200
    assert reports.status_code == 200
    assert {item["client_session_id"] for item in sessions.json()["items"]} == {
        "list-001-session-1",
        "list-001-session-2",
        "list-001-session-3",
    }
    assert recommendations.json()["items"][0]["id"] == reco.json()["recommendation_id"]
    assert media_history.json()["items"][0]["session_id"] == first_session_id
    assert reports.json()["items"]

    second_sessions = client.get("/api/emotion-sessions", headers=second_headers)
    assert second_sessions.status_code == 200
    assert {item["client_session_id"] for item in second_sessions.json()["items"]} == {
        "list-002-session-1"
    }
    assert first_device_id != second_device_id


def test_auth_cross_device_and_missing_data_errors_are_enforced(client):
    _, first_headers, first_session_id = _create_flow(client, "AUTH-001", ["stressed"])
    _, second_headers, _ = _create_flow(client, "AUTH-002", ["happy"])

    missing_auth = client.get("/api/emotion-sessions")
    assert missing_auth.status_code == 401

    invalid_auth = client.get(
        "/api/emotion-sessions",
        headers={"X-Device-Token": "not-a-real-token"},
    )
    assert invalid_auth.status_code == 401

    cross_device_reco = client.post(
        "/api/recommendations/request",
        headers=second_headers,
        json={"session_id": first_session_id},
    )
    assert cross_device_reco.status_code == 404

    cross_device_conversation = client.post(
        "/api/conversations/respond",
        headers=second_headers,
        json={"session_id": first_session_id, "user_message": "hello"},
    )
    assert cross_device_conversation.status_code == 404

    missing_session_feedback = client.post(
        "/api/feedback/media",
        headers=second_headers,
        json={
            "session_id": first_session_id,
            "media_item_id": _seed_media_items()[0],
            "feedback_score": 3,
        },
    )
    assert missing_session_feedback.status_code == 404


def test_crisis_safety_response_is_high_and_redacts_summary(client):
    _, headers, session_id = _create_flow(
        client, "SAFE-001", ["sad"], consent=True
    )

    response = client.post(
        "/api/conversations/respond",
        headers=headers,
        json={
            "session_id": session_id,
            "user_message": "toi muon chet va khong muon song nua",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["safety_flag"] == "high"
    assert body["card"]["severity"] == "alert"
    assert body["card"]["next_action"] == "contact_support"

    db = SessionLocal()
    try:
        conversation = db.query(ConversationRequest).one()
        assert conversation.safety_flag == "high"
        assert conversation.user_message_summary == "[high_safety_signal_redacted]"
    finally:
        db.close()


def test_report_with_limited_data_and_invalid_period_are_handled(client):
    _, headers, _ = _create_flow(client, "REPORT-001", ["neutral"])

    limited = client.post(
        "/api/reports/generate",
        headers=headers,
        json={"period_type": "daily"},
    )
    assert limited.status_code == 201
    assert limited.json()["data_quality"] == "limited_data"
    assert any(card["action_id"] == "report:limited" for card in limited.json()["cards"])

    invalid = client.get(
        "/api/reports",
        headers=headers,
        params={"period_type": "quarterly"},
    )
    assert invalid.status_code == 422
