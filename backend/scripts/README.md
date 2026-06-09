# Suggestion Pipeline Local Guide

This document explains the local flow for the habit-based suggestion feature in the backend.

## 1. What this feature does

The suggestion pipeline reads `activity_logs`, mines repeated behavior into `user_patterns`, scores whether a pattern is worth suggesting, then writes the final result to `suggestion_logs` for the mobile app and API.

Runtime flow:

```text
activity_logs
-> run_analytics.py
-> user_patterns
-> run_decision_scoring.py
-> suggestion_decision_logs
-> run_llm_formatter.py
-> suggestion_logs
-> GET /suggestions/me
```

## 2. Files in this folder

- `run_analytics.py`
  Mines `TIME_HABIT` and `ANOMALY` patterns from `activity_logs`.
- `run_decision_scoring.py`
  Scores each active pattern and decides whether it should become a suggestion.
- `run_llm_formatter.py`
  Converts approved patterns into user-facing suggestion text and stores them in `suggestion_logs`.
  If Ollama is unavailable, it falls back to a deterministic rule-based formatter.
- `seed_data.py`
  Creates demo users, devices, rooms, sensor data, and noisy `activity_logs` for local testing.

## 3. Prerequisites

- Docker Desktop running
- Project root: `D:\K2N3\PBL5\DUT.SmartHomeSystem-dev`
- Backend `.env` configured at [backend/.env](/D:/K2N3/PBL5/DUT.SmartHomeSystem-dev/backend/.env)

Current local DB URL used by backend scripts:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/smarthome
```

## 4. Start local services

From the repo root:

```powershell
docker compose up -d db backend
```

Check status:

```powershell
docker compose ps
```

Backend API should be available at:

```text
http://localhost:8000
```

## 5. Run a clean local demo

If you want a controlled dataset for suggestions, reseed the DB:

```powershell
docker compose run --rm --no-deps -v "${PWD}/backend/scripts:/app/scripts" `
  -e DATABASE_URL=postgresql://postgres:postgres@db:5432/smarthome `
  backend python scripts/seed_data.py --drop --days 60
```

Notes:

- `--drop` clears old demo data before seeding.
- This is the best path for local demo because it creates `activity_logs` that match the app's rooms and devices.

## 6. Run the suggestion pipeline

### Step 1: Analytics

```powershell
docker compose run --rm --no-deps -v "${PWD}/backend/scripts:/app/scripts" `
  -e DATABASE_URL=postgresql://postgres:postgres@db:5432/smarthome `
  backend python scripts/run_analytics.py
```

What it writes:

- `user_patterns`

Important behavior:

- The rule-based miner needs enough recent usage data.
- In practice, local demo works best with at least 7 days of activity.

### Step 2: Decision scoring

```powershell
docker compose run --rm --no-deps -v "${PWD}/backend/scripts:/app/scripts" `
  -e DATABASE_URL=postgresql://postgres:postgres@db:5432/smarthome `
  backend python scripts/run_decision_scoring.py --threshold 0.55
```

What it writes:

- `suggestion_decision_logs`

Threshold guidance:

- `0.65` is the default in code and is stricter.
- `0.55` is usually a better local-demo threshold.
- `0.50` may be needed if the current DB only has a few days of activity.

### Step 3: Suggestion formatting

```powershell
docker compose run --rm --no-deps -v "${PWD}/backend/scripts:/app/scripts" `
  -e DATABASE_URL=postgresql://postgres:postgres@db:5432/smarthome `
  backend python scripts/run_llm_formatter.py
```

What it writes:

- `suggestion_logs`

Behavior:

- If Ollama is available, the script can ask an LLM to format suggestions.
- If Ollama is unavailable or returns invalid JSON, the script falls back to built-in templates.

This means the suggestion feature can still run locally without LLM infrastructure.

## 7. Optional Ollama setup

The formatter supports Ollama through:

```env
OLLAMA_URL=http://host.docker.internal:11434
OLLAMA_MODEL=qwen2.5:3b-cpu
```

Example:

```powershell
docker compose run --rm --no-deps -v "${PWD}/backend/scripts:/app/scripts" `
  -e DATABASE_URL=postgresql://postgres:postgres@db:5432/smarthome `
  -e OLLAMA_URL=http://host.docker.internal:11434 `
  -e OLLAMA_MODEL=qwen2.5:3b-cpu `
  backend python scripts/run_llm_formatter.py
```

Recommendation:

- Use template fallback for stable demos.
- Use Ollama only if you specifically want to demo LLM phrasing.

## 8. API test

Suggestion endpoints require authentication.

Common flow:

1. Login
2. Extract `access_token`
3. Call `/suggestions/me`

Example login:

```powershell
$body = @{ email = "admin@gmail.com"; password = "123456" } | ConvertTo-Json
$token = (Invoke-RestMethod -Uri "http://localhost:8000/auth/login-json" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body).access_token
```

Get suggestions:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/suggestions/me?limit=5&include_old=true" `
  -Headers @{ Authorization = "Bearer $token" }
```

Other useful endpoints:

- `GET /suggestions/filter/by-type?action_type=SCHEDULE&limit=5`
- `GET /suggestions/{suggestion_id}`
- `POST /suggestions/{suggestion_id}/accept`
- `POST /suggestions/{suggestion_id}/feedback`

## 9. Useful DB checks

Count pipeline tables:

```powershell
docker exec dutsmarthomesystem-dev-db-1 psql -U postgres -d smarthome -c "
SELECT 'activity_logs' t, count(*) FROM activity_logs
UNION ALL SELECT 'user_patterns', count(*) FROM user_patterns
UNION ALL SELECT 'suggestion_decision_logs', count(*) FROM suggestion_decision_logs
UNION ALL SELECT 'suggestion_logs', count(*) FROM suggestion_logs;
"
```

See latest suggestions:

```powershell
docker exec dutsmarthomesystem-dev-db-1 psql -U postgres -d smarthome -c "
SELECT id, user_id, action_type, left(suggestion_text, 160), created_at
FROM suggestion_logs
ORDER BY created_at DESC, id DESC
LIMIT 10;
"
```

## 10. Known local caveats

- If the DB has too little recent activity, analytics may still create patterns but decision scoring may produce zero suggestions.
- If `max(decision_score)` is below the current threshold, `run_llm_formatter.py` will skip all homes because there are no approved candidates.
- Some older local users may use `.local` emails. The `/auth/login-json` request body is validated as an email address, so those accounts may not be usable through normal login until their email is updated.
- `seed_data.py` is best for demoing suggestion behavior that matches the current app's devices.
- Large external datasets such as CASAS are better treated as optional ETL input, not the main local demo path.

## 11. Recommended local demo recipe

Use this sequence for the most reliable local demo:

```powershell
docker compose up -d db backend

docker compose run --rm --no-deps -v "${PWD}/backend/scripts:/app/scripts" `
  -e DATABASE_URL=postgresql://postgres:postgres@db:5432/smarthome `
  backend python scripts/seed_data.py --drop --days 60

docker compose run --rm --no-deps -v "${PWD}/backend/scripts:/app/scripts" `
  -e DATABASE_URL=postgresql://postgres:postgres@db:5432/smarthome `
  backend python scripts/run_analytics.py

docker compose run --rm --no-deps -v "${PWD}/backend/scripts:/app/scripts" `
  -e DATABASE_URL=postgresql://postgres:postgres@db:5432/smarthome `
  backend python scripts/run_decision_scoring.py --threshold 0.55

docker compose run --rm --no-deps -v "${PWD}/backend/scripts:/app/scripts" `
  -e DATABASE_URL=postgresql://postgres:postgres@db:5432/smarthome `
  backend python scripts/run_llm_formatter.py
```

Expected result:

- `user_patterns` is populated
- `suggestion_decision_logs` is populated
- `suggestion_logs` contains `SCHEDULE`, `ALERT`, or `AUTOMATION` suggestions
- `GET /suggestions/me` returns suggestions for the authenticated user
