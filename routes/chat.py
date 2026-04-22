"""
AI Chat Route
Handles election Q&A using Google Gemini AI
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel, Field, field_validator
import bleach
from services.limiter_service import limiter
from config import (
    MAX_MESSAGE_LENGTH,
    MIN_MESSAGE_LENGTH,
)
from services.gemini_service import get_gemini_service, GeminiService
from services.firebase_service import get_firebase_service, FirebaseService
from services.vertex_service import get_vertex_service, VertexService

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=MIN_MESSAGE_LENGTH, max_length=MAX_MESSAGE_LENGTH)
    history: List[ChatMessage] = []
    country: Optional[str] = None
    session_id: Optional[str] = None

    @field_validator("message")
    @classmethod
    def sanitize_message(cls, v: str) -> str:
        """Sanitize message content using bleach."""
        # Remove all HTML tags and attributes
        cleaned = bleach.clean(v, tags=[], strip=True).strip()
        if not cleaned:
             raise ValueError("Message content cannot be empty after sanitization")
        return cleaned


@router.post("/api/chat")
@limiter.limit("20/minute")
async def chat(
    request: Request,
    request_data: ChatRequest,
    gemini_service: GeminiService = Depends(get_gemini_service),
    firebase_service: FirebaseService = Depends(get_firebase_service)
) -> dict:
    """
    Generate AI response to election questions asynchronously.

    Returns:
        JSON with 'response' field containing AI-generated answer
    """
    try:
        user_message = request_data.message  # Already sanitized by Pydantic validator

        # Convert Pydantic history to list of dicts for service
        history_dicts = [{"role": m.role, "content": m.content} for m in request_data.history]

        # Generate response asynchronously
        response_text = await gemini_service.generate_response(
            user_message=user_message,
            history=history_dicts,
            temperature=0.7,
        )

        if not response_text:
            logger.error("Failed to generate response")
            raise HTTPException(status_code=500, detail="Failed to generate response")

        # Save to Firestore if session_id provided
        if request_data.session_id and firebase_service.is_available():
            await firebase_service.save_message(request_data.session_id, "user", user_message)
            await firebase_service.save_message(request_data.session_id, "assistant", response_text)

        logger.info(f"Chat response generated for user (length: {len(response_text)})")

        return {
            "response": response_text,
            "country": request_data.country if request_data.country else None,
            "gemini_available": gemini_service.is_available(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat route error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred processing your request")


@router.post("/api/chat/grounded")
async def chat_grounded(
    request: Request,
    vertex_service: VertexService = Depends(get_vertex_service)
) -> dict:
    """
    Generate grounded, fact-checked response using Vertex AI Search.
    Includes citations and sources.

    Returns:
        JSON with 'response', 'sources', and 'grounded' fields
    """
    try:
        data = await request.json()
        user_message = _sanitize_input(data.get("message", ""))

        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")

        # Execute grounded search asynchronously
        result = await vertex_service.search_with_grounding(user_message)

        if result.get("error"):
            logger.warning(f"Grounded search unavailable: {result.get('error')}")
            raise HTTPException(status_code=503, detail=result.get("error"))

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Grounded chat error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process grounded query")


@router.get("/api/chat/history/{session_id}")
async def get_chat_history(
    session_id: str,
    firebase_service: FirebaseService = Depends(get_firebase_service)
) -> dict:
    """
    Retrieve chat history for a session asynchronously.

    Args:
        session_id: Unique session identifier

    Returns:
        JSON array of chat messages
    """
    try:
        # Validate session_id
        if not session_id or len(session_id) > 100:
            raise HTTPException(status_code=400, detail="Invalid session_id")

        if not firebase_service.is_available():
            logger.warning("Firebase service unavailable for history retrieval")
            raise HTTPException(status_code=503, detail="Chat history not available")

        history = await firebase_service.get_session_history(session_id, limit=50)

        return {
            "session_id": session_id,
            "messages": history,
            "count": len(history),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving chat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat history")
