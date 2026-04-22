"""
MatdaanHub Configuration
All environment variables, constants, and settings
"""

import os
from typing import Optional

# ──────────────────────────────────────────────
# APP CONFIG
# ──────────────────────────────────────────────

SECRET_KEY: str = os.environ.get("SECRET_KEY", "matdaanhub-dev-key-2026-change-in-production")
DEBUG: bool = os.environ.get("DEBUG", "false").lower() == "true"
TESTING: bool = os.environ.get("TESTING", "false").lower() == "true"
PORT: int = int(os.environ.get("PORT", 8080))
HOST: str = os.environ.get("HOST", "0.0.0.0")

# ──────────────────────────────────────────────
# GOOGLE GEMINI API
# ──────────────────────────────────────────────

GEMINI_API_KEY: Optional[str] = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL: str = "gemini-1.5-flash"

# System prompt for Gemini AI
SYSTEM_PROMPT: str = """You are MatdaanHub, a friendly and knowledgeable election education assistant. You help people understand electoral systems, voting processes, timelines, and democratic participation worldwide.

You have deep knowledge about elections in India, the USA, UK, EU, Brazil, and other countries.

Be concise, factual, and engaging. Use emojis sparingly. If asked about a specific country, provide accurate details about their electoral system. Always encourage civic participation.

If asked something outside elections/democracy/voting, politely redirect to your area of expertise.

Keep answers under 200 words unless complex detail is requested."""

# ──────────────────────────────────────────────
# GOOGLE CLOUD TRANSLATE V2
# ──────────────────────────────────────────────

TRANSLATE_ENABLED: bool = os.environ.get("GOOGLE_TRANSLATE_ENABLED", "false").lower() == "true"
SUPPORTED_LANGUAGES: list[str] = ["en", "hi", "ta", "es", "fr", "de", "pt", "ar"]

# ──────────────────────────────────────────────
# VERTEX AI GROUNDING
# ──────────────────────────────────────────────

VERTEX_PROJECT_ID: Optional[str] = os.environ.get("GOOGLE_CLOUD_PROJECT")
VERTEX_LOCATION: str = os.environ.get("VERTEX_LOCATION", "us-central1")
VERTEX_GROUNDING_ENABLED: bool = os.environ.get("VERTEX_GROUNDING_ENABLED", "false").lower() == "true"

# ──────────────────────────────────────────────
# FIREBASE / FIRESTORE
# ──────────────────────────────────────────────

FIREBASE_CREDENTIALS_PATH: Optional[str] = os.environ.get("FIREBASE_CREDENTIALS_PATH")
FIREBASE_ENABLED: bool = os.environ.get("FIREBASE_ENABLED", "false").lower() == "true"
FIRESTORE_CHAT_COLLECTION: str = "chat_sessions"
FIRESTORE_ELECTIONS_COLLECTION: str = "elections"
FIRESTORE_GLOSSARY_COLLECTION: str = "glossary"
CHAT_HISTORY_TTL_HOURS: int = 24

# ──────────────────────────────────────────────
# RATE LIMITING
# ──────────────────────────────────────────────

RATELIMIT_ENABLED: bool = True
RATELIMIT_STORAGE_URI: str = os.environ.get("RATELIMIT_STORAGE_URI", "memory://")
CHAT_REQUESTS_PER_MINUTE: int = 20
TRANSLATE_REQUESTS_PER_MINUTE: int = 30
GENERAL_REQUESTS_PER_MINUTE: int = 60

# ──────────────────────────────────────────────
# SECURITY HEADERS
# ──────────────────────────────────────────────

ALLOWED_ORIGINS: list[str] = [
    "http://localhost:8080",
    "http://localhost:5000",
    "http://127.0.0.1:8080",
    "https://matdaanhub.example.com"  # Update with actual Cloud Run URL
]

CORS_HEADERS: dict[str, str] = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "SAMEORIGIN",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}

# Content Security Policy
CSP_HEADER: str = (
    "default-src 'self'; "
    "script-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
    "style-src 'self' https://fonts.googleapis.com 'unsafe-inline'; "
    "font-src 'self' https://fonts.gstatic.com; "
    "img-src 'self' data: https:; "
    "connect-src 'self' https://generativelanguage.googleapis.com https://translation.googleapis.com; "
    "frame-ancestors 'none';"
)

# ──────────────────────────────────────────────
# INPUT VALIDATION
# ──────────────────────────────────────────────

MAX_MESSAGE_LENGTH: int = 500
MAX_TEXT_TRANSLATION_LENGTH: int = 5000
MIN_MESSAGE_LENGTH: int = 1
ALLOWED_COUNTRIES: list[str] = ["india", "usa", "uk", "eu", "brazil", "south_africa", "australia", "japan", "mexico", "canada"]

# ──────────────────────────────────────────────
# DATA FILES
# ──────────────────────────────────────────────

DATA_DIR: str = os.path.join(os.path.dirname(__file__), "data")
ELECTIONS_DATA_FILE: str = os.path.join(DATA_DIR, "elections.json")
GLOSSARY_DATA_FILE: str = os.path.join(DATA_DIR, "glossary.json")

# ──────────────────────────────────────────────
# LOGGING
# ──────────────────────────────────────────────

LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")
LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ──────────────────────────────────────────────
# PERFORMANCE
# ──────────────────────────────────────────────

CHAT_HISTORY_MAX_LENGTH: int = 8  # Keep last 8 messages for context
RESPONSE_TIMEOUT_SECONDS: int = 60
CACHE_TTL_SECONDS: int = 3600
