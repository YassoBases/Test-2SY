import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import get_settings
from app.db.session import AsyncSessionLocal, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
settings = get_settings()


async def _subscription_expiration_loop() -> None:
    from app.services.language_subscription_expiration_service import run_language_expiration_check
    from app.services.subscription_expiration_service import run_expiration_check

    interval = max(300, int(settings.SUBSCRIPTION_CHECK_INTERVAL_SECONDS))
    while True:
        try:
            async with AsyncSessionLocal() as db:
                stats = await run_expiration_check(db)
                lang_stats = await run_language_expiration_check(db)
                await db.commit()
                if stats.get("warnings") or stats.get("expired"):
                    logger.info("Subscription expiration check: %s", stats)
                if lang_stats.get("warnings") or lang_stats.get("expired"):
                    logger.info("Language subscription expiration check: %s", lang_stats)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Subscription expiration check failed")
        await asyncio.sleep(interval)


@asynccontextmanager
async def lifespan(app: FastAPI):
    upload_path = Path(settings.UPLOAD_DIR)
    upload_path.mkdir(parents=True, exist_ok=True)
    Path(settings.VECTOR_INDEX_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.TTS_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    logger.info("Uploads: %s", upload_path.resolve())
    logger.info("PostgreSQL: %s", settings.database_display)
    logger.info(
        "pgvector=%s embeddings=%s (keyword RAG when off)",
        settings.ENABLE_PGVECTOR,
        settings.ENABLE_EMBEDDINGS,
    )

    await init_db()
    expiration_task = asyncio.create_task(_subscription_expiration_loop())
    logger.info("%s ready — http://127.0.0.1:8000/docs", settings.APP_NAME)
    try:
        yield
    finally:
        expiration_task.cancel()
        try:
            await expiration_task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title=settings.APP_NAME,
    description="EduSpark — منصة تعليم ذكية | FastAPI + PostgreSQL",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_PREFIX)
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "database": settings.database_display,
        "pgvector": settings.ENABLE_PGVECTOR,
        "embeddings": settings.ENABLE_EMBEDDINGS,
    }
