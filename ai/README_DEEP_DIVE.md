# 🤖 Vietnamese NLP Intent Classification Server — Deep Dive

> Server phân loại ý định (intent) người dùng bằng tiếng Việt cho hệ thống Smart Home.  
> Được xây dựng trên **FastAPI + PhoBERT** với kiến trúc Hybrid Classifier.

---

## 📁 Cấu trúc thư mục

```
ai/
├── src/
│   ├── main.py                  # Entry point — khởi tạo FastAPI app
│   ├── bootstrap.py             # Khởi tạo tất cả shared resources
│   ├── config/
│   │   └── settings.py          # Cấu hình từ .env (host, port, JWT, Redis, model...)
│   ├── api/
│   │   ├── auth.py              # JWT authentication (Bearer token)
│   │   ├── rate_limiter.py      # Token bucket rate limiter
│   │   ├── response_builder.py  # Xây dựng và validate response
│   │   ├── error_handler.py     # Xử lý các loại lỗi
│   │   ├── timeout_handler.py   # Timeout middleware
│   │   └── v1/
│   │       ├── router.py        # Ghép tất cả sub-routers lại
│   │       └── endpoints/
│   │           ├── classify.py  # ← ENDPOINT CHÍNH: POST /intent/classify
│   │           ├── intents.py   # GET /intents (liệt kê intents)
│   │           ├── metrics.py   # GET /metrics (Prometheus)
│   │           └── model.py     # POST /model/reload (admin only)
│   ├── preprocessing/
│   │   └── pipeline.py          # Tiền xử lý văn bản tiếng Việt
│   ├── classifiers/
│   │   ├── rule_based.py        # Classifier dùng pattern matching
│   │   ├── ml_based.py          # Classifier dùng PhoBERT
│   │   ├── hybrid.py            # Kết hợp rule + ML (LUỒNG CHÍNH)
│   │   └── onnx_engine.py       # ONNX inference engine (tùy chọn)
│   ├── entities/
│   │   └── entity_extractor.py  # Trích xuất entities từ văn bản
│   ├── models/
│   │   └── schemas.py           # Pydantic models (request/response)
│   ├── cache/
│   │   └── response_cache.py    # Redis cache cho responses
│   ├── training/
│   │   └── phobert_classifier.py # Kiến trúc model PhoBERT (nn.Module)
│   └── monitoring/
│       ├── logger.py            # Structured JSON logger
│       └── metrics.py           # Prometheus metrics counters
├── scripts/                     # Scripts train/export/validate model
├── tests/                       # Unit, integration, performance tests
├── models/                      # Thư mục chứa model đã train
└── .env.example                 # Template biến môi trường
```

---

## 🚀 Khởi động server

```
uvicorn src.main:app --host 0.0.0.0 --port 8001
```

Hoặc chạy trực tiếp:
```
python -m src.main
```

---

## ⚙️ Phase 1 — Startup (Bootstrap)

Khi server khởi động, `startup_event()` trong `main.py` gọi `init_app_state(app)` từ `bootstrap.py`.  
Tất cả shared resources được khởi tạo **một lần duy nhất** và gắn vào `app.state`:

```
startup_event()
    └── init_app_state(app)
            ├── settings          ← cấu hình từ .env
            ├── ResponseBuilder   ← validate + build responses
            ├── PreprocessingPipeline  ← tiền xử lý văn bản
            ├── EntityExtractor   ← trích xuất entities
            ├── StructuredLogger  ← JSON logger
            ├── RateLimiter       ← token bucket (60 req/phút mỗi user)
            ├── ResponseCache     ← Redis cache (TTL 5 phút)
            └── load_models(app)
                    ├── RuleBasedClassifier   ← luôn khởi tạo
                    ├── MLBasedClassifier     ← thử ONNX trước, fallback PyTorch
                    └── HybridClassifier      ← kết hợp cả hai
```

**Fallback khi load model thất bại:**
- Nếu ONNX load lỗi → thử lại với PyTorch
- Nếu PyTorch cũng lỗi → chỉ dùng Rule-Based classifier
- Nếu không có Redis → cache bị tắt, server vẫn chạy bình thường

---

## 🔐 Phase 2 — Authentication

Mọi endpoint đều yêu cầu **JWT Bearer Token** (trừ `/` và `/health`).

```
Request Header: Authorization: Bearer <JWT_TOKEN>
         ↓
get_current_user() dependency
         ↓
JWTAuth.verify_jwt_token(token)
         ↓
    Hợp lệ?  →  Trả về payload (user_id, role...)
    Hết hạn? →  AuthenticationError 401
    Sai?     →  AuthenticationError 401
```

Endpoint `POST /model/reload` yêu cầu thêm `role: "admin"` trong JWT payload.

---

## 🔄 Luồng xử lý chính — POST `/api/v1/intent/classify`

Đây là endpoint quan trọng nhất. Luồng đầy đủ:

```
Client gửi POST /api/v1/intent/classify
{
    "text": "Bật đèn phòng khách và tắt quạt phòng ngủ",
    "user_id": "user_123",
    "device_context": {
        "current_room": "living_room",
        "devices": [...],
        "time_of_day": "evening"
    }
}
```

### Bước 1 — Rate Limit Check
```
rate_limiter.is_allowed(user_id)
    Token bucket: 60 token/phút, burst=60
    Hết token? → RateLimitError 429
```

### Bước 2 — Validate Input
```
response_builder.validate_and_build(text)
    - text không được None/rỗng/chỉ whitespace
    - độ dài <= 500 ký tự
    - phải chứa ít nhất 1 ký tự chữ cái (kể cả tiếng Việt)
    Lỗi? → trả về 400 ngay
```

### Bước 3 — Preprocessing Pipeline
```
preprocessing.preprocess(text)
    1. Lowercase: "BẬT ĐÈN" → "bật đèn"
    2. Remove punctuation: "bật đèn!" → "bật đèn"
    3. Remove emoji: "bật đèn 💡" → "bật đèn"
    4. Normalize slang: "k bật đèn" → "không bật đèn"
       (k/ko/hok→không, đc→được, vs→với, j→gì, tks→cảm ơn, ok/oke→được)
    5. Correct spelling: "khong bật den" → "không bật đèn"
       (khong→không, duoc→được, nha→nhà, toi→tôi...)
    6. Split sentences (multi-intent):
       "bật đèn và tắt quạt" → ["bật đèn", "tắt quạt"]
       (từ nối: và, rồi, sau đó, xong, tiếp theo, kế tiếp)
    
    Trả về: PreprocessedText(normalized_text, original_text, sentences=[...])
```

### Bước 4 — Cache Lookup
```
cache.get(normalized_text, context)
    - Key = SHA256(json({text, context}))
    - Cache hit? → trả về response ngay (bỏ qua toàn bộ inference)
    - Cache miss? → tiếp tục xử lý
```

### Bước 5 — Classification (Hybrid)
Mỗi sentence trong danh sách được phân loại độc lập:

```
_classify_with_timeout(request, sentence, context)
    └── hybrid_classifier.classify(sentence, context)
            │
            ├─ [Step A] should_use_rule_based(text)?
            │       Có action words (bật/tắt/mở/đóng)
            │       hoặc scene keywords (đi ngủ/về nhà...)
            │       VÀ độ dài <= 10 từ
            │       → True = thử rule-based trước
            │
            ├─ [Step B] rule_classifier.classify(text)
            │       Pattern matching theo thứ tự ưu tiên:
            │       1. Scene patterns: "đi ngủ" → activate_scene{sleep}
            │       2. Comfort patterns: "nóng quá" → environmental_comfort{cooling}
            │       3. Sensor query: "nhiệt độ bao nhiêu" → query_sensor{temperature}
            │       4. Device status: "đèn có bật không" → query_device_status{light}
            │       5. Control device: "bật đèn" → control_device{turn_on, light}
            │
            │       confidence=1.0 nếu match? → FAST PATH, trả về ngay (<10ms)
            │
            └─ [Step C] ml_classifier.classify(text, context)
                    1. Tokenize: PhoBERT tokenizer → input_ids, attention_mask
                    2. Encode context (nếu có):
                           current_room → one-hot vector (6 rooms)
                           devices      → binary vector (8 device types)
                           time_of_day  → sin/cos encoding
                           → context_embedding (1, 32)
                    3. Inference:
                           ONNX Runtime (nhanh hơn ~2-3x)
                           hoặc PyTorch (fallback)
                    4. Softmax → confidence scores
                    5. Top-3 intents với scores
                    
                    Trả về: {intent, confidence, top_k_intents, classifier_type="ml"}
            
            So sánh confidence:
            - rule >= ml? → dùng rule result
            - ml > rule?  → dùng ml result
            - ML lỗi?     → fallback về rule result
            - Cả hai lỗi? → {intent: "unknown", confidence: 0.0}
```

**Timeout handling:** Nếu hybrid classifier timeout (mặc định 5s):
```
asyncio.wait_for(hybrid.classify(...), timeout=5s)
    Timeout? → fallback về rule_classifier.classify(text)
    Rule cũng không có? → {intent: "unknown", fallback_reason: "timeout"}
```

### Bước 6 — Entity Extraction
Sau khi có intent, **merge entities** từ hai nguồn:
```
base_entities = result.entities  (từ classifier)
    +
extracted_entities = entity_extractor.extract(sentence, intent, context)
    
    Theo intent:
    - control_device:    device, action, location, value?, unit?
    - environmental_comfort: comfort_type (cooling/warming/brighten/dim/ventilate)
    - activate_scene:    scene_type (sleep/wake_up/movie/away/home)
    - query_sensor:      sensor_type (temperature/humidity/rain/gas/fire/motion)
    - query_device_status: device, location?
    - security_mode:     mode (armed/disarmed)
    - security_alert:    alert_type (fire/gas/intrusion), priority="high"
    
    Entity extraction dùng longest-match-first để tránh nhầm:
    "quạt trần" match trước "quạt"
    "phòng ngủ chính" match trước "phòng ngủ"
```

### Bước 7 — Confidence Check & Response Building

**Confidence threshold = 0.7** (cấu hình được qua `CONFIDENCE_THRESHOLD`):

```
confidence < 0.7?
    └── Với 1 câu → FallbackResponse:
            {
                "intent": "unknown",
                "confidence": 0.45,
                "clarification_needed": true,
                "suggestions": ["Bạn muốn bật thiết bị nào và ở phòng nào?"],
                "top_intents": [
                    {"intent": "control_device", "confidence": 0.45},
                    {"intent": "query_sensor", "confidence": 0.32},
                    ...
                ]
            }
    └── Với nhiều câu → intent = "unknown" nhưng vẫn tiếp tục

confidence >= 0.7?
    └── SuccessResponse:
            {
                "intent": "control_device",
                "entities": {
                    "device": "light",
                    "action": "turn_on",
                    "location": "living_room"
                },
                "confidence": 1.0,
                "classifier_type": "rule",
                "timestamp": "...",
                "priority": null
            }
```

### Bước 8 — Multi-Intent Merging
```
len(sentences) == 1? → trả về single IntentResponse
len(sentences) > 1?  → MultiIntentResponse:
    {
        "intents": [response1, response2, ...],
        "total_intents": 2,
        "timestamp": "..."
    }
```

### Bước 9 — Cache Store & Logging
```
cache.set(normalized_text, response, context)
    key = SHA256(json({text, context}))
    TTL = 300s (5 phút)

structured_logger.log_request(
    user_id, text, intent, confidence,
    response_time_ms, classifier_type
)
    → JSON log: {timestamp, event, user_id, text(truncated), intent, confidence, ...}
    → Sensitive data bị filter: password=***, Bearer ***, credit card numbers
```

---

## 🧠 Kiến trúc Model PhoBERT

```
Input: "bật đèn phòng khách"
    ↓
PhoBERT Tokenizer (vinai/phobert-base)
    ↓ input_ids, attention_mask (1, 128)
    ↓
PhoBERT Encoder (12-layer Transformer, hidden=768)
    ↓ CLS token → pooled_output (1, 768)
    ↓
Concatenate context_embedding (1, 32)  [hoặc zero padding nếu không có]
    ↓ (1, 800)
    ↓
Dropout(0.1)
    ↓
Linear(800 → 256) + ReLU
    ↓
Dropout(0.1)
    ↓
Linear(256 → 8)  [số intent classes]
    ↓ logits
    ↓
Softmax → probabilities
    ↓
Top-1 = predicted intent + confidence
```

**Model files cần có trong `models/phobert_intent_v1/`:**
- `best_model.pt` — PyTorch weights
- `config.json` — Cấu hình model (num_intents, hidden_size, context_dim...)
- `intent_mapping.json` — Mapping intent_name ↔ id
- `best_model.onnx` *(tùy chọn)* — ONNX exported model

---

## 🎯 Các Intent được hỗ trợ

| Intent | Ví dụ | Entities |
|--------|-------|---------|
| `control_device` | "Bật đèn phòng khách" | device, action, location, value? |
| `environmental_comfort` | "Nóng quá" | comfort_type |
| `query_sensor` | "Nhiệt độ bao nhiêu?" | sensor_type, location? |
| `query_device_status` | "Đèn có bật không?" | device, location? |
| `security_mode` | "Bật báo động" | mode (armed/disarmed) |
| `security_alert` | "Cháy rồi!" | alert_type, priority="high" |
| `activate_scene` | "Đi ngủ" | scene_type |
| `unknown` | (không nhận diện được) | — |

---

## 📡 Các Endpoints

| Method | Path | Auth | Mô tả |
|--------|------|------|-------|
| `GET` | `/` | ❌ | Server info |
| `GET` | `/health` | ❌ | Health check |
| `GET` | `/docs` | ❌ | Swagger UI |
| `POST` | `/api/v1/intent/classify` | ✅ JWT | **Endpoint chính** |
| `GET` | `/api/v1/intents` | ✅ JWT | Liệt kê danh sách intents |
| `GET` | `/api/v1/metrics` | ✅ JWT | Prometheus metrics |
| `POST` | `/api/v1/model/reload` | ✅ JWT Admin | Hot-reload model |

---

## 🛡️ Bảo mật & Giới hạn

| Tính năng | Chi tiết |
|-----------|---------|
| **Authentication** | JWT HS256, Bearer token |
| **Rate Limiting** | Token bucket: 60 req/phút/user, burst=60 |
| **CORS** | Cấu hình whitelist origins |
| **Input validation** | Max 500 ký tự, phải có ký tự chữ cái |
| **Inference timeout** | 5 giây (fallback về rule-based) |
| **Log filtering** | Password/token/credit card bị mask |

---

## 🔧 Biến môi trường quan trọng

| Biến | Mặc định | Mô tả |
|------|----------|-------|
| `API_PORT` | `8001` | Port server |
| `JWT_SECRET_KEY` | *(phải đổi!)* | Secret để sign JWT |
| `REDIS_URL` | `redis://localhost:6379/0` | URL Redis |
| `MODEL_PATH` | `models/phobert_intent_v1` | Thư mục model |
| `USE_ONNX` | `true` | Dùng ONNX Runtime |
| `CONFIDENCE_THRESHOLD` | `0.7` | Ngưỡng tin cậy |
| `RATE_LIMIT_PER_MINUTE` | `60` | Giới hạn request/phút |
| `INFERENCE_TIMEOUT_SECONDS` | `5` | Timeout inference |
| `CORS_ORIGINS` | `http://localhost:3000,...` | Danh sách origins |

---

## 📊 Metrics (Prometheus)

Server export các metrics tại `GET /api/v1/metrics`:

| Metric | Loại | Mô tả |
|--------|------|-------|
| `api_requests_total` | Counter | Tổng requests (endpoint, status) |
| `api_request_duration_seconds` | Histogram | Thời gian xử lý |
| `cache_hits_total` | Counter | Cache hit count |
| `cache_misses_total` | Counter | Cache miss count |
| `classification_confidence` | Histogram | Phân phối confidence score |
| `rate_limited_total` | Counter | Số request bị rate limit |
| `model_reloads_total` | Counter | Số lần reload model |

---

## 🔄 Tóm tắt luồng đầy đủ (flow diagram)

```
Client Request
      │
      ▼
[FastAPI Router]
      │
      ▼
[Auth: JWT Verify] ──fail──► 401 Unauthorized
      │
      ▼
[Rate Limit Check] ──exceed──► 429 Too Many Requests
      │
      ▼
[Input Validation] ──invalid──► 400 Bad Request
      │
      ▼
[Preprocessing Pipeline]
  lowercase → remove_punct → remove_emoji
  → normalize_slang → correct_spelling
  → split_sentences
      │
      ▼
[Cache Lookup (Redis)] ──HIT──► Return cached response
      │ MISS
      ▼
  ┌── For each sentence ──┐
  │                        │
  │  [Hybrid Classifier]   │
  │    ├─ Rule-based?      │
  │    │   confidence=1.0 ─┤──► Fast path return
  │    └─ ML (PhoBERT)     │
  │        ONNX / PyTorch  │
  │        with context    │
  │    Compare & pick best │
  │                        │
  │  [Entity Extractor]    │
  │   merge entities       │
  └────────────────────────┘
      │
      ▼
[Confidence Check]
  < 0.7? ──► FallbackResponse (clarification_needed: true)
  >= 0.7? ─► SuccessResponse
      │
      ▼
[Response Building]
  1 sentence  → IntentResponse
  N sentences → MultiIntentResponse
      │
      ▼
[Cache Store (Redis, TTL=5min)]
      │
      ▼
[Structured Logging (JSON)]
      │
      ▼
[Prometheus Metrics Update]
      │
      ▼
Return Response to Client
```

---

## 🏋️ Training & Scripts

Scripts trong `scripts/`:

| Script | Mô tả |
|--------|-------|
| `generate_training_data.py` | Sinh dữ liệu training tổng hợp |
| `data_augmenter.py` | Tăng cường dữ liệu (paraphrase, synonym, typo) |
| `split_dataset.py` | Chia train/val/test |
| `validate_dataset.py` | Kiểm tra chất lượng dataset |
| `train_phobert.py` | Fine-tune PhoBERT |
| `export_to_onnx.py` | Export model sang ONNX |

---

## 💡 Điểm quan trọng cần nhớ

1. **Rule-based có ưu tiên cao hơn** khi confidence = 1.0 → giảm latency xuống <10ms
2. **ML (PhoBERT) mạnh hơn** với câu tự nhiên phức tạp hơn (<300ms)
3. **Context embedding** giúp ML phân biệt ý định khi ngữ cảnh phòng/thiết bị/giờ thay đổi
4. **Cache Redis** làm giảm đáng kể latency với các câu lặp lại (smart home thường hỏi câu giống nhau)
5. **Security alert** (`cháy/gas/trộm`) có **false positive prevention**: nếu text có từ liên quan giải trí (`phim/game/nhạc...`) thì KHÔNG phân loại thành security_alert
6. **Multi-intent**: câu "bật đèn và tắt quạt" được tách thành 2 sub-sentences, mỗi câu phân loại độc lập
