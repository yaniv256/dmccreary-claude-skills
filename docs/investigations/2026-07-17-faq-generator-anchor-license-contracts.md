# FAQ Generator Anchor and License Contract Investigation

## Status

IN PROGRESS

## Incident

The `faq-generator` publishes incompatible instructions on its two current
documentation surfaces. `SKILL.md` forbids every anchor-fragment link, while
the skill README tells operators to use section anchors. The same files also
claim different licenses, and neither license claim exactly matches the
repository-wide CC BY-NC-SA 4.0 declaration.

## Impact

- An agent following `SKILL.md` and a person following the README produce
  different link shapes from the same skill.
- The README recommends an output that the operating skill later rejects as a
  hard validation failure.
- Users cannot determine the redistribution terms of the skill from its local
  documentation.
- Installed or copied skill directories can preserve stale guidance because no
  executable contract checks the two source files together.

## Phase 0: Tools

The investigation uses the checked-in Git history, focused text searches,
Python `unittest`, Git, and the repository's existing validation commands. No
production state or ephemeral evidence is involved.

## Phase 1: Timeline and preserved evidence

The defect is present at source commit
`2a66630c8f07c44f8df26150a5ae43cdefc0d0af`.

| Date / commit | Preserved change | Consequence |
| --- | --- | --- |
| 2025-11-01, `b95e17ce` | Created both FAQ files with MIT license text and README guidance to use section anchors. | The two local surfaces initially agreed. |
| 2025-11-11, `6403c8e6` | Declared the repository CC BY-NC-SA 4.0 in the root README. | The FAQ's local MIT claims became stale. |
| 2026-01-30, `2505b14f` | Changed only `skills/faq-generator/SKILL.md` to forbid anchor fragments as a hard rule. | The local README retained the opposite link instruction. |
| 2026-06-23, `14d80663` | Changed the FAQ frontmatter from MIT to CC BY-NC 4.0 but did not update its README. | The local surfaces diverged, and the frontmatter omitted the repository's ShareAlike term. |
| 2026-07-10, `6c8599ce` | Updated unrelated FAQ README references without reconciling anchors or licensing. | The stale README remained an active current surface. |

Current conflicting evidence:

| Location | Published contract |
| --- | --- |
| `skills/faq-generator/SKILL.md`, Critical Rule | All links must target files only; `#` fragments are prohibited. |
| `skills/faq-generator/README.md`, troubleshooting | Use specific section anchors rather than page links. |
| `skills/faq-generator/SKILL.md`, frontmatter | CC BY-NC 4.0. |
| `skills/faq-generator/README.md`, License | MIT and a nonexistent local `LICENSE` file. |
| Root `README.md`, License | CC BY-NC-SA 4.0 for the work. |

## Phase 2: Initial hypotheses

| Hypothesis | Category | Initial probability | Assumptions |
| --- | --- | ---: | --- |
| H1: Later contract changes updated only one of two independently maintained FAQ documentation surfaces. | documentation drift | 78% | Both files remain current user-facing guidance. |
| H2: The README is historical and should not be treated as current guidance. | classification | 8% | Users and repository tooling can identify it as historical. |
| H3: Anchor fragments are conditionally supported despite the hard prohibition. | specification ambiguity | 5% | A documented validation path distinguishes safe anchors. |
| H4: Each skill is intentionally licensed separately from the repository. | licensing boundary | 4% | A local license artifact or explicit exception defines those terms. |
| H5: The true cause is not yet listed. | unlisted | 5% | Another generated or packaged source controls the contract. |

H1 is the maximum-pain hypothesis because it explains both contradictions as a
single missing synchronization and validation boundary. It is tested first.

## Phase 3: Evidence

### E1: Anchor change scope

Commit `2505b14f` deliberately replaced section-anchor guidance with a repeated
file-only rule, but its diff contains only `SKILL.md`. The README's opposite
instruction therefore survived because the second current surface was outside
the change scope.

### E2: License change scope

The FAQ files began with matching MIT claims. The repository adopted CC
BY-NC-SA 4.0 before commit `14d80663` changed only the skill frontmatter to CC
BY-NC 4.0. No local FAQ `LICENSE` file exists, despite the README directing the
reader to one.

### E3: Current-surface evidence

The README was edited as recently as commit `6c8599ce` to update a dependency
reference. It is not marked historical or superseded and remains inside the
active skill directory, so H2 does not explain the contradiction.

### E4: Missing executable boundary

`skills/faq-generator` has no tests. Existing content skills use focused Python
documentation-contract tests to lock agreement between `SKILL.md`, README, and
integration surfaces, but no equivalent test covers FAQ anchors or licensing.

## Phase 4: Revised hypotheses

| Hypothesis | Revised probability | Evidence |
| --- | ---: | --- |
| H1: Independently maintained current surfaces drifted | **99%** | E1-E4 explain the exact surviving contradictions and their history. |
| H2: README is historical | 0% | E3 shows it is maintained and unmarked. |
| H3: Anchors are conditionally supported | 0% | The operating skill repeatedly defines zero fragments as a hard requirement. |
| H4: Intentional separate license | 0% | E2 finds no local license or explicit repository exception. |
| H5: Unlisted cause | 1% | No controlling generated copy has been found. |

## Phase 5: Remediation experiment

### X1: Reconcile and lock both contracts

- **Prediction before change:** a focused test requiring both local surfaces to
  reject anchor fragments and publish the repository license will fail against
  the preserved source.
- **Intervention:** retain the intentional file-only link contract, align both
  FAQ files with CC BY-NC-SA 4.0, remove the nonexistent local-license pointer,
  and add a focused documentation-contract test.
- **Expected success:** the focused test finds no affirmative anchor-fragment or
  MIT guidance, both local surfaces publish the same repository license, and
  the broader repository validation remains green.

## Phase 6: Final hypothesis

H1 is confirmed above 99%: the FAQ skill duplicates operational and licensing
contracts across two current files without a synchronization or regression
gate. Later single-file edits allowed each contract to diverge.

## Phase 7: Blame assignment

### Level 1: Responsible text

| Location | Fault | Severity |
| --- | --- | --- |
| `skills/faq-generator/README.md` troubleshooting | Recommends section anchors that `SKILL.md` rejects. | High |
| `skills/faq-generator/README.md` License | Claims MIT and points to a file that does not exist. | High |
| `skills/faq-generator/SKILL.md` frontmatter | Omits the repository's ShareAlike term. | Medium |

### Level 2: Anti-pattern

The skill duplicates current contracts in hand-maintained prose without a test
that reads the surfaces as one unit.

### Level 3: Development practice

The anchor and license changes were reviewed file-by-file. No class-level
search or documentation-contract test required the adjacent README to change
with the operating skill.

## Phase 8: Immediate remediation

1. Preserve this investigation before source edits.
2. Add a focused FAQ documentation-contract test that fails on the current
   anchor and license contradictions.
3. Make the FAQ README follow the intentional file-only link rule.
4. Make both local FAQ surfaces publish CC BY-NC-SA 4.0 and reference the root
   repository license declaration.
5. Run the focused and complete repository validation gates.
6. Record the reusable synchronization lesson with CE Compound.

## Phase 9: Class search

The same CC BY-NC 4.0 frontmatter appears in six other active skills. That is a
repository-wide licensing class that should be audited separately rather than
silently expanded into this FAQ remediation. This investigation changes only
the contradictory FAQ surfaces and adds a local regression gate.

## Phase 10: Remediation and closure plan

1. Add the failing focused regression.
2. Reconcile the anchor-fragment and license text.
3. Run the focused test, all repository Python tests, and the strict MkDocs
   build.
4. Run CE Compound and record durable guidance.
5. Commit, push, open and merge the source PR.
6. Verify the merged source and any installed or packaged FAQ copies against
   the same contract.

## Closure criteria

- `SKILL.md` and the FAQ README both require file-only internal links and do
  not recommend anchor fragments.
- Both local surfaces publish CC BY-NC-SA 4.0 consistently with the repository.
- The README no longer points to a nonexistent local license file.
- The focused regression fails against the preserved source and passes against
  the remediation.
- Complete repository validation and strict documentation build pass.
- CE Compound records the reusable prevention pattern.
- The source PR is merged and current source and installed or packaged copies
  are verified clean.

## Remediation evidence

- The focused FAQ documentation contract fails all three tests against the
  preserved source and passes all three after the remediation.
- All 83 skill contract tests pass.
- The six `book-metrics` unit tests and the Docker Python lab JavaScript runtime
  contract pass. The older standalone equation-count diagnostic still prints
  its known over-counting demonstration while exiting successfully; its fixed
  counterpart passes.
- The strict MkDocs build passes with `mkdocs-material[imaging]` and
  `mkdocs-glightbox` in an isolated `uvx` environment.
- CE Compound enriched
  `docs/solutions/logic-errors/behavioral-documentation-needs-executable-contracts.md`
  rather than creating an overlapping solution. Both its frontmatter and
  mechanical claims validators pass.
- Merge and post-merge source/package verification remain open closure gates.
