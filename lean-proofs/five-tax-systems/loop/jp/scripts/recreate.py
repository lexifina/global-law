"""Recreate the catalogue's techniques (a)/(b) with the loop jptax. Prints one row per technique:
id | scenario | Δ tax (income+復興+住民税) | Δ employee social | Δ benefits | Δ net income after the outlay | note
Saving = − Δtax − Δsocial + Δbenefits (positive = the technique saves money). Outlays (donations, contributions) are
shown separately where the technique is a deduction for money spent."""
import sys, json
sys.path.insert(0, __import__("os").path.dirname(__file__))
from jp import adult, hh, run, one, var, furusato_scan


def furusato_limit(h):
    lim, c = furusato_scan(h, hi=1500000)
    d = dict(c)
    return lim, d[lim], d.get(lim + 10000)

rows = []


def cmp(cid, name, without, with_, note="", outlay=0):
    a, b = run([without, with_])
    dt = b["_tax"] - a["_tax"]
    ds = b["_social"] - a["_social"]
    db = b["benefits"] - a["benefits"]
    dn = b["_net"] - a["_net"]
    rows.append(dict(id=cid, name=name, dTax=dt, dSocial=ds, dBenefits=db, dNet=dn, outlay=outlay,
                     saving=-dt - ds + db, netOfOutlay=-dt - ds + db - outlay, note=note,
                     taxWithout=a["_tax"], taxWith=b["_tax"]))


# C01 ふるさと納税: limit and the 2,000-yen cost (single, 5,000,000; couple 7,000,000 + child)
for w in (3000000, 5000000, 7000000, 10000000, 20000000):
    h = hh([adult(35, w)])
    lim, bur, bur1 = furusato_limit(h)
    rows.append(dict(id="C01", name=f"ふるさと納税 limit, single wage {w:,}", limit=lim, burdenAtLimit=bur,
                     burdenAt10000More=bur1, note="確定申告"))
# C01b ワンストップ vs 確定申告 at the same donation
for w in (3000000, 5000000, 10000000):
    h = hh([adult(35, w)])
    lim, _, _ = furusato_limit(h)
    cmp("C01b", f"ワンストップ vs 確定申告, wage {w:,}, donation {lim:,}",
        var(h, {"adults.0.furusato": lim}), var(h, {"adults.0.furusato": lim, "adults.0.oneStop": True}))
# C02 iDeCo, employee without a company plan (276,000 a year)
for w in (3000000, 5000000, 8000000):
    h = hh([adult(35, w)])
    cmp("C02", f"iDeCo 276,000, wage {w:,}", h, var(h, {"adults.0.ideco": 276000}), outlay=276000)
# C03 小規模企業共済 840,000 for a sole proprietor (business 8,000,000; 国保/国民年金 not modelled)
h = hh([adult(45, 0, 8000000)])
cmp("C03", "小規模企業共済 840,000, business 8,000,000", h, var(h, {"adults.0.shokibo": 840000}), outlay=840000)
cmp("C03b", "iDeCo 816,000 + 小規模企業共済 840,000, business 8,000,000", h,
    var(h, {"adults.0.shokibo": 840000, "adults.0.ideco": 816000}), outlay=1656000)
# C04 NISA: 1,000,000 of dividends and 1,000,000 of gains inside vs outside NISA
h = hh([adult(40, 5000000)], dividends=1000000, capitalGains=1000000)
cmp("C04", "NISA: 1,000,000 dividends + 1,000,000 gains tax-free", h, var(h, {"dividends": 0, "capitalGains": 0}),
    note="income itself unchanged; only the tax")
rows[-1]["saving"] = rows[-1]["saving"] - 0  # Δnet includes the income drop; saving = −Δtax
rows[-1]["dNet"] = rows[-1]["saving"]
# C05 配当 課税方式 (F16): wage 3,000,000 + dividends 1,000,000; and wage 9,000,000 + dividends 1,000,000
for w in (0, 3000000, 9000000):
    for mode in ("aggregate", "declared"):
        h = hh([adult(40, w)], dividends=1000000)
        cmp("C05", f"dividends 1,000,000 {mode} vs 確定申告不要, wage {w:,}", h, var(h, {"jpDividends": mode}))
# C06 損益通算: 1,000,000 dividends declared with a 600,000 listed-share loss (措置法第37条の12の2; pre-netted)
h = hh([adult(40, 5000000)], dividends=1000000)
cmp("C06", "listed-share loss 600,000 set against 1,000,000 dividends", h, var(h, {"dividends": 400000}),
    note="model has no negative gains: the netting of 措置法第37条の12の2 is applied to the input")
rows[-1]["note"] += "; saving = the tax on 600,000"
# C07 扶養の付け替え: couple 6,000,000 + 4,000,000, children 17 and 20; who claims
h = hh([adult(48, 6000000), adult(46, 4000000)], children=[17, 20])
cmp("C07", "children 17, 20 claimed by the 4,000,000 earner instead of the 6,000,000 earner", h,
    var(h, {"children.0.claimant": 1, "children.1.claimant": 1}))
h = hh([adult(48, 9000000), adult(46, 4000000)], children=[17, 20])
cmp("C07b", "children 17, 20 split: 20 to the 9,000,000 earner, 17 to the 4,000,000 earner (vs both to top)", h,
    var(h, {"children.0.claimant": 1}))
# C08 年少扶養 to the lower earner for the 住民税 非課税 limit (第295条 / 附則第3条の3)
h = hh([adult(40, 6000000), adult(38, 1300000)], children=[8, 5])
cmp("C08", "children 8, 5 (年少扶養) assigned to the 1,300,000 earner", h,
    var(h, {"children.0.claimant": 1, "children.1.claimant": 1}))
# C09 配偶者の年収の壁 management (F5): spouse 1,059,999 vs 1,060,000 (106万, large employer)
h = hh([adult(40, 6000000), adult(38, 1056000)], children=[8, 5])
cmp("C09", "spouse keeps pay at 1,055,999 instead of 1,056,000 (106万: 88,000 a month)", h, var(h, {"adults.1.wages": 1055999}),
    note="see F5 wall_106")
h = hh([adult(40, 6000000), adult(38, 1700000)])
cmp("C09b", "spouse 1,600,000 vs 1,700,000 (配偶者特別控除 steps, after insurance)", h,
    var(h, {"adults.1.wages": 1600000}))
# C10 特定親族特別控除: student 1,500,000 vs 1,230,000 (F4/F5)
h = hh([adult(50, 6000000), adult(48, 0)], children=[{"age": 20, "wages": 1500000}])
cmp("C10", "student earns 1,500,000 instead of 1,230,000 (parent keeps 630,000 deduction)",
    var(h, {"children.0.wages": 1230000}), h)
# C11 医療費控除 vs セルフメディケーション
h = hh([adult(40, 4000000, medical=150000, otc=60000)])
cmp("C11", "セルフメディケーション (otc 60,000) instead of 医療費控除 (medical 150,000)", h,
    var(h, {"adults.0.selfMed": True}))
h = hh([adult(40, 4000000, medical=80000, otc=60000)])
cmp("C11b", "セルフメディケーション when medical is 80,000 (below 100,000)", h, var(h, {"adults.0.selfMed": True}))
# C12 医療費 claimed by the lower-income spouse (5 % of 総所得金額等 below 2,000,000)
h = hh([adult(40, 7000000, medical=150000), adult(38, 1600000)])
cmp("C12", "family medical 150,000 claimed by the 1,600,000 spouse instead of the 7,000,000 earner", h,
    var(h, {"adults.0.medical": 0, "adults.1.medical": 150000}))
h = hh([adult(40, 12000000, medical=150000), adult(38, 1600000)])
cmp("C12b", "the same with a 12,000,000 earner", h, var(h, {"adults.0.medical": 0, "adults.1.medical": 150000}))
# C13 住宅ローン控除: 4,500,000 wage, balance 30,000,000 (limit 30,000,000), 所得税 too small: 住民税 residual
for w in (4500000, 8000000):
    h = hh([adult(35, w)])
    cmp("C13", f"住宅ローン控除 balance 30,000,000, wage {w:,}", h,
        var(h, {"adults.0.housingBalance": 30000000, "adults.0.housingLimit": 30000000}))
# C14 住宅ローン控除 + ふるさと納税: 確定申告 vs ワンストップ
h = hh([adult(35, 4500000, housingBalance=30000000, housingLimit=30000000, furusato=50000)])
cmp("C14", "housing loan + furusato 50,000: ワンストップ instead of 確定申告", h, var(h, {"adults.0.oneStop": True}))
# C15 生命保険料控除 (three new-contract categories at 80,000)
h = hh([adult(40, 5000000)])
cmp("C15", "生命保険料 80,000 × 3 categories", h, var(h, {"adults.0.lifeIns": [80000, 80000, 80000]}), outlay=240000)
cmp("C15b", "地震保険料 50,000", h, var(h, {"adults.0.earthquake": 50000}), outlay=50000)
# C16 青色申告特別控除 65万 (business 5,000,000)
h = hh([adult(45, 0, 5000000)])
cmp("C16", "青色申告特別控除 650,000 (e-Tax) vs 白色, business 5,000,000", h, var(h, {"adults.0.aoiro": 650000}))
cmp("C16b", "65万 vs 10万", var(h, {"adults.0.aoiro": 100000}), var(h, {"adults.0.aoiro": 650000}))
# C17 給与所得 vs 事業所得 (tax only; 国保/国民年金 not modelled)
for x in (3000000, 6000000, 10000000):
    cmp("C17", f"{x:,} as 事業所得 (青色 65万) instead of 給与 (tax only)", hh([adult(45, x)]),
        hh([adult(45, 0, x, aoiro=650000)]), note="employee social removed, NHI/NP not modelled: see Δtax only")
# C18 青色事業専従者給与 (第57条): business 10,000,000 vs 7,000,000 + spouse paid 3,000,000
h = hh([adult(45, 0, 10000000, aoiro=650000), adult(43, 0)])
cmp("C18", "青色事業専従者給与 3,000,000 to the spouse (business 10,000,000)", h,
    hh([adult(45, 0, 7000000, aoiro=650000), adult(43, 3000000, senjusha=True)]))
h = hh([adult(45, 0, 6000000, aoiro=650000), adult(43, 0)])
cmp("C18b", "青色事業専従者給与 1,000,000 to the spouse (business 6,000,000)", h,
    hh([adult(45, 0, 5000000, aoiro=650000), adult(43, 1000000, senjusha=True)]))
# C19 寡婦控除
h = hh([adult(55, 3000000)])
cmp("C19", "寡婦控除, wage 3,000,000", h, var(h, {"adults.0.widow": True}))
h = hh([adult(55, 2040000)])
cmp("C19b", "寡婦: 住民税 非課税 at 合計所得金額 ≤ 1,350,000 (wage 2,040,000)", h, var(h, {"adults.0.widow": True}))
# C20 ひとり親 (F5 wall_single_parent_135): single mother 2,044,000 vs 2,045,000
h = hh([adult(35, 2044000)], married=False, children=[6])
cmp("C20", "single mother keeps pay at 2,043,999 instead of 2,044,000 (住民税 非課税 135万)", h,
    var(h, {"adults.0.wages": 2043999}))
# C21 選択制DC: 276,000 of salary into company DC (salary falls; no outlay from net pay)
for w in (3000000, 5000000, 8000000):
    h = hh([adult(35, w)])
    cmp("C21", f"選択制DC 276,000 out of wage {w:,} (vs iDeCo of the same amount)",
        var(h, {"adults.0.ideco": 276000}), var(h, {"adults.0.wages": w - 276000}),
        note="both put 276,000 into a DC plan; Δ = 選択制 − iDeCo")
# C22 賞与 shift: 12,000,000 as salary vs 3,000,000 salary + 9,000,000 single bonus
cmp("C22", "12,000,000: salary only vs 3,000,000 salary + 9,000,000 December bonus", hh([adult(45, 12000000)]),
    hh([adult(45, 3000000, bonus=9000000)]))
cmp("C22b", "7,200,000: salary only vs 4,800,000 + 2,400,000 bonus", hh([adult(45, 7200000)]),
    hh([adult(45, 4800000, bonus=2400000)]))
# C23 106万 excludes bonuses: part-timer 87,999 × 12 + 300,000 bonus vs the same pay monthly
cmp("C23", "spouse: 1,255,988 as 87,999/month + 200,000 bonus vs 104,666/month",
    hh([adult(40, 6000000), adult(38, 1255988)]), hh([adult(40, 6000000), adult(38, 1055988, bonus=200000)]),
    note="賞与 not in the 88,000 test; under 130万 so a 被扶養者 (no contributions)")
# C24 認定NPO: 税額控除 vs 所得控除
for w in (3000000, 8000000, 20000000):
    h = hh([adult(40, w, npo=100000)])
    cmp("C24", f"認定NPO 100,000: 税額控除 instead of 所得控除, wage {w:,}", h, var(h, {"adults.0.npoCredit": True}))
# C25 児童手当: third-child rate kept by counting a supported 20-year-old
h = hh([adult(45, 6000000), adult(43, 0)], children=[20, 12, 8])
cmp("C25", "children 12, 8 with a supported 20-year-old (counts for birth order) vs without",
    hh([adult(45, 6000000), adult(43, 0)], children=[12, 8]), h,
    note="the 20-year-old also gives 特定扶養 630,000")
# C26 Marry by 31 December (第85条: status on 31 Dec)
cmp("C26", "couple 6,000,000 / 0 married by 31 Dec vs not", hh([adult(35, 6000000), adult(33, 0)], married=False),
    hh([adult(35, 6000000), adult(33, 0)], married=True))
# C27 老人扶養: supporting a parent aged 75 with no income (480,000)
h = hh([adult(50, 7000000)])
cmp("C27", "claim a parent aged 75 (老人扶養親族 480,000)", h, var(h, {"children": [{"age": 75}]}))
# C28 iDeCo for a non-earning spouse: no tax saving
h = hh([adult(40, 6000000), adult(38, 0)])
cmp("C28", "iDeCo 276,000 for the non-earning spouse", h, var(h, {"adults.1.ideco": 276000}), outlay=276000)
cmp("C28b", "the same 276,000 as the earner's iDeCo", h, var(h, {"adults.0.ideco": 276000}), outlay=276000)
# C29 Declare listed gains to use leftover deductions (R5): retiree pension 1,000,000, gains 2,000,000
h = hh([adult(70, 0, 0, 1000000)], married=False, capitalGains=2000000)
cmp("C29", "retiree: declare 2,000,000 listed gains to absorb unused deductions", h, var(h, {"jpGains": "declared"}))

print(json.dumps(rows, ensure_ascii=False, indent=0))
