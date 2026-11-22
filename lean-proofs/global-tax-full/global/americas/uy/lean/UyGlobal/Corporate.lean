import UyGlobal.Pit

/-!
# Uruguay 2025: IRAE (1200)

Source: T.O. 1996 (DGI, updated until the T.O. 2023 of 04/04/2024; `world/.../uy/src/to1996.txt`): grade B.
* **Título 4 art. 15**: "La tasa del impuesto será del 25% (veinticinco por ciento) sobre la renta neta fiscal" (Ley
  18.083). The IRNR (Título 8) rates on payments to non-residents were not read.

**Pass 7 (2026-11-21), withholding on payments abroad:** IRNR (T.O. DGI 2023 Título 8): art. 10 makes IRAE taxpayers that pay Uruguayan-source income to a non-resident withholding agents; art. 18 B): dividends paid by IRAE taxpayers 7 %, other income 12 % (25 % for low-tax jurisdictions); art. 19 exemptions. Grade A.
-/

namespace UyGlobal.Corporate
open TaxKernel TaxKernel.Global AmerCommon UyGlobal

def regime : CorpRegime :=
  { name := "Impuesto a las Rentas de las Actividades Económicas (IRAE)", sched := Schedule.flat 2500 }

def citStatute : String := "T.O. 1996 Título 4 art. 15 (25 %)"

def wht : Wht :=
  { name := "Withholding tax (non-residents)", rules := [{ kind := .dividend, rateBp := 700, statute := "T.O. DGI 2023 Título 8 (IRNR) art. 18 B): dividendos pagados por contribuyentes del IRAE 7 %" }, { kind := .interest, rateBp := 1200, statute := "T.O. DGI 2023 Título 8 (IRNR) art. 18 B): restantes rentas 12 %" }, { kind := .royalty, rateBp := 1200, statute := "T.O. DGI 2023 Título 8 (IRNR) art. 18 B): restantes rentas 12 %" }, { kind := .services, rateBp := 1200, statute := "T.O. DGI 2023 Título 8 (IRNR) art. 18 B): restantes rentas 12 %" }] }

def citF : Family := corpFamily "1200 Impuesto a las Rentas de las Actividades Económicas (IRAE)" (fun _ => regime) (fun _ => citStatute) wht (fun _ => [])

def families : List Family := [citF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.entity == .company) "losses brought forward, interest limitation and participation exemptions not modelled: taxable profit = profit + add-backs − exempt income"
  ++ when (g.entity == .company) "IRAE fictitious-income regimes for small companies (Título 4 art. 64 ff.) and minimum payments not modelled"
  ++ when (g.entity == .company && !g.company.paymentsAbroad.isEmpty) "IRNR 25 % for low- or no-tax jurisdictions (art. 18 B), interest exemptions (art. 19 A, B) and short-term deposit rates (art. 18 A) not modelled"

#guard regime.citTax { profit := 1000000 } == 250000
#guard wht.amount { kind := .dividend, amount := 1000000 } == 70000
#guard wht.amount { kind := .interest, amount := 1000000 } == 120000
#guard wht.amount { kind := .royalty, amount := 1000000 } == 120000
#guard wht.amount { kind := .services, amount := 1000000 } == 120000

end UyGlobal.Corporate
