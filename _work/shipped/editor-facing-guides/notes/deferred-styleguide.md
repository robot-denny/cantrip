# Deferred: the styleguide increment

_Captured 2026-08-25, when the editor-facing-guides increment was cut to stories 2–4. **Not a spec**
— carry-forward material so the styleguide's own spec starts from the decisions already made rather
than re-deriving them._

The styleguide was story 1 of four in `../discovery.md`. It is deferred as a **separate increment
with its own spec**, to be built directly after this one. This file holds what was already settled
about it, plus the scenarios drafted before the cut.

## Why it was the cut line

Discovery's sequencing note named it, and nothing since has argued against it: **stories 2–4 share
one dossier and one audit; story 1 shares only the guide-page scaffolding.** It is the only story
requiring new element types, new views, and a pre-existing design system.

Note the correction in `spec-revisions.md` §7, which still applies: discovery's cost gradient
claimed only the styleguide needs an established design system, and that was too clean. Every *page*
type needs a template, and a template is markup — so the guide page and the index need exemplars
too. The real line is **copying a structure that already exists** (cheap; any project with pages
demonstrates a rich-text body and a block area) versus **inventing rendering that exists nowhere**
(the token-reading swatch blocks, which have no analogue in a typical project). The styleguide is
the only story on the expensive side of that line, which is what makes it separable.

## Decisions already made

- **It is a spell, not a reference.** No case against it survived review: `/block` is already a
  noun-named spell in the same pack, so a second one does not strain the verbs-are-spells
  convention; contract check 16's ten-spell ceiling governs the core spellbook and pack spell counts
  are ungated ([ROADMAP.md](../../../ROADMAP.md), "Pack spell counts are ungated"), so the count is
  not a constraint; and its job is an action with a precondition, which is spell-shaped. Revisit
  only if the ungated-pack question closes by extending the ceiling to packs.
- **It states its precondition rather than assuming it.** An established design system is required,
  and the spell says so instead of producing plausible output from nothing.
- **It delegates view authoring to the existing block workflow** rather than shipping markup, on the
  same reasoning as the rest of the capability.
- **It scaffolds three things**: the element types that showcase design tokens, the page itself, and
  — shared with this increment — the guide page type. The shared half is the reason the scaffolding
  reference is worth citing from two places rather than duplicating.
- **Greenfield refusal is at its most intense here.** With no components to read from, the work
  stops. The specific hazard discovery named: a styleguide scaffolded at project setup makes a
  color-swatch view the exemplar every real block is later copied from.

## Scenarios drafted before the cut

Verbatim, so they are not re-derived. They were removed from the spec and the feature doc because
neither should assert behavior this increment does not deliver.

```scenario
Scenario: A designer changes a brand color and the styleguide follows
  Given a styleguide page is published with a color palette section
  And the project's primary brand color is defined in the codebase as a design token
  When a designer changes that token's value and the site is deployed
  Then the styleguide's palette section shows the new color on the next page load
  And no guide regeneration was run
```

```scenario
Scenario: Standing up a styleguide on a project that has components to copy from
  Given a project has twelve existing blocks and a design token system
  When a team member asks for a styleguide to be created
  Then a styleguide page is published with sections for colors, type scale, and common elements
  And each showcase section's markup follows the conventions of the existing blocks
```

```scenario
Scenario: A greenfield project stops rather than inventing conventions
  Given a project has no blocks yet
  When a team member asks for a styleguide to be created
  Then the work stops and reports that there is no existing component to take conventions from
  And no showcase block is created
```

The acceptance criterion they proved, also verbatim:

> A team member can generate a styleguide page whose showcase sections read the project's design
> tokens live, so it reflects current styles without regeneration.

## What this increment leaves it

- The guide page type, its container types, and the derived index — all scaffolded and in use, so
  the styleguide inherits a working section rather than standing one up.
- The shared scaffolding reference, whose second caller this was always meant to be.
- Content ownership by provenance, which the styleguide page will need unchanged.
