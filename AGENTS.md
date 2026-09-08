# Cantrip — agent context

This repo builds the toolkit; it is not a consuming project. There is no host site or app
here — the deliverable is markdown, templates, and small scripts.

See [README.md](README.md) for the layer model, invocation postures, and layout.

## Hard rule: this repo is public

Cantrip is public from day one, with no private staging period. Content is extracted from
real client projects, so:

- **Never commit client-identifying information.** No client names, URLs, hostnames,
  credentials, or verbatim client copy — in skills, starter facts, reviewer rules,
  examples, or commit messages.
- Ship the **shape and discipline** of high-value client assets, never their content.
- Starter facts are generic technical claims only (API behavior, version quirks), carrying
  provenance frontmatter — `applies:` and `verified:` — and no trace of where they were
  learned.

When extracting from a source repo, scrub as you write, not in a later pass.

<!-- contract-allow: department — this table states the rule and must name what it forbids -->

### Naming the source repos

This applies to *every* committed file, including ADRs, changelog entries, rationale notes, and
commit messages — not just shipped skills. Those documents legitimately need to discuss where
something came from, so use neutral aliases:

| Source | Refer to it as |
|---|---|
| The client project | **"the client project"** — never by name, and never by its assembly, host, or department names |
| The Umbraco 17 demo project | **"the demo project"** — safe to name directly; it is not client work |

When the distinction does not matter, "the source repos" is better than either. Run
`scripts/check-contract.sh` before committing; check 1 covers every publishable file precisely because
these documents are where the name tends to slip through.

### Naming the authoring org

**Different rule, different reason.** The org that authored this toolkit is credited in `LICENSE`, and
may be named in the README or a decision record — that is attribution, and it is intentional.

But it must **never appear inside a shipped skill.** "This is how <org> does it" is a project fact in an
L0 file, which the layer contract forbids regardless of whose project it is. A skill describes what must
be true; it does not describe one organization's way of working. Check 1b enforces exactly that split.

## Layer contract

- `skills/core/` (L0) and every stack pack under `skills/` (L1) must contain **no project facts**.
  They read L2 slots and degrade gracefully when a slot is empty.
- Anything project-specific belongs in a consuming project's L2 config, not here.
- Hardcoded absolute paths, tool versions, and environment assumptions are contract
  violations — they become slots.

## Authoring conventions

- Verbs are spells, nouns are reference.
- Spells chain by suggestion (`Next:` line), never by invoking another spell.
- Keep the core spellbook small — **ten workflow spells is the working ceiling**; merge two stages
  or add a router before letting the count creep ([ADR 0010](adr/0010-skills-not-commands.md)).
  `/setup` and `/update-toolkit` are configuration and maintenance, and count separately.
- Record shaping decisions as ADRs in [adr/](adr/); log user-visible changes in
  [CHANGELOG.md](CHANGELOG.md).
- **Contract checks cannot be fixture-tested, so verify a new one by hand and record it.**
  `scripts/check-contract.sh` does `cd "$(dirname "$0")/.."` on startup, so a subject run inside a
  `tests/` case directory re-scans the real repo instead of the fixture. Plant the defect the check
  is meant to catch, run the gate, confirm it fails and names the right file, then revert. Write the
  commands and their output into a validation log beside the increment.
- **Plant a defect for every rule a check claims.** A check that documents four rules and is tested
  on three will ship with the untested one broken. That has happened here: the category-table check
  promised a non-empty guidance cell and never tested for one, and the gate said `ok`. A passing gate
  says nothing about a branch nothing exercised.
- **Editing a reviewer agent needs a fresh session before you can test it.** Agent definitions are
  read once when a session starts. Skills hot-reload, so a new `.claude/skills/` symlink is available
  immediately, but a reviewer under `reviewer-discipline/agents/` does not: a reviewer dispatched
  after the edit still runs the definition from session start. The edit is on disk and the symlink
  resolves to it, which is what makes this look like a failed edit rather than a stale read.

  **Probe before you trust an after-test.** Ask the dispatched reviewer whether its own instructions
  contain the new rule, and to quote it. If it reports the rule absent, the definition is stale and
  the result is invalid rather than negative. Observed while adding the OWASP citation rule to
  `code-reviewer`: the before-test was real evidence, the after-test was not, and only the probe told
  them apart.

## Source repos

Extraction sources are granted as additional read-only working directories via
`.claude/settings.local.json` (git-ignored, machine-specific). Treat them as read-only
references: read to extract, never write, never copy identifying content.
