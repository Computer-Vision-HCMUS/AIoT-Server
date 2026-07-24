"""Authenticated text-to-speech endpoint backed by Groq."""

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field

from app.auth import get_current_device
from app.models.emoticare import Device
from app.services.tts import ESP_SAMPLE_RATE, TtsError, groq_tts_service

router = APIRouter(prefix="/api/tts", tags=["Text To Speech"])


class TtsSynthesisRequest(BaseModel):
    text: str = Field(min_length=1, max_length=200, description="Text to synthesize")
    output: Literal["pcm", "wav"] = Field(
        default="pcm",
        description="pcm is signed 16-bit LE, mono, 16 kHz for the ESP I2S speaker",
    )


@router.post("/synthesize", summary="Create speech with Groq TTS")
def synthesize_speech(
    payload: TtsSynthesisRequest,
    current_device: Device = Depends(get_current_device),
):
    """Return a fresh audio response; do not persist private companion content."""
    try:
        if payload.output == "pcm":
            audio = groq_tts_service.synthesize_pcm(payload.text)
            return Response(
                content=audio,
                media_type=f"audio/L16;rate={ESP_SAMPLE_RATE};channels=1",
                headers={
                    "X-Audio-Format": "s16le",
                    "X-Audio-Sample-Rate": str(ESP_SAMPLE_RATE),
                    "Cache-Control": "no-store",
                },
            )

        audio = groq_tts_service.synthesize_wav(payload.text)
        return Response(content=audio, media_type="audio/wav", headers={"Cache-Control": "no-store"})
    except TtsError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
