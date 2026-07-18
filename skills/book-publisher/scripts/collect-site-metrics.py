#!/usr/bin/env python3
"""Collect canonical README metrics plus explicitly supplemental observations.

Book-wide totals come only from ``docs/learning-graph/book-metrics.json``.
Filesystem scanning is restricted to values absent from that schema: Markdown
file count, fenced code-block count, and image-asset count.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict


AUTHORITY_SCRIPT = Path(__file__).with_name("metrics_authority.py")
AUTHORITY_SPEC = importlib.util.spec_from_file_location(
    "book_publisher_metrics_authority", AUTHORITY_SCRIPT
)
metrics_authority = importlib.util.module_from_spec(AUTHORITY_SPEC)
assert AUTHORITY_SPEC.loader is not None
AUTHORITY_SPEC.loader.exec_module(metrics_authority)

IMAGE_EXTENSIONS = ("gif", "jpeg", "jpg", "png", "svg", "webp")


class MetricsAuthorityError(ValueError):
    """Raised when canonical metrics cannot be trusted for publication."""


def count_fenced_code_blocks(content: str) -> int:
    """Count opening fenced code blocks without counting closing fences."""
    fence_pattern = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})([^\r\n]*)$")
    open_character = None
    open_length = 0
    count = 0
    for line in content.splitlines():
        match = fence_pattern.match(line)
        if not match:
            continue
        marker, info = match.groups()
        character = marker[0]
        if open_character is not None:
            if character == open_character and len(marker) >= open_length and not info.strip():
                open_character = None
                open_length = 0
            continue
        if character == "`" and "`" in info:
            continue
        count += 1
        open_character = character
        open_length = len(marker)
    return count


def collect_supplemental_metrics(docs_path: Path) -> Dict[str, Any]:
    markdown_files = sorted(path for path in docs_path.rglob("*.md") if path.is_file())
    code_blocks = 0
    for path in markdown_files:
        code_blocks += count_fenced_code_blocks(path.read_text(encoding="utf-8"))

    by_type: Dict[str, int] = {}
    for extension in IMAGE_EXTENSIONS:
        by_type[extension] = sum(
            1 for path in docs_path.rglob(f"*.{extension}") if path.is_file()
        )

    return {
        "markdownFiles": len(markdown_files),
        "codeBlocks": code_blocks,
        "imageAssets": sum(by_type.values()),
        "imageAssetsByType": by_type,
    }


def collect_metrics(repo_path: str = ".") -> Dict[str, Any]:
    """Return canonical and supplemental metrics with field-level provenance."""
    repo = Path(repo_path).resolve()
    authority = metrics_authority.inspect_repository(repo)
    if not authority["valid"]:
        detail = "; ".join(authority["issues"])
        if authority.get("newer_sources"):
            preview = ", ".join(authority["newer_sources"][:5])
            suffix = " ..." if len(authority["newer_sources"]) > 5 else ""
            detail += f"; newer sources: {preview}{suffix}"
        raise MetricsAuthorityError(f"Metrics authority {authority['state']}: {detail}")

    supplemental = collect_supplemental_metrics(repo / "docs")
    return {
        "repository": {"path": str(repo), "name": repo.name},
        "canonical": {
            "metrics": authority["metrics"],
            "provenance": authority["provenance"],
            "authority": {
                key: authority[key]
                for key in (
                    "path",
                    "metricsVersion",
                    "metricsGeneratedBy",
                    "metricsGeneratedOn",
                    "metricsGeneratedOnISO",
                )
            },
        },
        "identity": authority["identity"],
        "supplemental": supplemental,
        "supplementalProvenance": {
            "markdownFiles": "filesystem:docs/**/*.md",
            "codeBlocks": "filesystem:docs/**/*.md",
            "imageAssets": "filesystem:docs/**/*.{gif,jpeg,jpg,png,svg,webp}",
            "imageAssetsByType": "filesystem:docs/**/*.{gif,jpeg,jpg,png,svg,webp}",
        },
    }


def format_metrics_table(report: Dict[str, Any]) -> str:
    """Format a README table without re-deriving canonical totals."""
    metrics = report["canonical"]["metrics"]
    supplemental = report["supplemental"]
    rows = (
        ("Concepts in Learning Graph", metrics["concepts"]),
        ("Chapters", metrics["chapters"]),
        ("Markdown Files", supplemental["markdownFiles"]),
        ("Total Words", metrics["words"]),
        ("MicroSims", metrics["microsims"]),
        ("Glossary Terms", metrics["glossaryTerms"]),
        ("FAQ Questions", metrics["faqs"]),
        ("Quiz Questions", metrics["quizQuestions"]),
        ("Equations", metrics["equations"]),
        ("Images", supplemental["imageAssets"]),
        ("References", metrics["references"]),
    )
    lines = ["| Metric | Count |", "| --- | ---: |"]
    lines.extend(f"| {label} | {value:,} |" for label, value in rows)
    return "\n".join(lines) + "\n"


def main() -> int:
    repo_path = sys.argv[1] if len(sys.argv) > 1 else "."
    try:
        report = collect_metrics(repo_path)
    except MetricsAuthorityError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    print("\n--- Formatted Table ---", file=sys.stderr)
    print(format_metrics_table(report), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
