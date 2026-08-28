# Tests

The repo's first test harness, established by the `install-verification` increment because the
`stack.md → ## Tests` slot was empty and no convention existed.

## Convention

- **`run.sh`** — the runner. Dependency-free bash; no framework to install.
- **`<suite>/`** — one directory per subject under test. A suite holds a `subject` file plus one
  directory per case.
- **`<suite>/<case>/`** — a minimal fake project tree plus an `expect` file declaring the expected
  exit code and output substrings.
- **`make-fixtures.sh`** — regenerates the `install-check` suite.

```bash
tests/run.sh                              # every suite
tests/run.sh install-check                # one suite, every case
tests/run.sh install-check agents-unlinked   # one case
tests/make-fixtures.sh                    # regenerate install-check
```

A case name is only meaningful inside a suite, so the suite comes first. A mistyped suite name
exits 2 and lists the suites that do exist, rather than reporting a vacuous pass — the failure mode
a runner that silently found nothing to do would have.

## Why suites, and why `subject`

The first runner hardcoded one subject (`scripts/check-install.sh`) and one cases directory. That was
honest while there was exactly one thing to test, and wrong the moment there were two: the second
subject would have meant a second copy of the runner, and the two copies would have drifted.

So the subject is data, not code. `<suite>/subject` is one line holding a repo-relative path to an
executable:

```
scripts/check-install.sh
```

The runner resolves it to an absolute path **before** `cd`-ing into a case directory, because a case
runs with its own fixture tree as the working directory — a relative subject path would resolve
against the fixture and vanish.

`subject` lives inside the suite directory, which matters for `install-check`: `make-fixtures.sh`
does `rm -rf install-check` and rebuilds it, so the generator writes `subject` too. A hand-placed
`subject` would disappear on the next regeneration and every case would fail as "subject missing" —
a failure that points nowhere near its cause.

A suite whose subject does not exist yet fails every case with `subject missing or not executable`
rather than aborting the run. That is deliberate: it is the RED signal for a suite written before its
subject, which is the normal order.

## Why fixtures are generated, not committed by hand

The first pass built these by hand and one came out malformed — a directory named after an unexpanded
shell variable. The resulting failure was indistinguishable from a real bug in the code under test,
and the debugging went to the wrong place first.

A generator makes fixtures reproducible and reviewable: the *intent* of each case is readable in one
file, and a suspicious failure can be cleared by regenerating rather than inspecting trees.

## The `expect` format

```
exit: 0                        # required, once
args: --guides guides.json     # zero or one; a single line
contains: some substring       # zero or more, case-insensitive
not_contains: some substring   # zero or more
same_stdout_as: other-case     # zero or more
stdout_matches: golden.json    # zero or more; a file in the case directory
mask: "someDerivedField":      # zero or more; applies to stdout_matches only
```

`not_contains` is what asserts the check stays silent about things it should ignore — a project's own
skills, an absent stack pack.

`exit` and `args` are single-line directives, and declaring either twice **fails the case** rather
than taking the first and dropping the rest. A silently discarded second line would leave the case
running against arguments nobody reading the file would predict.

`args` exists because a subject with subcommands cannot be exercised by cwd alone. The line is split
on spaces and passed to the subject verbatim; it is **not** glob-expanded, so a `*` reaches the
subject as a literal rather than as whatever happens to sit in the fixture directory.

`same_stdout_as` asserts that this case's stdout byte-matches another case's stdout **in the same
suite**. It exists for claims no substring can express: that two fixtures describing the same thing
in different on-disk formats produce identical output. `contains:` cannot state that — it can only
assert a value both happen to print, which passes just as well if the two are read by two divergent
code paths that agree by luck on the one line the fixture checks.

Naming a case that does not exist is a failure, not a silently skipped assertion.

A mismatch prints the first six lines of the difference and says how many more there were, so a
clipped diff is never mistaken for the whole one.

### `stdout_matches` — when a substring cannot state the claim at all

`contains` finds a value **anywhere** in the output, so it cannot say that a value sits on the
*right* field. That is not a theoretical gap. The first version of the `guide-check` suite asserted
`"mandatory": true` and `"mandatory": false` and passed against a stub with the two flags transposed
onto the wrong properties; it asserted the option list and its default marker and passed against a
stub marking the wrong option. Both stubs were wrong in exactly the way the fixture existed to
prevent. (The dossier carried an option-default marker at the time and no longer does — two real
projects turned out to have none. The demonstration is why the case states a whole document.)

`stdout_matches: <file>` compares stdout byte for byte against a file committed in the case
directory. Field binding, nesting, and array order all become assertable, because the claim is the
whole document rather than a bag of values found in it.

**Author the golden file by hand, from the fixture's intent — never capture it from a run.** A
captured file asserts that the code still does what it did; an authored one asserts that the code
does what was asked. Capturing also makes the first implementation self-certifying, which is the one
thing a test must never be.

`mask: <regex>` neutralizes matching lines on **both** sides of that comparison, for values the
subject derives rather than reads — a content hash cannot be hand-authored, and pasting one in would
assert the implementation against itself. Mask that line and every other line stays exact. The regex
is used as a `sed` address, so it must not contain `|`.

Use `contains` for a claim worth stating in human terms, and the golden file for structure. Stating
structure in both places means two files to edit and one of them going stale.

### Why `same_stdout_as` re-runs the subject, and why it caches

`contains` and `not_contains` see stdout and stderr **merged**, so a fixture does not have to know
which stream a finding went to. A byte comparison cannot use that stream: any stderr noise, or a
different interleaving of the two streams between two runs, would fail the comparison for reasons
that have nothing to do with the claim.

Rather than change what `contains` sees — which would silently alter all 17 existing cases —
`same_stdout_as` runs the subject again with stderr discarded and compares those captures.

**Each capture is taken at most once per run**, cached under the run's temporary directory and keyed
by suite and case. Without the cache the cost tracks the number of *references* rather than the
number of cases: the natural shape of this assertion is several format variants all pointing at one
canonical case, and that canonical case would then be re-run once per variant to produce byte-identical
output every time. Measured on a five-case suite, that was 15 subject invocations where 10 suffice.

The cache assumes a case's stdout does not change within one run — true because subjects here are
deterministic and read-only, and because cases run sequentially. **If case execution is ever
parallelized, revisit this together with the cache key**, not separately.

## Fixtures worth understanding

Three cases encode decisions that are easy to implement backwards:

- **`agents-unlinked`** asserts **exit 0**. Unregistered reviewer agents are *degraded*, not broken —
  review still runs inline. Getting this wrong makes every core-only install look like a failure.
- **`no-config`** asserts **exit 0** with every slot empty. That is the fresh-install condition the
  layer contract is built around, so it must never read as a failure.
- **`dangling-symlink`** asserts broken. A directory listing looks fine while every read fails, which
  is why the check reads assets rather than listing them.

In `guide-check`, one pair of cases exists to keep a refusal from widening by accident:

- **`deploy-missing-alias` / `usync-missing-alias`** assert **exit 1** with no dossier printed. A
  folder that exists, reads fine, and holds no artifact for the requested alias cannot be answered,
  so it must not produce a thin document instead.
- **`deploy-propertyless` / `usync-propertyless` / `deploy-empty-tab`** assert **exit 0** with the
  dossier printed. A component with no editable fields is a real component — a taxonomy-style node,
  or a type contributing one empty tab — and both shapes were found among the demo project's 68
  document types. The line is whether anything was left *unresolved*, never how thin the result is,
  and these three are the cases that say so. A refusal with no case proving what it does **not**
  refuse is how the next increment tightens it by accident.
- **`models-only-rung`** asserts a thin dossier that says *what* is thin about it. Its golden file
  states `structureAvailable: false` plus a `structureGaps` entry per field the rung cannot report,
  because `"options": []` cannot tell a component with no choices from a source that could not read
  them. It also asserts `not_contains: declares no editable properties` — the property-less note and
  the gap list are different claims, and an implementation that flattened the properties somewhere
  the count could not see them would print both and contradict itself.
- **`inventory-palette`** is the only case in the suite whose value is a single number. Its project
  holds six element types and offers three of them as content blocks, so a determiner reading the
  element-type flag scores 6 and a determiner reading the palette scores 3 — and *no* assertion on a
  single component can tell those two apart. It compares `--json` output as a whole document
  because `contains` cannot say which list an alias landed in: `"mediaRowSettings"` contains
  `"mediaRow"`, and every excluded alias is deliberately named in the human report.
- **`inventory-page-types-proposed`** asserts the whole human report, including the word `PROPOSED`
  and the rule that produced each count. A page type, a folder, and an abstract base are separated
  by no structural flag, so the behavior under test is *what the report says it did* rather than a
  verdict — and all three aliases appear in the output, so section placement is the claim.
- **`inventory-models-refused`** asserts **exit 1**. A generated model carries no palette, so an
  empty inventory there would read as "this project offers no blocks" — true for some projects and
  false for others, with nothing to tell them apart. **`inventory-no-palette`** is its mirror and
  asserts **exit 0** with a note: a project that really has element types and no block editor gets
  a truthful zero *plus* the sentence saying which of the two readings it cannot distinguish. Those
  two cases together are what keeps the guard from becoming either a silent zero or a refusal that
  rejects a true answer.
- **`audit-orphan-and-sourceless`** compares the whole report because half its claim is a negative:
  a guide for a deleted component must be named as an orphan, and a hand-written guide claiming no
  source must appear in **none** of the three sections. `not_contains` can say the page is named
  nowhere; only the whole document can also say the counts were not inflated by it.
- **`audit-signature-mismatch`** is the only case supplying the **inventory** as a file as well as
  the guide set, and the reason is that a signature is a hash. A fixture cannot state the current
  one, so a project-backed case can only ever assert the *not compared* path — supplied on both
  sides, the comparison becomes hand-authorable in both directions at once: a differing pair named
  as stale, a matching pair named nowhere. A case asserting only the mismatch would pass against an
  implementation that called every signature-bearing guide stale. It is also the only coverage the
  `--inventory` seam has, which is how the spell will hand over a live read.
- **`audit-guides-unreadable` / `audit-guides-no-source-key` / `audit-guides-duplicate-source`** fix
  the refuse/permit line on the one input this command cannot check by re-reading the project. The
  first two assert **exit 1** with no report printed: a guides file half-read reports the components
  its dropped entries documented as undocumented, and nothing in the output would say so. The third
  asserts **exit 0** with a note — two pages claiming one source is answerable, since the component
  is documented either way. The permit case is the one that keeps the refusal from widening.
- **`audit-strict-exit` / `audit-strict-exit-gated` / `audit-strict-clean`** are one behavior in
  three cases, and the behavior is entirely the exit code. The first asserts **exit 0 with a
  finding** — the audit is a backlog, and one that exited non-zero on findings would fail a build
  by default in exactly the projects that wired it into CI early. The second asserts a non-zero
  exit under `--strict`, plus `same_stdout_as` the first, which is the whole of "and nothing else
  changes with it": a flag that also added a line naming itself would pass an exit-code assertion
  and still have changed the report. The third asserts `--strict` on a healthy project exits 0,
  which is what a flag implemented as "exit non-zero" rather than "exit non-zero on findings"
  fails.
- **`audit-rung-statement`** is a project readable only from generated models with a guide for
  every block: nothing undocumented, nothing orphaned, nothing stale, and a report that still owes
  its reader the statement that this source records no tabs, no required flags and no option lists.
  It is stated **once for the report** and never against a guide, so the report is compared whole —
  a per-guide incompleteness finding would satisfy every substring assertion in the case. Its
  inventory is supplied through `--inventory`, because the determiner refuses at the models rung on
  purpose (`inventory-models-refused`); nothing restricts what rung a supplied document may
  declare, which is what makes that seam worth having.
- **`plan-noop`** is the cheapest guard in the suite and the reason `plan` exists ahead of the
  spell: a page whose stored signature still matches its source produces no proposal, and the
  output says in words that **no model call is needed**. Without it, a regeneration loop that
  spends a model call on every run to rewrite prose identical to the prose already there passes
  every other case here. Asserted as the whole `--json` document, because `noop` and
  `modelCallNeeded` are what the spell reads to skip that call, and a report sentence is no use
  to it. Its dossier is supplied through `--dossier`: a *matching* signature is only
  hand-authorable that way, since a hash cannot be written into a fixture and computing one here
  would assert the implementation against itself — the same reason `audit-signature-mismatch`
  supplies both sides.
- **`plan-ownership`** is its twin at the other end, compared as the whole human report because
  "field, current value, proposed value" is a claim about *where* a value sits. Three things at
  once: the machine-owned fields are proposed — the bookkeeping reference and the property table,
  which is all the register leaves in that class; the seeded-once purpose sentence and example
  and the never-touched blurb, screenshot and page name come back **byte for byte**; and the
  when-to-use section this page never got is **reported** in a section of its own rather than
  proposed, because a seeded field's only write is at page creation and an empty field left out
  of a plan altogether reads as a finished one.
- **`plan-prose-left-alone`** is that case's mirror, and the whole report again: the same
  component, and a page carrying **both** prose blocks in an editor's own words. Neither is
  proposed and neither is offered, so nothing in the report asks anybody to approve a
  replacement for something a person wrote. It is also where the model-call sentence is pinned.
  With every prose field on a guide page seeded once, the count of machine-owned fields owing
  prose is nought — and the sentence that printed that nought read as a bug in the tool, so the
  form asserted here says a model is needed and says what for: the property table's markup,
  which comes from the project's own components.
- **`plan-other-rung`** holds the two signatures **identical** and the rungs different. A plan
  that compares them without checking the rung reports a no-op, and two rungs sign one component
  differently by design, so a matching string across rungs is no information at all. "No
  information" read as "no change" is a guide that silently stops being regenerated the day a
  project gains a serialization format.
- **`plan-project-read`** is the only `plan` case that reads a project off disk, since the three
  above all supply a dossier. Substrings rather than a golden: its claims are that the project was
  read at all, that a tab and a group both reach the property table, and that an inherited
  property is marked as inherited — a golden file would add a masked signature line and a second
  copy of `plan-ownership`'s report.

## Why 46 fixture `SKILL.md` files do not pollute an install

Fixtures contain real `SKILL.md` files, because the check under test looks for exactly those. That
raises a fair question: does installing this repo hand a consumer 46 junk skills?

Verified against `skills@1.5.21`: no. A full-repo listing finds 15 — the 13 core skills plus the 2
pack skills — and ignores everything under `tests/`.

Two reasons not to rely on that alone. It is **empirical, not guaranteed**: a change to the
installer's discovery could surface them. And the documented install command is subpath-scoped
(`skills add <repo>/skills/core`), which can never reach `tests/` regardless of discovery behavior.

So the defense is the subpath, and the observed behavior is a bonus. If a future fixture needs to
live somewhere other than `tests/`, re-verify with `skills add <repo> --list` before committing it.
