# Investigation: Active Skill Licenses Omit the Repository ShareAlike Term

- **Status:** CURRENT - investigation in progress
- **Opened:** 2026-07-18
- **Repository:** `yaniv256/dmccreary-claude-skills`
- **Trello:** https://trello.com/c/KuPPjfWx/235-investigation-active-skill-licenses-omit-repository-sharealike-term
- **Working branch:** `fix/active-skill-license-sharealike`
- **Baseline:** `e2dd7a0fa4293a31a4e140c904376e9d3c42ea5a`

## Symptom

The repository README and `docs/license.md` say repository content is licensed under Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0). Seven active skill frontmatters instead declare Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0), omitting ShareAlike.

The observed active files are:

- `skills/book-installer/SKILL.md`
- `skills/book-media-generator/SKILL.md`
- `skills/book-publisher/SKILL.md`
- `skills/chapter-content-generator/SKILL.md`
- `skills/course-description-analyzer/SKILL.md`
- `skills/faq-generator/SKILL.md`
- `skills/quiz-generator/SKILL.md`

## Impact

The repository presents two materially different downstream-use contracts for the same current skill content. A user reading only skill frontmatter can reasonably conclude that adaptations need attribution and noncommercial use restrictions but do not need to retain the same license. A user reading the repository license is told the opposite. This is a legal-metadata integrity defect affecting every distribution surface that copies or indexes active `SKILL.md` frontmatter.

Severity is **medium**: the mismatch does not corrupt runtime behavior, but it can cause consumers and automated skill registries to publish incorrect license metadata.

## Established Timeline

All timestamps below are Git commit timestamps and include their recorded timezone.

| Time / marker | Event | Confidence | Source | Timezone |
| --- | --- | --- | --- | --- |
| 2026-06-23 19:48:39 -05:00 | Commit `d2763452` rewrote all 22 skill descriptions as part of the metadata refactor window. | High | `git log --all` | UTC-05:00 from Git |
| 2026-06-23 19:48:57 -05:00 | Commit `25d6e71b` continued the skill-description rewrite. | High | `git log --all` | UTC-05:00 from Git |
| 2026-06-23 20:05:16 -05:00 | Commit `14d80663` continued skill description refactoring. | High | `git log --all` | UTC-05:00 from Git |
| 2026-07-16 10:31:16 -05:00 | Card baseline commit `2a66630c` contains the repository/active-frontmatter mismatch. | High | Git tree inspection | UTC-05:00 from Git |
| 2026-07-17 17:59:24 -05:00 | Current `origin/main` baseline `e2dd7a0f` still contains the mismatch. | High | Git tree inspection | UTC-05:00 from Git |
| 2026-07-18 | Investigation opened from the verified current baseline. | High | This artifact and Trello state | America/Chicago |

## Phase Status

- Phase 0: tools verified
- Phase 1: artifact opened
- Phase 1.5: calibrated prior recorded
- Phase 2: assumptions and initial hypotheses recorded
- Phase 3: passive evidence collected
- Phase 4: revised hypotheses recorded
- Phase 5 through Phase 10: pending

## Tooling Readiness

- Clean isolated worktree created from current `origin/main`.
- Git history and object inspection are available.
- `rg`, structured test discovery, Python, and repository test suites are available.
- The worktree has a fresh codebase-memory index: `home-agent-tomas-worktrees-dmccreary-active-skill-license-sharealike`.
- GitHub PR metadata and CI are available through the connected GitHub app.
- Trello is operable through the actions.json runtime and independently readable through the board projection.

## Generative Prior Calibration

The repository's current investigation corpus contains only four explicit hypothesis outcomes: two `CONFIRMED` and two `REFUTED`. That 50% apparent hit rate is too small and selection-biased to override the methodology's 20% default for a novel defect. I therefore assign a **20% first-pass hit-rate prior**: most hypotheses below will be wrong, and the true cause is probably not on the initial list.

This commits the investigation to obtaining executable evidence before accepting a causal account. The hypothesis table will reserve plurality probability for an unlisted cause, and at least one experiment must be capable of revealing a cause that the initial list did not name.

## Initial Assumptions

| # | Type | Assumption | Initial P | P(not A) | Verification |
| --- | --- | --- | ---: | ---: | --- |
| A1 | policy | The repository-wide CC BY-NC-SA statement applies to active `SKILL.md` content. | 70% | 30% | Inspect wording, history, and any documented exceptions. |
| A2 | behavior | Consumers treat `license:` frontmatter as authoritative licensing metadata. | 70% | 30% | Inspect repository schemas, validators, packaging, and registry use. |
| A3 | ordering | The June 2026 metadata refactor changed at least one affected license line. | 45% | 55% | Diff affected files across the refactor commits and their parents. |
| A4 | provenance | At least one affected skill entered this repository with CC BY-NC metadata. | 50% | 50% | Trace each file to its introduction commit and source history. |
| A5 | policy | No current document intentionally grants a per-skill exception from the repository license. | 80% | 20% | Search current tracked content and Git history for exception language. |
| A6 | ordering | No later commit intentionally relicensed the repository from CC BY-NC-SA to CC BY-NC. | 80% | 20% | Trace README and `docs/license.md` history through current HEAD. |
| A7 | distribution | At least one installed or packaged copy preserves the affected frontmatter. | 70% | 30% | Inventory managed installations and package artifacts by content hash. |

## Initial Hypotheses

The maximum-pain pass raises explanations that implicate repository-maintained metadata or root licensing documentation and discounts the comfortable claim that the two strings are merely harmless shorthand.

| # | Hypothesis | Category | Initial P | Assumptions | Ceiling |
| --- | --- | --- | ---: | --- | ---: |
| H1 | A June metadata refactor mechanically copied or normalized CC BY-NC frontmatter and accidentally dropped ShareAlike. | migration regression | 25% | A1, A2, A3 | 22% |
| H2 | Active skills are intentionally dual-licensed under CC BY-NC despite the repository-wide CC BY-NC-SA declaration. | licensing policy | 8% | not A1, A5 false | 6% |
| H3 | The repository README and license page are stale; the intended current repository license is CC BY-NC. | stale authority | 12% | A6 false | 20% |
| H4 | The skills retain licenses from separate source projects and were imported without a documented repository-level reconciliation. | provenance | 8% | A4, A5 | 40% |
| H5 | The frontmatter value is only a tooling category or abbreviated display label and is not intended as a legal boundary. | schema semantics | 7% | A2 false | 30% |
| H6 | Later skill-specific edits reintroduced a previously fixed CC BY-NC string into current active files. | recent regression | 5% | A1, A2 | 49% |
| H? | The true cause is not yet listed or cannot currently be named. | unknown | 35% | none | 100% |

The distribution sums to 100%. H1 is the highest-pain named hypothesis because it implicates the repository's own metadata process and requires a class-wide search rather than a one-line correction. It will be tested first, while the unlisted-cause bucket retains the plurality prior.

## Evidence

### E1: The repository license explicitly governs all repository content

- `docs/license.md`, introduced at `930fb40e` on 2025-11-01, says: "All content in this repository is governed by the following license agreement" and names CC BY-NC-SA 4.0.
- README lines 217-239 have named CC BY-NC-SA, linked its official deed, and explained ShareAlike since November 2025.
- `mkdocs.yml` publishes the same license in the site footer.
- No tracked current document declares a per-skill exception or a repository relicensing to CC BY-NC.
- **Implication:** A1, A5, and A6 are confirmed. H2 and H3 are refuted. Confidence: high.

### E2: CC BY-NC and CC BY-NC-SA impose different adaptation terms

- Creative Commons' official CC BY-NC 4.0 deed lists Attribution and NonCommercial terms, without ShareAlike: https://creativecommons.org/licenses/by-nc/4.0/
- Its official CC BY-NC-SA 4.0 deed additionally requires adaptations to use the same license: https://creativecommons.org/licenses/by-nc-sa/4.0/
- **Implication:** The frontmatter difference is material, not a harmless long-name abbreviation. Confidence: high.

### E3: The June metadata refactor introduced five active mismatches in one commit

- Commit `14d806631acbab50188b382e51224bae8bc1bfcc` added the exact CC BY-NC value to `book-installer`, `chapter-content-generator`, and `course-description-analyzer` where no license field existed.
- The same commit replaced `MIT` with CC BY-NC in `faq-generator` and `quiz-generator`.
- Its stated purpose was description refactoring; it carried no license-policy rationale or contract test.
- **Implication:** A3 is confirmed. H1 is strongly supported, but the evidence also shows the operation changed legal metadata outside the commit's stated scope. Confidence: high.

### E4: Two July meta-skill introductions repeated the same value

- `book-publisher` was introduced with CC BY-NC at `ac26066d` on 2026-07-10.
- `book-media-generator` was introduced with CC BY-NC at `d133ef8b` four minutes later.
- Both meta-skills consolidate repository content whose guides repeatedly describe the project default as CC BY-NC-SA.
- **Implication:** The defect is a reusable metadata-authoring pattern, not only one June diff. H1's causal class expands from a single refactor to repeated hard-coded frontmatter without a repository-wide invariant. Confidence: high.

### E5: The known FAQ correction is isolated on an unmerged stale branch

- Commit `070447e5` changes FAQ frontmatter to the exact repository license and adds a focused documentation contract.
- It is the sole commit on `origin/fix/faq-generator-contracts`, exposed as PR #25.
- PR #25 is open and currently not mergeable because its base is `2a66630c`, eleven mainline commits behind current `origin/main`.
- Current `origin/main` therefore still contains the FAQ mismatch.
- **Implication:** A later fix did not regress; it never reached main. H6 is refuted. The class remediation must coexist with or supersede the FAQ license hunk without claiming PR #25 is merged. Confidence: high.

### E6: The same omission exists in archived skill copies

- Six archived `SKILL.md` files carry the exact CC BY-NC value: `causal-loop-diagram-generator`, `init-textbook`, `linkedin-announcement-generator`, `linkedin-carousel-generator`, `readme-generator`, and `text-to-speech`.
- Archived `marp-generator` carries a hybrid long name that omits "ShareAlike" while its abbreviation says `CC BY-NC-SA 4.0`.
- Most were introduced by the same June metadata refactor or the July consolidation window.
- **Implication:** A source-only fix to six active files would leave contradictory discoverable metadata in tracked repository content. Confidence: high.

### E7: Distribution uses source symlinks, not independent package copies

- `scripts/bk-install-skills`, `scripts/bk-install-skills-codex`, and `scripts/bk-install-skills-antigravity` install live skill directories as symbolic links.
- No marketplace manifest, plugin package, ZIP, tarball, or copied skill bundle exists in the current repository.
- This host has no installed copies of the seven affected active skills under `~/.codex/skills` or `~/.claude/skills`.
- **Implication:** A7 is refuted for this host. There is no separate package artifact to migrate; source correctness is inherited by future symlink installations. Confidence: high.

### E8: The repository teaches `license` as meaningful skill metadata

- Repository learning material describes YAML frontmatter `license` as the skill's license metadata, even though Anthropic's official authoring requirements only require `name` and `description`: https://docs.claude.com/es/docs/agents-and-tools/agent-skills/best-practices
- No Python consumer in this repository currently parses a skill `license:` field, but human readers and external skill indexes can.
- **Implication:** H5 is refuted as an intent claim: the field is optional to Claude, but it is not an arbitrary category inside this project. A2 is confirmed as a publication/registry risk rather than a runtime-loading requirement. Confidence: medium-high.

### E9: External licensing guidance treats clarity and file-level metadata as substantive

- Creative Commons says a license notice should clearly communicate which license applies, link to the relevant deed, and make the covered material clear to future users: https://creativecommons.org/cc-license-your-work/
- The REUSE Specification defines a standardized method for comprehensive, unambiguous, human- and machine-readable licensing information for each file, and recommends keeping that information with the file so it survives copying: https://reuse.software/spec/
- Neither source makes this repository REUSE-compliant by itself, but both reject the premise that contradictory repository-level and file-level license notices are harmless presentation differences.
- **Implication:** file-local frontmatter is exactly where downstream ambiguity persists after a skill is copied or indexed. A2 is strengthened, and a class-wide executable invariant is justified. Confidence: high.

## Assumption Updates

| Assumption | Result | Updated P | Consequence |
| --- | --- | ---: | --- |
| A1 | Confirmed by explicit "All content" wording and unchanged history. | 99% | Per-skill CC BY-NC conflicts with repository authority. |
| A2 | Confirmed as published metadata; not required by Anthropic runtime. | 90% | Runtime behavior is unaffected, but distribution metadata is not. |
| A3 | Confirmed by commit `14d80663`. | 100% | H1 survives and strengthens. |
| A4 | Partly refuted: the relevant active values were added in this repository's history. | 15% | H4 is downgraded. |
| A5 | Confirmed; no exception language found. | 99% | H2 collapses. |
| A6 | Confirmed; root authority predates every mismatch and remains current. | 100% | H3 collapses. |
| A7 | Refuted on this host and in repository packaging. | 5% | No copied package migration is required. |

## Hypothesis Updates After Evidence Collection

| Hypothesis | Updated P | State | Reason |
| --- | ---: | --- | --- |
| H1 | 5% | Proximate contributor | Direct diffs prove the June refactor introduced five mismatches, but two later introductions show that one refactor is not the systemic cause. |
| H2 | 0% | Refuted | Repository authority explicitly covers all content and no exception exists. |
| H3 | 0% | Refuted | Root CC BY-NC-SA authority predates and outlives every mismatch. |
| H4 | 1% | Severely downgraded | Git history places the values in repository-authored commits. |
| H5 | 1% | Severely downgraded | Optional runtime metadata is still presented as licensing metadata. |
| H6 | 0% | Refuted | The FAQ correction is unmerged, not regressed. |
| H7 | 90% | **Leading root cause** | The repository had no executable global invariant connecting root license authority to file-level frontmatter, so unrelated refactors and new-skill templates repeatedly hard-coded a plausible but materially different CC BY-NC value. |
| H? | 3% | Reserved | A read-only executable inventory will still test whether an unrecognized mismatch class exists. |

## Phase 4 Revised Assumptions

| # | Assumption | Initial P | Revised P | Evidence |
| --- | --- | ---: | ---: | --- |
| A1 | Repository-wide CC BY-NC-SA applies to active `SKILL.md` content. | 70% | **99%** | E1: explicit all-content wording, unchanged history, and no exception. |
| A2 | Consumers can treat `license:` frontmatter as licensing metadata. | 70% | **95%** | E8 and E9: project teaching plus CC/REUSE clarity guidance. |
| A3 | June metadata refactoring changed affected license lines. | 45% | **100%** | E3: exact introducing commit and diffs. |
| A4 | Affected values came from independent imported source licensing. | 50% | **5%** | E3 and E4 place the values in repository-authored changes. |
| A5 | No current per-skill licensing exception exists. | 80% | **99%** | E1: repository-wide search and history. |
| A6 | No intentional repository relicense to CC BY-NC occurred. | 80% | **100%** | E1: root authority predates and outlives the mismatches. |
| A7 | Separate installed or packaged copies require migration. | 70% | **5%** | E7: source symlinks, no package artifacts, no affected local installs. |
| A8 | No executable repository-wide test currently rejects a contradictory Creative Commons skill license. | N/A | **100%** | Test/workflow inventory found only isolated FAQ coverage on an unmerged branch. |

## Phase 4 Revised Hypotheses

| # | Hypothesis | Initial P | Revised P | P ceiling | Key evidence |
| --- | --- | ---: | ---: | ---: | --- |
| H1 | One June metadata refactor accidentally dropped ShareAlike. | 25% | **5%** | 99% | E3 confirms the proximate event; E4 disproves sufficiency. |
| H2 | Active skills are intentionally dual-licensed. | 8% | **0%** | 1% | E1 refutes an exception. |
| H3 | Root licensing documentation is stale. | 12% | **0%** | 0% | E1 refutes repository relicensing. |
| H4 | Imported skills retained separate source-project licenses. | 8% | **1%** | 5% | E3 and E4 trace repository-authored values. |
| H5 | `license:` is a harmless tooling category. | 7% | **1%** | 5% | E8 and E9 establish published metadata consequences. |
| H6 | A later edit regressed a previously merged fix. | 5% | **0%** | 0% | E5 proves the known correction never merged. |
| H7 | **New: absent global license invariant allowed unrelated changes to repeatedly publish a materially different file-level contract.** | N/A | **90%** | 94% | E1, E3, E4, E6, E8, E9. |
| H? | Unknown cause or inventory class. | 35% | **3%** | 100% | Reserved for executable inventory results. |

H7 exceeds the methodology's 80% passive-evidence gate. No state-changing experiment is necessary to select the leading cause; Phase 5 will use a reversible read-only characterization probe to test the remaining inventory uncertainty before final blame assignment.

## Phase 5 Experimentation

Three-strike count for the repository-metadata-invariant category: **0** prior experiments. No category pivot is required.

### X1: Read-only global Creative Commons frontmatter characterization

- **Tests:** H7 (absence of a global invariant allowed a repeated metadata class) and H? (an unrecognized mismatch class exists).
- **Predicted outcome if H7 is true:** a repository-wide frontmatter parser will find the same noncanonical Creative Commons contract across multiple unrelated current and archived skills, while finding no executable global test that rejects it.
- **Predicted outcome if H7 is false:** the parser will reduce the symptom to one isolated file, identify intentional distinct per-skill license families, or reveal an existing global invariant that the affected files bypass through a narrower mechanism.
- **Procedure:** run an ephemeral Python program from the isolated worktree. It reads only the top YAML frontmatter block of every tracked `skills/**/SKILL.md`, groups nonempty `license` values, reports every Creative Commons value that differs from the repository's exact CC BY-NC-SA authority, and exits nonzero when mismatches exist. Then inventory tracked tests and workflows for an existing global license contract. The program creates no files and mutates no repository state.
- **Actual outcome:** The first one-level traversal correctly found the seven active mismatches but omitted nested `skills/archived/**` files. The corrected recursive traversal found **14** noncanonical Creative Commons values: 13 exact CC BY-NC declarations and one malformed hybrid whose long name omits ShareAlike while its abbreviation says `CC BY-NC-SA`. The affected set spans seven current and seven archived skills. The test/workflow inventory returned no global license-frontmatter contract.
- **Conclusion:** H7 is confirmed and rises to **97%**. The recursive probe confirms a repeated repository-maintained metadata class and proves that a substring-only guard would miss the malformed hybrid. H? falls to **1%**; the only new class was a formatting variant of the same contradiction, not a separate cause.

### E10: Post-experiment standards search supports exact, portable file-level identifiers

- SPDX recommends precise, portable, machine-readable per-file license identifiers because top-level license files can be separated from copied files and ambiguous names create compliance risk: https://spdx.dev/learn/handling-license-info/
- REUSE similarly states that licensing information should remain with each file when it is copied downstream: https://reuse.software/spec/
- **Implication:** the remediation should enforce one exact canonical value for repository-authored Creative Commons frontmatter. A check for a convenient substring or abbreviation would preserve the malformed MARP case. Confidence: high.

## Phase 6 Final Hypothesis Revision

| # | Hypothesis | Initial P | Post-evidence P | Post-experiment P | Key experiment |
| --- | --- | ---: | ---: | ---: | --- |
| H1 | One June metadata refactor accidentally dropped ShareAlike. | 25% | 5% | **1%** | X1 shows the class spans later introductions and archived variants. |
| H2 | Active skills are intentionally dual-licensed. | 8% | 0% | **0%** | X1 finds one repeated noncanonical family, not documented exceptions. |
| H3 | Root licensing documentation is stale. | 12% | 0% | **0%** | X1 changes no authority evidence; E1 remains conclusive. |
| H4 | Imported skills retained separate source-project licenses. | 8% | 1% | **0.5%** | X1 groups repository-authored current and archived surfaces together. |
| H5 | `license:` is a harmless tooling category. | 7% | 1% | **0.5%** | X1 demonstrates portable file-local publication and E10 explains downstream use. |
| H6 | A later edit regressed a previously merged fix. | 5% | 0% | **0%** | E5 remains conclusive. |
| H7 | **Absent global license invariant allowed unrelated changes to repeatedly publish a materially different file-level contract.** | N/A | 90% | **97%** | X1 finds 14 class members and no global rejecting test/workflow. |
| H? | Unknown cause or inventory class. | 35% | 3% | **1%** | X1's only new variant is the same root class with a malformed long-name/abbreviation pair. |

The distribution sums to 100%. H7 exceeds the 90% decision gate, so blame assignment can proceed without additional experiments.

## Phase 7 Blame Assignment

### Level 1: Faulting declarations and missing enforcement boundary

| File:line | Current declaration or boundary | Why it is wrong | Severity |
| --- | --- | --- | --- |
| `skills/book-installer/SKILL.md:5` | `CC BY-NC 4.0` | Contradicts the repository's all-content CC BY-NC-SA authority. | Medium |
| `skills/book-media-generator/SKILL.md:5` | `CC BY-NC 4.0` | Same contradiction in a current meta-skill. | Medium |
| `skills/book-publisher/SKILL.md:5` | `CC BY-NC 4.0` | Same contradiction in a current meta-skill. | Medium |
| `skills/chapter-content-generator/SKILL.md:5` | `CC BY-NC 4.0` | Same contradiction in a current generator. | Medium |
| `skills/course-description-analyzer/SKILL.md:5` | `CC BY-NC 4.0` | Same contradiction in a current analyzer. | Medium |
| `skills/faq-generator/SKILL.md:4` | `CC BY-NC 4.0` | Same contradiction in a current generator; a known correction remains unmerged. | Medium |
| `skills/quiz-generator/SKILL.md:4` | `CC BY-NC 4.0` | Same contradiction in a current generator. | Medium |
| `skills/archived/{causal-loop-diagram-generator,init-textbook,linkedin-announcement-generator,linkedin-carousel-generator,readme-generator,text-to-speech}/SKILL.md:4-5` | `CC BY-NC 4.0` | Archived but still tracked and copyable skill metadata publishes the same different contract. | Low |
| `skills/archived/marp-generator/SKILL.md:5` | Long name says BY-NC while abbreviation says `BY-NC-SA` | Internally contradictory metadata defeats substring-based verification and human interpretation. | Low |
| `.github/workflows/` and repository test surface | No global license-frontmatter contract exists. | Nothing rejects a future mismatch when any skill frontmatter changes. | High |

### Level 2: Anti-patterns

1. **AP8, Configuration Without Constraints:** `license:` is duplicated across skill files as free-form configuration with no canonical source, exact-value constraint, or repository-level validation. The value couples to `docs/license.md`, README, and the published site but that dependency is not executable.
2. **AP6, Silent Failure Escalation:** contradictory legal metadata passes every existing check and CI remains green. The defect is visible only to a reader comparing distant surfaces or to an external index that copies frontmatter.
3. **Copy-pasted authority:** a long legal label is manually repeated instead of derived from or checked against one canonical contract. The malformed MARP value demonstrates why partial string matching is insufficient.

### Level 3: Development practice

- Metadata refactors were reviewed and named as description changes while also changing licensing fields, so the effective contract change was outside the declared scope.
- Contract tests are organized around individual skills and workflows. There is no invariant test for rules that apply to every current and archived skill.
- New meta-skills copied an existing plausible-looking license value without a creation-time validator that reconciles it with repository authority.
- The repository does not require exact, portable license metadata before publication, despite treating skill frontmatter as a reusable distribution surface.

The remediation therefore needs all three scopes: replace every contradictory declaration, add one recursive exact-value contract, and run that contract automatically whenever root authority or any skill frontmatter can change.

## Phase 8 Immediate Fix

### Implemented changes

- Replaced all 13 exact CC BY-NC declarations with the canonical CC BY-NC-SA value.
- Replaced the archived MARP hybrid declaration with the same exact canonical value.
- Added `scripts/validate_skill_license_contract.py`, which recursively reads top-level `license:` frontmatter from every `skills/**/SKILL.md` and rejects any noncanonical Creative Commons value.
- Added `tests/test_skill_license_contract.py` with repository, authority, plain-BY-NC, malformed-hybrid, and canonical-value cases.
- Added `.github/workflows/skill-license-contract.yml`, triggered by root authority, skill frontmatter, validator, test, or workflow changes.

### Failure-path proof

The new five-test suite was copied unchanged into a temporary archive of baseline `origin/main` at `e2dd7a0f`. It failed exactly one repository contract test and reported 14 noncanonical declarations. The same suite passes on this branch. This proves the regression detects the original symptom rather than merely passing its own fixtures.

### Verification

- `python3 scripts/validate_skill_license_contract.py`: pass.
- `python3 -m unittest tests/test_skill_license_contract.py -v`: 6/6 pass after the Phase 9 lowercase-path regression was added.
- Every existing tracked Python test file under `skills/**/tests/test_*.py`: 129/129 pass.
- `git diff --check`: pass.

The immediate symptom is resolved in source: the recursive validator reports zero contradictory Creative Commons skill licenses.

## Phase 9 Anti-Pattern Audit

### Graph-first search

The refreshed codebase-memory graph identified the new repository contract test as the sole root-level skill-license validator and showed that existing YAML-frontmatter readers are scoped to book or MicroSim metadata. Tracing `check_yaml_frontmatter` reaches only the book-status entry point; no preexisting caller enforced repository skill licensing. This confirms the enforcement gap structurally rather than from filename search alone.

### Textual fallback for Markdown metadata

Markdown frontmatter is not represented as callable graph structure, so a repository-wide textual fallback searched non-ShareAlike Creative Commons declarations and all case variants of `skill.md`.

| Finding | Classification | Disposition |
| --- | --- | --- |
| `skills/archived/concept-classifier/skill.md` used lowercase filename and CC BY-NC frontmatter. | Medium; same AP8/AP6 class and missed by uppercase-only traversal. | Fixed; validator made case-insensitive and regression added. |
| `docs/chapters/16-user-global-claude/index.md` instructed users to choose CC BY-NC as the default textbook license. | Medium; stale duplicated authority could regenerate the defect in new projects. | Fixed; added to authority contract and workflow trigger. |
| Current and archived badge reference catalogs enumerate CC BY-NC among multiple valid badge choices while explicitly naming CC BY-NC-SA as project default. | Informational; intentional catalog, not a repository license claim. | Preserved. |
| Chapter-image guides discuss CC BY-NC compatibility for third-party media. | Informational; external asset licensing, not repository authority. | Preserved. |
| Test and investigation fixtures contain bad values to prove rejection and preserve evidence. | Informational; non-authoritative evidence. | Preserved. |

### Unified audit result

- **High:** no remaining unguarded current-skill declaration class after remediation.
- **Medium:** two additional same-class surfaces found and remediated: lowercase archived skill metadata and stale default-license teaching prose.
- **Low/informational:** intentional license catalogs, external-media policy, and negative test fixtures remain by design.

The permanent invariant now traverses `skill.md` case-insensitively and checks all known repository-authority teaching surfaces. A post-fix negative search is required in Phase 10 before closure.

Post-audit verification is green: 6/6 focused contract tests, 129/129 existing Python tests, the standalone validator, Python compilation, and `git diff --check`. The broad negative search now returns only the two intentional third-party media-license references classified above.

## Phase 10 Comprehensive Remediation Plan

### Phase 1: Stop the bleeding - immediate, under one day

**Status: implemented and locally verified.**

1. Normalize all 15 contradictory Creative Commons skill declarations: seven current skills, seven uppercase archived skills, and one lowercase archived skill.
2. Correct the stale user-global default-license instruction so newly created textbooks are not guided back to CC BY-NC.
3. Preserve intentional alternative-license examples for badge selection and third-party media compatibility.

### Phase 2: Structural hardening - this week

**Status: implemented and locally verified; merge/CI evidence pending.**

1. Enforce one exact canonical Creative Commons skill frontmatter value recursively and case-insensitively.
2. Test both known failure forms, lowercase legacy filenames, current repository content, root authority, and the default-license teaching surface.
3. Run the contract in GitHub Actions whenever any skill definition, root authority, default-license instruction, validator, test, or workflow changes.
4. Keep the validator dependency-free so it runs in a clean checkout without repository-specific package installation.
5. Reconcile the overlapping FAQ license hunk in stale PR #25 without claiming or discarding its unrelated FAQ anchor/README work.

### Phase 3: Architectural follow-through - next sprint only if evidence warrants it

**Status: no redesign currently required.**

1. If future non-Creative-Commons exceptions are introduced, require an explicit documented per-file exception and extend the validator around that declared policy rather than silently accepting arbitrary strings.
2. Consider standardized SPDX identifiers only as a separately reviewed repository-wide migration. Do not mix that format migration into this correctness fix.
3. Consider broader REUSE adoption only with a complete copyright and third-party-content inventory; the current fix should not imply REUSE compliance.

### Accepted debt

- Blank license fields and the archived MIT declaration are not changed by this incident because no evidence established whether they are omissions, historical exceptions, or obsolete metadata. They require separate authority decisions if promoted to current use.
- Badge catalogs intentionally enumerate multiple licenses and remain valid because they label CC BY-NC-SA as the project default.
- Third-party media guides intentionally discuss licenses that differ from the repository's own license.
- Historical prompts and investigation evidence may quote superseded values when clearly presented as history or negative fixtures.

### What not to do

- Do not treat `CC BY-NC-SA` as a sufficient substring; the malformed MARP declaration proved that the long name can still contradict the abbreviation.
- Do not rewrite every mention of CC BY-NC: external asset policy and license catalogs have different authority.
- Do not auto-normalize MIT, Apache, blank, or third-party licenses without provenance and copyright evidence.
- Do not close the investigation on local test success. Merge, CI, source-of-truth, and distribution-boundary verification remain required.

### Closure criteria

- [x] Root cause exceeds 90% and three-level blame is documented.
- [x] All known current, archived, lowercase, and teaching-surface contradictions are reconciled.
- [x] Regression fails on baseline and passes on the fix.
- [x] Focused and existing Python suites pass locally.
- [ ] Pull request is open, reviewed, merged, and relevant CI is green.
- [ ] Current `origin/main` passes the standalone validator and focused contract.
- [ ] Installation/package boundary is rechecked after merge; expected result is no copied package artifacts and source-symlink inheritance.
- [ ] CE Compound records the durable lesson before the Trello card enters Done.
