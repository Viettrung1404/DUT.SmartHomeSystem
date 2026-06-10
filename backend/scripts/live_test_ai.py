import json
import urllib.request
import urllib.error
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load backend environment variables
BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/smarthome")
AI_SERVER_URL = "http://localhost:8100/v1/chat"
API_KEY = "change_me"

def get_valid_user_and_home():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        # Lấy home_id và user_id hợp lệ
        result = conn.execute(text("""
            SELECT home_id, user_id 
            FROM home_users 
            LIMIT 1;
        """)).mappings().first()
        
        if result:
            return str(result["home_id"]), str(result["user_id"])
        
        # Fallback if no association found
        user_row = conn.execute(text("SELECT id FROM users LIMIT 1;")).mappings().first()
        home_row = conn.execute(text("SELECT id FROM homes LIMIT 1;")).mappings().first()
        
        uid = str(user_row["id"]) if user_row else "00000000-0000-0000-0000-000000000001"
        hid = str(home_row["id"]) if home_row else "00000000-0000-0000-0000-000000000001"
        return hid, uid

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
    except urllib.error.HTTPError as e:
        print(f"[!] HTTP Error: {e.code} - {e.read().decode('utf-8')}")
        return None
    except Exception as e:
        print(f"[!] Error connecting to AI Server: {e}")
        return None

def test_pipeline():
    home_id, user_id = get_valid_user_and_home()
    print(f"[*] Sử dụng Home ID: {home_id}")
    print(f"[*] Sử dụng User ID: {user_id}")
    print("=" * 80)
    
    # 10 Test Cases đa dạng và phức tạp
    test_cases = [
        {
            "id": 1,
            "message": "Đèn bếp đang bật hay tắt?",
            "desc": "Kiểm tra xem câu hỏi trạng thái có bị nhầm thành lệnh điều khiển bật đèn không (Lỗi trước đó)"
        },
        {
            "id": 2,
            "message": "Quạt phòng ngủ đang bật hay không?",
            "desc": "Kiểm tra xem câu hỏi trạng thái quạt có bị kích hoạt lệnh bật quạt trần không (Lỗi trước đó)"
        },
        {
            "id": 3,
            "message": "Thiết bị nào hoạt động nhiều nhất hôm qua?",
            "desc": "Kiểm tra tính toán thống kê cứng (Longest/Most Active Device) thay vì LLM bịa số liệu"
        },
        {
            "id": 4,
            "message": "Bật 2 cái đèn ở phòng khách",
            "desc": "Kiểm tra lọc theo phòng (phòng khách) và giới hạn số lượng điều khiển (target_count = 2)"
        },
        {
            "id": 5,
            "message": "Tắt tất cả các thiết bị ngoại trừ điều hòa phòng ngủ",
            "desc": "Kiểm tra lệnh tắt nhóm thiết bị đi kèm với ngoại lệ loại trừ phòng/thiết bị cụ thể"
        },
        {
            "id": 6,
            "message": "Có cảnh báo bất thường nào hôm nay không?",
            "desc": "Kiểm tra truy vấn an ninh bất thường (GUARDIAN_EVENT_QUERY)"
        },
        {
            "id": 7,
            "message": "Tại sao hệ thống đề xuất tắt đèn phòng khách?",
            "desc": "Kiểm tra khả năng đọc log và giải thích đề xuất tối ưu (SUGGESTION_EXPLAIN)"
        },
        {
            "id": 8,
            "message": "Tối qua tôi có quên tắt thiết bị nào không?",
            "desc": "Kiểm tra phát hiện quên tắt (FORGOT_OFF_QUERY) thông qua user_patterns/activity_logs"
        },
        {
            "id": 9,
            "message": "Đèn phòng khách đang bật hay tắt?",
            "desc": "Câu hỏi mồi để kiểm tra tính năng bộ nhớ ngữ cảnh ở bước tiếp theo"
        },
        {
            "id": 10,
            "message": "Thế thì tắt nó đi",
            "desc": "Kiểm tra bộ nhớ ngữ cảnh (FOLLOW_UP) - tự lấy lại thiết bị 'Đèn phòng khách' từ bước 9 để sinh lệnh tắt"
        }
    ]
    
    session_id = "test-live-session-999"
    
    for case in test_cases:
        print(f"\n[Test Case {case['id']}] {case['desc']}")
        print(f">> Câu hỏi: \"{case['message']}\"")
        
        payload = {
            "session_id": session_id,
            "user_id": user_id,
            "home_id": home_id,
            "message": case["message"],
            "timezone": "Asia/Ho_Chi_Minh"
        }
        
        res = run_chat_request(payload)
        if res:
            print(f"<- Trả lời: {res.get('answer')}")
            print(f"<- Ý định (Intent): {res.get('intent')}")
            print(f"<- Tool đã dùng: {', '.join(res.get('used_tools', [])) or 'None'}")
            
            cmds = res.get("device_commands") or []
            if not cmds and res.get("device_command"):
                cmds = [res.get("device_command")]
                
            if cmds:
                cmd_str = ", ".join([f"{c.get('device_name')} ({c.get('command')})" for c in cmds])
                print(f"<- Lệnh thiết bị sinh ra: {cmd_str}")
            else:
                print("<- Lệnh thiết bị sinh ra: Không có (Đúng)")
        else:
            print("[!] Không nhận được phản hồi từ AI Server.")
        print("-" * 80)

if __name__ == "__main__":
    test_pipeline()
