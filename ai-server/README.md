# Smart Home AI Server

FastAPI service tach rieng cho chat AI Smart Home. Service nay query DB bang tool an toan, tra ve evidence va dung Ollama neu co san.

## Run local

```bash
cd ai-server
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8100 --reload
```

## Docker stack

AI Server is hosted as a separate service on port `8100`. It uses the existing project PostgreSQL service and the existing Ollama process on the host machine.

```bash
docker compose up -d ai-server
```

Current Compose defaults:

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/smarthome
OLLAMA_URL=http://host.docker.internal:11434
```

## Environment

```env
AI_SERVER_PORT=8100
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5433/smarthome
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b
AI_SERVER_API_KEY=change_me
MEMORY_BACKEND=memory
REQUEST_TIMEOUT_SECONDS=60
MAX_TOOL_ROWS=50
```

## API

- `GET /health`
- `POST /v1/chat`
- `POST /v1/chat/reset`

When `AI_SERVER_API_KEY` is still `change_me`, API-key checks are relaxed for local development.

## Logs

AI Server logs request flow, intent, memory usage, tools, result counts, evidence count, LLM status, and fallback usage.

```bash
docker compose logs --tail=120 ai-server
```

Example log keys:

```text
chat.intent
tool.start
tool.done
chat.evidence
llm.start
llm.skip
chat.fallback
chat.done
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest -q
```
