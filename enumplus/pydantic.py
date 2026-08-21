from __future__ import annotations

from typing import TYPE_CHECKING, Any

from enumplus.enum import Enum

if TYPE_CHECKING:
    from pydantic import GetCoreSchemaHandler
    from pydantic_core import CoreSchema


def get_pydantic_core_schema(
    cls: type[Enum], source_type: Any, handler: GetCoreSchemaHandler
) -> CoreSchema:
    from pydantic_core import core_schema

    serialize_by_name = getattr(cls, "serialize_by_name", False)

    def validate(value: Any) -> Any:
        if isinstance(value, cls):
            return value
        if serialize_by_name and isinstance(value, str):
            try:
                return cls.from_name(value)
            except KeyError:
                raise ValueError(f"{value!r} is not a valid {cls.__name__} name") from None
        return cls.from_value(value)

    if serialize_by_name:
        serializer = lambda v: v.name
    else:
        serializer = lambda v: v.value

    return core_schema.no_info_after_validator_function(
        validate,
        core_schema.any_schema(),
        serialization=core_schema.plain_serializer_function_ser_schema(
            serializer,
            return_schema=core_schema.any_schema(),
        ),
    )
