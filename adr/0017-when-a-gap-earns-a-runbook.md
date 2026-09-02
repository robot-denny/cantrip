# 0017. When a gap earns a runbook

**Status:** Accepted
**Date:** 2026-09-02

## Context

`/guide` writes editor-facing guide pages. It does not create the four document types those pages are
pages of, and it never will — the templates they need are markup, and
[ADR 0006](0006-no-unguarded-preconditions.md)'s prohibition on fabricating a convention means a
project with nothing to copy is a stop rather than a gap to fill. That part is correct and settled.

What is not correct is what a person meets there. A greenfield user casting `/guide` is asked for the
guides node's key — *"the one fact only the project can supply"* — for a node that was never created,
with no indication that four document types and two templates stand between them and having one.

**The precondition is guarded, and the guard covers the wrong absence.** The `## Editor guides`
slot's `**If empty:**` clause handles exactly one state: the section exists and its key is not
recorded. Every branch downstream inherits that framing. There is no branch for *the section does not
exist at all*.

This is ADR 0006 landing on its own doorstep, and the interesting part is that its forcing function
**fired**. Gate check 4 refuses a `**Slot:**` without an adjacent `**If empty:**`, the clause is
present, and the check passes. A gate can see that an absence clause exists; it cannot see that the
absence it describes is not the only one. So the lesson from 0006 needs one more turn: *writing an
absence branch is not the same as enumerating the absences.*

Two other things were already true and pointed the same way.

**The toolkit has a declared home for human documentation and has never used it.**
[`docs/layout.md`](../docs/layout.md) has carried `docs/ — durable human reference: runbooks, guides
— evergreen` in the consuming-project tree since the layout was written. `audits/` beneath it has a
producer. The parent has never had a tenant.

**The roadmap has an open question this answers half of.** *"An installed project receives no
human-facing documentation at all"* lists four uncosted options — a README per unit, one orientation
file per pack, `/setup` writes a pointer, or declare the surface agent-only — and says **"Deciding is
cheap and is the actual blocker."** It has stayed open because every option costs per *unit* or per
*pack*, and neither is the thing that varies.

And the timing forces it. A greenfield pilot starts now, with a team using the toolkit for the first
time. ADR 0006 admitted it was waiting for exactly this project to exercise its speculative branches.
A team that hits walls with no test to sort them by produces a pile of anecdotes; the test has to
exist before the logging starts, not after.

## Decision

**A gap earns a runbook when all three of these hold. The test is conjunctive.**

| | The part | Why it is in the test |
|---|---|---|
| 1 | **The precondition is mechanical and identical on every project** | This is what lets the prose be exact — *create these six properties with these aliases* — rather than advisory. Advisory prose is what nobody reads |
| 2 | **The toolkit deliberately declines to automate it, and the decision is on record** | "We have not got to it yet" is a roadmap item. A runbook documenting work we intend to remove is work we will throw away |
| 3 | **Getting it wrong fails silently** | A mistake that errors at the point of the mistake needs a better error message. A mandatory `guideSource` does not error — it makes generated pages unsaveable halfway through a run, three weeks later |

**A gap that fails the test is not homeless.** Failing (1) means it is project-specific and belongs in
that project's own docs. Failing (2) means the automation decision comes first, and the gap is a
roadmap item until it is taken. Failing (3) means an error message is the whole fix, and it is
cheaper than prose.

**Three rules come with it.**

**A runbook is written to a person.** Second person, in `docs/runbooks/`, assuming platform
competence and no knowledge of any skill. Every other unit in this toolkit is written to an agent;
this is a different register and mixing them produces a file that serves neither.

**The guard names the runbook.** Whichever instruction stops on the missing precondition must name
the file, so it is reached at the moment somebody hits the wall. **Discoverability is the
deliverable** — a runbook nobody finds is the README problem wearing a new hat, and this toolkit has
already shipped 7,800 lines nobody is told are readable.

**A runbook cites what it duplicates and says the source wins.** Restating is permitted — a person
building document types in a backoffice needs the table in front of them, not a citation — but the
file names its authorities and states that they are right on any disagreement.

## Alternatives considered

- **A README beside each unit** — *rejected.* 32 hand-written files, which is the exact maintenance
  the 2026-09-01 README split was trying to avoid. Its cost scales with the catalogue, and the
  catalogue is not what varies.
- **One orientation file per pack** — *rejected.* One file per pack forever, whether or not that pack
  has a wall in it, and general enough to be unactionable. It would not have told anybody to untick
  *mandatory*.
- **Fold the setup sequence into the reference it belongs to** — *rejected.* The scaffolding reference
  is already the largest unit in any pack with a seam the roadmap has recorded, and every
  `/guide --audit` cast would pay for prose it never reads.
- **A `/scaffold-guides` spell** — *rejected.* A fourth unit in a pack already flagged for size, and it
  could not finish the job anyway: the templates are markup, so it would stop halfway and still need
  the prose.
- **Declare the installed surface deliberately agent-only** — *rejected for now.* Defensible, and it
  does nothing for a team starting next week.
- **A first-run branch in `/guide` that creates the four document types after approval** — *not
  rejected; deferred, and still the right answer for the schema half.* `/styleguide` already creates
  element types and a palette under a scoped approval, so the precedent exists. It is deferred because
  it does not remove the templates from the path, and because the runbook is needed before it could
  ship. **The runbook is not a substitute for fixing the guard.**

## Consequences

- **One runbook exists**, for the Umbraco guides section. Generalizing a mechanism from a single
  instance is thin, and the thinness is deliberate: `/setup` copying runbooks into a consuming
  project, and a gate pairing a runbook's restated tables against their source, both wait for a
  second instance to generalize from. This is [ADR 0006](0006-no-unguarded-preconditions.md)'s own
  rung 3 — seed thin, and make the thinness visible.
- **Runbooks do not ship.** Installs are subpath-scoped, so only `skills/` reaches a consumer. The
  pilot copies the file by hand. Which of the roadmap's options delivers it is still open, and this
  record does not settle it — it only removes the objection that there was nothing to deliver.
- **Sanctioned duplication with no gate.** The guides runbook restates seven property aliases whose
  authority is `REGISTER` in `changeplan.py`. Named, cited, and ungated until there is a second file
  to write the gate against. This is the one rule here that nothing enforces, and it says so.
- **A new constraint on instructions:** where a stop has a runbook remedy, the stop names the file.
  Not gated yet, for the same reason.
- **The guides guard is still wrong.** This record does not fix the `## Editor guides` slot's
  `**If empty:**` clause, which still describes two states where there are three. That fix, and the
  first-run branch it would point at, are outstanding work.
- **The pilot is the instrument, not the audience.** Every wall the team hits gets logged and tested
  against the three parts. Most will fail — becoming roadmap items, guard fixes, or better error
  messages — and that is the correct outcome, not a sign the test is too strict.
