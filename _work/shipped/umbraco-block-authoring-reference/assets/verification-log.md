# Step 5 — verification log

Working tree: branch `robot-denny/umbraco-block-authoring-reference`, HEAD `dbfd8c7`, clean. Baseline
gate: `bash scripts/check-contract.sh` reports 22 checks passed. Steps 1 to 4 are committed, each
with the fixes from its code review. "The demo project" below is the sibling Umbraco 17 demo site
the toolkit is dogfooded against; its path is machine-specific and is not recorded here.

Four checks follow. Predictions for each are written here before any of them runs. A prediction
that fails is recorded as a failure with what it means for the increment, not rewritten.

Three facts from the earlier steps are recorded first, because they change what two of the checks
are allowed to expect:

- **The single-holder grep lists citers as well as the holder.** The plan's Key Decision reads
  "each appears in exactly one shipped file." That was too strong for one phrase. "Closest existing
  block" is the Step 5 heading of `/block`, kept verbatim because `/styleguide` names it; it is a
  citation by heading in the same step; it is a handoff line in `/styleguide` Step 6; and it is a
  routing sentence in `umbraco-17-planning`. None of those states the rule. The rule lives once, in
  the reference. The check below expects the reference as the holder and those three files as
  citers, and would fail if the spell's body stated the rule rather than cited it.
- **The plan's Step 4 validation `grep -c 'cannot see' ROADMAP.md → 0` was wrong.** An unrelated
  entry in the roadmap's Later section uses the phrase. The removed entry's own phrase, "holds
  discipline that", is what proves removal, and the Step 4 worker used it.
- **Contract check 10's absence pattern is literal.** It accepts "the project has no", "if no",
  "when none", "has no ", "nothing analogous", and "not yet established". It does not accept "when a
  project has none". The Step 2 worker met this and reworded; the Step 3 envelope carried it.

## Predictions, written before any check ran

### Check 1 — the worker probe

A fresh general-purpose worker receives a synthetic plan step for a "Testimonial" block (a rich-text
quote and a text author name) whose prompt names `umbraco-17-block-authoring`, in the shape
`umbraco-17-planning` now prescribes. It is told not to edit files and to report the test it would
write and the questions it would ask.

Predicted: the worker loads the reference by name. Its test asserts presence with `toBeTruthy()`,
asserts `isElement` is true, and reads `properties ?? []` as a flat array; it does not use
`toBeNull()` or `groups.flatMap`. It says it would run the test to RED before creating the type. It
asks which existing block to copy, or says it would look for the closest one, and names what it
would carry over. It names candidate palettes and asks before adding to only one. It mentions the
rich-text `using`, because the block has a rich-text property and the reference now points at that
fact. It says it would check the exemplar's accessibility shape. A worker that asserts `toBeNull()`
or reads `groups.flatMap` is a FAIL and means the reference is not reached or not followed.

### Check 2 — structural walk for AC7 and AC8

Predicted: `/block` has eight `## Step` headings; Step 5's heading is "Author the view by copying
the closest existing block"; its report block ends `Next: /feature <elementTypeAlias>`; the spell
names `umbraco-17-block-authoring` once, in its opening paragraph, and every later step says "the
block-authoring reference". `/styleguide` is byte-identical to main, its Step 9 still says views are
`/block`'s work at Step 5, and its report's `Next:` line still says "author its view — the element
type and its palette already exist".

### Check 3 — single holder and core untouched

Predicted: the single-holder grep lists five files: the reference, `/block`, `/styleguide`,
`umbraco-17-planning`, and the starter facts' Management API file. Per the note above, the reference
is the holder, the starter facts hold the two facts, and the other three are citers. In `/block` the
only "closest existing block" hits are the Step 5 heading and its citation by heading.
`git diff --stat main -- skills/core` prints nothing.

### Check 4 — live cast on the demo project

Predicted: not run. The demo project's install predates `/block` and has no `umbraco-17-block-authoring`.
Recorded as not run with the reason, so AC7 rests on the structural walk in Check 2 and on the probe
in Check 1.

## Results

### Check 1 — the worker probe: PASS on content, PASS on load after a fixture

**Run 1: the synthetic step, as dispatched.** A general-purpose worker received a Step 2 prompt for
the "Testimonial" block in the shape `umbraco-17-planning` prescribes, with Key Decisions naming the
reference, the test location, an empty paths slot, and two palettes ("Page Body", "Landing
Sections") sharing six blocks. Dry run: no files, no commands.

The worker reported that `umbraco-17-block-authoring` **could not be loaded by name**: the Skill
tool returned `Unknown skill`. This repository links only core skills into `.claude/skills/`, so no
`umbraco-17` unit is available by name here. The worker read the file from disk instead and followed
it, and the two starter-facts files it cites. That is a FAIL of the prediction "loads the reference
by name" as stated, and the cause is the fixture, not the mechanism: a consuming project that
installed the pack has the unit by name, and this repository does not. Run 2 below closes the gap.

Every content prediction held. The test the worker would write, verbatim in its report:

```typescript
import { expect } from '@playwright/test';
import { test } from '@umbraco/playwright-testhelpers';

const elementTypeName = 'Testimonial';
const expectedAliases = ['testimonialQuote', 'testimonialAuthor'];

test('Testimonial element type exists with correct properties', async ({ umbracoApi }) => {
  const elementType = await umbracoApi.documentType.getByName(elementTypeName);
  expect(elementType).toBeTruthy();
  expect(elementType.isElement).toBe(true);
  const aliases = (elementType.properties ?? []).map((p: any) => p.alias);
  for (const alias of expectedAliases) {
    expect(aliases).toContain(alias);
  }
});
```

Truthiness for presence, `isElement` asserted, properties read as a flat array. No `toBeNull()`, no
`groups.flatMap`. It said it would capture the RED output before Step 3 creates anything, and that a
test passing first means a type already exists and Step 3 must be re-planned.

Before Step 3 it said it would: find the closest existing block by search because the paths slot is
empty, and record its name in the report; carry over the model directive, settings handling, styling
convention, and filename convention verbatim in shape without choosing between the two common
bindings; add the rich-text `using` because the quote is rich text and the exemplar may not carry it;
check the exemplar's accessibility shape, naming `<blockquote>` and `<cite>` over styled `div`s;
name both palettes, note that six shared blocks means parity, and record the choice as an open
decision for Key Decisions rather than pick, since a dispatched worker cannot ask; read membership
from the committed `.uda` files by resolving keys against Udis, comparing only palettes that already
share a block; record the found view location and propose it for the paths slot; create the type
through the Management API and never edit `.uda` by hand; and confirm both aliases carry the
element-name prefix. It also raised the `recurseChildren` short-circuit starter fact as the first
thing to check if the test stays RED after Step 3.

Every one of those is a sentence of the reference, followed. The worker also flagged, correctly,
that the presence assertion is fragile by `tdd-principles`' standard and kept it because the plan's
Test-first block fixes what the test asserts and the Management API is the observable interface for
schema.

**Run 2: the by-name load, with a fixture.** The envelope allows a fixture that does not exist to be
created, captured, and removed. A symlink `.claude/skills/umbraco-17-block-authoring ->
../../skills/umbraco-17/reference/umbraco-17-block-authoring` was created, a fresh worker was asked to
list matching skills, invoke the unit by name, and answer one question from what it loaded without
opening any file, and the symlink was removed afterwards.

```
- Matching skill names: umbraco-17-block-authoring
- umbraco-17-block-authoring: succeeded; first H1: "# Block authoring: the discipline one block is
  built under"; palette section heading: "## Which palette a block joins is the project's decision";
  exemplar section heading: "## A new block copies the closest existing block"
- Parity sentence: "If the project keeps parity between its palettes, adding to only one is a
  deliberate choice. Confirm it before making it."
- Files touched: none
```

The unit loads by name when installed, its sections resolve by their real headings, and a worker
can answer from it without touching the filesystem. With the earlier probe that loaded two core
references inside a dispatched worker before the spec was written, the mechanism is confirmed for a
pack unit as well as for core.

**What this means for the increment.** AC1 and AC2 rest on the reference being reachable and
followed. Both are shown: reachable by name where installed (Run 2), and followed to the letter when
read (Run 1). The one honest gap is that Run 1's worker fell back to reading from disk, which a
consuming-project worker would not need to do and could not do if the pack were absent. The
"where installed" condition is already the pack's precedent.

### Check 2 — structural walk for AC7 and AC8: PASS

```
$ grep -c '^## Step' skills/umbraco-17/spellbook/block/SKILL.md
8
$ grep -n '^## Step 5' skills/umbraco-17/spellbook/block/SKILL.md
89:## Step 5 — Author the view by copying the closest existing block
$ grep -n '^Next: ' skills/umbraco-17/spellbook/block/SKILL.md
137:Next: /feature <elementTypeAlias>   (draft its behavioral doc from the code)
$ grep -n 'umbraco-17-block-authoring' skills/umbraco-17/spellbook/block/SKILL.md | cut -d: -f1
14
$ grep -c 'block-authoring reference' skills/umbraco-17/spellbook/block/SKILL.md
4
$ git diff --stat main -- skills/umbraco-17/spellbook/styleguide
(empty)
$ grep -n "at its Step 5\|Next: /block" skills/umbraco-17/spellbook/styleguide/SKILL.md
375:So authoring those views is `/block`'s work, at its Step 5 — and **this spell suggests that cast
403:Next: /block <the swatch showcase element>   (author its view — the element type and its palette already exist)
```

Every prediction held. The unit is named once, on line 14 in the opening paragraph, and the four
later citations say "the block-authoring reference". AC8 rests on the styleguide being byte-identical to main and its two handoff
lines still describing what the thinned Step 5 does. AC7 rests on the eight steps, the unchanged
report, and the unchanged `Next:` line; the live cast that would prove it end to end is Check 4.

### Check 3 — single holder and core untouched: PASS

```
$ grep -rniE 'toBeNull|flat (properties )?array|closest existing block|first block in a project defines|project decision, not a technical one|hand-edit(ing)? `?\.uda|done when the test' skills/umbraco-17 --include=SKILL.md --include='*.md' -l
skills/umbraco-17/spellbook/styleguide/SKILL.md
skills/umbraco-17/spellbook/block/SKILL.md
skills/umbraco-17/reference/umbraco-17-planning/SKILL.md
skills/umbraco-17/reference/umbraco-17-block-authoring/SKILL.md
skills/umbraco-17/reference/umbraco-17-starter-facts/references/management-api.md
$ # hits in /block
89:## Step 5 — Author the view by copying the closest existing block
101:greenfield sequence under *A new block copies the closest existing block* in the block-authoring
$ # hits in styleguide
263:same way it inherits spacing and visibility: by copying the closest existing block, exactly as
$ # hits in planning
43:rule to copy the closest existing block. When the project has no blocks yet, it gives the sequence
$ git diff --stat main -- skills/core
(empty)
```

Five files, as predicted. The reference holds every rule. The Management API starter-facts file
holds the two facts (`toBeNull`, flat array). The spell's two hits are its Step 5 heading and a
citation by heading; the styleguide's hit is its handoff line; the planning reference's hit is its
routing sentence. None states the rule. Core is untouched.

### Check 4 — live cast on the demo project: NOT RUN

```
$ ls <the demo project>/.claude/skills/ | grep -cE 'block|authoring'
0
```

The demo project's install predates `/block` and has neither the spell nor the reference. Casting
there would have needed a reinstall of the pack from this branch first, which is outside this
increment. AC7 rests on Check 2 and on the probe in Check 1.
