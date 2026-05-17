# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Subkana is a Japanese sentence analysis backend API built with FastAPI. It provides two analysis modes:

- **Local analysis** (`POST /api/v1/analyze`) — Fast, no API key needed. Uses MeCab morphology + grammar rule matching + vocabulary lookup. Returns tokens with JLPT levels and matched grammar patterns. Response time: ~15ms.
- **AI analysis** (`POST /api/v1/analyze/ai`) — Deep LLM analysis for when the user wants translation, sentence breakdowns, nuanced explanations, and learning notes. Requires `LLM_API_KEY`. Response time: 1-5s.

Both endpoints share the same `AnalyzeResponse` shape: `analysis` field is `null` for local, populated for AI. `tokens` and `grammar_patterns` are always present.

## Development Commands

### Running the Server

```bash
# Install dependencies
pip install -r requirements.txt

# Development mode with auto-reload
uvicorn app.main:app --reload

# Alternative startup script
python main.py

# Custom port
uvicorn app.main:app --reload --port 8080

# Production
DEBUG=false uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### MeCab (Required for Local Analysis)

```bash
# macOS
brew install mecab mecab-ipadic

# Ubuntu/Debian
sudo apt-get install mecab libmecab-dev mecab-ipadic-utf8
```

### Running Tests

```bash
# All tests
python -m unittest tests.test_llm_service -v

# Integration test (requires running server + LLM_API_KEY)
python test_api.py
```

### Testing the API

```bash
# Local analysis (no API key needed)
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{"sentence": "行かなければなりません"}'

# AI analysis (needs LLM_API_KEY configured)
curl -X POST "http://localhost:8000/api/v1/analyze/ai" \
  -H "Content-Type: application/json" \
  -d '{"sentence": "なめてしまいました", "target_language": "zh"}'

# Health check
curl http://localhost:8000/api/v1/health
```

### Docker

```bash
docker build -t subkana .
docker run -p 8080:8080 -e LLM_API_KEY=your_key subkana
```

## Architecture

### Data Flow

```
POST /api/v1/analyze          POST /api/v1/analyze/ai
(local — fast, no key)        (AI — deep, needs key)
        ↓                              ↓
  MeCabTokenizer                 LLMAnalysisClient
        ↓                              ↓
  VocabularyLevelMapper        OpenAI-compatible API
        ↓                              ↓
  GrammarRuleEngine             LearningAnalysis
        ↓                              ↓
  AnalyzeResponse              AnalyzeResponse
  ├── analysis: null           ├── analysis: {...}
  ├── tokens: [...]            ├── tokens: [...]
  └── grammar_patterns: [...]  └── grammar_patterns: [...]
```

### Key Files

| File | Role |
|------|------|
| [app/main.py](app/main.py) | FastAPI app, CORS, middleware, lifespan init |
| [app/config.py](app/config.py) | All settings via env vars (pydantic-settings) |
| [app/dependencies.py](app/dependencies.py) | Service initialization (local components + LLM client) |
| [app/api/routes.py](app/api/routes.py) | `POST /analyze` (local), `POST /analyze/ai` (LLM), `GET /health` |
| [app/api/models.py](app/api/models.py) | `AnalyzeRequest` (sentence + target_language) |
| [app/core/models.py](app/core/models.py) | `AnalyzeResponse`, `Token`, `GrammarPattern`, `LearningAnalysis` (AI) |
| [app/core/service.py](app/core/service.py) | `AnalysisService` — `analyze_local()` and `analyze_with_ai()` |
| [app/core/tokenizer.py](app/core/tokenizer.py) | `MeCabTokenizer` — morphological analysis |
| [app/core/grammar_engine_optimized.py](app/core/grammar_engine_optimized.py) | `GrammarRuleEngine` — pattern matching with particle skipping, conjugation variants |
| [app/core/vocabulary.py](app/core/vocabulary.py) | `VocabularyLevelMapper` — JLPT level enrichment |
| [app/core/llm_client.py](app/core/llm_client.py) | `LLMAnalysisClient` — OpenAI-compatible API call with structured prompt |
| [app/middleware.py](app/middleware.py) | Request logging middleware |

### Data Files

| File | Used By | Description |
|------|---------|-------------|
| `data/grammar_rules_complete.json` | GrammarRuleEngine | 116 MeCab-compatible morphological rules (N5-N1) |
| `data/vocabulary_levels.json` | VocabularyLevelMapper | 8140 words with JLPT levels, readings, meanings |
| `data/grammar_rules.json` | _unused_ | 829 surface-only sentence templates (incompatible with engine) |

### Response Structure

```json
{
  "sentence": "...",
  "target_language": "zh",
  "analysis": null,              // null for local, populated for AI
  "tokens": [                    // always present
    {"surface": "行か", "lemma": "行く", "pos": "動詞", "conj": "未然形", "jlpt_level": "N5", ...}
  ],
  "grammar_patterns": [          // always present
    {"id": "n4_nakereba_naranai", "name": "〜なければならない", "level": "N4", "span": {...}, ...}
  ]
}
```

## Configuration

All via environment variables or `.env`. Required only for AI analysis:
- `LLM_API_KEY` — API key for LLM provider
- `LLM_BASE_URL` — default `https://api.openai.com/v1`
- `LLM_MODEL` — default `gpt-4o-mini`

Legacy settings (used by local analysis):
- `GRAMMAR_RULES_FILE` — default `data/grammar_rules_complete.json`
- `VOCABULARY_LEVELS_FILE` — default `data/vocabulary_levels.json`
- `MECAB_DICT_TYPE` — default `ipadic`
- `MECAB_RC_PATH` — default `/etc/mecabrc`

## API Endpoints

- `GET /` — Application info
- `GET /api/v1/health` — Component status (tokenizer, grammar_engine, vocabulary_mapper, llm)
- `POST /api/v1/analyze` — Local analysis (fast, no API key)
- `POST /api/v1/analyze/ai` — AI analysis (deep, needs LLM_API_KEY)
