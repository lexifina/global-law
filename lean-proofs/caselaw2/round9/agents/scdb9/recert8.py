"""scdb8: round-6/7 below_sc linker rows of INSTALLED classes that are not in v3 (diagnosis + candidate class R5).

    python -X utf8 recert8.py   -> rows_recert.jsonl, work/recert_stats.json

Input: work/rows_all_off.jsonl (sc8 with every round-8 rule off = round 6 + round 7 linkers, unchanged rules).
Kept: strict rows of round 6's installed anchor types (A1, HM_SYL, HM_REP), strict weak types passing round 7's R3
test (installed round-7 class weak_r3), loose rows of round 7's installed sub-classes (hm, zone, body), after round 7's
guards (conditional, side proceeding, footnote, re-pointed without name anchor). Situation of the acting opinion in v3:
  none        no review-kind row by it in v3 (the linker row was refused or never certified with alias index lines)
  reader      its only v3 review rows are round-4 reader rows (hist-regex-v2) on other decisions: round 7 skipped the
              opinion ("in_final2"); R5 adds the linker row (the reader rows stay)
  linker      it has a round-6/7 linker row on another decision: skipped (one decision under review per court)
No key file.
"""
import collections, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
WORK = os.path.join(HERE, "work")
NL = chr(10)
WEAK = {"A1w", "HM_A1", "A2", "A3"}
REVIEW = {"reversed", "vacated", "affirmed", "modified", "reviewDismissed"}


def main():
    v3 = collections.defaultdict(list)
    with open(os.path.join(C2, "round7", "stage", "v3", "history.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip(NL).split("\t")
            if p[4] in REVIEW:
                v3[int(p[2])].append((int(p[1]), p[12]))
    st = collections.Counter()
    out = []
    for l in open(os.path.join(WORK, "rows_all_off.jsonl"), encoding="utf-8"):
        r = json.loads(l)
        vr = v3.get(r["by"], [])
        if any(t == r["target"] for t, s in vr):
            continue
        if not vr:
            sit = "none"
        elif all(s.startswith("hist-regex") for t, s in vr):
            sit = "reader"
        else:
            st["skip:linker_row_other_target"] += 1
            continue
        typ = r["_typ"]
        if r["_path"] == "strict":
            if typ in WEAK:
                if not (r["_sole"] and r["_latest"] and r.get("_share") and r["_cap"]):
                    st["skip:weak_not_r3"] += 1
                    continue
                cls = "weak_r3"
            else:
                cls = typ.lower()
        else:
            if r.get("_sub") not in ("hm", "zone", "body"):
                st["skip:loose_" + str(r.get("_sub"))] += 1
                continue
            cls = "l_" + r["_sub"]
        if r.get("_dcond") or r.get("_side") or (not r["_before_disp"] and r.get("_sub") != "fn") or \
                (r["_rp"] and (r.get("_name_fail") or not r["ev"].startswith("name:"))):
            st["skip:r7_guard"] += 1
            continue
        if r["_modal"]:
            cls += "_modal"
        x = {k: v for k, v in r.items() if not k.startswith("_")}
        x["rule"] = "below:sc8_r5%s_%s" % ("" if sit == "reader" else "n", cls)
        x["table"] = "history"
        x["claim"] = "-"
        x["note"] = (x.get("note") or "") + "; scdb8 recert " + sit
        st["kept:%s:%s" % (sit, cls)] += 1
        st["kept:" + sit] += 1
        out.append(x)
    with open(os.path.join(HERE, "rows_recert.jsonl"), "w", encoding="utf-8", newline=NL) as f:
        for x in out:
            f.write(json.dumps(x, ensure_ascii=False) + NL)
    json.dump(st, open(os.path.join(WORK, "recert_stats.json"), "w"), indent=1, sort_keys=True)
    print(json.dumps(st, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
