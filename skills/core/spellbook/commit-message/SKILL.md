---
name: commit-message
description: Analyze staged changes and propose a commit message that opens with a plain-language summary of what shipped, then briefly records the reasoning a future reader could not recover from the code. Follows the project's own commit conventions. Shows a summary, proposes the message, and waits for approval — never auto-commits.
disable-model-invocation: true
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git commit:*)
---

## Context

- Current git status: !`git status`
- Currently staged diff: !`git diff --staged`

Analyze the staged changes above and create a commit message. **Open with a plain-language
summary of what shipped, then compress the reasoning behind it.** Present tense throughout.

A commit message serves two readers, and one shape serves both. Someone scanning history wants
to know what landed, in ordinary words, without opening the diff. Someone reconstructing a
decision later — a person or an agent — wants the reasoning that isn't recoverable from the code.
Lead with the first so the second is optional depth rather than a toll gate. A message that opens
mid-argument makes every reader pay the reconstruction cost, including the ones who only wanted
to know what changed.

If nothing is staged, say so and stop.

## Format

Follow the project's existing commit convention.

**Slot:** `.agents/config/conventions.md` → `## Commit format`
**If empty:** infer the convention from `git log --oneline -30` — whether the project uses
conventional-commit type prefixes, emoji, ticket references, a subject-line length limit, or plain
prose. Match what the history actually does. If the history is inconsistent or empty, use a plain
imperative subject line under ~72 characters, followed by a body.

**Take *form* from the history, not length.** Prefixes, trailers, and casing should match what the
project already does. Body length and density come from **Body shape** below — history tends to
drift longer over time, and matching the longest recent message is how a habit becomes a
convention nobody chose.

## Body shape

**First, a plain summary — 1–3 sentences.** Say what now works, moved, or is fixed, in language
that needs no context from the diff, the branch name, or the spec. Name things as a reader would
go looking for them rather than as the internal argument names them. This paragraph should stand
on its own for someone who reads nothing else.

**Then the why — as tight as it will go.** The reasoning, constraint, or problem that motivated
the change. One short paragraph, or bullets when there are genuinely separate decisions. Detail
earns a place here only if a future reader would otherwise re-derive it; context that is merely
interesting does not qualify.

**Budget: aim for a body under ~150 words.** Exceed it only when the change truly carries several
independent decisions, and treat ~250 as the ceiling. If the reasoning outgrows the change, it
belongs in an ADR or the feature doc — point there instead of restating it in the commit.

Compress rather than delete. One specific sentence beats three hedged ones. Cut narrative
connectives, the blow-by-blow of how the work unfolded, asides about what was considered and
rejected, and anything the diff already states plainly.

## Calibration

Both messages below describe the same change and carry the same facts. The first opens mid-argument,
so the reader assembles the point themselves:

> Retry handling is orthogonal to how work is delivered — the backoff helpers name no transport — so
> keeping them inside the queue module meant a direct caller could not take them without queue
> configuration alongside. The extracted module is transport-agnostic, which makes substitution
> concrete: replacing the queue leaves retry behaviour untouched.

The second leads with what shipped, and the reasoning follows in half the words:

> Retry and backoff helpers move into their own module, so any caller can use them without
> depending on the queue.
>
> They never referenced a transport, but living in the queue module meant pulling queue
> configuration to reach them. Separated, replacing the queue leaves retry behaviour alone.

The test: read only the first sentence. If it tells you what was committed, the shape is right.

## Attribution trailers

If the project's convention includes attribution or co-authorship trailers, place them at the very
end, separated from the body by a blank line.

**Slot:** `.agents/config/conventions.md` → `## Commit trailers`
**If empty:** check `git log` for trailers the project already uses and match them. If there are
none, add none — do not introduce a trailer convention the project hasn't adopted.

## Output

1. Show a summary of what is currently staged
2. Propose the commit message
3. Ask for confirmation before committing

Before proposing, reread the draft against **Body shape**: does the first sentence say what
shipped, and is the body inside its budget? If the why has crowded out the summary, or the body
has run long, tighten it before showing it — not after the user asks.

**Do not auto-commit.** Wait for approval, and only commit if the user says so.

`Next: push, or /retrofit if this change skipped the workflow`
