# Tests

The repo's first test harness, established by the `install-verification` increment because the
`stack.md → ## Tests` slot was empty and no convention existed.

## Convention

- **`run.sh`** — the runner. Dependency-free bash; no framework to install.
- **`install-check/<case>/`** — one directory per case: a minimal fake project tree plus an `expect`
  file declaring the expected exit code and output substrings.
- **`make-fixtures.sh`** — regenerates every fixture.

```bash
tests/run.sh                    # all cases
tests/run.sh agents-unlinked    # one case
tests/make-fixtures.sh          # regenerate fixtures
```

## Why fixtures are generated, not committed by hand

The first pass built these by hand and one came out malformed — a directory named after an unexpanded
shell variable. The resulting failure was indistinguishable from a real bug in the code under test,
and the debugging went to the wrong place first.

A generator makes fixtures reproducible and reviewable: the *intent* of each case is readable in one
file, and a suspicious failure can be cleared by regenerating rather than inspecting trees.

## The `expect` format

```
exit: 0                        # required, once
contains: some substring       # zero or more, case-insensitive
not_contains: some substring   # zero or more
```

`not_contains` is what asserts the check stays silent about things it should ignore — a project's own
skills, an absent stack pack.

## Fixtures worth understanding

Three cases encode decisions that are easy to implement backwards:

- **`agents-unlinked`** asserts **exit 0**. Unregistered reviewer agents are *degraded*, not broken —
  review still runs inline. Getting this wrong makes every core-only install look like a failure.
- **`no-config`** asserts **exit 0** with every slot empty. That is the fresh-install condition the
  layer contract is built around, so it must never read as a failure.
- **`dangling-symlink`** asserts broken. A directory listing looks fine while every read fails, which
  is why the check reads assets rather than listing them.
