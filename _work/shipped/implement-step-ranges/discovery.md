# Discovery: Implement-step ranges

_Discovery input for `/spec` — produced by `/explore` on 2026-09-25. Scope: heavyweight._

## Problem framing

- **Who is affected.** Developers running a plan through `/implement-step`. They like the work landing
  in small steps and want to keep that. What costs them is the loop around each step: cast, wait, read
  the report, cast `/code-review`, approve its recommendations, say "proceed" to the next step. On a
  plan of ten or more steps that loop is mostly the person being present to say "go on".
- **What is worth keeping.** The steps themselves, the fresh worker per step, the TDD envelope, and the
  human review at a boundary. Nothing the chain produces today may go missing. Only the count of
  confirmations should fall.
- **Observed, not assumed.** A developer asked for it directly. The same shape existed in the toolkit's
  pre-Cantrip ancestor and was used that way ("implement steps 1 to 3, then pause so I can check").
- **What a checkpoint actually catches.** Taste: the agent taking a less elegant or over-complicated
  route than the developer would. The team's standing remedy for that is to write the rule into the
  `.agents/config` conventions and stack slots, which reduces how often a human needs to be watching.
- **A separate problem seen alongside it.** One plan for a whole site header ran to fourteen steps. That
  is a spec that held several increments, and it is out of scope here.
- **The problem in one sentence.** The human wants to choose where to pause, independent of how the
  plan happened to be cut.

## Outcomes sought

- The same result at the end of the plan with fewer procedural confirmations along the way.
- The accordion test: a developer plans a small block, runs the early steps unattended, and comes back
  at the point where they can click the thing open and closed and read the code in its final place.

## Options considered

1. **A range argument.** `/implement-step <plan> 1-3` runs each step's worker in sequence, relays each
   report, and stops at the end of the range or on the first BLOCKED. Review is cast by the person at
   the pause. *Fits now and later*: no new artifact, no change to the plan format, and the single-step
   cast remains the same call with a range of one. *Worse at*: an unattended run costs more before
   anyone looks if a worker goes wrong; BLOCKED is the only brake.
2. **An open range.** `/implement-step <plan> 3-` runs to the end of the plan under the same rules. The
   "stop at the next manual check" reading was considered and rejected: two stopping rules behind one
   argument, and the plan report already tells the developer where the seams are. *Worse at*: invites
   use as a shortcut by someone who has not read the plan. Documented like any other cast, but not led
   with when teaching.
3. **Plan-side checkpoints.** `/plan` groups steps under named checkpoints and implement-step runs a
   group. *Dropped*: it re-couples the two decisions this work separates, because the planner would
   again be choosing where the human looks. A suggested first range in the plan's `Next:` line was also
   considered and left out.
4. **Coarser steps at plan time.** A granularity argument to `/plan`. *Dropped*: addresses plan size,
   not the misalignment between step cuts and human interest. The fourteen-step case is a sizing
   problem upstream of this spell and belongs on the roadmap on its own.
5. **Automatic review inside the loop.** Implement-step dispatches the reviewers itself between steps or
   at the pause. *Dropped*: ADR 0003 says spells chain by suggestion and never invoke each other, and
   the spell would have to duplicate `/code-review`'s reviewer discovery.

## Trade-offs & second-order effects

- **Notes between workers.** Each step gets a fresh worker, so in a range nobody reads step 2's report
  before step 3 starts. A deviation from the plan or a convention chosen because a slot was empty would
  be lost. Decided: the orchestrator passes the earlier steps' report blocks from the same run into each
  later worker's prompt as a short "earlier in this run" section. The worker then has what the human
  had.
- **Main-thread noise.** A ten-step range relays ten reports into the conversation the spell exists to
  keep clean. Decided: relay each step's report block verbatim as it lands, since the blocks are compact
  and a merged summary would hide which step a failed validation belonged to. One `Next:` line at the
  end of the run, not one per step.
- **Review scope after a range.** `/code-review` defaults to the uncommitted diff, which covers a whole
  range when steps leave changes in place. When a plan commits per step, that diff is empty at the pause.
  Decided: the closing `Next:` line names the scope, `uncommitted` normally and `branch` when any step in
  the run committed, and says why. Code-review usually notices on its own; the nudge stays anyway.
- **Finding the seams.** Choosing a range means knowing which steps end in a Manual check. Decided: the
  plan's closing report lists step titles and marks each step that carries a Manual validation, so the
  range is chosen from the summary and not from reading the file.
- **Indirect benefit.** The roadmap's open item about the security reference being read on every
  `/code-review` dispatch, paid once per step, becomes once per range. Nothing changes in that item; its
  cost falls.
- **Wording that assumes one step.** The `workflow` skill and the README both say implement-step runs one
  step at a time. ADR 0016's reasoning does not depend on it and survives unchanged.

## Direction

**Chosen: option 1 with option 2's open form.** A range argument on `/implement-step`, literal in its
bounds, stopping only on BLOCKED, with review cast by the person at the pause. The plan report gains
the Manual-check marks so a developer can choose a range without opening the file.

The rationale that carried it: it is the form a developer asked for and had used before, it adds no
artifact and no plan construct, it keeps every safeguard the single-step flow has, and a single step
stays the same cast with a range of one.

## Open questions for /spec

- **Argument grammar.** Whether `1-1` is accepted as a range of one, what a reversed or out-of-range
  bound does, and how `argument-hint` reads with three forms.
- **What gets passed forward.** Whether later workers receive earlier steps' whole report blocks or only
  their Notes, and whether that section is capped for long runs.
- **The dirty-tree prompt.** It should fire once before the first step, since the tree is dirty by
  design between steps. Confirm and write it down.
- **Older plans with a numbered spell-cast step.** Today a single cast refuses that step and hands it
  back. A range that reaches one should stop before it, relay what finished, and hand it back the same
  way rather than abort the whole run.
- **Where the open form is documented.** Spell cards and the README row document every cast, so `3-`
  is written down there. Decide whether the quick-start and teaching material mention it at all.
- **Wording updates.** The one-step sentence in the `workflow` skill and the README implement-step row.
- **The sizing problem.** File the fourteen-step header as its own roadmap entry, separate from this
  increment.
