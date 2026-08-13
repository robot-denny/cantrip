# Recommendation — where C# knowledge belongs, and what to change before it ships

**Status:** decisions made (§9). Nothing built yet.
**Role:** this increment's discovery, read by `/spec`. Not produced by `/explore` — it began as a
review of an external standards file and accumulated decisions, so it sits here rather than in `notes/`.
**Input:** a colleague's `csharp-standards.md`, used as an always-on rules file on .NET projects.
**Date:** 2026-08-11, decisions 2026-08-13

---

## 0. One correction to the framing

The premise was that C# knowledge was *lost* when `/code-review` was made technology-agnostic. Checked
against the reference instance in the client project — its `umbraco-code-reviewer` agent — that is not
quite what happened. The entire C#-specific content of that agent was one line:

> **C#**: PascalCase for types/methods, camelCase for locals; the codebase is `var`-dominant — match it.

Core's `code-reviewer` preserved the durable half of that as "match the file's dominant style rather than
importing your own." Neither source repo carried substantive C# standards anywhere — not in an agent, not
in `CLAUDE.md`, not in an L2 slot. `git log -S` over this repo confirms no such content was ever committed
and then generalized away.

So this is **new knowledge entering the toolkit, not restored knowledge**. That matters for two reasons:

- It has never been exercised through a Cantrip review, so it gets the scrutiny a new unit gets, not the
  lighter touch a restoration would get.
- The gap it fills is real and larger than described: the toolkit currently has **no per-file C# guidance
  at all**, only repo-level .NET audit posture (see §5).

Everything below proceeds on that footing.

---

## 1. Review of the file

The content is good and worth having. The problem is that it is three different kinds of statement wearing
one voice, and the layer contract treats them very differently.

### Bucket A — durable technology facts (belongs in L1)

These are true of the language or platform, explain a real failure when broken, and outlive a project:

| Rule | Why it earns its place |
|---|---|
| Structured logging via `ILogger`, no interpolated message | Interpolation collapses the named fields, so the log becomes unqueryable; it also formats eagerly, even when the level is disabled |
| No try/catch solely to log; none solely to rethrow | `throw ex;` resets the stack trace; log-and-rethrow duplicates every entry up the chain |
| `CancellationToken` at boundaries, async all the way down | Sync-over-async starves the thread pool and deadlocks in contexts with a synchronization context |
| Prefer `System.Text.Json`; camelCase attributes on DTOs, paired with Newtonsoft attributes where both are present | A DTO serialized by two libraries with one set of attributes changes shape depending on which one runs |
| `<Nullable>enable</Nullable>`, `string?` for nullable | Nullability is a compile-time contract; half-enabled it warns without protecting |
| Records for immutable data | Value equality and `with` are the point, not brevity |
| Collection expressions, target-typed `new()` (C# 12+) | Real modern syntax, but needs version scoping — see §2 |
| Naming by code element (PascalCase types/methods, camelCase params/locals, `_` private fields, `Async` suffix) | These are .NET-wide conventions, not preference |
| No magic strings — named consts or enums | Durable |

### Bucket B — house style the project owns (belongs in L2, not L1)

Defensible choices, but choices. If they ship as L1 facts, the pack starts overruling projects that
decided differently — which is exactly the failure the layer contract exists to prevent.

- **Block-scoped namespaces.** See §2 — this one is more than a preference, it inverts the platform default.
- **`sealed` by default.** Real devirtualization benefit, but it breaks mocking of concrete classes and
  proxy-based ORM patterns. A policy, and one with a cost.
- **Explicit types over `var`.** Directly contradicts core's `code-reviewer` ("match the file's dominant
  style") and both source repos, which are `var`-dominant. As an L1 fact this makes the pack fight the code.
- **Member ordering**, **using placement**, **one type per file**. Universal enough to state, but
  `.editorconfig` and StyleCop own them (see Bucket C).
- **FluentValidation for DTO validation.** A library choice. *"Validate DTOs at the boundary"* is the
  durable fact; *which library* is not.
- **The "3+ uses" helper-method threshold.** A useful heuristic with an arbitrary number.

### Bucket C — mechanically enforced already

Casing, using placement, member ordering, and namespace style are all enforced better by `.editorconfig`
plus Roslyn analyzers than by an agent re-checking them from prose. Spending skill budget here buys
nothing and risks the agent "fixing" formatting the formatter owns.

**Recommendation:** keep the naming table (it is cheap and it grounds review findings), but add a pointer
that where an `.editorconfig` exists it is the authority and the agent should not fight it. That single
sentence prevents a whole class of churn.

### Defects to fix regardless of placement

1. **`path: "*.cs"` is not a skill trigger.** Claude skills load on `name` + `description`. There is no
   path-glob mechanism. As written this file has no `name:` and no `description:`, so it fails contract
   check 6 and — more importantly — would never load. This is the single highest-impact fix.
2. **`.GetAwaiter().GetResult()` as the deadlock escape hatch is wrong.** It blocks identically to
   `.Result`; it only avoids the `AggregateException` wrapping. It does not prevent the deadlock the
   surrounding sentence claims it prevents. This also **contradicts a file already in the toolkit** —
   `architecture-audit/references/dotnet-hygiene.md` lists `.Result` / `.Wait()` as a smell to flag. Two
   installed files disagreeing is worse than either being absent.
3. **Public fields PascalCase** normalizes public fields. The durable rule is *prefer properties*; the
   casing of a public field is a detail of something to avoid.
4. **`s_` static prefix** is the `dotnet/runtime` repo's internal convention, not general .NET guidance.
   Fine as house style; not a fact.
5. **"Exactly one primary type per file"** bans nested types, `file`-local types, and private companions.
   Soften to *one public type per file, named for the file*.
6. **`IsNullOrWhiteSpace` always over `IsNullOrEmpty`** is a good default, not an always — where
   whitespace is significant the two differ meaningfully. State it as a default with its exception.
7. **Mojibake.** `Constants â Fields â Constructors` — the arrows are corrupted and would ship that way.
8. **No worked examples.** For the handful of rules where the wrong form is plausible — structured
   logging, log-and-rethrow, collection expressions, paired JSON attributes — a two-line before/after is
   worth more than the rule sentence. This is the "examples" half of the original concern, and it is
   genuinely missing.
9. **Voice.** ~60 rules of `ALWAYS` / `NEVER` with no *why*. `skill-creator` calls this out explicitly:
   caps-lock imperatives are a yellow flag, and explaining the reason produces better adherence than
   asserting the rule. Cantrip's own house voice (`tdd-principles`, `umbraco-17-review-rules`) is
   why-first prose. This needs rewriting into that voice, not pasting.

---

## 2. The namespace claim, called out on its own

`ALWAYS use block-scoped namespaces` is presented as a *modern* standard. It is the opposite: file-scoped
namespaces arrived in C# 10, the .NET SDK templates have emitted them since .NET 6, and they are the
documented modern form. Most repos' `.editorconfig` encodes that via
`csharp_style_namespace_declarations`.

Shipped as an L1 fact, this would make an agent rewrite conforming, template-default code into the
non-default form, and fight the project's own `.editorconfig` while claiming to be modernizing it.

**Not a reason to drop it** — an org may genuinely prefer block-scoped for its diff behavior. It is a
reason it must live in L2 as a stated preference, where a project can hold it or not, rather than in L1
as a fact about the language.

---

## 3. Placement: a new L1 `dotnet` pack

### Not core (L0)

Contract check 8 blocks the literal strings `dotnet` and `c#` in `skills/core/`. That gate is not
incidental — core asks for a *kind* of guidance and lets skill discovery route it (ADR 0003). A C#
standards file in core would break the honest "core works on any project" baseline.

### Not the `umbraco-17` pack

C# and .NET apply to every .NET project, Umbraco or not. Folding this in would:

- make it invisible to a .NET project that installs no CMS pack — the majority case;
- put language-lifetime content behind a CMS-version-scoped update cadence;
- mean a C#-only bugfix ships as an Umbraco pack release.

### Recommended: `skills/dotnet/`, sibling to `skills/umbraco-17/`

Per ADR 0003 this costs **nothing in core** — no L0 file changes, because L0 already asks for the kind of
guidance rather than naming a pack. Two units, mirroring the split the `umbraco-17` pack already proves:

```
skills/dotnet/reference/
├── dotnet-conventions/SKILL.md      what must be true when authoring C#
└── dotnet-review-rules/SKILL.md     what to look for in a C# diff, with severities
```

The second is what actually closes the gap that prompted this. `umbraco-17-review-rules` is the working
model: prose that says *what to look for* and assigns Blocker/Major, deferring the *why it is true* to a
companion file rather than restating it.

**A third unit, `dotnet-starter-facts`, is deliberately not proposed yet.** The `umbraco-17` pack needs one
because CMS behaviors are version-volatile and need `applies:` / `verified:` provenance. Language-spec
truths mostly are not. Version scoping can sit inline (`C# 12+`, `.NET 8+`) until the set of
version-conditional claims grows enough to earn its own file.

### Rejected alternatives

| Option | Why not |
|---|---|
| Extend core's `code-reviewer` agent with C# rules | Check 8 forbids it, and it is the wrong layer — an agent is L0 |
| One combined `dotnet` unit instead of two | Authoring and reviewing load at different times; one file means every review pays for the authoring half. The pack's existing split exists for this reason |
| Leave it as an L2 project skill | Then every .NET project hand-maintains a copy, which is the hand-porting problem the toolkit exists to end |
| A `csharp` pack rather than `dotnet` | Half the content is platform, not language — `ILogger`, `CancellationToken`, `IOptions`, csproj properties. `dotnet` is the honest scope |

---

## 4. The pack needs one new heading — corrected

An earlier draft of this section claimed no new slot was needed, on the grounds that two homes already
exist and are owned:

- **Authoring** → `.agents/config/conventions.md` → `## Implementation rules`, owned by
  `/implement-step`. The demo project's copy already holds exactly this kind of content — TWAE, nullable,
  "match the file's dominant style (`var`-heavy)".
- **Review** → `.agents/config/reviewer-rules/code.md`, owned by the `code-reviewer` agent.

**That was wrong, and the reason matters.** Those two homes do not share a fact. `code-reviewer` reads
*only* `reviewer-rules/code.md` — verified, it declares no other slot — so a preference recorded under
`## Implementation rules` reaches the implementer and is **invisible to the reviewer**. The failure is
concrete and self-inflicted: `/implement-step` writes code to the stated preference, then review flags
that same code against its own defaults.

The obvious repair — have the pack declare the existing heading too — is blocked by the gate. Check 9 keys
on the `**Slot:**` line text, so any second declarer must reproduce `/implement-step`'s fallback verbatim:
*"rely on the project's guidance files, which the envelope already points the worker at. Do not invent
rules."* That is authoring-shaped and meaningless to a reviewer.

**So the pack declares its own heading** — `.agents/config/conventions.md` → `## .NET style decisions` —
distinct from `## Implementation rules`, with one fallback that suits both consumers. The heading is new;
the file is not, which keeps the project's configuration surface in one place.

**Both consumers reach it through the pack skill rather than through their own slots.** `code-reviewer`
already carries the instruction to consult installed stack-pack review guidance before reporting, and a
worker writing C# loads `dotnet-conventions` by description. One declaration, one fallback, two consumers,
no duplication — which is what *one slot, one point of authority* actually asks for.

Worth recording the miss alongside the fix: the flaw was reasoning about slot *ownership* without checking
slot *reach*. Two owned homes is not the same as the fact arriving at both consumers, and no gate check
catches a fact that reaches only half of its audience.

What the pack contributes beyond the slot is the **dividing line** — a short table, in the shape
`tdd-principles` uses, saying which bucket each kind of statement falls into and where the other buckets
live. That is the part that keeps the pack from drifting into house style over time.

### The resolution order — what makes an asserted default safe

Baking best practices into L1 only avoids contradictions if the pack says plainly that its defaults yield.
Without this, a reviewer flags block-scoped namespaces in a repo that chose them deliberately, which is
the exact failure mode this whole design is trying to avoid.

So the pack states, once, that its asserted conventions resolve in this order:

1. **`.editorconfig`**, where it speaks. Machine-checkable and already in the repo — for namespace style
   that is literally `csharp_style_namespace_declarations`, so the agent can read the answer rather than
   assume it.
2. **A stated project decision** in `conventions.md` → `## Implementation rules`.
3. **The pack's default**, when neither of the above answered.
4. **The file's dominant style**, when even that does not fit.

The pack's asserted items are therefore *defaults, not mandates*. A project keeping block-scoped
namespaces states it once — or more likely already has it in `.editorconfig` — and no reviewer argues.

### Detection: the pack supplies the recipe, core supplies the mechanism

`/setup` fills pack slots by the same detect → mine → ask tiers it uses for core slots (Step 2, "read
them from the pack, do not hardcode them"). But its *detection* table is a core file, and check 8 forbids
core from naming `.cs`, `dotnet`, or `c#` — so **core cannot know how to detect whether a codebase is
`var`-dominant.** Nothing currently carries that recipe from the pack to setup, so tier 1 silently
degrades to tier 3 and setup asks a question it could have read.

The fix is an optional fourth line in the slot form, declared by the pack and honored by `/setup`:

```markdown
**Slot:** `.agents/config/conventions.md` → `## Implementation rules`
**If empty:** match the file's dominant style. Where an `.editorconfig` sets the rule, it is the
authority. Do not assert a convention you cannot evidence.
**Detect:** the ratio of `var` to explicit declarations across the project's C# files; whether types
carry `sealed`; the `csharp_style_*` keys already set in `.editorconfig`.
```

Precedent for a pack-declared, self-describing marker that `/setup` collects without knowing the
technology already exists twice: `**Companion:**`, and `architecture-audit`'s own "Detection recipes"
sections. Verified against the gate — check 4 requires `**If empty:**` within three lines of `**Slot:**`,
so a `**Detect:**` line after it does not break the pairing.

---

## 5. Resolving the overlap with `architecture-audit`

`skills/umbraco-17/reference/architecture-audit/references/dotnet-hygiene.md` already covers async and
`CancellationToken`, structured logging, nullable, secrets in config, and NuGet pinning. Left unaddressed,
the new pack would restate it — and, as §1 defect 2 shows, restate it *inconsistently*.

The honest dividing line:

| Concern | Where |
|---|---|
| Is this repo's .NET foundation sound? Repo-level signals, detection recipes, lifecycle-staged priorities | `architecture-audit` |
| Is this file, this method, this diff correct and idiomatic? | the `dotnet` pack |

Both new units should state that line explicitly and defer rather than repeat.

### The file stays where it is — decided

Moving `dotnet-hygiene.md` into the `dotnet` pack was considered and rejected on a mechanical ground that
only shows up when you read how it is wired: it is **Pillar 1 of a seven-pillar scored audit**, and its
1–5 scoring anchors live in `scoring-rubric.md`, which stays in the Umbraco pack. Moving the file splits
one pillar's signals from that pillar's anchors across two packs, and an Umbraco project without the
`dotnet` pack installed would run an audit whose rubric still scores Pillar 1 while its signal reference
has disappeared. A silently under-covered scored pillar is worse than the duplication.

**Resolve by ownership instead.** The `dotnet` pack owns the *rule*. `dotnet-hygiene.md` keeps its own
genuinely different job — repo-level signals, detection recipes, lifecycle-staged priorities, and the
evidence a score rests on — and defers where it currently restates a rule. Its existing closing section,
"cite the canonical Microsoft Learn doc", is already the fallback for when the `dotnet` pack is absent,
which is rung 2 of ADR 0006.

**The concrete contradiction needs no change in the Umbraco pack.** `dotnet-hygiene.md` is already
correct — it lists `.Result` and `.Wait()` as smells to flag. The wrong claim is the incoming
`.GetAwaiter().GetResult()` line (§1 defect 2), so the fix is not carrying it over.

---

## 6. Drafted descriptions

Per ADR 0003's recorded consequence — *"a pack skill with a weak description silently fails to load, and
the symptom is a plan that is merely generic rather than an error"* — these are the highest-leverage lines
in the whole proposal. Both are deliberately a little pushy, and both name the case where the user never
says "C#".

**`dotnet-conventions`**

> Modern C# and .NET authoring conventions — naming and casing by code element, async and
> `CancellationToken` discipline, structured logging with `ILogger`, `System.Text.Json` serialization and
> camelCase DTOs, nullable reference types, and the C# 12+ syntax that is now the default (collection
> expressions, target-typed `new`, primary constructors, records). Consult whenever writing or refactoring
> a `.cs` or `.csproj` file, or planning a step that adds a service, DTO, endpoint, controller, or record —
> including when the request only says "add a service" and never mentions C# or .NET at all.

**`dotnet-review-rules`**

> What to check when reviewing a C# or .NET diff — the rethrow and swallowed-exception patterns that
> destroy stack traces, interpolated log messages that defeat structured logging, async paths that block
> or drop cancellation, unvalidated payloads on endpoints, nullability gaps that warn without protecting,
> and how to tell a real defect from a house-style preference the project owns rather than the toolkit.
> Consult when reviewing a diff that touches `.cs`, `.csproj`, or `appsettings` files.

Both need trigger evals before landing (§8).

### A discovery risk worth naming

In an Umbraco repo, a C# diff should load **both** `dotnet-review-rules` and `umbraco-17-review-rules`.
Neither description should name the other pack — packs stay mutually anonymous for the same reason L0
does — so the load has to come from the descriptions being about genuinely different things: language and
platform mechanics versus CMS rendering surfaces. Worth checking directly in the evals, because the
failure is silent.

---

## 7. Voice: one worked rewrite

The transformation the whole file needs, on the rule most likely to be violated.

**Before**

> - ALWAYS use ILogger with Structured logging to log, no string interpolation and no other logging methods.

**After**

> **Log with named placeholders, not interpolation.** `logger.LogInformation("Order {OrderId} failed
> after {Attempts}", orderId, attempts)` writes `OrderId` and `Attempts` as queryable fields;
> `logger.LogInformation($"Order {orderId} failed after {attempts}")` writes one opaque string, and the
> data you actually wanted to filter on is gone by the time you need it. Interpolation also formats
> eagerly — the cost is paid even when the level is disabled and the message is discarded.
>
> The same reasoning rules out `Console.WriteLine` in a production path: it has no level, no scope, and no
> structure, so nothing downstream can route or filter it.

Same rule, roughly triple the length, and it tells the agent enough to make a correct call on a case the
rule never anticipated — which is the whole return on the extra words.

---

## 8. What landing this requires

Repo chores, verified against the gate rather than assumed.

**New pack (L1):**

- [ ] `skills/dotnet/reference/{dotnet-conventions,dotnet-review-rules}/SKILL.md` — directory name must
      match `name:` (check 6), no `disable-model-invocation` on a `reference/` unit (check 5), description
      ≥ 40 chars (check 6)
- [ ] `dotnet-conventions` carries: the asserted defaults, the single consolidated "project decides"
      section, the resolution order (§4), the `**Slot:**` / `**If empty:**` / `**Detect:**` declaration,
      and the dividing line against `architecture-audit` (§5)
- [ ] `dotnet-review-rules` defers to that one section rather than repeating it, and maps its findings
      onto the existing Blocker/Major/Minor/Nit scale

**Core mechanism (L0) — small, and it is what makes the `/setup` inference actually happen:**

- [ ] `docs/contract.md` — document the optional `**Detect:**` line in the reference pattern
- [ ] `skills/core/spellbook/setup/SKILL.md` — one sentence in Step 2 to honor a pack's `**Detect:**`
      before asking, plus one technology-agnostic row in the Step 1 table: where a formatter or editor
      config encodes mechanical style, it is authoritative where it speaks
- [ ] Confirm the added wording trips no check-8 technology name

**Documentation:**

- [ ] README: install line for the new pack, and fix "A stack pack adds its own spells on top" — which
      implies packs add spells, whereas this one adds only references
- [ ] `CHANGELOG.md` entry
- [ ] ADR covering both decisions: why `dotnet` is a peer of `umbraco-17` rather than inside it, and why
      the slot convention gained a `**Detect:**` line
- [ ] `scripts/check-contract.sh` passes
- [x] Trigger evals per `skill-creator` — run 2026-08-13, results in §10. Co-load risk retired

**Not required**, checked rather than assumed: checks 11 and 13 (self-hosting symlinks, install-checker
roster) are scoped to `skills/core/` only, so a new pack does not touch them. `scripts/check-install.sh`
needs no roster change — and per §4 the new `## .NET style decisions` heading lives in an existing config
file, so nothing about the install layout changes either.

---

## 9. Decisions

Settled 2026-08-13. The governing principles were stated as: **avoid contradictions**, **consolidate
rather than segregate tailorable style**, and **bake broadly-applicable best practices into the skills.**

| # | Question | Decision |
|---|---|---|
| 1 | Two units or three? | **Two.** Version scoping stays inline; `dotnet-starter-facts` is not created until the set of version-conditional claims earns a file |
| 2 | Where does the pack stop asserting? | **It asserts platform defaults, and consolidates the genuinely contested items into one "project decides" section** — plus the resolution order in §4, without which the assertion half is a contradiction machine |
| 3 | Where do the org's style answers live? | **Nowhere in this repo.** `/setup` detects what it can and asks for the rest, per project. No org answers ship, so check 1b has nothing to police |
| 4 | Move `dotnet-hygiene.md`? | **No** — it is Pillar 1 of a scored audit whose anchors stay in the Umbraco pack. Resolve the overlap by ownership instead (§5) |
| 5 | What happens when the pack is *not* installed? | **Generalize three failure modes into core, keep the idiom in the pack** (§9a) |

### 9a. Decision 5 — the absence case, and what it moves into core

A pack is optional, so four states have to work. The one that matters is not hypothetical: **adding a pack
is a manual `npx skills add`, so every existing Umbraco project sits in state 2 until someone runs it.**

| State | Consequence |
|---|---|
| Core only | Most degraded. Works — `code-reviewer` states outright that absent stack guidance is not an error |
| Umbraco pack, no `dotnet` pack | CMS rules present, C# rules absent. **The default state of every current install** |
| `dotnet` pack, no Umbraco pack | Plain ASP.NET project. Correct by design — this is the portability case |
| Both installed, neither triggers | A routing failure, not an absence failure. Addressed by trigger evals (§8) |

Nothing breaks in any state; every slot has a fallback. But a grep of `skills/core/` shows what states 1
and 2 genuinely miss on a C# diff. Core already covers swallowed exceptions, blocking calls in async
contexts, and missing null checks. It contains **no occurrence of "stack trace", "rethrow", or
"interpolat"**, and "cancel" appears only in `perf-reviewer`, not the quality reviewer.

So a rethrow that destroys the stack trace, and a log call that interpolates away its structured fields,
draw a finding from nobody — today, and permanently, unless core changes.

**None of those three are C# facts.** Each is a language-agnostic failure mode with a C# expression:

| Failure mode → core `code-reviewer` | Idiom → the pack |
|---|---|
| a rethrow that discards the original stack trace or error cause | `throw ex;` rather than `throw;` |
| a log call that interpolates values into the message instead of passing them as structured fields | `$"..."` rather than named placeholders |
| long-running work with no way for the caller to cancel it | a missing `CancellationToken` parameter |

Java, Python, and JS all have all three. Putting the failure mode in core and the idiom in the pack gives
better degradation in states 1 and 2, extends the benefit to every other language, and makes the pack
**smaller** — it names the C# form instead of arguing for why it matters.

This is the `tdd-principles` split applied to review: **core owns what makes something a defect; a pack
owns what that defect looks like in one language.** Worth applying deliberately, since losing that same
split on the TDD side is what prompted this work.

Constraint on the wording: check 8 forbids technology names in L0, so the core bullets must not name
`ILogger`, `CancellationToken`, or C# itself. They describe the failure, not the API.

What correctly stays pack-only: collection expressions, `IsNullOrWhiteSpace`, primary constructors,
`sealed`, record types, `System.Text.Json` attributes. A core-only .NET repo does not get these, and
should not — core carrying them would misrepresent what core is.

**Consequence for release:** since `/setup` cannot advertise a pack it does not have, the README install
line and the CHANGELOG entry are the only mechanism telling an existing project the pack exists. That
moves both from housekeeping to load-bearing.

Two consequences worth carrying forward, because both are conversations rather than code:

- **The pack contradicts the source file on two rules, and not in the same way** — the asymmetry matters:

  | | Platform position | What the pack does | Where the answer comes from |
  |---|---|---|---|
  | `var` vs explicit type | none — style guides genuinely disagree | asserts nothing; names it a project decision | `.editorconfig`, then L2, then the file's dominant style |
  | Namespace style | file-scoped, C# 10+, the SDK template default | **asserts file-scoped as its default** | `.editorconfig`, then L2, then the pack's default |

  So namespace style is not relocated to L2 — it becomes an L1 default that *yields*. The distinction is
  between the pack having no position and having one that can be overruled, and it is what lets a greenfield
  repo with an empty slot get the right namespace answer while getting no argument about `var`.

  Either way the colleague keeps his preference by stating it once, and most likely already has in
  `.editorconfig`. Worth telling him directly rather than letting him find out through a review finding.

- **The resolution order arbitrates taste, not failure modes.** It governs how code is *shaped* —
  declaration style, namespace form, ordering, sealing. It is not a general override chain for the pack's
  correctness content: an interpolated log message still loses its fields, `throw ex;` still resets the
  stack trace, an unvalidated payload is still unvalidated. Those must not be written as defaults that
  yield, or the order becomes a way to opt out of correctness.
- **Decision 3 widened the change into core.** Choosing "`/setup` infers" only pays off if the inference is
  written down somewhere core can reach without naming a technology, which is what the `**Detect:**` line in
  §4 is for. That is the one part of this proposal that touches L0.

---

## 10. Trigger evals — run, and the design assumption holds

Run 2026-08-13 against a throwaway repo with the **full 26-skill roster installed** (all of core, the
`umbraco-17` pack, and the two draft units) plus a real staged C# diff carrying three of the defects the
pack would own. Detection reads the `stream-json` transcript for `Skill` invocations and for any direct
`Read` of a `SKILL.md`, since a skill loaded by reading its file is still loaded.

| Group | n | Result |
|---|---|---|
| Authoring — expect `dotnet-conventions` | 8 | **8/8** |
| Review — expect `dotnet-review-rules` | 6 | **6/6** |
| Both packs co-load — the silent-failure case | 4 | **4/4** (at a realistic turn budget) |
| Near-miss negatives — expect neither unit | 8 | 7/8, and the miss is a mislabelled expectation |

**The co-load risk did not materialize.** A C# diff in an Umbraco repo loads `dotnet-review-rules` *and*
`umbraco-17-review-rules` together, every time. That was the one assumption the whole two-pack design
rested on, and it survives.

**The control arm settles the causal question.** Re-running the same four queries with the two draft units
*removed* loaded `umbraco-17-review-rules` in 3 of 4 — **fewer** than the 4 of 4 it managed with the drafts
present. So adding the `dotnet` pack does not crowd the Umbraco pack out of a review; the sharper review
framing appears to help both fire.

### The methodological trap, recorded because it will recur

A first pass capped runs at 5 turns and scored co-load at **2/4**. That produced a confident, wrong
diagnosis — that `umbraco-17-review-rules` scopes itself to rendering vocabulary and therefore abandons
service-layer C#. Raising the cap to 12 turns took the same queries to 4/4 with no wording change
anywhere. **The rendering-scope explanation is retracted; the data never supported it.**

The lesson is specific and worth carrying into the next pack's evals: **an agent orients before it routes.**
Several runs spent 6–10 turns on `Bash` and `Read` before invoking any skill, so a low turn cap measures
*how fast* a skill is reached, not *whether* it is reached — and reports the difference as a triggering
defect. Give trigger evals room to finish, and check `stop_reason` before believing a miss.

### Caveats worth stating

- **n is small** — 4 queries in the critical group, 26 overall. Enough to retire the co-load risk as the
  top concern, not enough to call the descriptions optimal.
- **The one negative "failure" is mine, not the description's.** `neg-2` asks to fill out a thin
  `.editorconfig` for a .NET project, and `dotnet-conventions` fired. Given that `.editorconfig` is rung 1
  of the resolution order (§4), consulting .NET conventions while writing one is arguably correct. Rescored
  as a pass rather than tuned against.
- Two runs hit the raised cap, but both had already loaded their skills, so their verdicts stand.

### What this changes in the plan

Nothing structural — the two-unit split and both drafted descriptions (§6) survive unchanged. The `**Detect:**`
mechanism, the resolution order, and decision 5 are all untouched by these results. The §8 eval item is
satisfied for the co-load case; a broader trigger sweep remains optional polish rather than a gate.

**Harness kept** at `scratchpad/trigger-eval/` — `evals.json`, `run.sh`, `run2.sh`, `score.py`. Reusable
for the next pack by swapping the skill directories and the eval set.
