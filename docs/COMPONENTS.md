# Components Documentation

This document provides detailed documentation for all components in the Medical PDF to Anki Converter application.

## Table of Contents

- [Components Layer](#components-layer)
  - [Generator](#generator-generatorpy)
  - [Sidebar](#sidebar-sidebarpy)
  - [Chat](#chat-chatpy)
  - [Standalone Chat](#standalone-chat-standalone_chatpy)
  - [Cards View](#cards-view-cards_viewpy)
  - [Header](#header-headerpy)
  - [Login](#login-loginpy)
  - [Onboarding](#onboarding-onboardingpy)
  - [PDF Viewer](#pdf-viewer-pdf_viewerpy)
  - [Card Viewer](#card-viewer-card_viewerpy)
  - [Styles](#styles-stylespy)
- [Utilities Layer](#utilities-layer)
  - [Auth](#auth-authpy)
  - [LLM Handler](#llm-handler-llm_handlerpy)
  - [PDF Processor](#pdf-processor-pdf_processorpy)
  - [Data Processing](#data-processing-data_processingpy)
  - [RAG](#rag-ragpy)
  - [Common](#common-commonpy)

---

## Components Layer

### Generator (`generator.py`)

The **Generator** component is the primary interface for uploading PDFs and generating flashcards. It's the main view users see after logging in.

#### Location
`components/generator.py` (~35KB, 900+ lines)

#### Responsibilities
- Multi-file PDF upload with drag-and-drop interface
- Processing mode selection (Process Files vs Fast Track)
- Configuration of card generation options
- Initiation of AI card generation
- Display of generation progress and results

#### Key Functions

##### `render_generator()`
Main rendering function that orchestrates the generator interface.

```python
def render_generator() -> None:
    """Render the main card generation interface."""
```

**Flow:**
1. Display file uploader
2. Show uploaded files with remove buttons
3. Display processing options
4. On submit, process files and generate cards

##### `process_files(uploaded_files, options)`
Processes uploaded PDF files based on selected options.

```python
def process_files(
    uploaded_files: list,
    fast_track: bool,
    card_density: str,
    answer_length: str,
    highlight_terms: bool,
    detect_chapters: bool,
    show_general_chat: bool
) -> None:
```

**Parameters:**
- `uploaded_files`: List of uploaded PDF file objects
- `fast_track`: Skip summaries if True
- `card_density`: "Low", "Normal", or "High"
- `answer_length`: "Short", "Medium", or "Long"
- `highlight_terms`: Bold important keywords if True
- `detect_chapters`: Split PDFs into chapters if True
- `show_general_chat`: Enable split-view chat panel

##### `display_processing_results()`
Shows the results of card generation with export options.

```python
def display_processing_results() -> None:
```

**Features:**
- Summary of generated cards
- Card preview (first 10 cards)
- Download button for TAB-separated export
- Push to Anki button (if AnkiConnect available)

#### Session State Variables

| Variable | Type | Purpose |
|----------|------|---------|
| `pdf_files` | list | Currently uploaded PDF files |
| `processing` | bool | Indicates active processing |
| `summaries` | dict | AI summaries per file |
| `generated_cards` | list | Generated flashcard objects |
| `cards_df` | DataFrame | Pandas DataFrame of cards |

#### UI Layout

```
┌─────────────────────────────────────────────────────────────┐
│  📄 Upload PDF Files                                        │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  Drag and drop PDF files here                           ││
│  │  or click to browse                                     ││
│  └─────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────┤
│  📁 Uploaded Files                                         │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ ☑ textbook_chapter1.pdf  [🗑️ Remove]                   ││
│  │ ☑ textbook_chapter2.pdf  [🗑️ Remove]                   ││
│  └─────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────┤
│  ⚙️ Processing Options                                     │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Mode: ⦿ Process Files  ⦾ Fast Track                    ││
│  │ Card Density: ⦿ Normal  ⦾ Low  ⦾ High                 ││
│  │ Answer Length: ⦿ Medium  ⦾ Short  ⦾ Long              ││
│  │ ☑ Highlight Key Terms                                  ││
│  │ ☑ Auto-Detect Chapters                                 ││
│  └─────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────┤
│                    [🚀 Generate Cards]                      │
└─────────────────────────────────────────────────────────────┘
```

---

### Sidebar (`sidebar.py`)

The **Sidebar** component provides configuration options for API keys, model selection, and global settings.

#### Location
`components/sidebar.py` (~10KB, 300+ lines)

#### Responsibilities
- API key input and storage
- Model selection per provider
- Global application settings
- User preferences persistence

#### Key Functions

##### `render_sidebar()`
Main rendering function for the sidebar.

```python
def render_sidebar() -> None:
    """Render the configuration sidebar."""
```

**Features:**
- API key inputs for each provider
- Model selection dropdowns
- Global settings (chunk size, formatting mode, etc.)
- Theme toggle
- User profile section

##### `save_api_key(provider, key)`
Encrypts and saves an API key to the user profile.

```python
def save_api_key(provider: str, key: str) -> bool:
```

**Parameters:**
- `provider`: "google", "zai", or "openrouter"
- `key`: API key string

**Returns:** True if successful, False otherwise

##### `get_models_for_provider(provider)`
Returns available models for a given provider.

```python
def get_models_for_provider(provider: str) -> list[str]:
```

#### Settings Options

| Setting | Options | Default | Description |
|---------|---------|---------|-------------|
| Provider | Google, Z.AI, OpenRouter | Z.AI | Primary AI provider |
| Model (Google) | gemini-2.5-flash, gemini-3-flash, gemma-3-27b-it | gemini-3-flash | Google model |
| Model (Z.AI) | GLM-4.7, GLM-4.5-air | GLM-4.7 | Z.AI model |
| Model (OpenRouter) | 100+ options | xiaomi/mimo-v2-flash:free | OpenRouter model |
| Chunk Size | 5000-50000 characters | 20000 | Text chunk size for processing |
| Formatting Mode | Basic + HTML, Markdown, Legacy LaTeX | Basic + HTML | Card output format |
| Deck Organization | Subdecks, Tags, Both | Subdecks | Anki organization |
| Theme Mode | Dark, Light | Dark | UI theme |

---

### Chat (`chat.py`)

The **Chat** component provides an AI-powered chat interface for interacting with PDF content using RAG (Retrieval-Augmented Generation).

#### Location
`components/chat.py` (~15KB, 400+ lines)

#### Responsibilities
- Display chat interface with message history
- Handle user queries
- Retrieve relevant PDF chunks
- Generate AI responses with citations
- Display source documents for answers

#### Key Functions

##### `render_chat(pdf_text=None)`
Main rendering function for the chat interface.

```python
def render_chat(pdf_text: str | None = None) -> None:
    """Render the chat interface.

    Args:
        pdf_text: Optional PDF text for context. If None, uses RAG.
    """
```

##### `handle_user_query(query, pdf_text)`
Processes a user query and generates an AI response.

```python
def handle_user_query(query: str, pdf_text: str | None = None) -> tuple[str, list]:
    """Process user query and return response with sources.

    Args:
        query: User's question
        pdf_text: Optional PDF text for direct context

    Returns:
        tuple: (response_text, source_documents)
    """
```

#### Chat Message Format

Messages are stored in `st.session_state.messages` as dictionaries:

```python
{
    "role": "user" | "assistant",
    "content": str,
    "sources": list[dict]  # For assistant messages only
}
```

#### Source Display Format

```python
{
    "filename": str,
    "page": int,
    "chunk_id": int,
    "relevance_score": float,
    "preview": str  # First 100 chars of the chunk
}
```

---

### Standalone Chat (`standalone_chat.py`)

The **Standalone Chat** component provides a general AI chat interface without PDF context. Useful for general questions and explanations.

#### Location
`components/standalone_chat.py` (~8KB, 200+ lines)

#### Responsibilities
- Display chat interface
- Handle general AI queries
- Maintain conversation history
- No PDF context required

#### Key Functions

##### `render_standalone_chat()`
Main rendering function.

```python
def render_standalone_chat() -> None:
    """Render the standalone chat interface."""
```

#### Differences from `chat.py`

| Feature | chat.py | standalone_chat.py |
|---------|---------|-------------------|
| PDF Context | Yes (via RAG) | No |
| Source Citations | Yes | No |
| Vector Store | Required | Not required |
| Use Case | PDF-specific Q&A | General questions |

---

### Cards View (`cards_view.py`)

The **Cards View** component displays generated flashcards with options to view, edit, and export.

#### Location
`components/cards_view.py` (~12KB, 350+ lines)

#### Responsibilities
- Display generated cards in a tabular format
- Allow card editing
- Provide export options
- Push cards to Anki

#### Key Functions

##### `render_cards_view()`
Main rendering function.

```python
def render_cards_view() -> None:
    """Render the cards view interface."""
```

##### `export_cards(format)`
Exports cards in the specified format.

```python
def export_cards(format: str = "tab") -> bytes:
    """Export cards in specified format.

    Args:
        format: "tab", "csv", or "json"

    Returns:
        File content as bytes
    """
```

##### `push_to_anki(deck_name)`
Pushes cards to Anki via AnkiConnect.

```python
def push_to_anki(deck_name: str) -> tuple[bool, str]:
    """Push cards to Anki.

    Args:
        deck_name: Target deck name

    Returns:
        tuple: (success, message)
    """
```

---

### Header (`header.py`)

The **Header** component provides navigation and user information at the top of the application.

#### Location
`components/header.py` (~5KB, 150+ lines)

#### Responsibilities
- Display app title and logo
- Show navigation tabs
- Display user information
- Logout button

#### Key Functions

##### `render_header()`
Main rendering function.

```python
def render_header() -> None:
    """Render the application header."""
```

#### Navigation Tabs

| Tab | Query Param | Description |
|-----|-------------|-------------|
| Generator | (default) | Main card generation interface |
| Chat | `view=chat` | Standalone AI chat |
| Cards | `view=cards` | View generated cards |

---

### Login (`login.py`)

The **Login** component handles user authentication (login, registration, password reset).

#### Location
`components/login.py` (~15KB, 400+ lines)

#### Responsibilities
- User registration form
- Login form
- Password reset request
- Password reset verification
- Guest mode entry

#### Key Functions

##### `render_login()`
Main rendering function that switches between login modes.

```python
def render_login() -> None:
    """Render the login interface."""
```

##### `handle_registration(email, password)`
Processes user registration.

```python
def handle_registration(email: str, password: str) -> tuple[bool, str]:
    """Handle user registration.

    Args:
        email: User email address
        password: User password

    Returns:
        tuple: (success, message)
    """
```

##### `handle_login(email, password)`
Processes user login.

```python
def handle_login(email: str, password: str) -> tuple[bool, str]:
    """Handle user login.

    Args:
        email: User email address
        password: User password

    Returns:
        tuple: (success, message)
    """
```

##### `handle_password_reset_request(email)`
Initiates password reset.

```python
def handle_password_reset_request(email: str) -> tuple[bool, str]:
    """Handle password reset request.

    Args:
        email: User email address

    Returns:
        tuple: (success, message)
    """
```

#### Login States

| State | Description |
|-------|-------------|
| `login` | Default login form |
| `register` | New user registration |
| `reset_request` | Request password reset |
| `reset_verify` | Verify reset code and set new password |

---

### Onboarding (`onboarding.py`)

The **Onboarding** component guides first-time users through API key configuration.

#### Location
`components/onboarding.py` (~8KB, 200+ lines)

#### Responsibilities
- Welcome screen for new users
- API key setup wizard
- Provider selection
- First card generation tutorial

#### Key Functions

##### `render_onboarding()`
Main rendering function.

```python
def render_onboarding() -> None:
    """Render the onboarding wizard."""
```

##### `complete_onboarding()`
Marks onboarding as complete and redirects to generator.

```python
def complete_onboarding() -> None:
    """Complete onboarding and redirect to generator."""
```

---

### PDF Viewer (`pdf_viewer.py`)

The **PDF Viewer** component displays uploaded PDFs in the browser.

#### Location
`components/pdf_viewer.py` (~6KB, 150+ lines)

#### Responsibilities
- Render PDF content in browser
- Page navigation
- Text selection
- Full-screen mode

#### Key Functions

##### `render_pdf_viewer(file)`
Displays a PDF file.

```python
def render_pdf_viewer(file) -> None:
    """Render a PDF file in the viewer.

    Args:
        file: Uploaded file object
    """
```

---

### Card Viewer (`card_viewer.py`)

The **Card Viewer** component provides a preview of flashcards before export.

#### Location
`components/card_viewer.py` (~7KB, 180+ lines)

#### Responsibilities
- Display cards in flip-card format
- Allow card editing
- Batch editing
- Delete individual cards

#### Key Functions

##### `render_card_viewer(cards)`
Displays cards for preview and editing.

```python
def render_card_viewer(cards: list) -> list:
    """Render card viewer and return modified cards.

    Args:
        cards: List of card dictionaries

    Returns:
        Modified list of cards
    """
```

---

### Styles (`styles.py`)

The **Styles** component manages CSS and theming for the application.

#### Location
`components/styles.py` (~10KB, 250+ lines)

#### Responsibilities
- Dark/Light theme definitions
- Custom CSS injection
- Responsive design
- Component-specific styling

#### Key Functions

##### `get_css(theme_mode)`
Returns CSS for the specified theme.

```python
def get_css(theme_mode: str = "dark") -> str:
    """Get CSS for the specified theme.

    Args:
        theme_mode: "dark" or "light"

    Returns:
        CSS string
    """
```

##### `inject_styles()`
Injects the current theme's CSS into the Streamlit app.

```python
def inject_styles() -> None:
    """Inject current theme styles into the app."""
```

#### Theme Variables

| Variable | Dark | Light |
|----------|------|-------|
| `--bg-primary` | #0e1117 | #ffffff |
| `--bg-secondary` | #1a1d24 | #f0f2f6 |
| `--text-primary` | #fafafa | #0e1117 |
| `--text-secondary` | #b8b8b8 | #5a5a5a |
| `--accent` | #4a9eff | #0069ff |
| `--border` | #30363d | #d0d7de |

---

## Utilities Layer

### Auth (`auth.py`)

The **Auth** utility handles all authentication and user management operations.

#### Location
`utils/auth.py` (~20KB, 500+ lines)

#### Responsibilities
- User registration and login
- Password hashing and verification
- API key encryption and storage
- Session management
- Password reset flow
- User preferences

#### Key Functions

##### `register_user(email, password)`
Registers a new user.

```python
def register_user(email: str, password: str) -> tuple[bool, str]:
    """Register a new user.

    Args:
        email: User email address
        password: User password (must meet requirements)

    Returns:
        tuple: (success, message)

    Raises:
        ValueError: If password doesn't meet requirements
    """
```

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit

##### `authenticate_user(email, password)`
Authenticates a user.

```python
def authenticate_user(email: str, password: str) -> tuple[bool, str]:
    """Authenticate a user.

    Args:
        email: User email address
        password: User password

    Returns:
        tuple: (success, session_token or error_message)
    """
```

##### `save_api_key(email, provider, key)`
Saves an encrypted API key.

```python
def save_api_key(email: str, provider: str, key: str) -> bool:
    """Save an encrypted API key for a user.

    Args:
        email: User email address
        provider: "google", "zai", or "openrouter"
        key: API key to encrypt and store

    Returns:
        True if successful, False otherwise
    """
```

**Encryption Method:** Fernet (AES-128-CBC with HMAC)

##### `get_api_key(email, provider)`
Retrieves and decrypts an API key.

```python
def get_api_key(email: str, provider: str) -> str | None:
    """Get and decrypt an API key for a user.

    Args:
        email: User email address
        provider: "google", "zai", or "openrouter"

    Returns:
        Decrypted API key or None if not found
    """
```

##### `initiate_password_reset(email)`
Initiates the password reset flow.

```python
def initiate_password_reset(email: str) -> tuple[bool, str]:
    """Initiate password reset for a user.

    Sends a reset code via email.

    Args:
        email: User email address

    Returns:
        tuple: (success, message)
    """
```

**Process:**
1. Generate cryptographically secure reset code
2. Hash the reset code (SHA-256)
3. Store hashed code with expiration (15 minutes)
4. Send email with reset code

##### `verify_reset_code(email, code)`
Verifies a password reset code.

```python
def verify_reset_code(email: str, code: str) -> bool:
    """Verify a password reset code.

    Uses timing-safe comparison to prevent timing attacks.

    Args:
        email: User email address
        code: Reset code to verify

    Returns:
        True if code is valid and not expired
    """
```

##### `reset_password(email, new_password)`
Resets a user's password.

```python
def reset_password(email: str, new_password: str) -> tuple[bool, str]:
    """Reset a user's password.

    Args:
        email: User email address
        new_password: New password (must meet requirements)

    Returns:
        tuple: (success, message)
    """
```

#### Rate Limiting

```python
def check_rate_limit(operation: str, identifier: str) -> bool:
    """Check if an operation is rate limited.

    Args:
        operation: "login", "register", "reset_request", "reset_verify"
        identifier: Email address or IP address

    Returns:
        True if allowed, False if rate limited
    """
```

**Limits:**
- 5 attempts per 5 minutes for all operations

---

### LLM Handler (`llm_handler.py`)

The **LLM Handler** utility provides a unified interface for interacting with multiple AI providers.

#### Location
`utils/llm_handler.py` (~32KB, 800+ lines)

#### Responsibilities
- Abstract differences between AI providers
- Handle API authentication
- Implement automatic fallback on rate limits
- Model-specific prompt optimization
- Error handling and retry logic

#### Supported Providers

| Provider | Models | API Base URL |
|----------|--------|--------------|
| Google AI | gemini-2.5-flash, gemini-3-flash, gemma-3-27b-it | https://generativelanguage.googleapis.com |
| Z.AI | GLM-4.7, GLM-4.5-air | https://api.z.ai |
| OpenRouter | 100+ models | https://openrouter.ai/api |

#### Key Classes

##### `LLMHandler`
Main handler class for LLM interactions.

```python
class LLMHandler:
    """Handler for LLM API interactions with automatic fallback."""

    def __init__(
        self,
        provider: str,
        api_key: str,
        model: str,
        fallback_keys: dict | None = None
    ):
        """Initialize LLM handler.

        Args:
            provider: Primary provider ("google", "zai", "openrouter")
            api_key: API key for primary provider
            model: Model name
            fallback_keys: Optional dict of backup API keys
        """
```

##### Methods

###### `generate_completion(prompt, system_prompt=None)`
Generates a completion from the LLM.

```python
def generate_completion(
    self,
    prompt: str,
    system_prompt: str | None = None
) -> tuple[bool, str]:
    """Generate a completion.

    Args:
        prompt: User prompt
        system_prompt: Optional system prompt

    Returns:
        tuple: (success, response_text or error_message)
    """
```

**Behavior:**
1. Try primary provider
2. On rate limit (429), try fallback providers
3. Return success or error message

#### Model-Specific Prompts

Different models receive optimized prompts for best performance:

```python
PROMPT_TEMPLATES = {
    "gemini": {
        "card_generation": "You are a medical education expert...",
        "summary": "Summarize the following medical text...",
        "chat": "You are a helpful medical tutor..."
    },
    "glm": {
        "card_generation": "请生成高质量的医学卡片...",  # Chinese-optimized
        "summary": "总结以下医学文本...",
        "chat": "你是一位医学导师..."
    },
    # ... more templates
}
```

---

### PDF Processor (`pdf_processor.py`)

The **PDF Processor** utility handles text extraction and processing from PDF files.

#### Location
`utils/pdf_processor.py` (~8KB, 200+ lines)

#### Responsibilities
- Extract text from PDF files
- Detect chapter boundaries
- Split text into chunks
- Clean and normalize text

#### Key Functions

##### `extract_text_from_pdf(file)`
Extracts text from a PDF file.

```python
def extract_text_from_pdf(file) -> dict:
    """Extract text from a PDF file.

    Args:
        file: Uploaded file object

    Returns:
        dict: {
            "filename": str,
            "text": str,
            "pages": int,
            "chapters": list[dict]
        }
    """
```

**Features:**
- Handles multi-column layouts
- Removes headers/footers
- Preserves paragraph structure
- Extracts page numbers

##### `detect_chapters(text)`
Detects chapter boundaries in text.

```python
def detect_chapters(text: str) -> list[dict]:
    """Detect chapter boundaries in text.

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

**Detection Heuristics:**
1. Lines in ALL CAPS
2. Lines starting with "Chapter"
3. Roman numerals (I., II., III., etc.)
4. Numbered sections (1., 2., 3., etc.)

##### `chunk_text(text, max_size=20000)`
Splits text into manageable chunks.

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

**Splitting Strategy:**
1. Try to split on paragraph boundaries
2. If paragraph too long, split on sentences
3. Preserve sentence structure
4. Avoid splitting mid-sentence

---

### Data Processing (`data_processing.py`)

The **Data Processing** utility handles card formatting and Anki integration.

#### Location
`utils/data_processing.py` (~10KB, 250+ lines)

#### Responsibilities
- Format flashcards for Anki import
- Generate deck names
- Interact with AnkiConnect
- Export to various formats

#### Key Functions

##### `format_card(front, back, deck, tags, format_mode)`
Formats a flashcard for Anki import.

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
        Formatted card string
    """
```

**Output Format (TAB-separated):**
```
Front	Back	Tags	Deck
What is the main function of the heart?	The heart pumps blood throughout the body.	cardiovascular	Medical::Anatomy::Heart
```

##### `generate_deck_name(filename, chapter=None)`
Generates a deck name with optional chapter subdeck.

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

##### `push_to_anki(cards, deck_name, url)`
Pushes cards to Anki via AnkiConnect.

```python
def push_to_anki(
    cards: list[dict],
    deck_name: str,
    url: str = "http://localhost:8765"
) -> tuple[int, int]:
    """Push cards to Anki.

    Args:
        cards: List of card dictionaries
        deck_name: Target deck name
        url: AnkiConnect URL

    Returns:
        tuple: (success_count, failure_count)
    """
```

**AnkiConnect Actions:**
1. Check if deck exists, create if not
2. Get available models
3. Add notes (cards)
4. Return results

---

### RAG (`rag.py`)

The **RAG** utility implements Retrieval-Augmented Generation for the chat interface.

#### Location
`utils/rag.py` (~12KB, 300+ lines)

#### Responsibilities
- Create and manage vector store
- Generate embeddings
- Perform similarity search
- Retrieve context for queries

#### Key Classes

##### `VectorStore`
SQLite-backed vector store with in-memory caching.

```python
class VectorStore:
    """SQLite-backed vector store for RAG."""

    def __init__(self, db_path: str = "data/vector_store.db"):
        """Initialize vector store.

        Args:
            db_path: Path to SQLite database
        """
```

##### Methods

###### `add_documents(texts, metadatas)`
Adds documents to the vector store.

```python
def add_documents(
    self,
    texts: list[str],
    metadatas: list[dict]
) -> None:
    """Add documents to the vector store.

    Args:
        texts: List of document texts
        metadatas: List of metadata dictionaries
    """
```

**Process:**
1. Generate embeddings for each text
2. Store in SQLite with embeddings
3. Cache in memory for faster retrieval

###### `similarity_search(query, k=5)`
Searches for similar documents.

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

**Algorithm:**
1. Generate query embedding
2. Calculate cosine similarity with all stored embeddings
3. Return top K results

---

### Common (`common.py`)

The **Common** utility contains shared helper functions.

#### Location
`utils/common.py` (~5KB, 150+ lines)

#### Key Functions

##### `sanitize_filename(filename)`
Sanitizes a filename for safe file system usage.

```python
def sanitize_filename(filename: str) -> str:
    """Sanitize a filename.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
```

##### `truncate_text(text, max_length)`
Truncates text to a maximum length.

```python
def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length.

    Args:
        text: Text to truncate
        max_length: Maximum length

    Returns:
        Truncated text with ellipsis
    """
```

##### `validate_email(email)`
Validates an email address.

```python
def validate_email(email: str) -> bool:
    """Validate an email address.

    Args:
        email: Email to validate

    Returns:
        True if valid, False otherwise
    """
```

---

*Last updated: 2025*
