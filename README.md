# media-agent

An AI-powered media management agent for Plex servers, built with LangChain and Groq.

## What it does

Automatically scans a Plex media library for files missing subtitles, uses an LLM to reason about ambiguous matches, downloads subtitles from multiple sources, and logs every decision with full reasoning traces to a local SQLite database.

## Architecture

The agent uses a hybrid pipeline — deterministic logic runs first, and the LLM is only invoked when confidence is low. This keeps API costs minimal and latency fast.

- **Layer 1 — Deterministic**: Scans library, parses filenames, scores confidence
- **Layer 2 — LLM Reasoning**: Groq-powered LLaMA 3 resolves ambiguous matches and decides on actions
- **Layer 3 — Action + Logging**: Downloads subtitles, logs all decisions with reasoning to SQLite

## Tech Stack

- Python 3.12
- LangChain — agent framework and tool orchestration
- Groq (LLaMA 3.3 70B) — fast, free LLM inference
- subliminal — multi-source subtitle downloading
- TMDB API — show and movie metadata
- SQLite — local decision logging and reasoning traces
- plexapi — Plex server integration

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/qjsmith/media-agent.git
cd media-agent
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your API keys: