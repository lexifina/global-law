import BdGlobal.Pit

/-!
# Bangladesh 2025: income tax on companies (1200) and tax deducted from payments to non-residents

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
2024) rule 5 (1) Table (see the entry).
-/

namespace BdGlobal.Corporate
open TaxKernel TaxKernel.Global

def wht : Wht :=
  { name := "Tax deducted from payments to non-residents (ITA 2023 s. 119)", rules := [
      { kind := .dividend, toCompany := some true, rateBp := 2000, statute := "ITA 2023 s. 119 (1); উৎসে কর কর্তন বিধিমালা, ২০২৪ (SRO 161) rule 5 (1) Table item 20 (1): dividend to a company, fund or trust 20 %" },
      { kind := .dividend, toCompany := some false, rateBp := 3000, statute := "ITA 2023 s. 119 (1); Withholding Rules 2024 (SRO 161) rule 5 (1) Table item 20 (2): dividend to other persons 30 %" },
      { kind := .interest, rateBp := 2000, statute := "ITA 2023 s. 119 (1); Withholding Rules 2024 (SRO 161) rule 5 (1) Table item 11 (20 %)" },
      { kind := .royalty, rateBp := 2000, statute := "ITA 2023 s. 119 (1); Withholding Rules 2024 (SRO 161) rule 5 (1) Table item 10: royalty, licence fee, intangibles (20 %)" },
      { kind := .services, rateBp := 2000, statute := "ITA 2023 s. 119 (1); Withholding Rules 2024 (SRO 161) rule 5 (1) Table items 1, 3, 8: advisory, professional and technical services, management services (20 %)" }] }



/-- Income year 2025-26 (Finance Ordinance 2025 তফসিল-২ অনুচ্ছেদ-খ), basis points. -/
def rateOf (co : Company) : Int :=
  if co.flags.contains "bank" then (if co.flags.contains "listed" then 3750 else 4000)
  else if co.flags.contains "listed" then (if co.flags.contains "cashless" then 2000 else 2250)
  else 2750
/-- Income year 2024-25 (Finance Act 2024 তফসিল-৩ অনুচ্ছেদ-খ), basis points. -/
def rate24 (co : Company) : Int :=
  if co.flags.contains "bank" then (if co.flags.contains "listed" then 3750 else 4000)
  else if co.flags.contains "listed" then (if co.flags.contains "cashless" then 2000 else 2250)
  else (if co.flags.contains "cashless" then 2500 else 2750)

def cit (co : Company) : CorpRegime :=
  { name := "Income tax on companies",
    sched := Schedule.flat (rateOf co) }

def citStatute : String := "ITA 2023; Finance Act 2024 s. 88, তফসিল-৩ (income year 2024-25) and Finance Ordinance 2025 s. 136, তফসিল-২ (income year 2025-26), by days"

/-- Calendar 2025: 181 days of income year 2024-25 and 184 days of income year 2025-26. -/
def split25 (iy24 iy25 : Int) : Int := divR .halfUp (181 * iy24 + 184 * iy25) 365
/-- Income tax on companies for calendar 2025: each income year's rate on the taxable profit, by days. -/
def citSplit (co : Company) : Charge :=
  let ti := (cit co).taxableProfit co
  charge .cit "Income tax on companies: income year 2024-25 rate to 30 June, income year 2025-26 rate from 1 July 2025 (by days)" ti id
    (fun x => split25 (divR .halfUp (rate24 co * pos x) BP) (divR .halfUp (rateOf co * pos x) BP))
    (statute := citStatute)

def families : List Family :=
  [{ name := "1200 corporate income tax and withholding", covers := [.cit],
     run := fun _ g _ => if g.entity != .company then [] else
       wht.charges g.company
       ++ [citSplit g.company] }]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  (if true then ["calendar 2025 split by days between income year 2024-25 (181/365) and 2025-26 (184/365); minimum tax (s. 163), sector rates (tobacco, mobile operators, merchant banks), one-person companies and publicly traded companies with 10 % or less by IPO not modelled"] else [])

#guard wht.amount { kind := .dividend, amount := 1000, toCompany := false } == 300
#guard wht.amount { kind := .interest, amount := 1000 } == 200
#guard (citSplit { profit := 1000000 }).due == 275000
#guard (citSplit { profit := 1000000, flags := ["cashless"] }).due == 262603
#guard (citSplit { profit := 1000000, flags := ["listed"] }).due == 225000
#guard (citSplit { profit := 1000000, flags := ["listed", "cashless"] }).due == 200000
#guard (citSplit { profit := 1000000, flags := ["bank"] }).due == 400000
#guard (citSplit { profit := 1000000, flags := ["bank", "listed"] }).due == 375000

end BdGlobal.Corporate
