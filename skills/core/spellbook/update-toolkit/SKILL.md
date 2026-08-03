---
name: update-toolkit
description: Update the installed toolkit safely. Wraps the skills installer with a git guard, because the underlying update silently overwrites local modifications with no warning — this makes every change reviewable, tells you which of your tailorings were reverted, and helps move them somewhere updates cannot reach. Run when you want newer toolkit versions.
disable-model-invocation: true
allowed-tools: Read, Edit, Glob, Grep, Bash(git status:*), Bash(git diff:*), Bash(git stash:*), Bash(git check-ignore:*), Bash(git rev-parse:*), Bash(npx skills:*)
---

<!-- contract-allow: npx — this spell wraps the toolkit's own installer, so it must name it. Not a
     project build command, which is what the technology-name check exists to catch. -->

You are updating the installed toolkit. **The underlying installer silently overwrites local
modifications** — no warning, no merge, no check against local state. Verified: a local edit to an
installed skill was reverted to pristine, and the output reported success with no mention of it.

Your whole job is to make that safe and reviewable. **Git is the safety net** — that is why every step
below revolves around it.

## Step 1 — Establish the safety net

Three preconditions, in order. Stop on any failure.

**a. This must be a git repository.** If not, stop: `Not a git repository. The update overwrites
local modifications with no warning and nothing here could recover them. Initialize git, commit the
installed skills, then re-run.`

**b. The working tree must be clean.** Run `git status --porcelain`. If anything is uncommitted, stop
and say so. This is not fussiness: after the update runs, `git diff` is the *only* record of what it
changed, and pre-existing uncommitted work would be indistinguishable from the update's own edits.
Offer the two ways forward — commit the work, or stash it — and let the user choose.

**c. The installed skills must be tracked by git.** Check with `git check-ignore` against the install
directory and confirm files there are tracked. If they are ignored or untracked, stop:

> The installed skills are not tracked by git, so an update that overwrites your tailorings would
> leave no trace. Either commit them first, or accept that this update is irreversible and say
> `proceed anyway`.

Only continue without the net on explicit confirmation.

## Step 2 — Record what is installed

Read `skills-lock.json` and list what is installed, with its source. Report the count and the sources
in one line, so the user knows the blast radius before anything runs.

Note the lockfile's hash is **not** a plain digest of the installed file, so it cannot be used to
detect local modification. Git is the mechanism; do not attempt a hash comparison.

## Step 3 — Update

Run the installer's update with telemetry disabled — it uploads skill file contents by default:

```
DISABLE_TELEMETRY=1 npx skills update -y
```

Report its output verbatim, including any warnings. A "failed to check for deleted skills" warning is
known and benign: the lockfile records the repository without the subpath it was installed from, so
enumeration of the source can fail while the update itself succeeds.

## Step 4 — Review every change

This is the step the wrapper exists for. Run `git diff --stat` over the install directory, then
`git diff` for detail.

**Classify each changed file into one of three buckets:**

**Clean upstream update** — the diff only adds or revises upstream content, and touches nothing the
project had changed. Nothing to do.

**Reverted local tailoring** — the diff *removes* content that upstream never had. **This is a
tailoring the update destroyed.** Quote the removed content for the user; it is the thing they would
otherwise discover missing weeks later.

**Both** — upstream revised a file the project had also edited. Show the upstream change and the lost
local change separately, since the resolution differs for each.

If `git diff` is empty, say so plainly: everything was already current, and nothing was lost.

## Step 5 — Reconcile

For each reverted tailoring, present three options and a recommendation:

1. **Move it to L2 (recommended).** A tailoring that gets clobbered by updates belongs in a slot, a
   project skill, or a reviewer rule — somewhere updates cannot reach. Read `docs/contract.md` for
   where it fits, and propose the specific destination.
2. **Restore it in place**, accepting that the next update will clobber it again. Offer the exact
   `git checkout -p` or `git revert` to bring it back.
3. **Let it go**, if upstream now covers what it was doing.

**A tailoring with nowhere to go in L2 is a missing slot, not a user error.** Say so explicitly, and
suggest reporting it upstream — the contract treats "tailoring requires editing core" as a defect in
the toolkit, not in the project.

Apply nothing without confirmation.

## Step 6 — Report

```
Toolkit update
  Skills checked:     N
  Cleanly updated:    N
  Tailorings reverted: N   <- these need a decision
  Unchanged:          N

Next: <the reconciliation decisions, or "nothing further — everything was current">
```

If tailorings were reverted and the user has not yet decided, end there and wait. **Do not commit.**
The user reviews and commits, exactly as with every other spell.

## Why this wrapper exists

The bare update is not merely unhelpful about local edits — it is actively unsafe, because it reports
success while destroying work. Wrapping it converts a silent data-loss path into a reviewable diff.

This is also why the contract states that editing a vendored file is a **divergence rather than a
workflow**: not because tailoring is wrong, but because *that* place for it is fragile. The right
response to a clobbered edit is almost never to restore it — it is to move it where updates cannot
reach.
