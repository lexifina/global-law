"""Round 10: write round10/FREEZE.md for one staged variant (rules, code, data, Lean output, binary), before the single
sealed runs. LEAD ONLY. (= round9/freeze9.py on round-10 paths and file lists, agent infra10.)

Hashed: the frozen stage's tables (the ten row tables + every table TABLES.txt lists: history_bridge, part_zone,
history_remand, adoption, succession, --table copies; an extra table that is not staged is recorded as `absent` and
--check fails if it appears later), MANIFEST.txt, TABLES.txt; the Lean output (status, certs, classes, findings,
summary, RUN.txt); the runner BINARY named by RUN.txt (in WSL, line `wsl:<path>  binary sha1 <sha1>`; must equal the
sha1 RUN.txt records); v9c's output and tables (round9/out/v9c, round9/stage/v9c: the comparison build of the new keys);
every round-10 script (round10/*.py, *.sh, agents/*/*.py, agents/*/*.sh, audit/*.py), briefs, rules and LEAN_REQUEST
files, round10/*.txt except KEEP.txt and logs; the scorers (dev scorers, the round-8 h0 shadow, benchmarks/<k>/score.py
of the four round-8 keys); wsl/r10_run.sh; the Lean sources, statements.lock and the cue table; for songer_treat,
brace_hall_state and every key named in round10/FRESH_KEYS.txt: benchmarks/<k>/score.py, key.tsv, key_nodes.tsv (when
present), MAPPING.md, READY (bytes only: hashed, never parsed or shown).
NOT hashed (so a late note does not break the check): NOTES.md, *LOG*.md, logs (*.log, *log*.txt), PROGRESS.md,
KEEP.txt, results/.

    python -X utf8 round10/freeze10.py <name> --note "<one line>"
    python -X utf8 round10/freeze10.py --check        (exit 1 if any listed file changed or is missing)
    python -X utf8 round10/freeze10.py <name> --dry-run   (lists what would be hashed, with sizes; writes nothing)

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
EXTRA = ("history_bridge", "part_zone", "history_remand")  # round10/stage10.py EXTRA_TABLES
KEYS = ("fjc_idb_appeals", "shadow_docket", "scdb_disposition", "state_overruled_tables")
R9_KEYS = ("songer_treat", "brace_hall_state")  # second use in round 10
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
    if first.startswith("NOBUILD frozen r9v9c"):
        path = "~/caselaw2/r10_bin/caselaw2_r9v9c"
    elif first.startswith("NOBUILD R10BIN="):
        path = "~/caselaw2/r10_bin/run_%s" % name
    elif first.startswith("built"):
        path = "~/caselaw2/r10_bin/caselaw2_%s" % name
    else:
        sys.exit("RUN.txt: unknown run kind: %s" % first[:60])
    return path, m.group(1)


def check():
    if not os.path.exists(OUT):
        sys.exit("no round10/FREEZE.md")
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
    o = os.path.join(HERE, "out", name)
    for t in ("status.tsv", "certs.tsv", "classes.tsv", "findings.tsv", "summary.tsv", "RUN.txt"):
        files.append(os.path.join(o, t))
    # the comparison build of the new keys (step 5 of score_sealed10.sh): v9c output and its listed tables
    v9o, v9s = os.path.join(C2, "round9", "out", "v9c"), os.path.join(C2, "round9", "stage", "v9c")
    for t in ("status.tsv", "certs.tsv", "classes.tsv", "findings.tsv", "summary.tsv", "RUN.txt"):
        files.append(os.path.join(v9o, t))
    for line in open(os.path.join(v9s, "TABLES.txt"), encoding="utf-8"):
        t = line.split("\t")[0].strip()
        if t:
            files.append(os.path.join(v9s, t + ".tsv"))
    files.append(os.path.join(v9s, "TABLES.txt"))
    for t in ("DESIGN10.md", "LEAN10.md", "FRESH_KEYS.txt"):
        p = os.path.join(HERE, t)
        if os.path.exists(p) or t == "DESIGN10.md":
            files.append(p)
    for pat in ("*.py", "*.sh", "*.txt", "agents/*/*.py", "agents/*/*.sh", "agents/*/READER_BRIEF*.md",
                "agents/*/RULES*.md", "agents/*/LEAN_REQUEST*.md", "audit/*.py", "audit/*BRIEF*.md"):
        for p in sorted(glob.glob(os.path.join(HERE, pat))):
            if p not in files and not SKIP_NAMES.search(os.path.basename(p)):
                files.append(p)
    for pat in ("bench_h0/*.py", "bench_h0/*/*.py", "bench_h0/*/key*.tsv"):
        files.extend(sorted(p for p in glob.glob(os.path.join(R8, pat)) if p not in files))
    for t in ("round7/score_fresh7.py", "round7/score_hist_dev.py", "round6/shepardized/compare.py",
              "round5/gold_fresh/score_fresh.py", "round5/tests/score_holdout.py", "round5/tests/check_no_leak.py",
              "round9/agents/calpart9/build_zones.py", "round9/agents/calpart9/partzone.py",
              "round9/agents/calpart9/partfix.py", "wsl/r10_run.sh", "audit/statements.lock",
              "benchmarks/common/benchlib.py", "benchmarks/shadow_docket/sdlib.py"):
        files.append(os.path.join(C2, t))
    for k in KEYS:
        files.append(os.path.join(C2, "benchmarks", k, "score.py"))
    # the round-9 keys (second use) and the round-10 fresh keys (first use): scorer + key files, bytes only.
    # A dry run neither reads FRESH_KEYS.txt nor names or touches any key file (infra / track agents may run it).
    if not touch_keys:
        KEYFILES.add("(the round-9 keys' and FRESH_KEYS.txt keys' score.py, key.tsv, key_nodes.tsv, MAPPING.md, READY:"
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
        f.write("# Round 10 freeze\n\nFrozen %s. Variant `%s` (data `round10/stage/%s`, Lean output `round10/out/%s`). %s\n\n"
                "The sealed halves (fresh lists, sixth use; Shepardized, fifth use), the h1 halves of the four round-8 "
                "keys (third use), songer_treat and brace_hall_state (second use) and the round-10 fresh keys (first "
                "and only use, with v9c) are scored once on exactly these files (`round10/score_sealed10.sh %s`); "
                "`freeze10.py --check` refuses if any line below no longer matches. Nothing is re-tuned after the "
                "sealed runs.\n\n```\n" % (now, a.name, a.name, a.name, a.note, a.name))
        f.write("\n".join(lines) + "\n```\n")
    print("wrote", OUT, len(lines), "files")


if __name__ == "__main__":
    main()
