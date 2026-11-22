import PeGlobal.Pit
import TaxKernel.Global2

/-!
# PE 2025: Property family — no dated statute text reached (grade C)

* Inheritance, gift and wealth taxes (none (no inheritance tax): not cited): tried not read in this pass; would unlock: the act's 2025 text.

**Pass 12 (2026-11-21), Impuesto al Patrimonio Vehicular (5200, grade B):** Decreto Legislativo 776 (Ley de Tributación
Municipal, 1993 text: Congreso PDF, scan, `pe/law/dleg776.ocr.txt`) **art. 30**: annual tax on the ownership of
"vehículos automóviles, camionetas y station wagons con una antigüedad no mayor de tres (3) años"; **art. 31**: the owner
at 1 January; **art. 32**: base "el valor original de adquisición, importación o de ingreso al patrimonio", not below the
MEF reference table; **art. 33**: "La tasa del impuesto es de 1%", "En ningún caso, el monto a pagar será inferior al
1.5% de la UIT vigente al 1 de enero". UIT 2025 S/ 5,350 (D.S. 260-2024-EF art. 1, held by the 1.x builder): minimum
S/ 80.25, booked as 80. The TUO (D.S. 156-2004-EF; D.Leg. 952 added trucks and buses) is not held, so grade B. Reading:
taxed in the three years after the year of first registration (owner at 1 January): first registered 2022-2024. The
vehicle's `value` stands for the original acquisition value (the MEF table floor not applied).

**Pass 15 (2026-11-21), net wealth (4200): not levied (A).** Not levied (convention R5-3k-G, pass 15): Constitución art. 74: "Los tributos se crean, modifican o derogan, o se establece una exoneración, exclusivamente por ley o decreto legislativo" (`pe/law/const_art-074.md`). The Impuesto Temporal a los Activos Netos (Ley 28424, Congreso text `pe/law/congreso_ley28424_itan.*`, OCR) falls on the net assets of third-category (business) income earners in the general regime (arts. 1, 2, 4), and the amount paid is a credit against the income tax's monthly advance payments and the annual settlement, refundable on a loss (art. 8): an advance income tax on businesses (heading 1200), not a tax on net wealth. Its term was extended to 2007 by Ley 28929 art. 8 (`pe/law/congreso_ley28929.*`) and D.Leg. 976 (`pe/law/congreso_dleg976.*`) set 0.4 % above S/ 1,000,000 from 2009; the later law keeping it in force and any later wording of art. 8 were not read: whichever reading holds in 2025, no tax on net wealth is levied. No law read in this build levies a recurrent tax on net wealth (laws read include: TUO Ley del IGV e ISC art. 17, Apéndices I-II; TUO Ley del IGV e ISC Título II; TUO LIR art. 55 (29,5 %); TUO LIR art. 56 a), d), e), f); 1.x model (see its summary.json); LIR TUO arts. 2, 21.1, 36, 52-A).


**4300 (gap pass 2, 2026-11-22)**: not levied (grade B): Not levied (grade B, gap pass 2, 2026-11-22): the OECD Revenue Statistics detailed table for Peru (DSD_REV_LAC@DF_REVPER v2.1, sdmx.oecd.org, fetched 2026-11-21 with a plain research user-agent, copy americas/p7t/oecd/PER.csv): general government heading 4300 (estate, inheritance and gift taxes) = 0.0 in 2021, 2022, 2023 and 2024, no 4310 or 4320 line; Interpretative Guide §52 (4300 = taxes on estates, inheritances and gifts). No estate, inheritance or gift tax is known in the national law. Peru has had no inheritance tax since its repeal in 1979 (no text held for the repeal itself). 2025 revenue statistics not yet published.
-/

namespace PeGlobal.Property
open TaxKernel TaxKernel.Global AmerCommon PeGlobal

/-- UIT 2025 (D.S. 260-2024-EF art. 1). -/
def uitV : Int := 5350

/-- D.Leg. 776 arts. 30-33: 1 % of the original value of cars, camionetas and station wagons in their first three years, at least 1.5 % of the UIT. -/
def vehicular : VehicleTax :=
  { name := "Impuesto al Patrimonio Vehicular", kinds := ["car", "pickup", "pickupSingleCab", "stationWagon", "van"],
    regFrom := 2022, regTo := 2024, parts := [(.value, { steps := [(0, 100)], den := 10000 })], minAmount := 80,
    level := .local, statute := "D.Leg. 776 (Ley de Tributación Municipal) arts. 30-33: 1 % of the original value, vehicles up to three years old, at least 1.5 % of the UIT (S/ 5,350 in 2025: 80.25)" }

def vehF : Family := vehicleTaxFamily "Impuesto al Patrimonio Vehicular" [vehicular]

def families : List Family := [vehF]

def absent : List Absent :=
  [{ oecd := .wealth, why := "Not levied (convention R5-3k-G, pass 15): Constitución art. 74: \"Los tributos se crean, modifican o derogan, o se establece una exoneración, exclusivamente por ley o decreto legislativo\" (`pe/law/const_art-074.md`). The Impuesto Temporal a los Activos Netos (Ley 28424, Congreso text `pe/law/congreso_ley28424_itan.*`, OCR) falls on the net assets of third-category (business) income earners in the general regime (arts. 1, 2, 4), and the amount paid is a credit against the income tax's monthly advance payments and the annual settlement, refundable on a loss (art. 8): an advance income tax on businesses (heading 1200), not a tax on net wealth. Its term was extended to 2007 by Ley 28929 art. 8 (`pe/law/congreso_ley28929.*`) and D.Leg. 976 (`pe/law/congreso_dleg976.*`) set 0.4 % above S/ 1,000,000 from 2009; the later law keeping it in force and any later wording of art. 8 were not read: whichever reading holds in 2025, no tax on net wealth is levied. No law read in this build levies a recurrent tax on net wealth (laws read include: TUO Ley del IGV e ISC art. 17, Apéndices I-II; TUO Ley del IGV e ISC Título II; TUO LIR art. 55 (29,5 %); TUO LIR art. 56 a), d), e), f); 1.x model (see its summary.json); LIR TUO arts. 2, 21.1, 36, 52-A)." },
   { oecd := .estate, why := "Not levied (grade B, gap pass 2, 2026-11-22): the OECD Revenue Statistics detailed table for Peru (DSD_REV_LAC@DF_REVPER v2.1, sdmx.oecd.org, fetched 2026-11-21 with a plain research user-agent, copy americas/p7t/oecd/PER.csv): general government heading 4300 (estate, inheritance and gift taxes) = 0.0 in 2021, 2022, 2023 and 2024, no 4310 or 4320 line; Interpretative Guide §52 (4300 = taxes on estates, inheritances and gifts). No estate, inheritance or gift tax is known in the national law. Peru has had no inheritance tax since its repeal in 1979 (no text held for the repeal itself). 2025 revenue statistics not yet published." }]

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String := (if !g.vehicles.isEmpty then ["Impuesto al Patrimonio Vehicular: the vehicle's value stands for the original acquisition value (MEF reference table floor not applied); taxed for vehicles first registered 2022-2024 (three years after the year of first registration, owner at 1 January); trucks and buses (D.Leg. 952) not computed; minimum 80.25 booked as 80"] else []) ++ vehicleTaxUnknown "Impuesto al Patrimonio Vehicular" [vehicular] g ++ vehicleTaxUnmatched "Impuesto al Patrimonio Vehicular" [vehicular] g

-- a car worth S/ 50,000 first registered in 2023: 1 % = 500
#guard vehicular.amount 2025 { value := 50000, firstRegYear := 2023 } == 500
-- S/ 5,000: 50, below the minimum 1.5 % x 5,350 = 80.25 -> 80
#guard vehicular.amount 2025 { value := 5000, firstRegYear := 2023 } == 80

end PeGlobal.Property
