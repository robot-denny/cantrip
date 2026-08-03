# Cantrip

An agentic spellbook for cross-functional teams.

A *cantrip* is a minor spell cast at will, without preparation — and a Scots word for a
small charm. That is the invocation model here: user-cast spells, deliberate and repeatable.

Cantrip packages a spec → plan → implement → review workflow as portable skills, so the same
discipline can be installed into many projects instead of hand-ported between them. It works on a
new project or an existing one.

## Install

Core only — works on any project, no stack assumptions:

```bash
npx skills add robot-denny/cantrip/skills/core --all
```

Add a stack pack if one fits your project:

```bash
npx skills add robot-denny/cantrip/skills/umbraco-17 --all
```

Skills land in `.agents/skills/` with `.claude/skills/` symlinked to them, and `skills-lock.json`
records the source and a content hash for each. Packs are opt-in: the core install brings no
stack-specific content at all.

The installer also creates a top-level `agent/` directory holding a partial copy of the skills. That
is a quirk of the installer, not a broken install — you can ignore or delete it.

> `npx skills` uploads skill file contents as telemetry by default. Prefix with
> `DISABLE_TELEMETRY=1` if that matters to you.

### Check the install

```bash
scripts/check-install.sh          # or --verbose to list what is wired
```

Reports what is wired, what is degraded but working, and what is broken — with the fix for each. It
exits non-zero **only** when something is genuinely broken, so it is safe in a pipeline: a core-only
install with no configuration and no linked agents is a working install and passes.

### One extra step for parallel review

The three reviewer agents install as assets of the `reviewer-discipline` skill, but registering them
as dispatchable subagents is something the installer cannot do. Link them once:

```bash
mkdir -p .claude/agents
for f in .claude/skills/reviewer-discipline/agents/*.md; do
  n=$(basename "$f"); ln -s "../skills/reviewer-discipline/agents/$n" ".claude/agents/$n"
done
```

This is purely additive — any agents your project already has are untouched.

Until you do, `/code-review` and `/retrofit` run the three review passes inline instead of in
parallel. Everything works either way — you are trading concurrency, not capability.

## The spellbook

Verbs are spells, cast with `/<name>`. They are invisible to the model and run only when you ask.

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

One maintenance spell sits outside the workflow chain:

| Spell | What it does |
|---|---|
| `/update-toolkit` | Updates the installed toolkit behind a git guard, because the bare installer silently overwrites local modifications. |

Nouns are references, which the model reaches for on its own: `workflow` (the spine and work-type
classification), `bdd-principles`, `reviewer-discipline`, `memory-discipline`.

**Spells chain by suggestion, never invocation.** Every spell ends with a `Next:` line; none of them
calls another. That is what keeps this a toolbox rather than a funnel.

```
explore → spec → plan → implement-step → feature → code-review → commit-message
                                              ↑
                        retrofit (out-of-flow entry) ┘
```

## How it is layered

| Layer | Contents | Owned by |
|---|---|---|
| **L0 Core** | Workflow spine, spellbook, references, templates, reviewer agents | this repo |
| **L1 Stack pack** | Tech-specific spells, rules, and starter facts. First pack: `umbraco-17` | this repo |
| **L2 Project** | Stack facts, project skills, reviewer rules, agent memory | the consuming project |

**L0 and L1 files contain no fact about any specific project.** They read L2 *slots* and degrade
gracefully when a slot is empty — so a fresh install works before you have configured anything, and
every spell either does real work or asks for the one fact it is missing.

Configure by filling slots in `.agents/config/` — `paths.md`, `stack.md`, `conventions.md`, and
`reviewer-rules/`. Nothing is required to start.

Editing a vendored file is possible but is a **divergence**, not a workflow: tailoring belongs in
L2. If tailoring needs a core edit, that is a missing slot — please report it as one.

See [docs/contract.md](docs/contract.md) for the full contract.

## Layout

```
skills/core/spellbook/     # the spells
skills/core/reference/     # model-invoked references, and the reviewer agents
skills/umbraco-17/         # first stack pack
docs/                      # durable reference
adr/                       # toolkit decision records
scripts/                   # contract gate and extraction checks
```

## Contributing

This repo is public and draws on real client projects. Content harvested from client work is
scrubbed of client-identifying information **before** it is committed — see [AGENTS.md](AGENTS.md).
`scripts/check-contract.sh` enforces that plus the layer contract, and runs before every commit.

Decisions are recorded as ADRs in [adr/](adr/); user-visible changes go in
[CHANGELOG.md](CHANGELOG.md).
