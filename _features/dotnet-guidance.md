# Feature: .NET Guidance

A team working in a .NET project gets guidance that knows the language they are writing in — how to write
a C# file, and what to look for when reviewing a change to one. The guidance states what the platform has
already decided and stays deliberately silent on what each project prefers, so it helps a project without
overruling it: a stated preference or an editor-config setting always wins over the guidance's own
default.

**Source**: `_work/shipped/dotnet-pack/spec.md`
**Last verified**: 2026-08-17

> **Thin by design.** This records what the pack's first increment established. The guidance itself is
> larger than what appears below — the naming table, serialization, nullability, records, and the modern
> syntax section all ship and appear in no scenario, because the increment's acceptance criteria did not
> reach them. That is visible debt with a known remedy: `/feature`'s from-code mode against the two units.

---

## Increments

The per-feature mini-roadmap: shipped increments, planned increments, and parking-lot ideas.
Newest planned items first. When an item ships, flip the checkbox and point it at the archived
increment.

- [x] 2026-08-17 — The codebase audit joined this pack, so a .NET project with no content
      management system can get a structural assessment
      (`_work/shipped/pack-boundaries-and-succession/spec.md`)
- [x] 2026-08-14 — The .NET pack, its two units, and the detection line it enables
      (`_work/shipped/dotnet-pack/spec.md`)
- [x] **Prerequisite, landed 2026-08-13**: two language-agnostic review failure modes moved into core.
      Split out by dependency direction — the pack's wording follows them, and they help every project in
      every language with no pack installed. Their behavior belongs to a core review capability doc, not
      this one
- [ ] **Backfill**: the sections named in the note above. A candidate for `/feature`'s from-code mode
- [ ] Parking lot: worked examples for the remaining conventions, if the first set proves they carry
      more than the rule sentence does
- [x] **Was parked, now shipped**: the audit moved here from the CMS pack — the whole unit rather than
      just its .NET pillar. `_work/shipped/dotnet-pack/discovery.md` §5 deferred the question; the
      pack-boundary increment answered it, because the audit named no CMS version and so was pinned to a
      major it did not depend on
- [ ] **Backfill**: the audit's own five pillars, its scoring anchors, and the comparison report shape.
      The scenarios below cover what a user observes, not how a pillar is scored
- [ ] Parking lot: the review unit ships eight eval cases and nothing runs them. If a pack's descriptions
      are meant to be eval-verified the way ADR 0003 says core references are, that is unowned work
- [ ] Parking lot: one eval case carries an unconditioned `Minor–Major` severity, the shape review
      corrected on another case. Worth a pass over all eight
- [ ] **Known gap**: nothing enforces the detection line. It is optional by design, so there is nothing
      to pair it with the way a slot's fallback is paired — its use rests on authoring discipline

---

## Behaviors

Scenarios are grouped by Rule — the business rule the scenarios prove. Use concrete values and
business language. See the `bdd-principles` skill for guidance.

### Rule: The guidance applies to the work, not to the wording of the request

```scenario
Scenario: A request that never names the language still gets the conventions
  Given a project with the .NET pack installed
  When a developer asks for a service that caches the subscriber count for an hour
  Then the .NET authoring conventions inform the code that is written
  And the developer did not have to name C# or .NET to get them
```

```scenario
Scenario: A non-.NET project sees none of it
  Given a project with the .NET pack installed and no .NET code
  When a developer asks for a change to a stylesheet
  Then the .NET conventions do not surface
```

### Rule: A review names the C# form of a defect core already describes

```scenario
Scenario: A rethrow that loses the original error is reported
  Given a change whose error handler rethrows the caught exception by name
  When the change is reviewed
  Then the review reports that where the failure started is no longer recorded
  And the finding names the C# form that preserves it
  And the reason the defect matters is not argued a second time
```

```scenario
Scenario: A log message that hides its values is reported
  Given a change that logs an order number and a retry count inside one built-up message string
  When the change is reviewed
  Then the review reports that neither value can be filtered or grouped on afterwards
```

```scenario
Scenario: A sanitized response to an external caller draws no finding
  Given a handler that returns a generic failure message to an external caller
  And the original error is recorded internally where the team can read it
  When the change is reviewed
  Then no finding is raised about a lost origin
```

### Rule: The guidance supplies an idiom for a rule it does not own

```scenario
Scenario: Cancellation is the performance reviewer's finding, not this guidance's
  Given a change with a multi-minute outbound call that accepts no cancellation
  When all three reviewers review the change and their findings are merged
  Then the missing cancellation appears once, attributed to the performance reviewer
  And the .NET guidance supplied the C# form of the fix without claiming a severity for it
```

```scenario
Scenario: A deadline is a separate requirement from a token
  Given an outbound call whose method accepts a cancellation token and passes it on
  And nothing anywhere sets a time limit on the call
  When the change is reviewed
  Then the missing deadline is still reported
  And the review names a client-wide timeout or a linked token with a deadline as the C# forms
```

### Rule: The project's own style decisions outrank the guidance's defaults

```scenario
Scenario: An editor config setting wins over the default
  Given a project whose editor config asks for block-scoped namespaces
  And the guidance's own default is file-scoped
  When a developer adds a class
  Then the class is written block-scoped
  And no review finding is raised about namespace style
```

```scenario
Scenario: A recorded decision wins where the editor config is silent
  Given a project that has recorded "types are sealed unless a test needs to mock them"
  And an editor config that says nothing about sealing
  When a review covers a new unsealed type that a test mocks
  Then no finding is raised about sealing
```

```scenario
Scenario: With nothing stated, the surrounding file decides
  Given a project with no recorded style decisions
  And an editor config that says nothing about declaration style
  And surrounding files that declare locals with var throughout
  When a developer adds a local variable
  Then it is declared the same way as its neighbours
  And no finding is raised about declaration style
```

```scenario
Scenario: The order settles shape, never correctness
  Given a project whose editor config and recorded decisions say nothing about logging
  When a review covers a log call that folds its values into the message text
  Then the finding is raised regardless
  And no configuration setting could have excused it
```

### Rule: A contested decision is named without being answered

```scenario
Scenario: Sealing is named as the project's decision
  Given a developer reading the .NET conventions
  When they look for whether types should be sealed by default
  Then sealing is listed among the decisions the project owns
  And the guidance states no answer of its own
```

```scenario
Scenario: The contested items live in one place
  Given a developer looking for which style questions the project owns
  When they read the guidance
  Then all of them appear in a single list
  And the review guidance points at that list rather than repeating it
```

### Rule: Configuration reads what the repository already shows

```scenario
Scenario: An observable answer is proposed, not asked
  Given a project whose files declare locals with var throughout
  When someone configures the toolkit
  Then the declaration-style answer is proposed from what the project already shows
  And it is not put to them as a question
```

```scenario
Scenario: The cheap signal is read before the expensive one
  Given a project whose editor config already sets the declaration-style rule
  When someone configures the toolkit
  Then that setting answers it
  And no scan of the project's files is undertaken for a question already settled
```

```scenario
Scenario: Only the unobservable is asked
  Given a project with nothing recorded about which validation approach it uses
  When someone configures the toolkit
  Then they are asked about validation
  And they are told the answer may be left empty
```

### Rule: Two packs inform one review without duplicating a rule

```scenario
Scenario: A C# change in a CMS project draws on both packs
  Given a project with both the .NET pack and the CMS pack installed
  When a review covers a new C# service that a content block calls when it renders
  Then both the .NET guidance and the CMS guidance inform the review
```

```scenario
Scenario: A rule both packs could claim is reported once
  Given a project with both packs installed
  When a review covers a form submission handler whose outbound call is consumed synchronously
  Then the finding appears once
  And it is the CMS pack's, because for a form handler it states the rule more specifically
```

### Rule: An existing project can discover that the pack exists

```scenario
Scenario: The install documentation lists the pack
  Given someone reading the toolkit's install documentation
  When they look for the available stack packs
  Then the .NET pack is listed with the command that installs it
  And they are told what installing it costs in context on every request
```

### Rule: A codebase can be judged on its structure, with or without a content management system

```scenario
Scenario: A service with no content management system is assessed
  Given a .NET service with no content management system in it
  When the developer asks whether it is structured sensibly for the team to grow into
  Then they get a written assessment covering the five pillars
  And no finding refers to a content management system
```

```scenario
Scenario: The assessment is a written report, not a conversation
  Given a developer who asks for an audit of their architecture
  When the assessment runs
  Then the result is a written report naming strengths and weaknesses
  And its recommendations are ranked by how urgent each one is
```

### Rule: Recommendations are framed for how far along the codebase is

```scenario
Scenario: A freshly scaffolded project is told to be ambitious
  Given a web application just created from a project template
  When the developer asks for an audit
  Then foundational recommendations are raised as cheap to apply now
```

```scenario
Scenario: An inherited codebase is told to understand before changing
  Given a .NET codebase the developer has just taken over from someone else
  When the developer asks for help working out what they have
  Then the report leads with a map of the codebase before recommending any change
```

```scenario
Scenario: A stage that cannot be read is asked about once
  Given a codebase whose stage the assessment cannot determine from its contents
  When the assessment runs
  Then the developer is asked once how they would describe it
  And their answer is accepted rather than overridden
```

### Rule: Two codebases can be compared without one being declared correct

```scenario
Scenario: Two differently organized codebases are compared
  Given one codebase organized by feature and another organized by kind of component
  When the developer asks how theirs compares to the other
  Then the report describes the trade-off each organization makes
  And neither is declared universally correct
```

---

## Edge Cases

### Rule: A project that has decided differently is respected, not corrected

```scenario
Scenario: The editor config and a recorded decision disagree
  Given an editor config asking for file-scoped namespaces
  And a recorded decision asking for block-scoped
  When someone configures the toolkit
  Then the editor config decides, because it is the setting the build already enforces
  And both are reported, with a statement of which was recorded
```

### Rule: An inconclusive reading is left open rather than guessed

```scenario
Scenario: A repository split evenly between two styles
  Given a project whose files are split evenly between two declaration styles
  When someone configures the toolkit
  Then no declaration-style answer is asserted
  And the reason it was left open is recorded
```

### Rule: A file with no dominant style falls back without inventing one

```scenario
Scenario: The first file in a new area
  Given a project with no recorded style decisions and no editor config
  When a developer adds the first C# file in a new area
  Then the guidance's own defaults apply
  And no finding is raised for having no neighbours to match
```

### Rule: A deferral must not become a loss

```scenario
Scenario: A CMS project that has not installed the .NET pack
  Given a project with the CMS pack installed and the .NET pack absent
  When a review covers a form submission handler with an uncancellable outbound call
  Then the finding is still raised
  And the CMS guidance applies the general rule itself, because nothing else is installed to
```

```scenario
Scenario: The rule reaches beyond the surface the CMS pack narrowed to
  Given the same project with only the CMS pack installed
  When a review covers an outbound call that is not behind a form
  Then the rule still applies to it
```

### Rule: Work outside the assessment's competence is declined, not attempted

```scenario
Scenario: A codebase on another platform is declined
  Given a codebase that is not .NET
  When the developer asks for a structural audit
  Then the assessment declines and says its signals are .NET-specific
  And it does not produce a report scored on signals it cannot read
```

```scenario
Scenario: A request for a quick opinion is not answered with a document
  Given a developer who wants a gut check rather than a written report
  When they ask informally
  Then the assessment offers to discuss it instead
```

### Rule: Documentation is credited by what exists, not penalized by what is missing

```scenario
Scenario: An unconventional documentation layout is credited
  Given a codebase recording its decisions in a folder named unlike the common convention
  When the assessment scores documentation and onboarding
  Then the documentation it does find is credited
  And no finding penalizes the absence of a particular filename
```

---

## Test Coverage

There is **no automated harness for a review** in this project, none for a configuration run, and none
for an assessment. What exists instead is committed eval cases — definitions of what a run should
produce, scoreable by hand. All three units of this pack now follow that pattern: the review unit ships
eight cases, the audit six. A case is a *specified check*, not a passing one, so nothing below is
`Covered`.

Rows citing an **audit eval case** are numbered against
`skills/dotnet/reference/codebase-audit/evals/evals.json`; unqualified case numbers are the review
unit's. Those cases test *triggering* — whether the right unit fires for a given request — so a row
citing one has evidence that the guidance is reached, not that its output is right.

| Scenario | Evidence | Status |
|----------|-----------|--------|
| A request that never names the language still gets the conventions | trigger measured in `_work/shipped/dotnet-pack/discovery.md` §10 | Not covered |
| A non-.NET project sees none of it | — | Not covered |
| A rethrow that loses the original error is reported | eval case 1 | Not covered — case defined |
| A log message that hides its values is reported | eval case 2 | Not covered — case defined |
| A sanitized response to an external caller draws no finding | — | Not covered |
| Cancellation is the performance reviewer's finding, not this guidance's | eval cases 3 and 6 | Not covered — case defined |
| A deadline is a separate requirement from a token | — | Not covered |
| An editor config setting wins over the default | eval case 5 | Not covered — case defined |
| A recorded decision wins where the editor config is silent | — | Not covered |
| With nothing stated, the surrounding file decides | — | Not covered |
| The order settles shape, never correctness | — | Not covered |
| Sealing is named as the project's decision | — | Not covered |
| The contested items live in one place | — | Not covered |
| An observable answer is proposed, not asked | recorded run, `1475440` | Not covered |
| The cheap signal is read before the expensive one | — | Not covered |
| Only the unobservable is asked | — | Not covered |
| A C# change in a CMS project draws on both packs | co-load measured 4/4, `discovery.md` §10 | Not covered |
| A rule both packs could claim is reported once | eval case 7; recorded run, `04de059` | Not covered — case defined |
| The install documentation lists the pack | install command run, `9b899fe` | Not covered |
| The editor config and a recorded decision disagree | — | Not covered |
| A repository split evenly between two styles | — | Not covered |
| The first file in a new area | — | Not covered |
| A CMS project that has not installed the .NET pack | eval case 8 | Not covered — case defined |
| The rule reaches beyond the surface the CMS pack narrowed to | eval case 8 | Not covered — case defined |
| A service with no content management system is assessed | audit eval case 5 | Not covered — case defined |
| The assessment is a written report, not a conversation | audit eval case 1 | Not covered — case defined |
| A freshly scaffolded project is told to be ambitious | audit eval case 2 | Not covered — case defined |
| An inherited codebase is told to understand before changing | audit eval case 4 | Not covered — case defined |
| A stage that cannot be read is asked about once | — | Not covered |
| Two differently organized codebases are compared | audit eval case 3 | Not covered — case defined |
| A codebase on another platform is declined | — | Not covered |
| A request for a quick opinion is not answered with a document | — | Not covered |
| An unconventional documentation layout is credited | — | Not covered |

<!-- Covered: a test asserts it. Not covered: specified, untested. Not covered (code-derived):
     inferred from reading the code, never specified and never tested — the weakest claim here.
     Keeping the third distinct is what lets a reader tell verified behavior from inferred. -->

**Twelve of thirty-three have a defined eval case, and none of the thirty-three has a test.** The distinction
matters: a case states what a run should produce, so it can be scored — but nothing runs it, and nothing
fails when the behavior regresses. Where a scenario cites a commit instead, the evidence is a recorded
before-and-after captured while the step was implemented; the working files were not committed, so what
survives is the commit's own account of it rather than the capture.

---

## Revision Notes

- 2026-08-13: Draft scenarios from initial spec
- 2026-08-14: Verified against the shipped pack. Draft banner removed.
- 2026-08-14: **One scenario was wrong and is corrected.** The draft had "work that cannot be cancelled is
  reported" under the failure modes this guidance owns. It does not own that: the shipped unit supplies
  the C# idiom and explicitly withholds a severity, because `reviewer-discipline` assigns cancellation on
  outbound work to the performance reviewer. It now has its own Rule about supplying an idiom for a rule
  the guidance does not own, which is a different and more useful thing to have documented.
- 2026-08-14: Four scenarios added for behavior that shipped after the draft was written — that a deadline
  is a separate requirement from a token, that the cheap configuration signal is read before any scan,
  that the resolution order settles shape and never correctness, and that the CMS pack's deferral still
  reaches outbound calls that are not behind a form. Each came from a review finding during implementation
  rather than from the spec.
- 2026-08-17: The codebase audit joined this pack, and nine scenarios record what it observably does —
  under three new Rules in Behaviors and two in Edge Cases. It arrived from a pack where no feature doc
  covered it, so this is a backfill rather than a rename: the assessment works on a .NET project with no
  content management system, frames its recommendations by how far along the codebase is, compares two
  repositories without ranking them, and declines work outside its competence rather than scoring signals
  it cannot read. Five of the nine cite the audit's own eval cases; those test *triggering*, so they
  evidence that the guidance is reached, not that its output is right. A parking-lot item asking whether
  the audit's .NET pillar would move here is now closed — though not on the terms it was parked. It asked
  about moving the .NET pillar out of the CMS pack; the whole unit moved instead, which sidesteps the
  problem that parked it (splitting Pillar 1's signals from its scoring anchors) rather than solving it as
  posed. Its five pillars and scoring anchors remain undocumented and are parked as backfill. The move
  mechanics stay in the shipped spec.
- 2026-08-17: **The tally in the note below was wrong and is corrected here.** It read "six of
  twenty-four" while the table held seven rows with a defined case. The current figure — twelve of
  thirty-three — is counted from the table rather than derived from the old one, so the inherited
  off-by-one does not survive in it. Recorded because a reader comparing versions would otherwise see
  six become twelve and conclude this increment added six cases; it added five.
- 2026-08-14: The coverage table now distinguishes a *defined* eval case from no evidence at all. Six
  scenarios have one. Nothing is `Covered`, which is accurate rather than pessimistic — a case nothing
  runs cannot catch a regression.
