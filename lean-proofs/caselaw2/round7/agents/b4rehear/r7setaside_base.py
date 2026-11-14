"""Round 7, track B4 (d): base history rows (rounds 4-5 reader, `hist-regex-v2`) of kind `vacated` that the round-6
frozen Lean run rejects with `noCue` (out/final2/certs.tsv) and whose quote says "set aside": a `setAside` claim for
them, under the same object rules as the new rows (r7setaside_bo.setaside_object_ok: R7-S1, R7-S2).

    python -X utf8 r7setaside_base.py     -> rows_setaside_base.jsonl, rows_setaside_base_stats.json, work/base_setaside_drops.tsv

The rows are written as linker rows with the base row's own (by, target, kind), quote span, part, evidence and
anchor; certify7 recognises them as base rows and writes only a history_claim line for the base id after checking
the base certificate with the claim (`claim_on_base`). Rows carried by the target's own text (by = -1) are left out.
Reads the frozen stage tables and the Lean verdicts of round 6 only (no answer key).
"""
import sys

sys.dont_write_bytecode = True
import collections, json, os, re  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
R6H = os.path.normpath(os.path.join(HERE, "..", "..", "..", "round6", "history"))
sys.path.insert(0, HERE)
import r7setaside_bo as S  # noqa: E402

NL = chr(10)


def main():
    nc = set()
    for line in open(os.path.join(R6H, "out", "final2", "certs.tsv"), encoding="utf-8"):
        p = line.rstrip(NL).split("\t")
        if p[0] == "history" and p[2] == "noCue":
            nc.add(p[1])
    anchors = {}
    for line in open(os.path.join(R6H, "stage", "final2", "history_anchor.tsv"), encoding="utf-8"):
        p = line.rstrip(NL).split("\t")
        anchors.setdefault(p[0], p)
    FD = S.L.Facts()
    S.BO.init()
    st = collections.Counter()
    out, drops = [], []
    for line in open(os.path.join(R6H, "stage", "final2", "history.tsv"), encoding="utf-8"):
        p = line.rstrip(NL).split("\t")
        if p[0] not in nc or p[4] != "vacated":
            continue
        st["base_nocue_vacated"] += 1
        q = p[9]
        if "set aside" not in q.lower():
            continue
        st["with_set_aside"] += 1
        if int(p[2]) < 0:
            st["drop:target_text"] += 1
            continue
        if "vacat" in q.lower():
            st["drop:has_vacat"] += 1
            continue
        ok, why = S.setaside_object_ok(q, int(FD.date[int(p[1])]), same_court=int(FD.court[int(p[1])]) == int(FD.court[int(p[2])]),
                                       target_tier=S.BO.court_at(int(FD.court[int(p[1])]), int(FD.date[int(p[1])]))[1])
        if not ok:
            st["drop:" + why] += 1
            drops.append((why, p[0], q[:300]))
            continue
        # R7-S7 on a base row: partial words in the quote while the base row says scope `all` -> no claim (the claim
        # cannot change the base row's scope)
        if p[5] == "all" and re.search(r"\bremainder\b|\bportions?\b|\bpart\s+of\b|\binsofar\b|\bin\s+so\s+far\b|"
                                       r"\bas\s+to\b|\bexcept\b|\bto\s+the\s+extent\b|\bin\s+part\b", q, re.I):
            st["drop:partial_words_scope_all"] += 1
            drops.append(("partial_words_scope_all", p[0], q[:300]))
            continue
        a = anchors.get(p[0])
        out.append({"rule": "r7setaside:base:" + p[12], "table": "history", "by": int(p[2]), "target": int(p[1]),
                    "kind": "vacated", "scope": p[5], "main": [int(p[7]), int(p[8])], "part": p[11], "ev": p[10],
                    "joined": [], "claim": "setAside", "doctrine": "-", "field_limit": "-", "text": "by",
                    "anchor": [int(a[1]), int(a[2])] if a else None, "anchor_part": a[4] if a else "",
                    "note": "base " + p[0]})
        st["rows"] += 1
    with open(os.path.join(HERE, "rows_setaside_base.jsonl"), "w", encoding="utf-8", newline=NL) as o:
        for r in out:
            o.write(json.dumps(r, ensure_ascii=False) + NL)
    with open(os.path.join(HERE, "work", "base_setaside_drops.tsv"), "w", encoding="utf-8", newline=NL) as o:
        for d in drops:
            o.write("\t".join(str(x).replace("\t", " ") for x in d) + NL)
    json.dump(dict(sorted(st.items())), open(os.path.join(HERE, "rows_setaside_base_stats.json"), "w"), indent=1)
    print(dict(sorted(st.items())))


if __name__ == "__main__":
    main()
