# Cantrip

An agentic spellbook for cross-functional teams.

A *cantrip* is a minor spell cast at will, without preparation — and a Scots word for a small charm.
That is the invocation model here: user-cast spells, deliberate and repeatable.

Cantrip packages a **spec → plan → implement → review** workflow as portable skills, so the same
discipline can be installed into many projects instead of hand-ported between them. It works on a new
project or an existing one.

---

## What you actually get

Three things, and they are easier to judge than a skill list.

**A workflow you cast, not one that runs you.** Every stage is a slash command you type. Spells suggest
the next one and never call it, so you can enter anywhere, stop anywhere, and use one piece without
buying the rest.

**Documentation that outlives the work.** Most agent workflows produce a burst of files nobody reads
again. This one separates *what the system does* — which stays true — from *how one change got made* —
which stops being interesting the moment it ships. See [The artifacts](#the-artifacts-and-why-there-are-two-kinds).

**Review with guardrails.** Three reviewers, one shared contract that constrains what they may claim,
what evidence they must cite, and what they must stay quiet about. The rules exist because an
unconstrained reviewer produces confident findings nobody can act on. See
[Code review](#code-review-and-its-guardrails).

```
explore → spec → plan → implement-step → feature → code-review → commit-message
                                             ↑
                       retrofit (out-of-flow entry) ┘
```

---

## Quick start

```bash
# 1. Install the core workflow — works on any project, no stack assumptions
npx skills add robot-denny/cantrip/skills/core --all

# 2. Add a stack pack only if one fits
npx skills add robot-denny/cantrip/skills/umbraco-17 --all   # Umbraco 17 CMS work
npx skills add robot-denny/cantrip/skills/dotnet --all       # C# and .NET, CMS or not

# 3. Configure it — reads what your repo already answers, asks only for the rest
/setup
```

Then cast `/spec` on your next piece of work.

**Nothing is required to configure.** A fresh install works before `/setup` runs; every spell either
does real work or asks for the single fact it is missing.

Install edge cases — Windows symlinks, name collisions with existing commands, choosing an install
shape, registering the reviewers for parallel dispatch — are in [Installing in
detail](#installing-in-detail). Skip them until something looks wrong.

---

## The spellbook

Verbs are spells, cast with `/<name>`. They are invisible to the model and run only when you ask for
them by name.

| Spell | What it does |
|---|---|
| `/explore` | Interview-driven discovery *before* a decision. Widens the option space instead of narrowing it. |
| `/spec` | Turns an idea into a spec with acceptance criteria, draft BDD scenarios, and a work-type classification. |
| `/plan` | Turns a spec into TDD-first steps, each runnable in a fresh context, each with a paste-ready prompt. |
| `/implement-step` | Runs one plan step in an isolated context, then reports back. |
| `/feature` | Writes or updates a living behavioral doc. Also backfills one from code alone. |
| `/code-review` | Three reviewers in parallel, merged into one report with an ordered action plan. |
| `/commit-message` | Proposes a message that explains *why*, following your project's own convention. |
| `/retrofit` | The easy button for a change that skipped the flow — reconciles intent against the diff, then proposes the missing tests and docs. |

**Eight workflow spells, and that is deliberate.** The count is held at eight so the spellbook stays
learnable; a ninth stage would mean merging two or adding a router. Two more sit outside the chain,
because they are not stages of doing work:

| Spell | What it does |
|---|---|
| `/setup` | Configures the toolkit for a project. Run once after installing. |
| `/update-toolkit` | Updates the installed toolkit behind a git guard, because the bare installer silently overwrites local modifications. |

**Spells chain by suggestion, never invocation.** Every spell ends with a `Next:` line; none of them
calls another. That is what keeps this a toolbox rather than a funnel.

---

## The references

Nouns are references. **You never invoke them** — the model reaches for one when its description
matches the work in front of it. They are where the toolkit's opinions live.

### Core — installed with the workflow

| Reference | What it knows |
|---|---|
| `workflow` | The spine: how work flows from roadmap to feature to spec to plan, and the work-type classification deciding which durable artifacts a change earns |
| `bdd-principles` | What behavior to specify — Given/When/Then in business language, Example Mapping, specification by example |
| `tdd-principles` | What a test should *assert* — observable behavior over implementation artifacts, and what counts as a RED→GREEN signal in a project with no harness |
| `reviewer-discipline` | The contract every reviewer follows: scope, severity, evidence, and where two reviewers' domains abut |
| `memory-discipline` | How an agent's persistent project memory should be written and calibrated, including recording its own false positives |
| `design-system-authoring` | How to write your project's *own* design-system skill, so an agent conforms to your visual system instead of inventing a look |

The last one is worth noticing: it is a skill for writing skills. Your visual conventions are yours, so
the toolkit teaches the shape rather than shipping an answer.

### `umbraco-17` pack

| Unit | Kind | What it does |
|---|---|---|
| `umbraco-17-starter-facts` | reference | Verified platform facts that are easy to get wrong and **fail silently** — Management API shapes, unset-versus-false property behavior, Deploy and `.uda` mechanics |
| `umbraco-17-planning` | reference | How to inspect live backoffice schema before designing schema steps, and which authoritative extension skill to route each kind of work to |
| `umbraco-17-review-rules` | reference | CMS-specific review surfaces — rendering security, alias traps, per-request cost, editor-authored accessibility |
| `umbraco-17-feature-backfill` | reference | Reverse-engineering behavioral docs from Umbraco code when no spec exists |
| `architecture-audit` | reference | A seven-pillar written assessment of an Umbraco/.NET codebase, staged to its maturity |
| `/block` | spell | Creates a block through a test-first workflow — failing test, element type, view, palette membership |
| `/check-uda` | spell | Finds Deploy schema conflicts and drift before they reach a commit |
| `/umbraco-edit` | spell | Edits content through the Management API from outside the backoffice |

### `dotnet` pack

| Unit | Kind | What it does |
|---|---|---|
| `dotnet-conventions` | reference | Writing C# — naming, async and cancellation, structured logging, serialization, nullability, and which style questions belong to your project rather than the toolkit |
| `dotnet-review-rules` | reference | Reviewing a C# diff, on the same severity scale every reviewer uses |

**What a reference costs.** Its *description* sits in context from the moment you install it; only its
*body* loads when triggered. So an installed reference you never use is cheap, not free — the two
`dotnet` units add roughly 271 tokens against about 2,900 for the whole toolkit. That is the real
argument for packs being opt-in.

---

## The artifacts, and why there are two kinds

This is the part most worth understanding, because it decides where things go and what stays true.

| | Holds | Stays true until |
|---|---|---|
| `_features/<area>.md` | **What the system does now**, as Given/When/Then behavior in business language, one file per capability | the behavior itself changes |
| `_work/<slug>/` | **How one change got made** — its discovery, spec, plan, notes | it ships; then it moves to `_work/shipped/` |

**Grouped by lifecycle, not by type.** A capability doc and a spec are both markdown full of scenarios,
so a type-based layout would file them together — and then half of it silently rots while the other
half stays current, with no way to tell which is which.

The split is what makes the docs trustworthy:

- **A feature doc is the answer to "what does this do?"** — for QA writing regression tests, for a new
  developer, for a stakeholder. It never records that something *changed*; it records what *is*.
- **A spec is the answer to "why did we build it that way?"** — read once during the work, occasionally
  again during an argument, then archived.

`/spec` classifies every piece of work as a **new capability**, a **change to** an existing one, or a
**fix**, and that classification decides which artifacts it earns. A refactor does not get a feature doc
named after the refactor; its observable behavior folds into the capability's existing doc, and its
point-in-time criteria stay in the shipped spec. That one rule is what stops a capability catalogue
turning into a changelog.

---

## Code review, and its guardrails

`/code-review` dispatches three reviewers over the same diff and merges them into one ranked report.

| Reviewer | Domain |
|---|---|
| `code-reviewer` | Secrets, input validation, error handling, clarity, conventions, duplication |
| `perf-reviewer` | Rendering and data-access cost, payload size, caching, client-side weight |
| `accessibility-reviewer` | Semantics, focus, keyboard, labelling, assistive-technology behavior |

All three follow `reviewer-discipline`, which exists to stop the failure modes that make review output
worthless:

- **Diff-only scope.** A reviewer may not reference, infer, or speculate about code it was not shown.
  Unchanged code is neither correct nor incorrect — it is out of scope.
- **One severity scale.** Blocker / Major / Minor / Nit, shared by all three, which is what lets three
  reports merge into a single ranking. A reviewer inventing "Critical" cannot be merged.
- **Evidence, not impressions.** Every finding cites a file and a line, carries a concrete fix, and
  quantifies impact where it can.
- **Do not over-report, do not under-report.** A confident wrong finding costs more than a missed minor
  one, because it teaches the reader to discount you. But no defect is skipped for being awkward to fix.
- **Say what was checked and clean.** Otherwise a reader cannot tell "checked and fine" from "not
  checked".
- **Where two domains abut, one reviewer owns the rule and the others stay silent** — in a merged
  report. Otherwise one defect arrives twice, and neither reviewer can see it, because the duplication
  exists only after merging.

Reviewers keep **persistent project memory** and are expected to record their own false positives, so a
finding you rejected once stops coming back.

---

## Core, packs, and your project

Three layers, and knowing which one you are looking at answers most "where does this go?" questions.

| Layer | Holds | Owned by |
|---|---|---|
| **Core** | The workflow, the spellbook, the references, the reviewer agents | this repo |
| **Stack pack** | Knowledge about one technology at one major version | this repo |
| **Your project** | Your paths, your commands, your conventions, your reviewer rules | you |

**Core and packs contain no fact about any specific project** — not a path, not a build command, not an
architectural framing. They read *slots* you fill in `.agents/config/`, and degrade gracefully when a
slot is empty.

### Why packs exist

An agent's knowledge of a platform is **every version it was trained on at once**, attributed to none of
them. So it interpolates: guidance that blends releases, work that hits a roadblock and gets
backtracked, or code that ships looking idiomatic while violating the practices of the version you are
actually on.

A pack pins the version so it stops. That is why a pack earns its place *even when the model already
knows the technology* — knowing it in general is exactly the problem.

It is also why packs are opt-in. `/check-uda` is a superpower in an Umbraco repo and clutter in every
other one, and stack units cost context on every request in a project that will never use them. Where
majors break, there is a pack per major; where majors only add, one pack annotates features with the
version they arrived in. [ADR 0015](adr/0015-what-a-stack-pack-is-and-what-it-owes.md) has the full
reasoning.

### What you own

Fill slots in `.agents/config/` — `paths.md`, `stack.md`, `conventions.md`, and `reviewer-rules/`.
`/setup` drafts most of it by reading your repo, and asks only for what it cannot observe.

Editing an installed file is possible but is a **divergence**, not a workflow — `/update-toolkit` will
surface it, and the bare installer would overwrite it. Tailoring belongs in your layer. If tailoring
needs a core edit, that is a missing slot; please report it as one.

See [docs/contract.md](docs/contract.md) for the full contract.

---

## Layout

What your project looks like once installed and configured:

```
your-project/
├── .agents/config/        ◀ the only part you edit (slots)
├── .claude/skills/          the installed spells and references
├── ROADMAP.md               Now / Next / Later                    ── evergreen
├── _features/<area>.md      one file per capability                ── evergreen
├── _work/<slug>/            discovery.md · spec.md · plan.md        ── temporal
│                            plus notes/ and assets/
│   └── shipped/<slug>/      archived as one unit
├── docs/                    runbooks and guides, docs/audits/      ── evergreen
├── _scratch/                git-ignored wholesale                  ── throwaway
└── skills-lock.json         source + content hash per skill
```

And this repository itself:

```
skills/core/spellbook/     # the spells
skills/core/reference/     # references, and the reviewer agents
skills/umbraco-17/         # stack pack — the CMS
skills/dotnet/             # stack pack — the language and platform
docs/                      # durable reference
adr/                       # decision records
scripts/                   # the contract gate and the install checker
```

Full annotated trees and which spell writes which artifact: **[docs/layout.md](docs/layout.md)**.

---

## Installing in detail

Everything below is an edge case. The [Quick start](#quick-start) is enough for most projects.

### Check the install

```bash
scripts/check-install.sh          # or --verbose to list what is wired
```

Reports what is wired, what is degraded but working, and what is broken — with the fix for each. It
exits non-zero **only** when something is genuinely broken, so it is safe in a pipeline: a core-only
install with no configuration and no linked agents is a working install and passes.

### One extra step for parallel review

The three reviewer agents install as assets of `reviewer-discipline`, but registering them as
dispatchable subagents is something the installer cannot do. Link them once:

```bash
mkdir -p .claude/agents
for f in .claude/skills/reviewer-discipline/agents/*.md; do
  n=$(basename "$f"); ln -s "../skills/reviewer-discipline/agents/$n" ".claude/agents/$n"
done
```

Purely additive — any agents your project already has are untouched.

On Windows, copy instead. `check-install.sh` compares content rather than looking for a link, so a copy
registers identically. The tradeoff is that copies do not follow `/update-toolkit`, so re-copy after an
update.

```powershell
New-Item -ItemType Directory -Force .claude\agents
Copy-Item .claude\skills\reviewer-discipline\agents\*.md .claude\agents\
```

Until you do, `/code-review` and `/retrofit` run the three passes inline instead of in parallel.
Everything works either way — you are trading concurrency, not capability.

### Pick your install shape

`--all` is shorthand for `--skill '*' --agent '*'` — every skill, to **every agent tool it can detect**.
Verified, that means four write locations: `.agents/skills/` (real files), `.claude/skills/` (symlinks
to them), a top-level `agent/` directory, and — **if your project already has a bare `skills/`
directory, it writes into that too**. Nothing is overwritten, but a project with its own `skills/`
folder gets it populated.

If you only use Claude Code, this is cleaner — same skills, assets and agents included, one write
location, an existing `skills/` folder left alone, and **no symlinks anywhere**:

```bash
npx skills add robot-denny/cantrip/skills/core --skill '*' --agent claude-code -y
```

| | `--all` | `--skill '*' --agent claude-code` |
|---|---|---|
| Skills installed | 16 | 16 |
| Bundled assets and agents | ✓ | ✓ |
| Writes to | `.agents/`, `.claude/`, `agent/`, `skills/` | `.claude/` only |
| Canonical `.agents/` tree | ✓ | ✗ (files copied into `.claude/skills/`) |
| Other agent tools supported | ✓ | ✗ |
| Creates symlinks | ✓ `.claude/skills/` → `.agents/skills/` | ✗ real files only |

**On Windows, prefer the single-agent shape** — the last row is why, not the tool count. Symlinks exist
in the `--all` layout precisely *because* it serves several tools from one canonical tree, and Git for
Windows only materializes them when `core.symlinks=true`, which its installer disables unless the
account can create them. Where it is off you get a small text file containing the target path instead
of a link, so `.claude/skills/plan` looks present and contains no `SKILL.md` — the spell silently does
not exist. The single-agent shape writes real files and has nothing to materialize.

For several tools on Windows, run the installer once per tool with a single `--agent` each. That trades
the shared canonical tree for one independent copy per tool, and needs no symlink support.

Either way `skills-lock.json` records the source and a content hash per skill. If your project already
has one, the installer **merges** into it rather than replacing it.

Note that `--all` overrides a preceding `--skill`, so `--skill workflow --all` installs everything.

> `npx skills` uploads skill file contents as telemetry by default. Prefix with `DISABLE_TELEMETRY=1`
> if that matters to you.

### If your project already has commands with these names

**A skill shadows a same-named command.** There is no namespace and no error — install `/spec` and an
existing `.claude/commands/spec.md` becomes present but unreachable. It is not a fallback you can still
get to.

This matters most for a project already running its own version of this workflow. **Install on a branch
first.** Shadowing is then contained: switching back restores your commands intact, and you can compare
the two side by side. Commands whose names the toolkit does not use are unaffected.

### Recommended companions for the `umbraco-17` pack

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
| `tdd-principles` | the `tdd` skill — what a good test asserts, tautological tests, vertical slicing |
| `/explore` | the `grill-me` skill — one question at a time, walking the decision tree branch by branch, looking before asking |

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
