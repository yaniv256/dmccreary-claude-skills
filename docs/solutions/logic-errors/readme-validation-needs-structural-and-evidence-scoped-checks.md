---
title: README validation needs structural parsing and evidence-scoped claims
date: 2026-07-18
category: logic-errors
module: book-publisher
problem_type: logic_error
component: tooling
symptoms:
  - "Headings inside fenced examples could satisfy required README sections."
  - "Repository-relative links passed without the target file or heading existing."
  - "The report described syntax-valid external URLs as working links without testing reachability."
root_cause: missing_validation
resolution_type: code_fix
severity: high
tags:
  - markdown
  - readme-validator
  - link-validation
  - evidence-scope
  - fail-closed
---

# README validation needs structural parsing and evidence-scoped claims

## Problem

A README validator can produce strong-sounding but false evidence when it
reduces Markdown to unrelated regular-expression matches. A token that looks
like a heading may be example code, a link-shaped string may point to nothing,
and a syntactically valid external URL has not necessarily been reached.

In this case, fenced example headings satisfied required sections, a
nested-parenthesis destination was truncated at its first closing parenthesis,
and any non-empty relative path passed as a working link without repository
resolution. The complete causal record is in
[the investigation](../../investigations/readme-validator-sections-and-links.md).

## Symptoms

- `## Overview` inside a fenced `markdown` example counted as the real
  Overview section.
- A synthetic link whose destination contained balanced parentheses became an
  invalid partial destination ending at the first closing parenthesis.
- A missing file, repository escape, or missing Markdown heading anchor did
  not affect the report.
- Leading-slash links risked being misclassified as repository-root paths even
  though GitHub resolves them against the host.
- A naive balanced-delimiter repair took about 25 seconds on 20,000 unmatched
  opening brackets, making adversarial input capable of stalling validation.

## What Didn't Work

- **Independent line and substring checks.** Markdown meaning depends on fence,
  heading, delimiter, and reference-definition state.
- **One inline-link regex.** Balanced parentheses, reference links, images,
  badge nesting, and multiline destinations are not regular delimiter shapes.
- **Calling syntax validation a working-link check.** Syntax can reject a bad
  scheme, but it cannot prove a local target exists or an external server
  responds.
- **Treating `/path` as repository-relative.** On GitHub, it is
  origin-relative; checking a similarly named local file would certify the
  wrong destination.
- **Repeated forward scans for matching brackets.** The result was quadratic
  on malformed input even though one stack pass can pair every bracket.

## Solution

Build one structural view of visible Markdown and make every claim name its
evidence boundary:

1. Mask fenced code, indented code, and HTML comments while preserving line
   positions (`skills/book-publisher/scripts/validate-readme.py:117`).
2. Extract ATX and Setext headings from that view, then reuse those records for
   required sections, named sections, header hierarchy, and GitHub-style
   anchors (`skills/book-publisher/scripts/validate-readme.py:176`).
3. Pair square brackets in one linear stack pass before parsing links
   (`skills/book-publisher/scripts/validate-readme.py:305`). This supports
   balanced inline destinations, full and collapsed references, images,
   nested badge images, autolinks, and multiline destinations without the
   malformed-input slowdown.
4. Resolve README-relative destinations against the checkout, canonicalize the
   result, reject paths outside the repository, require targets to exist, and
   verify fragments against Markdown heading anchors
   (`skills/book-publisher/scripts/validate-readme.py:712-753`).
5. Classify `http`, `https`, and origin-relative destinations as
   syntax-valid-but-unverified. The deterministic local validator performs no
   network request and therefore makes no reachability claim
   (`skills/book-publisher/scripts/validate-readme.py:673-723`).
6. Make malformed or broken local links a hard validation failure, while
   retaining typed issue reasons and compatibility report fields
   (`skills/book-publisher/scripts/validate-readme.py:1232-1272`).

The regression matrix covers visible versus fenced headings, Setext and ATX
sections, relative and origin-relative paths, repository escape, same-document
and target-document fragments, duplicate anchors, nested destinations,
references, images, badges, multiline links, code spans, unreadable Markdown,
unsupported schemes, malformed hosts, external reachability scope, and bounded
behavior on unmatched delimiters
(`skills/book-publisher/tests/test_validate_readme.py:101-377`).

## Why This Works

The parser preserves exactly the context needed to interpret the constructs
the validator claims to understand. A heading is evidence only when it is a
visible structural heading. A local link is verified only after its canonical
target remains inside the repository and exists. A Markdown fragment is
verified only when the target document generates that anchor. An external URL
is reported at the weaker evidence level the validator actually measured.

This distinction also prevents one validation mechanism from accumulating
hidden policy and availability assumptions. External requests can trigger rate
limits, authentication, robots policies, redirects, or mutable network
failures, so they belong in a separate policy-aware publication check rather
than an offline repository validator.

## Prevention

- Parse paired, nested, or stateful syntax with explicit state; do not infer
  structure from token-shaped substrings.
- Name validation fields after what was measured: `local_verified` and
  `external_unverified` are safer than a generic `working` flag.
- Canonicalize paths before repository-boundary checks so `..` and symlink
  escapes cannot pass as local evidence.
- Treat host-relative and repository-relative destinations as different
  classes.
- Include positive, negative, malformed, nested, multiline, and performance
  fixtures in validator contracts.
- Run final-artifact validation as a hard publication gate; do not bury broken
  semantic claims inside a weighted presentation score.
- Keep external reachability in a separate, explicit, policy-aware workflow.

## Related Issues

- [README validators must track fenced-code parser state](readme-validator-fences-require-parser-state.md)
- [Permission Claims Require Typed Publication Authority](permission-claims-require-typed-authority.md)
- [Publication metrics require field-level authority](publication-metrics-require-field-level-authority.md)
