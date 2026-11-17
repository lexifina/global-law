"""Adapter: our 2042-box returns -> INES (Insee, Drees, Cnaf; gitlab.com/insee_drees_cnaf/ines-public, R, CeCILL 2.1),
its income-tax chain 07_impot_revenus.R run by impl_ines_run.R on tables built from the boxes (no ERFS data).

Scope: income 2020-2024 (INES parameters 'valeur_INES_2021' .. '_2025' = tax paid 2021-2025); every box whose
exact label (INES dictionary, 2042 form of income 2021) is read by the tax chain (runs/impl/ines/used_boxes.json),
plus the family boxes INES's SIF fields carry (0AM/0AO/0AC/0AD/0AV, 0AL 0AN 0AP 0AF 0AW 0AS 0AG 0BT 0AZ,
0CF 0CG 0CR 0DJ 0DN 0CH 0CI, 0DA 0DB; children's birth years are not used by INES).
"""
import concurrent.futures as cf, json, os, subprocess, tempfile, time

FR = os.path.expanduser("~/fr")
RSCRIPT = f"{FR}/refs/impl/mamba/renv/bin/Rscript"
INES = f"{FR}/refs/impl/ines-public"
RUNNER = f"{FR}/harness/impl_ines_run.R"
NAME = "INES 2024.1 (Insee/Drees/Cnaf, R)"
KEY = "ines"
YEARS = range(2020, 2025)
FIELDS = ["NBPT", "RNI", "REVKIRE", "IDRS", "IDEC", "IDRS4", "CHRAPRES", "IMPNET"]
FAMILY = {"0AM", "0AO", "0AC", "0AD", "0AV", "0AL", "0AN", "0AP", "0AF", "0AW", "0AS", "0AG", "0BT", "0AZ",
          "0CF", "0CG", "0CR", "0DJ", "0DN", "0CH", "0CI", "0DA", "0DB"}
_used = None


def used():
    global _used
    if _used is None:
        p = f"{FR}/runs/impl/ines/used_boxes.json"
        if not os.path.exists(p):
            os.makedirs(os.path.dirname(p), exist_ok=True)
            dummy = f"{FR}/runs/impl/ines/empty.json"
            open(dummy, "w").write("[]")
            subprocess.run([RSCRIPT, RUNNER, INES, dummy, p, "--used-boxes"], capture_output=True)
        _used = {}
        for u in json.load(open(p)):
            _used.setdefault(int(u["annee"]), set()).add(u["case_fiscale"][2:].upper())
    return _used


SCOPE_BY_YEAR = True


def in_scope(b, year):
    """every box read by INES's tax chain under that year's label (its own dictionary for the form of that year)"""
    u = used().get(year, set())
    return all(k in FAMILY or k in u or (k[:2] in ("0F", "0H", "0J", "0P") and k[2:].isdigit()) for k in b)


OVERTIME = {"1GH": "1AJ", "1HH": "1BJ", "1IH": "1CJ", "1JH": "1DJ"}
# Income that the flat tax (PFU, art. 200 A) reaches when 2OP is not ticked: INES books that 12.8 % in the year it is
# paid (pfu_n1 = lag of the previous year's row), so a one-year table has no value for it: IMPNET not compared then.
PFU_BOXES = {"2DC", "2TR", "2TS", "2FU", "2CH", "2EE", "2VV", "2WW", "2ZZ", "2YY", "2TT", "2TQ", "2ZA", "3VG", "3VZ",
             "3UA", "3AN", "3TJ", "3TK", "2CG", "2AB", "2CK", "2BH"}


def ines_boxes(b):
    """NOT USED: tried and wrong. INES reads 1GH itself (its "salaires" aggregate includes the exempt-overtime label and
    calcule_rbg subtracts exo_hsup = min(hsup, cap)), so the boxes go in unchanged."""
    b = dict(b)
    for ot, sal in OVERTIME.items():
        if b.get(ot):
            b[sal] = b.get(sal, 0) + b[ot]
    return b


def _chunk(cases):
    d = tempfile.mkdtemp(prefix="ines_", dir=f"{FR}/runs/impl/ines")
    json.dump([{"id": c["id"], "year": c["year"], "boxes": c["boxes"]} for c in cases], open(f"{d}/in.json", "w"))
    pfu = {c["id"]: (not c["boxes"].get("2OP")) and any(k in PFU_BOXES for k in c["boxes"]) for c in cases}
    r = subprocess.run([RSCRIPT, RUNNER, INES, f"{d}/in.json", f"{d}/out.json"], capture_output=True, text=True)
    if not os.path.exists(f"{d}/out.json"):
        return {c["id"]: {"_error": r.stderr[-300:]} for c in cases}, 0.0
    o = json.load(open(f"{d}/out.json"))
    res = {}
    for row in o["rows"]:
        g = lambda k: row.get(k)
        res[row["id"]] = {"NBPT": g("npart"), "RNI": g("rib"), "REVKIRE": g("rfr"), "IDRS": g("impot2"),
                          "IDEC": g("decote1"), "IDRS4": g("impot3"), "CHRAPRES": g("cehr"),
                          "IMPNET": None if g("impot_du") is None or pfu[row["id"]] else g("impot_du") - (g("cehr") or 0),
                          "raw": row}
    for f in ("in.json", "out.json"):
        os.remove(f"{d}/{f}")
    os.rmdir(d)
    return res, o["seconds"]


def run(cases, chunk=4000, jobs=10):
    """-> ({id: outputs}, engine microseconds summed over chunks: R's vectorised chain, without R start-up)"""
    parts = [cases[i:i + chunk] for i in range(0, len(cases), chunk)]
    out, secs = {}, 0.0
    with cf.ThreadPoolExecutor(jobs) as ex:
        for r, s in ex.map(_chunk, parts):
            out.update(r)
            secs += s
    return out, secs * 1e6
