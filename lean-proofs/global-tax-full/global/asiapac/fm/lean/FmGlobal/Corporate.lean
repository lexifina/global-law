import FmGlobal.Pit

/-!
# Micronesia (FSM) 2025: no national tax on profits; the national tax on gross revenues

Source: FSM Code Title 54 ch. 1 (2014 codification, `cmp20/world/B14-pacific/fm/law/T54_Ch01_SubChpII_2014.txt`).
* **§ 141 (1)**: "a tax of $80 per year upon that portion of the amount of taxable gross revenues … [that] does not exceed
  $10,000 per year"; **(2)**: "a tax of three percent per year upon that portion … " above $10,000 (`grt`). OECD treats
  a gross-receipts tax under 5113 (general taxes on goods and services): booked as `.salesTax`.
* Gap-closing session (lexifina/micronesia-law, enrolled public laws from cfsm.gov.fm): **54 FSMC ch. 3 taxes Major
  Corporations on taxable income**. Public Law No. 21-09 (approved 5 July 2019) s. 1 rewrote **§ 321**: for taxable years
  ending on or after 31 March 2020, 21 % on the first $300,000,000, 25 % above that and below $500,000,000, 30 % above;
  PL 20-158 (§ 352: annual return, no interim payments) and PL 23-23 (§ 325: 0 % of the tax to the FSM Trust Fund, 2023)
  confirm the tax is in force. The session-1 cited absence ("no tax on business profits") was wrong and is withdrawn.
  The definition of a Major Corporation (ch. 3) was not read: only a company flagged `majorCorporation` is charged;
  other companies pay the gross revenue tax (§ 141). The repository holds 321 of the public laws: later amendments of
  § 321 are not excluded (B).
-/

namespace FmGlobal.Corporate
open TaxKernel TaxKernel.Global

def wht : Wht :=
  { name := "No withholding on payments abroad (FSMC Title 54)", rules := [
      { kind := .dividend, rateBp := 0, statute := "FSMC Title 54 ch. 1 (2014 codification): the national taxes are on wages and salaries (§ 121, withheld by employers § 131) and on business gross revenues (§ 141); no tax is withheld from payments abroad" },
      { kind := .interest, rateBp := 0, statute := "FSMC Title 54 ch. 1 (2014 codification): the national taxes are on wages and salaries (§ 121, withheld by employers § 131) and on business gross revenues (§ 141); no tax is withheld from payments abroad" },
      { kind := .royalty, rateBp := 0, statute := "FSMC Title 54 ch. 1 (2014 codification): the national taxes are on wages and salaries (§ 121, withheld by employers § 131) and on business gross revenues (§ 141); no tax is withheld from payments abroad" },
      { kind := .services, rateBp := 0, statute := "FSMC Title 54 ch. 1 (2014 codification): the national taxes are on wages and salaries (§ 121, withheld by employers § 131) and on business gross revenues (§ 141); no tax is withheld from payments abroad" }] }

/-- § 141: $80 on the first $10,000 of gross revenue, 3 % above. -/
def grt (t : Int) : Int := if t ≤ 0 then 0 else 80 + divR .down (300 * pos (t - 10000)) BP
def grtCharge (co : Company) : Charge :=
  charge .salesTax "Tax on gross revenues (§ 141)" co.turnover id grt (statute := "FSMC Title 54 § 141 (1)-(2)")
/-- 54 FSMC § 321 as amended by PL 21-09: 21 % to $300 m, 25 % to $500 m, 30 % above (taxable years ending from 31 Mar 2020). -/
def mcRegime : CorpRegime :=
  { name := "Major corporations tax", sched := Schedule.ofList [(0, 2100), (300000000, 2500), (500000000, 3000)] }

def families : List Family :=
  [{ name := "1200 corporate income tax and withholding", covers := [.cit, .salesTax],
     run := fun _ g _ => if g.entity != .company then [] else
       wht.charges g.company
       ++ [grtCharge g.company]
       ++ (if g.company.flags.contains "majorCorporation" then [mcRegime.citCharge g.company "54 FSMC § 321 as amended by PL 21-09 (2019): 21 % / 25 % / 30 %"] else []) }]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  (if true then ["1200 major corporations tax (54 FSMC ch. 3, § 321 as amended by PL 21-09): charged only on a company flagged majorCorporation (the definition of a Major Corporation was not read); other companies pay the gross revenue tax (§ 141)"] else [])

#guard grt 5000 == 80
#guard grt 110000 == 3080
#guard mcRegime.citTax { profit := 400000000 } == 88000000
#guard mcRegime.citTax { profit := 1000000 } == 210000

end FmGlobal.Corporate
