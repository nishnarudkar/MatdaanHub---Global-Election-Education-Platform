"""
Shared rate limiter service for FastAPI routers.
Uses memory:// by default for local dev.
Set RATELIMIT_STORAGE_URI=redis://host:port in production (e.g. Cloud Memorystore)
to share limits across multiple Cloud Run instances.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
import config

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=config.RATELIMIT_STORAGE_URI,
)
