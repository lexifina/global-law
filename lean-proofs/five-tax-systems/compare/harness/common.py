"""Shared pieces of the five-country harness: parameters, the canonical household, running each country's exe.

Every country's model reads canonical households (JSONL, amounts in whole local currency units, ~/cmp/shared/CONTRACT.md)
and writes one result line per household. Incomes are set in multiples of each country's average wage (AW, OECD Taxing
Wages 2026, 2025 values; data/params.json) so that the same household means the same place in each country's wage
distribution.
"""
import hashlib
import json
import os
import shutil
import subprocess
import time

HOME = os.path.expanduser("~")
ROOT = os.path.join(HOME, "cmp", "compare")
PARAMS = json.load(open(os.path.join(ROOT, "data", "params.json")))
COUNTRIES = ["US", "FR", "UK", "DE", "JP"]
CUR = {c: PARAMS["countries"][c]["currency"] for c in COUNTRIES}
AW = {c: PARAMS["countries"][c]["aw"] for c in COUNTRIES}
PPP = {c: PARAMS["countries"][c]["ppp_oecd"] for c in COUNTRIES}
PPP_CONS = {c: PARAMS["countries"][c]["ppp_wb_consumption"] for c in COUNTRIES}
YEAR = 2025

CMPTAX = os.path.join(ROOT, "lean", ".lake", "build", "bin", "cmptax")
EXES = {
    "US": ([CMPTAX, "us"], None),
    "FR": ([CMPTAX, "fr"], None),
    "UK": ([os.path.join(HOME, "cmp", "uk", "lean", ".lake", "build", "bin", "uktax")], None),
    "DE": ([os.path.join(HOME, "cmp", "de", "lean", ".lake", "build", "bin", "detax")], None),
    "JP": ([os.path.join(HOME, "cmp", "jp", "lean", ".lake", "build", "bin", "jptax")], None),
}
# Overrides written when a country's EXAMPLE.md names another command line (one JSON list per country).
_ovr = os.path.join(ROOT, "harness", "exes.json")
if os.path.exists(_ovr):
    for k, v in json.load(open(_ovr)).items():
        EXES[k] = (v["cmd"], v.get("cwd"))


# A frozen set of binaries for a whole run (harness/freeze.py, exported by final_run.sh as CMP_FROZEN)
_fz = os.environ.get("CMP_FROZEN")
if _fz and os.path.exists(os.path.join(_fz, "frozen.json")):
    for k, v in json.load(open(os.path.join(_fz, "frozen.json"))).items():
        if v.get("ok"):
            EXES[k] = (v["cmd"], v.get("cwd"))


def available(country):
    cmd, _ = EXES[country]
    return os.path.exists(cmd[0]) and os.access(cmd[0], os.X_OK)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def snapshot_exe(country, run_dir):
    """Copy the country's exe into the run folder (so a rebuild during a run cannot change it) and return the command
    line and the exe's hash."""
    cmd, cwd = EXES[country]
    os.makedirs(os.path.join(run_dir, "bin"), exist_ok=True)
    dst = os.path.join(run_dir, "bin", f"{country.lower()}_" + os.path.basename(cmd[0]))
    if not os.path.exists(dst):
        shutil.copy2(cmd[0], dst)
    return [dst] + cmd[1:], cwd, sha256(dst)


def money(x):
    return int(round(x))


def adult(age=40, wages=0, se=0, pension=0):
    return {"age": age, "wages": money(wages), "selfEmployment": money(se), "pension": money(pension)}


def household(hid, adults, married=False, children=(), interest=0, dividends=0, capitalGains=0, rentalIncome=0,
              charitable=0, pensionContributions=0, year=YEAR):
    return {"id": hid, "year": year, "adults": adults, "married": married,
            "children": [{"age": a} for a in children], "interest": money(interest), "dividends": money(dividends),
            "capitalGains": money(capitalGains), "rentalIncome": money(rentalIncome), "charitable": money(charitable),
            "pensionContributions": money(pensionContributions)}


def gross(h):
    return (sum(a["wages"] + a["selfEmployment"] + a["pension"] for a in h["adults"]) + h["interest"]
            + h["dividends"] + h["capitalGains"] + h["rentalIncome"])


def surtax_total(o):
    return sum(v for v in (o.get("surtaxes") or {}).values())


def net(o, g):
    return g - o["incomeTax"] - surtax_total(o) - o.get("localIncomeTax", 0) - o["employeeSocial"] + o.get("benefits", 0)


def run_exe(cmd, cwd, households, timeout=3600):
    inp = "".join(json.dumps(h, separators=(",", ":")) + "\n" for h in households)
    t0 = time.time()
    p = subprocess.run(cmd, cwd=cwd, input=inp, capture_output=True, text=True, timeout=timeout)
    dt = time.time() - t0
    if p.returncode != 0:
        raise RuntimeError(f"{cmd} exited {p.returncode}: {p.stderr[:2000]}")
    outs = [json.loads(l) for l in p.stdout.splitlines() if l.strip()]
    if len(outs) != len(households):
        raise RuntimeError(f"{cmd}: {len(households)} households in, {len(outs)} lines out; stderr {p.stderr[:500]}")
    for h, o in zip(households, outs):
        if o.get("id") != h["id"]:
            raise RuntimeError(f"{cmd}: id mismatch {h['id']} vs {o.get('id')}")
    return outs, dt


# Elections the law leaves to the taxpayer and that a model takes as an input instead of making itself. The comparison
# assumes every household makes the cheapest one, as the other models already do inside: France's adapter takes the
# cheaper of the flat levy and the scale (CGI art. 200 A, 2), Germany applies § 32d (6) EStG when cheaper, the UK model
# sets reliefs as ITA 2007 s. 25(2) orders. Japan (JP FINDINGS F16): listed-share dividends left to final withholding
# (措置法第8条の5, the model's default), declared separately (第8条の4) or taxed with other income with the 配当控除
# (所得税法第92条); listed-share gains withheld (特定口座, default) or declared (第37条の11). Germany: spouses choose
# joint assessment with splitting (§ 26b, the model's default) or individual assessment (§ 26a; `detax --separate`),
# EStG § 26 (1). Not run: US married filing separately (the adapter files jointly), France (joint taxation is compulsory
# for married and PACS partners, CGI art. 6). Each rule: when it applies, the household field it sets or the command-line
# arguments it adds, and its values, the model's default first.
ELECTIONS = {
    "JP": [{"applies": lambda h: h.get("dividends", 0) > 0, "field": "jpDividends",
            "values": ["separate", "declared", "aggregate"]},
           {"applies": lambda h: h.get("capitalGains", 0) > 0, "field": "jpGains", "values": ["withheld", "declared"]}],
    "DE": [{"applies": lambda h: bool(h.get("married")) and len(h.get("adults", [])) == 2, "name": "deAssessment",
            "values": ["joint", "separate"], "args": {"joint": [], "separate": ["--separate"]}}],
}


def is_default(country, cmb):
    """True when every choice in `cmb` is the model's default (the first value of its rule)."""
    rules = ELECTIONS.get(country, [])
    return all(cmb[k] == next(r["values"][0] for r in rules if r.get("field", r.get("name")) == k) for k in cmb)


def run_with_elections(country, cmd, cwd, households, timeout=3600):
    """run_exe, then for each household that an election applies to (and that does not fix the election itself) run
    every combination and keep the one with the highest net income. The chosen election and the default's net income
    go into the output's detail (`cmp_election`, `cmp_net_default`); returns (outs, seconds, {id: election})."""
    outs, dt = run_exe(cmd, cwd, households, timeout)
    rules = ELECTIONS.get(country)
    if not rules:
        return outs, dt, {}
    groups = {}  # extra command-line arguments -> [(index, election, household variant)]
    nv = 0
    for i, h in enumerate(households):
        opts = [r for r in rules if r["applies"](h) and r.get("field", r.get("name")) not in h]
        if not opts:
            continue
        combos = [{}]
        for r in opts:
            key = r.get("field", r.get("name"))
            combos = [dict(c, **{key: v}) for c in combos for v in r["values"]]
        for cmb in combos:
            hv = dict(h)
            args = []
            for r in opts:
                if "field" in r:
                    hv[r["field"]] = cmb[r["field"]]
                else:
                    args += r["args"][cmb[r["name"]]]
            hv["id"] = f"{h['id']}#e{nv}"
            nv += 1
            groups.setdefault(tuple(args), []).append((i, cmb, hv))
    if not groups:
        return outs, dt, {}
    best = {}
    for args, variants in groups.items():
        vouts, dt2 = run_exe(list(cmd) + list(args), cwd, [v[2] for v in variants], timeout)
        dt += dt2
        for (i, cmb, hv), o in zip(variants, vouts):
            n = net(o, gross(hv))
            # ties keep the model's default (first in every rule's values)
            first = is_default(country, cmb)
            if i not in best or n > best[i][0] + 1e-9 or (abs(n - best[i][0]) <= 1e-9 and first):
                best[i] = (n, cmb, o)
    chosen = {}
    for i, (n, cmb, o) in best.items():
        h = households[i]
        o = dict(o, id=h["id"])
        o["detail"] = dict(o.get("detail") or {}, cmp_election=cmb, cmp_net_default=net(outs[i], gross(h)))
        outs[i] = o
        chosen[h["id"]] = cmb
    return outs, dt, chosen


def tidy_row(country, h, o, meta=None):
    """One row of the results table: the household, the country's figures and the derived totals."""
    g = gross(h)
    st = o.get("surtaxes") or {}
    row = {"id": h["id"], "country": country, "currency": o.get("currency", CUR[country]), "gross": g,
           "gross_aw": g / AW[country], "gross_usd_ppp": g / PPP[country],
           "incomeTax": o["incomeTax"], "surtaxes": surtax_total(o), "localIncomeTax": o.get("localIncomeTax", 0),
           "employeeSocial": o["employeeSocial"], "benefits": o.get("benefits", 0)}
    row["net"] = net(o, g)
    row["taxes_all"] = g - row["net"]
    for k, v in st.items():
        row["surtax_" + k] = v
    row["detail"] = o.get("detail", {})
    row["unsupported"] = o.get("unsupported", [])
    if isinstance(row["detail"], dict) and "cmp_election" in row["detail"]:
        row["election"] = row["detail"]["cmp_election"]
        row["net_default"] = row["detail"]["cmp_net_default"]
    if meta:
        row.update(meta)
    return row
