# README Route Canonical Metrics Investigation

## Status

CURRENT

## Symptom

The active `book-publisher` README route declares
`docs/learning-graph/book-metrics.json` to be the single source of truth for
book-wide metrics, but the same guide still presents
`scripts/collect-site-metrics.py` as a broad source for chapters, words,
MicroSims, glossary terms, FAQs, quizzes, references, equations, and learning
graph statistics.

The fallback scanner recursively counts the entire `docs/` tree and returns
those derived values under canonical-looking field names. A generated README
can therefore contradict `book-metrics.json` while still following the route's
documented example session.

## Impact

Publication artifacts can report plausible but false book totals. The defect
crosses the shared publication boundary: a README can disagree with LinkedIn,
carousel, case-study, and press-release artifacts that correctly consume the
canonical metrics file. Because review and evidence documents are included in
the scanner's word count, the error grows as quality documentation improves.

## Preserved Reproduction

Source under investigation: `yaniv256/dmccreary-claude-skills`, branch
`fix/readme-canonical-metrics`, based on `92f9af35`.

Representative target: `yaniv256/x-marketing-frontier-textbook`.

The card's preserved canonical report records 12 chapters, 158 concepts,
14 MicroSims, 162,054 words, 158 glossary terms, 48 FAQs, and 3 equations.
Running the current fallback scanner against the local textbook checkout on
2026-07-17 returned:

- 0 chapters
- 0 concepts
- 14 MicroSims
- 177,072 words
- 158 glossary terms
- 48 FAQs
- 30 equations
- 309 Markdown files

The exact totals vary with the target checkout, which is itself evidence of
the problem: the scanner includes non-learner-facing review, evidence, and
operational Markdown that the canonical generator classifies deliberately.

## Source Evidence

| Location | Observed behavior |
| --- | --- |
| `skills/book-publisher/references/readme-guide.md`, Step 6 | Correctly says README metrics must come from `book-metrics.json`; permits the scanner only for fields absent from the canonical schema. |
| `skills/book-publisher/references/readme-guide.md`, Supporting Scripts | Contradicts Step 6 by advertising the scanner for chapter, word, MicroSim, glossary, FAQ, quiz, image, diagram, and learning-graph statistics. |
| `skills/book-publisher/references/readme-guide.md`, Example Session | Tells the agent to scan `docs/` and run `collect-site-metrics.py` to gather broad statistics. |
| `skills/book-publisher/scripts/collect-site-metrics.py` | Recursively scans all Markdown and emits chapters, words, equations, concepts, quizzes, glossary terms, FAQs, references, and MicroSims without reading canonical JSON. |
| `skills/book-publisher/tests/` | Contains no executable contract separating canonical fields from fallback-only fields. |

## Root Cause Hypothesis

The active route combines two contracts that were never reconciled:

1. The original standalone README generator used one broad repository scanner
   as its source for publication metrics.
2. The consolidated `book-publisher` route later established
   `book-metrics.json` as the cross-artifact authority.
3. Step 6 was updated to describe the new authority, but the scanner API,
   Supporting Scripts section, Example Session, and executable tests retained
   the original broad-scanner contract.
4. The scanner returns ordinary integers with no per-field authority or
   provenance, so downstream generation cannot distinguish canonical fields
   from fallback observations.
5. No semantic validator rejects a README candidate whose values disagree
   with canonical JSON.

This produces the symptom directly: a compliant agent can choose the legacy
example path, publish scanner-derived totals, and still believe it followed
the active route.

## Prediction

If the contract split is the root cause, a fixture whose canonical JSON
intentionally disagrees with scanned content will currently produce both sets
of values without an error or authority marker. After remediation, canonical
fields will come only from validated `book-metrics.json`; the fallback scanner
will expose only explicitly unsupported observations, and a candidate that
substitutes scanner values for canonical fields will fail validation.

## Required Remediation

1. Make validated `book-metrics.json` the only authority for every field in
   its schema.
2. Narrow the fallback scanner's public output to explicitly unsupported
   observations such as Markdown-file, code-block, and image-asset counts.
3. Emit per-field provenance suitable for README audit and validation.
4. Fail closed when canonical metrics are missing, malformed, stale, or
   inconsistent with supplied identity metadata.
5. Correct active, archived, and historical guidance that advertises broad
   scanning.
6. Add flat-layout, directory-layout, missing, malformed, stale, and
   disagreement regressions.
7. Run repository-wide validation and installed-skill parity after merge.

## Closure Gate

Keep this investigation `CURRENT` until the remediation is merged, the source
branch is verified on `origin/main`, and the installed `book-publisher` skill
is byte-identical to the merged source.

## Remediation Evidence

The review branch now:

- exposes canonical and supplemental fields in separate namespaces with
  per-field provenance;
- validates schema, freshness, metadata mirrors, identity, and symlink
  boundaries before publication;
- checks README claims against canonical values and rejects malformed or
  conflicting claims;
- delegates archived scanner and validator entry points to the active contract;
- covers flat and directory chapter layouts, source additions and deletions,
  clean-checkout mtime ordering, stale/missing/malformed authority, identity
  disagreement, symlinked parents, and README claim disagreement.

Local validation on 2026-07-17 passed all 53 `book-publisher` tests, all 179
tests in the repository-wide acceptance matrix, Python compilation,
`git diff --check`, and a normal MkDocs build. Strict MkDocs remains blocked by
244 pre-existing warnings. Installed-skill parity remains a post-merge closure
gate.
