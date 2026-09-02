# Installing in detail

What lands where, how to verify it, the install shapes, and what to do when a skill name collides
with one you already have. The two commands in [README.md](../README.md#quick-start) cover most
cases — this is for when they do not.

**Companions for the `umbraco-17` pack are named in
[README.md](../README.md#recommended-companions-for-the-umbraco-17-pack)** instead of here, because
that is a decision to make before installing rather than during.

---

## Check the install

```bash
scripts/check-install.sh          # or --verbose to list what is wired
```

Reports what is wired, what is degraded but working, and what is broken — with the fix for each. It
exits non-zero **only** when something is genuinely broken, so it is safe in a pipeline: a core-only
install with no configuration and no linked agents is a working install and passes.

## One extra step for parallel review

The three reviewer agents install as assets of `reviewer-discipline`, but registering them as
dispatchable subagents is something the installer cannot do. Link them once:

```bash
mkdir -p .claude/agents
for f in .claude/skills/reviewer-discipline/agents/*.md; do
  n=$(basename "$f"); ln -s "../skills/reviewer-discipline/agents/$n" ".claude/agents/$n"
done
```

Purely additive — any agents your project already has are untouched.

On Windows, copy instead. `check-install.sh` compares content rather than looking for a link, so a copy
registers identically. The tradeoff is that copies do not follow `/update-toolkit`, so re-copy after an
update.

```powershell
New-Item -ItemType Directory -Force .claude\agents
Copy-Item .claude\skills\reviewer-discipline\agents\*.md .claude\agents\
```

Until you do, `/code-review` and `/retrofit` run the three passes inline instead of in parallel.
Everything works either way — you are trading concurrency, not capability.

## Pick your install shape

`--all` is shorthand for `--skill '*' --agent '*'` — every skill, to **every agent tool it can detect**.
Verified, that means four write locations: `.agents/skills/` (real files), `.claude/skills/` (symlinks
to them), a top-level `agent/` directory, and — **if your project already has a bare `skills/`
directory, it writes into that too**. Nothing is overwritten, but a project with its own `skills/`
folder gets it populated.

If you only use Claude Code, this is cleaner — same skills, assets and agents included, one write
location, an existing `skills/` folder left alone, and **no symlinks anywhere**:

```bash
DISABLE_TELEMETRY=1 npx skills add robot-denny/cantrip/skills/core --skill '*' --agent claude-code -y
```

| | `--all` | `--skill '*' --agent claude-code` |
|---|---|---|
| Skills installed | 17 | 17 |
| Bundled assets and agents | ✓ | ✓ |
| Writes to | `.agents/`, `.claude/`, `agent/`, `skills/` | `.claude/` only |
| Canonical `.agents/` tree | ✓ | ✗ (files copied into `.claude/skills/`) |
| Other agent tools supported | ✓ | ✗ |
| Creates symlinks | ✓ `.claude/skills/` → `.agents/skills/` | ✗ real files only |

**On Windows, prefer the single-agent shape** — the last row is why, not the tool count. Symlinks exist
in the `--all` layout precisely *because* it serves several tools from one canonical tree, and Git for
Windows only materializes them when `core.symlinks=true`, which its installer disables unless the
account can create them. Where it is off you get a small text file containing the target path instead
of a link, so `.claude/skills/plan` looks present and contains no `SKILL.md` — the spell silently does
not exist. The single-agent shape writes real files and has nothing to materialize.

For several tools on Windows, run the installer once per tool with a single `--agent` each. That trades
the shared canonical tree for one independent copy per tool, and needs no symlink support.

Either way `skills-lock.json` records the source and a content hash per skill. If your project already
has one, the installer **merges** into it rather than replacing it.

Note that `--all` overrides a preceding `--skill`, so `--skill workflow --all` installs everything.

> **Every install command shown here sets `DISABLE_TELEMETRY=1`**, because `npx skills` uploads
> skill file contents by default. Keep the prefix on any command you copy — a repo holding client work,
> internal architecture, or unreleased plans should not be publishing its skill files
> ([ADR 0009](../adr/0009-skills-cli-role-split.md)).

## If your project already has commands with these names

**A skill shadows a same-named command.** There is no namespace and no error — install `/spec` and an
existing `.claude/commands/spec.md` becomes present but unreachable. It is not a fallback you can still
get to.

This matters most for a project already running its own version of this workflow. **Install on a branch
first.** Shadowing is then contained: switching back restores your commands intact, and you can compare
the two side by side. Commands whose names the toolkit does not use are unaffected.
