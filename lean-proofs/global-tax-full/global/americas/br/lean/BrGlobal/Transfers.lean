import BrGlobal.Pit
import TaxKernel.Global2

/-!
# Brazil 2025 (São Paulo): IPTU (4100) and ITBI (4400)

Sources: Município de São Paulo, Legislação Municipal (legislacao.prefeitura.sp.gov.br, fetched 2026-11-21; `br/law/`):
Lei 6.989/1966 (IPTU) and Lei 11.154/1991 (ITBI), compiled texts with every wording and the amending law. Grade A for
the rates; the R$ band limits are those printed in Lei 15.889/2013 (flagged).
* **IPTU, Lei 6.989 art. 7º** (Lei 13.250/2001): "O imposto calcula-se à razão de 1,0% sobre o valor venal do imóvel,
  para imóveis utilizados exclusiva ou predominantemente como residência"; **art. 7º-A** (Lei 15.889/2013): on the
  portion of the valor venal in each band: "até R$ 150.000,00 - 0,3%; acima de R$ 150.000,00 até R$ 300.000,00 - 0,1%;
  acima de R$ 300.000,00 até R$ 600.000,00 + 0,1%; acima de R$ 600.000,00 até R$ 1.200.000,00 + 0,3%; acima de R$
  1.200.000,00 + 0,5%". Marginal rates 0.7 / 0.9 / 1.1 / 1.3 / 1.5 %.
* **art. 8º**: other built property 1,5 %; **art. 8º-A** (Lei 15.889/2013): -0,4 / -0,2 / 0,0 / +0,2 / +0,4 % on the same
  bands: 1.1 / 1.3 / 1.5 / 1.7 / 1.9 %. Land (Imposto Territorial, art. 27: 1,5 % with art. 28-A bands): not modelled.
* **ITBI, Lei 11.154 art. 10** (Lei 16.098/2014): "II - nas demais transmissões, pela alíquota de 3% (três por cento)";
  I: SFH/PAR/HIS purchases up to R$ 600.000: 0,5 % on the financed value up to R$ 100.000 and 3 % on the rest (financing
  not in the line: flagged). Base: the higher of the price and the venal value of reference (art. 7): `higherOfAssessed`.

**Pass 9 (2026-11-21), IPVA (kernel 2.4.0 vehicles):** Lei SP 13.296/2008 (ALESP updated text) art. 9 as worded by Lei 17.473/2021 (from 2022): 1.5 % trucks; 2 % buses, single-cab pickups, motorcycles, machinery; 4 % any other motor vehicle (the former 3 % for alcohol/gas/electric engines was repealed by Lei 17.293/2020); art. 7 base: the valor venal; art. 13 VIII: exempt over 20 years. The vehicle's value is taken as the valor venal; kind strings "truck", "motorcycle", "bus", "minibus", "pickupSingleCab", "machinery" select the lower rates, anything else 4 %.

**Pass 14 (kernel 2.6.0): new vehicles by the month.** Lei 13.296 art. 3 II (taxable event of a new vehicle: its first acquisition by the consumer), art. 7 II (base: the invoice value) and art. 11 with its sole paragraph (proportional to the months left in the year, the month of the event included): one rule per month of first registration in 2025 and rate class; the 1 January rules (art. 3 I) select vehicles first registered up to 2024. A vehicle without `firstRegYear`, or a 2025 vehicle without `firstRegMonth`, is grade C.
-/

namespace BrGlobal.Transfers
open TaxKernel TaxKernel.Global AmerCommon BrGlobal

/-- IPTU, residential: art. 7º 1,0 % with the art. 7º-A bands (marginal). -/
def resSched : Schedule := Schedule.ofList [(0, 70), (150000, 90), (300000, 110), (600000, 130), (1200000, 150)]
/-- IPTU, other built property: art. 8º 1,5 % with the art. 8º-A bands. -/
def otherSched : Schedule := Schedule.ofList [(0, 110), (150000, 130), (300000, 150), (600000, 170), (1200000, 190)]

def iptu : PropertyTax :=
  { name := "IPTU (São Paulo)", sched := otherSched, homeSched := some resSched, kinds := [.home, .realEstate] }
def iptuF : Family := propertyFamily "4100 IPTU São Paulo" iptu "Lei SP 6.989/1966 arts. 7º, 7º-A, 8º, 8º-A (Lei 15.889/2013)"

def itbi : TransferDuty := { name := "ITBI (São Paulo)", sched := Schedule.flat 300, higherOfAssessed := true }
def itbiF : Family := transferFamily "4400 ITBI São Paulo" [(itbi, "Lei SP 11.154/1991 art. 10 II (3 %, Lei 16.098/2014), art. 7 (valor venal de referência)", .local)]

/-- IPVA SP 2025 (Lei 13.296 art. 9, 13 VIII): the first rule that computes applies (vehicleTaxFamily firstOnly). -/
def ipvaOld : VehicleTax := { name := "IPVA (SP): over 20 years, exempt", regTo := 2004, level := .state, statute := "Lei SP 13.296/2008 art. 13 VIII: exempt, vehicles over 20 years from manufacture (first registration taken as manufacture)" }
def ipvaTruck : VehicleTax := { regTo := 2024, name := "IPVA (SP) 1.5 %", kinds := ["truck"], parts := [(.value, QtyTable.perUnit 150 10000)], level := .state, statute := "Lei SP 13.296/2008 art. 9 I (Lei 17.473/2021): 1.5 % trucks" }
def ipva2 : VehicleTax := { regTo := 2024, name := "IPVA (SP) 2 %", kinds := ["motorcycle", "bus", "minibus", "pickupSingleCab", "machinery"], parts := [(.value, QtyTable.perUnit 200 10000)], level := .state, statute := "Lei SP 13.296/2008 art. 9 II (Lei 17.473/2021): 2 %" }
def ipva4 : VehicleTax := { regTo := 2024, name := "IPVA (SP) 4 %", parts := [(.value, QtyTable.perUnit 400 10000)], level := .state, statute := "Lei SP 13.296/2008 art. 9 III (Lei 17.473/2021): 4 % any other motor vehicle" }
/-- art. 3 II-X, 7 II, 11: a vehicle first acquired in month k + 1 of 2025 pays `rateBp` x value x (12 - k) / 12. -/
def ipvaNew (t : VehicleTax) (rateBp : Int) : List VehicleTax := (List.range 12).map fun (k : Nat) =>
  { t with
      name := s!"{t.name} (first acquired in month {k + 1} of 2025: {12 - k}/12)", regTo := 0, occasion := .registration,
      proRata := false, «when» := [(.firstRegMonth, (k : Int), (k : Int) + 1)],
      parts := [(.value, QtyTable.perUnit (rateBp * (12 - (k : Int))) 120000)],
      statute := t.statute ++ s!"; art. 3 II and 11 (with sole paragraph): {12 - k}/12 of the year, the month of acquisition included; art. 7 II: invoice value" }

def ipvaTs : List VehicleTax := [ipvaOld, ipvaTruck, ipva2, ipva4] ++ ipvaNew ipvaTruck 150 ++ ipvaNew ipva2 200 ++ ipvaNew ipva4 400
def ipvaF : Family := vehicleTaxFamily "IPVA (São Paulo)" ipvaTs (firstOnly := true)

def families : List Family := [iptuF, itbiF, ipvaF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String := when (g.assets.any fun a => a.kind == .land) "Imposto Territorial Urbano on land (Lei 6.989 art. 27: 1,5 % with art. 28-A bands) not modelled"
  ++ when (g.assets.any fun a => a.kind == .home || a.kind == .realEstate) "IPTU band limits as printed in Lei 15.889/2013 (annual updates by decree, the residential exemption by venal value and the 2014+ annual increase caps not applied); valor venal = the asset's assessed value when given"
  ++ when (g.purchases.any fun p => p.firstHome) "ITBI: the SFH/PAR/HIS rate (0,5 % on the financed part up to R$ 100.000, art. 10 I) needs the financed value: 3 % charged"
  ++ when (!g.vehicles.isEmpty) "IPVA (SP): every vehicle taken as registered in São Paulo; value taken as the valor venal of art. 7; the 2025-2026 exemptions of the transitional arts. 4-5 (Lei 18.065/2024: hydrogen, natural-gas trucks and buses, ethanol hybrids up to a value) and the 1 % for rental fleets (art. 9 § 1) not applied; a vehicle first acquired in 2025 pays by the month of first registration (art. 3 II, 11), the 1 January rules read firstRegYear (up to 2024): no year, or a 2025 vehicle without a month, is grade C; a used vehicle brought from another State in 2025 (art. 3 IX, also proportional) is taken as a 1 January vehicle"
  ++ vehicleTaxUnknown "IPVA (São Paulo)" ipvaTs g

#guard iptu.amount { kind := .home, value := 500000 } == 4600
#guard iptu.amount { kind := .realEstate, value := 500000 } == 6600
#guard itbi.amount { kind := .home, price := 800000 } == 24000
#guard itbi.amount { kind := .home, price := 800000, assessed := 900000 } == 27000
#guard ipva4.amount 2025 { value := 100000 } == 4000
#guard ipva2.amount 2025 { kind := "motorcycle", value := 100000 } == 2000
#guard ipvaTruck.amount 2025 { kind := "truck", value := 100000 } == 1500
-- new car (4 %) acquired in March 2025, invoice 100.000: 4.000 x 10/12 = 3.333,3
#guard ((ipvaNew ipva4 400).getD 2 ipva4).amount 2025 { value := 100000, firstRegYear := 2025, firstRegMonth := 3, newReg := true } == 3333
-- new motorcycle (2 %) November, 30.000: 600 x 2/12 = 100
#guard ((ipvaNew ipva2 200).getD 10 ipva2).amount 2025 { kind := "motorcycle", value := 30000, firstRegYear := 2025, firstRegMonth := 11, newReg := true } == 100
-- new truck (1.5 %) July, 500.000: 7.500 x 6/12 = 3.750
#guard ((ipvaNew ipvaTruck 150).getD 6 ipvaTruck).amount 2025 { kind := "truck", value := 500000, firstRegYear := 2025, firstRegMonth := 7, newReg := true } == 3750
#guard ipva4.computes 2025 { value := 100000, firstRegYear := 2025, firstRegMonth := 3, newReg := true } == false
#guard ipva4.computes 2025 { value := 100000, firstRegYear := 2020 } == true
#guard (ipvaTs.filter (·.computes 2025 { value := 100000, firstRegYear := 2025, firstRegMonth := 3, newReg := true })).length == 1
#guard (ipvaTs.filter (·.computes 2025 { value := 100000, firstRegYear := 2025, newReg := true })).isEmpty

end BrGlobal.Transfers
