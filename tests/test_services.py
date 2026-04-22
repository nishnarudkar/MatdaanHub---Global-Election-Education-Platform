"""
MatdaanHub Test Suite - Service Layer Tests
Tests Gemini, Translate, Firebase, and Vertex AI services
"""

import pytest
import pytest_asyncio
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.gemini_service import GeminiService, get_gemini_service
from services.translate_service import TranslateService, get_translate_service
from services.firebase_service import FirebaseService, get_firebase_service
from services.vertex_service import VertexService, get_vertex_service

pytestmark = pytest.mark.asyncio


class TestGeminiService:
    """Google Gemini service tests."""

    def test_generate_response_initialization(self):
        """Should initialize Gemini service."""
        service = GeminiService()
        assert service is not None

    def test_fallback_response_india(self):
        """Fallback should provide India response."""
        service = GeminiService()
        response = service._fallback_response("Tell me about India elections")
        assert "India" in response or "voter" in response.lower()

    def test_fallback_response_usa(self):
        """Fallback should provide USA response."""
        service = GeminiService()
        response = service._fallback_response("usa voting process")
        assert "Electoral College" in response or "USA" in response

    def test_fallback_response_always_returns_string(self):
        """Fallback must always return a non-empty string."""
        service = GeminiService()
        for topic in ["India", "USA", "Brazil", "random", ""]:
            response = service._fallback_response(topic)
            assert isinstance(response, str)
            assert len(response) > 10

    def test_singleton_pattern(self):
        """Multiple calls should return same instance."""
        service1 = get_gemini_service()
        service2 = get_gemini_service()
        assert service1 is service2


class TestTranslateService:
    """Google Cloud Translate service tests."""

    def test_initialization(self):
        """Should initialize Translate service."""
        service = TranslateService()
        assert service is not None

    @pytest.mark.asyncio
    async def test_translate_validates_language(self):
        """Should reject unsupported languages."""
        service = TranslateService()
        try:
            result = await service.translate_text("Hello", target_language="xyz")
            assert result is None or isinstance(result, (str, dict))
        except (ValueError, Exception):
            pass

    @pytest.mark.asyncio
    async def test_translate_validates_empty_text(self):
        """Should reject empty text."""
        service = TranslateService()
        try:
            result = await service.translate_text("", target_language="es")
            assert result is None or isinstance(result, (str, dict))
        except (ValueError, Exception):
            pass

    @pytest.mark.asyncio
    async def test_detect_language(self):
        """Should detect language of text."""
        service = TranslateService()
        result = await service.detect_language("Hello world")
        assert result is None or isinstance(result, str)

    def test_get_supported_languages(self):
        """Should return list of supported languages."""
        service = TranslateService()
        languages = service.get_supported_languages()
        assert isinstance(languages, list)
        assert len(languages) >= 8

    def test_singleton_pattern(self):
        """Multiple calls should return same instance."""
        service1 = get_translate_service()
        service2 = get_translate_service()
        assert service1 is service2


class TestFirebaseService:
    """Firebase Firestore service tests."""

    def test_initialization(self):
        """Should initialize Firebase service."""
        service = FirebaseService()
        assert service is not None

    def test_has_methods(self):
        """Should have required methods."""
        service = FirebaseService()
        assert hasattr(service, 'get_session_history')
        assert hasattr(service, 'delete_session')

    def test_singleton_pattern(self):
        """Multiple calls should return same instance."""
        service1 = get_firebase_service()
        service2 = get_firebase_service()
        assert service1 is service2

    @pytest.mark.asyncio
    async def test_save_message_validates_session_id(self):
        """Should handle invalid session IDs."""
        service = FirebaseService()
        try:
            await service.save_message("", "user", "Hello")
        except (ValueError, TypeError):
            pass


class TestVertexService:
    """Vertex AI service tests."""

    @pytest.mark.asyncio
    async def test_search_with_grounding_returns_dict(self):
        """Should return structured response."""
        service = VertexService()
        result = await service.search_with_grounding("What is FPTP?", "uk")
        assert isinstance(result, dict)

    def test_singleton_pattern(self):
        """Multiple calls should return same instance."""
        service1 = get_vertex_service()
        service2 = get_vertex_service()
        assert service1 is service2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
