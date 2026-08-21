from __future__ import annotations

import json
from typing import Any, cast

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
    try:
        return cast(dict[str, Any], json.loads(data))
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}") from None


class SerializableEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        from enumplus.enum import Enum

        if isinstance(obj, Enum):
            return obj.value
        return super().default(obj)
