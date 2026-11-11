import LegalProofs.USTax.TaxCourt.Schedule
import TaxCode.Individual.A.SocialSecurity
import TaxCode.Individual.A.SelfEmployment

/-!
# Income items that change by year: self-employment tax (§§1401–1402), taxable social security (§86), the 2020
unemployment exclusion (§85(c) as added by ARPA §9042)

* **§86** has no indexed figures; this reuses the 2025 model's exact core (`TaxCode.Individual.A.taxableSS40`, in
  fortieths of a dollar) and base amounts unchanged.
* **SE tax**: the 2025 model's computation with the year's contribution and benefit base in place of $176,100
  (`seTaxY_eq_2025` proves the two agree at the 2025 base). Computed per individual: each spouse's own net earnings and
  own wages (§1402(b)(1) reduces the base by "wages paid to such individual").
* **2020 unemployment**: up to $10,200 of unemployment compensation per individual is excluded if modified AGI is less
  than $150,000 (any filing status), MAGI being AGI computed with all of it included (§85(c)(1)–(2)).
-/

namespace Legal.USTax.TaxCourt
open TaxCode.Individual

/-! ## Self-employment tax, by year -/

/-- §1402(b)(1): the part of self-employment income under the year's base less the individual's wages, in
1/10,000 dollars. -/
def oasdiBaseY (base se wages : Int) : Int := min (A.seIncome10k se) (10000 * max 0 (base - wages))

/-- §1401(a) 12.4% (to the base) plus §1401(b)(1) 2.9% (all), rounded once to the dollar. -/
def seTaxY (base se wages : Int) : Int := roundDollar (124 * oasdiBaseY base se wages + 29 * A.seIncome10k se) 10000000

/-- §164(f): one-half of the §1401(a)–(b)(1) taxes, rounded. -/
def halfSeTaxY (base se wages : Int) : Int :=
  roundDollar (124 * oasdiBaseY base se wages + 29 * A.seIncome10k se) 20000000

/-- At the 2025 base this is exactly the 2025 model's self-employment tax. -/
theorem seTaxY_eq_2025 (se w : Int) : seTaxY 176100 se w = A.seTaxCore se w := by
  unfold seTaxY oasdiBaseY A.seTaxCore A.oasdiBase10k A.wageBase2025; rfl

theorem seTaxY_nonneg (base se w : Int) : 0 ≤ seTaxY base se w := by
  unfold seTaxY oasdiBaseY A.seIncome10k A.nese10k roundDollar
  split <;> omega

theorem seTaxY_mono (base se se' w : Int) (h : se ≤ se') : seTaxY base se w ≤ seTaxY base se' w := by
  unfold seTaxY oasdiBaseY A.seIncome10k A.nese10k roundDollar
  split <;> split <;> omega

/-- Net earnings from self-employment for the EIC and ACTC (§32(c)(2)(A)(ii): "determined with regard to the
deduction allowed ... by section 164(f)"): net profit less one-half of SE tax. -/
def seEarned (base se wages : Int) : Int := se - halfSeTaxY base se wages

-- 2016: $50,000 of profit, no wages: 92.35% = $46,175; × 15.3% = $7,064.78 → $7,065.
#guard seTaxY 118500 50000 0 = 7065
-- 2016 wage-base coordination: wages $118,500 (the base): only 2.9% remains: $1,339.08 → $1,339.
#guard seTaxY 118500 50000 118500 = 1339
-- 2024: profit $200,000: 92.35% = $184,700; 12.4% of $168,600 = $20,906.40; 2.9% of $184,700 = $5,356.30.
#guard seTaxY 168600 200000 0 = 26263
-- The $400 floor: $433 of profit owes nothing in any year.
#guard seTaxY 127200 433 0 = 0 ∧ seTaxY 127200 434 0 = 61

/-! ## Employee share of FICA (for §24(d)(2)) -/

/-- §3101(a)–(b)(1): 6.2% of wages up to the base plus 1.45% of all wages, rounded (assumes correct withholding). -/
def employeeFica (base wages : Int) : Int := roundDollar (62 * min (pos wages) base + 145 * pos wages / 10) 1000

#guard employeeFica 168600 50000 = 3825

/-! ## §86 taxable social security -/

/-- Taxable social security benefits, §86, given modified AGI (AGI without §86 and §221, plus tax-exempt interest),
benefits, filing status and (for married filing separately) whether the spouses lived apart all year. -/
def taxableSocialSecurity (f : Filing) (livedApart : Bool) (benefits magi86 : Int) : Int :=
  roundDollar (A.taxableSS40 (A.baseAmount f livedApart) (A.adjustedBaseAmount f livedApart) (pos benefits) magi86) 40

/-! ## 2020 unemployment compensation exclusion -/

/-- §85(c) (ARPA §9042), 2020 only: excluded unemployment compensation, given each spouse's unemployment
compensation and MAGI (AGI with all unemployment compensation included, §85(c)(2)). -/
def unemploymentExclusion (year : Nat) (ucTaxpayer ucSpouse magi : Int) : Int :=
  if year == 2020 && magi < 150000 then min (pos ucTaxpayer) 10200 + min (pos ucSpouse) 10200 else 0

#guard unemploymentExclusion 2020 15000 0 60000 = 10200
#guard unemploymentExclusion 2020 15000 4000 60000 = 14200
#guard unemploymentExclusion 2020 15000 0 150000 = 0
#guard unemploymentExclusion 2021 15000 0 60000 = 0

end Legal.USTax.TaxCourt
