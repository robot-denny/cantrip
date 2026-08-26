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
prevent.

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
