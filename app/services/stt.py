"""Speech-to-text service powered by faster-whisper."""

import os
import tempfile
from dataclasses import dataclass

from starlette.concurrency import run_in_threadpool

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
            # Conda's MKL packages and CTranslate2 may each load Intel OpenMP on
            # Windows.  Set this before importing faster-whisper so a local dev
            # server can run instead of aborting with OMP Error #15.
            if os.name == "nt":
                os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
            from faster_whisper import WhisperModel

            self._model = WhisperModel(
                self.model_size,
                device=settings.WHISPER_DEVICE,
                compute_type=settings.WHISPER_COMPUTE_TYPE,
                cpu_threads=settings.WHISPER_CPU_THREADS,
            )
        return self._model

    def _transcribe_file(self, path: str) -> TranscriptionResult:
        model = self._load_model()
        segments, info = model.transcribe(
            path,
            beam_size=settings.WHISPER_BEAM_SIZE,
            language=settings.WHISPER_LANGUAGE,
            vad_filter=settings.WHISPER_VAD_FILTER,
        )
        text = " ".join(segment.text.strip() for segment in segments).strip()
        return TranscriptionResult(
            transcript=text,
            language=getattr(info, "language", None),
            duration_sec=getattr(info, "duration", None),
        )

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
            # CTranslate2 inference is CPU-bound.  Keep it off FastAPI's event
            # loop so health checks and other API requests remain responsive.
            return await run_in_threadpool(self._transcribe_file, temp_path)
        finally:
            try:
                os.remove(temp_path)
            except OSError:
                pass


stt_service = WhisperSttService()
