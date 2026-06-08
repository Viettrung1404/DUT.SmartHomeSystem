# PLAN.md — Smart Home AI Server tách riêng cho L3/L4 RAG Agent

## 1. Mục tiêu

Mục tiêu là tách phần AI/LLM ra thành một service riêng gọi là **AI Server**. Backend Smart Home hiện tại không chạy trực tiếp Ollama/RAG/Agent nữa, mà chỉ gọi API sang AI Server.

AI Server sẽ tận dụng lại tư duy từ dự án RAG cũ, đặc biệt là:

- **L3 — Tool-Augmented RAG**: LLM không tự trả lời theo trí nhớ, mà chọn tool để truy vấn dữ liệu thật.
- **L4 — Memory / Conversation Context**: chatbot nhớ ngữ cảnh hội thoại trong một session, ví dụ câu trước hỏi về “đèn bếp”, câu sau hỏi “thiết bị đó thì sao?”.

Mục tiêu tính năng:

```text
User hỏi bằng tiếng Việt
→ Backend gọi AI Server
→ AI Server dùng tool truy vấn dữ liệu Smart Home
→ Ollama local tổng hợp câu trả lời
→ Backend trả kết quả cho Mobile/Web
```

Ví dụ câu hỏi:

```text
Tối qua nhà tôi có gì bất thường không?
Tại sao hệ thống gợi ý tắt đèn bếp?
Thiết bị nào hay bị quên tắt nhất?
Tuần này điều hòa phòng ngủ dùng nhiều không?
Vì sao có cảnh báo cửa chính lúc 2h sáng?
```

---

## 2. Nguyên tắc thiết kế

### 2.1 AI Server là service độc lập

Backend chính chỉ cần gọi HTTP API:

```text
Backend Smart Home → AI Server → Ollama / Tools / Memory
```

Backend không cần biết bên trong AI Server dùng model gì, prompt gì, hay tool nào.

### 2.2 Không để LLM đọc database trực tiếp

LLM không được tự viết SQL tự do. AI Server phải cung cấp tool an toàn, có tham số rõ ràng.

Ví dụ tool hợp lệ:

```text
query_activity_logs(home_id, user_id, time_range, device_slug)
query_user_patterns(home_id, user_id, pattern_type)
query_suggestion_logs(user_id, status)
query_guardian_events(home_id, severity, time_range)
query_device_status(home_id, device_slug)
```

### 2.3 LLM chỉ tổng hợp và giải thích

Phần phát hiện pattern/anomaly vẫn do pipeline hiện tại làm:

```text
activity_logs
→ run_analytics.py
→ user_patterns
→ run_decision_scoring.py
→ suggestion_logs
```

AI Server chỉ đọc kết quả từ các bảng này để trả lời người dùng.

### 2.4 Có fallback khi Ollama lỗi

Nếu Ollama không chạy hoặc timeout, AI Server vẫn trả về câu trả lời template đơn giản dựa trên tool result.

---

## 3. Kiến trúc tổng thể

```text
Mobile/Web
   ↓
Backend Smart Home
   ↓ HTTP
AI Server
   ├── Chat API
   ├── L4 Memory Manager
   ├── L3 Tool Router
   ├── Smart Home Tools
   ├── Prompt Builder
   ├── Ollama Client
   └── Response Formatter
        ↓
PostgreSQL / Smart Home DB
```

Luồng xử lý:

```text
1. User gửi câu hỏi lên Backend.
2. Backend gọi POST /v1/chat của AI Server.
3. AI Server đọc memory theo session_id.
4. AI Server phân loại intent câu hỏi.
5. Tool Router chọn tool phù hợp.
6. Tool truy vấn DB hoặc gọi API Backend.
7. Prompt Builder gom tool_result + memory + user question.
8. Ollama sinh câu trả lời.
9. Response Formatter trả answer + evidence + used_tools.
10. Memory Manager cập nhật context hội thoại.
```

---

## 4. Phạm vi phiên bản đầu tiên

Version đầu tiên chỉ cần hỗ trợ 5 nhóm câu hỏi:

### 4.1 Hỏi bất thường / cảnh báo

Ví dụ:

```text
Tối qua nhà tôi có gì bất thường không?
Có cảnh báo nào nghiêm trọng không?
```

Tool dùng:

```text
query_guardian_events
query_suggestion_logs(action_type=ALERT)
query_user_patterns(pattern_type=ANOMALY)
```

Nếu chưa có bảng `guardian_events`, tạm thời lấy từ:

```text
user_patterns pattern_type = ANOMALY
suggestion_logs action_type = ALERT
```

### 4.2 Hỏi lý do gợi ý

Ví dụ:

```text
Tại sao app gợi ý bật đèn phòng khách?
Vì sao hệ thống nói tôi hay quên tắt đèn bếp?
```

Tool dùng:

```text
query_suggestion_logs
query_user_patterns
```

### 4.3 Hỏi lịch sử thiết bị

Ví dụ:

```text
Đèn bếp hôm qua bật bao lâu?
Tuần này điều hòa phòng ngủ chạy mấy lần?
```

Tool dùng:

```text
query_activity_logs
```

### 4.4 Hỏi thiết bị hay bị quên tắt

Ví dụ:

```text
Thiết bị nào hay bị quên tắt nhất?
```

Tool dùng:

```text
query_user_patterns(pattern_type=ANOMALY)
query_activity_logs(event_type=FORGOT_OFF)
```

### 4.5 Hỏi tiếp theo dựa trên memory

Ví dụ:

```text
User: Đèn bếp hôm qua bật bao lâu?
Bot: ...
User: Thế tuần này thì sao?
```

L4 Memory phải hiểu “thế” = đèn bếp.

---

## 5. Cấu trúc source code đề xuất

Tạo service riêng:

```text
ai-server/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── api/
│   │   ├── chat_routes.py
│   │   └── health_routes.py
│   ├── agent/
│   │   ├── agent.py
│   │   ├── intent_router.py
│   │   ├── tool_router.py
│   │   └── response_formatter.py
│   ├── tools/
│   │   ├── activity_tools.py
│   │   ├── pattern_tools.py
│   │   ├── suggestion_tools.py
│   │   ├── guardian_tools.py
│   │   └── device_tools.py
│   ├── memory/
│   │   ├── memory_store.py
│   │   └── summarizer.py
│   ├── llm/
│   │   ├── ollama_client.py
│   │   └── prompts.py
│   ├── db/
│   │   ├── session.py
│   │   └── repositories.py
│   └── schemas/
│       ├── chat_schema.py
│       ├── tool_schema.py
│       └── response_schema.py
├── tests/
│   ├── test_intent_router.py
│   ├── test_tools.py
│   ├── test_chat_api.py
│   └── test_memory.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 6. API contract giữa Backend và AI Server

### 6.1 Health check

```http
GET /health
```

Response:

```json
{
  "status": "ok",
  "ollama": "ok",
  "db": "ok"
}
```

### 6.2 Chat API

```http
POST /v1/chat
```

Request:

```json
{
  "session_id": "session-abc-123",
  "user_id": "user-uuid",
  "home_id": "home-uuid",
  "message": "Tối qua nhà tôi có gì bất thường không?",
  "timezone": "Asia/Ho_Chi_Minh"
}
```

Response:

```json
{
  "answer": "Tối qua có 1 cảnh báo đáng chú ý: cửa chính mở lúc 2:14 sáng, nằm ngoài khung giờ sinh hoạt bình thường. Sau đó hệ thống không ghi nhận chuyển động trong 10 phút.",
  "intent": "GUARDIAN_EVENT_QUERY",
  "used_tools": [
    "query_guardian_events",
    "query_activity_logs"
  ],
  "evidence": [
    {
      "type": "guardian_event",
      "device_name": "Cửa chính",
      "event_time": "2026-06-05T02:14:00+07:00",
      "severity": "HIGH",
      "risk_score": 0.86
    }
  ],
  "suggested_actions": [
    "Kiểm tra camera",
    "Kiểm tra trạng thái khóa cửa"
  ],
  "memory_updated": true
}
```

### 6.3 Reset memory

```http
POST /v1/chat/reset
```

Request:

```json
{
  "session_id": "session-abc-123",
  "user_id": "user-uuid"
}
```

Response:

```json
{
  "success": true
}
```

---

## 7. L3 Tool-Augmented RAG

### 7.1 Tool Router

Tool Router nhận intent và chọn tool.

Ví dụ mapping:

```python
TOOL_MAP = {
    "GUARDIAN_EVENT_QUERY": [
        "query_guardian_events",
        "query_activity_logs"
    ],
    "SUGGESTION_EXPLAIN": [
        "query_suggestion_logs",
        "query_user_patterns"
    ],
    "DEVICE_HISTORY": [
        "query_activity_logs"
    ],
    "FORGOT_OFF_QUERY": [
        "query_user_patterns",
        "query_activity_logs"
    ],
    "DEVICE_STATUS_QUERY": [
        "query_device_status"
    ]
}
```

### 7.2 Tool output phải có cấu trúc

Ví dụ output của `query_guardian_events`:

```json
{
  "tool_name": "query_guardian_events",
  "result_count": 1,
  "items": [
    {
      "event_type": "DOOR_OPEN_AT_NIGHT",
      "device_name": "Cửa chính",
      "created_at": "2026-06-05T02:14:00+07:00",
      "severity": "HIGH",
      "risk_score": 0.86,
      "summary": "Cửa chính mở ngoài khung giờ bình thường."
    }
  ]
}
```

### 7.3 Không cho LLM trả lời nếu không có evidence

Prompt phải ép model:

```text
Nếu tool_result không có dữ liệu, hãy nói rõ là chưa tìm thấy dữ liệu phù hợp. Không được tự bịa thời gian, thiết bị, số lần, hoặc nguyên nhân.
```

---

## 8. L4 Memory / Conversation Context

### 8.1 Memory cần lưu gì?

Không cần lưu toàn bộ chat dài. Chỉ lưu context ngắn:

```json
{
  "session_id": "session-abc-123",
  "user_id": "user-uuid",
  "home_id": "home-uuid",
  "last_intent": "DEVICE_HISTORY",
  "last_device_slug": "kitchen_light",
  "last_device_name": "Đèn bếp",
  "last_time_range": "yesterday",
  "conversation_summary": "Người dùng đang hỏi về lịch sử sử dụng đèn bếp."
}
```

### 8.2 Khi nào dùng memory?

Dùng memory cho câu hỏi thiếu chủ ngữ:

```text
Thế tuần này thì sao?
Còn phòng khách?
Tại sao lại vậy?
Có nghiêm trọng không?
```

### 8.3 Memory store phiên bản đầu

Version đầu dùng Redis hoặc in-memory dictionary.

Nếu muốn nhanh nhất:

```text
In-memory dictionary theo session_id
```

Sau đó nâng cấp:

```text
Redis
```

---

## 9. Prompt cho Ollama

### 9.1 System prompt

```text
Bạn là AI Smart Home Guardian Assistant.
Nhiệm vụ của bạn là trả lời câu hỏi của người dùng dựa trên dữ liệu từ hệ thống nhà thông minh.
Bạn chỉ được dùng dữ liệu trong TOOL_RESULTS và MEMORY_CONTEXT.
Không được bịa thời gian, số lần, tên thiết bị, nguyên nhân hoặc trạng thái.
Nếu dữ liệu không đủ, hãy nói rõ chưa đủ dữ liệu.
Trả lời bằng tiếng Việt, ngắn gọn, dễ hiểu.
Nếu có cảnh báo an toàn, hãy nêu mức độ và hành động đề xuất.
```

### 9.2 User prompt template

```text
USER_QUESTION:
{message}

MEMORY_CONTEXT:
{memory_context}

TOOL_RESULTS:
{tool_results}

Yêu cầu output JSON:
{
  "answer": "...",
  "severity": "none|low|medium|high|critical",
  "suggested_actions": ["..."],
  "evidence_summary": ["..."]
}
```

---

## 10. Database access strategy

Có 2 cách:

### Cách A — AI Server đọc trực tiếp PostgreSQL

```text
AI Server → PostgreSQL Smart Home DB
```

Ưu điểm:

- Nhanh triển khai.
- Tool query dễ viết.
- Không cần tạo nhiều API nội bộ ở Backend.

Nhược điểm:

- AI Server cần quyền DB.
- Phải cẩn thận bảo mật query.

### Cách B — AI Server gọi Backend Internal API

```text
AI Server → Backend Internal API → PostgreSQL
```

Ưu điểm:

- Backend kiểm soát quyền dữ liệu.
- AI Server không cần biết schema DB chi tiết.

Nhược điểm:

- Cần viết thêm nhiều API.

### Khuyến nghị

Để triển khai nhanh:

```text
Giai đoạn 1: AI Server đọc trực tiếp PostgreSQL với quyền read-only.
Giai đoạn 2: Chuyển dần sang Backend Internal API nếu cần bảo mật hơn.
```

---

## 11. Environment variables

```env
AI_SERVER_PORT=8100
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/smarthome
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
AI_SERVER_API_KEY=change_me
MEMORY_BACKEND=memory
REQUEST_TIMEOUT_SECONDS=60
MAX_TOOL_ROWS=50
```

---

## 12. Backend tích hợp như thế nào?

Backend thêm service client:

```text
backend/services/ai_server_client.py
```

Pseudo-code:

```python
import requests

class AIServerClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key

    def chat(self, session_id, user_id, home_id, message):
        response = requests.post(
            f"{self.base_url}/v1/chat",
            headers={"X-API-Key": self.api_key},
            json={
                "session_id": session_id,
                "user_id": user_id,
                "home_id": home_id,
                "message": message,
                "timezone": "Asia/Ho_Chi_Minh"
            },
            timeout=60
        )
        response.raise_for_status()
        return response.json()
```

Backend endpoint:

```http
POST /chat/smart-home
```

Backend nhận request từ mobile rồi forward sang AI Server.

---

## 13. Docker Compose đề xuất

```yaml
services:
  ai-server:
    build: ./ai-server
    ports:
      - "8100:8100"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - OLLAMA_URL=http://ollama:11434
      - OLLAMA_MODEL=qwen2.5:7b
      - AI_SERVER_API_KEY=${AI_SERVER_API_KEY}
    depends_on:
      - ollama

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

volumes:
  ollama_data:
```

Nếu Ollama đã chạy trên máy host thì không cần service `ollama`, chỉ cần:

```env
OLLAMA_URL=http://host.docker.internal:11434
```

---

## 14. Roadmap triển khai

### Phase 1 — AI Server skeleton

Mục tiêu:

```text
Chạy được FastAPI server + health check + chat endpoint mock.
```

Việc cần làm:

- Tạo folder `ai-server`.
- Cài FastAPI, Uvicorn, SQLAlchemy, requests/httpx.
- Tạo `/health`.
- Tạo `/v1/chat` trả mock response.
- Backend gọi thử được AI Server.

Done khi:

```text
Backend gọi POST /v1/chat và nhận response thành công.
```

### Phase 2 — L3 tools đọc DB

Mục tiêu:

```text
AI Server query được dữ liệu Smart Home thật.
```

Việc cần làm:

- Viết DB session read-only.
- Viết `query_activity_logs`.
- Viết `query_user_patterns`.
- Viết `query_suggestion_logs`.
- Viết `query_guardian_events` nếu đã có bảng.
- Nếu chưa có `guardian_events`, map từ `suggestion_logs` và `user_patterns`.

Done khi:

```text
Hỏi: “Tối qua có gì bất thường không?”
AI Server trả về dữ liệu từ DB, chưa cần Ollama hay trả lời hay.
```

### Phase 3 — Intent Router

Mục tiêu:

```text
Phân loại câu hỏi và chọn tool đúng.
```

Việc cần làm:

- Implement rule-based intent trước.
- Keyword mapping tiếng Việt.
- Test 10 câu hỏi mẫu.

Ví dụ:

```text
“bất thường”, “cảnh báo”, “nguy hiểm” → GUARDIAN_EVENT_QUERY
“tại sao”, “vì sao”, “gợi ý” → SUGGESTION_EXPLAIN
“bật bao lâu”, “mấy lần”, “lịch sử” → DEVICE_HISTORY
“quên tắt” → FORGOT_OFF_QUERY
```

Done khi:

```text
10/10 câu hỏi demo chọn đúng intent cơ bản.
```

### Phase 4 — Ollama response generation

Mục tiêu:

```text
Tool result được Ollama viết lại thành câu trả lời tiếng Việt.
```

Việc cần làm:

- Viết `ollama_client.py`.
- Viết prompt chống hallucination.
- Parse JSON output.
- Có fallback template nếu Ollama lỗi.

Done khi:

```text
Bot trả lời tự nhiên nhưng vẫn có evidence.
```

### Phase 5 — L4 Memory

Mục tiêu:

```text
Bot hiểu câu hỏi nối tiếp.
```

Việc cần làm:

- Lưu memory theo `session_id`.
- Lưu last_device, last_time_range, last_intent.
- Khi câu hỏi thiếu thông tin, dùng memory để bổ sung.

Test:

```text
User: Đèn bếp hôm qua bật bao lâu?
Bot: ...
User: Thế tuần này thì sao?
Bot phải hiểu vẫn đang hỏi đèn bếp.
```

### Phase 6 — Evidence + UI support

Mục tiêu:

```text
Mobile/Web hiển thị được câu trả lời kèm bằng chứng.
```

Việc cần làm:

- Response có `evidence`.
- Response có `used_tools`.
- Response có `suggested_actions`.
- Backend trả nguyên JSON về mobile.

---

## 15. Demo script đề xuất

### Demo 1 — Hỏi bất thường

User:

```text
Tối qua nhà tôi có gì bất thường không?
```

Expected:

```text
Có 1 cảnh báo mức cao: cửa chính mở lúc 2:14 sáng. Sau đó không có chuyển động trong 10 phút. Bạn nên kiểm tra camera hoặc trạng thái khóa cửa.
```

### Demo 2 — Hỏi lý do gợi ý

User:

```text
Tại sao app gợi ý tắt đèn bếp?
```

Expected:

```text
Vì trong dữ liệu gần đây, đèn bếp có dấu hiệu hoạt động lâu bất thường 5 lần. Hệ thống xem đây là nguy cơ lãng phí điện nên tạo cảnh báo.
```

### Demo 3 — Hỏi lịch sử thiết bị

User:

```text
Điều hòa phòng ngủ tuần này chạy nhiều không?
```

Expected:

```text
Tuần này điều hòa phòng ngủ hoạt động 12 lần, tổng thời gian khoảng 18 giờ. Nếu so với thói quen trung bình, mức sử dụng này cao hơn bình thường.
```

### Demo 4 — Hỏi nối tiếp dùng memory

User:

```text
Đèn bếp hôm qua bật bao lâu?
```

Bot:

```text
Hôm qua đèn bếp bật tổng cộng 3 giờ 20 phút.
```

User:

```text
Thế tuần này thì sao?
```

Bot:

```text
Tuần này đèn bếp bật tổng cộng 14 giờ 10 phút.
```

---

## 16. Testing checklist

### API tests

- `/health` trả ok.
- `/v1/chat` thiếu `message` thì trả lỗi 422.
- API key sai thì trả 401.
- Chat endpoint trả đúng schema.

### Tool tests

- `query_activity_logs` không trả quá `MAX_TOOL_ROWS`.
- Tool chỉ query theo `home_id` và `user_id` hợp lệ.
- Tool không expose dữ liệu user khác.

### Intent tests

- Câu hỏi cảnh báo chọn `GUARDIAN_EVENT_QUERY`.
- Câu hỏi gợi ý chọn `SUGGESTION_EXPLAIN`.
- Câu hỏi lịch sử chọn `DEVICE_HISTORY`.
- Câu hỏi quên tắt chọn `FORGOT_OFF_QUERY`.

### Memory tests

- Câu hỏi nối tiếp dùng đúng `last_device`.
- Reset memory xóa context session.

### LLM tests

- Tool result rỗng thì bot không bịa.
- Ollama timeout thì fallback template.
- Output parse được JSON.

---

## 17. Rủi ro và cách xử lý

### Rủi ro 1 — LLM bịa dữ liệu

Cách xử lý:

- Prompt cấm bịa.
- Tool result phải có evidence.
- Response bắt buộc kèm `evidence`.
- Nếu không có evidence, trả “chưa tìm thấy dữ liệu”.

### Rủi ro 2 — Chậm do Ollama

Cách xử lý:

- Dùng model nhỏ trước: `qwen2.5:3b`.
- Timeout 30–60s.
- Cache câu trả lời theo query phổ biến.
- Fallback template.

### Rủi ro 3 — Tool query quá nhiều dữ liệu

Cách xử lý:

- Luôn giới hạn time range.
- `MAX_TOOL_ROWS=50`.
- Tool trả summary thay vì raw logs dài.

### Rủi ro 4 — Backend bị phụ thuộc AI Server

Cách xử lý:

- Nếu AI Server down, backend trả thông báo:

```text
Trợ lý AI hiện chưa sẵn sàng, vui lòng thử lại sau.
```

- Không ảnh hưởng các tính năng chính như điều khiển thiết bị, gợi ý, đăng nhập.

---

## 18. Kết luận thiết kế

Hướng này phù hợp nhất vì:

- Không phá pipeline Smart Home hiện tại.
- Tận dụng được L3 Tool-Augmented RAG từ repo cũ.
- Tận dụng được L4 Memory để hội thoại tự nhiên hơn.
- AI Server tách riêng nên backend dễ tích hợp.
- Có thể demo nhanh bằng dữ liệu thật từ `activity_logs`, `user_patterns`, `suggestion_logs`.
- Sau này có thể nâng cấp thành AI Home Guardian đầy đủ.

Luồng cuối nên chốt:

```text
Backend chính xử lý nghiệp vụ Smart Home.
AI Server xử lý hỏi đáp, giải thích, truy vấn thông minh và memory.
LLM không quyết định hành động nguy hiểm; chỉ giải thích và đề xuất.
```
