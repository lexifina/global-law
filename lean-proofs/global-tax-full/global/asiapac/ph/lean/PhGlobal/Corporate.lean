import PhGlobal.Pit

/-!
# Philippines 2025: corporate income tax and final tax on non-resident foreign corporations (1200)

NIRC as amended by RA 11534 (CREATE), RA 12066 (CREATE MORE) and RA 12214 (CMEPA): texts read in lexifina/philippines-law
(gap-closing session; official source elibrary.judiciary.gov.ph showdocs/2/93191, /2/98085, /2/99213): RA 12066 s. 1 (s. 27 (A),
in force 2024-12-03): 25 %; 20 % where net taxable income ≤ PHP 5 m and total assets ≤ PHP 100 m (the words "One hundred
million pesos" govern the misprinted figure "P1,000,000,000"); RA 12214 s. 5 (s. 25 (B): 25 %) and s. 7 (s. 28 (B) (1): 25 %);
RA 11534 s. 7 (s. 28 (B) (5) (b): 15 % on intercorporate dividends, tax-sparing condition). s. 28 (B) (5) (a) (interest on
foreign loans 20 %) is "x x x" in every amending act read: not read.
* **s. 27 (A)**: 25 %; 20 % for domestic corporations with net taxable income ≤ PHP 5 m and total assets ≤ PHP 100 m
  (flag `small`). **s. 27 (E)**: MCIT 2 % of gross income from the fourth year (not modelled).
* **s. 28 (B) (1)**: non-resident foreign corporations 25 % of gross income (royalties, services); **(5) (a)**: interest
  on foreign loans 20 %; **(5) (b)**: intercorporate dividends 15 % (tax-sparing condition; else 25 %).
-/

namespace PhGlobal.Corporate
open TaxKernel TaxKernel.Global

/-- The rate by the company's flags (sector), else the general rate. -/
def rateOf (co : Company) : Int := if co.flags.contains "small" then 2000 else 2500

def cit (co : Company) : CorpRegime :=
  { name := "Corporate income tax",
    sched := Schedule.flat (rateOf co) }

def citStatute : String := "NIRC s. 27 (A) as amended by RA 11534 s. 6 and RA 12066 s. 1"

def wht : Wht :=
  { name := "Withholding tax on payments to non-residents", rules := [
      { kind := .dividend, toCompany := some true, rateBp := 1500, statute := "NIRC s. 28 (B) (5) (b)" },
      { kind := .interest, toCompany := some true, rateBp := 2000, statute := "NIRC s. 28 (B) (5) (a)" },
      { kind := .royalty, toCompany := some true, rateBp := 2500, statute := "NIRC s. 28 (B) (1)" },
      { kind := .services, toCompany := some true, rateBp := 2500, statute := "NIRC s. 28 (B) (1)" },
      { kind := .dividend, toCompany := some false, rateBp := 2500, statute := "NIRC s. 25 (B): nonresident alien not engaged in trade or business, 25 % of the gross amount" },
      { kind := .interest, toCompany := some false, rateBp := 2500, statute := "NIRC s. 25 (B): nonresident alien not engaged in trade or business, 25 % of the gross amount" },
      { kind := .royalty, toCompany := some false, rateBp := 2500, statute := "NIRC s. 25 (B): nonresident alien not engaged in trade or business, 25 % of the gross amount" },
      { kind := .services, toCompany := some false, rateBp := 2500, statute := "NIRC s. 25 (B): nonresident alien not engaged in trade or business, 25 % of the gross amount" }] }

def families : List Family :=
  [{ name := "1200 corporate income tax and withholding", covers := [.cit],
     run := fun _ g _ => if g.entity != .company then [] else
       [(cit g.company).citCharge g.company citStatute]
       ++ wht.charges g.company }]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  (if true then ["MCIT 2 % of gross income (s. 27 (E)), improperly accumulated earnings and RBE incentive regimes not modelled"] else [])

#guard (cit { profit := 1000000 }).citTax { profit := 1000000 } == 250000
#guard wht.amount { kind := .dividend, amount := 1000, toCompany := true } == 150
#guard wht.amount { kind := .interest, amount := 1000, toCompany := true } == 200
#guard wht.amount { kind := .royalty, amount := 1000, toCompany := true } == 250
#guard wht.amount { kind := .services, amount := 1000, toCompany := true } == 250
#guard wht.amount { kind := .interest, amount := 1000, toCompany := false } == 250

end PhGlobal.Corporate
