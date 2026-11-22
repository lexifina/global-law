import UsGlobal.Pit

/-!
# United States 2025: capital income and gains of households (1100), all disposals, stacked on the 1.x model

Sources: 26 U.S.C. § 1 (h), § 121, § 1222 (Cornell LII, fetched 2026-11-21; `us/law/`). § 1222: a "short-term capital
gain" is gain "from the sale or exchange of a capital asset held for not more than 1 year"; long-term above 1 year.
§ 1 (h) taxes net long-term gains at the preferential rates (the 1.x model's `capitalGains`, which holds long-term
gains); short-term gains are ordinary income: routed into the 1.x model's `interest` (taxed at the ordinary rates as
interest is: an accounting convention with the same tax). § 121 (b) (1): the gain on a principal residence "shall not
exceed $250,000" of exclusion ($500,000 on certain joint returns): $250,000 is excluded per main-home sale (upper
bound for joint filers). Grade B.
-/

namespace UsGlobal.Capital
open TaxKernel TaxKernel.Global AmerCommon UsGlobal

def homeExcl : Int := 250000
def gainAfterHome (d : Disposal) : Int := if d.mainHome && d.kind == .home then pos (d.gain - homeExcl) else d.gain
def addAll (g : CanonGlobal) : HouseholdAdd :=
  { routedAdd g with
    capitalGains := pos (isum ((g.disposals.filter fun d => decide (d.heldMonths > 12)).map gainAfterHome)),
    interest := (routedAdd g).interest + pos (isum ((g.disposals.filter fun d => decide (d.heldMonths ≤ 12)).map gainAfterHome)) }
def capF : Family :=
  { name := "1100 capital income and gains (all disposals) stacked on the 1.x model", covers := [],
    run := fun args g _ =>
      if g.entity == .company then [] else
      let a := addAll g
      let tot := a.capitalGains + a.interest + a.dividends + a.rentalIncome
      if tot == 0 then [] else
      [charge .pit "Income tax on additional capital income and gains (1.x model, stacked)" tot id
        (fun _ => stackedTax (pitOf args) g.household a) (event := "capital income") (statute := "26 U.S.C. §§ 1 (h) (long-term rates), 1222 (1 year), 121 (b) ($250,000 home exclusion); 1.x model (stackedTax)")] }

def families : List Family := [capF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String := when (g.entity != .company && !g.disposals.isEmpty) "long-term gains at the § 1 (h) rates of the 1.x model (unrecaptured § 1250 gain at 25 % and collectibles at 28 % not separated); short-term gains taxed as ordinary income via the 1.x interest field; long and short results netted separately at zero (no cross-netting, no carry-over); § 121 exclusion $250,000 per main-home sale (ownership and use tests assumed met; $500,000 joint not applied); California taxes gains as ordinary income in the 1.x model"
  ++ when (g.entity != .company && g.incomes.any fun i => i.kind != .interest && i.kind != .dividend && i.kind != .rent) "additional income items other than interest, dividends and rent: not taxed by this family"

#guard (addAll { id := "x", household := { id := "x" }, disposals := [{ kind := .realEstate, proceeds := 500, cost := 200, heldMonths := 30 }, { kind := .unlistedShares, proceeds := 300, cost := 100, heldMonths := 6 }] }).capitalGains == 300
#guard (addAll { id := "x", household := { id := "x" }, disposals := [{ kind := .unlistedShares, proceeds := 300, cost := 100, heldMonths := 6 }] }).interest == 200
#guard gainAfterHome { kind := .home, proceeds := 900000, cost := 500000, mainHome := true } == 150000
#guard (capF.run [] { id := "g", household := { id := "g" } } []).length == 0

end UsGlobal.Capital
