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

/-! ## 2012: the payroll tax holiday

For 2012 the OASDI rates were cut by 2 points (TRUIRJCA §601 as extended by Pub. L. 112-78 §101 and Pub. L. 112-96
§1001): employee 4.2% (§3101(a)), self-employment 10.4% (§1401(a)). §601(b)(2) replaces the §164(f) deduction for
those years with 59.6% of the §1401(a) tax plus one-half of the §1401(b) tax — Schedule SE (2012) line 13. (The
short Schedule SE line 6, "multiply line 5 by 57.51% ... or 50% and add $1,100", approximates the same amount.) -/

/-- §1401(a) at 10.4% (to the base) plus 2.9%, rounded once (2012). -/
def seTax2012 (base se wages : Int) : Int := roundDollar (104 * oasdiBaseY base se wages + 29 * A.seIncome10k se) 10000000

/-- TRUIRJCA §601(b)(2): 59.6% of the 10.4% tax plus one-half of the 2.9% tax, rounded once (2012). -/
def halfSeTax2012 (base se wages : Int) : Int :=
  roundDollar (61984 * oasdiBaseY base se wages + 14500 * A.seIncome10k se) 10000000000

/-- SE tax for the year's parameters. -/
def seTaxP (p : Params) (se wages : Int) : Int :=
  if p.year == 2012 then seTax2012 p.ssWageBase se wages else seTaxY p.ssWageBase se wages

/-- The §164(f) deduction for the year's parameters. -/
def halfSeTaxP (p : Params) (se wages : Int) : Int :=
  if p.year == 2012 then halfSeTax2012 p.ssWageBase se wages else halfSeTaxY p.ssWageBase se wages

-- 2012, $50,000 of profit: 92.35% = $46,175 × 13.3% = $6,141.28 → $6,141; deduction 59.6% × $4,802.20 + ½ × $1,339.08
-- = $2,862.11 + $669.54 = $3,531.65 → $3,532 (Schedule SE (2012) long form lines 10–13).
#guard seTax2012 110100 50000 0 = 6141 ∧ halfSeTax2012 110100 50000 0 = 3532
-- Above the base: $150,000 profit: NESE $138,525; 10.4% × $110,100 = $11,450.40 (Schedule SE (2012) short line 5:
-- "add $11,450.40") + 2.9% × $138,525 = $4,017.23: $15,467.63 → $15,468.
#guard seTax2012 110100 150000 0 = 15468

/-! ## Employee share of FICA (for §24(d)(2)) -/

/-- §3101(a)–(b)(1): 6.2% of wages up to the base plus 1.45% of all wages, rounded (assumes correct withholding). -/
def employeeFica (base wages : Int) : Int := roundDollar (62 * min (pos wages) base + 145 * pos wages / 10) 1000

#guard employeeFica 168600 50000 = 3825

/-- The year's employee share: 4.2% OASDI in 2012 (TRUIRJCA §601(a)(1) as extended). -/
def employeeFicaP (p : Params) (wages : Int) : Int :=
  if p.year == 2012 then roundDollar (42 * min (pos wages) p.ssWageBase + 145 * pos wages / 10) 1000
  else employeeFica p.ssWageBase wages

#guard employeeFicaP ((params? 2012).getD default) 50000 = 2825

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
