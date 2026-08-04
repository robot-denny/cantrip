---
name: memory-discipline
description: How an agent with persistent project memory should write, organize, and calibrate it — the MEMORY.md index plus topic files, the entry format with its Why and How-to-apply lines, the three entry types (pattern, false-positive suppression, fixed-with-guard), and what belongs in memory versus what does not. Consult when writing to or reorganizing agent memory, when deciding whether an observation is worth persisting, or when a recurring wrong finding needs calibrating away.
---

# Agent memory discipline

Persistent memory is what turns a competent reviewer into one that knows *this* project. Its value
is almost entirely in **calibration** — learning what to stop flagging is worth as much as learning
what to flag, because a reviewer that repeats a wrong finding every session gets ignored entirely.

## Two memory systems — know which one you are writing to

A project usually has **two**, and this skill governs only the first:

1. **Per-agent project memory** — the reviewers' own directories, inside the repo. Committed and
   shared with the team, so it is subject to the repo's rules, including any prohibition on
   client-identifying content. **This is what the discipline below applies to.**
2. **Cross-session project memory** — a per-project store outside the repo entirely, not managed by
   this toolkit and not covered by its layout or entry format.

Two consequences worth stating, because both are easy to get wrong:

- **Backups must cover both.** A backup scoped to the repo silently misses the second, which lives
  outside it and often has no version history at all.
- **Renaming an agent orphans its memory.** Per-agent memory is keyed by directory name. If an
  agent is renamed — during a migration, say — its directory must be renamed to match, or the
  memory stays on disk, unread, while review appears to work normally. That silent-degradation mode
  is worse than an error.

## Layout

```
<memory-dir>/
  MEMORY.md          # index — always loaded into the system prompt
  <topic>.md         # detailed notes, one file per topic
```

**`MEMORY.md` is an index, not a container.** It is loaded into the system prompt every session and
truncated past 200 lines, so it holds one line per topic file and nothing else:

```markdown
# <Agent Name> — Memory Index

- [Recurring Anti-Patterns](patterns-antipatterns.md) — oversized payloads, reserved aliases, hardcoded identifiers
- [Auth Setup Conventions](auth-conventions.md) — the client-credentials pattern, the env-var typo, import cycle
```

The hook after the em dash matters: it is what tells you whether to open the file. Write it as a
list of the specific things inside, not a category label.

**Organize topic files semantically, never chronologically.** A file per subject area, not per
session or per date.

## Entry format

Each entry in a topic file is a claim, its reasoning, and its operational consequence:

```markdown
## <The claim, as a statement>

<One or two sentences of detail.>

**Why:** <the underlying reason — what makes this true, not just that it is>

**How to apply:** <what to do differently next time you see it>

**Type:** pattern | false-positive-suppression | fixed-with-guard
**Recorded:** YYYY-MM-DD

---
```

Topic files carry frontmatter with `name`, `description`, and `metadata.type`.

The **How to apply** line is what makes an entry actionable rather than trivia. If you cannot write
one, you do not yet understand the finding well enough to persist it.

## The three entry types

Every durable entry is one of these. Naming the type keeps the memory honest about what it is
doing:

**`pattern`** — a defect to catch. *How to apply* starts with "Flag…".
> Flag any wholesale object serialization into a client-visible attribute. Require a scoped
> projection.

**`false-positive-suppression`** — calibration. A finding you previously raised that was **wrong**,
recorded so you stop raising it. *How to apply* starts with "Do not flag…" or "Accept…".
> Do not flag the module-level cache as a concurrency bug when the runner is single-worker.

This type is the highest-value and the most often skipped. Every wrong finding you suppress buys
back trust in the ones you do raise.

**`fixed-with-guard`** — a real issue, since resolved, kept so a regression is caught rather than
re-litigated. *How to apply* names the condition for it becoming live again.
> Resolved in current code. If a future change reintroduces its own config loading, the ordering
> bug returns — flag it then.

## What to save

- Stable patterns and conventions confirmed across **multiple** interactions
- Calibrations: findings that turned out to be wrong, and why
- Key architectural decisions, important paths, and project structure
- Preferences for workflow, tools, and communication style
- Solutions to recurring problems, and debugging insights

## What not to save

- **Session-specific context** — the current task, in-progress work, temporary state
- **Anything unverified.** Check against project docs before writing. A speculative conclusion
  drawn from a single file is worse than no entry, because it will be trusted later.
- Anything duplicating or contradicting the project's guidance files
- Facts the repository already records — code structure, git history

## Explicit requests

When the user asks you to remember something across sessions, save it — no need to wait for
repetition. When they ask you to forget something, find and remove the relevant entries.

Memory that is project-scoped and committed is **shared with the team**, so write it for a
colleague reading it cold, and keep it free of anything client-identifying if the repository is
public.

## Maintenance

- Update or delete entries that turn out to be wrong. A stale memory is an active liability, not
  neutral clutter.
- When a version-tagged claim's version moves, re-verify rather than assuming it still holds.
- If `MEMORY.md` approaches 200 lines, you are keeping content in the index — move it into topic
  files.

**Slot:** `.agents/config/conventions.md` → `## Memory`
**If empty:** use the layout and entry format above unchanged. They are the default, not a
placeholder.
