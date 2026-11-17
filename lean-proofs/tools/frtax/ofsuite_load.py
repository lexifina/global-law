"""Load every YAML test of OpenFisca-France (tests/**) into flat records, with the income year, the input variables
(entity, person id, annual value for that year) and the expected outputs. Shared by ofsuite_inventory.py and
ofsuite_convert.py.
"""
import glob, os, re
import yaml

OFDIR = os.path.expanduser("~/fr/refs/openfisca-france")
ENT_PLURAL = {"individus": "individu", "foyers_fiscaux": "foyer_fiscal", "menages": "menage", "familles": "famille"}
ENT_SINGULAR = {"individu": "individu", "foyer_fiscal": "foyer_fiscal", "menage": "menage", "famille": "famille"}
ROLE_KEYS = {"declarants", "personnes_a_charge", "parents", "enfants", "personne_de_reference", "conjoint",
             "enfants", "autres", "declarant", "personne_a_charge"}


def year_of(period):
    m = re.search(r"(\d{4})", str(period))
    return int(m.group(1)) if m else None


def annual(v, year, monthly_ok=True):
    """Value of an input for income year `year`: a scalar as given; a period dict -> the value for that year, or the
    sum of that year's months. Returns (value, note); value None if the dict has nothing for the year."""
    if not isinstance(v, dict):
        return v, None
    ys = str(year)
    tot, found, note = 0, False, None
    for k, x in v.items():
        k = str(k)
        if k == ys or k == f"year:{ys}":
            return x, None
        if re.fullmatch(rf"{ys}-\d\d", k) or re.fullmatch(rf"month:{ys}-\d\d", k):
            if isinstance(x, (int, float)) and not isinstance(x, bool):
                tot += x
                found = True
            else:
                return x, "monthly non-numeric"
        m = re.fullmatch(r"(?:year:)?(\d{4})(?:-01)?:(\d+)", k)  # e.g. "year:2024:1" or "2024-01:12"
        if m and m.group(1) == ys:
            return x, None
    if found:
        return tot, "months summed"
    return None, "no value for the year"


def walk_entities(inp):
    """-> (persons {pid: {var: raw}}, groups {entity: {gid: {"roles": {role: [pids]}, "vars": {var: raw}}}}, flat)
    flat True when the test gives bare variables (one implicit person and one implicit group of each kind)."""
    keys = set(inp)
    if not keys & (set(ENT_PLURAL) | set(ENT_SINGULAR)):
        return None, None, True
    persons, groups = {}, {}
    for k, v in inp.items():
        if k == "individus":
            for pid, d in (v or {}).items():
                persons[str(pid)] = d or {}
        elif k == "individu":
            persons["_p0"] = v or {}
        elif k in ENT_PLURAL:
            ent = ENT_PLURAL[k]
            for gid, d in (v or {}).items():
                d = d or {}
                roles = {r: ([d[r]] if isinstance(d[r], str) else list(d[r] or [])) for r in d if r in ROLE_KEYS}
                groups.setdefault(ent, {})[str(gid)] = {"roles": roles, "vars": {x: y for x, y in d.items() if x not in ROLE_KEYS}}
        elif k in ENT_SINGULAR:
            ent = ENT_SINGULAR[k]
            d = v or {}
            roles = {r: ([d[r]] if isinstance(d[r], str) else list(d[r] or [])) for r in d if r in ROLE_KEYS}
            groups.setdefault(ent, {})["_g0"] = {"roles": roles, "vars": {x: y for x, y in d.items() if x not in ROLE_KEYS}}
    return persons, groups, False


def load_all(skip_dirs=()):
    recs = []
    files = sorted(glob.glob(OFDIR + "/tests/**/*.yaml", recursive=True) + glob.glob(OFDIR + "/tests/**/*.yml", recursive=True))
    for f in files:
        rel = os.path.relpath(f, OFDIR + "/tests")
        if any(rel.startswith(s) for s in skip_dirs):
            continue
        try:
            docs = yaml.safe_load(open(f))
        except Exception as e:
            recs.append({"file": rel, "idx": 0, "load_error": repr(e)[:200]})
            continue
        if docs is None:
            continue
        for i, t in enumerate(docs if isinstance(docs, list) else [docs]):
            if not isinstance(t, dict):
                continue
            recs.append({"file": rel, "idx": i, "id": f"{rel}#{i}", "name": t.get("name"), "period": t.get("period"),
                         "year": year_of(t.get("period")), "input": t.get("input") or {}, "output": t.get("output") or {},
                         "reforms": t.get("reforms") or t.get("reform"), "extensions": t.get("extensions"),
                         "margin": t.get("absolute_error_margin"), "rel_margin": t.get("relative_error_margin"),
                         "max_spiral_loops": t.get("max_spiral_loops"),
                         "keywords": t.get("keywords")})
    return recs


def output_vars(out):
    """-> list of (variable, entity-or-None, gid-or-None, raw expected)"""
    res = []
    for k, v in out.items():
        if k in ENT_PLURAL and isinstance(v, dict) and all(isinstance(d, dict) or d is None for d in v.values()):
            for gid, d in (v or {}).items():
                for x, y in (d or {}).items():
                    res.append((x, ENT_PLURAL[k], str(gid), y))
        elif k in ENT_SINGULAR and isinstance(v, dict):
            for x, y in (v or {}).items():
                res.append((x, ENT_SINGULAR[k], "_g0", y))
        else:
            res.append((k, None, None, v))
    return res


def input_vars(inp):
    persons, groups, flat = walk_entities(inp)
    if flat:
        return [(k, None, None, v) for k, v in inp.items()]
    res = []
    for pid, d in persons.items():
        for x, y in d.items():
            res.append((x, "individu", pid, y))
    for ent, gs in groups.items():
        for gid, g in gs.items():
            for x, y in g["vars"].items():
                res.append((x, ent, gid, y))
    return res
