import JpTax.Household
import JpTax.Beppyo5

/-!
# Tests against official figures (each kernel-checked with `decide`)

Sources (copies in `refs/`):
* [NC] 国税庁「令和７年分 年末調整のしかた」(nencho2025/pdf/nencho_all.pdf), page numbers as printed.
* [TA] 国税庁 タックスアンサー No.2260 (所得税の税率), No.1600 (公的年金等の課税関係), No.1411 (所得金額調整控除), read
  2026-11-18.
* [KK] 協会けんぽ 令和7年度保険料額表 (令和7年3月分から), 東京支部 (r7ippan3.xlsx); 令和6年度 (r6ippan3.xlsx).
* [MH] 厚生労働省「令和７（2025）年度 雇用保険料率のご案内」(content/001401966.pdf).
* [CF] 児童手当法第6条 (amounts) — no worked example is used for 児童手当.
-/

namespace JpTax

/-! ## 給与所得 and 所得金額調整控除 ([NC] pp. 36–37) -/

/-- [NC] p.36: "７，６５４，３２１円×９０％－１，１００，０００円＝５，７８８，８８８．９円（切り捨て）" → 5,788,888 円. -/
theorem nc_p36_kyuyo : kyuyoShotoku 7654321 = 5788888 := by decide

/-- [NC] p.37: "（８，７６５，４３２円－８，５００，０００円）×１０％＝ ２６，５４３．２円（切り上げ）" → 26,544 円. -/
theorem nc_p37_adjust : adjust1 8765432 true = 26544 := by decide

/-- [NC] p.37: "１５万円" is the most 所得金額調整控除 can be ("最高１５万円"). -/
theorem nc_p37_adjust_max : adjust1 10000000 true = 150000 ∧ adjust1 25000000 true = 150000 := by decide

/-! ## 速算表 ([NC] p.38, p.55; [TA] No.2260) -/

/-- [NC] p.38: "２，６９６，０００円×１０％－９７，５００円＝１７２，１００円". -/
theorem nc_p38_tax : tax89 2696000 = 172100 := by decide

/-- [TA] No.2260 具体例: "7,000,000円×0.23 - 636,000円= 974,000円" and "974,000×0.021＝20,454円". -/
theorem ta2260 : tax89 7000000 = 974000 ∧ fukko 974000 = 20454 := by decide

/-- [NC] p.55 速算表, every row at its two ends (the table stops at 18,050,000 yen, the 年末調整 ceiling). -/
theorem nc_p55_quick :
    tax89 1950000 = 1950000 * 5 / 100 ∧
    tax89 1951000 = 1951000 * 10 / 100 - 97500 ∧ tax89 3300000 = 3300000 * 10 / 100 - 97500 ∧
    tax89 3301000 = 3301000 * 20 / 100 - 427500 ∧ tax89 6950000 = 6950000 * 20 / 100 - 427500 ∧
    tax89 6951000 = 6951000 * 23 / 100 - 636000 ∧ tax89 9000000 = 9000000 * 23 / 100 - 636000 ∧
    tax89 9001000 = 9001000 * 33 / 100 - 1536000 ∧ tax89 18000000 = 18000000 * 33 / 100 - 1536000 ∧
    tax89 18001000 = 18001000 * 40 / 100 - 2796000 ∧ tax89 18050000 = 18050000 * 40 / 100 - 2796000 := by
  decide

/-! ## 基礎控除, 特定親族特別控除, 扶養控除 ([NC] p.56) -/

/-- [NC] p.56 「令和７年分の基礎控除額の表」, every row at both ends. -/
theorem nc_p56_kiso :
    kisoKojo 0 = 950000 ∧ kisoKojo 1320000 = 950000 ∧
    kisoKojo 1320001 = 880000 ∧ kisoKojo 3360000 = 880000 ∧
    kisoKojo 3360001 = 680000 ∧ kisoKojo 4890000 = 680000 ∧
    kisoKojo 4890001 = 630000 ∧ kisoKojo 6550000 = 630000 ∧
    kisoKojo 6550001 = 580000 ∧ kisoKojo 23500000 = 580000 ∧
    kisoKojo 23500001 = 480000 ∧ kisoKojo 24000000 = 480000 ∧
    kisoKojo 24000001 = 320000 ∧ kisoKojo 24500000 = 320000 ∧
    kisoKojo 24500001 = 160000 ∧ kisoKojo 25000000 = 160000 ∧ kisoKojo 25000001 = 0 := by decide

/-- [NC] p.56 「令和７年分の特定親族特別控除額の表」: nine rows by the relative's 合計所得金額, and the salaries printed beside
them ("収入が給与だけの場合の収入金額": 123万円超150万円以下 ... 185万円超188万円以下). -/
theorem nc_p56_tokutei_shinzoku :
    let k := fun i => tokuteiShinzokuKojo ⟨20, i⟩
    let ks := fun w => tokuteiShinzokuKojo ⟨20, kyuyoShotoku w⟩
    (k 580001 = 630000 ∧ k 850000 = 630000 ∧ k 850001 = 610000 ∧ k 900000 = 610000 ∧
     k 900001 = 510000 ∧ k 950000 = 510000 ∧ k 950001 = 410000 ∧ k 1000000 = 410000 ∧
     k 1000001 = 310000 ∧ k 1050000 = 310000 ∧ k 1050001 = 210000 ∧ k 1100000 = 210000 ∧
     k 1100001 = 110000 ∧ k 1150000 = 110000 ∧ k 1150001 = 60000 ∧ k 1200000 = 60000 ∧
     k 1200001 = 30000 ∧ k 1230000 = 30000) ∧
    (ks 1230000 = 0 ∧ ks 1230001 = 630000 ∧ ks 1500000 = 630000 ∧ ks 1500001 = 610000 ∧
     ks 1550000 = 610000 ∧ ks 1550001 = 510000 ∧ ks 1600000 = 510000 ∧ ks 1650000 = 410000 ∧
     ks 1700000 = 310000 ∧ ks 1750000 = 210000 ∧ ks 1800000 = 110000 ∧ ks 1850000 = 60000 ∧
     ks 1880000 = 30000 ∧ ks 1880001 = 0) := by decide

/-- [NC] p.56 「令和７年分の扶養控除額等の表」: 一般の控除対象扶養親族 380,000; 特定扶養親族 630,000; 老人扶養親族 (同居老親等
以外) 480,000; ひとり親控除 350,000. -/
theorem nc_p56_fuyo :
    fuyoKojo ⟨16, 0⟩ = 380000 ∧ fuyoKojo ⟨19, 0⟩ = 630000 ∧ fuyoKojo ⟨22, 580000⟩ = 630000 ∧
    fuyoKojo ⟨23, 0⟩ = 380000 ∧ fuyoKojo ⟨70, 0⟩ = 480000 ∧ fuyoKojo ⟨15, 0⟩ = 0 ∧
    fuyoKojo ⟨19, 580001⟩ = 0 ∧ hitorioyaKojo true 5000000 = 350000 ∧ hitorioyaKojo true 5000001 = 0 := by
  decide

/-! ## 配偶者控除・配偶者特別控除 ([NC] p.55, 「〔参考〕令和７年分の配偶者控除額及び配偶者特別控除額の一覧表」) -/

/-- Every cell of the 一覧表: the spouse's 合計所得金額 (rows) against the claimant's (900万円以下, 900万円超950万円以下,
950万円超1,000万円以下). -/
theorem nc_p55_spouse_table :
    let d := fun g s => haigushaKojo g s false + haigushaTokubetsu g s
    (d 9000000 580000 = 380000 ∧ d 9500000 580000 = 260000 ∧ d 10000000 580000 = 130000) ∧
    (d 9000000 580001 = 380000 ∧ d 9500000 950000 = 260000 ∧ d 10000000 950000 = 130000) ∧
    (d 9000000 950001 = 360000 ∧ d 9500000 1000000 = 240000 ∧ d 10000000 1000000 = 120000) ∧
    (d 9000000 1000001 = 310000 ∧ d 9500000 1050000 = 210000 ∧ d 10000000 1050000 = 110000) ∧
    (d 9000000 1050001 = 260000 ∧ d 9500000 1100000 = 180000 ∧ d 10000000 1100000 = 90000) ∧
    (d 9000000 1100001 = 210000 ∧ d 9500000 1150000 = 140000 ∧ d 10000000 1150000 = 70000) ∧
    (d 9000000 1150001 = 160000 ∧ d 9500000 1200000 = 110000 ∧ d 10000000 1200000 = 60000) ∧
    (d 9000000 1200001 = 110000 ∧ d 9500000 1250000 = 80000 ∧ d 10000000 1250000 = 40000) ∧
    (d 9000000 1250001 = 60000 ∧ d 9500000 1300000 = 40000 ∧ d 10000000 1300000 = 20000) ∧
    (d 9000000 1300001 = 30000 ∧ d 9500000 1330000 = 20000 ∧ d 10000000 1330000 = 10000) ∧
    (d 9000000 1330001 = 0 ∧ d 10000001 580000 = 0) := by decide

/-- The salaries printed beside the 一覧表 ("配偶者の収入が給与所得だけの場合の配偶者の給与等の収入金額"): 1,230,000 円以下;
1,600,000 円以下; 1,650,000; 1,700,000; 1,750,000; 1,800,000; 1,850,000; 1,903,999; 1,971,999; 2,015,999 円以下 — each
the last salary whose 給与所得 stays within the row, as 別表第五 gives it. -/
theorem nc_p55_spouse_salaries :
    kyuyoShotoku 1230000 = 580000 ∧ kyuyoShotoku 1230001 > 580000 ∧
    kyuyoShotoku 1600000 = 950000 ∧ kyuyoShotoku 1600001 > 950000 ∧
    kyuyoShotoku 1650000 = 1000000 ∧ kyuyoShotoku 1650001 > 1000000 ∧
    kyuyoShotoku 1700000 ≤ 1050000 ∧ kyuyoShotoku 1700001 > 1050000 ∧
    kyuyoShotoku 1750000 ≤ 1100000 ∧ kyuyoShotoku 1750001 > 1100000 ∧
    kyuyoShotoku 1800000 ≤ 1150000 ∧ kyuyoShotoku 1800001 > 1150000 ∧
    kyuyoShotoku 1850000 ≤ 1200000 ∧ kyuyoShotoku 1850001 > 1200000 ∧
    kyuyoShotoku 1903999 ≤ 1250000 ∧ kyuyoShotoku 1904000 > 1250000 ∧
    kyuyoShotoku 1971999 ≤ 1300000 ∧ kyuyoShotoku 1972000 > 1300000 ∧
    kyuyoShotoku 2015999 ≤ 1330000 ∧ kyuyoShotoku 2016000 > 1330000 := by decide

/-- [NC] p.55: the claimant columns "（１，０９５万円以下）", "１，１４５万円以下", "１，１９５万円以下" are the salaries giving
9,000,000 / 9,500,000 / 10,000,000 yen of 合計所得金額 (and "所得金額調整控除の適用がある場合は、括弧内の各金額に１５万円を
加えてください"). -/
theorem nc_p55_claimant_salaries :
    kyuyoShotoku 10950000 = 9000000 ∧ kyuyoShotoku 11450000 = 9500000 ∧ kyuyoShotoku 11950000 = 10000000 ∧
    kyuyoShotoku 11100000 - adjust1 11100000 true = 9000000 ∧
    kyuyoShotoku 12100000 - adjust1 12100000 true = 10000000 := by decide

/-! ## 所得要件 ([NC] p.4 【所得要件】) -/

/-- "58 万円以下（123 万円以下）", "58 万円超 133 万円以下（123 万円超 201 万 5,999 円以下）", 勤労学生 "85 万円以下（150 万円以下）";
before the reform 48万 (103万) and 75万 (130万). -/
theorem nc_p4_income_tests :
    kyuyoShotoku 1230000 = 580000 ∧ kyuyoShotoku 2015999 ≤ 1330000 ∧ kyuyoShotoku 2016000 > 1330000 ∧
    kyuyoShotoku 1500000 = 850000 := by decide

/-! ## The worked example of the booklet ([NC] p.57 設例, computed on p.58) -/

/-- 設例: 給与 8,970,000 円 (no other income); 社会保険料 1,386,102 円; 生命保険料控除 120,000 円 and 地震保険料控除 50,000 円
(the booklet's own amounts, not modelled here); 一般の控除対象配偶者 (給与所得 400,000 円); 一般の控除対象扶養親族 1 人,
特定扶養親族 1 人, 老人扶養親族 (同居老親等, 一般の障害者) 1 人 — 扶養控除と障害者控除 together 1,860,000 円 as printed
(380,000 + 630,000 + 580,000 + 270,000); 特定親族 (給与所得 1,000,000 円); 住宅借入金等特別控除 76,500 円. Printed: 給与所得
控除後 7,020,000; 所得金額調整控除 47,000; 6,973,000; 所得控除の合計 4,786,102; 課税給与所得 2,186,000; 算出所得税額
121,100; 年調所得税額 44,600; 年調年税額 45,500 円. -/
theorem nc_p57_example :
    let w := 8970000
    let g := kyuyoShotoku w - adjust1 w true
    let ded := 1386102 + 120000 + 50000 + haigushaKojo g 400000 false +
      tokuteiShinzokuKojo ⟨20, 1000000⟩ + (fuyoKojo ⟨17, 0⟩ + fuyoKojo ⟨20, 0⟩ + 580000 + 270000) + kisoKojo g
    let t := trunc1000 (g - ded)
    kyuyoShotoku w = 7020000 ∧ adjust1 w true = 47000 ∧ g = 6973000 ∧ ded = 4786102 ∧ t = 2186000 ∧
    tax89 t = 121100 ∧ tax89 t - 76500 = 44600 ∧ nationalPayable (tax89 t - 76500) = 45500 := by decide

/-! ## 公的年金等 ([TA] No.1600) -/

/-- [TA] No.1600 例1: 65 歳以上, 公的年金等に係る雑所得以外の合計所得金額 500 万円, 収入 350 万円: "3,500,000円×75％-275,000円
＝2,350,000円". -/
theorem ta1600 : nenkinZatsu 3500000 5000000 true = 2350000 := by decide

/-! ## Social insurance ([KK], [MH]) -/

/-- [KK] 令和7年度 東京: 標準報酬月額 58,000 円 → 全額 5,747.8 / 折半額 2,873.9 (no 介護); 110,000 円 → 折半額 5,450.5
(an exact half: withheld as 5,450 円 under note ①); with 介護 (11.50 %) 410,000 円 → 折半額 23,575; 厚生年金 (18.3 %)
650,000 円 → 折半額 59,475. -/
theorem kk_r7_tokyo :
    58000 * 9910 = 574780000 ∧ rhd (58000 * 9910) 200000 = 2874 ∧
    rhd (110000 * 9910) 200000 = 5450 ∧ rhd (410000 * 11500) 200000 = 23575 ∧
    rhd (650000 * 18300) 200000 = 59475 := by decide

/-- [KK] the grade boundaries: 報酬月額 395,000 円 → 410,000 (健保 27級, 厚年 24級); 635,000 → 650,000 (厚年 32級, the
cabinet-order grade); 1,355,000 → 1,390,000 (健保 50級). -/
theorem kk_grades :
    kenpoStd (12 * 394999) = 380000 ∧ kenpoStd (12 * 395000) = 410000 ∧
    kouseiStd (12 * 634999) = 620000 ∧ kouseiStd (12 * 635000) = 650000 ∧
    kenpoStd (12 * 1355000) = 1390000 ∧ kouseiStd (12 * 88000) = 88000 ∧ kenpoStd (12 * 88000) = 88000 := by
  decide

/-- [MH] 雇用保険 労働者負担: "6/1,000" (令和６年度, to March 2025) and "5.5/1,000" (令和７年度, from April 2025). -/
theorem mh_koyo : koyoRate 3 = 600 ∧ koyoRate 4 = 550 ∧ rhd (300000 * 550) 100000 = 1650 := by decide

end JpTax
