"""
Election Data Routes
Provides endpoints for election system information and timelines
"""

import json
import logging
from fastapi import APIRouter, HTTPException, Depends
from config import ALLOWED_COUNTRIES, ELECTIONS_DATA_FILE, GLOSSARY_DATA_FILE
from services.firebase_service import get_firebase_service, FirebaseService
from schemas.election_schemas import ElectionProfile, GlossaryTerm

logger = logging.getLogger(__name__)

router = APIRouter()


def _load_local_elections() -> dict:
    """Load all elections from the bundled JSON file."""
    try:
        with open(ELECTIONS_DATA_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load local elections.json: {e}")
        return {}


def _load_local_glossary() -> list:
    """Load glossary from the bundled JSON file."""
    try:
        with open(GLOSSARY_DATA_FILE, encoding="utf-8") as f:
            return json.load(f).get("glossary", [])
    except Exception as e:
        logger.error(f"Failed to load local glossary.json: {e}")
        return []


@router.get("/api/elections")
async def get_all_elections(
    firebase_service: FirebaseService = Depends(get_firebase_service)
) -> dict:
    """Get summary of all supported countries."""
    try:
        data = await firebase_service.get_all_elections()

        # Fall back to local JSON if Firestore is unavailable or empty
        if not data:
            logger.warning("Firestore empty — using local elections.json")
            data = _load_local_elections()

        summary = {}
        for country_id, country_data in data.items():
            try:
                profile = ElectionProfile(**country_data)
                summary[country_id] = {
                    "name": profile.name,
                    "flag": profile.flag,
                    "system": profile.system,
                    "color": profile.color,
                    "voters": profile.voters,
                    "body": profile.body,
                    "frequency": profile.frequency,
                }
            except Exception as ve:
                logger.warning(f"Invalid election data for {country_id}: {ve}")
                summary[country_id] = {
                    "name": country_data.get("name"),
                    "flag": country_data.get("flag"),
                    "system": country_data.get("system"),
                    "color": country_data.get("color"),
                    "voters": country_data.get("voters"),
                    "body": country_data.get("body"),
                    "frequency": country_data.get("frequency"),
                }

        return summary
    except Exception as e:
        logger.error(f"Error fetching elections: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch elections data")


@router.get("/api/elections/{country_id}")
async def get_election_details(
    country_id: str,
    firebase_service: FirebaseService = Depends(get_firebase_service)
) -> dict:
    """Get full election details for a country."""
    country_id = country_id.lower()

    if country_id not in ALLOWED_COUNTRIES:
        logger.warning(f"Invalid country requested: {country_id}")
        raise HTTPException(status_code=404, detail="Country not found")

    try:
        country_data = await firebase_service.get_election_data(country_id)

        # Fall back to local JSON
        if not country_data:
            logger.warning(f"Firestore empty for {country_id} — using local elections.json")
            country_data = _load_local_elections().get(country_id)

        if not country_data:
            raise HTTPException(status_code=404, detail="Country data not found")

        profile = ElectionProfile(**country_data)
        return profile.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching election details for {country_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch election data")


@router.get("/api/elections/{country_id}/timeline")
async def get_election_timeline(
    country_id: str,
    firebase_service: FirebaseService = Depends(get_firebase_service)
) -> dict:
    """Get election timeline for a country."""
    country_id = country_id.lower()

    if country_id not in ALLOWED_COUNTRIES:
        raise HTTPException(status_code=404, detail="Country not found")

    try:
        country_data = await firebase_service.get_election_data(country_id)

        if not country_data:
            country_data = _load_local_elections().get(country_id)

        if not country_data:
            raise HTTPException(status_code=404, detail="Country data not found")

        profile = ElectionProfile(**country_data)
        if not profile.timeline:
            raise HTTPException(status_code=404, detail="Timeline not found")

        return {
            "country": country_id,
            "country_name": profile.name,
            "timeline": [p.model_dump() for p in profile.timeline],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching timeline for {country_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch timeline")


@router.get("/api/elections/{country_id}/voting-steps")
async def get_voting_steps(
    country_id: str,
    firebase_service: FirebaseService = Depends(get_firebase_service)
) -> dict:
    """Get how-to-vote steps for a country."""
    country_id = country_id.lower()

    if country_id not in ALLOWED_COUNTRIES:
        raise HTTPException(status_code=404, detail="Country not found")

    try:
        country_data = await firebase_service.get_election_data(country_id)

        if not country_data:
            country_data = _load_local_elections().get(country_id)

        if not country_data:
            raise HTTPException(status_code=404, detail="Country data not found")

        profile = ElectionProfile(**country_data)
        if not profile.steps:
            raise HTTPException(status_code=404, detail="Voting steps not found")

        return {
            "country": country_id,
            "country_name": profile.name,
            "steps": [s.model_dump() for s in profile.steps],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching voting steps for {country_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch voting steps")


@router.get("/api/glossary")
async def get_glossary(
    firebase_service: FirebaseService = Depends(get_firebase_service)
) -> dict:
    """Get election terminology glossary."""
    try:
        glossary_list = await firebase_service.get_glossary()

        if not glossary_list:
            logger.warning("Firestore glossary empty — using local glossary.json")
            glossary_list = _load_local_glossary()

        validated_glossary = []
        for item in glossary_list:
            try:
                term = GlossaryTerm(**item)
                validated_glossary.append(term.model_dump())
            except Exception as ve:
                logger.warning(f"Invalid glossary term: {ve}")
                validated_glossary.append(item)

        return {"glossary": validated_glossary}
    except Exception as e:
        logger.error(f"Error fetching glossary: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch glossary")


@router.get("/api/glossary/{term}")
async def get_glossary_term(
    term: str,
    firebase_service: FirebaseService = Depends(get_firebase_service)
) -> dict:
    """Get definition for a specific glossary term."""
    try:
        term_data = await firebase_service.get_glossary_term(term)

        # Fall back to local glossary
        if not term_data:
            local = _load_local_glossary()
            term_data = next(
                (t for t in local if t.get("term", "").lower() == term.lower()),
                None
            )

        if not term_data:
            raise HTTPException(status_code=404, detail="Term not found")

        glossary_term = GlossaryTerm(**term_data)
        return glossary_term.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching glossary term {term}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch term")
