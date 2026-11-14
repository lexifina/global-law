"""Round 8 blind audit: the decoy pools (items whose right answer is known from earlier audits). Port of
round7/audit/decoys7.py (round-5 and round-6 pools rebuilt the same way) plus the round-7 audited rows.

    python -X utf8 round8/audit/decoys8.py [--min-conf medium] [--out-dir round8/audit] [--no-r7]

Type A (treatments: what a court does or says about decision X), from the round-5 blind audits round5/audit/*/
(key.tsv + answers/*.jsonl):
  wrong  a sampled row that every answer rejected on `stated`, `x_ok` or `y_ok` (an extent-only failure is not
         used); a decoy of that audit (synthetic wrong-X / wrong-Y item, or a reader answer judged not a statement)
         that no answer accepted
  right  a sampled row that every answer confirmed with its extent (right_and_extent): self-announced controls
         ("X is overruled" in the court's own words), recognised rows, operative rows
Type B (history: what a court did to a decision under review), from the round-6 blind audits
round6/history/audit/{v1,v2,r1,a3}/ (sample.tsv + verdicts_*.jsonl, judged with the round-6 rules):
  wrong  a sampled row that every verdict found not linked (same case and acted on), none unsure, confidence at
         least --min-conf; a wrong-target decoy that every verdict rejected (shown with the source row's passage)
  right  a sampled row that every verdict confirmed with kind and scope, all with high confidence; a base-table
         control that every verdict confirmed with its kind, all with high confidence

Types A and B, from the round-7 blind audits round7/audit/r7a*/ (sample.tsv + answers/*.jsonl, judged with
score_audit8's rules = the round-7 rules, by_match_overrides.tsv honoured; sampled rows only, the round-7 decoys came
from the pools above):
  wrong  A: every answer not `right` (failed on x, own, act or by; never extent-only), no `unsure` in speaks_of_x /
         own_opinion / act, confidence at least --min-conf; B: every answer not linked, none unsure, confidence at
         least --min-conf
  right  every answer right + extent, all with high confidence
  The row (quotes, joined / anchor spans, text sha) is reloaded from the run's own --cert inputs (manifest.json).

Writes decoy_pool_A.jsonl, decoy_pool_B.jsonl and decoy_pool_summary.tsv. One pool line:
  {"did", "type", "family", "truth": right|wrong, "how", "row_id", "speaker" (A: the decision whose text is shown),
   "by", "target", "y", "kind", "scope", "effect" (A), "text_sha", "spans": [[s, e], ...] (main quote first),
   "quotes", "conf", "why"}
`why` (the earlier auditor's words) stays in the pool and the key; it never reaches a pack.
Nothing under gold/, round5/gold_fresh/, round6/shepardized/, split/, round7/heldout/ or benchmarks/ is read.
"""
import argparse
import glob
import json
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit8lib as A  # noqa: E402

CONF_RANK = {"low": 0, "medium": 1, "high": 2}


# ---- round 5 (type A) ----------------------------------------------------------------------------------------------
def r5_answer(v):
    st = v.get("stated", v.get("states"))
    st = "yes" if st is True else "no" if st is False else str(st).strip().lower()
    ex = str(v.get("extent", "")).strip().lower().replace(" ", "").replace("_", "")
    ex = {"all": "whole", "partial": "part", "inpart": "part", "othergrounds": "otherGrounds"}.get(ex, ex)

    def b(x):
        return x if isinstance(x, bool) else str(x).strip().lower() in ("true", "yes", "1", "y")
    return {"stated": st, "x_ok": b(v.get("x_ok", False)), "y_ok": b(v.get("y_ok", False)), "extent": ex,
            "words": str(v.get("words", "")), "note": str(v.get("note", ""))}


def r5_pool():
    out, seen = [], set()
    for kp in sorted(glob.glob(os.path.join(A.R5A, "*", "key.tsv"))):
        adir = os.path.dirname(kp)
        name = os.path.basename(adir)
        kr = A.read_tsv(kp)
        if not kr:
            continue
        head = kr[0]
        key = {r[0]: dict(zip(head, r + [""] * (len(head) - len(r)))) for r in kr[1:]}
        ans = {}
        for fp in sorted(glob.glob(os.path.join(adir, "answers", "*.jsonl"))):
            for v in A.read_jsonl(fp):
                i = str(v.get("id", v.get("item", "")))
                if i in key:
                    ans.setdefault(i, {})[os.path.basename(fp)] = r5_answer(v)  # last answer of a file wins
        for i, k in key.items():
            xs = list(ans.get(i, {}).values())
            dec = k.get("decoy") == "1"
            y = k.get("y", "-")
            y = int(y) if y not in ("", "-") else -1
            right = [x["stated"] == "yes" and x["x_ok"] and x["y_ok"] for x in xs]
            rext = [r and (k.get("scope_class") != "all" or x["extent"] == "whole") for r, x in zip(right, xs)]
            core_fail = [x["stated"] != "yes" or not x["x_ok"] or not x["y_ok"] for x in xs]
            if dec:
                if any(right):
                    continue
                truth, how = "wrong", ("synthetic" if "synthetic" in k.get("note", "") else "reader-rejected")
                eff = "report_part" if y >= 0 else "own_part"
                fam = "r5:%s:decoy" % name
            else:
                if not xs:
                    continue
                if all(rext):
                    truth, how = "right", "audited"
                elif all(core_fail):
                    truth, how = "wrong", "audited"
                else:
                    continue
                wit = k.get("witness_row") == "1"
                whole = k.get("scope_class") == "all"
                eff = ("report_" if wit else "own_") + ("whole" if whole else "part")
                fam = "r5:%s:%s" % (name, k.get("stratum", ""))
            try:
                sp, x, s, e = int(k["speaker"]), int(k["x"]), int(k["start"]), int(k["end"])
            except (KeyError, ValueError):
                continue
            did = "r5:%s:%s" % (name, i)
            if did in seen:
                continue
            seen.add(did)
            why = " || ".join("%s/%s/%s/%s: %s %s" % (x["stated"], "T" if x["x_ok"] else "F",
                                                      "T" if x["y_ok"] else "F", x["extent"], x["words"], x["note"])
                              for x in xs) or k.get("note", "")
            out.append({"did": did, "type": "A", "family": fam, "truth": truth, "how": how,
                        "row_id": k.get("treatment_id", ""), "speaker": sp, "by": y if y >= 0 else sp,
                        "target": x, "y": y, "kind": k.get("kind", "-"), "scope": k.get("scope", "-"), "effect": eff,
                        "text_sha": k.get("text_sha", ""), "spans": [[s, e]], "quotes": [""],
                        "conf": "-", "why": why[:600]})
    return out


# ---- round 6 (type B) ----------------------------------------------------------------------------------------------
def b_norm(v):
    def y(name, default="unsure"):
        r = A.ynu(v.get(name))
        return r if r else default
    d = str(v.get("disposition", "")).strip().lower().replace(" ", "_").replace("-", "_")
    if d not in A.DISPOSITIONS:
        d = "other"
    return {"same_case": y("same_case"), "acted_on": y("acted_on"), "disposition": d,
            "whole": "yes" if y("whole", "no") == "yes" else "no",
            "confidence": str(v.get("confidence", "")).strip().lower(), "note": str(v.get("note", "")),
            "evidence": str(v.get("evidence", ""))}


def b_judge(kind, scope, v):
    link = v["same_case"] == "yes" and v["acted_on"] == "yes"
    d = v["disposition"]
    kind_ok = d in A.B_COMPAT.get(kind, set()) or (scope != "all" and d in A.B_COMPAT_PARTIAL.get(kind, set()))
    scope_ok = scope != "all" or v["whole"] == "yes"
    return {"link": link, "link_kind": link and kind_ok, "link_kind_scope": link and kind_ok and scope_ok}


def r6_rows(paths, want):
    """{row id: (row, anchor)} for the wanted ids from history tables (and their anchor side tables)."""
    got = {}
    for p in paths:
        if not p or not os.path.exists(p):
            continue
        for q in A.read_tsv(p):
            if q[0] in want and q[0] not in got:
                r = A.hist_row(q)
                if r:
                    got[q[0]] = [r, None]
        ap = os.path.join(os.path.dirname(p), "history_anchor_delta.tsv")
        for q in A.read_tsv(ap):
            if q[0] in got and got[q[0]][1] is None and len(q) >= 5:
                try:
                    got[q[0]][1] = (int(q[1]), int(q[2]), q[3])
                except ValueError:
                    pass
    return got


def r6_pool(min_conf):
    out = []
    for sp in sorted(glob.glob(os.path.join(A.R6A, "*", "sample.tsv"))):
        rdir = os.path.dirname(sp)
        run = os.path.basename(rdir)
        man = {}
        if os.path.exists(os.path.join(rdir, "manifest.json")):
            man = json.load(open(os.path.join(rdir, "manifest.json"), encoding="utf-8"))
        if man.get("self_test"):
            continue
        kr = A.read_tsv(sp)
        head = kr[0]
        key = {r[0]: dict(zip(head, r + [""] * (len(head) - len(r)))) for r in kr[1:]}
        ver = {}
        for vp in sorted(glob.glob(os.path.join(rdir, "verdicts_*.jsonl"))):
            seen = set()
            for v in A.read_jsonl(vp):
                i = str(v.get("item", ""))
                if i in key and i not in seen:
                    seen.add(i)
                    ver.setdefault(i, []).append(b_norm(v))
        cand = []
        for i, k in key.items():
            vs = ver.get(i)
            if not vs:
                continue
            role = k["role"]
            conf_min = min(CONF_RANK.get(v["confidence"], 0) for v in vs)
            unsure = any("unsure" in (v["same_case"], v["acted_on"]) for v in vs)
            if role == "real":
                js = [b_judge(k["kind"], k["scope"], v) for v in vs]
                if all(not j["link"] for j in js) and not unsure and conf_min >= CONF_RANK[min_conf]:
                    cand.append((i, k, "wrong", "audited", k["row_id"], int(k["target_node"]), vs))
                elif all(j["link_kind_scope"] for j in js) and conf_min >= CONF_RANK["high"]:
                    cand.append((i, k, "right", "audited", k["row_id"], int(k["target_node"]), vs))
            elif role == "decoy_wrong":
                js = [b_judge("other", "unknown", v) for v in vs]
                if all(not j["link"] for j in js):
                    cand.append((i, k, "wrong", "wrong-target", k["source_row"], int(k["target_node"]), vs))
            elif role == "decoy_base":
                js = [b_judge(k["kind"], k["scope"], v) for v in vs]
                if all(j["link_kind"] for j in js) and conf_min >= CONF_RANK["high"]:
                    cand.append((i, k, "right", "base-control", k["row_id"], int(k["target_node"]), vs))
        paths = [x["delta"] for x in man.get("inputs", [])]
        if man.get("base"):
            paths.append(man["base"])
        rows = r6_rows(paths, {c[4] for c in cand})
        for i, k, truth, how, rid, target, vs in cand:
            if rid not in rows:
                continue
            r, anc = rows[rid]
            spans, quotes = [[r["start"], r["end"]]], [r["quote"]]
            if anc:
                spans.append([anc[0], anc[1]])
                quotes.append(anc[2])
            kind = r["kind"] if how != "wrong-target" else "-"
            why = " || ".join("%s/%s/%s/%s/%s: %s" % (v["same_case"], v["acted_on"], v["disposition"], v["whole"],
                                                      v["confidence"], v["note"]) for v in vs)
            out.append({"did": "r6:%s:%s" % (run, i), "type": "B",
                        "family": "r6:%s:%s" % (run, k["class"] if k["role"] == "real" else k["role"]),
                        "truth": truth, "how": how, "row_id": rid, "speaker": -1, "by": r["by"], "target": target,
                        "y": -1, "kind": kind, "scope": r["scope"] if how != "wrong-target" else "unknown",
                        "effect": "-", "text_sha": r["text_sha"], "spans": spans, "quotes": quotes,
                        "conf": min((v["confidence"] for v in vs), key=lambda c: CONF_RANK.get(c, 0)),
                        "why": why[:600]})
    return out


def r7_pool(min_conf):
    import score_audit8 as S
    out, seen_rows = [], set()
    for sp in sorted(glob.glob(os.path.join(A.R7A, "r7a*", "sample.tsv"))):
        rdir = os.path.dirname(sp)
        run = os.path.basename(rdir)
        mp = os.path.join(rdir, "manifest.json")
        if not os.path.exists(mp):
            continue
        man = json.load(open(mp, encoding="utf-8"))
        if man.get("self_test"):
            continue
        kr = A.read_tsv(sp)
        head = kr[0]
        key = {r[0]: dict(zip(head, r + [""] * (len(head) - len(r)))) for r in kr[1:]}
        overrides = {}
        for p in A.read_tsv(os.path.join(rdir, "by_match_overrides.tsv"), 3):
            overrides[(p[0], p[1])] = p[2].strip().lower()
        ans = {}
        for fp in sorted(glob.glob(os.path.join(rdir, "answers", "*.jsonl"))):
            fn = os.path.basename(fp)
            seen = set()
            for v in A.read_jsonl(fp):
                i = str(v.get("item", v.get("id", "")))
                if i not in key or i in seen or key[i]["role"] != "real":
                    continue
                seen.add(i)
                k = key[i]
                if k["type"] == "A":
                    x, _bad = S.norm_a(v)
                    j = S.judge_a(k, x, overrides.get((i, fn), overrides.get((i, "*"))))
                    unsure = "unsure" in (x["speaks_of_x"], x["own_opinion"], x["act"])
                else:
                    x, _bad = S.norm_b(v)
                    j = S.judge_b(k, x)
                    unsure = "unsure" in (x["same_case"], x["acted_on"])
                ans.setdefault(i, []).append((x, j, unsure))
        cand = {}
        for i, xs in ans.items():
            k = key[i]
            conf_min = min(CONF_RANK.get(x["confidence"], 0) for x, _j, _u in xs)
            if all(j["right_extent"] for _x, j, _u in xs) and conf_min >= CONF_RANK["high"]:
                truth = "right"
            elif not any(u for _x, _j, u in xs) and conf_min >= CONF_RANK[min_conf] and                     all(not (j["right"] if k["type"] == "A" else j["link"]) for _x, j, _u in xs):
                truth = "wrong"
            else:
                continue
            if k["row_id"] in seen_rows:
                continue
            cand[k["row_id"]] = (i, k, truth, xs)
        if not cand:
            continue
        rows = {}
        for c in man.get("args", {}).get("cert", []):
            try:
                rs, _info = A.load_cert(A.resolve(c), set(cand) - set(rows))
            except SystemExit:
                continue
            for r in rs:
                rows.setdefault(r["id"], r)
        for rid, (i, k, truth, xs) in sorted(cand.items()):
            r = rows.get(rid)
            if r is None:
                continue
            seen_rows.add(rid)
            spans, quotes = [[r["start"], r["end"]]], [r["quote"]]
            if k["type"] == "A":
                for jn in r.get("joined") or []:
                    spans.append([jn[1], jn[2]])
                    quotes.append(jn[3])
            elif r.get("anchor"):
                spans.append([r["anchor"][0], r["anchor"][1]])
                quotes.append(r["anchor"][2])
            if k["type"] == "A":
                why = " || ".join("%s/%s/%s/%s/%s: %s %s" % (x["speaks_of_x"], x["act"], x["extent"], x["own_opinion"],
                                                            x["confidence"], x["words"], x["note"]) for x, _j, _u in xs)
            else:
                why = " || ".join("%s/%s/%s/%s/%s: %s" % (x["same_case"], x["acted_on"], x["disposition"], x["whole"],
                                                         x["confidence"], x["note"]) for x, _j, _u in xs)
            y = A._int(k["y_node"], -1)
            out.append({"did": "r7:%s:%s" % (run, i), "type": k["type"], "family": "r7:%s:%s" % (run, k["class"]),
                        "truth": truth, "how": "audited", "row_id": rid,
                        "speaker": int(k["shown_node"]) if k["type"] == "A" else -1,
                        "by": r["by"], "target": r["target"], "y": y, "kind": r["kind"], "scope": r["scope"],
                        "effect": k["effect"] if k["type"] == "A" else "-", "text_sha": r["text_sha"],
                        "spans": spans, "quotes": quotes,
                        "conf": min((x["confidence"] for x, _j, _u in xs), key=lambda c: CONF_RANK.get(c, 0)),
                        "why": why[:600]})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-conf", default="medium", choices=("low", "medium", "high"))
    ap.add_argument("--out-dir", default="round8/audit")
    ap.add_argument("--no-r7", action="store_true")
    a = ap.parse_args()
    A.utf8_stdout()
    od = A.resolve(a.out_dir, must_exist=False)
    A.must_be_under_audit(os.path.join(od, "x"))
    pa, pb = r5_pool(), r6_pool(a.min_conf)
    if not a.no_r7:
        for d in r7_pool(a.min_conf):
            (pa if d["type"] == "A" else pb).append(d)
    summ = [["type", "family", "truth", "how", "items"]]
    for typ, pool in (("A", pa), ("B", pb)):
        A.write_text(os.path.join(od, "decoy_pool_%s.jsonl" % typ),
                     "".join(json.dumps(d, ensure_ascii=False) + A.NL for d in pool))
        c = {}
        for d in pool:
            c[(d["family"], d["truth"], d["how"])] = c.get((d["family"], d["truth"], d["how"]), 0) + 1
        for (f, t, h), n in sorted(c.items()):
            summ.append([typ, f, t, h, n])
        print("type %s: %d decoys (%d known wrong, %d known right)" % (
            typ, len(pool), sum(1 for d in pool if d["truth"] == "wrong"), sum(1 for d in pool if d["truth"] == "right")))
    A.write_tsv(os.path.join(od, "decoy_pool_summary.tsv"), summ)
    for r in summ[1:]:
        print("  " + "\t".join(str(x) for x in r))


if __name__ == "__main__":
    main()
