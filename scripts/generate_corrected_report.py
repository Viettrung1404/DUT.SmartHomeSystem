from __future__ import annotations

import zipfile
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "Bao_cao_PBL5_corrected_2026-06-09.docx"


def xml_text(text: str) -> str:
    return escape(text, {'"': "&quot;"})


def paragraph(text: str = "", style: str | None = None, bold: bool = False) -> str:
    ppr = ""
    if style:
        ppr = f"<w:pPr><w:pStyle w:val=\"{style}\"/></w:pPr>"
    rpr = "<w:rPr><w:b/></w:rPr>" if bold else ""
    return f"<w:p>{ppr}<w:r>{rpr}<w:t xml:space=\"preserve\">{xml_text(text)}</w:t></w:r></w:p>"


def bullet(text: str) -> str:
    return (
        "<w:p><w:pPr><w:pStyle w:val=\"ListParagraph\"/>"
        "<w:numPr><w:ilvl w:val=\"0\"/><w:numId w:val=\"1\"/></w:numPr></w:pPr>"
        f"<w:r><w:t xml:space=\"preserve\">{xml_text(text)}</w:t></w:r></w:p>"
    )


def table(rows: list[list[str]]) -> str:
    cells = []
    for row in rows:
        cell_xml = []
        for value in row:
            cell_xml.append(
                "<w:tc><w:tcPr><w:tcW w:w=\"3000\" w:type=\"dxa\"/></w:tcPr>"
                f"{paragraph(value)}</w:tc>"
            )
        cells.append(f"<w:tr>{''.join(cell_xml)}</w:tr>")
    return (
        "<w:tbl><w:tblPr><w:tblStyle w:val=\"TableGrid\"/>"
        "<w:tblW w:w=\"0\" w:type=\"auto\"/>"
        "<w:tblBorders><w:top w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"auto\"/>"
        "<w:left w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"auto\"/>"
        "<w:bottom w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"auto\"/>"
        "<w:right w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"auto\"/>"
        "<w:insideH w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"auto\"/>"
        "<w:insideV w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"auto\"/>"
        f"</w:tblBorders></w:tblPr>{''.join(cells)}</w:tbl>"
    )


def page_break() -> str:
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def document_xml(body: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <w:body>
    {body}
    <w:sectPr>
      <w:pgSz w:w="11906" w:h="16838"/>
      <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="708" w:footer="708" w:gutter="0"/>
    </w:sectPr>
  </w:body>
</w:document>
"""


CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>
"""

RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>
"""

DOCUMENT_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>
</Relationships>
"""

STYLES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:qFormat/>
    <w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="26"/></w:rPr>
    <w:pPr><w:spacing w:after="120" w:line="276" w:lineRule="auto"/><w:jc w:val="both"/></w:pPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Title">
    <w:name w:val="Title"/>
    <w:basedOn w:val="Normal"/>
    <w:qFormat/>
    <w:rPr><w:b/><w:sz w:val="34"/></w:rPr>
    <w:pPr><w:jc w:val="center"/><w:spacing w:before="240" w:after="240"/></w:pPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="heading 1"/>
    <w:basedOn w:val="Normal"/>
    <w:qFormat/>
    <w:rPr><w:b/><w:sz w:val="32"/></w:rPr>
    <w:pPr><w:outlineLvl w:val="0"/><w:spacing w:before="360" w:after="180"/></w:pPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading2">
    <w:name w:val="heading 2"/>
    <w:basedOn w:val="Normal"/>
    <w:qFormat/>
    <w:rPr><w:b/><w:sz w:val="28"/></w:rPr>
    <w:pPr><w:outlineLvl w:val="1"/><w:spacing w:before="240" w:after="120"/></w:pPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="ListParagraph">
    <w:name w:val="List Paragraph"/>
    <w:basedOn w:val="Normal"/>
    <w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr>
  </w:style>
  <w:style w:type="table" w:styleId="TableGrid">
    <w:name w:val="Table Grid"/>
    <w:tblPr><w:tblBorders><w:top w:val="single" w:sz="4" w:space="0" w:color="auto"/><w:left w:val="single" w:sz="4" w:space="0" w:color="auto"/><w:bottom w:val="single" w:sz="4" w:space="0" w:color="auto"/><w:right w:val="single" w:sz="4" w:space="0" w:color="auto"/><w:insideH w:val="single" w:sz="4" w:space="0" w:color="auto"/><w:insideV w:val="single" w:sz="4" w:space="0" w:color="auto"/></w:tblBorders></w:tblPr>
  </w:style>
</w:styles>
"""

NUMBERING = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:abstractNum w:abstractNumId="0">
    <w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="•"/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr></w:lvl>
  </w:abstractNum>
  <w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>
</w:numbering>
"""


def build_body() -> str:
    parts: list[str] = []

    parts += [
        paragraph("ĐẠI HỌC ĐÀ NẴNG", bold=True),
        paragraph("TRƯỜNG ĐẠI HỌC BÁCH KHOA", bold=True),
        paragraph("KHOA CÔNG NGHỆ THÔNG TIN", bold=True),
        paragraph("BÁO CÁO PBL5 - DỰ ÁN KỸ THUẬT MÁY TÍNH", "Title"),
        paragraph("ĐỀ TÀI", bold=True),
        paragraph("HỆ THỐNG QUẢN LÝ THIẾT BỊ TRONG NHÀ VÀ GỢI Ý THEO THÓI QUEN NGƯỜI DÙNG", "Title"),
        paragraph("Sinh viên thực hiện: Trương Lê Gia Ân, Nguyễn Phan Anh Bảo, Phan Phước Trí, Nguyễn Việt Trung"),
        paragraph("CBHD: ThS. Trần Hồ Thủy Tiên"),
        paragraph("Đà Nẵng, 06/2026"),
        page_break(),
    ]

    parts += [
        paragraph("TÓM TẮT ĐỒ ÁN", "Heading1"),
        paragraph(
            "Đồ án xây dựng một hệ thống nhà thông minh gồm phần cứng IoT, backend FastAPI, cơ sở dữ liệu PostgreSQL, "
            "ứng dụng di động React Native Expo và AI Server hỗ trợ hỏi đáp/điều khiển bằng ngôn ngữ tự nhiên. "
            "Raspberry Pi đóng vai trò gateway phần cứng, đọc dữ liệu từ cảm biến và điều khiển relay, servo, buzzer "
            "thông qua GPIO. Backend nhận dữ liệu qua MQTT, lưu trạng thái vào database, phát cập nhật thời gian thực "
            "qua WebSocket và cung cấp REST API cho mobile. AI Server là dịch vụ FastAPI riêng, sử dụng cơ chế "
            "rule-based intent routing, command parser, tool planning, truy vấn dữ liệu có giới hạn theo home_id/user_id "
            "và dùng Ollama để sinh câu trả lời khi khả dụng."
        ),
        paragraph(
            "Hệ thống hiện hỗ trợ quản lý người dùng, nhà, phòng, thiết bị, trạng thái thiết bị, tự động hóa theo thời gian, "
            "theo dõi năng lượng, sự kiện an ninh, gợi ý thói quen, nhận diện khuôn mặt bằng InsightFace/ONNXRuntime và "
            "điều khiển thiết bị qua MQTT. Các chức năng như push notification, automation phức tạp theo nhiều điều kiện "
            "và kiểm thử tải quy mô lớn được xác định là hướng phát triển tiếp theo."
        ),
        paragraph("BẢNG PHÂN CÔNG NHIỆM VỤ", "Heading1"),
        table(
            [
                ["Sinh viên", "Nhiệm vụ chính", "Kết quả"],
                ["Phan Phước Trí", "Lập trình IoT, GPIO, MQTT, cảm biến, camera và servo", "Hoàn thành phần gateway IoT và tích hợp MQTT"],
                ["Nguyễn Việt Trung", "AI Server, intent routing, command parser, tool-agent, tích hợp Ollama", "Hoàn thành trợ lý AI theo kiến trúc hiện tại"],
                ["Nguyễn Phan Anh Bảo", "Backend FastAPI, database, API nghiệp vụ, analytics/gợi ý", "Hoàn thành backend và các pipeline chính"],
                ["Trương Lê Gia Ân", "Mobile React Native Expo, UI/UX, realtime, voice/chat flow", "Hoàn thành ứng dụng di động các màn hình chính"],
            ]
        ),
        page_break(),
    ]

    parts += [
        paragraph("CHƯƠNG 1. GIỚI THIỆU", "Heading1"),
        paragraph("1.1. Thực trạng", "Heading2"),
        paragraph(
            "Các hệ thống nhà thông minh thương mại thường phụ thuộc nhiều vào nền tảng đám mây, chi phí thiết bị cao "
            "và chưa tối ưu cho tiếng Việt. Người dùng Việt Nam cần một hệ thống linh hoạt, có thể chạy cục bộ, hỗ trợ "
            "thiết bị phần cứng phổ biến như Raspberry Pi, cảm biến giá rẻ và có khả năng đồng bộ trạng thái theo thời gian thực."
        ),
        paragraph("1.2. Vấn đề cần giải quyết", "Heading2"),
        bullet("Quản lý tập trung nhà, phòng và thiết bị theo từng người dùng/thành viên trong nhà."),
        bullet("Điều khiển thiết bị vật lý qua MQTT nhưng vẫn đảm bảo mobile không giao tiếp trực tiếp với phần cứng."),
        bullet("Đồng bộ trạng thái thiết bị theo thời gian thực cho ứng dụng di động."),
        bullet("Thu thập dữ liệu hoạt động để phục vụ gợi ý thói quen và phân tích hành vi."),
        bullet("Tích hợp nhận diện khuôn mặt để hỗ trợ mở cửa tự động trong mô hình thử nghiệm."),
        bullet("Hỗ trợ hỏi đáp và điều khiển bằng ngôn ngữ tự nhiên tiếng Việt ở mức thực dụng."),
        paragraph("1.3. Giải pháp tổng quan", "Heading2"),
        paragraph(
            "Giải pháp được tổ chức thành các lớp: IoT Layer dùng Raspberry Pi và cảm biến; Communication Layer dùng MQTT, "
            "REST API và WebSocket; Backend Layer dùng FastAPI và PostgreSQL; AI Layer dùng dịch vụ AI Server riêng kết nối "
            "Ollama; Mobile Layer dùng React Native Expo. Backend là trung tâm xác thực, kiểm tra quyền truy cập, chuẩn hóa "
            "lệnh, publish MQTT và lưu dữ liệu."
        ),
    ]

    parts += [
        paragraph("CHƯƠNG 2. GIẢI PHÁP VÀ THIẾT KẾ", "Heading1"),
        paragraph("2.1. Phần cứng IoT", "Heading2"),
        paragraph(
            "Gateway IoT hiện nằm trong file Iot/iot_client.py. Chương trình đọc biến môi trường từ Iot/.env, nạp device_map.json "
            "để ánh xạ device_id với loại thiết bị, sau đó kết nối MQTT broker. Các thành phần phần cứng được hỗ trợ gồm đèn, quạt, "
            "servo cửa, servo mái che mưa, cảm biến DHT11, cảm biến siêu âm HC-SR04, cảm biến gas, cảm biến lửa, cảm biến mưa, "
            "buzzer, nút bấm và camera."
        ),
        bullet("Đèn và quạt được điều khiển qua GPIO/relay/PWM."),
        bullet("Cửa và mái che mưa được điều khiển qua servo theo góc cấu hình."),
        bullet("Cảm biến gas và flame có thể kích hoạt buzzer tại Raspberry Pi."),
        bullet("Camera hỗ trợ OpenCV, picamera và picamera2 để chụp ảnh khuôn mặt gửi về backend."),
        paragraph("2.2. Giao tiếp MQTT", "Heading2"),
        paragraph(
            "MQTT là kênh giao tiếp chính giữa backend và Raspberry Pi. Backend subscribe các topic trạng thái, năng lượng, "
            "khuôn mặt và topic legacy. Khi mobile gửi lệnh điều khiển qua REST API, backend kiểm tra quyền, cập nhật logic "
            "nghiệp vụ và publish lệnh MQTT đến thiết bị."
        ),
        bullet("device/{device_id}/command: backend gửi lệnh có dạng JSON {command, value}."),
        bullet("device/{device_id}/status: IoT client gửi trạng thái online, status, timestamp và metadata."),
        bullet("device/{device_id}/energy: thiết bị/gateway gửi chỉ số tiêu thụ điện để lưu EnergyLog."),
        bullet("home/{home_id}/face: IoT client gửi ảnh base64 cho chức năng upload, enroll hoặc verify khuôn mặt."),
        bullet("smarthome/{home_id}/status, smarthome/{home_id}/sensors, smarthome/{home_id}/commands: topic legacy để tương thích phần cứng cũ."),
        paragraph("2.3. Backend FastAPI", "Heading2"),
        paragraph(
            "Backend nằm trong thư mục backend/src. Entry point là src.main:app. Khi khởi động, backend tạo bảng nếu cần, "
            "khởi tạo MQTT client, gắn event loop cho WebSocket broadcast và khởi động automation engine. Các router chính gồm "
            "auth, users, homes, rooms, devices, automations, energy, security, suggestions, face và ai_chat."
        ),
        bullet("Auth dùng JWT access token, refresh token và bảng auth_sessions để quản lý phiên đăng nhập."),
        bullet("HomeUser quản lý quan hệ nhiều-người-dùng/nhiều-nhà và role theo từng nhà."),
        bullet("Devices API kiểm tra quyền theo home trước khi trả dữ liệu hoặc publish MQTT command."),
        bullet("Face API dùng InsightFace/ONNXRuntime, lưu gallery khuôn mặt theo home/person và hỗ trợ verify/enroll/batch enroll."),
        bullet("AI Chat API đóng vai trò proxy an toàn từ backend sang AI Server."),
        paragraph("2.4. Cơ sở dữ liệu", "Heading2"),
        paragraph(
            "Cơ sở dữ liệu chính là PostgreSQL. Docker Compose hiện cấu hình PostgreSQL 17 Alpine với database smarthome. "
            "Không có Redis trong compose hiện tại; AI memory đang dùng in-memory backend. Các bảng quan trọng gồm homes, "
            "home_users, rooms, devices, device_states, users, auth_sessions, activity_logs, sensor_data, energy_logs, "
            "security_events, user_patterns, suggestion_logs, suggestion_feedback_logs, suggestion_decision_logs, automations, "
            "automation_conditions và automation_actions."
        ),
        paragraph("2.5. WebSocket realtime", "Heading2"),
        paragraph(
            "Endpoint WebSocket là /ws/home/{home_id}. Client phải gửi access token qua query parameter. Backend giải mã token, "
            "kiểm tra user có thuộc home_id không rồi mới accept connection. ConnectionManager nhóm kết nối theo home_id và hỗ trợ "
            "broadcast device_update, security_alert và automation_triggered."
        ),
        paragraph("2.6. Automation", "Heading2"),
        paragraph(
            "Automation engine hiện dùng APScheduler kiểm tra mỗi phút. Phiên bản hiện tại thực thi ổn định nhất với điều kiện "
            "condition_type = 'time'. Các điều kiện khác như device_status, motion, energy hoặc temperature đã có hướng thiết kế "
            "trên mobile/API nhưng engine backend chưa thực thi đầy đủ. Vì vậy báo cáo xác định automation theo cảm biến/ngữ cảnh "
            "là hướng mở rộng thay vì kết quả đã hoàn thiện."
        ),
        paragraph("2.7. AI Server", "Heading2"),
        paragraph(
            "AI Server là dịch vụ FastAPI riêng trong thư mục ai-server, chạy cổng 8100. Dịch vụ cung cấp /health, /v1/chat và "
            "/v1/chat/reset. Khác với hướng fine-tune PhoBERT, phiên bản hiện tại dùng rule-based intent classifier, command parser, "
            "LLM tool planner và các tool truy vấn PostgreSQL. LLM mặc định là Ollama model qwen2.5:3b, cấu hình qua OLLAMA_URL "
            "và OLLAMA_MODEL. Nếu Ollama không sẵn sàng, hệ thống vẫn có fallback dựa trên evidence từ tool."
        ),
        bullet("query_device_status: truy vấn trạng thái thiết bị trong nhà hiện tại."),
        bullet("query_activity_logs: truy vấn lịch sử hoạt động thiết bị."),
        bullet("query_user_patterns: đọc các mẫu thói quen/anomaly đã tính."),
        bullet("query_suggestion_logs: đọc gợi ý đã sinh và phản hồi người dùng."),
        bullet("query_guardian_events/search_smart_home_records: hỗ trợ câu hỏi về cảnh báo, bất thường và dữ liệu tổng hợp."),
        paragraph("2.8. Mobile App", "Heading2"),
        paragraph(
            "Ứng dụng mobile dùng React Native Expo và Expo Router. services/api.ts xử lý base URL, token, refresh token và API calls. "
            "Các màn hình chính gồm Dashboard, Rooms, Room Detail, Device Detail, Automation, Suggestions, Assistant, Settings và Auth. "
            "use-websocket.ts kết nối /ws/home/{home_id} để cập nhật thiết bị realtime. Voice input có hook riêng, nhưng trên Expo Go "
            "có giới hạn và cần dev client/native build cho thư viện nhận dạng giọng nói."
        ),
    ]

    parts += [
        paragraph("CHƯƠNG 3. KẾT QUẢ TRIỂN KHAI", "Heading1"),
        paragraph("3.1. Kết quả backend", "Heading2"),
        bullet("Hoàn thành API xác thực, đăng ký, đăng nhập JSON, refresh token, logout và quản lý phiên."),
        bullet("Hoàn thành API quản lý nhà, phòng, thiết bị với kiểm tra quyền theo home membership."),
        bullet("Hoàn thành API điều khiển thiết bị qua REST và publish MQTT command."),
        bullet("Hoàn thành WebSocket realtime cho cập nhật trạng thái thiết bị."),
        bullet("Hoàn thành API face verify/enroll/upload và lưu ảnh khuôn mặt cuối cùng."),
        bullet("Hoàn thành API security, energy, suggestions và chat proxy sang AI Server."),
        paragraph("3.2. Kết quả IoT", "Heading2"),
        bullet("IoT client chạy all-in-one: MQTT command, sensor loop, button loop, camera capture và face send loop."),
        bullet("Hỗ trợ device_map.json để ánh xạ nhiều thiết bị vật lý với device_id trên backend."),
        bullet("Có cơ chế chạy simulation khi một số thư viện Raspberry Pi không tồn tại trên máy dev."),
        bullet("Có hỗ trợ TLS MQTT, username/password và topic legacy để tương thích phần cứng cũ."),
        paragraph("3.3. Kết quả mobile", "Heading2"),
        bullet("Dashboard hiển thị nhà, phòng, thiết bị, quick actions và AI insights."),
        bullet("Room Detail hiển thị trạng thái thiết bị, metadata gas/rain/door/speed/temperature."),
        bullet("Automation UI cho phép tạo automation theo các bước chọn điều kiện và hành động."),
        bullet("Suggestions tab hiển thị gợi ý, cho phép accept/reject."),
        bullet("Assistant tab kết nối backend chat API để hỏi đáp và điều khiển nhà thông minh."),
        paragraph("3.4. Kết quả AI và analytics", "Heading2"),
        paragraph(
            "Hệ thống analytics backend có script tính thói quen theo thời gian từ activity_logs, phát hiện anomaly dựa trên thời lượng "
            "sử dụng vượt ngưỡng và lưu vào user_patterns. Trong file run_analytics.py vẫn có helper KMeans/DBSCAN cho clustering, "
            "nhưng orchestrator hiện tại ưu tiên rule-based habit mining và anomaly detection. Do đó báo cáo không khẳng định đã "
            "huấn luyện PhoBERT hay đạt F1 score như bản cũ."
        ),
        paragraph(
            "AI Server khai thác các bảng devices, device_states, activity_logs, user_patterns, suggestion_logs và security_events "
            "để trả lời dựa trên evidence. Với câu lệnh điều khiển, AI Server xác định thiết bị và lệnh đề xuất; backend/mobile có thể "
            "dùng kết quả đó để gọi API điều khiển thiết bị."
        ),
    ]

    parts += [
        paragraph("CHƯƠNG 4. ĐÁNH GIÁ, HẠN CHẾ VÀ HƯỚNG PHÁT TRIỂN", "Heading1"),
        paragraph("4.1. Đánh giá", "Heading2"),
        paragraph(
            "Hệ thống đã hình thành kiến trúc hoàn chỉnh cho một smart home demo: phần cứng có gateway IoT, backend có phân quyền và "
            "lưu trạng thái, mobile có giao diện sử dụng được, AI Server có khả năng hỏi đáp dựa trên dữ liệu thật. Cách tách backend "
            "và AI Server giúp giảm rủi ro khi LLM lỗi, vì backend vẫn giữ vai trò điều khiển và kiểm tra quyền."
        ),
        paragraph("4.2. Hạn chế hiện tại", "Heading2"),
        bullet("Chưa có push notification thật cho sự kiện khẩn cấp; hiện chủ yếu dùng WebSocket và buzzer tại thiết bị."),
        bullet("Automation engine mới thực thi chắc chắn điều kiện thời gian, chưa hoàn thiện các điều kiện cảm biến/ngữ cảnh."),
        bullet("Chưa có Redis trong môi trường chạy hiện tại; AI memory dùng in-memory nên mất khi restart AI Server."),
        bullet("Chưa có bằng chứng benchmark cho các mục tiêu 300ms API, 1.000 thiết bị hoặc uptime 99,5%."),
        bullet("Grafana provisioning có trong repo nhưng service Grafana đang bị comment trong docker-compose."),
        bullet("Một số file code còn duplicate import/router/handler cần cleanup để giảm rủi ro bảo trì."),
        paragraph("4.3. Hướng phát triển", "Heading2"),
        bullet("Hoàn thiện push notification cho gas, flame, cửa mở bất thường, thiết bị offline và tiêu thụ điện bất thường."),
        bullet("Mở rộng automation engine cho device_status, sensor threshold, energy threshold, presence và tổ hợp nhiều điều kiện."),
        bullet("Bổ sung Redis hoặc persistent store cho AI memory nếu cần hội thoại dài hạn sau restart."),
        bullet("Thêm benchmark/load test và dashboard giám sát backend, MQTT, AI Server và database."),
        bullet("Chuẩn hóa lại báo cáo/sơ đồ ERD theo schema hiện tại và thêm sequence diagram cho lệnh điều khiển thiết bị."),
        bullet("Cải thiện bảo mật: quản lý secret, phân quyền thiết bị chi tiết hơn, chống replay MQTT và tách cấu hình production/dev."),
    ]

    parts += [
        paragraph("TÀI LIỆU THAM KHẢO", "Heading1"),
        bullet("FastAPI documentation: https://fastapi.tiangolo.com/"),
        bullet("React Native documentation: https://reactnative.dev/docs/getting-started"),
        bullet("Expo documentation: https://docs.expo.dev/"),
        bullet("MQTT Version 5.0 OASIS Standard: https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html"),
        bullet("PostgreSQL documentation: https://www.postgresql.org/docs/"),
        bullet("Ollama documentation: https://ollama.com/"),
        bullet("InsightFace project: https://github.com/deepinsight/insightface"),
        bullet("Raspberry Pi documentation: https://www.raspberrypi.com/documentation/"),
    ]

    parts += [
        paragraph("PHỤ LỤC. ĐỐI CHIẾU VỚI BÁO CÁO CŨ", "Heading1"),
        table(
            [
                ["Nội dung báo cáo cũ", "Tình trạng trong code hiện tại", "Cách sửa trong báo cáo mới"],
                ["PhoBERT fine-tuned, NER + CRF, F1 94.6%", "Không có dependency/model tương ứng trong repo", "Mô tả AI Server rule/tool-agent + Ollama"],
                ["PostgreSQL + Redis", "Compose chỉ có PostgreSQL; memory AI là in-memory", "Ghi PostgreSQL, Redis là hướng mở rộng"],
                ["Push notification khi gas/cháy", "Chưa thấy Expo push notification; có WebSocket/buzzer", "Đưa vào hạn chế/hướng phát triển"],
                ["Automation theo cảm biến/ngữ cảnh đầy đủ", "Engine hiện chủ yếu condition_type=time", "Ghi rõ giới hạn hiện tại"],
                ["Grafana vận hành", "Provisioning có, service bị comment", "Ghi là tùy chọn/chưa bật mặc định"],
                ["Chỉ số tải/uptime cụ thể", "Chưa có benchmark chứng minh", "Chuyển thành mục tiêu cần kiểm thử"],
            ]
        ),
    ]

    return "\n".join(parts)


def write_docx() -> None:
    now = date.today().isoformat()
    core = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
 xmlns:dc="http://purl.org/dc/elements/1.1/"
 xmlns:dcterms="http://purl.org/dc/terms/"
 xmlns:dcmitype="http://purl.org/dc/dcmitype/"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>Báo cáo PBL5 Smart Home - bản chỉnh theo code hiện tại</dc:title>
  <dc:creator>Codex</dc:creator>
  <cp:lastModifiedBy>Codex</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{now}T00:00:00Z</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{now}T00:00:00Z</dcterms:modified>
</cp:coreProperties>
"""
    app = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
 xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Codex</Application>
</Properties>
"""
    with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED) as docx:
        docx.writestr("[Content_Types].xml", CONTENT_TYPES)
        docx.writestr("_rels/.rels", RELS)
        docx.writestr("word/_rels/document.xml.rels", DOCUMENT_RELS)
        docx.writestr("word/document.xml", document_xml(build_body()))
        docx.writestr("word/styles.xml", STYLES)
        docx.writestr("word/numbering.xml", NUMBERING)
        docx.writestr("docProps/core.xml", core)
        docx.writestr("docProps/app.xml", app)


if __name__ == "__main__":
    write_docx()
    print(OUTPUT)
