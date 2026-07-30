# CLAUDE.md

Project context lives in [AGENTS.md](AGENTS.md) — read that first.

## Claude-specific notes

- Skills live in `skills/` and are symlinked into `.claude/skills/` when this repo
  dogfoods its own toolkit. `.claude/` is an adapter layer only: thin wrappers, symlinks,
  and settings. Treat it as regenerable.
- Spells set `disable-model-invocation: true` — they are invisible to the model and cast
  only by the user as `/<name>`. Do not invoke a spell on the user's behalf.
- `.claude/settings.local.json` is git-ignored and holds machine-specific paths, including
  read-only access to the extraction source repos.
