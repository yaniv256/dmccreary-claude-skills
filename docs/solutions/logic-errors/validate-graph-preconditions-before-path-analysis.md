---
title: Validate Graph Preconditions Before Path Analysis
date: 2026-07-16
category: logic-errors
module: learning-graph-generator
problem_type: logic_error
component: tooling
symptoms:
  - "A self-dependent concept causes RecursionError instead of a quality report"
  - "The analyzer claims no self-dependencies without computing that result"
root_cause: missing_validation
resolution_type: code_fix
severity: high
tags: [learning-graph, dag, cycle-detection, validation-order, recursion]
---

# Validate Graph Preconditions Before Path Analysis

## Problem

The learning-graph analyzer verified whether a graph was acyclic, then ran its
recursive longest-path routine even when that verification failed. A self-edge
or larger cycle therefore produced `RecursionError` before the analyzer could
write the diagnostic report the user needed.

The report also printed a constant `Self-Dependencies: None detected` line.
The claimed validation result had no corresponding computation.

## Symptoms

- A one-row graph with `Dependencies=1` crashes in `find_longest_chain`.
- No Markdown quality report is written for the invalid graph.
- The report source contains a successful self-dependency statement regardless
  of input.

## What Didn't Work

DAG detection alone did not protect the analyzer. Validation results matter
only when downstream control flow respects them. Computing `is_dag` and then
calling a DAG-only algorithm unconditionally left the original failure intact.

Adding an active-recursion guard only to longest-path DFS would prevent the
stack overflow, but it would still blur responsibilities. Cycle detection owns
diagnosis; longest-path analysis should run only after its DAG precondition is
established.

## Solution

Collect self-edges explicitly, validate the DAG, and gate longest-path analysis
on that result:

```python
self_dependencies = find_self_dependencies(dependencies)
is_dag, cycles = verify_dag(concepts, dependencies)
if is_dag:
    max_chain_length, max_chain_path = find_longest_chain(
        concepts, dependencies
    )
else:
    max_chain_length, max_chain_path = 0, []
```

For cyclic input, generate the rest of the report and explain that path length
was not computed. For self-edges, report each offending concept ID and label.
PR [#7](https://github.com/yaniv256/dmccreary-claude-skills/pull/7)
implements this behavior.

Regression tests cover three boundaries:

1. A one-node self-edge produces a complete report naming the concept.
2. A two-node cycle produces a complete report without a false self-edge.
3. A valid three-node DAG retains longest-path length 3.

## Why This Works

Longest-path analysis in this implementation is defined for a DAG. DAG
validation is therefore not merely another metric; it is a runtime precondition
for the recursive path algorithm. Gating on `is_dag` turns invalid input into
an ordinary diagnostic state instead of an uncontrolled recursion path.

Computing self-edges separately also keeps the report honest. A statement in a
quality report should be backed by a measured value, including successful
statements such as "none detected."

## Prevention

- Treat structural validators as control-flow gates for algorithms that depend
  on the validated property.
- Include invalid fixtures for self-edges and multi-node cycles, not only valid
  DAG examples.
- Never print a successful validation statement from a constant string; bind
  it to a computed result.
- Require invalid input to produce a useful report without an exception.

## Related Issues

- [Investigation record](../../investigations/2026-07-16-learning-graph-analyzer-self-dependency.md)
- [PR #7](https://github.com/yaniv256/dmccreary-claude-skills/pull/7)
