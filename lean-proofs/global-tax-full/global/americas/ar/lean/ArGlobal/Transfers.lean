import ArGlobal.Pit
import TaxKernel.Global2

/-!
# AR 2025: Transfers family: CABA property taxes (4100); stamp duty grade C

Source: Ley Tarifaria para el año 2025 de la Ciudad Autónoma de Buenos Aires (Ley 6.806, Anexo, IF-2024-47992374-GCABA-MHFGC; archived `ar/law/ley6806_tarifaria_2025_anexo.*`):
* **art. 43** Impuesto Inmobiliario (Código Fiscal art. 364 a)): II = CF + (VFH - lm) x al x USC; segments A 0-17,950,000 0.60 %, B to 26,600,000 CF 107,700 + 0.65 %, C to 38,000,000 CF 163,925 + 0.70 %, D to 56,000,000 0.75 %, E to 85,000,000 0.80 %, F to 136,000,000 0.85 %, G to 260,000,000 0.90 %, H to 800,000,000 1.00 %, I to 5,000,000,000 1.10 %, J above 1.20 % (the cuotas fijas are the sums of the lower segments: a marginal schedule); the 5 % of Ley 23.514 is included.
* **art. 44** Tasa Retributiva (ABL, art. 364 b)): TRS = VFH x 0.80 % x [1 + (CG x 0.5)] x USC, CG by barrio/subzone 0 to 2.00: the barrio is not an input, CG = 0 (lower bound).
* **art. 45** USC = 1.
Not applied (flagged): art. 46 caps each instalment at the previous one plus the IPCBA (+2/3/4 % by zone) and sets a $12,800 minimum per partida; Código Fiscal art. 363 exemptions. The base is the asset's statutory value (VFH when `assessed` is given). Impuesto de Sellos stays C (Código Fiscal articles not read).

**Vehicles (kernel 2.4.0):** Ley Tarifaria 2025 art. 51 a) patente on automobiles and motorcycles: marginal scale 1.60 % to 8.00 % of the valuación fiscal (cuotas fijas = sums of the lower segments), + 10 % (f), the effective rate at most 6 % of the valuation (binds above $48,655,978), minimum $8,750. The vehicle's `value` is taken as the valuación fiscal.
-/

namespace ArGlobal.Transfers
open TaxKernel TaxKernel.Global AmerCommon ArGlobal

/-- Ley Tarifaria 2025 CABA art. 43: marginal segments of the Valuación Fiscal Homogénea (whole pesos), USC = 1 (art. 45). -/
def inmob : PropertyTax :=
  { name := "Impuesto Inmobiliario (CABA)",
    sched := Schedule.ofList [(0, 60), (17950000, 65), (26600000, 70), (38000000, 75), (56000000, 80), (85000000, 85), (136000000, 90), (260000000, 100), (800000000, 110), (5000000000, 120)] }
/-- art. 44: alícuota base 0.80 %; the barrio coefficient CG (0 to 2.00, weight 0.5) is not an input: CG = 0. -/
def trs : PropertyTax := { name := "Tasa Retributiva por Alumbrado, Barrido y Limpieza (ABL, CABA)", sched := Schedule.flat 80 }
def inmobF : Family := propertyFamily "4100 impuesto inmobiliario (CABA)" inmob "Ley Tarifaria 2025 de la Ciudad Autónoma de Buenos Aires (Ley 6.806, Anexo) art. 43: II = CF + (VFH - lm) x al x USC, segments A-J 0.60 % to 1.20 % of the Valuación Fiscal Homogénea (5 % of Ley 23.514 included); art. 45: USC = 1"
def trsF : Family := propertyFamily "4100 tasa retributiva ABL (CABA)" trs "Ley Tarifaria 2025 CABA (Ley 6.806, Anexo) art. 44: TRS = VFH x 0.80 % x [1 + (CG x 0.5)] x USC; CG by barrio 0 to 2.00 (taken as 0); art. 45: USC = 1"

/-- Ley Tarifaria 2025 art. 51 a): marginal scale on the valuación fiscal (the vehicle's `value`). -/
def patTbl : QtyTable := { steps := [(0, 160), (4909680, 400), (11292480, 450), (17675280, 550), (24058080, 650), (33145200, 700), (48116160, 800)], den := 10000 }
/-- f) +10 %; the 6 % cap on the effective rate binds above $48,655,978 (1.1 x scale = 6 % of value there). -/
def patCap : Int := 48655978
def patA : VehicleTax := { name := "Patente sobre vehículos (CABA)", kinds := ["car", "motorcycle"], «when» := [(.value, -1, patCap)], parts := [(.value, patTbl)], multiplierBp := 11000, minAmount := 8750, level := .local, statute := "Ley Tarifaria 2025 CABA (Ley 6.806, Anexo) art. 51 a): automobiles, motorcycles and the like, on the valuación fiscal (Código Fiscal art. 414 table): to $4,909,680 1.60 %, CF 78,555 + 4.00 % to $11,292,480, ... CF 2,610,777 + 8.00 % above $48,116,160; f) + 10 %; effective rate at most 6 % of the valuation; minimum $8,750 a year" }
def patB : VehicleTax := { name := "Patente sobre vehículos (CABA, 6 % cap)", kinds := ["car", "motorcycle"], «when» := [(.value, patCap, 1000000000000000)], parts := [(.value, QtyTable.perUnit 600 10000)], level := .local, statute := "Ley Tarifaria 2025 CABA (Ley 6.806, Anexo) art. 51 a): automobiles, motorcycles and the like, on the valuación fiscal (Código Fiscal art. 414 table): to $4,909,680 1.60 %, CF 78,555 + 4.00 % to $11,292,480, ... CF 2,610,777 + 8.00 % above $48,116,160; f) + 10 %; effective rate at most 6 % of the valuation; minimum $8,750 a year" }
def patTs : List VehicleTax := [patA, patB]
def patF : Family := vehicleTaxFamily "patentes sobre vehículos (CABA)" patTs

def families : List Family := [inmobF, trsF, patF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String := (if g.assets.any (·.kind.isRealEstate) then ["CABA inmobiliario and ABL on each real-estate asset at its statutory value (the VFH where `assessed` is given, else market value), every property taken as in CABA; ABL barrio coefficient taken as 0 (lower bound: up to x2); art. 46 instalment cap (previous instalment + IPCBA, plus 2/3/4 % by zone) and the $12,800 minimum per partida not applied; exemptions (Código Fiscal art. 363: jubilados, single homes up to $205,332,000 VFH and others) not applied"] else []) ++ (if !g.purchases.isEmpty then ["Impuesto de Sellos (CABA) on real-estate transfers not computed (grade C): Ley Tarifaria 2025 arts. 31, 35 read (1 %, 3.5 % for Código Fiscal arts. 323-325, 332), the Código Fiscal articles not read"] else []) ++ (if !g.vehicles.isEmpty then ["patentes (CABA): every vehicle taken as radicado in CABA; the vehicle's value taken as the art. 414 valuación fiscal; the 6 % cap read as on the amount with the 10 % increment; trucks, buses, taxis and machinery (b-e) not computed"] else []) ++ vehicleTaxUnknown "patentes sobre vehículos (CABA)" patTs g ++ vehicleTaxUnmatched "patentes sobre vehículos (CABA)" patTs g

#guard inmob.amount { kind := .home, value := 17950000 } == 107700
#guard inmob.amount { kind := .home, value := 26600000 } == 163925
#guard inmob.amount { kind := .home, value := 260000000 } == 2160225
#guard inmob.amount { kind := .home, value := 6000000000 } == 53760225 + 12000000
#guard trs.amount { kind := .home, value := 100000000 } == 800000
#guard inmob.amount { kind := .deposits, value := 100000000 } == 0
#guard patTbl.amount 1000000 == 16000
#guard patA.amount 2025 { value := 1000000 } == 17600
#guard patA.amount 2025 { value := 100000 } == 8750
#guard patB.amount 2025 { value := 100000000 } == 6000000

end ArGlobal.Transfers
