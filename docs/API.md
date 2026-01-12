# API Documentation

This document provides comprehensive API documentation for the Medical PDF to Anki Converter, including LLM provider APIs, AnkiConnect integration, and internal utility APIs.

## Table of Contents

- [Overview](#overview)
- [LLM Provider APIs](#llm-provider-apis)
  - [Google AI (Gemini)](#google-ai-gemini)
  - [Z.AI (GLM)](#zai-glm)
  - [OpenRouter](#openrouter)
- [AnkiConnect API](#ankiconnect-api)
- [Internal Utility APIs](#internal-utility-apis)
  - [Authentication API](#authentication-api)
  - [LLM Handler API](#llm-handler-api)
  - [PDF Processor API](#pdf-processor-api)
  - [Data Processing API](#data-processing-api)
  - [RAG API](#rag-api)

---

## Overview

The application integrates with multiple external APIs and provides internal utility APIs for component interaction.

### External APIs

| API | Purpose | Base URL |
|-----|---------|----------|
| Google AI | LLM for card generation | `https://generativelanguage.googleapis.com` |
| Z.AI | Alternative LLM provider | `https://api.z.ai` |
| OpenRouter | Multi-provider LLM gateway | `https://openrouter.ai/api` |
| AnkiConnect | Anki Desktop integration | `http://localhost:8765` |
| SMTP | Email for password reset | (configured per provider) |

### Internal APIs

Internal APIs are Python functions within the `utils/` module that components can import and use.

---

## LLM Provider APIs

### Google AI (Gemini)

#### API Base URL
```
https://generativelanguage.googleapis.com/v1beta/models
```

#### Authentication
```python
headers = {
    "Content-Type": "application/json",
}
params = {
    "key": os.getenv("GOOGLE_API_KEY")
}
```

#### Supported Models

| Model ID | Context Window | Best For |
|----------|----------------|----------|
| `gemini-2.5-flash` | 1M tokens | Fast card generation |
| `gemini-3-flash` | 1M tokens | Summaries and generation |
| `gemma-3-27b-it` | 128K tokens | Chapter detection |

#### Generate Content Endpoint

**Request**
```http
POST https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={api_key}

{
  "contents": [{
    "parts": [{
      "text": "Your prompt here..."
    }]
  }],
  "generationConfig": {
    "temperature": 0.7,
    "maxOutputTokens": 8192,
    "topP": 0.9
  },
  "systemInstruction": {
    "parts": [{
      "text": "You are a medical education expert..."
    }]
  }
}
```

**Response**
```json
{
  "candidates": [{
    "content": {
      "parts": [{
        "text": "Generated response..."
      }],
      "role": "model"
    },
    "finishReason": "STOP"
  }],
  "usageMetadata": {
    "promptTokenCount": 100,
    "candidatesTokenCount": 500,
    "totalTokenCount": 600
  }
}
```

#### Rate Limits

| Tier | Requests/Minute | Requests/Day |
|------|-----------------|--------------|
| Free | 15 | 1,500 |
| Paid | varies by plan | varies by plan |

#### Error Handling

| Status Code | Meaning | Retry |
|-------------|---------|-------|
| 200 | Success | - |
| 400 | Invalid request | No |
| 401 | Invalid API key | No |
| 429 | Rate limit exceeded | Yes (exponential backoff) |
| 500 | Server error | Yes |

---

### Z.AI (GLM)

#### API Base URL
```
https://open.bigmodel.cn/api/paas/v4
```

#### Authentication
```python
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}
```

#### Supported Models

| Model ID | Context Window | Best For |
|----------|----------------|----------|
| `glm-4.7` | 128K tokens | Card generation, summaries |
| `glm-4.5-air` | 128K tokens | Fast chat, summaries |

#### Chat Completions Endpoint

**Request**
```http
POST https://open.bigmodel.cn/api/paas/v4/chat/completions

{
  "model": "glm-4.7",
  "messages": [
    {
      "role": "system",
      "content": "You are a medical education expert..."
    },
    {
      "role": "user",
      "content": "Your prompt here..."
    }
  ],
  "temperature": 0.7,
  "max_tokens": 8192,
  "top_p": 0.9
}
```

**Response**
```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "glm-4.7",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "Generated response..."
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 100,
    "completion_tokens": 500,
    "total_tokens": 600
  }
}
```

#### Rate Limits

| Tier | Requests/Minute | Requests/Day |
|------|-----------------|--------------|
| Free | 60 | 5,000 |
| Paid | varies by plan | varies by plan |

---

### OpenRouter

#### API Base URL
```
https://openrouter.ai/api/v1
```

#### Authentication
```python
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}",
    "HTTP-Referer": "https://your-app-url.com",
    "X-Title": "Your App Name"
}
```

#### Supported Models (Free Tier)

| Model ID | Provider | Best For |
|----------|----------|----------|
| `xiaomi/mimo-v2-flash:free` | Xiaomi | Fast card generation |
| `google/gemini-2.0-flash-exp:free` | Google | Summaries |
| `google/gemma-3-27b-it:free` | Google | Chapter detection |
| `deepseek/deepseek-chat:free` | DeepSeek | General chat |
| `qwen/qwen-2.5-72b-instruct:free` | Alibaba | Complex reasoning |

#### Chat Completions Endpoint

**Request**
```http
POST https://openrouter.ai/api/v1/chat/completions

{
  "model": "xiaomi/mimo-v2-flash:free",
  "messages": [
    {
      "role": "system",
      "content": "You are a medical education expert..."
    },
    {
      "role": "user",
      "content": "Your prompt here..."
    }
  ],
  "temperature": 0.7,
  "max_tokens": 8192
}
```

**Response**
```json
{
  "id": "gen-123",
  "model": "xiaomi/mimo-v2-flash",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "Generated response..."
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 100,
    "completion_tokens": 500,
    "total_tokens": 600
  }
}
```

#### Rate Limits

| Model | Requests/Day | Notes |
|-------|--------------|-------|
| Free models | 200 | Varies by model |
| Paid models | Per plan | No limit on paid tiers |

---

## AnkiConnect API

AnkiConnect is a local API that allows external applications to interact with Anki Desktop.

### Base URL

```
http://localhost:8765
```

### Request Format

All AnkiConnect requests use JSON-RPC 2.0 format:

```json
{
  "action": "actionName",
  "version": 6,
  "params": {
    // action-specific parameters
  }
}
```

### Supported Actions

#### 1. Version

Get AnkiConnect version.

**Request**
```json
{
  "action": "version",
  "version": 6
}
```

**Response**
```json
{
  "result": 6,
  "error": null
}
```

#### 2. Deck Names

Get list of all deck names.

**Request**
```json
{
  "action": "deckNames",
  "version": 6
}
```

**Response**
```json
{
  "result": ["Default", "Medical::Anatomy", "Medical::Pharmacology"],
  "error": null
}
```

#### 3. Create Deck

Create a new deck.

**Request**
```json
{
  "action": "createDeck",
  "version": 6,
  "params": {
    "deck": "Medical::New Deck"
  }
}
```

**Response**
```json
{
  "result": 1703189733346,
  "error": null
}
```

#### 4. Model Names

Get list of all note types (models).

**Request**
```json
{
  "action": "modelNames",
  "version": 6
}
```

**Response**
```json
{
  "result": ["Basic", "Basic (and reversed card)", "Cloze"],
  "error": null
}
```

#### 5. Add Note

Add a new note (card) to Anki.

**Request**
```json
{
  "action": "addNote",
  "version": 6,
  "params": {
    "note": {
      "deckName": "Medical::Anatomy",
      "modelName": "Basic",
      "fields": {
        "Front": "What is the heart?",
        "Back": "The heart is a muscular organ that pumps blood..."
      },
      "tags": ["cardiovascular", "anatomy"],
      "options": {
        "allowDuplicate": false
      }
    }
  }
}
```

**Response**
```json
{
  "result": 1703189733347,
  "error": null
}
```

#### 6. Add Notes (Batch)

Add multiple notes in one request.

**Request**
```json
{
  "action": "addNotes",
  "version": 6,
  "params": {
    "notes": [
      {
        "deckName": "Medical::Anatomy",
        "modelName": "Basic",
        "fields": {
          "Front": "Question 1",
          "Back": "Answer 1"
        },
        "tags": ["tag1"]
      },
      {
        "deckName": "Medical::Anatomy",
        "modelName": "Basic",
        "fields": {
          "Front": "Question 2",
          "Back": "Answer 2"
        },
        "tags": ["tag2"]
      }
    ]
  }
}
```

**Response**
```json
{
  "result": [1703189733348, 1703189733349],
  "error": null
}
```

#### 7. Find Notes

Search for notes by query.

**Request**
```json
{
  "action": "findNotes",
  "version": 6,
  "params": {
    "query": "deck:Medical::Anatomy front:Heart"
  }
}
```

**Response**
```json
{
  "result": [1703189733347, 1703189733348],
  "error": null
}
```

#### 8. Get Note Info

Get information about specific notes.

**Request**
```json
{
  "action": "notesInfo",
  "version": 6,
  "params": {
    "notes": [1703189733347]
  }
}
```

**Response**
```json
{
  "result": [
    {
      "noteId": 1703189733347,
      "deckName": "Medical::Anatomy",
      "modelName": "Basic",
      "fields": {
        "Front": "What is the heart?",
        "Back": "The heart is a muscular organ..."
      },
      "tags": ["cardiovascular", "anatomy"]
    }
  ],
  "error": null
}
```

### Python Usage Example

```python
import requests
import json

def anki_connect(action, **params):
    """Make a request to AnkiConnect."""
    url = "http://localhost:8765"
    payload = {
        "action": action,
        "version": 6,
        "params": params
    }
    response = requests.post(url, json=payload)
    return response.json()

# Create a deck
result = anki_connect("createDeck", deck="Medical::Test Deck")

# Add a note
note = {
    "deckName": "Medical::Test Deck",
    "modelName": "Basic",
    "fields": {
        "Front": "Test question",
        "Back": "Test answer"
    },
    "tags": ["test"]
}
result = anki_connect("addNote", note=note)
```

---

## Internal Utility APIs

Internal APIs are Python functions within the `utils/` module. These are not REST APIs but Python functions that components can import.

### Authentication API

**Module:** `utils/auth.py`

#### `register_user(email, password)`

Register a new user account.

```python
def register_user(email: str, password: str) -> tuple[bool, str]:
    """Register a new user.

    Args:
        email: User email address
        password: User password (8+ chars, uppercase, lowercase, digit)

    Returns:
        tuple: (success: bool, message: str)

    Raises:
        ValueError: If password doesn't meet requirements
        FileExistsError: If user already exists
    """
```

**Example:**
```python
from utils.auth import register_user

success, message = register_user("user@example.com", "SecurePass123")
if success:
    print("Registration successful!")
else:
    print(f"Error: {message}")
```

#### `authenticate_user(email, password)`

Authenticate a user and create a session.

```python
def authenticate_user(email: str, password: str) -> tuple[bool, str]:
    """Authenticate a user.

    Args:
        email: User email address
        password: User password

    Returns:
        tuple: (success: bool, session_token_or_error: str)
    """
```

#### `save_api_key(email, provider, key)`

Save an encrypted API key for a user.

```python
def save_api_key(email: str, provider: str, key: str) -> bool:
    """Save an encrypted API key.

    Args:
        email: User email address
        provider: "google", "zai", or "openrouter"
        key: API key to encrypt and store

    Returns:
        True if successful, False otherwise
    """
```

#### `get_api_key(email, provider)`

Retrieve and decrypt a user's API key.

```python
def get_api_key(email: str, provider: str) -> str | None:
    """Get and decrypt an API key.

    Args:
        email: User email address
        provider: "google", "zai", or "openrouter"

    Returns:
        Decrypted API key or None if not found
    """
```

#### `initiate_password_reset(email)`

Initiate password reset flow.

```python
def initiate_password_reset(email: str) -> tuple[bool, str]:
    """Send password reset code via email.

    Args:
        email: User email address

    Returns:
        tuple: (success: bool, message: str)
    """
```

#### `verify_reset_code(email, code)`

Verify a password reset code.

```python
def verify_reset_code(email: str, code: str) -> bool:
    """Verify a reset code.

    Args:
        email: User email address
        code: Reset code to verify

    Returns:
        True if code is valid and not expired
    """
```

#### `reset_password(email, new_password)`

Reset a user's password.

```python
def reset_password(email: str, new_password: str) -> tuple[bool, str]:
    """Reset a user's password.

    Args:
        email: User email address
        new_password: New password (must meet requirements)

    Returns:
        tuple: (success: bool, message: str)
    """
```

---

### LLM Handler API

**Module:** `utils/llm_handler.py`

#### `LLMHandler` Class

```python
class LLMHandler:
    """Handler for LLM API interactions with automatic fallback.

    Attributes:
        provider: Primary provider name
        model: Model name
        api_key: API key for primary provider
        fallback_keys: Dict of backup API keys
    """

    def __init__(
        self,
        provider: str,
        api_key: str,
        model: str,
        fallback_keys: dict | None = None
    ):
        """Initialize LLM handler."""
```

#### `generate_completion(prompt, system_prompt=None)`

Generate a completion from the LLM.

```python
def generate_completion(
    self,
    prompt: str,
    system_prompt: str | None = None
) -> tuple[bool, str]:
    """Generate a completion with automatic fallback.

    Args:
        prompt: User prompt
        system_prompt: Optional system prompt

    Returns:
        tuple: (success: bool, response_or_error: str)
    """
```

**Example:**
```python
from utils.llm_handler import LLMHandler

handler = LLMHandler(
    provider="google",
    api_key="your_api_key",
    model="gemini-3-flash",
    fallback_keys={"zai": "backup_key"}
)

success, response = handler.generate_completion(
    prompt="What are the symptoms of myocardial infarction?",
    system_prompt="You are a medical education expert."
)

if success:
    print(response)
else:
    print(f"Error: {response}")
```

#### `generate_cards(text, options)`

Generate flashcards from text.

```python
def generate_cards(
    self,
    text: str,
    density: str = "normal",
    answer_length: str = "medium",
    highlight_terms: bool = True
) -> tuple[bool, list | str]:
    """Generate flashcards from text.

    Args:
        text: Source text for card generation
        density: "low", "normal", or "high"
        answer_length: "short", "medium", or "long"
        highlight_terms: Whether to bold key terms

    Returns:
        tuple: (success: bool, cards_list_or_error: str)
    """
```

#### `generate_summary(text)`

Generate a summary of text.

```python
def generate_summary(self, text: str) -> tuple[bool, str]:
    """Generate a summary of text.

    Args:
        text: Text to summarize

    Returns:
        tuple: (success: bool, summary_or_error: str)
    """
```

---

### PDF Processor API

**Module:** `utils/pdf_processor.py`

#### `extract_text_from_pdf(file)`

Extract text from a PDF file.

```python
def extract_text_from_pdf(file) -> dict:
    """Extract text from a PDF file.

    Args:
        file: Uploaded file object from Streamlit

    Returns:
        dict: {
            "filename": str,
            "text": str,
            "pages": int,
            "chapters": list[dict]
        }
    """
```

**Example:**
```python
from utils.pdf_processor import extract_text_from_pdf

# In a Streamlit app
uploaded_file = st.file_uploader("Upload PDF")
if uploaded_file:
    result = extract_text_from_pdf(uploaded_file)
    st.write(f"Extracted {result['pages']} pages")
    st.text_area("Content", result['text'][:1000] + "...")
```

#### `detect_chapters(text)`

Detect chapter boundaries in text.

```python
def detect_chapters(text: str) -> list[dict]:
    """Detect chapter boundaries.

    Args:
        text: Full document text

    Returns:
        list[dict]: [
            {
                "title": str,
                "start": int,
                "end": int,
                "level": int
            },
            ...
        ]
    """
```

#### `chunk_text(text, max_size=20000)`

Split text into chunks.

```python
def chunk_text(text: str, max_size: int = 20000) -> list[str]:
    """Split text into chunks.

    Args:
        text: Text to split
        max_size: Maximum chunk size in characters

    Returns:
        list[str]: List of text chunks
    """
```

---

### Data Processing API

**Module:** `utils/data_processing.py`

#### `format_card(front, back, deck, tags, format_mode)`

Format a flashcard for Anki import.

```python
def format_card(
    front: str,
    back: str,
    deck: str,
    tags: list[str],
    format_mode: str = "html"
) -> str:
    """Format a flashcard for Anki import.

    Args:
        front: Card front (question)
        back: Card back (answer)
        deck: Deck name
        tags: List of tags
        format_mode: "html", "markdown", or "latex"

    Returns:
        TAB-separated formatted card string
    """
```

#### `generate_deck_name(filename, chapter=None)`

Generate a deck name with optional chapter subdeck.

```python
def generate_deck_name(
    filename: str,
    chapter: str | None = None
) -> str:
    """Generate a deck name.

    Args:
        filename: PDF filename
        chapter: Optional chapter name

    Returns:
        Deck name like "Medical::Filename::Chapter"
    """
```

#### `push_to_anki(cards, deck_name, url)`

Push cards to Anki via AnkiConnect.

```python
def push_to_anki(
    cards: list[dict],
    deck_name: str,
    url: str = "http://localhost:8765"
) -> tuple[int, int]:
    """Push cards to Anki.

    Args:
        cards: List of card dictionaries with 'front', 'back', 'tags'
        deck_name: Target deck name
        url: AnkiConnect URL

    Returns:
        tuple: (success_count: int, failure_count: int)
    """
```

**Example:**
```python
from utils.data_processing import push_to_anki

cards = [
    {
        "front": "What is the heart?",
        "back": "A muscular organ that pumps blood.",
        "tags": ["cardiovascular"]
    }
]

success, failed = push_to_anki(cards, "Medical::Anatomy")
print(f"Added {success} cards, {failed} failed")
```

#### `export_to_csv(cards)`

Export cards to TAB-separated format.

```python
def export_to_csv(cards: list[dict]) -> str:
    """Export cards to TAB-separated format.

    Args:
        cards: List of card dictionaries

    Returns:
        TAB-separated string for Anki import
    """
```

---

### RAG API

**Module:** `utils/rag.py`

#### `VectorStore` Class

```python
class VectorStore:
    """SQLite-backed vector store for RAG.

    Attributes:
        db_path: Path to SQLite database
        cache: In-memory embedding cache
    """

    def __init__(self, db_path: str = "data/vector_store.db"):
        """Initialize vector store."""
```

#### `add_documents(texts, metadatas)`

Add documents to the vector store.

```python
def add_documents(
    self,
    texts: list[str],
    metadatas: list[dict]
) -> None:
    """Add documents to the vector store.

    Args:
        texts: List of document texts
        metadatas: List of metadata dicts (filename, page, etc.)
    """
```

**Example:**
```python
from utils.rag import VectorStore

store = VectorStore()
store.add_documents(
    texts=["The heart is a muscular organ...", "The brain is the..."],
    metadatas=[
        {"filename": "anatomy.pdf", "page": 1},
        {"filename": "anatomy.pdf", "page": 2}
    ]
)
```

#### `similarity_search(query, k=5)`

Search for similar documents.

```python
def similarity_search(
    self,
    query: str,
    k: int = 5
) -> list[dict]:
    """Search for similar documents.

    Args:
        query: Search query
        k: Number of results to return

    Returns:
        list[dict]: [
            {
                "text": str,
                "metadata": dict,
                "score": float
            },
            ...
        ]
    """
```

#### `rag_query(query, llm_handler)`

Generate an AI response with retrieved context.

```python
def rag_query(
    self,
    query: str,
    llm_handler: LLMHandler
) -> tuple[str, list[dict]]:
    """Generate RAG response.

    Args:
        query: User query
        llm_handler: LLM handler for generation

    Returns:
        tuple: (response: str, sources: list[dict])
    """
```

---

*Last updated: 2025*
