"""infra11: derive the round-11 tools from the round-10 files by exact replacements (round-10 files are only read).

    python -X utf8 round11/agents/infra11/mk_round11.py

Each replacement in `tr` must occur exactly the stated number of times (default once) in the round-10 source;
`gl` replacements are global and must occur at least once. The §4 node overlay (--nodes) is added afterwards to
round11/stage11.py, zones11.py, certify11.py by hand edits (see NOTES.md), so re-running this overwrites them:
run it only before Part B.
"""
import os
import sys

C2 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def tr(src, dst, reps, glob=(), post=()):
    s = open(os.path.join(C2, src), "rb").read().decode("utf-8")
    assert "\r" not in s, src
    for r in reps:
        a, b = r[0], r[1]
        n = r[2] if len(r) > 2 else 1
        assert s.count(a) == n, (src, a[:80], s.count(a), n)
        s = s.replace(a, b)
    for a, b in list(glob) + list(post):  # post: fix-ups of what a global replacement over-replaced
        assert s.count(a) >= 1, (src, "glob", a)
        s = s.replace(a, b)
    p = os.path.join(C2, dst)
    if os.path.exists(p) and "--force" not in sys.argv:
        print("exists, kept (use --force):", dst)
        return
    open(p, "wb").write(s.encode("utf-8"))
    print("written", dst)


BASE10 = ('BASE = os.path.join(C2, "round9", "stage", "v9c")', 'BASE = os.path.join(C2, "round10", "stage", "v10d")')

# ---- 1. certifiers
tr("round10/certify10.py", "round11/certify11.py", [
    ('"""Round 10 (= round9/certify9.py with base round9/stage/v9c and ids t10: / h10:; round 9 = round8/certify8.py,\n'
     'itself round7/certify7.py): turn',
     '"""Round 11 (= round10/certify10.py with base round10/stage/v10d and ids t11: / h11:; round 10 = round9/certify9.py,\n'
     'round 9 = round8/certify8.py, itself round7/certify7.py): turn'),
    ("    python -X utf8 round10/certify10.py --rows", "    python -X utf8 round11/certify11.py --rows"),
    ("(id t10:<by>:<target>:<start>, explicit 1", "(id t11:<by>:<target>:<start>, explicit 1"),
    ("(id h10:<by>:<target>:<kind>)", "(id h11:<by>:<target>:<kind>)"),
    BASE10,
    ('hid = "h10:%d:%d:%s"', 'hid = "h11:%d:%d:%s"'),
    ('tid = "t10:%d:%d:%d"', 'tid = "t11:%d:%d:%d"'),
])
tr("round10/certify10_claims.py", "round11/certify11_claims.py", [
    ("# round 10 (agent infra10): round9/agents/state9/certify9_claims.py with base round9/stage/v9c, ids t10: / h10:,\n"
     "# C2 = the parent of round10/ (nothing else changed); for rows with claim joinedFar or implicitReject.\n",
     "# round 11 (agent infra11): round10/certify10_claims.py with base round10/stage/v10d, ids t11: / h11: (nothing else\n"
     "# changed); for rows with claim joinedFar or implicitReject.\n"
     "# round 10 (agent infra10): round9/agents/state9/certify9_claims.py with base round9/stage/v9c, ids t10: / h10:,\n"
     "# C2 = the parent of round10/ (nothing else changed); for rows with claim joinedFar or implicitReject.\n"),
    ("    python -X utf8 round10/certify10_claims.py --rows", "    python -X utf8 round11/certify11_claims.py --rows"),
    ("(id t10:<by>:<target>:<start>, explicit 1", "(id t11:<by>:<target>:<start>, explicit 1"),
    ("(id h10:<by>:<target>:<kind>)", "(id h11:<by>:<target>:<kind>)"),
    BASE10,
    ('hid = "h10:%d:%d:%s"', 'hid = "h11:%d:%d:%s"'),
    ('tid = "t10:%d:%d:%d"', 'tid = "t11:%d:%d:%d"'),
])
tr("round10/certify_recog10.py", "round11/certify_recog11.py", [
    ("# round 10 (agent `infra10`): copy of round9/certify_recog9.py with the base changed to round9/stage/v9c (nothing else).\n",
     "# round 11 (agent `infra11`): copy of round10/certify_recog10.py with the base changed to round10/stage/v10d (nothing else).\n"
     "# round 10 (agent `infra10`): copy of round9/certify_recog9.py with the base changed to round9/stage/v9c (nothing else).\n"),
    ("# round-10 base build round9/stage/v9c; answers,", "# round-11 base build round10/stage/v10d; answers,"),
    ('R.DATA = os.path.join(C2, "round9", "stage", "v9c")', 'R.DATA = os.path.join(C2, "round10", "stage", "v10d")'),
])
tr("round10/certify_opwords10.py", "round11/certify_opwords11.py", [
    ('"""Round 10 copy of round9/certify_opwords9.py (agent infra10; base round9/stage/v9c + round9/out/v9c, ids t10:).\n',
     '"""Round 11 copy of round10/certify_opwords10.py (agent infra11; base round10/stage/v10d + round10/out/v10d, ids t11:).\n'
     'Round 10 copy of round9/certify_opwords9.py (agent infra10; base round9/stage/v9c + round9/out/v9c, ids t10:).\n'),
    BASE10,
    ('OUTB = os.path.join(C2, "round9", "out", "v9c")', 'OUTB = os.path.join(C2, "round10", "out", "v10d")'),
    ("tid = f\"t10:{t['by']}:{t['target']}:{t['start']}\"", "tid = f\"t11:{t['by']}:{t['target']}:{t['start']}\""),
])

# ---- 2. stage11 (from the lead-patched stage10.py) + zones11
tr("round10/stage10.py", "round11/stage11.py", [
    ('"""Round 10: build a complete data directory for one variant, without touching data/ or earlier rounds\' folders.\n',
     '"""Round 11: build a complete data directory for one variant, without touching data/ or earlier rounds\' folders.\n'
     '(= round10/stage10.py as patched by the round-10 lead (history_remand 12 columns, history_tbridge) with base\n'
     'round10/stage/v10d, output round11/stage/<name>/, zones from round11/zones11.py; agent infra11.)\n'),
    ("    python -X utf8 round10/stage10.py <name>", "    python -X utf8 round11/stage11.py <name>"),
    ("Base = round9/stage/v9c (the frozen round-9 build, which contains rounds 5-9; DESIGN10 D10-1), used in place,\n"
     "read-only. Output: round10/stage/<name>/ with",
     "Base = round10/stage/v10d (the frozen round-10 build, which contains rounds 5-10; DESIGN11 D11-1), used in place,\n"
     "read-only. Output: round11/stage/<name>/ with"),
    ("wsl/r10_run.sh copies exactly these", "wsl/r11_run.sh copies exactly these"),
    ("--delta DIR     a folder written by round10/certify10.py,", "--delta DIR     a folder written by round11/certify11.py, round10/certify10.py,"),
    ("so wsl/r10_run.sh copies it and freeze10.py", "so wsl/r11_run.sh copies it and freeze11.py"),
    ("Writes round10/stage/<name>/MANIFEST.txt", "Writes round11/stage/<name>/MANIFEST.txt"),
    ("    from round10/zones10.py (= round9", "    from round11/zones11.py (= round10/zones10.py = round9"),
    BASE10,
    ("    # round 10: part zones for the acting text nodes of staged rows that have none (zones10.py)\n",
     "    # round 10: part zones for the acting text nodes of staged rows that have none (zones11.py = zones10.py)\n"),
    ("        import zones10\n        zl, zinfo = zones10.missing_zone_lines(",
     "        import zones11\n        zl, zinfo = zones11.missing_zone_lines("),
])
tr("round10/zones10.py", "round11/zones11.py", [
    ('"""Round 10 (agent infra10): part-zone lines',
     '"""Round 11 (agent infra11): round10/zones10.py with the base round10/stage/v10d (check-stage, self-test); builder\n'
     'unchanged. Round 10 (agent infra10): part-zone lines'),
    ("    python -X utf8 round10/zones10.py --check-stage round10/stage/<name>",
     "    python -X utf8 round11/zones11.py --check-stage round11/stage/<name>"),
    ("    python -X utf8 round10/zones10.py --selftest", "    python -X utf8 round11/zones11.py --selftest"),
    ("        rebuild the zone lines of K random (seed 10) or all nodes of round9/stage/v9c/part_zone.tsv",
     "        rebuild the zone lines of K random (seed 10) or all nodes of round10/stage/v10d/part_zone.tsv"),
    ("        and compare them byte for byte (per node, in order) with v9c's lines.",
     "        and compare them byte for byte (per node, in order) with v10d's lines."),
    ('V9C = os.path.join(C2, "round9", "stage", "v9c")', 'V9C = os.path.join(C2, "round10", "stage", "v10d")  # round 11: the base v10d'),
    ('print("zones10 selftest: %d v9c nodes rebuilt', 'print("zones11 selftest: %d v10d nodes rebuilt'),
])

# ---- 4. scoring
tr("round10/old_by_class10.py", "round11/old_by_class11.py", [
    ('"""Round 10: round9/old_by_class9.py on round-10 paths (round10/out, round10/stage, round10/results; nothing else\n'
     'changed).',
     '"""Round 11: round10/old_by_class10.py on round-11 paths (round11/out, round11/stage, round11/results; nothing else\n'
     'changed). Round 10: round9/old_by_class9.py on round-10 paths (nothing else\nchanged).'),
    ("    python round10/old_by_class10.py <name>    (reads round10/out/<name>, round10/stage/<name>;\n"
     "                                                writes round10/results/<name>/old_by_class.json)",
     "    python round11/old_by_class11.py <name>    (reads round11/out/<name>, round11/stage/<name>;\n"
     "                                                writes round11/results/<name>/old_by_class.json)"),
])
tr("round10/summary10.py", "round11/summary11.py", [
    ('"""Round 10: one-page summary of a scored variant (round10/results/<name>/summary.txt; called by score10.sh).\n',
     '"""Round 11: one-page summary of a scored variant (round11/results/<name>/summary.txt; called by score11.sh).\n'
     '= round10/summary10.py on round-11 paths; round-11 rows (t11: / h11:) counted by verdict too.\n'
     'Round 10: one-page summary of a scored variant (round10/results/<name>/summary.txt; called by score10.sh).\n'),
    ('    python round10/summary10.py <name>\nReads only the files score10.sh wrote in round10/results/<name>/',
     '    python round11/summary11.py <name>\nReads only the files score11.sh wrote in round11/results/<name>/'),
    ('L.append("round 10 variant %s: dev-side scores (results in round10/results/%s/)" % (n, n))',
     'L.append("round 11 variant %s: dev-side scores (results in round11/results/%s/)" % (n, n))'),
    ('''    cv10 = collections.Counter()
''', '''    cv10 = collections.Counter()
    cv11 = collections.Counter()
'''),
    ('''                    cv10["%s %s" % (p[1][:3], p[2])] += 1
''', '''                    cv10["%s %s" % (p[1][:3], p[2])] += 1
                elif len(p) >= 3 and (p[1].startswith("t11:") or p[1].startswith("h11:")):
                    cv11["%s %s" % (p[1][:3], p[2])] += 1
'''),
    ('''    L.append("round-10 rows by verdict: " + (", ".join("%s %d" % kv for kv in sorted(cv10.items())) or "none"))
''', '''    L.append("round-10 rows by verdict: " + (", ".join("%s %d" % kv for kv in sorted(cv10.items())) or "none"))
    L.append("round-11 rows by verdict: " + (", ".join("%s %d" % kv for kv in sorted(cv11.items())) or "none"))
'''),
])
tr("round10/score10.sh", "round11/score11.sh", [
    ("# round 10: every DEV-side score for one variant + the four round-8 keys on h0.   usage: bash round10/score10.sh <name> [beh] [noold] [nobench]\n"
     "#   reads round10/out/<name>/ (Lean output, wsl/r10_run.sh) and round10/stage/<name>/ (its data folder, stage10.py);\n"
     "#   writes round10/results/<name>/ and a one-page summary.txt there (round10/summary10.py).\n"
     "#   = round9/score9.sh on round-10 paths (agent infra10);",
     "# round 11: every DEV-side score for one variant + the four round-8 keys on h0.   usage: bash round11/score11.sh <name> [beh] [noold] [nobench]\n"
     "#   reads round11/out/<name>/ (Lean output, wsl/r11_run.sh) and round11/stage/<name>/ (its data folder, stage11.py);\n"
     "#   writes round11/results/<name>/ and a one-page summary.txt there (round11/summary11.py).\n"
     "#   = round10/score10.sh on round-11 paths (agent infra11; round10/score10.sh = round9/score9.sh on round-10 paths);"),
    ("# never the round-7 time split (round7/heldout/), never the round-9 keys (Songer / Brace & Hall), never a round-10\n"
     "# fresh key. The sealed halves are scored once, by the lead, after round10/FREEZE.md (round10/score_sealed10.sh).",
     "# never the round-7 time split (round7/heldout/), never the closed keys (Songer, Brace & Hall, Federal Circuit),\n"
     "# never a round-10 or round-11 fresh key. The sealed halves are scored once, by the lead, after round11/FREEZE.md\n"
     "# (round11/score_sealed11.sh)."),
    ('echo "usage: score10.sh <name>', 'echo "usage: score11.sh <name>'),
    ('OUT="$C2/round10/out/$N"; DATA="$C2/round10/stage/$N"', 'OUT="$C2/round11/out/$N"; DATA="$C2/round11/stage/$N"'),
    ('R="$C2/round10/results/$N"', 'R="$C2/round11/results/$N"'),
    ('L="r10_$N"', 'L="r11_$N"'),
    ("(round7/score_fresh7.py --out round10/results/<name>/fresh7)", "(round7/score_fresh7.py --out round11/results/<name>/fresh7)"),
    ("python round10/old_by_class10.py", "python round11/old_by_class11.py"),
    ("--res round-10 paths ->", "--res round-11 paths ->"),
    ("python round10/summary10.py", "python round11/summary11.py"),
])

# ---- 3. run / clean scripts (global replacements; reviewed by diff, see NOTES.md)
tr("wsl/r10_clean.sh", "wsl/r11_clean.sh", [
    ("# round 10 (agent infra10): WSL side of round10/clean10.sh",
     "# round 11 (agent infra11; = wsl/r10_clean.sh on round-11 names): WSL side of round11/clean11.sh"),
], glob=[("r10_", "r11_")])
tr("round10/clean10.sh", "round11/clean11.sh", [
    ("# round 10 (agent infra10): delete one variant's intermediates.",
     "# round 11 (agent infra11; = round10/clean10.sh on round-11 paths): delete one variant's intermediates."),
    ("#   round9/stage/v9c lose only this directory entry", "#   round10/stage/v10d lose only this directory entry"),
], glob=[("round10/", "round11/"), ("r10_", "r11_"), ("clean10.sh", "clean11.sh"), ("R10BIN", "R11BIN")])

# ---- 3b. the run script (r10_run.sh -> r11_run.sh): specific replacements first, then global names
tr("wsl/r10_run.sh", "wsl/r11_run.sh", [
    ("# round 10 (agent infra10; = wsl/r9_run.sh on round-10 paths, base v9c): run the Lean runner",
     "# round 11 (agent infra11; = wsl/r10_run.sh on round-11 paths, base v10d, frozen round-10 binary): run the Lean runner"),
    ("#   NOBUILD=1 r10_run.sh <name>        no sync, no build: runs the FROZEN round-9 checker\n"
     "#                                      ~/caselaw2/r10_bin/caselaw2_r9v9c (a copy of ~/caselaw2/r9_bin/run_v9c, the\n"
     "#                                      binary of the round-9 frozen run v9c (round9/out/v9c/RUN.txt, round9/FREEZE.md),\n"
     "#                                      sha1 22bab5cdc71237876c807a8c9354cad7a47c6e1f; checked before each run), so a\n"
     "#                                      build by `lean10` cannot change it mid-round. Allowed without LEAN_READY.",
     "#   NOBUILD=1 r11_run.sh <name>        no sync, no build: runs the FROZEN round-10 checker\n"
     "#                                      ~/caselaw2/r11_bin/caselaw2_r10v10d (a copy of ~/caselaw2/r10_bin/run_v10d, the\n"
     "#                                      binary of the round-10 frozen run v10d (round10/out/v10d/RUN.txt),\n"
     "#                                      sha1 e7e32592cc6c6393506e25dc9654d4254af218ea; checked before each run), so a\n"
     "#                                      build by `lean11` cannot change it mid-round. Allowed without LEAN_READY."),
    ("# Base mirror: base_r10_v9c/ in the mirror = round9/stage/v9c, built once from the round-9 mirror data_r9_v9c (a hard\n"
     "# link to the real file behind each of its regular files and symlinks: no table is copied, and the mirror does not\n"
     "# depend on earlier data dirs staying) and checked file by file with cmp against Windows round9/stage/v9c (marker\n"
     "# .verified, with the sha1 of every table in .sha1). The variant's data dir is data_r10_<name>: symlinks to\n"
     "# base_r10_v9c, and every table listed in round10/stage/<name>/TABLES.txt (stage10.py: the ten staged tables +\n"
     "# EXTRA_TABLES history_bridge, part_zone, history_remand + adoption, succession) put over it:",
     "# Base mirror: base_r11_v10d/ in the mirror = round10/stage/v10d, built once from the round-10 data dir data_r10_v10d\n"
     "# (a hard link to the real file behind each of its regular files and symlinks: no table is copied, and the mirror\n"
     "# does not depend on earlier data dirs staying) and checked file by file with cmp against Windows round10/stage/v10d\n"
     "# (marker .verified, with the sha1 of every table in .sha1). The variant's data dir is data_r11_<name>: symlinks to\n"
     "# base_r11_v10d, and every table listed in round11/stage/<name>/TABLES.txt (stage11.py: the ten staged tables +\n"
     "# EXTRA_TABLES history_bridge, part_zone, history_remand, history_tbridge + adoption, succession) put over it:"),
    ("# earlier-round mode). Lean output goes to Windows round10/out/<name>/ (+ RUN.txt). Same runner call as\n"
     "# wsl/r9_run.sh (asOf 20261112, 8 shards).",
     "# earlier-round mode). Lean output goes to Windows round11/out/<name>/ (+ RUN.txt). Same runner call as\n"
     "# wsl/r10_run.sh (asOf 20261112, 8 shards). Node count: round11/stage/<name>/nodes.count when present (a stage\n"
     "# with DESIGN11 section-4 order nodes, stage11.py --nodes), else ../graph/nodes.count (the corpus's)."),
    ("FROZEN=~/caselaw2/r10_bin/caselaw2_r9v9c\nFROZEN_SRC=~/caselaw2/r9_bin/run_v9c\nFROZEN_SHA=22bab5cdc71237876c807a8c9354cad7a47c6e1f",
     "FROZEN=~/caselaw2/r11_bin/caselaw2_r10v10d\nFROZEN_SRC=~/caselaw2/r10_bin/run_v10d\nFROZEN_SHA=e7e32592cc6c6393506e25dc9654d4254af218ea"),
    ("B=$M/base_r10_v9c\nWB=$W/round9/stage/v9c", "B=$M/base_r11_v10d\nWB=$W/round10/stage/v10d"),
    ("  [ -d $M/data_r9_v9c ] || { echo \"no $M/data_r9_v9c to build the base mirror from\"; exit 2; }\n"
     "  echo \"building the base mirror $B from data_r9_v9c (hard links)\"",
     "  [ -d $M/data_r10_v10d ] || { echo \"no $M/data_r10_v10d to build the base mirror from\"; exit 2; }\n"
     "  echo \"building the base mirror $B from data_r10_v10d (hard links)\""),
    ("    b=$(basename $f); m=$M/data_r9_v9c/$b", "    b=$(basename $f); m=$M/data_r10_v10d/$b"),
    ('      echo "  $b: not in data_r9_v9c or different; copied from Windows"; cp $f $B.tmp/$b',
     '      echo "  $b: not in data_r10_v10d or different; copied from Windows"; cp $f $B.tmp/$b'),
    ('    HOW="NOBUILD frozen r9v9c"', '    HOW="NOBUILD frozen r10v10d"'),
    ("(NOBUILD=1 runs the frozen round-9 binary)", "(NOBUILD=1 runs the frozen round-10 binary)"),
    (r"""  NODES=$(tr -d ' \n' < ../graph/nodes.count)
""",
     r"""  if [ -f $S/nodes.count ]; then NODES=$(tr -d ' \r\n' < $S/nodes.count); else NODES=$(tr -d ' \n' < ../graph/nodes.count); fi
  [[ "$NODES" =~ ^[0-9]+$ ]] || { echo "bad node count '$NODES'"; return 1; }
  echo "node count $NODES"
"""),
    (r"""echo "history verdicts, round-10 rows (h10:):"
awk -F'\t' '$1=="history" && $2 ~ /^h10:/""",
     r"""echo "history verdicts, round-11 rows (h11:):"
awk -F'\t' '$1=="history" && $2 ~ /^h11:/"""),
    (r"""echo "treatment verdicts, round-10 rows (t10:):"
awk -F'\t' '$1=="treatment" && $2 ~ /^t10:/""",
     r"""echo "treatment verdicts, round-11 rows (t11:):"
awk -F'\t' '$1=="treatment" && $2 ~ /^t11:/"""),
], glob=[("r10_", "r11_"), ("round10/", "round11/"), ("R10BIN", "R11BIN"), ("round-10 run", "round-11 run")],
   post=[("round11/stage/v10d", "round10/stage/v10d"), ("round11/out/v10d", "round10/out/v10d"),
         ("data_r11_v10d", "data_r10_v10d"), ("~/caselaw2/r11_bin/run_v10d", "~/caselaw2/r10_bin/run_v10d"),
         ("= wsl/r11_run.sh on round-11 paths", "= wsl/r10_run.sh on round-11 paths"),
         ("Same runner call as\n# wsl/r11_run.sh", "Same runner call as\n# wsl/r10_run.sh"),
         ("round11/stage10.py", "round11/stage11.py")])
