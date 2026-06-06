# AI Server V1

FastAPI service tách riêng cho hai năng lực AI:

- `NLP assistant`: hiểu lệnh tiếng Việt, trích entity, phát hiện thiếu thông tin hoặc ngoài phạm vi, rồi trả `action_draft`.
- `Environment prediction`: dự báo nhiệt độ và độ ẩm 30 phút tới cho một ambient zone, kèm khoảng tin cậy, comfort proxy, và action hint.

## Data Strategy

V1 này đã được nâng lên theo hướng dữ liệu rõ ràng hơn:

- `NLP` dùng custom smart-home corpus tiếng Việt làm nguồn chính.
- `Production NLU` dùng kiến trúc hybrid:
  - baseline `TF-IDF + Logistic Regression` cho intent routing
  - `diacritic restoration` cho câu không dấu
  - `PhoBERT slot model` cho entity extraction sâu khi artifact đã được train
- `PhoATIS`, `MASSIVE`, hoặc các nguồn public tương tự chỉ nên dùng để tham khảo ontology, negative/OOS, và benchmark phụ.
- `Environment prediction` chỉ claim cho `1 ambient zone` vì phần cứng hiện tại giả định `1 DHT11`.
- `PhoBERT` được chuẩn bị qua notebook benchmark riêng mà không đổi API contract.

## Project Layout

```text
ai-server/
|-- app/
|-- artifacts/
|-- data/
|   |-- environment/
|   `-- nlp/
|-- notebooks/
|-- scripts/
`-- tests/
```

## Setup

```bash
cd ai-server
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Optional deps for PhoBERT experiments:

```bash
pip install -r requirements-phobert.txt
```

## Run

```bash
uvicorn app.main:app --reload --port 8010
```

Swagger:

- `http://localhost:8010/docs`

## Main Endpoints

- `GET /health`
- `GET /api/v1/meta/capabilities`
- `POST /api/v1/nlp/parse`
- `POST /api/v1/assistant/chat`
- `POST /api/v1/predict/environment`
- `POST /api/v1/predict/environment/batch`

## NLP Dataset Workflow

Build the bootstrap corpus and split files:

```bash
python scripts/build_nlp_dataset.py
```

This writes:

- `data/nlp/master.jsonl`
- `data/nlp/train.jsonl`
- `data/nlp/val.jsonl`
- `data/nlp/test.jsonl`
- `data/nlp/bio/*.jsonl`
- `data/nlp/summary.json`

Then retrain the baseline classifier:

```bash
python scripts/train_nlp.py
```

Train the PhoBERT slot artifact used by the hybrid runtime:

```bash
python scripts/train_phobert_slot.py --epochs 2 --batch-size 8
```

## Environment Data Workflow

Put real house logs at:

- `data/environment/house_ambient_log.csv`

Template:

- `data/environment/house_ambient_log.csv.example`

Train from a specific CSV:

```bash
python scripts/train_environment.py --csv data/environment/house_ambient_log.csv
```

Without `--csv`, the trainer uses:

1. `house_ambient_log.csv`
2. `reference_environment_log.csv`
3. synthetic bootstrap fallback

## PhoBERT Benchmark

Notebook scaffold:

- `notebooks/baseline_vs_phobert.ipynb`

Use it to compare:

- intent accuracy
- macro-F1
- slot F1 from BIO exports
- exact match
- confusion cases
- latency and model size
- clean vs no-diacritic vs restored Vietnamese inputs

The notebook now runs an end-to-end robustness experiment:

- baseline hybrid trained once on the clean split
- PhoBERT trained once on the clean split
- both evaluated on `clean`, `no_diacritic`, and `restored`
- restoration quality and tokenizer fragmentation are surfaced as explicit analysis tables

## Integration Notes

- AI server does not publish MQTT.
- AI server does not replace backend auth or device ownership checks.
- `action_draft` remains backend-friendly and side-effect free.
- `comfort_proxy` is not exact PMV because V1 does not model air speed, clothing, or metabolic rate.
