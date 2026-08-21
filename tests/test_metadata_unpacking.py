from __future__ import annotations

from enumplus import Enum


def test_tuple_value_unpacked() -> None:
    class Color(Enum):
        RED = ("red", {"hex": "#FF0000"})

    assert Color.RED.value == "red"  # type: ignore[comparison-overlap]
    assert Color.RED._metadata_ == {"hex": "#FF0000"}


def test_tuple_without_metadata() -> None:
    class Color(Enum):
        RED = "red"

    assert Color.RED.value == "red"
    assert Color.RED._metadata_ == {}


def test_tuple_not_metadata_two_elements() -> None:
    class Point(Enum):
        ORIGIN = (0, 0)

    assert Point.ORIGIN.value == (0, 0)


def test_tuple_three_elements() -> None:
    class Coord(Enum):
        A = (1, 2, 3)

    assert Coord.A.value == (1, 2, 3)


def test_dict_value_not_unpacked() -> None:
    class Config(Enum):
        DEFAULT = {"key": "val"}  # noqa: RUF012

    assert Config.DEFAULT.value == {"key": "val"}


def test_empty_metadata_dict() -> None:
    class Color(Enum):
        RED = ("red", {})  # type: ignore[var-annotated]

    assert Color.RED.value == "red"  # type: ignore[comparison-overlap]
    assert Color.RED._metadata_ == {}
