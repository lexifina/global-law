"""infra10: derive the round-10 tools from the round-9 files by exact replacements (round-9 files are only read).

    python -X utf8 round10/agents/infra10/mk_round10.py

Each replacement must occur exactly the stated number of times (default once) in the round-9 source.
"""
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
    p = os.path.join(C2, dst)
    open(p, "wb").write(s.encode("utf-8"))
    print("written", dst)


# ---- 1. certifiers
tr("round9/certify9.py", "round10/certify10.py", [
    ('"""Round 9 (= round8/certify8.py, itself round7/certify7.py, with base round8/stage/v8e and ids t9: / h9:): turn\n'
     'linker / reader rows (DESIGN7 section 4) into certified table deltas.',
     '"""Round 10 (= round9/certify9.py with base round9/stage/v9c and ids t10: / h10:; round 9 = round8/certify8.py,\n'
     'itself round7/certify7.py): turn linker / reader rows (DESIGN7 section 4) into certified table deltas.'),
    ("    python -X utf8 round9/certify9.py --rows", "    python -X utf8 round10/certify10.py --rows"),
    ("                                      [--no-base-skip]", "                                        [--no-base-skip]"),
    ("(id t9:<by>:<target>:<start>, explicit 1", "(id t10:<by>:<target>:<start>, explicit 1"),
    ("(id h9:<by>:<target>:<kind>)", "(id h10:<by>:<target>:<kind>)"),
    ('BASE = os.path.join(C2, "round8", "stage", "v8e")', 'BASE = os.path.join(C2, "round9", "stage", "v9c")'),
    ('hid = "h9:%d:%d:%s"', 'hid = "h10:%d:%d:%s"'),
    ('tid = "t9:%d:%d:%d"', 'tid = "t10:%d:%d:%d"'),
])
# round 9's claims joinedFar / implicitReject (DESIGN9 sections 5 and 7, in the v9c Lean) were certified with state9's
# copy round9/agents/state9/certify9_claims.py (round9/certify9.py does not know them): same port for round 10.
tr("round9/agents/state9/certify9_claims.py", "round10/certify10_claims.py", [
    ("# state9 (round 9): copy of round9/certify9.py with the two claims",
     "# round 10 (agent infra10): round9/agents/state9/certify9_claims.py with base round9/stage/v9c, ids t10: / h10:,\n"
     "# C2 = the parent of round10/ (nothing else changed); for rows with claim joinedFar or implicitReject.\n"
     "# state9 (round 9): copy of round9/certify9.py with the two claims"),
    ("    python -X utf8 round9/certify9.py --rows", "    python -X utf8 round10/certify10_claims.py --rows"),
    ("(id t9:<by>:<target>:<start>, explicit 1", "(id t10:<by>:<target>:<start>, explicit 1"),
    ("(id h9:<by>:<target>:<kind>)", "(id h10:<by>:<target>:<kind>)"),
    ('C2 = os.path.normpath(os.path.join(HERE, "..", "..", ".."))', 'C2 = os.path.dirname(HERE)'),
    ('BASE = os.path.join(C2, "round8", "stage", "v8e")', 'BASE = os.path.join(C2, "round9", "stage", "v9c")'),
    ('hid = "h9:%d:%d:%s"', 'hid = "h10:%d:%d:%s"'),
    ('tid = "t9:%d:%d:%d"', 'tid = "t10:%d:%d:%d"'),
])
tr("round9/certify_recog9.py", "round10/certify_recog10.py", [
    ("# round 9 (agent `infra9`): copy of round8/certify_recog8.py with the base changed to round8/stage/v8e (nothing else).\n",
     "# round 10 (agent `infra10`): copy of round9/certify_recog9.py with the base changed to round9/stage/v9c (nothing else).\n"
     "# round 9 (agent `infra9`): copy of round8/certify_recog8.py with the base changed to round8/stage/v8e (nothing else).\n"),
    ("# round-9 base build round8/stage/v8e; answers,", "# round-10 base build round9/stage/v9c; answers,"),
    ('R.DATA = os.path.join(C2, "round8", "stage", "v8e")', 'R.DATA = os.path.join(C2, "round9", "stage", "v9c")'),
])
tr("round9/certify_opwords9.py", "round10/certify_opwords10.py", [
    ('"""Round 9 copy of round8/certify_opwords8.py (agent infra9; base round8/stage/v8e + round8/out/v8e, ids t9:).\n',
     '"""Round 10 copy of round9/certify_opwords9.py (agent infra10; base round9/stage/v9c + round9/out/v9c, ids t10:).\n'
     'Round 9 copy of round8/certify_opwords8.py (agent infra9; base round8/stage/v8e + round8/out/v8e, ids t9:).\n'),
    ('BASE = os.path.join(C2, "round8", "stage", "v8e")', 'BASE = os.path.join(C2, "round9", "stage", "v9c")'),
    ('OUTB = os.path.join(C2, "round8", "out", "v8e")', 'OUTB = os.path.join(C2, "round9", "out", "v9c")'),
    ("tid = f\"t9:{t['by']}:{t['target']}:{t['start']}\"", "tid = f\"t10:{t['by']}:{t['target']}:{t['start']}\""),
])

# ---- 2. stage10
tr("round9/stage9.py", "round10/stage10.py", [
    ('"""Round 9: build a complete data directory for one variant, without touching data/ or earlier rounds\' folders.\n'
     '(= round8/stage8.py with base round8/stage/v8e, output round9/stage/<name>/, EXTRA_TABLES history_bridge +\n'
     'part_zone; round8/stage8.py = round7/stage7.py with an extensible staged-table list.)\n\n'
     '    python -X utf8 round9/stage9.py <name>',
     '"""Round 10: build a complete data directory for one variant, without touching data/ or earlier rounds\' folders.\n'
     '(= round9/stage9.py with base round9/stage/v9c, output round10/stage/<name>/, EXTRA_TABLES history_bridge +\n'
     'part_zone + history_remand (DESIGN10 section 4), adoption / succession listed in TABLES.txt, and part zones added\n'
     'for the acting text nodes of staged rows that have none (round10/zones10.py, calpart9\'s builder);\n'
     'round9/stage9.py = round8/stage8.py with --table; round8/stage8.py = round7/stage7.py with extra tables.)\n\n'
     '    python -X utf8 round10/stage10.py <name>'),
    ("                                    [--replace FILE ...] [--claims FILE ...] [--keep-ids FILE] [--force-write]\n"
     "                                    [--extra-table NAME ...]",
     "                                      [--replace FILE ...] [--claims FILE ...] [--keep-ids FILE] [--force-write]\n"
     "                                      [--extra-table NAME ...] [--table NAME=FILE ...] [--no-zones] [--procs N]"),
    ("Base = round8/stage/v8e (the frozen round-8 build, which contains rounds 5-7; DESIGN9 D9-1). Output:\n"
     "round9/stage/<name>/ with",
     "Base = round9/stage/v9c (the frozen round-9 build, which contains rounds 5-9; DESIGN10 D10-1), used in place,\n"
     "read-only. Output: round10/stage/<name>/ with"),
    ("wsl/r9_run.sh copies exactly these", "wsl/r10_run.sh copies exactly these"),
    ("--delta DIR     a folder written by round9/certify9.py, round7/certify7.py,",
     "--delta DIR     a folder written by round10/certify10.py, round9/certify9.py, round7/certify7.py,"),
    ("FILE (non-empty, LF only), listed in TABLES.txt (how = table) so wsl/r9_run.sh copies it and freeze9.py",
     "FILE (non-empty, LF only), listed in TABLES.txt (how = table) so wsl/r10_run.sh copies it and freeze10.py"),
    ("Writes round9/stage/<name>/MANIFEST.txt with counts and sha1 of the staged tables.\nNo answer-key file is read.",
     "Writes round10/stage/<name>/MANIFEST.txt with counts and sha1 of the staged tables.\n"
     "Round 10 additions:\n"
     "  - part zones (DESIGN9 section 4, v9c's part_zone.tsv covers every round-9 row): after remove / deltas / claims /\n"
     "    replace / drop, every staged row's acting text node (treatments: `by`, or the witness node; history: `by` when\n"
     "    decisions2's text_sha of `by` equals the row's, else `target`) that has no part_zone line gets its zone lines\n"
     "    from round10/zones10.py (= round9/agents/calpart9/build_zones.py's per-node builder, same rules, same line\n"
     "    format). --no-zones skips this (logged). --procs N (default 8) for the zone builder.\n"
     "  - adoption / succession (v9c's New Jersey tables) are listed in TABLES.txt (how = base, or table with --table).\n"
     "No answer-key file is read."),
    ('BASE = os.path.join(C2, "round8", "stage", "v8e")', 'BASE = os.path.join(C2, "round9", "stage", "v9c")'),
    ("# Round 8/9: tables a Lean rule may add. List a new table HERE (one place); stage9 stages it from\n"
     "# `<name>_delta.tsv` files and lists it in TABLES.txt, and wsl/r9_run.sh copies whatever TABLES.txt lists.\n",
     "# Round 8/9/10: tables a Lean rule may add. List a new table HERE (one place); stage10 stages it from\n"
     "# `<name>_delta.tsv` files and lists it in TABLES.txt, and wsl/r10_run.sh copies whatever TABLES.txt lists.\n"
     "# history_remand: DESIGN10 section 4 (id, b_node, b_start, b_end, docket); absent or empty => not written\n"
     "# (round-9 mode by presence).\n"),
    ('EXTRA_TABLES = ["history_bridge", "part_zone"]\n'
     'XCOL = {"part_zone": 5}  # round 9: lines of an extra table with another column count are reported (still staged)',
     'EXTRA_TABLES = ["history_bridge", "part_zone", "history_remand"]\n'
     'XCOL = {"part_zone": 5, "history_remand": 5}  # lines of an extra table with another column count are reported\n'
     '# round 10: base non-row tables listed in TABLES.txt (hard links, how = base) so r10_run.sh / freeze10.py see them\n'
     'LISTED = ["adoption", "succession"]'),
    ('                self.log.append("  NOTE: %s: %d delta lines without %d columns (staged as given; Lean drops the "\n'
     '                                "node\'s zones)" % (t, bad, XCOL[t]))',
     '                self.log.append("  NOTE: %s: %d delta lines without %d columns (staged as given; Lean ignores / "\n'
     '                                "counts them)" % (t, bad, XCOL[t]))'),
    ('    ap.add_argument("--base", default=BASE, help=argparse.SUPPRESS)\n',
     '    ap.add_argument("--base", default=BASE, help=argparse.SUPPRESS)\n'
     '    ap.add_argument("--no-zones", action="store_true", help="round 10: do not add part zones for new rows\' nodes")\n'
     '    ap.add_argument("--procs", type=int, default=8, help="round 10: processes of the zone builder")\n'),
    ('    amb = sum(1 for v in S.ci.values() if len(v) > 1)\n',
     '    # round 10: part zones for the acting text nodes of staged rows that have none (zones10.py)\n'
     '    if a.no_zones:\n'
     '        log.append("part zones: --no-zones (not checked, none added)")\n'
     '    else:\n'
     '        import zones10\n'
     '        zl, zinfo = zones10.missing_zone_lines(S.tabs, os.path.join(a.base, "decisions2.tsv"), procs=a.procs)\n'
     '        log.append("part zones: " + zinfo)\n'
     '        if zl:\n'
     '            S.add_extra("part_zone", zl)\n'
     '    amb = sum(1 for v in S.ci.values() if len(v) > 1)\n'),
    ('''    n = 0
    for fn in sorted(os.listdir(a.base)):''',
     '''    for t in LISTED:  # round 10: v9c's adoption / succession are listed (how = base) unless --table replaced them
        bp = os.path.join(a.base, t + ".tsv")
        if t in repl or not os.path.exists(bp):
            continue
        p = os.path.join(out, t + ".tsv")
        if os.path.exists(p) and not os.path.samefile(p, bp):
            os.remove(p)
        if not os.path.exists(p):
            os.link(bp, p)
        h = sha1_file(p)
        rows = len(read_lines(p))
        log.append("%s.tsv\\t%d rows\\tsha1 %s\\tbase (hard link, listed)" % (t, rows, h))
        tables.append((t, rows, h, "base"))
    n = 0
    for fn in sorted(os.listdir(a.base)):'''),
])

# ---- 4. scoring
tr("round9/old_by_class9.py", "round10/old_by_class10.py", [
    ('"""Round 9: round8/old_by_class8.py on round-9 paths (round9/out, round9/stage, round9/results; nothing else\n'
     'changed).',
     '"""Round 10: round9/old_by_class9.py on round-10 paths (round10/out, round10/stage, round10/results; nothing else\n'
     'changed). Round 9: round8/old_by_class8.py on round-9 paths (nothing else\nchanged).'),
    ("    python round9/old_by_class9.py <name>      (reads round9/out/<name>, round9/stage/<name>;\n"
     "                                                writes round9/results/<name>/old_by_class.json)",
     "    python round10/old_by_class10.py <name>    (reads round10/out/<name>, round10/stage/<name>;\n"
     "                                                writes round10/results/<name>/old_by_class.json)"),
])
tr("round9/summary9.py", "round10/summary10.py", [
    ('"""Round 9: one-page summary of a scored variant (round9/results/<name>/summary.txt; called by score9.sh).\n'
     '= round8/summary8.py on round-9 paths; round-8 (t8: / h8:) and round-9 (t9: / h9:) rows counted by verdict;\n'
     'Lean zone counters (part_zone) shown when present; the four round-8 keys on h0 only.\n',
     '"""Round 10: one-page summary of a scored variant (round10/results/<name>/summary.txt; called by score10.sh).\n'
     '= round9/summary9.py on round-10 paths; round-8, round-9 and round-10 (t10: / h10:) rows counted by verdict;\n'
     'Lean zone and remand counters shown when present; the four round-8 keys on h0 only.\n'
     '(round 9: = round8/summary8.py on round-9 paths, zone counters.)\n'),
    ('    python round9/summary9.py <name>\nReads only the files score9.sh wrote in round9/results/<name>/',
     '    python round10/summary10.py <name>\nReads only the files score10.sh wrote in round10/results/<name>/'),
    ('L.append("round 9 variant %s: dev-side scores (results in round9/results/%s/)" % (n, n))',
     'L.append("round 10 variant %s: dev-side scores (results in round10/results/%s/)" % (n, n))'),
    ('r"anchor|joined|hclaim|class_|recognised_rows|operative_rows|doctrine|orderhead|setaside|bad_rows|zone", k, re.I)]',
     'r"anchor|joined|hclaim|class_|recognised_rows|operative_rows|doctrine|orderhead|setaside|bad_rows|zone|remand", k,\n'
     '        re.I)]'),
    ('''    cv9 = collections.Counter()
''', '''    cv9 = collections.Counter()
    cv10 = collections.Counter()
'''),
    ('''                elif len(p) >= 3 and (p[1].startswith("t9:") or p[1].startswith("h9:")):
                    cv9["%s %s" % (p[1][:2], p[2])] += 1
''', '''                elif len(p) >= 3 and (p[1].startswith("t9:") or p[1].startswith("h9:")):
                    cv9["%s %s" % (p[1][:2], p[2])] += 1
                elif len(p) >= 3 and (p[1].startswith("t10:") or p[1].startswith("h10:")):
                    cv10["%s %s" % (p[1][:3], p[2])] += 1
'''),
    ('''    L.append("round-9 rows by verdict: " + (", ".join("%s %d" % kv for kv in sorted(cv9.items())) or "none"))
''', '''    L.append("round-9 rows by verdict: " + (", ".join("%s %d" % kv for kv in sorted(cv9.items())) or "none"))
    L.append("round-10 rows by verdict: " + (", ".join("%s %d" % kv for kv in sorted(cv10.items())) or "none"))
'''),
])
tr("round9/score9.sh", "round10/score10.sh", [
    ("# round 9: every DEV-side score for one variant + the four round-8 keys on h0.   usage: bash round9/score9.sh <name> [beh] [noold] [nobench]\n"
     "#   reads round9/out/<name>/ (Lean output, wsl/r9_run.sh) and round9/stage/<name>/ (its data folder, stage9.py);\n"
     "#   writes round9/results/<name>/ and a one-page summary.txt there (round9/summary9.py).\n"
     "#   = round8/score8.sh on round-9 paths (agent infra9); the h0 scorer is still round8/bench_h0/score_h0.py.",
     "# round 10: every DEV-side score for one variant + the four round-8 keys on h0.   usage: bash round10/score10.sh <name> [beh] [noold] [nobench]\n"
     "#   reads round10/out/<name>/ (Lean output, wsl/r10_run.sh) and round10/stage/<name>/ (its data folder, stage10.py);\n"
     "#   writes round10/results/<name>/ and a one-page summary.txt there (round10/summary10.py).\n"
     "#   = round9/score9.sh on round-10 paths (agent infra10); the h0 scorer is still round8/bench_h0/score_h0.py,\n"
     "#   which scores only the four round-8 keys (fjc_idb_appeals, shadow_docket, scdb_disposition,\n"
     "#   state_overruled_tables) and only their h0 half."),
    ("# never the round-7 time split (round7/heldout/), never a round-9 fresh key. The sealed halves are scored once, by\n"
     "# the lead, after round9/FREEZE.md (round9/score_sealed9.sh).",
     "# never the round-7 time split (round7/heldout/), never the round-9 keys (Songer / Brace & Hall), never a round-10\n"
     "# fresh key. The sealed halves are scored once, by the lead, after round10/FREEZE.md (round10/score_sealed10.sh)."),
    ('echo "usage: score9.sh <name>', 'echo "usage: score10.sh <name>'),
    ('OUT="$C2/round9/out/$N"; DATA="$C2/round9/stage/$N"', 'OUT="$C2/round10/out/$N"; DATA="$C2/round10/stage/$N"'),
    ('R="$C2/round9/results/$N"', 'R="$C2/round10/results/$N"'),
    ('L="r9_$N"', 'L="r10_$N"'),
    ("(round7/score_fresh7.py --out round9/results/<name>/fresh7)", "(round7/score_fresh7.py --out round10/results/<name>/fresh7)"),
    ("python round9/old_by_class9.py", "python round10/old_by_class10.py"),
    ("--res round-9 paths ->", "--res round-10 paths ->"),
    ("python round9/summary9.py", "python round10/summary10.py"),
])
