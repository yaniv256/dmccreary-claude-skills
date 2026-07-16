---
title: Init Textbook Scaffold Has No Fail-Closed Write Contract
date: 2026-07-16
status: current
severity: high
component: skills/book-installer/references/init-textbook.md
trello: https://trello.com/c/zSHaskG3/219-investigation-init-textbook-scaffold-can-overwrite-files-and-corrupt-metadata
---

# Init Textbook Scaffold Has No Fail-Closed Write Contract

## Symptom

The active `book-installer` route tells an agent to copy the canonical
`assets/init-textbook/` tree and perform placeholder replacement with an
inline `sed` or Python command. It has no executable initializer that owns
preflight validation, substitution, copying hidden files, or post-write
verification.

That leaves three user-visible failure paths:

1. The documented preflight checks only `mkdocs.yml`, `docs/index.md`, and
   `docs/license.md`. Other destination files, including `.gitignore`, a VS
   Code workspace, `plugins/social_override.py`, and starter pages, can be
   overwritten even though the guide says existing content is authoritative.
2. A literal substitution can emit invalid YAML when human metadata contains
   a single quote. Values containing replacement metacharacters can also be
   corrupted by an ad hoc `sed` command.
3. The scaffold config labels its GitHub control "Edit this page" while
   `edit_uri: 'blob/main/docs'` sends the reader to a read-only source view.

The `mkdocs.yml` template also describes an obsolete social-hook contract. It
claims the hook emits all social tags on every page with a site-wide cover
fallback; the shipped hook deliberately changes only `og:image` and
`twitter:image` when a page explicitly declares `image:`.

## Preserved evidence

- The archived standalone skill and the active `book-installer` template tree
  are byte-identical. Commit `f93e0172` archived the standalone skill because
  it was consolidated into feature 0, not because its behavior was rejected.
- A representative scaffold with ordinary values has no unresolved template
  tokens and passes `uvx --with mkdocs-material mkdocs build --strict`.
- The generated home page contains the expected cover `og:image` and
  `twitter:image`; an ordinary page contains no injected social tags. This
  refutes the active `mkdocs.yml` comment while matching the hook source.
- The generated edit control resolves to
  `https://github.com/yaniv256/demo-book/blob/main/docs/index.md` despite its
  accessible title "Edit this page".
- No focused test currently exercises feature 0. The only tests under
  `skills/book-installer/tests/` cover feature detection.

## Initial hypotheses

| Hypothesis | Prior | Evidence | Status |
| --- | ---: | --- | --- |
| Consolidation copied the old prose but omitted an executable boundary | 65% | Feature 0 is a verbatim migration and has no initializer script | Confirmed |
| The templates cannot produce a strict build at all | 15% | Representative strict build succeeds | Refuted |
| The social hook still implements the site-wide fallback described in config | 10% | Hook returns unchanged HTML when `image:` is absent | Refuted |
| None of the listed causes | 10% | Reserved for another write path | Still possible |

## Root cause

The route treats project creation as prose-guided file manipulation rather
than a transaction. The instructions specify desired files but do not provide
one executable owner for input validation, collision detection, format-aware
substitution, and verification. The archived-to-active consolidation preserved
that weak boundary and then accumulated config-comment and GitHub-link drift.

## Remediation

1. Add a standard-library initializer with explicit arguments for every
   placeholder and an optional preview mode.
2. Precompute every destination and fail before writing when any output would
   collide with an existing path.
3. Validate identifiers and one-line metadata before writes; escape values in
   quoted YAML contexts rather than relying on raw replacement.
4. Copy hidden and binary assets, rename the workspace deterministically, and
   fail if any placeholder remains.
5. Correct the GitHub edit URI and the social-hook comment.
6. Route every feature-0 entry point and example through the initializer and
   make strict build plus social metadata checks agent-owned verification, not
   merely commands suggested to the user.
7. Add focused tests for happy-path output, punctuation-safe metadata,
   collision atomicity, preview non-mutation, hidden/binary assets, unresolved
   placeholders, and generated configuration semantics.
8. Run the representative scaffold against a real MkDocs Material build,
   complete independent review, merge, and read back from `origin/main`.

## Closure criteria

- Existing destination files cannot be overwritten without an explicit future
  contract that is separately designed and tested.
- Apostrophes and ordinary punctuation in human metadata produce valid YAML.
- Preview and validation failures leave the destination byte-for-byte
  unchanged.
- The canonical scaffold includes all hidden and binary assets and contains no
  unresolved placeholders.
- The generated edit control targets GitHub's edit surface.
- Config comments match the actual social-hook boundary.
- Focused tests and a strict representative build pass.
- The fix is merged, independently verified on the target branch, and the
  reusable transactional-scaffolding lesson is compounded.
