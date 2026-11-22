import TaxKernel.Global2
import R5Common

/-!
# Morocco 2025: taxe spéciale annuelle sur les véhicules (vignette, 5200)

Code général des impôts, DGI 2025 edition (`law/cgi2025fr.txt`), Livre III Titre II:
* art. 259: vehicles registered in Morocco circulating on public roads (motorcycles and agricultural vehicles excluded);
* art. 260-15° (LF 73-16): electric and hybrid (electric and thermal) vehicles exempt; 260-3° taxis exempt;
* art. 262-I-A (LF 22-12, from 1/1/2013): vehicles up to 3 000 kg total laden weight (and non-professional 4x4 of any
  weight), by fiscal horsepower: petrol below 8 CV **350 DH**, 8 to 10 CV **650 DH**, 11 to 14 CV **3 000 DH**, 15 CV and
  above **8 000 DH**; diesel **700 / 1 500 / 6 000 / 20 000 DH**; diesel pick-ups of natural persons at the petrol tariff;
* art. 261-I, 262-II: a vehicle put into circulation during the year owes 1/12 per month remaining (part month = month).
Model: cars (`vehicleKind` "car") by `fiscalHp` and `fuel`; held `months` of the year pro rata (kernel `proRata`).
Weight-based tariffs (262-I-B, C: above 3 000 kg) and LPG or other fuels: no rule (listed). **Grade A** (code text read).
-/

namespace MaGlobal
open TaxKernel TaxKernel.Global

def tsavaPetrol : VehicleTax :=
  { name := "taxe spéciale annuelle sur les véhicules", kinds := ["car"], fuels := [.petrol],
    parts := [(.fiscalHp, QtyTable.ofCeilings [(7, 350), (10, 650), (14, 3000)] 8000)],
    statute := "CGI art. 259, 262-I-A (essence: 350 / 650 / 3 000 / 8 000 DH), 262-II" }

def tsavaDiesel : VehicleTax :=
  { name := "taxe spéciale annuelle sur les véhicules", kinds := ["car"], fuels := [.diesel],
    parts := [(.fiscalHp, QtyTable.ofCeilings [(7, 700), (10, 1500), (14, 6000)] 20000)],
    statute := "CGI art. 259, 262-I-A (gasoil: 700 / 1 500 / 6 000 / 20 000 DH), 262-II" }

def tsavaExempt : VehicleTax :=
  { name := "taxe spéciale annuelle sur les véhicules", kinds := ["car"], fuels := [.electric, .hybrid, .pluginHybrid],
    statute := "CGI art. 260-15° (électriques et hybrides exonérés)" }

def tsava : List VehicleTax := [tsavaPetrol, tsavaDiesel, tsavaExempt]

def vehicles : Family := vehicleTaxFamily "taxe spéciale annuelle sur les véhicules" tsava

def vehiclesUnsupported (g : CanonGlobal) : List String :=
  vehicleTaxUnknown "taxe spéciale annuelle sur les véhicules" tsava g
  ++ vehicleTaxUnmatched "taxe spéciale annuelle sur les véhicules" tsava g
  ++ (if g.vehicles.isEmpty then [] else
      ["vignette: cars taken as up to 3 000 kg (262-I-A); diesel pick-ups of natural persons (petrol tariff) and taxis (exempt) not distinguished"])

#guard (QtyTable.ofCeilings [(7, 350), (10, 650), (14, 3000)] 8000).amount 7 == 350
#guard (QtyTable.ofCeilings [(7, 350), (10, 650), (14, 3000)] 8000).amount 8 == 650
#guard (QtyTable.ofCeilings [(7, 700), (10, 1500), (14, 6000)] 20000).amount 15 == 20000

end MaGlobal
