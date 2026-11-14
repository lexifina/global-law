"""infra10: round10/sealed_lines10.py and round10/shep_sealed10.py from the round-9 files (exact replacements)."""
import os

C2 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def tr(src, dst, reps):
    s = open(os.path.join(C2, src), "rb").read().decode("utf-8")
    assert "\r" not in s, src
    for r in reps:
        a, b = r[0], r[1]
        n = r[2] if len(r) > 2 else 1
        assert s.count(a) == n, (src, a[:80], s.count(a), n)
        s = s.replace(a, b)
    open(os.path.join(C2, dst), "wb").write(s.encode("utf-8"))
    print("written", dst)


tr("round9/sealed_lines9.py", "round10/sealed_lines10.py", [
    ('"""Round 9 (agent infra9): one SEALED_LOG.md line from a sealed scorer\'s own output file (fixes round 8\'s empty lines,',
     '"""Round 10 (agent infra10; = round9/sealed_lines9.py, names only). Round 9 (agent infra9): one SEALED_LOG.md line\n'
     'from a sealed scorer\'s own output file (fixes round 8\'s empty lines,'),
    ("python -I round9/sealed_lines9.py", "python -I round10/sealed_lines10.py", 5),
])
tr("round9/shep_sealed9.py", "round10/shep_sealed10.py", [
    ('"""Round 9 (= round8/shep_sealed8.py with round9/FREEZE.md and round9/SEALED_LOG.md; agent infra9): the Shepardized\n'
     'sealed run through round 6\'s compare.py, with the freeze check pointed at round9/FREEZE.md.',
     '"""Round 10 (= round9/shep_sealed9.py with round10/FREEZE.md and round10/SEALED_LOG.md; agent infra10): the\n'
     'Shepardized sealed run through round 6\'s compare.py, with the freeze check pointed at round10/FREEZE.md.'),
    ("round9/FREEZE.md (same \"<sha1>  <path>\" format, every round-9 model file) and SEALED_LOG at round9/SEALED_LOG.md, and",
     "round10/FREEZE.md (same \"<sha1>  <path>\" format, every round-10 model file) and SEALED_LOG at round10/SEALED_LOG.md, and"),
    ("    python -I round9/shep_sealed9.py --split sealed", "    python -I round10/shep_sealed10.py --split sealed"),
    ('    sys.exit("shep_sealed9.py is for --split sealed only")', '    sys.exit("shep_sealed10.py is for --split sealed only")'),
])
