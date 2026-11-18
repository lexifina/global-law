import JpTax.Household

/-!
# The 年収の壁 ("income walls"), kernel-checked on whole households

`netIncome` is the contract's net income: gross − incomeTax − 復興特別所得税 − 住民税 − employee social insurance +
児童手当. Each theorem evaluates the whole model (`compute`) in the kernel for two salaries one yen (or one row) apart.
The walls of the 2025 debate: 103万 (the old income-tax threshold, gone), 106万 (employee insurance at a large employer),
110万 (住民税 均等割), 123万 (the new 扶養 threshold), 130万 (losing 被扶養者 status: not reached in this model, where an
earner above 106万 is insured), 150万 / 188万 (the new 特定親族特別控除 for students), 160万 (where a single earner
starts to pay income tax; where the 配偶者特別控除 starts to fall).
-/

namespace JpTax

set_option maxRecDepth 200000

def grossOf (h : Household) : Int :=
  h.adults.foldl (fun a x => a + x.wages + x.selfEmployment + x.pension) 0 + h.children.foldl (fun a c => a + c.wages) 0

def netIncome (h : Household) : Int :=
  let r := compute h
  grossOf h - r.incomeTax - r.fukkoTotal - r.localTax - r.employeeSocial + r.benefits

def single (w : Int) : Household :=
  { id := "single", year := 2025, adults := [⟨30, w, 0, 0⟩], married := false, children := [] }

/-- A couple: the first earns 6,000,000 yen, the second `w`; two children aged 8 and 5. -/
def couple (w : Int) : Household :=
  { id := "couple", year := 2025, adults := [⟨40, 6000000, 0, 0⟩, ⟨38, w, 0, 0⟩], married := true,
    children := [⟨8, 0⟩, ⟨5, 0⟩] }

/-- Parents earning 6,000,000 and 0, with one child of the given age earning `w`. -/
def withChild (age w : Int) : Household :=
  { id := "child", year := 2025, adults := [⟨50, 6000000, 0, 0⟩, ⟨48, 0, 0, 0⟩], married := true,
    children := [⟨age, w⟩] }

/-- A single mother aged 35 with a child aged 6. -/
def singleMother (w : Int) : Household :=
  { id := "single-parent", year := 2025, adults := [⟨35, w, 0, 0⟩], married := false, children := [⟨6, 0⟩] }

/-! ## 103万 and 123万 are no longer walls for a spouse -/

/-- **103万円 is no wall**: a spouse earning 1,030,000 yen or one yen more changes nothing but that yen (the spouse is
still a 同一生計配偶者 up to 1,230,000 yen and pays no income tax up to 1,600,000 yen). -/
theorem wall_103_gone : netIncome (couple 1030001) - netIncome (couple 1030000) = 1 := by decide

/-- **123万円 is no wall for a spouse**: at 1,230,001 yen the 配偶者控除 (380,000) becomes a 配偶者特別控除 of the same
380,000 yen (第83条の2第1項第1号イ). -/
theorem wall_123_spouse_gone : netIncome (couple 1230001) - netIncome (couple 1230000) = 1 := by decide

/-! ## The walls that remain -/

/-- **106万円 (employee insurance)**: at 88,000 yen a month (1,056,000 a year) a part-timer at a large employer joins
健康保険 and 厚生年金 (健康保険法第3条第1項第9号ロ): one more yen of pay costs 154,946 yen of contributions. -/
theorem wall_106 : netIncome (single 1056000) - netIncome (single 1055999) = -154945 := by decide

/-- **110万円 (住民税 均等割)**: a single person whose 合計所得金額 passes 450,000 yen (salary 1,100,000) owes the 均等割
(1,000 + 3,000) and 森林環境税 (1,000) (第295条第3項, 施行令第47条の3: 350,000 × 1 + 100,000 in Tokyo's wards). -/
theorem wall_110 : netIncome (single 1100001) - netIncome (single 1100000) = -4999 := by decide

/-- **123万円 for a child aged 16–18**: the parent loses the 扶養控除 (380,000 yen; 住民税 330,000) when the child's
合計所得金額 passes 580,000 yen; the 特定親族特別控除 only exists for ages 19–22. The household loses 71,797 yen for one
more yen of the child's pay. -/
theorem wall_123_highschool : netIncome (withChild 17 1230001) - netIncome (withChild 17 1230000) = -71797 := by
  decide

/-- **123万円 for a student aged 19–22: a 500-yen wall remains.** The 特定扶養控除 (630,000) becomes a 特定親族特別控除 of
630,000, but the 住民税 調整控除 table (地方税法第37条, 第314条の6) has a row for the 特定扶養親族 (180,000 yen) and none for
the 特定親族, so the parent's 調整控除 falls. -/
theorem wall_123_student : netIncome (withChild 20 1230001) - netIncome (withChild 20 1230000) = -499 := by decide

/-- **150万円 for a student**: the 特定親族特別控除 falls from 630,000 to 610,000 yen (第84条の2第1項第2号). -/
theorem wall_150_student : netIncome (withChild 20 1500001) - netIncome (withChild 20 1500000) = -1020 := by decide

/-- **188万円 for a student**: the last step, 30,000 to nothing (第84条の2第1項: "百二十三万円以下"). -/
theorem wall_188_student : netIncome (withChild 20 1880001) - netIncome (withChild 20 1880000) = -6062 := by decide

/-- **160万円 for a spouse**: the 配偶者特別控除 starts to fall (380,000 → 360,000) when the spouse's 合計所得金額 passes
950,000 yen; then every 50,000 yen of the spouse's income costs the household a step. -/
theorem wall_160_spouse :
    netIncome (couple 1600001) - netIncome (couple 1600000) = -2041 ∧
    netIncome (couple 1650001) - netIncome (couple 1650000) = -7104 ∧
    netIncome (couple 1700001) - netIncome (couple 1700000) = -10104 := by decide

/-- **The 132万 notch**: the spouse's own 基礎控除 falls from 950,000 to 880,000 yen when the spouse's 合計所得金額 passes
1,320,000 yen (措置法第41条の16の2第1項第1号イ, ロ): one more 1,000 yen of pay at 2,004,000 costs 2,930 yen net. -/
theorem notch_132 : netIncome (couple 2004000) - netIncome (couple 2003000) = -2930 := by decide

/-- **135万 for a single parent (住民税)**: a ひとり親 with a 合計所得金額 of at most 1,350,000 yen pays no 住民税 at all
(第295条第1項第2号); at 1,350,800 (salary 2,044,000) she pays 32,000 yen. -/
theorem wall_single_parent_135 :
    netIncome (singleMother 2044000) - netIncome (singleMother 2043999) = -31999 := by decide

/-! ## The income tax is not monotone in pay once social insurance is counted -/

/-- **Income tax falls when pay rises**: at 195,000 yen a month (2,340,000 a year) the 標準報酬月額 moves up a grade
(190,000 → 200,000) in both health insurance and 厚生年金; the employee's contributions jump by 16,937 yen, the
社会保険料控除 with them, and the income tax falls by 700 yen — while net income falls by 14,721 yen. -/
theorem incomeTax_not_monotone :
    (compute (single 2340000)).incomeTax < (compute (single 2339999)).incomeTax ∧
    netIncome (single 2340000) - netIncome (single 2339999) = -14721 := by decide

/-- **The top rate on a whole household**: a self-employed person (no employee contributions) earning 100,000,000 yen
pays exactly 11,189 yen more of 所得税 + 復興特別所得税 + 住民税 for 20,000 yen more: 55.945 %. -/
theorem top_rate_household :
    let h := fun x : Int => ({ id := "top", year := 2025, adults := [⟨50, 0, x, 0⟩], married := false,
                               children := [] } : Household)
    let tot := fun x => (compute (h x)).incomeTax + (compute (h x)).fukkoTotal + (compute (h x)).localTax
    tot 100020000 - tot 100000000 = 11189 := by decide

/-! ## The dividend regime is the taxpayer's choice, and the default is the dearest at low incomes -/

/-- A single retiree aged 70 with a public pension of 1,500,000 yen and listed-share dividends `d`, under 確定申告不要
(`agg = false, decl = false`), 総合課税 (`agg`) or 申告分離課税 (`decl`). -/
def retiree (d : Int) (agg decl : Bool) : Household :=
  { id := "retiree", year := 2025, adults := [⟨70, 0, 0, 1500000⟩], married := false, children := [],
    dividends := d, aggregateDividends := agg, declaredDividends := decl }

def taxTotal (h : Household) : Int :=
  let r := compute h
  r.incomeTax + r.fukkoTotal + r.localTax

/-- **The same 2,000,000 yen of dividends costs 406,300 yen left to withholding (措置法第8条の5), 336,288 declared
separately (第8条の4: the unused 基礎控除 comes off the dividends) and 143,500 taxed with the pension (総合課税, with the
配当控除 of 所得税法第92条 wiping out the income tax).** The default most retail investors keep is the dearest. -/
theorem dividend_regimes_retiree :
    taxTotal (retiree 2000000 false false) = 406300 ∧ taxTotal (retiree 2000000 false true) = 336288 ∧
    taxTotal (retiree 2000000 true false) = 143500 := by decide

#print axioms wall_106
#print axioms wall_123_highschool
#print axioms incomeTax_not_monotone

end JpTax
