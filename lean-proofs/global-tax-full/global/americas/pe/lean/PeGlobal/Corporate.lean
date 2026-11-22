import PeGlobal.Pit

/-!
# Peru 2025: impuesto a la renta de tercera categoría and non-domiciled withholding (1200)

Source: TUO de la Ley del Impuesto a la Renta, SUNAT chapters (`world/.../pe/src/capvii.txt`, the 1.x builder's copy).
* **art. 55**: "la tasa de veintinueve coma cincuenta por ciento (29,50%)".
* **art. 56** (non-domiciled legal persons): dividends "cinco por ciento (5%)"; d) "Regalías: treinta por ciento
  (30%)"; interest 30 % (4,99 % for qualifying foreign loans: flagged).

**Pass 8 (2026-11-21), withholding on payments abroad:** services: TUO LIR art. 56 f): technical assistance to a non-domiciled company 15 % (an audit report is needed above 140 UIT); art. 76: the payer withholds. Other services used in Peru fall under art. 56 j) (30 %): flagged. Grade A.
-/

namespace PeGlobal.Corporate
open TaxKernel TaxKernel.Global AmerCommon PeGlobal

def regime : CorpRegime :=
  { name := "Impuesto a la renta (tercera categoría)", sched := Schedule.flat 2950 }

def citStatute : String := "TUO LIR art. 55 (29,5 %)"

def wht : Wht :=
  { name := "Withholding tax (non-residents)", rules := [{ kind := .dividend, rateBp := 500, statute := "TUO LIR art. 56 (5 %)" }, { kind := .royalty, rateBp := 3000, statute := "TUO LIR art. 56 d) (30 %)" }, { kind := .interest, rateBp := 3000, statute := "TUO LIR art. 56 (30 %; 4,99 % qualifying loans not modelled)" }, { kind := .services, rateBp := 1500, statute := "TUO LIR art. 56 f) (D. Leg. 1120): asistencia técnica 15 %" }] }

def citF : Family := corpFamily "1200 Impuesto a la renta (tercera categoría)" (fun _ => regime) (fun _ => citStatute) wht (fun _ => [])

def families : List Family := [citF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.entity == .company) "losses brought forward, interest limitation and participation exemptions not modelled: taxable profit = profit + add-backs − exempt income"
  ++ when (g.entity == .company) "RMT and RER regimes for small companies not modelled"
  ++ when (g.entity == .company && !g.company.paymentsAbroad.isEmpty) "TUO LIR: services are taken as technical assistance used in Peru (art. 56 f), 15 %); services performed in Peru and digital services used in Peru (art. 56 j), 30 %) and services performed abroad that are not Peruvian-source (art. 9) not distinguished"

#guard regime.citTax { profit := 1000000 } == 295000
#guard wht.amount { kind := .dividend, amount := 1000000 } == 50000
#guard wht.amount { kind := .royalty, amount := 1000000 } == 300000
#guard wht.amount { kind := .interest, amount := 1000000 } == 300000
#guard wht.amount { kind := .services, amount := 1000000 } == 150000

end PeGlobal.Corporate
