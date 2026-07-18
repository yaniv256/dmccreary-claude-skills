---
title: Publication metrics require field-level authority, not plausible recounting
date: 2026-07-17
category: logic-errors
module: book-publisher
problem_type: logic_error
component: tooling
symptoms:
  - "README totals contradicted canonical book metrics while following the documented publication route."
  - "A broad filesystem scan emitted plausible chapter, word, equation, and concept counts without identifying their authority."
root_cause: logic_error
resolution_type: code_fix
severity: high
tags:
  - book-publisher
  - canonical-metrics
  - provenance
  - semantic-validation
---

# Publication metrics require field-level authority, not plausible recounting

## Problem

The README publication route named `docs/learning-graph/book-metrics.json` as
the canonical source for book-wide totals, but also offered a broad filesystem
scanner that independently recounted the same fields. A compliant caller could
therefore publish a plausible README whose chapter, word, equation, or concept
counts contradicted the canonical artifact.

## Symptoms

- One target book's canonical report said 12 chapters and 162,054 words while
  the fallback scanner said zero chapters and 177,072 words.
- The scanner exposed recounted values under ordinary metric names, with no
  marker distinguishing canonical values from local observations.
- The README validator checked Markdown shape but did not compare metric claims
  to canonical JSON.
- Adding review and evidence Markdown changed the published word count even
  though learner-facing content had not changed.

## What Didn't Work

Documenting a "single source of truth" was insufficient while the same route
still advertised another producer for the same fields. Schema validation was
also insufficient: both the canonical value and the conflicting recount can be
valid non-negative integers.

Raw modification-time freshness checks were not reliable in clean Git
checkouts because checkout order can make an unchanged source look newer than
its generated artifact. Conversely, checking only files that still exist
misses source deletions. Freshness needed repository history when Git evidence
was available and a filesystem fallback only when it was not.

## Solution

The publication boundary now separates two namespaces:

1. `canonical` contains every field defined by
   `docs/learning-graph/book-metrics.json`, with JSON Pointer provenance for
   each value (`skills/book-publisher/scripts/metrics_authority.py:424`).
2. `supplemental` contains only observations absent from the canonical schema:
   Markdown-file count, fenced-code-block count, and image-asset count
   (`skills/book-publisher/scripts/collect-site-metrics.py:59`).

The authority module fails closed when canonical data is missing, malformed,
schema-invalid, stale, mirrored inconsistently, reached through a symlinked
path, or paired with disagreeing identity metadata
(`skills/book-publisher/scripts/metrics_authority.py:312`). Git-backed
freshness includes additions, modifications, renames, and deletions after the
canonical artifact's last commit (`skills/book-publisher/scripts/metrics_authority.py:183`).

README validation parses recognized metric rows only from the mandated
`Site Status and Metrics` section and compares every canonical claim with its
authoritative field. Conflicts, duplicate values, and non-numeric substitutions
are hard failures (`skills/book-publisher/scripts/validate-readme.py:245`).

The archived README generator delegates to the active scanner and validator
instead of carrying a second implementation. Contract tests also scan every
guidance surface so prose cannot silently restore broad fallback recounting
(`skills/book-publisher/tests/test_readme_metrics_contract.py:22`).

## Why This Works

The system no longer asks whether two numbers look reasonable. It asks which
producer is authorized to define each field. Once a field belongs to the
canonical schema, no fallback may substitute for it. Supplemental scanning can
still provide useful repository observations, but its separate namespace and
provenance prevent those observations from impersonating publication facts.

Git-aware freshness avoids checkout-mtime false positives while still detecting
committed and working-tree source changes, including deletions. Semantic README
validation closes the last gap by checking the final human-facing artifact, not
only the intermediate JSON.

## Prevention

- Give each published field exactly one authority and include per-field
  provenance in machine-readable output.
- Put fallback observations in an explicitly separate namespace; never reuse a
  canonical field name for a recount.
- Validate final publication claims against canonical values, including
  duplicate, malformed, missing, stale, and disagreement cases.
- Use Git history for generated-artifact freshness in tracked clean checkouts;
  use mtimes only when Git cannot prove freshness.
- Include source deletions, symlink boundaries, identity disagreement, and both
  supported source layouts in adversarial tests.
- Delegate archived entry points to the active implementation so compatibility
  surfaces cannot drift into a second contract.

## Related Issues

- Investigation: `docs/investigations/readme-route-canonical-metrics.md`
- Generator-side layout learning:
  `docs/solutions/logic-errors/book-metrics-layout-discovery.md`
