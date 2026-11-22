S = {'cc': 'BD', 'doc': '# Bangladesh 2025-26: income tax on companies (1200)\n\nIncome Tax Act 2023 (consolidated 2025-07-08, `cmp20/world/B11-south-asia/bd/law/ita2023_consol_20250708.txt`) and the\nFinance Ordinance 2025: the Second Schedule rates were not re-located in the text in this pass (B).\n* Non-listed companies 27.5 % (if receipts and payments go through banks; else 30 %); listed 20 %; banks 37.5 %.\n* Minimum tax (s. 163) and withholding on non-residents (s. 120 and the withholding rules): not reached (C).', 'regimeName': 'Income tax on companies', 'unsupported': [['company', 'minimum tax on gross receipts (s. 163) and the 30 % rate for companies not meeting the banking-transaction condition not modelled']], 'taxes': [{'oecd': '1200', 'tax': 'Income tax on companies', 'statute': 'ITA 2023 Second Schedule (Finance Ordinance 2025)', 'dated': 'income year 2025-26', 'grade': 'B', 'kernel_parts': ['CorpRegime'], 'unsupported': []}, {'oecd': '1200/1100', 'tax': 'Withholding tax on payments to non-residents', 'statute': 'ITA 2023 s. 120; Income Tax (Withholding) Rules', 'dated': 'not reached', 'grade': 'C', 'kernel_parts': [], 'unsupported': ['rules not reached']}], 'sched': [(0, 2750)], 'citStatute': 'ITA 2023 Second Schedule (Finance Ordinance 2025)', 'guards': ['(cit { profit := 1000000 }).citTax { profit := 1000000 } == 275000'], 'rateByFlag': [('bank', 3750), ('listed', 2000)]}

# --- R3 session 5 (2026-11-21): withholding under kernel 2.3.0 ---
def _s5_wht_entry(**kw):
    for t in S['taxes']:
        if t['oecd'] == '1200/1100':
            t.update(kw); return
    S['taxes'].append(dict({'oecd': '1200/1100', 'kernel_parts': ['Wht'], 'unsupported': []}, **kw))

S['wht'] = [dict(kind='dividend', toCompany=True, rate=2000, statute='ITA 2023 s. 119 (1); উৎসে কর কর্তন বিধিমালা, ২০২৪ (SRO 161) rule 5 (1) Table item 20 (1): dividend to a company, fund or trust 20 %'),
            dict(kind='dividend', toCompany=False, rate=3000, statute='ITA 2023 s. 119 (1); Withholding Rules 2024 (SRO 161) rule 5 (1) Table item 20 (2): dividend to other persons 30 %'),
            dict(kind='interest', rate=2000, statute='ITA 2023 s. 119 (1); Withholding Rules 2024 (SRO 161) rule 5 (1) Table item 11 (20 %)'),
            dict(kind='royalty', rate=2000, statute='ITA 2023 s. 119 (1); Withholding Rules 2024 (SRO 161) rule 5 (1) Table item 10: royalty, licence fee, intangibles (20 %)'),
            dict(kind='services', rate=2000, statute='ITA 2023 s. 119 (1); Withholding Rules 2024 (SRO 161) rule 5 (1) Table items 1, 3, 8: advisory, professional and technical services, management services (20 %)')]
S['whtName'] = 'Tax deducted from payments to non-residents (ITA 2023 s. 119)'
_s5_wht_entry(tax='Tax deducted from payments to non-residents (20 %; dividends to non-company persons 30 %)',
    statute='Income Tax Act 2023 s. 119 (bdlaws, Wayback 20250418124050: "prescribed rate, not exceeding 30 %"); উৎসে কর কর্তন বিধিমালা, ২০২৪ (SRO 161-Ain/Aikor/2024, Bangladesh Gazette Extraordinary 29 May 2024) rule 5 (1) Table',
    dated='income year 2025-26 (rules of 2024; 2025 amendments of the Table not checked; Finance Ordinance 2025 moved the s. 119 (6) exclusions into rule 5)', grade='A', kernel_parts=['Wht'],
    unsupported=['contractors 7.5 %, advertising 15 %, insurance 10 % and the other Table items not distinguished from the 20 % services rate', 'rule 5 (3) excluded payments (tuition, liaison office costs) not modelled'])
S['guards'] = S['guards'] + ['wht.amount { kind := .dividend, amount := 1000, toCompany := false } == 300', 'wht.amount { kind := .interest, amount := 1000 } == 200']

# --- R3 session 12 (2026-11-21): year in force: calendar 2025 = income year 2024-25 (1 Jan - 30 Jun) + income year 2025-26 (1 Jul - 31 Dec) ---
S['doc'] = """# Bangladesh 2025: income tax on companies (1200) and tax deducted from payments to non-residents

**Session 12 (year in force), grade A.** Under the Income Tax Act 2023 a Finance Act fixes the rates for a tax year
(করবর্ষ) beginning on 1 July, which assesses the income year that ended the day before. Calendar 2025 straddles:
* **income year 2024-25** (1 Jan - 30 Jun 2025) = tax year beginning 1 July 2025: **Finance Act 2024** (Act No. 5 of 2024,
  Bangladesh Gazette Extraordinary 30 June 2024; bdlaws upload, Internet Archive 2025-08-13, `bd/law/bd_act5_2024_wb20250813.pdf`,
  Bengali OCR `tools/p12/ocr/bd5_all.ocr.txt`, the rate pages checked on the page image) s. 88 and তফসিল-৩ প্রথম অংশ
  অনুচ্ছেদ-খ: (1) (ক) (অ) publicly traded company with more than 10 % of paid-up capital floated by IPO 22.5 % (20 % if all
  receipts and every payment above Tk 5 lakh, Tk 36 lakh a year, go through bank transfer); (আ) other publicly traded 25 %
  (22.5 %); (ই) one-person company 22.5 % (20 %); (ঈ) other companies 27.5 % (25 % on the same bank-transfer condition);
  (খ) banks, insurers and finance companies: publicly traded 37.5 %, others 40 %; (গ) merchant banks 37.5 %; (ঘ) tobacco 45 %;
  (ঙ) mobile operators 45 % (40 % if publicly traded).
* **income year 2025-26** (1 Jul - 31 Dec 2025) = tax year beginning 1 July 2026: **Finance Ordinance 2025** (Ordinance
  No. 28 of 2025, Gazette Extraordinary 2 June 2025; `cmp20/world/B11-south-asia/bd/law/ord28_2025.pdf`, page 103 read on
  the image) s. 136 and তফসিল-২ অনুচ্ছেদ-খ: (1) (ক) (অ) publicly traded (> 10 % by IPO) 22.5 % (20 % if all receipts go
  through bank transfer); (আ) all other companies 27.5 % (no proviso); (খ) banks etc. publicly traded 37.5 %, others 40 %;
  (গ) tobacco 45 %; (ঘ) mobile operators 45 % (40 %). The Ordinance does not amend the Finance Act 2024 schedule.
The year's tax is the two income years' rates applied by days: 181/365 at the 2024-25 rate, 184/365 at the 2025-26 rate
(a company with another income year is not modelled). Company flags: `"listed"` = publicly traded with more than 10 % by
IPO; `"bank"` = bank, insurer or finance company (publicly traded if also `"listed"`); `"cashless"` = the bank-transfer
proviso is met. Before session 12 the model charged listed 20 % and banks 37.5 % unconditionally (the proviso and the
publicly traded case); the default 27.5 % is unchanged unless `"cashless"`.
Not modelled: minimum tax on gross receipts (s. 163), publicly traded companies with 10 % or less by IPO, one-person
companies, merchant banks, tobacco and mobile operators (sector rates), surcharge.

Tax deducted from payments to non-residents: Income Tax Act 2023 s. 119 and উৎসে কর কর্তন বিধিমালা, ২০২৪ (SRO 161, 29 May
2024) rule 5 (1) Table (see the entry)."""
_rates = '''/-- Income year 2025-26 (Finance Ordinance 2025 তফসিল-২ অনুচ্ছেদ-খ), basis points. -/
def rateOf (co : Company) : Int :=
  if co.flags.contains "bank" then (if co.flags.contains "listed" then 3750 else 4000)
  else if co.flags.contains "listed" then (if co.flags.contains "cashless" then 2000 else 2250)
  else 2750
/-- Income year 2024-25 (Finance Act 2024 তফসিল-৩ অনুচ্ছেদ-খ), basis points. -/
def rate24 (co : Company) : Int :=
  if co.flags.contains "bank" then (if co.flags.contains "listed" then 3750 else 4000)
  else if co.flags.contains "listed" then (if co.flags.contains "cashless" then 2000 else 2250)
  else (if co.flags.contains "cashless" then 2500 else 2750)'''
S['citStatute'] = "ITA 2023; Finance Act 2024 s. 88, তফসিল-৩ (income year 2024-25) and Finance Ordinance 2025 s. 136, তফসিল-২ (income year 2025-26), by days"
S['extra_lean'] = (S.get('extra_lean') or '') + '\n\n' + _rates + '''

def cit (co : Company) : CorpRegime :=
  { name := "Income tax on companies",
    sched := Schedule.flat (rateOf co) }

def citStatute : String := "''' + S['citStatute'] + '''"

/-- Calendar 2025: 181 days of income year 2024-25 and 184 days of income year 2025-26. -/
def split25 (iy24 iy25 : Int) : Int := divR .halfUp (181 * iy24 + 184 * iy25) 365
/-- Income tax on companies for calendar 2025: each income year's rate on the taxable profit, by days. -/
def citSplit (co : Company) : Charge :=
  let ti := (cit co).taxableProfit co
  charge .cit "Income tax on companies: income year 2024-25 rate to 30 June, income year 2025-26 rate from 1 July 2025 (by days)" ti id
    (fun x => split25 (divR .halfUp (rate24 co * pos x) BP) (divR .halfUp (rateOf co * pos x) BP))
    (statute := citStatute)'''
S['sched'] = None
S['rateByFlag'] = None
S['extra_run'] = ["[citSplit g.company]"]
S['extra_covers'] = [".cit"]
S['unsupported'] = [["company", "calendar 2025 split by days between income year 2024-25 (181/365) and 2025-26 (184/365); minimum tax (s. 163), sector rates (tobacco, mobile operators, merchant banks), one-person companies and publicly traded companies with 10 % or less by IPO not modelled"]]
S['guards'] = [g for g in S['guards'] if not g.startswith('(cit ')] + [
    '(citSplit { profit := 1000000 }).due == 275000',
    '(citSplit { profit := 1000000, flags := ["cashless"] }).due == 262603',
    '(citSplit { profit := 1000000, flags := ["listed"] }).due == 225000',
    '(citSplit { profit := 1000000, flags := ["listed", "cashless"] }).due == 200000',
    '(citSplit { profit := 1000000, flags := ["bank"] }).due == 400000',
    '(citSplit { profit := 1000000, flags := ["bank", "listed"] }).due == 375000']
for _t in S['taxes']:
    if _t['oecd'] == '1200':
        _t['statute'] = "ITA 2023; Finance Act 2024 (Act No. 5 of 2024) s. 88, তফসিল-৩; Finance Ordinance 2025 (No. 28 of 2025) s. 136, তফসিল-২"
        _t['dated'] = ("2025, split at 1 July 2025 by days: income year 2024-25 (Finance Act 2024 schedule for the tax year from 1 July 2025, "
                       "gazette of 30 June 2024, Internet Archive 2025-08-13) and income year 2025-26 (Finance Ordinance 2025 schedule for the tax "
                       "year from 1 July 2026, gazette of 2 June 2025); session 12 year in force")
        _t['grade'] = 'A'
        _t['unsupported'] = ["split by days (181/365, 184/365); minimum tax s. 163; sector rates; one-person companies; publicly traded with 10 % or less by IPO"]
