# The layer contract

Normative reference for anyone authoring or reviewing toolkit files. The decision record and
rationale live in [adr/0001-layer-contract-and-slots.md](../adr/0001-layer-contract-and-slots.md);
this document is the spec you check your work against.

## The three layers

| Layer | Lives in | Owned by | Contains |
|---|---|---|---|
| **L0 Core** | `skills/core/` | this repo | Workflow spine, spellbook, references, templates, agent skeletons |
| **L1 Stack pack** | `skills/<pack>/` | this repo | Tech-specific spells, rules, starter facts |
| **L2 Project** | `.agents/config/`, `.agents/skills/`, `.agents/memory/` | the consuming project | Every fact about *this* project |

**The invariant, stated once:** an L0 or L1 file contains no fact about any specific project.
Not a path, not a port, not a build command, not a client name, not a project's architectural
framing. Those live in L2 slots, which L0/L1 files *read*.

L1 may contain facts about a *technology* (Umbraco 17 reserves the `level` alias) but never
about a *project* (this site's blocks live under `src/<AssemblyName>.Features/Blocks/`).

## Slots

A slot is a named, project-owned section that toolkit files read. Four files, chosen because
the facts found in the source repos cluster into exactly these four kinds:

### `.agents/config/paths.md` — where things live

Workspace paths (`_work/`, `_features/`, `docs/audits/`, shipped archives, template
locations) and code layout by kind (where a block lives, where a page type lives, where
generated models are written, where schema files are kept). Also which paths are *generated
output* rather than authored source, so review and retrofit can skip bundles.

### `.agents/config/stack.md` — how to run things

Build command, frontend build, test commands and their locations, local URL, runtime version
and how to invoke it, and any tooling mode that changes behavior (e.g. whether models are
generated or committed). This is the slot that eliminates hardcoded environment assumptions —
the source repos carried absolute `nvm` paths pinned to two different Node versions, which is
precisely the fact that cannot ship.

### `.agents/config/conventions.md` — how this project works

Project-specific discipline that shapes *how* a spell does its job rather than *where* it
looks: the project's own framing of what a unit of work is, its TDD conventions, test
resilience rules, and any standing constraint a plan or review must respect.

### `.agents/config/reviewer-rules/` — per-reviewer project rules

One file per reviewer agent, holding the project-specific rules that reviewer applies, plus
the short repo-context blurb it needs to orient. Kept separate from `conventions.md` because
reviewers load only their own.

## The reference pattern

Every point where a toolkit file reaches into L2 uses this three-part form. It is plain
markdown — no templating, no build step, no substitution pass:

```markdown
**Slot:** `.agents/config/stack.md` → `## Build`
**If empty:** infer the build command from the repo root (`*.sln`, `package.json`,
`Makefile`); if still ambiguous, ask the user rather than guessing.
```

Rules:

1. **Every `**Slot:**` has an adjacent `**If empty:**`.** Enforced by
   `scripts/check-contract.sh`. A slot reference without a fallback is a contract violation,
   because it turns an unfilled slot into a broken spell.
2. **Name the file and the heading**, so a reader can find the fact and an author can see
   what the slot is expected to hold.
3. **Fallbacks degrade, never fabricate.** The three legitimate fallback shapes are *infer
   from the repo*, *skip this step and say so*, and *ask the user*. Inventing a plausible
   path or command is the failure mode this rule exists to prevent.
4. **Prefer inference over interrogation** — per the direction doc's "detection over
   interrogation" principle, asking is the last resort, not the first.

The pattern is proven: `/check-uda`'s existing git-only fallback is exactly this shape, and
it is why that spell already works in repos without the full environment.

### One slot, one point of authority

A slot is referenced where it is *owned*, and every other file defers to that owner rather
than repeating the reference.

The workspace layout is the worked example. The `workflow` skill owns it — it carries the
`paths.md` slot reference and the default layout as its fallback. Spells that write artifacts
do **not** each re-declare that slot; they say "artifact locations follow the layout in the
`workflow` skill" and read it.

The reason is drift. Eight spells each carrying their own copy of the same slot reference is
eight places to update and eight chances for the fallbacks to disagree — which is precisely how
the two source repos ended up with the same command in two different states. A spell should
carry a slot reference only for a fact no other toolkit file already owns.

Corollary: **toolkit-internal paths are not slots.** A spell reading
`.agents/skills/workflow/templates/spec.md` is naming something the toolkit itself controls and
installs, not a project fact. Name those paths directly; save slots for facts the project owns.

## Graceful degradation is a hard requirement

Every L0 and L1 file must produce useful behavior with **all slots empty**. That is the
acceptance test for a fresh install: a project that has installed the toolkit and filled in
nothing should still be able to cast every spell and get either real work or a clear,
specific request for the one fact that's missing.

This is what makes the toolkit installable into an existing project on day one, before any
setup interview has run.

## Editing vendored files

Projects vendor their copy of L0/L1, so editing it is *possible*. It is not a workflow.

- A local edit to a vendored file is a **divergence**, surfaced by `/update-toolkit` for
  reconciliation — not a supported way to tailor the toolkit.
- Tailoring belongs in L2: fill a slot, add a project skill, write a reviewer rule.
- If tailoring a project requires editing L0/L1, that is a **missing slot** and should be
  reported as one. The fix is a new slot in the contract, not a local patch.

This hardens from principle to requirement because the underlying `skills update` was
verified to silently clobber local modifications — no warning, no merge, no hash check
against local state. A local edit is not just untracked; it is *fragile*.

## Checklist

Before any L0/L1 file is considered done:

- [ ] No project name, client name, or client-identifying term
- [ ] No absolute path, no `/Users/`, no `~`
- [ ] No hostname or port
- [ ] No build, test, or run command spelled out inline
- [ ] Every project fact replaced by a `**Slot:**` + `**If empty:**` pair
- [ ] Reads correctly with every slot empty
- [ ] L1 files contain technology facts only, never project facts
- [ ] `scripts/check-contract.sh` passes
