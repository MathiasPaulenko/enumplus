from __future__ import annotations

import pytest

from enumplus import OrderedEnum


def test_ordered_lt() -> None:
    class Priority(OrderedEnum):
        LOW = 1
        MEDIUM = 2
        HIGH = 3

    assert Priority.LOW < Priority.HIGH


def test_ordered_gt() -> None:
    class Priority(OrderedEnum):
        LOW = 1
        MEDIUM = 2
        HIGH = 3

    assert Priority.HIGH > Priority.LOW


def test_ordered_le_ge() -> None:
    class Priority(OrderedEnum):
        LOW = 1
        MEDIUM = 2
        HIGH = 3

    assert Priority.LOW <= Priority.LOW
    assert Priority.LOW <= Priority.MEDIUM
    assert Priority.HIGH >= Priority.HIGH
    assert Priority.HIGH >= Priority.MEDIUM


def test_ordered_sorted() -> None:
    class Priority(OrderedEnum):
        LOW = 1
        MEDIUM = 2
        HIGH = 3

    assert sorted([Priority.HIGH, Priority.LOW, Priority.MEDIUM]) == [
        Priority.LOW,
        Priority.MEDIUM,
        Priority.HIGH,
    ]


def test_ordered_min_max() -> None:
    class Priority(OrderedEnum):
        LOW = 1
        MEDIUM = 2
        HIGH = 3

    assert min(Priority) is Priority.LOW
    assert max(Priority) is Priority.HIGH


def test_ordered_different_enum_raises() -> None:
    class Priority(OrderedEnum):
        LOW = 1
        HIGH = 3

    class Status(OrderedEnum):
        ACTIVE = "active"

    with pytest.raises(TypeError):
        _ = Priority.LOW < Status.ACTIVE


def test_ordered_non_member_raises() -> None:
    class Priority(OrderedEnum):
        LOW = 1
        HIGH = 3

    with pytest.raises(TypeError):
        _ = Priority.LOW < "red"
