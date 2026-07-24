from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str = "sqlite:///./aiot.db"
    MIGRATION_DATABASE_URL: str | None = None
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_DEBUG: bool = False
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    PLAYGROUND_API: str = "GEMINI"
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GROQ_API_KEY: str | None = None
    GROQ_MODEL: str = "groq/compound-mini"
    # Groq's current Orpheus English model is the available option for TTS.
    # Keep these separate from GROQ_MODEL, which is used for chat completion.
    GROQ_TTS_MODEL: str = "canopylabs/orpheus-v1-english"
    GROQ_TTS_VOICE: str = "hannah"
    GROQ_TTS_TIMEOUT_SEC: float = 45.0
    WHISPER_MODEL_SIZE: str = "base"
    WHISPER_DEVICE: str = "cpu"
    WHISPER_COMPUTE_TYPE: str = "int8"
    WHISPER_BEAM_SIZE: int = 1
    WHISPER_CPU_THREADS: int = 4
    WHISPER_VAD_FILTER: bool = True
    WHISPER_LANGUAGE: str | None = "vi"
    SUPABASE_URL: str | None = None
    SUPABASE_SERVICE_ROLE_KEY: str | None = None
    SUPABASE_MEDIA_BUCKET: str = "media-demo"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


settings = Settings()
