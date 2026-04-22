"""
Google Vertex AI Search Service
Handles grounded search and fact-checked election Q&A
"""

import logging
from typing import Optional
from config import (
    VERTEX_PROJECT_ID,
    VERTEX_LOCATION,
    VERTEX_GROUNDING_ENABLED,
)

logger = logging.getLogger(__name__)

try:
    from google.cloud import aiplatform
    from google.cloud.aiplatform import generative_models

    AIPLATFORM_AVAILABLE = True
except ImportError:
    AIPLATFORM_AVAILABLE = False
    logger.warning("google-cloud-aiplatform not installed. Vertex AI grounding will be unavailable.")


class VertexService:
    """
    Wrapper for Google Vertex AI Search and grounding.
    Provides fact-checked, sourced election Q&A using Google Search grounding.
    """

    def __init__(self) -> None:
        """Initialize Vertex AI service if enabled."""
        self.available: bool = False
        self.call_count: int = 0

        if not AIPLATFORM_AVAILABLE:
            logger.warning("Vertex AI service not available: google-cloud-aiplatform not installed")
            return

        if not VERTEX_GROUNDING_ENABLED:
            logger.info("Vertex AI grounding disabled: VERTEX_GROUNDING_ENABLED=false")
            return

        if not VERTEX_PROJECT_ID:
            logger.warning("Vertex AI service not available: GOOGLE_CLOUD_PROJECT not set")
            return

        try:
            aiplatform.init(project=VERTEX_PROJECT_ID, location=VERTEX_LOCATION)
            self.available = True
            logger.info(f"Vertex AI service initialized for project: {VERTEX_PROJECT_ID}")
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI service: {e}")
            self.available = False

    async def search_with_grounding(
        self,
        query: str,
        country: Optional[str] = None,
    ) -> dict:
        """
        Search for election information with Google Search grounding asynchronously.
        Results include cited sources for fact-checking.

        Args:
            query: The election question/search query
            country: Optional country context (e.g., 'india', 'usa')

        Returns:
            Dictionary with 'answer', 'sources', 'grounded', and other metadata
        """
        if not self.available:
            logger.warning("Grounded search requested but service unavailable")
            return {
                "answer": None,
                "sources": [],
                "grounded": False,
                "error": "Vertex AI grounding service unavailable",
            }

        try:
            self.call_count += 1

            # Build context-aware query
            search_query = query
            if country:
                search_query = f"{country} election {query}"

            # TODO: Implement actual Vertex AI Search when credentials are available
            # For now, return structured response format
            logger.info(f"Grounded search would query: {search_query} (call #{self.call_count})")

            # Placeholder for actual grounding implementation
            return {
                "answer": None,
                "sources": [],
                "grounded": False,
                "message": "Vertex AI grounding not fully configured in this environment",
            }

        except Exception as e:
            logger.error(f"Vertex AI search error: {e}")
            return {
                "answer": None,
                "sources": [],
                "grounded": False,
                "error": str(e),
            }

    def cite_sources(self, sources: list[dict]) -> str:
        """
        Format sources as citations for inclusion in response.

        Args:
            sources: List of source dictionaries with 'title', 'url', etc.

        Returns:
            Formatted citation string
        """
        if not sources:
            return ""

        citations = "\n\n**Sources:**\n"
        for i, source in enumerate(sources[:5], 1):
            title = source.get("title", "Source")
            url = source.get("url", "")
            if url:
                citations += f"{i}. [{title}]({url})\n"
            else:
                citations += f"{i}. {title}\n"

        return citations

    def is_available(self) -> bool:
        """Check if Vertex AI service is available."""
        return self.available

    def get_call_count(self) -> int:
        """Get the number of API calls made."""
        return self.call_count


# Singleton instance
_vertex_service: Optional[VertexService] = None


def get_vertex_service() -> VertexService:
    """Get or create the Vertex AI service instance."""
    global _vertex_service
    if _vertex_service is None:
        _vertex_service = VertexService()
    return _vertex_service
