from typing import Any
from pydantic import BaseModel


class ToolResult(BaseModel):
    tool_name: str
    result_count: int
    items: list[dict[str, Any]] = []

