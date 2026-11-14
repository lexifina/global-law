"""Round 9 blind audit, step 3: join the auditors' answers to the key and score them. Port of
round7/audit/score_audit7.py (same measures) plus the pair form (type C).

    python -X utf8 round9/audit/score_audit9.py <run> [--threshold 0.90]

Reads <run>/sample.tsv (the key), strata.tsv, manifest.json and every <run>/answers/*.jsonl (one file per reader;
a reader may answer one pack or several). Optional <run>/by_match_overrides.tsv (item, answer file or *, yes|no):
the lead's decision whether a reader's `other_decision` names the row's Y, where the automatic match is wrong.

Type A answer: {"item", "speaks_of_x", "act", "extent", "own_opinion", "other_decision", "doctrine", "words",
                "confidence", "note"}
  right         speaks_of_x yes AND own_opinion yes AND act agrees with the row's effect class
                (audit9lib.A_COMPAT: own_whole -> overrule; own_part -> overrule | reject_doctrine; doctrine ->
                reject_doctrine | overrule; report_* -> report_other AND other_decision names the row's Y)
  right_extent  right AND (effect own_whole / report_whole => extent whole)
Type B answer: the round-6 verdict {"item", "same_case", "acted_on", "disposition", "whole", "evidence",
                "confidence", "note"}
  link          same_case yes AND acted_on yes
  right         link AND the disposition agrees with the row's kind (audit9lib.B_COMPAT, B_COMPAT_PARTIAL)
  link_effect   link AND the disposition has the row's status effect (reversed ~ vacated ~ withdrawn)
  right_extent  right AND (scope `all` => whole yes)
Type C (pair form, make_packs9 --pairs): the type-B answer, judged against row 1 (the measures above: right,
  right_extent, link, link_effect) and against row 2 (row2_right, row2_right_extent, row2_link_effect); only1_right
  = row 1 right and row 2 not, only2_right = row 2 right and row 1 not. The class flag is on row 1's `right`.
`unsure` never counts as right. An item read by several readers: a measure holds only if it holds for every reader
(the strict reading); agreement is reported.
Decoys: a known-wrong decoy is answered accurately when the reader does not confirm it (type A: not `right` against
the decoy's own claim; type B: not `link`); a known-right decoy when the reader confirms it (`right`). Accuracy per
pack, per answer file (= per reader) and per decoy family.
Per class: pooled Wilson 95% intervals, by federal / state, by decade, per stratum, and a corpus-weighted estimate
(strata weighted by their population; Wilson at the Kish effective sample size, finite-population corrected).
Writes <run>/score.json, score.md and errors.tsv (every reader answer on a real row that is not right_extent, and
every inaccurate decoy answer, with the reader's words and note).
"""
import argparse
import glob
import json
import os
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit9lib as A  # noqa: E402

EXT = {"whole": "whole", "all": "whole", "part": "part", "partial": "part", "in_part": "part",
       "other_grounds": "other_grounds", "othergrounds": "other_grounds", "unclear": "unclear", "": "unclear",
       "none": "unclear", "unknown": "unclear"}


# ---- answers -------------------------------------------------------------------------------------------------------
def norm_a(v):
    bad = []

    def y(name):
        r = A.ynu(v.get(name))
        if r is None:
            bad.append("%s=%r read as unsure" % (name, v.get(name)))
            return "unsure"
        return r
    act = str(v.get("act", "")).strip().lower().replace(" ", "_").replace("-", "_")
    if act not in A.ACTS:
        bad.append("act=%r read as unsure" % v.get("act"))
        act = "unsure"
    ex = str(v.get("extent", "")).strip().lower().replace(" ", "_").replace("-", "_")
    if ex not in EXT:
        bad.append("extent=%r read as unclear" % v.get("extent"))
    return {"speaks_of_x": y("speaks_of_x"), "act": act, "extent": EXT.get(ex, "unclear"),
            "own_opinion": y("own_opinion"), "other_decision": str(v.get("other_decision") or ""),
            "doctrine": str(v.get("doctrine") or ""), "words": str(v.get("words") or ""),
            "confidence": str(v.get("confidence") or "").strip().lower(), "note": str(v.get("note") or "")}, bad


def norm_b(v):
    bad = []

    def y(name, default="unsure"):
        r = A.ynu(v.get(name))
        if r is None:
            bad.append("%s=%r read as %s" % (name, v.get(name), default))
            return default
        return r
    d = str(v.get("disposition", "")).strip().lower().replace(" ", "_").replace("-", "_")
    if d not in A.DISPOSITIONS:
        bad.append("disposition=%r read as other" % v.get("disposition"))
        d = "other"
    return {"same_case": y("same_case"), "acted_on": y("acted_on"), "disposition": d,
            "whole": "yes" if y("whole", "no") == "yes" else "no",
            "confidence": str(v.get("confidence") or "").strip().lower(), "evidence": str(v.get("evidence") or ""),
            "note": str(v.get("note") or "")}, bad


def judge_a(k, v, override=None):
    eff = k["effect"]
    act_ok = v["act"] in A.A_COMPAT.get(eff, set())
    by_ok, by_how = True, ""
    if eff.startswith("report"):
        if override in ("yes", "no"):
            by_ok, by_how = override == "yes", "override"
        else:
            txt = v["other_decision"] or v["words"]
            m, by_how = A.by_match(txt, [c for c in k["y_cites"].split(" | ") if c], k["y_name"])
            by_ok = m == "yes"
    right = v["speaks_of_x"] == "yes" and v["own_opinion"] == "yes" and act_ok and by_ok
    rext = right and (eff not in A.A_NEEDS_WHOLE or v["extent"] == "whole")
    fail = []
    if v["speaks_of_x"] != "yes":
        fail.append("x")
    if v["own_opinion"] != "yes":
        fail.append("own")
    if not act_ok:
        fail.append("act")
    if not by_ok:
        fail.append("by")
    if right and not rext:
        fail.append("extent")
    return {"right": right, "right_extent": rext, "link": v["speaks_of_x"] == "yes", "by_how": by_how,
            "fail": "+".join(fail)}


def judge_b(k, v):
    kind, scope, d = k["kind"], k["scope"], v["disposition"]
    link = v["same_case"] == "yes" and v["acted_on"] == "yes"
    kind_ok = d in A.B_COMPAT.get(kind, set()) or (scope != "all" and d in A.B_COMPAT_PARTIAL.get(kind, set()))
    part_ok = scope != "all" and d == "reversed_or_vacated_in_part"
    if kind == "rehearingEnBancGranted":
        eff_ok = kind_ok
    elif kind in A.H_STATUS:
        eff_ok = d in A.B_NEGATIVE or part_ok
    else:
        eff_ok = d in A.B_NEUTRAL or kind_ok
    scope_ok = scope != "all" or v["whole"] == "yes"
    right = link and kind_ok
    fail = "link" if not link else "kind" if not kind_ok else "scope" if not scope_ok else ""
    if fail == "kind" and eff_ok:
        fail = "kind (same status effect)"
    return {"right": right, "right_extent": right and scope_ok, "link": link, "link_effect": link and eff_ok,
            "by_how": "", "fail": fail}


def judge_c(k, v):
    j1 = judge_b(k, v)
    j2 = judge_b(dict(k, kind=k["kind2"], scope=k["scope2"]), v)
    j1.update({"row2_right": j2["right"], "row2_right_extent": j2["right_extent"],
               "row2_link_effect": j2["link_effect"], "only1_right": j1["right"] and not j2["right"],
               "only2_right": j2["right"] and not j1["right"]})
    if j2["fail"] and j1["fail"]:
        j1["fail"] += "; row 2: " + j2["fail"]
    return j1


C_MEAS = ("row2_right", "row2_right_extent", "row2_link_effect", "only1_right", "only2_right")


def accurate(k, j):
    if k["role"] == "decoy_wrong":
        return not (j["link"] if k["type"] == "B" else j["right"])
    if k["role"] == "decoy_right":
        return j["right"]
    return None


# ---- statistics ----------------------------------------------------------------------------------------------------
def rate(k, n):
    p, lo, hi = A.wilson(k, n)
    r4 = lambda x: None if x is None else round(x, 4)  # noqa: E731
    return {"k": k, "n": n, "p": r4(p), "lo": r4(lo), "hi": r4(hi)}


def show(r):
    if not r or not r.get("n"):
        return "-"
    return "%d/%d = %.3f [%.3f, %.3f]" % (r["k"], r["n"], r["p"], r["lo"], r["hi"])


MEAS = ("right", "right_extent", "link")


def block(items, meas):
    b = {"n": len(items)}
    for m in meas:
        b[m] = rate(sum(1 for it in items if it["j"][m]), len(items))
    return b


def decade_num(s):
    try:
        return int(s.rstrip("s"))
    except ValueError:
        return None


def nearest(s, answered):
    sy, dec = s.split("|")
    best, bt = None, None
    for t in answered:
        sy2, dec2 = t.split("|")
        a, b = decade_num(dec), decade_num(dec2)
        dist = abs(a - b) if a is not None and b is not None else 500
        sc = (0 if sy2 == sy else 1, dist, t)
        if best is None or sc < best:
            best, bt = sc, t
    return bt


def weighted(by_stratum, popn, measure):
    ans = {s: v for s, v in by_stratum.items() if v}
    if not ans:
        return None
    N = {s: max(popn.get(s, 0), len(ans[s])) for s in ans}
    folded = 0
    for s, n in popn.items():
        if s in ans or not n:
            continue
        t = nearest(s, list(ans))
        N[t] += n
        folded += n
    tot = float(sum(N.values()))
    p = q = 0.0
    for s, items in ans.items():
        n = len(items)
        w = N[s] / tot
        p += w * sum(1 for it in items if it["j"][measure]) / n
        q += w * w * max(0.0, 1.0 - n / float(N[s])) / n
    out = {"p": round(p, 4), "population": int(tot), "rows_folded_from_unanswered_strata": folded}
    if q <= 0:
        out.update({"lo": round(p, 4), "hi": round(p, 4), "n_eff": None})
    else:
        neff = 1.0 / q
        _p, lo, hi = A.wilson(p * neff, neff)
        out.update({"lo": round(lo, 4), "hi": round(hi, 4), "n_eff": round(neff, 1)})
    return out


def showw(w):
    if not w:
        return "-"
    return "%.3f [%.3f, %.3f]%s" % (w["p"], w["lo"], w["hi"],
                                    " (n_eff %.0f)" % w["n_eff"] if w.get("n_eff") else " (read in full)")


# ---- main ----------------------------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run", nargs="?")
    ap.add_argument("--run", dest="run_opt")
    ap.add_argument("--threshold", type=float, default=0.90)
    a = ap.parse_args()
    A.utf8_stdout()
    rname = a.run or a.run_opt
    if not rname:
        sys.exit("usage: score_audit9.py <run>")
    run = A.resolve(rname) if os.path.isabs(rname) or os.path.exists(rname) else A.resolve(os.path.join(A.HERE, rname))
    A.must_be_under_audit(os.path.join(run, "x"))
    kr = A.read_tsv(os.path.join(run, "sample.tsv"))
    if not kr:
        sys.exit("no sample.tsv in " + run)
    head = kr[0]
    key = {r[0]: dict(zip(head, r + [""] * (len(head) - len(r)))) for r in kr[1:]}
    popn = {}
    for r in A.read_tsv(os.path.join(run, "strata.tsv"))[1:]:
        popn.setdefault(r[0], {})[r[1]] = int(r[2])
    man = {}
    if os.path.exists(os.path.join(run, "manifest.json")):
        man = json.load(open(os.path.join(run, "manifest.json"), encoding="utf-8"))
    selftest = bool(man.get("self_test"))
    overrides = {}
    for p in A.read_tsv(os.path.join(run, "by_match_overrides.tsv"), 3):
        overrides[(p[0], p[1])] = p[2].strip().lower()

    # ---- answers
    files = sorted(glob.glob(os.path.join(run, "answers", "*.jsonl"))) + \
        sorted(glob.glob(os.path.join(run, "verdicts_*.jsonl")))
    problems, unknown, fnames = [], [], []
    answers = {}  # item -> [(file, answer, judgement)]
    for path in files:
        fn = os.path.basename(path)
        fnames.append(fn)
        seen = set()
        with open(path, encoding="utf-8-sig") as f:
            for ln, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    v = json.loads(line)
                    i = str(v.get("item", v.get("id", "")))
                except (ValueError, AttributeError):
                    problems.append("%s:%d does not parse" % (fn, ln))
                    continue
                if i not in key:
                    unknown.append("%s:%d item %s" % (fn, ln, i))
                    continue
                if i in seen:
                    problems.append("%s:%d item %s answered twice in one file; the first answer is used" % (fn, ln, i))
                    continue
                seen.add(i)
                k = key[i]
                if k["type"] == "A":
                    x, bad = norm_a(v)
                    ov = overrides.get((i, fn), overrides.get((i, "*")))
                    j = judge_a(k, x, ov)
                elif k["type"] == "C":
                    x, bad = norm_b(v)
                    j = judge_c(k, x)
                else:
                    x, bad = norm_b(v)
                    j = judge_b(k, x)
                if bad:
                    problems.append("%s:%d item %s: %s" % (fn, ln, i, "; ".join(bad)))
                answers.setdefault(i, []).append((fn, x, j))

    scored = []
    for i, lst in answers.items():
        k = key[i]
        meas = [m for m in ("right", "right_extent", "link", "link_effect") + C_MEAS if m in lst[0][2]]
        j = {m: all(e[2][m] for e in lst) for m in meas}
        scored.append({"item": i, "key": k, "each": lst, "j": j})
    real = [s for s in scored if s["key"]["role"] == "real"]
    typ = man.get("type") or (next(iter(key.values()))["type"] if key else "A")
    meas = MEAS + (("link_effect",) if typ in ("B", "C") else ()) + (C_MEAS if typ == "C" else ())

    # ---- per class
    classes = sorted({k["class"] for k in key.values() if k["role"] == "real"} | set(popn))
    per = {}
    for c in classes:
        mine = [s for s in real if s["key"]["class"] == c]
        pc = popn.get(c, {})
        bys = {}
        for s in mine:
            bys.setdefault(s["key"]["stratum"], []).append(s)

        def cut(f):
            g = {}
            for s in mine:
                g.setdefault(f(s["key"]), []).append(s)
            return {x: block(v, meas) for x, v in sorted(g.items())}
        b = block(mine, meas)
        flag = ("nothing answered" if not b["n"] else "BELOW %.2f" % a.threshold if b["right"]["p"] < a.threshold
                else "interval reaches below %.2f" % a.threshold if b["right"]["lo"] < a.threshold else "ok")
        dist = {}
        fails = {}
        for s in mine:
            for _fn, x, jj in s["each"]:
                v = x["act"] if typ == "A" else x["disposition"]
                dist[v] = dist.get(v, 0) + 1
                if jj["fail"]:
                    fails[jj["fail"]] = fails.get(jj["fail"], 0) + 1
        strata = {}
        for s_ in sorted(set(pc) | set(bys)):
            sb = block(bys.get(s_, []), meas)
            sb["population"] = pc.get(s_, 0)
            sb["sampled"] = sum(1 for k in key.values() if k["role"] == "real" and k["class"] == c
                                and k["stratum"] == s_)
            strata[s_] = sb
        per[c] = {"population": sum(pc.values()),
                  "in_key": sum(1 for k in key.values() if k["role"] == "real" and k["class"] == c),
                  "answered": len(mine), "all": b, "flag": flag,
                  "weighted": {m: weighted(bys, pc, m) for m in ("right", "right_extent")},
                  "by_system": cut(lambda k: k["stratum"].split("|")[0]),
                  "by_decade": cut(lambda k: k["stratum"].split("|")[1]),
                  "by_effect": cut(lambda k: k["effect"] if typ == "A" else k["kind"] if typ == "B"
                                   else "%s/%s vs %s/%s" % (k["kind"], k["scope"], k["kind2"], k["scope2"])),
                  "answer_distribution": dict(sorted(dist.items())), "failures": dict(sorted(fails.items())),
                  "strata": strata}

    # ---- decoys: per answer, per pack, per file, per family
    dec_rows = []
    for s in scored:
        k = s["key"]
        if k["role"] == "real":
            continue
        for fn, x, jj in s["each"]:
            dec_rows.append((k, fn, x, jj, accurate(k, jj)))

    def dacc(rows_):
        return rate(sum(1 for r in rows_ if r[4]), len(rows_))
    dec = {"in_key": {"wrong": sum(1 for k in key.values() if k["role"] == "decoy_wrong"),
                      "right": sum(1 for k in key.values() if k["role"] == "decoy_right")},
           "accuracy": dacc(dec_rows),
           "known_wrong_rejected": dacc([r for r in dec_rows if r[0]["role"] == "decoy_wrong"]),
           "known_right_confirmed": dacc([r for r in dec_rows if r[0]["role"] == "decoy_right"]),
           "per_pack": {}, "per_file": {}, "per_family": {},
           "missed": sorted({(r[0]["item"], r[1]) for r in dec_rows if not r[4]})}
    for grp, f in (("per_pack", lambda r: "pack_%s" % r[0]["pack"]), ("per_file", lambda r: r[1]),
                   ("per_family", lambda r: r[0]["decoy_family"])):
        g = {}
        for r in dec_rows:
            g.setdefault(f(r), []).append(r)
        dec[grp] = {x: {"accuracy": dacc(v), "wrong_rejected": dacc([r for r in v if r[0]["role"] == "decoy_wrong"]),
                        "right_confirmed": dacc([r for r in v if r[0]["role"] == "decoy_right"])}
                    for x, v in sorted(g.items())}

    # ---- readers
    perfile = {}
    for fn in fnames:
        mine = [(s["key"], x, jj) for s in scored for f, x, jj in s["each"] if f == fn]
        rr = [t for t in mine if t[0]["role"] == "real"]
        packs = sorted({t[0]["pack"] for t in mine}, key=lambda p: int(p) if p.isdigit() else 0)
        perfile[fn] = {"items": len(mine), "packs": packs, "real_right": rate(sum(1 for t in rr if t[2]["right"]),
                                                                              len(rr)),
                       "decoy_accuracy": dec["per_file"].get(fn, {}).get("accuracy", rate(0, 0)),
                       "unsure": sum(1 for t in mine if "unsure" in (
                           (t[1]["speaks_of_x"], t[1]["own_opinion"], t[1]["act"]) if t[0]["type"] == "A"
                           else (t[1]["same_case"], t[1]["acted_on"]))),
                       "low_confidence": sum(1 for t in mine if t[1]["confidence"] == "low")}
    dbl = [s for s in scored if len(s["each"]) >= 2]
    agree = None
    if dbl:
        fld = "act" if typ == "A" else "disposition"
        agree = {"items_read_twice": len(dbl),
                 "agree_right": rate(sum(1 for s in dbl if s["each"][0][2]["right"] == s["each"][1][2]["right"]),
                                     len(dbl)),
                 "agree_" + fld: rate(sum(1 for s in dbl if s["each"][0][1][fld] == s["each"][1][1][fld]), len(dbl)),
                 "rule": "a measure holds only if it holds for every reader"}
    unanswered = sorted(i for i in key if i not in answers)
    out = {"run": os.path.basename(run), "type": typ, "self_test": selftest, "answer_files": fnames,
           "items_in_key": len(key), "items_answered": len(scored), "unanswered": unanswered, "classes": per,
           "decoys": dec, "readers": perfile, "agreement": agree, "problems": problems, "unknown_items": unknown,
           "threshold": a.threshold,
           "definitions": {
               "right": ("speaks_of_x yes, own_opinion yes, act agrees with the effect class (report_*: and "
                         "other_decision names Y)") if typ == "A" else "link and the disposition agrees with the kind"
                        + (" of row 1 (row2_*: of row 2)" if typ == "C" else ""),
               "right_extent": ("right and (own_whole / report_whole => extent whole)" if typ == "A"
                                else "right and (scope all => whole yes)"),
               "interval": "Wilson 95%; weighted: Wilson at the Kish effective sample size, finite-population "
                           "corrected, strata weighted by population",
               "decoy_accuracy": "known wrong: not confirmed (A: not right; B: not link); known right: right"}}
    A.write_text(os.path.join(run, "score.json"), json.dumps(out, indent=1, ensure_ascii=False) + A.NL)

    # ---- errors.tsv
    if typ == "A":
        acols = ["speaks_of_x", "act", "extent", "own_opinion", "other_decision", "doctrine", "words"]
    else:
        acols = ["same_case", "acted_on", "disposition", "whole", "evidence"]
    err = [["item", "pack", "role", "class", "stratum", "row_id", "kind", "scope", "effect", "claim", "shown_node",
            "by_node", "target_node", "y_node", "answer_file", "failed"] + acols + ["confidence", "note", "decoy_why",
                                                                                  "row2_id", "kind2", "scope2",
                                                                                  "row2_right"]]
    for s in sorted(scored, key=lambda s: (s["key"]["role"] != "real", s["key"]["stratum"], s["item"])):
        k = s["key"]
        for fn, x, jj in s["each"]:
            if k["role"] == "real":
                if jj["right_extent"]:
                    continue
                what = jj["fail"] or "-"
            else:
                if accurate(k, jj):
                    continue
                what = "decoy known %s, answered otherwise" % k["role"].split("_")[1]
            if jj.get("by_how") and "by" in what:
                what += " (%s)" % jj["by_how"]
            err.append([s["item"], k["pack"], k["role"], k["class"], k["stratum"], k["row_id"], k["kind"], k["scope"],
                        k["effect"], k["claim"], k["shown_node"], k["by_node"], k["target_node"], k["y_node"], fn,
                        what] + [x[c] for c in acols] + [x["confidence"], x["note"],
                                                         k["decoy_why"] if k["role"] != "real" else "",
                                                         k.get("row2_id", ""), k.get("kind2", ""),
                                                         k.get("scope2", ""),
                                                         ("yes" if jj["row2_right"] else "no")
                                                         if "row2_right" in jj else ""])
    A.write_tsv(os.path.join(run, "errors.tsv"), err)

    # ---- score.md
    md = []
    w = md.append
    w("# Blind audit score: %s (type %s)%s" % (os.path.basename(run), typ, "  (SELF-TEST)" if selftest else ""))
    w("")
    if selftest:
        w("**Self-test of the audit tools**: synthetic input, answers written by the self-test. The numbers say "
          "nothing about any rule.")
        w("")
    w("- items in the key: %d (%d sampled rows, %d known-wrong decoys, %d known-right decoys); answered: %d; "
      "answer files: %d" % (len(key), sum(1 for k in key.values() if k["role"] == "real"), dec["in_key"]["wrong"],
                            dec["in_key"]["right"], len(scored), len(fnames)))
    if unanswered:
        w("- **unanswered items: %d** (%s%s)" % (len(unanswered), ", ".join(unanswered[:12]),
                                                " ..." if len(unanswered) > 12 else ""))
    w("- right: %s. right + extent: %s. `unsure` is never right; several readers: strict reading. Wilson 95%%."
      % (out["definitions"]["right"], out["definitions"]["right_extent"]))
    w("")
    w("## Per class")
    w("")
    extra = [m for m in ("link_effect",) + C_MEAS if m in meas]
    ename = {"link_effect": "link + effect", "row2_right": "row 2 right", "row2_right_extent": "row 2 right + extent",
             "row2_link_effect": "row 2 link + effect", "only1_right": "only row 1 right",
             "only2_right": "only row 2 right"}
    w("| class | population | answered | right | right + extent | link%s | %.2f rule |"
      % ("".join(" | " + ename[m] for m in extra), a.threshold))
    w("|---|---|---|---|---|---|%s---|" % ("---|" * len(extra)))
    for c in classes:
        p_, b = per[c], per[c]["all"]
        w("| %s | %d | %d | %s | %s | %s%s | %s |" % (c, p_["population"], b["n"], show(b["right"]),
                                                    show(b["right_extent"]), show(b["link"]),
                                                    "".join(" | " + show(b[m]) for m in extra),
                                                    p_["flag"]))
    w("")
    w("Corpus-weighted (strata = federal / state x decade, weighted by population):")
    w("")
    for c in classes:
        wt = per[c]["weighted"]
        w("- %s: right %s; right + extent %s" % (c, showw(wt["right"]), showw(wt["right_extent"])))
    w("")
    w("Answers on sampled rows (every reader): %s" % "; ".join(
        "%s: %s" % (c, ", ".join("%s %d" % kv for kv in per[c]["answer_distribution"].items())) for c in classes))
    w("")
    w("Failures (every reader; x = not X / not linked, own = not the court's own words, act = other act, by = other "
      "decision is not Y, extent = whole wanted): %s" % "; ".join(
          "%s: %s" % (c, ", ".join("%s %d" % kv for kv in per[c]["failures"].items()) or "none") for c in classes))
    w("")
    w("## Decoys (reader accuracy on items whose answer is known)")
    w("")
    w("- all decoy answers: %s" % show(dec["accuracy"]))
    w("- known wrong, not confirmed: %s" % show(dec["known_wrong_rejected"]))
    w("- known right, confirmed: %s" % show(dec["known_right_confirmed"]))
    w("")
    w("| per pack | accuracy | known wrong rejected | known right confirmed |")
    w("|---|---|---|---|")
    for x, r in dec["per_pack"].items():
        w("| %s | %s | %s | %s |" % (x, show(r["accuracy"]), show(r["wrong_rejected"]), show(r["right_confirmed"])))
    w("")
    w("| per decoy family | accuracy |")
    w("|---|---|")
    for x, r in dec["per_family"].items():
        w("| %s | %s |" % (x, show(r["accuracy"])))
    w("")
    w("## Readers")
    w("")
    w("| answer file | packs | items | sampled rows right | decoy accuracy | unsure | low confidence |")
    w("|---|---|---|---|---|---|---|")
    for fn, p_ in perfile.items():
        w("| %s | %s | %d | %s | %s | %d | %d |" % (fn, ",".join(p_["packs"]), p_["items"], show(p_["real_right"]),
                                                  show(p_["decoy_accuracy"]), p_["unsure"], p_["low_confidence"]))
    if agree:
        w("")
        w("Items read twice: %d; same right answer %s. %s." % (agree["items_read_twice"], show(agree["agree_right"]),
                                                              agree["rule"].capitalize()))
    w("")
    w("## Per class: federal / state, decade, effect, stratum")
    w("")
    w("| class | cut | answered | right | right + extent |")
    w("|---|---|---|---|---|")
    for c in classes:
        for name in ("by_system", "by_decade", "by_effect"):
            for x, b in per[c][name].items():
                w("| %s | %s | %d | %s | %s |" % (c, x, b["n"], show(b["right"]), show(b["right_extent"])))
        for s_, b in per[c]["strata"].items():
            if b["sampled"] or b["n"]:
                w("| %s | stratum %s (population %d, sampled %d) | %d | %s | %s |" % (
                    c, s_, b["population"], b["sampled"], b["n"],
                    "%d/%d" % (b["right"]["k"], b["n"]) if b["n"] else "-",
                    "%d/%d" % (b["right_extent"]["k"], b["n"]) if b["n"] else "-"))
    if problems or unknown:
        w("")
        w("## Problems in the answer files")
        w("")
        for p_ in problems + ["unknown item: " + u for u in unknown]:
            w("- " + p_)
    w("")
    w("Wrong items and missed decoys, with the readers' words: `errors.tsv` (%d lines)." % (len(err) - 1))
    A.write_text(os.path.join(run, "score.md"), A.NL.join(md) + A.NL)
    print(A.NL.join(md[:md.index("## Readers")] if "## Readers" in md else md))
    print("wrote %s: score.json, score.md, errors.tsv (%d lines)" % (run, len(err) - 1))


if __name__ == "__main__":
    main()
