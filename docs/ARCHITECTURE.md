# Architecture Overview

This document provides a comprehensive overview of the Medical PDF to Anki Converter architecture, including system design, component interactions, data flow, and technology stack.

## Table of Contents

- [System Overview](#system-overview)
- [Architecture Diagram](#architecture-diagram)
- [Technology Stack](#technology-stack)
- [Directory Structure](#directory-structure)
- [Core Components](#core-components)
- [Data Flow](#data-flow)
- [Security Architecture](#security-architecture)
- [State Management](#state-management)
- [Error Handling](#error-handling)

---

## System Overview

The Medical PDF to Anki Converter is a **single-page web application** built with Streamlit that enables medical students to convert PDF textbooks into Anki flashcards using AI models. The application follows a **modular, component-based architecture** with clear separation between UI components and business logic.

### Design Principles

1. **Separation of Concerns**: UI components are isolated from business logic in the `utils/` directory
2. **State-Driven UI**: Streamlit's session state drives all UI interactions and persistence
3. **Provider Agnostic**: Abstracted LLM handlers allow switching between AI providers
4. **Security First**: All sensitive data is encrypted, and authentication is enforced server-side
5. **Fail-Safe Design**: Automatic fallback mechanisms ensure service continuity

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER BROWSER                                    │
│                         (Streamlit Frontend)                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        │ HTTPS
                                        │
┌─────────────────────────────────────────────────────────────────────────────┐
│                         STREAMLIT APPLICATION                                │
│                              (app.py)                                        │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                          COMPONENTS LAYER                              │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐  │  │
│  │  │  login   │  │generator │  │  chat    │  │cards_view│  │sidebar  │  │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └─────────┘  │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐  │  │
│  │  │   header │  │  onboard │  │   pdf_   │  │standalone│  │  card_  │  │  │
│  │  │          │  │   ing     │  │  viewer  │  │  _chat   │  │  viewer │  │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └─────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                        │                                      │
│                                        ▼                                      │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                          UTILITIES LAYER                               │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │  │
│  │  │   auth.py    │  │ llm_handler  │  │ pdf_processor│  │    rag    │  │  │
│  │  │              │  │      .py     │  │     .py      │  │    .py    │  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └───────────┘  │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │  │
│  │  │    data_     │  │    styles    │  │   common     │                 │  │
│  │  │ processing.py│  │     .py      │  │    .py       │                 │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘                 │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │                    │
                    ┌───────────────┴────────────────────┴───────────────┐
                    │                                                       │
                    ▼                                                       ▼
┌───────────────────────────────────────┐               ┌───────────────────────────────┐
│         LOCAL FILE SYSTEM              │               │      EXTERNAL APIS             │
│  ┌──────────────┐  ┌──────────────┐  │               │  ┌──────────────┐              │
│  │  users.json  │  │ vector_store │  │               │  │  Google AI   │              │
│  │              │  │     .db      │  │               │  │   (Gemini)   │              │
│  └──────────────┘  └──────────────┘  │               │  └──────────────┘              │
│  ┌──────────────┐                    │               │  ┌──────────────┐              │
│  │  history/    │                    │               │  │     Z.AI     │              │
│  │  (user data) │                    │               │  │  (GLM-4.x)   │              │
│  └──────────────┘                    │               │  └──────────────┘              │
└───────────────────────────────────────┘               │  ┌──────────────┐              │
                                                        │  │  OpenRouter  │              │
                                                        │  │ (100+ models)│              │
                                                        │  └──────────────┘              │
                                                        └───────────────────────────────┘
```

---

## Technology Stack

### Frontend Layer

| Technology | Version | Purpose |
|------------|---------|---------|
| **Streamlit** | 1.41+ | Web framework and UI rendering |
| **HTML/CSS** | Custom | Enhanced styling and themes |
| **JavaScript** | Minimal | Client-side interactivity |

### Backend Layer

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.11+ | Core application language |
| **PyMuPDF (fitz)** | Latest | PDF text extraction |
| **cryptography** | Latest | Fernet encryption for API keys |
| **bcrypt** | Latest | Password hashing |
| **pandas** | Latest | Data manipulation |
| **requests** | Latest | HTTP client for API calls |

### Data Storage

| Storage | Type | Purpose |
|---------|------|---------|
| **JSON files** | Flat file | User accounts, API keys, preferences |
| **SQLite** | Relational | Vector store for RAG |
| **Session state** | In-memory | Runtime UI state |

### Deployment

| Technology | Purpose |
|------------|---------|
| **Docker** | Containerization |
| **Docker Compose** | Multi-container orchestration |
| **Cloudflare Tunnel** | Secure remote access |

---

## Directory Structure

```
Anki-Ai/
├── app.py                      # Main Streamlit application entry point
├── requirements.txt            # Python dependencies
├── docker-compose.yml          # Docker service orchestration
├── Dockerfile                  # Container image definition
├── .env.example               # Environment variable template
│
├── components/                 # UI Components (11 modules)
│   ├── __init__.py
│   ├── generator.py           # Card generation interface (core UI)
│   ├── sidebar.py             # Settings and API key configuration
│   ├── chat.py                # PDF chat interface with RAG
│   ├── standalone_chat.py     # General AI chat (no PDF context)
│   ├── cards_view.py          # View and export generated cards
│   ├── header.py              # Navigation header component
│   ├── login.py               # Authentication forms (login/register)
│   ├── onboarding.py          # First-time API key setup
│   ├── pdf_viewer.py          # PDF preview in browser
│   ├── card_viewer.py         # Card preview before export
│   └── styles.py              # CSS and theme definitions
│
├── utils/                      # Backend Logic (7 modules)
│   ├── __init__.py
│   ├── auth.py                # Authentication, sessions, password reset
│   ├── llm_handler.py         # LLM provider abstraction and API calls
│   ├── pdf_processor.py       # PDF text extraction and chunking
│   ├── data_processing.py     # Card formatting and AnkiConnect integration
│   ├── rag.py                 # Vector store and RAG implementation
│   ├── common.py              # Shared utility functions
│   └── styles.py              # Styling utilities
│
├── data/                       # Persistent Data (created at runtime)
│   ├── users.json             # User database (encrypted)
│   ├── vector_store.db        # SQLite vector embeddings
│   └── history/               # Per-user processing history
│       └── {user_email}/      # Individual user directories
│
├── tests/                      # Test Suite
│   ├── test_auth.py           # Authentication tests
│   ├── test_pdf_processor.py  # PDF processing tests
│   └── test_rag.py            # RAG functionality tests
│
├── docs/                       # Documentation
│   ├── ARCHITECTURE.md        # This file
│   ├── COMPONENTS.md          # Component documentation
│   ├── API.md                 # API reference
│   ├── DEVELOPER.md           # Developer guide
│   ├── DEPLOYMENT.md          # Deployment guide
│   └── CONTRIBUTING.md        # Contributing guidelines
│
├── cloudflared/               # Cloudflare Tunnel Configuration
│   └── config.yml.example     # Tunnel configuration template
│
└── README.md                  # Project overview and quick start
```

---

## Core Components

### 1. Application Entry Point (`app.py`)

The main Streamlit application that orchestrates all components.

**Responsibilities:**
- Initialize Streamlit configuration (page title, icon, layout)
- Manage session state (user authentication, preferences, UI state)
- Route between different views (generator, chat, cards)
- Handle auto-login via session cookies
- Coordinate component rendering based on authentication state

**Key Functions:**
- `initialize_session_state()`: Sets up all session state variables
- `check_auto_login()`: Validates session tokens for persistent login
- `render_app()`: Main rendering loop that dispatches to appropriate views

---

### 2. Components Layer

#### `components/generator.py`
The primary UI for card generation. Handles file uploads, processing options, and initiates the card generation workflow.

**Key Features:**
- Multi-file PDF upload with drag-and-drop
- Processing mode selection (Process Files vs Fast Track)
- Card density and answer length controls
- Chapter detection and organization options

#### `components/sidebar.py`
Configuration panel for API keys, model selection, and user preferences.

**Key Features:**
- API key input for each provider
- Model selection dropdowns per provider
- Global settings (chunk size, formatting mode, etc.)
- Theme toggle (dark/light)

#### `components/chat.py` & `components/standalone_chat.py`
AI chat interfaces for PDF interaction and general Q&A.

**Key Features:**
- RAG-powered chat with PDF context
- Conversation history
- Source citation display
- Split-view mode with generator

#### `components/cards_view.py`
Displays generated cards with export options.

**Key Features:**
- Card preview with editing
- Download as TAB-separated text
- Push directly to Anki via AnkiConnect

---

### 3. Utilities Layer

#### `utils/auth.py`
Handles all authentication and authorization logic.

**Key Functions:**
- `register_user(email, password)`: Creates new user accounts
- `authenticate_user(email, password)`: Validates credentials
- `save_api_key(email, provider, key)`: Encrypts and stores API keys
- `get_api_key(email, provider)`: Retrieves and decrypts API keys
- `initiate_password_reset(email)`: Sends reset code via email
- `verify_reset_code(email, code)`: Validates reset codes
- `reset_password(email, new_password)`: Updates password with bcrypt

**Security Features:**
- Bcrypt password hashing (12 rounds)
- Rate limiting (5 attempts per 5 minutes)
- Fernet encryption for API keys
- SHA-256 hashed reset codes
- Timing-safe string comparison

#### `utils/llm_handler.py`
Abstracts LLM provider interactions and implements automatic fallback.

**Supported Providers:**
- **Google AI**: Gemini 2.5 Flash, Gemini 3.0 Flash, Gemma 3 27B
- **Z.AI**: GLM-4.7, GLM-4.5 Air
- **OpenRouter**: 100+ models including Xiaomi Mimo, DeepSeek, Qwen

**Key Classes:**
- `LLMHandler`: Main interface for making API calls
- `ModelConfig`: Configuration for each model (endpoint, headers, prompt template)

**Key Functions:**
- `generate_completion(prompt, system_prompt, provider)`: Main generation function
- `call_gemini()`: Google AI API integration
- `call_zai()`: Z.AI API integration
- `call_openrouter()`: OpenRouter API integration
- `handle_rate_limit()`: Automatic fallback to backup models

#### `utils/pdf_processor.py`
Extracts and processes text from PDF files.

**Key Functions:**
- `extract_text_from_pdf(file)`: Extracts raw text using PyMuPDF
- `detect_chapters(text)`: Identifies chapter boundaries using heuristics
- `split_text_by_chapter(text, chapters)`: Splits text into chapter chunks
- `chunk_text(text, max_size)`: Splits large texts into manageable chunks

**Features:**
- Preserves document structure (headings, paragraphs)
- Removes headers/footers
- Handles multi-column layouts

#### `utils/rag.py`
Implements Retrieval-Augmented Generation for the chat interface.

**Key Classes:**
- `VectorStore`: SQLite-backed vector storage with in-memory caching

**Key Functions:**
- `add_documents(texts, metadata)`: Embeds and stores document chunks
- `similarity_search(query, k=5)`: Retrieves most relevant chunks
- `rag_query(query, llm_handler)`: Generates responses with retrieved context

**Features:**
- Cached embeddings for performance
- Relevance scoring
- Source citation

#### `utils/data_processing.py`
Handles card formatting and Anki integration.

**Key Functions:**
- `format_card(front, back, deck, tags)`: Formats card for Anki import
- `generate_deck_name(filename, chapter)`: Creates deck hierarchy
- `push_to_anki(cards, deck_name)`: Sends cards via AnkiConnect
- `export_to_csv(cards)`: Creates TAB-separated export

---

## Data Flow

### Authentication Flow

```
┌─────────┐     ┌──────────────┐     ┌──────────┐     ┌─────────────┐
│  User   │────▶│  components/ │────▶│  utils/  │────▶│  data/users │
│ Action  │     │   login.py   │     │  auth.py │     │   .json     │
└─────────┘     └──────────────┘     └──────────┘     └─────────────┘
                     │                     │                   │
                     │            ┌────────┴────────┐         │
                     │            │                 │         │
                     ▼            ▼                 ▼         ▼
              ┌──────────┐  ┌──────────┐   ┌──────────┐  ┌────────┐
              │ Validate │  │  Bcrypt  │   │  Update  │  │ Return │
              │  Input   │  │  Hash    │   │ Session  │  │ Token  │
              └──────────┘  └──────────┘   └──────────┘  └────────┘
```

### Card Generation Flow

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Upload PDF  │────▶│  pdf_processor.py │────▶│  Extract Text    │
└──────────────┘     └──────────────────┘     └──────────────────┘
                                                        │
                     ┌──────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────────┐
│                      Processing Options                           │
│  ┌──────────────────┐          ┌──────────────────┐              │
│  │  Process Files   │          │   Fast Track     │              │
│  │  (Summarize)     │          │  (No Summary)    │              │
│  └──────────────────┘          └──────────────────┘              │
└──────────────────────────────────────────────────────────────────┘
                     │                              │
                     ▼                              ▼
┌──────────────────────┐               ┌──────────────────────────┐
│  Generate Summary    │               │   Direct to Generation   │
│  (Optional)          │               │                          │
└──────────────────────┘               └──────────────────────────┘
                     │                              │
                     └──────────────┬───────────────┘
                                    ▼
                        ┌──────────────────────┐
                        │   llm_handler.py     │
                        │  Generate Cards      │
                        └──────────────────────┘
                                    │
                                    ▼
                        ┌──────────────────────┐
                        │ data_processing.py   │
                        │  Format & Export     │
                        └──────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
            ┌───────────┐   ┌───────────┐   ┌───────────┐
            │  Download │   │ Push Anki │   │   View    │
            │    .txt   │   │Connect    │   │  Cards    │
            └───────────┘   └───────────┘   └───────────┘
```

### RAG Chat Flow

```
┌─────────────┐     ┌──────────────────┐     ┌──────────────────┐
│ User Query  │────▶│  Generate Query   │────▶│  Vector Store    │
└─────────────┘     │   Embedding       │     │  Similarity      │
                    └──────────────────┘     │  Search          │
                              │              └──────────────────┘
                              ▼                       │
                    ┌──────────────────┐             │
                    │  Retrieve Top K   │◄────────────┘
                    │  Chunks + Sources │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐     ┌──────────────────┐
                    │  Build Prompt    │────▶│  llm_handler.py  │
                    │  with Context    │     │  Generate Answer │
                    └──────────────────┘     └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Display Answer  │
                    │  + Sources       │
                    └──────────────────┘
```

---

## Security Architecture

### Password Security

| Component | Implementation |
|-----------|----------------|
| Hashing Algorithm | bcrypt (12 rounds) |
| Salt | Automatically generated per password |
| Legacy Migration | SHA-256 → bcrypt on first login |
| Requirements | 8+ chars, uppercase, lowercase, digit |

### API Key Storage

| Component | Implementation |
|-----------|----------------|
| Encryption | Fernet symmetric encryption (AES-128-CBC) |
| Key Derivation | Password-based key derivation from user email |
| Storage | Encrypted at rest in `data/users.json` |
| Transit | HTTPS only in production |

### Authentication

| Component | Implementation |
|-----------|----------------|
| Session Tokens | 32-byte hex strings |
| Token Storage | Server-side in `users.json` |
| Client Storage | Secure HTTP-only cookies |
| Expiration | 30 days of inactivity |

### Rate Limiting

| Operation | Limit | Window | Enforcement |
|-----------|-------|--------|-------------|
| Login | 5 attempts | 5 minutes | Per IP |
| Registration | 5 attempts | 5 minutes | Per IP |
| Password Reset | 5 attempts | 5 minutes | Per email |

---

## State Management

Streamlit's session state (`st.session_state`) is the single source of truth for UI state. Key state variables:

### Authentication State
```python
st.session_state.authenticated = bool()     # User logged in status
st.session_state.user = str()               # User email
st.session_state.session_token = str()      # Session token
```

### Preferences State
```python
st.session_state.provider = str()           # Selected AI provider
st.session_state.model_name = str()         # Selected model
st.session_state.theme_mode = str()         # "dark" or "light"
st.session_state.api_keys = dict()          # Cached API keys
```

### Application State
```python
st.session_state.view = str()               # Current view ("generator", "chat", "cards")
st.session_state.pdf_chunks = list()        # Processed PDF chunks
st.session_state.generated_cards = list()   # Generated flashcards
st.session_state.processing = bool()        # Processing status
```

### Chat State
```python
st.session_state.messages = list()          # Chat history
st.session_state.vector_store = VectorStore()  # RAG vector store
```

---

## Error Handling

### Exception Handling Strategy

The application uses a **layered error handling approach**:

1. **UI Layer**: User-friendly error messages with `st.error()`
2. **Utility Layer**: Exception logging and re-raising with context
3. **API Layer**: Automatic retry and fallback on rate limits

### Error Categories

| Error Type | Handling | User Feedback |
|------------|----------|---------------|
| Invalid Credentials | Increment rate limit counter | "Invalid email or password" |
| Rate Limit (429) | Switch to fallback model | "Switching to backup model..." |
| PDF Parse Error | Skip file, continue processing | "Could not process {filename}" |
| API Key Missing | Prompt for key in sidebar | "Please configure API key" |
| AnkiConnect Unavailable | Disable push option | "AnkiConnect not available" |
| Network Error | Retry with exponential backoff | "Connection error, retrying..." |

### Logging Strategy

```python
# Utility functions log errors with context
import logging
logger = logging.getLogger(__name__)

try:
    result = risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    st.error("An error occurred. Please try again.")
```

---

## Performance Considerations

### PDF Processing
- **Chunking**: Large PDFs split into 20,000 character chunks
- **Caching**: Extracted text cached in session state
- **Streaming**: Progress bars for long-running operations

### LLM Calls
- **Batching**: Multiple cards generated in single API call when possible
- **Fallback**: Automatic provider switching on rate limits
- **Timeout**: 60-second timeout per API call

### Vector Store
- **In-Memory Cache**: Embeddings cached during session
- **Lazy Loading**: Chunks embedded only when RAG is used
- **Connection Pooling**: Single SQLite connection per session

---

## Scalability Notes

### Current Limitations
- Single-server deployment (no horizontal scaling)
- In-memory session state (lost on restart)
- File-based user storage (not suitable for 10,000+ users)

### Scaling Paths
1. **Database Migration**: Replace JSON with PostgreSQL for user data
2. **Redis Cache**: Use Redis for session state persistence
3. **Load Balancer**: Add nginx for multi-instance deployment
4. **Message Queue**: Background job processing for large PDFs

---

*Last updated: 2025*
