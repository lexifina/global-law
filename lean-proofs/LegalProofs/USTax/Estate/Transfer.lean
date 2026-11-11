import LegalProofs.USTax.Estate.Rates

/-!
# The gift tax, the estate tax, portability and the GST tax

## Gift tax (§§2501–2505)

* §2503(a)–(b): a year's taxable gifts are its gifts less the annual exclusion for each donee's present interests, less
  the deductions. A gift to a spouse who is a US citizen is deducted in full (§2523(a)), as is a gift to charity
  (§2522(a)). Gifts of future interests get no exclusion. Here each `Gift` is the *year's total* to one donee.
* §2513 gift splitting: each spouse reports half of every gift to a third party (`split`).
* §2502(a): the tax for a year is the tentative tax on all taxable gifts to date less the tentative tax on the prior
  years' gifts, both at the current year's rates.
* §2505(a): against it, the applicable credit amount (on the basic exclusion plus any DSUE) less the credits allowable
  for all prior periods, recomputed at the current year's rates. `schedule` is the Form 709 Schedule B worksheet
  (columns B–N) that does this recomputation period by period.

## Estate tax (§§2001, 2010, 2051–2058)

* Taxable estate (§2051) = gross estate less expenses, debts and claims (§2053), casualty losses (§2054), the
  charitable deduction (§2055), the marital deduction (§2056) and state death taxes (§2058). Valuation of the gross
  estate and of each deduction is a fact supplied by the caller.
* §2001(b): tentative tax on taxable estate plus adjusted taxable gifts, less the gift tax that would have been payable
  on post-1976 gifts at the rates in force at death (§2001(g)), less the applicable credit (§2010(a)).
* §2010(c)(4), portability: the DSUE amount a decedent leaves the surviving spouse is the lesser of the basic exclusion
  amount and the excess of the decedent's applicable exclusion amount over the §2001(b)(1) base (taxable estate plus
  adjusted taxable gifts). The basic exclusion in the cap is the one for the decedent's year of death
  (Treas. Reg. §20.2010-2(c)(1)(i)). The regulation's adjustment for gift tax paid (§20.2010-2(c)(2)) is not modelled.

## GST tax (§§2601–2642), the basics

The tax is the taxable amount times the applicable rate: the maximum estate tax rate (§2641(b)) times the inclusion
ratio (§2642(a)), one minus the applicable fraction (exemption allocated over the value transferred, rounded to three
places, Treas. Reg. §26.2642-1(d)). The GST exemption is the basic exclusion amount (§2631(c)).
-/

namespace Legal.USTax.Estate

/-! ## Gift tax -/

structure Gift where
  value : Int
  present : Bool := true   -- a present interest, eligible for the §2503(b) exclusion
  spouse : Bool := false   -- to a citizen spouse: §2523
  charity : Bool := false  -- §2522
  deriving Repr, DecidableEq

/-- The taxable part of one donee's gifts for the year. -/
def Gift.taxable (y : Nat) (g : Gift) : Int :=
  if g.spouse || g.charity then 0
  else if g.present then max 0 (g.value - annualExclusion y)
  else g.value

/-- §2503(a): the year's taxable gifts. -/
def taxableGifts (y : Nat) (gs : List Gift) : Int := (gs.map (Gift.taxable y)).sum

/-- §2513: the half of each third-party gift a consenting spouse reports. Gifts to the spouse are not split. -/
def split (gs : List Gift) : List Gift :=
  gs.filter (fun g => !g.spouse) |>.map fun g => { g with value := g.value / 2 }

/-- One calendar period of a donor's gift history. -/
structure Period where
  year : Nat
  taxable : Int            -- taxable gifts of the period
  dsue : Int := 0          -- DSUE (and restored exclusion) available to the donor in the period
  deriving Repr, DecidableEq

/-- One row of the Schedule B worksheet: tax on the period's gifts (G), credit allowable (N), tax after credit. -/
structure Row where
  gross : Int
  credit : Int
  tax : Int
  deriving Repr, DecidableEq

/-- The Form 709 Schedule B worksheet, every period at the rates of year `r`: G = F − E, K = credit on (I + H),
M = K − L, N = min(G, M). -/
def schedule (r : Nat) (ps : List Period) : List Row :=
  (ps.foldl (fun (acc : Int × Int × List Row) p =>
      let g := tentative r (acc.1 + p.taxable) - tentative r acc.1
      let m := max 0 (credit r (bea p.year + p.dsue) - acc.2.1)
      let n := min g m
      (acc.1 + p.taxable, acc.2.1 + n, acc.2.2 ++ [⟨g, n, g - n⟩])) (0, 0, [])).2.2

/-- §§2502, 2505: the gift tax for the last period of `ps` (the earlier periods are its prior periods). -/
def giftTax (ps : List Period) : Int :=
  match ps.getLast? with
  | none => 0
  | some p => match (schedule p.year ps).getLast? with
    | none => 0
    | some row => row.tax

/-! ## Estate tax -/

structure Death where
  year : Nat
  gross : Int                  -- gross estate, §§2031–2046 (valuation is the caller's fact)
  expenses : Int := 0          -- §2053: funeral and administration expenses, debts, claims
  losses : Int := 0            -- §2054
  charitable : Int := 0        -- §2055
  marital : Int := 0           -- §2056
  stateTax : Int := 0          -- §2058
  gifts : List Period := []    -- post-1976 taxable gifts not included in the gross estate
  dsue : Int := 0              -- DSUE received from the last deceased spouse (§2010(c)(4)), as allowed
  deriving Repr

def Death.deductions (d : Death) : Int := d.expenses + d.losses + d.charitable + d.marital + d.stateTax

/-- §2051. -/
def Death.taxableEstate (d : Death) : Int := max 0 (d.gross - d.deductions)

/-- §2001(b): adjusted taxable gifts. -/
def Death.adjustedTaxableGifts (d : Death) : Int := (d.gifts.map Period.taxable).sum

/-- §2001(b)(1): the amount on which the tentative tax is computed (Form 706, Part 2, line 5). -/
def Death.base (d : Death) : Int := d.taxableEstate + d.adjustedTaxableGifts

/-- §2001(b)(2), (g): gift tax payable on post-1976 gifts, recomputed at the rates in force at death. -/
def Death.giftTaxPayable (d : Death) : Int := ((schedule d.year d.gifts).map Row.tax).sum

/-- §2010(c)(2): applicable exclusion amount. -/
def Death.exclusion (d : Death) : Int := bea d.year + d.dsue

/-- §2001(b) less the §2010 credit: the net estate tax (Form 706, Part 2, line 11). -/
def Death.tax (d : Death) : Int :=
  max 0 (tentative d.year d.base - d.giftTaxPayable - credit d.year d.exclusion)

/-- §2010(c)(4): the DSUE amount this decedent leaves a surviving spouse. -/
def Death.dsueOut (d : Death) : Int := max 0 (min (bea d.year) (d.exclusion - d.base))

/-- §2010(c)(2) for a surviving spouse dying (or giving) in year `y`. -/
def survivorExclusion (y : Nat) (dsue : Int) : Int := bea y + dsue

/-! ## GST tax -/

/-- Applicable fraction in thousandths, rounded to the nearest thousandth (§2642(a)(2); Reg. §26.2642-1(d)). -/
def applicableFraction (allocated value : Int) : Int :=
  if value ≤ 0 then 1000 else min 1000 ((allocated * 2000 + value) / (2 * value))

/-- §2642(a)(1): inclusion ratio in thousandths. -/
def inclusionRatio (allocated value : Int) : Int := 1000 - applicableFraction allocated value

/-- §§2602, 2641: GST tax on a taxable amount with `allocated` exemption, to the nearest dollar. -/
def gstTax (y : Nat) (amount allocated : Int) : Int :=
  (amount * maxRate y * inclusionRatio allocated amount + 50000) / 100000

end Legal.USTax.Estate
