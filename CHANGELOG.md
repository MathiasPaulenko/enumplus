# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.1] - 2026-08-23

### Fixed

- `to_dict()` and `to_json()` no longer double-evaluate callable labels — the callable is invoked exactly once and the result is reused in both the top-level `label` field and the `metadata` dict.
- `__version__` is now loaded dynamically from package metadata via `importlib.metadata`, eliminating version mismatch between `__init__.py` and `pyproject.toml`.
- `__contains__`, `from_value()`, `is_valid()`, and `get()` no longer produce false positives when passed a foreign enum member with the same value as a member of the queried enum.
- `__contains__`, `from_value()`, `is_valid()`, and `get()` now correctly handle members whose value is an enum member from another class. Previously, the foreign-enum guard rejected all foreign enum members, making it impossible to look up such members by value.
- `to_json()` now uses `SerializableEncoder` internally, so members whose value (or metadata) is an enum member from another class are serialized correctly instead of raising `TypeError`.
- `_safe_equal()` now catches all exceptions (not just `TypeError` and `ValueError`) from custom `__eq__` implementations, preventing crashes when comparing with objects that raise unexpected exceptions.
- Falsy but valid labels (`0`, `""`, `False`) are now respected instead of being silently replaced by `name.title()`. Only `None` and missing labels trigger the fallback.
- Removed dead `_serialize_value` function from `serialize.py`.
- Updated `SECURITY.md` to include `1.2.x` in supported versions.

## [1.2.0] - 2026-08-23

### Fixed

- `serialize_by_name` is now correctly inherited by subclass enums instead of being silently reset to `False`.

### Changed

- Improved README with table of contents, requirements section, and dynamic CI badge.
- Added `pydantic` optional dependency extra for Pydantic v2 integration.
- Added concurrency groups to CI and release workflows to cancel superseded runs.
- Updated issue templates with correct version examples.
- Updated CONTRIBUTING with cross-version testing instructions and repository name clarification.

## [1.1.0] - 2025-01-15

### Added

- Case-insensitive lookup via `case_insensitive=True` on `from_value()` and `from_name()`.
- `serialize_by_name` class config for Pydantic v2 validation and serialization by member name.
- `to_dict()` method for serializing an enum to a nested dictionary.
- `get()` method for dict-style lookup with a default.
- `map()` method for mapping each member to a value.
- `keys()` method as an alias of `names()`.
- `get_initial()` and `get_final()` for declaration-order access.
- Callable labels for i18n / translatable labels.
- `@dataclass_transform()` on the metaclass for type-checker metadata attribute support.
- `py.typed` marker for PEP 561 typed-package support.
- Python 3.14 support and CI coverage.

### Fixed

- `auto()` now works correctly after metadata tuples on Python 3.11–3.14.
- Class config (`serialize_by_name`) no longer registers as an enum member or corrupts `auto()` state.
- `__eq__`, `__hash__`, `__contains__`, `from_value`, `is_valid`, and `filter` are now safe for unhashable values and non-boolean comparison results.
- `from_json` validates input type and JSON shape (`TypeError` for wrong type, `ValueError` for invalid JSON).
- `from_name` raises `TypeError` for non-string input instead of `KeyError`.
- `to_dict()` and `to_json()` no longer invoke non-label callable metadata values.
- Removed redundant import in `SerializableEncoder`.

### Changed

- Improved package metadata: classifiers, project URLs, and dev dependency lower bounds.
- Release workflow uses `${{ github.repository }}` for dynamic changelog URLs.
- CONTRIBUTING and SUPPORT docs updated with correct commands.

## [1.0.0] - 2024-12-01

### Added

- `Enum` base class as a drop-in replacement for `enum.Enum`.
- `OrderedEnum` with declaration-order comparison operators.
- Per-member labels with automatic `name.title()` fallback.
- Per-member metadata via `(value, dict)` tuple syntax.
- Metadata attribute access via `__getattr__`.
- `choices()`, `from_value()`, `from_name()`, `is_valid()`, `validate()`.
- `values()`, `names()`, `labels()`.
- `filter()` by metadata key-value pairs.
- `to_json()` / `from_json()` serialization.
- `SerializableEncoder` for `json.dumps`.
- Pydantic v2 integration via `__get_pydantic_core_schema__`.
- Full test suite, CI, and release workflows.

[Unreleased]: https://github.com/MathiasPaulenko/enumpy/compare/v1.2.1...HEAD
[1.2.1]: https://github.com/MathiasPaulenko/enumpy/releases/tag/v1.2.1
[1.2.0]: https://github.com/MathiasPaulenko/enumpy/releases/tag/v1.2.0
[1.1.0]: https://github.com/MathiasPaulenko/enumpy/releases/tag/v1.1.0
[1.0.0]: https://github.com/MathiasPaulenko/enumpy/releases/tag/v1.0.0
