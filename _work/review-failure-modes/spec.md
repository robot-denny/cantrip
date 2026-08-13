# Spec for review-failure-modes

> This spec captures initial requirements and design rationale. For **current system
> behavior**, see the doc named on the **Work type** line below — a new feature doc for a new
> capability, an existing feature doc for a change, or a `docs/` runbook for a fix.

branch: review-failure-modes
design reference (if any): none

**Work type**: change-to code-review
**Feature doc**: code-review

## Summary

Core's reviewers cover generic web-application concerns, but two specific failure modes are absent
everywhere: an error rethrown in a way that discards where it came from, and a log call that folds its
values into the message text instead of passing them as separate fields. Neither draws a finding today
from any reviewer, in any language.

Both are language-agnostic. Every language with exceptions can lose an error's origin on rethrow; every
structured logging library can be defeated by building the message as one string. So they belong in core
rather than in any stack pack, and adding them improves review for every project regardless of stack or
which packs are installed.

**Scope correction made while writing this spec.** The work was framed as *three* failure modes, the
third being long-running work the caller cannot cancel. Checking core first showed that one is **already
owned** — the performance reviewer names "missing cancellation propagation" among its focus areas and
requires long-running outbound calls to propagate cancellation and carry a timeout. Adding it to the
quality reviewer as well would put one rule in two reviewers whose findings are **merged into a single
report**, so the reader would see it twice. It stays where it is, and this increment instead states the
ownership explicitly so anything extending review later knows which reviewer to extend.

This increment is a prerequisite for the `dotnet-pack` increment, which names the C# form of each defect
core describes. It ships and stands on its own.

## Functional Requirements

- **FR1** — A review reports an error rethrown in a way that discards its original origin, and names what
  preserves it.
- **FR2** — A review reports a log call that builds its message as one interpolated string instead of
  passing its values as separate fields, and says what is lost.
- **FR3** — Cancellation of long-running work stays owned by the performance reviewer. The quality
  reviewer does not report it, and the ownership is written down where a future author will look.
- **FR4** — Both new checks are stated as failure modes with their consequence, naming no
  language-specific interface, so they read correctly for any language.
- **FR5** — Both map onto the existing Blocker/Major/Minor/Nit scale rather than introducing a severity.
- **FR6** — Neither duplicates what core already covers — swallowed exceptions and empty catch blocks,
  and blocking calls in async contexts, are already there.
- **FR7** — Core stays free of technology names and the layer-contract gate passes.

## Design Reference (only if one exists)

None. The reasoning for splitting this out from the .NET pack increment — that these have standalone
value in any language, and that the pack's wording follows them — is recorded in
`_work/dotnet-pack/discovery.md` §9a and in that increment's spec.

## Possible Edge Cases

- **A language without exceptions.** Where errors are returned rather than thrown, "discarding the
  original" looks like replacing an error instead of wrapping it. The wording has to cover both without
  naming either language's mechanism.
- **A deliberate wrap.** Replacing a low-level error with a domain-specific one *that carries the original*
  is correct practice, not a defect. Flagging it would train readers to discount the check.
- **A log line with no values.** A fixed human-readable message has nothing to pass as fields, so
  interpolation is not the issue and no finding applies.
- **A logging library with no structured mode at all.** The finding is then about the library choice, not
  the call — and may be out of scope for the diff under review.
- **Overlap with the existing swallowed-exception bullet.** A catch block that logs and discards can trip
  both; the reader should see one finding, not two.
- **The merged report.** Three reviewers' findings combine into one ranked list, so a rule owned by one
  reviewer appearing from another is a visible defect, not a harmless redundancy.
- **A short-lived operation.** Not everything needs cancellation, and over-reporting here is the failure
  mode — which is part of why this stays with the reviewer that already reasons about cost.

## Acceptance Criteria

- A review of a change that rethrows an error while discarding its origin reports it, and names what
  preserves the origin.
- A review of a change that logs values by building one interpolated message reports it, and says the
  values can no longer be filtered on afterwards.
- A change that wraps an error while carrying the original draws no finding.
- A log line with no values in it draws no finding.
- A change with long-running uncancellable work is reported by the performance reviewer, and **not**
  additionally by the quality reviewer — the merged report shows it once.
- Both new checks carry a severity from the existing four-level scale.
- Both read correctly against a diff in a language other than C#, which is the evidence that they belong
  in core rather than in a stack pack.
- The layer-contract gate passes, with no technology name introduced into core.

## Scenarios (Draft)

Draft BDD scenarios derived from the acceptance criteria using Example Mapping. Each Rule maps
to an acceptance criterion; scenarios use concrete examples. These get verified and refined
after implementation — the feature doc holds the verified version.

### Rule: An error rethrown without its origin is reported

```scenario
Scenario: A rethrow that replaces the original error is reported
  Given a change whose error handler rethrows the error it caught, by name
  When the change is reviewed
  Then the review reports that where the error came from is discarded
  And it names the form that would preserve it
```

```scenario
Scenario: A wrap that carries the original draws no finding
  Given a change that replaces a storage error with a domain-specific one
  And the replacement carries the original error inside it
  When the change is reviewed
  Then no finding is raised about losing the error's origin
```

### Rule: A log call that hides its values is reported

```scenario
Scenario: An interpolated message is reported
  Given a change that logs an order number and a retry count as one built-up message string
  When the change is reviewed
  Then the review reports that the order number cannot be filtered on afterwards
```

```scenario
Scenario: A message with no values draws no finding
  Given a change that logs the fixed message "Nightly import finished"
  When the change is reviewed
  Then no finding is raised about how the message was built
```

### Rule: Cancellation belongs to one reviewer, and the merged report shows it once

```scenario
Scenario: Uncancellable work is reported once, by the performance reviewer
  Given a change that calls an external service with no way for the caller to cancel
  When all three reviewers review the change and their findings are merged
  Then the missing cancellation appears once
  And it is attributed to the performance reviewer
```

### Rule: Both checks read correctly outside any one language

```scenario
Scenario: A rethrow in a language that returns errors rather than throwing
  Given a change in a language where errors are returned rather than thrown
  And the change replaces an error without carrying the original
  When the change is reviewed
  Then the review reports the lost origin
  And its wording does not assume exceptions
```

```scenario
Scenario: An interpolated log message in a non-.NET project
  Given a project with no .NET code and no stack pack installed
  When a review covers a change that logs values inside a built-up message string
  Then the review reports that the values can no longer be filtered on
```

### Rule: Neither check duplicates one core already has

```scenario
Scenario: A catch block that logs and discards yields one finding
  Given a change whose error handler logs the error and then continues
  When the change is reviewed
  Then the reader sees one finding about the discarded error
  And not both a swallowed-exception finding and a lost-origin finding
```

## Open Questions

- **The `code-review` capability doc does not exist yet.** This is a `change-to` an undocumented area, so
  there is nothing to amend. The workflow skill is explicit that classification must not depend on
  whether documentation exists, so the fix is to let `/feature` seed the area doc thin rather than to
  inflate this into a new capability. Worth confirming that is the intent before `/plan` targets it.
- **Which file holds the two checks** — the quality reviewer's own focus areas, or the shared
  `reviewer-discipline` contract? They are domain checks rather than shared discipline, which argues for
  the agent. But the cancellation-ownership statement (FR3) is a cross-reviewer fact, and that argues for
  the shared file. They may not belong in the same place.
- **How much evidence does "language-agnostic" need?** One non-.NET diff is the cheap version. Two
  languages with different error mechanisms would be stronger, and the error-return case is exactly where
  the wording is most likely to read badly.
- **The `dotnet-pack` increment says "three".** Its spec, plan, and draft feature doc were written before
  this scope correction and describe three failure modes moving into core. They need updating to two plus
  the ownership statement — on that branch, not this one.
- **Does the perf reviewer need a matching statement?** FR3 says the quality reviewer defers. Whether the
  performance reviewer should also assert ownership, so the pair is legible from either side, is a small
  call with a real cost in duplication.
- **The allocation cost of interpolated logging has no owner — found during review, deliberately not fixed
  here.** The log entry states only the queryability cost, on the reasoning that cost belongs to the
  performance reviewer. The reasoning is sound and the premise turned out to be false: `perf-reviewer.md`
  mentions logging nowhere, and its "string building in loops" phrase is scoped to iteration, so it does
  not reach a single hot-path call or a call at a level that is disabled and discards the result. Verified
  by grep — the only matches for "log" in that file are "logic" and "technology".

  Left unfixed on purpose. It is a third failure mode, absent from this spec's acceptance criteria, and it
  belongs to a different reviewer's domain — so it earns its own written-down RED rather than riding in on
  this increment's evidence. Adding a performance entry without proving it would be the assert-without-
  evidence this increment has twice avoided.

  **Carry it forward**: it belongs in the capability doc's parking lot when `/feature update code-review`
  runs, and the suggested wording is in the perf reviewer's own (gitignored) agent memory at
  `.claude/agent-memory/perf-reviewer/reviewer_domain_split_logging.md`.

## Testing Guidelines

Meaningful tests for the cases below, without going too heavy:

- **The gate first** — `scripts/check-contract.sh` must pass. Check 8 forbids technology names in core, and
  the natural phrasing for both checks reaches for a specific logging interface or a specific keyword. A
  single slip fails the build, which is the intended guard rather than an obstacle.
- **A written-down RED before each addition.** There is no automated harness for a review, so per the
  `tdd-principles` skill the signal is a build plus one concrete manual check recorded in advance: run the
  review, confirm the finding is genuinely absent, then add the check and confirm it appears.
- **Use a non-.NET diff for at least one of them.** The whole claim justifying core ownership is that
  these are not C#-shaped, and a C# diff cannot demonstrate that.
- **The negative cases matter as much as the positives.** A deliberate wrap and a value-free log line must
  draw nothing. A check that only ever fires is one readers learn to ignore.
- **The merged report, for FR3.** Run all three reviewers over one uncancellable-work change and confirm
  the finding appears once. This is the only case where the defect is visible solely after merging.

Not worth doing: adding a fixture under `tests/install-check/`. That harness tests the install checker,
and nothing here changes what it reports.
