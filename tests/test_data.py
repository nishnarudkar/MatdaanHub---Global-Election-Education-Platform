"""
MatdaanHub Test Suite - Data Integrity Tests
Comprehensive validation of all data structures and content
"""

import pytest
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def _load_elections_data():
    with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'elections.json'), encoding='utf-8') as f:
        return json.load(f)
ELECTION_DATA = _load_elections_data()


SUPPORTED_COUNTRIES = ["india", "usa", "uk", "eu", "brazil"]
REQUIRED_COUNTRY_FIELDS = [
    "name", "flag", "system", "body", "frequency", "voters",
    "description", "timeline", "steps", "facts", "color"
]
REQUIRED_TIMELINE_FIELDS = ["phase", "days", "description"]
REQUIRED_STEP_FIELDS = ["icon", "title", "detail"]


class TestElectionsDataStructure:
    """Tests for overall elections data structure."""

    def test_all_countries_present(self):
        """All 5 supported countries should exist."""
        for country in SUPPORTED_COUNTRIES:
            assert country in ELECTION_DATA, f"Country {country} missing"

    def test_no_extra_countries(self):
        """Should not have unexpected countries."""
        from config import ALLOWED_COUNTRIES
        for country in ELECTION_DATA.keys():
            assert country in ALLOWED_COUNTRIES, f"Unexpected country: {country}"

    @pytest.mark.parametrize("country", SUPPORTED_COUNTRIES)
    def test_country_is_dict(self, country):
        """Country data should be a dictionary."""
        assert isinstance(ELECTION_DATA[country], dict)

    @pytest.mark.parametrize("country", SUPPORTED_COUNTRIES)
    def test_country_has_all_required_fields(self, country):
        """Country should have all required fields."""
        data = ELECTION_DATA[country]
        for field in REQUIRED_COUNTRY_FIELDS:
            assert field in data, f"Missing field '{field}' in {country}"


class TestCountryBasicInfo:
    """Tests for basic country information."""

    @pytest.mark.parametrize("country", SUPPORTED_COUNTRIES)
    def test_country_name_not_empty(self, country):
        """Country name should not be empty."""
        name = ELECTION_DATA[country]["name"]
        assert len(name) > 0
        assert isinstance(name, str)

    @pytest.mark.parametrize("country", SUPPORTED_COUNTRIES)
    def test_country_flag_is_emoji(self, country):
        """Country flag should be a valid emoji."""
        flag = ELECTION_DATA[country]["flag"]
        assert len(flag) > 0
        # Emoji should be at least 1 character
        assert len(flag) >= 1

    @pytest.mark.parametrize("country", SUPPORTED_COUNTRIES)
    def test_country_system_documented(self, country):
        """Electoral system should be documented."""
        system = ELECTION_DATA[country]["system"]
        assert len(system) > 0
        assert isinstance(system, str)
        # Should contain recognizable system type
        system_lower = system.lower()
        assert any(s in system_lower for s in [
            "parliamentary", "presidential", "mixed", "fptp",
            "proportional", "first past", "direct", "parliament",
            "supranational", "democratic", "union"
        ]), f"Unclear system for {country}: {system}"

    @pytest.mark.parametrize("country", SUPPORTED_COUNTRIES)
    def test_country_color_valid_hex(self, country):
        """Country color should be valid hex."""
        color = ELECTION_DATA[country]["color"]
        assert color.startswith("#"), f"Color not starting with # in {country}"
        # Valid hex colors are #RGB or #RRGGBB
        hex_part = color[1:]
        assert len(hex_part) in [3, 6], f"Invalid hex color in {country}: {color}"
        try:
            int(hex_part, 16)
        except ValueError:
            pytest.fail(f"Invalid hex digits in {country}: {color}")

    @pytest.mark.parametrize("country", SUPPORTED_COUNTRIES)
    def test_country_body_documented(self, country):
        """Governing body should be documented."""
        body = ELECTION_DATA[country]["body"]
        assert len(body) > 0
        assert isinstance(body, str)

    @pytest.mark.parametrize("country", SUPPORTED_COUNTRIES)
    def test_country_frequency_reasonable(self, country):
        """Election frequency should be documented."""
        freq = ELECTION_DATA[country]["frequency"]
        assert len(freq) > 0
        assert isinstance(freq, str)
        # Should contain a number indicating years
        assert any(c.isdigit() for c in freq), f"No year number in frequency for {country}"

    @pytest.mark.parametrize("country", SUPPORTED_COUNTRIES)
    def test_country_voters_format(self, country):
        """Voters field should document population."""
        voters = ELECTION_DATA[country]["voters"]
        assert len(voters) > 0
        assert isinstance(voters, str)
        voters_lower = voters.lower()
        # Should contain size indicator
        assert any(s in voters_lower for s in [
            "million", "m", "billion", "b", "thousand"
        ]), f"Voters field unclear for {country}: {voters}"

    @pytest.mark.parametrize("country", SUPPORTED_COUNTRIES)
    def test_country_description_substantial(self, country):
        """Description should be a meaningful paragraph."""
        desc = ELECTION_DATA[country]["description"]
        assert len(desc) >= 50, f"Description too short for {country}"
        assert isinstance(desc, str)
        # Should contain multiple sentences
        assert "." in desc, f"Description lacks proper sentence structure in {country}"


class TestTimeline:
    """Tests for country timelines."""

    @pytest.mark.parametrize("country", SUPPORTED_COUNTRIES)
    def test_timeline_exists_and_is_list(self, country):
        """Timeline should exist and be a list."""
        timeline = ELECTION_DATA[country].get("timeline", [])
        assert isinstance(timeline, list)
        assert len(timeline) > 0, f"Timeline empty for {country}"

    @pytest.mark.parametrize("country", SUPPORTED_COUNTRIES)
    def test_timeline_has_multiple_phases(self, country):
        """Timeline should have 5+ phases."""
        timeline = ELECTION_DATA[country]["timeline"]
        assert len(timeline) >= 5, f"Timeline has fewer than 5 phases in {country}"

    @pytest.mark.parametrize("country", SUPPORTED_COUNTRIES)
    def test_timeline_items_have_required_fields(self, country):
        """Each timeline item should have required fields."""
        timeline = ELECTION_DATA[country]["timeline"]
        for i, item in enumerate(timeline):
            for field in REQUIRED_TIMELINE_FIELDS:
                assert field in item, \
                    f"Timeline item {i} missing '{field}' in {country}"

    @pytest.mark.parametrize("country", SUPPORTED_COUNTRIES)
    def test_timeline_days_are_numeric(self, country):
        """Timeline days should be numeric."""
        timeline = ELECTION_DATA[country]["timeline"]
        for i, item in enumerate(timeline):
            days = item["days"]
            assert isinstance(days, (int, str)), \
                f"Timeline item {i} has non-numeric days in {country}"
            if isinstance(days, str):
                # Should be convertible to int or contain numbers
                assert any(c.isdigit() for c in days), \
                    f"Timeline item {i} days field unclear in {country}: {days}"

    @pytest.mark.parametrize("country", SUPPORTED_COUNTRIES)
    def test_timeline_descriptions_substantial(self, country):
        """Timeline descriptions should be meaningful."""
        timeline = ELECTION_DATA[country]["timeline"]
        for i, item in enumerate(timeline):
            desc = item["description"]
            assert len(desc) >= 10, \
                f"Timeline item {i} description too short in {country}"


class TestVotingSteps:
    """Tests for voting step guides."""

    @pytest.mark.parametrize("country", SUPPORTED_COUNTRIES)
    def test_steps_exists_and_is_list(self, country):
        """Steps should exist and be a list."""
        steps = ELECTION_DATA[country].get("steps", [])
        assert isinstance(steps, list)
        assert len(steps) > 0, f"Steps empty for {country}"

    @pytest.mark.parametrize("country", SUPPORTED_COUNTRIES)
    def test_steps_has_minimum_count(self, country):
        """Should have at least 5 voting steps."""
        steps = ELECTION_DATA[country]["steps"]
        assert len(steps) >= 5, f"Fewer than 5 steps in {country}"

    @pytest.mark.parametrize("country", SUPPORTED_COUNTRIES)
    def test_all_steps_have_required_fields(self, country):
        """Each step should have required fields."""
        steps = ELECTION_DATA[country]["steps"]
        for i, step in enumerate(steps):
            for field in REQUIRED_STEP_FIELDS:
                assert field in step, \
                    f"Step {i} missing '{field}' in {country}"

    @pytest.mark.parametrize("country", SUPPORTED_COUNTRIES)
    def test_steps_have_icons(self, country):
        """Steps should have icon identifiers."""
        steps = ELECTION_DATA[country]["steps"]
        for i, step in enumerate(steps):
            icon = step["icon"]
            assert len(icon) > 0, f"Step {i} has empty icon in {country}"
            # Could be emoji, icon name, or URL

    @pytest.mark.parametrize("country", SUPPORTED_COUNTRIES)
    def test_step_titles_concise(self, country):
        """Step titles should be concise."""
        steps = ELECTION_DATA[country]["steps"]
        for i, step in enumerate(steps):
            title = step["title"]
            assert len(title) > 3, f"Step {i} title too short in {country}"
            assert len(title) < 100, f"Step {i} title too long in {country}"

    @pytest.mark.parametrize("country", SUPPORTED_COUNTRIES)
    def test_step_details_substantial(self, country):
        """Step details should be descriptive."""
        steps = ELECTION_DATA[country]["steps"]
        for i, step in enumerate(steps):
            detail = step["detail"]
            assert len(detail) >= 20, \
                f"Step {i} detail too short in {country}"


class TestFacts:
    """Tests for country facts."""

    @pytest.mark.parametrize("country", SUPPORTED_COUNTRIES)
    def test_facts_exists_and_is_list(self, country):
        """Facts should exist and be a list."""
        facts = ELECTION_DATA[country].get("facts", [])
        assert isinstance(facts, list)
        assert len(facts) > 0, f"Facts empty for {country}"

    @pytest.mark.parametrize("country", SUPPORTED_COUNTRIES)
    def test_facts_has_minimum_count(self, country):
        """Should have at least 3 facts."""
        facts = ELECTION_DATA[country]["facts"]
        assert len(facts) >= 3, f"Fewer than 3 facts in {country}"

    @pytest.mark.parametrize("country", SUPPORTED_COUNTRIES)
    def test_facts_are_strings(self, country):
        """Facts should be strings."""
        facts = ELECTION_DATA[country]["facts"]
        for i, fact in enumerate(facts):
            assert isinstance(fact, str), \
                f"Fact {i} is not a string in {country}"

    @pytest.mark.parametrize("country", SUPPORTED_COUNTRIES)
    def test_facts_are_substantial(self, country):
        """Facts should be meaningful statements."""
        facts = ELECTION_DATA[country]["facts"]
        for i, fact in enumerate(facts):
            assert len(fact) >= 20, \
                f"Fact {i} too short in {country}: {fact}"
            assert len(fact) < 500, \
                f"Fact {i} too long in {country}"


class TestDataConsistency:
    """Cross-field consistency tests."""

    @pytest.mark.parametrize("country", SUPPORTED_COUNTRIES)
    def test_country_id_matches_expected(self, country):
        """Country IDs should be lowercase."""
        assert country == country.lower(), \
            f"Country ID not lowercase: {country}"

    def test_all_countries_have_unique_colors(self):
        """Each country should have a distinct color."""
        colors = {}
        for country in SUPPORTED_COUNTRIES:
            color = ELECTION_DATA[country]["color"]
            if color in colors:
                pytest.fail(f"Duplicate color {color} for {country} and {colors[color]}")
            colors[color] = country

    def test_all_countries_have_unique_flags(self):
        """Each country should have a distinct flag."""
        flags = {}
        for country in SUPPORTED_COUNTRIES:
            flag = ELECTION_DATA[country]["flag"]
            if flag in flags:
                pytest.fail(f"Duplicate flag {flag} for {country} and {flags[flag]}")
            flags[flag] = country

    def test_no_empty_string_values(self):
        """No required field should be an empty string."""
        for country in SUPPORTED_COUNTRIES:
            data = ELECTION_DATA[country]
            # Check top-level string fields
            for field in ["name", "flag", "system", "body", "frequency", "voters", "description", "color"]:
                value = data.get(field, "")
                assert value != "", \
                    f"Empty {field} for {country}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
