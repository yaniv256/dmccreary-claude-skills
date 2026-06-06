#!/usr/bin/env python3
"""
generate-sims-index.py — Build the MicroSims gallery page (docs/sims/index.md).

Scans ``docs/sims/`` for directories containing ``index.md``, extracts each
sim's display title and screenshot, and writes a responsive thumbnail-card grid
into ``docs/sims/index.md``. Each card links to the sim and shows its ``.png``
screenshot (sims without a screenshot get a neutral "no preview" placeholder).

This is the gallery counterpart to ``update-mkdocs-nav.py`` (which wires the
nav and points "List of MicroSims" at ``sims/index.md``). Idempotent and safe
to run repeatedly.

Usage:
    python3 generate-sims-index.py [--project-dir PATH] [--dry-run] [--verbose]
"""

import argparse
import html
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shared import (
    find_project_root, parse_yaml_frontmatter,
    GREEN, RED, YELLOW, CYAN, BOLD, DIM, RESET, CHECK, CROSS, WARN, ARROW,
)

SKIP_DIRS = {"TODO"}


def _extract_title(index_path):
    """Display title: frontmatter ``title`` > first ``# Heading`` > dir name."""
    with open(index_path, encoding="utf-8") as f:
        content = f.read()
    fm, _ = parse_yaml_frontmatter(content)
    if fm.get("title"):
        return fm["title"].strip()
    m = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return os.path.basename(os.path.dirname(index_path)).replace("-", " ").title()


def _find_screenshot(sim_dir, name):
    """Return the screenshot filename for a sim, or None.

    Prefers ``<name>.png``; otherwise the first ``.png`` alphabetically that is
    not an obvious non-screenshot (icon/logo).
    """
    preferred = f"{name}.png"
    if os.path.isfile(os.path.join(sim_dir, preferred)):
        return preferred
    pngs = sorted(f for f in os.listdir(sim_dir) if f.lower().endswith(".png"))
    return pngs[0] if pngs else None


def scan_sims(project_dir, verbose=False):
    """Return a list of dicts sorted by title: {name, title, shot}."""
    sims_dir = os.path.join(project_dir, "docs", "sims")
    if not os.path.isdir(sims_dir):
        print(f"{RED}{CROSS} docs/sims/ not found in {project_dir}{RESET}")
        return []
    sims = []
    for name in sorted(os.listdir(sims_dir)):
        if name in SKIP_DIRS or name.startswith("."):
            continue
        sim_dir = os.path.join(sims_dir, name)
        index_path = os.path.join(sim_dir, "index.md")
        if not os.path.isfile(index_path):
            continue
        sims.append({
            "name": name,
            "title": _extract_title(index_path),
            "shot": _find_screenshot(sim_dir, name),
        })
    sims.sort(key=lambda s: s["title"].lower())
    if verbose:
        missing = [s["name"] for s in sims if not s["shot"]]
        print(f"{DIM}Scanned {len(sims)} sims; {len(missing)} without a screenshot{RESET}")
    return sims


def _fm_value(v):
    """Quote a frontmatter scalar value for YAML if it needs it."""
    if v == "" or v != v.strip() or v[:1] in "-?&*!|>%@`\"'[]{},#" or ":" in v:
        return '"' + v.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return v


def existing_meta(out_path):
    """Return (title, description) from an existing index.md frontmatter, or (None, None)."""
    if not os.path.isfile(out_path):
        return None, None
    with open(out_path, encoding="utf-8") as f:
        fm, _ = parse_yaml_frontmatter(f.read())
    return fm.get("title"), fm.get("description")


def build_page(sims, title, description):
    n = len(sims)
    n_shot = sum(1 for s in sims if s["shot"])
    cards = []
    for s in sims:
        card_title = html.escape(s["title"])
        href = f"{s['name']}/"
        if s["shot"]:
            media = (f'<img src="{s["name"]}/{s["shot"]}" alt="{card_title}" loading="lazy" '
                     'style="width:100%;aspect-ratio:16/10;object-fit:cover;background:#f5f7fa;'
                     'display:block;border-bottom:1px solid #eee;">')
        else:
            media = ('<span style="display:flex;align-items:center;justify-content:center;width:100%;'
                     'aspect-ratio:16/10;background:linear-gradient(135deg,#eef2f7,#dde6f0);'
                     'color:#8a97a5;font-size:0.8rem;border-bottom:1px solid #eee;">no preview</span>')
        cards.append(
            f'  <a href="{href}" title="{card_title}" '
            'style="display:block;border:1px solid #e3e7ec;border-radius:8px;overflow:hidden;'
            'text-decoration:none;color:inherit;box-shadow:0 1px 3px rgba(0,0,0,0.08);">'
            f'{media}'
            f'<span style="display:block;padding:9px 11px;font-size:0.85rem;font-weight:600;'
            f'line-height:1.3;">{card_title}</span></a>'
        )
    grid = ('<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));'
            'gap:18px;margin-top:1.5em;">\n' + "\n".join(cards) + "\n</div>")
    intro = (f"This book includes **{n} interactive MicroSims** — self-contained, "
             "browser-based visualizations you can explore directly. "
             "Click any thumbnail to open the MicroSim.")
    # Frontmatter: always hide the table of contents on this gallery page.
    frontmatter = (
        "---\n"
        f"title: {_fm_value(title)}\n"
        f"description: {_fm_value(description)}\n"
        "hide:\n"
        "  - toc\n"
        "---\n\n"
    )
    return (
        f"{frontmatter}"
        f"# {title}\n\n"
        f"{intro}\n\n"
        "<!-- This gallery is generated by generate-sims-index.py — edits here will be overwritten. -->\n\n"
        f"{grid}\n"
    )


def main():
    ap = argparse.ArgumentParser(description="Generate the MicroSims gallery page (docs/sims/index.md).")
    ap.add_argument("--project-dir", default=None, help="Project root (auto-detected if omitted).")
    ap.add_argument("--title", default=None, help="Page title (frontmatter + H1). Preserved from existing frontmatter, else 'MicroSims'.")
    ap.add_argument("--description", default=None, help="Frontmatter description. Preserved from existing frontmatter, else auto-generated.")
    ap.add_argument("--dry-run", action="store_true", help="Print the page instead of writing it.")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    project_dir = args.project_dir or find_project_root()
    if not project_dir:
        print(f"{RED}{CROSS} Could not locate project root (no mkdocs.yml found).{RESET}")
        sys.exit(1)

    sims = scan_sims(project_dir, verbose=args.verbose)
    if not sims:
        print(f"{YELLOW}{WARN} No sims found.{RESET}")
        sys.exit(1)

    out_path = os.path.join(project_dir, "docs", "sims", "index.md")
    # Title/description precedence: CLI flag > existing frontmatter > default.
    prev_title, prev_desc = existing_meta(out_path)
    title = args.title or prev_title or "MicroSims"
    description = args.description or prev_desc or (
        f"A gallery of {len(sims)} interactive MicroSims — self-contained, "
        "browser-based visualizations you can explore directly.")
    page = build_page(sims, title, description)
    if args.dry_run:
        print(page)
        return
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page)
    n_shot = sum(1 for s in sims if s["shot"])
    print(f"{GREEN}{CHECK} Wrote {out_path} — {len(sims)} cards ({n_shot} with screenshots){RESET}")


if __name__ == "__main__":
    main()
