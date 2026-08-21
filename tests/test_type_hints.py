from __future__ import annotations

from enumplus import Enum


def test_typed_metadata() -> None:
    class Color(Enum):
        RED = ("red", {"hex": "#FF0000"})

    assert Color.RED.hex == "#FF0000"


def test_typed_metadata_int() -> None:
    class Priority(Enum):
        HIGH = (1, {"weight": 10})

    assert Priority.HIGH.weight == 10
    assert isinstance(Priority.HIGH.weight, int)
