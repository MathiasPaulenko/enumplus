from __future__ import annotations

import enumplus


def test_public_api() -> None:
    assert hasattr(enumplus, "Enum")
    assert hasattr(enumplus, "OrderedEnum")
    assert hasattr(enumplus, "SerializableEncoder")
    assert hasattr(enumplus, "__version__")


def test_all_exports() -> None:
    assert set(enumplus.__all__) == {"Enum", "OrderedEnum", "SerializableEncoder", "__version__"}


def test_version() -> None:
    from importlib.metadata import version

    assert enumplus.__version__ == version("enumplus")
