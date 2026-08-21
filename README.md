# enumplus — Enhanced Enums for Python

![PyPI](https://img.shields.io/pypi/v/enumplus)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Tests](https://img.shields.io/badge/tests-116%20passing-brightgreen)

## Why

Python's `enum.Enum` is basic. `enumplus` adds display names, metadata, JSON serialization, `choices()`, and value-based comparison — all with zero dependencies and full stdlib compatibility. Just change your import and everything still works.

## Installation

```bash
pip install enumplus
```

## Quick Start

```python
from enumplus import Enum

class Color(Enum):
    RED = ("red", {"label": "Red", "hex": "#FF0000"})
    GREEN = ("green", {"label": "Green", "hex": "#00FF00"})
    BLUE = "blue"  # no metadata needed

# Display names
print(Color.RED.label)          # "Red"
print(str(Color.RED))           # "Red"

# Metadata access
print(Color.RED.hex)            # "#FF0000"
print(Color.RED.metadata)       # {"label": "Red", "hex": "#FF0000"}

# choices() for forms/dropdowns
print(Color.choices())          # [("red", "Red"), ("green", "Green"), ("blue", "Blue")]

# Lookup by value
print(Color.from_value("red"))  # Color.RED

# Compare with values directly
print(Color.RED == "red")       # True

# Membership test
print("red" in Color)           # True
```

## Features

### Display Names (label)

Every member gets a human-readable label, auto-generated from the member name or set explicitly via metadata.

```python
class Status(Enum):
    PENDING = "pending"                              # label: "Pending"
    IN_PROGRESS = ("in_progress", {"label": "In Progress"})

print(Status.PENDING.label)       # "Pending"
print(Status.IN_PROGRESS.label)   # "In Progress"
print(str(Status.IN_PROGRESS))    # "In Progress"
```

### Metadata

Attach arbitrary metadata to enum members using `(value, dict)` tuples. Access via attribute or the `metadata` property.

```python
class Color(Enum):
    RED = ("red", {"hex": "#FF0000", "description": "Pure red"})

print(Color.RED.hex)           # "#FF0000"
print(Color.RED.description)   # "Pure red"
print(Color.RED.metadata)      # {"hex": "#FF0000", "description": "Pure red"}
```

### choices()

Returns a list of `(value, label)` tuples — perfect for forms and dropdowns.

```python
class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

print(Priority.choices())   # [(1, "Low"), (2, "Medium"), (3, "High")]
```

### from_value() / from_name()

Look up members by value or name, with optional defaults.

```python
class Color(Enum):
    RED = "red"
    GREEN = "green"

Color.from_value("red")              # Color.RED
Color.from_value("blue")             # raises ValueError
Color.from_value("blue", default=None)  # None

Color.from_name("RED")               # Color.RED
Color.from_name("BLUE", default=None)   # None
```

### is_valid() / validate()

Check if a value is valid, or validate and raise.

```python
class Color(Enum):
    RED = "red"

Color.is_valid("red")       # True
Color.is_valid("blue")      # False
Color.is_valid(Color.RED)   # True

Color.validate("red")       # Color.RED
Color.validate("blue")      # raises ValueError
```

### values() / names() / labels()

Get lists of all values, names, or labels.

```python
class Color(Enum):
    RED = ("red", {"label": "Red"})
    GREEN = ("green", {"label": "Green"})

Color.values()   # ["red", "green"]
Color.names()    # ["RED", "GREEN"]
Color.labels()   # ["Red", "Green"]
```

### filter()

Filter members by metadata key-value pairs (AND logic).

```python
class Color(Enum):
    RED = ("red", {"hex": "#FF0000", "category": "warm"})
    GREEN = ("green", {"hex": "#00FF00", "category": "cool"})

Color.filter(category="warm")              # [Color.RED]
Color.filter(hex="#FF0000", category="warm")  # [Color.RED]
Color.filter()                             # [Color.RED, Color.GREEN]
```

### Comparison with values (==)

Members compare equal to their values directly.

```python
class Color(Enum):
    RED = "red"

Color.RED == "red"          # True
Color.RED == Color.RED      # True
Color.RED == "RED"          # False (name != value)
Color.RED != 42             # True
```

### Membership test (in)

Check if a value or member belongs to an enum.

```python
class Color(Enum):
    RED = "red"

"red" in Color          # True
"blue" not in Color     # True
Color.RED in Color      # True
42 not in Color         # True
```

### OrderedEnum

Order members by declaration order using `<`, `<=`, `>`, `>=`.

```python
from enumplus import OrderedEnum

class Priority(OrderedEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

Priority.LOW < Priority.HIGH    # True
Priority.HIGH > Priority.LOW    # True
sorted([Priority.HIGH, Priority.LOW, Priority.MEDIUM])  # [LOW, MEDIUM, HIGH]
min(Priority)   # Priority.LOW
max(Priority)   # Priority.HIGH
```

### JSON Serialization (to_json / from_json)

Serialize an enum class to JSON and parse it back.

```python
class Color(Enum):
    RED = ("red", {"hex": "#FF0000"})

json_str = Color.to_json()
# {
#   "name": "Color",
#   "members": [
#     {"name": "RED", "value": "red", "label": "Red", "metadata": {"hex": "#FF0000"}}
#   ]
# }

data = Color.from_json(json_str)   # parse back to dict
```

### SerializableEncoder

Serialize enum members to their values in JSON via a custom encoder.

```python
import json
from enumplus import Enum, SerializableEncoder

class Color(Enum):
    RED = "red"

json.dumps(Color.RED, cls=SerializableEncoder)           # '"red"'
json.dumps([Color.RED], cls=SerializableEncoder)         # '["red"]'
json.dumps({"color": Color.RED}, cls=SerializableEncoder)  # '{"color": "red"}'
```

### Pydantic v2

`enumplus` works with Pydantic v2 out of the box. Members validate from values and serialize to values.

```python
from pydantic import BaseModel
from enumplus import Enum

class Color(Enum):
    RED = "red"
    GREEN = "green"

class MyModel(BaseModel):
    color: Color

model = MyModel(color="red")     # validates "red" -> Color.RED
print(model.color)               # Color.RED
print(model.model_dump())        # {"color": "red"}
print(model.model_dump_json())   # '{"color":"red"}'
```

### Type hints in metadata

The `@dataclass_transform()` decorator on the metaclass enables type checkers to recognize metadata fields.

```python
class Color(Enum):
    RED = ("red", {"hex": "#FF0000"})

# Type checkers recognize .hex as a valid attribute
reveal_type(Color.RED.hex)  # str
```

## Migration from stdlib

Just change one import:

```python
# Before
from enum import Enum

# After
from enumplus import Enum
```

All existing enum code continues to work — `Enum["RED"]`, `Enum("red")`, `list(Enum)`, `len(Enum)`, `@unique`, `auto()`, `isinstance` checks, everything.

## License

MIT
