"""
Card History management for Anki AI.
Stores all generated cards per user in JSON files.
"""
import json
import os
import logging
from datetime import datetime
import pandas as pd

HISTORY_DIR = "data/history"
logger = logging.getLogger(__name__)


class CardHistory:
    def __init__(self, history_dir=HISTORY_DIR):
        self.history_dir = history_dir
        self._ensure_dir()

    def _ensure_dir(self):
        """Creates the history directory if it doesn't exist."""
        os.makedirs(self.history_dir, exist_ok=True)

    def _get_user_file(self, email):
        """Returns the path to a user's history file."""
        # Sanitize email for filename
        safe_email = email.replace("@", "_at_").replace(".", "_")
        return os.path.join(self.history_dir, f"{safe_email}.json")

    def _load_history(self, email):
        """Loads a user's card history."""
        filepath = self._get_user_file(email)
        if not os.path.exists(filepath):
            return []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_history(self, email, history):
        """Saves a user's card history."""
        filepath = self._get_user_file(email)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)

    def add_cards(self, email, cards_df: pd.DataFrame, source: str = "Generated"):
        """
        Adds cards from a DataFrame to the user's history.
        Each card record includes: front, back, deck, tag, source, timestamp.
        """
        if cards_df.empty:
            return

        history = self._load_history(email)
        timestamp = datetime.now().isoformat()

        for _, row in cards_df.iterrows():
            card_record = {
                "front": str(row.get('Front', '')),
                "back": str(row.get('Back', '')),
                "deck": str(row.get('Deck', 'Default')),
                "tag": str(row.get('Tag', '')),
                "source": source,
                "timestamp": timestamp
            }
            history.append(card_record)

        self._save_history(email, history)
        logger.info(f"Added {len(cards_df)} cards to history for {email}")

    def get_history(self, email) -> list[dict]:
        """Returns the user's entire card history."""
        return self._load_history(email)

    def get_history_df(self, email) -> pd.DataFrame:
        """Returns the user's card history as a DataFrame."""
        history = self._load_history(email)
        if not history:
            return pd.DataFrame(columns=["front", "back", "deck", "tag", "source", "timestamp"])
        return pd.DataFrame(history)

    def clear_history(self, email):
        """Clears a user's card history."""
        filepath = self._get_user_file(email)
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"Cleared history for {email}")

    def get_card_count(self, email) -> int:
        """Returns the total number of cards in history."""
        return len(self._load_history(email))

    def delete_deck(self, email, deck_name: str, include_subdecks: bool = True) -> int:
        """
        Deletes all cards from a specific deck.
        
        Args:
            email: User's email
            deck_name: Name of the deck to delete
            include_subdecks: If True, also deletes cards from subdecks (e.g., "Anatomy::Heart")
        
        Returns:
            Number of cards deleted
        """
        history = self._load_history(email)
        original_count = len(history)
        
        if include_subdecks:
            # Delete cards from this deck and all subdecks (deck names starting with "deck_name::")
            filtered_history = [
                card for card in history 
                if card.get('deck') != deck_name and not card.get('deck', '').startswith(f"{deck_name}::")
            ]
        else:
            # Delete only cards from this exact deck
            filtered_history = [card for card in history if card.get('deck') != deck_name]
        
        deleted_count = original_count - len(filtered_history)
        
        if deleted_count > 0:
            self._save_history(email, filtered_history)
            logger.info(f"Deleted {deleted_count} cards from deck '{deck_name}' for {email}")
        
        return deleted_count
