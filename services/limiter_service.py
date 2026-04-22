"""
Shared rate limiter service for FastAPI routers.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize the limiter
# Note: storage_uri could be configured from config.py if needed (e.g., redis)
limiter = Limiter(key_func=get_remote_address)
