"""enumplus — Enhanced Enums for Python.

Drop-in replacement for ``enum.Enum`` with labels, metadata, serialization,
and Pydantic v2 integration.
"""

from enumplus.enum import Enum, OrderedEnum
from enumplus.serialize import SerializableEncoder

__version__ = "1.1.0"

__all__ = ["Enum", "OrderedEnum", "SerializableEncoder", "__version__"]
