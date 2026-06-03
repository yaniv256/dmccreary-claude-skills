# Refactor Log: Fold `book-metrics-generator` into `book-installer`

**Status:** ✅ Completed and published (June 3, 2026).
Commits `eebdc0fa` (edits + new guide) and `0a33910c` (skill deletions) on `main`;
deployed to https://dmccreary.github.io/claude-skills/ via `mkdocs gh-deploy`.
Skill count reduced 28 → 27.

The approved implementation plan that was executed is preserved below.

---

# Plan: Fold `book-metrics-generator` into the `book-installer` meta-skill

## Context

The repo currently has **28 top-level skills**. Every skill's `SKILL.md`
frontmatter `description` is loaded into Claude's context, so the count is
pressured against Claude Code's ~30-skill limit and eats into the token budget.
`book-metrics-generator` is a good consolidation candidate: its actual runtime
(the `bk-generate-book-metrics` wrapper) already points at
`src/book-metrics/book-metrics.py` — the single source of truth established last
session — and the `book-installer` meta-skill's `supplementary-content-generator`
guide *already* invokes that wrapper. So the standalone skill's
`SKILL.md` + duplicate `scripts/` add a skill slot without adding capability.

**Goal:** turn `book-metrics-generator` into one guide inside `book-installer`,
delete the standalone skill, and update every live reference — bringing the count
to **27** with no loss of capability and `mkdocs build --strict` still passing.

## Confirmed decisions

- **DRY script handling.** No copy of `book-metrics.py` goes into book-installer.
  The new guide invokes `bk-generate-book-metrics` (primary) with a `python3`
  fallback to `src/book-metrics/book-metrics.py`. `src/book-metrics/book-metrics.py`
  stays the single source of truth.
- **Keep & update the docs-site catalog page** (`docs/skill-descriptions/book/book-metrics-generator.md`)
  and its nav entry — it's human documentation, doesn't affect the skill token
  budget, and keeping it avoids `--strict` breakage. Just refresh its stale run path.

## Implementation steps

### 1. Create the new guide `skills/book-installer/references/book-metrics.md`
Condense the standalone `SKILL.md` content into book-installer guide style:
- **Purpose / What it produces**: `docs/learning-graph/book-metrics.md`,
  `chapter-metrics.md`, and the merged `metrics` block + `metricsGenerated*`
  provenance in `docs/learning-graph/book-metadata.json` (author fields preserved;
  unparseable JSON left untouched with a warning; botany `speciesCards` extension
  when `docs/plants/` exists).
- **Prerequisites**: `docs/`, `docs/chapters/NN-*/index.md`; optional enhancers
  (`learning-graph.csv`, `glossary.md`, `faq.md`, `docs/sims/`, `docs/stories/`,
  `docs/img/mascot/`, `docs/appendices/`, per-chapter `quiz.md`/`references.md`,
  `mkdocs.yml extra.development_stage`). Requires `$BK_HOME` exported and
  `bk-generate-book-metrics` on `$PATH` (same assumption as `bk-diagram-reports`).
- **How to run** (literal):
  ```bash
  # Primary — resolves $BK_HOME/src/book-metrics/book-metrics.py
  bk-generate-book-metrics
  # Fallback if not on $PATH (run from project root):
  python3 "$BK_HOME/src/book-metrics/book-metrics.py" docs
  ```
- Carry over the **12-element Book Composition table**, the **page formula**
  (`Pages = Words÷250 + Diagrams×0.25 + MicroSims×0.5`), the **nav snippet**,
  and a condensed **Troubleshooting** section.

### 2. Wire it into `skills/book-installer/SKILL.md`
- **Help list** (after current item 39, ~line 70):
  `40. Book metrics report - chapters, concepts, glossary/FAQ counts, quiz & reference totals, diagrams, equations, MicroSims, word count & equivalent pages`
- **Routing table** (after the item-39 row, ~line 137):
  `| book metrics, generate metrics, book-metrics, chapter metrics, content statistics, word count, page count, equivalent pages, book composition, metrics report, 40 | `references/book-metrics.md` | Generate book-metrics.md, chapter-metrics.md, and the metrics block in book-metadata.json via bk-generate-book-metrics |`
- **Decision tree** (after the supplementary block, ~line 201): a `book-metrics.md` branch.
- Add the matching `### book-metrics.md` descriptive block in the guides section
  (mirrors every other guide). Optional Example entry for discoverability.

### 3. Cross-reference updates
**SHOULD-fix (accuracy/discoverability; no build impact):**
- `CLAUDE.md`: line ~23 add `book-metrics` to book-installer's "Routes to:" comment;
  line ~29 remove the `book-metrics-generator/` repo-tree line; line ~82 meta-skill
  table — add `book-metrics` to book-installer's sub-skills; line ~270 step 11 →
  `(book-installer → book-metrics, microsim-utils)`.
- `skills/linkedin-announcement-generator/SKILL.md` lines ~527, ~543: reword
  "run the book-metrics-generator skill" → "run `bk-generate-book-metrics`
  (book-installer → book-metrics)".
- `skills/book-installer/references/feature-checklist-generator.md` line ~250 and
  `.../references/assets/templates/docs/feature-checklist.md` line ~3: point to the
  book-metrics guide / `bk-generate-book-metrics`.
- `docs/skill-descriptions/book/linkedin-announcement-generator.md` line ~66: reword.
- `docs/workshops/intelligent-textbook-workshop-outline.md` (~203),
  `intelligent-textbook-cheat-sheet.md` (row 11), `workshop-prework.md`
  (installed-skills list): `/skill book-metrics-generator` → `bk-generate-book-metrics`;
  drop it from the expected `~/.claude/skills` listing.
- `docs/skill-descriptions/book/book-metrics-generator.md` line ~58: stale path
  `~/.claude/skills/book-metrics-generator/scripts/book-metrics-generator.sh` →
  `bk-generate-book-metrics`; add a one-line note that the capability now lives in
  book-installer. **(Keep the page + its mkdocs.yml:74 nav entry + index.md link.)**
- Optionally add a discoverability cross-link from `supplementary-content-generator.md`
  step 8 to the new `book-metrics.md` guide.

**LEAVE (historical — do not edit):** `docs/prompts/book-metrics-skill-creation.md`,
`logs/*`.

### 4. Delete the standalone skill (after all edits above)
- `rm -rf skills/book-metrics-generator` (removes its `SKILL.md`,
  `scripts/book-metrics.py`, `scripts/book-metrics-generator.sh` — confirmed
  redundant; the canonical script in `src/` and the `bk-` wrapper are untouched).
- Remove the now-dangling symlink: `rm ~/.claude/skills/book-metrics-generator`.
- Do **not** touch `scripts/bk-generate-book-metrics`,
  `~/.local/bin/bk-generate-book-metrics`, or `src/book-metrics/book-metrics.py`.

### 5. Auto-commit marker
Write `.claude-pending-commit.txt` (subject + why) so the whole consolidation
lands as a single commit.

## Critical files
- `skills/book-installer/references/book-metrics.md` *(new)*
- `skills/book-installer/SKILL.md` *(help item, routing row, decision branch, guide block)*
- `CLAUDE.md` *(repo tree, meta-skill table, 12-step workflow)*
- `skills/book-metrics-generator/` *(delete)* + `~/.claude/skills/book-metrics-generator` symlink *(remove)*
- `mkdocs.yml` / `docs/skill-descriptions/book/book-metrics-generator.md` *(keep; minor path edit)*

## Verification (read-only, from repo root)
1. `ls skills/ | grep -v '^archived$' | wc -l` → **27**; `test ! -d skills/book-metrics-generator`.
2. `test ! -e ~/.claude/skills/book-metrics-generator` (symlink gone).
3. `grep -n 'references/book-metrics.md' skills/book-installer/SKILL.md` shows the new
   routing row + decision branch; `test -f skills/book-installer/references/book-metrics.md`.
4. Script still runs against a throwaway fixture (not a real repo):
   `python3 src/book-metrics/book-metrics.py /tmp/bm-test/docs` (and/or
   `BK_HOME=$PWD bk-generate-book-metrics /tmp/bm-test/docs`) → writes
   `book-metrics.md`, `chapter-metrics.md`, updates `book-metadata.json`, no error.
5. `mkdocs build --strict 2>&1 | tail -20` → no WARNING/ERROR/Aborted.
6. No stale references:
   `grep -rn "book-metrics-generator" --include='*.md' --include='*.yml' . | grep -vE '^\./(logs|docs/prompts|site)/'`
   → only the intentionally-kept docs catalog page/link remain;
   `grep -rn "skills/book-metrics-generator/scripts" .` → nothing outside logs/prompts.

## Risks / notes
- **`--strict` couples page↔nav↔link.** We keep all three, so no break. If anyone
  later deletes the catalog page they must also clear `mkdocs.yml:74` and the
  `index.md` item-10 link together.
- **`$BK_HOME` is unset in some shells.** The wrapper fails with a clear
  message; the guide states the prerequisite (it's exported in the user's profile).
- **`linkedin-announcement-generator`** only reads the *output files*, not the
  skill — keeps working once `bk-generate-book-metrics` runs. `init-textbook` and
  `readme-generator` have no coupling (readme-generator uses its own
  `collect-site-metrics.py`).
- **Skill list reload:** Claude Code may still advertise `book-metrics-generator`
  until the skill set reloads after the symlink removal — cosmetic only.

---

## Execution notes (what actually happened)

- All steps executed as planned. The new guide, SKILL.md wiring, cross-reference
  updates, skill-directory deletion, and dangling-symlink removal were completed.
- Verified: skill count **27**; symlink gone; routing wired; the metrics script
  runs via **both** `python3 src/book-metrics/book-metrics.py` and the
  `bk-generate-book-metrics` wrapper, with author fields preserved on merge.
- `mkdocs build --strict` aborts on **28 pre-existing broken internal links**
  (in `index.md`, `prompts/`, `sims/`, `skill-descriptions/`) that are unrelated
  to this change — none touch the edited files or the book-metrics catalog
  page/nav/link. Flagged separately for cleanup. `mkdocs gh-deploy` (no `--strict`)
  built and deployed cleanly.
- The work landed as two commits rather than one: the prior turn's auto-commit
  Stop hook committed and pushed the edits + new guide (`eebdc0fa`), but its
  staging missed the `rm -rf` directory deletions, which were committed separately
  (`0a33910c`). History was not rewritten since `eebdc0fa` was already on `origin`.
