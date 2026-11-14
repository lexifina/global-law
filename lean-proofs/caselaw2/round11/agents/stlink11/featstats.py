"""stlink11: tie yields and agreement over work/feat.jsonl (no key)."""
import collections, json, os

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    recs = [json.loads(l) for l in open(os.path.join(HERE, "work", "feat.jsonl"), encoding="utf-8")]
    c = collections.Counter()
    era = collections.defaultdict(collections.Counter)
    xt = collections.Counter()
    agree = collections.Counter()
    for r in recs:
        dec = r["date"] // 100000 * 10
        e = "pre1950" if dec < 1950 else ("1950-89" if dec < 1990 else "1990+")
        cs = [x for x in r.get("cands", []) if "err" not in x]
        c["D"] += 1
        era[e]["D"] += 1
        if r.get("uu"):
            c["D_unique_r10"] += 1
        full = [x for x in cs if x["names"] == "full"]
        best = "full" if full else next((k for k in ("mismatch", "surname_only", "frequent_only", "none", "no_parties")
                                         if any(x["names"] == k for x in cs)), "no_text")
        c["D_names:" + best] += 1
        era[e]["names:" + best] += 1
        for x in cs:
            t2 = [k for k, ok in (("docket", x["docket"] == "strong"), ("docketweak", x["docket"] == "weak"),
                                  ("cite", x["cite"] in ("front", "body")), ("date", x["date"] == "present")) if ok]
            xt[(x["names"], "+".join(t2) or "-")] += 1
        if not full:
            continue
        full.sort(key=lambda x: x["tdate"])
        T = full[-1]
        sib = [x for x in full[:-1] if x["tdate"] == T["tdate"]]
        if sib:
            c["full:sibling_same_date"] += 1
            continue
        t2 = [k for k, ok in (("docket", T["docket"] == "strong"), ("docketweak", T["docket"] == "weak"),
                              ("cite", T["cite"] in ("front", "body")), ("date", T["date"] == "present")) if ok]
        c["full_latest:" + ("+".join(t2) or "-")] += 1
        era[e]["latest_tie:" + ("+".join(t2) or "-")] += 1
        # do ties on earlier full-name candidates point elsewhere?
        for x in full[:-1]:
            if x["docket"] == "strong" or x["cite"] in ("front", "body"):
                agree["earlier_cand_has_docket_or_cite:latest_has:" + ("+".join(t2) or "-")] += 1
                break
        if T["names"] == "full" and T["docket"] in ("strong", "weak"):
            agree["docket_and_cite" if T["cite"] in ("front", "body") else "docket_not_cite"] += 1
        if T["cite"] in ("front", "body"):
            agree["cite_with_t_docket_avail:" + T["docket"]] += 1
            agree["cite_with_t_date:" + T["date"]] += 1
    print("== counts")
    for k, v in sorted(c.items()):
        print(k, v)
    print("== by era")
    for e in sorted(era):
        print(e, dict(sorted(era[e].items())))
    print("== names x ties (all candidates)")
    for k, v in sorted(xt.items(), key=lambda kv: -kv[1])[:40]:
        print(k, v)
    print("== agreement")
    for k, v in sorted(agree.items()):
        print(k, v)


if __name__ == "__main__":
    main()
