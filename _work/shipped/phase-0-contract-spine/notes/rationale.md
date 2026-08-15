# Phase 0 rationale — contract, spine, packaging

**Date:** 2026-08-03
**Increments:** 0.1 – 0.6
**Gate:** `scripts/check-contract.sh` — 7/7 passing, all checks negative-tested

## What was decided, and why

### ADR 0001 — the slot mechanism is plain markdown, not templating

The alternative was token substitution (`{{slot:stack.build_command}}`) with a processor.
Rejected because a file needing preprocessing to be read violates the markdown-first,
LLM-portable principle, and the `**Slot:**` / `**If empty:**` convention recovers most of the
validation benefit — a grep can verify the pairing, which check 4 now does.

The four slot files came out of evidence, not invention. Surveying what the L0-bound files
actually embed produced exactly four clusters: where things live, how to run things, how this
project works, and what each reviewer enforces. The most persuasive single find was absolute
`nvm` paths pinned to **two different Node versions** across the two repos — a fact that
cannot ship under any packaging scheme.

### ADR 0002 — everything installable is a skill directory

Driven by a mechanical limit: the skills CLI installs skill directories, but the spine,
templates, and agents are not skills. Rather than defer installability to the setup skill
(Phase 6), non-skill assets ship *inside* skill directories.

This was not a guess — both source repos already prove the pattern. `architecture-audit`
ships `scripts/`, `references/`, `assets/`, `evals/`; `skill-creator` ships `agents/` plus
four more. Both install to `.agents/skills/<name>/` and whole-directory symlink into
`.claude/skills/`, so assets travel free.

One distinction worth keeping straight: `skill-creator`'s bundled `agents/*.md` are prompts it
dispatches internally, **not** agents Claude Code registers. The three reviewers must be
genuinely registered to be invocable, so they stay at repo-root `agents/` and rely on the
CLI's `--agent` support. That is the one unverified dependency in Phase 0, flagged in ADR 0002
for confirmation at increment 3.1.

### Layout: taxonomy over flat

Restructured to `skills/core/spellbook/` and `skills/core/reference/` mid-phase, matching the
direction doc's §5 legibility convention. The payoff was unplanned: invocation posture becomes
enforceable *by path*, so check 5 can assert that everything under `spellbook/` is
user-cast-only and everything under `reference/` is model-invoked. A naming convention that the
gate can check is worth more than one that only reads well.

Repo layout and install layout are deliberately different — install flattens to
`.agents/skills/<name>/`, so the source tree is free to organize for humans.

## De-projection of the spine

~80 lines of source spine (the client project's `CLAUDE.md` spine section as base, plus the
demo project's `/retrofit` paragraph and richer work-types table) became a 143-line reference
skill. It grew, as ADR 0001
predicted it would — slot references cost three lines where an inline fact cost one.

What moved or went:

| Source | Disposition |
|---|---|
| Project-specific "a feature is a vertical slice" framing | → `conventions.md` slot, with a repo-inference fallback |
| `_specs/`, `_plans/`, `_features/`, `_audits/` | → `_work/<slug>/` increment bundle + `docs/audits/` |
| `_prds/` | Dropped — never materialized in either repo, and §6a says not to reserve the directory |
| References to `CLAUDE.md` for the work-types table | → this skill owns the spine; four spells will link here instead |
| `.claude/skills/BDD.md` | → the `bdd-principles` skill |
| The demo project's work-type Examples column (all project-specific) | → generic-but-concrete examples |
| The demo project's retired-doc citations | Dropped — point-in-time project history |

Preserved intact because it is the load-bearing content: the five-layer flow, one-spec-per-
increment, the `Next:`-line-never-invoke rule, the retrofit standing rule, three-way work-type
classification, *the tell*, and *the key judgment* on observable versus point-in-time criteria.

## Notable: the gate caught a real violation on first run

`docs/contract.md` used a client assembly name as an illustrative example of a project fact.
The irony is instructive — the document defining the no-client-facts rule broke it, in a
sentence explaining the rule. Fixed to `src/<AssemblyName>.Features/Blocks/`.

That is the argument for building the gate in Phase 0 rather than later. It also validates
making check 1 repo-wide rather than shipped-units-only: the violation was in `docs/`, which a
skills-only scan would have missed entirely.

## Carried forward

- **`--agent` install support is unverified** (ADR 0002). Confirm at 3.1; if it does not
  register agents, the reviewers fall back to setup-skill placement and that ADR row is
  superseded.
- `BDD.md` arrived already carrying `name: bdd-principles` frontmatter and scanned clean for
  project facts, so 0.5 was a genuine free move. Only the description needed
  trigger-engineering — the original was 52 characters, below the 40-char floor check 6 now
  enforces but far too thin to trigger reliably.
- Phase 0 could only be validated structurally. Checkpoint B is the first real test of whether
  the contract reads well on an actual extracted spell.
