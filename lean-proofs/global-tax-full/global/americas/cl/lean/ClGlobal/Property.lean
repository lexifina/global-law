import ClGlobal.Pit
import TaxKernel.Global2

/-!
# CL 2025: Property family (P5 entries) — permiso de circulación (5200); property and transfer taxes C

* Transfer, stamp and recurrent property taxes (DL 3.475 (timbres y estampillas); Ley 17.235 (impuesto territorial)): tried not read in this pass (texts not local); would unlock: the acts and the 2025 municipal rates.

**Pass 10 (2026-11-21), permiso de circulación (kernel 2.4.0 VehicleTax):** DL 3.063 texto refundido (D. 2.385/1996) art. 12 a), LeyChile `get_norma_json` idNorma 18967, idVersion 2025-07-01 (`cl/law/rentas_municipales_18967_2025-07-01.*`): "escala progresiva y acumulativa sobre su precio corriente en plaza": to 60 UTM 1 %, to 120 UTM 2 %, to 250 UTM 3 %, to 400 UTM 4 %, above 400 UTM 4,5 %; "no podrá ser, en caso alguno, inferior a media unidad tributaria mensual"; the precio corriente en plaza is the SII's January list. Grade A.

**FT review (sixth pass):** the bands and the half-UTM minimum use the UTM of January 2025 (67.429): art. 12 last paragraph ("mes anteprecedente al de vencimiento") with art. 15 N° 1 (due 31 March); the December 2025 UTM was used before.


**Pass 14 (kernel 2.6.0): first permits by the month.** DL 3.063 art. 18: a vehicle's first permit pays the tax for the months left in the year, its invoice month included; art. 12 last paragraph: at the UTM of the month before the one preceding the payment; art. 17: new vehicles at their invoice price. One rule per month of first registration in 2025 (`firstRegMonth`), UTM Nov 2024 to Oct 2025 from the SII tables (`cl/law/sii_utm2024.htm`, `sii_utm2025.htm`); the payment is taken as made in that month. The March renewal now selects vehicles first registered up to 2024; a 2025 vehicle without a month, or a vehicle without `firstRegYear`, is grade C (never guessed).


**Customs (gap pass, kernel 2.8.0 `TariffRule`)**: Ley 18.687 art. 1 inc. 1 "Fíjanse en un 6 % los derechos de aduana que deben pagarse por las mercaderías procedentes del extranjero al ser importadas al país" (as amended by Ley 19.589 art. 1 e); LeyChile version in force from 1 Nov 2013, no later version): one general rate, so the tariff is `otherBp := 600` with no lines. DL 825 art. 16 a): the IVA base is the customs value plus the duties (`dutyInVatBase`). Origins with a Chilean trade agreement are flagged (schedule not read).
-/

namespace ClGlobal.Property
open TaxKernel TaxKernel.Global AmerCommon ClGlobal

/-- DL 3.063 art. 12 last paragraph + art. 15 N° 1: the UTM of the month before the one preceding the March due date: January 2025 (SII: 67.429). -/
def utmP : Int := 67429

/-- DL 3.063 art. 12 a): marginal 1 %, 2 %, 3 %, 4 %, 4.5 % on the precio corriente en plaza (the vehicle's `value`). -/
def permisoTbl : QtyTable := { steps := [(0, 100), (60 * utmP, 200), (120 * utmP, 300), (250 * utmP, 400), (400 * utmP, 450)], den := 10000 }

def permiso : VehicleTax :=
  { name := "Impuesto por permiso de circulación", regTo := 2024, kinds := ["car", "motorcycle", "van", "pickup", "pickupSingleCab", "stationWagon"],
    parts := [(.value, permisoTbl)], minAmount := utmP / 2, level := .local, statute := "DL 3.063 (Ley de Rentas Municipales), texto refundido D. 2.385/1996 art. 12 a) (LeyChile idNorma 18967, version 2025-07-01): automobiles, station wagons, vans, pickups, motorcycles: progressive and cumulative scale on the precio corriente en plaza (SII list): to 60 UTM 1 %, to 120 UTM 2 %, to 250 UTM 3 %, to 400 UTM 4 %, above 4.5 %; at least half a UTM" }

/-- DL 3.063 art. 12 last paragraph: a first permit of month m uses the UTM of month m - 2 (SII: Nov 2024 ... Oct 2025). -/
def utmFirst : List Int := [66628, 67294, 67429, 67294, 68034, 68306, 68648, 68785, 68923, 68647, 69265, 69265]

/-- art. 12 a) scale on UTM `u`, times `n` / 12 (art. 18: the months left, the invoice month included). -/
def firstTbl (u n : Int) : QtyTable := { steps := [(0, 100 * n), (60 * u, 200 * n), (120 * u, 300 * n), (250 * u, 400 * n), (400 * u, 450 * n)], den := 120000 }

/-- First permits of 2025 by the month of first registration (art. 18, art. 12 last paragraph, art. 17). -/
def permisoFirst : List VehicleTax := (List.range 12).map fun (k : Nat) =>
  let u := utmFirst.getD k 0
  let n : Int := 12 - (k : Int)
  { permiso with
      name := s!"Impuesto por permiso de circulación (first permit, month {k + 1})", regTo := 0,
      occasion := .registration, proRata := false, «when» := [(.firstRegMonth, (k : Int), (k : Int) + 1)],
      parts := [(.value, firstTbl u n)], minAmount := u * n / 24,
      statute := s!"DL 3.063 t.r. art. 18 (first permit: {12 - k}/12 of the year), art. 12 a) and last paragraph (UTM {u} of the month before the one preceding the payment), art. 17 (invoice price)" }

def permisoTs : List VehicleTax := permiso :: permisoFirst

def permisoF : Family := vehicleTaxFamily "permiso de circulación" permisoTs

/-! ## 5123 customs import duties (kernel 2.8.0 `TariffRule`; gap pass 2026-11-21) -/

def tariff : TariffRule :=
  { name := "derechos de aduana", country := "CL", vatBp := 1900,
    lines := [],
    otherBp := 600,
    preferences := [],
    mfnIfOriginUnknown := false,
    statute := "Ley 18.687 art. 1 inc. 1 (texto vigente desde el 1 Nov 2013, LeyChile idNorma 30069): derechos de aduana 6 % ad valorem on goods from abroad (Ley 19.589 art. 1 e)); DL 825 art. 16 a): the IVA base on imports is the customs value plus the duties" }

def customsF : Family := customsFamily [tariff] "5123 customs import duties (Ley 18.687 art. 1)"

/-- Imported lines whose duty this model cannot settle (grade C lines; the MFN or preferential duty is still shown). -/
def customsFlags (g : CanonGlobal) : List String :=
  (consumptionC g).zipIdx.flatMap fun ((s, x, c), i) =>
    let hs := (hsNormalize c.hsRaw).getD ""
    if !(x.imported || c.origin != "") || tariff.isDomestic c || !tariff.takesGood s.good then [] else
    let o := if c.origin == "" then "not given" else c.origin
    let pre := s!"5120 derechos de aduana: line {i + 1} ({s.good.name}), origin {o}, hs {hs}: "
    (if ["US", "CA", "MX", "GB", "CH", "LI", "NO", "IS", "KR", "CN", "JP", "AU", "NZ", "SG", "BN", "MY", "VN", "TH", "ID", "IN", "HK", "TR", "PA", "CR", "SV", "GT", "HN", "NI", "CO", "PE", "EC", "BO", "VE", "AR", "BR", "PY", "UY", "CU", "AE", "PH", "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE"].contains c.origin then [pre ++ "Chile has a trade agreement with this origin whose tariff schedule is not read here; the 6 % MFN duty is booked and may overstate (grade C)"] else []) ++
    (if hs.startsWith "84" || hs.startsWith "85" then [pre ++ "a capital good under Ley 18.634 is duty-free (Ley 18.687 art. 1 inc. 3); household goods are taken as not capital goods (grade C)"] else [])

def customsUnknown (g : CanonGlobal) : List String := tariff.unknown g ++ customsFlags g

/-- A one-household line with the given consumption lines (for the guards). -/
def custLine (lines : String) : CanonGlobal :=
  match Lean.Json.parse ("{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"consumption\":[" ++ lines ++ "]}") with
  | .ok j => match parseGlobal j with | .ok g => g | .error _ => default
  | .error _ => default

def families : List Family := [permisoF, customsF]

def absent : List Absent :=
  [{ oecd := .wealth, why := "Not levied (convention R5-3k-G, pass 12): Constitución art. 65 inc. 4 num. 1: \"Imponer, suprimir, reducir o condonar tributos de cualquier clase o naturaleza\" (`cl/law/const_art-065.md`). no law read in this build levies a recurrent tax on net wealth (laws read include: DL 3.063 (Ley de Rentas Municipales), texto refundido D. 2.385/1996 art. 12 a) (LeyChile idNorma 18967, version 2025-07-01): automobiles, station wagons, vans, pickups, motorcycles: progressive and cumulative scale on the precio corriente en plaza (SII list): to 60 UTM 1 %, to 120 UTM 2 %, to 250 UTM 3 %, to 400 UTM 4 %, above 4.5 %)." }]

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String := ((if true then ["Transfer, stamp and recurrent property taxes: statute not reached in a dated form (grade C): not computed"] else []) ++ (if !g.vehicles.isEmpty then ["permiso de circulación: the vehicle's value taken as the SII precio corriente en plaza; UTM of January 2025 (art. 12 last paragraph: the month before the one preceding the 31 March due date of art. 15 N° 1); a first permit of 2025 (art. 18) is priced by the month of first registration (firstRegMonth: the invoice month), at the UTM of two months earlier, and the payment month is taken as that month; the March renewal reads firstRegYear (up to 2024); taxis, buses, trucks and trailers (art. 12 b), fixed UTM amounts) not computed"] else []) ++ vehicleTaxUnknown "permiso de circulación" permisoTs g ++ vehicleTaxUnmatched "permiso de circulación" permisoTs g) ++ customsUnknown g

#guard utmP == 67429
-- 10.000.000: 1 % of 4.045.740 + 2 % of 4.045.740 + 3 % of 1.908.520 = 178.627,8
#guard permiso.amount 2025 { value := 10000000 } == 178627
-- 1.000.000: 10.000, below the half UTM (33.714,5)
#guard permiso.amount 2025 { value := 1000000 } == 33714
-- 40.000.000: 40.457,4 + 80.914,8 + 3 % of 8.765.770 + 4 % of 10.114.350 + 4.5 % of 13.028.400 = 1.375.197,3
#guard permiso.amount 2025 { value := 40000000 } == 1375197
-- first permit June 2025, invoice 10.000.000: UTM April 68.306; 40.983,6 + 81.967,2 + 3 % of 1.803.280 = 177.049,2; x 7/12 = 103.278,7
#guard (permisoFirst.getD 5 permiso).amount 2025 { value := 10000000, firstRegYear := 2025, firstRegMonth := 6, newReg := true } == 103278
-- first permit January 2025, 1.000.000: 10.000 below half the November 2024 UTM (33.314), x 12/12
#guard (permisoFirst.getD 0 permiso).amount 2025 { value := 1000000, firstRegYear := 2025, firstRegMonth := 1, newReg := true } == 33314
-- first permit December 2025, 10.000.000: UTM October 69.265; 41.559 + 83.118 + 50.646 = 175.323; x 1/12 = 14.610,25
#guard (permisoFirst.getD 11 permiso).amount 2025 { value := 10000000, firstRegYear := 2025, firstRegMonth := 12, newReg := true } == 14610
#guard (permisoFirst.getD 5 permiso).computes 2025 { value := 10000000, firstRegYear := 2025, firstRegMonth := 6, newReg := true } == true
#guard (permisoFirst.getD 6 permiso).computes 2025 { value := 10000000, firstRegYear := 2025, firstRegMonth := 6, newReg := true } == false
-- a 2025 vehicle pays no March renewal; a 2024 one does
#guard permiso.computes 2025 { value := 10000000, firstRegYear := 2025, firstRegMonth := 6, newReg := true } == false
#guard permiso.computes 2025 { value := 10000000, firstRegYear := 2024 } == true
-- rice from Russia (no agreement): 11 900 / 1,19 = 10 000; / 1,06 = 9 433; 6 % = 565
#guard (tariff.charges (custLine "{\"good\":\"food\",\"amount\":11900,\"hs\":\"1006.30\",\"origin\":\"RU\"}")).map (·.due) == [565]
-- a domestic line pays nothing
#guard (tariff.charges (custLine "{\"good\":\"food\",\"amount\":11900,\"hs\":\"1006.30\",\"origin\":\"domestic\"}")).map (·.due) == []
-- rice from China: 565 booked, one grade-C line (agreement schedule not read)
#guard (customsUnknown (custLine "{\"good\":\"food\",\"amount\":11900,\"hs\":\"1006.30\",\"origin\":\"CN\"}")).length == 1
-- imported with no hs: grade C
#guard (customsUnknown (custLine "{\"good\":\"food\",\"amount\":11900,\"imported\":true}")).length == 1

end ClGlobal.Property
