import HnGlobal.Pit

/-!
# Honduras 2025: impuesto sobre la renta de personas jurídicas (1200)

Source: LISR consolidated by SAR (07-2025; `world/.../hn/src/lisr.txt`).
* **art. 22**: personas jurídicas 25 %. **art. 53**: non-residents: 4) profits of branches 10 %, 5) "Rentas,
  utilidades, dividendos …" 10 %, 3) compensation for services 25 %, 1) rents 25 %.
* The aportación solidaria and the 1.5 % minimum on gross income were not read.

**Pass 8 (2026-11-21), withholding on payments abroad:** LISR art. 5 (the consolidation's "Artículo 53" is art. 5 with footnote 3): non-residents pay on gross Honduran-source income: 25 % on services (num. 3), 10 % on dividends (num. 5), 25 % on royalties (num. 6), 10 % on interest (num. 7); art. 50: the payer withholds. Grade A.
-/

namespace HnGlobal.Corporate
open TaxKernel TaxKernel.Global AmerCommon HnGlobal

def regime : CorpRegime :=
  { name := "Impuesto sobre la renta (personas jurídicas)", sched := Schedule.flat 2500 }

def citStatute : String := "LISR art. 22 (25 %)"

def wht : Wht :=
  { name := "Withholding tax (non-residents)", rules := [{ kind := .dividend, rateBp := 1000, statute := "LISR (Decreto-Ley 25, SAR consolidation to Acuerdo SAR 07-2025) art. 5 num. 5): dividendos 10 %" }, { kind := .services, rateBp := 2500, statute := "LISR (Decreto-Ley 25, SAR consolidation to Acuerdo SAR 07-2025) art. 5 num. 3): compensación por servicios prestados dentro o fuera del territorio 25 %" }, { kind := .interest, rateBp := 1000, statute := "LISR (Decreto-Ley 25, SAR consolidation to Acuerdo SAR 07-2025) art. 5 num. 7): intereses 10 %" }, { kind := .royalty, rateBp := 2500, statute := "LISR (Decreto-Ley 25, SAR consolidation to Acuerdo SAR 07-2025) art. 5 num. 6): regalías por patentes, marcas, derechos de autor 25 %" }] }

def citF : Family := corpFamily "1200 Impuesto sobre la renta (personas jurídicas)" (fun _ => regime) (fun _ => citStatute) wht (fun _ => [])

def families : List Family := [citF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.entity == .company) "losses brought forward, interest limitation and participation exemptions not modelled: taxable profit = profit + add-backs − exempt income"
  ++ when (g.entity == .company) "aportación solidaria (5 % above L1 million) and the 1.5 % minimum on gross income not modelled"
  ++ when (g.entity == .company && !g.company.paymentsAbroad.isEmpty) "LISR art. 5: interest paid to a related party is taxed as a dividend (also 10 %); num. 9 (10 % software and telecoms) and num. 13 (10 % other operating income) not distinguished from services"

#guard regime.citTax { profit := 1000000 } == 250000
#guard wht.amount { kind := .dividend, amount := 1000000 } == 100000
#guard wht.amount { kind := .services, amount := 1000000 } == 250000
#guard wht.amount { kind := .interest, amount := 1000000 } == 100000
#guard wht.amount { kind := .royalty, amount := 1000000 } == 250000

end HnGlobal.Corporate
