"""
Translation Route
Handles text translation using Google Cloud Translate
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel, Field, field_validator
import bleach
from services.limiter_service import limiter
from config import (
    MAX_TEXT_TRANSLATION_LENGTH,
)
from services.translate_service import get_translate_service, TranslateService

logger = logging.getLogger(__name__)

router = APIRouter()


class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=MAX_TEXT_TRANSLATION_LENGTH)
    target_language: str = Field(..., min_length=2, max_length=5)
    source_language: Optional[str] = None

    @field_validator("text")
    @classmethod
    def sanitize_text(cls, v: str) -> str:
        """Sanitize text content using bleach."""
        cleaned = bleach.clean(v, tags=[], strip=True).strip()
        if not cleaned:
            raise ValueError("Text content cannot be empty after sanitization")
        return cleaned


class TranslateBatchRequest(BaseModel):
    texts: List[str] = Field(..., min_length=1)
    target_language: str = Field(..., min_length=2, max_length=5)
    source_language: Optional[str] = None

    @field_validator("texts")
    @classmethod
    def sanitize_texts(cls, v: List[str]) -> List[str]:
        """Sanitize text content using bleach."""
        cleaned_texts = []
        for text in v:
            # We want to skip empty texts or clean them
            if text:
                cleaned = bleach.clean(text, tags=[], strip=True).strip()
                cleaned_texts.append(cleaned)
            else:
                cleaned_texts.append("")
                
        # Calculate total length
        total_len = sum(len(t) for t in cleaned_texts)
        if total_len > MAX_TEXT_TRANSLATION_LENGTH * 5: # Allow higher total for batch, but not insane
            raise ValueError(f"Total batch text length exceeds limit ({total_len})")
            
        return cleaned_texts

class DetectRequest(BaseModel):

    text: str = Field(..., min_length=1, max_length=MAX_TEXT_TRANSLATION_LENGTH)

    @field_validator("text")
    @classmethod
    def sanitize_text(cls, v: str) -> str:
        """Sanitize text content using bleach."""
        cleaned = bleach.clean(v, tags=[], strip=True).strip()
        if not cleaned:
            raise ValueError("Text content cannot be empty after sanitization")
        return cleaned


@router.post("/api/translate")
@limiter.limit("30/minute")
async def translate_text_route(
    request: Request,
    request_data: TranslateRequest,
    translate_service: TranslateService = Depends(get_translate_service)
) -> dict:
    """
    Translate text to target language asynchronously.

    Returns:
        JSON with translated_text, source_language, target_language
    """
    try:
        text = request_data.text
        
        if not translate_service.is_available():
            logger.warning("Translation service unavailable")
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "Translation service not available",
                    "text": text,
                }
            )

        # Translate asynchronously
        result = await translate_service.translate_text(
            text=text,
            target_language=request_data.target_language.lower(),
            source_language=request_data.source_language.lower() if request_data.source_language else None,
        )

        if result.get("error"):
            logger.warning(f"Translation error: {result.get('error')}")
            raise HTTPException(status_code=400, detail=result)

        logger.info(
            f"Translation completed: {result.get('source_language')} "
            f"-> {result.get('target_language')}"
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Translation route error: {e}")
        raise HTTPException(status_code=500, detail="Failed to translate text")


@router.post("/api/translate/batch")
@limiter.limit("20/minute")
async def translate_batch_route(
    request: Request,
    request_data: TranslateBatchRequest,
    translate_service: TranslateService = Depends(get_translate_service)
) -> dict:
    """
    Translate a batch of texts to target language asynchronously.

    Returns:
        JSON with translated_texts, source_language, target_language
    """
    try:
        texts = request_data.texts
        
        if not translate_service.is_available():
            logger.warning("Translation service unavailable")
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "Translation service not available",
                    "translated_texts": texts,
                }
            )

        # Translate asynchronously
        result = await translate_service.translate_batch(
            texts=texts,
            target_language=request_data.target_language.lower(),
            source_language=request_data.source_language.lower() if request_data.source_language else None,
        )

        if result.get("error"):
            logger.warning(f"Batch translation error: {result.get('error')}")
            raise HTTPException(status_code=400, detail=result)

        logger.info(
            f"Batch translation completed ({len(texts)} items): {result.get('source_language')} "
            f"-> {result.get('target_language')}"
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch translation route error: {e}")
        raise HTTPException(status_code=500, detail="Failed to translate text batch")

@router.post("/api/detect")
@limiter.limit("60/minute")
async def detect_language_route(
    request: Request,
    request_data: DetectRequest,
    translate_service: TranslateService = Depends(get_translate_service)
) -> dict:
    """
    Detect language of given text asynchronously.

    Returns:
        JSON with detected_language code
    """
    try:
        text = request_data.text  # Already sanitized by Pydantic validator
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")

        if not translate_service.is_available():
            logger.warning("Translation service unavailable for language detection")
            raise HTTPException(status_code=503, detail="Translation service not available")

        detected_lang = await translate_service.detect_language(text)

        return {
            "text": text,
            "detected_language": detected_lang,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Language detection error: {e}")
        raise HTTPException(status_code=500, detail="Failed to detect language")


@router.get("/api/languages")
async def get_supported_languages_route(
    translate_service: TranslateService = Depends(get_translate_service)
) -> dict:
    """
    Get list of supported languages for translation.

    Returns:
        JSON with list of language codes
    """
    try:
        languages = translate_service.get_supported_languages()

        return {
            "supported_languages": languages,
            "count": len(languages),
        }

    except Exception as e:
        logger.error(f"Error fetching supported languages: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch language list")
