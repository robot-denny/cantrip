# Stand-in for the edited spell's Step 1 and Step 2: apply the grammar and the bound rules
# exactly as written to a plan file, and print what a cast would do before any worker starts.
# It is not the spell; it is the spell's parsing rules with nothing added, kept beside the
# validation log so the log's transcript can be audited and re-run.
#
#   python3 step1-standin.py <plan.md> <cast> [<cast> ...]
import re, sys
plan = sys.argv[1]
text = open(plan).read()
found = [int(m) for m in re.findall(r'^### Step (\d+) — ', text, re.M)]
final = re.findall(r'^### Final — ', text, re.M)
print(f"steps found: {found}; unnumbered final step present: {bool(final)}")
for cast in sys.argv[2:]:
    m = re.match(r'^(\d+)(?:-(\d+)?)?$', cast)
    if not m:
        print(f"{cast:>4}: MALFORMED -> usage line, no worker"); continue
    first = int(m.group(1))
    last = int(m.group(2)) if m.group(2) else (max(found) if '-' in cast else first)
    steps = list(range(first, last + 1))
    if first < 1 or first not in found or last not in found or first > last \
            or any(n not in found for n in steps):
        print(f"{cast:>4}: OUT OF RANGE -> abort listing steps found {found}, no worker"); continue
    single = len(steps) == 1
    nxt = ("/commit-message, archive" if steps[-1] == max(found) else f"/implement-step <plan> {steps[-1]+1}")
    print(f"{cast:>4}: run {steps} -> {len(steps)} worker(s), {len(steps)} report block(s), "
          f"{'single-step output' if single else 'run'}, one Next: -> {nxt}")
