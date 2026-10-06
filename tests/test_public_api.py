from __future__ import annotations

import pytest

import enumplus


def test_public_api() -> None:
    assert hasattr(enumplus, "Enum")
    assert hasattr(enumplus, "OrderedEnum")
    assert hasattr(enumplus, "SerializableEncoder")
    assert hasattr(enumplus, "__version__")


def test_all_exports() -> None:
    assert set(enumplus.__all__) == {"Enum", "OrderedEnum", "SerializableEncoder", "__version__"}


def test_version() -> None:
    from importlib.metadata import PackageNotFoundError, version

    try:
        expected = version("enumplus")
    except PackageNotFoundError:
        pytest.skip("enumplus is not installed")
    assert enumplus.__version__ == expected
