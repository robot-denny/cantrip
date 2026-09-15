# Installing in detail

[README.md](../README.md#quick-start) has the install itself, for macOS, Linux and Windows. This
page is everything around it: how to turn telemetry off in your shell, the second install shape and
when it earns its keep, checking what landed, name collisions with commands you already run,
updating later, and the handful of failures that give you no signal at all.

**Companions for the `umbraco-17` pack are named in
[README.md](../README.md#recommended-companions-for-the-umbraco-17-pack)** rather than here, because
that is a decision to make before installing rather than during.

---

## Turning telemetry off, once per shell

`npx skills` uploads the contents of your skill files by default. Every documented command turns
that off, because a repo holding client work, internal architecture, or unreleased plans should not
be publishing its skill files ([ADR 0009](../adr/0009-skills-cli-role-split.md)).

**It is one statement per shell session, not one per command.**

| Your shell | Set it with | It lasts for |
|---|---|---|
| bash or zsh | `export DISABLE_TELEMETRY=1` | the rest of that terminal session |
| PowerShell | `$env:DISABLE_TELEMETRY = "1"` | the rest of that PowerShell session |
| Command Prompt | `set DISABLE_TELEMETRY=1` | the rest of that window |

Run it before your first `npx skills` command and every install in that window is covered. Open a
new window and you set it again. Nothing reports whether it took, so if you are unsure, set it again
before installing.

**PowerShell cannot take the variable inline.** `DISABLE_TELEMETRY=1 npx skills add ...` is bash
syntax. PowerShell reads the whole first word as a command name and the line fails. If you want it
on one line there, separate the two statements with a semicolon:

```powershell
$env:DISABLE_TELEMETRY = "1"; npx skills add robot-denny/cantrip/skills/core --skill '*' --agent claude-code -y
```

---

## Choose your install shape

There are two. The README uses the first, and most projects should stay with it.

### The single-agent shape, which the README uses

```bash
export DISABLE_TELEMETRY=1
npx skills add robot-denny/cantrip/skills/core --skill '*' --agent claude-code -y
```

Real files land in `.claude/skills/` and nowhere else. No symlinks, no `.agents/` tree, and an
existing `skills/` directory of your own is left alone. For a different tool, replace `claude-code`
with `cursor`, `codex`, or `copilot`, and run the command once per tool you want to serve.

### `--all`, when you run several agent tools from one tree

```bash
export DISABLE_TELEMETRY=1
npx skills add robot-denny/cantrip/skills/core --all
```

`--all` is shorthand for `--skill '*' --agent '*'`: every skill, to every agent tool it can detect.
It builds one canonical tree at `.agents/skills/` and symlinks `.claude/skills/` to it, so several
tools share a single copy. That sharing is the benefit, and symlinks are what it costs.

It also writes more widely than most people expect. A top-level `agent/` directory gets a copy, and
**if your project already has a bare `skills/` directory, the installer writes into that too.**
Nothing is overwritten, but a project with its own `skills/` folder will find it populated. The safe
cleanup is `git clean -fd agent skills`, never `rm -rf skills/`, which would take your own tracked
content with it.

| | `--skill '*' --agent claude-code` | `--all` |
|---|---|---|
| Core skills installed | 19 | 19 |
| Bundled assets and agents | ✓ | ✓ |
| Writes to | `.claude/` only | `.agents/`, `.claude/`, `agent/`, and `skills/` if you already have one |
| Canonical `.agents/` tree | ✗ (files copied into `.claude/skills/`) | ✓ |
| Other agent tools supported | one per run | ✓ |
| Creates symlinks | ✗ real files only | ✓ `.claude/skills/` → `.agents/skills/` |
| Safe to commit on a mixed team | ✓ | ✗ |

Those counts are core only. Each pack adds its own on top, so a checker run reports a larger number.

### Does it matter which machine you install from?

Not for you. It matters for everyone who clones afterwards.

The install is committed, so your teammates get the toolkit by pulling rather than by repeating any
of this. Whatever shape you picked is the shape they get.

Under `--all`, what you commit includes the symlinks pointing from `.claude/skills/` into
`.agents/skills/`. Git for Windows only materializes a committed symlink when `core.symlinks=true`,
and its installer turns that off unless the account can create symlinks. A Windows teammate then
gets a small text file holding a path where a skill directory should be. So `.claude/skills/plan`
looks present, contains no `SKILL.md`, and `/plan` does not exist. Nothing says so.

**A Mac install is therefore not the safer one.** A Mac install with `--all` is the shape most
likely to break for somebody else. The single-agent shape commits real files, which clone
identically on every platform, and that is why the README uses it.

Windows can also drop a symlink at the writing end. Creating one there needs Developer Mode or an
elevated shell, so the installer may not manage it even on a fresh install. Same symptom, equally
quiet.

Two things follow.

**Whoever installs first sets the shape for everyone.** If a Windows install landed first and
committed real files under `.claude/skills/`, keep that shape on the Mac too rather than
reinstalling with `--all`. Do not mix shapes in one repository.

**Once it is installed, the platform stops mattering.** Casting a spell reads files. It creates no
links and needs none, so a Windows user and a Mac user work identically from the same commit. The
platform question belongs to installing and updating, not to using.

### Two smaller notes

Both were observed rather than tested against a recorded CLI version, so re-check them if they
matter to you. Either shape writes `skills-lock.json`, recording the source and a content hash for
each skill; if your project already has one, the installer **merges** into it rather than replacing
it. And `--all` overrides a preceding `--skill`, so `--skill workflow --all` installs everything.

---

## Turn on parallel review

The three reviewer agents install as assets of `reviewer-discipline`. Registering them as agents
your tool can dispatch is the one step the installer cannot do for you. The README's step 3 does it.

Until you do it, `/code-review` and `/retrofit` run their three passes one after another rather than
in parallel. Everything works either way. You are trading speed rather than capability, which is
what makes this easy to skip forever: nothing later tells you that you did.

### Copying is the portable answer

The README copies the files on both platforms. A copy clones identically everywhere, and
`check-install.sh` compares file contents rather than looking for a link, so a copy verifies as
registered.

**The cost of copying is that updates do not follow.** A copy in `.claude/agents/` keeps its old
content after an update, and nothing reports that it did. `/update-toolkit` step 6 exists for this:
it lists the registrations that no longer match the installed source and offers the refresh. Run it
by hand if you updated some other way. The `-f` and `-Force` are what overwrite the stale copies:

```bash
cp -f .claude/skills/reviewer-discipline/agents/*.md .claude/agents/
```

```powershell
Copy-Item .claude\skills\reviewer-discipline\agents\*.md .claude\agents\ -Force
```

### Linking instead, on a team with no Windows users

On macOS and Linux you can symlink them, and then updates follow with nothing to re-run. Take this
only if you are confident nobody will clone the repository on Windows, for the reason in
[Does it matter which machine you install from?](#does-it-matter-which-machine-you-install-from)
above.

```bash
mkdir -p .claude/agents
for f in .claude/skills/reviewer-discipline/agents/*.md; do
  n=$(basename "$f"); ln -s "../skills/reviewer-discipline/agents/$n" ".claude/agents/$n"
done
```

`ln -s` refuses to overwrite an existing file, so this is additive in the same way the copy is.

### If your project already has a reviewer by one of these names

The README's copy commands skip any file that already exists, and `ln -s` errors with `File exists`.
Either way, that is the expected case rather than a fault, and the advice is to leave it alone. Keep
yours and let the toolkit's stay unregistered, or adopt the toolkit's under a different filename so
both remain available. **Do not force a copy or a link over your own reviewers.** `/code-review`
discovers whichever reviewers are registered rather than assuming the canonical three, so a tailored
one under a different name is used as it stands.

---

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

It is a bash script, so on Windows run it from Git Bash rather than PowerShell.

It reports what is wired, what is degraded but working, and what is broken, with the fix for each.
It exits non-zero **only** when something is genuinely broken, so it is safe in a pipeline. A
core-only install with no configuration and no linked agents is a working install, and it passes.

Delete `check-install.sh` afterwards, or leave it out of the commit. It is not part of the install.

---

## If your project already has commands with these names

**A skill shadows a command of the same name.** There is no namespace and no error. Install `/spec`
on a project with an existing `.claude/commands/spec.md` and that command becomes present but
unreachable. It is not a fallback you can still get to.

This matters most on a project already running its own version of this workflow. **Install on a
branch first.** Shadowing is then contained: switching back restores your commands intact, and you
can compare the two side by side. Commands whose names the toolkit does not use are unaffected.

---

## Updating later

Cast `/update-toolkit` rather than re-running the installer. The bare installer overwrites local
modifications with no warning and reports success. `/update-toolkit` wraps it behind a git guard, so
every change is reviewable and it names whichever of your tailorings were reverted.

Two things to know. Re-copy the reviewer agents afterwards, as above, because copies do not follow.
And `.agents/config/` is safe: it is your configuration rather than installed content, so nothing in
an update reaches it. A tailoring you want to survive updates belongs there.

---

## Things that go wrong quietly

None of these announce themselves, which is the only reason they are worth a table.

| Symptom | Cause | Fix |
|---|---|---|
| A skill directory exists but holds no `SKILL.md` | `--all` was used, and a symlink did not materialize on Windows | Reinstall with `--skill '*' --agent claude-code` |
| A spell does nothing when you cast it | A project command of the same name is shadowing it, or the skill did not land | Run the checker |
| `DISABLE_TELEMETRY=1 npx skills ...` fails on Windows | That is bash syntax | Set `$env:DISABLE_TELEMETRY = "1"` as its own statement first |
| `/code-review` feels slow | The reviewers were never registered, so the passes run in sequence | Re-run step 3 of the README's quick start |
| Reviewers behave like the old version after an update | The copies did not follow | Re-copy with `-f` or `-Force` |
| A teammate's plans lack backoffice guidance | The `umbraco-17` companions are enabled in user settings only | Move `enabledPlugins` into the committed `.claude/settings.json` |
| `/update-toolkit` reverted a local edit to a skill | Expected. It reports what it reverted | Move the tailoring into `.agents/config/`, which updates cannot reach |
| A top-level `agent/` or a populated `skills/` folder appeared | `--all` scatters copies across every target it detects | `git clean -fd agent skills`, never `rm -rf skills/` |
