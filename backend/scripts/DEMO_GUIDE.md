# Smart Home Intelligence - Demo Guide for Team 🚀

Tài liệu này hướng dẫn các thành viên trong nhóm cách xem kết quả phân tích AI và chạy Pipeline gợi ý thông minh.

---

## LỰA CHỌN 1: XEM NHANH KẾT QUẢ (Quick View)
Dành cho những ai muốn xem ngay thành quả mà không cần chạy code.

1.  **Xem Báo cáo Analytics**: Mở file `backend/scripts/metrics_dashboard_sample.html` bằng trình duyệt. Bạn sẽ thấy biểu đồ và các chỉ số thông minh.
2.  **Xem Logic Ra Quyết Định (Decision Logic)**: Mở file `backend/scripts/decision_candidates_t065_useful.json`. Đây là nơi AI "giải thích" tại sao nó lại chọn gợi ý này và bỏ gợi ý kia (xem các trường `score`, `usefulness_reasons`).

---

## LỰA CHỌN 2: CHẠY THỰC TẾ TRÊN MÁY (Full Pipeline)
Dành cho việc demo trực tiếp quá trình AI xử lý dữ liệu.

### Bước 0: Chuẩn bị dữ liệu (BẮT BUỘC)
Để các file có sẵn hoạt động được trên máy bạn, bạn **PHẢI** nạp dữ liệu mẫu vào DB để các mã ID (ID của thiết bị, thói quen) được đồng bộ:
```bash
python scripts/seed_data.py
```

### Bước 1: Khai thác thói quen (Analytics Layer)
```bash
python scripts/run_analytics.py
```

### Bước 2: Chấm điểm và Lọc (Decision Layer)
```bash
python scripts/run_decision_scoring.py --threshold 0.65 --write-json scripts/decision_candidates.json
```

### Bước 3: Viết lời gợi ý (Delivery Layer)
*(Yêu cầu đang chạy Ollama model qwen2.5:3b)*
```bash
python scripts/run_llm_formatter.py --decision-json scripts/decision_candidates.json
```

---

## 3. Kiểm tra qua API (Swagger UI)

1.  Khởi động Backend FastAPI: `uvicorn main:app --reload`
2.  Truy cập `http://localhost:8000/docs`
3.  **Xem Dashboard Data**: Gọi API `GET /suggestions/metrics/dashboard`
4.  **Xem Câu Gợi Ý Tiếng Việt**: Gọi API `GET /suggestions`

---

## 4. Giải thích các file quan trọng trong thư mục `scripts/`
*   `analytics_best_config.json`: Cấu hình "bí kíp" của mô hình ML (KMeans/DBSCAN). **Không nên xóa**.
*   `decision_candidates*.json`: Kết quả chấm điểm trung gian. **Có thể dùng để xem nhanh**.
*   `SYSTEM_CURRENT_OVERVIEW.md`: Tài liệu giải thích kiến trúc 3 tầng cho buổi thuyết trình.

---
**Chúc cả nhóm demo thành công!** 🏠💡
