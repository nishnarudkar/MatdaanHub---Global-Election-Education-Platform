"""
Election Data Routes
Provides endpoints for election system information and timelines
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends
from config import ALLOWED_COUNTRIES
from services.firebase_service import get_firebase_service, FirebaseService
from schemas.election_schemas import ElectionProfile, GlossaryTerm

logger = logging.getLogger(__name__)

router = APIRouter()




@router.get("/api/elections")
async def get_all_elections(
    firebase_service: FirebaseService = Depends(get_firebase_service)
) -> dict:
    """
    Get summary of all supported countries.

    Returns:
        JSON with country summaries: name, flag, system, color, voters
    """
    try:
        data = await firebase_service.get_all_elections()
        summary = {}

        for country_id, country_data in data.items():
            # Validate with schema
            try:
                profile = ElectionProfile(**country_data)
                summary[country_id] = {
                    "name": profile.name,
                    "flag": profile.flag,
                    "system": profile.system,
                    "color": profile.color,
                    "voters": profile.voters,
                    "body": profile.body,
                }
            except Exception as ve:
                logger.warning(f"Invalid election data for {country_id}: {ve}")
                # Fallback to raw data if validation fails but we want to return what we have
                summary[country_id] = {
                    "name": country_data.get("name"),
                    "flag": country_data.get("flag"),
                    "system": country_data.get("system"),
                    "color": country_data.get("color"),
                    "voters": country_data.get("voters"),
                    "body": country_data.get("body"),
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
    """
    Get full election details for a country.

    Args:
        country_id: Country identifier (india, usa, uk, eu, brazil)

    Returns:
        JSON with complete election data including timeline and voting steps
    """
    country_id = country_id.lower()

    if country_id not in ALLOWED_COUNTRIES:
        logger.warning(f"Invalid country requested: {country_id}")
        raise HTTPException(status_code=404, detail="Country not found")

    try:
        country_data = await firebase_service.get_election_data(country_id)

        if not country_data:
            raise HTTPException(status_code=404, detail="Country data not found")

        # Validate with schema
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
    """
    Get election timeline for a country.

    Args:
        country_id: Country identifier

    Returns:
        JSON array of timeline phases with dates and descriptions
    """
    country_id = country_id.lower()

    if country_id not in ALLOWED_COUNTRIES:
        raise HTTPException(status_code=404, detail="Country not found")

    try:
        country_data = await firebase_service.get_election_data(country_id)
        
        if not country_data:
             raise HTTPException(status_code=404, detail="Country data not found")

        # Validate with schema
        profile = ElectionProfile(**country_data)
        timeline = profile.timeline

        if not timeline:
            logger.warning(f"No timeline found for {country_id}")
            raise HTTPException(status_code=404, detail="Timeline not found")

        return {
            "country": country_id,
            "country_name": profile.name,
            "timeline": [p.model_dump() for p in timeline],
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
    """
    Get how-to-vote steps for a country.

    Args:
        country_id: Country identifier

    Returns:
        JSON array of voting steps with icons and details
    """
    country_id = country_id.lower()

    if country_id not in ALLOWED_COUNTRIES:
        raise HTTPException(status_code=404, detail="Country not found")

    try:
        country_data = await firebase_service.get_election_data(country_id)
        
        if not country_data:
             raise HTTPException(status_code=404, detail="Country data not found")

        # Validate with schema
        profile = ElectionProfile(**country_data)
        steps = profile.steps

        if not steps:
            logger.warning(f"No voting steps found for {country_id}")
            raise HTTPException(status_code=404, detail="Voting steps not found")

        return {
            "country": country_id,
            "country_name": profile.name,
            "steps": [s.model_dump() for s in steps],
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
    """
    Get election terminology glossary.

    Returns:
        JSON array of terms and definitions
    """
    try:
        glossary_list = await firebase_service.get_glossary()
        
        # Validate each term
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
    """
    Get definition for a specific glossary term.

    Args:
        term: Term to look up

    Returns:
        JSON with term definition and examples
    """
    try:
        term_data = await firebase_service.get_glossary_term(term)

        if not term_data:
            logger.warning(f"Glossary term not found: {term}")
            raise HTTPException(status_code=404, detail="Term not found")

        # Validate with schema
        glossary_term = GlossaryTerm(**term_data)
        return glossary_term.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching glossary term {term}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch term")
