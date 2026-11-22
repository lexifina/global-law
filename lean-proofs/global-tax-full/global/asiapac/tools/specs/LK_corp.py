S = {'cc': 'LK', 'doc': '# Sri Lanka 2025-26: income tax on companies and withholding on non-residents (1200)\n\nInland Revenue Act No. 24 of 2017 as amended by Act No. 45 of 2022 (B: First and Fifth Schedules as read by the registry;\nlean1 copies `sched1_20251001.txt`, `sched5_s52.txt` not re-read).\n* **First Schedule para. 2**: companies 30 % (from 2022-10-01).\n* **s. 84-85, Fifth Schedule**: dividends 15 %, interest and royalties to non-residents 15 %.', 'regimeName': 'Income tax on companies', 'unsupported': [['company', 'concessionary sector rates (15 %, 0 %) not modelled']], 'taxes': [{'oecd': '1200', 'tax': 'Income tax on companies', 'statute': 'IRA 2017 First Schedule (Act No. 45 of 2022)', 'dated': 'year of assessment 2025/26', 'grade': 'B', 'kernel_parts': ['CorpRegime'], 'unsupported': []}, {'oecd': '1200/1100', 'tax': 'Withholding tax on payments to non-residents', 'statute': 'IRA 2017 ss. 84-85, Fifth Schedule', 'dated': 'year of assessment 2025/26', 'grade': 'B', 'kernel_parts': ['Wht'], 'unsupported': []}], 'sched': [(0, 3000)], 'citStatute': 'IRA 2017 First Schedule (Act No. 45 of 2022)', 'wht': [{'kind': 'dividend', 'rate': 1500, 'statute': 'IRA 2017 s. 84, Fifth Schedule'}, {'kind': 'interest', 'rate': 1500, 'statute': 's. 85, Fifth Schedule'}, {'kind': 'royalty', 'rate': 1500, 'statute': 's. 85, Fifth Schedule'}], 'whtName': 'Withholding tax on payments to non-residents', 'guards': ['cit.citTax { profit := 1000000 } == 300000', 'wht.amount { kind := .dividend, amount := 1000 } == 150', 'wht.amount { kind := .interest, amount := 1000 } == 150', 'wht.amount { kind := .royalty, amount := 1000 } == 150']}

# ---- FT review (2026-11-21): First Schedule para. 10 withholding rates (the model cited the Fifth Schedule, which holds reliefs) ----
S["doc"] = S["doc"].replace("* **s. 84-85, Fifth Schedule**: dividends 15 %, interest and royalties to non-residents 15 %.", "") + '''

FT review (2026-11-21). The withholding rates are in the **First Schedule para. 10**, not the Fifth Schedule (which
lists qualifying payments and reliefs). Read: the Act as enacted (parliament.lk `6054.pdf`, `lk/law/ira2017_6054.pdf`)
and the amending sections (copies in `cmp20/world/B11-south-asia/lk/law/act45_2022_sel.txt`, `act2_2025.txt`):
* **s. 84 (1) (a) (i)**: withholding "at the rate provided for in paragraph 10 of the First Schedule" where a person
  "pays a dividend, interest, discount, charge, natural resource payment, rent, royalty ..."; **s. 85 (1) (b)**: where a
  person "pays a service fee or an insurance premium with a source in Sri Lanka to a non-resident person".
* **para. 10 (1) (c) (ii)**: "service fees referred to in section 85(1)(b) - 14%".
* **para. 10 (1) (d)** (added by Act No. 45 of 2022 s. 33 (6) (c), for payments to which s. 84A (1A) applies):
  "(iv) all other payments except dividend - 14%; and (v) dividend paid-15%"; **(d) (ii)** as replaced by Act No. 2 of
  2025 s. 3 (3): "interest or discount paid ... (b) with effect from April 1, 2025 - 10%".
Grade B: s. 84A (1A) (its scope) and Act No. 10 of 2021 were not read; para. 10 (1) (b) (s. 84 (1) (a): interest 5 %,
other 14 %) would give 5 % on interest. Dividends 15 % and royalties 14 % under (d).'''
S["wht"] = [{"kind": "dividend", "rate": 1500, "statute": "IRA 2017 First Schedule para. 10 (1) (d) (v) (Act No. 45 of 2022)"},
            {"kind": "interest", "rate": 1000, "statute": "First Schedule para. 10 (1) (d) (ii) (b) (Act No. 2 of 2025: 10 % from 2025-04-01)"},
            {"kind": "royalty", "rate": 1400, "statute": "First Schedule para. 10 (1) (d) (iv) (14 %)"},
            {"kind": "services", "rate": 1400, "statute": "s. 85 (1) (b); First Schedule para. 10 (1) (c) (ii) (14 %)"}]
S["guards"] = [g for g in S["guards"] if not g.startswith("wht.amount")] + [
  "-- First Schedule para. 10 (1) (d) (v), (d) (ii) (b), (d) (iv), (c) (ii)",
  "wht.amount { kind := .dividend, amount := 1000 } == 150",
  "wht.amount { kind := .interest, amount := 1000 } == 100",
  "wht.amount { kind := .royalty, amount := 1000 } == 140",
  "wht.amount { kind := .services, amount := 1000 } == 140"]
S["unsupported"] = S["unsupported"] + [["abroad", "withholding rates: s. 84A (1A) scope not read (para. 10 (1) (b) would give 5 % on interest); treaty rates not modelled"]]
for _t in S["taxes"]:
    if _t["oecd"] == "1200/1100":
        _t.update({"statute": "IRA 2017 ss. 84 (1) (a) (i), 85 (1) (b); First Schedule para. 10 (1) (c) (ii), (d) (ii), (iv), (v)",
                   "dated": "Act No. 24 of 2017 as enacted; Act No. 45 of 2022 s. 33 (6); Act No. 2 of 2025 s. 3 (3) (from 2025-04-01)", "grade": "B",
                   "unsupported": ["s. 84A (1A) scope not read"]})

# --- R3 session 12 (2026-11-21): year in force: Y/A 2024/25 (to 31 Mar 2025) against 2025/26: First Schedule para. 4 read ---
S['doc'] = S['doc'].replace("* **First Schedule para. 2**: companies 30 % (from 2022-10-01).",
    "* **First Schedule para. 4 (1) (d)**: companies 30 % \"with effect from April 1, 2023\" (para. 2 is partnerships).") + """

**Session 12 (year in force), 1200 grade A.** IRD consolidated text of the Inland Revenue Act "incorporating amendments up to
31st March 2025" (dated 30 June 2025; Acts No. 10 of 2021, 45 of 2022, 4 of 2023, 14 of 2023, 2 of 2025, each with its
effective date; ird.gov.lk, Internet Archive 2026-03-08, `lk/law/lk_ira_cons2025_ird_wb20260308.pdf`) and Act No. 2 of 2025
(`lk/law/lk_ira_act02_2025_ird_wb20250709.pdf`): First Schedule para. 4 (1) "(d) with effect from April 1, 2023 shall be
taxed at the rate of 30%" (Act No. 45 of 2022 s. 33 (3)); Act No. 2 of 2025 s. 3 (2) only adds (2C) from 1 April 2025
(foreign-currency service and foreign-source gains 15 %; betting, gaming, liquor and tobacco 45 %) and closes (2B) (40 %)
at 31 March 2025. The general 30 % is the same in Y/A 2024/25 (1 Jan - 31 Mar 2025) and 2025/26: no split. The sector
rates (para. 4 (2A)-(2C)) are not modelled (flagged)."""
S['citStatute'] = "IRA 2017 First Schedule para. 4 (1) (d) (30 % from 1 April 2023; Act No. 45 of 2022 s. 33 (3))"
S['unsupported'] = [u if u[0] != 'company' else ['company', 'concessionary and sector rates (First Schedule para. 4 (2A) 14 %, (2B) 40 % to 31 March 2025, (2C) 15 % / 45 % from 1 April 2025) and gains on investment assets (para. 4 (4): 30 %) not modelled'] for u in S['unsupported']]
for _t in S['taxes']:
    if _t['oecd'] == '1200':
        _t['statute'] = "IRA 2017 First Schedule para. 4 (1) (d) (Act No. 45 of 2022 s. 33 (3)); Act No. 2 of 2025 s. 3 (2)"
        _t['dated'] = ("2025: IRD consolidated text incorporating amendments up to 31 March 2025 (dated 30 June 2025, Internet Archive "
                       "2026-03-08): 30 % with effect from 1 April 2023, the same in Y/A 2024/25 and 2025/26 (no split); session 12 year in force")
        _t['grade'] = 'A'
        _t['unsupported'] = ["sector rates para. 4 (2A)-(2C) not modelled"]
