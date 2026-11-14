"""Round 13: write round13/FREEZE.md for one staged variant (rules, code, data, Lean output, binary), before the single
sealed runs. LEAD ONLY. (agent infra12: = round11/freeze11.py on round-13 paths: closed keys songer_treat,
brace_hall_state (fourth use), fedcir_dataset (third use) and bhk_enbanc (second use); the binary of a NOBUILD run is
~/caselaw2/r13_bin/caselaw2_r11v11d (frozen round-11 s51); the order-node folder given to stage13 --nodes (from the
stage's MANIFEST args: nodes.tsv, CHANGED.tsv, *.md, text/*.txt) is hashed when the stage was built with --nodes;
v11d (round12/out/v12a + round12/stage/v12a) is the comparison build; a dry run never names round13/agents/bench12/
files or key files. Round 11 = round10/freeze10.py on round-11 paths and file lists, agent infra11; round 11 adds:
history_tbridge in the extra tables, the order-node files of a stage built with --nodes (decisions2.tsv when
TABLES.txt lists it, decisions2_nodes.tsv, nodes.count, nodes_map.tsv) and round13/data_orders/nodes.tsv + text/*.txt
when present, round13/nodes13.py, wsl/r13_run.sh; the closed keys songer_treat, brace_hall_state (third use) and
fedcir_dataset (second use) are hashed like round 10's round-9 keys; v10d is the comparison build.)

Hashed: the frozen stage's tables (the ten row tables + every table TABLES.txt lists: history_bridge, part_zone,
history_remand, adoption, succession, --table copies; an extra table that is not staged is recorded as `absent` and
--check fails if it appears later), MANIFEST.txt, TABLES.txt; the Lean output (status, certs, classes, findings,
summary, RUN.txt); the runner BINARY named by RUN.txt (in WSL, line `wsl:<path>  binary sha1 <sha1>`; must equal the
sha1 RUN.txt records); v10d's output and tables (round12/out/v12a, round12/stage/v12a: the comparison build of the new
keys); every round-13 script (round13/*.py, *.sh, agents/*/*.py, agents/*/*.sh, audit/*.py), briefs, rules and LEAN_REQUEST
files, round13/*.txt except KEEP.txt and logs; the scorers (dev scorers, the round-8 h0 shadow, benchmarks/<k>/score.py
of the four round-8 keys); wsl/r13_run.sh; the Lean sources, statements.lock and the cue table; for songer_treat,
brace_hall_state, fedcir_dataset and every key named in round13/FRESH_KEYS.txt: benchmarks/<k>/score.py, key.tsv, key_nodes.tsv (when
present), MAPPING.md, READY (bytes only: hashed, never parsed or shown).
NOT hashed (so a late note does not break the check): NOTES.md, *LOG*.md, logs (*.log, *log*.txt), PROGRESS.md,
KEEP.txt, results/.

    python -X utf8 round13/freeze13.py <name> --note "<one line>"
    python -X utf8 round13/freeze13.py --check        (exit 1 if any listed file changed or is missing)
    python -X utf8 round13/freeze13.py <name> --dry-run   (lists what would be hashed, with sizes; writes nothing)

Lines are "<sha1>  <path relative to caselaw-lean-2>" ("missing  <path>" / "absent  <path>" for files not there at
freeze time; "wsl:<path>  binary sha1 <sha1>" for the binary: a form round 6's compare.py freeze check skips). Refuses to overwrite an existing FREEZE.md.
"""
import argparse, datetime, glob, hashlib, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(HERE)
R8 = os.path.join(C2, "round8")
LEAN = os.path.join(os.path.dirname(os.path.dirname(C2)), "global-law-lean", "lean-proofs")
OUT = os.path.join(HERE, "FREEZE.md")
TEN = ("treatments", "treatment_witness", "treatment_class", "history", "history_anchor", "history_claim", "joined",
       "cert_text", "window_sha", "cite_index")
EXTRA = ("history_bridge", "part_zone", "history_remand", "history_tbridge", "history_identity")  # round13/stage13.py EXTRA_TABLES
NODE_FILES = ("decisions2_nodes.tsv", "nodes.count", "nodes_map.tsv")  # stage13.py --nodes (absent otherwise)
KEYS = ("fjc_idb_appeals", "shadow_docket", "scdb_disposition", "state_overruled_tables")
R9_KEYS = ("songer_treat", "brace_hall_state", "fedcir_dataset", "bhk_enbanc", "fjc_idb_unpub")  # closed keys: 5th, 5th, 4th, 3rd, 2nd use (round 13)
BENCH12 = os.path.join(HERE, "agents", "bench12")  # round 12: the fresh-key builder's folder (never named in a dry run)
NOWIN = 0x08000000 if os.name == "nt" else 0
KEYFILES = set()  # dry run: key files listed by name only (never opened, never stat'ed)
SKIP_NAMES = re.compile(r"(^NOTES\.md$|^PROGRESS\.md$|LOG|log|^KEEP\.txt$)")


def sha1(p):
    h = hashlib.sha1()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def wsl_sha1(path):
    r = subprocess.run(["wsl.exe", "-d", "Ubuntu", "--", "bash", "-lc", "sha1sum < %s | cut -c1-40" % path],
                       capture_output=True, text=True, creationflags=NOWIN, env=dict(os.environ, MSYS_NO_PATHCONV="1"))
    s = r.stdout.strip()
    return s if re.fullmatch(r"[0-9a-f]{40}", s) else None


def rel(p):
    return os.path.relpath(p, C2).replace(os.sep, "/")


def key_list(name):
    p = os.path.join(HERE, name)
    if not os.path.exists(p):
        return []
    ks = [l.split()[0] for l in open(p, encoding="utf-8") if l.strip() and not l.startswith("#")]
    for k in ks:
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", k):
            sys.exit("bad key folder name in %s: %r" % (name, k))
    return ks


def binary_of(run_txt):
    """(wsl path, sha1) of the runner a RUN.txt names: '<how> run, binary sha1 <sha>, ...'."""
    if not os.path.exists(run_txt):
        sys.exit("no %s" % rel(run_txt))
    first = open(run_txt, encoding="utf-8").readline()
    m = re.search(r"binary sha1 ([0-9a-f]{40})", first)
    if not m:
        sys.exit("RUN.txt names no binary sha1")
    name = os.path.basename(os.path.dirname(run_txt))
    if first.startswith("NOBUILD frozen r11v11d"):
        path = "~/caselaw2/r13_bin/caselaw2_r11v11d"
    elif first.startswith("NOBUILD R13BIN="):
        path = "~/caselaw2/r13_bin/run_%s" % name
    elif first.startswith("built"):
        path = "~/caselaw2/r13_bin/caselaw2_%s" % name
    else:
        sys.exit("RUN.txt: unknown run kind: %s" % first[:60])
    return path, m.group(1)


def check():
    if not os.path.exists(OUT):
        sys.exit("no round13/FREEZE.md")
    bad, n = [], 0
    for line in open(OUT, encoding="utf-8"):
        m = re.fullmatch(r"wsl:(\S+)  binary sha1 ([0-9a-f]{40})", line.rstrip("\n"))
        if m:
            n += 1
            if wsl_sha1(m.group(1)) != m.group(2):
                bad.append("wsl:" + m.group(1))
            continue
        parts = line.rstrip("\n").split("  ", 1)
        if len(parts) != 2:
            continue
        p = os.path.normpath(os.path.join(C2, parts[1]))
        if parts[0] == "absent":
            n += 1
            if os.path.exists(p):
                bad.append(parts[1] + " (absent at freeze time, present now)")
            continue
        if len(parts[0]) != 40:
            continue
        n += 1
        if not os.path.exists(p) or sha1(p) != parts[0]:
            bad.append(parts[1])
    if bad:
        print("FREEZE mismatch:", *bad, sep="\n  ")
        sys.exit(1)
    print("FREEZE ok:", n, "files")


def file_list(name, touch_keys=True):
    files, absent = [], []
    st = os.path.join(HERE, "stage", name)
    if not os.path.isdir(st):
        sys.exit("no stage %s" % st)
    tabs = list(TEN)
    tp = os.path.join(st, "TABLES.txt")
    if os.path.exists(tp):
        for line in open(tp, encoding="utf-8"):
            t = line.split("\t")[0].strip()
            if t and t not in tabs:
                tabs.append(t)
    for t in EXTRA:
        if t not in tabs:
            if os.path.exists(os.path.join(st, t + ".tsv")):
                tabs.append(t)
            else:
                absent.append(os.path.join(st, t + ".tsv"))
    for t in tabs:
        files.append(os.path.join(st, t + ".tsv"))
    files += [os.path.join(st, "MANIFEST.txt"), tp]
    # round 11: order-node files of a --nodes stage (decisions2.tsv itself is in TABLES.txt then), and the folder
    for t in NODE_FILES:
        p = os.path.join(st, t)
        (files if os.path.exists(p) else absent).append(p)
    # round 12: the node folder of `--nodes DIR` (MANIFEST.txt args) when the stage was built with it
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
                files.append(p)
    o = os.path.join(HERE, "out", name)
    for t in ("status.tsv", "certs.tsv", "classes.tsv", "findings.tsv", "summary.tsv", "RUN.txt"):
        files.append(os.path.join(o, t))
    # the comparison build of the new keys (step 5 of score_sealed13.sh): v11d output and its listed tables
    v9o, v9s = os.path.join(C2, "round12", "out", "v12a"), os.path.join(C2, "round12", "stage", "v12a")
    for t in ("status.tsv", "certs.tsv", "classes.tsv", "findings.tsv", "summary.tsv", "RUN.txt"):
        files.append(os.path.join(v9o, t))
    for line in open(os.path.join(v9s, "TABLES.txt"), encoding="utf-8"):
        t = line.split("\t")[0].strip()
        if t:
            files.append(os.path.join(v9s, t + ".tsv"))
    files.append(os.path.join(v9s, "TABLES.txt"))
    for t in ("DESIGN13.md", "LEAN12.md", "FRESH_KEYS.txt"):
        p = os.path.join(HERE, t)
        if os.path.exists(p) or t == "DESIGN13.md":
            files.append(p)
    for pat in ("*.py", "*.sh", "*.txt", "agents/*/*.py", "agents/*/*.sh", "agents/*/READER_BRIEF*.md",
                "agents/*/RULES*.md", "agents/*/LEAN_REQUEST*.md", "audit/*.py", "audit/*BRIEF*.md", "data_orders/*.md"):
        for p in sorted(glob.glob(os.path.join(HERE, pat))):
            if p not in files and not SKIP_NAMES.search(os.path.basename(p)):
                if not touch_keys and os.path.normpath(p).startswith(BENCH12 + os.sep):
                    KEYFILES.add("(round13/agents/bench12/ scripts: not named in a dry run)")
                    continue
                files.append(p)
    for pat in ("bench_h0/*.py", "bench_h0/*/*.py", "bench_h0/*/key*.tsv"):
        files.extend(sorted(p for p in glob.glob(os.path.join(R8, pat)) if p not in files))
    for t in ("round7/score_fresh7.py", "round7/score_hist_dev.py", "round6/shepardized/compare.py",
              "round5/gold_fresh/score_fresh.py", "round5/tests/score_holdout.py", "round5/tests/check_no_leak.py",
              "round9/agents/calpart9/build_zones.py", "round9/agents/calpart9/partzone.py",
              "round9/agents/calpart9/partfix.py", "wsl/r13_run.sh", "audit/statements.lock",
              "benchmarks/common/benchlib.py", "benchmarks/shadow_docket/sdlib.py"):
        files.append(os.path.join(C2, t))
    for k in KEYS:
        files.append(os.path.join(C2, "benchmarks", k, "score.py"))
    # the closed keys (songer / brace & hall fourth use, fedcir third, bhk_enbanc second) and the round-13 fresh keys (first use):
    # scorer + key files, bytes only.
    # A dry run neither reads FRESH_KEYS.txt nor names or touches any key file (infra / track agents may run it).
    if not touch_keys:
        KEYFILES.add("(the closed keys' and FRESH_KEYS.txt keys' score.py, key.tsv, key_nodes.tsv, MAPPING.md, READY:"
                     " not named in a dry run)")
    for k in (list(R9_KEYS) + [k for k in key_list("FRESH_KEYS.txt") if k not in R9_KEYS]) if touch_keys else []:
        kd = os.path.join(C2, "benchmarks", k)
        for t in ("score.py", "key.tsv", "key_nodes.tsv", "MAPPING.md", "READY"):
            p = os.path.join(kd, t)
            if t != "key_nodes.tsv" or os.path.exists(p):
                files.append(p)
    for t in sorted(glob.glob(os.path.join(LEAN, "LegalProofs", "CaseLaw2", "*.lean")) +
                    glob.glob(os.path.join(LEAN, "LegalProofs", "CaseLaw2", "Spec", "*.lean"))):
        files.append(t)
    files.append(os.path.join(LEAN, "tools", "caselaw2", "cues", "cue_table.json"))
    return files, absent, os.path.join(o, "RUN.txt")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name", nargs="?")
    ap.add_argument("--note", default="")
    ap.add_argument("--classes", default=None, help="round 13: a Markdown file inserted before the hash block "
                                                       "(installed classes, incl. those installed on user decision)")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.check:
        return check()
    if not a.name:
        sys.exit("name required")
    if os.path.exists(OUT) and not a.dry_run:
        sys.exit("FREEZE.md exists; refusing to overwrite")
    files, absent, run_txt = file_list(a.name, touch_keys=not a.dry_run)
    if a.dry_run:
        tot = 0
        for p in sorted(KEYFILES):
            print("   (keys)  %s" % p)
        for p in files:
            if os.path.basename(p) == "FRESH_KEYS.txt":
                print("   (listed by name only)  %s" % rel(p))
                continue
            s = os.path.getsize(p) if os.path.exists(p) else -1
            tot += max(s, 0)
            print("%12d  %s" % (s, rel(p)))
        for p in absent:
            print("      absent  %s" % rel(p))
        print("dry run: %d files, %.1f MB, %d absent; binary %s (not hashed in a dry run)" % (
            len(files), tot / 1048576, len(absent), binary_of(run_txt) if os.path.exists(run_txt) else "?"))
        return
    bpath, bsha = binary_of(run_txt)
    have = wsl_sha1(bpath)
    if have != bsha:
        sys.exit("binary %s hashes to %s, RUN.txt says %s: refusing" % (bpath, have, bsha))
    lines = ["wsl:%s  binary sha1 %s" % (bpath, bsha)]  # a form round 6's compare.py freeze regex skips
    for p in files:
        if os.path.exists(p):
            lines.append("%s  %s" % (sha1(p), rel(p)))
        else:
            lines.append("missing  %s" % rel(p))
    for p in absent:
        lines.append("absent  %s" % rel(p))
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("# Round 13 freeze\n\nFrozen %s. Variant `%s` (data `round13/stage/%s`, Lean output `round13/out/%s`). %s\n\n"
                "The sealed halves (fresh lists and Shepardized, both burned), the h1 halves of the four round-8 "
                "keys (sixth use), songer_treat and brace_hall_state (fifth use), fedcir_dataset (fourth use), "
                "bhk_enbanc (third use) and fjc_idb_unpub (second use) are scored once on exactly "
                "these files (`round13/score_sealed13.sh %s`); "
                "`freeze13.py --check` refuses if any line below no longer matches. Nothing is re-tuned after the "
                "sealed runs.\n\n" % (now, a.name, a.name, a.name, a.note, a.name))
        if a.classes:  # round 13: installed classes (incl. those installed on user decision)
            f.write(open(a.classes, encoding="utf-8").read().rstrip("\n") + "\n\n")
        f.write("```\n" + "\n".join(lines) + "\n```\n")
    print("wrote", OUT, len(lines), "files")


if __name__ == "__main__":
    main()
