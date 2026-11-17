"""Adapter: our 2042-box returns -> Publicodes modele-social (betagouv/mon-entreprise, npm modele-social).

Scope (what the rules can express): one household, situation single/divorced (célibataire), married/pacsed (couple)
or widowed (veuf); n dependent children (0CF, no shared custody, no disability); case T (parent isolé) for a single
parent; exactly one salary (1AJ or 1BJ, with the 10 % allowance); net income without allowance (4BA) entered as
"autres revenus imposables". Publicodes 'date' is the year of payment: income year + 1.
"""
import json, os, subprocess

NODE = os.path.expanduser("~/fr/refs/impl/node/bin/node")
PKG = os.path.expanduser("~/fr/refs/impl/publicodes")
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "impl_publicodes_run.mjs")
RUNNER = PKG + "/run.mjs"  # ESM resolves packages from the script's own directory: copied there
SIT = {"0AC": "célibataire", "0AD": "célibataire", "0AM": "couple", "0AO": "couple", "0AV": "veuf"}
NAME = "Publicodes modele-social 11.1.0 (betagouv/mon-entreprise)"
KEY = "publicodes"
YEARS = range(2020, 2026)  # rules carry figures for payment years 2021-2026
FIELDS = ["NBPT", "RNI", "REVKIRE", "IDRS", "IDEC", "IDRS4", "CHRAPRES"]


def in_scope(b):
    allowed = set(SIT) | {"0DA", "0DB", "0CF", "0BT", "1AJ", "1BJ", "4BA"} | {f"0F{i}" for i in range(10)}
    if not all(k in allowed for k in b):
        return False
    if sum(k in b for k in SIT) != 1:
        return False
    if "1AJ" in b and "1BJ" in b:
        return False
    if "0BT" in b and not (("0AC" in b or "0AD" in b) and b.get("0CF", 0) > 0):
        return False
    return True


def situation(year, b):
    sit = next(SIT[k] for k in SIT if k in b)
    s = {"date": f"'01/01/{year + 1}'", "dirigeant": "non", "impôt . méthode de calcul": "'barème standard'",
         "impôt . foyer fiscal . situation de famille": f"'{sit}'",
         "impôt . foyer fiscal . enfants à charge": str(int(b.get("0CF", 0)))}
    if "0BT" in b:
        s["impôt . foyer fiscal . parent isolé"] = "oui"
    sal = b.get("1AJ", b.get("1BJ", 0))
    s["salarié . rémunération . net . imposable"] = f"{sal} €/an"
    if b.get("4BA"):
        s["impôt . foyer fiscal . revenu imposable . autres revenus imposables"] = f"{b['4BA']} €/an"
    return s


def run(cases):
    """cases: list of dicts {id, year, boxes}; returns ({id: outputs}, total_microseconds_in_engine)."""
    inp = "".join(json.dumps({"id": c["id"], "situation": situation(c["year"], c["boxes"])}) + "\n" for c in cases)
    import shutil; shutil.copyfile(SRC, RUNNER)
    env = dict(os.environ)
    r = subprocess.run([NODE, RUNNER], input=inp, capture_output=True, text=True, env=env, cwd=PKG)
    out, us = {}, 0.0
    for l in r.stdout.splitlines():
        d = json.loads(l)
        o = d["out"]
        # common names: IDRS4 = tax after QF cap and décote, before reductions (publicodes: impôt sur le revenu)
        o["IDRS4"] = o.get("IR")
        o["CHRAPRES"] = o.get("CEHR")
        out[d["id"]] = o
        us += d["us"]
    if r.returncode:
        raise RuntimeError(r.stderr[-2000:])
    return out, us
