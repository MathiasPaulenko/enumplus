"""Edge case and regression tests for enumplus.

Covers: pickle, copy, bool/int equivalence, NaN, Unicode, aliases,
_ignore_, custom _generate_next_value_, subclassing, __getattr__,
SerializableEncoder with None, empty/whitespace values, bytes values.
"""
from __future__ import annotations

import copy
import enum
import json
import pickle
from typing import Any

import pytest

from enumplus import Enum, OrderedEnum, SerializableEncoder

# ---------- Pickle ----------


class PickleColor(Enum):
    RED = "red"
    GREEN = "green"


def test_pickle_round_trip() -> None:
    data = pickle.dumps(PickleColor.RED)
    restored = pickle.loads(data)
    assert restored is PickleColor.RED


def test_pickle_all_members() -> None:
    for member in PickleColor:
        restored = pickle.loads(pickle.dumps(member))
        assert restored is member


# ---------- Copy / deepcopy ----------


def test_copy_returns_same_singleton() -> None:
    assert copy.copy(PickleColor.RED) is PickleColor.RED


def test_deepcopy_returns_same_singleton() -> None:
    assert copy.deepcopy(PickleColor.RED) is PickleColor.RED


# ---------- Bool / int equivalence ----------


class BoolIntEnum(Enum):
    ONE = 1
    ZERO = 0


def test_bool_int_eq() -> None:
    assert BoolIntEnum.ONE == True  # noqa: E712
    assert BoolIntEnum.ZERO == False  # noqa: E712
    assert BoolIntEnum.ONE == 1
    assert BoolIntEnum.ZERO == 0


def test_bool_int_hash() -> None:
    assert hash(BoolIntEnum.ONE) == hash(1)
    assert hash(BoolIntEnum.ONE) == hash(True)


def test_bool_int_contains() -> None:
    assert True in BoolIntEnum
    assert False in BoolIntEnum


def test_bool_int_from_value() -> None:
    assert BoolIntEnum.from_value(True) is BoolIntEnum.ONE
    assert BoolIntEnum.from_value(1) is BoolIntEnum.ONE
    assert BoolIntEnum.from_value(False) is BoolIntEnum.ZERO
    assert BoolIntEnum.from_value(0) is BoolIntEnum.ZERO


# ---------- NaN ----------


class NaNEnum(Enum):
    NAN = float("nan")
    ONE = 1.0


def test_nan_from_value_raises() -> None:
    with pytest.raises(ValueError):
        NaNEnum.from_value(float("nan"))


def test_nan_is_valid_false() -> None:
    assert not NaNEnum.is_valid(float("nan"))


def test_nan_not_in_enum() -> None:
    assert float("nan") not in NaNEnum


# ---------- Unicode / emoji ----------


class UnicodeEnum(Enum):
    CAFÉ = "café"
    NAÏVE = "naïve"


def test_unicode_from_value() -> None:
    assert UnicodeEnum.from_value("café") is UnicodeEnum.CAFÉ


def test_unicode_eq() -> None:
    assert UnicodeEnum.CAFÉ == "café"


def test_unicode_to_json() -> None:
    data = json.loads(UnicodeEnum.to_json())
    assert data["members"][0]["value"] == "café"


class EmojiEnum(Enum):
    SMILE = "😀"
    HEART = "❤️"


def test_emoji_from_value() -> None:
    assert EmojiEnum.from_value("😀") is EmojiEnum.SMILE


def test_emoji_to_json() -> None:
    data = json.loads(EmojiEnum.to_json())
    assert data["members"][0]["value"] == "😀"


# ---------- Aliases ----------


class AliasedEnum(Enum):
    A = 1
    B = 1  # alias for A
    C = 2


def test_alias_is_same_object() -> None:
    assert AliasedEnum.B is AliasedEnum.A  # type: ignore[comparison-overlap]


def test_alias_from_value_returns_first() -> None:
    assert AliasedEnum.from_value(1) is AliasedEnum.A


def test_alias_not_in_iteration() -> None:
    names = [m.name for m in AliasedEnum]
    assert names == ["A", "C"]


def test_alias_to_dict_excludes_alias() -> None:
    d = AliasedEnum.to_dict()
    assert "A" in d
    assert "C" in d
    assert "B" not in d


# ---------- _ignore_ ----------


class IgnoreEnum(Enum):
    _ignore_ = ["TEMP"]  # noqa: RUF012
    A = 1
    TEMP = 99


def test_ignore_excludes_member() -> None:
    assert not hasattr(IgnoreEnum, "TEMP")


def test_ignore_keeps_real_members() -> None:
    assert IgnoreEnum.A.value == 1
    assert len(list(IgnoreEnum)) == 1


# ---------- Custom _generate_next_value_ ----------


class CustomGnvEnum(Enum):
    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list[Any]
    ) -> str:
        return name.lower()

    A = enum.auto()
    B = enum.auto()


def test_custom_gnv_values() -> None:
    assert CustomGnvEnum.A.value == "a"
    assert CustomGnvEnum.B.value == "b"


# ---------- Subclass of empty enum ----------


class EmptyBase(Enum):
    pass


class SubEnum(EmptyBase):
    A = 1
    B = 2


def test_subclass_of_empty_base() -> None:
    assert len(list(SubEnum)) == 2
    assert SubEnum.A.value == 1


def test_subclass_isinstance_base() -> None:
    assert isinstance(SubEnum.A, EmptyBase)


# ---------- __getattr__ with dunder names ----------


class DunderMetaEnum(Enum):
    A = ("a", {"__custom__": "value"})


def test_getattr_blocks_dunder_meta() -> None:
    with pytest.raises(AttributeError):
        _ = DunderMetaEnum.A.__custom__


def test_dunder_meta_accessible_via_dict() -> None:
    assert DunderMetaEnum.A._metadata_["__custom__"] == "value"


# ---------- SerializableEncoder with None value ----------


class NoneValueEnum(Enum):
    NULL = None


def test_encoder_none_value() -> None:
    assert json.dumps(NoneValueEnum.NULL, cls=SerializableEncoder) == "null"


def test_to_json_none_value() -> None:
    data = json.loads(NoneValueEnum.to_json())
    assert data["members"][0]["value"] is None


# ---------- Empty / whitespace values ----------


class EmptyStringEnum(Enum):
    EMPTY = ""
    OTHER = "other"


def test_empty_string_from_value() -> None:
    assert EmptyStringEnum.from_value("") is EmptyStringEnum.EMPTY


def test_empty_string_eq() -> None:
    assert EmptyStringEnum.EMPTY == ""


def test_empty_string_contains() -> None:
    assert "" in EmptyStringEnum


def test_empty_string_case_insensitive() -> None:
    assert EmptyStringEnum.from_value("", case_insensitive=True) is EmptyStringEnum.EMPTY


class WhitespaceEnum(Enum):
    A = "  "
    B = "\t\n"


def test_whitespace_from_value() -> None:
    assert WhitespaceEnum.from_value("  ") is WhitespaceEnum.A


def test_whitespace_eq() -> None:
    assert WhitespaceEnum.A == "  "


# ---------- Bytes values ----------


class BytesEnum(Enum):
    A = b"hello"
    B = b"world"


def test_bytes_from_value() -> None:
    assert BytesEnum.from_value(b"hello") is BytesEnum.A


def test_bytes_eq() -> None:
    assert BytesEnum.A == b"hello"


def test_bytes_not_eq_str() -> None:
    assert BytesEnum.A != "hello"


def test_bytes_contains() -> None:
    assert b"hello" in BytesEnum


# ---------- Tuple values (non-metadata) ----------


class TupleEnum(Enum):
    ORIGIN = (0, 0)
    UNIT = (1, 1)


def test_tuple_from_value() -> None:
    assert TupleEnum.from_value((0, 0)) is TupleEnum.ORIGIN


def test_tuple_eq() -> None:
    assert TupleEnum.ORIGIN == (0, 0)


def test_tuple_contains() -> None:
    assert (0, 0) in TupleEnum


# ---------- None value ----------


class NoneEnum(Enum):
    NULL = None


def test_none_from_value() -> None:
    assert NoneEnum.from_value(None) is NoneEnum.NULL


def test_none_eq() -> None:
    assert NoneEnum.NULL == None  # noqa: E711


def test_none_contains() -> None:
    assert None in NoneEnum


def test_none_is_valid() -> None:
    assert NoneEnum.is_valid(None)


# ---------- Negative values ----------


class NegativeEnum(Enum):
    MINUS_ONE = -1
    MINUS_TWO = -2


def test_negative_from_value() -> None:
    assert NegativeEnum.from_value(-1) is NegativeEnum.MINUS_ONE


def test_negative_eq() -> None:
    assert NegativeEnum.MINUS_ONE == -1


# ---------- Large int ----------


class BigIntEnum(Enum):
    A = 10**100


def test_big_int_from_value() -> None:
    assert BigIntEnum.from_value(10**100) is BigIntEnum.A


def test_big_int_eq() -> None:
    assert BigIntEnum.A == 10**100


# ---------- Complex number ----------


class ComplexEnum(Enum):
    A = 1 + 2j
    B = 3 + 4j


def test_complex_from_value() -> None:
    assert ComplexEnum.from_value(1 + 2j) is ComplexEnum.A


def test_complex_eq() -> None:
    assert ComplexEnum.A == 1 + 2j


# ---------- Frozenset value ----------


class FrozenSetEnum(Enum):
    A = frozenset({1, 2})
    B = frozenset({3, 4})


def test_frozenset_from_value() -> None:
    assert FrozenSetEnum.from_value(frozenset({1, 2})) is FrozenSetEnum.A


def test_frozenset_eq() -> None:
    assert FrozenSetEnum.A == frozenset({1, 2})


# ---------- Set value (unhashable) ----------


class SetEnum(Enum):
    A = {1, 2}  # noqa: RUF012
    B = {3, 4}  # noqa: RUF012


def test_set_from_value() -> None:
    assert SetEnum.from_value({1, 2}) is SetEnum.A


def test_set_eq() -> None:
    assert SetEnum.A == {1, 2}


def test_set_hash_fallback() -> None:
    # Unhashable value should fall back to id()
    d = {SetEnum.A: 1}
    assert d[SetEnum.A] == 1


# ---------- Dict value (unhashable) ----------


class DictValueEnum(Enum):
    A = {"x": 1}  # noqa: RUF012


def test_dict_from_value() -> None:
    assert DictValueEnum.from_value({"x": 1}) is DictValueEnum.A


def test_dict_eq() -> None:
    assert DictValueEnum.A == {"x": 1}


# ---------- Float / int equivalence ----------


class FloatIntEnum(Enum):
    A = 1.0
    B = 2


def test_float_int_from_value() -> None:
    assert FloatIntEnum.from_value(1.0) is FloatIntEnum.A
    assert FloatIntEnum.from_value(1) is FloatIntEnum.A  # 1 == 1.0
    assert FloatIntEnum.from_value(2) is FloatIntEnum.B
    assert FloatIntEnum.from_value(2.0) is FloatIntEnum.B  # 2.0 == 2


# ---------- from_json with edge cases ----------


def test_from_json_empty_string_raises() -> None:
    with pytest.raises(ValueError, match="Invalid JSON"):
        Enum.from_json("")


def test_from_json_whitespace_raises() -> None:
    with pytest.raises(ValueError, match="Invalid JSON"):
        Enum.from_json("   ")


def test_from_json_null_raises() -> None:
    with pytest.raises(TypeError, match="JSON object"):
        Enum.from_json("null")


def test_from_json_number_raises() -> None:
    with pytest.raises(TypeError, match="JSON object"):
        Enum.from_json("42")


def test_from_json_boolean_raises() -> None:
    with pytest.raises(TypeError, match="JSON object"):
        Enum.from_json("true")


def test_from_json_empty_object() -> None:
    result = Enum.from_json("{}")
    assert result == {}


# ---------- OrderedEnum additional ----------


def test_ordered_enum_eq_inherited() -> None:
    class Priority(OrderedEnum):
        LOW = 1
        HIGH = 2

    # OrderedEnum inherits __eq__ from Enum (value-based)
    assert Priority.LOW == 1
    assert Priority.LOW != 99


def test_ordered_enum_hash_consistency() -> None:
    class Priority(OrderedEnum):
        LOW = 1
        HIGH = 2

    assert hash(Priority.LOW) == hash(1)


def test_ordered_enum_in_set_with_values() -> None:
    class Priority(OrderedEnum):
        LOW = 1
        HIGH = 2

    assert Priority.LOW in {1}


# ---------- Functional API ----------


def test_functional_api() -> None:
    Dynamic = Enum("Dynamic", {"A": 1, "B": 2})  # type: ignore[call-arg]
    assert Dynamic.A.value == 1
    assert Dynamic.B.value == 2
    assert len(list(Dynamic)) == 2


def test_functional_api_from_value() -> None:
    Dynamic = Enum("Dynamic", {"A": 1, "B": 2})  # type: ignore[call-arg]
    assert Dynamic.from_value(1) is Dynamic.A


# ---------- Enum with methods ----------


class MethodEnum(Enum):
    A = 1
    B = 2

    def double(self) -> int:
        return int(self._value_) * 2


def test_enum_method() -> None:
    assert MethodEnum.A.double() == 2
    assert MethodEnum.B.double() == 4


# ---------- Enum with property ----------


class PropertyEnum(Enum):
    A = ("a", {"hex": "#FF0000"})

    @property
    def upper_value(self) -> str:
        return str(self._value_).upper()


def test_enum_property() -> None:
    assert PropertyEnum.A.upper_value == "A"
