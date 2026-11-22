import CrGlobal.Pit

/-!
# Costa Rica 2025: impuesto a las utilidades (1200)

Source: Ley 7092 (LIR), SINALEVI version 148972 (`world/.../cr/src/sinalevi/ley7092_v83.txt`).
* **art. 15 a)**: "Personas jurídicas: Treinta por ciento (30%)". The reduced scale for small companies (gross
  income below a limit updated by decree each year) were not read.
* **art. 59** (non-residents, same SINALEVI version): c) fees and personal services 25 % (Ley 9635); g) dividends
  15 % (5 % per arts. 18-19 cases, not modelled); h) interest and financial costs 15 % (Ley 10335 of 2022; 5.5 % to
  supervised foreign banks and group banks not modelled); j) technical-financial advice, patents, trademarks, franchises
  and royalties 25 %.
-/

namespace CrGlobal.Corporate
open TaxKernel TaxKernel.Global AmerCommon CrGlobal

def regime : CorpRegime :=
  { name := "Impuesto sobre las utilidades", sched := Schedule.flat 3000 }

def citStatute : String := "Ley 7092 art. 15 a) (30 %)"

def wht : Wht :=
  { name := "Withholding tax (non-residents)", rules := [{ kind := .interest, rateBp := 1500, statute := "Ley 7092 art. 59 h) (15 %)" }, { kind := .royalty, rateBp := 2500, statute := "Ley 7092 art. 59 j) (25 %)" }, { kind := .services, rateBp := 2500, statute := "Ley 7092 art. 59 c), j) (25 %)" }, { kind := .dividend, rateBp := 1500, statute := "Ley 7092 art. 59 g) (15 %)" }] }

def citF : Family := corpFamily "1200 Impuesto sobre las utilidades" (fun _ => regime) (fun _ => citStatute) wht (fun _ => [])

def families : List Family := [citF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.entity == .company) "losses brought forward, interest limitation and participation exemptions not modelled: taxable profit = profit + add-backs − exempt income"
  ++ when (g.entity == .company) "small-company scale (art. 15 b), limits updated by decree) not modelled"
  ++ when (g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind != .interest && p.kind != .royalty && p.kind != .services && p.kind != .dividend)) "payments abroad of a kind without a rule read get no withholding"
  ++ when (g.entity == .company) "art. 59: 5 % dividend cases, 5.5 % interest to supervised foreign banks, transport/communications 8.5 %, reinsurance 5.5 % not modelled"

#guard regime.citTax { profit := 1000000 } == 300000
#guard wht.amount { kind := .interest, amount := 1000000 } == 150000
#guard wht.amount { kind := .royalty, amount := 1000000 } == 250000
#guard wht.amount { kind := .services, amount := 1000000 } == 250000
#guard wht.amount { kind := .dividend, amount := 1000000 } == 150000

end CrGlobal.Corporate
