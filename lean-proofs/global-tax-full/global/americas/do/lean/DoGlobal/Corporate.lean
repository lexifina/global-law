import DoGlobal.Pit

/-!
# Dominican Republic 2025: ISR de personas jurídicas (1200)

Source: Código Tributario Título II (DGII PDF, `world/.../do/law/t2.txt`).
* **art. 297**: "A partir del ejercicio fiscal 2015: 27%". **art. 305** (Ley 253-12): payments abroad withheld at "la
  misma tasa establecida en el artículo 297"; **art. 306**: interest "diez por ciento (10%)".
* The 1 % tax on assets (art. 401 ff., Título IV) is a minimum against the ISR: not modelled.

**Pass 8 (2026-11-21), withholding on payments abroad:** Código Tributario art. 308 (Ley 253-12): whoever pays dividends of Dominican source to residents or non-residents withholds 10 %, final. Grade A.
-/

namespace DoGlobal.Corporate
open TaxKernel TaxKernel.Global AmerCommon DoGlobal

def regime : CorpRegime :=
  { name := "Impuesto sobre la renta (personas jurídicas)", sched := Schedule.flat 2700 }

def citStatute : String := "Código Tributario art. 297 (27 %)"

def wht : Wht :=
  { name := "Withholding tax (non-residents)", rules := [{ kind := .interest, rateBp := 1000, statute := "Código Tributario art. 306 (10 %)" }, { kind := .royalty, rateBp := 2700, statute := "Código Tributario art. 305 (art. 297 rate)" }, { kind := .services, rateBp := 2700, statute := "Código Tributario art. 305 (art. 297 rate)" }, { kind := .dividend, rateBp := 1000, statute := "Código Tributario (Ley 11-92) art. 308 (Ley 253-12): dividends to residents or non-residents 10 %, pago único y definitivo" }] }

def citF : Family := corpFamily "1200 Impuesto sobre la renta (personas jurídicas)" (fun _ => regime) (fun _ => citStatute) wht (fun _ => [])

def families : List Family := [citF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.entity == .company) "losses brought forward, interest limitation and participation exemptions not modelled: taxable profit = profit + add-backs − exempt income"
  ++ when (g.entity == .company) "impuesto sobre los activos (1 %, credited against ISR)"
  ++ when (g.entity == .company && !g.company.paymentsAbroad.isEmpty) "Código Tributario art. 308 Párrafo I (dividends paid out of a dividend account of an inter-company dividend: no withholding) not modelled"

#guard regime.citTax { profit := 1000000 } == 270000
#guard wht.amount { kind := .interest, amount := 1000000 } == 100000
#guard wht.amount { kind := .royalty, amount := 1000000 } == 270000
#guard wht.amount { kind := .services, amount := 1000000 } == 270000
#guard wht.amount { kind := .dividend, amount := 1000000 } == 100000

end DoGlobal.Corporate
