"""
Emotion Sessions router.

POST /api/emotion-sessions/sync — đồng bộ emotion sessions từ Edge (idempotent)
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth import get_current_device
from app.database import get_db
from app.models.emoticare import Device, EmotionSession
from app.schemas import EmotionSessionSyncRequest, EmotionSessionSyncResponse

router = APIRouter(prefix="/api/emotion-sessions", tags=["Emotion Sessions"])


@router.post(
    "/sync",
    response_model=EmotionSessionSyncResponse,
    status_code=status.HTTP_200_OK,
    summary="Đồng bộ emotion sessions từ Edge Device (idempotent)",
)
def sync_emotion_sessions(
    payload: EmotionSessionSyncRequest,
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    """
    Nhận batch emotion sessions từ Edge.
    Idempotent: nếu client_session_id đã tồn tại thì bỏ qua, không tạo trùng.
    Trả về danh sách client_session_id đã được nhận (mới + đã có sẵn).
    """
    received_ids: list[str] = []
    new_count = 0

    for session_data in payload.sessions:
        # Idempotency check
        existing = (
            db.query(EmotionSession)
            .filter(
                EmotionSession.device_id == current_device.id,
                EmotionSession.client_session_id == session_data.client_session_id,
            )
            .first()
        )
        if existing:
            received_ids.append(session_data.client_session_id)
            continue

        new_session = EmotionSession(
            id=str(uuid.uuid4()),
            client_session_id=session_data.client_session_id,
            user_id=current_device.user_id,
            device_id=current_device.id,
            emotion_label=session_data.emotion_label,
            confidence_score=session_data.confidence_score,
            quality_flag=session_data.quality_flag,
            inference_latency_ms=session_data.inference_latency_ms,
            client_created_at=session_data.client_created_at,
            created_at=datetime.now(timezone.utc),
        )
        db.add(new_session)
        received_ids.append(session_data.client_session_id)
        new_count += 1

    db.commit()

    return EmotionSessionSyncResponse(
        received_count=new_count,
        total_submitted=len(payload.sessions),
        received_ids=received_ids,
    )


@router.get(
    "",
    summary="Liệt kê emotion sessions gần nhất của thiết bị",
)
def list_emotion_sessions(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    sessions = (
        db.query(EmotionSession)
        .filter(EmotionSession.device_id == current_device.id)
        .order_by(EmotionSession.client_created_at.desc())
        .limit(limit)
        .all()
    )
    return {
        "items": [
            {
                "id": item.id,
                "client_session_id": item.client_session_id,
                "emotion_label": item.emotion_label,
                "confidence_score": float(item.confidence_score),
                "quality_flag": item.quality_flag,
                "inference_latency_ms": item.inference_latency_ms,
                "client_created_at": item.client_created_at,
                "created_at": item.created_at,
            }
            for item in sessions
        ]
    }
