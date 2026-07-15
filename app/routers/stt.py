"""Speech-to-text router."""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.auth import get_current_device
from app.models.emoticare import Device
from app.schemas import SttTranscriptionResponse
from app.services.stt import stt_service

router = APIRouter(prefix="/api/stt", tags=["Speech To Text"])

ALLOWED_AUDIO_TYPES = {
    "audio/mpeg",
    "audio/mp3",
    "audio/wav",
    "audio/x-wav",
    "audio/webm",
    "audio/mp4",
    "application/octet-stream",
}


@router.post(
    "/transcribe",
    response_model=SttTranscriptionResponse,
    summary="Transcribe uploaded audio with Whisper",
)
async def transcribe_audio(
    file: UploadFile = File(...),
    current_device: Device = Depends(get_current_device),
):
    if file.content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported audio type. Upload an MP3 or another audio file.",
        )

    try:
        result = await stt_service.transcribe_upload(file)
    except ImportError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Whisper STT dependency is not installed",
        ) from exc

    return SttTranscriptionResponse(
        transcript=result.transcript,
        language=result.language,
        duration_sec=result.duration_sec,
        stored=False,
    )
