from __future__ import annotations

import enum

import pytest

from enumplus import Enum


def test_basic_enum_value() -> None:
    class Color(Enum):
        RED = "red"
        GREEN = "green"

    assert Color.RED.value == "red"


def test_basic_enum_name() -> None:
    class Color(Enum):
        RED = "red"
        GREEN = "green"

    assert Color.RED.name == "RED"


def test_basic_access_by_value() -> None:
    class Color(Enum):
        RED = "red"
        GREEN = "green"

    assert Color("red") is Color.RED  # type: ignore[call-arg]


def test_basic_access_by_name() -> None:
    class Color(Enum):
        RED = "red"
        GREEN = "green"

    assert Color["RED"] is Color.RED


def test_basic_iteration() -> None:
    class Color(Enum):
        RED = "red"
        GREEN = "green"

    assert list(Color) == [Color.RED, Color.GREEN]


def test_isinstance_stdlib() -> None:
    class Color(Enum):
        RED = "red"
        GREEN = "green"

    assert isinstance(Color.RED, enum.Enum)
    assert isinstance(Color, enum.EnumType)


def test_label_explicit() -> None:
    class Color(Enum):
        RED = ("red", {"label": "Red"})

    assert Color.RED.label == "Red"


def test_label_auto() -> None:
    class Color(Enum):
        RED = "red"

    assert Color.RED.label == "Red"


def test_label_none_falls_back() -> None:
    class Color(Enum):
        RED = ("red", {"label": None})

    assert Color.RED.label == "Red"


def test_label_empty_falls_back() -> None:
    class Color(Enum):
        RED = ("red", {"label": ""})

    assert Color.RED.label == "Red"


def test_label_with_spaces() -> None:
    class Status(Enum):
        IN_PROGRESS = ("in_progress", {"label": "In Progress"})

    assert Status.IN_PROGRESS.label == "In Progress"


def test_label_underscore_without_label() -> None:
    class Status(Enum):
        IN_PROGRESS = "in_progress"

    assert Status.IN_PROGRESS.label == "In_Progress"


def test_metadata_by_attribute() -> None:
    class Color(Enum):
        RED = ("red", {"hex": "#FF0000", "description": "Pure red"})

    assert Color.RED.hex == "#FF0000"
    assert Color.RED.description == "Pure red"


def test_metadata_as_dict() -> None:
    class Color(Enum):
        RED = ("red", {"hex": "#FF0000"})

    assert Color.RED.metadata == {"hex": "#FF0000"}


def test_metadata_empty() -> None:
    class Color(Enum):
        RED = "red"

    assert Color.RED.metadata == {}


def test_metadata_preserves_types() -> None:
    class Priority(Enum):
        HIGH = (1, {"weight": 10})

    assert isinstance(Priority.HIGH.weight, int)


def test_metadata_callable_not_invoked() -> None:
    def func() -> str:
        return "called"

    class Color(Enum):
        RED = ("red", {"cb": func})

    assert callable(Color.RED.cb)
    assert Color.RED.cb() == "called"


def test_attribute_error_missing() -> None:
    class Color(Enum):
        RED = ("red", {"hex": "#FF0000"})

    with pytest.raises(AttributeError, match="has no attribute 'nonexistent'"):
        _ = Color.RED.nonexistent


def test_metadata_none_value() -> None:
    class Color(Enum):
        RED = ("red", {"optional": None})

    assert Color.RED.optional is None


def test_str_returns_label() -> None:
    class Color(Enum):
        RED = ("red", {"label": "Red"})

    assert str(Color.RED) == "Red"


def test_str_auto_label() -> None:
    class Color(Enum):
        RED = "red"

    assert str(Color.RED) == "Red"


def test_str_custom_label() -> None:
    class Status(Enum):
        IN_PROGRESS = ("in_progress", {"label": "In Progress"})

    assert str(Status.IN_PROGRESS) == "In Progress"


def test_repr_string_value() -> None:
    class Color(Enum):
        RED = "red"

    assert repr(Color.RED) == "<Color.RED: 'red'>"


def test_repr_int_value() -> None:
    class Priority(Enum):
        HIGH = 1

    assert repr(Priority.HIGH) == "<Priority.HIGH: 1>"


def test_eq_with_value() -> None:
    class Color(Enum):
        RED = "red"

    assert Color.RED == "red"


def test_eq_with_member_same() -> None:
    class Color(Enum):
        RED = "red"

    assert Color.RED == Color.RED


def test_eq_with_member_different() -> None:
    class Color(Enum):
        RED = "red"
        GREEN = "green"

    assert Color.RED != Color.GREEN


def test_eq_with_name_not_value() -> None:
    class Color(Enum):
        RED = "red"

    assert Color.RED != "RED"


def test_eq_incompatible_type() -> None:
    class Color(Enum):
        RED = "red"

    assert Color.RED != 42


def test_eq_none() -> None:
    class Color(Enum):
        RED = "red"

    assert Color.RED != None


def test_hash_consistency() -> None:
    class Color(Enum):
        RED = "red"

    assert hash(Color.RED) == hash("red")


def test_member_in_dict_by_value() -> None:
    class Color(Enum):
        RED = "red"

    d: dict[str, int] = {"red": 1}
    assert Color.RED in d
    assert d[Color.RED] == 1  # type: ignore[index]


def test_member_in_set() -> None:
    class Color(Enum):
        RED = "red"

    assert Color.RED in {"red"}


def test_contains_value() -> None:
    class Color(Enum):
        RED = "red"
        GREEN = "green"

    assert "red" in Color
    assert "blue" not in Color


def test_contains_member() -> None:
    class Color(Enum):
        RED = "red"

    assert Color.RED in Color


def test_contains_other_enum_member() -> None:
    class Color(Enum):
        RED = "red"

    class Status(Enum):
        ACTIVE = "active"

    assert Color.RED not in Status


def test_contains_incompatible() -> None:
    class Color(Enum):
        RED = "red"

    assert 42 not in Color
    assert None not in Color


def test_eq_with_unhashable_value() -> None:
    class Container(Enum):
        LIST = [1, 2]  # noqa: RUF012

    assert Container.LIST == [1, 2]
    assert Container.LIST != [1, 3]
    assert Container.LIST != (1, 2)


def test_hash_with_unhashable_value() -> None:
    class Container(Enum):
        LIST = [1, 2]  # noqa: RUF012

    # Unhashable values should fall back to id(), so the member itself is usable
    # as a dict key.
    d = {Container.LIST: 1}
    assert d[Container.LIST] == 1


def test_contains_unhashable_value() -> None:
    class Container(Enum):
        LIST = [1, 2]  # noqa: RUF012

    assert [1, 2] in Container
    assert [1, 3] not in Container


def test_from_value_unhashable_value() -> None:
    class Container(Enum):
        LIST = [1, 2]  # noqa: RUF012

    assert Container.from_value([1, 2]) is Container.LIST


def test_is_valid_unhashable_value() -> None:
    class Container(Enum):
        LIST = [1, 2]  # noqa: RUF012

    assert Container.is_valid([1, 2]) is True
    assert Container.is_valid([1, 3]) is False


def test_choices_basic() -> None:
    class Color(Enum):
        RED = ("red", {"label": "Red"})
        GREEN = ("green", {"label": "Green"})

    assert Color.choices() == [("red", "Red"), ("green", "Green")]


def test_choices_empty() -> None:
    class Empty(Enum):
        pass

    assert Empty.choices() == []


def test_choices_order() -> None:
    class Status(Enum):
        PENDING = "pending"
        ACTIVE = "active"
        CLOSED = "closed"

    values = [v for v, _ in Status.choices()]
    assert values == ["pending", "active", "closed"]


def test_choices_int_values() -> None:
    class Priority(Enum):
        HIGH = 1
        LOW = 2

    assert Priority.choices() == [(1, "High"), (2, "Low")]


def test_choices_custom_labels() -> None:
    class Status(Enum):
        PENDING = ("pending", {"label": "Waiting Approval"})

    assert Status.choices() == [("pending", "Waiting Approval")]


def test_from_value_exists() -> None:
    class Color(Enum):
        RED = "red"
        GREEN = "green"

    assert Color.from_value("red") is Color.RED


def test_from_value_not_exists() -> None:
    class Color(Enum):
        RED = "red"

    with pytest.raises(ValueError, match="is not a valid Color value"):
        Color.from_value("blue")


def test_from_value_default_none() -> None:
    class Color(Enum):
        RED = "red"

    assert Color.from_value("blue", default=None) is None


def test_from_value_default_member() -> None:
    class Color(Enum):
        RED = "red"
        GREEN = "green"

    assert Color.from_value("blue", default=Color.RED) is Color.RED


def test_from_value_none_raises() -> None:
    class Color(Enum):
        RED = "red"

    with pytest.raises(ValueError, match="is not a valid Color value"):
        Color.from_value(None)


def test_from_value_wrong_type() -> None:
    class Color(Enum):
        RED = "red"

    with pytest.raises(ValueError, match="is not a valid Color value"):
        Color.from_value(42)


def test_from_name_exists() -> None:
    class Color(Enum):
        RED = "red"
        GREEN = "green"

    assert Color.from_name("RED") is Color.RED


def test_from_name_not_exists() -> None:
    class Color(Enum):
        RED = "red"

    with pytest.raises(KeyError, match="is not a valid Color name"):
        Color.from_name("BLUE")


def test_from_name_case_sensitive() -> None:
    class Color(Enum):
        RED = "red"

    with pytest.raises(KeyError, match="is not a valid Color name"):
        Color.from_name("red")


def test_from_name_default() -> None:
    class Color(Enum):
        RED = "red"

    assert Color.from_name("BLUE", default=None) is None


def test_is_valid_exists() -> None:
    class Color(Enum):
        RED = "red"

    assert Color.is_valid("red") is True


def test_is_valid_not_exists() -> None:
    class Color(Enum):
        RED = "red"

    assert Color.is_valid("blue") is False


def test_is_valid_member() -> None:
    class Color(Enum):
        RED = "red"

    assert Color.is_valid(Color.RED) is True


def test_is_valid_none() -> None:
    class Color(Enum):
        RED = "red"

    assert Color.is_valid(None) is False


def test_is_valid_wrong_type() -> None:
    class Color(Enum):
        RED = "red"

    assert Color.is_valid(42) is False


def test_validate_exists() -> None:
    class Color(Enum):
        RED = "red"

    assert Color.validate("red") is Color.RED


def test_validate_raises() -> None:
    class Color(Enum):
        RED = "red"

    with pytest.raises(ValueError, match="is not a valid Color value"):
        Color.validate("blue")


def test_values() -> None:
    class Color(Enum):
        RED = "red"
        GREEN = "green"

    assert Color.values() == ["red", "green"]


def test_names() -> None:
    class Color(Enum):
        RED = "red"
        GREEN = "green"

    assert Color.names() == ["RED", "GREEN"]


def test_labels() -> None:
    class Color(Enum):
        RED = ("red", {"label": "Red"})
        GREEN = ("green", {"label": "Green"})

    assert Color.labels() == ["Red", "Green"]


def test_empty_enum_values_names_labels() -> None:
    class Empty(Enum):
        pass

    assert Empty.values() == []
    assert Empty.names() == []
    assert Empty.labels() == []


def test_int_values() -> None:
    class Priority(Enum):
        HIGH = 1
        LOW = 2

    assert Priority.values() == [1, 2]


def test_filter_single() -> None:
    class Color(Enum):
        RED = ("red", {"hex": "#FF0000"})
        GREEN = ("green", {"hex": "#00FF00"})

    assert Color.filter(hex="#FF0000") == [Color.RED]


def test_filter_multiple_and() -> None:
    class Color(Enum):
        RED = ("red", {"hex": "#FF0000", "category": "warm"})
        GREEN = ("green", {"hex": "#00FF00", "category": "cool"})

    assert Color.filter(hex="#FF0000", category="warm") == [Color.RED]


def test_filter_no_results() -> None:
    class Color(Enum):
        RED = ("red", {"hex": "#FF0000"})
        GREEN = ("green", {"hex": "#00FF00"})

    assert Color.filter(hex="#000000") == []


def test_filter_no_kwargs() -> None:
    class Color(Enum):
        RED = "red"
        GREEN = "green"

    assert Color.filter() == [Color.RED, Color.GREEN]


def test_filter_key_not_in_metadata() -> None:
    class Color(Enum):
        RED = ("red", {"hex": "#FF0000"})
        GREEN = ("green", {"hex": "#00FF00"})

    assert Color.filter(nonexistent=True) == []


def test_filter_none_value() -> None:
    class Color(Enum):
        RED = ("red", {"optional": None})
        GREEN = ("green", {"optional": "yes"})

    assert Color.filter(optional=None) == [Color.RED]
