import KhGlobal.Pit

/-!
# Cambodia 2025: tax on income and withholding on non-residents (1200)

Law on Taxation 2023: Khmer OCR on the build server (`cmp20/world/B03-asia-east-se/kh/law/law_taxation_2023_khm_ocr.txt`), the
rate articles not located in the OCR in this pass (B, GDT English summary).
* Tax on income 20 % (oil and gas, natural resources 30 %); minimum tax 1 % of turnover for taxpayers without proper
  accounting records (not modelled).
* Withholding on payments to non-residents (interest, royalties, services, dividends): 14 %.
-/

namespace KhGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Tax on income (companies)",
    sched := Schedule.flat 2000 }

def citStatute : String := "Law on Taxation 2023 (tax on income 20 %)"

def wht : Wht :=
  { name := "Withholding tax on payments to non-residents", rules := [
      { kind := .dividend, rateBp := 1400, statute := "Law on Taxation 2023 (non-resident withholding 14 %)" },
      { kind := .interest, rateBp := 1400, statute := "idem" },
      { kind := .royalty, rateBp := 1400, statute := "idem" },
      { kind := .services, rateBp := 1400, statute := "idem" }] }

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
  (if true then ["minimum tax (1 % of turnover), small-taxpayer bands and the 30 % resource rate not modelled"] else [])

#guard cit.citTax { profit := 1000000 } == 200000
#guard wht.amount { kind := .dividend, amount := 1000 } == 140
#guard wht.amount { kind := .interest, amount := 1000 } == 140
#guard wht.amount { kind := .royalty, amount := 1000 } == 140
#guard wht.amount { kind := .services, amount := 1000 } == 140

end KhGlobal.Corporate
