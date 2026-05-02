# MicroSim Layout Reviewer — Skill Creation Log

**Date:** 2026-05-02
**Author:** Dan McCreary (with Claude Opus 4.7, 1M context)
**Skill location:** `skills/microsim-layout-reviewer/`

## Why this skill exists

While generating the *Result Field Composition Explorer* MicroSim earlier
in the session, Claude noticed — by looking at the captured screenshot —
that the row labels on the 2×2 grid were partly clipped at the left
edge ("co" missing from "completion: true"), traced the cause to a
hard-coded `axisOffset = 60` that was smaller than the widest label's
`textWidth()`, and patched it (`60 → 110`) before the user saw the
broken version.

That triggered the question: **how do we make this a repeatable skill
rather than an ad-hoc behavior?** The user asked for it to be built
formally with the `skill-creator` workflow.

The complementary skill `microsim-iframe-tester` already existed — it
uses Playwright to assert that every interactive control's
bounding-box sits inside the iframe boundary. But pixel-precise
geometry checks miss the *visual* defects: text clipped at a panel
edge, a title overlapping a JSON column, the bar chart's tolerance
band rising into the chart title, low-contrast text on a colored
header. Those defects are obvious to a human looking at the
screenshot — and obvious to **Claude Vision (Opus 4.7)** looking at
the screenshot — but invisible to bounding-box assertions.

So this skill is the visual-review counterpart, sized to handle
exactly the failure modes that show up "to the eye" but slip past
geometry.

## What it does

```
1. Resolve the target sim (path / sim-id / "the one I just made")
2. Identify which file holds the layout logic (.js / main.html /
   data.json / *.mmd) — depends on the library
3. Read the iframe height from index.md
4. bk-capture-screenshot <sim-dir> 3 <iframe-height>
5. Read the PNG via the Read tool — Claude Vision sees it directly
6. Walk references/visual-checklist.md item-by-item; mark
   PASS / FAIL / N/A for each
7. For every FAIL, look up the symptom in references/common-fixes.md
   and apply the smallest patch that resolves it
8. Re-capture, re-read, re-walk the checklist
9. Stop after 3 cycles even if issues remain — surface the residue
   rather than over-tweak
10. Report library, edits, final state, and the active Claude Vision
    model version (anchors the judgment for future re-reads)
```

## Design choices and the reasoning behind them

### An explicit checklist, not "review the layout"

Claude Vision is **non-deterministic**: what it notices in an image
depends on what it's actively looking for. A casual "does this look
right?" pass misses defects that a directed "is anything clipped at
the left edge of the 2×2 grid?" question reliably catches. The
checklist (~30 items, organized into 6 sections) is what disciplines
review into reliable output — by forcing explicit attention to every
known failure mode, every time.

### A symptom → fix mapping table

`common-fixes.md` is the institutional memory of bug patterns we've
already debugged. Each entry has three parts:

- **Likely cause** — what's wrong in the source
- **Find** — where to look in the file
- **Fix** — the smallest edit that resolves it
- **Why** — the underlying bug pattern (so a similar manifestation
  next time gets recognized faster)

Library-specific entries are tagged with the library name in the
heading (e.g. *"Text has an ugly black outline (residual stroke)
*(p5.js)*"*). Library-agnostic entries (draw order, panel overflow,
text contrast, title-overlapping-panel) carry no tag.

The closing "When in doubt" section provides a four-step diagnostic
fallback for defects not yet in the table, plus an explicit
invitation to add new entries — the table grows over time from real
defects, not speculation.

### Bounded iteration (3 cycles max)

Without a cycle cap, Claude can ratchet a parameter (`axisOffset`
60 → 110 → 160 → 200 → 250) chasing a defect whose root cause is
elsewhere. Three cycles is enough for genuine fix-and-verify; past
that, it's better to surface "this design has a deeper issue" than
to quietly produce something subtly worse.

### Out-of-scope: iframe-edge clipping

If a sim's content extends past the iframe boundary (the bottom node
gets cut off), the right tool is `microsim-iframe-tester` plus
`fix-iframe-heights.py`, not this skill. The skill explicitly defers
those cases. Confining scope keeps the skill sharp.

### Out-of-scope: redesign

If the layout is fundamentally poorly conceived (12 controls in one
row, hierarchy too flat, etc.), the skill surfaces symptoms and
stops. Redesign needs human judgement.

### Out-of-scope: approved sims

If `index.md` frontmatter has `status: approved`, the skill skips
the sim. Approved sims are locked from incidental edits — explicit
sign-off has already happened.

## Tested on 16 non-approved MicroSims in `xapi-course`

Status filter: `status != approved` from `index.md` frontmatter.

| Sim | Verdict | Action |
|---|---|---|
| four-inverse-functional-identifiers | PASS | none |
| learning-standards-ecosystem | MARGINAL | iframe-tester |
| retry-with-backoff-state-machine | CLIPPED | iframe-tester (out of scope) |
| statement-field-ownership | PASS | none |
| statement-query-pagination-flow | CLIPPED | iframe-tester (out of scope) |
| xapi-statement-anatomy | PASS | none |
| result-field-composition-explorer | PASS | (already fixed earlier) |
| service-worker-offline-queue-flow | CLIPPED | iframe-tester (out of scope) |
| **standards-comparison-card-grid** | FAIL → FIXED | header text overlap |
| **statistical-representativeness-comparison** | FAIL → FIXED | chart bars over title |
| **three-context-comparison** | FAIL → FIXED | low-contrast axis labels |
| vocabulary-profile-architecture | PASS | none |
| 4 scaffolds | SKIP | not implemented yet |

**6 PASS / 4 SCAFFOLD-skip / 4 iframe-clipping (delegated) / 3 in-scope FAILs (all fixed).**

### Fixes applied in the test run

1. **standards-comparison-card-grid** — "Proprietary SDK / vendor-specific" overlapped in the rightmost card header because the year string was longer than the card column allowed. Changed `year: 'vendor-specific'` to `'closed'` in the data array.

2. **statistical-representativeness-comparison** — Tolerance band rectangles drew above the chart top into the title text because `maxV` did not account for the `(1 + tol)` multiplier. Updated `maxV` computation to include the upper edge of the tolerance band:
   ```js
   maxV = Math.max(maxV, REAL_VERBS[v] * (1 + tol), synthVerbs[v]);
   ```
   Same fix in both `drawVerbChart` and `drawDurChart`.

3. **three-context-comparison** — Top axis label "Reg" sat on top of the colored panel header, becoming nearly unreadable; bottom label "Anal" overlapped the "Top regulations" title. Added a translucent white pill background behind every axis label so they stay legible on any color:
   ```js
   fill(255, 255, 255, 220);
   rectMode(CENTER);
   rect(lx, ly, textWidth(label) + 6, 11, 3);
   rectMode(CORNER);
   fill('#475569');
   text(label, lx, ly);
   ```

## Iterations after the initial draft

The skill was refined three times after first creation, each based on
direct feedback from Dan:

### Iteration 1 — "Claude Vision" terminology

Originally the skill referred to "vision" / "multimodal vision" as
generic capabilities. Dan asked that this be promoted to a **proper
noun "Claude Vision"** with the model version pinned on first
reference (e.g. "Claude Vision (Opus 4.7)"). Reasoning: the
capability is real and improving release-over-release, and pinning
the version anchors any review judgment to a specific model so
future re-reads can tell whether the underlying capability has
changed.

Saved as a feedback memory so this naming applies across all future
work, not just this skill.

### Iteration 2 — Library-agnostic refactor

The original skill was framed entirely around p5.js — "patches the
`.js` file", "axisOffset", `noStroke()`, etc. The test run on
`xapi-course/docs/sims` proved the skill was already useful on
non-p5 sims (Mermaid flowcharts surfaced clipping issues; the
Chart.js bar-chart overflow was caught), but the language was
discouraging that interpretation.

Updated the skill to be explicit:

- Description mentions p5.js, Mermaid, Chart.js, vis-network,
  vis-timeline, Leaflet by name.
- Step 2 of the workflow now identifies which file holds the layout
  logic — depending on the library this could be a `.js`, the
  inline config in `main.html`, a `data.json` content file, or an
  `*.mmd` Mermaid graph definition.
- `common-fixes.md` opens with a library-to-patch-file table.
- Every p5.js-specific fix entry is tagged `*(p5.js)*`. Agnostic
  entries (draw order, panel overflow, text contrast,
  title-overlapping-panel) carry no tag.
- `visual-checklist.md` section 5 retitled "Library-specific
  elements" with explicit fallback guidance for libraries not yet
  covered.

### Iteration 3 — Description size and YAML quoting

Skill descriptions have a soft budget of ~130 tokens (the load
mechanism keeps every available skill's description in context, so
size compounds across the whole skill library). The original
description was ~184 tokens; after a tight rewrite it lands at
~133 token-estimate, ~130 actual.

Dan also flagged that his downstream tooling errors on **unquoted
colons inside YAML description values** — even where YAML spec would
parse them cleanly. Fixed by:

- Wrapping the description in single quotes (the one apostrophe in
  `MicroSim's` doubled to `''`; internal double quotes pass through
  as-is, simpler than the backslash-escape dance double-quotes need).
- Replacing the two interior colons (after "Claude Vision" and
  "Triggers") with em-dashes — belt and suspenders, so even tools
  that don't honor YAML quoting don't trip.
- Verified the result parses cleanly under PyYAML.

Saved as a feedback memory: always single-quote YAML descriptions
when generating skills, and run a PyYAML round-trip check before
finishing.

## Ancillary memories saved

Three memories were created during this work (in
`~/.claude/projects/-Users-dan-Documents-ws-xapi-course/memory/`):

1. `feedback_claude_vision_terminology.md` — "Claude Vision" is a
   proper noun; include model version on first reference.
2. `feedback_skill_yaml_quoting.md` — Always single-quote YAML
   description values; verify with PyYAML.
3. *(updated)* `MEMORY.md` — index entries for the above.

These persist across conversations, so future sessions automatically
respect both rules without needing the same flags from Dan.

---

# Possible next steps

Concrete improvements, in rough order of expected leverage. Not
sequenced — many can be tackled independently.

### 1. `--strict` mode with sub-region cropping

Claude Vision is more thorough on a 200×200 region than on a full
800×600 screenshot. A `--strict` mode would crop the screenshot into
named sub-regions (control area only, JSON panel only, 2×2 grid
only, title bar only) and review each in isolation, then combine the
findings. Worth the extra capture cost when a sim has ≥3 distinct
visual zones.

Implementation: small Python helper using Pillow to crop, or pass
multiple `<image>` blocks to Claude Vision in the same review call.

### 2. Width-responsive testing

MicroSims must render correctly across iframe widths (400 px mobile,
700 px tablet content column, 1000 px desktop). The current skill
captures only at 800 px (the `bk-capture-screenshot` default). A
single sim that passes at 800 px can break at 400 px (button row
wraps poorly, slider labels collide), and that defect is invisible
without multi-width capture.

Add `--widths "400,700,1000"` (or a default triple) and run the
checklist against each width's screenshot. Flag any defect that
manifests at one width but not another — those are the responsive-
design bugs that today escape into production.

### 3. Animation-aware capture

For sims that animate (rotating, pulsing, particles), a single
screenshot misses defects that only appear mid-animation: a label
that's clear at t=0 but overlapped at t=1.5 s, an axis that's
correct on first frame but drifts off-canvas as a value crosses a
threshold. Capture multiple frames at staggered delays (1 s, 3 s,
5 s) and compare.

This is closer to a small video-review than a screenshot review;
the rule "Claude Vision is non-deterministic" applies even more
strongly across frames.

### 4. Color-contrast assertion

The visual checklist checks contrast "by eye" — Claude Vision can
spot dark-gray-on-aliceblue as fine and dark-gray-on-red-header as
hard to read. But a numeric WCAG contrast ratio gives a defensible
threshold, especially for accessibility audits.

Add a small Python helper that samples pixel colors at known text
locations (using `data.json` overlay coordinates if available, or a
tighter cropped region of the screenshot) and computes the WCAG
ratio against the surrounding background. Fail anything below 4.5:1
for body text, 3:1 for large text. Pure addition — Claude Vision
still does the qualitative review; this is the quantitative
backstop.

### 5. Auto-invoke from `microsim-generator`

The most natural place for this skill is the final step of
`microsim-generator`: after the .js is written and the iframe height
fixed, run the layout reviewer. That makes "looks right when
embedded" part of the definition of done for new sims, not a
separate manual QA step. Already alluded to in the description
("also proactively after generating a new MicroSim"); making it an
explicit hand-off in the generator's workflow is the next concrete
step.

### 6. Eval set with assertions

The current test was qualitative: I reviewed 16 sims, found defects,
applied fixes, re-verified. To follow `skill-creator`'s full
workflow, the next step is an `evals/evals.json` with ~5 prompts
covering known-broken sims (with planted defects) and known-good
sims, plus assertions like:

- "report identifies the clipped axis labels"
- "patch increases axisOffset to ≥ textWidth(label) + 8"
- "approved sims are skipped without modification"
- "iframe-clipping issues are delegated, not fixed in-place"

That gives a regression-testable benchmark for future skill
revisions — including model upgrades that improve Claude Vision.

### 7. Library coverage expansion

`common-fixes.md` covers p5.js deeply and Mermaid / vis-network /
Chart.js / Leaflet at a thinner layer. Other libraries used in the
project but not yet covered:

- **Plotly** — axis-range mismatch with annotation positions
- **vis-timeline** — overlapping items at narrow widths
- **comparison-table** / **html-table** — column-overflow,
  detail-panel positioning
- **Venn.js** — circle radii vs. label collision

Each library's quirks deserve their own section with at least 2-3
real-world failure patterns drawn from production sims.

### 8. Defect taxonomy + severity

Currently every FAIL is reported flat. A severity tier:

- **Critical** — sim is unusable (controls obscured, key info
  unreadable, sim doesn't render)
- **Major** — clearly wrong but functional (clipped labels,
  overlapping titles, low contrast)
- **Minor** — aesthetic only (slight misalignment, suboptimal color
  choice)

Lets the user batch-fix Critical first, defer Minor for a polish
pass. Easy to add to the report template.

### 9. Baseline screenshots and visual diffing

Once a sim is `approved`, capture a "baseline" screenshot. On any
future revisit, diff the new screenshot against the baseline (e.g.
with ImageMagick's `compare` or pixelmatch). Any pixel-level
divergence flags a regression that the layout reviewer should look
at carefully — even if the new state passes the checklist on its
own, regressing from a previously-approved layout is a flag.

### 10. Library-detection automation

Step 2 currently has Claude open `main.html` and figure out which
library is in use. A simple deterministic helper that grep's
`main.html` for known CDN URLs (`p5.js`, `mermaid`, `chart.js`,
`leaflet`, etc.) and returns the library name would be more reliable
and save Claude's reading budget for the actual review.

Could also auto-route to the relevant section of `common-fixes.md`
based on the detection.

### 11. Cross-sim consistency checker

Beyond per-sim review: a consistency check across all sims in a
project. Are color schemes consistent? Do all sims use the same
title font size? Is the aliceblue-on-white drawing/control split
applied uniformly? Catches drift over time as different sims get
generated by different sessions.

This is meaningfully different from per-sim review — it's a
**collection** review. May warrant a sibling skill rather than a
mode of this one.

### 12. Output formats

Currently the skill produces a markdown report. For batch runs,
JSON output (machine-readable) would let other tools consume it.
For chapter-level review (review every sim in a chapter at once), a
single combined report keyed by chapter section.

---

## Closing note

The skill in its current form is genuinely useful — it caught three
in-scope defects across 16 sims on its first run, all of which were
real (not false positives) and all fixable with small targeted
edits. The library-agnostic framing lets it work on Mermaid and
Chart.js sims as well as p5.js, which broadens its applicability
considerably.

The biggest force multiplier for the next iteration is probably
**width-responsive testing** (item 2). MicroSims live or die by how
they look at the actual content-column width in the deployed site,
not at whatever default Chrome window happens to be open. Catching
responsive bugs at QA time keeps them from becoming production
issues.
