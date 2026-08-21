from __future__ import annotations

import json
from typing import Any

from enumplus.enum import Enum

__all__ = ["SerializableEncoder", "from_json", "to_json"]


def _serialize_value(value: Any, *, evaluate_callable: bool = False) -> Any:
    """Serialize a single metadata value.

    Only callables in the ``label`` key are evaluated; all other values are
    returned as-is so that function references or class objects stored in
    metadata are not accidentally invoked.
    """
    if evaluate_callable and callable(value):
        return value()
    return value


def to_json(cls: type[Enum]) -> str:
    """Serialize an enum class to a pretty-printed JSON string.

    The output structure is::

        {
          "name": "ClassName",
          "members": [
            {"name": "MEMBER", "value": ..., "label": ..., "metadata": {...}}
          ]
        }
    """
    data: dict[str, Any] = {
        "name": cls.__name__,
        "members": [
            {
                "name": member.name,
                "value": member.value,
                "label": member.label,
                "metadata": {
                    k: _serialize_value(v, evaluate_callable=(k == "label"))
                    for k, v in member._metadata_.items()
                },
            }
            for member in cls
        ],
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def from_json(data: str) -> dict[str, Any]:
    """Parse a JSON string into a dictionary.

    Raises:
        TypeError: If ``data`` is not a string or the parsed JSON is not an object.
        ValueError: If ``data`` is not valid JSON.
    """
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
    """JSON encoder that serializes enumplus members to their values.

    Usage::

        json.dumps(Color.RED, cls=SerializableEncoder)
    """

    def default(self, obj: Any) -> Any:
        if isinstance(obj, Enum):
            return obj.value
        return super().default(obj)
