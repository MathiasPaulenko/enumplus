from __future__ import annotations

import json
from typing import Any

from enumplus.enum import Enum


def _serialize_value(value: Any) -> Any:
    if callable(value):
        return value()
    return value


def to_json(cls: type[Enum]) -> str:
    data: dict[str, Any] = {
        "name": cls.__name__,
        "members": [
            {
                "name": member.name,
                "value": member.value,
                "label": member.label,
                "metadata": {
                    k: _serialize_value(v) for k, v in member._metadata_.items()
                },
            }
            for member in cls
        ],
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def from_json(data: str) -> dict[str, Any]:
    if not isinstance(data, str):
        raise TypeError(
            f"from_json expects a JSON string, got {type(data).__name__}"
        )
    try:
        result = json.loads(data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}") from None
    if not isinstance(result, dict):
        raise TypeError(
            f"from_json expects a JSON object, got {type(result).__name__}"
        )
    return result


class SerializableEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, Enum):
            return obj.value
        return super().default(obj)
