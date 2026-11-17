import FrTax.Income

/-!
# Prélèvements sociaux on investment and property income

Three levies on the income of capital, assessed with the income tax:

* CSG: Code de la sécurité sociale, art. L136-6 (patrimony income) and L136-8 (rates): 9.2 %. For income
  2025, loi n° 2025-1403 de financement de la sécurité sociale pour 2026 raised the rate on investment
  income to 10.6 %; property income keeps 9.2 % (what M applies: BCSG excludes rents in 2025).
* CRDS: ordonnance n° 96-50 du 24 janvier 1996, art. 15: 0.5 %.
* Prélèvement de solidarité: CGI art. 235 ter: 7.5 %.

Each levy is rounded on its own (art. 1657, 1). Income on which the paying bank already withheld the levies
(2BH, 2CG) is not charged again.
-/

namespace FrTax

/-- Investment income and gains charged here: dividends, interest, other distributions, unlisted PEA income,
life insurance (2DC, 2TR, 2TS, 2FU, 2CH), less what was already charged at source (2BH, 2CG); net gains
(3VG − 3VH). -/
def psInvestmentBase (d : Decl) : Int :=
  pos (d.sum ["2DC", "2TR", "2TS", "2FU", "2CH", "2VV", "2WW", "2ZZ", "2YY"] - d.get "2BH" - d.get "2CG")
    + pos (d.get "3VG" - d.get "3VH")
    -- life annuities bought for value: the taxable fraction of art. 158, 6 (CSS art. L136-6, I, a... "rentes
    -- viagères constituées à titre onéreux")
    + annuities d

/-- Property income: the micro-foncier net (70 % of 4BE), the real-regime result (4BA), less deficits on
property income (4BB, 4BD); for income 2024, furnished letting under the micro regime (5ND, 50 %). -/
def psPropertyBase (d : Decl) : Int :=
  let micro := d.get "4BE" - pct 3000 (d.get "4BE")
  -- furnished letting shares one services allowance with professional services (art. 50-0): the levies fall
  -- on its share, the allowance less the part assigned pro rata to the professional services (M: MIB_ABNPPV)
  let share (pro fur : String) : Int :=
    let t := d.get pro + d.get fur
    if d.year > 2024 || d.get fur ≤ 0 then 0 else
    let a := min t (max 305 (pct 5000 t))
    let aPro := rnd (a * d.get pro) t
    d.get fur - (a - aPro)
  let furnished := share "5KP" "5ND" + share "5LP" "5OD" + share "5MP" "5PD"
  pos (d.get "4BA" - d.get "4BB" - d.get "4BD") + micro + furnished

/-- The levies, with CSG and CRDS rounded together (what M does: its `CSG` is 9.7 %, its `RDS` is empty; rounding
them apart can differ by 1 €, a reading of art. 1657, 1 we record, not a finding). Not collected when the
total is under 61 € (CSS art. L136-6, III: "Il n'est pas procédé au recouvrement de la contribution lorsque
le montant total par article de rôle ... est inférieur à 61 euros"). -/
def socialLevies (d : Decl) : Int :=
  let inv := psInvestmentBase d
  let prop := psPropertyBase d
  let csgInv : Int := if d.year ≥ 2025 then 1060 else 920
  -- CSG + CRDS per group of income with its own rate, then the 7.5 % on the whole (M: CSG on investment
  -- income and on property income rounded apart in 2025, when their rates differ)
  let total :=
    if csgInv = 920 then rnd (970 * (inv + prop)) 10000 + rnd (750 * (inv + prop)) 10000
    else rnd ((csgInv + 50) * inv) 10000 + rnd (970 * prop) 10000 + rnd (750 * (inv + prop)) 10000
  if total < 61 then 0 else total

end FrTax
