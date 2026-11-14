"""Round 8: write round8/FREEZE.md for one staged variant (rules, code, data, Lean output), before the single sealed runs.
(= round7/freeze7.py on round-8 paths and file lists.)

    python -X utf8 round8/freeze8.py <name> --note "<one line>"
    python -X utf8 round8/freeze8.py --check        (exit 1 if any listed file changed or is missing)

Lines are "<sha1>  <path relative to caselaw-lean-2>". Refuses to overwrite an existing FREEZE.md. Hashed: every
staged table of round8/stage/<name>/ (TABLES.txt: the ten + EXTRA_TABLES) with MANIFEST.txt and TABLES.txt; the Lean
output (status, certs, classes, findings, summary, RUN.txt: the runner binary's sha1); the round-8 scripts, h0 shadow,
agents' code / reader briefs / rules / Lean requests, audit code; the scorers the sealed runs use (round 5/6/7 files
and benchmarks/<key>/score.py + helpers); wsl/r8_run.sh; audit/statements.lock; the Lean sources and cue table.
"""
import argparse, datetime, glob, hashlib, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(HERE)
LEAN = os.path.join(os.path.dirname(os.path.dirname(C2)), "global-law-lean", "lean-proofs")
OUT = os.path.join(HERE, "FREEZE.md")
TEN = ("treatments", "treatment_witness", "treatment_class", "history", "history_anchor", "history_claim", "joined",
       "cert_text", "window_sha", "cite_index")
KEYS = ("fjc_idb_appeals", "shadow_docket", "scdb_disposition", "state_overruled_tables")


def sha1(p):
    h = hashlib.sha1()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def rel(p):
    return os.path.relpath(p, C2).replace(os.sep, "/")


def check():
    if not os.path.exists(OUT):
        sys.exit("no round8/FREEZE.md")
    bad, n = [], 0
    for line in open(OUT, encoding="utf-8"):
        parts = line.rstrip("\n").split("  ", 1)
        if len(parts) != 2 or len(parts[0]) != 40:
            continue
        n += 1
        p = os.path.normpath(os.path.join(C2, parts[1]))
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
    files = []
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
    for t in tabs:
        files.append(os.path.join(st, t + ".tsv"))
    files += [os.path.join(st, "MANIFEST.txt"), tp]
    o = os.path.join(HERE, "out", a.name)
    for t in ("status.tsv", "certs.tsv", "classes.tsv", "findings.tsv", "summary.tsv", "RUN.txt"):
        files.append(os.path.join(o, t))
    for t in ("DESIGN8.md", "CERTIFIERS.md", "certify8.py", "certify_recog8.py", "certify_opwords8.py", "stage8.py",
              "score8.sh", "summary8.py", "old_by_class8.py", "freeze8.py", "score_sealed8.sh", "shep_sealed8.py"):
        files.append(os.path.join(HERE, t))
    for pat in ("*.txt", "bench_h0/*.py", "bench_h0/*/*.py", "bench_h0/*/key*.tsv", "agents/*/*.py",
                "agents/*/READER_BRIEF*.md", "agents/*/RULES*.md", "agents/*/LEAN_REQUEST*.md", "audit/*.py",
                "audit/*BRIEF*.md"):
        files.extend(sorted(p for p in glob.glob(os.path.join(HERE, pat)) if p not in files))
    for t in ("round7/score_fresh7.py", "round7/score_hist_dev.py", "round6/shepardized/compare.py",
              "round5/gold_fresh/score_fresh.py", "round5/tests/score_holdout.py", "round5/tests/check_no_leak.py",
              "wsl/r8_run.sh", "audit/statements.lock", "benchmarks/common/benchlib.py",
              "benchmarks/shadow_docket/sdlib.py"):
        files.append(os.path.join(C2, t))
    for k in KEYS:
        files.append(os.path.join(C2, "benchmarks", k, "score.py"))
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
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("# Round 8 freeze\n\nFrozen %s. Variant `%s` (data `round8/stage/%s`, Lean output `round8/out/%s`). %s\n\n"
                "The sealed halves (fresh lists, Shepardized) and the h1 halves of the four new keys are scored once on "
                "exactly these files (`round8/score_sealed8.sh %s`); `freeze8.py --check` refuses if any line below no "
                "longer matches. Nothing is re-tuned after the sealed runs.\n\n```\n" % (
                    now, a.name, a.name, a.name, a.note, a.name))
        f.write("\n".join(lines) + "\n```\n")
    print("wrote", OUT, len(lines), "files")


if __name__ == "__main__":
    main()
