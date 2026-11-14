"""Round 5: write FREEZE.md: hashes of the rules, code, data and output of the frozen build, BEFORE the sealed test.

    python round5/freeze.py <variant>
"""
import datetime
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(HERE)
LP = r"~\Documents\global-law-lean\lean-proofs"
v = sys.argv[1]


def sha(p):
    h = hashlib.sha1()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def tree(d, exts):
    h = hashlib.sha1()
    n = 0
    for root, dirs, files in os.walk(d):
        dirs[:] = sorted(x for x in dirs if x not in ("__pycache__", ".lake"))
        for fn in sorted(files):
            if fn.endswith(exts):
                p = os.path.join(root, fn)
                h.update(os.path.relpath(p, d).replace("\\", "/").encode())
                h.update(sha(p).encode())
                n += 1
    return h.hexdigest(), n


L = ["# Round 5 freeze record", "",
     "Written %s, before the single run of the sealed half. Nothing listed here was changed afterwards." %
     datetime.datetime.now().strftime("%d %B %Y, %H:%M"), "",
     "Frozen build: variant `%s` (`round5/stage/%s`, output `round5/out/%s`). %s" % (
         v, v, v, open(os.path.join(HERE, "results", v, "ABOUT.txt"), encoding="utf-8").read().strip()), "",
     "## Rules and code", "", "| What | Files | SHA-1 |", "|---|---|---|"]
for name, d, exts in [
        ("Lean sources (`LegalProofs/CaseLaw2`)", os.path.join(LP, "LegalProofs", "CaseLaw2"), (".lean",)),
        ("Cue table and generator (`tools/caselaw2/cues`)", os.path.join(LP, "tools", "caselaw2", "cues"), (".json", ".py")),
        ("Python reference (`tools/caselaw2/ref`)", os.path.join(LP, "tools", "caselaw2", "ref"), (".py", ".json")),
        ("Recognised reader: brief, certifier, verifier (`round5/recog`)", os.path.join(HERE, "recog"), (".py", ".md")),
        ("Operative-words reader (`round5/opwords`; not installed)", os.path.join(HERE, "opwords"), (".py", ".md")),
        ("Audit tools (`round5/audit`)", os.path.join(HERE, "audit"), (".py",))]:
    h, n = tree(d, exts)
    L.append("| %s | %d | `%s` |" % (name, n, h))
for name, p in [("Design (`round5/DESIGN5.md`)", os.path.join(HERE, "DESIGN5.md")),
                ("Staging script (`round5/stage.py`)", os.path.join(HERE, "stage.py")),
                ("Runner script (`run_lean.sh`)", os.path.join(C2, "run_lean.sh")),
                ("Theorem lock (`audit/statements.lock`)", os.path.join(C2, "audit", "statements.lock")),
                ("Fresh-list scorer (`gold_fresh/score_fresh.py`, not ours)", os.path.join(HERE, "gold_fresh", "score_fresh.py"))]:
    L.append("| %s | 1 | `%s` |" % (name, sha(p)))
L += ["", "## Data of the frozen build (`round5/stage/%s`)" % v, "", "| Table | Rows | SHA-1 |", "|---|---|---|"]
for t in ["treatments", "treatment_witness", "treatment_class", "cert_text", "window_sha", "cite_index"]:
    p = os.path.join(HERE, "stage", v, t + ".tsv")
    L.append("| `%s.tsv` | %d | `%s` |" % (t, sum(1 for _ in open(p, "rb")), sha(p)))
L += ["", "Every other table is the round-4 table, unchanged (hard links to `data/`).", "",
      "## Output of the frozen build (`round5/out/%s`)" % v, "", "| File | Lines | SHA-1 |", "|---|---|---|"]
for fn in sorted(os.listdir(os.path.join(HERE, "out", v))):
    if fn.endswith(".tsv") and fn != "summary.tsv":
        p = os.path.join(HERE, "out", v, fn)
        L.append("| `%s` | %d | `%s` |" % (fn, sum(1 for _ in open(p, "rb")), sha(p)))
L += ["", "## What was used to get here", "",
      "- The open (dev) half of the fresh lists: scored for `it0_claims`, `it1`, `it2` and `%s`; its misses were read "
      "(`diag2/`). One row was removed and the operative cue lists were extended because of that reading." % v,
      "- The sealed half: never opened, never scored by this agent before this record.",
      "- The burned lists (SCDB, CRS, Christiansen-Eskridge, Hasen): not used to choose any candidate; the 66 SCDB "
      "misses were read for diagnosis only (`diag/`).",
      "- Later-court statements: only speakers with power over the target (the `feed` side of `tests/split`); "
      "`check_no_leak.py` exits 0 on this build.", ""]
open(os.path.join(HERE, "FREEZE.md"), "w", encoding="utf-8", newline="\n").write("\n".join(L))
print("\n".join(L[:14]))
