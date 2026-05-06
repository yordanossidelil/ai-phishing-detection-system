from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

from app.core.config import get_settings
from app.core.database import connect_db, close_db
from app.api import analysis, auth
from app.middleware.rate_limit import limiter, rate_limit_exceeded_handler

settings = get_settings()

app = FastAPI(
    title="AI Phishing Detection API",
    description="Detects phishing emails and messages using ML/NLP. Supports English, Amharic, and Afaan Oromo.",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(analysis.router)


@app.on_event("startup")
async def startup():
    await connect_db()
    # Pre-load ML model
    from app.services.ml_service import get_detector
    get_detector()


@app.on_event("shutdown")
async def shutdown():
    await close_db()


@app.get("/health")
async def health():
    return {"status": "ok", "service": "AI Phishing Detection API"}
