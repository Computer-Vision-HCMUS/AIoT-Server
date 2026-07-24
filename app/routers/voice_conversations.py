"""End-to-end Companion Chat voice pipeline for the ESP device."""

from __future__ import annotations

import logging
import threading
import time
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy.orm import Session

from app.auth import get_current_device
from app.database import get_db
from app.models.emoticare import ConversationRequest, Device, EmotionSession
from app.services.conversation import chat, detect_safety_flag, next_action, summarize_user_message
from app.services.stt import stt_service
from app.services.tts import ESP_SAMPLE_RATE, TtsError, groq_tts_service

router = APIRouter(prefix="/api/conversations", tags=["Conversations"])
logger = logging.getLogger("uvicorn.error")

MAX_PCM_BYTES = 30 * ESP_SAMPLE_RATE * 2
AUDIO_TTL_SEC = 300
_audio_cache: dict[str, tuple[float, str, bytes]] = {}
_audio_lock = threading.Lock()


def _store_reply_audio(device_id: str, pcm: bytes) -> str:
    now = time.monotonic()
    with _audio_lock:
        for audio_id, (expires_at, _, _) in list(_audio_cache.items()):
            if expires_at <= now:
                del _audio_cache[audio_id]
        audio_id = str(uuid.uuid4())
        _audio_cache[audio_id] = (now + AUDIO_TTL_SEC, device_id, pcm)
    return audio_id


@router.post("/voice", summary="PCM → local Whisper → chat → Groq TTS → PCM")
async def companion_voice_reply(
    request: Request,
    session_id: str = Query(min_length=36, max_length=36),
    sample_rate: int = Query(default=ESP_SAMPLE_RATE, ge=8_000, le=48_000),
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    """Accept raw signed PCM; temporary audio is never persisted after STT."""
    if request.headers.get("content-type", "").split(";", 1)[0] != "application/octet-stream":
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Upload raw PCM")
    pcm = await request.body()
    logger.info(
        "Companion PCM received: device=%s session=%s bytes=%d sample_rate=%d",
        current_device.id, session_id, len(pcm), sample_rate,
    )
    if not pcm or len(pcm) % 2:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid 16-bit PCM")
    if len(pcm) > MAX_PCM_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Recording exceeds 30 seconds")

    session = (
        db.query(EmotionSession)
        .filter(EmotionSession.id == session_id, EmotionSession.device_id == current_device.id)
        .first()
    )
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Emotion session not found")

    try:
        stt_result = await stt_service.transcribe_pcm_s16le(pcm, sample_rate)
    except (ImportError, RuntimeError) as exc:
        logger.exception("Companion voice STT failed")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Local Whisper is unavailable") from exc
    transcript = stt_result.transcript.strip()
    logger.info("Companion Whisper result: device=%s transcript=%r", current_device.id, transcript)
    if not transcript:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="No speech detected")

    safety_flag = detect_safety_flag(transcript)
    try:
        reply_text = chat(session.emotion_label, transcript, safety_flag)[:200]
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AI reply is unavailable") from exc

    conversation = ConversationRequest(
        id=str(uuid.uuid4()),
        session_id=session.id,
        user_message_summary=summarize_user_message(transcript, safety_flag),
        response_text=reply_text,
        safety_flag=safety_flag,
    )
    db.add(conversation)
    db.commit()

    try:
        reply_pcm = groq_tts_service.synthesize_pcm(reply_text)
    except TtsError as exc:
        logger.warning("Companion reply generated without audio: %s", exc)
        return {
            "conversation_id": conversation.id,
            "transcript": transcript,
            "reply_text": reply_text,
            "safety_flag": safety_flag,
            "next_action": next_action(session.emotion_label, safety_flag),
            "audio_path": None,
            "audio_error": str(exc),
        }

    audio_id = _store_reply_audio(current_device.id, reply_pcm)
    logger.info("Companion reply ready: device=%s conversation=%s pcm_bytes=%d",
                current_device.id, conversation.id, len(reply_pcm))
    return {
        "conversation_id": conversation.id,
        "transcript": transcript,
        "reply_text": reply_text,
        "safety_flag": safety_flag,
        "next_action": next_action(session.emotion_label, safety_flag),
        "audio_path": f"/api/conversations/voice-audio/{audio_id}",
    }


@router.get("/voice-audio/{audio_id}", summary="Fetch a short-lived Companion PCM reply")
def companion_voice_audio(
    audio_id: str,
    current_device: Device = Depends(get_current_device),
):
    with _audio_lock:
        audio = _audio_cache.get(audio_id)
        if audio is None or audio[0] <= time.monotonic() or audio[1] != current_device.id:
            _audio_cache.pop(audio_id, None)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reply audio expired")
        _, _, pcm = audio
        # A reply is private and intended for a single ESP playback request.
        del _audio_cache[audio_id]
    logger.info("Companion audio served: device=%s audio=%s pcm_bytes=%d",
                current_device.id, audio_id, len(pcm))
    return Response(
        content=pcm,
        media_type=f"audio/L16;rate={ESP_SAMPLE_RATE};channels=1",
        headers={"X-Audio-Format": "s16le", "Cache-Control": "no-store"},
    )
