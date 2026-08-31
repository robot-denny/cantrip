# Cantrip — spell card content

Card content for a flashcard deck teaching the Cantrip toolkit. **One card per unit**: 30 cards, 14
spells and 16 references. Every fact here is drawn from the units themselves; nothing is invented.

This file is content only. Formatting, layout, and card art are the reading agent's call.

**Basis, and when to regenerate.** Written against the 30 units in `skills/` as of `1df963f`
(2026-08-31). The deck is a snapshot: a new spell or reference means a missing card, and nothing here
will notice. A `/styleguide` spell is in flight for the `umbraco-17` pack and will take the count to
31, so check `skills/` against the card list before treating this as complete.

---

## How to read this file

Each card is one `###` heading — the card title is the unit's invocation name (`/spec`) or its
reference name (`workflow`). Under it, a fixed set of labelled fields. **Fields are optional except
`Type`, `Group`, and `Does`**; when a field is absent, that unit has nothing true to put there — do
not fabricate a value to balance the layout.

| Field | Card region | Holds | Cap |
|---|---|---|---|
| `Type` | header badge | `Spell` (you cast it) or `Reference` (the model reaches for it) | one word |
| `Group` | header badge / deck suit | Core spellbook · Core reference · umbraco-17 · umbraco-cloud · dotnet | — |
| `Cast` | stat block | exact invocation, spells only | one line |
| `Triggers` | stat block | when the model reaches for it, references only | one line |
| `Needs` | stat block | prerequisites — input artifact, slot, credentials | one line |
| `Leaves` | stat block | what persists after it runs | one line |
| `Does` | body | what it does and when to use it | 2 sentences, ≤40 words |
| `Modes` | secondary body | flags and variant behaviours | ≤2 lines |
| `Watch for` | callout | the one thing newcomers get wrong | one line |
| `Then` / `Pairs with` | footer | the suggested next spell, or related units | one line |

Two structural facts worth surfacing on the card faces somehow, because they are the toolkit's whole
posture:

- **Spells are invisible to the model.** They run only when a person types `/<name>`. No spell ever
  invokes another — the `Then` field is a suggestion, which is what makes this a toolbox and not a funnel.
- **References are never invoked.** They load when their description matches the work in front of the
  model. Nothing to memorise; the card is so you recognise the opinion when it shows up.

---

## Deck dividers

Five group cards, if the deck wants them — text for the back of each.

- **Core spellbook** — Ten spells. Eight are the workflow chain, two are configuration. Cast by name, never automatically.
- **Core reference** — Six opinions the toolkit holds. You never cast these; the model reaches for them.
- **umbraco-17** — Optional pack, pinned to the CMS major. Six references, three spells.
- **umbraco-cloud** — Optional pack for Umbraco Deploy. Applies to any licensed install, not only Cloud.
- **dotnet** — Optional pack for C# and .NET, CMS or not. Three references, no spells.

**The chain, for the box lid:**

```
explore → spec → plan → implement-step → feature → code-review → commit-message
                                            ↑
                      retrofit (out-of-flow entry) ┘
```

**Five cards for a first sitting:** `/spec`, `/plan`, `/implement-step`, `/code-review`, `workflow`.
Everything else is either a later stage or an opinion you will meet when it applies.

---

# Core spellbook

### /explore

- **Type:** Spell
- **Group:** Core spellbook
- **Cast:** `/explore [problem or area]` — asks if you omit it
- **Needs:** a decision nobody has made yet
- **Leaves:** `_work/<slug>/discovery.md`
- **Does:** Interviews you one question at a time to *widen* the option space — frames the problem, generates and stress-tests rival options, then probes second-order effects.
- **Watch for:** it withholds its own recommendation while framing, on purpose.
- **Then:** `/spec <slug>`

### /spec

- **Type:** Spell
- **Group:** Core spellbook
- **Cast:** `/spec <short feature description>`
- **Needs:** an idea — or a discovery doc to continue from
- **Leaves:** `_work/<slug>/spec.md`, a working branch, a work-type line
- **Does:** Turns an idea into a spec with acceptance criteria and draft Given/When/Then scenarios. Classifies the work as new capability, change-to, or fix — and that decides which durable docs it earns.
- **Watch for:** only a new capability gets its own feature doc; a change folds into the existing one.
- **Then:** `/plan <slug>`

### /plan

- **Type:** Spell
- **Group:** Core spellbook
- **Cast:** `/plan <spec path | short description>`
- **Needs:** a spec, ideally
- **Leaves:** `_work/<slug>/plan.md`
- **Does:** Turns a spec into phased, test-first steps — each independently runnable in a fresh context, each with a paste-ready prompt, plus key decisions recorded so no step re-derives them.
- **Watch for:** the last step records durable behaviour; it is a spell you cast, not a step you run.
- **Then:** `/implement-step <slug> 1`

### /implement-step

- **Type:** Spell
- **Group:** Core spellbook
- **Cast:** `/implement-step <plan> <step-number>`
- **Needs:** a saved plan
- **Leaves:** the code change, plus a DONE or BLOCKED report
- **Does:** Runs one step in an isolated context so a long plan never clutters your main conversation. Enforces the plan's test-first and validation contract, then relays a short structured report.
- **Watch for:** one step per cast — the isolation is the whole point.
- **Then:** the next step; `/code-review` once the plan is done

### /feature

- **Type:** Spell
- **Group:** Core spellbook
- **Cast:** `/feature <spec path | capability | update <slug> | a code entity>`
- **Needs:** nothing but the code, in the fallback case
- **Leaves:** `_features/<area>.md` — one file per capability
- **Does:** Writes the living doc of what a capability does *now*: business-language Given/When/Then under rules, with a test coverage table. Backfills from code alone when no spec, plan, or test exists.
- **Modes:** `update <slug>` refreshes an existing doc. From-code mode is the cold-start fallback, not a shortcut.
- **Watch for:** feature docs are named for capabilities, never for the work that changed them.
- **Then:** `/code-review` before merge

### /code-review

- **Type:** Spell
- **Group:** Core spellbook
- **Cast:** `/code-review [uncommitted | branch]`
- **Needs:** a diff; reviewers linked into `.claude/agents/` for parallel runs
- **Leaves:** one merged, de-duplicated report and an ordered action plan
- **Does:** Runs the accessibility, code-quality, and performance reviewers over the same diff, then merges their findings onto one severity scale. Changes nothing without your explicit approval.
- **Modes:** `uncommitted` (default) is `git diff` plus staged. `branch` is everything since the upstream fork point, plus uncommitted and untracked.
- **Watch for:** pass `branch` when steps were committed — the default reviews only the last one and reports it clean.
- **Then:** `/commit-message`

### /commit-message

- **Type:** Spell
- **Group:** Core spellbook
- **Cast:** `/commit-message` — reads staged changes
- **Needs:** something staged
- **Leaves:** a proposed message, awaiting approval; it never commits
- **Does:** Opens with a plain-language summary of what shipped, then records briefly the reasoning a future reader could not recover from the code. Follows your project's own commit convention.
- **Then:** push — or `/retrofit` if this change skipped the flow

### /retrofit

- **Type:** Spell
- **Group:** Core spellbook
- **Cast:** `/retrofit [what you changed] [git range or ref]`
- **Needs:** a change that skipped spec → plan → implement
- **Leaves:** only what you confirm — tests, docs, feature-doc updates
- **Does:** The easy button for out-of-flow work. Reconciles your stated intent against the actual diff, runs the reviewers, surfaces edge cases, then proposes the tests and docs the flow would have produced.
- **Watch for:** run it before committing — or before pushing, if you already committed.
- **Then:** a fresh `/code-review`, then `/commit-message`

### /setup

- **Type:** Spell
- **Group:** Core spellbook
- **Cast:** `/setup` — from the project root, no arguments
- **Needs:** an installed toolkit
- **Leaves:** the `.agents/config/` slots and the workspace scaffold
- **Does:** Configures the toolkit for one project — detects what the repo already answers, mines its existing guidance files, and asks only for the residue. Reports what it could not determine.
- **Watch for:** run it once after installing, and again after adding a pack.
- **Then:** `/explore` for a new problem, or `/spec` to start an increment

### /update-toolkit

- **Type:** Spell
- **Group:** Core spellbook
- **Cast:** `/update-toolkit`
- **Needs:** git — it builds a safety net before touching anything
- **Leaves:** newer skills, plus a list of your local tailorings that were reverted
- **Does:** Wraps the skills installer behind a git guard, because the bare update overwrites local modifications with no warning. Makes every change reviewable and helps move tailoring where updates cannot reach it.
- **Watch for:** editing an installed file is a divergence, not a workflow. If tailoring needs a core edit, that is a missing slot.

---

# Core reference

### workflow

- **Type:** Reference
- **Group:** Core reference
- **Triggers:** before a spec, plan, or feature doc; when classifying work; when a change landed outside the flow
- **Holds:** the entry points, the work types, where every artifact lives, the templates
- **Does:** The spine. Explains how work flows from roadmap through feature, spec, plan, and implementation, and which durable artifacts each work type earns.
- **Watch for:** every path it names is a default, overridable through the `paths.md` slot.
- **Pairs with:** every spell in the chain

### bdd-principles

- **Type:** Reference
- **Group:** Core reference
- **Triggers:** writing or reviewing scenarios, drafting acceptance criteria, choosing domain vocabulary
- **Holds:** Given/When/Then in business language, Example Mapping, specification by example, ubiquitous language
- **Does:** Keeps scenarios about observable behaviour a stakeholder would recognise, grouped under business rules — and tells you when a scenario is really a unit test.
- **Pairs with:** `/spec`, `/feature`

### tdd-principles

- **Type:** Reference
- **Group:** Core reference
- **Triggers:** writing a test, filling a step's Test-first block, or diagnosing a test that broke with no behaviour change
- **Holds:** assert behaviour not implementation, independently-sourced expected values, one behaviour per cycle
- **Does:** What a test should *assert* so it proves something and survives refactoring. Includes what counts as a RED→GREEN signal in a project with no test harness.
- **Pairs with:** `/plan`, `/implement-step`

### reviewer-discipline

- **Type:** Reference
- **Group:** Core reference
- **Triggers:** performing a review, calibrating a finding's severity, authoring a new reviewer
- **Holds:** diff-only scope, the Blocker/Major/Minor/Nit scale, the evidence standard, the report shape — and the three reviewer agents
- **Does:** The contract all three reviewers share. It exists to stop the failure modes that make review output worthless: speculation about unseen code, invented severities, findings with no file and line.
- **Watch for:** the agents ship here but must be linked into `.claude/agents/` once, or review runs inline instead of in parallel.
- **Pairs with:** `/code-review`, `/retrofit`

### memory-discipline

- **Type:** Reference
- **Group:** Core reference
- **Triggers:** writing or reorganising agent memory; when a wrong finding keeps coming back
- **Holds:** the MEMORY.md index plus topic files, the entry format with its Why and How-to-apply lines, the three entry types
- **Does:** How an agent's persistent project memory stays small and calibrated — including recording its own false positives, so a finding you rejected once stops returning.
- **Pairs with:** the three reviewers

### design-system-authoring

- **Type:** Reference
- **Group:** Core reference
- **Triggers:** creating a project's design-system skill; when front-end work keeps drifting from your conventions
- **Holds:** find the load-bearing mechanism, write pointer-first, derive a conformance list, engineer the description
- **Does:** A skill for writing a skill. Your visual conventions are your own, so rather than ship rules you would fight, it walks you through writing down the ones you already have.
- **Pairs with:** `/plan`, the accessibility reviewer

---

# umbraco-17 pack

### umbraco-17-starter-facts

- **Type:** Reference
- **Group:** umbraco-17
- **Triggers:** writing or reviewing Umbraco code, debugging a silent failure, wondering whether behaviour is a bug or the platform
- **Holds:** Management API shapes and quirks, content-model traps where unset is indistinguishable from false, AI and Search configuration traps
- **Does:** Verified platform facts that are easy to get wrong and usually **fail silently**. Each carries what it applies to and when it was last verified.

### umbraco-17-planning

- **Type:** Reference
- **Group:** umbraco-17
- **Triggers:** planning Umbraco work — document types, element types, compositions, data types, or a backoffice extension
- **Holds:** inspect live backoffice schema before designing steps, the layer vocabulary a feature spans, the step order that usually works
- **Does:** Stack-specific planning guidance, and the router: it sends dashboards, property editors, workspaces, trees, and block views to the authoritative extension skill for each.
- **Watch for:** it routes to two companion plugin skill sets; without them its extension guidance is thinner, and it says so.
- **Pairs with:** `/plan`, `/block`

### umbraco-17-review-rules

- **Type:** Reference
- **Group:** umbraco-17
- **Triggers:** reviewing a diff in an Umbraco project
- **Holds:** CMS rendering security, null-safety and alias traps in published content, per-request cost in view-model construction, editor-authored accessibility
- **Does:** What to check that only applies because this is a CMS. Feeds all three reviewers on the same severity scale they already use.
- **Pairs with:** `/code-review`

### umbraco-17-feature-backfill

- **Type:** Reference
- **Group:** umbraco-17
- **Triggers:** documenting an Umbraco capability with no spec, plan, or tests; resolving an alias to its implementation
- **Holds:** locating the serialized schema (Deploy `.uda` or uSync `.config`), the generated model, and the Razor view; data-type UDI to readable field type
- **Does:** How to reverse-engineer behavioural documentation from Umbraco code — parsing property structure and compositions out of either serialization format.
- **Pairs with:** `/feature` in from-code mode

### umbraco-17-audit-patterns

- **Type:** Reference
- **Group:** umbraco-17
- **Triggers:** auditing or inheriting an Umbraco codebase, or comparing two solutions
- **Holds:** composition and service registration, schema-as-code discipline, content access and block patterns, decoupled-frontend readiness
- **Does:** Criteria for judging whether a site is *idiomatic*, not merely working.
- **Watch for:** judgement criteria, not a defect list — for one diff, use the review rules instead.
- **Pairs with:** `codebase-audit`

### umbraco-17-guide-scaffolding

- **Type:** Reference
- **Group:** umbraco-17
- **Triggers:** building a guides section, or deciding whether a value on a guide page may be overwritten
- **Holds:** the guide document type, the property-row element type and which of its six columns tooling may write, the stored source reference, the audit's report shape
- **Does:** The schema an editor-facing guides section needs. Ownership follows a page's provenance, not a field's declaration — which is what decides what a regeneration may touch.
- **Watch for:** you create the document types. Nothing here does it for you.
- **Pairs with:** `/guide`

### /block

- **Type:** Spell
- **Group:** umbraco-17
- **Cast:** `/block <the block, its properties, and editor experience>`
- **Needs:** an Umbraco project, and access to create the element type
- **Leaves:** an element type, its palette registration, a view, and a test that went RED then GREEN
- **Does:** Creates a block test-first — derives names and aliases, writes a failing test, creates the element type, registers it in the right palette, copies the closest existing block's view, then builds to green.
- **Watch for:** `level` is reserved, and unprefixed aliases like `content` collide — both fail silently.
- **Then:** `/feature <elementTypeAlias>`

### /guide

- **Type:** Spell
- **Group:** umbraco-17
- **Cast:** `/guide <component alias>` · `/guide --audit`
- **Needs:** a guides section that already exists, and a schema source — Deploy artifacts, uSync, or a live instance
- **Leaves:** one guide page, written only after you approve the difference
- **Does:** Writes an editor-facing guide for one component from the schema it already declares. Reads, plans, shows what a regeneration would change, asks, then writes.
- **Modes:** `--audit` reports which components have no guide, which guides name a component the project no longer holds, and which have gone stale.
- **Watch for:** nothing reaches the CMS before the ask.
- **Then:** `/guide <next alias>`

### /umbraco-edit

- **Type:** Spell
- **Group:** umbraco-17
- **Cast:** `/umbraco-edit <what to change, and on which page>`
- **Needs:** Umbraco 14+, a local URL, and OAuth client credentials in the project's env file
- **Leaves:** changed content in the CMS — with confirmation asked before anything destructive
- **Does:** Edits document properties, or invokes a configured AI agent, through the Management API. For work that would normally be a backoffice click but needs doing from the terminal.
- **Watch for:** tokens expire in 299 seconds; re-authenticate per group of operations, not once per session.

---

# umbraco-cloud pack

### umbraco-deploy-facts

- **Type:** Reference
- **Group:** umbraco-cloud
- **Triggers:** reading or diffing `.uda` files, dashboard entries that will not clear, a transfer failing on schema mismatch
- **Holds:** how `.uda` artifacts are written and read, why files and a database drift apart, which dashboard control genuinely imports, the API calls that clear stuck entries
- **Does:** Deploy schema mechanics, and the remediation paths that actually work rather than the ones that look like they should.
- **Watch for:** applies to any licensed Deploy install, not only Cloud. Cloud-only behaviours are marked as such.
- **Pairs with:** `/check-uda`

### /check-uda

- **Type:** Spell
- **Group:** umbraco-cloud
- **Cast:** `/check-uda` — before staging schema changes
- **Needs:** a Deploy project. Live OAuth credentials are optional and unlock the drift check
- **Leaves:** a risk-rated report with remediation for each finding
- **Does:** Finds Deploy schema conflicts before they reach a commit — accidental local regeneration, unpulled remote changes, both-modified files, and, with credentials, database-versus-file drift git cannot see.
- **Watch for:** Umbraco regenerates `.uda` files on startup, so a change you are about to stage may not be yours.

---

# dotnet pack

### dotnet-conventions

- **Type:** Reference
- **Group:** dotnet
- **Triggers:** writing or refactoring a `.cs` or `.csproj`, or planning a step that adds a service, DTO, endpoint, or record — even when nobody said "C#"
- **Holds:** naming by code element, async and `CancellationToken` discipline, structured logging, `System.Text.Json` and camelCase DTOs, nullable reference types, the modern syntax that is now the default
- **Does:** How to write C# that looks like current C#. It also names the style questions that belong to your project rather than the toolkit.
- **Pairs with:** `/plan`, `/implement-step`

### dotnet-review-rules

- **Type:** Reference
- **Group:** dotnet
- **Triggers:** reviewing a diff that touches `.cs`, `.csproj`, or `appsettings`
- **Holds:** rethrows that destroy stack traces, interpolated log messages that defeat structured logging, async that blocks or drops cancellation, unvalidated payloads, nullability gaps that warn without protecting
- **Does:** What to check in a C# diff — and how to tell a real defect from a house-style preference the project owns rather than the toolkit.
- **Pairs with:** `/code-review`

### codebase-audit

- **Type:** Reference
- **Group:** dotnet
- **Triggers:** asked to audit an architecture, judge whether a solution is set up right, assess a repo you are inheriting, or compare two
- **Holds:** five pillars — platform hygiene, architectural separation, documentation and onboarding, resilience and operations, suitability for agentic coding
- **Leaves:** a markdown report with prioritised P0/P1/P2 recommendations, framed for the codebase's lifecycle stage
- **Does:** A structural verdict on a whole .NET codebase, staged to where it is in its life. Can run head-to-head against a second repository.
- **Modes:** `--compare <path>` for a head-to-head, `--stage` to override the detected lifecycle stage, `--out` for the report path.
- **Watch for:** a verdict on structure, not a line-level review of a diff.
