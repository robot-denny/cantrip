# Feature: Test Coverage

A developer or QA engineer can ask what a capability claims to do that nothing proves, and get back a
ranked account of the gap rather than a guess. Where a scenario can be proved, the missing test is
written and run on approval and the capability's own doc records what the run established; where it
cannot, the reason is named — a missing piece of test infrastructure, or a deliberate decision that
the scenario is not testable here. A project-wide report reads the same docs and names drift in both
directions: scenarios nothing proves, and tests whose scenarios have since changed or gone.

**Source**: `_work/testify/spec.md`
**Last verified**: 2026-09-01

> **Draft** — These scenarios have not yet been verified against an implementation. They will be
> refined during planning and verified after implementation.

---

## Increments

The per-feature mini-roadmap: shipped increments, planned increments, and parking-lot ideas.
Newest planned items first. When an item ships, flip the checkbox and point it at the archived
increment.

- [ ] The `/testify` spell: a coverage gap report, approval-gated test authoring against a capability
      doc, a project-wide audit that names drift in both directions, and two new coverage statuses
      (`_work/testify/spec.md`, planned in `_work/testify/plan.md`)
- [ ] Parking lot: splitting the Status column in two. Five statuses encode two independent facts in
      one cell — whether a test exists, and what its last run established. Deferred because it
      rewrites every existing coverage table
- [ ] Parking lot: nothing re-runs a failing test, so a `Test failing` row understates what is proved
      once the work landing behind it ships
- [ ] Parking lot: an expiry story for a `Ruled out` reason. A reason stops being true when
      something changes, and nothing in the current design re-reads it
- [ ] Parking lot: coverage for work that earned no capability doc. A `change-to` or `fix-infra`
      increment can ship real behavior with no scenarios of its own, which makes it invisible here

---

## Behaviors

Scenarios are grouped by Rule — the business rule the scenarios prove. Use concrete values and
business language. See the `bdd-principles` skill for guidance.
### Rule: A developer names a capability and gets back a report of which of its scenarios nothing proves, before any file is written

```scenario
Scenario: A capability with three unproved scenarios is reported before anything is written
  Given the "Article Card" capability doc lists eight scenarios
  And five of them name a test that proves them
  When a developer asks for the article card's missing tests
  Then the report lists the three scenarios nothing proves
  And it does not list the five that are already proved
  And no test file has been created or changed
```

```scenario
Scenario: A capability whose scenarios are all proved reports nothing to do
  Given every scenario in the "Site Search" capability doc names a test that proves it
  When a developer asks for site search's missing tests
  Then the report says every scenario is already proved
  And no work is proposed
```

```scenario
Scenario: The name given is an increment rather than a capability
  Given the project has a capability doc named "Article Card"
  And it has no capability doc named "Placeholder Graphics For Imageless Cards"
  When a developer asks for the missing tests for "placeholder graphics for imageless cards"
  Then the report says no capability of that name is documented
  And it offers "Article Card" as the closest documented capability
  And no test file has been created or changed
```

### Rule: The report separates scenarios that can be tested now from those blocked on missing test infrastructure, and names what each blocked one needs

```scenario
Scenario: One scenario needs a browser the project cannot drive
  Given the "Article Card" capability doc has two unproved scenarios
  And one of them describes what a visitor sees on screen
  And the project has no way to drive a browser
  When a developer asks for the article card's missing tests
  Then the scenario about what a visitor sees is reported as blocked
  And the report names driving a browser as what that scenario needs
  And the other scenario is reported as writable now
```

```scenario
Scenario: A blocked scenario sends the developer to write a spec
  Given every unproved scenario in the "Article Card" capability doc is blocked on missing test infrastructure
  When a developer asks for the article card's missing tests
  Then the report names what the missing infrastructure is
  And it points the developer at writing a spec for that infrastructure
  And no test file has been created or changed
```

### Rule: Scenarios inferred from code rather than specified are reported separately, with the warning that proving one turns an inference into a contract

```scenario
Scenario: An inferred scenario is offered apart from the specified ones
  Given the "Article Card" capability doc has one unproved scenario that was specified
  And it has one unproved scenario that was inferred by reading the code
  When a developer asks for the article card's missing tests
  Then the specified scenario and the inferred scenario are reported in separate groups
  And the inferred group says that proving one of these makes a reading of the code binding
```

### Rule: A scenario too vague to name a specific observable outcome produces a question for its author rather than a test

```scenario
Scenario: A scenario naming no observable outcome is returned as a question
  Given the "Article Card" capability doc contains the scenario "A card looks right on mobile"
  When a developer asks for the article card's missing tests
  Then that scenario is reported as a question for whoever wrote the doc
  And the report says it names nothing that can be compared
  And no test is proposed for it
```

### Rule: No test file is created or changed until the developer approves that specific scenario

```scenario
Scenario: A developer approves one scenario and declines another
  Given the report offers tests for "A card with no image shows a placeholder" and "A card truncates a long title"
  When the developer approves only "A card with no image shows a placeholder"
  Then a test is written for the card with no image
  And no test is written for the truncated title
  And the truncated title is still listed as unproved
```

### Rule: A scenario's row records what its test's last run established, whether or not the doc is still a draft

```scenario
Scenario: A test that passes marks its scenario proved
  Given a developer has approved a test for "A card with no image shows a placeholder"
  When the test is written and run and it passes
  Then the capability doc records that scenario as proved
  And it names the test that proves it
```

```scenario
Scenario: A test that fails is recorded as failing, not as absent
  Given a developer has approved a test for "A card truncates a long title"
  When the test is written and run and it fails
  Then the capability doc records that scenario as having a failing test
  And it names the test that is failing
```

```scenario
Scenario: Half a half-built capability passes and the rest fails
  Given the "Article Card" capability doc is still marked as a draft
  And four of its six scenarios have been built and two have not
  When a developer asks for the article card's missing tests and approves all six
  Then the four built scenarios are recorded as proved
  And the two unbuilt scenarios are recorded as having failing tests
  And none of the four passing tests is reported as proving nothing
```

```scenario
Scenario: A test that cannot be run leaves the scenario unproved
  Given a developer has approved a test for "A card with no image shows a placeholder"
  And the way to run tests is not recorded and cannot be worked out
  When the test is written
  Then the capability doc still records that scenario as unproved
  And the report says the test was written but never run
```

### Rule: A failing test is explained as expected of work in flight when the doc is still a draft, and as the doc disagreeing with the code when it is not

```scenario
Scenario: A failure against a draft doc is explained as work still to come
  Given the "Article Card" capability doc is still marked as a draft
  And a test for "A card truncates a long title" has been written and has failed
  When the developer reads the report
  Then it says the failure is expected of a capability still being built
  And it does not say the capability is broken
```

```scenario
Scenario: The same failure against a verified doc is explained as a disagreement
  Given the "Article Card" capability doc is no longer marked as a draft
  And a test for "A card truncates a long title" has been written and has failed
  When the developer reads the report
  Then it says the capability does not behave the way its doc claims
  And it says either the code or the doc is wrong
```

### Rule: Each proposed test is reported alongside the specific ways it could have passed while the behavior was broken, and a verified-doc report states that no red-to-green signal is available

```scenario
Scenario: A proposed test is reported with the ways it could have passed while broken
  Given the report offers a test for "A card with no image shows a placeholder"
  When the developer reads the report
  Then it says the test would fail if the placeholder text were wrong
  And it says the test would fail if the card were rendered on a different page
  And it says the test would fail on an empty page
  And it says the expected placeholder text was taken from the scenario rather than from the code
```

### Rule: Every test the spell writes records which capability doc and which scenarios it came from

```scenario
Scenario: A written test names its source doc and scenarios
  Given a developer has approved tests for two of the article card's scenarios
  When the tests are written
  Then the test file opens with a note naming the "Article Card" capability doc
  And the note lists both scenario names
  And the note carries the date the tests were written
  And the note is written the way comments are written in the project's other tests
```

### Rule: A scenario the project has decided cannot be tested carries that decision and its reason in the coverage table, and is never proposed again

```scenario
Scenario: A scenario the project cannot test is recorded with its reason and skipped
  Given the "Design Tokens" capability doc records "A showcase reports a token it cannot resolve" as not coverable
  And the recorded reason is that this toolkit ships no rendering layer
  When a developer asks for design tokens' missing tests
  Then that scenario is not offered
  And the report says one scenario is recorded as not coverable and gives the recorded reason
```

### Rule: Where proving a scenario would require establishing a testing convention the project does not have, the spell declines to establish it and routes that work to a spec

```scenario
Scenario: A project with no tests at all is told to decide its convention deliberately
  Given the "Article Card" capability doc lists four unproved scenarios
  And the project has no tests and no recorded place to put them
  When a developer asks for the article card's missing tests
  Then the report says where tests go has never been decided here
  And it declines to decide it
  And it points the developer at writing a spec for the project's testing setup
  And no test file has been created or changed
```

### Rule: A developer can ask for a project-wide report that writes nothing and names coverage drift in both directions

```scenario
Scenario: A project-wide report ranks capabilities by how much is unproved
  Given the project documents four capabilities
  And "Article Card" has three unproved scenarios and "Site Search" has none
  When a developer asks for a project-wide coverage report
  Then the report covers all four capabilities
  And "Article Card" appears above "Site Search"
  And no test file has been created or changed
  And no test is run
  And the developer is not asked to approve anything
```

```scenario
Scenario: A test whose scenario has been reworded is reported as stale
  Given a test names the article card scenario "A card with no image shows a placeholder"
  And that scenario has since been reworded to "A card with no image shows the house silhouette"
  When a developer asks for a project-wide coverage report
  Then the report says that test is stale
  And it shows the scenario as it was written and as it reads now
  And the test is not changed
```

```scenario
Scenario: A test whose scenario has been deleted is reported as orphaned
  Given a test names the article card scenario "A card shows a byline"
  And that scenario has been removed from the article card's doc
  When a developer asks for a project-wide coverage report
  Then the report says that test is orphaned
  And it asks whether the behavior is still expected
  And the test is not deleted
```

```scenario
Scenario: A row claiming proof whose test has gone is reported
  Given the article card's doc records "A card truncates a long title" as proved by a named test
  And that test no longer exists
  When a developer asks for a project-wide coverage report
  Then the report says the doc claims proof that nothing provides
  And that scenario is counted as unproved
```

```scenario
Scenario: A project-wide report in a project with no capability docs says so
  Given the project documents no capabilities
  When a developer asks for a project-wide coverage report
  Then the report says no capability is documented
  And it names writing the first capability doc as the thing that has to happen first
```

### Rule: Behavior the spell notices that no scenario describes is named and handed to /feature, never written into the doc by this spell

```scenario
Scenario: Undocumented behavior found while writing a test is handed on
  Given a developer has approved a test for "A card with no image shows a placeholder"
  And the card also shortens a long title, which no scenario describes
  When the test is written
  Then the report says the card does something no scenario describes
  And it points the developer at documenting it
  And no scenario has been added to the capability doc
```

### Rule: The spell works in a project with no stack pack installed, and says what it could not determine rather than guessing

```scenario
Scenario: A project with tests but no stack pack still gets a report
  Given the project has tests but no stack pack is installed
  When a developer asks for a capability's missing tests
  Then the report lists the unproved scenarios
  And the proposed tests follow the conventions of the tests the project already has
  And the report names the existing tests it took those conventions from
```

```scenario
Scenario: What could not be determined is stated rather than invented
  Given the project has tests but no recorded way to run them
  And the way to run them cannot be worked out from the project
  When a developer asks for a capability's missing tests
  Then the report says the way to run tests could not be determined
  And it does not invent one
```

---

## Edge Cases

Behavior at the boundaries is drafted above rather than separated out — the empty capability doc, the
vague scenario, the half-built increment, the project with no tests, and the test that disagrees with
its doc each prove a rule of their own and are grouped with it. This section is deliberately empty for
now; planning may lift some of the spec's *Possible Edge Cases* here once their behavior is settled,
in particular:

- A test left failing long after the work that would make it pass landed, because nothing re-ran it
- One test proving scenarios in two different capability docs, or in a doc that has since been split

---

## Test Coverage

| Scenario | Test File | Status |
|----------|-----------|--------|
| A capability with three unproved scenarios is reported before anything is written | — | Not covered |
| A capability whose scenarios are all proved reports nothing to do | — | Not covered |
| The name given is an increment rather than a capability | — | Not covered |
| One scenario needs a browser the project cannot drive | — | Not covered |
| A blocked scenario sends the developer to write a spec | — | Not covered |
| An inferred scenario is offered apart from the specified ones | — | Not covered |
| A scenario naming no observable outcome is returned as a question | — | Not covered |
| A developer approves one scenario and declines another | — | Not covered |
| A test that passes marks its scenario proved | — | Not covered |
| A test that fails is recorded as failing, not as absent | — | Not covered |
| Half a half-built capability passes and the rest fails | — | Not covered |
| A test that cannot be run leaves the scenario unproved | — | Not covered |
| A failure against a draft doc is explained as work still to come | — | Not covered |
| The same failure against a verified doc is explained as a disagreement | — | Not covered |
| A proposed test is reported with the ways it could have passed while broken | — | Not covered |
| A written test names its source doc and scenarios | — | Not covered |
| A scenario the project cannot test is recorded with its reason and skipped | — | Not covered |
| A project with no tests at all is told to decide its convention deliberately | — | Not covered |
| A project-wide report ranks capabilities by how much is unproved | — | Not covered |
| A test whose scenario has been reworded is reported as stale | — | Not covered |
| A test whose scenario has been deleted is reported as orphaned | — | Not covered |
| A row claiming proof whose test has gone is reported | — | Not covered |
| A project-wide report in a project with no capability docs says so | — | Not covered |
| Undocumented behavior found while writing a test is handed on | — | Not covered |
| A project with tests but no stack pack still gets a report | — | Not covered |
| What could not be determined is stated rather than invented | — | Not covered |

<!-- Status vocabulary, per templates/feature.md, which is the authority.

     Four record an observation — what was seen, or that nothing was:
     Covered (a test asserts it and its last run passed); Test failing (a test asserts it and its
     last run did not pass, named for the observation rather than its cause); Not covered
     (specified, nothing asserts it); Not covered (code-derived) (inferred from reading the code,
     never specified and never tested, the weakest claim here).

     One records a decision, and is set apart because its name begins like two of theirs and means
     the opposite: Ruled out — <reason> (the project decided this cannot be proved here). -->

Every row is uncovered because nothing has been built yet. This doc would be the first thing
`/testify` is pointed at once it exists — useful dogfooding, and an equally useful trap: several of
these scenarios describe judgment a reader makes about a report's prose, and the spec's *Testing
Guidelines* already rules those out of harness scope.

---

## Revision Notes

- 2026-09-01: Draft scenarios from initial spec
