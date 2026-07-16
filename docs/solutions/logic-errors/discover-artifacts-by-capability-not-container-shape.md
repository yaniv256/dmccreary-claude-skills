---
title: Discover Artifacts by Capability, Not Container Shape
date: 2026-07-16
category: logic-errors
module: microsim-utils
problem_type: logic_error
component: tooling
symptoms:
  - "A support-only directory is counted and graded as a learner-facing MicroSim"
  - "A fictitious validation row lowers the aggregate quality score"
root_cause: missing_validation
resolution_type: code_fix
severity: high
tags: [microsim, discovery, validation, support-directories, capability-detection]
---

# Discover Artifacts by Capability, Not Container Shape

## Problem

The MicroSim batch validator assumed every visible child directory under
`docs/sims/` was a simulation. A `shared` directory containing only common CSS
and JavaScript was therefore graded as a broken learning object and included in
the aggregate score.

## Symptoms

- A textbook with 14 runnable simulations reported 15 validation results.
- The extra `shared` result received score 5/D even though it was not intended
  to be learner-facing.
- The aggregate score mixed product artifacts with implementation support.

## What Didn't Work

Hard-coding `shared` as a skipped directory would fix one repository layout but
would repeat the same bug for `assets`, `runtime`, or any future support folder.

Requiring every candidate to contain the complete generated bundle would also
be wrong. The validator is responsible for reporting missing `main.html`,
`index.md`, and `metadata.json`; requiring all three during discovery would
silently hide the incomplete simulations it needs to diagnose.

## Solution

Define a small set of identity-bearing artifacts and admit a directory when it
contains any one of them:

```python
MICROSIM_IDENTITY_FILES = ("main.html", "index.md", "metadata.json")


def discover_sim_dirs(sims_dir):
    return sorted([
        name for name in os.listdir(sims_dir)
        if os.path.isdir(os.path.join(sims_dir, name))
        and not name.startswith(".")
        and any(
            os.path.isfile(os.path.join(sims_dir, name, identity_file))
            for identity_file in MICROSIM_IDENTITY_FILES
        )
    ])
```

The defining behavior is in
`src/microsim-utils/validate-sims.py:42-60`. Batch mode uses the discovery
function, while explicit `--sim NAME` remains a direct diagnostic path at
`src/microsim-utils/validate-sims.py:385-389`.

PR [#10](https://github.com/yaniv256/dmccreary-claude-skills/pull/10)
implements and regression-tests this contract.

## Why This Works

The boundary now asks whether a directory carries evidence of the artifact the
validator understands, rather than treating directory placement as sufficient
identity. Support-only folders have no MicroSim identity and are excluded.

Using an any-of rule preserves partial construction states. A directory with
only `index.md`, for example, is still validated and receives the actionable
missing-entrypoint and missing-metadata findings that motivated the validator.

Keeping explicit single-directory validation separate also preserves a useful
escape hatch: maintainers can deliberately inspect any named directory without
weakening normal batch results.

## Prevention

- Define artifact identity at filesystem discovery boundaries; do not infer it
  from parent location or directory shape alone.
- Prefer capability markers over hard-coded support-folder names.
- Include both support-only and partially built artifacts in discovery tests.
- When a validator checks completeness, avoid a discovery rule that requires
  completeness first.
- Preserve an explicit diagnostic path for maintainers who need to inspect an
  otherwise excluded object.

## Related Issues

- [Investigation record](../../investigations/2026-07-16-microsim-validator-support-directory.md)
- [PR #10](https://github.com/yaniv256/dmccreary-claude-skills/pull/10)
