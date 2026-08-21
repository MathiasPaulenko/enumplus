from __future__ import annotations

import enum
from typing import Any, cast

try:
    from typing import dataclass_transform
except ImportError:
    from typing_extensions import dataclass_transform

_SENTINEL = object()


@dataclass_transform()
class EnumMeta(enum.EnumMeta):
    """Base metaclass for enumplus enums."""

    def __new__(
        cls,
        name: str,
        bases: tuple[type, ...],
        namespace: Any,
        **kwargs: Any,
    ) -> EnumMeta:
        member_metadata: dict[str, dict[str, Any]] = {}

        member_names: list[str] = list(getattr(namespace, "_member_names", []))
        last_values: list[Any] = getattr(namespace, "_last_values", [])

        class_config: dict[str, Any] = {}
        _config_keys = {"serialize_by_name"}

        ns_member_names = getattr(namespace, "_member_names", None)

        for key in _config_keys:
            if key in namespace:
                class_config[key] = namespace[key]
                dict.__delitem__(namespace, key)
                if ns_member_names is not None and key in ns_member_names:
                    if isinstance(ns_member_names, dict):
                        del ns_member_names[key]
                    else:
                        ns_member_names.remove(key)

        for key, value in list(namespace.items()):
            if isinstance(value, tuple) and len(value) == 2 and isinstance(value[1], dict):
                actual_value, metadata = value
                member_metadata[key] = metadata
                if key in member_names:
                    idx = member_names.index(key)
                    last_values[idx] = actual_value
                dict.__setitem__(namespace, key, actual_value)

        new_cls = super().__new__(cls, name, bases, namespace, **kwargs)

        for key, value in class_config.items():
            setattr(new_cls, key, value)

        if not hasattr(new_cls, "serialize_by_name"):
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

    serialize_by_name: bool = False

    def __contains__(cls, item: Any) -> bool:
        if isinstance(item, cls):
            return True
        member: Any
        for member in cls:
            if member.value == item:
                return True
        return False


class Enum(enum.Enum, metaclass=EnumMeta):
    """Base enum class for enumplus."""

    _label_: str
    _metadata_: dict[str, Any]
    _index_: int

    @property
    def label(self) -> str:
        label = self._label_
        if callable(label):
            return str(label())
        return str(label)

    @property
    def metadata(self) -> dict[str, Any]:
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
        return bool(self.value == other)

    def __hash__(self) -> int:
        return hash(self.value)

    @classmethod
    def choices(cls) -> list[tuple[Any, str]]:
        return [(member.value, member.label) for member in cls]

    @classmethod
    def from_value(
        cls, value: Any, default: Any = _SENTINEL, *, case_insensitive: bool = False
    ) -> Enum:
        member: Any
        if case_insensitive and isinstance(value, str):
            lowered = value.lower()
            for member in cls:
                if isinstance(member.value, str) and member.value.lower() == lowered:
                    return cast(Enum, member)
        else:
            for member in cls:
                if member.value == value:
                    return cast(Enum, member)
        if default is not _SENTINEL:
            return cast(Enum, default)
        raise ValueError(f"{value!r} is not a valid {cls.__name__} value")

    @classmethod
    def from_name(
        cls, name: str, default: Any = _SENTINEL, *, case_insensitive: bool = False
    ) -> Enum:
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
            return cast(Enum, default)
        raise KeyError(f"{name!r} is not a valid {cls.__name__} name")

    @classmethod
    def is_valid(cls, value: Any) -> bool:
        member: Any
        for member in cls:
            if member.value == value or member is value:
                return True
        return False

    @classmethod
    def validate(cls, value: Any) -> Enum:
        return cls.from_value(value)

    @classmethod
    def values(cls) -> list[Any]:
        return [member.value for member in cls]

    @classmethod
    def names(cls) -> list[str]:
        return [member.name for member in cls]

    @classmethod
    def labels(cls) -> list[str]:
        return [member.label for member in cls]

    @classmethod
    def keys(cls) -> list[str]:
        return [member.name for member in cls]

    @classmethod
    def get(cls, value: Any, default: Any = None) -> Enum | None:
        return cls.from_value(value, default=default)

    @classmethod
    def get_initial(cls) -> Enum:
        members = list(cls)
        if not members:
            raise ValueError(f"{cls.__name__} has no members")
        return members[0]

    @classmethod
    def get_final(cls) -> Enum:
        members = list(cls)
        if not members:
            raise ValueError(f"{cls.__name__} has no members")
        return members[-1]

    @classmethod
    def map(cls, mapping: dict[Enum, Any]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for member in cls:
            result[member.name] = mapping.get(member, None)
        return result

    @classmethod
    def to_dict(cls) -> dict[str, dict[str, Any]]:
        result: dict[str, dict[str, Any]] = {}
        for member in cls:
            result[member.name] = {
                "value": member.value,
                "label": member.label,
                "metadata": {
                    k: (v() if callable(v) else v)
                    for k, v in member._metadata_.items()
                },
            }
        return result

    @classmethod
    def filter(cls, **kwargs: Any) -> list[Enum]:
        if not kwargs:
            return list(cls)
        result: list[Enum] = []
        member: Any
        for member in cls:
            if all(
                key in member._metadata_ and member._metadata_[key] == value
                for key, value in kwargs.items()
            ):
                result.append(cast(Enum, member))
        return result

    @classmethod
    def to_json(cls) -> str:
        from enumplus.serialize import to_json

        return to_json(cls)

    @classmethod
    def from_json(cls, data: str) -> dict[str, Any]:
        from enumplus.serialize import from_json

        return from_json(data)

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: Any) -> Any:
        from enumplus.pydantic import get_pydantic_core_schema

        return get_pydantic_core_schema(cls, source_type, handler)


class OrderedEnum(Enum):
    """Enum mixin with ordering based on declaration order."""

    def __lt__(self, other: OrderedEnum) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._index_ < other._index_

    def __le__(self, other: OrderedEnum) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._index_ <= other._index_

    def __gt__(self, other: OrderedEnum) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._index_ > other._index_

    def __ge__(self, other: OrderedEnum) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._index_ >= other._index_
