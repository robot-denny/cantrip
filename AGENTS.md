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

### Naming the source repos

This applies to *every* committed file, including ADRs, changelog entries, rationale notes, and
commit messages — not just shipped skills. Those documents legitimately need to discuss where
something came from, so use neutral aliases:

| Source | Refer to it as |
|---|---|
| The client project | **"the client project"** — never by name, and never by its assembly, host, or department names |
| The Umbraco 17 demo project | **"the demo project"** — safe to name directly; it is not client work |

When the distinction does not matter, "the source repos" is better than either. Run
`scripts/check-contract.sh` before committing; check 1 is repo-wide precisely because these
documents are where the name tends to slip through.

## Layer contract

- `skills/core/` (L0) and `skills/umbraco-17/` (L1) must contain **no project facts**.
  They read L2 slots and degrade gracefully when a slot is empty.
- Anything project-specific belongs in a consuming project's L2 config, not here.
- Hardcoded absolute paths, tool versions, and environment assumptions are contract
  violations — they become slots.

## Authoring conventions

- Verbs are spells, nouns are reference.
- Spells chain by suggestion (`Next:` line), never by invoking another spell.
- Keep the core spellbook to 6–8 spells; add a router spell before letting the count creep.
- Record shaping decisions as ADRs in [adr/](adr/); log user-visible changes in
  [CHANGELOG.md](CHANGELOG.md).

## Source repos

Extraction sources are granted as additional read-only working directories via
`.claude/settings.local.json` (git-ignored, machine-specific). Treat them as read-only
references: read to extract, never write, never copy identifying content.
