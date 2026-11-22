# KR findings

## FT review, third pass (2026-11-21; dev cases only)
- **KR FTR-1 (4300).** 상증법 art. 19 (1), (4): spouse deduction = amount received, 5억 to 30억 (with art. 21: 35억). Inheritance grid 210 -> 218 / 364; the rest is the art. 69 3 % filing credit the tool assumes (convention).
- **KR FTR-2 (4400).** 지방세특례제한법 art. 36-3 (1) 2: first home ≤ 12억 less 200만원. 128 -> 166 / 707 (w1% 692).

- **KR FTS-1 / FTS-2 (gift tax with earlier gifts; FT review 4).** 상증법 art. 58 (1): the credit is the tax computed at the
  time on the earlier gift; (2) capped at the aggregate tax × (earlier 과세표준 / aggregate). Hand check (spouse; earlier
  920 725 983 two years before; now 59 983 627): 66,14 m − 54,14 m = 12,00 m = the model; kcalc 5,82 m (FTS-1);
  budongsanskills returns 0 on several such cases (FTS-2).
- **KR FTS-3 (acquisition tax; FT review 4).** kcalc and budongsantax omit the first-home relief (지방세특례제한법 art. 36-3 (1) 2:
  200만원 on homes ≤ 12억); the 171 dev cases that lost exactness after KR FTR-2 are all first homes.

- **KR FTC-1 (자동차세 installments, `kr_ft_vehicle_suwontable_grid`, open; FT review 6).** All 691 dev cases within 1 %; 140
  differ by 10-18 won: the referee truncates each half-year installment (지방세법 art. 128 (1): the annual amount in two halves)
  to 10 won. The 10-won 끝수 rule for local taxes (지방회계법 / 국고금 관리법 art. 47 as applied) is not held: not changed.
- **KR 재산세 after session 10 (FT review 7, Dataset round 5 R5-7): not a regression.** On every one-home dev case of
  `kr_ft_property_kcalc_grid` (679) and `kr_ft_property_budongsanskills_grid` (409 homes) the referee total = the model's 재산세 x
  1.2 + 0.14 % of the base (시가표준액 x 43 / 44 / 45 %): the model's 재산세 (지방세법 art. 111-2 (1), 시행령 art. 109 (1) 2 단서, 2025
  wording) equals the referees' 재산세; the referees add the 지방교육세 (art. 151 (1) 6: 20 % of the 재산세; **M**, requested in
  PROGRESS_ASIAPAC) and the 도시지역분 (art. 112 (1) 2: 0.14 % in council-designated urban zones; the entity has no location: **KR
  FTC-2**, referee input `urbanArea: true`). Before session 10 the 60 % ratio and art. 111 (1) 3 rates came near the referee
  totals by offsetting errors.
