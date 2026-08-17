# Layout

Two trees: what a **consuming project** looks like once the toolkit is installed and configured, and
what **this repository** looks like for anyone working on the toolkit itself.

Every path in the first tree is a *default*, overridable through the `paths.md` slot. The `workflow`
skill is the authority for it — this file is the picture.

## A consuming project

```
your-project/
│
├── .claude/                     ADAPTER LAYER — regenerable, safe to delete and reinstall
│   ├── skills/                    the installed spells and references
│   ├── agents/                    reviewer agents, linked once (see README)
│   └── settings.json              enabled plugins, including any pack companions
│
├── .agents/
│   ├── skills/                    canonical install: real files, symlinked from .claude/skills/
│   └── config/                  ◀ L2 — THE ONLY PART YOU EDIT
│       ├── paths.md               ## Workspace · ## Code layout · ## Generated output
│       ├── stack.md               ## Build · ## Tests
│       ├── conventions.md         ## Branch naming · ## Commit format · ## Commit trailers
│       │                          ## Implementation rules · ## Memory · ## Planning gotchas
│       │                          ## Unit of work
│       └── reviewer-rules/        per-reviewer project rules, plus shared repo context
│           ├── accessibility.md
│           ├── code.md
│           └── performance.md
│
├── ROADMAP.md                   Now / Next / Later / Recently shipped        ── evergreen
│
├── _features/                   ONE FILE PER CAPABILITY                     ── evergreen
│   └── <area>.md                  Given/When/Then under `Rule:` headings, business language
│
├── _work/                       ONE DIRECTORY PER INCREMENT                 ── temporal
│   ├── <slug>/
│   │   ├── discovery.md           ← /explore   (only when discovery ran)
│   │   ├── spec.md                ← /spec
│   │   ├── plan.md                ← /plan
│   │   ├── notes/                 rationale and decisions
│   │   └── assets/                increment-scoped; archives with the bundle
│   └── shipped/<slug>/            archived increments, moved as one unit
│
├── docs/                        durable human reference: runbooks, guides   ── evergreen
│   └── audits/                    dated audit reports, committed
│
├── _scratch/                    disposable — git-ignored wholesale          ── throwaway
│
└── skills-lock.json             source + content hash per installed skill
```

**Install shape note.** `--all` creates the canonical `.agents/skills/` tree with `.claude/skills/`
symlinking into it. The Claude-Code-only shape puts real files in `.claude/skills/` and no `.agents/skills/`
at all. **`.agents/config/` is where slots live either way** — it is configuration, not installed content,
so nothing overwrites it on update.

**Agent memory** is not shown with a fixed path on purpose: its location is set by
`conventions.md → ## Memory`. Note that a project usually has *two* memory stores — the reviewers'
committed per-agent directories, which this toolkit governs, and a cross-session store outside the repo,
which it does not. A backup scoped to the repo misses the second.

### The one idea the structure encodes

**Lifecycle over type.** Files are grouped by how long they stay true, not by what kind of thing they are.

| | Holds | Lives until |
|---|---|---|
| **Evergreen** | `_features/`, `ROADMAP.md`, `docs/` | the behavior changes |
| **Temporal** | `_work/<slug>/` | the increment ships, then archived |
| **Throwaway** | `_scratch/` | whenever; git-ignored |

That is why `_features/` sits at the root and specs sit a level down. Capability docs are the
cross-functional artifact and their visibility is the point; a spec mid-flight is developer- and
agent-facing and loses nothing by being one level in.

**The increment bundle.** A spec, its plan, its discovery notes and its assets are created, reviewed, and
archived together — so they live together, and archiving is one move. Every spell's contract is just
*"look in `_work/<slug>/`."*

### Which spell touches what

```
/explore  ─▶ _work/<slug>/discovery.md       opens the increment's working directory
/spec     ─▶ _work/<slug>/spec.md            reads discovery.md when given its slug
/plan     ─▶ _work/<slug>/plan.md            reads spec.md
/implement-step ─▶ your codebase             reads plan.md, one step per cast
/feature  ─▶ _features/<area>.md             reads spec.md — or reads code alone (from-code mode)
/code-review ─▶ a report                     reads the diff
/commit-message ─▶ a message                 reads the diff + conventions.md
/setup    ─▶ .agents/config/* and the scaffold above
```

`_features/<area>.md` is named for a **capability**, never for a piece of work — and its name is
independent of the increment slug, which is why a spec carries an explicit `feature-doc:` field.

## This repository

```
cantrip/
├── skills/
│   ├── core/                    L0 — technology-agnostic, works on any project
│   │   ├── spellbook/             10 user-cast spells
│   │   └── reference/             6 model-invoked references (+ the reviewer agents)
│   ├── umbraco-17/              L1 — the CMS, pinned to a major
│   │   ├── spellbook/             2 spells
│   │   └── reference/             5 references
│   ├── umbraco-cloud/           L1 — Umbraco Deploy, versionless
│   │   ├── spellbook/             1 spell
│   │   └── reference/             1 reference
│   └── dotnet/                  L1 — the language and platform, versionless
│       └── reference/             3 references
│
├── docs/                        contract, layout, durable reference
├── adr/                         15 decision records
├── scripts/                     check-contract.sh · check-install.sh · check-preserved.py
├── tests/                       install-verification fixtures
├── _work/ · _features/          the toolkit dogfooding its own workflow
└── .githooks/pre-commit         runs the contract gate before every commit
```

In words, since the tree above carries it only in indentation: `skills/` holds one directory per layer
— `core/` for L0, then one directory per stack pack. Each of those contains a `reference/` for
model-invoked units and, **only if the pack has spells to name**, a `spellbook/` beside it. `umbraco-17`
has both, with 2 spells and 5 references; `umbraco-cloud` has both, with 1 each; `dotnet` has
`reference/` alone, holding 3 units, because a language earns references rather than repeatable
operations. Every unit is a directory holding a `SKILL.md`, whatever depth it sits at.

**Only `skills/` ships.** Installs are subpath-scoped, so `LICENSE`, `README.md`, `docs/`, and `adr/` never
reach a consuming project. Worth knowing when deciding where something belongs: guidance a consumer needs
at cast time has to live inside a skill, because nothing else travels.

## The three layers, as directories

| Layer | Where it lives | Who owns it | Contains |
|---|---|---|---|
| **L0 core** | `skills/core/` → installed | the toolkit | no technology names, no project facts |
| **L1 pack** | `skills/<pack>/` → installed | the toolkit | technology facts, no project facts |
| **L2 project** | `.agents/config/` | **you** | every project fact, in slots |

The contract is that L0 and L1 are *vendored copies you do not edit* — a local edit is a divergence that
`/update-toolkit` surfaces, not a way to tailor. Tailoring goes in L2. If tailoring needs an L0 edit, that
is a missing slot and should be reported as one.

**L1 is one directory per pack, and packs are independent.** A project installs any combination —
subpath-scoped installs mean taking one pack costs nothing in the others — and each pack is *replaced*
rather than upgraded when its technology moves a major. Where a pack's boundary falls, and why some pack
names carry a version while no spell name does, is
[adr/0015](../adr/0015-what-a-stack-pack-is-and-what-it-owes.md).

See [contract.md](contract.md) for the normative rules, and [adr/0001](../adr/0001-layer-contract-and-slots.md)
for why the split falls here.
