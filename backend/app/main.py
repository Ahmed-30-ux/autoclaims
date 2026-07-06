import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import init_db
from app.api.claims import router as claims_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AutoClaims backend...")
    init_db()
    logger.info(f"Database initialized. API key set: {bool(settings.qwen_api_key)}")
    yield
    logger.info("Shutting down AutoClaims backend...")


app = FastAPI(
    title="AutoClaims - AI-Powered Insurance Claims Processing",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(claims_router)


@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "app": settings.app_name,
        "qwen_configured": bool(settings.qwen_api_key),
    }
