"""Helpers: run the loop jptax on households, compute net income and tax-only totals."""
import json, subprocess, os, copy
EXE = os.path.expanduser("~/cmp/loop/jp/lean/.lake/build/bin/jptax")


def adult(age=40, wages=0, se=0, pension=0, **ext):
    a = {"age": age, "wages": wages, "selfEmployment": se, "pension": pension}
    a.update(ext)
    return a


def hh(adults, married=None, children=(), **kw):
    h = {"id": kw.pop("id", "x"), "year": 2025, "adults": list(adults),
         "married": (len(adults) == 2) if married is None else married,
         "children": [c if isinstance(c, dict) else {"age": c} for c in children],
         "interest": 0, "dividends": 0, "capitalGains": 0, "rentalIncome": 0, "charitable": 0,
         "pensionContributions": 0}
    h.update(kw)
    return h


def run(hs):
    inp = "\n".join(json.dumps(h, ensure_ascii=False) for h in hs) + "\n"
    out = subprocess.run([EXE], input=inp, capture_output=True, text=True, check=True).stdout
    res = [json.loads(l) for l in out.splitlines() if l.strip()]
    for h, r in zip(hs, res):
        gross = sum(a["wages"] + a.get("bonus", 0) + a["selfEmployment"] + a["pension"] for a in h["adults"])
        gross += sum(c.get("wages", 0) for c in h["children"])
        gross += h["interest"] + h["dividends"] + h["capitalGains"] + h["rentalIncome"]
        tax = r["incomeTax"] + sum(r["surtaxes"].values()) + r["localIncomeTax"]
        outlay = h["charitable"] + h["pensionContributions"] + sum(
            a.get("furusato", 0) + a.get("npo", 0) + a.get("shokibo", 0) + max(a.get("ideco", 0), 0)
            for a in h["adults"])
        r["_tax"] = tax
        r["_social"] = r["employeeSocial"]
        r["_net"] = gross - tax - r["employeeSocial"] + r["benefits"]
        r["_netAfterOutlay"] = r["_net"] - outlay
        r["_gross"] = gross
    return res


def one(h):
    return run([h])[0]


def var(h, path_updates):
    """Copy of h with updates: dict of 'adults.0.furusato' -> value."""
    g = copy.deepcopy(h)
    for k, v in path_updates.items():
        parts = k.split(".")
        o = g
        for p in parts[:-1]:
            o = o[int(p)] if p.isdigit() else o[p]
        last = parts[-1]
        if last.isdigit():
            o[int(last)] = v
        else:
            o[last] = v
    return g


def furusato_limit(h, who=0, step=1000, hi=5000000, onestop=False):
    """Largest donation (multiple of `step`) whose self-burden (donation − tax reduction) is at most 2,000 yen."""
    base = one(h)["_tax"]

    def burden(d):
        g = var(h, {f"adults.{who}.furusato": d, f"adults.{who}.oneStop": onestop})
        return d - (base - one(g)["_tax"])
    lo, up = 0, hi // step
    while lo < up:
        mid = (lo + up + 1) // 2
        if burden(mid * step) <= 2000:
            lo = mid
        else:
            up = mid - 1
    return lo * step, burden(lo * step), burden(lo * step + step)


def furusato_scan(h, who=0, step=1000, hi=2000000, onestop=False, tol=200):
    """Burden curve: [(d, burden)] for d = 0, step, ..., hi; limit = largest d with burden <= 2,000 + tol."""
    ds = list(range(0, hi + 1, step))
    hs = [var(h, {f"adults.{who}.furusato": d, f"adults.{who}.oneStop": onestop}) for d in ds]
    res = run(hs)
    base = res[0]["_tax"]
    curve = [(d, d - (base - r["_tax"])) for d, r in zip(ds, res)]
    lim = max(d for d, b in curve if b <= 2000 + tol)
    return lim, curve
