# 0016. A coverage status names an observation, not a diagnosis

**Status:** Accepted
**Date:** 2026-09-01

## Context

A capability doc ends with a Test Coverage table: one row per scenario, naming the test that proves
it and a status. Three statuses have carried that table since it was introduced — `Covered`,
`Not covered`, and `Not covered (code-derived)` — and all three describe a *static* relationship
between a scenario and a test file. None of them describes a **test run**.

That was fine while the table was filled in by hand at the end of `/plan`. `/testify` changes it: the
spell writes tests, runs them, and writes the result back. So for the first time something has to
record what a run established, and the obvious first draft of that — a status per *reason* a test did
not pass — turns out to be unwritable.

**A failing test has at least three causes and the run cannot distinguish them.**

| What was observed | What it might mean |
|---|---|
| Test written, run, did not pass | The behavior has not been built yet — normal partway through an increment |
| Test written, run, did not pass | The behavior was built and has since regressed |
| Test written, run, did not pass | The behavior is fine and the doc's claim about it is wrong |

Nothing available at the moment the row is written separates these. Not the test output, which is the
same in all three cases. Not the doc's Draft banner either: `/plan` phases its work and
`/implement-step` runs one step at a time, so **a draft doc with some scenarios genuinely passing is
the normal middle state of the flow**, not an anomaly. A status named `Not built yet` would be a guess
recorded as a fact, in the one document a project treats as its behavioral contract.

The prior art pushed the other way. A test-generation skill read from the client project decides from
a git diff that nothing is built yet and wraps everything it writes in an expect-to-fail marker. That
is sound for its trigger — a spec file changed and nothing else did — and unsound for this one, where
the input is a capability doc covering an increment built in phases.

## Decision

**A coverage status names what was observed, never why.** Two statuses join the vocabulary:

- **`Test failing`** — a test asserts this scenario and its last run did not pass. Deliberately not
  `Not built yet`, `Regression`, or `Doc wrong`. The row names the test and stops.
- **`Not coverable — <reason>`** — the project has decided this scenario cannot be proved here. The
  reason travels inside the cell, because a decision whose grounds are not recorded cannot be
  re-judged when the grounds change.

**Interpretation lives in the report, not in the table.** Whoever writes the row also writes prose
around it, and prose is where a failure gets argued: expected of work in flight while the doc is a
draft, a disagreement between doc and code once it is not. Same observation, same status, different
sentence. **The Draft banner is report framing and never control flow** — it changes how a result is
explained, never which result is recorded.

**A failing test is never downgraded to `Not covered`.** A test that exists and fails is strictly more
than no test, and collapsing the two throws away the only proof anybody has written.

## Alternatives considered

**Split the Status column in two** — one cell for whether a test exists, one for what its last run
established. This is the honest normalization: five statuses in one cell encode two independent facts,
which is why `Covered` and `Test failing` differ only in the second and `Not covered` and
`Not coverable` only in the first. Rejected *for now* on cost: it rewrites every coverage table in
every existing capability doc, in an increment whose subject is something else. Parked in the
Test Coverage feature doc rather than dropped.

**Cause-named statuses** (`Not built yet` / `Regression` / `Doc wrong`). Rejected above: the writer
cannot tell them apart, so the vocabulary would force a guess and then preserve it. A reader who later
finds the guess wrong has no way to know it was ever a guess.

**Infer the cause from the Draft banner** — a failure under a draft is unbuilt work, a failure under a
verified doc is a regression. Rejected because the premise is false. A draft doc is not a doc for
unbuilt behavior; it is a doc whose scenarios have not been verified, and it routinely describes work
that is half built. The banner earns its place framing the sentence, not choosing the status.

**Leave a failing test as `Not covered`.** Rejected: it is a lie of omission that makes an existing
test invisible, and it guarantees the test is written twice.

**A `Blocked` status for a scenario with no harness to prove it.** Rejected as a category error.
Blocked-ness is a property of a *report* at a moment in time — nobody has decided anything, and the
row is still an ordinary gap. `Not coverable` is admissible precisely because it is the opposite: a
decision was made, and a decision is durable enough to belong in a document. Where infrastructure is
genuinely missing, the row stays `Not covered` and the missing infrastructure becomes spec-sized work.

## Consequences

- The vocabulary is five statuses in one column, and the parking-lot item above is the price. Anyone
  reading a table has to hold two questions in one cell.
- **Three shipped files now share one vocabulary** — the template declares it, `/feature` and `/spec`
  write it — with nothing but an author's memory linking them. Gate check 17 closes that: it reads the
  statuses the template declares and fails if either spell does not name one. Writing it immediately
  found real drift, in that `/spec` had never named a single status despite creating the table.
- `Not coverable — <reason>` is the first status carrying free text. The vocabulary stays L0 and the
  reason stays the project's, which is the same split every slot makes.
- **Nothing re-runs a `Test failing` row.** A row goes stale the moment the work behind it lands, and
  the status then understates what is proved. Recorded as a known gap rather than solved here: the fix
  is a re-run, and nothing in the flow owns re-running yet.
- The same applies to a `Not coverable` reason, which stops being true when the thing it names
  changes, and which nothing re-reads.
