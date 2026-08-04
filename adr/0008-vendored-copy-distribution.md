# 0008. Distribute as a vendored copy with a lockfile and an assisted update

**Status:** Accepted — backfilled 2026-08-04; decided before this repository existed
**Date:** 2026-07-30 (decision) / 2026-08-04 (recorded)

## Context

Three distribution models were on the table for getting a toolkit into many projects.

The tailoring problem drives the choice. A toolkit that cannot be tailored per project is useless for
agency work, where every codebase has different conventions — but tailoring that forks the toolkit
destroys the ability to ship improvements. **At decision time it was not yet known where the tailoring
seams would fall**, which turned out to be the deciding constraint.

## Decision

**Projects vendor a copy.** The toolkit's files are visible in the consuming repository, plain markdown,
editable, and readable by any agent. A lockfile records the source and a content hash per unit. An
update flow reconciles the vendored copy against upstream and surfaces local modifications for review.

## Alternatives considered

**A read-only plugin.** Cleanest update story — the toolkit is a dependency, never edited, always
current. Rejected because **it forecloses tailoring before the seams are known.** A project needing one
project-specific behavior would have no way to express it except forking wholesale, and at decision time
nobody could enumerate which behaviors would need to vary.

The slot mechanism (ADR 0001) is what eventually made tailoring expressible without editing — but that
mechanism was designed *after* this decision, and could not have been specified in advance.

**Copy once and diverge.** What the two source projects were already doing, which is the pain this
toolkit exists to remove: a third project had begun hand-trading files with them. Rejected as the status
quo being escaped.

## Consequences

- Consumers can read every file the toolkit runs, which matters for trust in a tool that edits code.
- Improvements reach existing projects only if someone runs the update — a real cost, and the reason
  `/update-toolkit` exists rather than leaving `update` to the bare installer.
- **The lockfile's source string becomes part of each consumer's repository**, with the consequences for
  ownership changes recorded in ADR 0007.
- Local edits are possible and therefore must be *discouraged by contract* rather than prevented by
  mechanism — hence ADR 0001's rule that editing a vendored file is a divergence, and that needing to
  edit one means a missing slot.
- A plugin wrapper can be added later for faster installs once the seams have stabilized. Both
  distribution models can ship from one repository.
