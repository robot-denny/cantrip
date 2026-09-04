# Installing in detail

The two commands in [README.md](../README.md#quick-start) cover most installs. This page is for the
rest: choosing an install shape, checking what landed, turning on parallel review, and name
collisions with commands you already have.

**Companions for the `umbraco-17` pack are named in
[README.md](../README.md#recommended-companions-for-the-umbraco-17-pack)** rather than here, because
that is a decision to make before installing rather than during.

---

## Choose your install shape

There are two, and it is worth picking before you run anything.

`--all` is shorthand for `--skill '*' --agent '*'`: every skill, to every agent tool it can detect.
In practice that is four write locations. `.agents/skills/` holds the real files. `.claude/skills/`
holds symlinks to them. A top-level `agent/` directory gets a copy. And **if your project already
has a bare `skills/` directory, the installer writes into that too.** Nothing is overwritten, but a
project with its own `skills/` folder will find it populated.

If Claude Code is the only agent tool you use, the single-agent shape is cleaner. Same skills, same
bundled assets and agents, one write location, an existing `skills/` folder left alone, and no
symlinks anywhere:

```bash
DISABLE_TELEMETRY=1 npx skills add robot-denny/cantrip/skills/core --skill '*' --agent claude-code -y
```

| | `--all` | `--skill '*' --agent claude-code` |
|---|---|---|
| Core skills installed | 18 | 18 |
| Bundled assets and agents | ✓ | ✓ |
| Writes to | `.agents/`, `.claude/`, `agent/`, and `skills/` if you already have one | `.claude/` only |
| Canonical `.agents/` tree | ✓ | ✗ (files copied into `.claude/skills/`) |
| Other agent tools supported | ✓ | ✗ |
| Creates symlinks | ✓ `.claude/skills/` → `.agents/skills/` | ✗ real files only |

Those counts are core only. Each pack you add brings its own on top, so a checker run will report a
larger number.

### On Windows, use the single-agent shape

Several things on this page fail without announcing themselves. This is the one that leaves a spell
looking installed when it is not. Decide it on the symlink row, not on how many tools each shape
supports.

The `--all` layout uses symlinks because it serves several tools from one canonical tree. Windows can
drop them at either end. Creating a symlink there needs Developer Mode or an elevated shell, so the
installer may not manage it. And where symlinks were committed and a teammate clones the repo, Git
for Windows only materializes them when `core.symlinks=true`, which its installer turns off unless
the account can create them.

The symptom is the same from both directions. You get a small text file holding the target path
instead of a link, so `.claude/skills/plan` looks present, holds no `SKILL.md`, and the spell does
not exist with nothing saying so.

The single-agent shape writes real files and has nothing to materialize.

For several tools on Windows, run the installer once per tool with a single `--agent` each. That
trades the shared canonical tree for one independent copy per tool, and needs no symlink support.

> **Every install command on this page sets `DISABLE_TELEMETRY=1`**, because `npx skills` uploads
> skill file contents by default. Keep the prefix on any command you copy. A repo holding client
> work, internal architecture, or unreleased plans should not be publishing its skill files
> ([ADR 0009](../adr/0009-skills-cli-role-split.md)).

Two smaller notes, both observed rather than tested against a recorded CLI version, so re-check them
if they matter to you. Either shape writes `skills-lock.json`, recording the source and a content
hash for each skill; if your project already has one, the installer **merges** into it rather than
replacing it. And `--all` overrides a preceding `--skill`, so `--skill workflow --all` installs
everything.

## Check the install

**The checker is not part of your install.** Installs are scoped to `skills/`, and the script lives
in the toolkit repository, so nothing puts it beside the skills you just added. Fetch it when you
want it:

```bash
curl -sO https://raw.githubusercontent.com/robot-denny/cantrip/main/scripts/check-install.sh
bash check-install.sh          # or --verbose to list what is wired
```

Cloning the repository somewhere and running `scripts/check-install.sh` from there works equally
well. Either way it inspects the project you run it in.

It reports what is wired, what is degraded but working, and what is broken, with the fix for each.
It exits non-zero **only** when something is genuinely broken, so it is safe in a pipeline. A
core-only install with no configuration and no linked agents is a working install, and it passes.

## Turn on parallel review

The three reviewer agents install as assets of `reviewer-discipline`. Registering them as agents
your tool can dispatch is the one step the installer cannot do for you. Link them once:

```bash
mkdir -p .claude/agents
for f in .claude/skills/reviewer-discipline/agents/*.md; do
  n=$(basename "$f"); ln -s "../skills/reviewer-discipline/agents/$n" ".claude/agents/$n"
done
```

This is purely additive. Any agents your project already has are untouched, and `ln -s` will not
overwrite one.

**If your project already has an agent by one of these names**, you get a `File exists` error for
that one. That is the expected case rather than a fault, and the checker's advice is to leave it
alone: keep yours and let the toolkit's stay unregistered, or adopt the toolkit's under a different
filename so both remain available. Do not force-link over your own reviewers. `/code-review`
discovers whichever reviewers are registered rather than assuming the canonical three, so a tailored
one under a different name is used as it stands.

On Windows, copy instead. `check-install.sh` compares file contents rather than looking for a link,
so a copy registers identically. The tradeoff is that copies do not follow `/update-toolkit`, so
re-copy after an update.

```powershell
New-Item -ItemType Directory -Force .claude\agents
Copy-Item .claude\skills\reviewer-discipline\agents\*.md .claude\agents\
```

Until you do this, `/code-review` and `/retrofit` run the three passes one after another rather than
in parallel. Everything works either way, and you are trading speed rather than capability.

## If your project already has commands with these names

**A skill shadows a command of the same name.** There is no namespace and no error. Install `/spec`
on a project with an existing `.claude/commands/spec.md` and that command becomes present but
unreachable. It is not a fallback you can still get to.

This matters most on a project already running its own version of this workflow. **Install on a
branch first.** Shadowing is then contained: switching back restores your commands intact, and you
can compare the two side by side. Commands whose names the toolkit does not use are unaffected.
