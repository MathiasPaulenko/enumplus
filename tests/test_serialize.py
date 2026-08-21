from __future__ import annotations

import json

import pytest

from enumplus import Enum, SerializableEncoder


def test_to_json_basic() -> None:
    class Color(Enum):
        RED = ("red", {"hex": "#FF0000"})
        GREEN = ("green", {"hex": "#00FF00"})

    data = json.loads(Color.to_json())
    assert data["name"] == "Color"
    assert len(data["members"]) == 2
    red = data["members"][0]
    assert red["name"] == "RED"
    assert red["value"] == "red"
    assert red["label"] == "Red"
    assert red["metadata"] == {"hex": "#FF0000"}


def test_to_json_empty() -> None:
    class Empty(Enum):
        pass

    data = json.loads(Empty.to_json())
    assert data["name"] == "Empty"
    assert data["members"] == []


def test_from_json_valid() -> None:
    class Color(Enum):
        RED = "red"

    data = Color.from_json('{"name": "Color", "members": []}')
    assert data["name"] == "Color"
    assert data["members"] == []


def test_from_json_invalid() -> None:
    class Color(Enum):
        RED = "red"

    with pytest.raises(ValueError, match="Invalid JSON"):
        Color.from_json("not valid json")


def test_round_trip() -> None:
    class Color(Enum):
        RED = ("red", {"hex": "#FF0000"})
        GREEN = ("green", {"hex": "#00FF00"})

    original = Color.to_json()
    parsed = Color.from_json(original)
    assert parsed["name"] == "Color"
    assert parsed["members"][0]["name"] == "RED"
    assert parsed["members"][0]["value"] == "red"
    assert parsed["members"][0]["label"] == "Red"
    assert parsed["members"][0]["metadata"] == {"hex": "#FF0000"}


def test_to_json_metadata_none() -> None:
    class Color(Enum):
        RED = ("red", {"optional": None})

    data = json.loads(Color.to_json())
    assert data["members"][0]["metadata"]["optional"] is None


def test_encoder_single() -> None:
    class Color(Enum):
        RED = "red"

    assert json.dumps(Color.RED, cls=SerializableEncoder) == '"red"'


def test_encoder_list() -> None:
    class Color(Enum):
        RED = "red"
        GREEN = "green"

    assert json.dumps([Color.RED, Color.GREEN], cls=SerializableEncoder) == '["red", "green"]'


def test_encoder_dict() -> None:
    class Color(Enum):
        RED = "red"

    assert json.dumps({"c": Color.RED}, cls=SerializableEncoder) == '{"c": "red"}'


def test_encoder_without_encoder_raises() -> None:
    class Color(Enum):
        RED = "red"

    with pytest.raises(TypeError):
        json.dumps(Color.RED)


def test_encoder_non_enum_delegates() -> None:
    class Custom:
        pass

    with pytest.raises(TypeError):
        json.dumps(Custom(), cls=SerializableEncoder)


def test_from_json_non_object() -> None:
    class Color(Enum):
        RED = "red"

    with pytest.raises(TypeError, match="JSON object"):
        Color.from_json('["not", "an", "object"]')


def test_from_json_non_string_input() -> None:
    class Color(Enum):
        RED = "red"

    with pytest.raises(TypeError, match="JSON string"):
        Color.from_json(123)  # type: ignore[arg-type]
