# Step 6 — validation log

Working tree: branch `robot-denny/implement-step-ranges`, HEAD `e3bd705`, clean before the edit.

This step edits no spell. It updates every surface that described `/implement-step` as one step
per cast, so the test is the grep the plan names, run before and after. RED is the grep as it
stood. GREEN is the same grep with each surviving hit describing the single step as one of three
forms, and no hit saying "one step per cast" as a limit. The contract gate is the automated check.
The read of the spell card as a developer who has never used a range is the person's; the card is
reproduced at the end so it can be judged from here.

---

## RED, before the edit

```
$ grep -rn -i 'one step' README.md docs skills/core/reference/workflow
docs/measurements.md:47:to it: one step's three fixture cases carried 33 `.uda` files between them and moved the full gate
docs/spell-cards.md:125:- **Does:** Runs one step in a separate context, so a long plan never clutters your main conversation. It holds the step to the plan's test-first and validation contract, then relays a short structured report.
docs/spell-cards.md:126:- **Watch for:** one step per cast. The isolation is the point.
docs/installing.md:129:your tool can dispatch is the one step the installer cannot do for you. The README's step 3 does it.
docs/layout.md:89:/implement-step ─▶ your codebase             reads plan.md, one step per cast
skills/core/reference/workflow/SKILL.md:25:`/implement-step` runs one step at a time against a fresh context so the main thread stays
```

The `measurements.md` and `installing.md` hits use "one step" in unrelated senses and are out of
scope. The `README.md` row does not contain the phrase "one step"; it read "Runs one plan step in
an isolated context, then reports back." and was found during planning by reading, not by this
grep. That leaves four in-scope hits: `spell-cards.md:125`, `spell-cards.md:126`, `layout.md:89`,
and `workflow/SKILL.md:25`, of which two say "one step per cast" as a limit.

One more blind spot, found at review rather than by this grep: the workflow skill's chain line at
`workflow/SKILL.md:19` read `/implement-step <slug> N` (per step), two lines above the paragraph
this step rewrote. "(per step)" does not contain "one step", so the grep never surfaced it, and the
file contradicted itself. It now reads "(per step, or a range)". The rewritten paragraph was also
tightened after review: the stop-at-blocked clause was dropped, since the spell card and the
changelog carry it and this reference loads on many turns.

## GREEN, after the edit

```
$ grep -rn -i 'one step' README.md docs skills/core/reference/workflow
docs/measurements.md:47:to it: one step's three fixture cases carried 33 `.uda` files between them and moved the full gate
docs/installing.md:129:your tool can dispatch is the one step the installer cannot do for you. The README's step 3 does it.
docs/spell-cards.md:125:- **Does:** Runs one step in a separate context, so a long plan never clutters your main conversation. Given a range, it runs each step the same way, in order, with a fresh context per step, and relays each report as it lands. It holds every step to the plan's test-first and validation contract.
docs/spell-cards.md:126:- **Watch for:** one fresh context per step, whether you cast one step or a range. The isolation is the point. A run stops at the first blocked step and says which range to re-invoke, and one `Next:` line closes the cast with the `/code-review` scope named.
docs/layout.md:89:/implement-step ─▶ your codebase             reads plan.md, one step or a range per cast
skills/core/reference/workflow/SKILL.md:25:`/implement-step` runs one step against a fresh context so the main thread stays clean across
```

Each of the four in-scope hits survives and now leads with the single step, then names the range
in the same line or the next. No hit says "one step per cast". The two out-of-scope hits are
unchanged.

## Contract gate

```
$ ./scripts/check-contract.sh
22 checks passed.
```

The README row kept its link to `skills/core/spellbook/implement-step/SKILL.md`, so check 18
(every shipped unit is linked from the README) still passes.

## Spell cards as edited, for the person's read

The manual validation is to read the `/implement-step` card as a developer who has never used a
range and confirm the three forms are shown and the single step still comes first. That read is
still owed. The cards as they stand after this step:

```
### /plan

- **Type:** Spell
- **Group:** Core spellbook
- **Cast:** `/plan <spec path | short description>`
- **Needs:** a spec, ideally
- **Leaves:** `_work/<slug>/plan.md`
- **Does:** Turns a spec into phased steps, each written test-first, each runnable on its own in a fresh context with a paste-ready prompt. Records the key decisions once, so no later step works them out again.
- **Watch for:** the last step records durable behavior. It is a spell you cast rather than a step you run. The closing report lists every step and marks those that end in a manual check, so you can pick a range for `/implement-step` without opening the plan.
- **Then:** `/implement-step <slug> 1`

### /implement-step

- **Type:** Spell
- **Group:** Core spellbook
- **Cast:** `/implement-step <plan> <step>`, where the step is one number (`4`), a closed range (`1-3`), or an open range to the last step (`3-`)
- **Needs:** a saved plan
- **Leaves:** the code change, plus a DONE or BLOCKED report
- **Does:** Runs one step in a separate context, so a long plan never clutters your main conversation. Given a range, it runs each step the same way, in order, with a fresh context per step, and relays each report as it lands. It holds every step to the plan's test-first and validation contract.
- **Watch for:** one fresh context per step, whether you cast one step or a range. The isolation is the point. A run stops at the first blocked step and says which range to re-invoke, and one `Next:` line closes the cast with the `/code-review` scope named.
- **Then:** the next step, alone or as the start of a range; `/code-review` once the plan is done
```

## Other surfaces, as edited

`README.md` spellbook row:

> Runs one plan step in an isolated context, then reports back. Give it a range, `1-3` or `3-`,
> and it runs those steps in order, one fresh context each.

`skills/core/reference/workflow/SKILL.md`, the paragraph at line 25:

> `/implement-step` runs one step against a fresh context so the main thread stays clean across
> a long plan. It also takes a range, `1-3` or `3-`, and runs those steps in order, one fresh
> context each. Either way a step runs in a dispatched subagent, or you paste its prompt into a
> new session, whichever suits the setup.

`ROADMAP.md` *Now* opens with one sentence naming the branch and nothing else. The *Later* entry
on plan sizing and the `CHANGELOG.md` entry under *Unreleased → Added* are in the diff.
