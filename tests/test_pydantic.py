from __future__ import annotations

import pytest

pytest.importorskip("pydantic")

from pydantic import BaseModel, ValidationError

from enumplus import Enum


class Color(Enum):
    RED = "red"
    GREEN = "green"


class MyModel(BaseModel):
    color: Color


def test_pydantic_validate_string() -> None:
    model = MyModel(color="red")  # type: ignore[arg-type]
    assert model.color is Color.RED


def test_pydantic_validate_member() -> None:
    model = MyModel(color=Color.RED)
    assert model.color is Color.RED


def test_pydantic_invalid() -> None:
    with pytest.raises(ValidationError):
        MyModel(color="blue")  # type: ignore[arg-type]


def test_pydantic_dump() -> None:
    model = MyModel(color=Color.RED)
    assert model.model_dump() == {"color": "red"}


def test_pydantic_dump_json() -> None:
    model = MyModel(color=Color.RED)
    assert model.model_dump_json() == '{"color":"red"}'


class ColorByName(Enum):
    RED = "red"
    GREEN = "green"

    serialize_by_name = True


class MyModelByName(BaseModel):
    color: ColorByName


def test_pydantic_serialize_by_name_validate() -> None:
    model = MyModelByName(color="RED")  # type: ignore[arg-type]
    assert model.color is ColorByName.RED


def test_pydantic_serialize_by_name_validate_member() -> None:
    model = MyModelByName(color=ColorByName.RED)
    assert model.color is ColorByName.RED


def test_pydantic_serialize_by_name_invalid() -> None:
    with pytest.raises(ValidationError):
        MyModelByName(color="blue")  # type: ignore[arg-type]


def test_pydantic_serialize_by_name_dump() -> None:
    model = MyModelByName(color=ColorByName.RED)
    assert model.model_dump() == {"color": "RED"}


def test_pydantic_serialize_by_name_dump_json() -> None:
    model = MyModelByName(color=ColorByName.RED)
    assert model.model_dump_json() == '{"color":"RED"}'
