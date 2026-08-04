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
the two source repos ended up with the same command in two different states.

**The rule governs the fact, not the reference.** Some slots genuinely have several independent
consumers: `/plan` and `/retrofit` both need the build command, and neither can inherit it from the
other because retrofit operates on an arbitrary change with no plan to read. That is fine. What must
never happen is **two files declaring different fallbacks for the same slot** — that is the drift the
rule exists to prevent, and it is worse than duplication because the two behaviors diverge silently
when a slot is empty.

So: prefer deferring to an owner when one exists and the fact can reach you through an artifact —
`/implement-step` gets the build command from the plan that recorded it. When you genuinely need a
slot no artifact carries to you, reference it directly, and **keep the fallback wording identical to
every other reference to that same slot.**

Corollary: **toolkit-internal paths are not slots.** A spell reading
`.agents/skills/workflow/templates/spec.md` is naming something the toolkit itself controls and
installs, not a project fact. Name those paths directly; save slots for facts the project owns.

## No unguarded preconditions

The slot mechanism above handles one kind of absence: a project fact the toolkit reads. But **any**
instruction can depend on something existing — a document, an exemplar, a test harness, a git history, an
established mechanism — and the same discipline applies.

**No instruction may assume its precondition exists.** When it might not, say what to do instead, choosing
the highest rung that applies:

| Rung | Response |
|---|---|
| 1 | **Infer from the project** — something comparable exists to read |
| 2 | **Borrow from a named external reference** — another codebase, published docs, a sibling project. Ask for it; never assume one exists, and never silently import outside conventions as though they were the project's |
| 3 | **Seed thin, marked to grow** — create the artifact minimally now and let it accrete through use |
| 4 | **Proceed without, and say so** — name what was skipped |
| 5 | **Ask** — one specific question, when proceeding wrongly would be costly |

**Never fabricate.** Never invent a convention, layout, or mechanism and present it as the project's own.
A stated gap is recoverable; an invented convention gets followed, copied, and quietly becomes real.

### Rung 3 is the one worth reaching for

"Seed thin, accrete through use" runs through the toolkit already: an undocumented area gets a thin
area-level feature doc flagged for backfill (ADR 0005); starter facts ship as claims to verify and become
earned facts once confirmed; a project with no test harness gets a proposed location recorded as a new
convention. **Where a precondition is missing but creatable, create it thin and make the thinness
visible.** Visible debt with a known remedy beats both a hard failure and a confident invention.

### Why this needed to be written down

Every *slot* fallback in the toolkit was already guarded for absence, and almost no *non-slot*
instruction was. Not through carelessness — slots have a forcing function. Check 4 refuses a `**Slot:**`
without an `**If empty:**`, so writing one *made* the author consider absence. Nothing asked the same
question of "copy the closest existing component", so it went unasked.

Gate check 10 now supplies a forcing function for exemplar-dependent instructions specifically, since
that is the pattern that slipped twice. The general principle still depends on authoring discipline —
which is why it is stated here rather than left implicit in the slot rules.

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
