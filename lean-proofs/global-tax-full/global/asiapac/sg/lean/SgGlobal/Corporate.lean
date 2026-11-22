import SgGlobal.Pit

/-!
# Singapore YA 2025: corporate income tax and withholding (1200)

Income Tax Act 1947: the SSO historical text was not fetched for this package (laptop route works; deferred to the upgrade
pass); rates from IRAS tables (B).
* **s. 43 (1) (a)**: 17 %. **s. 43 (6)**: partial exemption, 75 % of the first $10,000 and 50 % of the next $190,000 of
  chargeable income exempt: modelled as effective bands 4.25 % / 8.5 % / 17 %.
* **s. 45, s. 12 (7)**: interest 15 %, royalties 10 % (s. 43 (3A)), services 17 % to non-residents; no tax on dividends.
-/

namespace SgGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Corporate income tax",
    sched := Schedule.ofList [(0, 425), (10000, 850), (200000, 1700)] }

def citStatute : String := "ITA 1947 s. 43 (1) (a), s. 43 (6)"

def wht : Wht :=
  { name := "Withholding tax on payments to non-residents", rules := [
      { kind := .dividend, rateBp := 0, statute := "ITA 1947 s. 13 (1) (za): dividends paid by a Singapore-resident company are exempt" },
      { kind := .interest, rateBp := 1500, statute := "ITA 1947 s. 12 (6), s. 43 (3) (a), s. 45 (1) (a) (iii) (15 %)" },
      { kind := .royalty, rateBp := 1000, statute := "ITA 1947 s. 12 (7) (a), (b), s. 43 (3A), s. 45A (10 %)" },
      { kind := .services, toCompany := some false, rateBp := 2400, statute := "ITA 1947 s. 12 (7) (c) management fees, s. 45A, s. 45 (1) (a) (i) (24 % for individuals)" },
      { kind := .services, rateBp := 1700, statute := "ITA 1947 s. 12 (7) (c) management fees, s. 45A, s. 45 (1) (a) (ii) (17 %)" }] }

def families : List Family :=
  [{ name := "1200 corporate income tax and withholding", covers := [.cit],
     run := fun _ g _ => if g.entity != .company then [] else
       [cit.citCharge g.company citStatute]
       ++ wht.charges g.company }]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  (if true then ["YA 2025 50 % CIT rebate (cap $40,000), start-up exemption (s. 43 (6A)) and the MNE minimum tax not modelled"] else [])

#guard cit.citTax { profit := 1000000 } == 152575
#guard wht.amount { kind := .interest, amount := 1000 } == 150
#guard wht.amount { kind := .royalty, amount := 1000 } == 100
#guard wht.amount { kind := .services, amount := 1000 } == 170
#guard wht.amount { kind := .services, amount := 1000, toCompany := false } == 240
#guard wht.amount { kind := .services, amount := 1000 } == 170
#guard wht.amount { kind := .dividend, amount := 1000 } == 0

end SgGlobal.Corporate
