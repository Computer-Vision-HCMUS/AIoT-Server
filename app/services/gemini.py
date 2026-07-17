"""Provider-agnostic text generation for the EmotiCare playground."""

from time import sleep

import httpx

from app.config import settings


class PlaygroundClient:
    """Select Gemini or Groq with ``PLAYGROUND_API`` without changing callers."""

    @property
    def provider(self) -> str:
        return settings.PLAYGROUND_API.strip().upper()

    @property
    def available(self) -> bool:
        return bool(settings.GROQ_API_KEY) if self.provider in {"GROQ", "GROK"} else bool(settings.GEMINI_API_KEY)

    def _generate_groq(self, prompt: str) -> str:
        response = httpx.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}"}, json={"model": settings.GROQ_MODEL, "messages": [{"role": "system", "content": "You are EmotiCare, a warm, concise Vietnamese wellbeing companion. Do not diagnose medical conditions."}, {"role": "user", "content": prompt}], "temperature": 0.5}, timeout=30)
        response.raise_for_status()
        return ((response.json().get("choices") or [{}])[0].get("message", {}).get("content", "")).strip()

    def _generate_gemini(self, prompt: str) -> str:
        from google import genai
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        return (getattr(client.models.generate_content(model=settings.GEMINI_MODEL, contents=prompt), "text", None) or "").strip()

    def generate_text(self, prompt: str, *, fallback: str, require_live: bool = False) -> str:
        if not self.available:
            if require_live:
                raise RuntimeError("Gemini is not configured")
            return fallback
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                text = self._generate_groq(prompt) if self.provider in {"GROQ", "GROK"} else self._generate_gemini(prompt)
                if text:
                    return text.strip()
                break
            except Exception as exc:
                last_error = exc
                is_rate_limited = "429" in str(exc) or "RESOURCE_EXHAUSTED" in str(exc)
                if not is_rate_limited or attempt == 2:
                    break
                sleep(8 * (attempt + 1))
        if last_error is not None:
            if require_live:
                raise RuntimeError("AI provider request failed") from last_error
            return fallback
        if require_live:
            raise RuntimeError("AI provider returned an empty response")
        return fallback


gemini_client = PlaygroundClient()
