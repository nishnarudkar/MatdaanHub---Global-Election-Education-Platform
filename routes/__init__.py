"""
MatdaanHub Routes Package
"""

from .health import router as health_router
from .elections import router as elections_router
from .chat import router as chat_router
from .translate import router as translate_router

__all__ = ["health_router", "elections_router", "chat_router", "translate_router"]
