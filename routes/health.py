"""
Health Check Route
Provides service status endpoint for load balancers and monitoring
"""

import logging
from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint for Cloud Run and monitoring systems.

    Returns:
        JSON response with service status
    """
    return {
        "status": "ok",
        "service": "MatdaanHub",
        "version": "1.0.0",
        "component": "api-server",
    }
