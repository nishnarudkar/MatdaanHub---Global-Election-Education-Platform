"""
Firebase / Firestore Service
Handles chat session storage and history management
"""

import logging
from typing import Optional
from datetime import datetime, timedelta
from config import (
    FIREBASE_ENABLED,
    FIREBASE_CREDENTIALS_PATH,
    FIRESTORE_CHAT_COLLECTION,
    FIRESTORE_ELECTIONS_COLLECTION,
    FIRESTORE_GLOSSARY_COLLECTION,
    CHAT_HISTORY_TTL_HOURS,
)

logger = logging.getLogger(__name__)

try:
    import firebase_admin
    from firebase_admin import credentials, firestore

    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    logger.warning("firebase-admin not installed. Firestore chat history will be unavailable.")


class FirebaseService:
    """
    Wrapper for Firebase Admin SDK and Firestore.
    Stores and retrieves chat session history with automatic TTL.
    """

    def __init__(self) -> None:
        """Initialize Firebase service if enabled."""
        self.available: bool = False
        self.db = None
        self.call_count: int = 0

        if not FIREBASE_AVAILABLE:
            logger.warning("Firebase service not available: firebase-admin not installed")
            return

        if not FIREBASE_ENABLED:
            logger.info("Firebase service disabled: FIREBASE_ENABLED=false")
            return

        try:
            # Check if Firebase app is already initialized
            try:
                app = firebase_admin.get_app()
            except ValueError:
                # App not initialized, initialize it
                if FIREBASE_CREDENTIALS_PATH:
                    cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
                    app = firebase_admin.initialize_app(cred)
                else:
                    # Use Application Default Credentials (works on Cloud Run)
                    app = firebase_admin.initialize_app()

            self.db = firestore.client()
            self.available = True
            logger.info("Firebase service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase service: {e}")
            self.available = False

    async def save_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[dict] = None,
    ) -> bool:
        """
        Save a chat message to Firestore asynchronously.

        Args:
            session_id: Unique session identifier
            role: 'user' or 'assistant'
            content: Message content
            metadata: Optional metadata dict

        Returns:
            True if successful, False otherwise
        """
        if not self.available or not self.db:
            logger.warning("Save message requested but Firebase unavailable")
            return False

        if not session_id or not role or not content:
            logger.warning("Invalid message parameters")
            return False

        try:
            self.call_count += 1
            import anyio

            def _sync_save():
                # Document reference: chat_sessions/{session_id}/messages/{timestamp}
                collection_ref = self.db.collection(FIRESTORE_CHAT_COLLECTION).document(session_id)

                # Set TTL metadata on session doc if first message
                collection_ref.set(
                    {
                        "created_at": firestore.SERVER_TIMESTAMP,
                        "updated_at": firestore.SERVER_TIMESTAMP,
                        "ttl": firestore.SERVER_TIMESTAMP,
                        "message_count": firestore.Increment(1),
                    },
                    merge=True,
                )

                # Add individual message
                messages_ref = collection_ref.collection("messages")
                messages_ref.add({
                    "role": role,
                    "content": content,
                    "timestamp": firestore.SERVER_TIMESTAMP,
                    "metadata": metadata or {},
                })

            await anyio.to_thread.run_sync(_sync_save)
            logger.info(f"Message saved to session {session_id} (call #{self.call_count})")
            return True

        except Exception as e:
            logger.error(f"Error saving message: {e}")
            return False

    async def get_session_history(self, session_id: str, limit: int = 20) -> list[dict]:
        """
        Retrieve chat history for a session asynchronously.

        Args:
            session_id: Session identifier
            limit: Maximum number of messages to retrieve

        Returns:
            List of message dictionaries
        """
        if not self.available or not self.db:
            logger.warning("Get history requested but Firebase unavailable")
            return []

        if not session_id:
            logger.warning("Invalid session_id")
            return []

        try:
            self.call_count += 1
            import anyio

            def _sync_get():
                messages_ref = (
                    self.db.collection(FIRESTORE_CHAT_COLLECTION)
                    .document(session_id)
                    .collection("messages")
                    .order_by("timestamp", direction=firestore.Query.DESCENDING)
                    .limit(limit)
                )

                docs = messages_ref.stream()
                history = []
                for doc in docs:
                    data = doc.to_dict()
                    history.insert(0, {
                        "id": doc.id,
                        "role": data.get("role"),
                        "content": data.get("content"),
                        "timestamp": data.get("timestamp"),
                    })
                return history

            history = await anyio.to_thread.run_sync(_sync_get)
            logger.info(f"Retrieved {len(history)} messages from session {session_id}")
            return history

        except Exception as e:
            logger.error(f"Error retrieving history: {e}")
            return []

    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a chat session and all its messages asynchronously.

        Args:
            session_id: Session identifier

        Returns:
            True if successful, False otherwise
        """
        if not self.available or not self.db:
            logger.warning("Delete session requested but Firebase unavailable")
            return False

        if not session_id:
            logger.warning("Invalid session_id")
            return False

        try:
            self.call_count += 1
            import anyio

            def _sync_delete():
                session_ref = self.db.collection(FIRESTORE_CHAT_COLLECTION).document(session_id)
                messages = session_ref.collection("messages").stream()
                for msg in messages:
                    msg.reference.delete()
                session_ref.delete()

            await anyio.to_thread.run_sync(_sync_delete)
            logger.info(f"Session {session_id} deleted")
            return True

        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            return False

    async def get_election_data(self, country_id: str) -> Optional[dict]:
        """
        Fetch election profile for a country from Firestore.

        Args:
            country_id: Unique country identifier

        Returns:
            Dictionary with election data or None
        """
        if not self.available or not self.db:
            return None

        try:
            import anyio

            def _sync_get():
                doc_ref = self.db.collection(FIRESTORE_ELECTIONS_COLLECTION).document(country_id)
                doc = doc_ref.get()
                return doc.to_dict() if doc.exists else None

            return await anyio.to_thread.run_sync(_sync_get)
        except Exception as e:
            logger.error(f"Error fetching election data for {country_id}: {e}")
            return None

    async def get_all_elections(self) -> dict:
        """
        Fetch all election summaries from Firestore.

        Returns:
            Dictionary mapping country_id to election summary
        """
        if not self.available or not self.db:
            return {}

        try:
            import anyio

            def _sync_get_all():
                docs = self.db.collection(FIRESTORE_ELECTIONS_COLLECTION).stream()
                all_data = {}
                for doc in docs:
                    all_data[doc.id] = doc.to_dict()
                return all_data

            return await anyio.to_thread.run_sync(_sync_get_all)
        except Exception as e:
            logger.error(f"Error fetching all elections: {e}")
            return {}

    async def get_glossary(self) -> list[dict]:
        """
        Fetch all glossary terms from Firestore.

        Returns:
            List of dictionaries with term and definition
        """
        if not self.available or not self.db:
            return []

        try:
            import anyio

            def _sync_get_glossary():
                docs = self.db.collection(FIRESTORE_GLOSSARY_COLLECTION).stream()
                return [doc.to_dict() for doc in docs]

            return await anyio.to_thread.run_sync(_sync_get_glossary)
        except Exception as e:
            logger.error(f"Error fetching glossary: {e}")
            return []

    async def get_glossary_term(self, term: str) -> Optional[dict]:
        """
        Fetch a specific glossary term from Firestore.

        Args:
            term: The term to look up

        Returns:
            Dictionary with term details or None
        """
        if not self.available or not self.db:
            return None

        try:
            import anyio

            def _sync_get_term():
                # We search by the 'term' field (case-insensitive usually handled at route)
                # But here we assume terms are document IDs or we query
                # Let's assume term is the document ID for efficiency if possible
                doc_ref = self.db.collection(FIRESTORE_GLOSSARY_COLLECTION).document(term.lower())
                doc = doc_ref.get()
                if doc.exists:
                    return doc.to_dict()
                
                # If not found as ID, try searching by field
                query = self.db.collection(FIRESTORE_GLOSSARY_COLLECTION).where("term", "==", term).limit(1)
                docs = list(query.stream())
                return docs[0].to_dict() if docs else None

            return await anyio.to_thread.run_sync(_sync_get_term)
        except Exception as e:
            logger.error(f"Error fetching glossary term {term}: {e}")
            return None

    def is_available(self) -> bool:
        """Check if Firebase service is available."""
        return self.available

    def get_call_count(self) -> int:
        """Get the number of API calls made."""
        return self.call_count


# Singleton instance
_firebase_service: Optional[FirebaseService] = None


def get_firebase_service() -> FirebaseService:
    """Get or create the Firebase service instance."""
    global _firebase_service
    if _firebase_service is None:
        _firebase_service = FirebaseService()
    return _firebase_service
