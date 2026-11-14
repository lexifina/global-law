"""scdb8: Python simulation of D8-5 (claim `anchorWide`) until lean8's LEAN_READY: certify8 run on rows that ALL carry
the claim, with the anchor-cue list = `anchor` + `anchor_wide` (DESIGN8 section 5). Every other check is certify8's.
Writes certify8's output folder, then adds the history_claim lines `<id>\tanchorWide\tr7:<rule>` for every admitted
anchored row (certify8 itself writes claim lines only for orderHead / setAside).

    python -X utf8 certify8w.py --rows ROWS.jsonl --out DIR [--procs N]
Input rows must have "claim": "anchorWide"; they are passed to certify8 as claim "-" (the claim's only effect is the
cue list, which this wrapper widens for the whole run).
"""
import json, os, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(C2, "round8"))
sys.path.insert(0, HERE)
import certify8  # noqa: E402
from sc8 import ANCHOR_WIDE  # noqa: E402

_orig = certify8.load_cues


def load_cues_wide():
    cues, src = _orig()
    cues["anchor"] = list(cues["anchor"]) + [c for c in ANCHOR_WIDE if c not in cues["anchor"]]
    src["anchor"] = "cue_table anchor + DESIGN8 section 5 anchor_wide (simulated claim anchorWide)"
    return cues, src


def main():
    a = sys.argv[1:]
    rows_p = a[a.index("--rows") + 1]
    out = a[a.index("--out") + 1]
    rows = [json.loads(l) for l in open(rows_p, encoding="utf-8")]
    assert all(r.get("claim") == "anchorWide" for r in rows), "every row must carry claim anchorWide"
    tmp = os.path.join(HERE, "work", "w_rows_as_plain.jsonl")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(dict(r, claim="-"), ensure_ascii=False) + "\n")
    a[a.index("--rows") + 1] = tmp
    certify8.load_cues = load_cues_wide
    sys.argv = [certify8.__file__] + a
    certify8.main()
    anchored = set()
    with open(os.path.join(out, "history_anchor_delta.tsv"), encoding="utf-8") as f:
        for l in f:
            anchored.add(l.split("\t")[0])
    n = 0
    with open(os.path.join(out, "history_delta.tsv"), encoding="utf-8") as f, \
            open(os.path.join(out, "history_claim_delta.tsv"), "a", encoding="utf-8", newline="\n") as o:
        for l in f:
            p = l.rstrip("\n").split("\t")
            if p[0] in anchored:
                o.write("%s\tanchorWide\t%s\n" % (p[0], p[12]))
                n += 1
    print("anchorWide claim lines:", n)


if __name__ == "__main__":
    main()
