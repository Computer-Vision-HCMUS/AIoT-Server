# Gemini and Whisper Integration

This backend supports two AI integrations:

- Gemini for short TFT-friendly chat/reason text.
- Whisper via `faster-whisper` for speech-to-text.

Both integrations are optional at local development time. The API keeps
rule-based fallbacks so tests and demos can run without external credentials.

## Environment

```env
GEMINI_API_KEY=<google-ai-studio-api-key>
GEMINI_MODEL=gemini-2.5-flash
WHISPER_MODEL_SIZE=base
```

`WHISPER_MODEL_SIZE=base` is the recommended demo default for CPU. Use `small`
only if the demo machine has enough RAM and startup time.

## Gemini Behavior

Gemini is used by:

- `POST /api/conversations/respond`
- recommendation reason generation in activity/music/podcast cards

Fallback behavior:

- If `GEMINI_API_KEY` is missing, the backend returns deterministic rule-based
  templates.
- If the Gemini API fails, the backend still returns a valid TFT card.
- Crisis and medium-risk safety responses do not depend on Gemini.

The response text is capped to fit existing database and TFT constraints.

## Whisper STT Behavior

Endpoint:

```http
POST /api/stt/transcribe
```

Request:

```text
multipart/form-data
file=@sample.mp3
```

Response:

```json
{
  "transcript": "noi dung nhan dien",
  "language": "vi",
  "duration_sec": 20.0,
  "stored": false
}
```

Privacy rule:

- Uploaded user audio is written only to a temporary file for Whisper.
- The temporary file is deleted after transcription.
- The API does not store raw user audio by default.

## Local Verification

```bash
pytest -q
uvicorn app.main:app --reload
```

Then open:

```text
http://localhost:8000/docs
```

Use the seeded device token:

```text
demo-emoticare-device-token-local-dev
```
