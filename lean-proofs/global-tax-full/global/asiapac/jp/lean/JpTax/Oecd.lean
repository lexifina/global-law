import JpTax.Person

/-!
# OECD Taxing Wages 2026 (tax year 2025), Japan — like-for-like checks

Source: OECD SDMX API, dataflow `OECD.CTP.TPS:DSD_TAX_WAGES_COU@DF_TW_COU(2.1)`, REF_AREA JPN, TIME_PERIOD 2025
(`refs/oecd/tw_cou_2025.csv`, downloaded 2026-11-18). Average wage (GEBT, 100 % AW) 5,703,038.49 yen; employee social
security contributions (EECSSC) 838,346.66 yen (14.7 % of earnings, the OECD's flat national rate). The OECD figures:

| household | CGTC (taxable) | CGITLETC (所得税) | CGITFP (with 復興) | SLT (住民税) |
|---|---|---|---|---|
| single, 100 % AW | 2,604,000 | 162,900 | 166,300 | 286,900 |
| single, 167 % AW (9,524,074.28; SSC 1,242,286.12) | 5,751,000 | 722,700 | 737,800 | 591,600 |
| couple + 2 children, 100 % AW + no earnings | 2,224,000 | 124,900 | 127,500 | 253,900 |
| single, 67 % AW (3,821,035.79; SSC 561,692.26) | 1,175,000 | 58,750 | 59,900 | 164,000 |
| single parent + 2 children, 67 % AW | 1,175,000 | 58,750 | 59,900 | 164,000 (HFTA 0: no ひとり親控除) |

The model is run on the same salary (whole yen) and the OECD's contribution (whole yen) as the 社会保険料控除.
-/

namespace JpTax

def oecdPerson (w ssc : Int) (spouse : Option Relative) : PersonOut :=
  person { age := 30, wages := w, business := 0, pension := 0, rental := 0, dividends := 0, ideco := 0,
           donations := 0, socialIns := ssc, childUnder23 := false, singleParent := false,
           singleParentMother := true, spouse := spouse, dependants := [{ age := 11, income := 0 }, { age := 6, income := 0 }] }

/-- Single, 100 % AW: the statute's 給与所得 (別表第五, 第28条第4項) is 4,120,000 yen, the OECD's formula gives
4,122,430.79; so the taxable income is 2,601,000 (OECD 2,604,000) and the income tax 162,600 (OECD 162,900). -/
theorem oecd_single_aw100 :
    let o := person { age := 30, wages := 5703038, business := 0, pension := 0, rental := 0, dividends := 0,
                      ideco := 0, donations := 0, socialIns := 838346, childUnder23 := false, singleParent := false,
                      singleParentMother := true, spouse := none, dependants := [] }
    o.kyuyo = 4120000 ∧ o.taxable = 2601000 ∧ o.kijun = 162600 ∧ o.national = 166000 ∧
    o.loc.pref + o.loc.muni = 282500 ∧ o.loc.total = 287500 := by decide

/-- Above 6,600,000 yen the formula is the statute (第28条第3項), and the model gives the OECD's taxable income and
income tax exactly: single, 167 % AW. -/
theorem oecd_single_aw167 :
    let o := person { age := 30, wages := 9524074, business := 0, pension := 0, rental := 0, dividends := 0,
                      ideco := 0, donations := 0, socialIns := 1242286, childUnder23 := false, singleParent := false,
                      singleParentMother := true, spouse := none, dependants := [] }
    o.taxable = 5751000 ∧ o.kijun = 722700 ∧ o.national = 737800 := by decide

/-- Couple with two children (ages under 16: no 扶養控除), one earner at 100 % AW, spouse without income: 配偶者控除
380,000 yen. -/
theorem oecd_couple_aw100 :
    let o := oecdPerson 5703038 838346 (some { age := 30, income := 0 })
    o.dHaigusha = 380000 ∧ o.taxable = 2221000 ∧ o.kijun = 124600 := by decide

/-- Single, 67 % AW: 給与所得 2,616,000 by the table (OECD 2,616,828.63 by the formula); taxable 1,174,000 (OECD
1,175,000); income tax 58,700 (OECD 58,750). -/
theorem oecd_single_aw67 :
    let o := person { age := 30, wages := 3821035, business := 0, pension := 0, rental := 0, dividends := 0,
                      ideco := 0, donations := 0, socialIns := 561692, childUnder23 := false, singleParent := false,
                      singleParentMother := true, spouse := none, dependants := [] }
    o.kyuyo = 2616000 ∧ o.taxable = 1174000 ∧ o.kijun = 58700 := by decide

/-- **The OECD gives a single parent no ひとり親控除.** At 67 % AW with two children the statute (所得税法第81条: 350,000
yen; 地方税法第314条の2第1項第8号の2: 300,000 yen) lowers the taxable income to 824,000 yen and the income tax to 41,200 yen;
the OECD reports the childless single person's 1,175,000 and 58,750 (HFTA = 0). -/
theorem oecd_single_parent_aw67 :
    let o := person { age := 30, wages := 3821035, business := 0, pension := 0, rental := 0, dividends := 0,
                      ideco := 0, donations := 0, socialIns := 561692, childUnder23 := true, singleParent := true,
                      singleParentMother := true, spouse := none, dependants := [{ age := 11, income := 0 }, { age := 6, income := 0 }] }
    o.dHitorioya = 350000 ∧ o.taxable = 824000 ∧ o.kijun = 41200 := by decide

end JpTax
