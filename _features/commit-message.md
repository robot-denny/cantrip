# Feature: Commit Message

A developer casts `/commit-message` to get a proposed commit for their current work. The spell
decides which changed files belong in the commit, proposes a message that says what shipped before
it says why, and stages and commits only when the developer approves. It follows the project's own
commit conventions rather than imposing one.

**Source**: `_work/shipped/commit-message-stage-by-default/spec.md` for the staging rules; the message-shape
and convention rules are derived from `skills/core/spellbook/commit-message/SKILL.md` (2026-11-04)
with no originating spec
**Last verified**: 2026-11-04

---

## Increments

The per-feature mini-roadmap: shipped increments, planned increments, and parking-lot ideas.
Newest planned items first. When an item ships, flip the checkbox and point it at the archived
increment.

- [ ] Verify the code-derived message-shape and convention rules below with real casts
- [x] 2026-11-04 — Stage related files by default (`_work/shipped/commit-message-stage-by-default/spec.md`)

---

## Behaviors

Scenarios are grouped by Rule — the business rule or acceptance criterion the scenarios prove.
Use concrete values (Specification by Example) and business language (Ubiquitous Language). See
the `bdd-principles` skill for guidance.

### Rule: Changes the developer has not staged are still considered

```scenario
Scenario: Nothing staged, one edited file
  Given the developer has edited "README.md" and staged nothing
  When the developer casts /commit-message
  Then the spell does not stop
  And it proposes committing "README.md" with a message
```

```scenario
Scenario: A brand-new file is judged by what it says
  Given "docs/notes.md" is a new file holding a short note on release tagging
  And nothing else has changed
  When the developer casts /commit-message
  Then the proposal lists "docs/notes.md" as a file to add
  And the message describes release tagging, not merely that a file was added
```

### Rule: Which files belong is the agent's judgment, and the proposal shows it

```scenario
Scenario: A spell edit and its changelog entry
  Given the developer has staged an edit to the commit-message spell
  And has an unstaged "CHANGELOG.md" entry describing that same edit
  When the developer casts /commit-message
  Then the proposal lists "CHANGELOG.md" as a file to add
  And when the developer approves, both files land in one commit
```

### Rule: Nothing is staged or committed until the developer approves

```scenario
Scenario: Developer declines the proposal
  Given the developer has an unstaged edit to "CHANGELOG.md"
  And the spell has proposed committing it
  When the developer declines
  Then no commit is made
  And "CHANGELOG.md" is still unstaged
```

```scenario
Scenario: Developer approves the proposal
  Given the spell has proposed committing "CHANGELOG.md" and "docs/spell-cards.md"
  When the developer approves
  Then exactly those two files are staged and committed together
  And no other changed file is added to the commit
```

### Rule: A developer can limit the commit to what is already staged

```scenario
Scenario: Opting out in plain language
  Given the developer has staged "CHANGELOG.md"
  And has an unstaged edit to "README.md"
  When the developer casts /commit-message and says "just what's staged"
  Then the proposal covers "CHANGELOG.md" only
  And "README.md" stays unstaged
```

### Rule: The message says what shipped before it says why

*Derived from the spell's text; not yet verified by a cast written for it.*

```scenario
Scenario: First sentence stands alone
  Given the developer has moved retry helpers out of the queue module
  When the developer casts /commit-message
  Then the first sentence of the body says the retry helpers moved into their own module
  And it needs no diff to be understood
  And the reasoning follows in a short paragraph
  And the body stays under about 150 words
```

### Rule: The message follows the project's own conventions

*Derived from the spell's text; not yet verified by a cast written for it.*

```scenario
Scenario: A configured format wins over history
  Given the project's configuration says commits use a "type: subject" prefix
  And its last 30 commits use plain subjects with no prefix
  When the developer casts /commit-message
  Then the proposed subject uses the "type: subject" prefix
```

```scenario
Scenario: Matching the history's form
  Given the project's last 30 commits use plain imperative subjects with no type prefix
  When the developer casts /commit-message
  Then the proposed subject is a plain imperative line with no type prefix
```

```scenario
Scenario: Trailers only where the project uses them
  Given the project's history ends commits with a co-author trailer
  When the developer casts /commit-message
  Then the proposed message ends with that trailer after a blank line
```

```scenario
Scenario: No trailer convention to follow
  Given no commit in the project's history carries a trailer
  When the developer casts /commit-message
  Then the proposed message carries no trailer
```

---

## Edge Cases

### Rule: With nothing to commit, the spell stops

```scenario
Scenario: A clean working tree
  Given the developer has no staged, unstaged, or new files
  When the developer casts /commit-message
  Then the spell says there is nothing to commit
  And it proposes no message
```

### Rule: Extra words that do not change the request are ignored

```scenario
Scenario: Casting with "staging any files necessary"
  Given the developer has edited "README.md" and staged nothing
  When the developer casts /commit-message staging any files necessary
  Then the outcome is the same as casting /commit-message with no words added
```

---

## Test Coverage

This repository ships no test harness for spells. The staging scenarios were walked against the
spell by a stand-in in `_work/shipped/commit-message-stage-by-default/assets/step1-validation-log.md`, which
reads the spell and follows it; a walk-through is not a test, so those rows stay `Not covered`.
Three real casts on 2026-11-04 are recorded under **Real casts** in the same log. Between them they
exercised "Nothing staged", "A brand-new file is judged by what it says", "Developer declines" and
"Developer approves" (commits `16de057` and `a092f1a`). The developer later verified "Opting out in
plain language", an unrelated file being left out, and staging without a permission prompt by hand.
A cast is not a test either, so those rows also stay `Not covered`. Rows marked code-derived were read from the spell's text and never
specified.

| Scenario | Test File | Status |
|----------|-----------|--------|
| Nothing staged, one edited file | — | Not covered |
| A brand-new file is judged by what it says | — | Not covered |
| A spell edit and its changelog entry | — | Not covered |
| Developer declines the proposal | — | Not covered |
| Developer approves the proposal | — | Not covered |
| Opting out in plain language | — | Not covered |
| First sentence stands alone | — | Not covered (code-derived) |
| A configured format wins over history | — | Not covered (code-derived) |
| Matching the history's form | — | Not covered (code-derived) |
| Trailers only where the project uses them | — | Not covered (code-derived) |
| No trailer convention to follow | — | Not covered (code-derived) |
| A clean working tree | — | Not covered |
| Casting with "staging any files necessary" | — | Not covered |

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

     - Ruled out — <reason>: the project has decided this scenario cannot be proved here, and
       the reason travels in the row so a later reader can judge whether it still holds. -->

---

## Revision Notes

- 2026-11-04: Initial feature doc. Staging rules from the `commit-message-stage-by-default` spec and
  implementation; message-shape and convention rules backfilled from the spell's text and marked
  code-derived.
