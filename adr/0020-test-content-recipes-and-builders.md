# 0020. Test content: a recipe the toolkit writes, a builder the project owns

**Status:** Accepted
**Date:** 2026-11-23

## Context

The client project built a way to generate QA test pages for any block or page type. It has two
halves: a spell that reads a component's schema and writes a committed JSON **recipe** of variations,
and a project-side **builder** (several thousand lines of C# and an admin dashboard, with tests) that
builds test pages from recipes in each environment. Extracting it raised three questions the
existing ADRs do not answer.

1. **The spell is useless alone.** A recipe nothing can build is a file. But the builder is shaped by
   one project's page grid, shared-block pattern, fixtures and brands, and is far beyond the
   markdown, templates and small scripts this repository ships.
2. **The method is not Umbraco's.** The variation rules (a realistic baseline, layout differences one
   at a time, content stress combined, common setups first, mixed backgrounds, rich text on every
   background) hold for any component system. Only how a schema is read, how a layout is expressed
   and how a value is stored differ by platform.
3. **A second platform was asked for at once.** The same capability is wanted for Optimizely CMS,
   for which no pack exists. Only a CMS 12 project was available to check against.

## Decision

- **The toolkit ships the recipe side and a builder blueprint; the project builds its builder once.**
  Each CMS pack carries a `/test-content` spell and a `<pack>-test-content-builder` reference. The
  reference is design input for `/spec` and `/plan`: the modules, the platform services each uses,
  the stored value formats, and the tests that pin them. It asserts what the platform decided and
  names what the project decides (its page grid, test-content root, environments, allowed real
  content) without answering it, per [0015](0015-what-a-stack-pack-is-and-what-it-owes.md) §7.
- **The method is a core reference, `test-content-principles`.** It holds the general rules G1 to
  G12, the gray-area discipline, a stack-neutral recipe format, value tokens, page-type recipes,
  refresh semantics, the report, and the list of guarantees any builder owes a recipe. It names no
  technology, and both packs defer to it rather than restating it. Its template is the starting point
  for a project's QA-owned rules file.
- **The page's layout vocabulary belongs to the project.** Row types, row settings, spans and item
  types are the project's grid, so the recipe format leaves them open, and the project rules file
  and the builder's validator define them. The client project's grid is not shipped as if it were
  general.
- **Project rules live in a file the spell locates through `paths.md → ## Test content`**, declared
  identically by both packs' spells. The file is named by the slot rather than added as a fifth slot
  file, because it is QA's working document, not a configuration fact.
- **An `optimizely-12` pack, and no `optimizely-13` yet.** Per 0015 §3 a CMS whose majors break gets a
  pack per major. CMS 13 gets its own pack once a CMS 13 project exists to check it against, rather
  than a pack written from documentation alone.
- **Both spells are named `/test-content`.** Spell names carry no version (0015 §5), and a project
  runs one CMS. The install checker's pack-source list cannot name two packs for one unit, so
  `test-content` is left out of it and takes the pack-less reinstall hint.

## Alternatives considered

**The spell builds pages directly through the CMS's API, with no builder.** Simpler to adopt, but it
loses rebuilds on shared environments, the out-of-date check, hand-edit protection and the admin
screen, which are what make the pages trustworthy over time. On Optimizely it would also need an
API package many sites do not install.

**Ship the recipe spell alone.** It would do nothing until each project designed a builder unaided,
rediscovering the stored-value traps and the ordering rules the blueprint records.

**The general rules in each pack.** Duplicated method drifts. Two packs can't both own G1 to G12,
and 0015 §7 asks a pack to defer rather than duplicate.

**One versionless `optimizely` pack.** It contradicts 0015 §3 for a CMS, and CMS 13's differences
were unverified.

## Consequences

- A project adopting test content does real work first: a spec and plan for its builder. The README
  says so on both blueprint rows.
- Core gains a reference that only CMS-shaped projects use. Its description costs context in every
  install, accepted because the method also applies to component libraries outside a CMS.
- The Optimizely blueprint is checked against one real CMS 12 codebase's shape but not yet against a
  built builder. The first project to build one should feed corrections back.
- An `optimizely-13` pack, when it comes, copies the two units and checks each CMS 12 claim against 13.
