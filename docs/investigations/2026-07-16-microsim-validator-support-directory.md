---
title: MicroSim Validator Treats Support Directories as Simulations
date: 2026-07-16
status: investigating
severity: high
component: src/microsim-utils/validate-sims.py
trello: https://trello.com/c/bQdJl9wF/203-investigation-microsim-validator-treats-shared-runtime-as-a-simulation
---

# MicroSim Validator Treats Support Directories as Simulations

## Symptom

Running the batch validator against the X Marketing with actions.json textbook
reports 15 MicroSims although the book contains 14 deployable simulations. The
extra result is `docs/sims/shared`, a support directory containing only the
common `microsim.css` and `microsim.js` runtime assets. It receives a score of
5 and grade D, lowering the aggregate score with a fictitious learning object.

## Minimal reproduction

```text
docs/sims/
├── real-sim/
│   ├── main.html
│   └── index.md
└── shared/
    ├── microsim.css
    └── microsim.js
```

```bash
python3 src/microsim-utils/validate-sims.py \
  --project-dir /path/to/book --format json
```

Observed before remediation: both `real-sim` and `shared` are returned.

Expected: batch discovery returns `real-sim` only. Explicit `--sim shared`
remains available for diagnostics rather than silently changing that command's
meaning.

## Preserved evidence

- The pre-fix batch command against the textbook returned 15 rows and assigned
  `shared` score 5/D.
- The textbook contains 14 directories with a simulation entry point and one
  support-only directory.
- The validator's discovery comprehension currently accepts every non-hidden
  child directory under `docs/sims/`.
- The utilities README defines generated MicroSims by `main.html`, `index.md`,
  and `metadata.json`, and its lifecycle table defines a scaffold using
  `main.html` plus `index.md`.
- The official intelligent-textbook skills overview likewise describes a
  MicroSim as a directory containing `main.html`, code, `index.md`, and
  `metadata.json`: https://dmccreary.github.io/intelligent-textbooks/skills/
- Repository and upstream issue/PR searches found no prior report or pending
  remediation for `validate-sims` and support directories.

## Initial hypotheses

| Hypothesis | Prior | Evidence | Status |
| --- | ---: | --- | --- |
| Batch discovery equates every directory with a MicroSim | 80% | The discovery comprehension checks only directory-ness and a leading dot | Confirmed |
| A stale generated index introduces the `shared` row | 8% | The validator reads the filesystem directly, not an index | Refuted |
| `shared` contains hidden metadata that identifies it as a MicroSim | 5% | It contains only CSS and JavaScript runtime assets | Refuted |
| None of the listed causes | 7% | Reserved for an unobserved discovery path | Refuted by direct trace |

## Root cause

The all-sim discovery branch in `main()` enumerates every non-hidden directory
under `docs/sims/`. Directory placement is treated as sufficient simulation
identity. Support folders therefore flow into `validate_sim`, where the
missing-file checks correctly score absent MicroSim files but apply those
checks to the wrong object.

The tests did not catch this because `validate-sims.py` had no automated test
suite and its original examples assumed `docs/sims/` contained only
simulations.

## Causal chain

1. A textbook centralizes common browser assets in `docs/sims/shared`.
2. Batch discovery accepts `shared` because it is a visible directory.
3. `validate_sim` applies the quality rubric to that support directory.
4. The p5 convention check awards its non-p5 benefit-of-doubt points while all
   learner-object checks fail, producing score 5/D.
5. The fictitious row increments the validated count and lowers the aggregate
   score.

## Remediation plan

1. Add a minimal fixture proving a support-only directory is excluded while a
   real and a partially built MicroSim remain discoverable.
2. Extract batch discovery into a testable function.
3. Treat `main.html`, `index.md`, or `metadata.json` as identity-bearing
   MicroSim artifacts. Requiring all three would hide the missing-file defects
   the validator is meant to report.
4. Preserve explicit `--sim NAME` behavior so a requested directory is always
   validated.
5. Run focused tests, all repository Python tests, and the validator against
   the real textbook.
6. Search sibling utilities for the same broad-directory assumption.
7. Merge the fix, compound the reusable discovery-boundary lesson, and update
   this record with immutable evidence.

## Closure criteria

- A support-only directory does not appear in batch results.
- Directories containing any MicroSim identity artifact remain candidates, so
  incomplete simulations still receive actionable missing-file findings.
- Explicit single-sim validation retains its current behavior.
- The real textbook reports 14, not 15, batch candidates.
- Focused and repository validation pass.
- The fix and durable learning are merged and linked here.

## Pre-merge verification

- The regression test failed before the fix because batch results were
  `index-only`, `main-only`, `metadata-only`, and `shared`.
- Focused discovery tests pass 2/2 after the fix.
- The real X Marketing with actions.json textbook reports 14 candidates and no
  `shared` result.
- Repository Python tests pass 24/24 across book installer, README validation,
  glossary scoring, learning-graph analysis, book metrics, and MicroSim
  validation.
- Same-class search found three sibling discovery paths. `book-status.py` and
  the TODO utility already require `main.html`; the navigation and gallery
  generators require `index.md`. None treats every directory as a MicroSim.
