S = {'cc': 'JP', 'doc': '# Japan 2025: corporation tax, local corporation tax, withholding on non-residents (1200)\n\nSources: e-Gov API v2, asof 2025-07-01 (`jp/law/egov/hojinzei_2025-07-01.*`, `chihohojinzei_…`, `shotokuzei_…`, `fukko_…`).\n* **法人税法 art. 66 (1)**: ordinary corporations "百分の二十三・二の税率"; **(2)**: capital ≤ 1億円, the first 8 m yen of\n  income "百分の十九"; **租特 art. 42-3-2**: that 19 % read as 15 % for years beginning by 2027-03-31 (flag `sme`).\n* **地方法人税法 art. 10 (1)**: "課税標準法人税額に百分の十・三の税率" (10.3 % of the corporation tax).\n* **所得税法 arts. 212 (1), 213 (1) 1**: 20 % on domestic-source income paid to non-residents and foreign corporations;\n  **復興財源確保法 art. 28**: special reconstruction income tax 2.1 % of that tax (to 2037): 20.42 %.', 'regimeName': '法人税 (corporation tax)', 'unsupported': [['company', 'enterprise tax (事業税, size-based above 1億 capital), 特別法人事業税 and corporate inhabitants tax (地方税法) not modelled'], ['abroad', '15.315 % on deposit/bond interest (所得税法 213 (1) 3) and listed dividends (租特 9-3) not modelled; treaty rates not applied']], 'taxes': [{'oecd': '1200/1100', 'tax': 'Withholding tax on payments to non-residents', 'statute': '所得税法 arts. 161, 212, 213 (1) 1; 復興財源確保法 art. 28', 'dated': 'asof 2025-07-01', 'grade': 'A', 'kernel_parts': ['Wht'], 'unsupported': []}, {'oecd': '1200', 'tax': '法人税 (corporation tax)', 'statute': '法人税法 (昭和40年法律第34号) art. 66 (1)-(2) (e-Gov revision 20250620, asof 2025-07-01); 租税特別措置法 art. 42-3-2 (15 % on the first 8 m yen, years beginning by 2027-03-31)', 'dated': 'asof 2025-07-01', 'grade': 'A', 'kernel_parts': ['CorpRegime'], 'unsupported': ['enterprise tax, special corporate enterprise tax, corporate inhabitants tax', 'group (通算) taxation']}, {'oecd': '1200', 'tax': '地方法人税 (local corporation tax)', 'statute': '地方法人税法 art. 10 (1) (10.3 %)', 'dated': 'asof 2025-07-01', 'grade': 'A', 'kernel_parts': ['charge'], 'unsupported': []}], 'wht': [{'kind': 'dividend', 'rate': 2042, 'statute': '所得税法 213 (1) 1 (20 %) + 復興財源確保法 28 (2.1 % of it)'}, {'kind': 'royalty', 'rate': 2042, 'statute': '所得税法 161 (1) 11, 213 (1) 1 + 復興 28'}, {'kind': 'services', 'rate': 2042, 'statute': '所得税法 161 (1) 6, 213 (1) 1 + 復興 28'}], 'whtName': 'Withholding tax on payments to non-residents', 'guards': ['citSme.citTax { profit := 10000000, flags := ["sme"] } == 1664000', 'cit.citTax { profit := 1000000 } == 232000', '(localCorp { profit := 1000000 }).due == 23896'], 'extra_lean': 'def cit : CorpRegime := { name := "法人税 (corporation tax)", sched := Schedule.flat 2320 }\ndef citSme : CorpRegime := { name := "法人税 (中小法人)", sched := Schedule.ofList [(0, 1500), (8000000, 2320)] }\ndef citOf (co : Company) : CorpRegime := if co.flags.contains "sme" then citSme else cit\ndef citStatute : String := "法人税法 (昭和40年法律第34号) art. 66 (1)-(2) (e-Gov revision 20250620, asof 2025-07-01); 租税特別措置法 art. 42-3-2 (15 % on the first 8 m yen, years beginning by 2027-03-31)"\n/-- 地方法人税法 art. 10 (1): 10.3 % of the corporation tax. -/\ndef localCorp (co : Company) : Charge :=\n  let n := (citOf co).citTax co\n  charge .cit "地方法人税 (local corporation tax)" n id (fun x => divR .down (1030 * x) BP) (statute := "地方法人税法 art. 10 (1) (asof 2025-07-01)")', 'extra_run': ['[(citOf g.company).citCharge g.company citStatute, localCorp g.company]']}


# ---- FT review (2026-11-21, third pass): 国税通則法 art. 118 (1), 119 (1) truncation (jp_ft_cit_opentax_v2_grid dev; IMPROVE_FT "JP opentax v2") ----
S["doc"] += r'''
## FT review (2026-11-21, third pass): truncation of the base and of the tax
e-Gov API v2, 国税通則法 (昭和37年法律第66号) asof 2025-07-01 (`jp/law/egov/tsusokuho_2025-07-01.*`):
* **art. 118 (1)**: "国税（印紙税及び附帯税を除く。…）の課税標準 … を計算する場合において、その額に千円未満の端数があるとき、
  又はその全額が千円未満であるときは、その端数金額又はその全額を切り捨てる" (the base to 1,000 yen);
* **art. 119 (1)**: "国税（自動車重量税、印紙税及び附帯税を除く。…）の確定金額に百円未満の端数があるとき、又はその全額が百円未満
  であるときは、その端数金額又はその全額を切り捨てる" (the tax to 100 yen).
法人税 (base: 所得の金額) and 地方法人税 (base: 課税標準法人税額, art. 9 of its act) are both 国税 under these articles.
The withholding charges keep 1-yen amounts (art. 119 (2) with 施行令 art. 40: not changed here).
'''
S["extra_lean"] = S["extra_lean"].replace(
    '/-- 地方法人税法 art. 10 (1): 10.3 % of the corporation tax. -/\ndef localCorp (co : Company) : Charge :=\n  let n := (citOf co).citTax co\n  charge .cit "地方法人税 (local corporation tax)" n id (fun x => divR .down (1030 * x) BP) (statute := "地方法人税法 art. 10 (1) (asof 2025-07-01)")',
    r'''/-- 国税通則法 art. 118 (1): a national tax's base is truncated to 1,000 yen; art. 119 (1): the tax to 100 yen. -/
def base1000 (x : Int) : Int := (Rule.downTo 1000).apply x
def citTaxJ (co : Company) : Int := (citOf co).sched.tax (Rule.downTo 100) (base1000 ((citOf co).taxableProfit co))
def citChargeJ (co : Company) : Charge :=
  charge .cit (citOf co).name ((citOf co).beforeLosses co) (fun _ => base1000 ((citOf co).taxableProfit co)) (fun _ => citTaxJ co)
    (statute := citStatute ++ "; 国税通則法 art. 118 (1) (base: 1,000 円未満切捨て), 119 (1) (tax: 100 円未満切捨て)")
/-- 地方法人税法 art. 10 (1): 10.3 % of the corporation tax (base and tax truncated, 国税通則法 118 (1), 119 (1)). -/
def localCorp (co : Company) : Charge :=
  let n := citTaxJ co
  charge .cit "地方法人税 (local corporation tax)" n base1000 (fun x => (Rule.downTo 100).apply (divR .down (1030 * x) BP)) (statute := "地方法人税法 art. 10 (1) (asof 2025-07-01); 国税通則法 art. 118 (1), 119 (1)")''')
assert "citChargeJ" in S["extra_lean"]
S["extra_run"] = [r.replace("(citOf g.company).citCharge g.company citStatute", "citChargeJ g.company") for r in S["extra_run"]]
assert "citChargeJ" in S["extra_run"][0]
S["guards"] = [g for g in S["guards"] if "localCorp" not in g] + [
    "(localCorp { profit := 1000000 }).due == 23800",
    "citTaxJ { profit := 1000999 } == 232000",
    "-- 1,003,999 yen: base 1,003,000 x 23.2 % = 232,696 -> 232,600; local: 232,000 x 10.3 % = 23,896 -> 23,800",
    "citTaxJ { profit := 1003999 } == 232600",
    "(localCorp { profit := 1003999 }).due == 23800"]

# --- R3 session 5 (2026-11-21): withholding under kernel 2.3.0 ---
def _s5_wht_entry(**kw):
    for t in S['taxes']:
        if t['oecd'] == '1200/1100':
            t.update(kw); return
    S['taxes'].append(dict({'oecd': '1200/1100', 'kernel_parts': ['Wht'], 'unsupported': []}, **kw))

S['wht'] = S['wht'] + [dict(kind='interest', rate=2042, statute='所得税法 161 (1) 10 (loan interest), 213 (1) 1 (20 %) + 復興財源確保法 28 (2.1 % of it)')]
S['unsupported'] = [u for u in S['unsupported'] if u[0] != 'abroad'] + [['abroad', '15.315 % on bond and deposit interest (所得税法 161 (1) 8, 213 (1) 3) and listed dividends (租特 9-3) not distinguished: interest is taken as loan interest (161 (1) 10, 20.42 %); treaty rates not applied']]
S['guards'] = S['guards'] + ['wht.amount { kind := .interest, amount := 10000 } == 2042']
