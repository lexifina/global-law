import SrGlobal.Pit

/-!
# SR 2025: corporate income tax (1200)

Wet Inkomstenbelasting 1922 (as amended): "De belasting van lichamen wordt geheven … naar een tarief van 36 percent"; the solidarity levy of 2021 "vervalt op 1 januari 2022": grade B (2023-2025 amendments not checked).

**Pass 7 (2026-11-21), withholding on payments abroad:** Wet Inkomstenbelasting art. 1 lid 3: non-residents are taxed only on binnenlands onzuiver inkomen; art. 27 lid 2 lists the domestic sources: real property, claims secured on Surinamese property, profit shares in a business managed in Suriname (not from securities), PE profits, certain employments and pensions. Unsecured interest, royalties and fees of a non-resident without a PE are not among them: cited 0. Dividends fall under the Wet Dividendbelasting 1973 (not held): grade C.

**Pass 8 (2026-11-21), withholding on payments abroad:** dividends: Wet Dividendbelasting 1973 art. 1: a direct tax on whoever is entitled to the proceeds of shares in a company established in Suriname; art. 5 lid 1: 25 percent; art. 6: withheld by the company. Grade A.
-/

namespace SrGlobal.Corporate
open TaxKernel TaxKernel.Global AmerCommon SrGlobal

def regime : CorpRegime :=
  { name := "Inkomstenbelasting van lichamen", sched := Schedule.flat 3600 }

def citStatute : String := "Wet Inkomstenbelasting art. 47 lid 1: 36 percent"

def wht : Wht :=
  { name := "Withholding tax (non-residents)", rules := [{ kind := .interest, rateBp := 0, statute := "Wet Inkomstenbelasting 1922 art. 1 lid 3, art. 27 lid 2 (S.B. 2024 no. 3): not a binnenlandse bron of a non-resident: no tax, none withheld" }, { kind := .royalty, rateBp := 0, statute := "Wet Inkomstenbelasting 1922 art. 1 lid 3, art. 27 lid 2 (S.B. 2024 no. 3): not a binnenlandse bron of a non-resident: no tax, none withheld" }, { kind := .services, rateBp := 0, statute := "Wet Inkomstenbelasting 1922 art. 1 lid 3, art. 27 lid 2 (S.B. 2024 no. 3): not a binnenlandse bron of a non-resident: no tax, none withheld" }, { kind := .dividend, rateBp := 2500, statute := "Wet Dividendbelasting 1973 (G.B. 1973 no. 8, laatstelijk S.B. 1984 no. 109) art. 5 lid 1: 25 percent van de opbrengst, ingehouden (art. 6)" }] }

def citF : Family := corpFamily "1200 Inkomstenbelasting van lichamen" (fun _ => regime) (fun _ => citStatute) wht (fun _ => [])

def families : List Family := [citF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.entity == .company) "losses brought forward, interest limitation and participation exemptions not modelled: taxable profit = profit + add-backs − exempt income"
  ++ when (g.entity == .company && !g.company.paymentsAbroad.isEmpty) "interest secured by a mortgage on Surinamese real property is a domestic source (art. 27 lid 2 b 1°): not distinguished"
  ++ when (g.entity == .company && !g.company.paymentsAbroad.isEmpty) "Wet Dividendbelasting art. 4 (no withholding on distributions to Surinamese investment companies and continuous Surinamese shareholders) and art. 5 lid 2 (grossing-up when the company bears the tax) not modelled"

#guard regime.citTax { profit := 1000000 } == 360000
#guard wht.amount { kind := .interest, amount := 1000000 } == 0
#guard wht.amount { kind := .royalty, amount := 1000000 } == 0
#guard wht.amount { kind := .services, amount := 1000000 } == 0
#guard wht.amount { kind := .dividend, amount := 1000000 } == 250000

end SrGlobal.Corporate
