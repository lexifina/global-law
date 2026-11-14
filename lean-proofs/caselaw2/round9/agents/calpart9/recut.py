"""calpart9: history rows whose main quote straddles head matter and the opinion of the court (zone check refuses
them). General rule RC: re-cut the quote to its part inside the opinion zone (from the first non-blank line after the
section heading line to the quote's end, or the zone's end); keep the row when the re-cut quote still passes the
round-6 text checks (cue of the kind in the quote, no disqualifier, evidence within 400 characters, part) --
certify6.check_row. RC-A: when only the evidence fails (targetUnresolved), the head-matter part of the original
quote becomes the row's anchor (anchored row: anchor cue + evidence in the anchor, anchor part headmatter allowed).
Otherwise the row's cue / evidence is in the head matter and it stays refused.

    python -X utf8 recut.py work/v8e/refused.tsv --out work/recut

Writes rows.jsonl (certify9 input: history rows, same by/target/kind, main = re-cut span, part = the zone's part),
recut.tsv (id, outcome, where the cue is, new span) and prints counts. No answer-key file is read.
"""
import argparse
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import partzone as PZ  # noqa: E402

C2 = PZ.C2
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import certify6 as C6  # noqa: E402

L = PZ.L
NL, TAB = "\n", "\t"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("refused")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rows = [ln.rstrip(NL).split(TAB) for ln in open(a.refused, encoding="utf-8")]
    rows = [r for r in rows if r[1] == "history" and r[7] == "straddle"]
    hist = {}
    want = set(r[0] for r in rows)
    for ln in open(os.path.join(C2, "round8", "stage", "v8e", "history.tsv"), encoding="utf-8"):
        p = ln.rstrip(NL).split(TAB)
        if p[0] in want:
            hist[p[0]] = p
    cues, _ = C6.load_cues()
    texts = L.fetch_texts(set(int(r[3]) for r in rows))
    cnt = collections.Counter()
    fo = open(os.path.join(a.out, "rows.jsonl"), "w", encoding="utf-8", newline=NL)
    ft = open(os.path.join(a.out, "recut.tsv"), "w", encoding="utf-8", newline=NL)
    for r in rows:
        h = hist[r[0]]
        n, s, e = int(r[3]), int(r[4]), int(r[5])
        text = texts[n][1]
        zs, _ = PZ.zones(text)
        # the opinion zone the quote ends in (a court part)
        z = next((zz for zz in zs if zz[0] < e <= zz[1]), None)
        if z is None or z[2] not in C6.PARTS or z[0] <= s:
            cnt["no_court_zone_at_end"] += 1
            ft.write(TAB.join([r[0], "noZone", "-", "-", "-"]) + NL)
            continue
        hl = text.find(NL, z[0])  # end of the section heading line
        s2 = hl + 1 if 0 <= hl < e else z[0]
        while s2 < e and text[s2] in " \t\n":
            s2 += 1
        head_q = C6.lower(C6.norm(text[s:z[0]]))
        op_q = C6.lower(C6.norm(text[s2:e]))
        kc = cues["hist"].get(h[4], ())
        where = ("head" if any(c in head_q for c in kc) else "") + ("+op" if any(c in op_q for c in kc) else "")
        cnt["cue:" + (where or "none")] += 1
        rr = {"anchor": None, "disp": (s2, e), "kind": h[4], "ev": h[10], "self_text": False, "cite_fail": "",
              "part": z[2], "ordered": True, "by": int(h[2]), "target": int(h[1])}
        reason, detail, _ = C6.check_row(rr, text, cues) if s2 < e else ("empty", "", None)
        anchor = None
        if reason == "targetUnresolved":
            # RC-A: the head-matter part of the original quote becomes the row's anchor (anchor parts admit
            # headmatter; the anchor must carry an anchor cue and the evidence, as any anchored row)
            a1 = z[0]
            while a1 > s and text[a1 - 1] in " \t\n":
                a1 -= 1
            zh = PZ.zone_at(zs, s, a1)
            if zh and zh[2] in C6.ANCHOR_PARTS and s < a1:
                rr2 = dict(rr, anchor=(s, a1), anchor_part=zh[2])
                reason2, detail2, _ = C6.check_row(rr2, text, cues)
                cnt["anchor:" + (reason2 or "pass")] += 1
                if reason2 is None:
                    reason, anchor = None, [s, a1, zh[2]]
        out = (reason or "pass") + ("A" if anchor else "")
        cnt[out] += 1
        ft.write(TAB.join([r[0], out, where or "none", "%d-%d" % (s2, e), L.norm(text[s2:e])[:200]]) + NL)
        if reason is None:
            fo.write(json.dumps({"rule": "calpart9:RC", "table": "history", "by": int(h[2]), "target": int(h[1]),
                                 "kind": h[4], "scope": h[5], "main": [s2, e], "part": z[2], "ev": h[10],
                                 "claim": "-", "anchor": anchor[:2] if anchor else None,
                                 "anchor_part": anchor[2] if anchor else None, "text": "by",
                                 "note": "re-cut of " + r[0]}, ensure_ascii=False) + NL)
    fo.close()
    ft.close()
    print(len(rows), json.dumps(dict(cnt)))


if __name__ == "__main__":
    main()
