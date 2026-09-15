# 0019. The documented default install shape

**Status:** Accepted — supersedes decision 4 of [ADR 0004](0004-install-layout-corrections.md)
**Date:** 2026-09-15

## Context

ADR 0004 verified two install shapes and documented the `--all` one:

> Core only: `npx skills add <repo>/skills/core --all`

That was recorded as a subpath-scoping finding rather than as a recommendation, and the README
carried it forward as the default for the toolkit's whole life. `docs/installing.md` separately told
Windows readers to use the single-agent shape instead, under a heading two scrolls below the first
command.

Watching a team install the toolkit showed what that split costs. **Most Windows users ran `--all`**,
because they reached the README's Quick start, copied it, and never opened the installation page. The
platform recommendation was correct, complete, and in the one place nobody looked.

Three further findings from the same observation, each of which the split caused rather than merely
failed to prevent:

- `DISABLE_TELEMETRY=1 npx skills ...` is bash syntax. PowerShell reads the whole first word as a
  command name, so the README's commands fail on Windows before telemetry is even the question.
- The README said to keep the prefix on every command; the installation page said one setting
  covers a session. Both were true in their own shell and the pair read as a contradiction.
- The reviewer registration in the README was the `ln -s` loop, with the Windows copy deferred to the
  installation page. Readers who got there had usually run the link command already.

The deeper problem is that **a symlink install is not a personal choice.** The install is committed,
so `--all` commits symlinks from `.claude/skills/` into `.agents/skills/`. Git for Windows
materializes a committed symlink only when `core.symlinks=true`, which its installer turns off unless
the account can create symlinks. One Mac install therefore breaks every Windows clone, silently, with
a text file where a skill directory should be.

## Decision

**The single-agent shape is the documented default, on every platform.**

```
npx skills add robot-denny/cantrip/skills/core --skill '*' --agent claude-code -y
```

`--all` moves to `docs/installing.md` as the case for running several agent tools from one tree.

**The README's Quick start is self-sufficient for a first install.** It carries a complete block per
platform, and every decision a first-time reader has to make is above the command that depends on it.
Nothing required to get a working install lives behind a link. `docs/installing.md` holds what a
reader needs afterwards: verification, collisions, the other shape, updating, and the silent failures.

**Reviewer agents are registered by copying on both platforms**, using forms that skip a file the
project already has. The symlink loop stays documented for teams with no Windows users. `/update-toolkit`
gains a step that finds stale copies and offers the refresh, which is the cost copying incurs.

**Telemetry is documented as one statement per shell session**, in each shell's own syntax, rather
than as an inline prefix per command. Contract check 15 now scopes coverage to the fenced block in
markdown instead of the line: an invocation passes when an earlier line of the same fence sets the
variable. Outside a fence, and in every `.sh` file, the inline prefix is still required, because
those are lines someone pastes on their own.

## Alternatives considered

**Keep `--all` as the default and make the Windows warning louder.** Rejected. The warning was
already correct and already present. Making it louder does not move it to where the reader is, and
the failure it prevents is silent, so a reader who misses it gets no second signal.

**Ask the reader to choose a shape in the Quick start.** Rejected. A decision presented before
someone knows what symlinks cost them here is a decision they make by guessing. The safe shape is
safe for nearly everyone, so the right move is to remove the choice from the critical path rather
than to highlight it.

**Keep the line-level telemetry rule and document the bash prefix only.** Rejected: the gate would
then enforce the one form that fails on Windows. A rule that rejects the working syntax is a rule
with a bug, not a stricter rule.

**Symlink the reviewers on Mac and copy on Windows, as before.** Rejected. It makes the committed
result depend on who installed, which is the same trap one layer down.

## Consequences

- **Consumers on `--all` are not broken and are not asked to migrate.** Both shapes remain supported
  and `check-install.sh` verifies all three layouts. The change is to what a new reader is told.
- `check-install.sh` prints the single-agent shape in its reinstall hints and a `cp -n` in its
  registration hint. Its fixture expectation changed with it.
- **Copying is now the default, so stale reviewers become the common failure** rather than an edge
  case. `/update-toolkit` step 6 exists to catch it, and it must distinguish a stale copy from a
  reviewer the project tailored on purpose, because overwriting the second is the data loss the whole
  wrapper exists to prevent.
- ADR 0004's subpath-scoping finding stands untouched. Only the invocation printed alongside it is
  superseded.
- The README's Quick start grew. That is the trade accepted here: a longer first page against a
  second page nobody opened.
