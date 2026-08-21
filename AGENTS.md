# Agent Notes for enumplus

## Project purpose

`enumplus` is a zero-dependency Python library that extends `enum.Enum` with:

- Per-member display labels (`label`)
- Arbitrary per-member metadata, accessible as attributes
- `(value, metadata)` tuple unpacking at class definition
- `choices()`, `from_value()`, `from_name()`, `filter()`, `get()`, `map()`
- JSON serialization (`to_json`, `from_json`, `SerializableEncoder`)
- Declaration-order comparison (`OrderedEnum`)
- Optional Pydantic v2 integration (install with `pip install "enumplus[pydantic]"`)

Requires Python `>=3.11`.

## Important implementation details

- The metaclass in `enumplus/enum.py` uses a custom `_EnumPlusDict` namespace.
  This is required to:
  - Unpack `(value, {metadata})` tuples before stdlib enum machinery sees them.
  - Keep class config keys such as `serialize_by_name` from becoming enum members
    or affecting `auto()` generation.
  - Support `auto()` following a metadata tuple on Python 3.11–3.14.
- `Enum.__eq__` and `EnumMeta.__contains__` use `_safe_equal`, which coerces
  `a == b` to a `bool` without raising on shape/length mismatches (e.g. NumPy
  arrays, unhashable container values).
- `Enum.__hash__` uses `hash(self.value)` when possible and falls back to
  `id(self)` for unhashable values, so enum members with list/dict values are
  still usable as dict keys.
- `serialize.py` `from_json` validates that input is a `str` and that the
  parsed JSON is a `dict` (`TypeError` otherwise). Invalid JSON strings raise
  `ValueError`.
- `py.typed` is included in the wheel so the package is a PEP 561 typed package.

## Build and verification commands

```bash
python -m ruff check enumplus/ tests/
python -m mypy --strict enumplus/ tests/
python -m pytest --tb=short
python -m build
```

After building, verify the wheel contains `py.typed`:

```bash
python -m zipfile -l dist/*.whl
```

## Cross-version testing

CI tests Python 3.11, 3.12, 3.13, and 3.14. Locally, the following versions have
been verified:

- Python 3.11.2
- Python 3.12.4
- Python 3.14.5

Run a different version with the Windows launcher, e.g.:

```bash
py -3.11 -m pip install -e ".[dev]"
py -3.11 -m pytest --tb=short
py -3.11 -m mypy --strict enumplus/ tests/
```

## Known constraints

- The git remote is `MathiasPaulenko/enumpy`, while the package name and PyPI
  project are `enumplus`. Package URLs in `pyproject.toml` point to the actual
  remote repository; update if the repository is renamed.
- `ref/` is intentionally ignored (local reference material). Do not commit it.
