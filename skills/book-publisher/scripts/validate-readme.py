#!/usr/bin/env python3
"""
README Validation Script

Validates README.md files for:
- Required sections present
- Repository-local link targets and Markdown anchors
- External link syntax (reachability remains a separate check)
- Valid badge URLs
- Proper markdown formatting
- Common issues

Usage:
    python validate-readme.py [path/to/README.md]

Output:
    Validation report with score and recommendations
"""

import argparse
import html
import importlib.util
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import unquote, urlparse, urlsplit


AUTHORITY_SCRIPT = Path(__file__).with_name("license_authority.py")
AUTHORITY_SPEC = importlib.util.spec_from_file_location(
    "book_publisher_license_authority", AUTHORITY_SCRIPT
)
license_authority = importlib.util.module_from_spec(AUTHORITY_SPEC)
assert AUTHORITY_SPEC.loader is not None
AUTHORITY_SPEC.loader.exec_module(license_authority)

METRICS_AUTHORITY_SCRIPT = Path(__file__).with_name("metrics_authority.py")
METRICS_AUTHORITY_SPEC = importlib.util.spec_from_file_location(
    "book_publisher_metrics_authority", METRICS_AUTHORITY_SCRIPT
)
metrics_authority = importlib.util.module_from_spec(METRICS_AUTHORITY_SPEC)
assert METRICS_AUTHORITY_SPEC.loader is not None
METRICS_AUTHORITY_SPEC.loader.exec_module(metrics_authority)

README_METRIC_LABELS = {
    "concepts in learning graph": "concepts",
    "concepts": "concepts",
    "chapters": "chapters",
    "total words": "words",
    "words": "words",
    "microsims": "microsims",
    "glossary terms": "glossaryTerms",
    "faq questions": "faqs",
    "faqs": "faqs",
    "quiz questions": "quizQuestions",
    "chapter quizzes": "chapterQuizzes",
    "chapter references": "chapterReferences",
    "references": "references",
    "diagrams": "diagrams",
    "equations": "equations",
    "links": "links",
    "appendices": "appendices",
    "mascot images": "mascotImages",
    "equivalent pages": "equivalentPages",
}

def check_required_sections(
    content: str,
) -> Tuple[List[str], List[str], List[str], List[str]]:
    """Check for required README sections."""
    required = [
        'overview',
        'getting started',
        'contact'
    ]

    recommended = [
        'installation',
        'usage',
        'contributing',
        'acknowledgements',
        'issues',
        'license'
    ]

    found_required = []
    found_recommended = []
    missing_required = []
    missing_recommended = []

    section_headings = extract_section_headings(content)

    for section in required:
        if section in section_headings:
            found_required.append(section)
        else:
            missing_required.append(section)

    for section in recommended:
        if section in section_headings:
            found_recommended.append(section)
        else:
            missing_recommended.append(section)

    return (found_required, missing_required, found_recommended, missing_recommended)


def normalize_section_heading(heading: str) -> str:
    """Normalize a Markdown heading for exact section-name matching."""
    heading = re.sub(r"\s+#+\s*$", "", heading.strip())
    return re.sub(r"[-_\s]+", " ", heading).strip().lower()


def markdown_visible_lines(content: str) -> List[str]:
    """Mask fenced, indented-code, and HTML-comment content line-for-line."""
    lines = content.splitlines()
    visible: List[str] = []
    open_fence_character: Optional[str] = None
    open_fence_length = 0
    in_html_comment = False

    for line in lines:
        fence_match = re.match(r"^[ \t]{0,3}(`{3,}|~{3,})([^\r\n]*)$", line)
        if open_fence_character is not None:
            if fence_match:
                marker, info_string = fence_match.groups()
                if (
                    marker[0] == open_fence_character
                    and len(marker) >= open_fence_length
                    and not info_string.strip()
                ):
                    open_fence_character = None
                    open_fence_length = 0
            visible.append("")
            continue

        if fence_match:
            marker, info_string = fence_match.groups()
            if not (marker[0] == "`" and "`" in info_string):
                open_fence_character = marker[0]
                open_fence_length = len(marker)
                visible.append("")
                continue

        cleaned: List[str] = []
        cursor = 0
        while cursor < len(line):
            if in_html_comment:
                end = line.find("-->", cursor)
                if end < 0:
                    cursor = len(line)
                    break
                in_html_comment = False
                cursor = end + 3
                continue
            start = line.find("<!--", cursor)
            if start < 0:
                cleaned.append(line[cursor:])
                break
            cleaned.append(line[cursor:start])
            in_html_comment = True
            cursor = start + 4

        cleaned_line = "".join(cleaned)
        if re.match(r"^(?: {4}|\t)", cleaned_line):
            visible.append("")
        else:
            visible.append(cleaned_line)

    return visible


def extract_markdown_headings(content: str) -> List[Dict[str, object]]:
    """Extract structural ATX and Setext headings from visible Markdown."""
    lines = content.splitlines()
    visible = markdown_visible_lines(content)
    headings: List[Dict[str, object]] = []

    for index, line in enumerate(visible):
        atx_match = re.match(r"^[ \t]{0,3}(#{1,6})[ \t]+(.+?)\s*$", line)
        if atx_match:
            headings.append(
                {
                    "text": re.sub(r"\s+#+\s*$", "", atx_match.group(2)).strip(),
                    "level": len(atx_match.group(1)),
                    "line_index": index,
                    "body_start": index + 1,
                }
            )
            continue

        if index == 0 or not line.strip():
            continue
        setext_match = re.match(r"^[ \t]{0,3}(=+|-+)[ \t]*$", line)
        if setext_match and visible[index - 1].strip():
            headings.append(
                {
                    "text": lines[index - 1].strip(),
                    "level": 1 if setext_match.group(1).startswith("=") else 2,
                    "line_index": index - 1,
                    "body_start": index + 1,
                }
            )

    return headings


def extract_section_headings(content: str) -> Set[str]:
    """Extract normalized section names from structural Markdown headings."""
    return {
        normalize_section_heading(str(heading["text"]))
        for heading in extract_markdown_headings(content)
    }


def _heading_rendered_text(value: str) -> str:
    """Remove Markdown link destinations while preserving rendered labels."""
    output: List[str] = []
    bracket_pairs = _bracket_pairs(value)
    index = 0
    while index < len(value):
        is_image = value.startswith("![", index)
        opening = index + 1 if is_image else index
        if value[opening : opening + 1] != "[":
            output.append(value[index])
            index += 1
            continue

        closing = bracket_pairs.get(opening)
        if closing is None:
            output.append(value[index])
            index += 1
            continue

        label = value[opening + 1 : closing]
        cursor = closing + 1
        end = cursor
        if cursor < len(value) and value[cursor] == "(":
            _, parsed_end, _ = _parse_inline_destination(value, cursor)
            if parsed_end is not None:
                end = parsed_end + 1
        elif cursor < len(value) and value[cursor] == "[":
            reference_end = bracket_pairs.get(cursor)
            if reference_end is not None:
                end = reference_end + 1

        output.append(_heading_rendered_text(label))
        index = max(end, closing + 1)
    return "".join(output)


def github_heading_slug(heading: str) -> str:
    """Generate the base GitHub-style anchor slug for a Markdown heading."""
    value = html.unescape(heading).strip().lower()
    value = re.sub(r"<[^>]+>", "", value)
    value = _heading_rendered_text(value)
    value = value.replace("`", "").replace("*", "").replace("~", "")
    kept = []
    for character in value:
        category = unicodedata.category(character)
        if character in {"-", "_"} or character.isspace():
            kept.append(character)
        elif not category.startswith(("P", "S", "C")):
            kept.append(character)
    return re.sub(r"\s", "-", "".join(kept))


def extract_heading_anchors(content: str) -> Set[str]:
    """Return GitHub-style heading anchors, including duplicate suffixes."""
    counts: Dict[str, int] = {}
    anchors: Set[str] = set()
    for heading in extract_markdown_headings(content):
        base = github_heading_slug(str(heading["text"]))
        occurrence = counts.get(base, 0)
        counts[base] = occurrence + 1
        anchors.add(base if occurrence == 0 else f"{base}-{occurrence}")
    return anchors


def _mask_inline_code(line: str) -> str:
    """Blank matched backtick code spans while preserving character offsets."""
    characters = list(line)
    index = 0
    while index < len(line):
        if line[index] != "`":
            index += 1
            continue
        run_end = index
        while run_end < len(line) and line[run_end] == "`":
            run_end += 1
        marker = line[index:run_end]
        closing = line.find(marker, run_end)
        if closing < 0:
            index = run_end
            continue
        for masked_index in range(index, closing + len(marker)):
            characters[masked_index] = " "
        index = closing + len(marker)
    return "".join(characters)


def _bracket_pairs(text: str) -> Dict[int, int]:
    """Pair unescaped square brackets in one linear pass."""
    stack: List[int] = []
    pairs: Dict[int, int] = {}
    index = 0
    while index < len(text):
        if text[index] == "\\":
            index += 2
            continue
        if text[index] == "[":
            stack.append(index)
        elif text[index] == "]":
            if stack:
                opening = stack.pop()
                pairs[opening] = index
        index += 1
    return pairs


def _unescape_markdown_destination(destination: str) -> str:
    return re.sub(r"\\([\\`*{}\[\]()#+.!_<>-])", r"\1", destination)


def _parse_reference_destination(value: str) -> Optional[str]:
    value = value.strip()
    if not value:
        return None
    if value.startswith("<"):
        closing = value.find(">", 1)
        if closing < 0:
            return None
        return _unescape_markdown_destination(value[1:closing])

    depth = 0
    index = 0
    while index < len(value):
        character = value[index]
        if character == "\\":
            index += 2
            continue
        if character == "(":
            depth += 1
        elif character == ")":
            if depth == 0:
                break
            depth -= 1
        elif character.isspace() and depth == 0:
            break
        index += 1
    if index == 0 or depth != 0:
        return None
    return _unescape_markdown_destination(value[:index])


def _parse_inline_destination(
    text: str,
    opening_parenthesis: int,
) -> Tuple[Optional[str], Optional[int], bool]:
    index = opening_parenthesis + 1
    while index < len(text) and text[index].isspace():
        index += 1
    if index >= len(text):
        return None, None, True

    if text[index] == "<":
        closing_angle = text.find(">", index + 1)
        if closing_angle < 0:
            return text[index + 1 :], None, True
        destination = text[index + 1 : closing_angle]
        cursor = closing_angle + 1
    else:
        start = index
        depth = 0
        while index < len(text):
            character = text[index]
            if character == "\\":
                index += 2
                continue
            if character == "(":
                depth += 1
            elif character == ")":
                if depth == 0:
                    return (
                        _unescape_markdown_destination(text[start:index]),
                        index,
                        False,
                    )
                depth -= 1
            elif character.isspace() and depth == 0:
                break
            index += 1
        if index == start or depth != 0:
            return text[start:index], None, True
        destination = text[start:index]
        cursor = index

    remainder = text[cursor:]
    closing = remainder.find(")")
    if closing < 0:
        return _unescape_markdown_destination(destination), None, True
    between = remainder[:closing].strip()
    if between and not (
        (between.startswith('"') and between.endswith('"'))
        or (between.startswith("'") and between.endswith("'"))
        or (between.startswith("(") and between.endswith(")"))
    ):
        raw = text[opening_parenthesis + 1 : cursor + closing]
        return _unescape_markdown_destination(raw.strip()), cursor + closing, True
    return (
        _unescape_markdown_destination(destination),
        cursor + closing,
        False,
    )


def _normalize_reference_label(label: str) -> str:
    return re.sub(r"\s+", " ", label.strip()).casefold()


def _extract_nested_image_entries(
    label: str,
    references: Dict[str, str],
    line_number: int,
) -> List[Dict[str, object]]:
    """Extract images nested inside a link label, as used by badge markup."""
    entries: List[Dict[str, object]] = []
    bracket_pairs = _bracket_pairs(label)
    index = 0
    while index < len(label):
        opening = label.find("![", index)
        if opening < 0:
            break
        closing = bracket_pairs.get(opening + 1)
        if closing is None:
            break

        alt_text = label[opening + 2 : closing]
        cursor = closing + 1
        destination: Optional[str] = None
        malformed = False
        end = cursor
        if cursor < len(label) and label[cursor] == "(":
            destination, parsed_end, malformed = _parse_inline_destination(
                label,
                cursor,
            )
            end = parsed_end + 1 if parsed_end is not None else len(label)
        elif cursor < len(label) and label[cursor] == "[":
            reference_end = bracket_pairs.get(cursor)
            if reference_end is not None:
                reference_label = label[cursor + 1 : reference_end] or alt_text
                destination = references.get(
                    _normalize_reference_label(reference_label)
                )
                end = reference_end + 1
        else:
            destination = references.get(_normalize_reference_label(alt_text))

        if destination is not None:
            entries.append(
                {
                    "text": alt_text,
                    "destination": destination,
                    "element": "image",
                    "line": line_number,
                    "malformed": malformed,
                }
            )
        index = max(end, closing + 1)
    return entries


def _extract_multiline_inline_entries(
    visible: List[str],
    references: Dict[str, str],
    definition_lines: Set[int],
) -> List[Dict[str, object]]:
    """Extract inline destinations whose Markdown syntax spans lines."""
    lines = [
        "" if line_number in definition_lines else _mask_inline_code(line)
        for line_number, line in enumerate(visible, start=1)
    ]
    text = "\n".join(lines)
    entries: List[Dict[str, object]] = []
    bracket_pairs = _bracket_pairs(text)
    index = 0
    while index < len(text):
        is_image = text.startswith("![", index)
        opening = index + 1 if is_image else index
        if text[opening : opening + 1] != "[":
            index += 1
            continue
        closing = bracket_pairs.get(opening)
        if closing is None or closing + 1 >= len(text) or text[closing + 1] != "(":
            index += 1
            continue

        destination, parsed_end, malformed = _parse_inline_destination(
            text,
            closing + 1,
        )
        end = parsed_end + 1 if parsed_end is not None else len(text)
        if destination is None or "\n" not in text[index:end]:
            index = max(end, closing + 1)
            continue

        label = text[opening + 1 : closing]
        line_number = text.count("\n", 0, index) + 1
        if not is_image and "![" in label:
            entries.extend(
                _extract_nested_image_entries(label, references, line_number)
            )
        entries.append(
            {
                "text": label,
                "destination": destination,
                "element": "image" if is_image else "link",
                "line": line_number,
                "malformed": malformed,
            }
        )
        index = max(end, closing + 1)
    return entries


def extract_markdown_link_entries(content: str) -> List[Dict[str, object]]:
    """Extract inline, reference, image, and autolink destinations."""
    visible = markdown_visible_lines(content)
    references: Dict[str, str] = {}
    definition_lines: Set[int] = set()
    definition_pattern = re.compile(r"^[ \t]{0,3}\[([^\]]+)\]:[ \t]*(.*)$")

    for line_number, line in enumerate(visible, start=1):
        match = definition_pattern.match(line)
        if not match:
            continue
        destination = _parse_reference_destination(match.group(2))
        if destination is not None:
            references.setdefault(
                _normalize_reference_label(match.group(1)),
                destination,
            )
            definition_lines.add(line_number)

    entries: List[Dict[str, object]] = []
    for line_number, visible_line in enumerate(visible, start=1):
        if line_number in definition_lines:
            continue
        line = _mask_inline_code(visible_line)
        bracket_pairs = _bracket_pairs(line)
        occupied_spans: List[Tuple[int, int]] = []
        index = 0
        while index < len(line):
            is_image = line.startswith("![", index)
            opening = index + 1 if is_image else index
            if line[opening : opening + 1] != "[":
                index += 1
                continue
            closing = bracket_pairs.get(opening)
            if closing is None:
                index += 1
                continue
            label = line[opening + 1 : closing]
            cursor = closing + 1
            destination: Optional[str] = None
            malformed = False
            end = cursor

            if cursor < len(line) and line[cursor] == "(":
                destination, parsed_end, malformed = _parse_inline_destination(
                    line,
                    cursor,
                )
                end = parsed_end + 1 if parsed_end is not None else len(line)
            elif cursor < len(line) and line[cursor] == "[":
                reference_end = bracket_pairs.get(cursor)
                if reference_end is not None:
                    reference_label = line[cursor + 1 : reference_end] or label
                    destination = references.get(
                        _normalize_reference_label(reference_label)
                    )
                    end = reference_end + 1
            else:
                destination = references.get(_normalize_reference_label(label))

            if destination is not None:
                if not is_image and "![" in label:
                    entries.extend(
                        _extract_nested_image_entries(label, references, line_number)
                    )
                entries.append(
                    {
                        "text": label,
                        "destination": destination,
                        "element": "image" if is_image else "link",
                        "line": line_number,
                        "malformed": malformed,
                    }
                )
                occupied_spans.append((index, max(end, closing + 1)))
                index = max(end, closing + 1)
            else:
                index = closing + 1

        autolink_pattern = re.compile(
            r"<((?:https?://|mailto:)[^<>\s]+|"
            r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
            r"[A-Za-z0-9.-]+\.[A-Za-z]{2,})>"
        )
        for match in autolink_pattern.finditer(line):
            if any(start <= match.start() < end for start, end in occupied_spans):
                continue
            destination = match.group(1)
            if "@" in destination and not destination.startswith("mailto:"):
                destination = f"mailto:{destination}"
            entries.append(
                {
                    "text": match.group(1),
                    "destination": destination,
                    "element": "link",
                    "line": line_number,
                    "malformed": False,
                }
            )

    entries.extend(
        _extract_multiline_inline_entries(visible, references, definition_lines)
    )
    return entries


def extract_links(content: str) -> List[Tuple[str, str]]:
    """Compatibility wrapper returning Markdown link text and destinations."""
    return [
        (str(entry["text"]), str(entry["destination"]))
        for entry in extract_markdown_link_entries(content)
    ]

def validate_url_format(url: str) -> bool:
    """Validate URL format (basic check)."""
    try:
        candidate = url.strip()
        if not candidate or re.search(r"[\x00-\x20]", candidate):
            return False
        result = urlparse(candidate)
        if result.scheme:
            return result.scheme in {"http", "https", "mailto"}
        # Markdown destinations commonly use bare repository-relative paths.
        return bool(result.path or result.fragment or result.query)
    except ValueError:
        return False


def _validate_link_destination(
    destination: str,
    readme_path: Path,
    repo_root: Path,
    malformed: bool = False,
) -> Dict[str, object]:
    candidate = html.unescape(destination.strip())
    if malformed or not candidate or re.search(r"[\x00-\x1f\x7f]", candidate):
        return {"valid": False, "kind": "invalid", "reason": "invalid-destination"}

    try:
        parsed = urlsplit(candidate)
    except ValueError:
        return {"valid": False, "kind": "invalid", "reason": "invalid-destination"}

    scheme = parsed.scheme.lower()
    if scheme in {"http", "https"}:
        try:
            hostname = parsed.hostname
            parsed.port
        except ValueError:
            return {"valid": False, "kind": "external", "reason": "invalid-host"}
        if not parsed.netloc or not hostname:
            return {"valid": False, "kind": "external", "reason": "missing-host"}
        if re.search(r"\s", candidate):
            return {"valid": False, "kind": "external", "reason": "invalid-destination"}
        return {
            "valid": True,
            "kind": "external",
            "reason": None,
            "reachability_verified": False,
        }
    if scheme == "mailto":
        address = parsed.path
        if not address or "@" not in address or re.search(r"\s", address):
            return {"valid": False, "kind": "mail", "reason": "invalid-destination"}
        return {"valid": True, "kind": "mail", "reason": None}
    if scheme:
        return {"valid": False, "kind": "invalid", "reason": "unsupported-scheme"}
    if parsed.netloc:
        try:
            hostname = parsed.hostname
            parsed.port
        except ValueError:
            return {"valid": False, "kind": "external", "reason": "invalid-host"}
        if not hostname:
            return {"valid": False, "kind": "external", "reason": "missing-host"}
        return {
            "valid": True,
            "kind": "external",
            "reason": None,
            "reachability_verified": False,
        }

    root = repo_root.resolve()
    raw_path = unquote(parsed.path)
    if "\\" in raw_path:
        return {"valid": False, "kind": "local", "reason": "invalid-destination"}

    if raw_path.startswith("/"):
        return {
            "valid": True,
            "kind": "origin-relative",
            "reason": None,
            "reachability_verified": False,
        }

    if raw_path:
        target = (readme_path.resolve().parent / raw_path).resolve()
    else:
        target = readme_path.resolve()

    if not target.is_relative_to(root):
        return {"valid": False, "kind": "local", "reason": "repository-escape"}
    if not target.exists():
        return {"valid": False, "kind": "local", "reason": "missing-local-target"}

    fragment = unquote(parsed.fragment).strip()
    if fragment and target.is_file() and target.suffix.lower() in {".md", ".markdown"}:
        try:
            target_content = target.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            return {
                "valid": False,
                "kind": "local",
                "reason": "unreadable-local-target",
                "target": target.relative_to(root).as_posix(),
            }
        anchors = extract_heading_anchors(target_content)
        if fragment not in anchors:
            return {
                "valid": False,
                "kind": "local",
                "reason": "missing-markdown-anchor",
                "target": target.relative_to(root).as_posix(),
            }

    return {
        "valid": True,
        "kind": "local",
        "reason": None,
        "target": target.relative_to(root).as_posix(),
    }


def check_links(content: str, readme_path: Path, repo_root: Path) -> Dict[str, object]:
    """Validate Markdown destinations against syntax and local repository state."""
    entries = extract_markdown_link_entries(content)
    checked_entries: List[Dict[str, object]] = []
    issues: List[Dict[str, object]] = []

    for entry in entries:
        result = _validate_link_destination(
            str(entry["destination"]),
            readme_path,
            repo_root,
            malformed=bool(entry.get("malformed")),
        )
        checked = {**entry, **result}
        checked_entries.append(checked)
        if not result["valid"]:
            issues.append(
                {
                    "destination": entry["destination"],
                    "line": entry["line"],
                    "reason": result["reason"],
                }
            )

    invalid = [str(issue["destination"]) for issue in issues]
    return {
        "total": len(checked_entries),
        "entries": checked_entries,
        "issues": issues,
        "invalid": invalid,
        "invalid_count": len(invalid),
        "local_verified_count": sum(
            1 for entry in checked_entries if entry["valid"] and entry["kind"] == "local"
        ),
        "external_unverified_count": sum(
            1
            for entry in checked_entries
            if entry["valid"] and entry["kind"] == "external"
        ),
        "origin_relative_unverified_count": sum(
            1
            for entry in checked_entries
            if entry["valid"] and entry["kind"] == "origin-relative"
        ),
        "mail_count": sum(
            1 for entry in checked_entries if entry["valid"] and entry["kind"] == "mail"
        ),
    }

def extract_badges(content: str) -> List[str]:
    """Extract badge URLs from content."""
    badges = []
    # Find badge patterns like [![...](badge-url)](link-url)
    badge_pattern = r'\[!\[([^\]]*)\]\(([^\)]+)\)\]\(([^\)]+)\)'
    matches = re.findall(badge_pattern, content)
    for match in matches:
        badges.append(match[1])  # badge URL
    return badges


def extract_claimed_license_ids(
    content: str,
    allow_bare_identifiers: bool = False,
) -> List[str]:
    """Extract common license names that the README affirmatively claims."""
    patterns = {
        "MIT": r"\bmit license\b|license[- :]+mit\b",
        "Apache-2.0": r"\bapache(?: license)?(?:[- ]+version)?[- ]*2\.0\b",
        "GPL-3.0": r"\b(?:gnu general public license|gpl)(?:[- v]+)3(?:\.0)?\b",
        "CC-BY-NC-SA-4.0": (
            r"\bcc[- ]by[- ]nc[- ]sa[- ]4\.0\b|"
            r"creative commons attribution-noncommercial-sharealike 4\.0"
        ),
        "CC-BY-NC-4.0": (
            r"\bcc[- ]by[- ]nc[- ]4\.0\b|"
            r"creative commons attribution-noncommercial 4\.0"
        ),
        "CC-BY-SA-4.0": (
            r"\bcc[- ]by[- ]sa[- ]4\.0\b|"
            r"creative commons attribution-sharealike 4\.0"
        ),
        "CC-BY-4.0": (
            r"\bcc[- ]by[- ]4\.0\b|creative commons attribution 4\.0"
        ),
    }
    if allow_bare_identifiers:
        bare_patterns = {
            "MIT": r"\bmit\b",
            "Apache-2.0": r"\bapache[- ]2\.0\b",
            "GPL-3.0": r"\bgpl[- v]?3(?:\.0)?\b",
            "CC-BY-NC-SA-4.0": r"\bcc[- ]by[- ]nc[- ]sa[- ]4\.0\b",
            "CC-BY-NC-4.0": r"\bcc[- ]by[- ]nc[- ]4\.0\b",
            "CC-BY-SA-4.0": r"\bcc[- ]by[- ]sa[- ]4\.0\b",
            "CC-BY-4.0": r"\bcc[- ]by[- ]4\.0\b",
        }
        patterns = {
            license_id: f"(?:{pattern})|(?:{bare_patterns[license_id]})"
            for license_id, pattern in patterns.items()
        }

    return [
        license_id
        for license_id, pattern in patterns.items()
        if re.search(pattern, content, flags=re.IGNORECASE)
    ]


def extract_named_section(content: str, section_name: str) -> str:
    """Return one Markdown section body, stopping at its next peer heading."""
    lines = content.splitlines()
    headings = extract_markdown_headings(content)
    wanted = normalize_section_heading(section_name)
    selected_index: Optional[int] = None

    for index, heading in enumerate(headings):
        if normalize_section_heading(str(heading["text"])) == wanted:
            selected_index = index
            break

    if selected_index is None:
        return ""

    selected = headings[selected_index]
    start = int(selected["body_start"])
    level = int(selected["level"])
    boundary = len(lines)
    for heading in headings[selected_index + 1 :]:
        if int(heading["level"]) <= level:
            boundary = int(heading["line_index"])
            break
    return "\n".join(lines[start:boundary])


def extract_readme_metric_claims(content: str) -> Dict[str, int]:
    """Extract canonical numeric claims from the README metrics table."""
    section = extract_named_section(content, "site status and metrics")
    if not section:
        return {}

    claims: Dict[str, int] = {}
    for line in section.splitlines():
        match = re.match(r"^\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$", line)
        if not match:
            continue
        label = normalize_section_heading(match.group(1))
        field = README_METRIC_LABELS.get(label)
        if not field:
            continue
        raw_value = match.group(2).strip().replace(",", "")
        if not re.fullmatch(r"\d+", raw_value):
            raise ValueError(
                f"README metrics table value for {field} must be a non-negative "
                "integer so it can be checked against canonical metrics"
            )
        value = int(raw_value)
        if field in claims and claims[field] != value:
            raise ValueError(
                f"README metrics table claims two values for {field}: "
                f"{claims[field]} and {value}"
            )
        claims[field] = value
    return claims


def check_metrics_authority(content: str, repo_root: Path) -> Dict[str, object]:
    """Validate README metric claims against the canonical metrics file."""
    try:
        claims = extract_readme_metric_claims(content)
    except ValueError as error:
        return {
            "valid": False,
            "state": "conflicting-claims",
            "checked_fields": 0,
            "claims": {},
            "issues": [str(error)],
            "provenance": {},
        }

    if not claims:
        return {
            "valid": True,
            "state": "not-applicable",
            "checked_fields": 0,
            "claims": {},
            "issues": [],
            "provenance": {},
        }

    authority = metrics_authority.inspect_repository(repo_root)
    if not authority["valid"]:
        return {
            "valid": False,
            "state": authority["state"],
            "checked_fields": 0,
            "claims": claims,
            "issues": authority["issues"],
            "newer_sources": authority.get("newer_sources", []),
            "provenance": {},
        }

    issues = []
    for field, claimed_value in claims.items():
        canonical_value = authority["metrics"][field]
        if claimed_value != canonical_value:
            issues.append(
                f"README {field} claim {claimed_value:,} disagrees with "
                f"canonical value {canonical_value:,}"
            )

    return {
        "valid": not issues,
        "state": "canonical" if not issues else "disagreement",
        "checked_fields": len(claims),
        "claims": claims,
        "issues": issues,
        "newer_sources": [],
        "provenance": {
            field: authority["provenance"][field] for field in claims
        },
    }


def check_license_authority(
    content: str,
    repo_root: Path,
    authorized_license: Optional[str] = None,
) -> Dict[str, object]:
    """Validate README license claims against repository evidence."""
    authority = license_authority.inspect_repository(
        repo_root,
        authorized_license=authorized_license,
    )
    headings = extract_section_headings(content)
    has_section = "license" in headings
    claimed_ids = extract_claimed_license_ids(content)
    if has_section:
        section_claims = extract_claimed_license_ids(
            extract_named_section(content, "license"),
            allow_bare_identifiers=True,
        )
        claimed_ids = list(dict.fromkeys([*claimed_ids, *section_claims]))
    badge_matches = re.findall(
        r"\[!\[([^\]]*)\]\(([^\)]+)\)\]\(([^\)]+)\)",
        content,
    )
    has_badge = any(
        re.search(
            r"\blicen[cs]e\b|\bspdx\b|\bcc[-_ ]by\b|\bmit\b|\bapache\b|\bgpl\b",
            " ".join(match),
            flags=re.IGNORECASE,
        )
        for match in badge_matches
    )
    has_text_claim = bool(claimed_ids) and bool(
        re.search(
            r"\b(?:licensed|released|distributed|provided|available)\s+under\b|"
            r"\blicen[cs]e\s*:\s*",
            content,
            flags=re.IGNORECASE,
        )
    )
    has_claim = has_section or has_badge or has_text_claim
    if not has_claim:
        claimed_ids = []
    issues: List[str] = []

    if has_claim and not authority["claim_allowed"]:
        issues.append(
            "License claim is not authorized by repository evidence "
            f"(state: {authority['state']})"
        )

    root_evidence = authority["root_evidence"]
    authorized = authority["authorized_license"]
    if has_claim and authorized and claimed_ids:
        if any(claimed_id.lower() != authorized.lower() for claimed_id in claimed_ids):
            issues.append(
                "README license claim does not match the explicitly authorized "
                f"license ({authorized})"
            )

    if has_claim and len(root_evidence) == 1 and not authorized:
        evidence_path = root_evidence[0]
        linked_paths = {url.split("#", 1)[0] for _, url in extract_links(content)}
        if evidence_path not in linked_paths and f"./{evidence_path}" not in linked_paths:
            issues.append(f"License claim must link the evidence file: {evidence_path}")

        detected_id = authority["known_license_ids"].get(evidence_path)
        if claimed_ids and any(claimed_id != detected_id for claimed_id in claimed_ids):
            issues.append(
                "README license claim does not match the detected repository "
                f"license ({detected_id or 'unresolved custom terms'})"
            )

    return {
        **authority,
        "has_license_section": has_section,
        "has_license_badge": has_badge,
        "has_license_text_claim": has_text_claim,
        "claimed_license_ids": claimed_ids,
        "issues": issues,
        "valid": not issues,
    }


def count_unlabeled_fenced_code_blocks(content: str) -> int:
    """Count opening Markdown fences whose info string is empty.

    Fence meaning is stateful: a bare fence closes an existing block, but opens
    an unlabeled block when no block is active. Treating each fence as an
    independent regex match therefore misclassifies every valid closing fence.
    """
    fence_pattern = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})([^\r\n]*)$")
    open_fence_character = None
    open_fence_length = 0
    unlabeled_openings = 0

    for line in content.splitlines():
        match = fence_pattern.match(line)
        if not match:
            continue

        marker, info_string = match.groups()
        marker_character = marker[0]

        if open_fence_character is not None:
            is_closing_fence = (
                marker_character == open_fence_character
                and len(marker) >= open_fence_length
                and not info_string.strip()
            )
            if is_closing_fence:
                open_fence_character = None
                open_fence_length = 0
            continue

        # Backticks in a backtick fence's info string make it invalid Markdown,
        # so do not let that line alter parser state.
        if marker_character == "`" and "`" in info_string:
            continue

        if not info_string.strip():
            unlabeled_openings += 1

        open_fence_character = marker_character
        open_fence_length = len(marker)

    return unlabeled_openings


def check_markdown_formatting(content: str) -> List[str]:
    """Check for common markdown formatting issues."""
    issues = []

    lines = content.split('\n')

    # Check for lists without preceding blank line
    for i, line in enumerate(lines[1:], start=1):
        if re.match(r'^\s*[-*+]\s+', line) or re.match(r'^\s*\d+\.\s+', line):
            if i > 0 and lines[i-1].strip() and not re.match(r'^#+\s+', lines[i-1]):
                # Previous line is not blank and not a header
                if not (re.match(r'^\s*[-*+]\s+', lines[i-1]) or re.match(r'^\s*\d+\.\s+', lines[i-1])):
                    issues.append(f"Line {i+1}: List item should have blank line before it")

    # Check for code blocks without language specification
    unnamed_blocks = count_unlabeled_fenced_code_blocks(content)
    if unnamed_blocks > 0:
        issues.append(f"Found {unnamed_blocks} code block(s) without language specification")

    # Check for very long lines (> 120 chars, excluding URLs)
    for i, line in enumerate(lines, start=1):
        if len(line) > 120 and 'http' not in line:
            issues.append(f"Line {i}: Very long line ({len(line)} chars) - consider breaking")

    return issues

def check_header_structure(content: str) -> List[str]:
    """Check header structure and hierarchy."""
    issues = []
    h1_count = 0
    prev_level = 0

    for heading in extract_markdown_headings(content):
        level = int(heading["level"])
        line_number = int(heading["line_index"]) + 1

        if level == 1:
            h1_count += 1

        if prev_level > 0 and level > prev_level + 1:
            issues.append(
                f"Line {line_number}: Skipped header level "
                f"(#{prev_level} to #{level})"
            )

        prev_level = level

    if h1_count == 0:
        issues.append("No H1 header found (should have repository name)")
    elif h1_count > 1:
        issues.append(f"Multiple H1 headers found ({h1_count}) - should have only one")

    return issues

def validate_readme(
    file_path: str,
    repo_root: Optional[str] = None,
    authorized_license: Optional[str] = None,
) -> Dict:
    """Validate a README.md file and return detailed report."""
    path = Path(file_path)

    if not path.exists():
        return {
            'valid': False,
            'error': f"File not found: {file_path}",
            'score': 0
        }

    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {
            'valid': False,
            'error': f"Error reading file: {e}",
            'score': 0
        }

    repository_root = Path(repo_root).resolve() if repo_root else path.resolve().parent
    try:
        authority_report = check_license_authority(
            content,
            repository_root,
            authorized_license=authorized_license,
        )
    except ValueError as error:
        return {
            'valid': False,
            'error': str(error),
            'score': 0
        }

    metrics_authority_report = check_metrics_authority(content, repository_root)

    report = {
        'valid': True,
        'file': str(path),
        'size': len(content),
        'sections': {},
        'links': {},
        'badges': {},
        'formatting': {},
        'headers': {},
        'license_authority': authority_report,
        'metrics_authority': metrics_authority_report,
        'recommendations': [],
        'score': 0
    }

    # Check sections
    found_req, missing_req, found_rec, missing_rec = check_required_sections(content)
    report['sections'] = {
        'required_found': found_req,
        'required_missing': missing_req,
        'recommended_found': found_rec,
        'recommended_missing': missing_rec
    }

    # Validate local files and anchors. External reachability is intentionally
    # not claimed by this deterministic repository validator.
    report['links'] = check_links(content, path.resolve(), repository_root)
    invalid_links = report['links']['invalid']

    # Extract badges
    badges = extract_badges(content)
    report['badges'] = {
        'count': len(badges),
        'urls': badges
    }

    # Check markdown formatting
    formatting_issues = check_markdown_formatting(content)
    report['formatting'] = {
        'issues': formatting_issues,
        'issue_count': len(formatting_issues)
    }

    # Check header structure
    header_issues = check_header_structure(content)
    report['headers'] = {
        'issues': header_issues,
        'issue_count': len(header_issues)
    }

    # Generate recommendations
    if missing_req:
        report['recommendations'].append(f"Add missing required sections: {', '.join(missing_req)}")

    if missing_rec:
        report['recommendations'].append(f"Consider adding recommended sections: {', '.join(missing_rec)}")

    if invalid_links:
        report['valid'] = False
        link_reasons = ", ".join(
            sorted({str(issue['reason']) for issue in report['links']['issues']})
        )
        report['recommendations'].append(
            f"Fix {len(invalid_links)} invalid link(s): {link_reasons}"
        )

    if len(badges) == 0:
        report['recommendations'].append("Add badges for technologies used")

    if formatting_issues:
        report['recommendations'].append(f"Fix {len(formatting_issues)} formatting issue(s)")

    if header_issues:
        report['recommendations'].append(f"Fix {len(header_issues)} header structure issue(s)")

    if authority_report['issues']:
        report['valid'] = False
        report['recommendations'].extend(authority_report['issues'])

    if metrics_authority_report['issues']:
        report['valid'] = False
        report['recommendations'].extend(metrics_authority_report['issues'])

    # Calculate score (0-100)
    score = 100

    # Deduct for missing required sections (10 points each)
    score -= len(missing_req) * 10

    # Deduct for missing recommended sections (5 points each, max 20)
    score -= min(len(missing_rec) * 5, 20)

    # Deduct for invalid links (5 points each, max 15)
    score -= min(len(invalid_links) * 5, 15)

    # Deduct for no badges (10 points)
    if len(badges) == 0:
        score -= 10

    # Deduct for formatting issues (2 points each, max 15)
    score -= min(len(formatting_issues) * 2, 15)

    # Deduct for header issues (3 points each, max 10)
    score -= min(len(header_issues) * 3, 10)

    # Authority violations are a hard failure as well as a visible score cost.
    if authority_report['issues']:
        score -= 40

    if metrics_authority_report['issues']:
        score -= 40

    report['score'] = max(0, score)

    return report

def format_report(report: Dict) -> str:
    """Format validation report as readable text."""
    if 'error' in report:
        return f"ERROR: {report.get('error', 'Unknown error')}"

    output = []
    output.append("=" * 60)
    output.append("README VALIDATION REPORT")
    output.append("=" * 60)
    output.append(f"\nFile: {report['file']}")
    output.append(f"Size: {report['size']:,} bytes")
    output.append(f"\nOVERALL SCORE: {report['score']}/100")

    # Score interpretation
    if report['score'] >= 90:
        output.append("Status: EXCELLENT ✓")
    elif report['score'] >= 75:
        output.append("Status: GOOD ✓")
    elif report['score'] >= 60:
        output.append("Status: ADEQUATE")
    else:
        output.append("Status: NEEDS IMPROVEMENT")

    # Sections
    output.append("\n" + "-" * 60)
    output.append("SECTIONS")
    output.append("-" * 60)

    sections = report['sections']
    output.append(f"Required sections: {len(sections['required_found'])}/{len(sections['required_found']) + len(sections['required_missing'])}")
    if sections['required_missing']:
        output.append(f"  Missing: {', '.join(sections['required_missing'])}")

    output.append(f"Recommended sections: {len(sections['recommended_found'])}/{len(sections['recommended_found']) + len(sections['recommended_missing'])}")
    if sections['recommended_missing']:
        output.append(f"  Missing: {', '.join(sections['recommended_missing'])}")

    # Links
    output.append("\n" + "-" * 60)
    output.append("LINKS")
    output.append("-" * 60)
    output.append(f"Total links: {report['links']['total']}")
    output.append(
        f"Repository-local targets verified: "
        f"{report['links']['local_verified_count']}"
    )
    output.append(
        "External URLs syntax-valid, reachability not checked: "
        f"{report['links']['external_unverified_count']}"
    )
    output.append(
        "Origin-relative URLs unverified against their eventual host: "
        f"{report['links']['origin_relative_unverified_count']}"
    )
    output.append(f"Mail links syntax-valid: {report['links']['mail_count']}")
    output.append(f"Invalid links: {report['links']['invalid_count']}")
    if report['links']['issues']:
        for issue in report['links']['issues'][:5]:
            output.append(
                f"  - line {issue['line']}: {issue['destination']} "
                f"({issue['reason']})"
            )
        if len(report['links']['issues']) > 5:
            output.append(
                f"  ... and {len(report['links']['issues']) - 5} more"
            )

    # Badges
    output.append("\n" + "-" * 60)
    output.append("BADGES")
    output.append("-" * 60)
    output.append(f"Badge count: {report['badges']['count']}")

    # Formatting
    output.append("\n" + "-" * 60)
    output.append("FORMATTING")
    output.append("-" * 60)
    output.append(f"Issues found: {report['formatting']['issue_count']}")
    if report['formatting']['issues']:
        for issue in report['formatting']['issues'][:5]:  # Show first 5
            output.append(f"  - {issue}")
        if len(report['formatting']['issues']) > 5:
            output.append(f"  ... and {len(report['formatting']['issues']) - 5} more")

    # Headers
    output.append("\n" + "-" * 60)
    output.append("HEADER STRUCTURE")
    output.append("-" * 60)
    output.append(f"Issues found: {report['headers']['issue_count']}")
    if report['headers']['issues']:
        for issue in report['headers']['issues']:
            output.append(f"  - {issue}")

    authority = report['license_authority']
    output.append("\n" + "-" * 60)
    output.append("LICENSE AUTHORITY")
    output.append("-" * 60)
    output.append(f"Evidence state: {authority['state']}")
    output.append(
        "Root evidence: "
        + (", ".join(authority['root_evidence']) or "none")
    )
    output.append(
        "Scoped evidence: "
        + (", ".join(authority['scoped_evidence']) or "none")
    )
    output.append(f"Issues found: {len(authority['issues'])}")
    for issue in authority['issues']:
        output.append(f"  - {issue}")

    metrics = report['metrics_authority']
    output.append("\n" + "-" * 60)
    output.append("METRICS AUTHORITY")
    output.append("-" * 60)
    output.append(f"Evidence state: {metrics['state']}")
    output.append(f"Canonical fields checked: {metrics['checked_fields']}")
    output.append(f"Issues found: {len(metrics['issues'])}")
    for issue in metrics['issues']:
        output.append(f"  - {issue}")

    # Recommendations
    if report['recommendations']:
        output.append("\n" + "-" * 60)
        output.append("RECOMMENDATIONS")
        output.append("-" * 60)
        for i, rec in enumerate(report['recommendations'], start=1):
            output.append(f"{i}. {rec}")

    output.append("\n" + "=" * 60)

    return "\n".join(output)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate README presentation and claims.")
    parser.add_argument("readme")
    parser.add_argument("--repo-root")
    parser.add_argument("--authorized-license")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = validate_readme(
        args.readme,
        repo_root=args.repo_root,
        authorized_license=args.authorized_license,
    )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(format_report(report))

    # Exit with error code if score is below 60
    if not report.get('valid', False) or report['score'] < 60:
        sys.exit(1)

if __name__ == '__main__':
    main()
