import MxGlobal.Pit

/-!
# Mexico 2025: ISR de personas morales (1200)

Source: LISR (Cámara de Diputados PDF archived 2025-06-17, "Última Reforma DOF 01-04-2024"; `mx/law/LISR.txt`).
* **art. 9**: "al resultado fiscal obtenido en el ejercicio la tasa del 30%".
* Dividends paid abroad: "tasa adicional del 10% sobre las utilidades" (arts. 140, 164) withheld by the payer.
  Interest and royalty rates for non-residents (arts. 166, 167) not read.

**Pass 7 (2026-11-21), withholding on payments abroad:** LISR art. 166: interest paid abroad is withheld at 10 % (foreign banks, fr. I), 4.9 % (fr. II), 15 % (reinsurers), 21 % (fr. IV: paid by credit institutions, machinery suppliers, habilitación y avío) and otherwise (fr. V) the art. 152 top rate, 35 %: the lender's type is not an input, fr. V is applied; art. 167 fr. II: royalties and technical assistance 25 % (patents, trademarks and advertising at the art. 152 top rate); art. 156: services 25 % when rendered in Mexico (presumed when paid to a related party). Grade A.
-/

namespace MxGlobal.Corporate
open TaxKernel TaxKernel.Global AmerCommon MxGlobal

def regime : CorpRegime :=
  { name := "Impuesto sobre la renta (personas morales)", sched := Schedule.flat 3000 }

def citStatute : String := "LISR art. 9 (30 %)"

def wht : Wht :=
  { name := "Withholding tax (non-residents)", rules := [{ kind := .dividend, rateBp := 1000, statute := "LISR arts. 140, 164: additional 10 % on dividends" }, { kind := .interest, rateBp := 3500, statute := "LISR (DOF 01-04-2024) art. 166 fr. V: other interest, the art. 152 top rate (35 %)" }, { kind := .royalty, rateBp := 2500, statute := "LISR (DOF 01-04-2024) art. 167 fr. II: royalties 25 %" }, { kind := .services, rateBp := 2500, statute := "LISR (DOF 01-04-2024) art. 167 fr. II (technical assistance) and art. 156 (services presumed rendered in Mexico when paid to a related party): 25 %" }] }

def citF : Family := corpFamily "1200 Impuesto sobre la renta (personas morales)" (fun _ => regime) (fun _ => citStatute) wht (fun _ => [])

def families : List Family := [citF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.entity == .company) "losses brought forward, interest limitation and participation exemptions not modelled: taxable profit = profit + add-backs − exempt income"
  ++ when (g.entity == .company) "PTU (employees' profit share, 10 %) and losses not modelled"
  ++ when (g.entity == .company && !g.company.paymentsAbroad.isEmpty) "LISR art. 166 fr. I-IV reduced interest rates (banks 10 %, 4.9 %, reinsurers 15 %, fr. IV 21 %), the 35 % on patent and trademark royalties (art. 167) and the source rule for services rendered abroad by an unrelated provider (art. 156) not modelled"

#guard regime.citTax { profit := 1000000 } == 300000
#guard wht.amount { kind := .dividend, amount := 1000000 } == 100000
#guard wht.amount { kind := .interest, amount := 1000000 } == 350000
#guard wht.amount { kind := .royalty, amount := 1000000 } == 250000
#guard wht.amount { kind := .services, amount := 1000000 } == 250000

end MxGlobal.Corporate
