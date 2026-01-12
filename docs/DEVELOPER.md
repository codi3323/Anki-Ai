# Developer Guide

This document provides comprehensive information for developers who want to contribute to, extend, or customize the Medical PDF to Anki Converter application.

## Table of Contents

- [Development Environment Setup](#development-environment-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Debugging](#debugging)
- [Adding New Features](#adding-new-features)
- [Adding New LLM Providers](#adding-new-llm-providers)
- [Customizing UI Components](#customizing-ui-components)
- [Performance Optimization](#performance-optimization)

---

## Development Environment Setup

### Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.11+ | Required for type hinting |
| Git | Latest | For version control |
| Docker | Latest | Optional, for containerized testing |
| VS Code | Latest | Recommended, with Python extension |

### Step 1: Clone Repository

```bash
git clone https://github.com/thies2005/Anki-Ai.git
cd Anki-Ai
```

### Step 2: Create Virtual Environment

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install pytest pytest-cov black isort mypy
```

### Step 4: Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
# At minimum, configure one provider:
# GOOGLE_API_KEY=your_key_here
# or
# ZAI_API_KEY=your_key_here
```

### Step 5: Run Development Server

```bash
# Run Streamlit in development mode
streamlit run app.py

# With auto-reload (requires streamlit-server-state)
streamlit run app.py --server.runOnSave true
```

### Step 6: Verify Setup

1. Open `http://localhost:8501`
2. Register a new account
3. Configure an API key in the sidebar
4. Upload a test PDF and generate cards

---

## Project Structure

### Directory Layout

```
Anki-Ai/
├── app.py                      # Application entry point
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
│
├── components/                # UI Components
│   ├── __init__.py
│   ├── generator.py          # Card generation UI
│   ├── sidebar.py            # Settings panel
│   ├── chat.py               # PDF chat interface
│   ├── standalone_chat.py    # General AI chat
│   ├── cards_view.py         # Card display/export
│   ├── header.py             # Navigation header
│   ├── login.py              # Authentication UI
│   ├── onboarding.py         # First-time setup
│   ├── pdf_viewer.py         # PDF display
│   ├── card_viewer.py        # Card preview
│   └── styles.py             # CSS/theming
│
├── utils/                    # Business Logic
│   ├── __init__.py
│   ├── auth.py               # Authentication
│   ├── llm_handler.py        # LLM integration
│   ├── pdf_processor.py      # PDF processing
│   ├── data_processing.py    # Card formatting
│   ├── rag.py                # Vector store
│   ├── common.py             # Shared utilities
│   └── styles.py             # Style utilities
│
├── data/                     # Runtime data (gitignored)
│   ├── users.json           # User database
│   ├── vector_store.db      # RAG embeddings
│   └── history/             # User history
│
├── tests/                    # Test suite
│   ├── test_auth.py
│   ├── test_pdf_processor.py
│   └── test_rag.py
│
└── docs/                     # Documentation
    ├── ARCHITECTURE.md
    ├── COMPONENTS.md
    ├── API.md
    ├── DEVELOPER.md          # This file
    ├── DEPLOYMENT.md
    └── CONTRIBUTING.md
```

### Import Conventions

```python
# Import components
from components.generator import render_generator
from components.sidebar import render_sidebar

# Import utilities
from utils.auth import authenticate_user, register_user
from utils.llm_handler import LLMHandler
from utils.pdf_processor import extract_text_from_pdf
```

---

## Coding Standards

### Python Style Guide

The project follows **PEP 8** with some modifications:

| Rule | Standard | Notes |
|------|----------|-------|
| Line length | 100 (soft), 120 (hard) | Black formatter default |
| Quotes | Double | `"""` for docstrings, `"` for strings |
| Imports | Grouped | stdlib, third-party, local |
| Type hints | Required | All public functions |

### Example Code Style

```python
"""Module docstring.

This module provides functionality for...
"""

from __future__ import annotations

import streamlit as st
from utils.common import validate_email


def my_function(param1: str, param2: int | None) -> bool:
    """Function docstring.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value
    """
    if not param1:
        return False

    result = process_data(param1, param2 or 0)
    return result


def _private_helper(value: str) -> str:
    """Private helper function.

    Args:
        value: Input value

    Returns:
        Processed value
    """
    return value.strip().lower()
```

### Docstring Format

Use **Google-style docstrings**:

```python
def generate_cards(
    text: str,
    density: str = "normal",
    answer_length: str = "medium"
) -> list[dict]:
    """Generate flashcards from text.

    This function processes input text and generates
    flashcards based on the specified density and
    answer length settings.

    Args:
        text: Source text for card generation
        density: Card density ("low", "normal", "high")
        answer_length: Answer detail ("short", "medium", "long")

    Returns:
        List of card dictionaries with 'front', 'back', 'tags' keys

    Raises:
        ValueError: If density or answer_length is invalid

    Example:
        >>> cards = generate_cards("The heart pumps blood...")
        >>> print(cards[0]["front"])
        "What is the function of the heart?"
    """
```

### Type Hints

All functions should have type hints:

```python
from typing import Optional, List, Dict, Tuple, Union

# Modern syntax (Python 3.10+)
def process_data(items: list[str]) -> dict[str, int]:
    return {item: len(item) for item in items}

# With Optional
def find_user(email: str | None) -> dict | None:
    if not email:
        return None
    return {"email": email}

# With Union
def parse_value(value: str | int | float) -> float:
    return float(value)

# With TypedDict
from typing import TypedDict

class Card(TypedDict):
    front: str
    back: str
    tags: list[str]
    deck: str
```

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=utils --cov=components

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

### Test Structure

```python
"""Test module for auth.py."""

import pytest
from utils.auth import register_user, authenticate_user


class TestAuthentication:
    """Test authentication functions."""

    def test_register_user_success(self, tmp_path):
        """Test successful user registration."""
        # Arrange
        email = "test@example.com"
        password = "SecurePass123"

        # Act
        success, message = register_user(email, password)

        # Assert
        assert success is True
        assert "successfully" in message.lower()

    def test_register_user_invalid_password(self):
        """Test registration with invalid password."""
        success, message = register_user("test@example.com", "weak")
        assert success is False

    @pytest.fixture
    def clean_user_data(self, tmp_path):
        """Fixture to clean user data after test."""
        yield
        # Cleanup code
        pass
```

### Writing Tests

1. **Unit Tests**: Test individual functions in isolation
2. **Integration Tests**: Test component interactions
3. **Fixtures**: Use pytest fixtures for common setup

```python
import pytest
from utils.pdf_processor import extract_text_from_pdf, chunk_text


class TestPDFProcessor:
    """Test PDF processing utilities."""

    def test_chunk_text_basic(self):
        """Test basic text chunking."""
        text = "Word " * 10000  # 50,000 characters
        chunks = chunk_text(text, max_size=10000)

        assert len(chunks) == 5
        for chunk in chunks:
            assert len(chunk) <= 10000

    def test_chunk_text_preserves_sentences(self):
        """Test that chunking doesn't break sentences."""
        text = "This is sentence one. This is sentence two. " * 1000
        chunks = chunk_text(text, max_size=500)

        # No chunk should end mid-sentence
        for chunk in chunks:
            assert not chunk.endswith(". This")
```

---

## Debugging

### Streamlit Debugging

```python
import streamlit as st

# Print debug info to the UI
st.write(st.session_state)

# Display JSON nicely
st.json({"key": "value"})

# Show exception traceback
try:
    risky_operation()
except Exception as e:
    st.exception(e)
```

### Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Use in code
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message", exc_info=True)
```

### Remote Debugging (VS Code)

Create `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Streamlit",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/venv/bin/streamlit",
            "args": ["run", "app.py"],
            "console": "integratedTerminal",
            "justMyCode": false
        }
    ]
}
```

### Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Session state lost | Page rerun | Use `st.session_state` for persistence |
| API rate limit | Too many requests | Use fallback keys, reduce batch size |
| PDF parse error | Corrupted PDF | Try `pdfplumber` as fallback |
| AnkiConnect timeout | Anki not running | Start Anki Desktop with AnkiConnect |

---

## Adding New Features

### Adding a New Component

1. Create component file in `components/`

```python
# components/my_component.py
"""My new component."""

import streamlit as st


def render_my_component():
    """Render my new component."""
    st.title("My Component")
    st.write("Content here...")
```

2. Import and use in `app.py`:

```python
from components.my_component import render_my_component

# In your render_app() function
if st.session_state.view == "my_component":
    render_my_component()
```

### Adding a New Setting

1. Add to `components/sidebar.py`:

```python
def render_sidebar():
    """Render the sidebar."""
    # ... existing code ...

    # New setting
    st.session_state.my_new_setting = st.selectbox(
        "My New Setting",
        options=["Option 1", "Option 2"],
        index=0
    )
```

2. Use in your component:

```python
if st.session_state.my_new_setting == "Option 1":
    # Do something
```

3. Persist in `utils/auth.py`:

```python
def save_preferences(email: str, preferences: dict) -> None:
    """Save user preferences."""
    users = load_users()
    if email in users:
        users[email]["preferences"].update(preferences)
        save_users(users)
```

---

## Adding New LLM Providers

### Step 1: Update LLM Handler

Add provider configuration to `utils/llm_handler.py`:

```python
# In LLMHandler.__init__
PROVIDER_CONFIGS = {
    # ... existing providers ...
    "my_provider": {
        "base_url": "https://api.myprovider.com/v1",
        "models": {
            "model-1": "My Provider Model 1",
            "model-2": "My Provider Model 2"
        },
        "headers": lambda key: {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
    }
}
```

### Step 2: Implement API Call

```python
def call_my_provider(self, prompt: str, system_prompt: str | None) -> tuple[bool, str]:
    """Call My Provider API.

    Args:
        prompt: User prompt
        system_prompt: Optional system prompt

    Returns:
        tuple: (success, response_or_error)
    """
    config = PROVIDER_CONFIGS["my_provider"]
    headers = config["headers"](self.api_key)

    payload = {
        "model": self.model,
        "messages": [
            {"role": "system", "content": system_prompt or "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(
            f"{config['base_url']}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()

        data = response.json()
        content = data["choices"][0]["message"]["content"]
        return True, content

    except requests.HTTPError as e:
        if e.response.status_code == 429:
            # Rate limited, try fallback
            return self._try_fallback(prompt, system_prompt)
        return False, f"API error: {e}"
    except Exception as e:
        return False, f"Error: {e}"
```

### Step 3: Update Sidebar

Add to `components/sidebar.py`:

```python
# In render_sidebar()
MY_PROVIDER_MODELS = ["model-1", "model-2"]

st.session_state.my_provider_model = st.selectbox(
    "Model (My Provider)",
    options=MY_PROVIDER_MODELS,
    index=0
)
```

### Step 4: Update Environment

Add to `.env.example`:

```env
MY_PROVIDER_API_KEY=your_key_here
```

---

## Customizing UI Components

### Custom CSS

Edit `components/styles.py`:

```python
def get_custom_css() -> str:
    """Get custom CSS for the app."""
    return """
    <style>
    /* Your custom styles */
    .my-custom-class {
        background-color: #f0f0f0;
        padding: 1rem;
        border-radius: 0.5rem;
    }

    /* Target specific elements */
    div[data-testid="stFileUploader"] {
        border: 2px dashed #4a9eff;
    }
    </style>
    """
```

### Custom Streamlit Elements

```python
import streamlit as st

# Custom button with icon
def icon_button(label: str, icon: str, key: str):
    """Render a button with an icon."""
    cols = st.columns([1, 10])
    with cols[0]:
        st.markdown(f"{icon}")
    with cols[1]:
        return st.button(label, key=key)

# Usage
if icon_button("Generate", "🚀", "gen_btn"):
    st.write("Generating...")
```

---

## Performance Optimization

### PDF Processing Optimization

```python
# Use multiprocessing for large PDFs
from concurrent.futures import ProcessPoolExecutor

def process_multiple_pdfs(files):
    """Process multiple PDFs in parallel."""
    with ProcessPoolExecutor() as executor:
        results = executor.map(extract_text_from_pdf, files)
    return list(results)
```

### Caching

```python
# Streamlit caching for expensive operations
@st.cache_data(ttl=3600)  # Cache for 1 hour
def expensive_operation(data):
    """Cache expensive operations."""
    # Expensive computation
    return result

# For data that changes
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_user_preferences(email):
    """Cache user preferences."""
    return load_user_prefs(email)
```

### Database Optimization

```python
# Use connection pooling
import sqlite3
from contextlib import contextmanager

@contextmanager
def get_db_connection():
    """Get database connection with pooling."""
    conn = sqlite3.connect("data/vector_store.db")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# Usage
with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chunks LIMIT 10")
    results = cursor.fetchall()
```

### Async Operations

For long-running operations, use Streamlit's status updates:

```python
import time
import streamlit as st

def long_running_task():
    """Task with progress updates."""
    progress_bar = st.progress(0)
    status_text = st.empty()

    steps = ["Step 1", "Step 2", "Step 3"]
    for i, step in enumerate(steps):
        status_text.text(f"Processing: {step}")
        time.sleep(1)  # Simulate work
        progress_bar.progress((i + 1) / len(steps))

    status_text.text("Complete!")
    progress_bar.empty()
```

---

## Best Practices

### Security

1. **Never commit API keys** - Use environment variables
2. **Validate user input** - Check email format, password strength
3. **Encrypt sensitive data** - Use Fernet for API keys
4. **Use parameterized queries** - Prevent SQL injection
5. **Rate limit** - Prevent abuse

### Error Handling

```python
# Always handle exceptions
try:
    result = api_call()
except APIError as e:
    st.error(f"API error: {e}")
    logger.error(f"API call failed: {e}", exc_info=True)
except Exception as e:
    st.error("An unexpected error occurred")
    logger.critical(f"Unexpected error: {e}", exc_info=True)
```

### Logging

```python
# Use appropriate log levels
logger.debug("Detailed debugging info")
logger.info("Normal operation info")
logger.warning("Something unusual but not error")
logger.error("Error occurred")
logger.critical("Critical failure")
```

---

*Last updated: 2025*
