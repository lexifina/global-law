import R4Common.Stamp

/-! # R4Common: recurrent property tax by value bands on each holding (P5, OECD 4100; eleventh pass).

`onAnnual = true`: base = the holding's annual (rental) value less `abateBp` (holdings without an annual value are
skipped); `false`: base = its statutory value. Bands as in `bandDuty` (`marginal`: each band's rate on the part inside
it; otherwise the rate of the band the whole base falls in), nothing due at or below `nilUpTo`. Used for DJ contribution
foncière (10 / 18 / 25 % of rent less 20 %) and AO Imposto Predial on holding (0,1 % to Kz 5 m, Kz 5 000 to 6 m,
0,5 % of the excess over 5 m = marginal bands 0,1 % / 0 % / 0,5 %). -/

namespace R4
open TaxKernel TaxKernel.Global

def propertyBandBase (onAnnual : Bool) (abateBp : Int) (a : Asset) : Int :=
  if onAnnual then divR .down ((BP - abateBp) * pos a.annualValue) BP else a.statutoryValue

def propertyBandFamily (name : String) (kinds : List AssetKind) (bands : List (Int × Int)) (top : Int)
    (marginal onAnnual : Bool) (statute : String) (abateBp : Int := 0) (nilUpTo : Int := 0)
    (level : Level := .local) : Family :=
  { name := s!"4100 {name}", covers := [.propertyRecurrent],
    run := fun _ g _ =>
      (g.assets.zipIdx.filter (fun (a, _) => kinds.contains a.kind && (!onAnnual || decide (a.annualValue ≥ 0)))).map
        fun (a, i) =>
          charge .propertyRecurrent name (propertyBandBase onAnnual abateBp a) id
            (fun y => bandDuty bands top marginal nilUpTo y)
            (event := s!"asset {i + 1}") (level := level) (statute := statute) }

def tPB : CanonGlobal := { id := "x", household := { id := "x" }, assets := [{ kind := .home, value := 7000000 }, { kind := .realEstate, value := 0, annualValue := 5000000 }] }
-- AO-style marginal value bands on the home: 0,1 % x 5 m + 0 + 0,5 % x 1 m = 10 000 (= 0,5 % of the excess over 5 m).
#guard ((propertyBandFamily "t" [.home] [(5000000, 10), (6000000, 0)] 50 true false "s").run [] tPB []).map (·.due) == [10000]
-- DJ-style marginal bands on rent less 20 %: base 4 000 000 -> 112 000 + 489 600 + 40 000 = 641 600.
#guard ((propertyBandFamily "t" [.realEstate] [(1120000, 1000), (3840000, 1800)] 2500 true true "s" (abateBp := 2000)).run [] tPB []).map (·.due) == [641600]

end R4
