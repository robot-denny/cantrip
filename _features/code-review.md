# Feature: Code Review

A developer hands a change to review and gets one ranked report rather than three overlapping ones. Three
reviewers each cover their own domain — quality, performance, accessibility — under a shared contract that
governs scope, severity, evidence, and where their domains touch. The report names what is wrong, what it
costs, and what to do about it, with each defect appearing exactly once no matter how many reviewers could
have claimed it. Security is checked against a named public standard, so a finding says which category it
belongs to and a clean review says which areas it swept.

**Source**: `_work/shipped/review-failure-modes/spec.md`, `_work/shipped/owasp-security-review-rules/spec.md`
**Last verified**: 2026-09-08

> **Thin by design.** This doc records what the `review-failure-modes` and `owasp-security-review-rules`
> increments established, and nothing older. The review capability is considerably larger than what is
> documented here — the severity scale, the diff-only scope rule, the evidence standard, the Clean section
> itself, the reviewer-discovery behavior, and each reviewer's own domain checklist all predate any spec
> and appear in no scenario below. That is visible debt with a known remedy: `/feature`'s from-code mode
> can backfill the rest against the reviewer files. It is not a claim that the capability does only this.

---

## Increments

The per-feature mini-roadmap: shipped increments, planned increments, and parking-lot ideas.
Newest planned items first. When an item ships, flip the checkbox and point it at the archived
increment.

- [x] 2026-09-08 — Security checked against a named standard: a finding carries its OWASP category, a
      clean review names the areas it swept, and a change with nothing to check claims nothing
      (`_work/shipped/owasp-security-review-rules/spec.md`)
- [x] 2026-08-13 — Two language-agnostic review failure modes, plus the domain boundary that keeps a
      shared rule from being reported twice (`_work/shipped/review-failure-modes/spec.md`)
- [ ] **Backfill**: everything the capability did before this increment. See the note above — the
      from-code technique against `reviewer-discipline/SKILL.md` and the three agent files is the path
- [ ] Parking lot: the allocation cost of building an interpolated log message has no owner. The quality
      reviewer states only the queryability cost, on the grounds that cost belongs to the performance
      reviewer, and that reviewer's checklist does not mention logging at all. Recorded with evidence in
      the shipped spec's Open Questions
- [ ] Parking lot: cancellation on *local* long-running work — an in-process loop or batch job with no way
      to abandon it — is named explicitly by neither reviewer. Nobody is forbidden from raising it, so this
      is thinness rather than a hole, but the performance checklist is the natural home
- [ ] Parking lot: the quality reviewer's synchronous-blocking-call entry and the performance reviewer's
      async-correctness dimension are the next known domain overlap. Left open deliberately — each
      boundary wants evidence that the duplication actually reaches a reader

---

## Behaviors

Scenarios are grouped by Rule — the business rule the scenarios prove. Use concrete values and
business language. See the `bdd-principles` skill for guidance.

### Rule: A review reports an error passed onward with its origin no longer recorded

```scenario
Scenario: A handler that replaces an error and drops the original is reported
  Given a change whose handler catches a transport failure and throws a new "invoice unavailable" error
  And the transport failure is not carried inside the replacement and is not recorded anywhere else
  When the change is reviewed
  Then the review reports that where the failure started is no longer recorded
  And it names carrying the original as what would preserve it
```

```scenario
Scenario: The same rule applies where errors are returned rather than thrown
  Given a change whose function returns a new "could not load subscribers" error
  And the database error it received is discarded
  When the change is reviewed
  Then the review reports the lost origin
  And the wording of the finding does not assume that errors are thrown
```

```scenario
Scenario: A replacement that carries the original draws no finding
  Given a change that wraps a database error in a "loading subscribers for list 42" error
  And the wrapping keeps the original error inside it
  When the change is reviewed
  Then no finding is raised about a lost origin
```

```scenario
Scenario: A sanitized response to an external caller draws no finding
  Given a handler that returns a generic failure message to an external caller
  And the original error is recorded internally where the team can read it
  When the change is reviewed
  Then no finding is raised about a lost origin
```

### Rule: A review reports values folded into a log message instead of passed as fields

```scenario
Scenario: An interpolated message is reported, naming what can no longer be answered
  Given a change that logs an order number and a retry count inside one built-up message string
  When the change is reviewed
  Then the review reports that neither value can be filtered, grouped, or counted on afterwards
```

```scenario
Scenario: A message carrying no values draws no finding
  Given a change that logs the fixed message "Cache warm started"
  When the change is reviewed
  Then no finding is raised about how the message was built
```

```scenario
Scenario: A value that should not be logged at all is a different finding
  Given a change that logs a credential
  When the change is reviewed
  Then the review reports it as sensitive data being logged
  And the recommended fix is removing the value, not moving it into a named field
```

### Rule: Where two reviewers could claim one rule, the merged report shows it once

```scenario
Scenario: An uncancellable outbound call is reported once
  Given a change with a multi-minute outbound call that cannot be abandoned and has no time limit
  When all three reviewers review the change and their findings are merged
  Then the missing cancellation appears once in the ranked report
  And it is attributed to the performance reviewer
```

```scenario
Scenario: A reviewer working alone raises what it would otherwise leave to another
  Given the quality reviewer reviewing that same change on its own, with no other reviewer running
  When it reports its findings
  Then the missing cancellation is raised rather than withheld
```

```scenario
Scenario: Two different defects on one line are two findings
  Given that same outbound call, whose caller also catches the failure and continues
  When all three reviewers review the change and their findings are merged
  Then the swallowed failure is reported by the quality reviewer
  And the missing cancellation is reported by the performance reviewer
  And the report shows two findings rather than merging them into one
```

### Rule: A security finding names the category it belongs to

```scenario
Scenario: A visitor's search term reaching a data query is reported with its category
  Given a change whose handler passes a visitor's search term straight into a data query
  When the change is reviewed
  Then the review reports the defect
  And it names the security category the defect belongs to, by number and name
  And the category appears alongside the file and line the finding already carried
```

```scenario
Scenario: A committed secret keeps its rotation requirement and gains a category
  Given a change that commits a credential
  When the change is reviewed
  Then the review reports it as the most severe class of finding
  And it states that the credential must be treated as compromised and rotated, not merely removed
  And it names the security category, which displaces no part of the rotation requirement
```

### Rule: A finding that is not a security defect carries no category

```scenario
Scenario: An unclear helper name is reported with no category attached
  Given a change whose only defect is a helper named "doStuff"
  And the change contains no security defect anywhere
  When the change is reviewed
  Then the review reports the unclear name
  And the finding carries no security category
```

```scenario
Scenario: In one report, only the security finding is cited
  Given a change carrying both a data-query defect and several unrelated quality defects
  When the change is reviewed
  Then the data-query finding names its category
  And the unrelated findings name none
```

### Rule: A clean review names the security areas the change actually had code for

```scenario
Scenario: A validated contact form comes back with the areas it swept named
  Given a change adding a contact form that validates every submitted field
  And the form's insert passes its values as parameters, logs no submitted content, and stores no credential
  When the change is reviewed
  Then the review reports no security defect
  And it names the security areas it checked and found clean, by number and name
  And every area it names is one the change contains code for
```

```scenario
Scenario: An area the change has no code for is not named
  Given that same contact form change
  When the review names the areas it swept
  Then it names no area the change contains no code for
```

```scenario
Scenario: The two out-of-reach areas are never listed among those swept
  Given any change under review
  When the review names the security areas it swept
  Then it never lists the two areas a change-scoped review cannot reach
  And those two are a weakness in the design itself, and how old the dependency set has grown
```

---

## Edge Cases

### Rule: A handler that logs and continues yields one finding, not two

```scenario
Scenario: A swallowed failure is not also reported as a lost origin
  Given a change whose handler catches a publish failure, logs a warning, and continues the loop
  When the change is reviewed
  Then the review reports the swallowed failure
  And it does not additionally report a lost origin, because the failure never reaches the caller
```

### Rule: One line can carry both new defects at once

```scenario
Scenario: An error both replaced without its origin and logged as a built-up message
  Given a handler that discards the original error and logs the replacement inside one message string
  When the change is reviewed
  Then both are reported
  And that is correct, because they are two defects with two different fixes
```

### Rule: A change with nothing to check claims no security coverage

```scenario
Scenario: A rename gets no security line at all
  Given a change that only renames a local variable and reflows a comment
  And the change reads no input, and stores, logs, renders, and queries nothing
  When the change is reviewed
  Then the review names no security area
  And it makes no claim that the change was checked against the standard
```

```scenario
Scenario: Describing the change as having no security-relevant code is not a coverage claim
  Given that same rename
  When the review says the change contains no security-relevant code
  Then that is accurate, because it describes the change rather than claiming a sweep
```

```scenario
Scenario: A sweep of the whole standard is not claimed either
  Given that same rename
  When the change is reviewed
  Then the review does not state that the change was swept against the full range of categories
  And it does not state that no category applies to it
  And both would claim a sweep that never happened
```

---

## Test Coverage

There is **no automated harness for a review** in this project, so no scenario has a test file. Each was
instead proven by a manual check written down before the change and re-run after it, per the
`tdd-principles` skill's rule for a project with no harness. The captured before-and-after output is
committed alongside the increment, so each claim below is checkable rather than merely asserted.

| Scenario | Evidence | Status |
|----------|-----------|--------|
| A handler that replaces an error and drops the original is reported | `_work/shipped/review-failure-modes/assets/step1/` | Not covered — manual check recorded |
| The same rule applies where errors are returned rather than thrown | `_work/shipped/review-failure-modes/assets/step1/` | Not covered — manual check recorded |
| A replacement that carries the original draws no finding | `_work/shipped/review-failure-modes/assets/step1/` | Not covered — manual check recorded |
| A sanitized response to an external caller draws no finding | `_work/shipped/review-failure-modes/assets/step1/40-post-review-reverify.md` | Not covered — manual check recorded |
| An interpolated message is reported, naming what can no longer be answered | `_work/shipped/review-failure-modes/assets/step2/` | Not covered — manual check recorded |
| A message carrying no values draws no finding | `_work/shipped/review-failure-modes/assets/step2/` | Not covered — manual check recorded |
| A value that should not be logged at all is a different finding | — | Not covered |
| An uncancellable outbound call is reported once | `_work/shipped/review-failure-modes/assets/step3/` | Not covered — manual check recorded |
| A reviewer working alone raises what it would otherwise leave to another | — | Not covered |
| Two different defects on one line are two findings | `_work/shipped/review-failure-modes/assets/step3/` | Not covered — manual check recorded |
| A swallowed failure is not also reported as a lost origin | `_work/shipped/review-failure-modes/assets/step1/` | Not covered — manual check recorded |
| An error both replaced without its origin and logged as a built-up message | — | Not covered |
| A visitor's search term reaching a data query is reported with its category | `_work/shipped/owasp-security-review-rules/assets/step5-case-a-injection.md` | Not covered — manual check recorded |
| A committed secret keeps its rotation requirement and gains a category | `_work/shipped/owasp-security-review-rules/assets/step5-validation-log.md` | Not covered — probe only, no planted case |
| An unclear helper name is reported with no category attached | `_work/shipped/owasp-security-review-rules/assets/step5-case-b-naming-only.md` | Not covered — manual check recorded |
| In one report, only the security finding is cited | `_work/shipped/owasp-security-review-rules/assets/step5-case-a-injection.md` | Not covered — manual check recorded |
| A validated contact form comes back with the areas it swept named | `_work/shipped/owasp-security-review-rules/assets/step6-case-c-clean-with-security-code.md` | Not covered — manual check recorded |
| An area the change has no code for is not named | `_work/shipped/owasp-security-review-rules/assets/step6-case-c-clean-with-security-code.md` | Not covered — manual check recorded |
| The two out-of-reach areas are never listed among those swept | `_work/shipped/owasp-security-review-rules/assets/step6-case-c-clean-with-security-code.md` | Not covered — one change only |
| A rename gets no security line at all | `_work/shipped/owasp-security-review-rules/assets/step6-case-d-no-security-code.md` | Not covered — manual check recorded |
| Describing the change as having no security-relevant code is not a coverage claim | `_work/shipped/owasp-security-review-rules/assets/step6-case-d-no-security-code.md` | Not covered — manual check recorded |
| A sweep of the whole standard is not claimed either | `_work/shipped/owasp-security-review-rules/assets/step6-case-d-no-security-code.md` | Not covered — manual check recorded |

<!-- Covered: a test asserts it. Not covered: specified, untested. Not covered (code-derived):
     inferred from reading the code, never specified and never tested — the weakest claim here.
     Keeping the third distinct is what lets a reader tell verified behavior from inferred. -->

**Nothing here is `Covered`, and that is accurate rather than pessimistic.** A recorded manual check is
real evidence and better than an untested claim, but it is not a test: it does not re-run, so it cannot
catch a later regression. Three scenarios from the first increment have no evidence at all and are marked
plainly — two were derived from the wording of the rules rather than exercised, and the standalone-reviewer
scenario describes behavior the boundary statement introduced and which no run has exercised yet.

Two security rows carry a weaker qualifier than the rest, and the difference is deliberate. **The
committed-secret scenario was never planted**: the rule was confirmed by asking a dispatched reviewer to
quote its own instruction back, which proves the instruction is present and intact but not that a real
committed secret draws the finding. **The out-of-reach scenario was exercised against one change**, which
is enough to show the two areas were not listed and not enough to call it general. Both are honest gaps
rather than oversights, and both are cheap to close with a planted case when someone next touches this.

---

## Revision Notes

- 2026-08-13: Created at area level from `_work/shipped/review-failure-modes/spec.md`. Thin by design — records
  only this increment's behavior, with the rest of the capability flagged for from-code backfill.
- 2026-08-13: The plan directed that the cancellation-ownership statement not be recorded as a Rule, on
  the grounds that nothing observable changed. Recorded anyway, and the reasoning is worth keeping: a
  capability doc describes what the capability *does*, not what a change *altered*, and "the merged report
  shows one defect once" is standing behavior a reader can exercise. It is not transition-shaped, which is
  what that instruction was guarding against. The point-in-time criteria — that the gate passes, that the
  induced-RED edit was reverted — stay in the shipped spec and appear in no Rule here.
- 2026-08-13: The manual-check evidence was moved out of a temporary scratch directory into
  `_work/shipped/review-failure-modes/assets/` so the coverage table cites something that survives. It archives
  with the increment bundle.
- 2026-09-08: Folded in `owasp-security-review-rules`. Only observable behavior was taken: a security
  finding names its category, a non-security finding names none, a clean review names the areas it swept,
  and a change with nothing to check claims nothing. The increment's point-in-time criteria — the five
  registration gates, the two new contract checks, the roster and README entries, and the reviewer count
  staying three — stay in the shipped spec and appear in no Rule here.
- 2026-09-08: The increment was archived to `_work/shipped/owasp-security-review-rules/` in the same
  change, so every evidence path in the coverage table above resolves. Archiving also re-depthed the
  bundle's own links: five markdown links to `../../adr/` gained a level, and the plan's self-references
  now name the shipped path, matching what the previous increment did. The two `../../skills/...` strings
  in the plan were deliberately left alone — they document a symlink's target, which is relative to
  `.claude/skills/` and not to the file quoting it.
