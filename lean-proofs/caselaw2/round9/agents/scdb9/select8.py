"""scdb8: post-filter of sc8.py rows -> the rows round 8 may add, and the v3 rows the R4 rule replaces.

    python -X utf8 select8.py   -> rows8.jsonl, remove_r4.txt (v3 history ids replaced), work/select_stats.json

Inputs: work/rows_all.jsonl (sc8 with every round-8 rule), work/rows_all_off.jsonl (sc8 with the round-8 rules off =
round 6 + round 7 linkers), round7/stage/v3/history.tsv. No key file.
A row is NEW when the same (by, target, kind) is not in the rules-off run (the round-8 rules made it). Then:
  in_v3              the (by, target) pair already has a review-kind row in v3: nothing added
  r4_replace         the acting opinion has v3 review rows on another decision; the new row's target is an earlier
                     decision of the same court and every such v3 target is one the R4 rule now reads as a rehearing
                     denial order (the rules-off run targeted it): the new row is added and those v3 rows (made by the
                     round-6/7 below_sc linkers) are removed (remove_r4.txt)
  other_v3_row       the acting opinion has v3 review rows on another decision (not R4): nothing added
  weak_not_r3        a weak anchor type (A1w, HM_A1, A2, A3) that fails round 7's R3 test (sole + latest + share + cap)
  loose_nozone_fn    a round-7 R3 row of the sub-classes round 7 left out (nozone, fn)
  conditional / side_proceeding / footnote / rp_name_fail: round 7's guards, unchanged
Classes (rule ids below:sc8_<cls>): disp (D1-D5 judgment readings) / r4 (rehearing denial skipped) / r4rep (R4 replace).
"""
import collections, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
WORK = os.path.join(HERE, "work")
NL = chr(10)
WEAK = {"A1w", "HM_A1", "A2", "A3"}
REVIEW = {"reversed", "vacated", "affirmed", "modified", "reviewDismissed"}
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import r6lib as L  # noqa: E402


def load(p):
    return [json.loads(l) for l in open(p, encoding="utf-8")]


def main():
    F = L.Facts()
    wide = "--wide" in sys.argv
    full = load(os.path.join(WORK, "rows_all_aw.jsonl" if wide else "rows_all.jsonl"))
    off = load(os.path.join(WORK, "rows_all_off.jsonl"))
    off_k = {(r["by"], r["target"], r["kind"]) for r in off}
    if wide:
        # W: rows that only the claim-gated wide cue list makes (not made by the full run without it)
        off_k |= {(r["by"], r["target"], r["kind"]) for r in load(os.path.join(WORK, "rows_all.jsonl"))}
    off_by_t = collections.defaultdict(set)
    for r in off:
        off_by_t[r["by"]].add(r["target"])
    v3 = collections.defaultdict(list)
    with open(os.path.join(C2, "round7", "stage", "v3", "history.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip(NL).split("\t")
            if p[4] in REVIEW:
                v3[int(p[2])].append((p[0], int(p[1]), p[4], p[12]))
    # class attribution: which round-8 rule the row needs (leave-one-out runs; absent run file = not used)
    loo = {}
    for tag, c in (("_noD", "disp"), ("_noA", "anchor"), ("_noT", "trial"), ("_noR", "r4")):
        pth = os.path.join(WORK, "rows_all%s.jsonl" % tag)
        if os.path.exists(pth):
            loo[c] = {(r["by"], r["target"], r["kind"]) for r in load(pth)}
    st = collections.Counter()
    out, remove = [], []
    for r in full:
        st["in"] += 1
        okind = r["kind"]
        if (r["by"], r["target"], r["kind"]) in off_k:
            st["skip:not_new"] += 1
            continue
        st["new"] += 1
        vr = v3.get(r["by"], [])
        cls = "disp"
        rem = []
        if any(t == r["target"] for _i, t, _k, _s in vr):
            st["drop:in_v3"] += 1
            continue
        if vr:
            others = {t for _i, t, _k, _s in vr}
            ok = all(int(F.court[t]) == int(F.court[r["target"]]) and int(F.date[t]) > int(F.date[r["target"]]) and
                     t in off_by_t[r["by"]] for t in others)
            linker = all(s.startswith("r6:below:sc_") or s.startswith("r7:below:sc7_") for _i, _t, _k, s in vr)
            if ok and linker:
                cls = "r4rep"
                rem = [i for i, _t, _k, _s in vr]
            else:
                st["drop:other_v3_row"] += 1
                continue
        if not r.get("_share"):
            st["drop:no_shared_party_token"] += 1
            continue
        if r.get("_dock") == "drop":
            st["drop:docket_unresolved"] += 1
            continue
        if isinstance(r.get("_dock"), list):
            r["kind"], r["scope"] = r["_dock"]
            st["docket_resolved"] += 1
        typ = r["_typ"]
        if r["_path"] == "strict" and typ in WEAK and not (r["_sole"] and r["_latest"] and r.get("_share") and r["_cap"]):
            st["drop:weak_not_r3"] += 1
            continue
        if r["_path"] == "loose" and r.get("_sub") in ("nozone", "fn"):
            st["drop:loose_nozone_fn"] += 1
            continue
        if r.get("_dcond"):
            st["drop:conditional"] += 1
            continue
        if r.get("_side"):
            st["drop:side_proceeding"] += 1
            continue
        if not r["_before_disp"] and r.get("_sub") != "fn":
            st["drop:footnote"] += 1
            continue
        if r["_rp"] and (r.get("_name_fail") or not r["ev"].startswith("name:")):
            st["drop:rp_name_fail"] += 1
            continue
        if wide:
            cls = "wide" if cls == "disp" else cls + "w"
        elif cls == "disp" and loo:
            key = (r["by"], r["target"], okind)
            need = [c for c, ks in loo.items() if key not in ks]
            cls = need[0] if len(need) == 1 else ("multi" if need else "joint")
        elif cls == "disp" and off_by_t.get(r["by"]) and r["target"] not in off_by_t[r["by"]]:
            cls = "r4"
        sub = (typ.lower() if r["_path"] == "strict" else "l_" + r["_sub"])
        x = {k: v for k, v in r.items() if not k.startswith("_")}
        x["rule"] = "below:sc8_%s_%s" % (cls, sub)
        x["table"] = "history"
        x["claim"] = "anchorWide" if wide else "-"
        x["note"] = (x.get("note") or "") + "; scdb8 " + cls
        st["kept:" + cls] += 1
        st["kept:%s:%s" % (cls, sub)] += 1
        st["kept:%s/%s" % (x["kind"], x["scope"])] += 1
        out.append(x)
        remove.extend(rem)
    sfx = "_w" if wide else ""
    with open(os.path.join(HERE, "rows8%s.jsonl" % sfx), "w", encoding="utf-8", newline=NL) as f:
        for x in out:
            f.write(json.dumps(x, ensure_ascii=False) + NL)
    with open(os.path.join(HERE, "remove_r4%s.txt" % sfx), "w", encoding="utf-8", newline=NL) as f:
        for i in sorted(set(remove)):
            f.write(i + NL)
    st["rows"] = len(out)
    st["remove_ids"] = len(set(remove))
    json.dump(st, open(os.path.join(WORK, "select_stats%s.json" % sfx), "w"), indent=1, sort_keys=True)
    print(json.dumps(st, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
