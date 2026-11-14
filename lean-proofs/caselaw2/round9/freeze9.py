"""Round 9: write round9/FREEZE.md for one staged variant (rules, code, data, Lean output), before the single sealed runs.
(= round8/freeze8.py on round-9 paths and file lists, agent infra9: + every round-9 script, the round-8 h0 shadow that
score9.sh uses, every staged extra table (history_bridge, part_zone; a part_zone that is not staged is recorded as
`absent` and --check fails if it appears later), wsl/r9_run.sh, and for every round-9 fresh key named in
round9/FRESH_KEYS.txt: benchmarks/<k>/score.py, key.tsv, key_nodes.tsv (when present), MAPPING.md and READY, so the
freeze proves the keys did not change (their bytes are hashed only, never parsed or shown).)

    python -X utf8 round9/freeze9.py <name> --note "<one line>"
    python -X utf8 round9/freeze9.py --check        (exit 1 if any listed file changed or is missing)

Lines are "<sha1>  <path relative to caselaw-lean-2>" ("missing  <path>" / "absent  <path>" for files not there at
freeze time). Refuses to overwrite an existing FREEZE.md.
"""
import argparse, datetime, glob, hashlib, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(HERE)
R8 = os.path.join(C2, "round8")
LEAN = os.path.join(os.path.dirname(os.path.dirname(C2)), "global-law-lean", "lean-proofs")
OUT = os.path.join(HERE, "FREEZE.md")
TEN = ("treatments", "treatment_witness", "treatment_class", "history", "history_anchor", "history_claim", "joined",
       "cert_text", "window_sha", "cite_index")
EXTRA = ("history_bridge", "part_zone")  # round9/stage9.py EXTRA_TABLES
KEYS = ("fjc_idb_appeals", "shadow_docket", "scdb_disposition", "state_overruled_tables")


def sha1(p):
    h = hashlib.sha1()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def rel(p):
    return os.path.relpath(p, C2).replace(os.sep, "/")


def fresh_keys():
    p = os.path.join(HERE, "FRESH_KEYS.txt")
    if not os.path.exists(p):
        return []
    ks = [l.strip() for l in open(p, encoding="utf-8") if l.strip() and not l.startswith("#")]
    for k in ks:
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", k):
            sys.exit("bad key folder name in FRESH_KEYS.txt: %r" % k)
    return ks


def check():
    if not os.path.exists(OUT):
        sys.exit("no round9/FREEZE.md")
    bad, n = [], 0
    for line in open(OUT, encoding="utf-8"):
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name", nargs="?")
    ap.add_argument("--note", default="")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.check:
        return check()
    if not a.name:
        sys.exit("name required")
    if os.path.exists(OUT):
        sys.exit("FREEZE.md exists; refusing to overwrite")
    files, absent = [], []
    st = os.path.join(HERE, "stage", a.name)
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
    o = os.path.join(HERE, "out", a.name)
    for t in ("status.tsv", "certs.tsv", "classes.tsv", "findings.tsv", "summary.tsv", "RUN.txt"):
        files.append(os.path.join(o, t))
    for t in ("DESIGN9.md", "LEAN9.md", "CERTIFIERS.md", "certify9.py", "certify_recog9.py", "certify_opwords9.py",
              "stage9.py", "score9.sh", "summary9.py", "old_by_class9.py", "freeze9.py", "score_sealed9.sh",
              "shep_sealed9.py", "sealed_lines9.py"):
        p = os.path.join(HERE, t)
        if os.path.exists(p) or t not in ("LEAN9.md", "CERTIFIERS.md"):
            files.append(p)
    for pat in ("*.txt", "agents/*/*.py", "agents/*/READER_BRIEF*.md", "agents/*/RULES*.md",
                "agents/*/LEAN_REQUEST*.md", "audit/*.py", "audit/*BRIEF*.md"):
        files.extend(sorted(p for p in glob.glob(os.path.join(HERE, pat)) if p not in files))
    for pat in ("bench_h0/*.py", "bench_h0/*/*.py", "bench_h0/*/key*.tsv"):
        files.extend(sorted(p for p in glob.glob(os.path.join(R8, pat)) if p not in files))
    for t in ("round7/score_fresh7.py", "round7/score_hist_dev.py", "round6/shepardized/compare.py",
              "round5/gold_fresh/score_fresh.py", "round5/tests/score_holdout.py", "round5/tests/check_no_leak.py",
              "wsl/r9_run.sh", "audit/statements.lock", "benchmarks/common/benchlib.py",
              "benchmarks/shadow_docket/sdlib.py"):
        files.append(os.path.join(C2, t))
    for k in KEYS:
        files.append(os.path.join(C2, "benchmarks", k, "score.py"))
    # round-9 fresh keys (lead, 14 Nov): hash the scorer and the key files so the freeze proves they did not change
    # (bytes are hashed only; nothing is parsed). key_nodes.tsv only when present.
    for k in fresh_keys():
        kd = os.path.join(C2, "benchmarks", k)
        for t in ("score.py", "key.tsv", "key_nodes.tsv", "MAPPING.md", "READY"):
            p = os.path.join(kd, t)
            if t != "key_nodes.tsv" or os.path.exists(p):
                files.append(p)
    for t in sorted(glob.glob(os.path.join(LEAN, "LegalProofs", "CaseLaw2", "*.lean")) +
                    glob.glob(os.path.join(LEAN, "LegalProofs", "CaseLaw2", "Spec", "*.lean"))):
        files.append(t)
    files.append(os.path.join(LEAN, "tools", "caselaw2", "cues", "cue_table.json"))
    lines = []
    for p in files:
        if os.path.exists(p):
            lines.append("%s  %s" % (sha1(p), rel(p)))
        else:
            lines.append("missing  %s" % rel(p))
    for p in absent:
        lines.append("absent  %s" % rel(p))
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("# Round 9 freeze\n\nFrozen %s. Variant `%s` (data `round9/stage/%s`, Lean output `round9/out/%s`). %s\n\n"
                "The sealed halves (fresh lists, fifth use; Shepardized, fourth use), the h1 halves of the four round-8 "
                "keys (second use) and the round-9 fresh keys (first and only use, with v8e) are scored once on exactly "
                "these files (`round9/score_sealed9.sh %s`); `freeze9.py --check` refuses if any line below no longer "
                "matches. Nothing is re-tuned after the sealed runs.\n\n```\n" % (
                    now, a.name, a.name, a.name, a.note, a.name))
        f.write("\n".join(lines) + "\n```\n")
    print("wrote", OUT, len(lines), "files")


if __name__ == "__main__":
    main()
