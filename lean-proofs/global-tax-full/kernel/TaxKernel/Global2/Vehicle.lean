import TaxKernel.Global2.Assets
import TaxKernel.Global2.Basket
import TaxKernel.Global2.Fx

/-!
# TaxKernel.Global2.Vehicle (2.4.0, 2026-11-21; 2.5.0, 2.6.0, 2.7.0): motor-vehicle taxes from vehicle attributes (OECD 5200)

R1 Europe pass 7 (about 45 European 5200 entries; every region with an annual or registration vehicle tax): the
statutes set the tax per vehicle from CO2 g/km (UK VED, IE motor tax, FR malus), engine cm³ or kW (DE KraftStG § 9,
HR Zakon o lokalnim porezima čl. 11), fiscal horsepower (FR, R4 vignettes), mass and fuel (NL MRB), age and value.

**The vehicle record** (`Vehicle`, optional, read from the input line; `Asset` and `Company` are unchanged):
* every `assets` entry of `"kind": "vehicle"` is a vehicle, its attributes as fields of the same record (the form R4
  already uses for `fiscalHp`); its `value`, `person` and `region` are the asset's;
* a company line's `company.vehicles` entries (company entities; the form R4 uses for fleets).

| JSON field | `Vehicle` | meaning (not given: −1, or as shown) |
|---|---|---|
| `"vehicleKind"` (in `company.vehicles` also `"kind"`) | `kind` | `"car"` (default), `"motorcycle"`, `"van"`, `"truck"`, `"bus"`, … |
| `"engineCcm"` (or `"engineCc"`) | `engineCcm` | cylinder capacity, cm³ |
| `"engineKw"` | `engineKw` | engine power, kW |
| `"fiscalHp"` | `fiscalHp` | fiscal horsepower (CV, puissance administrative) |
| `"co2GKm"` | `co2GKm` | CO2 emissions, g/km (the statute's cycle) |
| `"massKg"` | `massKg` | mass, kg (the statute's mass: unladen, in running order, maximum) |
| `"fuel"` | `fuel` | `petrol diesel electric hybrid pluginHybrid lpg cng hydrogen other` (absent: `unknown`) |
| `"firstRegYear"` | `firstRegYear` | year of first registration (0: not given); age = year − it |
| `"seats"` | `seats` | seats |
| `"value"` | `value` | value (an asset's own value by default) |
| `"months"` | `months` | months of the year the vehicle is held (12) |
| `"registeredThisYear"` | `newReg` | registered in the tax year (default: `firstRegYear` = the year) |
| `"euroClass"` (2.5.0) | `euroClass`, `euroStage` | Euro emission class: a number 0-7 or a text (`"Euro 6d-TEMP"`, `"6d"`, `"5b"`); attribute `euroClass` = the class (6 for every Euro 6), `euroStage` = the sub-class in order (`euroStageOf`: 6b 62, 6c 63, 6d-TEMP 64, 6d 65, 6d-ISC-FCM 66, 6e 67, 6e-bis 68, 6e-bis-FCM 69; 5a 51, 5b 52; classes 0-4 and 7: 10 × class); a Euro 5 or 6 without its letter gives no stage |
| `"listPrice"` (2.5.0) | `listPrice` | price when new (list price), distinct from `value` (never taken from it) |
| `"firstRegMonth"` (2.6.0) | `firstRegMonth` | month of first registration, 1-12 (0: not given) |
| `"heldFrom"`, `"heldTo"` (2.7.0) | `heldFrom`, `heldTo` | first and last day of the tax year the vehicle is held (ISO `"YYYY-MM-DD"`; read only by 2.7.0 day pro rata and part windows) |
| `"firstRegDate"` (2.6.0) | `firstRegMonth`, `firstRegDay` | date of first registration, `"YYYY-MM-DD"` or `"YYYY-MM"`, **with `"firstRegYear"` of the same year** (the year is read only from `"firstRegYear"`, so a 2.5.0 model reads every record as before); gives the month when `"firstRegMonth"` is absent, and the day; a date of another year, or without `"firstRegYear"`, is not read |

**The part** (`VehicleTax`): selection (vehicle kinds, fuels, first-registration years, region, attribute ranges
`when`, the occasion: `annual` or at `registration`), then

    tax = clamp_[minAmount, maxAmount] round(fixed + Σ_parts table(attribute)) × ageFactor × multiplier) × months/12

(`parts`: one `QtyTable` per attribute, added: DE cm³ + CO2; `ageFactors` `(from age, bp)`: the highest reached;
`multiplierBp`: a local or provincial multiplier; `proRata` for annual taxes: months held / 12). A tax whose selection
matches a vehicle but needs an attribute it does not give books nothing for it; `vehicleTaxUnknown` lists it for
`unsupported` as grade C, and `vehicleTaxUnmatched` lists vehicles no tax selects (write a cited zero rule where the
statute exempts them). Charges (`vehicleTaxCharges`): one per (vehicle, tax that computes it); `firstOnly`: the first.
Base = the first part's attribute, relieved = it counted in started steps, due = the tax; event
`"vehicle <k> (<source>)"`.

**No vehicle, no change**: an entity without vehicles gets no charge (`vehicleTaxCharges_nil`), so adding the family
to a model leaves every such entity's charges and total as they were (`withVehicleFamily_charges`,
`withVehicleFamily_total`); a 1.x entity has none (`vehicles_ofCanon`).

**2.5.0 (R1 Europe pass 9)**: the emission class and the list price (two more attributes, `.euroClass`, `.euroStage`,
`.listPrice`; two more `Vehicle` fields with "not given" defaults). As every attribute, a tax that reads one of them books
nothing for a vehicle that does not give it and `vehicleTaxUnknown` lists it as grade C: a plain "Euro 6" never passes a
6d test, `value` is never read as the list price. A tax that does not read them is unchanged (`attr?_old`).

**2.6.0 (FT reviewer 6)**: when in the year the vehicle was first registered. Several 2025 charges change during the year
on the first-registration date (TZ Finance Act 2025 from 1 July 2025, FR malus barème from 1 March 2025, CL first permits
priced at the UTM of a month). The record may give `"firstRegMonth"` (1-12) or a whole `"firstRegDate"`; attributes
`.firstRegMonth` (1-12) and `.firstRegDay` (usable in `when`, e.g. `(.firstRegMonth, 6, 12)` = July to December), and a
**date window** on the tax: `regFromDate` / `regToDate` (ISO `"YYYY-MM-DD"`, both inclusive, `""` open). The vehicle's
first registration is known as a span of days (the day; else the whole month; else the whole year): a span wholly inside
the window selects, wholly outside does not, and a span across a bound is **never guessed**: the tax does not compute and
`vehicleTaxUnknown` lists the vehicle as grade C with what would decide it (`firstRegYear`, then `firstRegMonth`, then
`firstRegDay`). A window starting on the 1st of a month is decided by the month alone. A bound that is not a date selects
no vehicle. A tax without a window is exactly the 2.5.0 tax (`selects_noWindow`, `missing_noWindow`,
`computes_noWindow`); the new fields change no 2.5.0 attribute (`attr?_v25`; the year, and with it the age and
`newReg`, is read only from `"firstRegYear"`).

**2.7.0 (R1 Europe pass 15, R4-17-1)**: three opt-in options, last fields of `VehicleTax` (a tax that sets none of them is
exactly the 2.6.0 tax: `computesIn_v26`, `toChargeIn_v26`, `vehicleTaxCharges_v26`, `vehicleTaxUnknown_v26`):
* **by days held** (IS lög 39/1988 3. gr.): `proRataDays := true` charges an annual tax × days held / days of the year
  (`scaleDays`), and `dayPeriods := [("01-01", "06-30"), ("07-01", "12-31")]` charges each period an equal share of the
  year's amount by its days held (a period held whole pays its share; the whole year pays the year's amount). The days
  held run from `"heldFrom"` (else, for a vehicle registered in the tax year, its first-registration **day**, which
  needs `"firstRegYear"` = the year and the month and day; else 1 January) to `"heldTo"` (else 31 December). Not
  located (a vehicle registered this year without its day; registered this year but first registered in an earlier year
  without `"heldFrom"`; `"months"` < 12 without either date): no charge, grade C ("firstRegDay", "heldFrom" not given).
* **a part only for the first N months after first registration** (SE vägtrafikskattelag 2 kap. 9 a §: the CO2 amount
  for three years): `partWindows := [{ part := 1, months := 36 }]` multiplies part 1 (0-based, in `parts`) by the months
  of the tax year inside the window (from the month of first registration, or the month after: `fromNextMonth`) and
  inside the months held, / 12; such a part is not prorated again (the other parts are, as before). A window the
  record cannot place (no `"firstRegYear"`; no `"firstRegMonth"` and the window ends inside the year; months held < 12
  without dates while the window covers part of the year): grade C.
* **amounts in a foreign currency** (R4-17-1, ZW): `currency := "USD"` (the amounts `fixed`, `parts`, `minAmount`,
  `maxAmount` are in US$), converted at the entity's `"fxRates"` rate, else the tax's declared `fxRate` (`Fx`); no rate:
  no charge, grade C ("fxRates.USD not given"). The statute names the rate and its source.

Theorems also: `VehicleTax.yearAmount_le_max`, `yearAmount_ge_min`, `amount_full`, `amount_le_year`,
`computes_window_decided` (a computed tax never straddles its window).
-/

namespace TaxKernel.Global
open Lean TaxKernel

inductive VehicleFuel where
  | petrol | diesel | electric | hybrid | pluginHybrid | lpg | cng | hydrogen | other | unknown
  deriving Repr, DecidableEq, Inhabited, BEq

def VehicleFuel.ofString : String → VehicleFuel
  | "petrol" | "gasoline" => .petrol | "diesel" => .diesel | "electric" => .electric | "hybrid" => .hybrid
  | "pluginHybrid" => .pluginHybrid | "lpg" => .lpg | "cng" => .cng | "hydrogen" => .hydrogen | "" => .unknown
  | _ => .other

/-- A number for each fuel (the `fuel` attribute). -/
def VehicleFuel.code : VehicleFuel → Int
  | .petrol => 1 | .diesel => 2 | .electric => 3 | .hybrid => 4 | .pluginHybrid => 5 | .lpg => 6 | .cng => 7
  | .hydrogen => 8 | .other => 9 | .unknown => 0

def VehicleFuel.name : VehicleFuel → String
  | .petrol => "petrol" | .diesel => "diesel" | .electric => "electric" | .hybrid => "hybrid"
  | .pluginHybrid => "pluginHybrid" | .lpg => "lpg" | .cng => "cng" | .hydrogen => "hydrogen" | .other => "other"
  | .unknown => "unknown"

/-- The attributes a vehicle tax is keyed on. -/
inductive VehicleAttr where
  | engineCcm | engineKw | fiscalHp | co2GKm | massKg | seats | value | firstRegYear | age | fuel
  /-- 2.5.0: the Euro emission class (0-7: 6 for every Euro 6) -/
  | euroClass
  /-- 2.5.0: the Euro sub-class in order (`euroStageOf`: 6d-TEMP 64 < 6d 65 …); not given without its letter -/
  | euroStage
  /-- 2.5.0: price when new -/
  | listPrice
  /-- 2.6.0: month of first registration (1-12) -/
  | firstRegMonth
  /-- 2.6.0: day of the month of first registration (1-31) -/
  | firstRegDay
  deriving Repr, DecidableEq, Inhabited, BEq

def VehicleAttr.name : VehicleAttr → String
  | .engineCcm => "engineCcm" | .engineKw => "engineKw" | .fiscalHp => "fiscalHp" | .co2GKm => "co2GKm"
  | .massKg => "massKg" | .seats => "seats" | .value => "value" | .firstRegYear => "firstRegYear" | .age => "age"
  | .fuel => "fuel" | .euroClass => "euroClass" | .euroStage => "euroStage" | .listPrice => "listPrice"
  | .firstRegMonth => "firstRegMonth" | .firstRegDay => "firstRegDay"

/-- A vehicle of the entity (see the table above). −1 (0 for `firstRegYear`, `unknown` for `fuel`): not given. -/
structure Vehicle where
  kind : String := "car"
  engineCcm : Int := -1
  engineKw : Int := -1
  fiscalHp : Int := -1
  co2GKm : Int := -1
  massKg : Int := -1
  fuel : VehicleFuel := .unknown
  firstRegYear : Nat := 0
  seats : Int := -1
  value : Int := -1
  /-- months of the year held (1 … 12) -/
  months : Nat := 12
  /-- registered in the tax year -/
  newReg : Bool := false
  region : String := ""
  person : Nat := 0
  /-- where it was read: `"asset 3"`, `"company vehicle 1"` -/
  source : String := ""
  /-- 2.5.0: Euro emission class 0-7 (−1: not given) -/
  euroClass : Int := -1
  /-- 2.5.0: Euro sub-class code (`euroStageOf`; −1: not given) -/
  euroStage : Int := -1
  /-- 2.5.0: list price, price when new (−1: not given) -/
  listPrice : Int := -1
  /-- 2.6.0: month of first registration 1-12 (0: not given) -/
  firstRegMonth : Nat := 0
  /-- 2.6.0: day of first registration 1-31 (0: not given; only with the month) -/
  firstRegDay : Nat := 0
  /-- 2.7.0: first day of the tax year held (ISO; `""`: not given) -/
  heldFrom : String := ""
  /-- 2.7.0: last day of the tax year held (ISO; `""`: not given) -/
  heldTo : String := ""
  deriving Repr, Inhabited, BEq

/-- Days in month `m` of year `y` (2.6.0). -/
def daysInMonth (y m : Nat) : Nat :=
  if m = 2 then (if isLeapYear y then 29 else 28) else if m = 4 ∨ m = 6 ∨ m = 9 ∨ m = 11 then 30 else 31

/-- A day as one number, `y·10000 + m·100 + d` (ordered as the calendar). -/
def dayOrd (y m d : Nat) : Nat := y * 10000 + m * 100 + d

/-- `"YYYY-MM-DD"` (a real calendar day) → (y, m, d); else `none`. -/
def isoYmd? (s : String) : Option (Nat × Nat × Nat) :=
  match s.splitOn "-" with
  | [ys, ms, ds] =>
    match ys.toNat?, ms.toNat?, ds.toNat? with
    | some y, some m, some d => if 1 ≤ m ∧ m ≤ 12 ∧ 1 ≤ d ∧ d ≤ daysInMonth y m then some (y, m, d) else none
    | _, _, _ => none
  | _ => none

/-- `"firstRegDate"` of a vehicle record: (year, month, day) with 0 for a part not given (`"YYYY-MM"`: no day);
(0, 0, 0) when absent or not a date. -/
def regDateOfJson (j : Json) : Nat × Nat × Nat :=
  let s := strField j "firstRegDate"
  match isoYmd? s with
  | some ymd => ymd
  | none =>
    match s.splitOn "-" with
    | [ys, ms] => match ys.toNat?, ms.toNat? with
      | some y, some m => if 1 ≤ m ∧ m ≤ 12 then (y, m, 0) else (0, 0, 0)
      | _, _ => (0, 0, 0)
    | _ => (0, 0, 0)

/-- The Euro sub-class code of a text (2.5.0): `"Euro 6d-TEMP"`, `"6d-temp"`, `"EURO 5b"`, … (case, spaces, `-`, `_`
and the word "euro" ignored). Classes 0-4 and 7 have no letter: 10 × class; 5a 51, 5b 52; 6b 62, 6c 63, 6d-TEMP 64,
6d 65, 6d-ISC-FCM 66, 6e 67, 6e-bis 68, 6e-bis-FCM 69. −1: no sub-class named ("6", "5") or not a Euro class. -/
def euroStageOf (s : String) : Int :=
  match ((((s.toLower.replace "euro" "").replace " " "").replace "-" "").replace "_" "") with
  | "0" => 0 | "1" => 10 | "2" => 20 | "3" => 30 | "4" => 40 | "5a" => 51 | "5b" => 52 | "6b" => 62 | "6c" => 63
  | "6dtemp" => 64 | "6d" => 65 | "6discfcm" => 66 | "6e" => 67 | "6ebis" => 68 | "6ebisfcm" => 69 | "7" => 70
  | _ => -1

/-- The Euro class of a text: its stage's class, else a leading digit 0-7 ("6" → 6), else −1. -/
def euroClassOf (s : String) : Int :=
  let st := euroStageOf s
  if 0 ≤ st then st / 10 else
  match (((s.toLower.replace "euro" "").replace " " "").replace "-" "").toList.head? with
  | some ch => if '0' ≤ ch ∧ ch ≤ '7' then (ch.toNat - '0'.toNat : Nat) else -1
  | none => -1

/-- `"euroClass"` of a vehicle record: (class, stage). A number 0-7 is that class (stage 10 × class for 0-4 and 7, else
not given); a text as `euroClassOf`/`euroStageOf`; absent or anything else: (−1, −1). -/
def euroOfJson (j : Json) : Int × Int :=
  match j.getObjVal? "euroClass" with
  | .ok (.num n) =>
    let k := numToInt n
    if n.exponent = 0 ∧ 0 ≤ k ∧ k ≤ 7 then (k, if k ≤ 4 ∨ k = 7 then 10 * k else -1) else (-1, -1)
  | .ok (.str t) => (euroClassOf t, euroStageOf t)
  | _ => (-1, -1)

namespace Vehicle

/-- Read a vehicle record; `value`, `region`, `person` default to the asset's. -/
def ofJson (j : Json) (year : Nat) (kindKey : String := "vehicleKind") (value : Int := -1) (region : String := "")
    (person : Nat := 0) (source : String := "") : Vehicle :=
  let dt := regDateOfJson j
  let fr := natField j "firstRegYear"
  let dm := if fr != 0 && dt.1 == fr then dt.2.1 else 0
  let mo := natField j "firstRegMonth" 0
  let fm := if 1 ≤ mo ∧ mo ≤ 12 then mo else dm
  { firstRegMonth := fm, firstRegDay := if fm != 0 && fm == dm then dt.2.2 else 0,
    kind := strField j "vehicleKind" (strField j kindKey "car"),
    engineCcm := intField j "engineCcm" (intField j "engineCc" (-1)), engineKw := intField j "engineKw" (-1),
    fiscalHp := intField j "fiscalHp" (-1), co2GKm := intField j "co2GKm" (-1), massKg := intField j "massKg" (-1),
    fuel := VehicleFuel.ofString (strField j "fuel"), firstRegYear := fr, seats := intField j "seats" (-1),
    value := intField j "value" value, months := min 12 (natField j "months" 12),
    newReg := boolField j "registeredThisYear" (fr != 0 && fr == year), region := strField j "region" region,
    person := natField j "person" person, source, euroClass := (euroOfJson j).1, euroStage := (euroOfJson j).2,
    listPrice := intField j "listPrice" (-1), heldFrom := strField j "heldFrom", heldTo := strField j "heldTo" }

def given (x : Int) : Option Int := if 0 ≤ x then some x else none

/-- The attribute, when given (`age` = year − first registration, at least 0; `fuel`: `VehicleFuel.code`). -/
def attr? (v : Vehicle) (year : Nat) : VehicleAttr → Option Int
  | .engineCcm => given v.engineCcm
  | .engineKw => given v.engineKw
  | .fiscalHp => given v.fiscalHp
  | .co2GKm => given v.co2GKm
  | .massKg => given v.massKg
  | .seats => given v.seats
  | .value => given v.value
  | .firstRegYear => if v.firstRegYear = 0 then none else some v.firstRegYear
  | .age => if v.firstRegYear = 0 then none else some (pos ((year : Int) - v.firstRegYear))
  | .fuel => if v.fuel == .unknown then none else some v.fuel.code
  | .euroClass => given v.euroClass
  | .euroStage => given v.euroStage
  | .listPrice => given v.listPrice
  | .firstRegMonth => if 1 ≤ v.firstRegMonth ∧ v.firstRegMonth ≤ 12 then some v.firstRegMonth else none
  | .firstRegDay => if 1 ≤ v.firstRegMonth ∧ v.firstRegMonth ≤ 12 ∧ 1 ≤ v.firstRegDay ∧ v.firstRegDay ≤ 31
      then some v.firstRegDay else none

/-- 2.5.0: the new fields change no older attribute (a tax that reads none of the three new ones is unchanged). -/
theorem attr?_old (v : Vehicle) (y : Nat) (a : VehicleAttr) (h : a ≠ .euroClass ∧ a ≠ .euroStage ∧ a ≠ .listPrice)
    (e s l : Int) : ({ v with euroClass := e, euroStage := s, listPrice := l } : Vehicle).attr? y a = v.attr? y a := by
  cases a <;> simp_all [attr?]

/-- 2.6.0: the month and day change no 2.5.0 attribute. -/
theorem attr?_v25 (v : Vehicle) (y : Nat) (a : VehicleAttr) (h : a ≠ .firstRegMonth ∧ a ≠ .firstRegDay) (m d : Nat) :
    ({ v with firstRegMonth := m, firstRegDay := d } : Vehicle).attr? y a = v.attr? y a := by
  cases a <;> simp_all [attr?]

/-- 2.6.0: the days the first registration can have been on, as `dayOrd`s (the day; else the month; else the year);
`none` when the year is not given. -/
def regSpan? (v : Vehicle) : Option (Nat × Nat) :=
  let y := v.firstRegYear
  let m := v.firstRegMonth
  if y = 0 then none
  else if 1 ≤ m ∧ m ≤ 12 then
    (if 1 ≤ v.firstRegDay ∧ v.firstRegDay ≤ daysInMonth y m then some (dayOrd y m v.firstRegDay, dayOrd y m v.firstRegDay)
     else some (dayOrd y m 1, dayOrd y m (daysInMonth y m)))
  else some (dayOrd y 1 1, dayOrd y 12 31)

/-- What would narrow the span: the year, then the month, then the day. -/
def regNext (v : Vehicle) : VehicleAttr :=
  if v.firstRegYear = 0 then .firstRegYear else if 1 ≤ v.firstRegMonth ∧ v.firstRegMonth ≤ 12 then .firstRegDay
  else .firstRegMonth

end Vehicle

/-- The entity's vehicles: its assets of kind `vehicle` (attributes on the asset record), then, for a company entity,
its `company.vehicles`. -/
def CanonGlobal.vehicles (g : CanonGlobal) : List Vehicle :=
  (g.assets.zipIdx.filter fun (a, _) => a.kind == .vehicle).map (fun (a, i) =>
      Vehicle.ofJson (assetJson g i) g.year (value := a.value) (region := a.region) (person := a.person)
        (source := s!"asset {i + 1}"))
  ++ (if g.entity == .company then
        let cj := match g.raw.getObjVal? "company" with | .ok c => c | .error _ => Json.null
        (arrField cj "vehicles").toList.zipIdx.map fun (j, k) =>
          Vehicle.ofJson j g.year (kindKey := "kind") (source := s!"company vehicle {k + 1}")
      else [])

/-- A 1.x household has no vehicle. -/
theorem vehicles_ofCanon (c : Canon) : (CanonGlobal.ofCanon c).vehicles = [] := by
  simp [CanonGlobal.vehicles, CanonGlobal.ofCanon]
  intro h; exact absurd h (by decide)

/-- 2.7.0: a part of a vehicle tax that applies only during the first `months` months after the first registration
(SE vägtrafikskattelag 2 kap. 9 a §: three years). -/
structure PartWindow where
  /-- the part's position in `parts` (0-based) -/
  part : Nat
  /-- the window's length in months -/
  months : Nat
  /-- the window starts with the month after the month of first registration (default: with that month) -/
  fromNextMonth : Bool := false
  deriving Repr, Inhabited, BEq

inductive VehicleOccasion where
  /-- every year the vehicle is held (circulation tax, Kfz-Steuer, VED, motor tax) -/
  | annual
  /-- once, when it is registered in the tax year (registration tax, malus, BPM-like) -/
  | registration
  deriving Repr, DecidableEq, Inhabited, BEq

structure VehicleTax where
  name : String := "motor vehicle tax"
  oecd : Oecd := .useOfGoods
  occasion : VehicleOccasion := .annual
  /-- vehicle kinds (`[]`: any) -/
  kinds : List String := []
  /-- fuels (`[]`: any; a vehicle whose fuel is not given then lacks `fuel`) -/
  fuels : List VehicleFuel := []
  /-- first registered in `regFrom ≤ year ≤ regTo` (0: open) -/
  regFrom : Nat := 0
  regTo : Nat := 0
  /-- the vehicle's region (`""`: any) -/
  region : String := ""
  /-- attribute ranges the vehicle must be in: `(attribute, lo, hi)` for `lo < x ≤ hi`; from 2.5.0 `hi < 0`
  (`VehicleTax.noBound`, −1) means no upper bound, as `ExciseRule.maxUnitPrice` (`lo = −1` was already open below: a
  given attribute is ≥ 0) -/
  when : List (VehicleAttr × Int × Int) := []
  /-- a fixed amount -/
  fixed : Int := 0
  /-- tables, one per attribute, added -/
  parts : List (VehicleAttr × QtyTable) := []
  /-- `(from age in years, factor bp)`: the highest reached multiplies the amount (10000: none) -/
  ageFactors : List (Int × Int) := []
  /-- local or provincial multiplier, bp -/
  multiplierBp : Int := 10000
  minAmount : Int := 0
  /-- −1: no cap -/
  maxAmount : Int := -1
  /-- an annual tax for a vehicle held part of the year: × months / 12 -/
  proRata : Bool := true
  round : Rule := {}
  level : Level := .central
  statute : String := ""
  /-- 2.6.0: first registered on or after this day (ISO `"YYYY-MM-DD"`; `""`: open) -/
  regFromDate : String := ""
  /-- 2.6.0: first registered on or before this day (ISO; `""`: open) -/
  regToDate : String := ""
  /-- 2.7.0: the amounts (`fixed`, `parts`, `minAmount`, `maxAmount`) are in this currency (ISO 4217; `""`: the model's) -/
  currency : String := ""
  /-- 2.7.0: a declared rate for `currency` (the entity's `"fxRates"` wins; none: grade C without input) -/
  fxRate : Option FxRate := none
  /-- 2.7.0: an annual tax × days held / days of the year (instead of months / 12) -/
  proRataDays : Bool := false
  /-- 2.7.0: periods of the year (`("MM-DD", "MM-DD")`, inclusive), each an equal share of the year's amount, by days held -/
  dayPeriods : List (String × String) := []
  /-- 2.7.0: parts that apply only in the first months after first registration -/
  partWindows : List PartWindow := []
  deriving Repr, Inhabited

namespace VehicleTax

/-- 2.6.0: the tax has a first-registration date window. -/
def hasWindow (t : VehicleTax) : Bool := t.regFromDate != "" || t.regToDate != ""

/-- A window bound as a `dayOrd`: `""` is open (`some none`), a date is `some (some d)`, anything else `none`. -/
def windowBound (s : String) : Option (Option Nat) :=
  if s = "" then some none else (isoYmd? s).map fun (y, m, d) => some (dayOrd y m d)

/-- 2.6.0: is the first registration in the window? `some true`: every day it can have been on is inside; `some false`:
none is (or a bound is not a date); `none`: undecided (the vehicle does not say enough). No window: `some true`. -/
def window? (t : VehicleTax) (v : Vehicle) : Option Bool :=
  if !t.hasWindow then some true else
  match windowBound t.regFromDate, windowBound t.regToDate with
  | some lo, some hi =>
    match v.regSpan? with
    | none => none
    | some (a, b) =>
      let geLo (x : Nat) : Bool := match lo with | none => true | some l => decide (l ≤ x)
      let leHi (x : Nat) : Bool := match hi with | none => true | some h => decide (x ≤ h)
      if geLo a && leHi b then some true
      else if !geLo b || !leHi a then some false
      else none
  | _, _ => some false

/-- 2.6.0: what the window lacks to decide (`[]` when decided). -/
def windowMissing (t : VehicleTax) (v : Vehicle) : List VehicleAttr :=
  if (t.window? v).isNone then [v.regNext] else []

theorem window?_noWindow (t : VehicleTax) (v : Vehicle) (h : t.hasWindow = false) : t.window? v = some true := by
  simp [window?, h]

theorem windowMissing_noWindow (t : VehicleTax) (v : Vehicle) (h : t.hasWindow = false) : t.windowMissing v = [] := by
  simp [windowMissing, window?_noWindow t v h]

/-- 2.5.0: the open bound of a `when` range (−1): `(.value, 40000, noBound)` is "above 40 000". -/
def noBound : Int := -1

/-- `lo < x ≤ hi`, no upper bound when `hi < 0` (2.5.0; before, a negative `hi` selected nothing, and no table used
one: checked on every project). -/
def inRange (lo hi x : Int) : Bool := decide (lo < x) && (decide (hi < 0) || decide (x ≤ hi))

/-- A non-negative upper bound reads exactly as in 2.4.0 (the builders' large numbers give the same selection). -/
theorem inRange_bounded (lo hi x : Int) (h : 0 ≤ hi) : inRange lo hi x = (decide (lo < x) && decide (x ≤ hi)) := by
  have : decide (hi < 0) = false := by simp; omega
  simp [inRange, this]

/-- `noBound`: every value above `lo`. -/
theorem inRange_open (lo x : Int) : inRange lo noBound x = decide (lo < x) := by
  simp [inRange, noBound]

/-- The attributes the tax reads. -/
def needs (t : VehicleTax) : List VehicleAttr :=
  (t.parts.map Prod.fst ++ t.when.map Prod.fst ++ (if t.ageFactors.isEmpty then [] else [VehicleAttr.age])
    ++ (if t.regFrom == 0 && t.regTo == 0 then [] else [VehicleAttr.firstRegYear])
    ++ (if t.fuels.isEmpty then [] else [VehicleAttr.fuel])).eraseDups

/-- The needed attributes the vehicle does not give (2.5.0). -/
def missing25 (t : VehicleTax) (year : Nat) (v : Vehicle) : List VehicleAttr :=
  t.needs.filter fun a => (v.attr? year a).isNone

/-- The needed attributes the vehicle does not give; from 2.6.0 also what an undecided date window lacks. -/
def missing (t : VehicleTax) (year : Nat) (v : Vehicle) : List VehicleAttr :=
  t.missing25 year v ++ (t.windowMissing v).filter fun a => !(t.missing25 year v).contains a

theorem missing_noWindow (t : VehicleTax) (y : Nat) (v : Vehicle) (h : t.hasWindow = false) :
    t.missing y v = t.missing25 y v := by
  simp [missing, windowMissing_noWindow t v h]

/-- The 2.5.0 selection on what the vehicle gives (an attribute it does not give does not exclude it: it is
`missing`). -/
def selects25 (t : VehicleTax) (year : Nat) (v : Vehicle) : Bool :=
  (t.kinds.isEmpty || t.kinds.contains v.kind)
  && (t.fuels.isEmpty || v.fuel == .unknown || t.fuels.contains v.fuel)
  && (v.firstRegYear == 0 || ((t.regFrom == 0 || decide (t.regFrom ≤ v.firstRegYear))
        && (t.regTo == 0 || decide (v.firstRegYear ≤ t.regTo))))
  && (t.region == "" || t.region == v.region)
  && (t.occasion == .annual || v.newReg)
  && t.when.all fun (a, lo, hi) => match v.attr? year a with
      | some x => VehicleTax.inRange lo hi x
      | none => true

/-- Selection: the 2.5.0 selection and, from 2.6.0, a date window that does not exclude the vehicle (an undecided
window does not exclude it: what it lacks is `missing`). -/
def selects (t : VehicleTax) (year : Nat) (v : Vehicle) : Bool :=
  t.selects25 year v && t.window? v != some false

theorem selects_noWindow (t : VehicleTax) (y : Nat) (v : Vehicle) (h : t.hasWindow = false) :
    t.selects y v = t.selects25 y v := by
  simp [selects, window?_noWindow t v h]

/-- The tax is computed for the vehicle: selected and nothing it reads missing. -/
def computes (t : VehicleTax) (year : Nat) (v : Vehicle) : Bool := t.selects year v && (t.missing year v).isEmpty

/-- **A tax without a date window computes exactly as in 2.5.0.** -/
theorem computes_noWindow (t : VehicleTax) (y : Nat) (v : Vehicle) (h : t.hasWindow = false) :
    t.computes y v = (t.selects25 y v && (t.missing25 y v).isEmpty) := by
  simp [computes, selects_noWindow t y v h, missing_noWindow t y v h]

/-- **Never guessed**: a tax computes only on a decided window (every day the first registration can have been on lies
inside it). -/
theorem computes_window_decided (t : VehicleTax) (y : Nat) (v : Vehicle) (h : t.computes y v = true) :
    t.window? v = some true := by
  simp only [computes, selects, Bool.and_eq_true, bne_iff_ne, ne_eq, List.isEmpty_iff] at h
  obtain ⟨⟨_, hw⟩, hm⟩ := h
  cases hv : t.window? v with
  | none =>
    have hw' : t.windowMissing v = [v.regNext] := by simp [windowMissing, hv]
    simp only [missing, hw', List.append_eq_nil_iff] at hm
    obtain ⟨h1, h2⟩ := hm
    simp [h1] at h2
  | some b => cases b <;> simp_all

/-- Fixed amount + every table on its attribute. -/
def basic (t : VehicleTax) (year : Nat) (v : Vehicle) : Int :=
  t.fixed + isum (t.parts.map fun (a, tb) => tb.amount ((v.attr? year a).getD 0))

def ageBp (t : VehicleTax) (year : Nat) (v : Vehicle) : Int :=
  match v.attr? year .age with
  | some age => t.ageFactors.foldl (fun acc (f, b) => if f ≤ age then b else acc) 10000
  | none => 10000

/-- The tax for a whole year: basic × age factor × multiplier, rounded by `round`, within `[minAmount, maxAmount]`. -/
def yearAmount (t : VehicleTax) (year : Nat) (v : Vehicle) : Int :=
  let r := t.round.ofTicks (divR .down (t.basic year v * t.ageBp year v * t.multiplierBp) BP)
  let a := max r t.minAmount
  if 0 ≤ t.maxAmount then min a t.maxAmount else a

def partYear (t : VehicleTax) (v : Vehicle) : Bool := t.occasion == .annual && t.proRata && decide (v.months < 12)

/-- The tax: an annual tax for part of the year is `months / 12` of the year's amount (rounded down). -/
def amount (t : VehicleTax) (year : Nat) (v : Vehicle) : Int :=
  if t.partYear v then divR .down (t.yearAmount year v * v.months) 12 else t.yearAmount year v

/-- The first part's attribute (the statute's base), as given and as counted. -/
def shownBase (t : VehicleTax) (year : Nat) (v : Vehicle) : Int × Int :=
  match t.parts.head? with
  | some (a, tb) => let x := (v.attr? year a).getD 0; (x, tb.counted x)
  | none => (0, 0)

def toCharge (t : VehicleTax) (year : Nat) (v : Vehicle) (k : Nat) : Charge :=
  let b := t.shownBase year v
  let note := if t.partYear v then s!"; {v.months}/12 of the year" else ""
  charge t.oecd t.name b.1 (fun _ => b.2) (fun _ => t.amount year v) (event := s!"vehicle {k + 1} ({v.source})")
    (level := t.level) (statute := t.statute ++ note)

theorem yearAmount_le_max (t : VehicleTax) (y : Nat) (v : Vehicle) (h : 0 ≤ t.maxAmount) :
    t.yearAmount y v ≤ t.maxAmount := by
  simp only [yearAmount, h, ↓reduceIte]; omega

theorem yearAmount_ge_min (t : VehicleTax) (y : Nat) (v : Vehicle) (h : t.maxAmount < 0 ∨ t.minAmount ≤ t.maxAmount) :
    t.minAmount ≤ t.yearAmount y v := by
  simp only [yearAmount]; split <;> omega

/-- A vehicle held the whole year (or a registration tax) pays the year's amount. -/
theorem amount_full (t : VehicleTax) (y : Nat) (v : Vehicle) (h : v.months = 12) : t.amount y v = t.yearAmount y v := by
  simp [amount, partYear, h]

/-- Part of the year never costs more than the whole year (non-negative amount, at most 12 months). -/
theorem amount_le_year (t : VehicleTax) (y : Nat) (v : Vehicle) (h0 : 0 ≤ t.yearAmount y v) :
    t.amount y v ≤ t.yearAmount y v := by
  unfold amount
  split
  · rename_i hp
    simp only [partYear, Bool.and_eq_true, decide_eq_true_eq] at hp
    have hm : (v.months : Int) ≤ 12 := by omega
    simp only [divR]
    apply Int.ediv_le_of_le_mul (by omega)
    have : t.yearAmount y v * (v.months : Int) ≤ t.yearAmount y v * 12 := Int.mul_le_mul_of_nonneg_left hm h0
    exact this
  · omega

end VehicleTax

/-! ## 2.7.0: days held, part windows, a foreign currency -/

/-- 2.7.0: a calendar date as (year, day of its year, 0-based); `none` when it is not a calendar date. -/
def isoDay? (s : String) : Option (Nat × Nat) :=
  (isoYmd? s).map fun (y, m, d) => (y, daysBeforeMonth (isLeapYear y) m + d - 1)

/-- 2.7.0: the month (1-12) of day `d` (0-based) of `year`. -/
def monthOfDay (year : Nat) (d : Int) : Nat :=
  max 1 ((List.range 12).filter fun k => decide ((daysBeforeMonth (isLeapYear year) (k + 1) : Int) ≤ d)).length

namespace Vehicle

/-- 2.7.0: a held-from / held-to date as a day of `year` (0-based; a date of an earlier year is before the year (−1),
of a later year after it (days of the year)); `none` when it is not a date. -/
def heldDay? (year : Nat) (s : String) : Option Int :=
  (isoDay? s).map fun (y, d) => if y < year then -1 else if year < y then (daysInYear year : Int) else d

/-- 2.7.0: **the days of the tax year the vehicle is held**, `(first, last)` (0-based, inclusive; first > last: none), or
the field that would locate them. First: `"heldFrom"`; else, registered in the tax year, its first-registration day
(`firstRegYear` = the year, the month and the day); else 1 January (unless the vehicle is held fewer than 12 months and
gives no date). Last: `"heldTo"`, else 31 December. -/
def heldSpan (v : Vehicle) (year : Nat) : Except String (Int × Int) :=
  let n : Int := daysInYear year
  let first : Except String Int :=
    if v.heldFrom != "" then
      match heldDay? year v.heldFrom with
      | some d => .ok (max 0 d)
      | none => .error "heldFrom"
    else if v.newReg then
      if v.firstRegYear = year then
        if 1 ≤ v.firstRegMonth ∧ v.firstRegMonth ≤ 12 then
          (if 1 ≤ v.firstRegDay ∧ v.firstRegDay ≤ daysInMonth year v.firstRegMonth then
            .ok ((daysBeforeMonth (isLeapYear year) v.firstRegMonth + v.firstRegDay - 1 : Nat) : Int)
           else .error "firstRegDay")
        else .error "firstRegMonth"
      else .error "heldFrom"
    else if v.heldTo != "" || decide (12 ≤ v.months) then .ok 0
    else .error "heldFrom"
  let last : Except String Int :=
    if v.heldTo != "" then
      match heldDay? year v.heldTo with
      | some d => .ok (min (n - 1) d)
      | none => .error "heldTo"
    else .ok (n - 1)
  match first, last with
  | .ok a, .ok b => .ok (a, b)
  | .error e, _ => .error e
  | _, .error e => .error e

/-- 2.7.0: the months of the tax year the vehicle is held, `(first, last)` (1-12; first > last: none), when they are
located: by its dates, by 12 months held, or from its first registration in the year for `months` months. -/
def heldMonths (v : Vehicle) (year : Nat) : Except String (Option (Nat × Nat)) :=
  if v.heldFrom != "" || v.heldTo != "" then
    match v.heldSpan year with
    | .ok (a, b) => .ok (some (if b < a then (1, 0) else (monthOfDay year a, monthOfDay year b)))
    | .error e => .error e
  else if 12 ≤ v.months then .ok (some (1, 12))
  else if v.newReg ∧ v.firstRegYear = year ∧ 1 ≤ v.firstRegMonth ∧ v.firstRegMonth ≤ 12 then
    .ok (some (v.firstRegMonth, min 12 (v.firstRegMonth + v.months - 1)))
  else .ok none

end Vehicle

/-- 2.7.0: months `hs … he` of `year` inside the window of `n` months from the absolute month `s` (year × 12 + month − 1). -/
def winMonthsIn (year s n hs he : Nat) : Nat :=
  ((List.range 12).filter fun k => decide (hs ≤ k + 1) && decide (k + 1 ≤ he) && decide (s ≤ year * 12 + k)
    && decide (year * 12 + k < s + n)).length

theorem winMonthsIn_le (year s n hs he : Nat) : winMonthsIn year s n hs he ≤ 12 := by
  unfold winMonthsIn
  exact Nat.le_trans (List.length_filter_le _ _) (by simp)

namespace PartWindow

/-- The months of the window held in the tax year, for a first registration in month `m`. -/
def monthsAt (pw : PartWindow) (year : Nat) (v : Vehicle) (m : Nat) : Except String Nat :=
  let s := v.firstRegYear * 12 + (m - 1) + (if pw.fromNextMonth then 1 else 0)
  match ({ v with firstRegMonth := m } : Vehicle).heldMonths year with
  | .error e => .error e
  | .ok (some (hs, he)) => .ok (winMonthsIn year s pw.months hs he)
  | .ok none =>
    let w := winMonthsIn year s pw.months 1 12
    if w = 0 then .ok 0 else if w = 12 then .ok (min 12 v.months) else .error "heldFrom"

/-- **The months of the tax year the part applies** (inside the window and held), or what would decide them: the year of
first registration; its month, when the count depends on it (every month 1-12 is tried: the same count for all
decides). -/
def monthsIn (pw : PartWindow) (year : Nat) (v : Vehicle) : Except String Nat :=
  if v.firstRegYear = 0 then .error "firstRegYear"
  else if 1 ≤ v.firstRegMonth ∧ v.firstRegMonth ≤ 12 then pw.monthsAt year v v.firstRegMonth
  else
    match (List.range 12).map (fun k => pw.monthsAt year v (k + 1)) with
    | .ok w :: rest => if rest.all (fun e => match e with | .ok x => x == w | .error _ => false) then .ok w
                       else .error "firstRegMonth"
    | _ => .error "firstRegMonth"

end PartWindow

namespace VehicleTax

/-- 2.7.0: the tax uses a 2.7.0 option. -/
def uses27 (t : VehicleTax) : Bool :=
  t.currency != "" || t.proRataDays || !t.dayPeriods.isEmpty || !t.partWindows.isEmpty

/-- The window of part `i`, if any. -/
def windowOf (t : VehicleTax) (i : Nat) : Option PartWindow := t.partWindows.find? (·.part == i)

/-- The parts without a window. -/
def plainParts (t : VehicleTax) : List (VehicleAttr × QtyTable) :=
  (t.parts.zipIdx.filter fun (_, i) => (t.windowOf i).isNone).map (·.1)

/-- The parts with a window. -/
def windowParts (t : VehicleTax) : List (VehicleAttr × QtyTable × PartWindow) :=
  t.parts.zipIdx.filterMap fun ((a, tb), i) => (t.windowOf i).map fun pw => (a, tb, pw)

theorem plainParts_noWindows (t : VehicleTax) (h : t.partWindows = []) : t.plainParts = t.parts := by
  simp only [plainParts, windowOf, h, List.find?_nil, Option.isNone_none]
  rw [List.filter_eq_self.mpr (fun _ _ => rfl)]; simp

/-- The year's amount with every money amount × `num / den` (one rounding, as `yearAmount`). -/
def yearAmountAt (t : VehicleTax) (year : Nat) (v : Vehicle) (num den : Int) : Int :=
  let r := t.round.ofTicks (divR .down (t.basic year v * t.ageBp year v * t.multiplierBp * num) (BP * den))
  let a := max r (divR .down (t.minAmount * num) den)
  if 0 ≤ t.maxAmount then min a (divR .down (t.maxAmount * num) den) else a

/-- At `1/1`, the 2.6.0 year's amount. -/
theorem yearAmountAt_one (t : VehicleTax) (y : Nat) (v : Vehicle) : t.yearAmountAt y v 1 1 = t.yearAmount y v := by
  simp [yearAmountAt, yearAmount, divR]

/-- The periods as days of `year` (0-based, inclusive); `none` if one is not `"MM-DD"` of a calendar day or ends before
it starts. -/
def periodSpans (t : VehicleTax) (year : Nat) : Option (List (Int × Int)) :=
  let pd (s : String) : Option Int := (isoDay? s!"{year}-{s}").map fun (_, d) => (d : Int)
  t.dayPeriods.mapM fun (a, b) =>
    match pd a, pd b with
    | some x, some y => if x ≤ y then some (x, y) else none
    | _, _ => none

/-- Days of `(a, b)` inside `(p, q)`. -/
def overlap (a b p q : Int) : Int := pos (min b q - max a p + 1)

/-- Each period an equal share of `y`, by its days held; every period held whole: `y`. -/
def periodsAmount (y a b : Int) (ps : List (Int × Int)) : Int :=
  if ps.all (fun (p, q) => overlap a b p q == q - p + 1) then y
  else isum (ps.map fun (p, q) => divR .down (y * overlap a b p q) ((ps.length : Int) * (q - p + 1)))

theorem periodsAmount_full (y a b : Int) (ps : List (Int × Int))
    (h : ps.all (fun (p, q) => overlap a b p q == q - p + 1) = true) : periodsAmount y a b ps = y := by
  simp [periodsAmount, h]

/-- **The year's amount for the part of the year held**: a registration tax, or an annual tax without day options: as
2.6.0 (× months / 12 for part of a year); `proRataDays`: × days held / days of the year; `dayPeriods`: by period. With
the note for the statute. -/
def prorated (t : VehicleTax) (year : Nat) (v : Vehicle) (y : Int) : Except String (Int × String) :=
  if t.occasion != .annual || (t.dayPeriods.isEmpty && !t.proRataDays) then
    .ok (if t.partYear v then (divR .down (y * v.months) 12, s!"; {v.months}/12 of the year") else (y, ""))
  else
    match v.heldSpan year with
    | .error e => .error e
    | .ok (a, b) =>
      let n := daysInYear year
      if t.dayPeriods.isEmpty then
        let d := (pos (b - a + 1)).toNat
        .ok (scaleDays y d n, if d = n then "" else s!"; {d}/{n} days of the year")
      else
        match t.periodSpans year with
        | none => .error "dayPeriods (\"MM-DD\")"
        | some ps =>
          let parts := ps.map fun (p, q) => s!"{overlap a b p q}/{q - p + 1}"
          .ok (periodsAmount y a b ps, s!"; days held by period {", ".intercalate parts}")

/-- The windowed parts, each × its months / 12, × age factor × multiplier × `num / den`, rounded by `round`. -/
def windowAmountAt (t : VehicleTax) (year : Nat) (v : Vehicle) (num den : Int) : Except String (Int × String) :=
  match t.windowParts.mapM (fun (a, tb, pw) => (pw.monthsIn year v).map fun w => (tb.amount ((v.attr? year a).getD 0), w, pw)) with
  | .error e => .error e
  | .ok [] => .ok (0, "")
  | .ok xs =>
    let s := isum (xs.map fun (x, w, _) => x * (w : Int))
    let amt := t.round.ofTicks (divR .down (s * t.ageBp year v * t.multiplierBp * num) (12 * BP * den))
    .ok (amt, String.join (xs.map fun (_, w, pw) => s!"; part {pw.part + 1}: {w}/12 (first {pw.months} months)"))

/-- The rate the tax's amounts are converted at: `(1, 1)` in the model's currency; `none`: amounts in a currency with no
rate (grade C). -/
def fxOf (t : VehicleTax) (g : CanonGlobal) : Option (Int × Int × String) :=
  if t.currency = "" then some (1, 1, "")
  else (fxFor g t.currency t.fxRate).map fun r => (r.num, r.den, "; " ++ r.note)

/-- **The 2.7.0 amount** and its statute note, or the first field that is missing. -/
def amountIn (t : VehicleTax) (g : CanonGlobal) (v : Vehicle) : Except String (Int × String) :=
  match t.fxOf g with
  | none => .error s!"fxRates.{t.currency}"
  | some (num, den, fxNote) =>
    let tp : VehicleTax := { t with parts := t.plainParts }
    match tp.prorated g.year v (tp.yearAmountAt g.year v num den), t.windowAmountAt g.year v num den with
    | .ok (a, n1), .ok (w, n2) => .ok (a + w, n1 ++ n2 ++ fxNote)
    | .error e, _ => .error e
    | _, .error e => .error e

/-- What the 2.7.0 options lack for the vehicle (`[]`: nothing; a 2.6.0 tax: always `[]`). -/
def lacks27 (t : VehicleTax) (g : CanonGlobal) (v : Vehicle) : List String :=
  if !t.uses27 then [] else
  let errs : List (Except String (Int × String)) :=
    [match t.fxOf g with | none => .error s!"fxRates.{t.currency}" | some _ => .ok (0, ""),
     t.prorated g.year v 0, t.windowAmountAt g.year v 1 1]
  (errs.filterMap fun e => match e with | .error s => some s | .ok _ => none).eraseDups

/-- 2.7.0: the tax is computed for the vehicle of entity `g`: as 2.6.0, and nothing a 2.7.0 option needs is missing. -/
def computesIn (t : VehicleTax) (g : CanonGlobal) (v : Vehicle) : Bool := t.computes g.year v && (t.lacks27 g v).isEmpty

/-- The charge (2.7.0 amount and note; a 2.6.0 tax: `toCharge`). -/
def toChargeIn (t : VehicleTax) (g : CanonGlobal) (v : Vehicle) (k : Nat) : Charge :=
  if !t.uses27 then t.toCharge g.year v k else
  let b := t.shownBase g.year v
  let an : Int × String := match t.amountIn g v with | .ok x => x | .error _ => (0, "")
  charge t.oecd t.name b.1 (fun _ => b.2) (fun _ => an.1) (event := s!"vehicle {k + 1} ({v.source})")
    (level := t.level) (statute := t.statute ++ an.2)

theorem lacks27_v26 (t : VehicleTax) (g : CanonGlobal) (v : Vehicle) (h : t.uses27 = false) : t.lacks27 g v = [] := by
  simp [lacks27, h]

/-- **A tax without a 2.7.0 option computes as in 2.6.0.** -/
theorem computesIn_v26 (t : VehicleTax) (g : CanonGlobal) (v : Vehicle) (h : t.uses27 = false) :
    t.computesIn g v = t.computes g.year v := by
  simp [computesIn, lacks27_v26 t g v h]

/-- **… and books the 2.6.0 charge.** -/
theorem toChargeIn_v26 (t : VehicleTax) (g : CanonGlobal) (v : Vehicle) (k : Nat) (h : t.uses27 = false) :
    t.toChargeIn g v k = t.toCharge g.year v k := by
  simp [toChargeIn, h]

/-- **Never a rate of its own**: a tax in a foreign currency computes only with a declared rate (the entity's or the
rule's). -/
theorem computesIn_fx (t : VehicleTax) (g : CanonGlobal) (v : Vehicle) (hc : t.currency ≠ "")
    (h : t.computesIn g v = true) : (fxFor g t.currency t.fxRate).isSome = true := by
  have hu : t.uses27 = true := by simp [uses27, hc]
  cases hf : fxFor g t.currency t.fxRate with
  | some r => rfl
  | none =>
    have hfx : t.fxOf g = none := by simp [fxOf, hc, hf]
    simp [computesIn, lacks27, hu, hfx, List.eraseDups_cons] at h

/-- Days held never carry more than the year's amount (non-negative amount). -/
theorem scaleDays_held (y : Int) (d n : Nat) (hy : 0 ≤ y) (h : d ≤ n) : scaleDays y d n ≤ y := scaleDays_le y d n hy h

end VehicleTax

/-- One charge per (vehicle, tax that computes it), vehicles in order; `firstOnly`: only the first such tax. From 2.7.0
the 2.7.0 options are applied (`computesIn`, `toChargeIn`); a list of 2.6.0 taxes books the 2.6.0 charges
(`vehicleTaxCharges_v26`). -/
def vehicleTaxCharges (ts : List VehicleTax) (g : CanonGlobal) (firstOnly : Bool := false) : List Charge :=
  g.vehicles.zipIdx.flatMap fun (v, k) =>
    let ms := ts.filter (·.computesIn g v)
    (if firstOnly then ms.take 1 else ms).map (·.toChargeIn g v k)

/-- The 2.6.0 charges (kept to state `vehicleTaxCharges_v26`). -/
def vehicleTaxCharges26 (ts : List VehicleTax) (g : CanonGlobal) (firstOnly : Bool := false) : List Charge :=
  g.vehicles.zipIdx.flatMap fun (v, k) =>
    let ms := ts.filter (·.computes g.year v)
    (if firstOnly then ms.take 1 else ms).map (·.toCharge g.year v k)

/-- **Taxes without a 2.7.0 option book exactly the 2.6.0 charges.** -/
theorem vehicleTaxCharges_v26 (ts : List VehicleTax) (g : CanonGlobal) (fo : Bool) (h : ∀ t ∈ ts, t.uses27 = false) :
    vehicleTaxCharges ts g fo = vehicleTaxCharges26 ts g fo := by
  unfold vehicleTaxCharges vehicleTaxCharges26
  congr 1
  funext p
  have hf : ts.filter (·.computesIn g p.1) = ts.filter (·.computes g.year p.1) :=
    List.filter_congr (fun t ht => VehicleTax.computesIn_v26 t g p.1 (h t ht))
  have hm : ∀ l : List VehicleTax, (∀ t ∈ l, t ∈ ts) →
      l.map (·.toChargeIn g p.1 p.2) = l.map (·.toCharge g.year p.1 p.2) := fun l hl =>
    List.map_congr_left (fun t ht => VehicleTax.toChargeIn_v26 t g p.1 p.2 (h t (hl t ht)))
  simp only [hf]
  split
  · exact hm _ (fun t ht => (List.mem_filter.mp (List.mem_of_mem_take ht)).1)
  · exact hm _ (fun t ht => (List.mem_filter.mp ht).1)

/-- The 5200 family of a list of vehicle taxes (headings: those of the taxes). -/
def vehicleTaxFamily (name : String) (ts : List VehicleTax) (firstOnly : Bool := false) : Family :=
  { name := s!"5200 {name}", covers := (ts.map (·.oecd)).eraseDups,
    run := fun _ g _ => vehicleTaxCharges ts g firstOnly }

/-- Vehicles no tax computes although one selects them, with what they lack (for `unsupported`, grade C). -/
def vehicleTaxUnknown (name : String) (ts : List VehicleTax) (g : CanonGlobal) : List String :=
  g.vehicles.zipIdx.filterMap fun (v, k) =>
    if ts.any (·.computesIn g v) then none else
    match (ts.filter (·.selects g.year v)).head? with
    | some t => some s!"{t.oecd.code} {name}: vehicle {k + 1} ({v.source}, {v.kind}): {", ".intercalate ((t.missing g.year v).map (·.name) ++ t.lacks27 g v)} not given (grade C)"
    | none => none

/-- The 2.6.0 lines (kept to state `vehicleTaxUnknown_v26`). -/
def vehicleTaxUnknown26 (name : String) (ts : List VehicleTax) (g : CanonGlobal) : List String :=
  g.vehicles.zipIdx.filterMap fun (v, k) =>
    if ts.any (·.computes g.year v) then none else
    match (ts.filter (·.selects g.year v)).head? with
    | some t => some s!"{t.oecd.code} {name}: vehicle {k + 1} ({v.source}, {v.kind}): {", ".intercalate ((t.missing g.year v).map (·.name))} not given (grade C)"
    | none => none

/-- **Taxes without a 2.7.0 option give exactly the 2.6.0 grade-C lines.** -/
theorem vehicleTaxUnknown_v26 (name : String) (ts : List VehicleTax) (g : CanonGlobal) (h : ∀ t ∈ ts, t.uses27 = false) :
    vehicleTaxUnknown name ts g = vehicleTaxUnknown26 name ts g := by
  unfold vehicleTaxUnknown vehicleTaxUnknown26
  congr 1
  funext p
  have ha : ts.any (·.computesIn g p.1) = ts.any (·.computes g.year p.1) := by
    rw [Bool.eq_iff_iff]
    simp only [List.any_eq_true]
    constructor
    · rintro ⟨t, ht, hc⟩; exact ⟨t, ht, by rwa [VehicleTax.computesIn_v26 t g p.1 (h t ht)] at hc⟩
    · rintro ⟨t, ht, hc⟩; exact ⟨t, ht, by rwa [VehicleTax.computesIn_v26 t g p.1 (h t ht)]⟩
  simp only [ha]
  split
  · rfl
  · split
    · rename_i t ht
      have hm : t ∈ ts := (List.mem_filter.mp (List.mem_of_mem_head? ht)).1
      simp [VehicleTax.lacks27_v26 t g p.1 (h t hm)]
    · rfl

/-- Vehicles no tax selects (for `unsupported` where the statute should reach every vehicle). -/
def vehicleTaxUnmatched (name : String) (ts : List VehicleTax) (g : CanonGlobal) : List String :=
  g.vehicles.zipIdx.filterMap fun (v, k) =>
    if ts.any (·.selects g.year v) then none
    else some s!"5200 {name}: vehicle {k + 1} ({v.source}, {v.kind}, {v.fuel.name}): no rule for the vehicle (grade C)"

theorem vehicleTaxCharges_nil (ts : List VehicleTax) (g : CanonGlobal) (fo : Bool) (h : g.vehicles = []) :
    vehicleTaxCharges ts g fo = [] := by
  simp [vehicleTaxCharges, h]

/-- **An entity without vehicles is untouched by the vehicle family**: a household entity's charges are those of the
model without it. -/
theorem withVehicleFamily_charges (m : GlobalModel) (n : String) (ts : List VehicleTax) (fo : Bool) (args : List String)
    (g : CanonGlobal) (hv : g.vehicles = []) (h : (g.entity == .company) = false) :
    ((m.withFamily (vehicleTaxFamily n ts fo)).computeGlobal args g).charges = (m.computeGlobal args g).charges := by
  rw [withFamily_charges m _ args g h]
  simp [vehicleTaxFamily, vehicleTaxCharges_nil ts g fo hv]

/-- … and every entity's total (household or company). -/
theorem withVehicleFamily_total (m : GlobalModel) (n : String) (ts : List VehicleTax) (fo : Bool) (args : List String)
    (g : CanonGlobal) (hv : g.vehicles = []) :
    ((m.withFamily (vehicleTaxFamily n ts fo)).computeGlobal args g).total = (m.computeGlobal args g).total := by
  rw [withFamily_total]
  simp [vehicleTaxFamily, vehicleTaxCharges_nil ts g fo hv, isum]

end TaxKernel.Global
