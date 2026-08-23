"""enumplus — Enhanced Enums for Python.

Drop-in replacement for ``enum.Enum`` with labels, metadata, serialization,
and Pydantic v2 integration.
"""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

from enumplus.enum import Enum, OrderedEnum
from enumplus.serialize import SerializableEncoder

try:
    __version__ = _pkg_version("enumplus")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0.dev0"

__all__ = ["Enum", "OrderedEnum", "SerializableEncoder", "__version__"]
