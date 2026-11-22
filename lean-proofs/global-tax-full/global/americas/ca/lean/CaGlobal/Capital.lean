import CaGlobal.Pit

/-!
# Canada 2025: capital income and gains of households (1100), all disposals, stacked on the 1.x model

Pass 1 routed only gains on listed shares held over 12 months into the 1.x model's `capitalGains`. Canadian law has no
holding-period or asset-class distinction: Income Tax Act s. 38 (a) (Justice Laws consolidation current to 2026-10-29,
`ca/law/I-3.3.txt`; s. 38 (a) unchanged in 2025): "a taxpayer's taxable capital gain for a taxation year from the
disposition of any property is ½ of the taxpayer's capital gain", and s. 40 (2) (b) exempts the gain on a principal
residence. So every disposal's gain (real estate, unlisted and listed shares, any holding period) except a main home
is routed into `capitalGains`, which the 1.x model includes at ½; interest, dividends and rent are routed as before.
Grade B (the 1.x model's conventions; losses netted within the year).
-/

namespace CaGlobal.Capital
open TaxKernel TaxKernel.Global AmerCommon CaGlobal

def addAll (g : CanonGlobal) : HouseholdAdd :=
  { routedAdd g with capitalGains := pos (isum ((g.disposals.filter fun d => !(d.mainHome && d.kind == .home)).map (·.gain))) }
def capF : Family :=
  { name := "1100 capital income and gains (all disposals) stacked on the 1.x model", covers := [],
    run := fun args g _ =>
      if g.entity == .company then [] else
      let a := addAll g
      let tot := a.capitalGains + a.interest + a.dividends + a.rentalIncome
      if tot == 0 then [] else
      [charge .pit "Income tax on additional capital income and gains (1.x model, stacked)" tot id
        (fun _ => stackedTax (pitOf args) g.household a) (event := "capital income") (statute := "ITA s. 38 (a) (1/2 inclusion of the gain on any property), s. 40 (2) (b) (principal residence); 1.x model (stackedTax)")] }

def families : List Family := [capF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String := when (g.entity != .company && g.disposals.any fun d => d.mainHome && d.kind == .home) "principal residence: the whole gain read as exempt (s. 40 (2) (b) formula with the designated years not applied)"
  ++ when (g.entity != .company && !g.disposals.isEmpty) "gains of the year netted against losses (no carry-over); lifetime capital gains exemption (s. 110.6) and ABIL not applied; Ontario surtax as in the 1.x model"
  ++ when (g.entity != .company && g.incomes.any fun i => i.kind != .interest && i.kind != .dividend && i.kind != .rent) "additional income items other than interest, dividends and rent: not taxed by this family"

#guard (addAll { id := "x", household := { id := "x" }, disposals := [{ kind := .realEstate, proceeds := 500, cost := 200, heldMonths := 3 }, { kind := .home, proceeds := 900, cost := 100, mainHome := true }] }).capitalGains == 300
#guard (capF.run [] { id := "g", household := { id := "g" } } []).length == 0

end CaGlobal.Capital
