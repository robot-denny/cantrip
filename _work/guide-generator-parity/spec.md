# Spec for guide-generator-parity

> This spec captures initial requirements and design rationale. For **current system
> behavior**, see the doc named on the **Work type** line below — a new feature doc for a new
> capability, an existing feature doc for a change, or a `docs/` runbook for a fix.

branch: robot-denny/guide-generator-port
design reference (if any): the client project's backoffice Guide Generator dashboard, a C# port of
this pack's `guide.py`. Its behavior is read for this spec; none of its code, names or settings
travel.

**Work type**: change-to editor-guides
**Feature doc**: editor-guides

## Summary

`/guide` writes and refreshes editor guides from a developer's machine. The client project needed
the same job done from the backoffice, on Umbraco Cloud, where Python can't run, so it ported the
spell's script to C# and put a dashboard in front of it. Along the way the dashboard gained three
behaviors the spell doesn't have:

- **Ignoring a component** that will never need a guide, so the audit stops reporting it as
  undocumented. The list is kept on the guides node, so it travels with the content.
- **Marking an out-of-date guide as up to date** when it is already correct, for example after a
  content sync left its stored signature behind. Only the stored signature changes.
- **Refreshing AI-written text that nobody has edited.** Today `/guide` writes a guide's prose once,
  at creation, and never again. The dashboard records what it generated, and on regeneration
  rewrites text still exactly as generated while keeping anything a person changed, even by a word.

This increment brings those three behaviors to `/guide`, so the spell and a dashboard built beside
it give the same answer about every guide. It also accepts the Deploy 17.3.1 serialization format,
and adds an `umbraco-17` reference blueprint for a project that wants the dashboard: what it is
made of, how it stays in step with `guide.py`, and what it must never do.

**Work type:** a change to the existing editor-guides capability. The three behaviors are standing
behavior of guides, so they fold into `_features/editor-guides.md`. The blueprint adds no behavior of
its own to this repo; its rules for a dashboard are recorded there too, as behavior a built one owes.

## Functional Requirements

**Format support**

- `guide.py` reads Deploy files declaring `__version` 17.3.1, as it reads 17.2.1. The reason
  recorded beside the accepted-versions list says what was compared and what differed, without
  naming the project it was measured on.

**Ignoring a component**

- A developer can ask `/guide` to ignore a component, and to stop ignoring one. Each is a change
  to the guides node, proposed and written only on approval, like any other write.
- The ignore list is kept on the guides node, so it moves between environments with that node and
  is read the same way by the spell and by a dashboard.
- An ignored component is reported apart in the audit: not as undocumented, not as stale, and its
  existing guide not as an orphan. It is listed by name, so the list can't hide a component
  silently.
- `/guide <alias>` on an ignored component stops and says it is ignored, rather than generating.
- A guides node with no ignore field yet reads as "nothing ignored". The first ignore asks for the
  field to be added, per the scaffolding reference, rather than creating schema itself.

**Marking a guide as up to date**

- A developer can ask `/guide` to mark one component's guide as up to date. Only a guide the audit
  reports as **stale** can be marked; anything else is refused, saying why.
- Marking rewrites only the guide's stored signature to the component's current one. Rows, prose,
  examples and every other field are untouched. The report says plainly that schema changes since
  the last generation are not added by marking.
- The write is proposed and approved like any other. A published guide is saved, and republished
  only when it has no other unpublished changes; otherwise it is saved and the report says why it
  was not published.

**Protecting edited AI text**

- When `/guide` writes model-authored text (the purpose sentence, the when-to-use section, a row's
  note), it also records, on the guide page, a fingerprint of exactly what it wrote, per field and
  per row.
- On regeneration, each model-authored field is in one of three states, and the plan reports which:
  - **as generated**: its text still matches the recorded fingerprint. It is rewritten.
  - **edited**: its text differs from the fingerprint, by any amount. It is kept, and no
    replacement is proposed.
  - **no record**: the page holds no fingerprint for it, because it predates this change, was
    written by hand, or was written by a tool that recorded nothing. It is kept, exactly as an
    edited field is.
- Rewritten text is shown in the difference before anything is written, as row changes are today.
- A field nobody ever wrote stays as today's rule has it: named in the report, not proposed.
- Text edited between the plan and the write is kept: the write re-reads each field and skips one
  that no longer matches what the plan saw.
- Main body content, live examples, screenshots and the page's name, address and settings are never
  touched, as today.

**Agreement between the spell and a dashboard**

- The fingerprint, the ignore list and the stored signature are each defined once, in the script,
  so a port can be held to them. A dashboard and `/guide --audit` reading the same content report
  the same status for every component.
- The script can emit reference output (extract, signature, inventory, audit, plan, and the new
  fingerprint) from a fixed set of schema files, which a port's tests compare against.

**Dashboard blueprint**

- A new `umbraco-17` reference describes a backoffice guide-generator dashboard a project builds
  for itself, through `/spec` and `/plan`, as `umbraco-17-test-content-builder` does for test
  content. It covers:
  - why it is a port, and how it is kept equal to `guide.py` (reference output and the tests that
    compare against it, regenerated when the script changes);
  - the modules, and the Umbraco 17 services each uses;
  - the component list, its statuses, and the ignore and mark-up-to-date actions;
  - generating through a model API, with the key held as a server-side secret per environment and
    never committed, and a plain message when it is missing;
  - preview before save, drafts only, never publishing a new guide;
  - sanitizing model output before it is shown or saved;
  - checking generated prose against the project's guide style and showing what fails as a
    warning;
  - access: a configured user group, optionally narrowed by email domain, shared by the dashboard
    and every endpoint; no unauthenticated route reaches the model;
  - the accessibility the dashboard owes, as the core test-content reference lists for its admin
    screen.
- The blueprint names no client, organization, domain, model version or setting key from the
  project it came from.

**Scaffolding and docs**

- `umbraco-17-guide-scaffolding` gains the two new fields a guide set needs: the ignore list on
  the guides node, and the fingerprint record on a guide page, each read-only to editors.
- The pack's README section, the spell cards, CHANGELOG, `docs/layout.md` counts and the install
  checker's roster cover the new reference.

## Possible Edge Cases

- A row's note edited only in whitespace or markup normalization by the rich text editor reads as
  edited unless the fingerprint is taken over normalized text. Which normalization is an open
  question; erring toward "edited" is safe.
- A guide page copied from another environment carries the other environment's fingerprints. Since
  they describe the text on the page, they still hold; this is why they live on the page.
- A row whose field was renamed keeps its note and its fingerprint follows the row, not the label.
- An ignored component whose guide is later deleted, or a component ignored and then removed from
  the schema: the ignore entry is reported as naming nothing, not silently kept.
- Marking up to date on a guide whose component has no readable schema: refused.
- Two people ignoring different components from two environments: the last transfer of the guides
  node wins. The blueprint says so; the spell reports the list it read.
- A guide with fingerprints for some fields and not others (a partial write that stopped on a
  read-back difference): each field is judged on its own.
- The demo project's Deploy files declare 17.0.1, which the script also skips. Out of scope here
  unless measured the same way 17.3.1 was.

## Acceptance Criteria

- `guide.py` reads Deploy 17.3.1 files and reports them as it reports 17.2.1.
- A developer can ignore and stop ignoring a component through `/guide`, with approval, and the
  audit reports ignored components apart and never as gaps or orphans.
- A developer can mark a stale guide as up to date, which changes only its stored signature, and
  nothing else can be marked.
- On regeneration, model-authored text still as generated is rewritten, and text that was edited
  or has no record is kept.
- The spell and a port reading the same content give each component the same status, proved by
  reference output the script can produce.
- An `umbraco-17` reference blueprint describes the dashboard, with no client-identifying content.

## Scenarios (Draft)

Draft BDD scenarios derived from the acceptance criteria using Example Mapping. Each Rule maps
to an acceptance criterion; scenarios use concrete examples. These get verified and refined
after implementation — the feature doc holds the verified version.

### Rule: Schema saved by a current Deploy is read

```scenario
Scenario: A project on Deploy 17.3.1 is read
  Given a project whose Alert Banner element type is saved by Deploy 17.3.1
  When a developer asks for the Alert Banner's guide
  Then its fields are read as they are for a project on Deploy 17.2.1
  And no file is reported as skipped for its format version
```

### Rule: A component that will never need a guide can be ignored

```scenario
Scenario: An ignored component leaves the audit's gaps
  Given the Spacer block has no guide
  And a developer has ignored the Spacer block
  When the guide audit runs
  Then the Spacer block is listed among ignored components
  And it is not listed as undocumented
```

```scenario
Scenario: An ignored component's existing guide is not an orphan
  Given the Spacer block has a guide
  And a developer has ignored the Spacer block
  When the guide audit runs
  Then the Spacer block's guide is not reported as stale or as naming nothing
```

```scenario
Scenario: Ignoring is a change to the guides page, approved first
  Given nothing is ignored
  When a developer asks to ignore the Spacer block
  Then the change to the guides page's ignore list is shown
  And nothing is written until the developer approves it
```

```scenario
Scenario: A guide is not generated for an ignored component
  Given the Spacer block is ignored
  When a developer asks for the Spacer block's guide
  Then the spell stops and says the Spacer block is ignored
  And nothing is generated or written
```

```scenario
Scenario: Stopping ignoring brings the component back
  Given the Spacer block is ignored and has no guide
  When a developer stops ignoring it and the audit runs
  Then the Spacer block is listed as undocumented
```

### Rule: A stale guide that is already correct can be marked as up to date

```scenario
Scenario: Marking changes only the stored signature
  Given the Alert Banner guide is reported stale after a content sync
  When a developer marks it as up to date and approves
  Then only the guide's stored signature changes, to the Alert Banner's current one
  And the next audit reports the Alert Banner guide as current
```

```scenario
Scenario: Only a stale guide can be marked
  Given the Card block has no guide
  When a developer asks to mark the Card block's guide as up to date
  Then the request is refused, saying the Card block has no guide
  And nothing is written
```

```scenario
Scenario: A guide with other unpublished changes is saved but not published
  Given the Alert Banner guide is published and has another unpublished change
  When a developer marks it as up to date and approves
  Then it is saved and not published
  And the report says it was not published because of the other change
```

### Rule: Regeneration rewrites AI text nobody edited, and keeps everything else

```scenario
Scenario: A note still as generated is rewritten
  Given the Alert Banner guide's note on Level is exactly as the spell wrote it
  And the Alert Banner block has gained a Dismissible toggle
  When the guide is regenerated
  Then the difference shows a new note on Level and a new Dismissible row
  And after approval both are written
```

```scenario
Scenario: A note edited by one word is kept
  Given a content editor changed one word of the Alert Banner guide's note on Level
  When the guide is regenerated
  Then the note on Level is left exactly as the editor wrote it
  And no replacement is proposed
```

```scenario
Scenario: A guide written before fingerprints keeps all its prose
  Given the Alert Banner guide was generated before fingerprints were recorded
  And the block has gained a Dismissible toggle
  When the guide is regenerated
  Then the purpose sentence, the when-to-use section and every existing note are kept
  And only the Dismissible row, with its note, is added
```

```scenario
Scenario: Text edited between the plan and the write is kept
  Given a regeneration plan rewrites the Alert Banner guide's purpose sentence
  And a content editor changes that sentence before the developer approves
  When the developer approves
  Then the editor's sentence is kept
  And the report names it as skipped because it changed after the plan
```

### Rule: The spell and a dashboard agree about every guide

```scenario
Scenario: Reference output pins a port to the script
  Given a fixed set of schema files holding an Alert Banner block and a Home page type
  When the script writes its reference output for them
  Then the output includes each component's signature, the inventory, the audit and a plan
  And a port given the same files can be tested against that output
```

### Rule: A project can build a dashboard from the blueprint without learning the client's details

```scenario
Scenario: The blueprint names no client
  Given the new guide-generator reference
  When the contract check scans it for client names, the authoring organization, and email domains
  Then it finds none
```

## Open Questions

- **Where fingerprints live.** Recommended: on the guide page, in a read-only field, so they travel
  with the content and both tools read the same record. The client's dashboard keeps them in a
  per-environment store instead, which is why a guide moved from another environment loses its
  protection there. Confirm the page.
- **What a fingerprint covers.** A hash of the text after the rich text editor's normalization, or
  of the exact stored value? The first avoids false "edited" readings; the second is simpler and
  errs safe.
- **Commands.** Ignore, stop ignoring and mark up to date as new arguments to `/guide` (for example
  `--ignore <alias>`, `--unignore <alias>`, `--mark-current <alias>`), or as a separate spell?
  Recommended: arguments, since each is a small write against the same guide set.
- **Global blocks.** The client's dashboard lists reusable blocks stored as documents separately
  from element-type blocks, classified by name and a setting. Is that general enough to bring in,
  or a later increment?
- **Deploy 17.0.1.** The demo project's files declare 17.0.1, which the script skips. Measure and
  accept it here too, or leave it?
- **The client project.** Its dashboard keeps fingerprints per environment and calls the ignore
  field by its own name. Does it adopt this repo's shapes later, as the test-content builder will,
  and is that recorded as a follow-up in the feature doc?

## Testing Guidelines

Meaningful tests for the cases below, without going too heavy:

- 17.3.1 is accepted: a fixture declaring it is read; one declaring an unknown version is still
  skipped and named.
- Ignore list: the audit with an ignored undocumented component, an ignored component with a guide,
  an ignore entry naming nothing, and a guides node with no ignore field.
- Mark up to date: refused for each non-stale status; the plan for a stale guide changes only the
  signature.
- Fingerprints: the plan's three states (as generated, edited by one word, no record) for the
  purpose sentence, the when-to-use section and a row note; a renamed field's note follows its row.
- Reference output: the command that writes it is deterministic (run twice, identical output).
- The contract check scans the new reference for client names.
