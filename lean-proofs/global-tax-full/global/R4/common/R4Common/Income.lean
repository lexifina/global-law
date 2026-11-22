import R4Common.Stamp

/-! # R4Common: schedular taxes on household income by a marginal tariff (P3, OECD 1100).

`incomeBandFamily`: a final tax on each extra domestic income item of one kind, after a flat abatement (`abateBp`,
e.g. BF IRF art. 125: 50 % of gross rent), by a marginal tariff (`bands` = (upper bound, rate bp), `top` above) applied
per period (nothing is due when the per-period net amount is below `exemptBelow`): `periods` = 12 applies the bands to a twelfth of the annual net amount and multiplies the monthly tax by 12
(BF IRF: bands on the rent "of the month"); `periods` = 1: annual bands. -/

namespace R4
open TaxKernel TaxKernel.Global

def incomeBandTax (abateBp : Int) (bands : List (Int × Int)) (top periods y : Int) (exemptBelow : Int := 0) : Int :=
  let net := divR .down ((BP - abateBp) * pos y) BP
  let p := max 1 periods
  if divR .down net p < exemptBelow then 0 else
  p * divR .down (bandTicks bands top 0 (divR .down net p)) BP

def incomeBandFamily (kind : IncomeKind) (name : String) (abateBp : Int) (bands : List (Int × Int)) (top periods : Int)
    (statute : String) (exemptBelow : Int := 0) : Family :=
  { name := s!"1100 {name}", covers := [],
    run := fun _ g _ =>
      if g.entity == .company then [] else
      (g.incomes.zipIdx.filter (fun (x, _) => x.kind == kind && !x.foreign)).map fun (x, i) =>
        charge .pit name x.amount id (fun y => incomeBandTax abateBp bands top periods y exemptBelow)
          (event := s!"income {i + 1} ({kind.name})") (statute := statute) }

-- 2 400 000 a year, 50 % abatement: 100 000 a month at 18 % = 18 000 × 12; 4 800 000: 18 000 + 100 000 × 25 % a month.
#guard incomeBandTax 5000 [(100000, 1800)] 2500 12 2400000 == 216000
#guard incomeBandTax 5000 [(100000, 1800)] 2500 12 4800000 == 12 * (18000 + 25000)
#guard incomeBandTax 0 [(100000, 1000)] 2000 1 300000 == 10000 + 40000
-- GA TSIL: 15 % of gross rent, nil when the monthly rent is below 200 000.
#guard incomeBandTax 0 [] 1500 12 2388000 200000 == 0
#guard incomeBandTax 0 [] 1500 12 2400000 200000 == 360000
#guard ((incomeBandFamily .rent "t" 5000 [(100000, 1800)] 2500 12 "s").run []
  { id := "x", household := { id := "x" }, incomes := [{ kind := .rent, amount := 2400000 }] } []).map (·.due) == [216000]

/-- A recurrent property tax at a flat rate on the annual (rental) value of each built holding of the listed kinds
(e.g. ML taxe foncière 3 %, the owner-occupied home exempt: kinds = [.realEstate]). Holdings without an annual value
are skipped. `abateBp`: a flat deduction from the annual value before the rate (CF CFPB art. 170: 40 %); `floor`: a
minimum duty per holding (CF art. 177: 30 000 F). -/
def propertyAnnualTax (rateBp abateBp floor x : Int) : Int :=
  max floor (divR .down (rateBp * divR .down ((BP - abateBp) * pos x) BP) BP)

def propertyAnnualFamily (name : String) (rateBp : Int) (kinds : List AssetKind) (statute : String) (level : Level := .local)
    (abateBp : Int := 0) (floor : Int := 0) : Family :=
  { name := s!"4100 {name}", covers := [.propertyRecurrent],
    run := fun _ g _ =>
      (g.assets.zipIdx.filter (fun (a, _) => kinds.contains a.kind && decide (a.annualValue ≥ 0))).map fun (a, i) =>
        charge .propertyRecurrent name a.annualValue id (fun x => propertyAnnualTax rateBp abateBp floor x)
          (event := s!"asset {i + 1}") (level := level) (statute := statute) }

def tPA : CanonGlobal := { id := "x", household := { id := "x" }, assets := [{ kind := .home, value := 0, annualValue := 500000 }, { kind := .realEstate, value := 0, annualValue := 1000000 }] }
#guard ((propertyAnnualFamily "t" 300 [.realEstate] "s").run [] tPA []).map (·.due) == [30000]
#guard ((propertyAnnualFamily "t" 1500 [.realEstate] "s" (abateBp := 4000) (floor := 30000)).run [] tPA []).map (·.due) == [90000]

#guard propertyAnnualTax 1500 4000 30000 1000000 == 90000
#guard propertyAnnualTax 1500 4000 30000 100000 == 30000

/-- A fixed amount by value band on each purchase of the listed kinds (stamp duties with a tariff in money, e.g. CM
droit de timbre gradué art. 586: 25 000 F up to 1 M ... 400 000 F above 500 M): the amount of the first band whose
ceiling (inclusive) is at least the higher of price and assessed value, else `top`. -/
def fixedBandAmount (bands : List (Int × Int)) (top v : Int) : Int :=
  match bands.find? (fun b => v ≤ b.1) with
  | some b => b.2
  | none => top

def purchaseFixedBandFamily (name : String) (kinds : List AssetKind) (bands : List (Int × Int)) (top : Int)
    (statute : String) (level : Level := .central) : Family :=
  { name := s!"4400 {name}", covers := [.transactions],
    run := fun _ g _ =>
      (g.purchases.zipIdx.filter (fun (p, _) => kinds.contains p.kind)).map fun (p, i) =>
        charge .transactions name (max p.price p.assessed) id (fun y => fixedBandAmount bands top y)
          (event := s!"purchase {i + 1}") (level := level) (statute := statute) }

#guard fixedBandAmount [(1000000, 25000), (20000000, 50000)] 400000 1000000 == 25000
#guard fixedBandAmount [(1000000, 25000), (20000000, 50000)] 400000 1000001 == 50000
#guard fixedBandAmount [(1000000, 25000), (20000000, 50000)] 400000 900000000 == 400000

end R4
