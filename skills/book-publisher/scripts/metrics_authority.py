#!/usr/bin/env python3
"""Validate and expose the canonical README metrics authority.

README publication uses ``docs/learning-graph/book-metrics.json`` for every
book-wide total. Filesystem scans may add observations that the canonical
schema does not define, but they never replace canonical fields.
"""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List


METRICS_RELATIVE_PATH = Path("docs/learning-graph/book-metrics.json")
METADATA_RELATIVE_PATH = Path("docs/learning-graph/book-metadata.json")
DERIVED_METRICS_PATHS = {
    METRICS_RELATIVE_PATH.as_posix(),
    METADATA_RELATIVE_PATH.as_posix(),
    "docs/learning-graph/book-metrics.md",
    "docs/learning-graph/chapter-metrics.md",
}
REQUIRED_METRICS = {
    "concepts": int,
    "chapters": int,
    "microsims": int,
    "stories": int,
    "glossaryTerms": int,
    "faqs": int,
    "quizQuestions": int,
    "chapterQuizzes": int,
    "chapterReferences": int,
    "references": int,
    "diagrams": int,
    "equations": int,
    "words": int,
    "links": int,
    "appendices": int,
    "mascotImages": int,
    "developmentStage": str,
    "equivalentPages": int,
}
REQUIRED_TOP_LEVEL = {
    "metricsVersion": str,
    "metricsGeneratedBy": str,
    "metricsGeneratedOn": str,
    "metricsGeneratedOnISO": str,
    "metrics": dict,
}
ALLOWED_TOP_LEVEL = {"$schema", *REQUIRED_TOP_LEVEL}


def _failure(state: str, path: Path, issues: List[str], **extra: Any) -> Dict[str, Any]:
    return {
        "valid": False,
        "state": state,
        "path": path.as_posix(),
        "issues": issues,
        "newer_sources": [],
        "metrics": {},
        "provenance": {},
        "identity": {},
        **extra,
    }


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _has_symlink_component(repo_root: Path, relative_path: Path) -> bool:
    current = repo_root
    for part in relative_path.parts:
        current = current / part
        if current.is_symlink():
            return True
    return False


def _validate_payload(payload: Any) -> List[str]:
    issues: List[str] = []
    if not isinstance(payload, dict):
        return ["root: expected an object"]

    unexpected = sorted(set(payload) - ALLOWED_TOP_LEVEL)
    if unexpected:
        issues.append("root: unexpected keys: " + ", ".join(unexpected))

    for key, expected_type in REQUIRED_TOP_LEVEL.items():
        value = payload.get(key)
        if not isinstance(value, expected_type):
            issues.append(f"{key}: expected {expected_type.__name__}")

    version = payload.get("metricsVersion")
    if isinstance(version, str) and not re.fullmatch(r"\d+\.\d+", version):
        issues.append("metricsVersion: expected major.minor")

    generated_iso = payload.get("metricsGeneratedOnISO")
    if isinstance(generated_iso, str):
        try:
            datetime.fromisoformat(generated_iso.replace("Z", "+00:00"))
        except ValueError:
            issues.append("metricsGeneratedOnISO: expected an ISO 8601 timestamp")

    metrics = payload.get("metrics")
    if not isinstance(metrics, dict):
        return issues

    for key, expected_type in REQUIRED_METRICS.items():
        if key not in metrics:
            issues.append(f"metrics.{key}: missing required field")
            continue
        value = metrics[key]
        if expected_type is int:
            if isinstance(value, bool) or not isinstance(value, int):
                issues.append(f"metrics.{key}: expected a non-negative integer")
            elif value < 0:
                issues.append(f"metrics.{key}: expected a non-negative integer")
        elif not isinstance(value, expected_type):
            issues.append(f"metrics.{key}: expected {expected_type.__name__}")

    for key, value in metrics.items():
        if key in REQUIRED_METRICS:
            continue
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            issues.append(
                f"metrics.{key}: additional metrics must be non-negative integers"
            )

    return issues


def _source_files(repo_root: Path) -> Iterable[Path]:
    docs = repo_root / "docs"
    if docs.is_dir():
        for path in docs.rglob("*"):
            if not path.is_file() or path.is_symlink():
                continue
            relative = path.relative_to(repo_root).as_posix()
            if relative not in DERIVED_METRICS_PATHS:
                yield path
    mkdocs = repo_root / "mkdocs.yml"
    if mkdocs.is_file() and not mkdocs.is_symlink():
        yield mkdocs


def _relative_paths(repo_root: Path, paths: Iterable[Path]) -> List[str]:
    return sorted(path.relative_to(repo_root).as_posix() for path in paths)


def _run_git(repo_root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    command = ["git", "-C", str(repo_root), *arguments]
    try:
        return subprocess.run(
            command,
            capture_output=True,
            check=False,
            text=True,
        )
    except OSError as error:
        return subprocess.CompletedProcess(command, 127, "", str(error))


def _filter_source_paths(paths: Iterable[str]) -> List[str]:
    return sorted(
        {
            path.strip()
            for path in paths
            if path.strip()
            and path.strip() not in DERIVED_METRICS_PATHS
            and (
                path.strip() == "mkdocs.yml"
                or path.strip().startswith("docs/")
            )
        }
    )


def _git_freshness(repo_root: Path) -> Dict[str, Any] | None:
    """Return Git-aware freshness, or None when Git cannot prove it."""
    top_level = _run_git(repo_root, "rev-parse", "--show-toplevel")
    if top_level.returncode != 0:
        return None
    try:
        if Path(top_level.stdout.strip()).resolve() != repo_root:
            return None
    except OSError:
        return None

    metrics_path = METRICS_RELATIVE_PATH.as_posix()
    tracked = _run_git(repo_root, "ls-files", "--error-unmatch", "--", metrics_path)
    if tracked.returncode != 0:
        return None

    canonical_dirty = _run_git(repo_root, "diff", "--quiet", "HEAD", "--", metrics_path)
    if canonical_dirty.returncode == 1:
        return None
    if canonical_dirty.returncode != 0:
        return None

    canonical_commit = _run_git(
        repo_root, "log", "-1", "--format=%H", "--", metrics_path
    )
    if canonical_commit.returncode != 0 or not canonical_commit.stdout.strip():
        return None

    changed_after = _run_git(
        repo_root,
        "diff",
        "--name-only",
        "--diff-filter=ACMRD",
        f"{canonical_commit.stdout.strip()}..HEAD",
        "--",
        "docs",
        "mkdocs.yml",
    )
    working_changes = _run_git(
        repo_root,
        "diff",
        "--name-only",
        "--diff-filter=ACMRD",
        "HEAD",
        "--",
        "docs",
        "mkdocs.yml",
    )
    untracked = _run_git(
        repo_root,
        "ls-files",
        "--others",
        "--exclude-standard",
        "--",
        "docs",
        "mkdocs.yml",
    )
    commands = (changed_after, working_changes, untracked)
    if any(command.returncode != 0 for command in commands):
        return None

    sources = _filter_source_paths(
        line
        for command in commands
        for line in command.stdout.splitlines()
    )
    return {"mode": "git", "newer_sources": sources}


def _read_mkdocs_identity(repo_root: Path) -> Dict[str, Dict[str, str]]:
    path = repo_root / "mkdocs.yml"
    if not path.is_file() or path.is_symlink():
        return {}
    identity: Dict[str, Dict[str, str]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^(site_name|repo_url):\s*(.*?)\s*$", line)
        if not match:
            continue
        key, raw_value = match.groups()
        value = raw_value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            value = value[1:-1]
        if value:
            identity[key] = {
                "value": value,
                "provenance": f"mkdocs.yml#/{key}",
            }
    return identity


def _read_identity(repo_root: Path, metadata: Any) -> Dict[str, Any]:
    identity: Dict[str, Any] = {}
    if isinstance(metadata, dict):
        for key in ("title", "creator", "repository", "repoUrl", "siteUrl"):
            value = metadata.get(key)
            if isinstance(value, str) and value.strip():
                identity[key] = {
                    "value": value.strip(),
                    "provenance": f"{METADATA_RELATIVE_PATH.as_posix()}#/{key}",
                }
    identity.update(_read_mkdocs_identity(repo_root))
    return identity


def _identity_issues(identity: Dict[str, Any]) -> List[str]:
    issues: List[str] = []
    metadata_title = identity.get("title", {}).get("value")
    site_name = identity.get("site_name", {}).get("value")
    if metadata_title and site_name:
        normalize = lambda value: re.sub(r"\s+", " ", value).strip().casefold()
        if normalize(metadata_title) != normalize(site_name):
            issues.append(
                "book-metadata.json title disagrees with mkdocs.yml site_name"
            )

    metadata_repo = (
        identity.get("repository", {}).get("value")
        or identity.get("repoUrl", {}).get("value")
    )
    mkdocs_repo = identity.get("repo_url", {}).get("value")
    if metadata_repo and mkdocs_repo:
        normalize_url = lambda value: value.rstrip("/").removesuffix(".git").casefold()
        if normalize_url(metadata_repo) != normalize_url(mkdocs_repo):
            issues.append(
                "book-metadata.json repository disagrees with mkdocs.yml repo_url"
            )
    return issues


def inspect_repository(repo_root: Path | str) -> Dict[str, Any]:
    """Return a fail-closed canonical metrics authority report."""
    root = Path(repo_root).resolve()
    metrics_path = root / METRICS_RELATIVE_PATH
    relative_metrics_path = METRICS_RELATIVE_PATH

    if _has_symlink_component(root, METRICS_RELATIVE_PATH):
        return _failure(
            "unsafe-path",
            relative_metrics_path,
            ["Canonical metrics path contains a symbolic-link component"],
        )

    if not metrics_path.is_file() or metrics_path.is_symlink():
        return _failure(
            "missing",
            relative_metrics_path,
            [f"Missing canonical metrics: {relative_metrics_path.as_posix()}"],
        )

    try:
        payload = _load_json(metrics_path)
    except (OSError, json.JSONDecodeError) as error:
        return _failure(
            "malformed",
            relative_metrics_path,
            [f"Could not parse canonical metrics: {error}"],
        )

    issues = _validate_payload(payload)
    if issues:
        return _failure("invalid", relative_metrics_path, issues)

    metadata_path = root / METADATA_RELATIVE_PATH
    metadata: Any = None
    if metadata_path.exists():
        if (
            not metadata_path.is_file()
            or _has_symlink_component(root, METADATA_RELATIVE_PATH)
        ):
            return _failure(
                "inconsistent",
                relative_metrics_path,
                [f"{METADATA_RELATIVE_PATH.as_posix()} is not a regular file"],
            )
        try:
            metadata = _load_json(metadata_path)
        except (OSError, json.JSONDecodeError) as error:
            return _failure(
                "inconsistent",
                relative_metrics_path,
                [f"Could not parse {METADATA_RELATIVE_PATH.as_posix()}: {error}"],
            )
        if not isinstance(metadata, dict):
            return _failure(
                "inconsistent",
                relative_metrics_path,
                [f"{METADATA_RELATIVE_PATH.as_posix()} must contain an object"],
            )
        if "metrics" in metadata and metadata["metrics"] != payload["metrics"]:
            return _failure(
                "inconsistent",
                relative_metrics_path,
                [
                    f"{METADATA_RELATIVE_PATH.as_posix()} metrics disagree with "
                    f"{METRICS_RELATIVE_PATH.as_posix()}"
                ],
            )
        for key in ("metricsGeneratedBy", "metricsGeneratedOn"):
            if key in metadata and metadata[key] != payload[key]:
                return _failure(
                    "inconsistent",
                    relative_metrics_path,
                    [
                        f"{METADATA_RELATIVE_PATH.as_posix()} {key} disagrees with "
                        f"{METRICS_RELATIVE_PATH.as_posix()}"
                    ],
                )

    identity = _read_identity(root, metadata)
    identity_issues = _identity_issues(identity)
    if identity_issues:
        return _failure(
            "inconsistent",
            relative_metrics_path,
            identity_issues,
            identity=identity,
        )

    git_freshness = _git_freshness(root)
    if git_freshness is not None:
        freshness_mode = "git"
        relative_sources = git_freshness["newer_sources"]
    else:
        freshness_mode = "mtime"
        metrics_mtime = metrics_path.stat().st_mtime
        newer_sources = [
            path for path in _source_files(root) if path.stat().st_mtime > metrics_mtime
        ]
        relative_sources = _relative_paths(root, newer_sources)
    if relative_sources:
        return _failure(
            "stale",
            relative_metrics_path,
            [
                "Canonical metrics are older than source content; run "
                "bk-generate-book-metrics before publishing"
            ],
            newer_sources=relative_sources,
            freshnessMode=freshness_mode,
        )

    metrics = payload["metrics"]
    source = METRICS_RELATIVE_PATH.as_posix()
    return {
        "valid": True,
        "state": "canonical",
        "path": source,
        "issues": [],
        "newer_sources": [],
        "freshnessMode": freshness_mode,
        "metricsVersion": payload["metricsVersion"],
        "metricsGeneratedBy": payload["metricsGeneratedBy"],
        "metricsGeneratedOn": payload["metricsGeneratedOn"],
        "metricsGeneratedOnISO": payload["metricsGeneratedOnISO"],
        "metrics": metrics,
        "provenance": {
            key: f"{source}#/metrics/{key}" for key in metrics
        },
        "identity": identity,
    }
