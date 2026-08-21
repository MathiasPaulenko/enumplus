from __future__ import annotations

import enum
import sys
from typing import Any, Self, TypeVar, dataclass_transform, overload

if sys.version_info >= (3, 13):
    from enum import EnumDict
else:
    from enum import _EnumDict as EnumDict

_SENTINEL = object()
_T = TypeVar("_T")


class _EnumPlusDict(EnumDict):
    """Namespace dict that unwraps per-member metadata and class config.

    ``(value, metadata_dict)`` tuples are unpacked so the real value is used
    for enum machinery (including ``auto()`` generation), while the metadata is
    stored separately and attached to the created members.

    Class config keys such as ``serialize_by_name`` are kept as normal class
    attributes and are never registered as enum members, so they do not affect
    ``auto()`` values or member order.
    """

    _CONFIG_KEYS = frozenset({"serialize_by_name"})

    def __init__(self, cls_name: str | None = None) -> None:
        super().__init__()
        self._member_metadata: dict[str, dict[str, Any]] = {}
        self._class_config: dict[str, Any] = {}
        # In Python <3.13 _EnumDict.__init__ does not set _cls_name; in 3.13+
        # it is set by super().__init__() but defaulting to None. Ensure it is
        # always available for _is_private/_is_internal_class checks.
        if cls_name is not None:
            self._cls_name = cls_name

    def __setitem__(self, key: str, value: Any) -> None:
        if key in self._CONFIG_KEYS:
            self._class_config[key] = value
            # Store as a class attribute, but do not register as a member and
            # do not affect _last_values used by auto().
            dict.__setitem__(self, key, value)
            return

        if (
            isinstance(value, tuple)
            and len(value) == 2
            and isinstance(value[1], dict)
        ):
            actual_value, metadata = value
            self._member_metadata[key] = metadata
            value = actual_value

        super().__setitem__(key, value)


def _safe_equal(a: Any, b: Any) -> bool:
    """Return ``a == b`` as a bool, swallowing shape/length comparison errors.

    Handles values whose ``__eq__`` may raise (e.g. NumPy arrays with shape
    mismatches) or return non-boolean objects (e.g. arrays, ``NotImplemented``).
    """
    try:
        result = a == b
    except (TypeError, ValueError):
        return False
    if result is NotImplemented:
        return False
    try:
        return bool(result)
    except (TypeError, ValueError):
        return False


@dataclass_transform()
class EnumMeta(enum.EnumMeta):
    """Metaclass for enumplus enums.

    Extends ``enum.EnumMeta`` with:

    - Custom namespace (``_EnumPlusDict``) that unwraps metadata tuples
      and separates class config from enum members.
    - Per-member metadata and label assignment after member creation.
    - Safe ``__contains__`` that handles unhashable and non-boolean values.
    """

    @classmethod
    def __prepare__(  # type: ignore[override]
        metacls,
        cls: str,
        bases: tuple[type, ...],
        **kwds: Any,
    ) -> _EnumPlusDict:
        # Reuse EnumType.__prepare__ for existing-member checks and inherited
        # _generate_next_value_, then copy into our custom namespace.
        base_ns = super().__prepare__(cls, bases, **kwds)
        namespace = _EnumPlusDict(cls)
        for key, value in base_ns.items():
            namespace[key] = value
        gnv = getattr(base_ns, "_generate_next_value", None)
        if gnv is not None:
            namespace._generate_next_value = gnv  # type: ignore[attr-defined]
        return namespace

    def __new__(
        cls,
        name: str,
        bases: tuple[type, ...],
        namespace: Any,
        **kwargs: Any,
    ) -> EnumMeta:
        member_metadata: dict[str, dict[str, Any]]
        class_config: dict[str, Any]

        if isinstance(namespace, _EnumPlusDict):
            member_metadata = namespace._member_metadata
            class_config = namespace._class_config
        else:
            # Best-effort fallback for plain dicts/EnumDict not prepared by us.
            member_metadata = {}
            class_config = {}
            for key, value in list(namespace.items()):
                if (
                    isinstance(value, tuple)
                    and len(value) == 2
                    and isinstance(value[1], dict)
                ):
                    actual_value, metadata = value
                    member_metadata[key] = metadata
                    dict.__setitem__(namespace, key, actual_value)

        new_cls = super().__new__(cls, name, bases, namespace, **kwargs)

        for key, value in class_config.items():
            setattr(new_cls, key, value)

        if "serialize_by_name" not in class_config:
            new_cls.serialize_by_name = False

        members: list[Any] = list(new_cls)
        for index, member in enumerate(members):
            metadata = member_metadata.get(member.name, {})
            member._metadata_ = metadata

            label = metadata.get("label")
            if not label:
                member._label_ = member.name.title()
            else:
                member._label_ = label

            member._index_ = index

        return new_cls

    def __contains__(cls, item: Any) -> bool:
        if isinstance(item, cls):
            return True
        member: Any
        for member in cls:
            if _safe_equal(member.value, item):
                return True
        return False

    serialize_by_name: bool = False


class Enum(enum.Enum, metaclass=EnumMeta):
    """Enhanced enum base class with labels, metadata, and serialization.

    Drop-in replacement for ``enum.Enum`` that adds:

    - Human-readable labels (``label`` property, ``str()``)
    - Per-member metadata via ``(value, dict)`` tuple syntax
    - Metadata attribute access (``Color.RED.hex``)
    - Value-based equality (``Color.RED == "red"``)
    - Lookup helpers (``from_value``, ``from_name``, ``get``)
    - Validation helpers (``is_valid``, ``validate``)
    - Collection helpers (``choices``, ``values``, ``names``, ``labels``)
    - Filtering by metadata (``filter``)
    - JSON serialization (``to_json``, ``from_json``)
    - Pydantic v2 integration
    """

    _label_: str
    _metadata_: dict[str, Any]
    _index_: int

    @property
    def label(self) -> str:
        """Human-readable label for this member.

        If the label was set to a callable, it is evaluated on every access.
        Falls back to ``name.title()`` when no label is set.
        """
        label = self._label_
        if callable(label):
            return str(label())
        return str(label)

    @property
    def metadata(self) -> dict[str, Any]:
        """Metadata dictionary attached to this member."""
        return self._metadata_

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(name)
        try:
            return self._metadata_[name]
        except KeyError:
            raise AttributeError(
                f"{type(self).__name__}.{self.name!s} has no attribute {name!r}"
            ) from None

    def __str__(self) -> str:
        return self.label

    def __repr__(self) -> str:
        return f"<{type(self).__name__}.{self.name}: {self.value!r}>"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, enum.Enum):
            return self is other
        return _safe_equal(self.value, other)

    def __hash__(self) -> int:
        try:
            return hash(self.value)
        except TypeError:
            return id(self)

    @classmethod
    def choices(cls) -> list[tuple[Any, str]]:
        """Return ``[(value, label), ...]`` for forms and dropdowns."""
        return [(member.value, member.label) for member in cls]

    @overload
    @classmethod
    def from_value(
        cls, value: Any, *, case_insensitive: bool = False
    ) -> Self: ...

    @overload
    @classmethod
    def from_value(
        cls, value: Any, default: _T, *, case_insensitive: bool = False
    ) -> Self | _T: ...

    @classmethod
    def from_value(
        cls,
        value: Any,
        default: Any = _SENTINEL,
        *,
        case_insensitive: bool = False,
    ) -> Any:
        """Look up a member by value.

        Args:
            value: The value to search for.
            default: Returned if no match is found. If omitted, raises ``ValueError``.
            case_insensitive: If ``True``, perform case-insensitive string comparison.

        Returns:
            The matching member, or ``default`` if provided and no match found.

        Raises:
            ValueError: If no match is found and no default is provided.
        """
        member: Any
        if case_insensitive and isinstance(value, str):
            lowered = value.lower()
            for member in cls:
                if isinstance(member.value, str) and member.value.lower() == lowered:
                    return member
        else:
            for member in cls:
                if _safe_equal(member.value, value):
                    return member
        if default is not _SENTINEL:
            return default
        raise ValueError(f"{value!r} is not a valid {cls.__name__} value")

    @overload
    @classmethod
    def from_name(cls, name: str, *, case_insensitive: bool = False) -> Self: ...

    @overload
    @classmethod
    def from_name(cls, name: str, default: _T, *, case_insensitive: bool = False) -> Self | _T: ...

    @classmethod
    def from_name(
        cls,
        name: str,
        default: Any = _SENTINEL,
        *,
        case_insensitive: bool = False,
    ) -> Any:
        """Look up a member by name.

        Args:
            name: The member name to search for.
            default: Returned if no match is found. If omitted, raises ``KeyError``.
            case_insensitive: If ``True``, perform case-insensitive name comparison.

        Returns:
            The matching member, or ``default`` if provided and no match found.

        Raises:
            TypeError: If ``name`` is not a string.
            KeyError: If no match is found and no default is provided.
        """
        if not isinstance(name, str):
            raise TypeError(
                f"from_name expects a string, got {type(name).__name__}"
            )

        if case_insensitive:
            upper = name.upper()
            for member in cls:
                if member.name.upper() == upper:
                    return member
        else:
            found = cls.__members__.get(name)
            if found is not None:
                return found
        if default is not _SENTINEL:
            return default
        raise KeyError(f"{name!r} is not a valid {cls.__name__} name")

    @classmethod
    def is_valid(cls, value: Any) -> bool:
        """Return ``True`` if ``value`` is a valid member or member value."""
        for member in cls:
            if member is value or _safe_equal(member.value, value):
                return True
        return False

    @classmethod
    def validate(cls, value: Any) -> Self:
        """Validate ``value`` and return the matching member.

        Raises:
            ValueError: If ``value`` is not a valid member value.
        """
        return cls.from_value(value)

    @classmethod
    def values(cls) -> list[Any]:
        """Return a list of all member values in declaration order."""
        return [member.value for member in cls]

    @classmethod
    def names(cls) -> list[str]:
        """Return a list of all member names in declaration order."""
        return [member.name for member in cls]

    @classmethod
    def labels(cls) -> list[str]:
        """Return a list of all member labels in declaration order."""
        return [member.label for member in cls]

    @classmethod
    def keys(cls) -> list[str]:
        """Alias for :meth:`names` for dict-like ergonomics."""
        return [member.name for member in cls]

    @overload
    @classmethod
    def get(cls, value: Any) -> Self | None: ...

    @overload
    @classmethod
    def get(cls, value: Any, default: _T) -> Self | _T: ...

    @classmethod
    def get(cls, value: Any, default: Any = None) -> Any:
        """Dict-style lookup that returns ``default`` (``None``) instead of raising."""
        return cls.from_value(value, default=default)

    @classmethod
    def get_initial(cls) -> Self:
        """Return the first member by declaration order.

        Raises:
            ValueError: If the enum has no members.
        """
        members = list(cls)
        if not members:
            raise ValueError(f"{cls.__name__} has no members")
        return members[0]

    @classmethod
    def get_final(cls) -> Self:
        """Return the last member by declaration order.

        Raises:
            ValueError: If the enum has no members.
        """
        members = list(cls)
        if not members:
            raise ValueError(f"{cls.__name__} has no members")
        return members[-1]

    @classmethod
    def map(cls, mapping: dict[Self, Any]) -> dict[str, Any]:
        """Map each member to a value via ``mapping``.

        Returns ``{name: mapped_value}`` for every member. Members not present
        in ``mapping`` get ``None``.
        """
        result: dict[str, Any] = {}
        for member in cls:
            result[member.name] = mapping.get(member, None)
        return result

    @classmethod
    def to_dict(cls) -> dict[str, dict[str, Any]]:
        """Serialize the enum to a nested dict with ``value``, ``label``, ``metadata``."""
        result: dict[str, dict[str, Any]] = {}
        for member in cls:
            result[member.name] = {
                "value": member.value,
                "label": member.label,
                "metadata": {
                    k: (v() if callable(v) and k == "label" else v)
                    for k, v in member._metadata_.items()
                },
            }
        return result

    @classmethod
    def filter(cls, **kwargs: Any) -> list[Self]:
        """Filter members by metadata key-value pairs (AND logic).

        With no kwargs, returns all members.
        """
        if not kwargs:
            return list(cls)
        result: list[Self] = []
        for member in cls:
            if all(
                key in member._metadata_ and _safe_equal(member._metadata_[key], value)
                for key, value in kwargs.items()
            ):
                result.append(member)
        return result

    @classmethod
    def to_json(cls) -> str:
        """Serialize the enum class to a JSON string."""
        from enumplus.serialize import to_json

        return to_json(cls)

    @classmethod
    def from_json(cls, data: str) -> dict[str, Any]:
        """Parse a JSON string into a dictionary.

        Note: this returns the parsed dictionary, not a reconstructed enum class.

        Raises:
            TypeError: If ``data`` is not a string or the parsed JSON is not an object.
            ValueError: If ``data`` is not valid JSON.
        """
        from enumplus.serialize import from_json

        return from_json(data)

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: Any) -> Any:
        from enumplus.pydantic import get_pydantic_core_schema

        return get_pydantic_core_schema(cls, source_type, handler)


class OrderedEnum(Enum):
    """Enum with ordering operators based on declaration order.

    Supports ``<``, ``<=``, ``>``, ``>=`` between members of the same class.
    Also works with ``sorted()``, ``min()``, and ``max()``.
    """

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._index_ < other._index_

    def __le__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._index_ <= other._index_

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._index_ > other._index_

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._index_ >= other._index_
