# Feature: .NET Guidance

> **Draft** — These scenarios have not yet been verified against an implementation. They will be refined
> during planning and verified after implementation.

A team working in a .NET project gets guidance that knows the language they are writing in — how to write
a C# file, and what to look for when reviewing a change to one. The guidance states what the platform has
already decided and stays deliberately silent on what each project prefers, so it helps a project without
overruling it: a stated preference or an editor-config setting always wins over the guidance's own
default.

**Source**: `_work/dotnet-pack/spec.md`
**Last verified**: not yet — draft from spec

---

## Increments

The per-feature mini-roadmap: shipped increments, planned increments, and parking-lot ideas.
Newest planned items first. When an item ships, flip the checkbox and point it at the archived
increment.

- [ ] .NET pack, plus the detection line it enables (`_work/dotnet-pack/plan.md`)
- [ ] **Prerequisite, tracked elsewhere**: three language-agnostic review failure modes move into core.
      Split out by dependency direction — the pack's wording follows them, and they help every project in
      every language with no pack installed. Their behavior belongs to a core review capability doc, not
      this one
- [ ] Parking lot: worked examples for the remaining conventions, if the first set proves they carry
      more than the rule sentence does
- [ ] Parking lot: whether the audit's .NET pillar eventually moves here from the CMS pack — deferred
      deliberately, see `_work/dotnet-pack/discovery.md` §5
- [ ] **Backfill**: this doc covers only what its first increment establishes. The rest of .NET
      guidance is undocumented — a candidate for `/feature`'s from-code mode once the pack has grown

---

## Behaviors

Scenarios are grouped by Rule — the business rule the scenarios prove. Use concrete values and
business language. See the `bdd-principles` skill for guidance.

### Rule: .NET guidance applies to the work, not to the wording of the request

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

### Rule: A .NET review reports the failure modes the guidance owns

```scenario
Scenario: A rethrow that loses the original error is reported
  Given a change whose catch block rethrows the caught exception by name
  When the change is reviewed
  Then the review reports that the original error's origin is discarded
  And it names the form that preserves it
```

```scenario
Scenario: A log message that hides its values is reported
  Given a change that logs an order identifier by building the message as one interpolated string
  When the change is reviewed
  Then the review reports that the identifier cannot be filtered on afterwards
```

```scenario
Scenario: Work that cannot be cancelled is reported
  Given a change that calls an external service with no way for the caller to cancel
  When the change is reviewed
  Then the review reports the missing cancellation path
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
Scenario: A deliberate choice is not re-litigated on every review
  Given a project that has chosen block-scoped namespaces on purpose
  When three separate changes are reviewed
  Then none of the three reviews raises namespace style
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

### Rule: The guidance names the C# form without restating the reason

```scenario
Scenario: A finding points at the defect core already describes
  Given a project with the .NET pack installed
  When a review covers a catch block that rethrows the caught exception by name
  Then the finding names the C# form that preserves the original error
  And the reason the defect matters is not restated a second time
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
Scenario: A rule owned by one pack is reported once
  Given a project with both packs installed
  When a review covers an outbound call that is consumed synchronously and cannot be cancelled
  Then the finding appears once
```

### Rule: An existing project can discover that the pack exists

```scenario
Scenario: The install documentation lists the pack
  Given someone reading the toolkit's install documentation
  When they look for the available stack packs
  Then the .NET pack is listed with the command that installs it
```

---

## Edge Cases

### Rule: A project that has decided differently is respected, not corrected

```scenario
Scenario: The editor config and a recorded decision disagree
  Given an editor config asking for file-scoped namespaces
  And a recorded decision asking for block-scoped
  When a developer adds a class
  Then the editor config decides, because it is the setting the build already enforces
  And the disagreement is reported rather than silently resolved
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

### Rule: The common case is a CMS project without the .NET pack

```scenario
Scenario: A CMS project that has not installed the .NET pack
  Given a project with the CMS pack installed and the .NET pack absent
  When a review covers a C# service
  Then the CMS guidance and the generalized failure modes still apply
  And nothing reports the absent pack as a problem
```

---

## Test Coverage

| Scenario | Test File | Status |
|----------|-----------|--------|
| A request that never names the language still gets the conventions | — | Not covered |
| A non-.NET project sees none of it | — | Not covered |
| A rethrow that loses the original error is reported | — | Not covered |
| A log message that hides its values is reported | — | Not covered |
| Work that cannot be cancelled is reported | — | Not covered |
| An editor config setting wins over the default | — | Not covered |
| A recorded decision wins where the editor config is silent | — | Not covered |
| With nothing stated, the surrounding file decides | — | Not covered |
| A deliberate choice is not re-litigated on every review | — | Not covered |
| Sealing is named as the project's decision | — | Not covered |
| The contested items live in one place | — | Not covered |
| A finding points at the defect core already describes | — | Not covered |
| An observable answer is proposed, not asked | — | Not covered |
| Only the unobservable is asked | — | Not covered |
| A C# change in a CMS project draws on both packs | — | Not covered |
| A rule owned by one pack is reported once | — | Not covered |
| The install documentation lists the pack | — | Not covered |
| The editor config and a recorded decision disagree | — | Not covered |
| A repository split evenly between two styles | — | Not covered |
| The first file in a new area | — | Not covered |
| A CMS project that has not installed the .NET pack | — | Not covered |

<!-- Covered: a test asserts it. Not covered: specified, untested. Not covered (code-derived):
     inferred from reading the code, never specified and never tested — the weakest claim here.
     Keeping the third distinct is what lets a reader tell verified behavior from inferred. -->

Everything is Not covered because nothing is built yet. Two of these are already partly evidenced without
being tested: the trigger behavior behind the first scenario was measured during discovery
(`_work/dotnet-pack/discovery.md` §10), and the co-load behavior behind "draws on both packs" was measured
at 4/4 there. Neither is a test, so neither is claimed as coverage.

The parking lot also carries a standing risk worth not tidying away: the detection line is optional by
design and no gate check enforces it, so an unused mechanism would fail silently rather than loudly.

---

## Revision Notes

- 2026-08-13: Draft scenarios from initial spec
