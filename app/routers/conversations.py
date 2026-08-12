"""
Conversations router.

POST /api/conversations/respond — yêu cầu Cloud tạo phản hồi hỗ trợ cảm xúc
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.auth import get_current_device
from app.database import get_db
from app.models.emoticare import ConversationRequest, Device, EmotionSession, User
from app.schemas import (
    ConversationHistoryResponse,
    ConversationRespondRequest,
    ConversationRespondResponse,
)
from app.services.conversation import (
    chat,
    detect_safety_flag,
    next_action as conversation_next_action,
    summarize_user_message,
)
from app.services.stt import stt_service

router = APIRouter(prefix="/api/conversations", tags=["Conversations"])

MAX_VOICE_PCM_BYTES = 30 * 16000 * 2


def _summary_if_consented(
    user_id: str, message: str, safety_flag: str, db: Session
) -> str | None:
    """Persist conversation text only after the user's explicit opt-in."""
    consented = (
        db.query(User.consent_audio_storage)
        .filter(User.id == user_id)
        .scalar()
    )
    if consented is not True:
        return None
    return summarize_user_message(message, safety_flag)


@router.post(
    "/respond",
    response_model=ConversationRespondResponse,
    status_code=status.HTTP_200_OK,
    summary="Yêu cầu Cloud tạo phản hồi hỗ trợ cảm xúc",
)
def respond(
    payload: ConversationRespondRequest,
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    """
    Nhận user_message và emotion context.
    Áp dụng safety filter, trả về 1 response card rút gọn cho TFT.
    """
    # Verify session
    session = (
        db.query(EmotionSession)
        .filter(
            EmotionSession.id == payload.session_id,
            EmotionSession.device_id == current_device.id,
        )
        .first()
    )
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emotion session not found",
        )

    # Safety filter
    safety_flag = detect_safety_flag(payload.user_message or "")

    # Generate response
    try:
        response_text = chat(session.emotion_label, payload.user_message, safety_flag)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Live AI response is temporarily unavailable. Check the selected AI provider configuration and retry.",
        ) from exc
    next_action = conversation_next_action(session.emotion_label, safety_flag)

    user_message_summary = _summary_if_consented(
        session.user_id, payload.user_message or "", safety_flag, db
    )

    conversation = ConversationRequest(
        id=str(uuid.uuid4()),
        session_id=session.id,
        user_message_summary=user_message_summary,
        response_text=response_text,
        safety_flag=safety_flag,
        created_at=datetime.now(timezone.utc),
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    card = {
        "title": "Phản hồi hỗ trợ",
        "body": response_text,
        "severity": "alert" if safety_flag == "high" else ("warn" if safety_flag == "medium" else "info"),
        "next_action": next_action,
        "action_id": f"conversation:{conversation.id}",
    }

    return ConversationRespondResponse(
        conversation_id=conversation.id,
        safety_flag=safety_flag,
        card=card,
    )


@router.post("/voice", summary="Transcribe raw PCM and create a companion reply")
async def voice_respond(
    request: Request,
    session_id: str = Query(min_length=36, max_length=36),
    sample_rate: int = Query(default=16000, ge=8000, le=48000),
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    """Accept mono s16le PCM, then run STT and the conversation service."""
    session = (
        db.query(EmotionSession)
        .filter(
            EmotionSession.id == session_id,
            EmotionSession.device_id == current_device.id,
        )
        .first()
    )
    if session is None:
        raise HTTPException(status_code=404, detail="Emotion session not found")

    pcm = await request.body()
    if not pcm or len(pcm) % 2:
        raise HTTPException(status_code=400, detail="Body must be non-empty s16le PCM")
    if len(pcm) > MAX_VOICE_PCM_BYTES:
        raise HTTPException(status_code=413, detail="PCM recording exceeds 30 seconds")

    try:
        transcription = await stt_service.transcribe_pcm_s16le(pcm, sample_rate)
    except ImportError as exc:
        raise HTTPException(status_code=503, detail="Whisper STT dependency is not installed") from exc
    transcript = transcription.transcript.strip()
    if not transcript:
        raise HTTPException(status_code=422, detail="No speech detected")

    safety_flag = detect_safety_flag(transcript)
    try:
        reply_text = chat(session.emotion_label, transcript, safety_flag)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail="Live AI response is temporarily unavailable") from exc

    conversation = ConversationRequest(
        id=str(uuid.uuid4()),
        session_id=session.id,
        user_message_summary=_summary_if_consented(
            session.user_id, transcript, safety_flag, db
        ),
        response_text=reply_text,
        safety_flag=safety_flag,
        created_at=datetime.now(timezone.utc),
    )
    db.add(conversation)
    db.commit()

    return {
        "conversation_id": conversation.id,
        "transcript": transcript,
        "reply_text": reply_text,
        "safety_flag": safety_flag,
        # TTS is not configured yet; firmware treats an empty path as text-only.
        "audio_path": "",
    }


@router.get("/history", response_model=ConversationHistoryResponse)
def conversation_history(
    session_id: str | None = Query(default=None, min_length=36, max_length=36),
    limit: int = Query(default=30, ge=1, le=100),
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    """Load persisted assistant replies for sessions owned by this device."""
    query = (
        db.query(ConversationRequest)
        .join(ConversationRequest.session)
        .filter(EmotionSession.device_id == current_device.id)
    )
    if session_id:
        query = query.filter(ConversationRequest.session_id == session_id)

    conversations = query.order_by(ConversationRequest.created_at.desc()).limit(limit).all()
    return ConversationHistoryResponse(
        items=[
            {
                "id": item.id,
                "session_id": item.session_id,
                "user_message": item.user_message_summary,
                "response_text": item.response_text,
                "safety_flag": item.safety_flag,
                "created_at": item.created_at,
            }
            for item in reversed(conversations)
        ]
    )
