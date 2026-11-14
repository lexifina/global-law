"""Round 7: write round7/FREEZE.md for one staged variant (rules, code, data, Lean output), before the single sealed runs.

    python -X utf8 round7/freeze7.py <name> --note "<one line>"
    python -X utf8 round7/freeze7.py --check        (exit 1 if any listed file changed or is missing)

Lines are "<sha1>  <path relative to caselaw-lean-2>". Refuses to overwrite an existing FREEZE.md.
"""
import argparse, datetime, glob, hashlib, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(HERE)
LEAN = os.path.join(os.path.dirname(os.path.dirname(C2)), "global-law-lean", "lean-proofs")
OUT = os.path.join(HERE, "FREEZE.md")


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
        sys.exit("no round7/FREEZE.md")
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
    for t in ("treatments.tsv", "treatment_witness.tsv", "treatment_class.tsv", "history.tsv", "history_anchor.tsv",
              "history_claim.tsv", "joined.tsv", "cert_text.tsv", "window_sha.tsv", "cite_index.tsv", "MANIFEST.txt"):
        files.append(os.path.join(st, t))
    o = os.path.join(HERE, "out", a.name)
    for t in ("status.tsv", "certs.tsv", "classes.tsv", "findings.tsv", "summary.tsv"):
        files.append(os.path.join(o, t))
    for t in ("DESIGN7.md", "LEAN7.md", "certify7.py", "stage7.py", "score7.sh", "score_fresh7.py", "score_hist_dev.py",
              "summary7.py", "freeze7.py", "score_sealed7.sh", "stage_drop_v2.txt", "drop_b4_r3weak.txt"):
        files.append(os.path.join(HERE, t))
    for pat in ("agents/*/*.py", "agents/*/READER_BRIEF*.md", "agents/*/RULES*.md", "audit/*.py", "audit/AUDITOR_BRIEF7.md",
                "heldout/score_heldout.py"):
        files.extend(sorted(glob.glob(os.path.join(HERE, pat))))
    for t in ("round6/shepardized/compare.py", "round5/gold_fresh/score_fresh.py", "round5/tests/score_holdout.py",
              "round5/tests/check_no_leak.py", "wsl/r7_run.sh", "audit/statements.lock"):
        files.append(os.path.join(C2, t))
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
        f.write("# Round 7 freeze\n\nFrozen %s. Variant `%s` (data `round7/stage/%s`, Lean output `round7/out/%s`). %s\n\n"
                "The sealed halves and the time-split key are scored once on exactly these files "
                "(`round7/score_sealed7.sh %s`); `freeze7.py --check` refuses if any line below no longer matches. "
                "Nothing is re-tuned after the sealed runs.\n\n```\n" % (now, a.name, a.name, a.name, a.note, a.name))
        f.write("\n".join(lines) + "\n```\n")
    print("wrote", OUT, len(lines), "files")


if __name__ == "__main__":
    main()
