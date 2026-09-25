# Stand-in for the spell's Step 4, the prompt composer: given a SKILL.md, a plan, a cast, and the
# report blocks the earlier workers of this run returned, print the prompt the next worker would
# receive. It is not the spell. It lifts the worker prompt template out of the SKILL.md it is
# pointed at, the four-backtick fence in Step 4, and fills each placeholder as the spell says to,
# so the same script composes against the committed spell (RED) and the edited one (GREEN).
#
#   python3 step3-standin.py <SKILL.md> <plan.md> <cast> <step> [<report.md> ...]
#
# <cast> is the range as typed, so the script can say whether <step> is the first step of the
# run. Each <report.md> is one earlier worker's report block, given in run order. The reports are
# this run's only: nothing from an earlier cast is read, because nothing from one is passed.
import re, sys

skill, plan, cast, step = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
reports = [open(p).read().strip() for p in sys.argv[5:]]

skill_text = open(skill).read()
plan_text = open(plan).read()

# The template is the first four-backtick fence in the spell.
template = re.search(r'^````\n(.*?)^````', skill_text, re.S | re.M).group(1)

# Sections of the plan, per the spell's Step 2: a ## heading up to the next ## heading or the next
# top-level --- rule.
def section(name):
    m = re.search(r'^## ' + re.escape(name) + r'\n(.*?)(?=^## |^---\s*$)', plan_text, re.S | re.M)
    return m.group(1).strip()

def step_block(n):
    m = re.search(r'^### Step ' + str(n) + r' — .*?(?=^### Step |^---\s*$|\Z)', plan_text, re.S | re.M)
    return m.group(0).strip()

first = int(re.match(r'^(\d+)', cast).group(1))
if step == first and reports:
    sys.exit("the first step of a run has no earlier reports; none should be passed")

# Fill the multi-line placeholders, each a line starting with { through the line ending with }.
def fill(m):
    key = m.group(0)
    if 'Context section' in key:
        return section('Context')
    if 'Key Decisions section' in key:
        return section('Key Decisions')
    if 'Step N block' in key:
        return step_block(step)
    if 'report' in key:
        # One backtick longer than the longest run inside the block, never fewer than three.
        def fence(r):
            longest = max((len(m) for m in re.findall(r'`+', r)), default=0)
            return '`' * max(3, longest + 1)
        return '\n\n'.join(fence(r) + '\n' + r + '\n' + fence(r) for r in reports)
    return key

prompt = re.sub(r'^\{[^}]*\}$', fill, template, flags=re.M)
prompt = prompt.replace('{N}', str(step)).replace('{plan}', plan)

# The spell leaves the whole section out on the first step of a run: drop the heading through the
# line before the next ## heading.
if not reports:
    prompt = re.sub(r'^## Earlier in this run\n.*?(?=^## )', '', prompt, flags=re.S | re.M)

print(prompt, end='')
