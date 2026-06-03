#!/usr/bin/env python3
"""
Validate a book-metrics.json file against book-metrics.schema.json.

The canonical metrics file (docs/learning-graph/book-metrics.json) is produced
by book-metrics.py and consumed by several skills (readme-generator,
linkedin-announcement-generator, case-study-generator). This validator lets any
producer or consumer confirm the file conforms to the agreed format before
relying on it.

Usage:
    python validate-book-metrics.py [path/to/book-metrics.json]

Defaults to docs/learning-graph/book-metrics.json relative to the current
directory. Exits 0 on success, 1 on a validation error, 2 on a usage/IO error.

If the `jsonschema` package is installed it is used for full Draft 2020-12
validation; otherwise a dependency-free fallback checks the required keys and
their basic types so the script still works in a bare environment.
"""

import json
import sys
from pathlib import Path

SCHEMA_PATH = Path(__file__).resolve().parent / "book-metrics.schema.json"
DEFAULT_TARGET = Path("docs/learning-graph/book-metrics.json")


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def fallback_validate(data, schema) -> list:
    """Minimal validation used when jsonschema is not installed.

    Checks top-level required keys and the required keys/types inside the
    `metrics` object. Returns a list of human-readable error strings (empty on
    success).
    """
    errors = []

    if not isinstance(data, dict):
        return ["root: expected a JSON object"]

    for key in schema.get("required", []):
        if key not in data:
            errors.append(f"missing required top-level key: {key!r}")

    metrics = data.get("metrics")
    if not isinstance(metrics, dict):
        errors.append("'metrics': expected an object")
        return errors

    metrics_schema = schema["properties"]["metrics"]
    for key in metrics_schema.get("required", []):
        if key not in metrics:
            errors.append(f"metrics: missing required key: {key!r}")

    for key, value in metrics.items():
        if key == "developmentStage":
            if not isinstance(value, str):
                errors.append(f"metrics.{key}: expected a string")
        elif isinstance(value, bool) or not isinstance(value, int):
            # bool is a subclass of int but is not a valid count
            errors.append(f"metrics.{key}: expected a non-negative integer")
        elif value < 0:
            errors.append(f"metrics.{key}: must be >= 0")

    return errors


def main() -> int:
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_TARGET

    if not target.exists():
        print(f"❌ Not found: {target}")
        return 2
    if not SCHEMA_PATH.exists():
        print(f"❌ Schema not found: {SCHEMA_PATH}")
        return 2

    try:
        data = load_json(target)
        schema = load_json(SCHEMA_PATH)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {target}: {e}")
        return 1
    except OSError as e:
        print(f"❌ Could not read file: {e}")
        return 2

    try:
        import jsonschema  # type: ignore
        validator = jsonschema.Draft202012Validator(schema)
        errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
        if errors:
            print(f"❌ {target} failed schema validation:")
            for err in errors:
                loc = "/".join(str(p) for p in err.path) or "(root)"
                print(f"   - {loc}: {err.message}")
            return 1
        print(f"✅ {target} is valid (jsonschema, Draft 2020-12).")
        return 0
    except ImportError:
        errors = fallback_validate(data, schema)
        if errors:
            print(f"❌ {target} failed validation (fallback checker):")
            for err in errors:
                print(f"   - {err}")
            return 1
        print(f"✅ {target} is valid (fallback checker; install `jsonschema` "
              f"for full validation).")
        return 0


if __name__ == "__main__":
    sys.exit(main())
