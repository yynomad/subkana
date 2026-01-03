# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Subkana is a Japanese sentence analysis backend API built with FastAPI. It analyzes Japanese sentences by:
- Performing morphological analysis using MeCab
- Identifying grammar patterns based on JLPT levels (N5, N4, N3)
- Mapping vocabulary to JLPT levels
- Returning structured analysis results via a single REST endpoint

The application is designed as a backend service for browser extensions and other clients that need Japanese language analysis.

## Development Commands

### Running the Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload

# Alternative startup script (includes MeCab compatibility setup)
python main.py

# Custom port
uvicorn app.main:app --reload --port 8080

# Production mode (no API docs)
DEBUG=false uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Environment Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Verify MeCab installation
mecab --version
echo "テスト" | mecab
```

### MeCab Installation (Required System Dependency)

**macOS:**
```bash
brew install mecab mecab-ipadic
```

**Ubuntu/Debian:**
```bash
sudo apt-get install mecab libmecab-dev mecab-ipadic-utf8
```

**Docker:** Automatically installed via Dockerfile

### Testing the API

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Analyze a sentence
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{"sentence": "行かなければなりません"}'

# Access API docs (only in DEBUG mode)
open http://localhost:8000/docs
```

### Docker Deployment

```bash
# Build
docker build -t subkana .

# Run
docker run -p 8000:8000 subkana
```

## Architecture

### Core Design Principle

The application is built around a **single unified analysis endpoint** (`/analyze`) rather than separate endpoints for tokenization, grammar matching, and vocabulary lookup. This design ensures:
- All analysis is based on the same morphological analysis result
- Reduced network round-trips for clients
- Simplified frontend integration
- Easier caching and optimization

### Data Flow

```
Client Request → FastAPI Route → AnalysisService
                                    ↓
                            ┌───────────────┐
                            │ MeCabTokenizer│ → Morphological analysis
                            └───────────────┘
                                    ↓
                    ┌───────────────────────────────┐
                    │  GrammarRuleEngine +          │
                    │  VocabularyLevelMapper        │
                    └───────────────────────────────┘
                                    ↓
                            AnalyzeResponse
                                    ↓
                            JSON Response
```

### Key Components

**app/main.py** - FastAPI application entry point
- Configures CORS (important for browser extension compatibility)
- Sets up middleware and logging
- Auto-detects MeCab paths for macOS Homebrew

**app/core/service.py** - AnalysisService
- Orchestrates the three-step analysis pipeline:
  1. Tokenization via MeCabTokenizer
  2. Grammar pattern matching via GrammarRuleEngine
  3. Vocabulary level mapping via VocabularyLevelMapper
- Calculates character positions (spans) for frontend highlighting

**app/core/tokenizer.py** - MeCabTokenizer
- Wrapper around MeCab morphological analyzer
- Returns Token objects with: surface, lemma (dictionary form), conj (conjugation form), pos (part of speech)

**app/core/grammar_engine.py** - GrammarRuleEngine
- Uses sliding window algorithm to match grammar patterns
- Patterns are defined in JSON files (not code)
- Supports multiple pattern matches in a single sentence
- Each rule specifies: id, name, level, meaning, pattern

**app/core/vocabulary.py** - VocabularyLevelMapper
- Maps token lemmas to JLPT levels (N5, N4, N3)
- Data loaded from JSON file

### Configuration

All configuration is managed through environment variables using pydantic-settings:
- `PORT` - Server port (default: 8000)
- `DEBUG` - Enable API docs and detailed logging (default: false)
- `CORS_ORIGINS` - Allowed origins for CORS (default: ["*"])
- `GRAMMAR_RULES_FILE` - Path to grammar rules JSON (default: data/grammar_rules.json)
- `VOCABULARY_LEVELS_FILE` - Path to vocabulary levels JSON (default: data/vocabulary_levels.json)

See [app/config.py](app/config.py) for complete settings.

### Data Files

**data/grammar_rules.json** - Grammar pattern definitions
- Currently contains 24 patterns (N5: 5, N4: 10, N3: 9)
- Each pattern has a `pattern` array with matching conditions
- Pattern matching conditions can use: `pos` (part of speech), `lemma` (dictionary form), `surface` (actual form), `conj` (conjugation form)

**data/vocabulary_levels.json** - Vocabulary to JLPT level mapping
- Currently contains 247 words (N5: 133, N4: 84, N3: 30)
- Simple key-value format: {"word": "N5"}

See [data/README.md](data/README.md) for detailed documentation on extending data.

## Extending the System

### Adding New Grammar Patterns

1. Edit [data/grammar_rules.json](data/grammar_rules.json)
2. Add a new rule with pattern matching conditions:
   ```json
   {
     "id": "n3_new_pattern",
     "name": "〜新句型",
     "level": "N3",
     "meaning": "句型含义",
     "pattern": [
       {"pos": "動詞"},
       {"lemma": "特定詞", "conj": "連用形"}
     ]
   }
   ```
3. Pattern matching is based on MeCab output - test tokenization first

### Adding Vocabulary

1. Edit [data/vocabulary_levels.json](data/vocabulary_levels.json)
2. Add entries in format: `{"word_form": "N5"}`
3. Use the lemma (dictionary form) for accurate matching

### MeCab Integration Notes

- The app auto-detects MeCab paths for macOS Homebrew installations
- Pattern matching relies on MeCab's part-of-speech and conjugation analysis
- Always test patterns against actual MeCab output - the tokenizer returns all morphological features
- Token.lemma is the dictionary form (used for vocabulary lookup)
- Token.conj is the conjugation form (used for grammar pattern matching)
- Token.pos is the part of speech (used for both)

### Common Pitfalls

1. **Pattern Matching**: Grammar patterns must match MeCab's output exactly. Use `echo "sentence" | mecab` to see the actual tokenization and features before writing patterns.

2. **Character Positions**: The span calculation in AnalysisService assumes tokens appear in order. Complex sentence structures may require more sophisticated span calculation.

3. **CORS**: Browser extensions need proper CORS configuration. In production, set `CORS_ORIGINS` to specific extension URLs rather than wildcard.

4. **MeCab Dictionary**: The app uses IPADIC dictionary. Different dictionaries (UniDic, etc.) produce different tokenization and will break pattern matching.

## API Endpoints

- `GET /` - Application info
- `GET /api/v1/health` - Service health check
- `POST /api/v1/analyze` - Main analysis endpoint (see [app/api/routes.py](app/api/routes.py))

## Testing Strategy

Currently no automated tests are implemented. Manual testing via curl or the Swagger UI (`/docs`) is the primary testing method.

When adding tests, focus on:
1. Tokenization accuracy for various sentence structures
2. Grammar pattern matching edge cases (overlapping patterns, partial matches)
3. Vocabulary lookup for different word forms (dictionary form vs conjugated)
