---
name: content-model
description: Umbraco 17 published-content and generated-model behaviors, property alias rules, and rendering traps that fail silently
metadata:
  type: reference
---

# Content model and rendering facts

## `level` is a reserved property alias, and unprefixed generics collide

`level` is used internally by the published content model. Unprefixed generic aliases — `content`,
`value`, `title` — collide in the same way.

**Why:** Reuse causes silent failures or unpredictable delivery behavior rather than a validation
error, so the property appears to save and then does not behave.

**How to apply:** Prefix element-type property aliases with the element name — `alertLevel`, not
`level`; `calloutContent`, not `content`. Flag any element-type property using a reserved or
unprefixed generic alias.
**Type:** pattern
**Applies:** umbraco >=17 <18
**Verified:** 17.3 (2026-07)

---

## The dropdown editor UI alias is `Umb.PropertyEditorUi.Dropdown` — `SelectBox` does not exist

The schema alias is `Umbraco.DropDown.Flexible`; the UI alias is `Umb.PropertyEditorUi.Dropdown`.

**Why:** `SelectBox` is a plausible-looking value that produces a property editor which silently
fails to render, rather than an error naming the unknown alias.

**How to apply:** Flag `"SelectBox"` anywhere — setup scripts, `.uda` files, migrations.
**Type:** pattern
**Applies:** umbraco >=17 <18
**Verified:** 17.3 (2026-07)

---

## Reading an undefined property returns empty, not an error

`Model.Value<string>("someAlias")` against an alias that does not exist on the type returns an empty
value rather than throwing.

**Why:** A typo'd alias therefore renders as blank content and looks like an editorial gap — "the
editor hasn't filled that in yet" — rather than a code defect. It can survive review indefinitely.

**How to apply:** When a template renders nothing where content is expected, verify the alias against
the type before assuming the content is missing. Flag alias strings that do not resolve against the
document type.
**Type:** pattern
**Applies:** umbraco >=17 <18
**Verified:** 17.3 (2026-07)

---

## A "Default On" toggle returns `false` when never set, indistinguishable from an explicit `false`

An `Umbraco.TrueFalse` property configured with *Default Value = On* returns `false` from the
generated model when it has never been saved. Using the generated property alone, "never set" and
"explicitly unchecked" are the same value.

**Why:** This breaks any inheritance chain. A page that should inherit an enabled default instead
reads as an explicit override to off — so the feature silently defaults to the wrong state on every
untouched page, which is most of them.

**How to apply:** Use `IPublishedContent.HasValue(alias)` to distinguish:
- `HasValue` false → never stored; treat as null and inherit.
- `HasValue` true → an editor saved it explicitly; use the boolean.

Pass `null`, not `false`, up a resolver chain when unset. Flag any inheritance logic reading the
generated boolean directly without a `HasValue` guard.
**Type:** pattern
**Applies:** umbraco >=17 <18
**Verified:** 17.3 (2026-07)

---

## Rich text needs an explicit `using` for its encoded-string type

`IHtmlEncodedString` is typically not imported by `_ViewImports.cshtml`.

**How to apply:** Add `@using Umbraco.Cms.Core.Strings` to any view rendering a rich-text property.
The failure is a build error that does not obviously point at a missing import.
**Type:** pattern
**Applies:** umbraco >=17 <18
**Verified:** 17.3 (2026-07)

---

## Rich-text editor images carry no width or height

Images inserted through the rich-text editor are emitted without intrinsic dimensions.

**Why:** That is a layout-shift source whose cause is the editor, not the template — so a reviewer
looking at the view finds nothing wrong with it.

**How to apply:** Note it as a known layout-shift gap attributable to the editor. Do not flag the
template as the defect; if it matters for a project, the fix is post-processing the editor's output,
not the view.
**Type:** false-positive-suppression
**Applies:** umbraco >=17 <18
**Verified:** 17.4 (2026-07)

---

## An element type is distinguished from a document type by `isElement: true`

**How to apply:** Assert it when creating or verifying an element type. A type created without it is
not offerable as a block, and the symptom is that the block never appears in a palette.
**Type:** pattern
**Applies:** umbraco >=17 <18
**Verified:** 17.3 (2026-07)

---

## Only a block editor's top-level `blocks[]` is palette membership

A block-editor data type's `Configuration.blocks[]` is the palette. Nested
`areas[].specifiedAllowance[]` entries are area-scoped allowances, not palette offerings.

**How to apply:** When computing what a palette offers, read only `blocks[]`. Counting allowances
inflates membership and produces false drift findings.
**Type:** pattern
**Applies:** umbraco >=17 <18
**Verified:** 17.4 (2026-07)

---

## Generated models are not the place for hand edits

Generated model files are output. Where a project commits them, they are still regenerated rather
than edited.

**How to apply:** Flag any hand edit to a generated model file. The change will be silently lost at
the next regeneration, which may be much later and by someone else.
**Type:** pattern
**Applies:** umbraco >=17 <18
**Verified:** 17.3 (2026-07)
