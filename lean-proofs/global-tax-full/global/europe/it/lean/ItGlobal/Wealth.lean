import ItGlobal.Pit

/-!
# IT 2025: Wealth family not reached (grade C)

* 4300 Inheritance and gift tax (D.Lgs. 346/1990 art. 7 (4 %, 6 %, 8 %) (fetched; rates not extracted)): tried not read in the P6 pass; would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)
* 4200 Net wealth tax (IVIE / IVAFE (DL 201/2011 art. 19)): tried not read in the P6 pass; would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)

* **4200 not levied (cited, pass 6, grade B)**: PwC Worldwide Tax Summaries, Italy, Individual - Other taxes, accessed 2025-07-21 (Wayback capture; `law/pwc_indother_wb2025.txt`): general net wealth tax: none; IVIE (1,06 % from 2024) and IVAFE reach only real estate and financial assets abroad (DL 201/2011 art. 19, not read): not modelled, assets in the input taken as Italian (PwC WWTS Individual - Other taxes, 2025-07-21 (Wayback capture))


## 4300 Imposta sulle successioni e donazioni (pass 6)
Source: D.Lgs. 346/1990 (TUS successioni e donazioni) art. 7, normattiva vigente al 2025-07-01 (testo in vigore dal 3-10-2024, effect from 1.1.2025 by D.Lgs. 139/2024 art. 9 c. 3), `it/law/tus346_vig20250701_art7.txt`; art. 56-bis c. 2 (`..._art56.txt`) refers to the gift rate of art. 56 c. 1 lett. d).
* art. 7 c. 1 (rates by relationship, each on the beneficiary's net share): a) spouse and lineal relatives 4 % on the part above EUR 1 000 000; b) brothers and sisters 6 % above EUR 100 000; c) other relatives to the fourth degree, lineal in-laws and collateral in-laws to the third degree 6 % with no franchigia; d) everyone else 8 %
* art. 7 c. 2: a disabled beneficiary (L. 104/1992 art. 3 c. 3) is taxed only above EUR 1 500 000 (not modelled)
-/

namespace ItGlobal.Wealth
open TaxKernel TaxKernel.Global

/-- D.Lgs. 346/1990 art. 7 c. 1 lett. a)-d) (4 % above EUR 1 000 000 per beneficiary; 6 % above EUR 100 000; 6 %; 8 %) -/
def p6succClass : Relation → Nat
  | .spouse => 0
  | .child => 0
  | .grandchild => 0
  | .parent => 0
  | .sibling => 1
  | .nieceNephew => 2
  | .otherRelative => 2
  | _ => 3
def p6succ : InheritanceTax :=
  { name := "Imposta sulle successioni e donazioni", classOf := p6succClass,   classes := [{ allowance := 1000000, sched := Schedule.flat 400 },   { allowance := 100000, sched := Schedule.flat 600 },   { allowance := 0, sched := Schedule.flat 600 },   { allowance := 0, sched := Schedule.flat 800 }],   exemptRelations := [], lookbackYears := 0 }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4300 Imposta sulle successioni e donazioni", covers := [.estate],
     run := fun args g prev =>
       p6succ.charges g.transfers "D.Lgs. 346/1990 art. 7 c. 1 lett. a)-d) (4 % above EUR 1 000 000 per beneficiary; 6 % above EUR 100 000; 6 %; 8 %)" }]

def absent : List Absent :=
  [{ oecd := .wealth, why := "general net wealth tax: none; IVIE (1,06 % from 2024) and IVAFE reach only real estate and financial assets abroad (DL 201/2011 art. 19, not read): not modelled, assets in the input taken as Italian" }]

def notes : List String := ["IT 4300 Imposta sulle successioni e donazioni: normattiva, art. 7 testo in vigore dal 3-10-2024 (applies to successions from 1.1.2025) (grade A)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.transfers.any (·.kind == .gift) then ["4300 gifts: art. 56 (same letters a)-d), cited through art. 56-bis c. 2) not read; the art. 7 rates and franchigie are applied; the coacervo of earlier gifts (art. 57) is not applied"] else [])
  ++ (if !g.transfers.isEmpty then ["4300 imposte ipotecaria e catastale (2 % + 1 %) on inherited real estate, the disabled-beneficiary franchigia (art. 7 c. 2), exempt beneficiaries (art. 3: public bodies, ONLUS) and reductions (arts. 25-26) not modelled"] else [])

#guard p6succ.tax { kind := .inheritance, value := 100000, relation := .spouse } == 0
#guard p6succ.tax { kind := .inheritance, value := 1000000, relation := .spouse } == 0
#guard p6succ.tax { kind := .inheritance, value := 100000, relation := .child } == 0
#guard p6succ.tax { kind := .inheritance, value := 1000000, relation := .child } == 0
#guard p6succ.tax { kind := .inheritance, value := 100000, relation := .sibling } == 0
#guard p6succ.tax { kind := .inheritance, value := 1000000, relation := .sibling } == 54000
#guard p6succ.tax { kind := .inheritance, value := 100000, relation := .unrelated } == 8000
#guard p6succ.tax { kind := .inheritance, value := 1000000, relation := .unrelated } == 80000

end ItGlobal.Wealth
