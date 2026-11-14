import os
C2 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
p = os.path.join(C2, "round12", "summary12.py")
s = open(p, encoding="utf-8").read()
def rep(a, b):
    global s
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)
rep('''= round10/summary10.py on round-12 paths; round-12 rows (t12: / h12:) counted by verdict too.
''', '''= round11/summary11.py on round-12 paths (agent infra12); round-11 (t11: / h11:) and round-12 (t12: / h12:) rows
counted by verdict. Round 11: = round10/summary10.py on round-11 paths.
''')
rep('''    cv11 = collections.Counter()
''', '''    cv11 = collections.Counter()
    cv12 = collections.Counter()
''')
rep('''                elif len(p) >= 3 and (p[1].startswith("t12:") or p[1].startswith("h12:")):
                    cv11["%s %s" % (p[1][:3], p[2])] += 1
''', '''                elif len(p) >= 3 and (p[1].startswith("t11:") or p[1].startswith("h11:")):
                    cv11["%s %s" % (p[1][:3], p[2])] += 1
                elif len(p) >= 3 and (p[1].startswith("t12:") or p[1].startswith("h12:")):
                    cv12["%s %s" % (p[1][:3], p[2])] += 1
''')
rep('''    L.append("round-12 rows by verdict: " + (", ".join("%s %d" % kv for kv in sorted(cv11.items())) or "none"))
''', '''    L.append("round-11 rows by verdict: " + (", ".join("%s %d" % kv for kv in sorted(cv11.items())) or "none"))
    L.append("round-12 rows by verdict: " + (", ".join("%s %d" % kv for kv in sorted(cv12.items())) or "none"))
''')
open(p, "w", encoding="utf-8", newline="\n").write(s)
p = os.path.join(C2, "round12", "score12.sh")
s = open(p, encoding="utf-8").read()
rep('''# round 11: every DEV-side score''', '''# round 12: every DEV-side score''')
rep('''#   = round10/score10.sh on round-12 paths (agent infra11; round10/score10.sh''',
    '''#   = round11/score11.sh on round-12 paths (agent infra12; round11/score11.sh = round10/score10.sh on round-11 paths; round10/score10.sh''')
rep('''never the closed keys (Songer, Brace & Hall, Federal Circuit),
# never a round-10 or round-12 fresh key.''', '''never the closed keys (songer_treat, brace_hall_state,
# fedcir_dataset, bhk_enbanc), never a round-10, round-11 or round-12 fresh key.''')
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
