# Feature: {Feature Name}

{2-3 sentence summary from the user's perspective. No implementation details. Use ubiquitous
language — business terms ("content editor", "visitor", "page"), not technical terms ("document
type", "controller", "API endpoint").}

**Source**: `_work/{slug}/spec.md`
**Last verified**: {date}

---

## Increments

The per-feature mini-roadmap: shipped increments, planned increments, and parking-lot ideas.
Newest planned items first. When an item ships, flip the checkbox and point it at the archived
increment.

- [x] {YYYY-MM-DD} — {shipped increment name} (`_work/shipped/{slug}/spec.md`)
- [ ] {planned increment} (`_work/{slug}/spec.md`, no plan yet)
- [ ] {parking lot idea} (no spec yet)

---

## Behaviors

Scenarios are grouped by Rule — the business rule or acceptance criterion the scenarios prove.
Use concrete values (Specification by Example) and business language (Ubiquitous Language). See
the `bdd-principles` skill for guidance.

### Rule: {Business rule in plain language}

```scenario
Scenario: {Descriptive name using concrete examples}
  Given {specific precondition with concrete values}
  When {user action}
  Then {observable outcome}
```

```scenario
Scenario: {Another scenario proving the same rule}
  Given {different precondition}
  When {action}
  Then {outcome}
```

### Rule: {Another business rule}

```scenario
Scenario: {name}
  Given {precondition}
  When {action}
  Then {outcome}
```

---

## Edge Cases

### Rule: {Boundary condition or unusual situation}

```scenario
Scenario: {Edge case name}
  Given {unusual precondition}
  When {action}
  Then {graceful outcome}
```

---

## Test Coverage

| Scenario | Test File | Status |
|----------|-----------|--------|
| {scenario name} | `{test file}:L42` | Covered |
| {scenario name} | `{test file}:L58` | Test failing |
| {scenario name} | — | Not covered |
| {scenario name} | — | Not covered (code-derived) |
| {scenario name} | — | Not coverable — {why it cannot be proved here} |

<!-- Status vocabulary. Each status is a claim about what is proved, not a stage in a process:
     read a row as its answer to "what does this entitle me to believe?"

     FOUR STATUSES RECORD AN OBSERVATION — what was seen, or that nothing was:

     - Covered: a test asserts this scenario, and its last run passed.
     - Test failing: a test asserts this scenario, and its last run did not pass. Named for what was
       observed rather than for its cause, because the cause may be behavior not built yet, a
       regression, or a doc that is simply wrong, and the row cannot tell those apart. Whatever
       reported the run is where the cause gets argued.
     - Not covered: the scenario is specified, and nothing asserts it.
     - Not covered (code-derived): the rule was inferred by reading the code — never specified and
       never tested, and so the weakest claim in this table.

     ONE STATUS RECORDS A DECISION, and it is the only one a person writes deliberately:

     - Not coverable — <reason>: the project has decided this scenario cannot be proved here, and
       the reason travels in the row so a later reader can judge whether it still holds.

     The split is the point, and it is why this status is set apart rather than listed fourth among
     three others whose names also begin "Not cover". The four above say what happened. This one says
     somebody chose — which is the difference between a gap nobody has got to yet and a gap the
     project decided to live with, and it is the easiest distinction in the table to lose while
     scanning. Read the whole of "Not coverable —" before concluding a row is an ordinary gap. -->

---

## Revision Notes

- {date}: Initial feature doc from spec + implementation
- {date}: Updated after {change description}
