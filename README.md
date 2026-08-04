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

Packs are opt-in: the core install brings no stack-specific content at all.

### Recommended companions for the `umbraco-17` pack

The pack **routes** backoffice-extension and testing work to two external skill sets rather than
duplicating what they already document. They are **recommended, not required** — the pack works without
them, and says so in a plan's Key Decisions when it planned without them — but its extension and test
guidance is thinner in their absence.

| Skill set | What the pack routes to it |
|---|---|
| `umbraco-cms-backoffice-skills` | Dashboards, property editors, workspaces, trees, the context API, entry points, entity actions, block editor views |
| `umbraco-cms-backoffice-testing-skills` | End-to-end and integration test setup for backoffice extensions |

Both come from one Claude Code plugin marketplace, `umbraco/Umbraco-CMS-Backoffice-Skills`, added with
`/plugin` rather than with `npx skills`. Enabled, they appear in settings as:

```json
"enabledPlugins": {
  "umbraco-cms-backoffice-skills@umbraco-backoffice-marketplace": true,
  "umbraco-cms-backoffice-testing-skills@umbraco-backoffice-marketplace": true
}
```

**Enable them in the project's `.claude/settings.json`, not only in your user settings.** Both locations
work for you; only the committed project one works for your teammates. A user-level enablement is the
classic works-on-my-machine gap — your plans get the extension guidance and theirs quietly do not.

`/setup` reports which of the two are enabled and where they were enabled from.

### Pick your install shape

`--all` is shorthand for `--skill '*' --agent '*'` — every skill, to **every agent tool it can
detect**. Verified, that means it writes to four places: `.agents/skills/` (real files),
`.claude/skills/` (symlinks to them), a top-level `agent/` directory, and — **if your project already
has a bare `skills/` directory, it writes into that too**, alongside whatever is already there.
Nothing is overwritten, but a project with its own `skills/` folder gets it populated.

If you only use Claude Code, this is cleaner — same 16 skills, assets and agents included, one write
location, and an existing `skills/` folder left alone:

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

Either way `skills-lock.json` records the source and a content hash per skill. If your project already
has one, the installer **merges** into it rather than replacing it — existing entries are preserved.

Note that `--all` overrides a preceding `--skill`, so `--skill workflow --all` installs everything.

> `npx skills` uploads skill file contents as telemetry by default. Prefix with
> `DISABLE_TELEMETRY=1` if that matters to you.

### If your project already has commands with these names

**A skill shadows a same-named command.** There is no namespace and no error — install
`/spec` and an existing `.claude/commands/spec.md` becomes present but unreachable. It is not a
fallback you can still get to.

This matters most for a project already running its own version of this workflow. **Install on a
branch first.** Shadowing is then contained: switching back to your default branch restores your
commands intact, and you can compare the two side by side before committing to either.

Commands whose names the toolkit does not use are unaffected.

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

**Eight workflow spells, and that is deliberate.** The count is held at eight so the spellbook stays
learnable; a ninth workflow stage would mean merging two or adding a router. Two further spells sit
outside the chain and are counted separately, because they are not stages of doing work:

| Spell | What it does |
|---|---|
| `/setup` | Configures the toolkit for a project — detects what the repo answers, mines what its guidance files already say, asks only for the rest. Run once after installing. |
| `/update-toolkit` | Updates the installed toolkit behind a git guard, because the bare installer silently overwrites local modifications. |

A stack pack adds its own spells on top — the `umbraco-17` pack adds three. A project only ever sees core
plus the packs it installed.

Nouns are references, which the model reaches for on its own: `workflow` (the spine and work-type
classification), `bdd-principles` (what behavior to specify), `tdd-principles` (what a test should
assert), `reviewer-discipline`, `memory-discipline`, and `design-system-authoring`.

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

## Acknowledgements

Two units here are adaptations of skills published by **[Matt Pocock](https://github.com/mattpocock/skills)** (MIT):

| This toolkit | Adapted from |
|---|---|
| `tdd-principles` | the `tdd` skill — what a good test asserts, tautological tests, vertical slicing |
| `/explore` | the `grill-me` skill — one question at a time, walking the decision tree branch by branch, looking before asking |

Both were re-expressed and extended rather than copied, and what was deliberately *not* carried over is
recorded with the reasoning in [ADR 0013](adr/0013-attribution-for-adapted-external-work.md). Credit is
given here because it is owed as courtesy and because a borrowed rule is easier to re-check when you know
it was borrowed.

## License

MIT — see [LICENSE](LICENSE). Install it, vendor it, edit your copy, ship it in client work.

Copyright is held by Diagram; the repository is personally administered. The MIT grant is the same either
way — see [ADR 0007](adr/0007-repository-ownership.md) if you are curious why they differ.

## Contributing

This repo is public and draws on real client projects. Content harvested from client work is
scrubbed of client-identifying information **before** it is committed — see [AGENTS.md](AGENTS.md).
`scripts/check-contract.sh` enforces that plus the layer contract, and runs before every commit.

Decisions are recorded as ADRs in [adr/](adr/); user-visible changes go in
[CHANGELOG.md](CHANGELOG.md).
