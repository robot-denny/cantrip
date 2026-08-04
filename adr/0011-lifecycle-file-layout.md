# 0011. Organize the workspace by lifecycle, not by artifact type

**Status:** Accepted — backfilled 2026-08-04; decided before this repository existed
**Date:** 2026-07-30 (decision) / 2026-08-04 (recorded)

## Context

The source projects kept one directory per artifact type — specs together, plans together, capability
docs together — each with its own `shipped/` archive. It works, but it splits a single increment's
artifacts across three places and archives them independently.

The methodology's central distinction is **temporal versus evergreen**: a spec and a plan describe one
moment's intent and stop mattering once shipped; a capability doc describes how the system behaves right
now and never stops mattering. A type-based layout does not express that at all.

## Decision

**Group by lifecycle, and make the increment a bundle.**

| Path | Holds | Lifecycle |
|---|---|---|
| `_features/<area>.md` | One file per capability, named by area | Evergreen |
| `_work/<slug>/` | One directory per increment: spec, plan, discovery, notes, assets | Temporal |
| `_work/shipped/<slug>/` | The whole bundle, archived in one move | Temporal, closed |
| `docs/` | Runbooks, guides, dated audits | Evergreen |
| `_scratch/` | Disposable, git-ignored wholesale | Throwaway |

`_features/` stays root-prominent deliberately: capability docs are the cross-functional artifact, and
that visibility carries the thesis. Specs and plans mid-flight are developer-facing and lose nothing one
level down.

## Consequences worth having noticed

- **The bundle absorbs cardinality changes.** If the spec-to-plan relationship stops being one-to-one, it
  changes inside one directory rather than across three. Every spell's contract is just "look in
  `_work/<slug>/`".
- **Archiving is one move**, and nothing is left behind in a sibling directory.
- **Location enforces commit status.** A report-producing spell asks *durable or temporal* and writes to
  `docs/audits/` or `_scratch/` accordingly — so commit status is a consequence of where a file goes
  rather than a separate thing to remember.
- Discovery output opening the increment directory means the *thinking* archives with the increment it
  produced, which the type-based layout could not do.

## Alternatives considered

**Nest specs and plans under the feature they belong to.** Rejected on cardinality: fix-and-infra work
belongs to no feature, and a body of work can span several.

**Put everything under `docs/`.** Rejected as re-filing living truth as passive documentation — the exact
conflation the temporal/evergreen split exists to prevent.

## The migration cost, and how it was handled

Every path contract changes. The canary consumer resolved this by **adopting the layout for new work and
freezing its legacy directories in place**, recording the split in its `## Workspace` slot. That is now
the recommended answer for an existing project: migrating history buys nothing, since no spell reads a
shipped archive.
