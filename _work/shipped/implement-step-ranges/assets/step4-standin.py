# Stand-in for the edited spell's run envelope (Steps 3, 4, and 6): given a plan, a cast, the state
# of the tree, and the outcome each worker returns, print what the developer would see: each
# dirty-tree prompt and where it fell, which workers started, what was relayed, and the one Next:
# line. It is not the spell; it is the rules as written, kept beside the validation log so the
# log's transcripts can be audited and re-run. It extends step2-standin.py's outcome model.
#
#   python3 step4-standin.py <plan.md> <cast> [--tree clean|dirty] [--answer yes|no] [<outcome> ...]
#
# Outcomes are given in run order and are one of DONE, COMMITTED, BLOCKED, NOREPORT. COMMITTED is
# DONE with a report whose Notes carry the line `Committed: yes`. A step past the last outcome given is
# assumed DONE. The parse is the same as step1-standin.py. A step whose prompt line begins
# "Run `/" is a spell-cast, as Step 2 marks it: no worker is ever dispatched for it.
import re, sys
args = sys.argv[1:]
plan, cast = args[0], args[1]
tree, answer, outcomes = "clean", "yes", []
i = 2
while i < len(args):
    if args[i] == "--tree":
        tree = args[i + 1]; i += 2
    elif args[i] == "--answer":
        answer = args[i + 1]; i += 2
    else:
        outcomes.append(args[i]); i += 1
text = open(plan).read()
found = [int(m) for m in re.findall(r'^### Step (\d+) — ', text, re.M)]
m = re.match(r'^(\d+)(?:-(\d+)?)?$', cast)
first = int(m.group(1))
last = int(m.group(2)) if m.group(2) else (max(found) if '-' in cast else first)
steps = list(range(first, last + 1))
# A step's block ends at the next "### Step" heading or the next top-level "---", as Step 2 says,
# so the unnumbered "### Final" section after the last step never counts as part of it.
blocks = re.split(r'^(?=### Step \d+ — )|^---$', text, flags=re.M)
spell = {}
for b in blocks:
    h = re.match(r'### Step (\d+) — ', b)
    c = re.search(r'\*\*Prompt\*\*: Run `(/[^`]+)`', b)
    if h and c:
        spell[int(h.group(1))] = c.group(1)
single = first == last
print(f"cast {cast}: steps to run {steps}, first={first}, last={last}, "
      f"{'single-step cast' if single else 'run'}; tree {tree} at the start")

# Step 3: once per cast, before the first worker, never again.
prompts = 0
if tree == "dirty":
    prompts += 1
    print(f"  prompt before step {steps[0]}: Working tree is dirty. This cast will edit files on top "
          f"of your uncommitted changes. Continue? (yes/no) -> {answer}")
    if answer == "no":
        print("  Nothing ran.")
        print(f"  prompts seen: {prompts}; workers started: []; relayed: nothing; Next: none")
        sys.exit(0)

started, relayed, stop, committed = [], [], None, False
for i, n in enumerate(steps):
    if i > 0:
        tree = "dirty"   # a real plan's finished step leaves its changes in place
    if n in spell:
        msg = f"Step {n} is a spell-cast, not implementation work. Cast it directly: `{spell[n]}`."
        if i == 0:
            print(f"  {msg}")
            print(f"  prompts seen: {prompts}; workers started: []; relayed: the message alone; Next: none")
            sys.exit(0)
        print(f"  run ends before step {n}: no worker is composed or dispatched for it")
        relayed.append(msg)
        stop = ("spell", n)
        break
    outcome = outcomes[i] if i < len(outcomes) else "DONE"
    started.append(n)
    print(f"  worker {n} starts (tree {tree}, no prompt) -> returns {outcome}")
    if outcome in ("DONE", "COMMITTED"):
        relayed.append(f"## Step {n} — DONE" + ("  (Notes: Committed: yes)" if outcome == "COMMITTED" else ""))
        committed = committed or outcome == "COMMITTED"
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
print(f"  prompts seen: {prompts}; workers started: {started}; "
      f"not started: {[n for n in steps if n not in started]}")
scope = ("branch (a step in this run committed, so the uncommitted diff would miss it)" if committed
         else "uncommitted (the run's changes are still uncommitted)")
if isinstance(stop, tuple):
    S = stop[1]
    tail = ("/commit-message. After commit, archive the increment." if S == max(found)
            else f"/implement-step <plan> {S + 1}.")
    print(f"  Next: review changes (git diff), cast {spell[S]} directly, run /code-review {scope}, "
          f"then {tail}")
elif stop is None:
    n = steps[-1]
    if n == max(found):
        print(f"  Next: review changes (git diff), run /code-review {scope}, then /commit-message. "
              f"After commit, archive the increment.")
    else:
        print(f"  Next: review changes (git diff), run /code-review {scope} when satisfied, then "
              f"/implement-step <plan> {n + 1}.")
else:
    pointer = f"{stop}" if (single or stop == last) else f"{stop}-{last}"
    print(f"  Next: read the worker's notes, resolve the blocker, then re-invoke "
          f"/implement-step <plan> {pointer}")
