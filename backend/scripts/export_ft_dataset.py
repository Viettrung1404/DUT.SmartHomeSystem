import json
import os
from sqlalchemy import create_engine, text

# Kết nối database giống với cấu hình dự án
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/smarthome")

def export_sft_dataset():
    """
    Trích xuất dữ liệu cho Supervised Fine-Tuning (SFT)
    Dạy model từ một câu nói tự nhiên của user -> trích xuất ra đúng Intent và Device Command JSON
    """
    engine = create_engine(DATABASE_URL)
    query = """
        SELECT 
            sl.suggestion_text AS user_message,
            sl.suggestion_json AS structured_output,
            up.pattern_type::text AS pattern_type
        FROM suggestion_logs sl
        JOIN user_patterns up ON up.id = sl.pattern_id
        WHERE sl.suggestion_json IS NOT NULL
        LIMIT 1000;
    """
    
    dataset = []
    with engine.connect() as conn:
        result = conn.execute(text(query))
        for row in result.mappings():
            # Định dạng Alpaca Format (chuẩn cho LLM Fine-tuning)
            dataset.append({
                "instruction": "Bạn là AI Smart Home Guardian Assistant. Hãy phân tích yêu cầu sau và đưa ra lệnh điều khiển hoặc phân tích dạng JSON.",
                "input": row["user_message"],
                "output": json.dumps(row["structured_output"], ensure_ascii=False)
            })
            
    output_path = "sft_dataset.jsonl"
    with open(output_path, "w", encoding="utf-8") as f:
        for entry in dataset:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            
    print(f"[*] Đã xuất thành công {len(dataset)} mẫu SFT vào file {output_path}")


def export_dpo_dataset():
    """
    Trích xuất dữ liệu cho Direct Preference Optimization (DPO)
    Dựa trên nút Chấp nhận (was_accepted) của người dùng để phân loại gợi ý Tốt (chosen) và Xấu (rejected).
    """
    engine = create_engine(DATABASE_URL)
    # Lấy các đề xuất cùng một thiết bị nhưng có phản hồi khác nhau
    query = """
        SELECT 
            sl.suggestion_text AS prompt,
            sl.suggestion_text AS chosen_response,
            sl.was_accepted
        FROM suggestion_logs sl
        LIMIT 1000;
    """
    
    dataset = []
    # Giả lập gom nhóm chosen và rejected
    # Trong thực tế DPO cần cặp: Prompt - Chosen (Được Accept) - Rejected (Bị từ chối)
    with engine.connect() as conn:
        result = conn.execute(text(query))
        rows = list(result.mappings())
        
        # Nhóm theo mục đích/thiết bị để tìm cặp so sánh
        for i in range(len(rows) - 1):
            row_a = rows[i]
            row_b = rows[i+1]
            # Giả lập so sánh nếu cùng prompt nhưng phản ứng khác nhau
            if row_a["was_accepted"] is True and row_b["was_accepted"] is False:
                dataset.append({
                    "prompt": row_a["prompt"],
                    "chosen": row_a["chosen_response"],
                    "rejected": row_b["chosen_response"]
                })

    output_path = "dpo_dataset.jsonl"
    with open(output_path, "w", encoding="utf-8") as f:
        for entry in dataset:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            
    print(f"[*] Đã xuất thành công {len(dataset)} mẫu DPO (Preference) vào file {output_path}")

if __name__ == "__main__":
    export_sft_dataset()
    export_dpo_dataset()
