---
title: "Investigation: README validator sections and links"
status: CURRENT
date: 2026-07-18
repository: yaniv256/dmccreary-claude-skills
area: skills/book-publisher
---

# README Validator Sections And Links

## Symptom

The active README validator can treat headings inside fenced examples as real
README sections. Its link check also reports repository-relative destinations
as valid based only on URL syntax, even when the target file or heading does not
exist. The inline-link regular expression truncates destinations containing
balanced parentheses and does not model reference links or images.

## Reproduction

The investigation branch starts from the exact tree published by stacked PR
#38. At that point:

- ordinary prose containing section names is correctly rejected;
- a synthetic repository-relative guide path is correctly accepted as a
  syntactically valid Markdown destination;
- `## Overview`, `## Getting Started`, and `## Contact` inside a fenced
  `markdown` example are incorrectly accepted as required sections;
- a synthetic nested-parenthesis link destination is truncated at its first
  closing parenthesis;
- a syntactically valid link to a missing repository file is never resolved;
- heading fragments are never checked against the target Markdown document.

## Root Cause

`extract_section_headings()` recognizes ATX and Setext patterns without sharing
the stateful fenced-block classification already used elsewhere in the file.
Markdown example content therefore enters the section inventory.

`extract_links()` uses one regular expression whose destination ends at the
first closing parenthesis. Markdown destinations are balanced structures, and
reference links are resolved through separate definitions, so the expression
cannot represent the supported syntax.

`validate_url_format()` answers only whether a destination has an accepted
scheme or a non-empty path, fragment, or query. `validate_readme()` then labels
that result as a working-link check. No function receives repository context,
resolves a local path, prevents repository escape, verifies the target exists,
or checks a Markdown heading fragment.

The causal chain is therefore:

1. Markdown is reduced to independent line or regex matches.
2. Parser state and reference definitions are lost.
3. Syntactically plausible strings are classified as sections or links.
4. The report presents those classifications as structural and working-link
   evidence.
5. A broken README can receive a passing link result and an inflated section
   score.

## Confirmed Predictions

- If parser state is the missing boundary, a required heading inside a fenced
  example is counted while the same text in ordinary prose is not. Confirmed.
- If the inline regex is the destination boundary, the first balanced closing
  parenthesis truncates a valid nested-parenthesis path. Confirmed.
- If link checking is syntax-only, changing an internal target from an existing
  file to a missing file leaves the result valid. Confirmed.

## Remediation Plan

1. Introduce one stateful Markdown structure scan shared by section and link
   validation. Ignore fenced content and HTML comments.
2. Preserve ATX and Setext heading structure and generate deterministic GitHub
   heading anchors, including duplicate suffixes.
3. Extract inline links and images with balanced delimiters, resolve full and
   collapsed reference links, and recognize autolinks.
4. Classify destinations as external, mail, same-document fragment, or
   repository-local.
5. Resolve repository-local paths relative to the README, reject repository
   escapes, require targets to exist, and validate fragments for Markdown
   targets. Treat leading-slash links as origin-relative and unverified because
   GitHub resolves them against the host, not the repository checkout.
6. Keep external reachability explicitly unverified rather than performing
   policy-sensitive network requests inside the local validator.
7. Preserve the existing public report fields while adding typed link findings
   and field-level diagnostics.
8. Update the active guide so its claims match the measured contract.
9. Add red/green regression coverage, run repository-wide validation, compound
   the learning, and publish a stacked reviewable PR.

## Closure Criteria

- Fenced example headings cannot satisfy required sections.
- Existing relative, origin-relative, fragment, reference, image, nested-
  parenthesis, mail, and external destinations are classified correctly.
- Missing files, missing Markdown anchors, repository escapes, and malformed
  destinations fail with actionable reasons.
- External links are reported as syntax-valid but not reachability-verified.
- Existing license, canonical metrics, and stateful fence behavior remain green.
- The active guide no longer promises network-level working-link validation.
- The remediation is merged, propagated to the managed installed skill, and
  verified against a representative textbook README before this investigation
  is marked resolved.

## Remediation Evidence

The investigation branch now implements the planned contract:

- one stateful visible-Markdown scan supplies structural headings and named
  sections;
- a balanced scanner covers inline, reference, image, badge, autolink, and
  multiline destinations;
- repository-relative files and Markdown anchors are verified against the
  checkout, while repository escape and unreadable targets fail closed;
- origin-relative and external URLs are explicitly reported as unverified;
- broken local links make the overall validator result invalid;
- the active guide describes the same evidence boundary;
- a linear bracket-pairing pass prevents malformed input from creating
  quadratic scanning behavior.

Verification on 2026-07-18:

- 70 of 70 `book-publisher` contract tests passed;
- 194 of 194 tests passed across the ten repository skill test directories;
- 10,000 deterministic fuzz cases completed without a parser exception;
- `py_compile`, `compileall`, and `git diff --check` passed;
- the new CE Compound learning passed frontmatter and mechanical claim
  validation.

The implementation remains pending publication, merge, managed-install parity,
and representative downstream validation. This investigation therefore remains
`CURRENT` rather than claiming resolution early.
