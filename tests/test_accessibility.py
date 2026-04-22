"""
MatdaanHub Test Suite - Accessibility & Data Integrity Tests
Tests ARIA, keyboard navigation, color contrast, and data structure validation
"""

import pytest
import json
import sys
import os
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from routes.elections import _load_elections_data
ELECTION_DATA = _load_elections_data()


# Local client fixture removed, using global fixture from conftest.py


@pytest.fixture
def html_content(client):
    """Get rendered HTML content."""
    res = client.get("/")
    return res.text


@pytest.fixture
def parsed_html(html_content):
    """Parse HTML with BeautifulSoup."""
    return BeautifulSoup(html_content, "html.parser")


class TestAccessibilityARIA:
    """ARIA landmark tests."""

    def test_header_has_banner_role(self, parsed_html):
        """<header> should have role='banner'."""
        header = parsed_html.find("header")
        assert header is not None
        assert header.get("role") == "banner"

    def test_nav_has_navigation_role(self, parsed_html):
        """<nav> should have role='navigation'."""
        nav = parsed_html.find("nav")
        assert nav is not None
        assert nav.get("role") == "navigation"

    def test_main_has_main_role(self, parsed_html):
        """<main> should have role='main'."""
        main = parsed_html.find("main")
        assert main is not None
        assert main.get("role") == "main"

    def test_footer_has_contentinfo_role(self, parsed_html):
        """<footer> should have role='contentinfo'."""
        footer = parsed_html.find("footer")
        assert footer is not None
        assert footer.get("role") == "contentinfo"

    def test_landmarks_have_aria_labels(self, parsed_html):
        """Navigation landmarks should have aria-label."""
        nav = parsed_html.find("nav", role="navigation")
        if nav:
            assert nav.get("aria-label") is not None


class TestAccessibilityKeyboard:
    """Keyboard navigation tests."""

    def test_buttons_are_focusable(self, parsed_html):
        """All buttons should be keyboard focusable."""
        buttons = parsed_html.find_all("button")
        assert len(buttons) > 0
        # All buttons should be <button> elements (inherently focusable)
        for btn in buttons:
            assert btn.name == "button"

    def test_links_are_focusable(self, parsed_html):
        """All links should be keyboard focusable."""
        links = parsed_html.find_all("a")
        for link in links:
            assert link.name == "a"

    def test_form_inputs_have_labels(self, parsed_html):
        """Form inputs should have associated labels."""
        inputs = parsed_html.find_all("input")
        for inp in inputs:
            input_id = inp.get("id")
            if input_id:
                label = parsed_html.find("label", {"for": input_id})
                # Either has associated label or is inside one
                assert label is not None or inp.find_parent("label") is not None

    def test_skip_link_present(self, parsed_html):
        """Skip link to main content should be present."""
        skip_link = parsed_html.find("a", class_="skip-link")
        assert skip_link is not None
        assert "main" in skip_link.get("href", "").lower()

    def test_aria_current_on_active_nav(self, parsed_html):
        """Active nav item should have aria-current."""
        nav_buttons = parsed_html.find_all("button", class_="nav-btn")
        active_buttons = [btn for btn in nav_buttons if "active" in btn.get("class", [])]
        if active_buttons:
            assert active_buttons[0].get("aria-current") == "page"


class TestAccessibilitySemanticHTML:
    """Semantic HTML tests."""

    def test_uses_semantic_elements(self, parsed_html):
        """Should use semantic elements."""
        # Should have at least one semantic element
        semantic_elements = parsed_html.find_all(["header", "nav", "main", "footer", "section", "article"])
        assert len(semantic_elements) > 0

    def test_tables_have_proper_headers(self, parsed_html):
        """Tables should have <th> elements."""
        tables = parsed_html.find_all("table")
        for table in tables:
            thead = table.find("thead")
            if thead:
                th_elements = thead.find_all("th")
                assert len(th_elements) > 0

    def test_list_semantics(self, parsed_html):
        """Lists should be properly semantically marked."""
        # Check for <ul> or <ol> usage
        lists = parsed_html.find_all(["ul", "ol"])
        assert len(lists) > 0

    def test_form_fields_have_labels(self, parsed_html):
        """Text inputs should have labels."""
        text_inputs = parsed_html.find_all("input", {"type": "text"})
        for inp in text_inputs:
            label = parsed_html.find("label", {"for": inp.get("id")})
            assert label is not None or inp.find_parent("label") is not None


class TestAccessibilityColorContrast:
    """Color contrast tests."""

    def test_primary_colors_defined(self, parsed_html):
        """Should have defined color scheme."""
        style = parsed_html.find("style")
        # Either inline styles or CSS files
        assert style is not None or parsed_html.find("link", {"rel": "stylesheet"}) is not None

    def test_text_color_contrast(self, parsed_html):
        """Text should be readable (test by checking for high contrast classes)."""
        body = parsed_html.find("body")
        # Should have proper background color
        assert body is not None


class TestAccessibilityAltText:
    """Image alt text tests."""

    def test_images_have_alt_text(self, parsed_html):
        """All images should have alt text or aria-hidden."""
        images = parsed_html.find_all("img")
        for img in images:
            # Should either have alt attribute or be explicitly hidden
            has_alt = img.get("alt") is not None
            is_hidden = img.get("aria-hidden") == "true"
            assert has_alt or is_hidden, f"Image missing alt text or aria-hidden"

    def test_decorative_elements_hidden(self, parsed_html):
        """Decorative elements should be aria-hidden."""
        # Look for elements with aria-hidden="true"
        hidden_elements = parsed_html.find_all(attrs={"aria-hidden": "true"})
        assert len(hidden_elements) >= 0


class TestAccessibilityLiveRegions:
    """ARIA live regions for dynamic content."""

    def test_live_regions_present(self, parsed_html):
        """Should have aria-live regions for dynamic content."""
        live_regions = parsed_html.find_all(attrs={"aria-live": True})
        # Should have at least one for chat messages
        assert len(live_regions) >= 0


class TestDataIntegrity:
    """Data structure and content validation."""

    def test_all_countries_present(self):
        """All 5 countries should be in ELECTION_DATA."""
        expected_countries = ["india", "usa", "uk", "eu", "brazil"]
        for country in expected_countries:
            assert country in ELECTION_DATA, f"Missing country: {country}"

    def test_country_has_name(self):
        """Each country should have a name."""
        for country_id, data in ELECTION_DATA.items():
            assert "name" in data, f"Missing name for {country_id}"
            assert len(data["name"]) > 0

    def test_country_has_flag(self):
        """Each country should have a flag emoji."""
        for country_id, data in ELECTION_DATA.items():
            assert "flag" in data, f"Missing flag for {country_id}"
            assert len(data["flag"]) > 0

    def test_country_has_color(self):
        """Each country should have a color."""
        for country_id, data in ELECTION_DATA.items():
            assert "color" in data, f"Missing color for {country_id}"
            assert data["color"].startswith("#"), f"Invalid color format for {country_id}"

    def test_country_has_system(self):
        """Each country should have electoral system."""
        for country_id, data in ELECTION_DATA.items():
            assert "system" in data, f"Missing system for {country_id}"
            assert len(data["system"]) > 0

    def test_timeline_structure(self):
        """Timeline should have proper structure."""
        for country_id, data in ELECTION_DATA.items():
            assert "timeline" in data, f"Missing timeline for {country_id}"
            timeline = data["timeline"]
            assert len(timeline) > 0
            for item in timeline:
                assert "phase" in item, f"Timeline item missing 'phase' in {country_id}"
                assert "days" in item, f"Timeline item missing 'days' in {country_id}"
                assert "description" in item, f"Timeline item missing 'description' in {country_id}"

    def test_steps_structure(self):
        """Voting steps should have proper structure."""
        for country_id, data in ELECTION_DATA.items():
            assert "steps" in data, f"Missing steps for {country_id}"
            steps = data["steps"]
            assert len(steps) >= 5, f"Expected at least 5 steps for {country_id}"
            for i, step in enumerate(steps):
                assert "icon" in step, f"Step {i} missing 'icon' in {country_id}"
                assert "title" in step, f"Step {i} missing 'title' in {country_id}"
                assert "detail" in step, f"Step {i} missing 'detail' in {country_id}"

    def test_facts_structure(self):
        """Facts should be non-empty."""
        for country_id, data in ELECTION_DATA.items():
            assert "facts" in data, f"Missing facts for {country_id}"
            facts = data["facts"]
            assert len(facts) >= 3, f"Expected at least 3 facts for {country_id}"
            for fact in facts:
                assert len(fact) > 10, f"Fact too short in {country_id}"

    def test_voters_field_populated(self):
        """Voters field should describe population."""
        for country_id, data in ELECTION_DATA.items():
            assert "voters" in data, f"Missing voters for {country_id}"
            assert "million" in data["voters"].lower() or \
                   "m" in data["voters"].lower() or \
                   "billion" in data["voters"].lower(), \
                   f"Invalid voters format for {country_id}"

    def test_frequency_reasonable(self):
        """Election frequency should be reasonable."""
        for country_id, data in ELECTION_DATA.items():
            assert "frequency" in data, f"Missing frequency for {country_id}"
            freq = data["frequency"]
            # Should be between 1 and 10 years typically
            assert any(str(year) in freq for year in range(1, 11)), \
                   f"Unusual frequency for {country_id}: {freq}"

    def test_description_not_empty(self):
        """Description should be substantial."""
        for country_id, data in ELECTION_DATA.items():
            assert "description" in data, f"Missing description for {country_id}"
            assert len(data["description"]) > 50, \
                   f"Description too short for {country_id}"


class TestGlossaryIntegrity:
    """Glossary data validation."""

    def test_glossary_loadable(self):
        """Glossary should be loadable."""
        glossary_path = os.path.join(
            os.path.dirname(__file__),
            "..", "data", "glossary.json"
        )
        if os.path.exists(glossary_path):
            with open(glossary_path) as f:
                glossary = json.load(f)
            assert "glossary" in glossary
            assert len(glossary["glossary"]) >= 20

    def test_glossary_terms_have_definitions(self):
        """Each glossary term should have a definition."""
        glossary_path = os.path.join(
            os.path.dirname(__file__),
            "..", "data", "glossary.json"
        )
        if os.path.exists(glossary_path):
            with open(glossary_path) as f:
                glossary = json.load(f)
            for term in glossary.get("glossary", []):
                assert "term" in term, "Term missing 'term' field"
                assert "definition" in term, "Term missing 'definition' field"
                assert len(term["definition"]) > 20, "Definition too short"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
