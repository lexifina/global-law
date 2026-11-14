"""infra9: derive the round-9 tools from the round-8 files by exact replacements (round-8 files are only read).

    python -X utf8 round9/agents/infra9/mk_round9.py

Each replacement must occur exactly the stated number of times (default once) in the round-8 source.
"""
import os

C2 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def tr(src, dst, reps, mode=None):
    s = open(os.path.join(C2, src), "rb").read().decode("utf-8")
    assert "\r" not in s, src
    for r in reps:
        a, b = r[0], r[1]
        n = r[2] if len(r) > 2 else 1
        assert s.count(a) == n, (src, a[:80], s.count(a), n)
        s = s.replace(a, b)
    p = os.path.join(C2, dst)
    open(p, "wb").write(s.encode("utf-8"))
    print("written", dst)


# ---- 1. certifiers
tr("round8/certify8.py", "round9/certify9.py", [
    ('"""Round 8 (= round7/certify7.py with base round7/stage/v3 and ids t8: / h8:): turn linker / reader rows\n'
     '(DESIGN7 section 4) into certified table deltas.',
     '"""Round 9 (= round8/certify8.py, itself round7/certify7.py, with base round8/stage/v8e and ids t9: / h9:): turn\n'
     'linker / reader rows (DESIGN7 section 4) into certified table deltas.'),
    ("    python -X utf8 round8/certify8.py --rows", "    python -X utf8 round9/certify9.py --rows"),
    ("(id t8:<by>:<target>:<start>, explicit 1", "(id t9:<by>:<target>:<start>, explicit 1"),
    ("(id h8:<by>:<target>:<kind>)", "(id h9:<by>:<target>:<kind>)"),
    ('BASE = os.path.join(C2, "round7", "stage", "v3")', 'BASE = os.path.join(C2, "round8", "stage", "v8e")'),
    ('hid = "h8:%d:%d:%s"', 'hid = "h9:%d:%d:%s"'),
    ('tid = "t8:%d:%d:%d"', 'tid = "t9:%d:%d:%d"'),
])
tr("round8/certify_recog8.py", "round9/certify_recog9.py", [
    ("# round 8 (agent `infra`): copy of round7/agents/queue/certify_recog.py (= round5/recog/certify_recog.py, paths\n"
     "# only); only paths changed again. recog_common is round 5's (imported from round5/recog); the live tables are the\n"
     "# round-8 base build round7/stage/v3; answers, output, items and the pack index are named on the command line.",
     "# round 9 (agent `infra9`): copy of round8/certify_recog8.py with the base changed to round8/stage/v8e (nothing else).\n"
     "# round 8 (agent `infra`): copy of round7/agents/queue/certify_recog.py (= round5/recog/certify_recog.py, paths\n"
     "# only); only paths changed again. recog_common is round 5's (imported from round5/recog); the live tables are the\n"
     "# round-9 base build round8/stage/v8e; answers, output, items and the pack index are named on the command line."),
    ('R.DATA = os.path.join(C2, "round7", "stage", "v3")', 'R.DATA = os.path.join(C2, "round8", "stage", "v8e")'),
])
tr("round8/certify_opwords8.py", "round9/certify_opwords9.py", [
    ('"""Round 8 copy of round7/agents/opwords/certify_opwords7.py (agent infra; paths only: base round7/stage/v3 +\n'
     'round7/out/v3, ids t8:, answers / out / index / items named on the command line).',
     '"""Round 9 copy of round8/certify_opwords8.py (agent infra9; base round8/stage/v8e + round8/out/v8e, ids t9:).\n'
     'Round 8 copy of round7/agents/opwords/certify_opwords7.py (agent infra; paths only: base round7/stage/v3 +\n'
     'round7/out/v3, ids t8:, answers / out / index / items named on the command line).'),
    ('BASE = os.path.join(C2, "round7", "stage", "v3")', 'BASE = os.path.join(C2, "round8", "stage", "v8e")'),
    ('OUTB = os.path.join(C2, "round7", "out", "v3")', 'OUTB = os.path.join(C2, "round8", "out", "v8e")'),
    ("tid = f\"t8:{t['by']}:{t['target']}:{t['start']}\"", "tid = f\"t9:{t['by']}:{t['target']}:{t['start']}\""),
])

# ---- 2. stage9
tr("round8/stage8.py", "round9/stage9.py", [
    ('"""Round 8: build a complete data directory for one variant, without touching data/ or earlier rounds\' folders.\n'
     '(= round7/stage7.py with base round7/stage/v3, output round8/stage/<name>/, and an extensible staged-table list.)\n\n'
     '    python -X utf8 round8/stage8.py <name>',
     '"""Round 9: build a complete data directory for one variant, without touching data/ or earlier rounds\' folders.\n'
     '(= round8/stage8.py with base round8/stage/v8e, output round9/stage/<name>/, EXTRA_TABLES history_bridge +\n'
     'part_zone; round8/stage8.py = round7/stage7.py with an extensible staged-table list.)\n\n'
     '    python -X utf8 round9/stage9.py <name>'),
    ("Base = round7/stage/v3 (the frozen round-7 build, which contains rounds 5 and 6; DESIGN8 D8-1). Output:\n"
     "round8/stage/<name>/ with",
     "Base = round8/stage/v8e (the frozen round-8 build, which contains rounds 5-7; DESIGN9 D9-1). Output:\n"
     "round9/stage/<name>/ with"),
    ("wsl/r8_run.sh copies exactly these", "wsl/r9_run.sh copies exactly these"),
    ("--delta DIR     a folder written by round7/certify7.py,", "--delta DIR     a folder written by round9/certify9.py, round7/certify7.py,"),
    ("Writes round8/stage/<name>/MANIFEST.txt", "Writes round9/stage/<name>/MANIFEST.txt"),
    ('BASE = os.path.join(C2, "round7", "stage", "v3")', 'BASE = os.path.join(C2, "round8", "stage", "v8e")'),
    ("# Round 8: tables a round-8 Lean rule may add. List a new table HERE (one place); stage8 stages it from\n"
     "# `<name>_delta.tsv` files and lists it in TABLES.txt, and wsl/r8_run.sh copies whatever TABLES.txt lists.\n"
     'EXTRA_TABLES = ["history_bridge"]  # D8-3 (orderdock, 14 Nov): DESIGN8 section 4',
     "# Round 8/9: tables a Lean rule may add. List a new table HERE (one place); stage9 stages it from\n"
     "# `<name>_delta.tsv` files and lists it in TABLES.txt, and wsl/r9_run.sh copies whatever TABLES.txt lists.\n"
     "# history_bridge: D8-3 (in the v8e base). part_zone: DESIGN9 section 4 (node, z_start, z_end, part, src); absent\n"
     "# or empty => not written (round-8 mode by presence).\n"
     'EXTRA_TABLES = ["history_bridge", "part_zone"]\n'
     'XCOL = {"part_zone": 5}  # round 9: lines of an extra table with another column count are reported (still staged)'),
    ('''        if add:
            self.changed[t] = True
        self.log.append("  %s (extra) +%d (same line present %d)" % (t, add, same))''',
     '''        if add:
            self.changed[t] = True
        self.log.append("  %s (extra) +%d (same line present %d)" % (t, add, same))
        if t in XCOL:
            bad = sum(1 for l in lines if l.count(b"\\t") + 1 != XCOL[t])
            if bad:
                self.log.append("  NOTE: %s: %d delta lines without %d columns (staged as given; Lean drops the "
                                "node's zones)" % (t, bad, XCOL[t]))'''),
])

# ---- 4. scoring
tr("round8/old_by_class8.py", "round9/old_by_class9.py", [
    ('"""Round 8: round7/old_by_class7.py on round-8 paths (round8/out, round8/stage, round8/results; nothing else\nchanged).',
     '"""Round 9: round8/old_by_class8.py on round-9 paths (round9/out, round9/stage, round9/results; nothing else\n'
     'changed). Round 8: round7/old_by_class7.py on round-8 paths (nothing else\nchanged).'),
    ("    python round8/old_by_class8.py <name>      (reads round8/out/<name>, round8/stage/<name>;\n"
     "                                                writes round8/results/<name>/old_by_class.json)",
     "    python round9/old_by_class9.py <name>      (reads round9/out/<name>, round9/stage/<name>;\n"
     "                                                writes round9/results/<name>/old_by_class.json)"),
])
tr("round8/summary8.py", "round9/summary9.py", [
    ('"""Round 8: one-page summary of a scored variant (round8/results/<name>/summary.txt; called by score8.sh).\n'
     '= round7/summary7.py on round-8 paths, round-8 rows (t8: / h8:) counted by verdict, plus the four new keys on h0.\n\n'
     '    python round8/summary8.py <name>\nReads only the files score8.sh wrote in round8/results/<name>/',
     '"""Round 9: one-page summary of a scored variant (round9/results/<name>/summary.txt; called by score9.sh).\n'
     '= round8/summary8.py on round-9 paths; round-8 (t8: / h8:) and round-9 (t9: / h9:) rows counted by verdict;\n'
     'Lean zone counters (part_zone) shown when present; the four round-8 keys on h0 only.\n'
     '(round 8: = round7/summary7.py on round-8 paths, plus the four new keys on h0.)\n\n'
     '    python round9/summary9.py <name>\nReads only the files score9.sh wrote in round9/results/<name>/'),
    ('L.append("round 8 variant %s: dev-side scores (results in round8/results/%s/)" % (n, n))',
     'L.append("round 9 variant %s: dev-side scores (results in round9/results/%s/)" % (n, n))'),
    ('r"anchor|joined|hclaim|class_|recognised_rows|operative_rows|doctrine|orderhead|setaside|bad_rows", k, re.I)]',
     'r"anchor|joined|hclaim|class_|recognised_rows|operative_rows|doctrine|orderhead|setaside|bad_rows|zone", k, re.I)]'),
    ('''    cv = collections.Counter()
    try:
        with open(os.path.join(O, "certs.tsv"), encoding="utf-8") as f:
            next(f)
            for line in f:
                p = line.split("\\t", 3)
                if len(p) >= 3 and (p[1].startswith("t8:") or p[1].startswith("h8:")):
                    cv["%s %s" % (p[1][:2], p[2])] += 1
    except OSError:
        pass
    if cv:
        L.append("round-8 rows by verdict: " + ", ".join("%s %d" % kv for kv in sorted(cv.items())))''',
     '''    cv = collections.Counter()
    cv9 = collections.Counter()
    try:
        with open(os.path.join(O, "certs.tsv"), encoding="utf-8") as f:
            next(f)
            for line in f:
                p = line.split("\\t", 3)
                if len(p) >= 3 and (p[1].startswith("t8:") or p[1].startswith("h8:")):
                    cv["%s %s" % (p[1][:2], p[2])] += 1
                elif len(p) >= 3 and (p[1].startswith("t9:") or p[1].startswith("h9:")):
                    cv9["%s %s" % (p[1][:2], p[2])] += 1
    except OSError:
        pass
    if cv:
        L.append("round-8 rows by verdict: " + ", ".join("%s %d" % kv for kv in sorted(cv.items())))
    L.append("round-9 rows by verdict: " + (", ".join("%s %d" % kv for kv in sorted(cv9.items())) or "none"))'''),
])
tr("round8/score8.sh", "round9/score9.sh", [
    ("# round 8: every DEV-side score for one variant + the four new keys on h0.   usage: bash round8/score8.sh <name> [beh] [noold] [nobench]\n"
     "#   reads round8/out/<name>/ (Lean output, wsl/r8_run.sh) and round8/stage/<name>/ (its data folder, stage8.py);\n"
     "#   writes round8/results/<name>/ and a one-page summary.txt there (round8/summary8.py).",
     "# round 9: every DEV-side score for one variant + the four round-8 keys on h0.   usage: bash round9/score9.sh <name> [beh] [noold] [nobench]\n"
     "#   reads round9/out/<name>/ (Lean output, wsl/r9_run.sh) and round9/stage/<name>/ (its data folder, stage9.py);\n"
     "#   writes round9/results/<name>/ and a one-page summary.txt there (round9/summary9.py).\n"
     "#   = round8/score8.sh on round-9 paths (agent infra9); the h0 scorer is still round8/bench_h0/score_h0.py."),
    ("# never the round-7 time split (round7/heldout/). The sealed halves are scored once, by the lead, after\n"
     "# round8/FREEZE.md (round8/score_sealed8.sh).",
     "# never the round-7 time split (round7/heldout/), never a round-9 fresh key. The sealed halves are scored once, by\n"
     "# the lead, after round9/FREEZE.md (round9/score_sealed9.sh)."),
    ('echo "usage: score8.sh <name>', 'echo "usage: score9.sh <name>'),
    ('OUT="$C2/round8/out/$N"; DATA="$C2/round8/stage/$N"', 'OUT="$C2/round9/out/$N"; DATA="$C2/round9/stage/$N"'),
    ('R="$C2/round8/results/$N"', 'R="$C2/round9/results/$N"'),
    ('L="r8_$N"', 'L="r9_$N"'),
    ("(round7/score_fresh7.py --out round8/results/<name>/fresh7)", "(round7/score_fresh7.py --out round9/results/<name>/fresh7)"),
    ("python round8/old_by_class8.py", "python round9/old_by_class9.py"),
    ("--res round-8 paths ->", "--res round-9 paths ->"),
    ("python round8/summary8.py", "python round9/summary9.py"),
])
