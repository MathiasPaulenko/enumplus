from __future__ import annotations

import enum as stdlib_enum
from enum import auto, unique

from enumplus import Enum


def test_isinstance_stdlib_enum() -> None:
    class Color(Enum):
        RED = "red"

    assert isinstance(Color.RED, stdlib_enum.Enum)


def test_isinstance_stdlib_enumtype() -> None:
    class Color(Enum):
        RED = "red"

    assert isinstance(Color, stdlib_enum.EnumType)


def test_access_by_name() -> None:
    class Color(Enum):
        RED = "red"
        GREEN = "green"

    assert Color["RED"] is Color.RED


def test_access_by_value() -> None:
    class Color(Enum):
        RED = "red"
        GREEN = "green"

    assert Color("red") is Color.RED  # type: ignore[call-arg]


def test_iteration_order() -> None:
    class Color(Enum):
        RED = "red"
        GREEN = "green"
        BLUE = "blue"

    assert list(Color) == [Color.RED, Color.GREEN, Color.BLUE]


def test_len() -> None:
    class Color(Enum):
        RED = "red"
        GREEN = "green"
        BLUE = "blue"

    assert len(Color) == 3


def test_members_mapping() -> None:
    class Color(Enum):
        RED = "red"
        GREEN = "green"

    assert "RED" in Color.__members__
    assert "GREEN" in Color.__members__
    assert "BLUE" not in Color.__members__


def test_unique_decorator() -> None:
    @unique
    class Color(Enum):
        RED = "red"
        GREEN = "green"

    assert Color.RED.value == "red"
    assert Color.GREEN.value == "green"


def test_auto() -> None:
    class Number(Enum):
        ONE = auto()
        TWO = auto()
        THREE = auto()

    assert Number.ONE.value == 1
    assert Number.TWO.value == 2
    assert Number.THREE.value == 3


def test_value_property() -> None:
    class Color(Enum):
        RED = "red"

    assert Color.RED.value == "red"


def test_name_property() -> None:
    class Color(Enum):
        RED = "red"

    assert Color.RED.name == "RED"


def test_repr_format() -> None:
    class Color(Enum):
        RED = "red"

    r = repr(Color.RED)
    assert "Color" in r
    assert "RED" in r
    assert "'red'" in r


def test_auto_after_metadata_tuple() -> None:
    class Number(Enum):
        ONE = (1, {"label": "One"})
        TWO = auto()
        THREE = auto()

    assert Number.ONE.value == 1  # type: ignore[comparison-overlap]
    assert Number.TWO.value == 2
    assert Number.THREE.value == 3


def test_auto_with_class_config() -> None:
    class Number(Enum):
        serialize_by_name = True
        ONE = auto()
        TWO = auto()

    assert Number.ONE.value == 1
    assert Number.TWO.value == 2
    assert Number.serialize_by_name is True
