"""Print the dollar-bearing lines of given numbered paragraphs (".NN") of SECTION 3 of a Rev. Proc. text."""
import re, sys, os
f, nums = sys.argv[1], sys.argv[2:]
t = [l for l in open(os.path.expanduser(f'~/docs/irs/{f}.txt'), encoding='utf-8').read().split('\n') if l.strip()]
s = [i for i, l in enumerate(t) if re.match(r'\s*SECTION 3\.', l)][-1]
e = next(i for i, l in enumerate(t) if i > s and re.match(r'\s*SECTION 4\.', l))
cur = None
for l in t[s:e]:
    m = re.match(r'\s*\.(\d\d) ', l)
    if m: cur = m.group(1)
    if cur in nums and ('$' in l or m):
        print(cur, re.sub(r'\s+', ' ', l.strip())[:150])
