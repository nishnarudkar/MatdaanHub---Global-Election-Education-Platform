"""
Google Gemini AI Service
Handles chat interactions using Google's Gemini 1.5 Flash model
"""

import logging
from typing import Optional
from config import GEMINI_API_KEY, GEMINI_MODEL, SYSTEM_PROMPT, CHAT_HISTORY_MAX_LENGTH

logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logger.warning("google-generativeai not installed. AI chat will be unavailable.")


class GeminiService:
    """
    Wrapper for Google Gemini 1.5 Flash API.
    Handles message generation, context management, and error handling.
    """

    def __init__(self) -> None:
        """Initialize Gemini service with API key if available."""
        self.available: bool = False
        self.model = None
        self.call_count: int = 0

        if not GENAI_AVAILABLE:
            logger.warning("Gemini service not available: google-generativeai not installed")
            return

        if not GEMINI_API_KEY:
            logger.warning("Gemini service not available: GEMINI_API_KEY not set")
            return

        try:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel(GEMINI_MODEL)
            self.available = True
            logger.info(f"Gemini service initialized with model: {GEMINI_MODEL}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini service: {e}")
            self.available = False

    async def generate_response(
        self,
        user_message: str,
        history: Optional[list[dict]] = None,
        temperature: float = 0.7,
    ) -> str:
        """
        Generate a response using Gemini API asynchronously.

        Args:
            user_message: The user's question or message
            history: Previous chat messages for context
            temperature: Sampling temperature (0.0-1.0)

        Returns:
            The AI-generated response as a string
        """
        if not self.available or not self.model:
            return self._fallback_response(user_message)

        try:
            self.call_count += 1

            # Build conversation context
            conversation = SYSTEM_PROMPT + "\n\n"

            # Add recent history for context
            if history:
                for msg in history[-CHAT_HISTORY_MAX_LENGTH:]:
                    role = "User" if msg.get("role") == "user" else "Assistant"
                    content = msg.get("content", "")
                    conversation += f"{role}: {content}\n\n"

            # Add current message
            conversation += f"User: {user_message}\nAssistant:"

            # Call Gemini API asynchronously
            response = await self.model.generate_content_async(
                conversation,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=512,
                ),
            )

            if response and response.text:
                answer = response.text.strip()
                logger.info(f"Gemini response generated (call #{self.call_count})")
                return answer
            else:
                logger.warning("Gemini returned empty response")
                return self._fallback_response(user_message)

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return self._fallback_response(user_message)

    def _fallback_response(self, message: str) -> str:
        """
        Provide a fallback response when Gemini is unavailable.
        Uses keyword matching to provide relevant default responses.

        Args:
            message: User message to analyze

        Returns:
            A relevant fallback response
        """
        msg_lower = message.lower()

        if any(word in msg_lower for word in ["india", "indian", "lok sabha", "eci"]):
            return (
                "🇮🇳 India uses a Parliamentary system. The Election Commission of India (ECI) "
                "oversees elections. Citizens vote for 543 Lok Sabha seats every 5 years using "
                "Electronic Voting Machines (EVMs). The party or coalition with 272+ seats forms the government."
            )

        if any(word in msg_lower for word in ["usa", "united states", "america", "electoral college"]):
            return (
                "🇺🇸 The USA holds Presidential elections every 4 years. Citizens vote for Electors "
                "who form the Electoral College (538 total). A candidate needs 270 electoral votes to win. "
                "Congress elections occur every 2 years."
            )

        if any(word in msg_lower for word in ["eu", "europe", "european parliament", "mep"]):
            return (
                "🇪🇺 EU citizens elect 720 Members of European Parliament (MEPs) every 5 years. "
                "Each of the 27 member states uses proportional representation. "
                "The Parliament co-legislates EU law alongside the Council."
            )

        if any(word in msg_lower for word in ["uk", "britain", "england", "parliament", "fptp"]):
            return (
                "🇬🇧 The UK uses First Past the Post voting. Citizens elect 650 MPs to the House of Commons. "
                "The leader of the party with most MPs becomes Prime Minister, invited by the Monarch."
            )

        if any(word in msg_lower for word in ["brazil", "brazilian", "tse", "compulsory"]):
            return (
                "🇧🇷 Brazil has compulsory voting for ages 18–70. The President is elected via a two-round "
                "majority system. Brazil pioneered fully electronic voting in 1996."
            )

        return (
            "I'm MatdaanHub, your election education guide! Ask me about voting systems, timelines, "
            "or the election process in India, USA, UK, EU, Brazil, and more. 🗳️"
        )

    def is_available(self) -> bool:
        """Check if Gemini service is available."""
        return self.available

    def get_call_count(self) -> int:
        """Get the number of API calls made."""
        return self.call_count


# Singleton instance
_gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """Get or create the Gemini service instance."""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
