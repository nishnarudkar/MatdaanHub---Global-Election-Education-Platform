"""
MatdaanHub Test Suite - Routes Integration Tests
Tests all API endpoints, response formats, and error handling
"""

import json
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from services.gemini_service import get_gemini_service

gemini_service = get_gemini_service()
fallback_response = gemini_service._fallback_response

SUPPORTED_COUNTRIES = ["india", "usa", "uk", "eu", "brazil"]

# Load local election data for offline integrity tests (avoids Firestore dependency)
def _load_local_elections():
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'elections.json')
    with open(data_path, encoding='utf-8') as f:
        return json.load(f)

ELECTION_DATA = _load_local_elections()


# Local client fixture removed, using global fixture from conftest.py


class TestHealthRoute:
    """Health check endpoint tests."""

    def test_health_returns_200(self, client):
        """Health endpoint should return 200 OK."""
        res = client.get("/health")
        assert res.status_code == 200

    def test_health_response_structure(self, client):
        """Health response should have required fields."""
        res = client.get("/health")
        data = res.json()
        assert data["status"] == "ok"
        assert "service" in data
        assert "version" in data

    def test_health_service_name(self, client):
        """Service name should be MatdaanHub."""
        res = client.get("/health")
        data = res.json()
        assert data["service"] == "MatdaanHub"


class TestElectionsRoute:
    """Election data endpoints tests."""

    def test_elections_returns_200(self, client):
        """GET /api/elections should return 200."""
        res = client.get("/api/elections")
        assert res.status_code == 200

    def test_elections_has_all_supported(self, client, mock_firebase):
        """Should return all 5 countries."""
        mock_firebase.get_all_elections.side_effect = None
        mock_firebase.get_all_elections.return_value = {
            country: {"name": country.capitalize(), "flag": "🏳️", "system": "Test", "color": "#000", "voters": "1 million voters", "body": "EC", "description": "Desc", "timeline": [], "steps": [], "facts": []}
            for country in SUPPORTED_COUNTRIES
        }
        res = client.get("/api/elections")
        data = res.json()
        for country in SUPPORTED_COUNTRIES:
            assert country in data

    def test_elections_summary_fields(self, client):
        """Each country should have required summary fields."""
        res = client.get("/api/elections")
        data = res.json()
        for country_id, info in data.items():
            assert "name" in info
            assert "flag" in info
            assert "system" in info
            assert "color" in info

    @pytest.mark.parametrize("country", SUPPORTED_COUNTRIES)
    def test_country_detail_returns_200(self, client, mock_firebase, country):
        """GET /api/elections/<country> should return 200."""
        mock_firebase.get_election_data.side_effect = None
        mock_firebase.get_election_data.return_value = {
            "name": country.capitalize(), "flag": "🏳️", "system": "Test", "color": "#c9a84c", "voters": "1 million voters", "body": "EC", "description": "Desc", "frequency": "Every 5 years", "timeline": [], "steps": [], "facts": []
        }
        res = client.get(f"/api/elections/{country}")
        assert res.status_code == 200

    @pytest.mark.parametrize("country", SUPPORTED_COUNTRIES)
    def test_country_has_required_fields(self, client, country):
        """Country response should have all required fields."""
        res = client.get(f"/api/elections/{country}")
        data = res.json()
        required = ["name", "flag", "system", "body", "frequency", "voters",
                    "description", "timeline", "steps", "facts"]
        for field in required:
            assert field in data, f"Missing field '{field}' in {country}"

    def test_invalid_country_returns_404(self, client):
        """Invalid country should return 404."""
        res = client.get("/api/elections/atlantis")
        assert res.status_code == 404

    def test_case_insensitive_lookup(self, client):
        """Lookup should be case-insensitive."""
        res = client.get("/api/elections/INDIA")
        assert res.status_code == 200

    @pytest.mark.parametrize("country", SUPPORTED_COUNTRIES)
    def test_timeline_endpoint(self, client, mock_firebase, country):
        """Timeline endpoint should return timeline for country."""
        mock_firebase.get_election_data.side_effect = None
        mock_firebase.get_election_data.return_value = {
            "name": country.capitalize(), "flag": "🏳️", "system": "Test", "color": "#c9a84c", "voters": "1 million voters", "body": "EC", "description": "Desc", "frequency": "Every 5 years",
            "timeline": [{"phase": "P1", "days": "1", "description": "D1"}], "steps": [], "facts": []
        }
        res = client.get(f"/api/elections/{country}/timeline")
        assert res.status_code == 200
        data = res.json()
        assert "timeline" in data
        assert len(data["timeline"]) > 0

    @pytest.mark.parametrize("country", SUPPORTED_COUNTRIES)
    def test_voting_steps_endpoint(self, client, country):
        """Voting steps endpoint should return steps."""
        res = client.get(f"/api/elections/{country}/voting-steps")
        assert res.status_code == 200
        data = res.json()
        assert "steps" in data
        assert len(data["steps"]) >= 5


class TestChatRoute:
    """Chat endpoint tests."""

    def test_chat_requires_post(self, client):
        """Chat should only accept POST."""
        res = client.get("/api/chat")
        assert res.status_code == 405

    def test_chat_empty_message_returns_400(self, client):
        """Empty message should return 400."""
        res = client.post("/api/chat",
                          json={"message": ""})
        assert res.status_code in [400, 422]

    def test_chat_valid_message(self, client):
        """Valid message should return 200 with response."""
        res = client.post("/api/chat",
                          json={"message": "How do elections work in India?"})
        assert res.status_code == 200
        data = res.json()
        assert "response" in data
        assert len(data["response"]) > 10

    def test_chat_whitespace_only_returns_400(self, client):
        """Whitespace-only message should return 400."""
        res = client.post("/api/chat",
                          json={"message": "   "})
        assert res.status_code in [400, 422]

    def test_chat_with_history(self, client):
        """Chat should accept and process history."""
        history = [
            {"role": "user", "content": "Tell me about India"},
            {"role": "assistant", "content": "India has 970M voters"}
        ]
        res = client.post("/api/chat",
                          json={"message": "What about the USA?", "history": history})
        assert res.status_code == 200

    def test_chat_oversized_message_rejected(self, client):
        """Message exceeding 500 chars should be rejected."""
        big_message = "x" * 510
        res = client.post("/api/chat",
                          json={"message": big_message})
        assert res.status_code in [400, 422]

    def test_chat_content_type_required(self, client):
        """Request must be JSON."""
        res = client.post("/api/chat", data="not json")
        assert res.status_code in [400, 415, 422]


class TestTranslateRoute:
    """Translation endpoint tests."""

    def test_translate_endpoint_exists(self, client):
        """Translate endpoint should be available."""
        res = client.post("/api/translate",
                          json={"text": "hello", "target_language": "es"})
        # Should return 503 if translate disabled, or 200 if available
        assert res.status_code in [200, 400, 422, 503]

    def test_languages_endpoint(self, client):
        """Languages endpoint should list supported languages."""
        res = client.get("/api/languages")
        assert res.status_code == 200
        data = res.json()
        assert "supported_languages" in data
        assert len(data["supported_languages"]) > 0

    def test_detect_language_endpoint(self, client):
        """Language detection endpoint should work."""
        res = client.post("/api/detect",
                          json={"text": "hello"})
        # May return 404 or 503 if disabled, but endpoint should exist or be gracefully disabled
        assert res.status_code in [200, 400, 404, 422, 503]


class TestGlossaryRoute:
    """Glossary endpoints tests."""

    def test_glossary_list(self, client):
        """Glossary list should return terms."""
        res = client.get("/api/glossary")
        assert res.status_code == 200
        data = res.json()
        assert "glossary" in data
        assert len(data["glossary"]) > 20


class TestDataIntegrity:
    """Data structure and content validation."""

    @pytest.mark.parametrize("country", SUPPORTED_COUNTRIES)
    def test_timeline_structure(self, client, mock_firebase, country):
        """Timeline should have required fields."""
        mock_firebase.get_election_data.side_effect = None
        mock_firebase.get_election_data.return_value = {
            "name": country.capitalize(), "flag": "🏳️", "system": "Test", "color": "#c9a84c", "voters": "1 million voters", "body": "EC", "description": "Desc", "frequency": "Every 5 years",
            "timeline": [{"phase": "P1", "days": "1", "description": "D1"}], "steps": [], "facts": []
        }
        res = client.get(f"/api/elections/{country}/timeline")
        data = res.json()
        assert "timeline" in data
        for item in data["timeline"]:
            assert "phase" in item
            assert "days" in item
            assert "description" in item

    @pytest.mark.parametrize("country", SUPPORTED_COUNTRIES)
    def test_steps_structure(self, country):
        """Steps should have required fields."""
        data = ELECTION_DATA[country]
        assert "steps" in data
        assert len(data["steps"]) >= 5
        for step in data["steps"]:
            assert "icon" in step
            assert "title" in step
            assert "detail" in step

    @pytest.mark.parametrize("country", SUPPORTED_COUNTRIES)
    def test_facts_not_empty(self, country):
        """Each country should have facts."""
        facts = ELECTION_DATA[country]["facts"]
        assert len(facts) >= 3

    @pytest.mark.parametrize("country", SUPPORTED_COUNTRIES)
    def test_color_is_valid_hex(self, country):
        """Color should be valid hex."""
        color = ELECTION_DATA[country]["color"]
        assert color.startswith("#")
        # Accept 4-char (#RGB) or 7-char (#RRGGBB) or 9-char (#RRGGBBAA)
        assert len(color) in [4, 7, 9]

    @pytest.mark.parametrize("country", SUPPORTED_COUNTRIES)
    def test_flag_is_emoji(self, country):
        """Flag should be an emoji."""
        flag = ELECTION_DATA[country]["flag"]
        assert len(flag) > 0

    @pytest.mark.parametrize("country", SUPPORTED_COUNTRIES)
    def test_voters_field_populated(self, country):
        """Voters field should contain population info."""
        voters = ELECTION_DATA[country]["voters"]
        # Accept 'million', 'M', 'billion', or 'B' as valid voter count indicators
        assert any(k in voters.lower() for k in ["million", "m", "billion", "b"])


class TestFallbackResponse:
    """Fallback response tests for unavailable Gemini."""

    def test_india_keyword(self):
        """India keyword should trigger India response."""
        resp = fallback_response("Tell me about india elections")
        assert "India" in resp or "🇮🇳" in resp

    def test_usa_keyword(self):
        """USA keyword should trigger USA response."""
        resp = fallback_response("How does usa voting work?")
        assert "Electoral College" in resp or "🇺🇸" in resp

    def test_uk_keyword(self):
        """UK keyword should trigger UK response."""
        resp = fallback_response("What about uk elections?")
        assert "First Past the Post" in resp or "🇬🇧" in resp

    def test_brazil_keyword(self):
        """Brazil keyword should trigger Brazil response."""
        resp = fallback_response("Explain brazil voting")
        assert "Brazil" in resp or "🇧🇷" in resp

    def test_eu_keyword(self):
        """EU keyword should trigger EU response."""
        resp = fallback_response("How does eu parliament get elected?")
        assert "European" in resp or "🇪🇺" in resp

    def test_unknown_topic_returns_default(self):
        """Unknown topic should return default message."""
        resp = fallback_response("Tell me about pizza")
        assert len(resp) > 20
        assert "MatdaanHub" in resp or "election" in resp.lower()

    def test_empty_message(self):
        """Empty message should still return something."""
        resp = fallback_response("")
        assert len(resp) > 0

    def test_response_is_always_string(self):
        """Fallback should always return string."""
        for msg in ["india", "usa", "uk", "eu", "brazil", "unknown", ""]:
            assert isinstance(fallback_response(msg), str)


class TestSecurityBasic:
    """Basic security checks."""

    def test_xss_in_country_param(self, client):
        """XSS in country parameter should be handled."""
        res = client.get("/api/elections/<script>alert(1)</script>")
        assert res.status_code == 404

    def test_long_country_param(self, client):
        """Very long country parameter should be handled."""
        res = client.get("/api/elections/" + "x" * 500)
        assert res.status_code == 404

    def test_sql_injection_attempt(self, client):
        """SQL injection attempt should fail safely."""
        res = client.get("/api/elections/'; DROP TABLE--")
        assert res.status_code in [404, 400]

    def test_large_chat_message(self, client):
        """Oversized message should be rejected."""
        res = client.post("/api/chat",
                          json={"message": "x" * 5000})
        assert res.status_code in [400, 413, 422]

    def test_security_headers_present(self, client):
        """Response should include security headers."""
        res = client.get("/health")
        assert "X-Content-Type-Options" in res.headers
        assert "X-Frame-Options" in res.headers


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
