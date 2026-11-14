"""stlink12 step 0: the full-names-only pool from round 11's feature file (read only) -> work/pool.jsonl.

A record = D with its latest full-name candidate T (no same-date sibling) and no docket / cite / date tie.
Counts how many of those rest only on a caption role phrase parsed as a person ("Defendant and Appellant").
"""
import collections, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ties  # noqa: E402

NL = chr(10)
FEAT = os.path.join(HERE, "..", "..", "..", "round11", "agents", "stlink11", "work", "feat.jsonl")
ROLEW = re.compile(r"^(?:plaintiffs?|defendants?|appellants?|appellees?|respondents?|petitioners?|cross|and|in|error|"
                   r"third|party|intervenors?|claimants?|movants?|relators?|counter|real|parties|interest|the)$", re.I)


def role_only(e):
    ws = re.findall(r"[A-Za-z]+", e)
    return bool(ws) and all(ROLEW.match(w) for w in ws)


def forms(x):
    return [k for k, ok in (("docket", x["docket"] == "strong"), ("docketweak", x["docket"] == "weak"),
                            ("cite", x["cite"] in ("front", "body")), ("date", x["date"] == "present")) if ok]


def main():
    st = collections.Counter()
    out = open(os.path.join(HERE, "work", "pool.jsonl"), "w", encoding="utf-8", newline=NL)
    for l in open(FEAT, encoding="utf-8"):
        r = json.loads(l)
        cs = [x for x in r.get("cands", []) if "err" not in x]
        full = sorted([x for x in cs if x["names"] == "full"], key=lambda x: x["tdate"])
        if not full:
            continue
        T = full[-1]
        if any(x["tdate"] == T["tdate"] for x in full[:-1]):
            continue
        f = [x for x in forms(T) if x != "docketweak"]
        if f:
            continue
        st["full_notie"] += 1
        ents = [e for e in (T["names_d"] or "").split("|") if e]
        real = [e for e in ents if not role_only(e)]
        if not real:
            st["role_phrase_only"] += 1
            continue
        st["real_name"] += 1
        out.write(json.dumps({"n": r["n"], "j": T["j"], "sys": r["sys"], "date": r["date"], "tdate": T["tdate"],
                              "ka": r["ka"], "ents": real, "dparties": r.get("dparties"),
                              "tparties": T.get("tparties"), "ncand_full": len(full)}, ensure_ascii=False) + NL)
    out.close()
    print(dict(st))


if __name__ == "__main__":
    main()
