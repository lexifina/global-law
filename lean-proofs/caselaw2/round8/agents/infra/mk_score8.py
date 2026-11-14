"""infra: derive round8/old_by_class8.py and round8/summary8.py from the round-7 files by exact replacements."""
import os

C2 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def tr(src, dst, reps):
    s = open(os.path.join(C2, src), "rb").read().decode("utf-8")
    assert "\r" not in s
    for a, b in reps:
        assert s.count(a) == 1, (src, a[:70])
        s = s.replace(a, b)
    open(os.path.join(C2, dst), "wb").write(s.encode("utf-8"))


tr("round7/old_by_class7.py", "round8/old_by_class8.py", [
    ('"""Round 7: round5/old_by_class.py on round-7 paths (the round-5 file is not changed).',
     '"""Round 8: round7/old_by_class7.py on round-8 paths (round8/out, round8/stage, round8/results; nothing else\n'
     'changed). Round 7: round5/old_by_class.py on round-7 paths (the round-5 file is not changed).'),
    ('    python round7/old_by_class7.py <name>      (reads round7/out/<name>, round7/stage/<name>;\n'
     '                                                writes round7/results/<name>/old_by_class.json)',
     '    python round8/old_by_class8.py <name>      (reads round8/out/<name>, round8/stage/<name>;\n'
     '                                                writes round8/results/<name>/old_by_class.json)'),
])

KEYS = '''    # round 8: the four new keys, h0 half only (round8/bench_h0/score_h0.py -> results/<name>/bench/SUMMARY.tsv)
    bs = rd(os.path.join(R, "bench", "SUMMARY.tsv"))
    if bs:
        L.append("NEW KEYS, h0 half only (k/n = share (Wilson 95%); primary first):")
        by = {}
        for line in bs.splitlines():
            p = line.split("\\t")
            if line.startswith("#") or len(p) < 8 or p[0] == "key" or p[1].startswith("extra:"):
                continue
            by.setdefault(p[0], []).append(p)
        for key, ps in by.items():
            def one(p):
                if p[5] == "-":
                    return "%s %s/%s" % (p[1], p[3], p[4])
                return "%s %s/%s = %.1f%% (%.1f-%.1f)" % (p[1], p[3], p[4], 100 * float(p[5]), 100 * float(p[6]),
                                                           100 * float(p[7]))
            prim = [p for p in ps if p[2] == "1"]
            rest = [p for p in ps if p[2] != "1" and p[1] in ("precision", "clean", "part", "recall_any",
                                                              "actor_agreement", "link_rate")]
            L.append("  %-26s %s; %s" % (key, "; ".join(one(p) for p in prim), "; ".join(one(p) for p in rest)))
    else:
        L.append("NEW KEYS, h0: not available (round8/bench_h0/score_h0.py not run)")
    print("\\n".join(L))'''

tr("round7/summary7.py", "round8/summary8.py", [
    ('"""Round 7: one-page summary of a scored variant (round7/results/<name>/summary.txt; called by score7.sh).\n\n'
     '    python round7/summary7.py <name>\nReads only the files score7.sh wrote in round7/results/<name>/ and the '
     'variant\'s Lean summary/certs. Dev only.',
     '"""Round 8: one-page summary of a scored variant (round8/results/<name>/summary.txt; called by score8.sh).\n'
     '= round7/summary7.py on round-8 paths, round-8 rows (t8: / h8:) counted by verdict, plus the four new keys on h0.\n\n'
     '    python round8/summary8.py <name>\nReads only the files score8.sh wrote in round8/results/<name>/ and the '
     'variant\'s Lean summary/certs. Dev only (new keys: h0 only).'),
    ('L.append("round 7 variant %s: dev-side scores (results in round7/results/%s/)" % (n, n))',
     'L.append("round 8 variant %s: dev-side scores (results in round8/results/%s/)" % (n, n))'),
    ('if len(p) >= 3 and (p[1].startswith("t7:") or p[1].startswith("h7:")):',
     'if len(p) >= 3 and (p[1].startswith("t8:") or p[1].startswith("h8:")):'),
    ('L.append("round-7 rows by verdict: "', 'L.append("round-8 rows by verdict: "'),
    ('    elif os.path.exists(os.path.join(HERE, "score_fresh7.py")):',
     '    elif os.path.exists(os.path.join(os.path.dirname(HERE), "round7", "score_fresh7.py")):'),
    ('    print("\\n".join(L))', KEYS),
])
print("written")
