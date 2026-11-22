import TlGlobal.Pit

/-!
# Timor-Leste 2025: income tax on companies and withholding (1200)

Source: Lei 8/2008 (Lei Tributária), Jornal da República 2008 n.º 26 (`cmp20/world/B03-asia-east-se/tl/law/jr2008_no26.txt`).
* Income tax rate table: "No caso de uma pessoa colectiva 10%".
* Withholding: royalties (art. 54), rent of land or buildings (art. 55), prizes (art. 56): "à taxa de 10%" of the gross;
  payments to non-residents (art. 60) at the same rate.
-/

namespace TlGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Imposto sobre o rendimento (pessoas colectivas)",
    sched := Schedule.flat 1000 }

def citStatute : String := "Lei 8/2008, tabela do imposto sobre o rendimento"

def wht : Wht :=
  { name := "Withholding tax on payments to non-residents", rules := [
      { kind := .dividend, rateBp := 0, statute := "Lei 8/2008 art. 29 (f): dividends are exempt income; art. 60 (1): withholding does not apply to amounts not subject to income tax" },
      { kind := .interest, rateBp := 1000, statute := "Lei 8/2008 art. 49 (1) (g), art. 57 (10 % on Timor-Leste-source payments to non-residents)" },
      { kind := .royalty, rateBp := 1000, statute := "Lei 8/2008 art. 49 (1) (g), art. 57 (10 %)" },
      { kind := .services, rateBp := 1000, statute := "Lei 8/2008 art. 49 (1) (g) (management fees paid by a resident), art. 57 (10 %)" },
      { kind := .rent, rateBp := 1000, statute := "Lei 8/2008 art. 57 (10 %)" }] }

def families : List Family :=
  [{ name := "1200 corporate income tax and withholding", covers := [.cit],
     run := fun _ g _ => if g.entity != .company then [] else
       [cit.citCharge g.company citStatute]
       ++ wht.charges g.company }]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard cit.citTax { profit := 1000000 } == 100000
#guard wht.amount { kind := .royalty, amount := 1000 } == 100
#guard wht.amount { kind := .rent, amount := 1000 } == 100
#guard wht.amount { kind := .interest, amount := 1000 } == 100
#guard wht.amount { kind := .dividend, amount := 1000 } == 0

end TlGlobal.Corporate
