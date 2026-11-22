import ArGlobal.Pit

/-!
# Argentina 2025: impuesto a las ganancias de sociedades (1200)

Sources: Ley de Impuesto a las Ganancias (t.o. 2019) **art. 73** as replaced by Ley 27.630 (InfoLEG texto actualizado,
read in pass 1): a progressive scale of 25 %, 30 % and 35 % whose amounts "se ajustarán anualmente ... considerando la
variación anual del Índice de Precios al Consumidor"; and ARCA's table "Impuesto a las Ganancias Personas Jurídicas -
Escala 2025" (`documentos/Ganancias-Escala-PJ-2025.pdf` linked from the ARCA page "Escala" for "ejercicios fiscales
iniciados a partir del 1° de enero de 2025", fetched 2026-11-21): "0,00 - 101.679.575,26: 0,00 + 25 %;
101.679.575,26 - 1.016.795.752,62: 25.419.893,82 + 30 %; 1.016.795.752,62 en adelante: 299.954.747,02 + 35 %".
The kernel marginal schedule reproduces both fixed amounts (to the peso). Grade B (official table for the indexed
amounts). Not modelled: the 7 % on dividends (art. 97), withholding on payments abroad (arts. 102-104, not read).

**Pass 7 (2026-11-21), withholding on payments abroad:** Ley de Impuesto a las Ganancias (T.O. 2019): art. 97 (Ley 27.630): dividends paid to beneficiarios del exterior: 7 %, withheld, final; art. 102: the payer of any other net gain to a beneficiary abroad withholds 35 % (art. 103) of the net gain art. 104 presumes: interest c) 2. 100 % (43 % when the borrower is a Ley 21.526 entity or the lender a bank in a cooperative jurisdiction), royalties and technical assistance a) 80 % / 60 % for contracts registered under Ley 22.426, otherwise i) 90 %. Grade A.
-/

namespace ArGlobal.Corporate
open TaxKernel TaxKernel.Global AmerCommon ArGlobal

def regime : CorpRegime :=
  { name := "Impuesto a las ganancias (sociedades)", sched := Schedule.ofList [(0, 2500), (101679575, 3000), (1016795752, 3500)] }

def citStatute : String := "LIG art. 73 (Ley 27.630); ARCA Escala 2025 (ejercicios iniciados desde el 1 Jan 2025): 25 % to $101,679,575.26, 30 % to $1,016,795,752.62, 35 % above"

def wht : Wht :=
  { name := "Withholding tax (non-residents)", rules := [{ kind := .dividend, rateBp := 700, statute := "LIG art. 97 (Ley 27.630) último párr.: beneficiarios del exterior 7 %, pago único y definitivo" }, { kind := .interest, rateBp := 3500, statute := "LIG arts. 102, 103, 104 c) 2.: 35 % of a presumed net gain of 100 %" }, { kind := .royalty, rateBp := 3150, statute := "LIG arts. 102, 103, 104 i): 35 % of a presumed 90 %" }, { kind := .services, rateBp := 3150, statute := "LIG arts. 102, 103, 104 i): 35 % of a presumed 90 %" }] }

def citF : Family := corpFamily "1200 Impuesto a las ganancias (sociedades)" (fun _ => regime) (fun _ => citStatute) wht (fun _ => [])

def families : List Family := [citF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.entity == .company) "losses brought forward, interest limitation and participation exemptions not modelled: taxable profit = profit + add-backs − exempt income"
  ++ when (g.entity == .company && !g.company.paymentsAbroad.isEmpty) "LIG art. 104 reduced presumptions not modelled: interest 43 % (financial-entity borrower or bank lender), royalties 80 % and technical assistance 60 % (contracts registered under Ley 22.426)"

#guard (regime.citTax { profit := 101679575 } - 25419893).natAbs ≤ 1
#guard (regime.citTax { profit := 1016795752 } - 299954747).natAbs ≤ 1
#guard (regime.citTax { profit := 2000000000 } - 644076233).natAbs ≤ 1
#guard wht.amount { kind := .dividend, amount := 1000000 } == 70000
#guard wht.amount { kind := .interest, amount := 1000000 } == 350000
#guard wht.amount { kind := .royalty, amount := 1000000 } == 315000
#guard wht.amount { kind := .services, amount := 1000000 } == 315000

end ArGlobal.Corporate
