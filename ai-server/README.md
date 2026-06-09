# Smart Home AI Server

AI Server la service FastAPI tach rieng cho tinh nang chat Smart Home.
Backend goi AI Server qua `POST /v1/chat`; AI Server doc database, lap ke hoach tool, roi goi Ollama neu can sinh cau tra loi tu nhien.

## Yeu cau

- Python virtual environment cua project: `..\.venv`
- PostgreSQL dang chay va co database `smarthome`
- Ollama dang chay o `http://localhost:11434`
- Model Ollama da duoc pull, mac dinh la `qwen2.5:3b`

Kiem tra Ollama:

```powershell
ollama list
Invoke-RestMethod http://localhost:11434/api/tags
```

Neu chua co model:

```powershell
ollama pull qwen2.5:3b
```

## Cai dependencies

Chay tu thu muc goc repo:

```powershell
.\.venv\Scripts\python.exe -m pip install -r ai-server\requirements.txt
```

## Chay local

Chay tu thu muc goc repo:

```powershell
$env:DATABASE_URL='postgresql+psycopg2://postgres:123456@localhost:5432/smarthome'
$env:OLLAMA_URL='http://localhost:11434'
$env:OLLAMA_MODEL='qwen2.5:3b'
cd ai-server
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8100 --reload
```

Neu database local cua ban dung port/user/password khac, sua lai `DATABASE_URL`.
Vi du khi dung PostgreSQL trong `docker-compose.yml` cua repo:

```powershell
$env:DATABASE_URL='postgresql+psycopg2://postgres:postgres@localhost:5433/smarthome'
```

## Kiem tra server

```powershell
Invoke-RestMethod http://localhost:8100/health
```

Ket qua tot:

```text
status ollama db
------ ------ --
ok     ok     ok
```

Neu `ollama` la `unavailable`, kiem tra lai `ollama serve`, port `11434`, va model.
Neu `db` la `error`, kiem tra lai `DATABASE_URL` va PostgreSQL.

## Cau hinh backend

Backend phai tro toi AI Server bang bien `AI_SERVER_URL`.
Trong `backend/.env` nen co:

```env
AI_SERVER_URL=http://localhost:8100
AI_SERVER_API_KEY=change_me
```

Sau khi sua `.env`, restart backend de no doc lai bien moi.

## Chay bang Docker

Tu thu muc goc repo:

```powershell
docker compose up -d ai-server
```

Mac dinh trong `docker-compose.yml`:

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/smarthome
OLLAMA_URL=http://host.docker.internal:11434
OLLAMA_MODEL=qwen2.5:3b
```

Dung `host.docker.internal` vi AI Server chay trong container, con Ollama chay tren may host.

Xem log:

```powershell
docker compose logs --tail=120 ai-server
```

## API

- `GET /health`
- `POST /v1/chat`
- `POST /v1/chat/reset`

Khi `AI_SERVER_API_KEY=change_me`, check API key duoc noi long cho local development.

## Tat server local

Neu dang chay foreground, bam `Ctrl+C`.

Neu can tim process dang giu port `8100` tren Windows:

```powershell
Get-NetTCPConnection -LocalPort 8100 -State Listen | Select-Object -ExpandProperty OwningProcess
Stop-Process -Id <PID> -Force
```

## Chay tests

```powershell
cd ai-server
..\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
..\.venv\Scripts\python.exe -m pytest -q
```
