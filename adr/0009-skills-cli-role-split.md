# 0009. Adopt the skills CLI for install, wrap it for update

**Status:** Accepted — backfilled 2026-08-04; decided before this repository existed
**Date:** 2026-07-30 (decision) / 2026-08-04 (recorded)

## Context

An existing CLI installs agent skills from a repository. Building a bespoke installer instead would mean
owning discovery, fetching, layout normalization, hashing, and cross-agent support — none of which is
this project's problem.

Evaluating it produced a **split verdict** rather than a yes or no.

## Decision

**Adopt it for install and discovery. Do not trust its update.**

What it does well, and is therefore used for: selective install, layout normalization across agent
tools, a lockfile with source and content hash, cross-agent support, and — discovered later — subpath
scoping, which is what makes a core-only baseline possible at all (ADR 0004).

What it does badly: **`update` silently overwrites local modifications.** No warning, no merge, no check
against local state. Verified empirically at increment 3.2 — a local edit was reverted to pristine and
the output reported success.

So `/update-toolkit` is a thin wrapper: require a clean git tree, require the skills to be tracked, run
the underlying update, then present the resulting diff for reconciliation. **Git is the safety net**,
because the lockfile's hash turns out not to be a plain digest of the installed file and cannot serve as
a tamper check.

Telemetry uploads skill file contents by default, so every documented invocation sets
`DISABLE_TELEMETRY=1`.

## Alternatives considered

**Build a bespoke installer.** Rejected: large surface area, no differentiation, and it would forfeit
cross-agent support that already works.

**Use the CLI's update as-is.** Rejected on evidence. It is not merely unhelpful about local edits — it
reports success while destroying work, which is worse than failing.

**Wrap install too.** Rejected: install is well-behaved and additive. Wrapping it would add a layer with
nothing to fix.

## Consequences

- A dependency on a third-party tool's behavior, which **has already changed under us**: two of the four
  layout and flag findings from the original evaluation did not survive four days (ADR 0004). Treat any
  recorded finding about it as dated.
- The safety of `/update-toolkit` rests on git, so a project that does not track its installed skills
  gets a loud warning and an explicit override rather than a silent risk.
- The contract's "never edit vendored files" rule hardens from principle to requirement, because the
  underlying tool will destroy such edits.
