---
title: Validated Filesystem Objects Must Stay Pinned Through Publication
date: 2026-07-17
category: logic-errors
module: book-installer
problem_type: logic_error
component: tooling
symptoms:
  - "A scaffold can publish through a pathname that changed after validation"
  - "Rollback can delete an attacker-controlled replacement instead of the staged tree"
  - "A generated value containing a placeholder token is substituted a second time"
root_cause: logic_error
resolution_type: code_fix
severity: critical
tags: [filesystem, descriptors, inode-identity, race-conditions, scaffolding, rollback]
---

# Validated Filesystem Objects Must Stay Pinned Through Publication

## Problem

The textbook scaffold validated paths and metadata before writing, but later
reacquired some of them by name. A concurrent rename or replacement could make
publication or cleanup operate on a different filesystem object than the one
that passed validation. Repeated placeholder replacement had the same logical
shape: it reinterpreted inserted data as fresh template syntax.

## Symptoms

- Replacing the staging-directory entry after rendering could redirect
  publication or cleanup.
- Creating an output parent after preflight could bind the write to an
  unvalidated directory.
- A metadata value containing another recognized token could be rewritten
  unexpectedly.

## What Didn't Work

Checking `Path.exists()`, rejecting symlinks, or comparing a directory identity
only once does not close the race. Those checks validate what a pathname meant
at that instant; a later pathname lookup is a new operation against mutable
state.

Likewise, escaping replacement values is not enough when the renderer loops
over placeholders. A later loop iteration still treats text inserted by an
earlier iteration as template input.

## Solution

Keep the validated filesystem identity alive through the entire transaction:

1. Open the project ancestry using directory-relative, no-follow operations.
2. Record each directory's device and inode identity.
3. Create and retain an open descriptor for the staging directory.
4. Render through `/proc/self/fd/<stage-fd>` instead of resolving the stage name
   again.
5. Publish and roll back with descriptor-relative operations, rechecking the
   expected identity before removing any named entry.
6. Fail closed when an output directory appears after the parent set was
   pinned.

The implementation opens and verifies the staging descriptor in
`skills/book-installer/scripts/init_textbook.py:370-400`, performs
descriptor-relative cleanup in
`skills/book-installer/scripts/init_textbook.py:417-454`, and rejects a newly
appeared output directory in
`skills/book-installer/scripts/init_textbook.py:487-509`.

For template values, perform one regex substitution pass. A token-looking
substring introduced by replacement is data, not a second template program.
The final rendered file is then checked for unresolved placeholders.

These changes landed in [PR #30](https://github.com/yaniv256/dmccreary-claude-skills/pull/30).

## Why This Works

An open directory descriptor refers to the opened object even if its pathname
is renamed or rebound. Device and inode comparisons prove that a named entry is
still the object the transaction pinned. Descriptor-relative operations keep
publication and rollback below the validated parent rather than restarting
resolution from a mutable absolute path.

The single-pass renderer applies the same rule at the syntax boundary: only
tokens present in the original template are executable placeholders. Inserted
values never become new instructions.

## Prevention

- Treat validation as binding to an object, not blessing a pathname forever.
- Carry descriptors or another stable identity from validation through write
  and rollback.
- Make cleanup fail closed when identity cannot be proved; do not broadly
  remove a path after an uncertain failure.
- Test adversarial rebinding between validation, staging, publication, and
  cleanup.
- Test replacement values that contain the template language's own delimiters.

The regression coverage is in
`skills/book-installer/tests/test_init_textbook.py:263-367`.

## Related Issues

- [Scaffold safety investigation](../../investigations/2026-07-16-init-textbook-scaffold-contract.md)
- [Linux `open(2)` rationale for directory descriptors](https://man7.org/linux/man-pages/man2/open.2.html)
