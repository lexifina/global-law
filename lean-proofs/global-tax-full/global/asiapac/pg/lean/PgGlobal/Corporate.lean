import PgGlobal.Pit

/-!
# Papua New Guinea 2025: company tax and withholding (1200)

Income Tax Act 1959 (PacLII copy `pg_ita1959116`, not a 2025 consolidation) and the Income Tax (Rates) Act: rates as read by
the registry (B). Resident companies 30 %; dividend withholding 17 %, interest 15 %, royalties 10 % (30 % to associates).
-/

namespace PgGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Income tax on companies",
    sched := Schedule.flat 3000 }

def citStatute : String := "Income Tax Act 1959 / Income Tax (Rates) Act (resident companies)"

def wht : Wht :=
  { name := "Withholding tax on payments to non-residents", rules := [
      { kind := .dividend, rateBp := 1700, statute := "ITA 1959 Div. 11A (dividend withholding)" },
      { kind := .interest, rateBp := 1500, statute := "Div. 11B" },
      { kind := .royalty, rateBp := 1000, statute := "Div. 11C (non-associates)" },
      { kind := .services, rateBp := 1700, statute := "Income Tax, Dividend (Withholding) Tax and Interest (Withholding) Tax Rates Act 1984 s. 6B (17 % of the gross taxable management fee); ITA 1959 Div. III.14C ss. 196R-196U" }] }

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
  (if true then ["non-resident company rate (48 %) and resource project rates not modelled"] else [])

#guard cit.citTax { profit := 1000000 } == 300000
#guard wht.amount { kind := .dividend, amount := 1000 } == 170
#guard wht.amount { kind := .interest, amount := 1000 } == 150
#guard wht.amount { kind := .royalty, amount := 1000 } == 100
#guard wht.amount { kind := .services, amount := 1000 } == 170

end PgGlobal.Corporate
