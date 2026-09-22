---
name: block
description: Create a new Umbraco block through a test-first workflow — derive names and properties, write a failing test for the element type, create it, register it in the right palette, author the view from an existing block, then build and confirm green. Use when adding a block or element type to an Umbraco project.
disable-model-invocation: true
argument-hint: "[Brief description of the block, its properties, and editor experience]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(git status:*), mcp__umbraco-mcp__*
---

The user wants to create a block: **$ARGUMENTS**

Artifact locations follow the layout in the `workflow` skill. This spell assumes nothing about where
the project keeps block views or how it binds their models — **those differ legitimately between
Umbraco projects**, and Step 5 discovers them rather than asserting them. Read
`umbraco-17-block-authoring` in full now. It is the reference that holds the discipline for one
block, every step below names a section of it, and you will not need to open it again. This spell
applies it to a block built from a bare description. A block built from a plan gets the same
discipline through the plan's steps.

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

Check every alias against *Alias hygiene is a set of facts, not a rule of this file* in the
block-authoring reference. That section states the prefix rule and cites the starter facts behind it.

State the names and properties clearly before proceeding.

## Step 2 — Write the test first (expect RED)

The test asserts that the element type exists with the expected property aliases. **It must fail now**
— the element type doesn't exist yet.

**Slot:** `.agents/config/stack.md` → `## Tests`
**If empty:** infer from existing test files. If the project has no tests yet, propose a location and
flag plainly that you are establishing a convention rather than following one — never settle it
silently.

Where this block is being built from a plan, that proposal and its flag belong in the plan's **Key
Decisions**, so the next block does not re-decide them. Built without one — this spell takes a bare
description, so that is a normal way to cast it — there is no Key Decisions section to write into,
and saying it in passing is how it gets lost: propose it for `.agents/config/stack.md` → `## Tests`
instead, so the second block inherits the answer rather than facing the same empty slot.

Write the test shown under *A block is proved to exist before it is built* in the block-authoring
reference. That section also cites the starter facts its assertions rest on. Run it and **confirm it
fails** before going on. A test that passes here is testing nothing.

**Slot:** `.agents/config/stack.md` → `## Build`
**If empty:** infer the build and test commands from the repo root and state which you used; if
genuinely ambiguous, ask rather than guessing.

## Step 3 — Create the element type

Use the MCP document-type tools, or the Management API, to create it with the name, alias,
`isElement: true`, and a property group containing the properties from Step 1. Never write the schema
file by hand. *Schema files are never hand-edited* in the block-authoring reference says why, for
Deploy and for uSync.

Verify it was created before moving on — a silent failure here makes Step 7 confusing.

## Step 4 — Register it in the right palette

A block that exists but is offered nowhere renders nowhere.

Find the block-editor data type the block belongs in, and add the new element type to its allowed
blocks. The block-authoring reference settles the rest under *Which palette a block joins is the
project's decision*: which palette is right, how to read the current palettes from committed files,
and when adding to one alone needs confirming. Follow that section, and name the palette you chose in
the report.

`/check-uda` reports palette drift, where installed, if you want to see the current state before
deciding.

## Step 5 — Author the view by copying the closest existing block

**Do not assume where views live or what they bind to.** Umbraco projects differ here, and the
reference names the common shapes without choosing between them. The project already chose.

**Slot:** `.agents/config/paths.md` → `## Umbraco`
**If empty:** locate each by search — the Deploy revision directory by its `*.uda` files, views by
their `*.cshtml` files, and the extension root by its `umbraco-package.json`. If no `*.uda` files
exist, check `uSync/*/ContentTypes/*.config` for the same schema before falling back to MCP; a folder
with no matching file is a partial export, not an empty schema.

If the project has no blocks yet, this spell stops to ask rather than picking a shape. The
greenfield sequence under *A new block copies the closest existing block* in the block-authoring
reference says what to ask. Otherwise follow that whole section: find the exemplar it describes,
check its accessibility shape as it says, carry over what it lists, and invent nothing beyond it.

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

All assertions must pass. If any fail, diagnose and fix the block before calling this done. What
done means, and what to do when an assertion disagrees with what was built, is settled by *A block
is done when its test passes* in the block-authoring reference.

## Step 8 — Report

```
Block: <Block Name> (<elementTypeAlias>)
Properties: <alias list>
Palette: <the data type it was registered in>
View: <path to the view created>
Tests: <RED confirmed, then GREEN>
Next: /feature <elementTypeAlias>   (draft its behavioral doc from the code)
```
