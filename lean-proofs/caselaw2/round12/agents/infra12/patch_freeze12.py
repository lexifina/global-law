"""infra12: hand edits of the generated round12/freeze12.py."""
import os
C2 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
p = os.path.join(C2, "round12", "freeze12.py")
s = open(p, encoding="utf-8").read()
def rep(a, b):
    global s
    assert s.count(a) == 1, a[:70]
    s = s.replace(a, b)
rep('''sealed runs. LEAD ONLY. (= round10/freeze10.py on round-12 paths and file lists, agent infra11; round 11 adds:''',
    '''sealed runs. LEAD ONLY. (agent infra12: = round11/freeze11.py on round-12 paths: closed keys songer_treat,
brace_hall_state (fourth use), fedcir_dataset (third use) and bhk_enbanc (second use); the binary of a NOBUILD run is
~/caselaw2/r12_bin/caselaw2_r11v11d (frozen round-11 s51); the order-node folder given to stage12 --nodes (from the
stage's MANIFEST args: nodes.tsv, CHANGED.tsv, *.md, text/*.txt) is hashed when the stage was built with --nodes;
v11d (round11/out/v11d + round11/stage/v11d) is the comparison build; a dry run never names round12/agents/bench12/
files or key files. Round 11 = round10/freeze10.py on round-11 paths and file lists, agent infra11; round 11 adds:''')
rep('''R9_KEYS = ("songer_treat", "brace_hall_state", "fedcir_dataset")  # closed keys: third, third, second use in round 11''',
    '''R9_KEYS = ("songer_treat", "brace_hall_state", "fedcir_dataset", "bhk_enbanc")  # closed keys: 4th, 4th, 3rd, 2nd use (round 12)
BENCH12 = os.path.join(HERE, "agents", "bench12")  # round 12: the fresh-key builder's folder (never named in a dry run)''')
rep('''    if first.startswith("NOBUILD frozen r10v10d"):
        path = "~/caselaw2/r12_bin/caselaw2_r10v10d"''', '''    if first.startswith("NOBUILD frozen r11v11d"):
        path = "~/caselaw2/r12_bin/caselaw2_r11v11d"''')
rep('''    od = os.path.join(HERE, "data_orders")
    for p in [os.path.join(od, "nodes.tsv")] + sorted(glob.glob(os.path.join(od, "text", "*.txt"))):
        if os.path.exists(p):
            files.append(p)''', '''    # round 12: the node folder of `--nodes DIR` (MANIFEST.txt args) when the stage was built with it
    od = None
    mf = os.path.join(st, "MANIFEST.txt")
    if os.path.exists(mf):
        args = (open(mf, encoding="utf-8").read().split("\n") + ["", ""])[1].split()
        if "--nodes" in args and args.index("--nodes") + 1 < len(args):
            od = os.path.join(C2, args[args.index("--nodes") + 1])
    if od:
        for p in ([os.path.join(od, "nodes.tsv"), os.path.join(od, "CHANGED.tsv")] +
                  sorted(glob.glob(os.path.join(od, "*.md"))) + sorted(glob.glob(os.path.join(od, "text", "*.txt")))):
            if os.path.exists(p) and p not in files:
                files.append(p)''')
rep('''    for t in ("DESIGN12.md", "LEAN11.md", "FRESH_KEYS.txt"):''', '''    for t in ("DESIGN12.md", "LEAN12.md", "FRESH_KEYS.txt"):''')
rep('''            if p not in files and not SKIP_NAMES.search(os.path.basename(p)):
                files.append(p)''', '''            if p not in files and not SKIP_NAMES.search(os.path.basename(p)):
                if not touch_keys and os.path.normpath(p).startswith(BENCH12 + os.sep):
                    KEYFILES.add("(round12/agents/bench12/ scripts: not named in a dry run)")
                    continue
                files.append(p)''')
rep('''                "The sealed halves (fresh lists, seventh use; Shepardized, sixth use; both burned), the h1 halves of "
                "the four round-8 keys (fourth use), songer_treat and brace_hall_state (third use), fedcir_dataset "
                "(second use) and the round-12 fresh keys (first and only use, with v10d) are scored once on exactly "''',
    '''                "The sealed halves (fresh lists and Shepardized, both burned), the h1 halves of the four round-8 "
                "keys (fifth use), songer_treat and brace_hall_state (fourth use), fedcir_dataset (third use), "
                "bhk_enbanc (second use) and the round-12 fresh keys (first and only use, with v11d) are scored once on exactly "''')
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
