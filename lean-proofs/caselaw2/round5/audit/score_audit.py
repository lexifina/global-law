"""Blind audit: join the auditors' answers to the private key and score them.

    python round5/audit/score_audit.py --name <audit name>

Reads round5/audit/<name>/key.tsv, strata_summary.tsv and every answers/*.jsonl. An answer line is
  {"id", "stated": "yes|no|unclear", "x_ok": bool, "y_ok": bool, "extent": "whole|part|otherGrounds|unclear",
   "words", "note"}.
Per item:
  right            = stated yes AND x_ok AND y_ok
  right_and_extent = right AND (model scope `all` => extent whole; a partial / otherGrounds / issues / demoted
                     scope is satisfied by any extent)            [key column scope_class: all | part]
If two answer files cover the same item, agreement is reported and the STRICTER answer is used, field by field:
stated = the lower of no < unclear < yes; x_ok and y_ok = both true; extent = whole only if both say whole.
A decoy counts as accepted when ANY answer file accepts it (the strict reading for the auditors); the per-file
table shows each auditor's own decoy acceptance, so an auditor who says yes to everything is visible.
Per stratum and overall (pooled over the real items; and weighted by the strata's population sizes): n, right,
right_and_extent with Wilson 95% intervals. Decoys: acceptance rate (a decoy is accepted when it is `right`).
Writes score.json, score.tsv and wrong.tsv (real rows that are not right_and_extent, with the answers) into the
audit folder and prints the table.
"""
import argparse
import json
import math
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit_common as AC  # noqa: E402

STATED = {"no": 0, "unclear": 1, "yes": 2}
EXTENT = {"whole": "whole", "all": "whole", "part": "part", "partial": "part", "inpart": "part",
          "othergrounds": "otherGrounds", "other": "otherGrounds", "unclear": "unclear", "": "unclear",
          "unknown": "unclear", "none": "unclear"}
EXT_RANK = {"unclear": 0, "otherGrounds": 1, "part": 2, "whole": 3}


def as_bool(v):
    if isinstance(v, bool):
        return v
    return str(v).strip().lower() in ("true", "yes", "1", "y")


def norm_answer(v):
    """(answer dict, problem or '')."""
    bad = ""
    st = v.get("stated", v.get("states"))
    st = "yes" if st is True else "no" if st is False else str(st).strip().lower()
    if st not in STATED:
        bad = "stated=%r read as unclear" % v.get("stated")
        st = "unclear"
    ex = str(v.get("extent", v.get("scope", ""))).strip().lower().replace(" ", "").replace("_", "")
    if ex not in EXTENT:
        bad = (bad + "; " if bad else "") + "extent=%r read as unclear" % v.get("extent")
    return {"stated": st, "x_ok": as_bool(v.get("x_ok", v.get("x_right", False))),
            "y_ok": as_bool(v.get("y_ok", v.get("y_right", False))), "extent": EXTENT.get(ex, "unclear"),
            "words": str(v.get("words", "")), "note": str(v.get("note", ""))}, bad


def right(a):
    return a["stated"] == "yes" and a["x_ok"] and a["y_ok"]


def right_ext(a, scope_class):
    return right(a) and (scope_class != "all" or a["extent"] == "whole")


def stricter(answers):
    if len(answers) == 1:
        return answers[0]
    return {"stated": min((x["stated"] for x in answers), key=lambda s: STATED[s]),
            "x_ok": all(x["x_ok"] for x in answers), "y_ok": all(x["y_ok"] for x in answers),
            "extent": min((x["extent"] for x in answers), key=lambda e: EXT_RANK[e]),
            "words": " | ".join(x["words"] for x in answers if x["words"]),
            "note": " | ".join(x["note"] for x in answers if x["note"])}


def rate(k, n):
    p, lo, hi = AC.wilson(k, n)
    return {"k": k, "n": n, "p": None if p is None else round(p, 4), "lo": None if p is None else round(lo, 4),
            "hi": None if p is None else round(hi, 4)}


def show(r):
    return "-" if not r["n"] else "%d/%d %.3f [%.3f, %.3f]" % (r["k"], r["n"], r["p"], r["lo"], r["hi"])


def kappa(pairs):
    n = len(pairs)
    if not n:
        return None
    po = sum(1 for x, y in pairs if x == y) / n
    p1, p2 = sum(1 for x, _ in pairs if x) / n, sum(1 for _, y in pairs if y) / n
    pe = p1 * p2 + (1 - p1) * (1 - p2)
    return None if pe >= 1 else round((po - pe) / (1 - pe), 3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    a = ap.parse_args()
    AC.utf8_stdout()
    adir = os.path.join(AC.HERE, a.name)
    krows = AC.read_rows(os.path.join(adir, "key.tsv"), 8)
    if not krows:
        sys.exit("no key.tsv in " + adir)
    head = krows[0]
    key = {r[0]: dict(zip(head, r)) for r in krows[1:]}
    strata = [r for r in AC.read_rows(os.path.join(adir, "strata_summary.tsv"), 4)[1:]]
    order = [r[0] for r in strata]
    popn = {r[0]: int(r[1]) for r in strata}
    sampled = {r[0]: int(r[2]) for r in strata}
    for k in key.values():
        if k["stratum"] not in order and k["decoy"] != "1":
            order.append(k["stratum"])

    # ---- answers
    ans, problems, unknown, files = {}, [], [], []
    adir_ans = os.path.join(adir, "answers")
    for fn in sorted(os.listdir(adir_ans)) if os.path.isdir(adir_ans) else []:
        if not fn.endswith(".jsonl"):
            continue
        files.append(fn)
        seen = {}
        with open(os.path.join(adir_ans, fn), encoding="utf-8") as f:
            for ln, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    v = json.loads(line)
                    i = str(v.get("id", v.get("item", "")))
                except ValueError:
                    problems.append("%s:%d does not parse" % (fn, ln))
                    continue
                if i not in key:
                    unknown.append("%s:%d id %s" % (fn, ln, i))
                    continue
                x, bad = norm_answer(v)
                if bad:
                    problems.append("%s:%d %s: %s" % (fn, ln, i, bad))
                if i in seen:
                    problems.append("%s:%d %s answered twice in one file, the last answer is used" % (fn, ln, i))
                seen[i] = x
        for i, x in seen.items():
            ans.setdefault(i, []).append((fn, x))

    # ---- per item
    items = {}
    for i, k in key.items():
        if i in ans:
            xs = [x for _, x in ans[i]]
            c = stricter(xs)
            items[i] = {"key": k, "c": c, "right": right(c), "right_ext": right_ext(c, k["scope_class"]),
                        "each": ans[i]}
    real = {i: it for i, it in items.items() if it["key"]["decoy"] != "1"}
    decoy = {i: it for i, it in items.items() if it["key"]["decoy"] == "1"}

    def block(sub):
        n = len(sub)
        return {"answered": n, "right": rate(sum(it["right"] for it in sub), n),
                "right_and_extent": rate(sum(it["right_ext"] for it in sub), n),
                "stated_yes": rate(sum(it["c"]["stated"] == "yes" for it in sub), n),
                "stated_unclear": sum(it["c"]["stated"] == "unclear" for it in sub),
                "x_ok": rate(sum(it["c"]["x_ok"] for it in sub), n),
                "y_ok": rate(sum(it["c"]["y_ok"] for it in sub), n)}

    per = {}
    for s in order:
        sub = [it for it in real.values() if it["key"]["stratum"] == s]
        b = block(sub)
        b["population"] = popn.get(s)
        b["sampled"] = sampled.get(s)
        b["in_key"] = sum(1 for k in key.values() if k["stratum"] == s and k["decoy"] != "1")
        per[s] = b
    overall = block(list(real.values()))
    overall["in_key"] = sum(1 for k in key.values() if k["decoy"] != "1")

    def weighted(field):
        """Population-weighted estimate over the strata with answers; normal interval with finite-population
        correction (a stratum audited in full adds no variance)."""
        tot = sum(popn[s] for s in order if popn.get(s) and per[s]["answered"])
        if not tot:
            return None
        p = v = 0.0
        for s in order:
            n, N = per[s]["answered"], popn.get(s)
            if not n or not N:
                continue
            ph = per[s][field]["k"] / n
            w = N / tot
            p += w * ph
            v += w * w * ph * (1 - ph) / n * max(0.0, 1 - n / N)
        se = math.sqrt(v)
        return {"p": round(p, 4), "lo": round(max(0.0, p - 1.96 * se), 4), "hi": round(min(1.0, p + 1.96 * se), 4),
                "population": tot}

    wt = {f: weighted(f) for f in ("right", "right_and_extent")} if popn else {}
    dn = len(decoy)
    dacc = {i for i, it in decoy.items() if any(right(x) for _, x in it["each"])}  # accepted by ANY auditor
    dec = {"in_key": sum(1 for k in key.values() if k["decoy"] == "1"), "answered": dn,
           "accepted": rate(len(dacc), dn),
           "stated_yes": rate(sum(any(x["stated"] == "yes" for _, x in it["each"]) for it in decoy.values()), dn),
           "accepted_items": sorted(dacc)}

    # ---- agreement (items with two or more answer files; the first two are compared)
    dbl = [it for it in items.values() if len(it["each"]) >= 2]
    agree = None
    if dbl:
        pr = [(right(it["each"][0][1]), right(it["each"][1][1])) for it in dbl]
        pe = [(right_ext(it["each"][0][1], it["key"]["scope_class"]),
               right_ext(it["each"][1][1], it["key"]["scope_class"])) for it in dbl]
        ps = [(it["each"][0][1]["stated"], it["each"][1][1]["stated"]) for it in dbl]
        agree = {"items_with_two_answers": len(dbl),
                 "agree_stated": rate(sum(x == y for x, y in ps), len(dbl)),
                 "agree_right": rate(sum(x == y for x, y in pr), len(dbl)), "kappa_right": kappa(pr),
                 "agree_right_and_extent": rate(sum(x == y for x, y in pe), len(dbl)),
                 "rule": "the stricter answer is used, field by field"}

    # ---- per answer file (each auditor on their own)
    perfile = {}
    for fn in files:
        mine = [(key[i], x) for i, lst in ans.items() for f, x in lst if f == fn]
        r = [(k, x) for k, x in mine if k["decoy"] != "1"]
        d = [(k, x) for k, x in mine if k["decoy"] == "1"]
        perfile[fn] = {"items": len(mine), "real_right": rate(sum(right(x) for _, x in r), len(r)),
                       "decoys_accepted": rate(sum(right(x) for _, x in d), len(d)),
                       "stated_yes_all": rate(sum(x["stated"] == "yes" for _, x in mine), len(mine))}

    unanswered = sorted(i for i in key if i not in ans)
    out = {"audit": a.name, "answer_files": files, "items_in_key": len(key), "items_answered": len(items),
           "unanswered": unanswered, "strata": per, "overall_pooled": overall, "overall_weighted": wt,
           "decoys": dec, "agreement": agree, "per_file": perfile, "problems": problems, "unknown_ids": unknown,
           "definitions": {"right": "stated yes and x_ok and y_ok",
                           "right_and_extent": "right and (scope_class all => extent whole)",
                           "interval": "Wilson 95% (weighted: normal, finite-population corrected)"}}
    AC.write_text(os.path.join(adir, "score.json"), json.dumps(out, indent=1, ensure_ascii=False) + "\n")

    cols = ["stratum", "population", "sampled", "in_key", "answered", "right_k", "right_p", "right_lo", "right_hi",
            "right_and_extent_k", "right_and_extent_p", "right_and_extent_lo", "right_and_extent_hi", "stated_yes_k",
            "x_ok_k", "y_ok_k"]
    tsv = [cols]

    def line(name, b):
        f = lambda v: "-" if v is None else v  # noqa: E731
        r, e = b["right"], b["right_and_extent"]
        return [name, f(b.get("population")), f(b.get("sampled")), b.get("in_key", "-"), b["answered"], r["k"],
                f(r["p"]), f(r["lo"]), f(r["hi"]), e["k"], f(e["p"]), f(e["lo"]), f(e["hi"]), b["stated_yes"]["k"],
                b["x_ok"]["k"], b["y_ok"]["k"]]

    for s in order:
        tsv.append(line(s, per[s]))
    tsv.append(line("ALL (pooled)", overall))
    if wt.get("right"):
        w, e = wt["right"], wt["right_and_extent"]
        tsv.append(["ALL (weighted by population)", w["population"], "-", "-", overall["answered"], "-", w["p"],
                    w["lo"], w["hi"], "-", e["p"], e["lo"], e["hi"], "-", "-", "-"])
    da = dec["accepted"]
    tsv.append(["DECOYS (accepted = right)", "-", "-", dec["in_key"], dn, da["k"],
                "-" if da["p"] is None else da["p"], "-" if da["p"] is None else da["lo"],
                "-" if da["p"] is None else da["hi"], "-", "-", "-", "-", dec["stated_yes"]["k"], "-", "-"])
    AC.write_rows(os.path.join(adir, "score.tsv"), tsv)

    wrong = [["item_id", "treatment_id", "stratum", "kind", "scope", "scope_class", "class", "failed", "stated",
              "x_ok", "y_ok", "extent", "words", "note", "answers"]]
    for i, it in sorted(real.items(), key=lambda t: (order.index(t[1]["key"]["stratum"]), t[1]["key"]["treatment_id"])):
        if it["right_ext"]:
            continue
        k, c = it["key"], it["c"]
        failed = [n for n, ok in (("stated", c["stated"] == "yes"), ("x", c["x_ok"]), ("y", c["y_ok"])) if not ok]
        if not failed:
            failed = ["extent"]
        each = " || ".join("%s: %s/%s/%s/%s" % (fn, x["stated"], "T" if x["x_ok"] else "F", "T" if x["y_ok"] else "F",
                                                 x["extent"]) for fn, x in it["each"])
        wrong.append([i, k["treatment_id"], k["stratum"], k["kind"], k["scope"], k["scope_class"], k["class"],
                      "+".join(failed), c["stated"], str(c["x_ok"]).lower(), str(c["y_ok"]).lower(), c["extent"],
                      AC.clean(c["words"]), AC.clean(c["note"]), each])
    AC.write_rows(os.path.join(adir, "wrong.tsv"), wrong)

    # ---- print
    print("audit %s: %d of %d items answered, %d answer files" % (a.name, len(items), len(key), len(files)))
    w0 = max([len(s) for s in order] + [28])
    print("%-*s %6s %5s %5s  %-30s %-30s" % (w0, "stratum", "pop", "samp", "answ", "right", "right_and_extent"))
    for s in order:
        b = per[s]
        print("%-*s %6s %5s %5d  %-30s %-30s" % (w0, s, "-" if b["population"] is None else b["population"],
                                                 "-" if b["sampled"] is None else b["sampled"], b["answered"],
                                                 show(b["right"]), show(b["right_and_extent"])))
    print("%-*s %6s %5s %5d  %-30s %-30s" % (w0, "ALL (pooled)", "", "", overall["answered"], show(overall["right"]),
                                             show(overall["right_and_extent"])))
    if wt.get("right"):
        print("%-*s %6d %5s %5s  %-30s %-30s" % (
            w0, "ALL (weighted by population)", wt["right"]["population"], "", "",
            "%.3f [%.3f, %.3f]" % (wt["right"]["p"], wt["right"]["lo"], wt["right"]["hi"]),
            "%.3f [%.3f, %.3f]" % (wt["right_and_extent"]["p"], wt["right_and_extent"]["lo"],
                                   wt["right_and_extent"]["hi"])))
    print("decoys: accepted %s; stated yes %s (of %d decoys in the key)" % (show(dec["accepted"]),
                                                                          show(dec["stated_yes"]), dec["in_key"]))
    if agree:
        print("two answers on %d items: agree on stated %s, on right %s (kappa %s), on right_and_extent %s; "
              "the stricter answer is used" % (agree["items_with_two_answers"], show(agree["agree_stated"]),
                                              show(agree["agree_right"]), agree["kappa_right"],
                                              show(agree["agree_right_and_extent"])))
    print("per answer file (each auditor alone):")
    for fn, b in perfile.items():
        print("  %-22s items %3d  real right %-28s decoys accepted %-24s" % (fn, b["items"], show(b["real_right"]),
                                                                           show(b["decoys_accepted"])))
    if unanswered:
        print("unanswered items: %d" % len(unanswered))
    for p in problems + ["unknown id: " + u for u in unknown]:
        print("problem: " + p)
    print("wrong rows: %d (wrong.tsv); score.json, score.tsv in %s" % (len(wrong) - 1, adir))


if __name__ == "__main__":
    main()
