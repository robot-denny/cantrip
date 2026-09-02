# Cantrip

An agentic spellbook for cross-functional teams.

A *cantrip* is a minor spell cast at will, without preparation — and a Scots word for a small charm.
That's the invocation model here.

Cantrip packages a **spec → plan → implement → review** workflow as portable skills, so the same
toolkit can be installed into many projects instead of hand-ported between them. The workflow itself
names no language or framework, so it works on any stack, on a new project or an existing one.

---

## The components

**A flexible spellbook, not a rigid ritual.** Weave a curated selection of slash commands into your
workflow. There's a natural sequence you can follow to explore, plan, build, and document. Spells
suggest the next one in the flow but never cast automatically, so you can enter anywhere, stop
anywhere, and use one piece without requiring the rest.

**Living feature documentation, not rotting specs.** Most agent workflows aim at writing code
faster, and leave behind a dragon's hoard of up-front specification — amassed with great care,
guarded fiercely, and worth nothing a week after it ships. This one separates the evergreen, living
documentation of *what the system does* — which stays true — from *what we are changing* — which is
temporal, and mainly useful at the time of implementation. See
[The artifacts](docs/concepts.md#the-artifacts-and-why-there-are-two-kinds).

**Review with guardrails.** Three reviewers, one shared contract: it limits them to the diff in
front of them, puts every finding on one shared severity scale, requires a file and line as evidence
for each one, and fixes the shape of the report they hand back. It's a means to continually improve
code quality, performance, and accessibility. See [Code review](docs/concepts.md#code-review-and-its-guardrails).

```
explore → spec → plan → implement-step → feature → code-review → commit-message
                                             ↑
                       retrofit (out-of-flow entry) ┘
```

---

## Quick start

```bash
# 1. Install the core workflow — works on any project, no stack assumptions
#    DISABLE_TELEMETRY=1 stops the installer uploading your skill files; keep it on every command
DISABLE_TELEMETRY=1 npx skills add robot-denny/cantrip/skills/core --all

# 2. Add a stack pack only if one fits — they are independent, take any combination
#    Umbraco 17 CMS work
DISABLE_TELEMETRY=1 npx skills add robot-denny/cantrip/skills/umbraco-17 --all
#    Umbraco Deploy, Cloud or on-premise
DISABLE_TELEMETRY=1 npx skills add robot-denny/cantrip/skills/umbraco-cloud --all
#    C# and .NET, CMS or not
DISABLE_TELEMETRY=1 npx skills add robot-denny/cantrip/skills/dotnet --all

# 3. Configure it — reads what your repo already answers, asks only for the rest
/setup
```

Then cast `/spec` on your next piece of work.

`/setup` analyzes your codebase and writes what it learns into **`.agents/config/`** — four files
holding your paths, your existing commands, and your team's coding standards. That directory is the
part you own and edit, and it is committed, so filling a slot answers it for your teammates too.
[What you own](docs/concepts.md#what-you-own) says which file takes what.

**Nothing is required to configure.** A fresh install works before `/setup` runs; every spell either
does real work or asks for the single fact it is missing.

Install edge cases — Windows symlinks, name collisions with existing commands, choosing an install
shape, registering the reviewers for parallel dispatch — are in
[Installing in detail](#installing-in-detail). Skip them until something looks wrong.

---

## The spellbook

Verbs are spells, cast with `/<name>`. They are invisible to the model and run only when you ask for
them by name.

| Spell | What it does |
|---|---|
| [/explore](skills/core/spellbook/explore/SKILL.md) | Interview-driven discovery *before* a decision. Widens the option space instead of narrowing it. |
| [/spec](skills/core/spellbook/spec/SKILL.md) | Turns an idea into a spec with acceptance criteria, draft BDD scenarios, and a work-type classification. |
| [/plan](skills/core/spellbook/plan/SKILL.md) | Turns a spec into TDD-first steps, each runnable in a fresh context, each with a paste-ready prompt. |
| [/implement-step](skills/core/spellbook/implement-step/SKILL.md) | Runs one plan step in an isolated context, then reports back. |
| [/feature](skills/core/spellbook/feature/SKILL.md) | Writes or updates a living behavioral doc. Also backfills one from code alone. |
| [/testify](skills/core/spellbook/testify/SKILL.md) | The other half of that doc: `/feature` records what a behavioral doc *claims*, this asks what nothing *proves*. Reports the scenarios no test covers, then writes and runs tests only for the rows you approve. `/testify audit` sweeps the whole project and writes nothing. |
| [/code-review](skills/core/spellbook/code-review/SKILL.md) | Three reviewers in parallel, merged into one report with an ordered action plan. |
| [/commit-message](skills/core/spellbook/commit-message/SKILL.md) | Proposes a message that explains *why*, following your project's own convention. |
| [/retrofit](skills/core/spellbook/retrofit/SKILL.md) | The easy button for a change that skipped the flow — reconciles intent against the diff, then proposes the missing tests and docs. |

**Nine workflow spells, and the count is meant to stay small.** A spellbook you can hold in your
head is worth more than one that covers every case, so ten is the working ceiling; past that, the
answer is to merge two stages or add a router rather than keep appending. Two more spells sit
outside the chain, because they are not stages of doing work:

| Spell | What it does |
|---|---|
| [/setup](skills/core/spellbook/setup/SKILL.md) | Configures the toolkit for a project. Run once after installing. |
| [/update-toolkit](skills/core/spellbook/update-toolkit/SKILL.md) | Updates the installed toolkit behind a git guard, because the bare installer silently overwrites local modifications. |

**Spells chain by suggestion, never invocation.** Every spell ends with a `Next:` line; none of them
calls another. That is what keeps this a toolbox rather than a funnel.

---

## The references

Nouns are references. **You never invoke them** — the model reaches for one when its description
matches the work in front of it. They are where the toolkit's opinions live.

### Core — installed with the workflow

| Reference | What it knows |
|---|---|
| [workflow](skills/core/reference/workflow/SKILL.md) | The spine: how work flows from roadmap to feature to spec to plan, and the work-type classification deciding which durable artifacts a change earns |
| [bdd-principles](skills/core/reference/bdd-principles/SKILL.md) | What behavior to specify — Given/When/Then in business language, Example Mapping, specification by example |
| [tdd-principles](skills/core/reference/tdd-principles/SKILL.md) | What a test should *assert* — observable behavior over implementation artifacts, and what counts as a RED→GREEN signal in a project with no harness |
| [reviewer-discipline](skills/core/reference/reviewer-discipline/SKILL.md) | The contract every reviewer follows: scope, severity, evidence, and where two reviewers' domains abut |
| [memory-discipline](skills/core/reference/memory-discipline/SKILL.md) | How an agent's persistent project memory should be written and calibrated, including recording its own false positives |
| [design-system-authoring](skills/core/reference/design-system-authoring/SKILL.md) | How to write your project's *own* design-system skill, so an agent conforms to your visual system instead of inventing a look |

The last one is a skill for writing skills. Your visual conventions are your own, so instead of
shipping design rules you would have to fight, the toolkit walks you through writing down the rules
you already have.

### Packs — optional add-on references

Packs layer in references for one tech stack, so the model follows that platform's established
practices instead of averaging across everything it has read. The three packs today cover Umbraco
and .NET because that is where the toolkit was built — nothing in core assumes them, and a pack for
any other stack drops in the same way.

**Three packs, cut on three different axes.** `umbraco-17` is pinned to a CMS major, `umbraco-cloud`
to a product that spans majors, `dotnet` to a language that only ever adds. Which axis a pack is cut
on is what decides whether its name carries a version — see
[ADR 0015](adr/0015-what-a-stack-pack-is-and-what-it-owes.md).

### `umbraco-17` pack

Version-pinned: the major is in the pack name, because Umbraco majors break — a new major can change
the options, the constraints, and what counts as good practice.

| Unit | Kind | What it does |
|---|---|---|
| [umbraco-17-starter-facts](skills/umbraco-17/reference/umbraco-17-starter-facts/SKILL.md) | reference | Verified platform facts that are easy to get wrong and **fail silently** — Management API shapes, unset-versus-false property behavior, AI and Search configuration traps |
| [umbraco-17-planning](skills/umbraco-17/reference/umbraco-17-planning/SKILL.md) | reference | How to inspect live backoffice schema before designing schema steps, and which authoritative extension skill to route each kind of work to |
| [umbraco-17-review-rules](skills/umbraco-17/reference/umbraco-17-review-rules/SKILL.md) | reference | CMS-specific review surfaces — rendering security, alias traps, per-request cost, editor-authored accessibility |
| [umbraco-17-feature-backfill](skills/umbraco-17/reference/umbraco-17-feature-backfill/SKILL.md) | reference | Reverse-engineering behavioral docs from Umbraco code when no spec exists |
| [umbraco-17-audit-patterns](skills/umbraco-17/reference/umbraco-17-audit-patterns/SKILL.md) | reference | Whether an existing Umbraco solution is idiomatic — composition, schema-as-code discipline, block and content-access patterns, decoupled-frontend readiness |
| [umbraco-17-guide-scaffolding](skills/umbraco-17/reference/umbraco-17-guide-scaffolding/SKILL.md) | reference | The document types an editor-facing guides section needs, the showcase element types a styleguide page is built from, which field the tooling may write and which stay a person's, and what the guide audit prints — **you create the document types; nothing here does it for you** |
| [/block](skills/umbraco-17/spellbook/block/SKILL.md) | spell | Creates a block through a test-first workflow — failing test, element type, view, palette membership |
| [/guide](skills/umbraco-17/spellbook/guide/SKILL.md) | spell | Writes editor-facing guide pages from the schema a component already declares, and audits which components have none. Reads schema from Deploy artifacts, uSync, or a live instance — **it proposes and never writes until you approve** |
| [/styleguide](skills/umbraco-17/spellbook/styleguide/SKILL.md) | spell | Writes a guide page whose showcase sections read the project's design tokens live, so the palette and type scale it shows stay current without a regeneration — **it stops unless a design system is already in place (a token layer a rendered page can read, and an existing view to take conventions from), and names the remedy for whichever half is missing** |
| [/umbraco-edit](skills/umbraco-17/spellbook/umbraco-edit/SKILL.md) | spell | Edits content through the Management API from outside the backoffice |

### `umbraco-cloud` pack

Versionless: Umbraco Deploy behaves the same across CMS majors, so releases are annotated per feature
instead. Deploy is also licensed on its own, so this pack applies to a self-hosted install that runs
it — **it is not Cloud-only despite the name.**

| Unit | Kind | What it does |
|---|---|---|
| [umbraco-deploy-facts](skills/umbraco-cloud/reference/umbraco-deploy-facts/SKILL.md) | reference | How `.uda` artifacts are written and read, why files and an environment's database drift apart, which dashboard control genuinely imports, and the API calls that clear stuck entries |
| [/check-uda](skills/umbraco-cloud/spellbook/check-uda/SKILL.md) | spell | Finds Deploy schema conflicts and drift before they reach a commit |

### `dotnet` pack

Versionless: .NET and C# majors add rather than break, so each newer form says when it arrived.

| Unit | Kind | What it does |
|---|---|---|
| [dotnet-conventions](skills/dotnet/reference/dotnet-conventions/SKILL.md) | reference | Writing C# — naming, async and cancellation, structured logging, serialization, nullability, and which style questions belong to your project rather than the toolkit |
| [dotnet-review-rules](skills/dotnet/reference/dotnet-review-rules/SKILL.md) | reference | Reviewing a C# diff, on the same severity scale every reviewer uses |
| [codebase-audit](skills/dotnet/reference/codebase-audit/SKILL.md) | reference | A five-pillar written assessment of a .NET codebase — hygiene, separation, documentation, resilience, refactorability — staged to its lifecycle and framework-neutral, with an optional head-to-head against a second repo |

**What a reference costs.** Its *description* sits in context from the moment you install it; only
its *body* loads when triggered. So an installed reference you never use is cheap, not free — the
three `dotnet` units add roughly 420 tokens against about 3,100 for the whole toolkit. That's the
reason packs are meant to be opt-in.

---

## How it works

The reasoning behind the toolkit's shape — the two kinds of document and why, how review is guarded,
and how core, packs, and your project layer together — is in **[docs/concepts.md](docs/concepts.md)**.

What your project looks like once installed, and what this repository looks like from the inside,
is in **[docs/layout.md](docs/layout.md)**.

---

## Installing in detail

The two commands in [Quick start](#quick-start) cover most cases. For what lands where, how to verify
it, the install shapes, and what to do when a skill name collides with one you already have, see
**[docs/installing.md](docs/installing.md)**.

---

## Recommended companions for the `umbraco-17` pack

Named here rather than in [docs/installing.md](docs/installing.md) because it is a decision to make
*before* installing, not during.

The pack **routes** backoffice-extension and testing work to two external skill sets rather than
duplicating what they already document. They are **recommended, not required** — the pack works without
them and says so in a plan's Key Decisions, but its extension and test guidance is thinner.

| Skill set | What the pack routes to it |
|---|---|
| `umbraco-cms-backoffice-skills` | Dashboards, property editors, workspaces, trees, the context API, entry points, entity actions, block editor views |
| `umbraco-cms-backoffice-testing-skills` | End-to-end and integration test setup for backoffice extensions |

Both come from one Claude Code plugin marketplace, `umbraco/Umbraco-CMS-Backoffice-Skills`, added with
`/plugin` rather than `npx skills`:

```json
"enabledPlugins": {
  "umbraco-cms-backoffice-skills@umbraco-backoffice-marketplace": true,
  "umbraco-cms-backoffice-testing-skills@umbraco-backoffice-marketplace": true
}
```

**Enable them in the project's `.claude/settings.json`, not only in your user settings.** Both work for
you; only the committed one works for your teammates. A user-level enablement is the classic
works-on-my-machine gap — your plans get the extension guidance and theirs quietly do not. `/setup`
reports which are enabled and where from.

---

## Acknowledgements

Two units here are adaptations of skills published by
**[Matt Pocock](https://github.com/mattpocock/skills)** (MIT):

| This toolkit | Adapted from |
|---|---|
| [tdd-principles](skills/core/reference/tdd-principles/SKILL.md) | the `tdd` skill — what a good test asserts, tautological tests, vertical slicing |
| [/explore](skills/core/spellbook/explore/SKILL.md) | the `grill-me` skill — one question at a time, walking the decision tree branch by branch, looking before asking |

Both were re-expressed and extended rather than copied, and what was deliberately *not* carried over is
recorded with the reasoning in [ADR 0013](adr/0013-attribution-for-adapted-external-work.md). Credit is
given here because it is owed as courtesy, and because a borrowed rule is easier to re-check when you
know it was borrowed.

## License

MIT — see [LICENSE](LICENSE). Install it, vendor it, edit your copy, ship it in client work.

Copyright is held by Diagram; the repository is personally administered. The MIT grant is the same
either way — see [ADR 0007](adr/0007-repository-ownership.md) if you are curious why they differ.

## Contributing

This repo is public and draws on real client projects. Content harvested from client work is scrubbed
of client-identifying information **before** it is committed — see [AGENTS.md](AGENTS.md).
`scripts/check-contract.sh` enforces that plus the layer contract, and runs before every commit.

Decisions are recorded as ADRs in [adr/](adr/); user-visible changes go in
[CHANGELOG.md](CHANGELOG.md). What is planned next is in [ROADMAP.md](ROADMAP.md).
