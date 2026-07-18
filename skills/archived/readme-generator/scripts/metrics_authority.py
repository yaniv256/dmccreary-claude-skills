#!/usr/bin/env python3
"""Compatibility copy of the active README canonical metrics authority."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ACTIVE_MODULE = (
    Path(__file__).parents[3]
    / "book-publisher"
    / "scripts"
    / "metrics_authority.py"
)
SPEC = importlib.util.spec_from_file_location("active_readme_metrics_authority", ACTIVE_MODULE)
active = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(active)

inspect_repository = active.inspect_repository
METRICS_RELATIVE_PATH = active.METRICS_RELATIVE_PATH
