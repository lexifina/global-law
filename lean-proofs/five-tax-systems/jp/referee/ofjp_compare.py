"""Referee B comparison: OpenFisca-Japan vs the Lean model (jptax), per adult and per household.
usage: venv-ofjp/bin/python ofjp_compare.py households.jsonl lean_out.jsonl [likeforlike]
Mode 'likeforlike' feeds OpenFisca the Lean model's 合計所得金額 and 社会保険料控除 for every person (adults and
children), so that only the deduction rules and the 住民税 formula are compared."""
import sys, json
from collections import Counter, defaultdict
from openfisca_japan import CountryTaxBenefitSystem
from openfisca_core.simulation_builder import SimulationBuilder

PERIOD = "2025-12-31"
hs = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8") if l.strip()]
lo = [json.loads(l) for l in open(sys.argv[2], encoding="utf-8") if l.strip()]
lfl = len(sys.argv) > 3 and sys.argv[3] == "likeforlike"


def kyuyo(w):   # the Lean model's 給与所得 for a child's wages, recomputed from jptax's own rule (statute table)
    if w < 651000:
        return 0
    if w < 1900000:
        return w - 650000
    if w < 3600000:
        return w // 4000 * 2800 - 80000
    if w < 6600000:
        return w // 4000 * 3200 - 440000
    if w < 8500000:
        return (10 * w - (17600000 + (w - 6600000))) // 10
    return w - 1950000


persons, households, index = {}, {}, []
for k, (h, o) in enumerate(zip(hs, lo)):
    if len(h["adults"]) == 2 and not h.get("married"):
        index.append(None)
        continue
    pids = []
    for j, a in enumerate(h["adults"]):
        pid = "h%d_a%d" % (k, j)
        d = {"誕生年月日": {"ETERNITY": "%d-06-15" % (2025 - a["age"])}, "収入": {PERIOD: a.get("wages", 0)}}
        if len(h["adults"]) == 1 and h.get("children"):
            d["性別"] = {PERIOD: "男性" if h.get("jpSingleParentSex") == "M" else "女性"}
        if lfl:
            p = o["detail"]["persons"][j]
            d["合計所得金額"] = {PERIOD: p["totalIncome_gokeiShotoku"]}
            d["所得"] = {PERIOD: p["totalIncome_gokeiShotoku"]}
            d["社会保険料控除"] = {PERIOD: p["deductions"]["social_shakaiHokenryo"]}
        persons[pid] = d
        pids.append(pid)
    cids = []
    for j, c in enumerate(h.get("children", [])):
        cid = "h%d_c%d" % (k, j)
        d = {"誕生年月日": {"ETERNITY": "%d-06-15" % (2025 - c["age"])}, "収入": {PERIOD: c.get("wages", 0)}}
        if lfl:
            d["合計所得金額"] = {PERIOD: kyuyo(c.get("wages", 0))}
            d["所得"] = {PERIOD: kyuyo(c.get("wages", 0))}
        persons[cid] = d
        cids.append(cid)
    households["h%d" % k] = {"親一覧": pids, "子一覧": cids}
    index.append((pids, cids))

tbs = CountryTaxBenefitSystem()
sim = SimulationBuilder().build_from_entities(tbs, {"世帯員": persons, "世帯一覧": households})
names = ["合計所得金額", "基礎控除", "配偶者控除", "配偶者特別控除", "扶養控除", "ひとり親控除", "社会保険料控除",
         "住民税所得割", "住民税均等割"]
pv = {v: sim.calculate(v, PERIOD) for v in names}
teate = sim.calculate("児童手当", PERIOD)
pidx = {p: i for i, p in enumerate(persons)}
hidx = {x: i for i, x in enumerate(households)}

lean_key = {"合計所得金額": lambda p: p["totalIncome_gokeiShotoku"],
            "基礎控除": lambda p: p["deductions"]["basic_kiso"],
            "配偶者控除": lambda p: p["deductions"]["spouse_haigusha"],
            "配偶者特別控除": lambda p: p["deductions"]["spouseSpecial_haigushaTokubetsu"],
            "扶養控除": lambda p: p["deductions"]["dependants_fuyo"],
            "ひとり親控除": lambda p: p["deductions"]["singleParent_hitorioya"],
            "社会保険料控除": lambda p: p["deductions"]["social_shakaiHokenryo"],
            "住民税所得割": lambda p: p["local"]["incomeLevy_shotokuwari_pref"] + p["local"]["incomeLevy_shotokuwari_muni"],
            "住民税均等割": lambda p: p["local"]["perCapita_kintowari"] + p["local"]["forestEnvironmentTax_shinrin"]}
eq, tot = Counter(), Counter()
ex = defaultdict(list)
hh_ok = 0
nhh = 0
for k, (h, o, ix) in enumerate(zip(hs, lo, index)):
    if ix is None:
        continue
    nhh += 1
    ok = True
    pids, cids = ix
    for j, pid in enumerate(pids):
        lp = o["detail"]["persons"][j]
        for v in names:
            a, b = lean_key[v](lp), float(pv[v][pidx[pid]])
            tot[v] += 1
            if abs(a - b) < 0.5:
                eq[v] += 1
            else:
                ok = False
                ex[v].append((h["id"], j, a, round(b, 2)))
    b = float(teate[hidx["h%d" % k]])
    tot["児童手当(月額×12)"] += 1
    if abs(o["benefits"] - 12 * b) < 0.5:
        eq["児童手当(月額×12)"] += 1
    else:
        ok = False
        ex["児童手当(月額×12)"].append((h["id"], o["benefits"], 12 * b))
    hh_ok += ok
print("mode:", "like-for-like" if lfl else "as is", " households compared:", nhh, " all equal:", hh_ok)

# --- classify the 住民税 differences (like-for-like mode): causes are statutory rules OpenFisca-Japan leaves out
if lfl:
    jdeds = sim.calculate("住民税所得控除", PERIOD)
    hchosei = sim.calculate("調整控除", PERIOD)
    cls = Counter()
    other = []
    for k, (h, o, ix) in enumerate(zip(hs, lo, index)):
        if ix is None:
            continue
        pids, cids = ix
        incomes = [o["detail"]["persons"][j]["totalIncome_gokeiShotoku"] for j in range(len(pids))]
        top = max(range(len(pids)), key=lambda j: (incomes[j], -j))
        for j, pid in enumerate(pids):
            lp = o["detail"]["persons"][j]
            L = lp["local"]
            lean_wari = L["incomeLevy_shotokuwari_pref"] + L["incomeLevy_shotokuwari_muni"]
            of_wari = float(pv["住民税所得割"][pidx[pid]])
            if abs(lean_wari - of_wari) < 0.5:
                continue
            base_exact = max(0, lp["totalIncome_gokeiShotoku"] - L["deductions"])
            lean_chosei = L["adjustmentCredit_choseiKojo_pref"] + L["adjustmentCredit_choseiKojo_muni"]
            of_ded = float(jdeds[pidx[pid]])
            of_chosei = float(hchosei[hidx["h%d" % k]]) if j == top else 0.0
            raw_unrounded = 0.1 * base_exact - lean_chosei
            if lean_wari == 0 and raw_unrounded > 0:
                c = "N: 所得割 not charged under 附則第3条の3 (非課税限度額) / 第295条 — OpenFisca charges it"
            elif abs(of_ded - L["deductions"]) >= 1:
                c = "D: 住民税 deductions differ (OpenFisca's 48万 thresholds / dependant claimant)"
            elif abs(of_chosei - lean_chosei) >= 1:
                c = "H: 調整控除 computed per household by OpenFisca, per taxpayer by 第37条/第314条の6"
            elif abs(lean_wari - of_wari) < 200:
                c = "T: truncations of 地方税法第20条の4の2 (課税標準 to 1,000 yen, 所得割 to 100 yen) not applied by OpenFisca"
            elif lean_wari < raw_unrounded - 200:
                c = "R: 附則第3条の3第2項・第5項 relief near the 非課税限度額 (not in OpenFisca)"
            else:
                c = "?: unexplained"
                other.append((h["id"], j, lean_wari, of_wari, base_exact, lean_chosei, of_chosei))
            cls[c] += 1
    print("\n住民税所得割 differences by cause:")
    for c, n in cls.most_common():
        print("  %5d  %s" % (n, c))
    if other:
        print("  unexplained examples:", other[:8])
    # 均等割
    kin = Counter()
    for k, (h, o, ix) in enumerate(zip(hs, lo, index)):
        if ix is None:
            continue
        for j, pid in enumerate(ix[0]):
            lp = o["detail"]["persons"][j]
            a = lp["local"]["perCapita_kintowari"] + lp["local"]["forestEnvironmentTax_shinrin"]
            b = float(pv["住民税均等割"][pidx[pid]])
            if abs(a - b) >= 0.5:
                kin["lean 0 / OpenFisca 5000: 均等割 非課税 (第295条第1項・第3項, 施行令第47条の3) not in OpenFisca" if a == 0 and b == 5000 else "other %s/%s" % (a, b)] += 1
    print("\n住民税均等割 differences by cause:")
    for c, n in kin.most_common():
        print("  %5d  %s" % (n, c))
for v in names + ["児童手当(月額×12)"]:
    print("  %-14s equal %5d / %5d" % (v, eq[v], tot[v]))
for v, l in ex.items():
    print("\n==", v, len(l), "differences; first:", l[:6])
