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
| {scenario name} | — | Not covered |

---

## Revision Notes

- {date}: Initial feature doc from spec + implementation
- {date}: Updated after {change description}
