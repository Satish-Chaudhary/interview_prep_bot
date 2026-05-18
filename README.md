# AI Interview Preparation Bot (Advanced Hybrid Edition)

An advanced, offline-capable AI-powered mock interview coach designed to simulate real-world, high-stakes technical and HR interviews. This project was developed as an academic BCA project but functions as a production-grade application featuring a strict anti-cheat system, adaptive difficulty scaling, privacy-first voice transcription, and a modern responsive UI.

It generates role-specific questions from a Job Description, evaluates answers using the STAR method, and produces a comprehensive, downloadable PDF report. It runs fully using **Groq AI API** (default: `llama-3.1-8b-instant` for lightning-fast and free inference).
---

## ✨ Key Features & Capabilities

### 🛡️ Strict Anti-Cheat System
- **Copy-Paste Detection:** Automatically detects if a user attempts to paste content into the answer field (e.g., copying from the Assistant Coach) and instantly flags the answer, assigning a 0 score.
- **Strict Scoring Protocol:** Skipped questions or cheated answers mathematically force a 0 score into the final overall average, preventing AI score hallucination.
- **Viewport Lockdown:** Custom CSS injects a `100vh` lock on the browser, preventing page scrolling and preventing users from clicking out of context.

### 🧠 Adaptive JIT (Just-In-Time) Question Generation
- Dynamic difficulty scaling: The backend continuously analyzes rolling performance scores.
- **High Scores:** If you score perfectly, the subsequent question is automatically generated to be significantly harder and more advanced.
- **Struggles/Skips:** If you skip or struggle with a question, the engine recalibrates and offers a more fundamental, core-concept question next.

### 🎙️ Privacy-First Voice Analytics
- **Offline Speech-to-Text:** Integrated `PocketSphinx` via `SpeechRecognition` to process voice answers entirely offline, ensuring candidate privacy.
- **Audio Recording:** Includes an integrated UI audio recorder (`audio-recorder-streamlit`) directly embedded alongside the text answer box.

### ⏱️ Stress Mode
- A toggleable feature that enforces a strict 2-minute (`120s`) countdown timer per question.
- **Auto-Lockout:** When the timer expires, the UI instantly locks the text area and forces an automatic evaluation, mimicking the pressure of timed live coding or behavioral interviews.

### 🤖 Asynchronous Assistant Coach (Sidebar)
- A modern, ChatGPT-style sidebar UI anchored to the left of the screen.
- Features a fixed, non-scrolling viewport with an independent internal chat scroll.
- **Instant Response UI:** Displays your prompt immediately and shows a "Thinking..." spinner asynchronously while fetching hints, explanations, or concepts from the Groq backend without freezing the main interview interface.
- Includes a dedicated, safe `Clear Chat` confirmation modal popup.

### 📊 Comprehensive Evaluation & PDF Generation
- AI assesses answers looking explicitly for the **STAR Method** (Situation, Task, Action, Result) in behavioral questions.
- Generates a beautifully formatted, downloadable PDF Report (`ReportLab`) containing the JD analysis, every Q&A, detailed scoring (1-10), identified strengths, and a readiness verdict.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- [Groq API Key](https://console.groq.com) (Free tier is sufficient for deployment)

### 2. Setup

```bash
# Clone and enter the project
cd interview-prep-bot

# Create virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install core dependencies and advanced RAG/Agent training libraries
pip install -r requirements.txt
pip install beautifulsoup4 arxiv pymupdf wikipedia langchain
```

### 3. Environment Variables

Create and edit `.env` in the root directory:

| Variable | Required | Default | Description |
|---|---|---|---|
| `LLM_PROVIDER` | Yes | `groq` | AI provider — use `groq` for cloud inference |
| `CORE_PROVIDER` | Yes | `groq` | Core provider (takes precedence over `LLM_PROVIDER`) |
| `GROQ_API_KEY` | Yes | — | Your free Groq API key |
| `GROQ_MODEL` | No | `llama-3.1-8b-instant` | Model for JD analysis, questions, evaluation, summary |
| `CORE_TEMPERATURE` | No | `0.3` | Temperature for JSON generation tasks |
| `CORE_MAX_TOKENS` | No | `1200` | Max tokens for core tasks |

### 4. Run the Application

Launch the Streamlit frontend:
```bash
streamlit run app.py
```
Open **http://localhost:8501** in your browser.

---

## 🏗️ Project Architecture

```
interview-prep-bot/
├── app.py                     # Main Streamlit application & layout locks
├── requirements.txt           # Project dependencies
├── .env                       # Environment configuration
├── prompts/                   # System prompt templates
│   ├── jd_analyzer.txt
│   ├── question_generator.txt
│   ├── dynamic_question_generator.txt  # Adaptive JIT prompt
│   ├── evaluation.txt         # STAR method evaluation rules
│   ├── summary.txt
│   └── assistant_system.txt
├── modules/
│   ├── config.py              # Configuration & constants
│   ├── schemas.py             # JSON generation schemas
│   ├── question_generator.py  # Base & JIT Adaptive generator
│   ├── answer_evaluator.py    # Answer evaluation & Anti-Cheat triggers
│   ├── interview_session.py   # State tracking & strict math scoring
│   ├── pdf_generator.py       # Downloadable Report generator
│   ├── voice_analyzer.py      # Offline PocketSphinx transcription
│   ├── assistant_bot.py       # Async sidebar chatbot integration
│   ├── providers/             # Groq wrapper
│   └── ui/
│       └── assistant_sidebar.py # ChatGPT-style responsive sidebar
└── tests/                     # Pytest suite
```

## 📚 Future-Proofing for RAG / Agentic Workflows
The environment includes pre-installed packages (`langchain`, `beautifulsoup4`, `pymupdf`, `wikipedia`, `arxiv`) deliberately included to support future integration of Retrieval-Augmented Generation (RAG). Future updates aim to allow the bot to scrape company websites or analyze uploaded resumes to dynamically generate hyper-personalized interview flows.

---
**License:** Academic Project — BCA
