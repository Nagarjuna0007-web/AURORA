# AURORA

A modular, locally run AI assistant. It chats through a local LLM (via [Ollama](https://ollama.com)),
answers from your own documents (RAG), searches the web with source grounding, uses small tools
(calculator, date, time), and remembers context across a session. It ships with a command-line
chat, a FastAPI backend and a browser UI.

> Status: personal project, LLM response tuning work in progress. Described from the source code; see **Known limitations**.

## Features
- **Local LLM** through Ollama (default model `llama3`, set `MODEL_NAME` in `.env`).
- **Capability routing:** a router decides whether a request needs a tool, documents or the web; an orchestrator and executor run the plan and a result synthesizer merges the output.
- **RAG:** document loader, text chunker, Ollama embeddings (Hugging Face optional), FAISS vector store, query rewriter, relevance checker, generator and an evaluator.
- **Web intelligence:** DuckDuckGo search (`ddgs`), temporal query rewriting, relevance scoring, result processing, source grounding and a release validator for answers.
- **Tools:** safe AST-based calculator (with size limits), date and time.
- **Memory and sessions:** memory extractor, summary manager, JSON session storage.
- **Interfaces:** CLI, REST API (`/health`, `/status`, `/chat`, `/chat/stream`) and a web page.

## Quick start
Prerequisites: Python 3.10+, Git, and Ollama with a chat model and an embedding model pulled:
`ollama pull llama3` and `ollama pull nomic-embed-text`.

```bash
python -m venv .venv
.venv\Scripts\activate            # macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
copy .env.example .env            # macOS/Linux: cp .env.example .env
```

Run the CLI:
```bash
python -m app.main
```
Run the API and web UI:
```bash
python -m backend.api            # open http://127.0.0.1:8000
```
Run the tests:
```bash
python -m pytest -q
```
Some tests load embedding models or call Ollama and need those installed.

## API
| Method | Path | Purpose |
|---|---|---|
| GET | `/` | web UI |
| GET | `/health` | liveness check |
| GET | `/status` | name, version, environment |
| POST | `/chat` | `{"message": "..."}` returns `{"response": "..."}` (1 to 4000 characters) |
| POST | `/chat/stream` | same input; newline-delimited JSON events |

## Project layout
```
app/        engine, agents, routing, orchestration, execution, rag, web, tools,
            memory, session, vectorstore, models, prompts, core (config, logger)
backend/    FastAPI app and static web UI
tests/      unit and integration tests
docs/       architecture notes
legacy/     an old copy of the engine kept for reference
```
See `docs/ARCHITECTURE.md`.

## Project Report
Explore the complete technical documentation of AURORA, covering its architecture, core capabilities, implementation, and development journey.
[View AURORA Project Report (PDF)](./AURORA_REPORT.pdf)

## Troubleshooting
- `model '...' not found (404)`: set `MODEL_NAME` in `.env` to a model shown by `ollama list`, or pull it.
- `Embedding model ... is not installed`: run `ollama pull nomic-embed-text`.
- `WinError 4551 ... Application Control policy has blocked ... torch`: Windows is blocking PyTorch. Use the default Ollama embeddings (no PyTorch needed); only set `EMBEDDING_PROVIDER=huggingface` if your system allows PyTorch.

## Known limitations
- A single global engine and chat history serve every API client: it is a single-user tool. There is no authentication or rate limiting, so keep it bound to `127.0.0.1`.
- Web and document content is passed to the model as context. Hidden instructions in a web page or document (indirect prompt injection) can influence answers; treat results from untrusted sources with care.
- `app/engine/aurora_engine.py` is large (about 1,300 lines) and would benefit from being split.
- Tests that need Ollama or downloaded models are not isolated from the network yet.

## License
MIT
