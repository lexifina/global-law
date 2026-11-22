import CoGlobal.Pit

/-!
# Colombia 2025: impuesto sobre la renta de personas jurídicas (1200)

Source: Estatuto Tributario (Secretaría del Senado; `co/law/et/estatuto_tributario_pr010.txt`).
* **art. 240** (Ley 2277 de 2022 art. 10): "La tarifa general del impuesto sobre la renta aplicable a las sociedades
  … será del treinta y cinco por ciento (35%)". The surcharges for financial institutions (par. 2) and the minimum
  tax (par. 6, tasa mínima de tributación 15 %).
* **art. 408** (Ley 2010 de 2019 art. 98): payments abroad of interest, commissions, fees, royalties, rents, personal
  services, technical services and assistance: "la tarifa de retención será del veinte por ciento (20%)"; **art. 245**
  (Ley 2277 de 2022 art. 4): dividends to foreign companies and non-residents 20 % (`co/law/et/estatuto_tributario_pr016.txt`,
  `pr010.txt`; Senado consolidation updated 15 Nov 2026). The 33 % on management fees (art. 408 inc. 7), the 1 % on
  reinsurance and the reduced rates for long-term loans are not modelled.
-/

namespace CoGlobal.Corporate
open TaxKernel TaxKernel.Global AmerCommon CoGlobal

def regime : CorpRegime :=
  { name := "Impuesto sobre la renta (personas jurídicas)", sched := Schedule.flat 3500 }

def citStatute : String := "Estatuto Tributario art. 240 (35 %)"

def wht : Wht :=
  { name := "Withholding tax (non-residents)", rules := [{ kind := .interest, rateBp := 2000, statute := "ET art. 408 inc. 1 (20 %)" }, { kind := .royalty, rateBp := 2000, statute := "ET art. 408 inc. 1 (20 %)" }, { kind := .services, rateBp := 2000, statute := "ET art. 408 incs. 1-2 (20 %)" }, { kind := .dividend, rateBp := 2000, statute := "ET art. 245 (Ley 2277 de 2022 art. 4: 20 %)" }] }

def citF : Family := corpFamily "1200 Impuesto sobre la renta (personas jurídicas)" (fun _ => regime) (fun _ => citStatute) wht (fun _ => [])

def families : List Family := [citF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.entity == .company) "losses brought forward, interest limitation and participation exemptions not modelled: taxable profit = profit + add-backs − exempt income"
  ++ when (g.entity == .company) "tasa mínima de tributación (art. 240 par. 6) and sector surcharges not modelled; payments abroad: 33 % on management fees (art. 408), 1 % reinsurance, reduced long-term-loan rates not modelled"

#guard regime.citTax { profit := 1000000 } == 350000
#guard wht.amount { kind := .interest, amount := 1000000 } == 200000
#guard wht.amount { kind := .royalty, amount := 1000000 } == 200000
#guard wht.amount { kind := .services, amount := 1000000 } == 200000
#guard wht.amount { kind := .dividend, amount := 1000000 } == 200000

end CoGlobal.Corporate
