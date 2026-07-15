"""Speech-to-text service powered by faster-whisper."""

import os
import tempfile
from dataclasses import dataclass

from fastapi import UploadFile

from app.config import settings


@dataclass
class TranscriptionResult:
    transcript: str
    language: str | None
    duration_sec: float | None


class WhisperSttService:
    def __init__(self, model_size: str | None = None):
        self.model_size = model_size or settings.WHISPER_MODEL_SIZE
        self._model = None

    def _load_model(self):
        if self._model is None:
            from faster_whisper import WhisperModel

            self._model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
        return self._model

    async def transcribe_upload(self, file: UploadFile) -> TranscriptionResult:
        suffix = os.path.splitext(file.filename or "")[1] or ".mp3"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            temp_path = tmp.name
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                tmp.write(chunk)

        try:
            model = self._load_model()
            segments, info = model.transcribe(temp_path, beam_size=5)
            text = " ".join(segment.text.strip() for segment in segments).strip()
            return TranscriptionResult(
                transcript=text,
                language=getattr(info, "language", None),
                duration_sec=getattr(info, "duration", None),
            )
        finally:
            try:
                os.remove(temp_path)
            except OSError:
                pass


stt_service = WhisperSttService()
