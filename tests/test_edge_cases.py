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
from enum import auto
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


# ---------- SerializableEncoder with OrderedEnum ----------


def test_encoder_ordered_enum() -> None:
    class Priority(OrderedEnum):
        LOW = 1
        HIGH = 2

    assert json.dumps(Priority.LOW, cls=SerializableEncoder) == "1"


# ---------- to_dict with empty enum ----------


def test_to_dict_empty_enum() -> None:
    class Empty(Enum):
        pass

    d = Empty.to_dict()
    assert d == {}


# ---------- filter with multiple results ----------


def test_filter_multiple_results() -> None:
    class Color(Enum):
        RED = ("red", {"category": "warm"})
        ORANGE = ("orange", {"category": "warm"})
        BLUE = ("blue", {"category": "cool"})

    result = Color.filter(category="warm")
    assert result == [Color.RED, Color.ORANGE]


# ---------- from_value with enum member as input ----------


def test_from_value_with_member() -> None:
    class Color(Enum):
        RED = "red"
        GREEN = "green"

    assert Color.from_value(Color.RED) is Color.RED


# ---------- validate with enum member ----------


def test_validate_with_member() -> None:
    class Color(Enum):
        RED = "red"

    assert Color.validate(Color.RED) is Color.RED


# ---------- get with enum member ----------


def test_get_with_member() -> None:
    class Color(Enum):
        RED = "red"

    assert Color.get(Color.RED) is Color.RED


# ---------- eq between different enum classes with same value ----------


def test_eq_different_enum_same_value() -> None:
    class Color(Enum):
        RED = "red"

    class Status(Enum):
        RED = "red"

    assert Color.RED != Status.RED


# ---------- from_value case_insensitive with mixed type values ----------


def test_from_value_case_insensitive_mixed_types() -> None:
    class Mixed(Enum):
        A = 1
        B = "b"

    assert Mixed.from_value(1, case_insensitive=True) is Mixed.A
    assert Mixed.from_value("B", case_insensitive=True) is Mixed.B


# ---------- OrderedEnum eq with different enum type ----------


def test_ordered_enum_eq_different_type() -> None:
    class Priority(OrderedEnum):
        LOW = 1

    class Status(OrderedEnum):
        LOW = 1

    assert Priority.LOW != Status.LOW


# ---------- map with unhashable member values ----------


def test_map_with_unhashable_values() -> None:
    class Container(Enum):
        LIST = [1, 2]  # noqa: RUF012

    result = Container.map({Container.LIST: "value"})
    assert result == {"LIST": "value"}


# ---------- from_name case_insensitive with unicode ----------


def test_from_name_case_insensitive_unicode() -> None:
    class UnicodeEnum(Enum):
        CAFÉ = "café"
        NAÏVE = "naïve"

    assert UnicodeEnum.from_name("café", case_insensitive=True) is UnicodeEnum.CAFÉ
    assert UnicodeEnum.from_name("NAÏVE", case_insensitive=True) is UnicodeEnum.NAÏVE


# ---------- to_json with callable label metadata consistency ----------


def test_to_json_callable_label_metadata_consistency() -> None:
    class Color(Enum):
        RED = ("red", {"label": lambda: "Rojo"})

    data = json.loads(Color.to_json())
    assert data["members"][0]["label"] == data["members"][0]["metadata"]["label"]


# ---------- Cross-enum false positive prevention ----------


def test_is_valid_rejects_foreign_enum_member() -> None:
    class A(Enum):
        X = "x"

    class B(Enum):
        X = "x"

    assert not A.is_valid(B.X)


def test_from_value_rejects_foreign_enum_member() -> None:
    class A(Enum):
        X = "x"

    class B(Enum):
        X = "x"

    with pytest.raises(ValueError, match="is not a valid A value"):
        A.from_value(B.X)


def test_from_value_foreign_enum_with_default() -> None:
    class A(Enum):
        X = "x"

    class B(Enum):
        X = "x"

    assert A.from_value(B.X, default=None) is None


def test_get_rejects_foreign_enum_member() -> None:
    class A(Enum):
        X = "x"

    class B(Enum):
        X = "x"

    assert A.get(B.X) is None


def test_is_valid_accepts_own_enum_member() -> None:
    class A(Enum):
        X = "x"

    assert A.is_valid(A.X)


def test_from_value_accepts_own_enum_member() -> None:
    class A(Enum):
        X = "x"

    assert A.from_value(A.X) is A.X


def test_contains_rejects_foreign_enum_member() -> None:
    class A(Enum):
        X = "x"

    class B(Enum):
        X = "x"

    assert B.X not in A


def test_contains_accepts_own_enum_member() -> None:
    class A(Enum):
        X = "x"

    assert A.X in A


# ---------- Label falsiness (Bug 7 regression) ----------


def test_label_zero_respected() -> None:
    class FalsyLabel(Enum):
        ZERO = ("zero", {"label": 0})

    assert FalsyLabel.ZERO.label == "0"


def test_label_empty_string_respected() -> None:
    class FalsyLabel(Enum):
        EMPTY = ("empty", {"label": ""})

    assert FalsyLabel.EMPTY.label == ""


def test_label_false_respected() -> None:
    class FalsyLabel(Enum):
        FALSE = ("false", {"label": False})

    assert FalsyLabel.FALSE.label == "False"


def test_label_none_falls_back() -> None:
    class FalsyLabel(Enum):
        A = ("a", {"label": None})

    assert FalsyLabel.A.label == "A"


def test_label_missing_falls_back() -> None:
    class NoLabel(Enum):
        A = "a"

    assert NoLabel.A.label == "A"


# ---------- _safe_equal with raising __eq__ (Bug 8 regression) ----------


def test_eq_with_raising_eq_returns_false() -> None:
    class BadEq:
        def __eq__(self, other: object) -> bool:
            raise RuntimeError("boom")

    class C(Enum):
        A = "a"

    assert C.A != BadEq()


def test_contains_with_raising_eq() -> None:
    class BadEq:
        def __eq__(self, other: object) -> bool:
            raise RuntimeError("boom")

    class C(Enum):
        A = "a"

    assert BadEq() not in C


def test_from_value_with_raising_eq() -> None:
    class BadEq:
        def __eq__(self, other: object) -> bool:
            raise RuntimeError("boom")

    class C(Enum):
        A = "a"

    with pytest.raises(ValueError, match="is not a valid C value"):
        C.from_value(BadEq())


def test_is_valid_with_raising_eq() -> None:
    class BadEq:
        def __eq__(self, other: object) -> bool:
            raise RuntimeError("boom")

    class C(Enum):
        A = "a"

    assert not C.is_valid(BadEq())


# ---------- Additional missing coverage ----------


def test_from_name_empty_string_raises() -> None:
    class C(Enum):
        A = "a"

    with pytest.raises(KeyError, match="is not a valid C name"):
        C.from_name("")


def test_from_name_empty_string_with_default() -> None:
    class C(Enum):
        A = "a"

    assert C.from_name("", default=None) is None


def test_from_name_case_insensitive_with_default() -> None:
    class C(Enum):
        A = "a"

    assert C.from_name("nonexistent", default=None, case_insensitive=True) is None


def test_from_value_case_insensitive_none_raises() -> None:
    class C(Enum):
        A = "a"

    with pytest.raises(ValueError, match="is not a valid C value"):
        C.from_value(None, case_insensitive=True)


def test_ordered_enum_empty_get_initial_raises() -> None:
    class Empty(OrderedEnum):
        pass

    with pytest.raises(ValueError, match="has no members"):
        Empty.get_initial()


def test_ordered_enum_empty_get_final_raises() -> None:
    class Empty(OrderedEnum):
        pass

    with pytest.raises(ValueError, match="has no members"):
        Empty.get_final()


def test_to_dict_with_callable_non_label_metadata_preserved() -> None:
    class C(Enum):
        A = ("a", {"cb": lambda: "called"})

    d = C.to_dict()
    assert callable(d["A"]["metadata"]["cb"])


def test_filter_with_underscore_key() -> None:
    class C(Enum):
        A = ("a", {"_private": "value"})
        B = "b"

    result = C.filter(_private="value")
    assert result == [C.A]


def test_eq_with_object_returning_non_bool_truthy() -> None:
    class TruthyEq:
        def __eq__(self, other: object) -> Any:
            return [True, False]

    class C(Enum):
        A = "a"

    assert C.A == TruthyEq()


def test_eq_with_object_returning_non_bool_falsy() -> None:
    class FalsyEq:
        def __eq__(self, other: object) -> Any:
            return []

    class C(Enum):
        A = "a"

    assert C.A != FalsyEq()


def test_repr_with_metadata() -> None:
    class C(Enum):
        A = ("a", {"hex": "#FF0000"})

    r = repr(C.A)
    assert "C.A" in r
    assert "'a'" in r


def test_str_with_falsy_label_zero() -> None:
    class C(Enum):
        ZERO = ("zero", {"label": 0})

    assert str(C.ZERO) == "0"


def test_str_with_falsy_label_empty_string() -> None:
    class C(Enum):
        EMPTY = ("empty", {"label": ""})

    assert str(C.EMPTY) == ""


def test_choices_with_falsy_label() -> None:
    class C(Enum):
        ZERO = ("zero", {"label": 0})
        ONE = ("one", {"label": 1})

    assert C.choices() == [("zero", "0"), ("one", "1")]


def test_labels_with_falsy_label() -> None:
    class C(Enum):
        ZERO = ("zero", {"label": 0})
        EMPTY = ("empty", {"label": ""})

    assert C.labels() == ["0", ""]


# ---------- Additional edge case coverage ----------


def test_from_value_bytes_case_insensitive() -> None:
    class C(Enum):
        A = b"hello"

    assert C.from_value(b"hello", case_insensitive=True) is C.A


def test_from_name_whitespace_raises() -> None:
    class C(Enum):
        A = 1

    with pytest.raises(KeyError):
        C.from_name("  A  ")


def test_from_name_case_insensitive_whitespace_raises() -> None:
    class C(Enum):
        A = 1

    with pytest.raises(KeyError):
        C.from_name("  a  ", case_insensitive=True)


def test_to_json_unicode() -> None:
    class C(Enum):
        CAFÉ = ("café", {"label": "Café"})
        日本 = ("日本", {"label": "日本"})

    data = json.loads(C.to_json())
    assert data["members"][0]["value"] == "café"
    assert data["members"][0]["label"] == "Café"
    assert data["members"][1]["value"] == "日本"
    assert data["members"][1]["label"] == "日本"


def test_filter_non_existent_key() -> None:
    class C(Enum):
        A = ("a", {"x": 1})

    assert C.filter(z=99) == []


def test_filter_multiple_kwargs_partial_match() -> None:
    class C(Enum):
        A = ("a", {"x": 1, "y": 2})
        B = ("b", {"x": 1, "y": 3})
        C_MEM = ("c", {"x": 2, "y": 2})

    assert C.filter(x=1, y=2) == [C.A]


def test_serializable_encoder_nested() -> None:
    class C(Enum):
        A = "a"
        B = "b"

    result = json.dumps(
        {"items": [C.A, C.B], "selected": C.A}, cls=SerializableEncoder
    )
    assert json.loads(result) == {"items": ["a", "b"], "selected": "a"}


def test_from_json_empty_dict() -> None:
    class C(Enum):
        A = "a"

    assert C.from_json("{}") == {}


def test_from_json_nested() -> None:
    class C(Enum):
        A = "a"

    result = C.from_json('{"a": {"b": {"c": [1, 2]}}}')
    assert result == {"a": {"b": {"c": [1, 2]}}}


def test_empty_enum_all_operations() -> None:
    class Empty(Enum):
        pass

    assert Empty.to_dict() == {}
    assert Empty.choices() == []
    assert Empty.values() == []
    assert Empty.names() == []
    assert Empty.labels() == []
    assert Empty.keys() == []
    assert Empty.map({}) == {}
    assert Empty.filter() == []
    assert Empty.filter(x=1) == []


def test_label_coerces_int_to_str() -> None:
    class C(Enum):
        A = ("a", {"label": 42})

    assert C.A.label == "42"
    assert isinstance(C.A.label, str)


def test_label_coerces_float_to_str() -> None:
    class C(Enum):
        A = ("a", {"label": 3.14})

    assert C.A.label == "3.14"
    assert isinstance(C.A.label, str)


def test_label_coerces_bool_to_str() -> None:
    class C(Enum):
        A = ("a", {"label": True})

    assert C.A.label == "True"
    assert isinstance(C.A.label, str)


def test_eq_float_int_cross_type() -> None:
    class C(Enum):
        ONE = 1

    assert C.ONE == 1.0
    assert C.ONE == True  # noqa: E712


def test_from_value_float_for_int_member() -> None:
    class C(Enum):
        ONE = 1

    assert C.from_value(1.0) is C.ONE


def test_hash_consistency_with_value() -> None:
    class C(Enum):
        A = "a"

    assert hash(C.A) == hash("a")


def test_hash_unhashable_value_uses_id() -> None:
    class C(Enum):
        A = [1, 2]  # noqa: RUF012

    assert hash(C.A) == id(C.A)


def test_alias_shares_index() -> None:
    class C(Enum):
        A = 1
        B = 2
        ALIAS_FOR_A = 1

    assert C.A is C.ALIAS_FOR_A  # type: ignore[comparison-overlap]
    assert C.A._index_ == C.ALIAS_FOR_A._index_
    assert len(C) == 2


def test_map_with_missing_member() -> None:
    class C(Enum):
        A = "a"
        B = "b"
        C_MEM = "c"

    result = C.map({C.A: 1, C.C_MEM: 3})
    assert result == {"A": 1, "B": None, "C_MEM": 3}


def test_auto_with_custom_generate_next_value() -> None:
    class C(Enum):
        @staticmethod
        def _generate_next_value_(name: str, start: int, count: int, last_values: list[Any]) -> str:
            return f"custom_{count}"

        A = auto()
        B = auto()

    assert C.A.value == "custom_0"
    assert C.B.value == "custom_1"


def test_auto_after_metadata_with_custom_gnv() -> None:
    class C(Enum):
        @staticmethod
        def _generate_next_value_(name: str, start: int, count: int, last_values: list[Any]) -> str:
            return f"auto_{count}"

        A = ("first", {"label": "First"})
        B = auto()
        C_MEM = auto()

    assert C.A.value == "first"  # type: ignore[comparison-overlap]
    assert C.B.value == "auto_1"
    assert C.C_MEM.value == "auto_2"


def test_ignore_excludes_from_members() -> None:
    class C(Enum):
        _ignore_ = ["TEMP"]  # noqa: RUF012
        TEMP = 999
        A = 1
        B = 2

    assert not hasattr(C, "TEMP")
    assert len(C) == 2


# ---------- Enum member as value (Bug 9 regression) ----------


def test_from_value_with_enum_member_as_value() -> None:
    class Inner(Enum):
        X = "x"

    class Outer(Enum):
        A = Inner.X

    assert Outer.from_value(Inner.X) is Outer.A


def test_is_valid_with_enum_member_as_value() -> None:
    class Inner(Enum):
        X = "x"

    class Outer(Enum):
        A = Inner.X

    assert Outer.is_valid(Inner.X) is True


def test_contains_with_enum_member_as_value() -> None:
    class Inner(Enum):
        X = "x"

    class Outer(Enum):
        A = Inner.X

    assert Inner.X in Outer


def test_from_value_with_enum_member_as_value_with_default() -> None:
    class Inner(Enum):
        X = "x"
        Y = "y"

    class Outer(Enum):
        A = Inner.X

    # Inner.Y is not a value of any Outer member
    assert Outer.from_value(Inner.Y, default=None) is None


def test_from_value_with_enum_member_as_value_raises() -> None:
    class Inner(Enum):
        X = "x"
        Y = "y"

    class Outer(Enum):
        A = Inner.X

    with pytest.raises(ValueError, match="is not a valid Outer value"):
        Outer.from_value(Inner.Y)


def test_cross_enum_no_false_positive_with_same_value() -> None:
    class A(Enum):
        RED = "red"

    class B(Enum):
        RED = "red"

    # A.RED and B.RED have the same value "red", but are different enum members
    assert B.from_value(A.RED, default=None) is None
    assert not B.is_valid(A.RED)
    assert A.RED not in B


def test_cross_enum_identity_match_allows_lookup() -> None:
    class Inner(Enum):
        X = "x"

    class Outer(Enum):
        A = Inner.X

    # Inner.X IS the value of Outer.A (identity), so lookup should work
    # even though Inner.X is a foreign enum member
    assert Outer.from_value(Inner.X) is Outer.A
    assert Outer.is_valid(Inner.X)
    assert Inner.X in Outer


# ---------- to_json with enum member as value (Bug 10 regression) ----------


def test_to_json_with_enum_member_as_value() -> None:
    class Inner(Enum):
        X = "x"

    class Outer(Enum):
        A = Inner.X

    data = json.loads(Outer.to_json())
    assert data["members"][0]["value"] == "x"


def test_to_json_with_enum_member_as_value_in_metadata() -> None:
    class Inner(Enum):
        X = "x"

    class Outer(Enum):
        A = ("a", {"ref": Inner.X})

    data = json.loads(Outer.to_json())
    assert data["members"][0]["metadata"]["ref"] == "x"


def test_to_json_with_list_of_enum_members_as_value() -> None:
    class Inner(Enum):
        X = "x"
        Y = "y"

    class Outer(Enum):
        A = [Inner.X, Inner.Y]  # noqa: RUF012

    data = json.loads(Outer.to_json())
    assert data["members"][0]["value"] == ["x", "y"]


def test_to_json_with_int_enum_member_as_value() -> None:
    class Inner(Enum):
        ONE = 1

    class Outer(Enum):
        A = Inner.ONE

    data = json.loads(Outer.to_json())
    assert data["members"][0]["value"] == 1


def test_to_json_with_nested_enum_member_as_value() -> None:
    class Innermost(Enum):
        Z = "z"

    class Middle(Enum):
        A = Innermost.Z

    class Outer(Enum):
        A = Middle.A

    data = json.loads(Outer.to_json())
    # Middle.A.value is Innermost.Z, which serializes to "z"
    assert data["members"][0]["value"] == "z"
