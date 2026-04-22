"""
Shared test fixtures for MatdaanHub FastAPI tests.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from main import app
from services.firebase_service import get_firebase_service

# ── Default mock election data used by most tests ──
def _make_country(country_id):
    return {
        "name": country_id.capitalize(),
        "flag": "🏳️",
        "system": "Parliamentary Democracy",
        "color": "#c9a84c",
        "voters": "100M eligible voters",
        "body": "Election Commission",
        "description": "A democratic nation with free and fair elections.",
        "frequency": "Every 5 years",
        "timeline": [{"phase": "Nomination", "days": "30", "description": "Candidates file."}],
        "steps": [
            {"icon": "1️⃣", "title": "Register", "detail": "Register to vote."},
            {"icon": "2️⃣", "title": "Get ID", "detail": "Obtain voter ID."},
            {"icon": "3️⃣", "title": "Find Booth", "detail": "Locate your polling booth."},
            {"icon": "4️⃣", "title": "Vote", "detail": "Cast your ballot."},
            {"icon": "5️⃣", "title": "Verify", "detail": "Check your vote is counted."},
        ],
        "facts": ["Fact one about elections.", "Fact two about elections.", "Fact three about elections."],
    }

SUPPORTED_COUNTRIES = ["india", "usa", "uk", "eu", "brazil"]

def _make_firebase_mock():
    """Build a fully-wired async mock for FirebaseService."""
    mock = MagicMock()
    # get_all_elections returns a dict of all countries
    mock.get_all_elections = AsyncMock(return_value={
        c: _make_country(c) for c in SUPPORTED_COUNTRIES
    })
    # get_election_data returns a single country (will be overridden per-test if needed)
    mock.get_election_data = AsyncMock(side_effect=lambda cid: _make_country(cid))
    # get_glossary returns 21 dummy terms (enough to pass the >20 assertion)
    mock.get_glossary = AsyncMock(return_value=[
        {"term": f"Term{i}", "definition": f"Definition number {i} explaining the concept."}
        for i in range(21)
    ])
    mock.get_glossary_term = AsyncMock(return_value=None)
    mock.store_chat_message = AsyncMock(return_value=None)
    mock.get_chat_history = AsyncMock(return_value=[])
    return mock


@pytest.fixture
def mock_firebase_instance():
    """Returns a shared async-capable firebase mock."""
    return _make_firebase_mock()


@pytest.fixture
def client(mock_firebase_instance):
    """Provides a FastAPI test client with Firebase dependency overridden."""
    app.dependency_overrides[get_firebase_service] = lambda: mock_firebase_instance
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def mock_firebase(mock_firebase_instance):
    """Expose the firebase mock so tests can customise return values."""
    return mock_firebase_instance


@pytest.fixture
def mock_gemini(mocker):
    """Mock the Gemini service."""
    mock_service = mocker.patch("routes.chat.get_gemini_service")
    return mock_service.return_value


@pytest.fixture
def mock_translate(mocker):
    """Mock the Translate service."""
    mock_service = mocker.patch("routes.translate.get_translate_service")
    return mock_service.return_value
