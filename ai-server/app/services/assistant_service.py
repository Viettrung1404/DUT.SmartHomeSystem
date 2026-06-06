from __future__ import annotations

from typing import Any

from app.schemas.assistant import ChatResponse
from app.schemas.common import ActionDraft, HomeContext
from app.schemas.nlp import ParseResponse
from app.services.nlp_pipeline import NLUPipeline
from app.services.text_normalizer import normalize_text


class AssistantService:
    def __init__(self, nlu: NLUPipeline | None = None) -> None:
        self.nlu = nlu or NLUPipeline()

    def respond(self, message: str, home_context: HomeContext | None = None) -> ChatResponse:
        parsed = self.nlu.parse(message, home_context)
        follow_up = self._follow_up_question(parsed)
        grounding = self._grounding_payload(parsed, home_context)
        reply_text = self._build_reply(message, parsed, grounding, follow_up)
        safety_flags = self._safety_flags(parsed)
        return ChatResponse(
            reply_text=reply_text,
            nlu=parsed,
            grounding=grounding,
            action_draft=parsed.action_draft,
            follow_up_question=follow_up,
            safety_flags=safety_flags,
        )

    def _build_reply(
        self,
        message: str,
        parsed: ParseResponse,
        grounding: dict[str, Any],
        follow_up: str | None,
    ) -> str:
        if parsed.intent == "greeting":
            return "Chào bạn. Mình có thể giúp kiểm tra sensor, trạng thái thiết bị hoặc hiểu lệnh điều khiển trong nhà."
        if parsed.out_of_scope:
            return (
                "Mình đang tập trung vào ngữ cảnh smart home: điều khiển thiết bị, hỏi sensor, hỏi trạng thái và hỗ trợ comfort. "
                "Yêu cầu này hiện nằm ngoài phạm vi đó."
            )
        if follow_up:
            return follow_up
        if parsed.intent == "query_sensor":
            sensor_summary = grounding.get("sensor_summary")
            if sensor_summary:
                return f"Mình đã ground được sensor liên quan. Hiện tại: {sensor_summary}."
            return "Mình hiểu bạn đang hỏi sensor, nhưng chưa thấy giá trị realtime phù hợp trong context hiện tại."
        if parsed.intent == "query_device_status":
            status_summary = grounding.get("device_status_summary")
            if status_summary:
                return f"Trạng thái mình suy ra được là: {status_summary}."
            return "Mình xác định được intent hỏi trạng thái, nhưng context hiện tại chưa đủ để trả lời chắc chắn."
        if parsed.intent == "environmental_comfort":
            comfort_type = parsed.entities.comfort_type or "comfort"
            if parsed.action_draft:
                return (
                    f"Mình hiểu đây là phản ánh về {comfort_type}. Dựa trên context hiện có, mình đã tạo action draft "
                    "để backend có thể quyết định bước điều khiển tiếp theo."
                )
            return "Mình hiểu đây là phản ánh về comfort trong nhà, nhưng chưa đủ grounding để gợi ý hành động cụ thể."
        if parsed.intent == "activate_scene":
            scene = parsed.entities.scene or "scene"
            return f"Mình đã nhận ra yêu cầu kích hoạt ngữ cảnh `{scene}` và tạo action draft ở mức orchestration."
        if parsed.intent in {"turn_off_all_devices", "lock_all_doors"}:
            return "Mình đã parse được yêu cầu phạm vi toàn nhà và tạo action draft tổng quát cho backend."
        if parsed.intent == "control_device":
            target = grounding.get("device_name") or grounding.get("room_name") or "thiết bị mục tiêu"
            action = parsed.action_draft.action if parsed.action_draft else parsed.entities.action or "dieu khien"
            return f"Mình hiểu bạn muốn `{action}` cho {target}. Action draft đã sẵn sàng để backend dùng tiếp."
        return f"Mình đã phân tích câu: `{normalize_text(message)}`."

    def _follow_up_question(self, parsed: ParseResponse) -> str | None:
        if not parsed.missing_slots:
            return None
        if "room" in parsed.missing_slots:
            return "Bạn muốn áp dụng cho phòng nào?"
        if "device" in parsed.missing_slots:
            return "Bạn muốn điều khiển thiết bị nào?"
        if "value" in parsed.missing_slots:
            return "Bạn muốn đặt giá trị cụ thể là bao nhiêu?"
        if "sensor_type" in parsed.missing_slots:
            return "Bạn muốn hỏi nhiệt độ, độ ẩm hay sensor nào khác?"
        if "scene" in parsed.missing_slots:
            return "Bạn muốn kích hoạt ngữ cảnh nào, ví dụ ngủ hay xem phim?"
        if "target" in parsed.missing_slots:
            return "Bạn muốn hỏi trạng thái của phòng hoặc thiết bị nào?"
        return "Bạn có thể nói rõ thêm mục tiêu cụ thể không?"

    def _grounding_payload(self, parsed: ParseResponse, home_context: HomeContext | None) -> dict[str, Any]:
        grounding: dict[str, Any] = {}
        entities = parsed.entities
        if entities.room_id:
            grounding["room_id"] = entities.room_id
            grounding["room_name"] = entities.room_name
        target_device = None
        if entities.device_id:
            grounding["device_id"] = entities.device_id
            grounding["device_name"] = entities.device_name
        if home_context:
            for device in home_context.devices:
                if entities.device_id and device.id == entities.device_id:
                    target_device = device
                    break
            if target_device is None and parsed.intent == "query_sensor":
                sensor_keys = {"temperature", "humidity", "gas_detected", "rain_detected", "distance_cm"}
                for device in home_context.devices:
                    same_room = not entities.room_id or device.room_id == entities.room_id
                    if same_room and any(key in device.metadata for key in sensor_keys):
                        target_device = device
                        grounding.setdefault("device_id", device.id)
                        grounding.setdefault("device_name", device.name)
                        break
            if target_device is None and parsed.intent == "query_device_status":
                for device in home_context.devices:
                    same_room = not entities.room_id or device.room_id == entities.room_id
                    same_type = not entities.device_type or normalize_text(device.type) == normalize_text(entities.device_type)
                    if same_room and same_type:
                        target_device = device
                        grounding.setdefault("device_id", device.id)
                        grounding.setdefault("device_name", device.name)
                        break
        if target_device is not None:
            grounding["device_metadata"] = target_device.metadata
            if parsed.intent == "query_sensor":
                sensor_bits = []
                for key in ("temperature", "humidity", "gas_detected", "rain_detected", "distance_cm"):
                    if key in target_device.metadata:
                        sensor_bits.append(f"{key}={target_device.metadata[key]}")
                grounding["sensor_summary"] = ", ".join(sensor_bits)
            if parsed.intent == "query_device_status":
                grounding["device_status_summary"] = (
                    f"{target_device.name} {'dang bat' if target_device.status else 'dang tat'}, "
                    f"{'online' if target_device.online_status else 'offline'}"
                )
        return grounding

    def _safety_flags(self, parsed: ParseResponse) -> list[str]:
        flags: list[str] = []
        if parsed.out_of_scope:
            flags.append("out_of_scope")
        if parsed.confidence < 0.5:
            flags.append("low_confidence")
        if parsed.missing_slots:
            flags.append("needs_clarification")
        return flags
