"""Blind search for loopholes in the 2025 individual income tax, using the Lean model as the oracle.

    python search.py build households.json work/       # writes work/variants.json, work/elections.json, work/meta.json
    lake env lean --run TaxCode/Individual/Run.lean work/variants.json work/results.json work/elections.json
    python search.py score households.json work/        # writes work/moves.json and prints the leaderboard

Nothing here knows any tax planning. For each household the search tries ordinary choices a family controls and asks
the Lean model what each costs or saves:

  split    file two separate returns instead of one joint return, choosing which spouse holds the investments, which
           spouse pays the deductible expenses, and which spouse claims the children; both itemize or neither does
           (§63(c)(6)(A)).
  ira      put k dollars into a deductible traditional IRA (the money stays the family's).
  earnless earn d dollars less (decline overtime, an unpaid week).
  gains    realize d dollars more or less of long-term gain this year.
  depend   let a parent aged 65+ who lives with the family be claimed as a dependent while filing their own return.

A move is a candidate loophole when its payoff is out of proportion to what it changes: a deduction that saves more
than the dollar deducted, less income that leaves the family richer, or the same income and the same spending taxed
very differently because of who holds a bank account.
"""
import json, sys, copy
from pathlib import Path

INV = ["taxableInterest", "taxExemptInterest", "ordinaryDividends", "qualifiedDividends", "shortTermGains",
       "longTermGains"]
DED = ["stateLocalTaxes", "mortgageInterest", "charitableCash", "medicalExpenses"]


def blank_mfs(h, person):
    g = copy.deepcopy(h)
    g.update(filing="mfs", head=dict(person), spouse=None, wagesSpouse=0, dependents=[])
    return g


def split(h, s_inv, s_ded, kids_to_head):
    """Two separate returns. Wages and SE income stay with the earner; `s_inv`, `s_ded` = the head's share of the
    investments and of the deductible payments; children go wholly to one spouse."""
    a = blank_mfs(h, h["head"]); b = blank_mfs(h, h["spouse"])
    head_w = h["wages"] - h["wagesSpouse"]
    a["wages"] = head_w; b["wages"] = h["wagesSpouse"]
    b["seIncome"] = 0; b["qbi"] = 0
    for k in INV + DED:
        x = h[k]; ah = int(round(x * (s_inv if k in INV else s_ded)))
        a[k] = ah; b[k] = x - ah
    if a["qualifiedDividends"] > a["ordinaryDividends"]:
        a["qualifiedDividends"] = a["ordinaryDividends"]
    b["qualifiedDividends"] = min(b["ordinaryDividends"], h["qualifiedDividends"] - a["qualifiedDividends"])
    for k in ["socialSecurity", "pensions", "iraDistributions", "unemployment", "otherIncome",
              "qualifiedTips", "qualifiedOvertime", "carLoanInterest", "iraContributions", "hsaContributions",
              "studentLoanInterest", "educatorExpenses", "retirementContributions", "childCareExpenses",
              "marketplacePremium", "benchmarkPremium"]:
        b[k] = 0                      # kept with the head; these follow the person, and the search does not move them
    a["qualifiedTuition"] = list(h["qualifiedTuition"]) if kids_to_head else []
    b["qualifiedTuition"] = [] if kids_to_head else list(h["qualifiedTuition"])
    (a if kids_to_head else b)["dependents"] = list(h["dependents"])
    if not kids_to_head:
        b["childCareExpenses"], a["childCareExpenses"] = h["childCareExpenses"], 0
    return a, b


def build(hs, work):
    V, E, M = [], [], []

    def add(h, elect, meta):
        V.append(h); E.append(elect); M.append(meta)

    for i, h in enumerate(hs):
        if h["filing"] == "qss":
            continue
        add(h, None, {"i": i, "move": "base"})
        earned = h["wages"] + max(0, h["seIncome"])
        # ira: deductible traditional IRA; per-person limit $7,000 (+$1,000 at 50); spousal IRA on joint returns
        if earned > 0 and not h["activeParticipant"]:
            room = 7000 + (1000 if h["head"]["age"] >= 50 else 0)
            if h["filing"] == "mfj" and h["spouse"]:
                room += 7000 + (1000 if h["spouse"]["age"] >= 50 else 0)
            room = min(room, earned) - h["iraContributions"]
            for k in sorted({500, 1000, 2000, 3000, 5000, 7000, 10000, 14000, 16000, room}):
                if 0 < k <= room:
                    g = copy.deepcopy(h)
                    g["iraContributions"] += k; g["retirementContributions"] += k
                    add(g, None, {"i": i, "move": "ira", "amount": k})
        # earnless: give up d dollars of wages
        if h["wages"] > 0:
            for d in (1, 50, 250, 1000, 2500, 5000):
                if d <= h["wages"] - h["wagesSpouse"]:
                    g = copy.deepcopy(h); g["wages"] -= d
                    g["qualifiedTips"] = min(g["qualifiedTips"], g["wages"] - g["wagesSpouse"])
                    g["qualifiedOvertime"] = min(g["qualifiedOvertime"], g["wages"] - g["wagesSpouse"])
                    add(g, None, {"i": i, "move": "earnless", "amount": d})
        # gains: realize more (or, if there are gains, less) long-term gain
        for d in (1000, 5000, 20000, 50000):
            g = copy.deepcopy(h); g["longTermGains"] += d
            add(g, None, {"i": i, "move": "gains", "amount": d})
            if h["longTermGains"] >= d:
                g = copy.deepcopy(h); g["longTermGains"] -= d
                add(g, None, {"i": i, "move": "gains", "amount": -d})
        # split: married couples choose separate returns and who holds what
        if h["filing"] == "mfj" and h["spouse"]:
            for s_inv in (0.0, 0.5, 1.0):
                for s_ded in (0.0, 0.5, 1.0):
                    for kids in ((True, False) if h["dependents"] else (True,)):
                        for elect in (True, False):
                            a, b = split(h, s_inv, s_ded, kids)
                            meta = {"i": i, "move": "split", "inv": s_inv, "ded": s_ded, "kids": "head" if kids else "spouse",
                                    "itemize": elect}
                            add(a, elect, dict(meta, side="a")); add(b, elect, dict(meta, side="b"))
        # depend: an elderly parent on their own return who can also be claimed as the family's dependent
    work.mkdir(parents=True, exist_ok=True)
    for name, x in (("variants", V), ("elections", E), ("meta", M)):
        json.dump(x, open(work / f"{name}.json", "w", encoding="utf-8"))
    print(f"{len(V)} returns to compute for {len(hs)} households")


def score(hs, work):
    R = json.load(open(work / "results.json", encoding="utf-8")); M = json.load(open(work / "meta.json", encoding="utf-8"))
    base, moves, splits = {}, [], {}
    for r, m in zip(R, M):
        if m["move"] == "base":
            base[m["i"]] = r
    for r, m in zip(R, M):
        i = m["i"]; b = base[i]
        if m["move"] == "split":
            key = (i, m["inv"], m["ded"], m["kids"], m["itemize"])
            splits.setdefault(key, {})[m["side"]] = r
            continue
        if m["move"] == "base":
            continue
        saved = b["netTax"] - r["netTax"]
        moves.append(dict(m, saved=saved, base=b["netTax"], after=r["netTax"]))
    for (i, inv, ded, kids, it), sides in splits.items():
        if len(sides) != 2:
            continue
        b = base[i]
        net = sides["a"]["netTax"] + sides["b"]["netTax"]
        moves.append({"i": i, "move": "split", "inv": inv, "ded": ded, "kids": kids, "itemize": it,
                      "saved": b["netTax"] - net, "base": b["netTax"], "after": net,
                      "a": {k: sides["a"][k] for k in ("agi", "taxableIncome", "netTax", "itemized", "deduction")},
                      "b": {k: sides["b"][k] for k in ("agi", "taxableIncome", "netTax", "itemized", "deduction")}})
    json.dump(moves, open(work / "moves.json", "w", encoding="utf-8"))
    # leaderboards
    def top(f, key, n=12):
        xs = sorted((x for x in moves if f(x)), key=key, reverse=True)[:n]
        return xs
    print("\n== separate returns beat the joint return (best arrangement per household)")
    best = {}
    for x in moves:
        if x["move"] == "split" and (x["i"] not in best or x["saved"] > best[x["i"]]["saved"]):
            best[x["i"]] = x
    wins = [x for x in best.values() if x["saved"] > 0]
    print(f"   {len(wins)} of {len(best)} married households pay less filing separately")
    for x in sorted(wins, key=lambda x: -x["saved"])[:12]:
        print("  ", x["i"], x["saved"], {k: x[k] for k in ("inv", "ded", "kids", "itemize")})
    print("\n== IRA dollars that save more than a dollar")
    for x in top(lambda x: x["move"] == "ira", lambda x: x["saved"] / x["amount"]):
        print("  ", x["i"], x["amount"], x["saved"], round(x["saved"] / x["amount"], 2))
    print("\n== earning less leaves the family richer")
    for x in top(lambda x: x["move"] == "earnless" and x["saved"] > x["amount"], lambda x: x["saved"] - x["amount"]):
        print("  ", x["i"], x["amount"], x["saved"], "net gain", x["saved"] - x["amount"])
    print("\n== realizing gains")
    for x in top(lambda x: x["move"] == "gains", lambda x: (x["saved"]) / abs(x["amount"])):
        print("  ", x["i"], x["amount"], x["saved"])


if __name__ == "__main__":
    cmd, hp, wd = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    hs = json.load(open(hp, encoding="utf-8"))
    {"build": build, "score": score}[cmd](hs, wd)
