# Validation log: test-content dry run

**Date:** 2026-11-23
**Subject:** the `umbraco-17` `/test-content` spell, followed step by step by hand against the
`alertBanner` block in the demo project. The spell is user-cast, and the demo project is a read-only
source, so nothing was written there. The recipe the run produced is
[notes/dry-run-alertBanner.recipe.json](notes/dry-run-alertBanner.recipe.json).

**What this proves:** the method in `test-content-principles` and the spell's steps produce a
coherent recipe for a real Umbraco 17 block. **What it does not prove:** that any builder builds
the recipe, since the demo project has none. Step 6 could not run as written.

## Step by step

| Step | Result |
|---|---|
| 0. Find recipes, rules, builder | The slot is empty, there is no `Recipes` folder, and there is no builder, so the spell **stops here as written**. That is the right behavior. The run went on past it deliberately, using the core template as the rules file. |
| 1. Read the component | **Failed on the primary path.** See finding 1. The schema was read directly from the Deploy files instead: `alertLevel` is a required `Umbraco.DropDown.Flexible` with options `emergency`, `warning`, `informational` and no configured default; `alertContent` is an optional `Umbraco.RichText`. The view maps each level to a color class, and **renders nothing when `alertContent` is empty**. |
| 2. Find old test content | No running site and no `umbraco-mcp`, so per the spell: empty `legacy`. |
| 3. Plan | 9 rows, 10 items: 1 common setup (2 stacked alerts) and 8 variation rows. The variation rows are the baseline, the 2 other levels, no content, the rich-text sample on each of the 3 levels, and content stress. There is no layout section (finding 3). As first written it had 7 rows, with the 3 rich-text alerts stacked in one; see *Review corrections*. |
| 4. Gray areas | 4 arose, each recorded in the recipe's `decisions` as a dry-run assumption rather than asked: the baseline level for a required dropdown with no default, whether empty content is layout or stress, the common setup, and whether a layout section is wanted. |
| 5. Write | Written in the core format, with no raw ids. |
| 6. Check | No builder validator exists. An ad-hoc structural check stood in for it: unique ids, values only for expected properties, options as spelled, one token per object, no raw ids, and no description without a label. **No problems.** The check was then proved by planting a duplicate id, an option not in the schema, and an object with two tokens; it reported all three, each at its path. |
| 7. Report | This log. |

Commands, from the cantrip root:

```
python3 skills/umbraco-17/spellbook/guide/scripts/guide.py extract alertBanner --project-root <demo project>
# stderr: guide.py: note: 103 Deploy artifacts were not read — their __version is not a
#         serialization shape this toolkit has been verified against: ... declares __version 17.0.1
# stdout: empty, exit 0

python3 skills/umbraco-17/spellbook/guide/scripts/guide.py extract alertBanner --project-root <demo project> --adapter models
# guide.py: error: no generated model class under <demo project> declares the alias 'alertBanner'.
```

## Findings

1. **Step 1's primary path returns nothing on a current Umbraco 17 project.** Every one of the demo
   project's 103 Deploy files declares `__version 17.0.1`, which the `/guide` script has not been
   verified against, so `extract` skips them all and prints nothing with exit code 0. The spell
   names `umbraco-mcp` as the fallback but not what to do when that is absent too. **Proposed:** say
   that an empty extract is a failure, not an empty component, and fall back to reading the
   serialized schema files directly. Separately, the script's accepted-version list is behind a
   current Umbraco 17; that belongs to `/guide`, outside this increment.
2. **The "no builder" stop works**, and is the first thing a project without one will see.
3. **The rules template assumes a 12-column grid.** The demo project's page body is a single-column
   Block List with no widths and no row backgrounds, so P3 to P5 have nothing to vary, and `span` is
   meaningless. **Proposed:** the core reference says that where the body has no widths, every item
   spans 12 and the recipe has no layout section; the template marks P3 to P5 "delete if your page
   body has no widths".
4. **A required dropdown with no default leaves G1 open.** G1 says each dropdown sits "at its default
   option", and this one has none. **Proposed:** add it to the typical gray areas, proposing the
   option the view falls back to, or the first option when there is none.
5. **A color option is not always called one.** The alert level is this block's only color option,
   since the view maps each level to a color class, but nothing in its name says so. G10 and G11 only
   held because the view was read. **Proposed:** G11 says to recognize a color option by what the
   view does with it, not by its name.
6. **G2 classified "content empty hides the block" correctly** as a layout variation rather than
   stress, and the rule's description guidance fit it, so the row gets "Nothing should render below
   this heading". The row as first written was still wrong: it used the `warning` level where the
   baseline uses `informational`, so it differed from the baseline in two settings, not one. Neither
   the run nor its ad-hoc check caught that; review did.

## Corrections applied

Findings 1, 3, 4 and 5 were applied on 2026-11-23, after the run:

- **1.** The `umbraco-17` spell's Step 1 now treats an empty extract as a failure, reads stderr, and
  falls back to `umbraco-mcp`, then to the serialized schema files directly (for Deploy, the
  document-type and data-type files the run itself used). The report says which way the schema
  was read. The script's version list is left to `/guide`.
- **3.** `test-content-principles` says what a recipe does when the page body has no widths: every
  item spans 12, and there is no `layout` section unless rows have settings worth varying. The rules
  template tells a single-column site to delete P3 and P4.
- **4.** G1 names a required dropdown with no default as a gray area, with a proposed answer, and the
  typical gray areas list it.
- **5.** G11 says to recognize a color option by what the view does with it, not by its name.

The dry-run recipe already follows all four, since the run worked around each by hand. It was not
re-run.

## Review corrections

Review on 2026-11-24 found two faults in the recipe itself, both fixed in the file:

- The "No Content" row used `warning`; it now uses the baseline's `informational`, so it differs from
  the baseline only in leaving the content empty.
- The 3 rich-text alerts sat stacked in one row, against the rule that a single-column page holds
  one component per row unless the row tests components side by side. They are now 3 rows, one per
  level.

The stress text also gained a long web address, which the rules template's P9 now asks for. The
ad-hoc check was not re-run against the corrected file; a script check confirmed the ids are still
unique.
