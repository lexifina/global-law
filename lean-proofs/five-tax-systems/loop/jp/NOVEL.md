# Japan: bounded search for novel interactions (`scripts/novel.py`, `scripts/novelA2.py`)

About 0.3 CPU-hours in all, a few hundred thousand households through the loop `jptax`. Outputs in `runs/novel_*.json`. Verdicts:
**novel** (no source found in 2 targeted searches), **known**, or **artefact**.

## N-A. ふるさと納税: the 2025 特定親族特別控除 and the dead row (7) push the gift's 特例控除 into the wrong bracket — NOVEL
- Mechanism: the 特例控除 rate (地方税法第314条の7第11項第1号, 附則第5条の6) is chosen on the 住民税 課税総所得金額 less the
  人的控除差調整額, built from the 調整控除 table of 第314条の6 plus (所得税 基礎控除 − 480,000). That table has no row for
  the 特定親族 (F4) and a dead row for a 配偶者特別控除 spouse (F2). So the rate test sees a taxable income 180,000 (student)
  or 50,000 (spouse with 合計所得 580,001–1,000,000) higher than the real 所得税 one; near a bracket edge it picks the next
  bracket's lower rate, and the donor loses 5.1 or 10.2 % of the gift. The parent's taxable incomes are unchanged.
- Paired scan (wages 2.5M–12M, gift 30,000): student earning 1.4M vs earning nothing — gift costs up to 3,000 more in
  bands 6.04M–6.33M, 7.86M–8.08M, 11.52M–11.71M of the parent's pay (142 of 1,901 wages); spouse with 合計所得 850,000 vs 0 —
  bands 5.28M–5.34M, 7.18M–7.29M, 11.12M–11.16M (39 of 1,901).
- Proof: `furusato_tokutei_shinzoku_gap` — parent on 8,000,000, gift 30,000: relief 25,159 when the student earns 1,400,000,
  28,059 when the student earns nothing (same 所得税 and 住民税 taxable incomes).
- Documented? 総務省 warns in general that the rate "所得税の税率と異なる場合があります"; the 2025 特定親族 instance (a reform
  that kept the parent's deductions equal but not this table) was not found. Size: small per donor, systematic.

## N-B. ワンストップ pays more than the gift less 2,000 yen — NOVEL (tiny)
- Where the 課税総所得金額 is below the 人的控除差調整額 (no 所得税 bracket) the 特例控除 is 90 % (第11項第2号). The 申告特例
  控除 table (附則第7条の2第5項, 第7条の3) has no row for a negative amount, which falls in "百九十五万円以下": it adds
  5.105/84.895 of the 特例控除 for 所得税 the donor never paid. Total relief ≈ 105.4 % of the gift above 2,000.
- Scan: single wage 1.10M–3.0M; ワンストップ cost at its limit below 1,900 yen from wage 1.46M; lowest 1,300 at 1,820,000
  (gift 12,000) — `furusato_onestop_overpays` (10,000 relief filing, 10,700 ワンストップ).
- Bounded by the 20 % cap on a small 所得割: a few hundred yen. Not found in sources (they state ワンストップ = 確定申告).

## N-C. Who claims which child — KNOWN (quantified)
- Couples 3M–15M × 0–6M, every assignment of children. Children aged 16–22: the default (top earner) is optimal in every grid
  case (2 one-yen exceptions, rounding). Children under 16: in 125 of 583 cases naming them on the lower earner's return is
  better, by up to 59,800 a year (second earner on 2,000,000: the 均等割 / 所得割 非課税 limits rise with dependants; mixed
  20/17/10: the 10-year-old to the 1.75M earner gains 38,000). FP literature mentions "年少扶養を妻に" for 住民税 非課税.

## N-D. Net income falling for one more yen with the new inputs — KNOWN types
- Widow (寡婦): −35,512 at 2,044,000 (住民税 非課税 135万 for 寡婦, the same wall as the ひとり親 one of F5); 106万 −162,354;
  標準報酬 grades about −30,000. Spouse with a 200,000 bonus: 106万 −168,256, grade at 93,000/month −15,041. Parent giving
  ふるさと 60,000: only the existing grade notches. No new kind of notch.

## N-E. Medical expenses: which spouse claims — KNOWN
- Lower spouse better in 64 of 651 grid cases, by up to 5,035 (5 % of a 総所得金額等 under 2,000,000 instead of 100,000);
  otherwise the top earner's higher rate wins.

## Other observations
- Bracket straddle (KNOWN): when a donation's 所得税 deduction pulls taxable income below a bracket edge, the 特例 rate (fixed
  on pre-gift income) overshoots the real 所得税 relief: single 13.1M (taxable 9,029,000) pays 9,026 for a 100,000 gift.
- 106万 ignores bonuses (C23, KNOWN to HR practice; the 2025 pension reform is to drop the 88,000 test).
- One large bonus (C22, KNOWN: 標準賞与額 caps).
- No artefacts found: every result above traces to a provision; the model reproduces F5's walls exactly with the additions.
