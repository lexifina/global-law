import R4Common.Vehicle

/-! # R4Common: stamp / transfer duties on conveyances by value bands (P5/P7, OECD 4400).

`marginal = true`: each band's rate on the part of the value inside it (TZ Cap. 189 Sch. item 22); `false`: the rate of
the band the whole value falls in applies to the whole value (GH Act 689 Sch. 1). Nothing is due when the value is at
most `nilUpTo`. Rates in basis points; base = the higher of price and assessed value. -/

namespace R4
open TaxKernel TaxKernel.Global

def bandDuty (bands : List (Int × Int)) (top : Int) (marginal : Bool) (nilUpTo v : Int) : Int :=
  if v ≤ nilUpTo then 0
  else if marginal then divR .down (bandTicks bands top 0 v) BP
  else
    let r := ((bands.find? (fun b => v ≤ b.1)).map (·.2)).getD top
    divR .down (r * pos v) BP

def transferBandFamily (name : String) (kinds : List AssetKind) (bands : List (Int × Int)) (top : Int)
    (marginal : Bool) (nilUpTo : Int) (statute : String) (level : Level := .central) : Family :=
  { name := s!"4400 {name}", covers := [.transactions],
    run := fun _ g _ =>
      (g.purchases.zipIdx.filter (fun (p, _) => kinds.contains p.kind)).map fun (p, i) =>
        charge .transactions name (max p.price p.assessed) id (fun y => bandDuty bands top marginal nilUpTo y)
          (event := s!"purchase {i + 1}") (level := level) (statute := statute) }

#guard bandDuty [(100000, 50)] 100 true 20000 1000000 == 500 + 9000
#guard bandDuty [(100000, 50)] 100 true 20000 20000 == 0
#guard bandDuty [(10000, 25), (50000, 50)] 100 false 0 60000 == 600
#guard bandDuty [(10000, 25), (50000, 50)] 100 false 0 50000 == 250

/-- A recurrent property tax at a flat rate on the statutory value (declared / assessed, else market value) of each
holding of the listed kinds (e.g. CM taxe sur la propriété foncière, 0,1 % of the value of land and buildings). -/
def propertyValueFamily (name : String) (rateBp : Int) (kinds : List AssetKind) (statute : String) (level : Level := .local)
    (den : Int := BP) : Family :=
  { name := s!"4100 {name}", covers := [.propertyRecurrent],
    run := fun _ g _ =>
      (g.assets.zipIdx.filter (fun (a, _) => kinds.contains a.kind)).map fun (a, i) =>
        charge .propertyRecurrent name a.statutoryValue id (fun x => divR .down (rateBp * pos x) den)
          (event := s!"asset {i + 1}") (level := level) (statute := statute) }

-- `den`: rates finer than a basis point (GQ IBI: 0,05 % of 30 % of the value = 15 / 100 000).
#guard ((propertyValueFamily "t" 15 [.home] "s" (den := 100000)).run [] { id := "x", household := { id := "x" }, assets := [{ kind := .home, value := 10000000 }] } []).map (·.due) == [1500]

end R4
