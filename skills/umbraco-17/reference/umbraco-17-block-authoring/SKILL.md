---
name: umbraco-17-block-authoring
description: The discipline one Umbraco 17 block is built under, whether it arrives as a planned step or a standalone cast — the test that proves an element type exists before anything is created, the rule to copy the closest existing block and what to do when a project has none, palette choice as the project's decision, schema files that are never hand-edited, and the definition of done. Consult when planning, implementing, or reviewing work that adds a block or element type to an Umbraco 17 project, when writing a step that creates an element type or authors a block view, or when deciding whether a block is finished.
---

# Block authoring: the discipline one block is built under

A block in Umbraco 17 is an element type, the view that renders it, and the palette that offers it.
This file holds the rules that make one block right, so a block planned by `/plan` and built by
`/implement-step` gets the same discipline a block cast through `/block` gets. Both cite this file
rather than carrying a copy of it.

## What this reference is, and what it is not

Discipline for one block, whether planned or cast. The platform facts it rests on live in
`umbraco-17-starter-facts`, in its Management API and content-model topic files
(`references/management-api.md` and `references/content-model.md`). This file cites those facts by
heading and restates none of them, because a fact copied here would stop agreeing with its source
the day the source is re-verified. Procedure lives elsewhere too: in a plan's steps for a block that
came through a spec, or in `/block` for a block built from a bare description.

## A block is proved to exist before it is built

The test asserts three things through the Management API. The element type is present. It is an
element. Each expected property alias is on it. Run the test to RED before creating anything; a test
that passes first is testing nothing, because the type it names does not exist yet.

```typescript
import { expect } from '@playwright/test';
import { test } from '@umbraco/playwright-testhelpers';

const elementTypeName = '<Block Name>';
const expectedAliases = ['<alias1>', '<alias2>'];

test('<Block Name> element type exists with correct properties', async ({ umbracoApi }) => {
  const elementType = await umbracoApi.documentType.getByName(elementTypeName);

  // getByName returns false (not null) when not found
  expect(elementType).toBeTruthy();
  expect(elementType.isElement).toBe(true);

  // Umbraco 17 returns a flat properties array, not nested in groups
  const aliases = (elementType.properties ?? []).map((p: any) => p.alias);
  for (const alias of expectedAliases) {
    expect(aliases).toContain(alias);
  }
});
```

Three lines of that sample rest on facts recorded in `umbraco-17-starter-facts`. Each is cited here
and argued there:

- Presence is asserted with truthiness, never with `.toBeNull()`, because of what `getByName()`
  returns on a miss. See *`getByName()` returns `false`, not `null`, when nothing matches* in
  `references/management-api.md`.
- Properties are read as a flat array directly off the type. See *Document-type properties come back
  as a flat array, not nested in groups* in the same file.
- `isElement: true` is what makes the type offerable as a block. See *An element type is
  distinguished from a document type by `isElement: true`* in `references/content-model.md`.

Where the test file lives is a project fact. A plan carries it in Key Decisions. A project with no
tests yet needs a location proposed and flagged as a convention being established, never settled
in passing.

## A new block copies the closest existing block

The existing blocks are the specification, and this file is not. If the project has no blocks yet,
read the greenfield sequence at the end of this section before doing anything else. Otherwise find
the closest existing block and carry these over from it rather than inventing them:

- the **model or inherits directive**, verbatim in shape
- **settings handling**, since many projects give blocks a settings model with a hide or spacing property
- the **styling convention**, whichever framework or token system the project uses
- the **filename convention**, usually matching the element type alias

If the block has a rich-text property, its view needs a `using` that the exemplar may not carry. See
*Rich text needs an explicit `using` for its encoded-string type* in `references/content-model.md`.

Look at the exemplar's accessibility shape before carrying it over, because it copies too. Alt text
on a media property, a real heading element rather than a styled `div`, a control that works from
the keyboard. A defect in any of these reproduces into every block copied from the exemplar. If the
exemplar looks suspect, say so plainly rather than copying it quietly. What a reviewer checks for is
stated in `umbraco-17-review-rules`, under *Accessibility*.

Two shapes are common and both are valid. One is a flat, editor-agnostic folder with one view per
block alias, bound to `IBlockReference<IPublishedElement, IPublishedElement>` so one view renders
under a list and a grid editor alike. The other is a per-block folder inside a Razor class library,
bound to the generated typed model. This file gives no verdict between them. The project already did.

Where views live is found in the plan's Key Decisions first. Failing that, the project's paths slot
(`.agents/config/paths.md` → `## Umbraco`, declared in `umbraco-17-planning`) names it. When neither
has it, the sequence below applies.

**When the project has no blocks, there is nothing to copy, and inventing a shape sets a convention
by accident.** In order:

1. Ask whether another codebase is the reference. A sibling project or a starter the team already
   trusts is a better source than invention. If one is named, read it and say which conventions were
   taken from it, so they are adopted deliberately.
2. Otherwise establish the convention explicitly and minimally, and say plainly that it is being
   established rather than followed: which view location, which model binding, which settings shape,
   and why. Record it in Key Decisions and propose it for the paths slot, so the second block has an
   exemplar and this ambiguity happens once.

Do not quietly pick a shape. The first block in a project defines its conventions whether or not
anyone decided to.

## Which palette a block joins is the project's decision

A block that exists but is offered nowhere renders nowhere. Which palette is the right one is a
project decision, not a technical one: a project may have several, some scoped to a single parent
block. Identify the candidates as the data types whose configuration has a top-level `blocks[]`, and
pick by where the block is meant to appear. If the project keeps parity between its palettes, adding
to only one is a deliberate choice. Confirm it before making it.

Compare only palettes that already share a block. A palette offering one block is normally scoped to
a single parent, and measuring it against a page-body palette reports noise rather than drift.

What counts as membership is a starter fact: *Only a block editor's top-level `blocks[]` is palette
membership* in `references/content-model.md`. For the current state, `/check-uda` reports palette
drift where the Deploy pack is installed. Without it, read the committed schema files first. Under
Deploy, each block-editor data type's `Configuration.blocks[]` lists element types by key. Resolve
each key against the `Udi` in the `document-type__*.uda` files to read them as aliases. Under uSync,
the same block list sits in the `<Config>` payload of `uSync/*/DataTypes/*.config`. Go to the running
instance only when no file matches the data type. A `DataTypes/` folder with no match for it is a
partial export, not an empty palette, so say so rather than reporting no palette.

## Schema files are never hand-edited

Never hand-edit `.uda` files under Deploy or `.config` files under uSync. Author the change through
the backoffice or the Management API and let the tooling write the file. The two formats fail in
opposite directions, and both fail silently. Deploy exports `.uda` from what the backoffice holds, so
a hand edit is lost on the next export and nothing reports it. uSync imports `.config` into the
backoffice, so a hand edit is not lost: it is applied to the live content model on the next import,
which is the worse outcome. The same rule covers generated model files; see *Generated models are
not the place for hand edits* in `references/content-model.md`.

## A block is done when its test passes

A block is done when the test that went red passes. It is not done when it compiles, and it is not
done when the view renders in one place. If an assertion fails, diagnose and fix the block. Do not
adjust the test to match what was built; the test was written first so that it could disagree. The
test proves the schema. The view's markup is proved at review, against `umbraco-17-review-rules`.

## Alias hygiene is a set of facts, not a rule of this file

The one rule that is discipline: prefix every property alias with the element name, so `alertContent`
rather than `content`. Why that matters is three starter facts in `references/content-model.md`, cited
rather than repeated. Two sit under *`level` is a reserved property alias, and unprefixed generics
collide*. The third is *The dropdown editor UI alias is `Umb.PropertyEditorUi.Dropdown`*. Each
describes a failure that raises no error, which is why the prefix is a rule and not a preference.

## How a plan uses this

A block is planned as ordinary steps, never as a step that casts `/block`. The planning reference,
`umbraco-17-planning`, says why. Each step that writes the test, creates the element type, registers
the palette entry, or authors the view names this reference in its prompt. That is the mechanism the
worker envelope already uses for `tdd-principles`.

The worker records two things in its report. Which existing block it copied, so a reviewer can check
the copy against its source. And which palette it chose, so the choice is visible as a decision
rather than buried in a data type's configuration.
