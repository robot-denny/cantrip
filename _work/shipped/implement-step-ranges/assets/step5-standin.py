# Stand-in for /plan's closing report (Step 7): given a saved plan, print the report a developer
# would see. It is not the spell; it is the report rule as written, kept beside the validation log
# so the log's transcripts can be audited and re-run.
#
#   python3 step5-standin.py <plan.md> [--committed]
#
# The step list is derived from the plan alone. A step is every `### Step N — <title>` heading. A
# step is marked `(manual check)` when its own block, which ends at the next `### Step` heading or
# the next top-level `---` as /implement-step reads it, carries a line beginning `- [Manual]` after
# its `**Validation**` line. The unnumbered `### Final` section is not a step and is never listed.
# With --committed the script prints the report the spell at HEAD~ produced, which has no list, so
# the RED transcript is mechanical too.
#
# Branch and Next are reproduced only so the report reads whole: the branch is the current one and
# the slug is the file stem with a trailing `-plan` removed, which is what Step 1 would extract from
# a path. Neither line is what this step tests.
import re, subprocess, sys
from pathlib import Path
args = sys.argv[1:]
committed = "--committed" in args
plan = [a for a in args if a != "--committed"][0]
text = Path(plan).read_text()
blocks = re.split(r'^(?=### Step \d+ — )|^---$', text, flags=re.M)
steps = []
for b in blocks:
    h = re.match(r'### Step (\d+) — (.+?)\s*$', b, re.M)
    if not h:
        continue
    after_validation = b.split("**Validation**", 1)[1] if "**Validation**" in b else ""
    manual = re.search(r'^- \[Manual\]', after_validation, re.M) is not None
    steps.append((int(h.group(1)), h.group(2).strip(), manual))
branch = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True).stdout.strip()
slug = re.sub(r'-plan$', '', Path(plan).stem)
print(f"Plan: {plan}")
print(f"Steps: {len(steps)}")
if not committed:
    for n, title, manual in steps:
        print(f"  {n}  {title}" + (" (manual check)" if manual else ""))
print(f"Branch: {branch}")
print(f"Next: /implement-step {slug} 1  (run each step in a fresh context to keep the main one clean)")
