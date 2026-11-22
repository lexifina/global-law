S = {'cc': 'CN', 'doc': '# China 2025: enterprise income tax and withholding on non-resident enterprises (1200)\n\nSources: flk.npc.gov.cn official docx (`cn/law/flk/cit_law_2018.*`, `cit_regs_2024.*`).\n* **企业所得税法 (2018-12-29) art. 4**: "企业所得税的税率为25％"; non-resident enterprises\' art. 3 (3) income 20 %.\n* **art. 28**: small low-profit enterprises 20 % (flag `smallLowProfit`), high and new technology enterprises 15 % (`hnte`).\n  The effective 5 % for small low-profit enterprises (财政部 税务总局公告2023年第12号, to 2027) is not reached here.\n* **art. 26 (2)**: dividends between resident enterprises exempt (participation, any stake).\n* **实施条例 (2024-12-06 version, in force 2025-01-20) art. 91**: art. 27 (5) income of non-resident enterprises "减按10%的税率".', 'regimeName': '企业所得税 (enterprise income tax)', 'unsupported': [['company', 'small low-profit enterprise effective 5 % (公告2023年第12号) and the art. 30 super deductions not modelled']], 'taxes': [{'oecd': '1200', 'tax': '企业所得税 (enterprise income tax)', 'statute': '企业所得税法 (2018) art. 4, art. 28', 'dated': '2018-12-29 law; 2025-01-20 regulations', 'grade': 'A', 'kernel_parts': ['CorpRegime'], 'unsupported': ['公告2023年第12号 effective 5 % for small low-profit enterprises (not reached)']}, {'oecd': '1200/1100', 'tax': 'Withholding tax on payments to non-residents', 'statute': '企业所得税法 arts. 3-4, 27 (5); 实施条例 art. 91', 'dated': '2018-12-29 law; 2025-01-20 regulations', 'grade': 'A', 'kernel_parts': ['Wht'], 'unsupported': []}], 'sched': [(0, 2500)], 'citStatute': '企业所得税法 (2018) art. 4, art. 28', 'wht': [{'kind': 'dividend', 'rate': 1000, 'statute': '企业所得税法 3 (3), 27 (5); 实施条例 91', 'toCompany': True}, {'kind': 'interest', 'rate': 1000, 'statute': '实施条例 91', 'toCompany': True}, {'kind': 'royalty', 'rate': 1000, 'statute': '实施条例 91', 'toCompany': True}], 'whtName': 'Withholding tax on payments to non-residents', 'guards': ['(cit { profit := 1000000 }).citTax { profit := 1000000 } == 250000', '(cit { profit := 1000000, flags := ["hnte"] }).citTax { profit := 1000000, flags := ["hnte"] } == 150000', 'wht.amount { kind := .dividend, amount := 1000, toCompany := true } == 100', 'wht.amount { kind := .interest, amount := 1000, toCompany := true } == 100', 'wht.amount { kind := .royalty, amount := 1000, toCompany := true } == 100'], 'rateByFlag': [('hnte', 1500), ('smallLowProfit', 2000)], 'participationBp': 10000}

# ---- FT review (2026-11-21): 财政部 税务总局公告2023年第12号 (small low-profit enterprises, 5 % effective) ----
S["doc"] = S["doc"].replace("small low-profit enterprises 20 % (flag `smallLowProfit`)", "small low-profit enterprises 20 %").replace(
  "\n  The effective 5 % for small low-profit enterprises (财政部 税务总局公告2023年第12号, to 2027) is not reached here.", "") + '''

FT review (2026-11-21): **财政部 税务总局公告2023年第12号** (2023-08-02; gov.cn 国务院部门文件,
`cn/law/mof/mof_sat_2023_12.html`, sha256 in `SOURCES.tsv`):
* **三**: "对小型微利企业减按25%计算应纳税所得额，按20%的税率缴纳企业所得税政策，延续执行至2027年12月31日" (2025: 5 % of
  the taxable income).
* **五**: "小型微利企业，是指从事国家非限制和禁止行业，且同时符合年度应纳税所得额不超过300万元、从业人数不超过300人、资产总额
  不超过5000万元等三个条件的企业" (replacing, for the notice, 实施条例 art. 92's 30万元 / 100 or 80 / 3000 or 1000万元).
The test is applied to the entity's own taxable profit, employees and assets (the quarterly averages taken as the
entity's values); flag `restrictedIndustry` excludes it, flag `smallLowProfit` forces it. A company that is both a high
and new technology enterprise (15 %) and a small low-profit enterprise pays the lower.'''
S["rateOfLean"] = '''/-- The regime before the rate (taxable profit only; same fields as `cit`). -/
def base : CorpRegime := { name := "企业所得税 (enterprise income tax)", sched := Schedule.flat 2500, participationBp := 10000 }
/-- 公告2023年第12号 五: 年度应纳税所得额 ≤ 300万元, 从业人数 ≤ 300人, 资产总额 ≤ 5000万元, non-restricted industry. -/
def smallLowProfit (co : Company) : Bool :=
  co.flags.contains "smallLowProfit" ||
  (!co.flags.contains "restrictedIndustry" && decide (base.taxableProfit co ≤ 3000000) && decide (co.employees ≤ 300)
    && decide (co.assets ≤ 50000000))
/-- art. 4 25 %; art. 28 (2) high and new technology enterprise 15 %; 公告2023年第12号 三: 25 % of the income at 20 % = 5 %. -/
def rateOf (co : Company) : Int := if smallLowProfit co then 500 else if co.flags.contains "hnte" then 1500 else 2500'''
S["citStatute"] = "企业所得税法 (2018) art. 4, art. 28; 财政部 税务总局公告2023年第12号 三, 五 (small low-profit enterprises, to 2027-12-31)"
S["unsupported"] = [u for u in S["unsupported"] if "公告2023年第12号" not in u[1]] + [["company", "the art. 30 super deductions not modelled; small low-profit test on the entity's own year-end employees and assets (not the quarterly averages of 公告2023年第12号 五), industry taken as non-restricted unless flagged `restrictedIndustry`"]]
S["guards"] = [("(cit { profit := 1000000, employees := 301 }).citTax { profit := 1000000, employees := 301 } == 250000"
                if g == "(cit { profit := 1000000 }).citTax { profit := 1000000 } == 250000" else
                ("(cit { profit := 1000000, employees := 301, flags := [\"hnte\"] }).citTax { profit := 1000000, employees := 301, flags := [\"hnte\"] } == 150000"
                 if g.startswith("(cit { profit := 1000000, flags := [\"hnte\"] })") else g)) for g in S["guards"]] + [
  "-- 公告2023年第12号 三, 五: 5 % up to 3,000,000 of taxable income, 300 employees, 50,000,000 of assets",
  "(cit { profit := 3000000, employees := 300, assets := 50000000 }).citTax { profit := 3000000, employees := 300, assets := 50000000 } == 150000",
  "(cit { profit := 3000001, employees := 300, assets := 50000000 }).citTax { profit := 3000001, employees := 300, assets := 50000000 } == 750000",
  "(cit { profit := 1000000, employees := 300, assets := 50000001 }).citTax { profit := 1000000, employees := 300, assets := 50000001 } == 250000",
  "(cit { profit := 1000000, flags := [\"restrictedIndustry\"] }).citTax { profit := 1000000 } == 250000"]
for _t in S["taxes"]:
    if _t["oecd"] == "1200":
        _t["statute"] = "企业所得税法 (2018) art. 4, art. 28; 财政部 税务总局公告2023年第12号 三, 五"
        _t["dated"] = "2018-12-29 law; 2025-01-20 regulations; 公告2023年第12号 (2023-08-02, to 2027-12-31)"
        _t["unsupported"] = [u for u in _t.get("unsupported", []) if "公告2023年第12号" not in u] + ["small low-profit test on year-end values, not quarterly averages"]

# --- R3 session 5 (2026-11-21): withholding under kernel 2.3.0 ---
def _s5_wht_entry(**kw):
    for t in S['taxes']:
        if t['oecd'] == '1200/1100':
            t.update(kw); return
    S['taxes'].append(dict({'oecd': '1200/1100', 'kernel_parts': ['Wht'], 'unsupported': []}, **kw))

S['wht'] = [dict(kind='dividend', toCompany=False, rate=2000, statute='个人所得税法 art. 3 (3) (20 %); 实施条例 art. 3 (5) (China-source)'),
            dict(kind='interest', toCompany=False, rate=2000, statute='个人所得税法 art. 3 (3) (20 %); 实施条例 art. 3 (5)'),
            dict(kind='services', toCompany=False, rate=0, statute='个人所得税法实施条例 art. 3 (1): services performed outside China are not China-source'),
            dict(kind='services', rate=0, statute='企业所得税法实施条例 art. 7 (2): services income is sourced where the services are performed; 企业所得税法 art. 3: a non-resident enterprise is taxed on China-source income only')] + S['wht']
_s5_wht_entry(statute='企业所得税法 arts. 3-4, 27 (5); 实施条例 arts. 7, 91; 个人所得税法 art. 3 (2018); 个人所得税法实施条例 art. 3 (2018)',
    unsupported=['dividends from foreign-invested enterprises to foreign individuals (财税字〔1994〕020号) not distinguished',
                 'royalties to non-resident individuals: the monthly comprehensive-income table on 80 % (个人所得税法 art. 6) not expressible as a flat rule (grade C line)',
                 'services performed in China by a non-resident enterprise (deemed-profit EIT) not modelled'])
S['guards'] = S['guards'] + ['wht.amount { kind := .dividend, amount := 1000, toCompany := false } == 200', 'wht.amount { kind := .services, amount := 1000 } == 0']

# --- R3 session 7 (2026-11-21): withholding pass 7 ---
def _s7_wht_entry(add_unsupported=(), drop_unsupported=(), **kw):
    for t in S['taxes']:
        if t['oecd'] == '1200/1100':
            t.update(kw)
            t['unsupported'] = [u for u in t.get('unsupported', []) if not any(d in u for d in drop_unsupported)] + list(add_unsupported)
            return
    S['taxes'].append(dict({'oecd': '1200/1100', 'kernel_parts': ['Wht'], 'unsupported': list(add_unsupported)}, **kw))

S['extra_lean'] = (S.get('extra_lean') or '') + """
/-- Non-resident individuals' royalties (个人所得税法 2018 art. 2 (1) 4, art. 6 (1) 2: 每次收入额; art. 6 para. 2: 收入额 =
收入 less 20 %; 附表一 注2: the 综合所得 table of art. 3 converted to a month: 3 000 / 12 000 / 25 000 / 35 000 / 55 000 /
80 000 yuan; art. 11 para. 3: withheld by the payer, no annual settlement). -/
def nrMonthly : Schedule := Schedule.ofList [(0, 300), (3000, 1000), (12000, 2000), (25000, 2500), (35000, 3000), (55000, 3500), (80000, 4500)]

def royaltyIndTax (amt : Int) : Int := nrMonthly.tax {} (pos amt * 8 / 10)

def royaltyIndCharges (co : Company) : List Charge :=
  co.paymentsAbroad.zipIdx.filterMap fun (p, i) =>
    if p.kind == .royalty && !p.toCompany then
      some (charge .pit "个人所得税 (非居民个人 特许权使用费所得)" p.amount (fun a => pos a * 8 / 10) (fun b => nrMonthly.tax {} b)
        (event := s!"payment {i + 1} ({p.kind.name})") (bearer := .withheld)
        (statute := "个人所得税法 (2018) art. 3, art. 6 (1) 2 and para. 2 (收入额 80 %), art. 11 para. 3; 附表一 注2 (按月换算)"))
    else none
"""
S['extra_run'] = (S.get('extra_run') or []) + ['royaltyIndCharges g.company']
_s7_wht_entry(drop_unsupported=['royalties to non-resident individuals'],
    add_unsupported=['royalties to non-resident individuals: each payment record is taken as one payment (每次); the year\'s payments to one person are not split'])
S['guards'] = S['guards'] + ['royaltyIndTax 10000 == 590', 'royaltyIndTax 0 == 0', 'royaltyIndTax 200000 == 56840']
