"""
Google Cloud Translate Service
Handles text translation and language detection
"""

import logging
from typing import Optional
from config import TRANSLATE_ENABLED, SUPPORTED_LANGUAGES

logger = logging.getLogger(__name__)

try:
    from google.cloud import translate_v2 as translate
    TRANSLATE_AVAILABLE = True
except ImportError:
    TRANSLATE_AVAILABLE = False
    logger.warning("google-cloud-translate not installed. Translation will be unavailable.")


class TranslateService:
    """
    Wrapper for Google Cloud Translate v2 API.
    Handles language translation and detection.
    """

    def __init__(self) -> None:
        """Initialize translation service if enabled."""
        self.available: bool = False
        self.client = None
        self.call_count: int = 0

        if not TRANSLATE_AVAILABLE:
            logger.warning("Translate service not available: google-cloud-translate not installed")
            return

        if not TRANSLATE_ENABLED:
            logger.info("Translate service disabled: GOOGLE_TRANSLATE_ENABLED=false")
            return

        try:
            self.client = translate.Client()
            self.available = True
            logger.info("Translate service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Translate service: {e}")
            self.available = False

    async def translate_text(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str] = None,
    ) -> dict:
        """
        Translate text to target language asynchronously.

        Args:
            text: Text to translate
            target_language: Target language code (e.g., 'es', 'fr', 'hi')
            source_language: Source language code (optional, auto-detected if not provided)

        Returns:
            Dictionary with 'translated_text', 'source_language', and 'target_language'
        """
        if not self.available or not self.client:
            logger.warning(f"Translation requested but service unavailable for: {target_language}")
            return {
                "translated_text": text,
                "source_language": source_language or "en",
                "target_language": target_language,
                "error": "Translation service unavailable",
            }

        if not text or not text.strip():
            return {
                "translated_text": text,
                "source_language": source_language or "en",
                "target_language": target_language,
                "error": "Empty text",
            }

        if len(text) > 5000:
            return {
                "translated_text": text,
                "source_language": source_language or "en",
                "target_language": target_language,
                "error": "Text too long (max 5000 characters)",
            }

        if target_language not in SUPPORTED_LANGUAGES:
            return {
                "translated_text": text,
                "source_language": source_language or "en",
                "target_language": target_language,
                "error": f"Language {target_language} not supported",
            }

        try:
            self.call_count += 1

            # Import anyio here to avoid dependency if not used elsewhere yet
            import anyio

            result = await anyio.to_thread.run_sync(
                self.client.translate,
                text,
                target_language,
                source_language
            )

            translated = result.get("translatedText", text)
            detected_source = result.get("detectedSourceLanguage", source_language or "en")

            logger.info(
                f"Translation completed: {detected_source} -> {target_language} "
                f"(call #{self.call_count})"
            )

            return {
                "translated_text": translated,
                "source_language": detected_source,
                "target_language": target_language,
            }

        except Exception as e:
            logger.error(f"Translation error: {e}")
            return {
                "translated_text": text,
                "source_language": source_language or "en",
                "target_language": target_language,
                "error": str(e),
            }

    async def translate_batch(
        self,
        texts: list[str],
        target_language: str,
        source_language: Optional[str] = None,
    ) -> dict:
        """
        Translate a list of texts to target language asynchronously.

        Args:
            texts: List of strings to translate
            target_language: Target language code
            source_language: Source language code

        Returns:
            Dictionary with 'translated_texts', 'source_language', and 'target_language'
        """
        if not self.available or not self.client:
            return {
                "translated_texts": texts,
                "source_language": source_language or "en",
                "target_language": target_language,
                "error": "Translation service unavailable",
            }

        if not texts:
            return {
                "translated_texts": [],
                "source_language": source_language or "en",
                "target_language": target_language,
            }

        if target_language not in SUPPORTED_LANGUAGES:
            return {
                "translated_texts": texts,
                "source_language": source_language or "en",
                "target_language": target_language,
                "error": f"Language {target_language} not supported",
            }

        try:
            self.call_count += 1
            import anyio

            # Extract actual strings and filter out empty ones while keeping indices
            valid_texts = [t for t in texts if t and t.strip()]
            
            if not valid_texts:
                return {
                    "translated_texts": texts,
                    "source_language": source_language or "en",
                    "target_language": target_language,
                }

            # Google Cloud Translate SDK handles lists directly
            results = await anyio.to_thread.run_sync(
                self.client.translate,
                texts,
                target_language,
                source_language
            )

            translated_texts = [res.get("translatedText", text) for res, text in zip(results, texts)]
            detected_source = results[0].get("detectedSourceLanguage", source_language or "en") if results else (source_language or "en")

            return {
                "translated_texts": translated_texts,
                "source_language": detected_source,
                "target_language": target_language,
            }

        except Exception as e:
            logger.error(f"Batch translation error: {e}")
            return {
                "translated_texts": texts,
                "source_language": source_language or "en",
                "target_language": target_language,
                "error": str(e),
            }

    async def detect_language(self, text: str) -> str:
        """
        Detect the language of given text asynchronously.

        Args:
            text: Text to detect language for

        Returns:
            Language code (e.g., 'en', 'es', 'hi')
        """
        if not self.available or not self.client:
            logger.warning("Language detection requested but service unavailable")
            return "en"

        if not text or not text.strip():
            return "en"

        try:
            import anyio
            result = await anyio.to_thread.run_sync(self.client.detect_language, text)
            language = result.get("language", "en")
            logger.debug(f"Detected language: {language}")
            return language
        except Exception as e:
            logger.error(f"Language detection error: {e}")
            return "en"

    def is_available(self) -> bool:
        """Check if translation service is available."""
        return self.available

    def get_call_count(self) -> int:
        """Get the number of API calls made."""
        return self.call_count

    def get_supported_languages(self) -> list[str]:
        """Get list of supported languages."""
        return SUPPORTED_LANGUAGES.copy()


# Singleton instance
_translate_service: Optional[TranslateService] = None


def get_translate_service() -> TranslateService:
    """Get or create the Translate service instance."""
    global _translate_service
    if _translate_service is None:
        _translate_service = TranslateService()
    return _translate_service
