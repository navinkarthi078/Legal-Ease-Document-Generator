"""
LegalEase FastAPI backend entry-point.
Run with:
    uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
"""
import sys
import os

# Ensure project root is on Python path (needed when running from root)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load .env from project root
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(dotenv_path=os.path.join(_ROOT, ".env"))

from backend.routes import router

# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title="LegalEase AI",
    description=(
        "Production-ready AI-powered legal document generator "
        "backed by Google Gemini."
    ),
    version="1.0.0",
    contact={
        "name": "LegalEase Support",
        "email": "support@legalease.ai",
    },
    license_info={
        "name": "MIT",
    },
)

# ---------------------------------------------------------------------------
# CORS — allow Streamlit (and any localhost origin) to call the API
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(router, tags=["Documents"])


# ---------------------------------------------------------------------------
# Root redirect
# ---------------------------------------------------------------------------

@app.get("/", tags=["Root"])
async def root() -> dict:
    """API root — returns a welcome message and docs link."""
    return {
        "message": "Welcome to LegalEase AI API",
        "docs": "/docs",
        "health": "/health",
    }
