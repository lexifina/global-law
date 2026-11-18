import JpTax.Walls

/-!
# Loopholes and optimisations, kernel-checked on whole households (`~/cmp/loop/jp`)

Each theorem evaluates the whole model (`compute`, with the additions of `Extras.lean`) for two choices the law leaves
to the household. `taxOf` = 所得税 + 復興特別所得税 + 住民税 (令和8年度 on 2025 income, Tokyo wards); `netOf` = gross pay
(salary + bonus + business + pension) − those taxes − employee contributions + 児童手当.
-/

namespace JpTax

set_option maxRecDepth 200000

def taxOf (h : Household) : Int :=
  let r := compute h
  r.incomeTax + r.fukkoTotal + r.localTax

def netOf (h : Household) : Int :=
  let r := compute h
  grossOf h + h.ext.foldl (fun a e => a + e.bonus) 0 - r.incomeTax - r.fukkoTotal - r.localTax - r.employeeSocial +
    r.benefits

/-! ## ふるさと納税 (地方税法第314条の7, 附則第5条の6; 所得税法第78条) -/

def single5m (d : Int) (oneStop : Bool) : Household :=
  { id := "f", year := 2025, adults := [⟨35, 5000000, 0, 0⟩], married := false, children := [],
    ext := [{ furusato := d, oneStop := oneStop }] }

/-- **The 2,000-yen deal.** A single employee on 5,000,000 yen who gives 61,000 yen to municipalities pays 59,024 yen
less tax (所得税 deduction + 住民税 基本控除 + 特例控除): the gift costs 1,976 yen net. -/
theorem furusato_5m_limit : taxOf (single5m 0 false) - taxOf (single5m 61000 false) = 59024 := by decide

/-- **Past the limit the 20 % cap binds**: 10,000 yen more given brings only 2,621 yen more relief. -/
theorem furusato_5m_past_limit : taxOf (single5m 61000 false) - taxOf (single5m 71000 false) = 2621 := by decide

def single182 (d : Int) (oneStop : Bool) : Household :=
  { id := "f", year := 2025, adults := [⟨30, 1820000, 0, 0⟩], married := false, children := [],
    ext := [{ furusato := d, oneStop := oneStop }] }

/-- **Novel N-B: ワンストップ pays back more than the gift less 2,000 yen.** For a donor with no 所得税 bracket (課税総所得
金額 below the 人的控除差調整額: 特例控除 at 90 %, 第314条の7第11項第2号), the 申告特例控除 (附則第7条の2第5項, 第7条の3)
still adds 5.105/84.895 of the 特例控除, because a negative amount falls in its "百九十五万円以下" row. Salary 1,820,000,
gift 12,000: relief 10,000 when filing (cost 2,000), 10,700 with ワンストップ (cost 1,300). -/
theorem furusato_onestop_overpays :
    taxOf (single182 0 false) - taxOf (single182 12000 false) = 10000 ∧
    taxOf (single182 0 true) - taxOf (single182 12000 true) = 10700 := by decide

/-! ## Household arbitrage: who claims the children -/

def coupleKids (w1 w2 : Int) (claim : List Int) : Household :=
  { id := "c", year := 2025, adults := [⟨45, w1, 0, 0⟩, ⟨43, w2, 0, 0⟩], married := true,
    children := [⟨8, 0⟩, ⟨5, 0⟩], claimants := claim }

/-- **年少扶養親族 on the lower earner's return.** Children under 16 give no 扶養控除, but they count in the 住民税
non-taxable limits (地方税法第295条第3項 / 附則第3条の3: 350,000 × (dependants + 1) + 100,000 (+ 210,000 / 320,000)).
Couple on 3,000,000 and 2,000,000: naming the two children (8 and 5) as the second earner's dependants exempts that
earner from 住民税 entirely: 59,800 yen a year. -/
theorem nensho_to_lower_earner :
    netOf (coupleKids 3000000 2000000 [1, 1]) - netOf (coupleKids 3000000 2000000 []) = 59800 := by decide

/-! ## Pay design: bonus versus salary -/

def spouseBonus (w b : Int) : Household :=
  { id := "b", year := 2025, adults := [⟨40, 6000000, 0, 0⟩, ⟨38, w, 0, 0⟩], married := true, children := [],
    ext := [{}, { bonus := b }] }

/-- **106万 counts no bonus.** 健康保険法第3条第1項第9号ロ tests "報酬（...賞与...を除く。）" against 88,000 yen a month.
A spouse paid 1,255,988 yen as 87,999 a month plus a 200,000-yen bonus stays outside employee insurance (and, under
130万, a 被扶養者); paid as 104,666 a month the same total is insured: 168,170 yen a year apart. -/
theorem bonus_escapes_106 :
    netOf (spouseBonus 1055988 200000) - netOf (spouseBonus 1255988 0) = 168170 := by decide

def payMix (salary bonus : Int) : Household :=
  { id := "p", year := 2025, adults := [⟨45, salary, 0, 0⟩], married := false, children := [],
    ext := [{ bonus := bonus }] }

/-- **One large bonus.** 12,000,000 yen as a 3,000,000 salary plus a 9,000,000 December bonus: 厚生年金 counts at most
1,500,000 of a bonus (厚生年金保険法第24条の4) and health insurance 5,730,000 a year (健康保険法第45条); net income is
305,975 yen higher than the same pay as salary (and the future pension lower). -/
theorem bonus_shift_12m : netOf (payMix 3000000 9000000) - netOf (payMix 12000000 0) = 305975 := by decide

/-! ## Business income: 青色事業専従者給与 (所得税法第57条第1項) -/

def soleTrader (biz spouseWage : Int) : Household :=
  { id := "s", year := 2025, adults := [⟨45, 0, biz, 0⟩, ⟨43, spouseWage, 0, 0⟩], married := true, children := [],
    ext := [{ aoiro := 650000 }, { senjusha := spouseWage > 0 }] }

/-- **Paying the spouse.** A 青色 sole trader with 10,000,000 yen of profit who pays the working spouse 3,000,000 as
青色事業専従者給与 (deductible; the spouse is then no 控除対象配偶者, 第2条第1項第33号) pays 675,804 yen less tax a
year (social insurance of the self-employed not modelled). -/
theorem senjusha_10m : taxOf (soleTrader 10000000 0) - taxOf (soleTrader 7000000 3000000) = 675804 := by decide

def parentStudent (childWage d : Int) : Household :=
  { id := "s", year := 2025, adults := [⟨50, 8000000, 0, 0⟩, ⟨48, 0, 0, 0⟩], married := true,
    children := [⟨20, childWage⟩], ext := [{ furusato := d }, {}] }

/-- **Novel N-A: the 2025 特定親族特別控除 is missing from the ふるさと rate test.** The 特例控除 rate is chosen on the 住民税
課税総所得金額 less the 人的控除差調整額 (第314条の7第11項第1号), built from the 調整控除 table of 第314条の6, which has a row
for a 特定扶養親族 (180,000) and none for a 特定親族 (F4). A parent on 8,000,000 whose 20-year-old earns 1,400,000 (特定親族
特別控除 630,000) has exactly the same taxable incomes as one whose student earns nothing (特定扶養控除 630,000), but the
rate test puts the first in the 20 % bracket (69.58 %) while his 所得税 bracket is 10 %: a 30,000-yen gift brings 25,159
yen of relief instead of 28,059. -/
theorem furusato_tokutei_shinzoku_gap :
    taxOf (parentStudent 1400000 0) - taxOf (parentStudent 1400000 30000) = 25159 ∧
    taxOf (parentStudent 0 0) - taxOf (parentStudent 0 30000) = 28059 := by decide

end JpTax
