# Medical PDF to Anki Converter (AI-Powered)

A comprehensive tool to convert medical PDFs into high-yield Anki cards using state-of-the-art AI models (Google Gemini & OpenRouter).

## 🚀 Key Features

*   **Dual AI Providers**: Support for **Google Gemini** (1.5, 2.0, 3.0) and **OpenRouter** (Xiaomi Mimo, DeepSeek, Qwen).
*   **Split-View Interface**: Generate Anki cards on the left while chatting with your PDF context on the right.
*   **AI Summaries**: Automatically generates high-yield summaries for every uploaded PDF file/chapter.
*   **Infinite Throughput**: Built-in rate limiting and key rotation (for Gemini) to handle massive textbooks.
*   **High Density**: Optimized prompts for "Extreme Density" card generation (30-50+ cards per chunk).
*   **Anki Ready**: Outputs Pipe-separated (`|`) CSV files with HTML/Markdown support, ready for immediate Anki import.

## 🛠 Getting Started

### Option 1: Using Docker
1.  Make sure you have **Docker Desktop** installed.
2.  Run: `docker-compose up --build`
3.  Access: http://localhost:8501

### Option 2: Manual Setup
1.  **Clone & Enter**: `git clone <repo> && cd <repo>`
2.  **Environment**: Create a venv and activate it.
3.  **Install**: `pip install -r requirements.txt`
4.  **Launch**: `streamlit run app.py`

## 🧪 Model Recommendations

*   **Anki Generation**: `xiaomi/mimo-v2-flash` (OpenRouter) or `gemini-3-flash` (Google).
*   **Summaries & Chat**: `google/gemini-2.0-flash-exp:free` or `gemma-3-27b-it`.

---
*Developed for USMLE and Medical Students focus.*
