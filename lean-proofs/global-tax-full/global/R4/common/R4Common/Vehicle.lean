import R4Common.Licence

/-! # R4Common: annual motor-vehicle taxes (vignette / taxe sur les véhicules à moteur) by fiscal horsepower (P7,
OECD 5200: taxes on the use of goods).

Inputs (extra fields of the input line, the kernel's `Asset` has no power): a household's `assets` entries of kind
`"vehicle"` with `fiscalHp` (puissance administrative, CV); a company's `company.vehicles` entries with `fiscalHp`.
A vehicle without `fiscalHp` is not charged (the tariff cannot be read). Companies use `company` when the statute has
a separate tariff for vehicles owned by companies, else `person`. -/

namespace R4
open TaxKernel TaxKernel.Global

/-- An annual amount by fiscal horsepower: the first band whose ceiling (inclusive) is at least the vehicle's CV. -/
structure VehTariff where
  bands : List (Int × Int) := []
  top : Int := 0
  deriving Repr, Inhabited

def VehTariff.amount (t : VehTariff) (hp : Int) : Int :=
  match t.bands.find? (fun b => hp ≤ b.1) with
  | some b => b.2
  | none => t.top

def arrOf (j : Lean.Json) (k : String) : List Lean.Json :=
  match j.getObjVal? k with
  | .ok (.arr a) => a.toList
  | _ => []

/-- The fiscal horsepower of each vehicle of the entity (household assets of kind vehicle, or company vehicles). -/
def vehicleHps (g : CanonGlobal) : List Int :=
  let xs := if g.entity == .company then arrOf (companyJson g) "vehicles"
    else (arrOf g.raw "assets").filter (fun a => strField a "kind" == "vehicle")
  (xs.map fun a => intField a "fiscalHp" (-1)).filter (· ≥ 0)

def vehicleFamily (name : String) (person : VehTariff) (company : Option VehTariff) (statute : String)
    (level : Level := .central) : Family :=
  { name := s!"5200 {name}", covers := [.useOfGoods],
    run := fun _ g _ =>
      let t := if g.entity == .company then company.getD person else person
      (vehicleHps g).zipIdx.map fun (hp, i) =>
        flatCharge .useOfGoods name (t.amount hp) (event := s!"vehicle {i + 1} ({hp} CV)") (level := level)
          (bearer := .entity) (statute := statute) (base := hp) }

def tVeh : VehTariff := { bands := [(7, 20000), (10, 30000), (15, 40000)], top := 60000 }
def tVehG : CanonGlobal := { id := "h", household := { id := "h" }, raw := (Lean.Json.parse "{\"assets\": [{\"kind\": \"vehicle\", \"value\": 1, \"fiscalHp\": 11}, {\"kind\": \"home\", \"value\": 1}, {\"kind\": \"vehicle\", \"value\": 1, \"fiscalHp\": 7}]}").toOption.getD Lean.Json.null }
#guard ((vehicleFamily "t" tVeh none "s").run [] tVehG []).map (·.due) == [40000, 20000]

end R4
