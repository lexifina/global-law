"""fjc9: Python simulation of DESIGN9 section 8 (D9-9) until lean9 lands it: certify9 run on rows that ALL carry the
claim `anchorWide`, with the anchor-cue list = `anchor` + `anchor_wide` + the judge strings ("district judge",
"magistrate judge", "trial judge"). Every other check is certify9's. Writes certify9's output folder, then adds the
history_claim lines `<id>\tanchorWide\tr7:<rule>` for every admitted anchored row (as round8/agents/scdb8/certify8w.py).

    python -X utf8 certify9j.py --rows ROWS.jsonl --out DIR [--procs N]
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(C2, "round9"))
import certify9  # noqa: E402

JUDGE = ["district judge", "magistrate judge", "trial judge"]
_orig = certify9.load_cues


def load_cues_wide():
    cues, src = _orig()
    t = json.load(open(certify9.CUE_JSON, encoding="utf-8"))
    extra = [c for c in t.get("anchor_wide", []) if c] + JUDGE
    cues["anchor"] = list(cues["anchor"]) + [c for c in extra if c not in cues["anchor"]]
    src["anchor"] = "cue_table anchor + anchor_wide + DESIGN9 section 8 judge strings (simulated claim anchorWide)"
    return cues, src


def main():
    a = sys.argv[1:]
    rows_p = a[a.index("--rows") + 1]
    out = a[a.index("--out") + 1]
    rows = [json.loads(l) for l in open(rows_p, encoding="utf-8")]
    assert all(r.get("claim") == "anchorWide" for r in rows), "every row must carry claim anchorWide"
    os.makedirs(os.path.join(HERE, "work"), exist_ok=True)
    tmp = os.path.join(HERE, "work", "j_rows_as_plain.jsonl")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(dict(r, claim="-"), ensure_ascii=False) + "\n")
    a[a.index("--rows") + 1] = tmp
    certify9.load_cues = load_cues_wide
    sys.argv = [certify9.__file__] + a
    certify9.main()
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
