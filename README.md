# Packaged Food Rating Agent

## Mission

Prototype a product-health lookup system that transforms barcodes and labels into a transparent, comparable health signal—grounded in authoritative, medically reliable sources—with clear explanations ordinary users can understand.

## Objective

Create an application that:

* Accepts a product (via barcode, ingredients text, or image)
* Produces a health score (0–100) with a band (A–E)
* Provides plain-language explanations (drivers)
* Displays evidence (rules and references used)
* Handles messy/incomplete data gracefully

## Features

* **LangGraph Orchestration** for intelligent routing
* **Tools Integrated**:

  * OpenFoodFacts API (domain-specific)
  * OCR via Tesseract (ingredients images)
  * Optional barcode decode (pyzbar)
* **Vector Memory (Chroma)** for RAG capabilities
* **Local Ollama LLM** for natural-language summary and embeddings
* **Human-in-the-Loop (HITL)** safety checkpoint system
* **OpenTelemetry Observability** for tracing/logging
* **Streamlit UI** for user interaction

## Architecture

```
[Streamlit UI] → [FastAPI Backend] → [LangGraph Pipeline]
   route → ingest (barcode, OCR, RAG) → normalize → HITL safety → score → evidence → summary (LLM)
```

### Modules

* `src/app/tools/`: OpenFoodFacts, OCR, barcode, web search
* `src/app/parsers/`: Ingredients/nutrition normalization
* `src/app/agent/`: LangGraph workflow nodes
* `src/app/memory/`: Chroma vector DB
* `src/app/llm/`: Ollama/OpenAI wrappers
* `src/app/hitl/`: HITL approval system
* `src/app/observability/`: OpenTelemetry instrumentation
* `src/server/main.py`: FastAPI entrypoint
* `src/ui/streamlit_app.py`: Streamlit UI

## Data Contracts

### Request: `POST /rate`

```json
{
  "query": "optional string",
  "barcode": "optional string",
  "ingredients_text": "optional string",
  "nutrition_raw": {"sugars": 23, "salt": 1.6, "saturated fat": 6, "protein": 9, "fiber": 2},
  "image_b64": "optional base64 image"
}
```

### Response (success)

```json
{
  "query": "...",
  "normalized": {...},
  "scoring": {"score": 47, "band": "C", "drivers": [...], "evidence": [...]},
  "summary": "Concise text",
  "action": "PROCEED",
  "logs": [...]
}
```

### Response (HITL pause)

```json
{
  "action": "PAUSE_HITL",
  "hitl_id": "uuid"
}
```

## Scoring

* Deterministic 0–100 scale (bands A–E)
* Rulebook in `data/kb/scoring_rules.yaml`
* Evidence references in `data/kb/references.yaml`

## Observability

* OpenTelemetry spans for key pipeline steps
* Exporter configurable via `.env`

## Installation & Running

### Prerequisites

* Python 3.10+
* Ollama installed with models:

  ```bash
  ollama pull llama3.1:8b
  ollama pull nomic-embed-text:latest
  ```
* Tesseract OCR installed (for image ingredients)

### Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit environment variables if needed
```

### Backend

```bash
uvicorn src.server.main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
API_BASE=http://127.0.0.1:8000 streamlit run src/ui/streamlit_app.py
```

### Health Check

```bash
curl http://127.0.0.1:8000/health
```

## Usage

* Enter a **barcode**, paste **ingredients/nutrition JSON**, or upload an **image**
* Hit **Run**
* View logs, normalized data, health score, evidence, and summary
* If HITL triggered, approve/reject in UI

## Configuration (.env)

* `USE_OLLAMA=true`
* `OLLAMA_HOST=http://localhost:11434`
* `OLLAMA_CHAT_MODEL=llama3.1:8b`
* `OLLAMA_EMBED_MODEL=nomic-embed-text:latest`
* `SERVER_HOST=0.0.0.0`
* `SERVER_PORT=8000`
* `API_BASE=http://127.0.0.1:8000`
* `HITL_SECRET=change-me`

## References

* OpenFoodFacts API
* WHO, FSSAI, EFSA guidelines
* Peer-reviewed nutrition references (examples in `references.yaml`)

## Testing

* Smoke test: `pytest tests/`
* Covers ingest, normalization, scoring, HITL, and LLM fallback

## Roadmap

* Category-specific rulebooks
* Product comparison view
* Richer UI (history, export)
* Extended internationalization

## License & Attribution

* Uses OpenFoodFacts public data
* OCR via Tesseract
* Embeddings/summaries via Ollama
