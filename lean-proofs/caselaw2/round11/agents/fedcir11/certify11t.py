"""fedcir11: Python simulation of DESIGN11 §5.1 (claim anchorTribunal, D11-4) until infra11's certify11_claims has
it: round11/certify11.py run on rows that ALL carry the claim `anchorTribunal`, with the anchor-cue list = `anchor` +
`anchor_wide` + `anchor_wide9` + `anchor_tribunal` (from the cue table when lean11 has added it, else the six
phrases of the request). Every other check is certify11's. Writes certify11's output folder, then adds the
history_claim lines `<id>\tanchorTribunal\t<src>` for every admitted anchored row (as round9 fjc9 certify9j.py).

    python -X utf8 certify11t.py --rows ROWS.jsonl --out DIR [--procs N]
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(C2, "round11"))
import certify11  # noqa: E402

TRIB = ["court of international trade", "customs court", "court of federal claims", "claims court", "veterans court",
        "court of veterans appeals"]
_orig = certify11.load_cues


def load_cues_trib():
    cues, src = _orig()
    t = json.load(open(certify11.CUE_JSON, encoding="utf-8"))
    extra = [c for c in t.get("anchor_wide", []) + t.get("anchor_wide9", []) + (t.get("anchor_tribunal") or TRIB) if c]
    cues["anchor"] = list(cues["anchor"]) + [c for c in extra if c not in cues["anchor"]]
    src["anchor"] = "cue_table anchor + anchor_wide + anchor_wide9 + anchor_tribunal (%s) (simulated claim anchorTribunal)" % (
        "cue table" if t.get("anchor_tribunal") else "DESIGN11 5.1 request list")
    return cues, src


def main():
    a = sys.argv[1:]
    rows_p = a[a.index("--rows") + 1]
    out = a[a.index("--out") + 1]
    rows = [json.loads(l) for l in open(rows_p, encoding="utf-8")]
    assert all(r.get("claim") == "anchorTribunal" for r in rows), "every row must carry claim anchorTribunal"
    os.makedirs(os.path.join(HERE, "work"), exist_ok=True)
    tmp = os.path.join(HERE, "work", "t_rows_as_plain.jsonl")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(dict(r, claim="-"), ensure_ascii=False) + "\n")
    a[a.index("--rows") + 1] = tmp
    certify11.load_cues = load_cues_trib
    sys.argv = [certify11.__file__] + a
    certify11.main()
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
                o.write("%s\tanchorTribunal\t%s\n" % (p[0], p[12]))
                n += 1
    print("anchorTribunal claim lines:", n)


if __name__ == "__main__":
    main()
