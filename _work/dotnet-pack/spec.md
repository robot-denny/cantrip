# Spec for dotnet-pack

> This spec captures initial requirements and design rationale. For **current system
> behavior**, see the doc named on the **Work type** line below — a new feature doc for a new
> capability, an existing feature doc for a change, or a `docs/` runbook for a fix.

branch: dotnet-pack
design reference (if any): none — `_work/dotnet-pack/discovery.md` holds the decisions and rationale

**Work type**: new-capability
**Feature doc**: dotnet-guidance

## Summary

The toolkit has no per-file .NET guidance. It carries repo-level .NET audit posture inside the CMS
pack, and core's reviewer knows generic web-application concerns, but nothing tells an agent how to
write or review a C# file. A .NET project installing the toolkit today gets a workflow and a generic
reviewer, and nothing that knows the language it is written in.

This increment adds that as an opt-in stack pack of two reference units — one for authoring, one for
review — and makes three supporting changes it depends on:

- **The slot convention gains an optional way for a pack to say how a project's answer can be
  detected**, so configuration can read what a repo already shows rather than interviewing for it.
  Core cannot hold the recipe itself — it may not name a technology — so the pack supplies it.
- **The CMS pack's general async rule defers to the new pack**, keeping one rule in one place.

### Depends on a separate increment, which must land first

The pack's review guidance is written as *the C# expression of a defect core already names*. Core naming
those defects is **not** part of this increment: two language-agnostic failure modes — a rethrow that
discards the original error, a log call that interpolates values instead of passing them as fields, and
long-running work with no way to cancel it — are split out, because they improve review for every project
in every language whether or not this pack is ever installed.

They were split on **dependency direction**, not on layer. That change must precede the pack, since the
pack's wording follows it; the detection line above must *follow* the pack, since nothing can exercise a
detection mechanism until a pack declares one. Splitting by layer would have put both in one increment
pointing opposite ways.

**Do not start this increment's pack units until that one has landed**, or the pack will name idioms for
defects core does not yet describe.

The governing principle throughout: **the pack asserts what the platform has decided and stays silent
on what a project owns.** A broadly-applicable default ships; a contested preference is named as the
project's to answer, and every asserted default yields to a project that has answered differently.

Documentation is part of the deliverable, not follow-up. Adding a pack is a manual install, so the
README and changelog are the only mechanism by which an existing project learns the pack exists.

## Functional Requirements

- **FR1** — A project with the pack installed gets .NET authoring guidance when C# is written or
  refactored, including when the request never names the language.
- **FR2** — A review of a .NET change reports the failure modes the pack owns, with the severity scale
  the toolkit already uses.
- **FR3** — Style questions resolve in a stated order: the project's editor config, then a decision the
  project has recorded, then the pack's default, then the dominant style of the surrounding file.
- **FR4** — Contested style items are named in **one** place as the project's to answer, and the pack
  asserts no answer for any of them.
- **FR5** — *Moved.* "A project with no pack installed still catches the generalized failure modes,
  in any language" is now the prerequisite increment's requirement, not this one's. Numbering is left
  intact rather than closed up, so a reference to FR6 or FR7 elsewhere still resolves.
- **FR6** — Configuring the toolkit proposes a project's style answers from what the repository already
  shows, and asks only for what cannot be observed.
- **FR7** — The .NET pack and the CMS pack both inform a single review of a C# change in a CMS project,
  and a rule owned by one is not reported twice.
- **FR8** — Someone reading the install documentation can discover the pack and how to install it, and
  the changelog records both the addition and the change to the already-shipped CMS pack.
- **FR9** — Core remains free of technology names, and the layer contract gate passes.

## Design Reference (only if one exists)

None. The decisions, the review of the source material, the rejected alternatives, and the trigger-eval
results are all in `_work/dotnet-pack/discovery.md`.

## Possible Edge Cases

- A project whose editor config and recorded decision **disagree** — the order must resolve it rather
  than reporting a conflict.
- A project with the pack but **no** editor config and **no** recorded decisions — every contested item
  falls through to the surrounding file's style.
- A file with **no dominant style** to match, because it is new or genuinely mixed.
- A .NET project with the CMS pack but **not** the .NET pack — the common state of every existing
  install until someone runs the install command.
- A **non-.NET** project, where none of the pack's guidance should surface at all.
- A change that trips a rule **both** packs could claim, where the reader must not see it twice.
- A pack that declares how to detect an answer for a project where the detection finds **nothing
  conclusive** — a repo split evenly between two styles.
- A project that has deliberately chosen a style the platform does not default to, and expects not to be
  corrected for it on every review.

## Acceptance Criteria

- A C# authoring request that never names the language still draws on the pack's conventions.
- A review of a C# change reports a rethrow that discards the original error, an interpolated log
  message, a missing cancellation path, and an unvalidated payload at a boundary — each with a severity
  from the existing scale.
- Where the editor config states a style, that style is followed and no finding is raised against it,
  **even when it contradicts the pack's default**.
- Where the editor config is silent and the project has recorded a decision, the decision is followed.
- Where neither speaks, the pack's default applies; where the pack has no default, the surrounding
  file's dominant style applies.
- Every contested style item is listed in one place as the project's to answer, and the pack offers no
  answer for any of them.
- The review guidance names the C# form of each defect core describes, without restating why the defect
  matters — core already carries that, and two copies is the drift the one-place rule exists to prevent.
- Configuring the toolkit proposes style answers read from the repository, and asks only for what it
  could not observe — stating that any answer may be left empty.
- A C# change in a project with both packs draws on both, and a rule owned by one pack appears once.
- The install documentation lists the pack with its command; the changelog records the pack as an
  addition and the CMS-pack edit as a change.
- The layer-contract gate passes, with no technology name in core.

## Scenarios (Draft)

Draft BDD scenarios derived from the acceptance criteria using Example Mapping. Each Rule maps
to an acceptance criterion; scenarios use concrete examples. These get verified and refined
after implementation — the feature doc holds the verified version.

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

### Rule: A .NET review reports the failure modes the pack owns

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

### Rule: The project's own style decisions outrank the pack's defaults

```scenario
Scenario: An editor config setting wins over the pack's default
  Given a project whose editor config asks for block-scoped namespaces
  And the pack's own default is file-scoped
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

### Rule: The pack names a contested decision without answering it

```scenario
Scenario: Sealing is named as the project's decision
  Given a developer reading the pack's conventions
  When they look for whether types should be sealed by default
  Then sealing is listed among the decisions the project owns
  And the pack states no answer of its own
```

```scenario
Scenario: The contested items live in one place
  Given a developer looking for which style questions the project owns
  When they read the pack
  Then all of them appear in a single list
  And the review guidance points at that list rather than repeating it
```

### Rule: The pack names the C# form without restating the reason

```scenario
Scenario: The review guidance points at the defect core already describes
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

```scenario
Scenario: An inconclusive reading is not guessed
  Given a project split evenly between two declaration styles
  When someone configures the toolkit
  Then no declaration-style answer is asserted
  And the reason it was left open is recorded
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

```scenario
Scenario: The changelog separates the addition from the change
  Given someone reading the changelog for this release
  Then the .NET pack is recorded as an addition
  And the edit to the already-shipped CMS pack is recorded as a change
```

## Open Questions

- ~~**Does this increment want splitting?**~~ **Settled 2026-08-13: yes, by dependency direction.** The
  generalized failure modes became their own increment because they have standalone value — they
  improve review in any language with no pack installed — and because the pack's wording follows them. The
  detection line stayed here, because it can only be exercised by a pack that declares one. See *Depends
  on a separate increment* above.
- **Is `dotnet-guidance` the right area name?** Chosen over `dotnet-pack` because the capability is the
  guidance, not its packaging, and because a doc named for the increment is the trap the workflow
  skill's naming tell warns about. Worth a second opinion before the doc accretes.--dotnet-guidance is ok
- **Should the generalized failure modes be proven outside .NET before shipping?** The claim is that all
  three are language-agnostic. One scenario asserts it, but nothing yet exercises it against a
  non-.NET diff. Cheap to check and the whole justification for putting them in core rests on it.
- **Does the new detection declaration need a gate check?** Every `**Slot:**` is gated for a paired
  fallback. A detection line is optional by design, so there is nothing to pair — but an optional
  mechanism nothing enforces is also one that silently stops being used.
- **Where does "one public type per file" land** — asserted default, or project-owned? Near-universal,
  but stating it as a rule bans nested and file-local types that the language supports deliberately.
- **How thin is too thin for the new area doc?** It will cover only what this increment establishes,
  with the rest of .NET guidance undocumented. That is intended visible debt, but it should be flagged
  for backfill rather than left looking complete.

## Testing Guidelines

Meaningful tests for the cases below, without going too heavy:

- **The layer-contract gate** — the pack's units carry a matching name and directory, a description long
  enough to trigger, no model-invocation suppression on a reference unit, and no technology name
  anywhere in core. This is the check that must pass before anything else counts.
- **The resolution order, at each rung** — one case where the editor config decides, one where a
  recorded decision decides, one where the pack's default decides, one where the surrounding file
  decides. The first is the important one: it must hold even when the config contradicts the pack.
- **Absence** — a CMS project *without* this pack still gets its CMS guidance and the generalized failure
  modes, and nothing reports the absent pack as a problem. (The generalized-failure-mode half is proven in
  the prerequisite increment, including against a non-.NET diff; do not re-prove it here.)
- **Content, not just triggering** — point the finished pack at a change carrying known planted defects
  and confirm it reports them. Triggering is already evidenced (`discovery.md` §10); nothing yet shows
  the bodies work.
- **No double reporting** — the rule both packs could claim appears once.
- **Documentation** — the install command in the README is the one that actually installs the pack, not
  a plausible-looking variant.

- **The install checker must actually know about the new pack.** Corrected from an earlier reading: the
  gate's roster check covers core only, but `check-install.sh` carries a **separate pack roster** and a
  **pack-slot survey**. A pack absent from both installs and verifies as though it were not there. The
  same list has already drifted once for core, which is why a gate check exists for it — and the pack
  half of it is currently ungated and already behind.

One note on what *not* to spend effort on: trigger evals for the two descriptions are already run and
recorded, and skill bodies cannot change triggering, so re-running them proves nothing.
