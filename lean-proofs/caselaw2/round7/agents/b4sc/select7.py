"""b4sc: post-filter of sc7.py rows -> the rows round 7 may add (DESIGN7 section 4 layout).

    python -X utf8 select7.py   -> rows_a.jsonl (B4 a), rows_e.jsonl (B4 e), work/select_stats.json

Drops (counted):
  in_final2        the acting decision already has a review-kind history row in the round-6 frozen build
  r6_class         a row round 6's own rules make (A1 / head-matter syllabus / reported-below) that is neither
                   re-pointed (R1) nor read from a modal judgment line (R2): round 6 made the call on it
  weak_not_r3      a weak anchor type (A1w, HM_A1, A2, A3) that fails the R3 test (sole + latest + shared token)
  footnote         the anchor (or the citation) is not before the judgment quote
  name_fail        a re-pointed row without an anchor quote holding the shared caption tokens
Classes (rule ids, for the audit): below:sc7_rp_* (R1, B4 e), below:sc7_modal_* (R2), below:sc7_weak_r3 (weak anchor +
R3), below:sc7_l_<hm|zone|body|nozone> (R3 selection).
"""
import collections, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "work")
WEAK = {"A1w", "HM_A1", "A2", "A3"}


def main():
    by_f2 = json.load(open(os.path.join(WORK, "final2_by.json")))
    st = collections.Counter()
    out_a, out_e = [], []
    for line in open(os.path.join(WORK, "rows_all.jsonl"), encoding="utf-8"):
        r = json.loads(line)
        st["in"] += 1
        if str(r["by"]) in by_f2:
            st["drop:in_final2"] += 1
            if r["_rp"]:
                st["rp_but_in_final2"] += 1
            continue
        typ = r["_typ"]
        if r["_path"] == "strict":
            if r["_rp"]:
                cls = "rp_" + typ.lower()
            elif r["_modal"] and typ not in WEAK:
                cls = "modal_" + typ.lower()
            elif typ in WEAK:
                if not (r["_sole"] and r["_latest"] and r.get("_share") and r["_cap"]):
                    st["drop:weak_not_r3"] += 1
                    continue
                cls = "weak_r3" + ("_modal" if r["_modal"] else "")
            else:
                st["drop:r6_class"] += 1
                continue
        else:
            cls = ("rp_" if r["_rp"] else "") + "l_" + r["_sub"] + ("_modal" if r["_modal"] else "")
        if r.get("_dcond"):
            st["drop:conditional_judgment_sentence"] += 1
            continue
        if r.get("_side"):
            st["drop:side_proceeding"] += 1
            continue
        if not r["_before_disp"] and r.get("_sub") != "fn":
            st["drop:footnote"] += 1
            continue
        if r["_rp"] and (r.get("_name_fail") or not r["ev"].startswith("name:")):
            st["drop:name_fail"] += 1
            continue
        x = {k: v for k, v in r.items() if not k.startswith("_")}
        x["rule"] = "below:sc7_" + cls
        x["table"] = "history"
        x["claim"] = "-"
        x["note"] = (x.get("note") or "") + "; b4sc " + cls
        st["kept:" + cls] += 1
        st["kept:%s/%s" % (x["kind"], x["scope"])] += 1
        (out_e if r["_rp"] else out_a).append(x)
    for name, rows in (("rows_a.jsonl", out_a), ("rows_e.jsonl", out_e)):
        with open(os.path.join(HERE, name), "w", encoding="utf-8", newline="\n") as f:
            for x in rows:
                f.write(json.dumps(x, ensure_ascii=False) + "\n")
    st["rows_a"], st["rows_e"] = len(out_a), len(out_e)
    json.dump(st, open(os.path.join(WORK, "select_stats.json"), "w"), indent=1, sort_keys=True)
    print(json.dumps(st, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
