import FrTax.Tax
import FrTax.Social
import FrTax.HighIncome

/-!
# From the gross tax to the tax due

art. 197, I, 5: the reductions of art. 199 quater F to 200 come off the tax after the décote, and cannot be
refunded; then the tax credits and withholdings, which can (art. 193, fourth paragraph).
-/

namespace FrTax

/-! ## Reductions (cannot exceed the tax) -/

/-- **art. 199 quater F.** School fees: 61 € per child at collège (7EA), 153 € at lycée (7EC), 183 € in higher
education (7EF); half for a child in shared residence (7EB, 7ED, 7EG). -/
def schoolReduction (d : Decl) : Int :=
  61 * d.get "7EA" + 153 * d.get "7EC" + 183 * d.get "7EF" +
    rnd (61 * d.get "7EB" + 153 * d.get "7ED" + 183 * d.get "7EG") 2

/-- **art. 199 quindecies.** Care-home costs: 25 % of at most 10 000 € per person accommodated (7CD, 7CE). -/
def careHomeReduction (d : Decl) : Int :=
  pct 2500 (min (d.get "7CD") 10000) + pct 2500 (min (d.get "7CE") 10000)

/-- **art. 200.** Gifts. To aid organisations: 75 % up to a limit; for income 2024 the limit is 1 000 € (7UD,
7VA); for income 2025, loi n° 2026-103, art. 28, raised it to 2 000 € for gifts made from 14 October 2025 (7UQ,
7VM), gifts made before keeping the 1 000 € limit (7UD, 7VA), the two together at most 2 000 €. To the upkeep
of religious heritage (7UJ): 75 % up to 1 000 €; for income 2024, to the victims of cyclone Chido in Mayotte
(7UO, gifts from 14 December 2024): 75 % up to 2 000 € (both as M and the 2042 form state the limits). The rest, with other gifts (7UF,
foreign organisations 7VC, political parties 7UH), 66 % within 20 % of the taxable income. -/
def giftsReduction (p : Params) (d : Decl) (rni : Int) : Int :=
  let old := d.get "7UD" + d.get "7VA"
  let new := if p.year ≥ 2025 then d.get "7UQ" + d.get "7VM" else 0
  let aid := if p.year ≥ 2025 then min 2000 (min old 1000 + min new 2000) else min old 1000
  let rel := min (d.get "7UJ") p.box7UJMax
  let chido := if p.year = 2024 then min (d.get "7UO") 2000 else 0
  -- the excess of the five previous years over the 20 % limit is carried forward (art. 200, 1, last
  -- paragraph: 7XS, 7XT, 7XU, 7XW, 7XY) and comes off with this year's gifts, within the same limit
  let carried := d.sum ["7XS", "7XT", "7XU", "7XW", "7XY"]
  -- box 7UJ did not exist for income 2020 (`box7UJMax = 0`): the DGFiP's simulator ignores it
  let relAll := if p.box7UJMax = 0 then 0 else d.get "7UJ"
  let rest := old + new - aid + relAll - rel + (if p.year = 2024 then d.get "7UO" - chido else 0)
    + d.get "7UF" + d.get "7VC" + d.get "7UH" + carried
  pct 7500 aid + pct 7500 rel + pct 7500 chido + pct 6600 (min rest (pct 2000 rni))

def reductions (p : Params) (d : Decl) (rni : Int) : Int :=
  schoolReduction d + careHomeReduction d + giftsReduction p d rni

/-! ## Tax credits (refundable) -/

/-- **art. 199 sexdecies.** 50 % of home-help costs (7DB) less the aid received (7DR), within 12 000 €
raised by 1 500 € per child in charge (half for shared residence) and per member over 65, at most 15 000 €;
15 000 € (at most 18 000 €) in the first year (7DQ); 20 000 € for a disabled holder (7DG). -/
def homeHelpCredit (d : Decl) : Int :=
  let spent := pos (d.get "7DB" - d.get "7DR")
  if spent = 0 then 0 else
  let f := family d
  let members : Int := (if over65 d "0DA" then 1 else 0) + (if d.couple && over65 d "0DB" then 1 else 0)
  -- "par enfant à charge au sens des articles 196 et 196 B": minors and attached children (0CF, 0DJ, 0DN),
  -- not the disabled people of art. 196 A bis (0CR)
  let kids : Int := d.get "0CF" + d.get "0DJ" + d.get "0DN"
  -- "et des ascendants ... âgés de plus de soixante-cinq ans" who receive the APA (7DL)
  let raise2 : Int := 2 * 1500 * (kids + members + d.get "7DL") + 1500 * f.alt       -- in half-euros
  let limit :=
    if d.has "7DG" then 20000
    else if d.has "7DQ" then min 18000 (15000 + raise2 / 2)
    else min 15000 (12000 + raise2 / 2)
  pct 5000 (min spent limit)

/-- **art. 200 quater B.** 50 % of childcare costs for each child under six, within 3 500 € (7GA, 7GB, 7GC),
half that in shared residence (7GE, 7GF, 7GG). -/
def childcareCredit (p : Params) (d : Decl) : Int :=
  let one (b : String) (lim : Int) := min (d.get b) lim
  let full := p.childcareMax
  let half := p.childcareMax / 2
  -- one credit, rounded once (art. 1657, 1: the amount of the reduction is rounded)
  pct 5000 (one "7GA" full + one "7GB" full + one "7GC" full + one "7GE" half + one "7GF" half + one "7GG" half)

/-- **art. 199 quater C.** 66 % of union dues (7AC, 7AE, 7AG), within 1 % "du montant du revenu brut désigné à
l'article 83" (the gross salaries and pensions, before the 10 % allowance); not for a person who uses actual
expenses ("ne s'applique pas aux bénéficiaires ... admis à justifier du montant de leurs frais réels"). -/
def unionCredit (p : Params) (d : Decl) : Int :=
  let usesActual (w : Who) : Bool :=
    let g := grossSalary d w
    d.has (row "1" "K" w) && min (actualExpenses d w) g > min g (max p.salMin (min p.salMax (pct 1000 g)))
  let one (b : String) (w : Who) :=
    if usesActual w then 0 else pct 6600 (min (d.get b) (pct 100 (grossSalary d w + grossPension d w)))
  one "7AC" .v + one "7AE" .c + one "7AG" .p1

/-- The 7.5 % levy withheld on 2DH proceeds is given back on the part covered by the allowance (art. 200 A, 2;
M: IRE). -/
def lifeLevyRefund (d : Decl) : Int := pct 750 (lifeSplit d).dh

/-- The refundable credits and prepayments: imputed on the tax, the excess refunded. -/
def credits (p : Params) (d : Decl) : Int :=
  homeHelpCredit d + childcareCredit p d + unionCredit p d + d.get "2CK" + lifeLevyRefund d

/-- **art. 199 ter, I, b.** The tax credits attached to foreign securities income under the tax treaties (2AB) are
imputed on the income tax and never refunded: "En ce qui concerne les revenus de source étrangère visés aux
articles 120 à 125, l'imputation est limitée au montant du crédit correspondant à l'impôt retenu à la source à
l'étranger [...] tel qu'il est prévu par les conventions internationales"; the refund of the second paragraph of
I, a covers only "les sommes retenues à la source" in France (art. 119 bis, 1678 bis). BOI-RPPM-RCM-20-10-20-60
§ 90: the credit "doit être limité à la fraction de l'impôt français correspondant aux revenus donnant lieu à
imputation"; BOI-INT-DG-20-20-100 § 43: "le crédit d'impôt sera limité au montant de l'impôt français calculé à
raison des mêmes revenus". It is imputed first, on the tax after reductions including the flat tax, and up to that
tax (what M does: CIRCMAVFT = max(0, min(IRB + ..., RCMAVFT)); the production simulator agrees). The per-income
limit is not checked beyond that: the declared amount is taken as the imputable credit computed on form 2047. -/
def foreignCredit (d : Decl) (taxBefore : Int) : Int := pos (min (d.get "2AB") taxBefore)

/-! ## The flat tax on investment income (art. 200 A, 1) -/

/-- **art. 200 A, 1, A.** Without the scale option, investment income and gains are taxed at 12.8 % on their
gross amount. -/
def flatBase (d : Decl) : Int :=
  if scaleOption d then 0
  else d.get "2DC" + d.get "2TR" + d.get "2TS" + d.get "2FU" + pos (d.get "3VG" - d.get "3VH") + life128 d

/-- 12.8 % on the flat base; 7.5 % on post-2017 life insurance of eight years or more within 150 000 € of
premiums (2VV, art. 200 A, 2 bis), after the allowance. -/
def flatTax (d : Decl) : Int :=
  -- the proportional taxes are rounded once, on their sum (what M does: IPROP)
  rnd (1280 * flatBase d + (if scaleOption d then 0 else 750 * life75 d)) 10000

/-- Income in the RFR outside the taxable income: the flat base, the 7.5 % life insurance after its allowance,
and in full the proceeds that bore the 7.5 % levy at source (2DH; 1417, IV, 1°, c). -/
def rfrInvestments (d : Decl) : Int :=
  flatBase d + (if scaleOption d then 0 else life75 d) + pos (d.get "2DH")

/-! ## The result -/

structure Result where
  quarters : Int
  rng : Int
  rni : Int
  capped : Capped
  decote : Int
  reductions : Int
  credits : Int
  flat : Int
  /-- The conventions credit 2AB imputed (art. 199 ter, I, b): at most the tax, never refunded. -/
  foreign : Int
  /-- Tax after reductions and after the imputed conventions credit 2AB, before the refundable credits (M: IAN). -/
  beforeCredits : Int
  /-- Net tax: tax after reductions less the 2AB credit imputed and the refundable credits; when the tax after
  reductions is under 61 € nothing is collected (art. 1657, 1 bis), the refundable credits are still refunded. -/
  net : Int
  rfr : Int
  social : Int
  cehr : Int
  cdhr : Int
  deriving Repr

/-- **art. 1417, IV, 1°.** The revenu fiscal de référence: the net taxable income plus income taxed at the flat
rate, exempt overtime pay (art. 81 quater), the exempt value-sharing bonus (loi n° 2022-1158, art. 1, VI quater)
and the 40 % allowance on dividends. -/
def rfr (p : Params) (d : Decl) (rni : Int) : Int :=
  let vl := flatLevyIncome d
  let base := if vl > 0 then taxableIncomeOn p d (netGlobalWith p d vl) else rni
  base + rfrInvestments d + Who.all.foldl (fun a w => a + overtimeForRfr p d w + ppvForRfr p d w) 0
    + retirementUsed p d vl
    + d.get "3VZ" + d.get "2EE"
    + (if scaleOption d then pct 4000 (d.get "2DC") else 0)

def compute (p : Params) (d : Decl) : Result :=
  let rng := netGlobal p d
  let rni := taxableIncome p d
  -- art. 197 C: with income under the flat levy, the tax is the tax on all the income times the share of
  -- taxable income, rounded (M rounds the tax on all the income first); the décote then applies to the
  -- result (a reading of "au taux correspondant à l'ensemble de ses revenus": what M does)
  let vl := flatLevyIncome d
  -- "l'ensemble de ses revenus": the taxable income recomputed on the revenu net global plus that income, so the
  -- allowance of art. 157 bis is tested on the total (what M does)
  let tot := if vl > 0 then taxableIncomeOn p d (netGlobalWith p d vl) else rni
  let c0 := capped p d tot
  -- (the reported full and capped amounts are scaled the same way, as M's IDRS2 and the simulator's "droits
  -- simples" are; only `tax` enters the liquidation)
  let c := if vl > 0 && rni > 0 then { c0 with tax := rnd (c0.tax * rni) tot, capped := rnd (c0.capped * rni) tot,
                                               full := rnd (c0.full * rni) tot }
           else if vl > 0 then { c0 with tax := 0, capped := 0, full := 0 } else c0
  let dec := decote p d c.tax
  let afterDec := c.tax - dec
  let red := min afterDec (reductions p d rni)
  let fl := flatTax d
  let before := afterDec - red + fl
  -- art. 199 ter, I, b: the conventions credit 2AB is imputed first, up to the tax, and the rest is lost
  let ab := foreignCredit d before
  let cr := credits p d
  -- The other credits are imputed on the tax due and only the excess is refunded (art. 199 sexdecies, 4; art.
  -- 200 quater B; art. 199 quater C: "l'excédent ... est restitué"). A positive balance is not collected when
  -- the tax after reductions, before any credit, is under 61 € (art. 1657, 1 bis).
  let rf := rfr p d rni
  let ce := cehr d rf
  -- art. 1657, 1 bis: the 61 € test is on the initial assessment, income tax and CEHR together, before the 2AB
  -- credit (what M does)
  let net := if ab + cr ≥ before then before - ab - cr else if before + ce < 61 then 0 else before - ab - cr
  let realCredits := cr - d.get "2CK"
  { quarters := quarters d, rng, rni, capped := c, decote := dec, reductions := red, credits := cr,
    flat := fl, foreign := ab, beforeCredits := before - ab, net, rfr := rf, social := socialLevies d, cehr := ce,
    cdhr := cdhr d rf (before - realCredits + flatLevyPaid d + pct 1900 (d.get "3VZ")) ce }

end FrTax
