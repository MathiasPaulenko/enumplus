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
- `serialize_by_name` is a reserved class config key: it must be a `bool`
  (`TypeError` otherwise) and can never be a member name.
- Metadata tuples are detected with `type(value) is tuple` (not
  `isinstance`), so tuple subclasses such as `NamedTuple` stay intact as
  member values.
- During class creation, `EnumMeta.__new__` injects the collected metadata map
  as the temporary `_enumplus_pending_metadata` class attribute and removes it
  after member post-processing. `Enum._resolve_metadata()` reads `_metadata_`
  first, then the pending map, so `label`/`metadata`/metadata attributes work
  inside member `__init__`. Members created via `enum._simple_enum` never get
  `_metadata_`/`_label_`/`_index_`; accessors degrade gracefully to auto
  labels, empty metadata, and `_sort_order_`-based ordering.
- Auto-generated labels use `name.replace("_", " ").title()`. `filter(label=...)`
  matches the evaluated label, not the raw metadata dict.
- `Enum.__eq__` compares enum-to-enum by identity links only (`self is other`,
  `self.value is other`, `other.value is self`) and everything else through
  `_safe_equal`, which coerces `a == b` to a `bool` without raising on
  shape/length mismatches (e.g. NumPy arrays, unhashable container values).
  `EnumMeta.__contains__`, `from_value()`, `is_valid()`, and `_missing_()`
  share `_match_enum_member` for the enum-member branch.
- `Enum._missing_` is implemented so `cls(value)` lookup agrees with
  `from_value()` on misses. For classes mixing in `enum.Flag`/`enum.IntFlag`
  it delegates to the nearest Flag-family `_missing_` in the MRO, preserving
  composite pseudo-members and `boundary=` semantics.
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

- The repository was renamed from `enumpy` to `enumplus` on GitHub. All
  project URLs point to `MathiasPaulenko/enumplus`; old `enumpy` links
  redirect automatically.
- `ref/` is intentionally ignored (local reference material). Do not commit it.
