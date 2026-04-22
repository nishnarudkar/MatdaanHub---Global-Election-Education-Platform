"""
MatdaanHub - Global Election Education Platform
Production-grade FastAPI application with Google AI integration
"""

import os
import logging
import time
from typing import Callable

from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from services.limiter_service import limiter

import config
from routes import (
    health_router,
    elections_router,
    chat_router,
    translate_router
)

# ──────────────────────────────────────────────
# LOGGING CONFIGURATION
# ──────────────────────────────────────────────

logging.basicConfig(
    level=config.LOG_LEVEL,
    format=config.LOG_FORMAT,
)
logger = logging.getLogger(__name__)

# Limiter is now handled in services/limiter_service.py

# ──────────────────────────────────────────────
# MIDDLEWARE
# ──────────────────────────────────────────────

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to apply security headers to all responses."""
    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        
        # Prevent content-type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        # XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # Content Security Policy
        response.headers["Content-Security-Policy"] = config.CSP_HEADER
        # Permissions Policy
        response.headers["Permissions-Policy"] = (
            "accelerometer=(), camera=(), geolocation=(), gyroscope=(), "
            "magnetometer=(), microphone=(), payment=(), usb=()"
        )
        
        return response

# ──────────────────────────────────────────────
# APP INITIALIZATION
# ──────────────────────────────────────────────

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    app = FastAPI(
        title="MatdaanHub API",
        description="Global Election Education Platform API",
        version="1.0.0",
        docs_url="/api/docs" if config.DEBUG else None,
        redoc_url="/api/redoc" if config.DEBUG else None,
    )

    # Rate Limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Security Middleware
    app.add_middleware(SecurityHeadersMiddleware)

    # Static Files & Templates
    app.mount("/static", StaticFiles(directory="static"), name="static")
    templates = Jinja2Templates(directory="templates")

    # ── Routes ──

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        """Render main SPA template."""
        from services.firebase_service import get_firebase_service
        firebase_service = get_firebase_service()
        
        elections_data = await firebase_service.get_all_elections()
        countries = {}
        for key, data in elections_data.items():
            countries[key] = {
                "name": data.get("name"),
                "flag": data.get("flag"),
                "system": data.get("system"),
                "color": data.get("color"),
            }

        return templates.TemplateResponse(
            request,
            "index.html", 
            {"countries": countries}
        )

    # Register routers
    app.include_router(health_router, tags=["System"])
    app.include_router(elections_router, tags=["Elections"])
    app.include_router(chat_router, tags=["AI Chat"])
    app.include_router(translate_router, tags=["Translation"])

    logger.info("FastAPI application created and configured")
    return app

app = create_app()

# ──────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    port = config.PORT
    logger.info(f"Starting MatdaanHub FastAPI server on {config.HOST}:{port}")
    uvicorn.run(
        "main:app", 
        host=config.HOST, 
        port=port, 
        reload=config.DEBUG,
        log_level="info"
    )
