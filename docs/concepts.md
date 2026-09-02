# How Cantrip works

The reasoning behind the toolkit's shape: why it keeps two kinds of document, how review is guarded,
and how core, packs, and your own project fit together. None of this is needed to install or cast a
spell — [README.md](../README.md) covers that. Read it when you want to know why the pieces are
arranged as they are.

---

## The artifacts, and why there are two kinds

Cantrip deliberately separates two kinds of artifact — source-of-truth docs describing what the
system does today, and temporal docs describing a change you are making to it.

| | Holds | Stays true until |
|---|---|---|
| `_features/<area>.md` | **What the system does now**, as Given/When/Then behavior in business language, one file per capability | the behavior itself changes |
| `_work/<slug>/` | **How one change got made** — its discovery, spec, plan, notes | it ships; then it moves to `_work/shipped/` |

**Grouped by lifecycle, not by type.** A capability doc and a spec are both markdown full of
scenarios, so a type-based layout would file them together — mixing source-of-truth docs in with
requirements that stopped being true the day they shipped, and no way to tell which is which.

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
| **Stack pack** | Knowledge about one technology — pinned to a major where majors break, versionless where they only add | this repo |
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
version they arrived in. A pack can also be wrong for you by **product** rather than by version —
Deploy guidance is correct on your Umbraco major and useless if you do not run Deploy — which is why
that content is its own pack.

**A pack is replaced, not upgraded.** When your platform moves a major, you swap one pack for the pack
named after the new major and leave the others alone. Reference names carry the version so your pinned
major is visible; **spell names never do**, so `/block` is still `/block` afterwards and nothing you
type has to change. [ADR 0015](../adr/0015-what-a-stack-pack-is-and-what-it-owes.md) has the full
reasoning, including the tests for deciding which axis a pack should be cut on.

### What you own

Your coding standards, style rules, commands, and team conventions all live in **`.agents/config/`**,
as *slots* — named markdown headings that toolkit files read. Four files, by what the fact is:

| File | What goes here | Examples |
|---|---|---|
| `paths.md` | **Where things live** — workspace directories, where each kind of code belongs, and which paths are generated output rather than authored source | `## Workspace`, `## Code layout`, `## Generated output` |
| `stack.md` | **How to run things** — build and test commands, local URL, runtime version and how to invoke it | `## Build`, `## Tests`, `## Local URL` |
| `conventions.md` | **How this project works** — your style decisions, commit and branch format, what a unit of work is, and any standing constraint a plan or review must respect | `## .NET style decisions`, `## Commit format`, `## Branch naming`, `## Unit of work` |
| `reviewer-rules/` | **Per-reviewer rules** — one file per reviewer, plus a shared two-line repo orientation they all read | `code.md`, `accessibility.md`, `performance.md` |

A slot is plain markdown under the heading — no schema, no templating. A rule as short as one line
under `## Branch naming` is a filled slot.

**Which file, when it is close.** A standard that shapes how any spell works goes in
`conventions.md`. A standard only one reviewer enforces goes in that reviewer's file under
`reviewer-rules/`, because reviewers load only their own — putting it in `conventions.md` would make
every reviewer carry the whole set.

**Slots are team settings, not personal ones.** `.agents/config/` is committed, so a slot you fill
binds everyone on the repo. There is deliberately no per-developer layer: if a preference should not
apply to your teammates, it belongs in your own agent tool's user-level config, outside the toolkit.

`/setup` drafts most of this by reading your repo, and asks only for what it cannot observe. You can
also just write a slot by hand at any time — nothing has to be regenerated.

Editing an installed file is possible but is a **divergence**, not a workflow — `/update-toolkit` will
surface it, and the bare installer would overwrite it. Tailoring belongs in your layer. If tailoring
needs a core edit, that is a missing slot; please report it as one.

[contract.md](contract.md) has the precise definition of each of the four and the rules a
toolkit file follows when it reads one — that one slot has one point of authority, and that a file
reading a slot has to degrade gracefully when it is empty rather than assuming a default.

---
