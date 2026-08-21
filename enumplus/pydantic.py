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

    def validate(value: Any) -> Any:
        if isinstance(value, cls):
            return value
        return cls.from_value(value)

    return core_schema.no_info_after_validator_function(
        validate,
        core_schema.any_schema(),
        serialization=core_schema.plain_serializer_function_ser_schema(
            lambda v: v.value,
            return_schema=core_schema.any_schema(),
        ),
    )
