import SmGlobal.Pit

/-!
# SM 2025: Property family not reached (grade C)

* 4400 Real-estate transfer and stamp duties (imposta di registro (Legge 85/2010)): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)
* 4100 Recurrent property tax (imposta sugli immobili): tried not read in the P5 pass; would unlock: the act and the reference municipality's 2025 rate (registry choice)


## 4400 Imposta di registro e di trascrizione (trasferimenti di immobili) (pass 6)
Source: Bollettino Ufficiale della Repubblica di San Marino (consolidated texts); read from lexifina/san-marino-law `imposte-di-registro-e-relativo-regolamento/legge-1981-85/art-76.md, legge 83/1981 art. 13` (commit 902a891, 32c9611, in force 3.6.2025).
* Tabella A n. 1 par. 1: registration duty on transfers of real estate 2,5 %, "ridotta sino al 31 dicembre 2025" (L. 202/2024 art. 1 c. 3)
* L. 83/1981 art. 13 tariff: transcription of transfers of property 1 % plus a fixed 70 EUR
* Hand check: purchase of 300 000: 7 500 + 3 000 = 10 500 (+ 70 fixed, not modelled)
-/

namespace SmGlobal.Property
open TaxKernel TaxKernel.Global

/-- Legge 29 ottobre 1981 n. 85 Tabella A n. 1 par. 1 (2,5 % per gli atti dal 1.1 al 31.12.2025, Legge 20 dicembre 2024 n. 202 art. 1 c. 3); Legge 29 ottobre 1981 n. 83 art. 13 tariffa (trascrizione 1 %) -/
def p6smRegistro : TransferDuty := { name := "Imposta di registro e di trascrizione (trasferimenti di immobili)", sched := Schedule.flat 350, kinds := [.home, .realEstate, .land] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4400 Imposta di registro e di trascrizione (trasferimenti di immobili)", covers := [.transactions],
     run := fun args g prev =>
       p6smRegistro.charges g.purchases "Legge 29 ottobre 1981 n. 85 Tabella A n. 1 par. 1 (2,5 % per gli atti dal 1.1 al 31.12.2025, Legge 20 dicembre 2024 n. 202 art. 1 c. 3); Legge 29 ottobre 1981 n. 83 art. 13 tariffa (trascrizione 1 %)" }]

def absent : List Absent :=
  []

def notes : List String := ["SM 4400 Imposta di registro e di trascrizione (trasferimenti di immobili): texts updated to 3.6.2025 (lexifina/san-marino-law); the reduced registration rate applies to deeds of 2025 (L. 202/2024) (grade A)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.purchases.isEmpty || g.assets.any (·.kind.isRealEstate) then ["4100 Recurrent property tax: not modelled (grade C: not read in the P5 pass)"] else [])
  ++ (if !g.purchases.isEmpty then ["4400 the fixed 70 EUR transcription charge and the mortgage tax (0,5 %) not modelled"] else [])

#guard p6smRegistro.amount { kind := .home, price := 200000 } == 7000
#guard p6smRegistro.amount { kind := .home, price := 2000000 } == 70000
#guard p6smRegistro.amount { kind := .vehicle, price := 100000 } == 0

end SmGlobal.Property
