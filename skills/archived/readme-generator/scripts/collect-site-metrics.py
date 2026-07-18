#!/usr/bin/env python3
"""Archived entry point delegated to the active canonical metrics contract."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ACTIVE_SCRIPT = (
    Path(__file__).parents[3]
    / "book-publisher"
    / "scripts"
    / "collect-site-metrics.py"
)
SPEC = importlib.util.spec_from_file_location("active_collect_site_metrics", ACTIVE_SCRIPT)
active = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(active)

collect_metrics = active.collect_metrics
format_metrics_table = active.format_metrics_table


if __name__ == "__main__":
    raise SystemExit(active.main())
