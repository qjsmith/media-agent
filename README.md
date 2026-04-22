# media-agent

An AI-powered media file renaming agent for Plex servers. Scans a media library for badly named files, identifies them using TMDB, and renames them to [TRaSH-standard](https://trash-guides.info/) naming conventions so that Sonarr, Radarr, and Bazarr work correctly.

## The Problem

Sonarr, Radarr, and Bazarr depend on consistent file naming to manage metadata, subtitles, and upgrades. Poorly named files break this chain. This agent fixes the root cause — the filename — so all existing tools start working again automatically.

## Pipeline

```
Scan media library for badly named files
              ↓
     Parse filename + folder context
              ↓
       Detect media type (tv / movie)
              ↓
      Search TMDB + score confidence
              ↓
     Score ≥ 90% and unambiguous?
          ↙           ↘
        YES             NO
          ↓               ↓
    Auto rename     Send to LLM with filename,
     + log it       folder context, candidates
                          ↓
                  LLM picks best match → Rename + log reasoning
                  LLM says UNKNOWN    → Flag for human review
```

The LLM is only invoked when deterministic confidence scoring fails — keeping API usage minimal and latency fast.

## Naming Convention (TRaSH Standard)

**TV Shows**
```
/mnt/media/TV Shows/
└── Show Name (Year)/
    └── Season 01/
        └── Show Name (Year) - S01E01 - Episode Title.mkv
```

**Movies**
```
/mnt/media/Movies/
└── Movie Title (Year)/
    └── Movie Title (Year).mkv
```

## Tech Stack

| Component | Tool |
|---|---|
| Language | Python 3.12 |
| Agent framework | LangChain 0.3.0 |
| LLM inference | Groq (LLaMA 3.3 70B) |
| Media metadata | TMDB API |
| Fuzzy matching | thefuzz + python-Levenshtein |
| Decision logging | SQLite |
| Plex integration | plexapi |

## Project Structure

```
media-agent/
├── agent/
│   ├── core.py              ← main agent pipeline
│   ├── prompts.py           ← LLM system prompt
│   └── tools/
│       ├── scanner.py       ← finds badly named files
│       ├── parser.py        ← extracts title/season/episode/year from filename
│       ├── confidence.py    ← fuzzy matches parsed info against TMDB results
│       ├── metadata.py      ← TMDB API calls
│       ├── renamer.py       ← builds TRaSH-standard paths and renames files
│       └── logger.py        ← logs all decisions to SQLite
├── db/                      ← SQLite database (gitignored)
├── config.py                ← loads .env variables
├── requirements.txt
└── .env.example
```

## Confidence Scoring

Each TMDB candidate is scored using a weighted combination of:

- **Title fuzzy match** (60%) — uses the best of `token_sort_ratio` and `ratio` from `thefuzz`
- **Year match** (30%) — exact match only
- **Popularity boost** (10–30%) — weighted higher when no year is available, helps disambiguate common titles like *The Office*

A score ≥ 90 triggers an automatic rename. Below 90, or when the top two candidates are within 25 points of each other, the file is escalated to the LLM.

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

Edit `.env`:

```
GROQ_API_KEY=...
TMDB_API_KEY=...
PLEX_URL=http://your-plex-ip:32400
PLEX_TOKEN=...
MEDIA_PATH=/mnt/media
```

### 4. Run in dry run mode first

In `agent/core.py`, `DRY_RUN` is set to `True` by default. This logs what the agent *would* do without moving any files. Review the output and SQLite log before setting it to `False`.

```bash
PYTHONPATH=. python agent/core.py
```

### 5. Review decisions

```bash
PYTHONPATH=. python agent/tools/logger.py
```

## Configuration

| Flag | Location | Default | Description |
|---|---|---|---|
| `DRY_RUN` | `agent/core.py` | `True` | Log actions without renaming files |
| `CONFIDENCE_THRESHOLD` | `agent/core.py` | `90.0` | Minimum score for auto rename |