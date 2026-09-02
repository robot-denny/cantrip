# Spec for testify

> This spec captures initial requirements and design rationale. For **current system
> behavior**, see the doc named on the **Work type** line below — a new feature doc for a new
> capability, an existing feature doc for a change, or a `docs/` runbook for a fix.

branch: robot-denny/feature/testify
design reference (if any): prior art only, contributing shape and no content — see *Design Reference* below

**Work type**: new-capability
**Feature doc**: test-coverage

## Summary

`/testify` is the toolkit's ninth workflow spell and its **first QA-owned verb**. Every other spell
in the chain either decides what to build or builds it; this one asks a different question — *what
does the project claim to do that nothing proves?*

Its contract is already written down. A capability doc ends with a **Test Coverage** table mapping
each scenario to the test that proves it and a status. Today that table is filled in by hand at the
end of `/plan` and drifts from there. `/testify` reads it as a work queue: report which scenarios are
unproved, write tests for the ones that can be written, run them, and record the result back in the
table. Its audit mode reads the same tables across the whole project and reports where doc and tests
have drifted apart in either direction.

That makes it a **pair with `/feature`** over the same living document rather than a new stage in the
`spec → plan → implement` chain. `/feature` owns what the capability does; `/testify` owns whether
anything proves it. Decided 2026-08-25 and recorded in `ROADMAP.md` → *Next*: a separate spell rather
than a mode on `/feature`, so the two share no machinery.

Two things the spell deliberately does **not** own. It holds no knowledge of any test library — that
is a stack pack's job, and this increment ships no pack changes. And it never establishes a project's
testing architecture: where a scenario needs a harness the project does not have, it says so and
stops rather than inventing one.

## Functional Requirements

**Two modes, one input shape.**

- `/testify <capability>` — the write path. Reads that capability's doc, reports the gap, then writes
  and runs on approval.
- `/testify audit` — the read-only path. Sweeps every capability doc and reports project-wide
  coverage and drift. Writes nothing, runs no test, touches no test file, and offers no approval
  prompt.

**The capability doc is the only source of what is unproved.** The spell reads `_features/<area>.md`
and works from its Test Coverage rows. Behavior that was never written as a scenario is invisible to
it. Where the spell notices such behavior in passing — reading code to write a test — it names it and
points at `/feature`, whose from-code mode already owns documenting it. It never writes a scenario of
its own.

**Report first, always.** Even in write mode the first output is a gap report, grouping the unproved
rows into three sets because each needs a different decision from the reader:

1. **Writable now** — the project has everything the test needs.
2. **Blocked on infrastructure** — no runner, fixture, or harness exists for that layer, naming what
   each row needs.
3. **Inferred, not specified** — rows marked `Not covered (code-derived)`, kept separate because
   proving one promotes a reading of the code into a contract the project never agreed to.

**Nothing is written before approval.** Same posture as `/guide` and `/styleguide`: propose, then
write only what the reader confirms, row by row.

**A vague scenario halts rather than producing a guess.** Where a scenario names no specific
observable outcome — no value to compare, nothing that distinguishes present from absent — the spell
reports it as a question for the doc's author and writes no test for it. A guessed assertion is worse
than an empty row, because it fills one.

**A test's result is recorded as observed, and never second-guessed from the doc's state.** A draft
capability doc is not a doc for unbuilt behavior. `/plan` phases its work and `/implement-step` runs
one step at a time, so a partly-built increment with some scenarios genuinely passing is the **normal
middle state of the flow**, not an edge case. The spell runs the test, records what happened, and
leaves the interpretation to the reader.

**The Draft banner frames the report; it does not fork the behavior.** Where the doc is still a
draft, a failing test is explained as expected of work in flight. Where the banner is gone, the same
failure is explained as the doc and the code disagreeing. Same observation, same status, different
sentence.

**No red-to-green signal is available for behavior that already works**, and the spell says so rather
than implying a proof it did not perform. Guarding against a test that passes *vacuously* is the job
of the assertion probes below, which run on every path — a test that would pass against an empty page
is caught there whether or not the doc is a draft. A mode that demanded a red run from a draft doc
would be a weaker, narrower duplicate of that check, and would misreport every legitimately-passing
test in a half-built increment.

**Assertion review stands in for the missing signal, with named probes.** For each proposed test the
spell reports the specific ways it could have passed while the behavior was broken — the value could
be wrong, the thing could be rendering somewhere else entirely, the page could be blank, the check
could be satisfied by the artifact merely existing — alongside the `tdd-principles` failure modes:
presence assertions, expected values derived the way the implementation derives them, coupling to
artifacts rather than to observable behavior.

**Every test the spell writes records where it came from.** A comment at the head of the file naming
the capability doc, the scenarios the file covers, and the date. **Core requires the header and its
content; the comment syntax belongs to the pack or to the project**, inferred from tests that already
exist. This makes the doc-to-test link bidirectional, which is what lets drift be detected rather than
guessed at by matching scenario names — the match that breaks precisely when a scenario is reworded,
which is when it is most needed.

**A row's status distinguishes what a test's result actually establishes.** The table gains two
statuses beside `Covered`, `Not covered`, and `Not covered (code-derived)`:

- **`Test failing`** — a test exists and its last run did not pass. Names the test file.
  **Deliberately named for the observation rather than its cause**, because the cause differs — not
  built yet, a regression, or a doc that is simply wrong — and the spell is not positioned to tell
  those apart. The Draft banner and the report are what the reader interprets it with.
- **`Ruled out — <reason>`** — the project has decided this scenario cannot be tested here.
  `/testify` skips these and never re-proposes them; the reason travels in the row so a reader can
  judge whether it still holds.

Both ripple into `templates/feature.md`, and into `/feature` and `/spec`, which write the table.

**Audit mode reports drift in both directions.** Four kinds, every one of them answered by reading:

1. A scenario no test proves.
2. A test whose scenario has since changed — **stale**; the row still claims proof of something
   nobody specified any more.
3. A test whose scenario has been deleted — **orphaned**.
4. A row claiming `Covered` whose named test no longer exists at all.

**Audit mode runs no test, and item 4 is deliberately the weaker half of the check it could have
been.** Learning that a `Covered` row's test *currently fails* would mean running it, and a sweep
that quietly executed a project's suite would be neither cheap nor read-only. It would also not be
safe: where a project's tests create and delete real content to exercise it, an audit would mutate
the very thing it claims to be reporting on, and "writes nothing" would be false in the way a user
would most object to. So the sweep asks only whether the named test still exists. Whether a row that
still names a live test is telling the truth is left to the next real run — see *Open Questions*.

**Stack knowledge comes from a pack or from the project, never from the spell.** The spell is L0. It
reads the `stack.md` → `## Tests` slot for where tests live and `## Build` for how to run them,
defers library idiom to whatever pack is installed, and degrades gracefully when neither is present.

**A blocked row is spec-sized work.** Where proving a scenario needs infrastructure that does not
exist, the spell names what is needed and ends pointing at `/spec`. It does not establish a testing
convention by accident — the same reasoning `/block` uses when a greenfield project has no exemplar
block to copy.

**Spell budget.** This takes the core workflow spellbook from eight to nine, leaving one under
[ADR 0010](../../adr/0010-skills-not-commands.md)'s ceiling of ten. Like every spell it sets
`disable-model-invocation: true` and chains by suggestion only.

## Design Reference (only if one exists)

Two existing bodies of work were read for shape. **Neither contributes any content**, and every
stack-specific fact in both — runner names, directory layouts, library quirks, commands, assembly and
project names — is L2 or pack material appearing nowhere in this spell.

- **The demo project's testing documentation.** Contributed the three-family test taxonomy, the
  cheapest-test-that-proves-it rubric, and the observation that a capability doc's coverage table is
  the bridge between what product wants and what is verified. Its rubric maps a *kind of change* to a
  *kind of test*; `/testify` cannot carry that table because the kinds are stack-specific, so it
  carries the principle and asks the pack or the project for the kinds.
- **A test-generation skill from the client project.** Contributed three shapes:
  concrete probes for a test that would pass while the feature is broken; marking a test stale when
  its scenario changed and orphaned when it was deleted; and a provenance header linking a test file
  back to the scenarios it covers. It also halts on a scenario too vague to yield an assertion rather
  than guessing one.

  **Its TDD-versus-code-first mode was taken up and then rejected.** That skill decides from a git
  diff that nothing is built yet and wraps every generated test in an expect-to-fail marker, which is
  sound for its trigger — a spec file changed and nothing else did. It is unsound for this one: a
  capability doc covers an increment `/implement-step` builds one step at a time, so demanding a red
  run from every scenario would misreport the majority that legitimately pass partway through. The
  vacuity probes already catch what that mode was protecting, and catch it on verified docs too, where
  the mode reaches nothing.

  **What was deliberately left behind** is as informative as what was taken. That skill is triggered
  by a git diff rather than by a named capability, which is the input shape rejected here as
  `/retrofit` overlap. It carries a CMS schema linter, page-object staleness handling, test tagging,
  and a generated-output folder — all four project- or stack-specific. A test spell accreting a
  schema linter inside itself is direct evidence for the L0-versus-pack split this spell is built on.

## Possible Edge Cases

- A capability doc exists but its Test Coverage table is missing or empty.
- A capability doc has no unproved rows — the spell has nothing to do and should say so briefly
  rather than manufacturing work.
- Two scenarios in different capability docs are proved by the same test.
- `/testify audit` runs in a project with no capability docs at all.
- The named capability has no doc — the argument matched an increment slug rather than an area name,
  which the workflow spine warns is routinely different.
- A test is still failing long after the work that would make it pass landed, because nobody re-ran it.
- A test file covers scenarios from a doc that has since been split into two.
- The project has no `stack.md` → `## Tests` slot and no test files to infer from.
- Approval is given for some rows and withheld for others in the same run.
- A test written against a verified doc fails — the behavior the doc claims does not actually hold.

## Acceptance Criteria

- A developer names a capability and gets back a report of which of its scenarios nothing proves,
  before any file is written.
- The report separates scenarios that can be tested now from those blocked on missing test
  infrastructure, and names what each blocked one needs.
- Scenarios inferred from code rather than specified are reported separately, with the warning that
  proving one turns an inference into a contract.
- A scenario too vague to name a specific observable outcome produces a question for its author
  rather than a test.
- No test file is created or changed until the developer approves that specific scenario.
- A scenario's row records what its test's last run established — proved when it passed, failing when
  it did not — whether or not the doc is still a draft.
- A failing test is explained as expected of work in flight when the doc is still a draft, and as the
  doc disagreeing with the code when it is not.
- Each proposed test is reported alongside the specific ways it could have passed while the behavior
  was broken, and a verified-doc report states that no red-to-green signal is available.
- Every test the spell writes records which capability doc and which scenarios it came from.
- A scenario the project has decided cannot be tested carries that decision and its reason in the
  coverage table, and is never proposed again.
- Where proving a scenario would require establishing a testing convention the project does not have,
  the spell declines to establish it and routes that work to a spec.
- A developer can ask for a project-wide report that writes nothing and names coverage drift in both
  directions — scenarios nothing proves, and tests whose scenarios have changed or gone.
- Behavior the spell notices that no scenario describes is named and handed to `/feature`, never
  written into the doc by this spell.
- The spell works in a project with no stack pack installed, and says what it could not determine
  rather than guessing.

## Scenarios (Draft)

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

## Open Questions

- **Five statuses may mean the Status column is doing two jobs.** After this increment a row can read
  `Covered`, `Test failing`, `Not covered`, `Not covered (code-derived)`, or `Ruled out —
  <reason>`. Two independent facts are encoded in one cell: whether a test exists, and what its last
  run established. Splitting into two columns would make `Test failing` fall out of the pair rather
  than needing a name of its own. **Not done here** because it rewrites every existing coverage table
  in the project. Worth deciding before a sixth status is proposed.
- **Nothing re-observes a row, so a status can go stale in either direction.** A `Test failing` row
  *understates*: the work that would make it pass lands, nobody re-runs it, and the row keeps
  reporting a failure that is over. A `Covered` row *overstates*: its test starts failing and the row
  goes on claiming proof — which audit mode deliberately does not catch, because catching it would
  mean running the suite. `/plan`'s final step verifies the doc's scenarios and a re-run of `/testify`
  would notice either, so candidates exist, but neither is obliged; a status naming an observation is
  only as good as the last time anything observed it. **The overstating direction costs more**, and
  whatever closes it has to answer the question audit mode dodged: who may run a project's tests, and
  when. Same shape as the stale-reason question below — the three are one question in three hats.
- **Whether a `Ruled out` reason expires, and what notices it.** A reason like "this toolkit ships
  no rendering layer" stops being true the moment something owns the render layer, and nothing in the
  design re-reads it. Skipping the row forever is the failure mode the status was introduced to
  create. Candidates: audit mode reports these rows separately as claims to re-check, `/feature`
  re-validates on update, or the reason carries a date and goes stale visibly. Not decided.
- **Whether the audit report's shape can be shared with the guides audit.** `ROADMAP.md` → *Next*
  records this as the open half of the editor-guides increment: the report shape shipped as a
  self-contained section of `umbraco-17-guide-scaffolding`, extractable to core if a second caller
  ever arrived, and the planned test spell was named as the candidate. This increment is that second
  caller. **The question is deliberately not answered here** — the two shapes are written
  independently first, and convergence is judged from two real shapes rather than predicted from one.
  Answering it also settles the scaffolding reference's size entry in *Later*, which points at the
  same seam.
- **Whether the two new statuses belong to this increment or to `/feature`.** The claim is uneven.
  `Test failing` records something `/testify` itself observed, so it plainly owns writing it.
  `Ruled out` is an editorial judgment about the doc, which `/feature` owns — `/testify` only
  reads it and skips. Shipping both here is the pragmatic call because this is the first spell that
  needs either, but the second may be in the wrong spell.
- **Whether a capability doc is the right queue when the work earned no doc.** `change-to` and
  `fix-infra` work folds into an existing doc or into a runbook, so an increment can ship real
  behavior with no scenarios of its own to test. The chosen input shape makes that work invisible to
  `/testify`. Accepted for now on the grounds that `/retrofit` already proposes tests for
  out-of-flow changes, but the two coverage stories do not meet anywhere.
- **How stale detection behaves when a capability doc is split in two.** A test file's header names
  one doc; splitting that doc leaves the header naming a file that may no longer contain the
  scenarios it lists. The workflow spine calls splitting an editorial act made deliberately, so a
  deliberate remedy is plausible — but nothing currently prompts for one.

## Testing Guidelines

Meaningful tests for the cases below, without going too heavy:

- **The layer contract holds.** `scripts/check-contract.sh` must pass over the new spell — no project
  facts, no hardcoded paths, no tool or library names, no naming of the source repos. This is the
  gate that matters most, because the spell's whole design rests on holding no stack knowledge, and
  because one of its two design references is client work.
- **Every slot the spell reads follows the house form.** Each `**Slot:**` line is paired with an
  `**If empty:**` line, and the empty behavior degrades rather than guesses.
- **The spell budget is stated and correct.** Nine workflow spells after this lands, against ADR
  0010's ceiling of ten; the README's spellbook table and the roadmap agree on the count.
- **The template change is complete.** Both new statuses appear in `templates/feature.md` with their
  explanatory comment, and both spells that write the table — `/feature` and `/spec` — describe them.
  A status defined in one place and unknown to its writers is worse than no status.
- **The provenance header is specified as shape, not as syntax.** The spell states what the header
  must carry and that it must be a comment, and names no comment syntax of any language.
- **The Draft banner never reaches control flow.** The spell's text must read the banner only to
  choose how a result is explained, never to decide what is written. A branch here would misreport
  every legitimately-passing test in a half-built increment, which is the normal middle state of the
  flow rather than an edge case.
- **The spell chains by suggestion only.** It ends with a `Next:` line and invokes no other spell.

Not worth building a harness for: the report's prose, the ranking order in audit mode, and the
wording of the vacuity probes. Those are judged by reading the spell, the same as every other
spellbook file.
