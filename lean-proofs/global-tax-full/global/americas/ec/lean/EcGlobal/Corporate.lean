import EcGlobal.Pit

/-!
# Ecuador 2025: impuesto a la renta de sociedades (1200)

Source: LRTI, SRI consolidation (última reforma 24.10.2025; `world/.../ec/src/lrti.txt`).
* **art. 37**: sociedades "aplicarán la tarifa del 25% sobre su base imponible".
* **art. 39**: income of non-residents without a specific withholding rate "pagarán la tarifa general prevista para
  sociedades" (25 %): applied to royalties and services; dividends and interest have specific rules (not read).

**Pass 8 (2026-11-21), withholding on payments abroad:** LRTI art. 39: non-residents' income without a specific rate bears the company rate (25 %), withheld at source (interest, royalties, services); art. 39.2 num. 4 (substituted 28 Aug 2025): dividends to non-residents 10 % (12 %/14 % with a resident beneficial owner). Grade A.
-/

namespace EcGlobal.Corporate
open TaxKernel TaxKernel.Global AmerCommon EcGlobal

def regime : CorpRegime :=
  { name := "Impuesto a la renta (sociedades)", sched := Schedule.flat 2500 }

def citStatute : String := "LRTI art. 37 (25 %)"

def wht : Wht :=
  { name := "Withholding tax (non-residents)", rules := [{ kind := .royalty, rateBp := 2500, statute := "LRTI art. 39 (general rate for non-residents)" }, { kind := .services, rateBp := 2500, statute := "LRTI art. 39 (general rate for non-residents)" }, { kind := .dividend, rateBp := 1000, statute := "LRTI art. 39.2 num. 4 (as substituted by Ley RO 3S 112, 28 Aug 2025): dividends to non-residents 10 %" }, { kind := .interest, rateBp := 2500, statute := "LRTI art. 39 inc. 1: income of non-residents without a specific rate: the art. 37 company rate (25 %)" }] }

def citF : Family := corpFamily "1200 Impuesto a la renta (sociedades)" (fun _ => regime) (fun _ => citStatute) wht (fun _ => [])

def families : List Family := [citF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.entity == .company) "losses brought forward, interest limitation and participation exemptions not modelled: taxable profit = profit + add-backs − exempt income"
  ++ when (g.entity == .company) "reduced rates (art. 37 second paragraph, reinvestment, micro and small enterprises) and the tax haven surcharge not modelled"
  ++ when (g.entity == .company && !g.company.paymentsAbroad.isEmpty) "LRTI art. 39 (tax-haven recipients: the top personal rate), art. 39.2 num. 4-5 (12 %/14 % where the beneficial owner is resident in Ecuador or the shareholding is not reported) and the art. 13 deductibility conditions for foreign interest not modelled"

#guard regime.citTax { profit := 1000000 } == 250000
#guard wht.amount { kind := .royalty, amount := 1000000 } == 250000
#guard wht.amount { kind := .services, amount := 1000000 } == 250000
#guard wht.amount { kind := .dividend, amount := 1000000 } == 100000
#guard wht.amount { kind := .interest, amount := 1000000 } == 250000

end EcGlobal.Corporate
