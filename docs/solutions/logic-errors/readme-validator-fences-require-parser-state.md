---
title: README validators must track fenced-code parser state
date: 2026-07-15
category: logic-errors
module: book-publisher
problem_type: logic_error
component: tooling
symptoms:
  - "Valid labeled Markdown code blocks were reported as missing language specifications."
  - "A genuinely unlabeled fenced block was counted twice, while tilde fences were ignored."
root_cause: logic_error
resolution_type: code_fix
severity: medium
tags:
  - markdown
  - fenced-code
  - readme-validator
  - semantic-validation
---

# README validators must track fenced-code parser state

## Problem

The book-publisher README validator counted each line matching a backtick-fence
regular expression independently. Because a valid closing fence has no info
string, every closing fence was reported as a new code block without a language
specification.

## Symptoms

- A labeled block such as ` ```bash ` followed by ` ``` ` produced one false
  formatting issue.
- An unlabeled block produced two findings: one for its opening fence and one
  for its closing fence.
- Tilde fences were outside the original regular expression and therefore
  escaped the same rule entirely.

## What Didn't Work

Counting empty captures from a line-oriented expression could not distinguish
an unlabeled opening from a closing fence. Expanding that expression to include
tilde markers would have widened syntax coverage without fixing the semantic
error: whether a bare marker opens or closes a block depends on the preceding
parser state.

Suppressing every bare fence would also have been wrong. A bare fence outside
an active block is precisely the unlabeled opening the validator is intended to
report.

## Solution

Replace the independent match count with a small stateful scanner. The scanner
records the active marker character and opening length, treats a bare matching
marker of at least that length as the closer, and counts an empty info string
only when no block is active
(`skills/book-publisher/scripts/validate-readme.py:89-131`).

The formatting check now consumes that semantic count instead of interpreting
regex captures itself
(`skills/book-publisher/scripts/validate-readme.py:148-151`).

Regression tests cover labeled backtick blocks, multiple blocks with a longer
outer fence, unlabeled blocks, tilde fences, and an unclosed unlabeled opening
(`skills/book-publisher/tests/test_validate_readme.py:13-60`).

## Why This Works

Fenced code is a paired construct. The same bare marker has opposite meanings
depending on whether the parser is outside or inside a block. Tracking that one
bit of state, plus the marker type and minimum closing length, gives each match
the context required to classify it correctly.

The negative controls protect both sides of the contract: labeled blocks must
not create findings, and genuinely unlabeled openings must still create exactly
one finding.

## Prevention

- When validating paired or nested syntax, model the minimum parser state
  needed to interpret a token instead of counting token-shaped regex matches.
- Include a valid example, an invalid example, and a negative control in the
  same regression suite so a false-positive fix cannot silence real errors.
- Cover every supported delimiter family and variable-length form explicitly.
- Verify reusable validators at both boundaries: their focused source tests and
  at least one mature downstream artifact that previously exposed the defect.

## Related Issues

- Investigation record:
  `docs/investigations/2026-07-15-readme-validator-closing-fences.md`
- Related semantic-validation learning with a different root cause:
  `docs/solutions/logic-errors/book-metrics-layout-discovery.md`
