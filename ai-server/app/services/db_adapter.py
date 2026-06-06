from __future__ import annotations

from collections import defaultdict
from typing import Any

from sqlalchemy import create_engine, text

from app.core.settings import get_settings
from app.schemas.prediction import DBSource, InlineHistoryPoint


class SensorHistoryAdapter:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._engine = create_engine(self.settings.database_url) if self.settings.database_url else None

    def is_configured(self) -> bool:
        return self._engine is not None

    def load_inline_history(self, source: DBSource) -> list[InlineHistoryPoint]:
        if self._engine is None:
            raise RuntimeError("AI server chưa được cấu hình DATABASE_URL read-only")

        device_id = source.device_id or self._resolve_device_id(source)
        if not device_id:
            raise RuntimeError("Không resolve được device_id cho DB source")

        sql = text(
            """
            SELECT time, metric_type::text AS metric_type, value
            FROM sensor_data
            WHERE device_id = CAST(:device_id AS uuid)
              AND time >= NOW() - (:lookback_minutes * INTERVAL '1 minute')
              AND metric_type::text IN ('TEMP', 'HUMIDITY')
            ORDER BY time ASC
            """
        )
        rows = []
        with self._engine.begin() as conn:
            rows = conn.execute(
                sql,
                {"device_id": device_id, "lookback_minutes": source.lookback_minutes},
            ).mappings().all()

        grouped: dict[Any, dict[str, Any]] = defaultdict(dict)
        for row in rows:
            grouped[row["time"]][str(row["metric_type"]).upper()] = float(row["value"])

        history: list[InlineHistoryPoint] = []
        for timestamp in sorted(grouped.keys()):
            bucket = grouped[timestamp]
            if "TEMP" not in bucket or "HUMIDITY" not in bucket:
                continue
            history.append(
                InlineHistoryPoint(
                    timestamp=timestamp,
                    temperature=float(bucket["TEMP"]),
                    humidity=float(bucket["HUMIDITY"]),
                )
            )
        return history

    def _resolve_device_id(self, source: DBSource) -> str | None:
        if self._engine is None:
            return None
        queries = []
        if source.room_id:
            queries.append(
                text(
                    """
                    SELECT id
                    FROM devices
                    WHERE room_id = CAST(:room_id AS uuid)
                      AND (
                        LOWER(CAST(type AS text)) = 'sensor'
                        OR LOWER(COALESCE(config->>'kind', '')) = 'temperature_humidity'
                      )
                    ORDER BY created_at ASC
                    LIMIT 1
                    """
                )
            )
        if source.home_id:
            queries.append(
                text(
                    """
                    SELECT d.id
                    FROM devices d
                    JOIN rooms r ON r.id = d.room_id
                    WHERE r.home_id = CAST(:home_id AS uuid)
                      AND (
                        LOWER(CAST(d.type AS text)) = 'sensor'
                        OR LOWER(COALESCE(d.config->>'kind', '')) = 'temperature_humidity'
                      )
                    ORDER BY d.created_at ASC
                    LIMIT 1
                    """
                )
            )
        with self._engine.begin() as conn:
            for query in queries:
                params = {
                    "room_id": source.room_id,
                    "home_id": source.home_id,
                }
                row = conn.execute(query, params).mappings().first()
                if row and row.get("id"):
                    return str(row["id"])
        return None
