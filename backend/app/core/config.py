"""Application settings — local PostgreSQL by default."""

import os
from functools import lru_cache
from pathlib import Path
try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# Dev-only placeholder. Rejected at startup when DEBUG is off (see apply_local_defaults).
_DEV_JWT_SECRET = "dev-only-insecure-jwt-secret-change-me"


def _backend_dir() -> Path:
    return Path(__file__).resolve().parents[2]


def _project_root() -> Path:
    return _backend_dir().parent


def _discover_env_files() -> tuple[str, ...]:
    candidates = [
        _project_root() / ".env",
        _backend_dir() / ".env",
        Path.cwd() / ".env",
        Path.cwd().parent / ".env",
    ]
    seen: set[str] = set()
    found: list[str] = []
    for p in candidates:
        if p.is_file():
            resolved = str(p.resolve())
            if resolved not in seen:
                seen.add(resolved)
                found.append(str(p))
    return tuple(found) if found else (str(_project_root() / ".env"),)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_discover_env_files(),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "EduSpark API"
    API_PREFIX: str = "/api"
    DEBUG: bool | str = False

    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "eduspark"
    POSTGRES_PASSWORD: str = "eduspark"
    POSTGRES_DB: str = "eduspark_syria"

    DATABASE_URL: str = ""
    # Sync driver for Alembic / scripts (postgresql+psycopg2). Alias: SYNC_DATABASE_URL.
    DATABASE_URL_SYNC: str = ""
    SYNC_DATABASE_URL: str = ""

    # pgvector / embeddings (off by default for local Windows Postgres)
    ENABLE_PGVECTOR: bool = False
    ENABLE_EMBEDDINGS: bool = False

    # Mistral OCR (documents) + minimum extracted text threshold for lesson PDFs
    MISTRAL_API_KEY: str = ""
    MISTRAL_OCR_MODEL: str = "mistral-ocr-latest"
    MIN_EXTRACTED_TEXT_CHARS: int = 120
    ENABLE_FAISS: bool = True
    EMBEDDING_MODEL: str = "BAAI/bge-m3"
    VECTOR_INDEX_DIR: str = ""

    ENABLE_WHISPER: bool = True
    WHISPER_MODEL: str = "turbo"
    WHISPER_MODEL_PATH: str = ""
    LESSON_VIDEO_WHISPER_LANGUAGE: str = "ar"
    LESSON_VIDEO_FASTER_WHISPER_MODEL: str = ""
    LESSON_VIDEO_GEMINI_TIMEOUT_SECONDS: int = 600

    LLM_PROVIDER: str = "claude"  # claude | ollama (local dev fallback)
    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    OLLAMA_MODEL: str = "gemma3"

    # Claude LLM (primary provider for all text/JSON generation)
    ANTHROPIC_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-sonnet-5"

    # Gemini — retained only for STT fallbacks (student chat, teacher/lesson audio/video)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

    ENABLE_TTS: bool = False
    TTS_PROVIDER: str = "elevenlabs"
    TTS_REQUEST_TIMEOUT_SECONDS: int = 120
    TTS_LANGUAGE: str = "ar"
    TTS_ALLOWED_LANGUAGES: str = "ar,en,fr"
    TTS_OUTPUT_DIR: str = ""
    TTS_MAX_TEXT_CHARS: int = 1200

    ELEVENLABS_API_KEY: str = ""
    ELEVENLABS_BASE_URL: str = "https://api.elevenlabs.io/v1"
    ELEVENLABS_MODEL_ID: str = "eleven_multilingual_v2"
    ELEVENLABS_OUTPUT_FORMAT: str = "mp3_44100_128"
    ELEVENLABS_VOICE_NAME_PREFIX: str = "EduSpark Teacher"
    ELEVENLABS_DEFAULT_VOICE_ID: str = ""
    ELEVENLABS_STABILITY: float = 0.45
    ELEVENLABS_SIMILARITY_BOOST: float = 0.85
    ELEVENLABS_STYLE: float = 0.0
    ELEVENLABS_USE_SPEAKER_BOOST: bool = True

    JWT_SECRET: str = _DEV_JWT_SECRET
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Per-course subscription term (days) after payment
    SUBSCRIPTION_TERM_DAYS: int = 30
    SUBSCRIPTION_EXPIRING_SOON_DAYS: int = 7
    SUBSCRIPTION_CHECK_INTERVAL_SECONDS: int = 3600

    # Language Learning module
    LANGUAGE_SUBSCRIPTION_TERM_DAYS: int = 365
    LANGUAGE_SUBSCRIPTION_EXPIRING_SOON_DAYS: int = 7
    LANGUAGE_PLACEMENT_RETAKE_DAYS: int = 90
    LANGUAGE_INACTIVITY_ALERT_DAYS: int = 7
    LANGUAGE_STREAK_MILESTONES: str = "7,14,30,60"
    LANGUAGE_CONVERSATION_MOCK_AI: bool = False
    LANGUAGE_CONVERSATION_SPEAKER_WAV: str = ""
    LANGUAGE_CONVERSATION_HISTORY_TURNS: int = 12
    LANGUAGE_TTS_PROVIDER: str = "supertonic"
    LANGUAGE_SUPERTONIC_VOICE: str = "M1"
    LANGUAGE_SUPERTONIC_AUTO_DOWNLOAD: bool = True
    LANGUAGE_CONVERSATION_LEVEL_WINDOW: int = 30
    LANGUAGE_CONVERSATION_WHISPER_MODEL: str = "small.en"
    LANGUAGE_CONVERSATION_WHISPER_COMPUTE_TYPE: str = "float32"
    LANGUAGE_CONVERSATION_WHISPER_BEAM_SIZE: int = 5
    LANGUAGE_CONVERSATION_WHISPER_VAD: bool = False
    LANGUAGE_CONVERSATION_WHISPER_INITIAL_PROMPT: str = ""
    LANGUAGE_CONVERSATION_ASYNC_TTS: bool = True
    OPENAI_API_KEY: str = ""
    LANGUAGE_STT_PROVIDER: str = "openai"  # openai | whisper
    LANGUAGE_STT_MODEL: str = "gpt-4o-transcribe"
    LANGUAGE_STT_ALLOW_WHISPER_FALLBACK: bool = True
    GENAI_EXAM_MAX_AUDIO_MB: int = 10
    LANGUAGE_MASTERY_WINDOW_SIZE: int = 8
    LANGUAGE_MASTERY_UP_THRESHOLD: float = 82.0
    LANGUAGE_MASTERY_DOWN_THRESHOLD: float = 40.0

    # Student lesson voice chat STT (Deepgram Nova — not used by Language module)
    DEEPGRAM_API_KEY: str = ""
    DEEPGRAM_STT_MODEL: str = "nova-3"

    UPLOAD_DIR: str = ""
    MAX_PDF_BYTES: int = 500 * 1024 * 1024
    MAX_AUDIO_BYTES: int = 10 * 1024 * 1024
    MAX_VOICE_SAMPLE_BYTES: int = 50 * 1024 * 1024
    VOICE_SAMPLE_MIN_SECONDS: int = 60
    VOICE_CLONE_MIN_QUALITY_SCORE: int = 65
    VOICE_CLONE_MIN_CLONE_CONFIDENCE: int = 60
    VOICE_CLONE_MIN_TRANSCRIPT_QUALITY: int = 50
    VOICE_CLONE_AUTO_REJECT_QUALITY: int = 45

    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Transactional email (Resend)
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "EduSpark <onboarding@resend.dev>"
    EMAIL_VERIFICATION_EXPIRE_HOURS: int = 24
    PASSWORD_RESET_EXPIRE_HOURS: int = 1
    TWO_FACTOR_CODE_EXPIRE_MINUTES: int = 10
    TWO_FACTOR_MAX_ATTEMPTS: int = 5
    TWO_FACTOR_RESEND_COOLDOWN_SECONDS: int = 60
    TWO_FACTOR_MAX_RESENDS: int = 3

    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    RAG_TOP_K: int = 5
    QUIZ_COUNT: int = 5

    DB_CONNECT_TIMEOUT: int = 10

    # Legacy ALTER/CREATE patches on startup — disable in production (use Alembic only).
    APPLY_LEGACY_SCHEMA_PATCHES: bool = False

    @model_validator(mode="after")
    def apply_local_defaults(self) -> Self:
        if isinstance(self.DEBUG, str):
            self.DEBUG = self.DEBUG.strip().lower() in ("1", "true", "yes", "on", "debug")

        # Never allow an insecure JWT secret in production (DEBUG off).
        secret = (self.JWT_SECRET or "").strip()
        insecure_secret = (
            not secret
            or secret == _DEV_JWT_SECRET
            or "change-me" in secret.lower()
            or "change-me-in-production" in secret.lower()
        )
        if not self.DEBUG and insecure_secret:
            raise ValueError(
                "JWT_SECRET is missing or set to an insecure placeholder. "
                "Set a strong, random JWT_SECRET (e.g. `python -c \"import secrets; "
                "print(secrets.token_urlsafe(64))\"`) in your environment before "
                "starting with DEBUG=false."
            )

        provider = (self.TTS_PROVIDER or "elevenlabs").strip().lower()
        if provider != "elevenlabs":
            provider = "elevenlabs"
        self.TTS_PROVIDER = provider

        language_tts_provider = (self.LANGUAGE_TTS_PROVIDER or "supertonic").strip().lower()
        if language_tts_provider not in {"supertonic", "disabled"}:
            language_tts_provider = "supertonic"
        self.LANGUAGE_TTS_PROVIDER = language_tts_provider

        language_stt_provider = (self.LANGUAGE_STT_PROVIDER or "openai").strip().lower()
        if language_stt_provider not in {"openai", "whisper"}:
            language_stt_provider = "openai"
        self.LANGUAGE_STT_PROVIDER = language_stt_provider

        in_docker = os.getenv("DOCKER_COMPOSE", "").lower() in ("1", "true", "yes")
        host = (self.POSTGRES_HOST or "localhost").strip()
        # Outside Docker, map compose service names to localhost for local Postgres
        if not in_docker and host in ("db", "postgres"):
            host = "localhost"

        if not self.DATABASE_URL.strip():
            self.DATABASE_URL = self._build_async_url(host)
        elif not in_docker:
            self.DATABASE_URL = self._ensure_localhost(self.DATABASE_URL)

        sync_raw = (self.SYNC_DATABASE_URL or self.DATABASE_URL_SYNC or "").strip()
        if not sync_raw:
            if self.DATABASE_URL.strip():
                sync_raw = self._async_to_sync_url(self.DATABASE_URL)
            else:
                sync_raw = self._build_sync_url(host)
        elif not in_docker:
            sync_raw = self._ensure_localhost(sync_raw)
        self.DATABASE_URL_SYNC = self._normalize_sync_url(sync_raw)

        if not self.UPLOAD_DIR.strip():
            self.UPLOAD_DIR = str(_backend_dir() / "uploads")
        elif not in_docker and self.UPLOAD_DIR.replace("\\", "/").startswith("/app/"):
            self.UPLOAD_DIR = str(_backend_dir() / "uploads")

        if not self.VECTOR_INDEX_DIR.strip():
            self.VECTOR_INDEX_DIR = str(Path(self.UPLOAD_DIR) / "indexes")
        elif not in_docker and self.VECTOR_INDEX_DIR.replace("\\", "/").startswith("/app/"):
            self.VECTOR_INDEX_DIR = str(Path(self.UPLOAD_DIR) / "indexes")

        if not self.TTS_OUTPUT_DIR.strip():
            self.TTS_OUTPUT_DIR = str(Path(self.UPLOAD_DIR) / "answers")
        elif not in_docker and self.TTS_OUTPUT_DIR.replace("\\", "/").startswith("/app/"):
            self.TTS_OUTPUT_DIR = str(Path(self.UPLOAD_DIR) / "answers")

        if not self.LANGUAGE_CONVERSATION_SPEAKER_WAV.strip():
            bundled = _backend_dir() / "scripts" / "_tts_verify_out" / "arabic_test.wav"
            if bundled.is_file():
                self.LANGUAGE_CONVERSATION_SPEAKER_WAV = str(bundled.resolve())

        self.POSTGRES_HOST = host
        # Embeddings require pgvector in DB
        if not self.ENABLE_PGVECTOR:
            self.ENABLE_EMBEDDINGS = False
        return self

    def _build_async_url(self, host: str) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{host}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    def _build_sync_url(self, host: str) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{host}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @staticmethod
    def _async_to_sync_url(url: str) -> str:
        """Convert runtime async URL to a sync Alembic URL."""
        normalized = url.strip()
        if "+asyncpg" in normalized:
            return normalized.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
        if normalized.startswith("postgresql://"):
            return normalized.replace("postgresql://", "postgresql+psycopg2://", 1)
        return normalized

    @staticmethod
    def _normalize_sync_url(url: str) -> str:
        """Ensure Alembic never receives asyncpg."""
        if "+asyncpg" in url:
            return Settings._async_to_sync_url(url)
        if url.startswith("postgresql://") and "+psycopg" not in url:
            return url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return url

    @staticmethod
    def _ensure_localhost(url: str) -> str:
        return (
            url.replace("@db:", "@localhost:")
            .replace("@db/", "@localhost/")
            .replace("@postgres:", "@localhost:")
        )

    @property
    def cors_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def database_display(self) -> str:
        return f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def sync_database_url(self) -> str:
        """Synchronous URL for Alembic migrations (psycopg2)."""
        return self.DATABASE_URL_SYNC


@lru_cache
def get_settings() -> Settings:
    return Settings()
