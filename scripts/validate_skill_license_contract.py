#!/usr/bin/env python3
"""Validate Creative Commons skill metadata against repository authority."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys


CANONICAL_LICENSE = (
    "Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International "
    "(CC BY-NC-SA 4.0)"
)
LICENSE_PATTERN = re.compile(r"^license:\s*(.*)$")


def frontmatter_license(path: Path) -> str | None:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return None

    for line in lines[1:]:
        if line.strip() == "---":
            return None
        match = LICENSE_PATTERN.match(line)
        if match:
            return match.group(1).strip().strip("\"'")
    return None


def creative_commons_mismatches(root: Path) -> list[tuple[Path, str]]:
    mismatches = []
    skill_files = (
        path
        for path in (root / "skills").rglob("*")
        if path.is_file() and path.name.lower() == "skill.md"
    )
    for path in sorted(skill_files):
        value = frontmatter_license(path)
        if value and value.startswith("Creative Commons") and value != CANONICAL_LICENSE:
            mismatches.append((path, value))
    return mismatches


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", type=Path, default=Path.cwd())
    args = parser.parse_args()

    mismatches = creative_commons_mismatches(args.root.resolve())
    if not mismatches:
        print("All Creative Commons skill licenses match repository authority.")
        return 0

    print("Creative Commons skill licenses contradict repository authority:", file=sys.stderr)
    for path, value in mismatches:
        print(f"- {path.relative_to(args.root.resolve())}: {value}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
