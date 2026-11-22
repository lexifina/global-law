# JP (kernel-2.x full-tax model): findings

## FT review (2026-11-21; dev cases of the FT grids only)
- **JP FTR-1 (4400 印紙税, model fix).** The stamp tax on the real-estate transfer contract was not modelled.
  印紙税法 別表第一 第一号 (不動産の譲渡に関する契約書; 1万円未満 非課税; 10万円以下 200円) and 租税特別措置法 art. 91 (1)
  (contracts made 2014-04-01 .. 2027-03-31: 200 / 500 / 1,000 / 5,000 / 10,000 / 30,000 / 60,000 / 160,000 / 320,000 /
  480,000 yen by band), one copy per purchase; e-Gov asof 2025-07-01. Spec: `tools/p3/e1.py` (appended block). 9 guards.
- **JP stamp tax page (suyama, `jp_ft_stamptax_suyama_grid`):** referee one band below the statute on every dev case;
  adapter check requested (HANDOFF_FT_cap R3) before recording a software error.

- **JP FTR-2 (4300 贈与税 特例税率, model fix, FT review 2).** 租特 art. 70-2-5 (1): gifts from a lineal ascendant to a recipient 18+ on 1 January use the special table (10/15/20/30/40/45/50/55 % with bands 200/400/600/1,000/1,500/3,000/4,500万). Fixed (`tools/p3/e1.py` block; 5 guards). NTA Tax Answer 4408 example 2: 530,000 -> 485,000 (practice 2 / 2).

## FT review, third pass (2026-11-21; dev cases only; IMPROVE_FT.md "Third pass")
- **JP FTR-3 (1200).** 国税通則法 art. 118 (1) (base to 1,000 yen) and 119 (1) (tax to 100 yen) for 法人税 and 地方法人税 (e-Gov asof 2025-07-01). `jp_ft_cit_opentax_v2_grid` dev 234 -> 703 / 703; 1200 on 940 of 25,216 JP dev lines.
- **JP FTS-4 (印紙税, `jp_ft_stamptax_suyama_grid`; FT review 7, Dataset round 5 R5-5).** The referee's `TAX_TABLES.no1_fudosan`
  pairs each bracket with the next row's amounts (e.g. "[5e6, 1000, 500]": 100万超500万 reduced 500, where 租特 art. 91 (1) [3] says
  千円 and the 本則 is 2,000) and makes everything under 100万円 非課税 (`zeroUnder: 1000000`; 印紙税法 非課税物件 1: under 1万円).
  The model's `inshi` is 租特 art. 91 (1) [1]-[10] as in the e-Gov text of 2025-07-01 (`jp/law/egov/sozeitokubetsu_2025-07-01.txt`):
  200 / 500 / 1 000 / 5 000 / 10 000 / 30 000 / 60 000 / 160 000 / 320 000 / 480 000. Every dev case (694) is one bracket low in
  the referee. Category S; the model is not changed.
