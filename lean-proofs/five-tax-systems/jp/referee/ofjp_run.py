"""Referee B: OpenFisca-Japan (project-inclusive/OpenFisca-Japan, v2.2.0) on canonical households.
Run with the venv's python: venv-ofjp/bin/python ofjp_run.py households.jsonl > out.jsonl
Only married couples and single adults (with or without children) are mapped; wages, ages and children's wages only.
Period: 2025-12-31 (OpenFisca-Japan variables are DAY-valued annual amounts)."""
import sys, json
from openfisca_japan import CountryTaxBenefitSystem
from openfisca_core.simulation_builder import SimulationBuilder

PERIOD = "2025-12-31"
VARS_P = ["合計所得金額", "給与所得控除額", "基礎控除", "配偶者控除", "配偶者特別控除", "扶養控除", "ひとり親控除",
          "社会保険料控除", "社会保険料", "住民税所得控除", "住民税所得割", "住民税均等割", "住民税"]
VARS_H = ["児童手当", "調整控除", "住民税非課税世帯"]

hs = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8") if l.strip()]
tbs = CountryTaxBenefitSystem()
persons, households, index = {}, {}, []
for k, h in enumerate(hs):
    if len(h["adults"]) == 2 and not h.get("married"):
        index.append(None)
        continue
    pids = []
    for j, a in enumerate(h["adults"]):
        pid = "h%d_a%d" % (k, j)
        persons[pid] = {"誕生年月日": {"ETERNITY": "%d-06-15" % (2025 - a["age"])},
                        "収入": {PERIOD: a.get("wages", 0)}}
        if len(h["adults"]) == 1 and h.get("children"):
            persons[pid]["性別"] = {PERIOD: "男性" if h.get("jpSingleParentSex") == "M" else "女性"}
        pids.append(pid)
    cids = []
    for j, c in enumerate(h.get("children", [])):
        cid = "h%d_c%d" % (k, j)
        persons[cid] = {"誕生年月日": {"ETERNITY": "%d-06-15" % (2025 - c["age"])},
                        "収入": {PERIOD: c.get("wages", 0)}}
        cids.append(cid)
    households["h%d" % k] = {"親一覧": pids, "子一覧": cids}
    index.append((pids, cids))

sim = SimulationBuilder().build_from_entities(tbs, {"世帯員": persons, "世帯一覧": households})
pv = {v: sim.calculate(v, PERIOD) for v in VARS_P}
hv = {v: sim.calculate(v, PERIOD) for v in VARS_H}
porder = list(persons.keys())
pidx = {p: i for i, p in enumerate(porder)}
horder = list(households.keys())
hidx = {x: i for i, x in enumerate(horder)}
for k, (h, ix) in enumerate(zip(hs, index)):
    if ix is None:
        print(json.dumps({"id": h["id"], "skipped": "unmarried couple"}, ensure_ascii=False))
        continue
    pids, cids = ix
    out = {"id": h["id"], "adults": [{v: float(pv[v][pidx[p]]) for v in VARS_P} for p in pids],
           "household": {v: (float(hv[v][hidx["h%d" % k]]) if hv[v].dtype != bool else bool(hv[v][hidx["h%d" % k]]))
                         for v in VARS_H}}
    print(json.dumps(out, ensure_ascii=False))
