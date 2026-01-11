
import pandas as pd
import csv
from io import StringIO
import requests
import json
import os
import logging

logger = logging.getLogger(__name__)

# Constants
ANKICONNECT_TIMEOUT = 5  # seconds

def check_ankiconnect(anki_url: str = None) -> tuple[bool, str]:
    """
    Check if AnkiConnect is reachable.
    Returns (is_reachable, error_message).
    """
    if not anki_url:
        anki_url = os.getenv("ANKI_CONNECT_URL", "http://localhost:8765")
    
    # Basic URL structure validation
    if not (anki_url.startswith("http://") or anki_url.startswith("https://")):
        return False, "Invalid URL: Must start with http:// or https://"
    
    try:
        response = requests.post(
            anki_url, 
            json={"action": "version", "version": 6},
            timeout=2
        )
        result = response.json()
        if result.get("result"):
            return True, f"AnkiConnect v{result['result']} at {anki_url}"
        return False, f"AnkiConnect error: {result.get('error')}"
    except requests.exceptions.ConnectionError:
        if "localhost" in anki_url:
            return False, "Cannot reach localhost:8765. Use ngrok tunnel for Cloud access."
        return False, f"Cannot connect to {anki_url}"
    except requests.exceptions.Timeout:
        return False, "AnkiConnect request timed out"
    except Exception as e:
        return False, f"AnkiConnect check failed: {e}"

def deduplicate_cards(new_cards: pd.DataFrame, existing_questions: list[str]) -> pd.DataFrame:
    """
    Filters out cards where the 'Front' is similar to existing questions.
    Uses simple exact match or normalized match for now to avoid overhead.
    """
    if new_cards.empty or not existing_questions:
        return new_cards
        
    # Normalize existing for comparison (lowercase, stripped)
    existing_set = {q.lower().strip() for q in existing_questions}
    
    # Filter
    unique_indices = []
    for idx, row in new_cards.iterrows():
        front = str(row['Front']).lower().strip()
        if front not in existing_set:
            unique_indices.append(idx)
            # Add to local set to avoid dupes within the same batch
            existing_set.add(front)
            
    return new_cards.loc[unique_indices]

def push_card_to_anki(front: str, back: str, deck: str, tags: list = None, anki_url: str = None) -> bool:
    """
    Pushes a single card to Anki via AnkiConnect.
    Automatically creates deck if it doesn't exist.
    Returns True if successful.
    """
    if tags is None: tags = []
    if not anki_url:
        anki_url = os.getenv("ANKI_CONNECT_URL", "http://localhost:8765")
    
    # First, ensure deck exists
    create_deck_payload = {
        "action": "createDeck",
        "version": 6,
        "params": {"deck": deck}
    }
    
    try:
        requests.post(anki_url, json=create_deck_payload, timeout=ANKICONNECT_TIMEOUT)
    except requests.exceptions.Timeout:
        logger.debug("Deck creation request timed out (will try with addNote)")
    except requests.exceptions.ConnectionError:
        logger.debug("Deck creation failed (will try with addNote)")
    except Exception as e:
        logger.debug(f"Deck creation attempt failed: {e}")
    
    note = {
        "deckName": deck,
        "modelName": "Basic",
        "fields": {
            "Front": front,
            "Back": back
        },
        "options": {
            "allowDuplicate": False,
            "duplicateScope": "deck"
        },
        "tags": tags
    }
    
    payload = {
        "action": "addNote",
        "version": 6,
        "params": {
            "note": note
        }
    }
    
    try:
        response = requests.post(anki_url, json=payload, timeout=ANKICONNECT_TIMEOUT)
        result = response.json()
        if result.get("error") is None:
            return True
        logger.warning(f"AnkiConnect error: {result.get('error')}")
        return False
    except requests.exceptions.Timeout:
        logger.warning("AnkiConnect request timed out")
        return False
    except requests.exceptions.ConnectionError:
        logger.warning("Could not connect to AnkiConnect")
        return False
    except Exception as e:
        logger.error(f"Unexpected error pushing to Anki: {e}")
        return False

def format_cards_for_ankiconnect(df: pd.DataFrame) -> list:
    """
    Formats a DataFrame of cards into the list of notes expected by AnkiConnect's addNotes.
    """
    notes = []
    for _, row in df.iterrows():
        notes.append({
            "deckName": str(row['Deck']),
            "modelName": "Basic",
            "fields": {
                "Front": str(row['Front']),
                "Back": str(row['Back'])
            },
            "options": {
                "allowDuplicate": False,
                "duplicateScope": "deck"
            },
            "tags": [str(row['Tag'])] if row['Tag'] else []
        })
    return notes

def robust_csv_parse(csv_text: str) -> pd.DataFrame:
    """
    Parses LLM-generated CSV/TSV text more robustly than pd.read_csv.
    Handles manual quote fixing and bad lines.
    Assumes TSV (Tab Separated) as per prompt instructions.
    """
    data = []
    lines = csv_text.strip().splitlines()
    
    for line in lines:
        line = line.strip()
        if not line: continue
        
        # heuristic: if it doesn't look like a TSV line, skip or try to fix
        if "\t" not in line:
            # Maybe it used | or comma?
            if "|" in line:
                parts = line.split("|")
            elif "," in line:
                # Naive comma split, mostly for fail-safe
                parts = line.split(",")
            else:
                continue
        else:
            parts = line.split("\t")
            
        if len(parts) < 2:
            continue
            
        # Clean quotes
        front = parts[0].strip()
        back = parts[1].strip()
        
        # Remove surrounding quotes if they exist
        if front.startswith('"') and front.endswith('"'):
            front = front[1:-1].replace('""', '"')
        if back.startswith('"') and back.endswith('"'):
            back = back[1:-1].replace('""', '"')
            
        # Combine remaining parts into back if there were extra tabs (e.g. inside content, though rare with quotes)
        # But per prompt, we asked for 2 columns.
        if len(parts) > 2:
            # Re-join the rest just in case
            extra = "\t".join(parts[2:])
            back = f"{back} {extra}".strip()
            if back.startswith('"') and back.endswith('"'):
                 back = back[1:-1].replace('""', '"')

        data.append({"Front": front, "Back": back})
        
    return pd.DataFrame(data)

def push_notes_to_anki(notes: list, anki_url: str = None) -> tuple[int, list]:
    """
    Pushes a batch of notes to Anki via AnkiConnect's addNotes.
    Returns (success_count, errors).
    """
    if not anki_url:
        anki_url = os.getenv("ANKI_CONNECT_URL", "http://localhost:8765")
        
    payload = {
        "action": "addNotes",
        "version": 6,
        "params": {
            "notes": notes
        }
    }
    
    try:
        response = requests.post(anki_url, json=payload, timeout=ANKICONNECT_TIMEOUT * 2)
        result = response.json()
        
        if result.get("error"):
            # Global error
            logger.error(f"AnkiConnect global error: {result.get('error')}")
            return 0, [str(result.get('error'))]
            
        # Result is a list of node IDs (int) or None (if error)
        # However, addNotes might return differently depending on version, 
        # usually it returns an array of note IDs for success, or nulls.
        # But if strict error handling is on, checking distinct errors might be tricky.
        # Let's assume result['result'] is the list.
        
        results = result.get('result', [])
        success_count = 0
        errors = []
        
        if results:
            for i, res in enumerate(results):
                if res:
                    success_count += 1
                else:
                    errors.append(f"Failed to add note {i+1}")
                    
        return success_count, errors
        
    except Exception as e:
        logger.error(f"Batch push failed: {e}")
        return 0, [str(e)]
