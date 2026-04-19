# SmartHome Analytics & Suggestions - Setup Guide

Hướng dẫn hoàn chỉnh để triển khai hệ thống phân tích lịch sử sinh hoạt và gợi ý thông minh.

## Kiến Trúc Tổng Thể

```
┌─────────────────────────────────────────────────────────────────┐
│                      SmartHome System                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐        ┌──────────────────┐               │
│  │  PostgreSQL     │────────│  Grafana        │               │
│  │  (Data + Logs)  │        │  (Visualization)│               │
│  └────────┬────────┘        └──────────────────┘               │
│           │                                                    │
│           ├─────── seed_data.py → Tạo giả lập data             │
│           ├─────── run_analytics.py → KMeans clustering        │
│           ├─────── run_llm_formatter.py → LLM text gen        │
│           │                                                    │
│  ┌────────▼────────────────────────────────────┐               │
│  │  FastAPI Backend (/suggestions/me)          │               │
│  └────────┬────────────────────────────────────┘               │
│           │                                                    │
│  ┌────────▼────────────────────────────────────┐               │
│  │  React Native (Expo) - Suggestions Tab      │               │
│  └─────────────────────────────────────────────┘               │
│                                                                 │
│  ┌─────────────────┐  (optional)                               │
│  │  Ollama (Qwen)  │  LLM cho text generation               │
│  └─────────────────┘                                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Các Bước Khởi Động

### 1. Khởi Động Docker Compose

```bash
cd d:\K2N3\PBL5\DUT.SmartHomeSystem-dev

# Khởi động tất cả services
docker-compose up -d

# Kiểm tra status
docker-compose ps

# Logs:
docker-compose logs backend  # FastAPI backend
docker-compose logs db       # PostgreSQL
docker-compose logs grafana  # Grafana
```

Services sẽ chạy tại:
- **Backend**: http://localhost:8000 (FastAPI)
- **PostgreSQL**: localhost:5433
- **Grafana**: http://localhost:3000 (user: admin, pass: admin)
- **Mobile (Expo)**: http://localhost:8081

---

### 2. Tạo Database Migration

```bash
# Vào thư mục backend
cd backend

# Chạy migration (Alembic)
# Windows PowerShell:
$env:DATABASE_URL="postgresql://postgres:postgres@localhost:5433/smarthome"
python -m alembic upgrade head

# Linux/Mac:
export DATABASE_URL="postgresql://postgres:postgres@localhost:5433/smarthome"
python -m alembic upgrade head
```

Migration sẽ tạo các bảng:
- `homes`, `home_users`, `rooms`, `devices`
- `users`, `user_patterns`, `suggestion_logs`
- `activity_logs`, `sensor_data`, `user_presence`

---

### 3. Seed Dữ Liệu Giả Lập

```bash
# Từ thư mục backend
python scripts/seed_data.py --days 60 --drop

# Output:
# - Tạo 1-2 user (Hùng, Mai)
# - Tạo 1 home
# - Tạo ~5-7 devices (đèn, quạt, điều hòa)
# - Sinh ra 60 ngày hoạt động với thội quen + noise

# Xem chi tiết kết quả:
psql postgresql://postgres:postgres@localhost:5433/smarthome
# \dt  — xem tất cả bảng
# SELECT COUNT(*) FROM activity_logs;  — đếm log
```

---

### 4. Xem Dữ Liệu trên Grafana

**Truy cập**: http://localhost:3000

**Đăng nhập**: user `admin` / password `admin` (hoặc đổi bất kỳ lúc nào)

**Dashboards có sẵn**:

1. **Biểu đồ Nhiệt độ theo Thời gian** (Line chart, 7 ngày)
   - Visualization của cột `temperature` từ metadata
   - Dùng để quân tr cảm biến nhiệt độ một cách trực quan

2. **Biểu đồ Độ Ẩm theo Thời gian** (Line chart, 7 ngày)  
   - Visualization của cột `humidity` từ metadata
   - Theo dõi mô hình độ ẩm hàng ngày

3. **Biểu đồ Số Lần Bật/Tắt của Từng Thiết Bị** (Bar chart, 30 ngày)
   - Thống kê tần suất sử dụng mỗi device
   - Giúp nhận biết thiết bị nào dùng nhiều nhất

4. **Lịch sử Hoạt động** (Table, 24h gần nhất)
   - Top 20 eventos gần đây nhất
   - Xem user nào, device nào, tác vụ gì

**Query SQL có sẵn**: Xem tại `grafana/provisioning/dashboards/smarthome-dashboard.json`

> 💡 **Tip**: Có thể viết query SQL tùy chỉnh trong Grafana query editor

---

### 5. Chạy Analytics Pipeline

#### 5.1 Run Analytics (KMeans + Habit Mining)

```bash
cd backend

# Set environment variables (Windows PowerShell)
$env:DATABASE_URL="postgresql://postgres:postgres@localhost:5433/smarthome"

# Chạy
python scripts/run_analytics.py

# Output:
# ── Home {id} ──
#   Data: 60 ngày / 2 users
#
#   User: hung@example.com
#   [Rule-based]
#     → 8 TIME_HABIT patterns cho user ...
#   [Anomaly]
#     → 2 ANOMALY patterns
#
#   User: mai@example.com
#   [Rule-based]
#     → 10 TIME_HABIT patterns ...
#   [Anomaly]
#     → 1 ANOMALY patterns
#
#   [KMeans]
#     → KMeans k=2, 2 users clustered
#
# ✓ Xong! Kiểm tra bảng user_patterns trong DB.
```

**Kiểm tra kết quả**:
```bash
psql postgresql://postgres:postgres@localhost:5433/smarthome

# Xem pattern tìm được:
SELECT id, user_id, device_id, pattern_type, confidence, is_active 
FROM user_patterns 
WHERE is_active = true
ORDER BY confidence DESC;

# Xem chi tiết pattern (JSON):
SELECT pattern_data FROM user_patterns 
WHERE pattern_type = 'TIME_HABIT' LIMIT 3;
```

#### 5.2 Run LLM Formatter (Chuyển Thành Text Gợi Ý)

**Yêu cầu**: Ollama server chạy với mô hình Qwen 2.5

```bash
# Terminal riêng: Khởi động Ollama
ollama serve

# Terminal khác: Pull model Qwen
ollama pull qwen2.5:3b

# Sau đó, từ thư mục backend:
$env:DATABASE_URL="postgresql://postgres:postgres@localhost:5433/smarthome"
$env:LLM_PROVIDER="ollama"
$env:OLLAMA_URL="http://localhost:11434"
$env:OLLAMA_MODEL="qwen2.5:3b"

python scripts/run_llm_formatter.py

# Output:
# LLM provider: ollama / model: qwen2.5:3b
#
# ── Home {id} ──
#   Xử lý 12 patterns...
#     [TIME_HABIT] light_bedroom → calling ollama...
#       JSON parse success: title='...'
#     [TIME_HABIT] fan_living → calling ollama...
#     [ANOMALY] ac_bedroom → calling ollama...
#     ...
#   → Tạo 8 suggestion_logs mới
#
# ✓ Done! Kiểm tra bảng suggestion_logs.
```

**Kiểm tra kết quả**:
```bash
psql postgresql://postgres:postgres@localhost:5433/smarthome

# Xem gợi ý vừa tạo:
SELECT id, user_id, action_type, suggestion_text, was_accepted, created_at
FROM suggestion_logs
ORDER BY created_at DESC
LIMIT 10;

# Xem chi tiết (JSON):
SELECT suggestion_json FROM suggestion_logs LIMIT 3;
```

---

### 6. Kiểm Tra API Backend

```bash
# Get suggestions cho user
curl -X GET "http://localhost:8000/suggestions/me?limit=10" \
  -H "Content-Type: application/json"

# Kết quả:
# {
#   "total": 8,
#   "suggestions": [
#     {
#       "id": 1,
#       "user_id": "550e8400-e29b-41d4-a716-446655440000",
#       "action_type": "SCHEDULE",
#       "suggestion_text": "Bật điều hòa phòng ngủ lúc 22h",
#       "suggestion_json": {...},
#       "was_accepted": null,
#       "created_at": "2026-03-25T10:00:00"
#     },
#     ...
#   ]
# }

# Accept/Dismiss một gợi ý
curl -X POST "http://localhost:8000/suggestions/1/accept" \
  -H "Content-Type: application/json" \
  -d '{"was_accepted": true, "action_taken": "SCHEDULED"}'
```

---

### 7. Chạy Mobile App (React Native + Expo)

```bash
# Terminal riêng
cd mobile

# Cài dependencies (lần đầu)
npm install

# Khởi động Expo
npm start

# Hiện menu:
# i           → iOS simulator
# a           → Android emulator
# w           → Web browser
# j           → toggle debugger
# r           → reload app

# Bấn 'a' để mở Android emulator
# Hoặc scan QR code bằng Expo Go app trên điện thoại
```

**Giao diện Suggestions Tab**:
- Hiển thị danh sách các gợi ý (tối đa 30 ngày gần nhất)
- Từng gợi ý là một card với:
  - Badge màu (SCHEDULE=green, ALERT=orange, AUTOMATION=blue)
  - Tiêu đề + mô tả
  - Nút "Bỏ qua" / "Chấp nhận"
- Khi swipe refresh, reload từ API
- Khi click "Chấp nhận", gợi ý sẽ xóa khỏi danh sách

---

## Full Workflow Demo

### Mục tiêu
Bạn là **Hùng**, người dùng hay bật điều hòa lúc 22h. Hệ thống sẽ phát hiện thói quen này và gợi ý tạo lịch tự động.

### Các bước
1. **Khởi động Docker**: `docker-compose up -d`
2. **Migration**: `python -m alembic upgrade head`
3. **Seed data**: `python scripts/seed_data.py --days 60 --drop`
4. **Xem dữ liệu trên Grafana**: http://localhost:3000
5. **Chạy analytics**: `python scripts/run_analytics.py`
6. **Khởi động Ollama**: `ollama serve` + `ollama pull qwen2.5:3b`
7. **Format gợi ý**: `python scripts/run_llm_formatter.py`
8. **Test API**: `curl http://localhost:8000/suggestions/me`
9. **Chạy mobile**: `cd mobile && npm start`
10. **Xem gợi ý trên app**: Tab "Suggestions" → Chấp nhận gợi ý!

---

## Troubleshooting

### API trả về 404
- Kiểm tra DB migration chạy OK: `SELECT * FROM suggestion_logs;`
- Kiểm tra dummy user_id trong `controller.py` đúng

### Ollama timeout
- Kiểm tra Ollama service: `ollama serve` vs port 11434
- Model pull OK: `ollama list`
- Temperature quá cao → LLM output khó parse

### Mobile app không kết nối API
- Xem `EXPO_PUBLIC_API_URL` trong environment
- Kiểm tra backend chạy: `curl http://localhost:8000/docs`
- Network simulator có thể block localhost → dùng IP thực

### Database connection error
- Kiểm tra PostgreSQL chạy: `docker-compose ps | grep db`
- Port mapping: `localhost:5433` (không phải 5432)
- User/pass: postgres/postgres

---

## Kết Tiếp

✅ Bạn đã hoàn thành:
- [x] Grafana dashboard để trực quan dữ liệu
- [x] KMeans clustering + Habit mining 
- [x] LLM text generation cho gợi ý tiếng Việt
- [x] API /suggestions/me  
- [x] React Native tab hiển thị & interact gợi ý

🚀 Bước tiếp theo:
- Integrate thực với MQTT devices
- Thiết kế lịch tự động (schedule creation)
- Thêm authentication/authorization tốt hơn
- Optimize query performance khi data lớn
- Deploy lên production (Docker swarm / K8s)

---

## Links Hữu Ích

- PostgreSQL: https://www.postgresql.org/docs/
- Grafana: https://grafana.com/docs/
- FastAPI: https://fastapi.tiangolo.com/
- Ollama: https://ollama.ai/
- React Native: https://reactnative.dev/
- Expo: https://docs.expo.dev/
