import TaxKernel.Global2
import R5Common

/-!
# Algeria 2025: vignette automobile (قسيمة السيارات, 5200)

Code du timbre (قانون الطابع), DGI 2025 Arabic edition (mfdgi.gov.dz `files/776/2025/2522/2025.pdf`, Wayback 2025-02-22;
`law/dz_ct2025ar.pdf`; the text layer maps digits wrongly, so pp. 42-43 were read by Arabic OCR,
`law/dz_ct2025ar_p42_43_ocr.txt`). Footnote 6 of p. 42: art. 300 re-enacted by LF 1997 art. 46 and amended by LF 2004
art. 16, LF 2016 art. 9 and **LF 2025 art. 55**: the table below is the one in force for 2025.
* art. 299: the vignette is levied on vehicles registered in Algeria; it is borne by the owner (natural or legal person).
* art. 300: annual tariff from the year the vehicle is put into circulation. Tourist cars and cars fitted as utility
  vehicles, by fiscal horsepower and age (DA):

  | power            | under 3 years | 3 to 6 years | over 6 to 10 years | over 10 years |
  |------------------|--------------:|-------------:|-------------------:|--------------:|
  | up to 6 CV       |         2 000 |        1 500 |              1 000 |           500 |
  | 7 to 9 CV        |         4 000 |        3 000 |              2 000 |         1 500 |
  | 10 CV and above  |        25 000 |       20 000 |             15 000 |        10 000 |

* art. 302: exempt include vehicles running on LPG or natural gas (and state, diplomatic, ambulance, fire, disabled
  persons' vehicles: not inputs).
* art. 303-304: paid in March; a vehicle acquired during the year pays the tariff when registered (no pro rata).
Model: `vehicleKind` "car" by `fiscalHp` and age = 2025 − `firstRegYear` (0-2: under 3 years; 3-6; 7-10; 11+).
Utility vehicles (by laden weight) and buses (by seats) of the first table: no rule (listed). **Grade A** (code read).
-/

namespace DzGlobal
open TaxKernel TaxKernel.Global

def vignetteBand (lo hi : Int) (a b c d : Int) (what : String) : VehicleTax :=
  { name := "قسيمة السيارات (vignette automobile)", kinds := ["car"], when := [(.fiscalHp, lo, hi)],
    parts := [(.age, QtyTable.ofCeilings [(2, a), (6, b), (10, c)] d)], proRata := false,
    statute := s!"Code du timbre art. 299, 300 (as amended by LF 2025 art. 55), 304: tourist cars {what}" }

def vignetteGas : VehicleTax :=
  { name := "قسيمة السيارات (vignette automobile)", kinds := ["car"], fuels := [.lpg, .cng], proRata := false,
    statute := "Code du timbre art. 302 (vehicles running on LPG or natural gas: exempt)" }

/-- exemption first (applied with `firstOnly`) -/
def vignette : List VehicleTax :=
  [vignetteGas,
   vignetteBand (-1) 6 2000 1500 1000 500 "up to 6 CV: 2 000 / 1 500 / 1 000 / 500 DA",
   vignetteBand 6 9 4000 3000 2000 1500 "7 to 9 CV: 4 000 / 3 000 / 2 000 / 1 500 DA",
   vignetteBand 9 VehicleTax.noBound 25000 20000 15000 10000 "10 CV and above: 25 000 / 20 000 / 15 000 / 10 000 DA"]

def vehicles : Family := vehicleTaxFamily "قسيمة السيارات" vignette (firstOnly := true)

def vehiclesUnsupported (g : CanonGlobal) : List String :=
  vehicleTaxUnknown "قسيمة السيارات" vignette g ++ vehicleTaxUnmatched "قسيمة السيارات" vignette g
  ++ (if g.vehicles.isEmpty then [] else
      ["vignette: age taken as 2025 − firstRegYear; exempt official, diplomatic, ambulance, fire and disabled persons' vehicles not distinguished"])

#guard (QtyTable.ofCeilings [(2, 2000), (6, 1500), (10, 1000)] 500).amount 2 == 2000
#guard (QtyTable.ofCeilings [(2, 2000), (6, 1500), (10, 1000)] 500).amount 3 == 1500
#guard (QtyTable.ofCeilings [(2, 4000), (6, 3000), (10, 2000)] 1500).amount 6 == 3000
#guard (QtyTable.ofCeilings [(2, 25000), (6, 20000), (10, 15000)] 10000).amount 11 == 10000

end DzGlobal
