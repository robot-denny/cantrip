# 0004. Install layout — corrections from verifying the CLI

**Status:** Accepted — supersedes two claims in [ADR 0002](0002-packaging-and-install-shape.md)
**Date:** 2026-08-03

## Context

ADR 0002 settled the packaging shape on two assumptions carried from the direction doc's
2026-07-30 CLI evaluation, and flagged one of them for verification at this increment. Verifying
against `skills@1.5.21` (vercel-labs) showed **both** were wrong, and turned up one capability
nobody had recorded.

Verification ran with `DISABLE_TELEMETRY=1` throughout, since the same evaluation found the CLI
uploads skill file contents by default.

## What was wrong

### `--agent` does not install agent definitions

The doc recorded "selective pick (`--skill`, `--agent`) works", which is true but means something
else: `--agent <agents>` selects **which agent tool** to install *to* — Claude Code, Cursor, Codex,
Copilot. It has nothing to do with installing agent definitions.

There is no mechanism in this CLI for installing a registered subagent. `--subagent` exists but
targets a different product's concept.

So the three reviewers at repo-root `agents/` were **not installable at all**, and would simply have
been absent after any install.

### The install layout has no `.agents/` tree

The doc recorded that the CLI "normalizes to canonical `.agents/skills/` + `.claude/skills/` symlink
(our exact convention)". It does not. A real install produces:

```
.claude/skills/<name>/     # real directory, copied — not a symlink
skills-lock.json
```

No `.agents/` directory is created. The install summary *mentions* an `.agents/skills/` path, which
is what made the original reading plausible, but nothing lands there.

This mattered more than it looks: ADR 0001's "canonical paths" refinement had three spells reading
`.agents/skills/workflow/templates/spec.md`, **a path that does not exist after installation.**

## What was right, and what was new

**Asset bundling works.** Installing the `workflow` skill brought `templates/spec.md` and
`templates/feature.md` along inside the skill directory. ADR 0002's core decision — non-skill assets
ship inside a skill directory — is verified.

**The lockfile is richer than expected.** The CLI writes `skills-lock.json` recording `source`,
`sourceType`, `skillPath`, and `computedHash` per skill — and `skillPath` tracks the source location
in our taxonomy layout, so it round-trips correctly.

**Subpath-scoped sources work — and this solves pack selection.** `add <repo>/skills/core` finds
exactly the 12 core skills; `add <repo>/skills/umbraco-17` finds the 2 pack skills. This was not in
the evaluation, and it delivers the doc's "public baseline = core + no pack" with no repo split, no
flag gymnastics, and no 12-name skill list.

That is a direct payoff from the Phase 0 taxonomy decision. `skills/core/` and `skills/<pack>/` were
chosen for legibility and to make invocation posture gate-checkable; they turn out to be the
install-scoping mechanism too.

## Decision

**1. Reference toolkit assets by skill and asset name, never by install path.**

A spell needing a template says "the `templates/spec.md` asset of the `workflow` skill", not any
absolute path. Install layout varies by agent tool and by CLI version — as this increment proves —
so any hardcoded path is a latent break. An agent with the skill installed can locate its own skill
directory.

This supersedes ADR 0001's "canonical paths" corollary, which was right to reject relative paths and
wrong about what to replace them with.

**2. The reviewer agents ship as assets of the `reviewer-discipline` skill.**

They move from repo-root `agents/` to `skills/core/reference/reviewer-discipline/agents/`. That makes
them install, and makes them hash-tracked by the lockfile like everything else.

Because Claude Code discovers registered subagents from `.claude/agents/`, placing them there remains
a step the CLI cannot perform. It is one documented command after install. Until it is run,
`/code-review` and `/retrofit` fall back to inline sequential review passes — a degradation both
already document — so **the toolkit is fully functional before that step, just without parallel
dispatch.** Standalone-first survives.

**3. Adopt `skills-lock.json` rather than inventing `toolkit-lock.json`.**

The plan called for a `toolkit-lock.json` generalizing the existing pattern. The CLI already writes
exactly what is needed, including the per-skill hash the update flow depends on. A parallel lockfile
would have to be kept in sync with the real one for no gain.

**4. Install is subpath-scoped.**

- Core only: `npx skills add <repo>/skills/core --all`
- Plus a pack: `npx skills add <repo>/skills/umbraco-17 --all`

## Consequences

- Three spells were reading a path that would not have resolved after install. Caught here rather
  than at first cast, which is exactly what this phase exists for.
- Root `agents/` disappears; the gate's technology-name check follows the files into `skills/core/`.
- Packs are opt-in by construction, so the public core-only baseline is real rather than a
  convention someone has to remember.
- **The direction doc's CLI evaluation should be treated as dated.** Two of its four recorded layout
  and flag findings did not survive contact with `1.5.21`, four days later. Its behavioral findings —
  that `update` clobbers local edits, that telemetry uploads content — still need their own
  verification at increment 3.2 rather than being trusted.
