# 0004. Install layout — corrections from verifying the CLI

**Status:** Accepted — supersedes two claims in [ADR 0002](0002-packaging-and-install-shape.md)
**Date:** 2026-08-03 — corrected 2026-09-04

> **One claim below was wrong when written.** Decision 2 calls the inline sequential fallback "a
> degradation both already document". Only `/code-review` documented it. `/retrofit` dispatched the
> same three reviewers and said nothing about the unregistered case. Its behavior there was
> undefined rather than degraded, and stayed that way for the month this record stood. `/retrofit`
> now documents the fallback and discovers registered reviewers the way `/code-review` does, which
> makes the sentence true. The decision itself is untouched: reviewers still ship as
> `reviewer-discipline` assets, and registration is still a step the CLI cannot perform. This is
> neither an amendment nor a supersession under [adr/README.md](README.md), since nothing was added
> to the decision and nothing reversed. The body stays as written, because a record should say what
> was actually seen at the time.

## Context

ADR 0002 settled the packaging shape on two assumptions carried from the direction doc's
2026-07-30 CLI evaluation, and flagged one of them for verification at this increment. Verifying
against `skills@1.5.21` (vercel-labs) found the first **flatly wrong** and the second **conditional
on how you invoke the installer** — and turned up one capability nobody had recorded.

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

### The install layout depends on how you invoke it

The doc recorded that the CLI "normalizes to canonical `.agents/skills/` + `.claude/skills/` symlink
(our exact convention)". That is true for some invocations and false for others:

| Invocation | Result |
|---|---|
| `--all` (implies `--agent '*'`) | Canonical: `.agents/skills/<name>/` holds real files, `.claude/skills/<name>` symlinks to it |
| `--agent claude-code` (a single agent) | Files **copied** into `.claude/skills/<name>/`; **no `.agents/` tree at all** |

So the doc's claim held for the multi-agent case, and an earlier draft of this ADR over-corrected it
after testing only the single-agent case. Both behaviors are real; neither is the whole story.

**This makes the path problem worse, not better.** ADR 0001's "canonical paths" refinement had three
spells reading `.agents/skills/workflow/templates/spec.md` — a path that exists under one invocation
and not the other. A hardcoded install path is not merely version-fragile; it is fragile against how
the *user* chose to install.

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
absolute path. Install layout varies by agent tool, by CLI version, **and by install flags** — as this
increment proves — so any hardcoded path is a latent break. An agent with the skill installed can
locate its own skill directory.

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
- **Documented commands must be layout-independent too.** The first draft of the README's
  agent-linking command was wrong twice over: it hardcoded `.agents/`, which does not exist under a
  single-agent install, and its glob resolved from the shell's directory while the symlink target must
  be relative to the link's own directory. The working form globs through `.claude/skills/`, which
  exists under *both* layouts, and builds each target relative to `.claude/agents/`. Verified in both
  a greenfield repo and an existing project.
- **Installing shadows same-named commands, with no error and no namespace.** Reported from the
  canary consumer and confirmed against the Claude Code docs: a skill takes precedence over a
  command of the same name. So installing core into a project that already runs its own version of
  this workflow makes those commands *present but unreachable* — not a live fallback.

  This corrects an assumption in the sequencing plan, which treated an additive install as genuine
  coexistence. It is additive on disk and **substitutive in resolution**. The consequence is that
  installing on a branch is not merely tidy, it is the containment mechanism: switching back to the
  default branch restores the original commands intact. Documented in the README, since that is
  where a consumer meets it.
- **`--all` scatters copies across every target it can detect**, which is more than the two documented
  above. Verified: `.agents/skills/` (real), `.claude/skills/` (symlinks), a top-level `agent/skills/`,
  **and — if the project already has a bare `skills/` directory — a full redundant copy inside it,
  alongside the project's own contents.** This last one was missing from the first draft of this ADR and
  only bites repos that already use a top-level `skills/`, which is why it went unnoticed until a
  consumer hit it.

  Nothing is overwritten and nothing breaks, but the project carries copies that `update` touches
  unevenly. Cleanup is `git clean -fd agent skills` — **not** `rm -rf skills/`, which would destroy
  tracked project content. `check-install.sh` now detects the scatter and prints the safe command,
  considering only toolkit-roster names so a project's own skills are never implicated.

  The single-target install (`--skill '*' --agent claude-code`) avoids it entirely; see the README.
- **The direction doc's CLI evaluation should be treated as dated, and so should any single test of
  mine.** Two of its four recorded layout and flag findings did not survive contact with `1.5.21` four
  days later — and my own first correction was itself wrong for having tested one invocation. The
  behavioral findings were verified separately at 3.2: `update` does silently clobber local edits, and
  that one holds exactly.
