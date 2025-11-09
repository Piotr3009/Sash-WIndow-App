"""FastAPI application entry point for the Sash Window web backend."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.api import calculate, exports

APP_TITLE = "Skylon Elements – Sash Window API"
APP_DESCRIPTION = (
    "Professional sash window calculation and export API migrated from the "
    "PyQt6 desktop application."
)

limiter = Limiter(key_func=get_remote_address, default_limits=["120/minute"])


def _rate_limit_exceeded_handler(request, exc):  # pragma: no cover - framework integration
    return limiter._rate_limit_exceeded_handler(request, exc)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(title=APP_TITLE, description=APP_DESCRIPTION, version="1.0.0")
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        max_age=86400,
    )

    app.include_router(calculate.router, prefix="/api")
    app.include_router(exports.router, prefix="/api")

    @app.get("/api/health", tags=["health"], summary="Health check")
    def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
