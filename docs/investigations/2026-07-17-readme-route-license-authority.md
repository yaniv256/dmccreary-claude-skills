# README Route License Authority Investigation

## Status

CURRENT

## Symptom

The active `book-publisher` README guide instructs an agent to publish a
Creative Commons BY-NC-SA 4.0 badge when it cannot find repository license
evidence:

> Default to Creative Commons BY-NC-SA 4.0 if not specified.

That instruction converts missing evidence into an affirmative legal grant.
The same route later requires a License section, so a generated README can
state licensing terms that the repository owner never selected.

## Impact

An agent following the active guide can misrepresent an unlicensed repository
as licensed, obscure conflicting or split code/content licenses, and produce a
README whose badge and prose disagree with the repository's actual legal
files. The defect affects every user of the active README route and can grant
apparent permissions that do not exist.

Severity is **high** because the generated publication artifact makes a legal
claim. GitHub's licensing guidance states that default copyright applies when
a repository has no license and no permission to reproduce, distribute, or
create derivative works is granted.

## Phase 0: Tools

The investigation uses a clean worktree based on `origin/main`, Git history,
the full codebase-memory index for the worktree, repository tests and release
validators, primary GitHub licensing documentation, and installed-skill parity
checks. The index includes active and archived scripts, the target source is
readable, the worktree is clean, and the existing focused test module loads.

## Established Timeline

| Time / marker | Event | Confidence | Source | Timezone |
| --- | --- | --- | --- | --- |
| 2025-11-11 13:11:06 CST, commit `6403c8e6` | The standalone README skill introduced the no-evidence CC BY-NC-SA 4.0 default. | High | `git blame` and `git log --follow` | Commit offset `-06:00` |
| 2026-07-10 05:52:45 CDT, commit `ac26066d` | The standalone README route was promoted into active `book-publisher` guidance without changing the license default. | High | `git log --follow` and current path history | Commit offset `-05:00` |
| 2026-07-17, source commit `e2dd7a0f` | The invented-license default remains in current `origin/main`. | High | Fresh worktree source read | Date only; no time claim |

## Preserved Source Evidence

| Location | Observed behavior |
| --- | --- |
| `skills/book-publisher/references/readme-guide.md:77-88` | The active route checks three weakly defined sources and defaults to a specific Creative Commons license when none is found. |
| `skills/book-publisher/references/readme-guide.md` | The guide later requires a License section but defines no fail-closed behavior for absent, conflicting, split, or nonstandard evidence. |
| `skills/book-publisher/scripts/validate-readme.py` | Required-section validation accepts the word `license` anywhere in the README and does not compare claims with repository evidence. |
| `skills/book-publisher/tests/test_validate_readme.py` | Existing tests cover Markdown fence parsing only; no licensing contract is executable. |

## Primary External Evidence

- [GitHub's repository licensing guide](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)
  says that without a license default copyright applies and the repository
  grants no general permission to reproduce, distribute, or create derivative
  works.
- The same guide says license detection can fail when a repository has
  multiple licenses or other complexity and recommends documenting that
  complexity rather than simplifying it into a false single-license claim.
- [GitHub's licenses API documentation](https://docs.github.com/en/rest/licenses/licenses)
  states that GitHub's detector compares the repository license file with
  known licenses and does not infer licensing from arbitrary documentation.

## Hypotheses

### Generative-prior calibration

Repository investigations contain only two `CONFIRMED` and two `REFUTED`
labels. That 50% apparent ratio is four sparse mentions rather than a
measured one-row-per-hypothesis track record, so it is not a defensible
first-pass hit rate. This investigation uses the methodology's conservative
20% prior: most hypotheses listed next will be wrong, and the true cause is
probably absent from the initial list.

No source-reading narrative becomes root cause without an executable
experiment. The Phase 2 table will reserve plurality probability for "the
true cause is not yet listed," and the experiment matrix will exercise real
repository states so it can reveal a mechanism that the initial list failed
to name.

### Assumptions

| # | Type | Assumption | Initial P | Inverse | Verification |
| --- | --- | --- | ---: | ---: | --- |
| A1 | route | The active guide is an operative agent contract. | 95% | 5% | Trace routing from `book-publisher/SKILL.md`. |
| A2 | architecture | No wrapper supplies a verified license decision before the guide runs. | 75% | 25% | Trace active callers and commands. |
| A3 | authority | Repository-wide policy does not authorize this route to license arbitrary target repositories. | 85% | 15% | Inspect repository license and route scope. |
| A4 | validation | README validation does not compare license claims with target-repository evidence. | 85% | 15% | Trace validator data flow and run fixtures. |
| A5 | semantics | `docs/license.md` can describe content scope rather than the whole repository. | 70% | 30% | Check documented conventions and repository examples. |
| A6 | complexity | A target repository can contain multiple applicable license files. | 95% | 5% | Check GitHub/SPDX documentation and fixtures. |
| A7 | behavior | An agent following the guide will publish its fallback badge and section. | 85% | 15% | Run the route instructions in a fixture repository. |
| A8 | prevention | No executable test currently covers license authority for the active route. | 80% | 20% | Search test graph and release commands. |

All assumptions are primitive binary claims and each inversion sums to 100%.
A2 and A4 are the initial bottlenecks because they determine whether another
boundary already prevents the guide's unsafe instruction from reaching a
publication artifact.

### Initial hypothesis table

| # | Hypothesis | Category | Initial P | Assumptions | Ceiling |
| --- | --- | --- | ---: | --- | ---: |
| H1 | A textbook-specific Creative Commons convention was promoted into a generic active README route without preserving the distinction between a project convention and target-repository authority. | migration | 18% | A1, A3, A7 | 69% |
| H2 | The validator certifies a README from prose mentions alone, so it creates false confidence without checking the repository evidence that authorizes the legal claim. | quality system | 10% | A4, A8 | 68% |
| H3 | The guide treats copyright metadata as license evidence and therefore collapses identity/attribution into permission. | data semantics | 7% | A5, A7 | 60% |
| H4 | Active and archived templates perpetuate the same default, so later promotion and packaging preserve it mechanically. | duplication | 8% | A1, A8 | 76% |
| H5 | The route has no typed license state such as absent, single, ambiguous, split, or explicitly authorized; prose generation therefore cannot fail closed. | architecture | 10% | A2, A4, A6 | 61% |
| H6 | The route silently selects or invents one license when source files conflict because its discovery order is treated as precedence. | evidence handling | 7% | A5, A6, A7 | 57% |
| H7 | The true cause is not yet listed. | unknown | 40% | none | 100% |

The probabilities sum to 100%. The maximum-pain candidates are H1 and H2:
they implicate the recent promotion decision and the repository's own
validation surface rather than a user's repository layout. H1 will be tested
first, while the fixture matrix will deliberately attempt to convert H7 into
a named mechanism.

## Evidence and Experiments

### Phase 3: Non-destructive evidence collection

#### Revised assumptions

| # | Assumption | Initial P | Revised P | Evidence |
| --- | --- | ---: | ---: | --- |
| A1 | The active guide is an operative agent contract. | 95% | **99%** | `book-publisher/SKILL.md` routes every README request directly to `references/readme-guide.md`. |
| A2 | No wrapper supplies a verified license decision first. | 75% | **99%** | The code graph and route text expose no caller, command, or typed discovery step before the guide writes README content. |
| A3 | Repository policy does not authorize arbitrary targets. | 85% | **99%** | The guide explicitly targets any repository; this repository's own content terms cannot license a caller's separate repository. |
| A4 | Validation ignores target-repository license evidence. | 85% | **99%** | `validate_readme()` receives only one README path; required-section logic searches lowercase prose for the substring `license`. |
| A5 | `docs/license.md` can have narrower scope than the repository. | 70% | **99%** | The current repository has `docs/license.md` describing “content” but no root `LICENSE*`; MkDocs defines `copyright` as theme display information, not a license grant. |
| A6 | A target can contain multiple applicable licenses. | 95% | **99%** | GitHub documents multiple-license complexity; SPDX defines `AND`, `OR`, `WITH`, and `LicenseRef` rather than collapsing it. |
| A7 | An agent following the guide publishes the fallback claim. | 85% | **85%** | Source makes the instruction explicit, but executable fixture proof remains Phase 5 work. |
| A8 | No test covers license authority. | 80% | **99%** | The only active validator tests cover Markdown fence parsing; no fixture passes repository evidence. |

#### E1: Active guidance is a near-verbatim archived promotion

- `git log --follow` identifies the standalone README route before the
  `book-publisher` promotion.
- A direct diff shows that the active guide differs mainly in frontmatter,
  title, wording from “skill” to “guide,” and an updated script path. The
  license fallback and full CC BY-NC-SA example survived unchanged.
- Confidence: high. Supports H1 and H4; confirms A1.

#### E2: No authority boundary precedes README generation

- `book-publisher/SKILL.md` routes the user request straight to the guide.
- The guide discovers strings from `LICENSE`, `docs/license.md`, and the
  MkDocs `copyright` field, but defines no typed result, scope, conflict state,
  or authorized human selection.
- No wrapper, CLI, or function accepts a verified license decision.
- Confidence: high. Supports H1 and H5; confirms A2-A3.

#### E3: Two independent instructions invent the same legal claim

- Step 3 publishes a CC BY-NC-SA 4.0 badge when no evidence is found.
- Step 10 unconditionally emits a full CC BY-NC-SA 4.0 License section and
  links `docs/license.md`, even when that file is absent or says something
  else.
- Step 15 requires License as a fixed section rather than deriving its
  presence from an evidence state.
- Confidence: high. Supports H1, H3, and H5.

#### E4: Validation certifies prose, not authority

- `validate_readme()` reads only the README file. It has no repository-root,
  license-file, metadata, or authorized-selection input.
- `check_required_sections()` marks License present when `license` appears
  anywhere in lowercase content, including prose, badges, acknowledgements,
  or unrelated dependency text.
- The code graph shows no licensing checker in the validator call tree.
- Confidence: high. Supports H2 and confirms A4 and A8.

#### E5: The repository itself demonstrates scope ambiguity

- This repository contains `docs/license.md`, whose prose governs “content,”
  but does not contain a root `LICENSE`, `LICENSE.md`, `COPYING`, or `NOTICE`.
- The active skill frontmatter identifies CC BY-NC 4.0 while the docs page
  identifies CC BY-NC-SA 4.0. Those are different terms and scopes.
- The guide's ordered list provides no rule for reconciling this conflict and
  would select a claim without establishing what files it covers.
- Confidence: high. Supports H3, H5, and H6; confirms A5-A6.

#### E6: The unsafe contract remains duplicated

- `skills/archived/readme-generator/SKILL.md` preserves the same default and
  unconditional License section.
- `docs/prompts/readme-generator-skill.md` also says the default is always CC
  BY-NC-SA 4.0.
- A fix limited to the active sentence would leave sources that can reintroduce
  the defect during a later promotion or regeneration.
- Confidence: high. Supports H4.

#### E7: Primary documentation requires fail-closed evidence handling

- GitHub states that default copyright applies when no license exists and
  documents detection failures for multiple-license complexity.
- GitHub's API documentation says Licensee identifies known repository license
  files and does not infer a project license from arbitrary documentation.
- MkDocs defines `copyright` as display information included by the theme.
- SPDX provides explicit compound expressions and custom `LicenseRef` values
  for states that cannot be represented by one common badge.
- Confidence: high. Confirms A3, A5, and A6.

### Phase 4: Revised hypotheses after evidence

| # | Hypothesis | Initial P | Revised P | Ceiling | Key evidence |
| --- | --- | ---: | ---: | ---: | --- |
| H1 | Textbook convention was promoted into a generic route without an authority boundary. | 18% | **5%** | 83% | Subsumed by H8 after E1-E4 connected promotion and prevention failure. |
| H2 | Prose-only validation creates false confidence. | 10% | **5%** | 98% | E4 confirms the mechanism, but it is one part of the full chain. |
| H3 | Copyright metadata is collapsed into permission. | 7% | **2%** | 84% | E5 and E7 confirm the semantic error, subsumed by H8. |
| H4 | Duplicated sources perpetuate the default. | 8% | **4%** | 98% | E1 and E6 confirm duplication, subsumed by H8. |
| H5 | The route has no typed license state and cannot fail closed. | 10% | **6%** | 96% | E2-E5 confirm the missing model, subsumed by H8. |
| H6 | Discovery order is mistaken for legal precedence. | 7% | **3%** | 83% | E3 and E5 show silent selection without scope/conflict rules. |
| H7 | The true cause is not yet listed. | 40% | **5%** | 100% | Retained until the fixture matrix directly executes the contract. |
| H8 | **The active incident is a promoted prose-only generator contract that has no license-authority state model, while a presentation-only validator and duplicated historical sources allow invented or ambiguous legal claims to be published as valid README content.** | N/A | **70%** | 78% | E1-E7 connect entry, mechanism, escape, and recurrence paths. |

The probabilities sum to 100%. H8 is between 50% and 80%, so Phase 5 must
exercise the current route and validator against real repository-state
fixtures before blame assignment. Primary GitHub, SPDX, REUSE, MkDocs, and
Creative Commons documentation all support the required distinction between
copyright display text, license evidence, authority to grant permissions, and
compound or file-scoped licensing.

### Phase 5: Experiments

No earlier experiment targets this architecture/quality-system category, so
the three-strike pivot is not active.

#### X1: No-license repository with invented CC README

- **Tests:** H8, including the entry and validator escape paths.
- **Predicted if H8 is true:** Following the guide in a repository with no
  license evidence yields the CC BY-NC-SA badge and section, and the validator
  reports no license-authority error.
- **Predicted if H8 is false:** The route declines to make a claim, asks for an
  authorized selection, or validation rejects the unsupported claim.
- **Procedure:** Create an isolated temporary repository containing no license
  file, write the guide's exact CC badge and section into its README, and run
  the unmodified active validator.
- **Actual outcome:** The unmodified validator reported all four required
  sections present, returned 80/100 with status `GOOD`, and emitted no
  license-authority error. The fixture contained no license file.
- **Conclusion:** Supports H8. The active quality gate treats an unsupported
  affirmative license grant as valid presentation content.

#### X2: Conflicting-license repository with one invented claim

- **Tests:** H5, H6, and the ambiguity branch of H8.
- **Predicted if H8 is true:** Adding distinct MIT and Apache license files does
  not change validator behavior; a README that claims only CC BY-NC-SA still
  passes the license section check.
- **Predicted if H8 is false:** Discovery reports ambiguity or validation
  rejects a single unsupported badge/section.
- **Procedure:** Create a separate fixture with `LICENSE-MIT` and
  `LICENSE-APACHE`, then validate the same README.
- **Actual outcome:** The unmodified validator produced the same 80/100
  `GOOD` result as X1. The presence of both `LICENSE-MIT` and
  `LICENSE-APACHE` caused no ambiguity signal and did not affect validation.
- **Conclusion:** Supports H5, H6, and H8. Repository evidence is outside the
  validator's data model, so contradictory source evidence cannot fail the
  generated single-license claim.

#### X3: Nonstandard license text

- **Tests:** H5 and the unknown-cause slot H7.
- **Predicted if H8 is true:** The route has no honest representation such as
  `LicenseRef`; validation ignores the nonstandard source and accepts the
  unrelated common-license claim.
- **Predicted if H8 is false:** The route preserves the source text or reports
  it as nonstandard without substituting a common badge.
- **Procedure:** Create a fixture with a custom root `LICENSE` and validate a
  README carrying the guide's CC claim.
- **Actual outcome:** The unmodified validator again returned 80/100 and
  `GOOD`. It ignored the root `LICENSE`, whose custom terms prohibit general
  redistribution, and accepted the unrelated CC BY-NC-SA claim.
- **Conclusion:** Supports H5 and H8 and reduces H7. The defect is not limited
  to GitHub-detectable common licenses; arbitrary source terms are invisible
  to the current route contract and quality gate.

#### X4: Prose mention masquerading as a License section

- **Tests:** H2 and the unknown-cause slot H7.
- **Predicted if H8 is true:** A README with no License heading can satisfy the
  required section merely by mentioning “license” in unrelated prose.
- **Predicted if H8 is false:** The validator requires a structural License
  heading and reports the section missing.
- **Procedure:** Validate a README whose acknowledgements say only that a
  dependency has a license, with no repository license badge or heading.
- **Actual outcome:** The validator credited all four required sections and
  returned 70/100 with status `ADEQUATE`, even though the README had no
  License heading or repository-license statement. The only occurrence was
  “A dependency's license is documented upstream.”
- **Conclusion:** Strongly supports H2 and H8. This was the most diagnostic
  surprise: the required-section check is not structural and can certify an
  unrelated prose mention as a repository License section.

#### Phase 5 result

The experiment matrix reproduced the unsafe entry, missing evidence model,
and validation escape independently. X1-X3 were presentation-identical to the
validator despite materially different legal states, while X4 proved the
validator does not even establish that the claimed required section exists.
H8 therefore explains the observed behavior without relying on an untested
agent interpretation or a repository-specific convention.

The post-experiment web checkpoint found matching primary-source semantics,
not an exceptional platform quirk: GitHub documents default copyright when
license evidence is absent and warns that multiple licenses create detection
complexity; SPDX explicitly models compound expressions, custom
`LicenseRef` values, `NoneLicense`, and `NoAssertionLicense`. The experiment's
four repository states are therefore states the route must preserve rather
than normalize into one Creative Commons claim.

### Phase 6: Final hypothesis revision

| # | Hypothesis | Initial P | Post-evidence P | Post-experiment P | Key experiment |
| --- | --- | ---: | ---: | ---: | --- |
| H1 | Textbook convention was promoted into a generic route without an authority boundary. | 18% | 5% | **0%** | X1 confirms the entry but H8 explains the complete chain. |
| H2 | Prose-only validation creates false confidence. | 10% | 5% | **1%** | X4 confirms it as one escape mechanism within H8. |
| H3 | Copyright metadata is collapsed into permission. | 7% | 2% | **0%** | No additional explanatory power beyond H8. |
| H4 | Duplicated sources perpetuate the default. | 8% | 4% | **1%** | Source search confirms recurrence risk, not the complete incident. |
| H5 | The route has no typed license state and cannot fail closed. | 10% | 6% | **1%** | X1-X3 confirm state blindness as one mechanism within H8. |
| H6 | Discovery order is mistaken for legal precedence. | 7% | 3% | **0%** | X2 confirms ambiguity is ignored, subsumed by H8. |
| H7 | The true cause is not yet listed. | 40% | 5% | **1%** | All four outcomes match H8 without an unexplained residual mechanism. |
| H8 | **A promoted prose-only generator contract has no license-authority state model, while presentation-only validation and duplicated historical sources let invented or ambiguous legal claims publish as valid README content.** | N/A | 70% | **96%** | X1-X3 reproduce evidence blindness; X4 reproduces false structural certification. |

The probabilities sum to 100%. H8 exceeds the 90% gate because it predicts
both invariances demonstrated by the fixture matrix: materially different
repository evidence cannot affect validation, and unrelated prose can satisfy
the supposed License-section requirement.

### Phase 7: Blame assignment

#### Level 1: Responsible lines

| Location | Behavior | Why it is wrong | Severity |
| --- | --- | --- | --- |
| `skills/book-publisher/references/readme-guide.md:79-88` | Treats `LICENSE`, a docs page, and MkDocs copyright display text as interchangeable, then invents CC BY-NC-SA when none is found. | Discovery order is not authority or scope, copyright display text is not permission, and missing evidence means default copyright rather than an affirmative grant. | Critical |
| `skills/book-publisher/references/readme-guide.md:346-364` | Unconditionally emits a complete CC BY-NC-SA license grant. | It can contradict, broaden, or replace the repository owner's actual terms. | Critical |
| `skills/book-publisher/references/readme-guide.md:499-514` | Requires a License section in every generated README. | The route has no representation for absent, ambiguous, split, custom, or unresolved evidence, so the required output pressures the agent to fabricate one. | High |
| `skills/book-publisher/scripts/validate-readme.py:25-61` | Detects required sections by substring search over all prose. | X4 proves an unrelated dependency-license mention is accepted as a repository License section. | High |
| `skills/book-publisher/scripts/validate-readme.py:189-224` | Accepts only a README path and initializes the report as valid. | Repository evidence and explicit authorization cannot affect the verdict, making unsupported legal claims indistinguishable from grounded ones. | High |
| `skills/archived/readme-generator/SKILL.md:81-99,350-357` and `docs/prompts/readme-generator-skill.md:25-31` | Preserve the same invented default in reusable historical sources. | A narrow active-guide fix can be mechanically reverted by later promotion or reuse. | Medium |

#### Level 2: Anti-patterns

1. **Configuration Without Constraints (AP8):** a security- and
   permission-sensitive default is treated as benign content configuration.
   No evidence, scope, or explicit-authority constraint protects it.
2. **Silent Failure Escalation (AP6):** the validator reports `GOOD` or
   `ADEQUATE` while the legal claim is unsupported or structurally absent.
   Its apparent health signal conceals the failed authority check.
3. **Untyped evidence collapse:** absent, one-file, multiple-file, custom,
   split-scope, and explicitly authorized states all collapse into prose. The
   generator cannot fail closed because it receives no typed state.
4. **Presentation validation standing in for semantic validation:** badges,
   links, substrings, and formatting are scored while the claim's source and
   scope are not part of the contract.
5. **Duplicated normative sources:** active guidance, archived guidance, and
   a historical prompt all restate the policy instead of deriving from one
   tested authority contract.

#### Level 3: Development practice

- A legal/permission decision was shipped as natural-language guidance rather
  than an executable evidence boundary with explicit inputs and outputs.
- Promotion from an archived standalone skill to an active route copied prose
  without a migration review of assumptions, target scope, or failure modes.
- Validation tests cover parser mechanics but omit adversarial repository
  states: absent evidence, conflicting files, custom terms, prose-only false
  positives, and explicitly authorized selections.
- The quality score starts from presentation completeness and has no
  fail-closed semantic gate for unsupported consequential claims.
- Repository-wide anti-pattern scans do not prevent unsafe legal defaults from
  being reintroduced through archived or generated teaching material.

The immediate fix must change the responsible lines. The systemic fix must
introduce a typed license-authority boundary and structural validation. The
durable practice change is to require negative fixtures and a repository-wide
contract scan whenever an agent route can publish permission, privacy,
security, or compliance claims.

### Phase 8: Immediate fix

- Removed the invented Creative Commons default and unconditional grant from
  the active README guide, archived source, and historical generation prompt.
- Made badges and License sections conditional on unambiguous repository
  evidence or an explicit owner-authorized selection for that repository.
- Defined absent, conflicting, compound, scoped, and nonstandard evidence as
  fail-closed states: omit a single-license claim and report the evidence
  state outside the generated README.
- Replaced substring section detection with ATX/Setext Markdown heading
  extraction and made License optional rather than a required section.
- Added regression tests proving that unrelated prose cannot satisfy a License
  section and that reusable guidance cannot restore the invented default.

Focused verification: 9/9 `book-publisher` tests pass, changed Python files
compile, `git diff --check` passes, and the targeted repository-wide unsafe
phrase scan has zero hits outside the repository's own licensed README and the
investigation evidence.

## Execution Checklist

- [x] Open the investigation and preserve the initial reproduction.
- [x] Calibrate the generative prior and record initial hypotheses.
- [x] Collect non-destructive source, history, route, and validation evidence.
- [x] Run targeted experiments against absent, conflicting, nonstandard, and
  prose-only license states.
- [x] Assign three-level blame after one hypothesis exceeds 90%.
- [ ] Implement the immediate and systemic remediation.
- [ ] Search the entire repository for the anti-pattern.
- [ ] Run focused, full, release, and installed-skill validation.
- [ ] Commit, open a PR, babysit it to merge, and verify `origin/main`.
- [ ] Run CE Compound and replace `CURRENT` with closure evidence.
