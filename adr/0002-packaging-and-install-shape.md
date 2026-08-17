# 0002. Packaging and install shape

**Status:** Accepted — two claims superseded by [ADR 0004](0004-install-layout-corrections.md)
**Date:** 2026-08-03

> **Superseded in part.** Verifying the CLI at increment 3.1 disproved two assumptions this ADR
> rested on: `--agent` selects a target agent *tool* rather than installing agent definitions, and the
> install produces no `.agents/` tree. The central decision — non-skill assets ship inside a skill
> directory — was verified and stands. See ADR 0004 for what changed and why.

## Context

The organizing goal is a standalone, `npx`-installable toolkit reached early rather than as
late polish. That runs into a specific mechanical limit: **the skills CLI installs skill
directories.** But three of the toolkit's load-bearing pieces are not skills —

- the workflow spine and work-types table, which four spells reference,
- the spec and feature templates, which three spells read,
- the three reviewer agent definitions.

If those can only be placed by a setup skill, then nothing but bare skills is installable
until the setup skill exists (increment 6.1), and "standalone and installable" is not
reachable at Phase 3. Since the layout determines where every file gets written, this has to
be settled before the first extracted file lands.

Surveying the source repos for how existing installed skills handle non-skill payloads
settled it, because the pattern is already proven twice over:

- `architecture-audit` ships `scripts/`, `references/`, `assets/`, and `evals/` subdirectories
  inside its skill directory.
- `skill-creator` ships `agents/`, `scripts/`, `references/`, `assets/`, and an `eval-viewer/`
  inside its skill directory.
- Both are installed to `.agents/skills/<name>/` and whole-directory symlinked to
  `.claude/skills/<name>`, so every asset comes along for free.

> **Naming note, added 2026-08-17.** The unit surveyed above as `architecture-audit` ships in this
> toolkit as `codebase-audit`, in the `dotnet` pack. The old name is left in place because this
> section records what was observed in the source repos on the date above, and rewriting an
> observation to match a later rename would make the record less true rather than more useful. No
> claim here is superseded — the layout it was cited as evidence for is unchanged.

There is also a counter-example in both repos worth naming: `BDD.md` sits as a bare loose file
directly in `.claude/skills/`, with no `SKILL.md` and no frontmatter. It is not a skill, is not
installable, and is the "legacy `skills/` folder" the direction doc flags for cleanup.

## Decision

**Everything installable ships as a skill directory.** No loose files at any install target.

| Piece | Ships as | Why |
|---|---|---|
| Spells (`spec`, `plan`, …) | One skill dir each, `disable-model-invocation: true` | Each must be individually castable as `/<name>`, which requires its own directory |
| References (`bdd-principles`, …) | One skill dir each, model-invoked | Description-triggered discovery is the point |
| Workflow spine + work-types | `skills/core/workflow/SKILL.md`, a model-invoked reference | It *is* knowledge the agent reaches for; making it a reference skill means the toolkit owns its spine as an installable unit rather than a loose file |
| Templates | `skills/core/workflow/templates/` — assets of the workflow skill | They are workflow artifacts, so this is their coherent home, and they install with the spine that describes them |
| Reviewer agents | `agents/` at repo root, installed via the CLI's `--agent` support | Claude Code discovers registered subagents from `.claude/agents/`, not from inside skill dirs, so these are not skill assets |

**Consequence for the earlier scaffold:** the root `templates/` directory is removed — it
would be an authoring location that has to be copied to an install location, and that
duplication is exactly how the two source repos drifted. Root `agents/` stays.

The distinction that makes the agents row different from the rest: `skill-creator`'s
`agents/*.md` are prompts *it* dispatches internally, not agents Claude Code registers. The
three reviewers must be genuinely registered to be invocable as subagents, so they cannot be
skill assets.

## Alternatives considered

**One monolithic `cantrip-core` skill holding every spell plus all assets.** Rejected: spells
must be individually castable as `/<name>`, and a single skill directory yields a single slash
command. It would also defeat selective install (`--skill`), which is how a project takes the
core without a pack.

**Shared assets inside one designated spell's directory** (e.g. templates under `spec/`).
Rejected: creates an arbitrary ownership hierarchy where `/plan` reads a file belonging to
`/spec`, and selectively installing `/plan` without `/spec` would silently break it.

**Setup-skill placement for non-skill assets.** Rejected as the *only* path, since it defers
installability to increment 6.1 and contradicts the standalone-first goal. Retained as an
additional path: setup still places the project scaffold (`AGENTS.md`, `_work/`, config slots),
which genuinely cannot ship as skill assets because they are L2 files the project owns.

**Loose files at the install target, like the existing `BDD.md`.** Rejected: not installable,
not versionable by the lockfile, and already identified as cleanup debt in both source repos.

## Consequences

- Phase 3's standalone install becomes reachable: a clean checkout installs spells,
  references, spine, templates, and agents with no setup skill in the loop.
- Every installable unit is hash-trackable by `toolkit-lock.json`, because the lockfile keys on
  skill directories and nothing lives outside one.
- Increment 0.5 converts `BDD.md` from a loose file into a proper `bdd-principles/` skill
  directory, clearing the flagged legacy-folder debt as a side effect.
- Cross-skill references use canonical paths rather than relative ones, per ADR 0001 — a spell
  referring to the spine names `.agents/skills/workflow/`, which survives being vendored into
  layouts we do not control.
- **Dependency to verify at 3.1:** this rests on the direction doc's recorded 2026-07-30
  finding that the CLI's `--skill` and `--agent` selective install work as described. If
  `--agent` turns out not to install registered agents, the reviewers fall back to
  setup-skill placement and this ADR gets superseded for that one row. Nothing else in the
  decision depends on it.
