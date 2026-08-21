from __future__ import annotations

import json
from typing import Any, cast

from enumplus.enum import Enum


def to_json(cls: type[Enum]) -> str:
    data: dict[str, Any] = {
        "name": cls.__name__,
        "members": [
            {
                "name": member.name,
                "value": member.value,
                "label": member.label,
                "metadata": member._metadata_,
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
