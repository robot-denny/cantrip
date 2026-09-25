# Stand-in for the edited spell's run loop and stop rule (Steps 4 and 6): given a plan, a cast,
# and the outcome each worker returns, print what the developer would see relayed, which workers
# started, and the one Next: line. It is not the spell; it is the stop rule as written, kept
# beside the validation log so the log's transcript can be audited and re-run.
#
#   python3 step2-standin.py <plan.md> <cast> <outcome> [<outcome> ...]
#
# Outcomes are given in run order and are one of DONE, BLOCKED, NOREPORT. A step past the
# last outcome given is assumed DONE. The parse is the same as step1-standin.py.
import re, sys
plan, cast, outcomes = sys.argv[1], sys.argv[2], sys.argv[3:]
text = open(plan).read()
found = [int(m) for m in re.findall(r'^### Step (\d+) — ', text, re.M)]
m = re.match(r'^(\d+)(?:-(\d+)?)?$', cast)
first = int(m.group(1))
last = int(m.group(2)) if m.group(2) else (max(found) if '-' in cast else first)
steps = list(range(first, last + 1))
single = first == last
print(f"cast {cast}: steps to run {steps}, first={first}, last={last}, "
      f"{'single-step cast' if single else 'run'}")
started, relayed, stop = [], [], None
for i, n in enumerate(steps):
    outcome = outcomes[i] if i < len(outcomes) else "DONE"
    started.append(n)
    print(f"  worker {n} starts -> returns {outcome}")
    if outcome == "DONE":
        relayed.append(f"## Step {n} — DONE")
        continue
    if outcome == "BLOCKED":
        relayed.append(f"## Step {n} — BLOCKED")
    else:
        relayed.append(f"(worker {n}'s final message, no report block)")
        relayed.append(f"Step {n} is treated as BLOCKED because no report arrived.")
    stop = n
    break
print("  relayed, in order:")
for r in relayed:
    print(f"    {r}")
print(f"  workers started: {started}; not started: {[n for n in steps if n not in started]}")
if stop is None:
    n = steps[-1]
    nxt = ("/commit-message, then archive" if n == max(found) else f"/implement-step <plan> {n + 1}")
    print(f"  Next: review, /code-review, then {nxt}")
else:
    pointer = f"{stop}" if (single or stop == last) else f"{stop}-{last}"
    print(f"  Next: read the worker's notes, resolve the blocker, then re-invoke "
          f"/implement-step <plan> {pointer}")
