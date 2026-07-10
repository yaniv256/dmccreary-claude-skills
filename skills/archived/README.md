# Archived Skills

These directories are the verbatim originals of standalone skills that were
consolidated into meta-skills. They are **never loaded** by Claude Code: skill
discovery only scans one level below `~/.claude/skills/`, and
`scripts/bk-install-skills` explicitly skips this directory. They are kept for
reference and rollback — to restore one, `git mv` it back to `skills/` and
rerun the installer.

## Alias map: old skill → where it lives now

| Old skill | New home | Trigger keywords |
|-----------|----------|------------------|
| `causal-loop-diagram-generator` | `microsim-generator` → `references/causal-loop-guide.md` | causal loop, CLD, feedback loop, reinforcing, balancing, systems archetype |
| `concept-classifier` | `microsim-generator` → `references/concept-classifier-guide.md` | classify, categorize, sort scenarios, identify types |
| `interactive-infographic-overlay` | `microsim-generator` → `references/infographic-overlay-guide.md` | diagram overlay, callout labels, anatomy, labeled illustration |
| `docker-python-lab` | `microsim-generator` → `references/docker-python-lab-guide.md` | python lab, code runner, runnable code block, docker |
