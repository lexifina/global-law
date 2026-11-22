import HrGlobal.Pit

/-!
# HR 2025: Wealth family not reached (grade C)

* 4300 Inheritance and gift tax (Zakon o lokalnim porezima (porez na nasljedstva i darove 4 %)): tried not read in the P6 pass; would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)
* 4200 Net wealth tax (none recorded): tried not read in the P6 pass; would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)

* **4200 not levied (cited, pass 6, grade B)**: PwC Worldwide Tax Summaries, Croatia, Individual - Other taxes, accessed 2025-08-02 (Wayback capture; `law/pwc_indother_wb2025.txt`): net wealth tax: none (PwC WWTS Individual - Other taxes, 2025-08-02 (Wayback capture))


## 4300 Porez na nasljedstva i darove (pass 6)
Source: Zakon o lokalnim porezima, Narodne novine 115/2016 (`hr/law/nn2016_115_2524_zlp.txt`); Porezna uprava, Porez na nasljedstva i darove (`hr/law/pu_nasljedstva.txt`).
* čl. 8: "Porez na nasljedstva i darove plaća se po stopi od 4%."
* čl. 9: not paid by "1. bračni drug, potomci i preci koji čine uspravnu liniju te posvojenici i posvojitelji"; 3. public bodies, religious communities, foundations
* čl. 4 (1): charged on cash, claims, securities and movables whose individual market value exceeds the threshold (Porezna uprava 2025: 6.700,00 eura); real estate is outside (porez na promet nekretnina)
-/

namespace HrGlobal.Wealth
open TaxKernel TaxKernel.Global

/-- Zakon o lokalnim porezima čl. 4 (cash, claims, securities, movables above EUR 6 700 each), čl. 8 (4 %), čl. 9 (spouse, lineal descendants and ascendants, public bodies, religious communities and foundations exempt) -/
def p6naslClass : Relation → Nat
  | _ => 0
def p6nasl : InheritanceTax :=
  { name := "Porez na nasljedstva i darove", classOf := p6naslClass,   classes := [{ allowance := 0, sched := Schedule.flat 400 }],   exemptRelations := [.spouse, .child, .grandchild, .parent, .charity], lookbackYears := 0,   exemptValue := fun t => min (pos t.statutoryValue) (pos t.homeValue) }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4300 Porez na nasljedstva i darove", covers := [.estate],
     run := fun args g prev =>
       p6nasl.charges g.transfers "Zakon o lokalnim porezima čl. 4 (cash, claims, securities, movables above EUR 6 700 each), čl. 8 (4 %), čl. 9 (spouse, lineal descendants and ascendants, public bodies, religious communities and foundations exempt)" }]

def absent : List Absent :=
  [{ oecd := .wealth, why := "net wealth tax: none" }]

def notes : List String := ["HR 4300 Porez na nasljedstva i darove: NN 115/2016 (amended NN 101/17, 114/22, 114/23, 152/24: amendments not read; Porezna uprava page fetched 2026-11-21 states 4 % and the EUR 6 700 threshold) (grade A)", "HR 4300 Porez na nasljedstva i darove: back to B (pass 17, 2025 text read)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.transfers.isEmpty then ["4300 real estate is outside this tax (čl. 4): only the transfer's homeValue is excluded, other real estate in the value is taxed here (overstates); movables up to EUR 6 700 each are not separated"] else [])

#guard p6nasl.tax { kind := .inheritance, value := 100000, relation := .spouse } == 0
#guard p6nasl.tax { kind := .inheritance, value := 1000000, relation := .spouse } == 0
#guard p6nasl.tax { kind := .inheritance, value := 100000, relation := .child } == 0
#guard p6nasl.tax { kind := .inheritance, value := 1000000, relation := .child } == 0
#guard p6nasl.tax { kind := .inheritance, value := 100000, relation := .sibling } == 4000
#guard p6nasl.tax { kind := .inheritance, value := 1000000, relation := .sibling } == 40000
#guard p6nasl.tax { kind := .inheritance, value := 100000, relation := .unrelated } == 4000
#guard p6nasl.tax { kind := .inheritance, value := 1000000, relation := .unrelated } == 40000
#guard p6nasl.tax { kind := .inheritance, value := 300000, homeValue := 200000, relation := .sibling } == 4000

end HrGlobal.Wealth
