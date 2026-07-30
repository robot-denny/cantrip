# Cantrip

An agentic spellbook for cross-functional teams.

A *cantrip* is a minor spell cast at will, without preparation — and a Scots word for a
small charm. That is the invocation model here: user-cast spells, deliberate and
repeatable.

Cantrip packages a spec → plan → implement → review workflow as portable Claude Code
skills, agents, and templates, so the same discipline can be installed into many projects
instead of hand-ported between them.

> **Status: scaffold.** The repo structure is in place; content extraction has not
> started. Nothing here is installable yet.

## How it is layered

| Layer | Contents | Owned by |
|---|---|---|
| **L0 Core** | Workflow spine, spellbook skeletons, references, templates, agent skeletons | this repo |
| **L1 Stack pack** | Tech-specific spells, rules, and starter facts. First pack: `umbraco-17` | this repo |
| **L2 Project** | Stack facts, project skills, reviewer rules, agent memory — filled config slots | the consuming project |

L0 and L1 files never contain project facts. They read L2 slots and degrade gracefully
when a slot is empty. Projects vendor their copy; an update flow reconciles it with
upstream.

## Invocation postures

| Posture | Mechanism | Contents |
|---|---|---|
| **Spell** (user-cast only) | `disable-model-invocation: true`, cast via `/<name>` | The orchestration chain: side-effectful, deliberate |
| **Reference** (model-invoked) | Trigger-engineered description, loaded at session start | Discipline and knowledge the agent reaches for |
| **Worker** (subagent) | Own context, preloads skills | The reviewers |

Conventions: **verbs are spells, nouns are reference** (`/spec`, `/plan` vs
`bdd-principles`, `design-system`). Spells **chain by suggestion, never invocation** —
every spell ends with a `Next:` line. That is what keeps this a toolbox rather than a
funnel.

## Layout

```
skills/core/         # L0 — spellbook + reference skills
skills/umbraco-17/   # L1 — first stack pack
agents/              # reviewer skeletons
templates/           # spec / plan / feature templates
docs/                # durable human reference
adr/                 # toolkit decision records
CHANGELOG.md
```

## Spell catalog

To be filled as spells land. Planned core set (6–8): `spec`, `plan`, `implement-step`,
`feature`, `retrofit`, `explore`, `code-review`, `commit-message`.

## Contributing

This repo is public from day one and draws on real client projects. Content harvested
from client work must be scrubbed of client-identifying information **before** it is
committed — there is no private staging period. See [AGENTS.md](AGENTS.md).

Toolkit decisions are recorded as ADRs in [adr/](adr/); user-visible changes go in
[CHANGELOG.md](CHANGELOG.md).
