"""
Shared test fixtures for MatdaanHub FastAPI tests.
"""

import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    """Provides a FastAPI test client."""
    with TestClient(app) as c:
        yield c

@pytest.fixture
def mock_gemini(mocker):
    """Mock the Gemini service."""
    mock_service = mocker.patch("routes.chat.get_gemini_service")
    return mock_service.return_value

@pytest.fixture
def mock_firebase(mocker):
    """Mock the Firebase service."""
    mock_service = mocker.patch("routes.chat.get_firebase_service")
    return mock_service.return_value

@pytest.fixture
def mock_translate(mocker):
    """Mock the Translate service."""
    mock_service = mocker.patch("routes.translate.get_translate_service")
    return mock_service.return_value
