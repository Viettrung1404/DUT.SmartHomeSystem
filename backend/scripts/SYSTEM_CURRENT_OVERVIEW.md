# Smart Home System - Current Architecture Overview (Integrated v2.1)

Tài liệu này giải thích luồng logic nhat quán của hệ thống Smart Home Intelligence Layer theo mô hình **3 Tầng (3-Layer Pipeline)**.

## 1. Luồng Logic nhat quán (The Value Chain)

Hệ thống hoạt động như một chuỗi dây chuyền sản xuất, trong đó mỗi bước đóng một vai trò quan trọng để đảm bảo gợi ý đến tay người dùng là chất lượng nhất.

| Tầng (Layer) | Script chính | Vai trò | Chế độ (Analogy) |
| :--- | :--- | :--- | :--- |
| **1. Analytics Layer** | `run_analytics.py` | **Khai thác (Mining)**: Tìm kiếm mọi thói quen, bất thường từ dữ liệu thô. | **Phóng viên**: Thu thập mọi tin tức. |
| **2. Decision Layer** | `run_decision_scoring.py` | **Kiểm duyệt (Filtering)**: Chấm điểm, lọc bỏ tin rác, kiểm tra Cooldown. | **Tổng biên tập**: Duyệt tin giá trị. |
| **3. Delivery Layer** | `run_llm_formatter.py` | **Biên tập (Formatting)**: Viết lại gợi ý bằng tiếng Việt tự nhiên qua LLM. | **Nhà văn**: Viết lời cho tin đã duyệt. |

---

## 2. Chi tiết từng tầng

### Tầng 1: Analytics Layer (Phóng viên)
*   **Mục tiêu**: Biến `activity_logs` thành `user_patterns`.
*   **Mô hình Học máy (ML)**: 
    *   Sử dụng **K-Means Clustering** (Unsupervised) để phân loại phong cách sống của người dùng dựa trên vector 27 chiều.
    *   Sử dụng **Statistical Analysis** để phát hiện thói quen theo giờ (Habit) và bất thường (Anomaly).
*   **Kết quả**: Một danh sách các "khả năng" (Candidates) nhưng chưa được kiểm chứng về mặt thời điểm gửi.

### Tầng 2: Decision Layer (Tổng biên tập) - **TRỌNG TÂM CẢI TIẾN**
*   **Mục tiêu**: Lọc bỏ "nhiễu" và ngăn chặn tình trạng người dùng bị làm phiền (Alert Fatigue).
*   **Logic chấm điểm (Scoring)**:
    *   `S = Confidence + Severity + Historical_Acceptance + Energy_Saving`.
    *   Chỉ những pattern có `S >= threshold` mới được đi tiếp.
*   **Hàng rào bảo vệ (Guardrails)**:
    *   **Cooldown**: Chặn các gợi ý cùng loại trong vòng 48h.
    *   **Decision Audit**: Mọi quyết định (Block/Pass) đều được ghi vào `suggestion_decision_logs` để phục vụ đo lường.

### Tầng 3: Delivery Layer (Nhà văn)
*   **Mục tiêu**: Biến dữ liệu kỹ thuật thành gợi ý tiếng Việt thân thiện.
*   **Cơ chế**: Nhận danh sách các ứng viên đã được "Tổng biên tập" duyệt từ file `decision_candidates.json`.
*   **Công nghệ**: Sử dụng **Ollama (Qwen2.5/Llama3)** hoặc **Claude** để sinh văn bản dựa trên Prompt có ngữ cảnh (Context-aware).

---

## 3. Hệ thống Quan sát & Đo lường (Observability)

Hệ thống không chỉ chạy mà còn tự đo lường hiệu quả thông qua:
*   **Metrics Service**: Tính toán tỷ lệ chấp nhận thực tế (`Effective Accept Rate`) dựa trên phản hồi của người dùng.
*   **Guardrail Metrics**: Đo lường "Công sức" của hệ thống trong việc chặn tin rác (`Cooldown Suppressions`).
*   **SaaS Dashboard**: Hiển thị trực quan xu hướng và hiệu quả của các mô hình ML theo thời gian thực.

## 4. Tại sao luồng này lại "Thông minh"?

Sự thông minh không chỉ nằm ở mô hình **K-Means** hay **LLM**, mà nằm ở **sự phối hợp giữa 3 tầng**:
1.  **K-Means** giúp gợi ý mang tính cá nhân hóa (Personalization).
2.  **Decision Layer** giúp gợi ý đúng thời điểm (Timeliness) và không gây phiền.
3.  **LLM** giúp gợi ý dễ hiểu (Readability).

**Kết luận**: Nếu thiếu bất kỳ tầng nào, hệ thống sẽ trở nên hoặc là quá "máy móc" (thiếu LLM), hoặc là quá "phiền phức" (thiếu Decision), hoặc là quá "đơn giản" (thiếu Analytics).
