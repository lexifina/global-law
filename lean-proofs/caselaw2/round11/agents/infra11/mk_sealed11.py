"""infra11 Part C: round11/freeze11.py, sealed_lines11.py, shep_sealed11.py and score_sealed11.sh from the round-10 files
(exact replacements; round-10 files are only read). LEAD ONLY scripts; infra11 runs only --help / --plan / --dry-run.

    python -X utf8 round11/agents/infra11/mk_sealed11.py [--force]
"""
import os
import sys

C2 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def tr(src, dst, reps, glob=()):
    s = open(os.path.join(C2, src), "rb").read().decode("utf-8")
    assert "\r" not in s, src
    for r in reps:
        a, b = r[0], r[1]
        n = r[2] if len(r) > 2 else 1
        assert s.count(a) == n, (src, a[:80], s.count(a), n)
        s = s.replace(a, b)
    for a, b in glob:
        assert s.count(a) >= 1, (src, "glob", a)
        s = s.replace(a, b)
    p = os.path.join(C2, dst)
    if os.path.exists(p) and "--force" not in sys.argv:
        print("exists, kept (use --force):", dst)
        return
    open(p, "wb").write(s.encode("utf-8"))
    print("written", dst)


tr("round10/sealed_lines10.py", "round11/sealed_lines11.py", [
    ('"""Round 10 (agent infra10; = round9/sealed_lines9.py, names only).',
     '"""Round 11 (agent infra11; = round10/sealed_lines10.py, names only). Round 10 (agent infra10; = '
     'round9/sealed_lines9.py, names only).'),
    ("python -I round10/sealed_lines10.py", "python -I round11/sealed_lines11.py", 5),
])
tr("round10/shep_sealed10.py", "round11/shep_sealed11.py", [
    ('"""Round 10 (= round9/shep_sealed9.py with round10/FREEZE.md and round10/SEALED_LOG.md; agent infra10): the\n'
     'Shepardized sealed run through round 6\'s compare.py, with the freeze check pointed at round10/FREEZE.md.',
     '"""Round 11 (= round10/shep_sealed10.py with round11/FREEZE.md and round11/SEALED_LOG.md; agent infra11): the\n'
     'Shepardized sealed run through round 6\'s compare.py, with the freeze check pointed at round11/FREEZE.md.'),
    ("round10/FREEZE.md (same \"<sha1>  <path>\" format, every round-10 model file) and SEALED_LOG at round10/SEALED_LOG.md, and",
     "round11/FREEZE.md (same \"<sha1>  <path>\" format, every round-11 model file) and SEALED_LOG at round11/SEALED_LOG.md, and"),
    ("    python -I round10/shep_sealed10.py --split sealed", "    python -I round11/shep_sealed11.py --split sealed"),
    ('    sys.exit("shep_sealed10.py is for --split sealed only")', '    sys.exit("shep_sealed11.py is for --split sealed only")'),
])

tr("round10/freeze10.py", "round11/freeze11.py", [
    ('"""Round 10: write round10/FREEZE.md for one staged variant (rules, code, data, Lean output, binary), before the single\n'
     'sealed runs. LEAD ONLY. (= round9/freeze9.py on round-10 paths and file lists, agent infra10.)\n',
     '"""Round 11: write round11/FREEZE.md for one staged variant (rules, code, data, Lean output, binary), before the single\n'
     'sealed runs. LEAD ONLY. (= round10/freeze10.py on round-11 paths and file lists, agent infra11; round 11 adds:\n'
     'history_tbridge in the extra tables, the order-node files of a stage built with --nodes (decisions2.tsv when\n'
     'TABLES.txt lists it, decisions2_nodes.tsv, nodes.count, nodes_map.tsv) and round11/data_orders/nodes.tsv + text/*.txt\n'
     'when present, round11/nodes11.py, wsl/r11_run.sh; the closed keys songer_treat, brace_hall_state (third use) and\n'
     'fedcir_dataset (second use) are hashed like round 10\'s round-9 keys; v10d is the comparison build.)\n'),
    ("sha1 RUN.txt records); v9c's output and tables (round9/out/v9c, round9/stage/v9c: the comparison build of the new keys);\n"
     "every round-10 script (round10/*.py,",
     "sha1 RUN.txt records); v10d's output and tables (round10/out/v10d, round10/stage/v10d: the comparison build of the new\n"
     "keys); every round-11 script (round11/*.py,"),
    ("files, round10/*.txt except KEEP.txt and logs;", "files, round11/*.txt except KEEP.txt and logs;"),
    ("of the four round-8 keys); wsl/r10_run.sh; the Lean sources, statements.lock and the cue table; for songer_treat,\n"
     "brace_hall_state and every key named in round10/FRESH_KEYS.txt:",
     "of the four round-8 keys); wsl/r11_run.sh; the Lean sources, statements.lock and the cue table; for songer_treat,\n"
     "brace_hall_state, fedcir_dataset and every key named in round11/FRESH_KEYS.txt:"),
    ("    python -X utf8 round10/freeze10.py <name> --note", "    python -X utf8 round11/freeze11.py <name> --note"),
    ("    python -X utf8 round10/freeze10.py --check ", "    python -X utf8 round11/freeze11.py --check "),
    ("    python -X utf8 round10/freeze10.py <name> --dry-run", "    python -X utf8 round11/freeze11.py <name> --dry-run"),
    ('EXTRA = ("history_bridge", "part_zone", "history_remand")  # round10/stage10.py EXTRA_TABLES',
     'EXTRA = ("history_bridge", "part_zone", "history_remand", "history_tbridge")  # round11/stage11.py EXTRA_TABLES\n'
     'NODE_FILES = ("decisions2_nodes.tsv", "nodes.count", "nodes_map.tsv")  # stage11.py --nodes (absent otherwise)'),
    ('R9_KEYS = ("songer_treat", "brace_hall_state")  # second use in round 10',
     'R9_KEYS = ("songer_treat", "brace_hall_state", "fedcir_dataset")  # closed keys: third, third, second use in round 11'),
    ('    if first.startswith("NOBUILD frozen r9v9c"):\n        path = "~/caselaw2/r10_bin/caselaw2_r9v9c"\n'
     '    elif first.startswith("NOBUILD R10BIN="):\n        path = "~/caselaw2/r10_bin/run_%s" % name\n'
     '    elif first.startswith("built"):\n        path = "~/caselaw2/r10_bin/caselaw2_%s" % name',
     '    if first.startswith("NOBUILD frozen r10v10d"):\n        path = "~/caselaw2/r11_bin/caselaw2_r10v10d"\n'
     '    elif first.startswith("NOBUILD R11BIN="):\n        path = "~/caselaw2/r11_bin/run_%s" % name\n'
     '    elif first.startswith("built"):\n        path = "~/caselaw2/r11_bin/caselaw2_%s" % name'),
    ('        sys.exit("no round10/FREEZE.md")', '        sys.exit("no round11/FREEZE.md")'),
    ('    files += [os.path.join(st, "MANIFEST.txt"), tp]\n',
     '    files += [os.path.join(st, "MANIFEST.txt"), tp]\n'
     '    # round 11: order-node files of a --nodes stage (decisions2.tsv itself is in TABLES.txt then), and the folder\n'
     '    for t in NODE_FILES:\n'
     '        p = os.path.join(st, t)\n'
     '        (files if os.path.exists(p) else absent).append(p)\n'
     '    od = os.path.join(HERE, "data_orders")\n'
     '    for p in [os.path.join(od, "nodes.tsv")] + sorted(glob.glob(os.path.join(od, "text", "*.txt"))):\n'
     '        if os.path.exists(p):\n'
     '            files.append(p)\n'),
    ("    # the comparison build of the new keys (step 5 of score_sealed10.sh): v9c output and its listed tables\n"
     '    v9o, v9s = os.path.join(C2, "round9", "out", "v9c"), os.path.join(C2, "round9", "stage", "v9c")',
     "    # the comparison build of the new keys (step 5 of score_sealed11.sh): v10d output and its listed tables\n"
     '    v9o, v9s = os.path.join(C2, "round10", "out", "v10d"), os.path.join(C2, "round10", "stage", "v10d")'),
    ('    for t in ("DESIGN10.md", "LEAN10.md", "FRESH_KEYS.txt"):\n        p = os.path.join(HERE, t)\n'
     '        if os.path.exists(p) or t == "DESIGN10.md":',
     '    for t in ("DESIGN11.md", "LEAN11.md", "FRESH_KEYS.txt"):\n        p = os.path.join(HERE, t)\n'
     '        if os.path.exists(p) or t == "DESIGN11.md":'),
    ('"audit/*.py", "audit/*BRIEF*.md"):', '"audit/*.py", "audit/*BRIEF*.md", "data_orders/*.md"):'),
    ('"round9/agents/calpart9/partfix.py", "wsl/r10_run.sh", "audit/statements.lock",',
     '"round9/agents/calpart9/partfix.py", "wsl/r11_run.sh", "audit/statements.lock",'),
    ("    # the round-9 keys (second use) and the round-10 fresh keys (first use): scorer + key files, bytes only.",
     "    # the closed keys (songer / brace & hall third use, fedcir second use) and the round-11 fresh keys (first use):\n"
     "    # scorer + key files, bytes only."),
    ('        KEYFILES.add("(the round-9 keys\' and FRESH_KEYS.txt keys\' score.py,',
     '        KEYFILES.add("(the closed keys\' and FRESH_KEYS.txt keys\' score.py,'),
    ('        f.write("# Round 10 freeze\\n\\nFrozen %s. Variant `%s` (data `round10/stage/%s`, Lean output `round10/out/%s`). %s\\n\\n"\n'
     '                "The sealed halves (fresh lists, sixth use; Shepardized, fifth use), the h1 halves of the four round-8 "\n'
     '                "keys (third use), songer_treat and brace_hall_state (second use) and the round-10 fresh keys (first "\n'
     '                "and only use, with v9c) are scored once on exactly these files (`round10/score_sealed10.sh %s`); "\n'
     '                "`freeze10.py --check` refuses',
     '        f.write("# Round 11 freeze\\n\\nFrozen %s. Variant `%s` (data `round11/stage/%s`, Lean output `round11/out/%s`). %s\\n\\n"\n'
     '                "The sealed halves (fresh lists, seventh use; Shepardized, sixth use; both burned), the h1 halves of "\n'
     '                "the four round-8 keys (fourth use), songer_treat and brace_hall_state (third use), fedcir_dataset "\n'
     '                "(second use) and the round-11 fresh keys (first and only use, with v10d) are scored once on exactly "\n'
     '                "these files (`round11/score_sealed11.sh %s`); "\n'
     '                "`freeze11.py --check` refuses'),
])
