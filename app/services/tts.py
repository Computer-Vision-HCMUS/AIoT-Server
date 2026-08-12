"""Groq text-to-speech client and conversion helpers for the ESP speaker."""

from __future__ import annotations

import logging
import subprocess

import httpx

from app.config import settings

logger = logging.getLogger("uvicorn.error")

GROQ_SPEECH_URL = "https://api.groq.com/openai/v1/audio/speech"
ESP_SAMPLE_RATE = 16_000


class TtsError(RuntimeError):
    """A safe, client-facing error raised while generating speech."""


class GroqTtsService:
    """Create WAV speech with Groq, with optional ESP-compatible PCM output."""

    def synthesize_wav(self, text: str) -> bytes:
        if not settings.GROQ_API_KEY:
            raise TtsError("Groq TTS is not configured")

        try:
            response = httpx.post(
                GROQ_SPEECH_URL,
                headers={
                    "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.GROQ_TTS_MODEL,
                    "voice": settings.GROQ_TTS_VOICE,
                    "input": text,
                    "response_format": "wav",
                },
                timeout=settings.GROQ_TTS_TIMEOUT_SEC,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.warning("Groq TTS rejected request: status=%s body=%s",
                           exc.response.status_code, exc.response.text[:500])
            raise TtsError("Groq TTS request was rejected") from exc
        except httpx.HTTPError as exc:
            logger.exception("Groq TTS request failed")
            raise TtsError("Groq TTS is temporarily unavailable") from exc

        if not response.content:
            raise TtsError("Groq TTS returned empty audio")
        return response.content

    def synthesize_pcm(self, text: str) -> bytes:
        """Return signed 16-bit little-endian, 16 kHz, mono PCM for I2S."""
        wav = self.synthesize_wav(text)
        try:
            conversion = subprocess.run(
                [
                    "ffmpeg", "-v", "error", "-i", "pipe:0", "-vn",
                    "-f", "s16le", "-acodec", "pcm_s16le", "-ac", "1",
                    "-ar", str(ESP_SAMPLE_RATE), "pipe:1",
                ],
                input=wav,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=30,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            logger.exception("Unable to launch ffmpeg for Groq TTS audio")
            raise TtsError("Audio conversion is temporarily unavailable") from exc

        if conversion.returncode != 0 or not conversion.stdout:
            logger.error("Groq TTS PCM conversion failed: %s", conversion.stderr.decode("utf-8", "replace"))
            raise TtsError("Audio conversion failed")
        return conversion.stdout


groq_tts_service = GroqTtsService()
