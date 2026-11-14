"""scdb10: post-filter of sc10.py rows -> the rows round 10 may add over the v9c base (from round 9's select9.py).

    python -X utf8 select10.py [--tag x]   -> rows10.jsonl, work/select10_stats.json

Inputs: work/rows_all<tag>.jsonl (sc10 run), round9/stage/v9c/history.tsv. No key file.
Classes (rule id below:sc10_<cls>_l_<sub>):
  a10   R3 rows whose anchor round 10's a10 extension made (the nearest sentence naming the target's court)
  a10t  R3 rows of round 7's left-out sub-rules (nozone, fn) whose anchor quote names the target's court
  a10n  strict rows whose anchor is a citation printed under another caption in the history zone, closing the report
        of the target court's act (sc10 a10n_upgrade); no caption test (the case was decided below under another name)
a10 / a10t (v2): the anchor quote names the target's court as the actor of a judicial act (sc10 act_tie: the court phrase
followed in its clause by a judicial verb, or the agent of a passive judicial verb).
Rows whose judgment reading needs a round-8/9 reading that was not installed (D1/D3/D5, j1-j4) are left out (their
own classes were not installed). Generic guards as select9 (shared party token, docket, conditional, side
proceeding, shared reporter page name evidence, rehearing-denial anchor).
"""
import collections, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
WORK = os.path.join(HERE, "work")
NL = chr(10)
REVIEW = {"reversed", "vacated", "affirmed", "modified", "reviewDismissed"}


def main():
    tag = sys.argv[sys.argv.index("--tag") + 1] if "--tag" in sys.argv else ""
    full = [json.loads(l) for l in open(os.path.join(WORK, "rows_all%s.jsonl" % tag), encoding="utf-8")]
    base = collections.defaultdict(list)
    with open(os.path.join(C2, "round9", "stage", "v9c", "history.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip(NL).split("\t")
            if p[4] in REVIEW:
                base[int(p[2])].append((p[0], int(p[1]), p[4], p[12]))
    st = collections.Counter()
    out = []
    for r in full:
        st["in"] += 1
        if r.get("_a10n"):
            cls = "a10n"
        elif r.get("_a10"):
            cls = "a10"
        elif r.get("_a10tie") and r.get("_path") == "loose" and r.get("_sub") in ("nozone", "fn"):
            cls = "a10t"
        else:
            continue
        st["cand:" + cls] += 1
        if cls != "a10n" and not r.get("_a10act"):
            st["drop:no_court_act:" + cls] += 1
            continue
        vr = base.get(r["by"], [])
        if any(t == r["target"] for _i, t, _k, _s in vr):
            st["skip:in_base:" + cls] += 1
            continue
        if vr:
            st["drop:other_base_row:" + cls] += 1
            continue
        if r.get("_j9") or r.get("_d1"):
            st["drop:uninstalled_judgment_reading:" + cls] += 1
            continue
        if cls != "a10n" and not r.get("_share"):
            st["drop:no_shared_party_token:" + cls] += 1
            continue
        if r.get("_dock") == "drop":
            st["drop:docket_unresolved:" + cls] += 1
            continue
        if isinstance(r.get("_dock"), list):
            r["kind"], r["scope"] = r["_dock"]
        if r.get("_reh9"):
            st["drop:reh9:" + cls] += 1
            continue
        if cls != "a10n" and not (r.get("_sole") and r.get("_latest") and r.get("_cap")):
            st["drop:r3:" + cls] += 1
            continue
        if r.get("_dcond"):
            st["drop:conditional:" + cls] += 1
            continue
        if r.get("_side"):
            st["drop:side_proceeding:" + cls] += 1
            continue
        if r["_rp"] and (r.get("_name_fail") or not r["ev"].startswith("name:")):
            st["drop:rp_name_fail:" + cls] += 1
            continue
        if not r.get("anchor"):
            st["drop:no_anchor_line:" + cls] += 1
            continue
        x = {k: v for k, v in r.items() if not k.startswith("_")}
        x["rule"] = ("below:sc10_a10n_%s" % r["_a10n"]) if cls == "a10n" else "below:sc10_%s_l_%s" % (cls, r.get("_sub"))
        x["table"] = "history"
        x["claim"] = "-"
        x["note"] = (x.get("note") or "") + "; scdb10 " + cls + ((" " + r["_a10why"]) if r.get("_a10why") else "")
        st["kept:" + cls] += 1
        st["kept:%s:%s/%s" % (cls, x["kind"], x["scope"])] += 1
        st["kept:%s:sub_%s" % (cls, r.get("_sub"))] += 1
        out.append(x)
    with open(os.path.join(HERE, "rows10%s.jsonl" % tag), "w", encoding="utf-8", newline=NL) as f:
        for x in out:
            f.write(json.dumps(x, ensure_ascii=False) + NL)
    st["rows"] = len(out)
    json.dump(st, open(os.path.join(WORK, "select10%s_stats.json" % tag), "w"), indent=1, sort_keys=True)
    print(json.dumps(st, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
