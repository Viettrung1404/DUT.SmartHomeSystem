import json
import urllib.request
import urllib.error
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Reconfigure encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/smarthome")
AI_SERVER_URL = "http://localhost:8100/v1/chat"
API_KEY = "change_me"

def get_valid_user_and_home():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT home_id, user_id 
            FROM home_users 
            LIMIT 1;
        """)).mappings().first()
        if result:
            return str(result["home_id"]), str(result["user_id"])
        return "00000000-0000-0000-0000-000000000001", "00000000-0000-0000-0000-000000000001"

def run_chat_request(payload):
    req = urllib.request.Request(
        AI_SERVER_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "X-API-Key": API_KEY
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print(f"[!] Lỗi: {e}")
        return None

def test_consecutive_memory():
    home_id, user_id = get_valid_user_and_home()
    session_id = "test-consecutive-session-777"
    
    # 4 câu hỏi liên tiếp để kiểm thử chuỗi lưu trữ memory
    steps = [
        {
            "step": 1,
            "message": "Đèn phòng khách đang bật hay tắt?",
            "desc": "Bước 1: Thiết lập chủ đề và thiết bị đích ban đầu (Đèn phòng khách)"
        },
        {
            "step": 2,
            "message": "Thế còn quạt ở đó thì sao?",
            "desc": "Bước 2: Thay đổi thiết bị (Đèn -> Quạt) nhưng giữ nguyên phòng (phòng khách) từ ngữ cảnh cũ"
        },
        {
            "step": 3,
            "message": "Bật nó lên",
            "desc": "Bước 3: Phát lệnh điều khiển bật bằng đại từ thế thân 'nó' (phân giải thành Quạt phòng khách)"
        },
        {
            "step": 4,
            "message": "Hôm qua nó hoạt động bao lâu?",
            "desc": "Bước 4: Hỏi lịch sử chạy của thiết bị đang nói đến (Quạt phòng khách) cho mốc thời gian hôm qua"
        }
    ]
    
    print("=" * 80)
    print("[*] BẮT ĐẦU KIỂM THỬ CHUỖI 4 CÂU HỎI LIÊN TIẾP VỚI BỘ NHỚ NGỮ CẢNH")
    print("=" * 80)
    
    for s in steps:
        print(f"\n[BƯỚC {s['step']}] {s['desc']}")
        print(f">> Người dùng: \"{s['message']}\"")
        
        payload = {
            "session_id": session_id,
            "user_id": user_id,
            "home_id": home_id,
            "message": s["message"],
            "timezone": "Asia/Ho_Chi_Minh"
        }
        
        res = run_chat_request(payload)
        if res:
            print(f"<- Trợ lý AI: {res.get('answer')}")
            print(f"<- Ý định thực tế (Intent): {res.get('intent')}")
            print(f"<- Tool đã chạy: {', '.join(res.get('used_tools', [])) or 'None'}")
            
            cmds = res.get("device_commands") or []
            if not cmds and res.get("device_command"):
                cmds = [res.get("device_command")]
            if cmds:
                cmd_str = ", ".join([f"{c.get('device_name')} ({c.get('command')})" for c in cmds])
                print(f"<- Lệnh kích hoạt: {cmd_str}")
        else:
            print("[!] Không nhận được phản hồi.")
        print("-" * 80)

if __name__ == "__main__":
    test_consecutive_memory()
