"""FastAPI application for resume parsing API."""

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure the repository root (containing `backend/`) is importable regardless of
# where uvicorn is started from (prevents PIPELINE_UNAVAILABLE in /parse).
_REPO_ROOT = Path(__file__).resolve().parents[2]
if (_REPO_ROOT / "backend").exists():
    sys.path.insert(0, str(_REPO_ROOT))

from .routes import router

app = FastAPI(title="ResumeAI API", version="1.0.0")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default
        "http://localhost:3000",  # Alternative React dev port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"ok": True}

