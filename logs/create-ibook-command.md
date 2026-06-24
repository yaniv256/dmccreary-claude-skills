# Session: Create the /ibook Command (+ MicroSim QA Consolidation)

**Date:** 2026-06-23
**Outcome:** Created the `/ibook` slash command, merged two MicroSim QA skills
into `microsim-utils` (28 → 26 skills), and wired global command installation
into `bk-install-skills`.

Companion document: [skill-analysis-merge-and-ibook.md](skill-analysis-merge-and-ibook.md)
holds the full skill-by-skill analysis, duplication findings, and deferred
recommendations. This file is the process/session summary.

---

## 1. Goal

Analyze the intelligent-textbook / MicroSim / infographic skill collection and:
- recommend which skills could be merged,
- find duplication,
- improve orchestration/ordering,
- decide whether to create an `/ibook` command that lists the textbook skills
  and the order to run them to build a book from a course description,
- pay special attention to `init-textbook` and `book-installer` (the
  foundation skills everything else depends on).

## 2. Approach

- **Exploration:** 3 parallel Explore agents mapped the three skill families
  (foundation, content pipeline, visualization) — inputs, outputs,
  prerequisites, and cross-references.
- **Direct reads:** confirmed the command format (`commands/skills.md`), the
  28-skill inventory, and that slash commands live in `commands/` and do **not**
  count against the 30-skill cap.
- **Decisions captured via AskUserQuestion:**
  1. Scope → *Analysis + build /ibook*
  2. `/ibook` behavior → *Passive runbook* (lists skills + gates; human invokes
     each manually; no auto-execution)
  3. QA-skill merge → *Merge them* (fold iframe-tester + layout-reviewer into
     `microsim-utils`)

## 3. What was built

### a. MicroSim QA consolidation (28 → 26 skills)

Merged `microsim-iframe-tester` + `microsim-layout-reviewer` into the
`microsim-utils` meta-skill so all three MicroSim QA concerns live together
(build-time height sync, geometric control-visibility, visual review).

- **Moved via `git mv`** (history preserved): `test-iframe-heights.py`,
  `visual-checklist.md`, `common-fixes.md` → `microsim-utils/`
- **New sub-guides:** `microsim-utils/references/iframe-tester.md`,
  `microsim-utils/references/layout-reviewer.md`
- **Retired:** both standalone skill dirs (incl. the deprecated Node.js tester +
  bundled `node_modules`) and their two dangling `~/.claude/skills` symlinks
- **Updated cross-refs:** `microsim-utils/SKILL.md` (routing table, decision
  tree, comparison table, examples, workflow), `microsim-generator/SKILL.md`
  (5 references), `CLAUDE.md` (both meta-skill tables), `visual-checklist.md`

### b. The `/ibook` command (`commands/ibook.md`)

A passive 8-phase runbook that:
- detects which pipeline artifacts exist (read-only) and shows "you are here",
- recommends the single next skill + the gate it must clear,
- lists the full ordered path with inputs/outputs/gates,
- **never auto-runs** a skill.

Phase 0 makes the `init-textbook` (once) → `book-installer` (repeatable)
foundation ordering explicit. Encodes the hard gates discovered in analysis:
course-description score ≥ 85, valid DAG, edge-direction validation, ≥ 30%
chapters before FAQ, and the `book-metrics.json` hub before any announce skill.

Chosen as a slash command (not a skill) because it costs nothing against the
30-skill cap and matches the existing `commands/skills.md` pattern.

### c. Global command installation (`scripts/bk-install-skills`)

The installer linked skill dirs but never handled `commands/`, so `/ibook` and
`/skills` weren't globally usable without a manual copy. Added a
command-symlinking section that links every `commands/*.md` into
`~/.claude/commands/` (clean stale links, replace symlinks, warn+skip real
files, skip archived `*-old.md`). `bk-install-skills` is now the single
installer for both skills and commands.

Also made `/ibook` work immediately: created the `~/.claude/commands/ibook.md`
symlink and converted the pre-existing byte-identical real-copy `skills.md` to a
symlink for consistency.

## 4. Verification

- `bash -n scripts/bk-install-skills` → syntax OK
- Full idempotent installer run → re-linked all 26 skills, `Installed 2 command
  link(s): /ibook /skills`, correctly skipped `skills-old.md`
- Harness registered `/ibook` as an available command after install
- Grep confirmed no stale references to the retired skills outside `logs/`

## 5. Deferred / open items

- **Document the causal-loop distinction** — note in `microsim-generator`'s
  causal-loop guide that the standalone `causal-loop-diagram-generator` is for
  multi-loop *articles*; the guide is for single embedded diagrams.
- **`concept-classifier` → p5 sub-guide** — possible future merge to free
  another slot; deferred (slot pressure relieved at 26/30).
- **`install-skills-command.sh`** — ✅ **removed** (redundant with the
  generalized command logic in `bk-install-skills`; its `list-skills.sh` copy
  was already dead, pointing at a nonexistent `scripts/list-skills.sh`).
  References in `docs/getting-started.md` and `docs/faq.md` were repointed to
  `bk-install-skills`.

## 6. Commits this session

- `d3f05f4d` — Consolidate MicroSim QA skills into microsim-utils; add /ibook runbook
- (pending) — Symlink slash commands globally in bk-install-skills
