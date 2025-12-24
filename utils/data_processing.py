
import pandas as pd
import csv
from io import StringIO
import requests
import json

def push_card_to_anki(front: str, back: str, deck: str, tags: list = None) -> bool:
    """
    Pushes a single card to Anki via AnkiConnect.
    Returns True if successful.
    """
    if tags is None: tags = []
    
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
        response = requests.post("http://localhost:8765", json=payload, timeout=2)
        result = response.json()
        if result.get("error") is None:
            return True
        return False
    except:
        return False

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
