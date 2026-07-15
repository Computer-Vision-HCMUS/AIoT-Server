"""Gemini API integration with safe fallback behavior."""

from app.config import settings


class GeminiClient:
    """Small wrapper around Google GenAI SDK.

    The SDK import is lazy so local tests can run without a configured API key.
    """

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key if api_key is not None else settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    def generate_text(self, prompt: str, *, fallback: str) -> str:
        if not self.available:
            return fallback
        try:
            from google import genai

            client = genai.Client(api_key=self.api_key)
            response = client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            text = getattr(response, "text", None)
            if text:
                return text.strip()
        except Exception:
            return fallback
        return fallback


gemini_client = GeminiClient()
