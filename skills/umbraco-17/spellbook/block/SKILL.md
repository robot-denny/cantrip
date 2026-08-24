---
name: block
description: Create a new Umbraco block through a test-first workflow — derive names and properties, write a failing test asserting the element type and its aliases, create the element type, register it in the right palette, author the view by copying the closest existing block, then build and confirm green. Use when adding a block or element type to an Umbraco project.
disable-model-invocation: true
argument-hint: "[Brief description of the block, its properties, and editor experience]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(git status:*), mcp__umbraco-mcp__*
---

The user wants to create a block: **$ARGUMENTS**

Artifact locations follow the layout in the `workflow` skill. This spell assumes nothing about where
the project keeps block views or how it binds their models — **those differ legitimately between
Umbraco projects**, and Step 5 discovers them rather than asserting them.

## Step 1 — Derive names and properties

From the description, determine:

- **Block name** — the display name, in Title Case
- **Element type alias** — camelCase
- **Properties** — each with its name, alias, and property editor

Common property editors:

| Purpose | Editor alias |
|---|---|
| Rich text | `Umbraco.RichText` |
| Plain text | `Umbraco.TextBox` / `Umbraco.TextArea` |
| Dropdown | `Umbraco.DropDown.Flexible` (schema alias); UI alias is `Umb.PropertyEditorUi.Dropdown` |
| Media | `Umbraco.MediaPicker3` |
| Toggle | `Umbraco.TrueFalse` |
| Nested blocks | `Umbraco.BlockList` / `Umbraco.BlockGrid` |

**Alias hygiene, which is easy to get wrong and fails silently:**

- **`level` is reserved** by the published content model. Reusing it causes silent failures.
- **Unprefixed generics collide** — `content`, `value`, `title`. Prefix with the element name instead:
  `alertContent`, not `content`.
- The **dropdown UI alias is `Umb.PropertyEditorUi.Dropdown`.** `SelectBox` does not exist, and using
  it produces a property editor that silently doesn't render.

State the names and properties clearly before proceeding.

## Step 2 — Write the test first (expect RED)

The test asserts that the element type exists with the expected property aliases. **It must fail now**
— the element type doesn't exist yet.

**Slot:** `.agents/config/stack.md` → `## Tests`
**If empty:** infer from existing test files; if the project has no tests yet, propose a location in
Key Decisions and flag it as a new convention being established.

Three Umbraco-specific facts the assertions depend on:

- **`getByName()` returns `false`, not `null`,** when an entity isn't found. Assert with
  `.toBeTruthy()` / `.toBeFalsy()` — never `.toBeNull()`, which passes on a missing entity and makes
  the test useless.
- **Properties come back as a flat array.** Use `elementType.properties ?? []`, not
  `groups?.flatMap(...)`.
- **`isElement: true`** is what distinguishes an element type from a document type.

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

Run it and **confirm it fails** before going on. A test that passes here is testing nothing.

**Slot:** `.agents/config/stack.md` → `## Build`
**If empty:** infer the build and test commands from the repo root and state which you used; if
genuinely ambiguous, ask rather than guessing.

## Step 3 — Create the element type

Use the MCP document-type tools, or the Management API, to create it with the name, alias,
`isElement: true`, and a property group containing the properties from Step 1.

Verify it was created before moving on — a silent failure here makes Step 7 confusing.

## Step 4 — Register it in the right palette

A block that exists but is offered nowhere renders nowhere.

Find the block-editor data type the block belongs in, and add the new element type to its allowed
blocks. **Which palette is the right one is a project decision, not a technical one** — a project may
have several, some scoped to a single parent block. Identify the candidates by looking for data types
whose `Configuration` has a `blocks[]` array, then pick based on where the block is meant to appear.

If the project maintains parity between palettes, adding to only one is a deliberate choice worth
confirming with the user. `/check-uda` reports palette drift, where installed, if you want to see the
current state before deciding.

**Without that spell**, read the current state directly — it is all local. Where the project uses
Deploy, each block-editor data type's `Configuration.blocks[]` *is* its palette, listing element types
by key; resolve each key against the `Udi` in the `document-type__*.uda` files to read them as aliases.
Where there are no `*.uda` files the project is not using Deploy — read the same data types from
`uSync/*/DataTypes/*.config`, whose `<Config>` payload carries the same block list, and go to the
running instance via MCP only when no config file matches this data type. A `DataTypes/` folder with
no match for it is a partial export, not an empty block list — say so rather than reporting no
palette. Either way, compare only palettes that already share a block — a palette offering just one
block is normally scoped to a single parent, so measuring it against a page-body palette reports
noise rather than drift.

## Step 5 — Author the view by copying the closest existing block

**Do not assume where views live or what they bind to.** Umbraco projects differ here, and both of
these are common and valid:

- a flat, editor-agnostic folder with one view per block alias, bound to
  `IBlockReference<IPublishedElement, IPublishedElement>` so the same view renders under both a list
  and a grid editor
- a per-block folder inside a Razor class library, bound to the generated typed model

**Slot:** `.agents/config/paths.md` → `## Umbraco`
**If empty:** locate each by search — the Deploy revision directory by its `*.uda` files, views by
their `*.cshtml` files, and the extension root by its `umbraco-package.json`. If no `*.uda` files
exist, check `uSync/*/ContentTypes/*.config` for the same schema before falling back to MCP; a folder
with no matching file is a partial export, not an empty schema.

**If the project has no blocks yet** — a greenfield build — there is nothing to copy, and inventing a
convention here would set one by accident that every later block inherits. Instead, in order:

1. **Ask whether another codebase should be the reference.** A sibling project or a starter the team
   already trusts is a far better source than invention. If one is named, read it and say which
   conventions you took from it, so they are adopted deliberately rather than absorbed.
2. **Otherwise establish the convention explicitly and minimally**, and say plainly that you are
   establishing rather than following it — which view location, which model binding, which settings
   shape, and why. Record it in the increment's Key Decisions and propose it for
   `.agents/config/paths.md`, so the *second* block has an exemplar and this ambiguity happens once.

Do not quietly pick a shape. **The first block in a project defines its conventions whether or not
anyone decided to.**

Otherwise: **find the closest existing block and follow it exactly.** Copy its view-model directive, its
naming, its folder placement, its settings handling, and its styling approach. The existing blocks are
the specification; this spell is not.

What to carry over from the exemplar rather than invent:

- The **model or inherits directive**, verbatim in shape
- **Settings handling** — many projects give blocks a settings model with a hide or spacing property
- The **styling convention** — which framework or token system the project uses
- The **filename convention** — usually matching the element type alias

One Umbraco gotcha that is not project-specific: for rich text properties, add
`@using Umbraco.Cms.Core.Strings`. `IHtmlEncodedString` is typically not in `_ViewImports.cshtml`, and
the failure is a build error that doesn't obviously point at the missing using.

## Step 6 — Build

Run the project's build. Fix any errors before proceeding.

If views compile at build time, this is where a misplaced view directory surfaces — some projects ship
views as embedded resources and require new directories to match a glob, or the view goes missing in
release builds while working locally.

**Slot:** `.agents/config/conventions.md` → `## Planning gotchas`
**If empty:** skip this check — do not invent constraints. If the codebase makes a non-obvious
structural requirement evident (a directory that must match a build glob, a registry a new file must
be added to), note it in Key Decisions and suggest recording it in the slot.

Scope: **constraints a plan must satisfy** — a directory that must match a build glob, a verification
step only a particular command surfaces, a package-version rule a validator enforces. **Not operational
topology** — which environment deploys where, how promotion works, who restarts what. That is runbook
material for `docs/`, and folding it in here turns one slot into a catch-all a planner reads past.

## Step 7 — Run the test again (expect GREEN)

All assertions must pass. If any fail, diagnose and fix before calling this done — do not adjust the
test to match what was built.

## Step 8 — Report

```
Block: <Block Name> (<elementTypeAlias>)
Properties: <alias list>
Palette: <the data type it was registered in>
View: <path to the view created>
Tests: <RED confirmed, then GREEN>
Next: /feature <elementTypeAlias>   (draft its behavioral doc from the code)
```

## Conventions

- Property aliases are camelCase, prefixed to avoid reserved and generic collisions
- **Never hand-edit `.uda` files** — they are managed by Deploy and regenerate on startup
- Follow the settings, spacing, and styling conventions of the exemplar block, not a default of your
  own
- A block is not done when it compiles; it is done when the test that failed in Step 2 passes
