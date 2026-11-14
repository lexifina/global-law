"""Round 8, agent doctrine8: the doctrine-dominance opportunity (measurement only; no answer key is read).

    python -X utf8 measure.py

Inputs (round 7, read only): round7/agents/doctrine/ties.jsonl.gz (resolved ties), scan/*.jsonl.gz (rejection
sentences), the node date / court arrays, round7/stage/v3/treatments.tsv (base pairs, for overlap).

For every rejection label in a court-of-last-resort sentence whose label is AMBIGUOUS in the round-7 registry (strict
ties to >= 2 decisions), the dominant target x1 (most strict ties), n1, the runner-up count n2. The same order and
power filters as round 7 (date(x1) < date(W); x1 in W's system or W SCOTUS) are applied with x = x1.
Also: does W itself strictly tie the label (own tie) to x1, to another decision, or not at all?

Writes work/dom_cands.jsonl (every surviving candidate with n1, n2, own-tie class) and work/curve.json.
"""
import collections, glob, gzip, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
R7 = os.path.expanduser("~/Documents/us-caselaw-lean-work/caselaw-lean-2/round7/agents/doctrine")
sys.path.insert(0, R7)
sys.path.insert(0, os.path.expanduser("~/Documents/us-caselaw-lean-work/caselaw-lean-2/round6/history"))
import r6lib as L  # noqa: E402
from build_registry import possessive_core  # noqa: E402

NL = "\n"
BASE = os.path.expanduser("~/Documents/us-caselaw-lean-work/caselaw-lean-2/round7/stage/v3")
THRESH = [(3, 2), (3, 3), (5, 2), (5, 3), (5, 4), (5, 6), (10, 3), (10, 4), (10, 10), (20, 4), (20, 10)]


def main():
    os.makedirs(os.path.join(HERE, "work"), exist_ok=True)
    F = L.Facts()
    strict = collections.defaultdict(collections.Counter)
    wties = collections.defaultdict(collections.Counter)  # (w, lk) -> strict own ties per x
    wties_any = collections.defaultdict(collections.Counter)
    with gzip.open(os.path.join(R7, "ties.jsonl.gz"), "rt", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r["x"] is None or possessive_core(r["core"], r["form"]):
                continue
            wties_any[(r["n"], r["lk"])][r["x"]] += 1
            if r["strict"]:
                strict[r["lk"]][r["x"]] += 1
                wties[(r["n"], r["lk"])][r["x"]] += 1
    amb = {k: c for k, c in strict.items() if len(c) >= 2}
    print("labels strict", len(strict), "ambiguous", len(amb), flush=True)
    base_pairs = set()
    with open(os.path.join(BASE, "treatments.tsv"), encoding="utf-8") as f:
        for l in f:
            p = l.split("\t", 3)
            base_pairs.add((int(p[1]), int(p[2])))
    st = collections.Counter()
    out, own_alt = [], []
    for p in sorted(glob.glob(os.path.join(R7, "scan", "*.jsonl.gz"))):
        with gzip.open(p, "rt", encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                if r["t"] != "rej":
                    continue
                w = r["n"]
                cw = int(F.court[w])
                if F.tier(cw) != "L":
                    continue
                seen = set()
                for lab in r["labels"]:
                    core, lk, form, noun, a, b = lab
                    if possessive_core(core, form) or lk not in amb or lk in seen:
                        continue
                    seen.add(lk)
                    st["amb-label-sentences"] += 1
                    c = amb[lk]
                    (x1, n1), (x2, n2) = c.most_common(2)
                    own = wties.get((w, lk), collections.Counter())
                    if own:
                        ownc = "own->x1" if set(own) == {x1} else ("own->x1+other" if x1 in own else "own->other")
                    else:
                        ownc = "no-own-strict" if not wties_any.get((w, lk)) else (
                            "plain->x1" if x1 in wties_any[(w, lk)] else "plain->other")
                    st["own:" + ownc] += 1
                    # alternative rule (for comparison only): W's own strict ties name exactly one decision xo
                    if len(own) == 1:
                        xo = next(iter(own))
                        cxo = int(F.court[xo])
                        if xo != w and 0 < int(F.date[xo]) < int(F.date[w]) and (
                                F.is_scotus(cw) or F.system(cxo) == F.system(cw)):
                            own_alt.append({"w": w, "x": xo, "lk": lk, "core": core, "form": form, "noun": noun,
                                            "la": [a, b], "s": r["s"], "q": r["q"], "part": r["part"],
                                            "cue": r["cue"], "n1": c[xo], "n2": max(v for k2, v in c.items() if k2 != xo),
                                            "ntargets": len(c), "own": "own-only",
                                            "base_pair": int((w, xo) in base_pairs), "own_ties": [],
                                            "w_date": int(F.date[w]), "x_date": int(F.date[xo]),
                                            "w_court": cw, "x_court": cxo})
                    if x1 == w or int(F.date[x1]) == 0 or int(F.date[x1]) >= int(F.date[w]):
                        st["drop:order"] += 1
                        continue
                    cx = int(F.court[x1])
                    if not (F.is_scotus(cw) or F.system(cx) == F.system(cw)):
                        st["drop:no-power"] += 1
                        continue
                    out.append({"w": w, "x": x1, "lk": lk, "core": core, "form": form, "noun": noun, "la": [a, b],
                                "s": r["s"], "q": r["q"], "part": r["part"], "cue": r["cue"], "n1": n1, "n2": n2,
                                "ntargets": len(c), "own": ownc, "base_pair": int((w, x1) in base_pairs),
                                "own_ties": [], "w_date": int(F.date[w]), "x_date": int(F.date[x1]),
                                "w_court": cw, "x_court": cx})
    with open(os.path.join(HERE, "work", "dom_cands.jsonl"), "w", encoding="utf-8", newline=NL) as f:
        for c in out:
            f.write(json.dumps(c, ensure_ascii=False) + NL)
    curve = {"stats": dict(sorted(st.items())), "after_order_power": len(out), "curve": []}
    for k, rr in THRESH:
        sel = [c for c in out if c["n1"] >= k and c["n1"] >= rr * max(c["n2"], 1)]
        labs = collections.Counter(c["lk"] for c in sel)
        curve["curve"].append({
            "min_ties": k, "ratio": rr, "sentences": len(sel), "w": len({c["w"] for c in sel}),
            "pairs": len({(c["w"], c["x"]) for c in sel}), "targets": len({c["x"] for c in sel}),
            "labels": len(labs), "own_x1": sum(1 for c in sel if c["own"].startswith("own->x1")),
            "own_other": sum(1 for c in sel if c["own"] == "own->other"),
            "pairs_in_base": len({(c["w"], c["x"]) for c in sel if c["base_pair"]}),
            "top_labels": labs.most_common(12)})
    # own-tie disambiguation (W's own strict tie names exactly one decision), regardless of dominance
    own_sel = [c for c in out if c["own"] == "own->x1"]
    curve["own_tie_to_x1_any_dominance"] = {"sentences": len(own_sel), "pairs": len({(c["w"], c["x"]) for c in own_sel})}
    curve["own_tie_single_target_any_x"] = {
        "sentences": len(own_alt), "pairs": len({(c["w"], c["x"]) for c in own_alt}),
        "x_is_dominant": sum(1 for c in own_alt if c["n1"] > c["n2"]),
        "pairs_in_base": len({(c["w"], c["x"]) for c in own_alt if c["base_pair"]})}
    with open(os.path.join(HERE, "work", "own_alt_cands.jsonl"), "w", encoding="utf-8", newline=NL) as f:
        for c in own_alt:
            f.write(json.dumps(c, ensure_ascii=False) + NL)
    with open(os.path.join(HERE, "work", "curve.json"), "w", encoding="utf-8", newline=NL) as f:
        json.dump(curve, f, indent=1, ensure_ascii=False)
    print(json.dumps(curve, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
