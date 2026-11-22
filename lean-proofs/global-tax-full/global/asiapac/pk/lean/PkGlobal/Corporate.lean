import PkGlobal.Pit

/-!
# Pakistan, tax year 2026 (1 July 2025 - 30 June 2026): company income tax, super tax, dividend tax (1200)

Source: Income Tax Ordinance 2001, FBR Income Tax Manual Part I "AMENDED UPTO 31st JULY, 2025"
(`cmp20/world/B11-south-asia/pk/law/ito25.txt`; the 1.x PK model uses the same tax year, 2026).
* **First Schedule Part I Division II** (Table substituted by the Income Tax (Amendment) Act 2025): banking company "Tax Year
  2025 44% / Tax Year 2026 43% / 2027 and onwards 42%"; "Small Company 20%"; "Any other company 29%" (flags `bank`,
  `smallCompany`; the s. 2 (59A) small-company test is the company's flag).
* **s. 4C + Division IIB** (Finance Act 2025, column for tax year 2026): super tax as a rate of the whole income: the 1.x
  model's `superTax` (≤ 150 m 0 %; to 200 m 1 %; 250 m 1.5 %; 300 m 2.5 %; 350 m 3.5 %; 400 m 5.5 %; 500 m 7.5 %; above 10 %).
* **s. 5 + Division III (b)** (Finance Act 2025): dividends 15 % (paid abroad: withheld, s. 150).

**Session 11 (year in force).** Calendar 2025 straddles tax year 2025 (to 30 June 2025, Finance Act 2024) and tax year 2026
(from 1 July 2025, Finance Act 2025). Compared in the FBR consolidations "AMENDED UPTO 30.06.2024" (`pk/law/pk_ito_upto20240630.pdf`)
and "AMENDED UPTO 31st JULY, 2025" (`cmp20/world/B11-south-asia/pk/law/ito_fbr_20250731.pdf`):
* unchanged: Division II "Any other company 29%", "Small Company 20%"; Division III (b) 15 % (FA 2024 and FA 2025 texts:
  only the mutual-fund cases moved, to (ba)); Division IV 15 % of royalties and fees for technical services; Part III
  Division II (2) 20 %.
* changed: Division II banking company "Tax Year 2025 44% / Tax Year 2026 43%" (Income Tax (Amendment) Act 2025); Division
  IIB column "For tax year 2023, 2024 and 2025" 0 / 1 / 2 / 3 / 4 / 6 / 8 / 10 % against "2026 and onwards" 0 / 1 / 1.5 / 2.5
  / 3.5 / 5.5 / 7.5 / 10 % (Finance Act 2025). Both are applied to the year's income by days: 181/365 at the tax year 2025
  rate, 184/365 at the tax year 2026 rate (a company whose accounts follow the calendar year has a special tax year,
  s. 74 (3): not modelled, flagged).
-/

namespace PkGlobal.Corporate
open TaxKernel TaxKernel.Global

/-- The rate by the company's flags (sector), else the general rate. -/
def rateOf (co : Company) : Int := if co.flags.contains "bank" then 4300 else if co.flags.contains "smallCompany" then 2000 else 2900

def cit (co : Company) : CorpRegime :=
  { name := "Income tax on companies",
    sched := Schedule.flat (rateOf co) }

def citStatute : String := "Income Tax Ordinance 2001 First Schedule Part I Division II (Income Tax (Amendment) Act 2025: banking company tax year 2025 44 % (difference charged separately for 1 Jan - 30 Jun 2025), tax year 2026 43 %; small company 20 %, any other company 29 % in both tax years)"

def wht : Wht :=
  { name := "Tax on dividends and on payments to non-residents (s. 5, s. 6, s. 150, s. 152)", rules := [
      { kind := .dividend, rateBp := 1500, statute := "ITO 2001 s. 5, First Schedule Part I Division III (b) (15 %, Finance Act 2025)" },
      { kind := .royalty, rateBp := 1500, statute := "ITO 2001 s. 6, s. 152 (1), First Schedule Part I Division IV (15 %, Finance Act 2022)" },
      { kind := .services, rateBp := 1500, statute := "ITO 2001 s. 6, s. 152 (1): fees for technical services, First Schedule Part I Division IV (15 %)" },
      { kind := .interest, rateBp := 2000, statute := "ITO 2001 s. 152 (2), First Schedule Part III Division II (2) (20 % of the gross amount)" }] }

/-- s. 4C super tax on high earning persons (First Schedule Part I Division IIB as substituted by the Finance Act 2025,
column for tax year 2026): the 1.x model's own function `superTax` (a rate of the whole income by band), on the company's
taxable income (income under s. 4C taken as taxable income). -/
def superTaxCharge (co : Company) : Charge :=
  let ti := (cit co).taxableProfit co
  charge .cit "Super tax (s. 4C)" ti id (fun x => PkTax.superTax x) (statute := "ITO 2001 s. 4C, First Schedule Part I Division IIB (Finance Act 2025)")

/-- Division IIB, column "For tax year 2023, 2024 and 2025" (FBR consolidation to 31.07.2025, footnote text of the Table
substituted by the Finance Act 2025; the 30.06.2024 consolidation column "2023 and onwards" is the same). -/
def superTaxRate25 (inc : Int) : Int :=
  if inc ≤ 150000000 then 0 else if inc ≤ 200000000 then 100 else if inc ≤ 250000000 then 200
  else if inc ≤ 300000000 then 300 else if inc ≤ 350000000 then 400 else if inc ≤ 400000000 then 600
  else if inc ≤ 500000000 then 800 else 1000
def superTax25 (inc : Int) : Int := divR .halfUp (superTaxRate25 inc * pos inc) BP
/-- Calendar 2025: 181 days of tax year 2025 (1 Jan - 30 Jun 2025) and 184 days of tax year 2026 (1 Jul - 31 Dec 2025). -/
def split25 (ty25 ty26 : Int) : Int := divR .halfUp (181 * ty25 + 184 * ty26) 365
/-- s. 4C super tax, split at 1 July 2025: tax year 2025 column on 181/365, tax year 2026 column (the 1.x `superTax`) on 184/365. -/
def superTaxSplit (co : Company) : Charge :=
  let ti := (cit co).taxableProfit co
  charge .cit "Super tax (s. 4C), tax year 2025 rates to 30 June and tax year 2026 rates from 1 July 2025 (by days)" ti id
    (fun x => split25 (superTax25 x) (PkTax.superTax x))
    (statute := "ITO 2001 s. 4C, First Schedule Part I Division IIB: column for tax years 2023-2025 (to 30 June 2025) and for tax year 2026 (Finance Act 2025, from 1 July 2025)")
/-- Banking company: Division II "Tax Year 2025 44%" for 1 Jan - 30 Jun 2025 against the 43 % of tax year 2026 charged by
`cit`: the difference, 1 % on 181/365 of the taxable income. -/
def bankTy25 (co : Company) : List Charge :=
  if !co.flags.contains "bank" then [] else
  let ti := (cit co).taxableProfit co
  [charge .cit "Banking company: tax year 2025 rate 44 % for 1 Jan - 30 Jun 2025 (1 % above the 43 % of tax year 2026, on 181/365)" ti id
    (fun x => divR .halfUp (181 * 100 * pos x) (365 * BP))
    (statute := "ITO 2001 First Schedule Part I Division II (Table substituted by the Income Tax (Amendment) Act 2025): banking company tax year 2025 44 %, tax year 2026 43 %")]

def families : List Family :=
  [{ name := "1200 corporate income tax and withholding", covers := [.cit],
     run := fun _ g _ => if g.entity != .company then [] else
       [(cit g.company).citCharge g.company citStatute]
       ++ wht.charges g.company
       ++ [superTaxSplit g.company]
       ++ bankTy25 g.company }]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  (if true then ["minimum tax on turnover (s. 113, 1.25 %) and the alternative corporate tax (s. 113C) are not modelled"] else [])
  ++ (if true then ["calendar 2025 split by days between tax year 2025 (181/365) and tax year 2026 (184/365) for the bank rate and the s. 4C super tax; a special tax year (s. 74 (3)) is not modelled"] else [])

#guard (cit { profit := 1000000 }).citTax { profit := 1000000 } == 290000
#guard (cit { profit := 1000000, flags := ["bank"] }).citTax { profit := 1000000 } == 430000
#guard wht.amount { kind := .dividend, amount := 1000 } == 150
#guard wht.amount { kind := .royalty, amount := 1000 } == 150
#guard wht.amount { kind := .interest, amount := 1000 } == 200
#guard wht.amount { kind := .interest, amount := 1000, toCompany := false } == 200
#guard (superTaxSplit { profit := 160000000 }).due == 1600000
#guard (superTaxSplit { profit := 150000000 }).due == 0
#guard (superTaxSplit { profit := 450000000 }).due == 34865753
#guard (superTaxSplit { profit := 600000000 }).due == 60000000
#guard (bankTy25 { profit := 1000000, flags := ["bank"] }).map (·.due) == [4959]
#guard (bankTy25 { profit := 1000000 }).length == 0

end PkGlobal.Corporate
