# Japan (令和7年分): individual tax planning techniques (節税策) — catalogue, triage, recreation

Model: `lean/` = the `../../jp` model (F1–F16) plus `JpTax/Extras.lean` and small patches
(`scripts/patch.py`): ふるさと納税 (寄附金税額控除 基本 + 特例, ワンストップ 申告特例控除), 住宅ローン控除 (所得税 + 住民税
residual), 青色申告特別控除, 小規模企業共済, 医療費控除 / セルフメディケーション, 生命保険料 / 地震保険料控除, 寡婦控除, 認定NPO
税額控除, per-adult iDeCo, a December bonus (標準賞与額), 青色事業専従者, and a free choice of which adult claims each child
(`children[].claimant`). Statute texts used: `law/*.txt` (extracted from the e-Gov XML listed in `../../jp/law/README.md`).
Regression: 9,000 households of the Japanese model's runs give identical outputs with the old and new binary.

Triage: **(a)** expressible with the existing inputs; **(b)** small statute-faithful addition made here; **(c)** out of scope.
Numbers: `recreate.json` (from `scripts/recreate.py`); "saving" = fall in 所得税 + 復興 + 住民税 (+ employee contributions,
− 児童手当 change). Social insurance of the self-employed (国保・国民年金) is not modelled: rows on business income compare
taxes only. Headline rows are kernel-checked in `lean/JpTax/Loop.lean` (marked ✓L).

## Recreated (a)/(b): 30 techniques

| id | technique | source | triage | scenario → result |
|---|---|---|---|---|
| C01 | ふるさと納税: give up to the limit, net cost 2,000 yen | 所得税法第78条第2項第1号; 地方税法第37条の2・第314条の7, 附則第5条の6; NTA No.1155 | b | single wage 3M/5M/7M/10M/20M: limit 28,000 / 61,000 / 108,000 / 184,000 / 568,000 (burden 1,936–2,072); 10,000 past the limit costs 7,500–10,400 more. 5M: 61,000 gift → 59,024 relief ✓L `furusato_5m_limit`, `furusato_5m_past_limit` |
| C01b | ワンストップ特例 instead of 確定申告 | 地方税法附則第7条・第7条の2・第7条の3 | b | same total within ±72 yen at 3M/5M/10M (rounding); see N-B for the case where it pays more |
| C02 | iDeCo (小規模企業共済等掛金控除) | 所得税法第75条; 確定拠出年金法施行令第36条; NTA No.1135 | a | 276,000/yr: saves 41,690 / 52,257 / 83,859 at wage 3M / 5M / 8M (15 %–30 %) |
| C03 | 小規模企業共済 (sole trader) | 第75条第2項第1号 | b | business 8M, 840,000: 269,924; with iDeCo 816,000 too: 518,251 on 1,656,000 |
| C04 | NISA (tax-free dividends and gains) | 措置法第9条の8・第37条の14 | a | 1M dividends + 1M gains in NISA: 406,300 (20.315 %) |
| C05 | 配当: 総合課税 / 申告分離 / 申告不要 | 所得税法第92条; 措置法第8条の4・第8条の5; NTA No.1330 | a | 1M dividends: aggregate saves 171,650 (no wage), 164,740 (3M wage), 29,050 (9M wage); declared saves 161,993 with no wage, 0 with wages (F16) |
| C06 | 損益通算: listed-share loss against dividends | 措置法第37条の12の2; NTA No.1474 | a (input pre-netted) | 600,000 loss vs 1M dividends: 121,890 |
| C07 | 扶養の付け替え (16+ dependants) | 所得税法施行令第219条; NTA No.1180 | b | default (top earner) is best: moving children 17, 20 to the 4M spouse costs 29,890; N-C finds no grid case where a 16–22 child is better with the lower earner (beyond 1 yen) |
| C08 | 年少扶養親族 on the lower earner's return | 地方税法第295条第3項, 附則第3条の3 | b | spouse 1.3M: 6,200; spouse 2M: 59,800 ✓L `nensho_to_lower_earner` (N-C) |
| C09 | stay under 106万 (88,000/month) | 健康保険法第3条第1項第9号ロ (F5) | a | 1,055,999 vs 1,056,000: 154,946 of contributions |
| C09b | 配偶者特別控除 steps / 160万 | 第83条の2 (F5, F8) | a | spouse 1.6M instead of 1.7M: 31,753 less tax + contributions on 100,000 less pay |
| C10 | student earns up to 150万 (特定親族特別控除) | 第84条の2 (F4, F5) | a | 1.5M instead of 1.23M: parent pays 500 more (the 調整控除 gap) |
| C11 | セルフメディケーション vs 医療費控除 | 第73条; 措置法第41条の17; NTA No.1120, 1129 | b | medical 150,000 vs OTC 60,000: 医療費控除 better by 303; medical 80,000: セルフメディケーション saves 7,250 |
| C12 | 医療費 claimed by the spouse under 200万 (5 % threshold) | 第73条第1項 | b | 7M + 1.6M spouse: lower spouse better by 195; 12M earner: top earner better by 6,442; N-E: lower spouse best in 64/651 grid cases, up to 5,035 |
| C13 | 住宅ローン控除 (0.7 %, residual to 住民税) | 措置法第41条; 地方税法附則第5条の4の2; NTA No.1211-1 | b | balance 30M (limit 30M): 179,741 at wage 4.5M (≈30,000 of the 210,000 credit lost to the 住民税 cap), 214,410 at 8M (credit + 復興 on it) |
| C14 | 住宅ローン + ふるさと: use ワンストップ | as C01b, C13 | b | 4.5M, gift 50,000: ワンストップ saves 2,500 more (the 所得税 deduction is wasted once the credit has used the 所得税) |
| C15 | 生命保険料控除 / 地震保険料控除 | 第76条, 第77条; 地方税法第314条の2第1項第5号・第5号の3 | b | 3 × 80,000: 19,252; earthquake 50,000: 7,605 (wage 5M) |
| C16 | 青色申告特別控除 65万 | 措置法第25条の2; NTA No.2072 | b | business 5M: 207,940 vs 白色; 177,520 vs 10万 |
| C17 | 給与 → 事業所得 | 第27条, 第28条 | a (tax only) | 3M/6M/10M as business (青色 65万): taxes +122,753 / +538,017 / +860,152 (no 給与所得控除); employee social disappears but 国保・国民年金 are not modelled — not a loophole on tax |
| C18 | 青色事業専従者給与 | 第57条第1項; 第2条第1項第33号; NTA No.2075 | b | profit 10M, 3M paid to spouse: 675,804 ✓L `senjusha_10m`; profit 6M, 1M: 203,814 |
| C19 | 寡婦控除 (and 住民税 非課税 135万) | 第80条; 地方税法第295条第1項第2号 | b | wage 3M: 40,283; wage 2,040,000: 70,359 (非課税) |
| C20 | ひとり親: stay under 合計所得 135万 | 地方税法第295条第1項第2号 (F5) | a | 2,043,999 vs 2,044,000: 32,000 |
| C21 | 選択制DC (salary sacrifice) vs iDeCo | 確定拠出年金法; 標準報酬月額 | a | 276,000: 46,330 / 46,248 / 5,224 more than iDeCo at 3M / 5M / 8M (contributions fall; future 厚生年金 too) |
| C22 | pay as one large bonus (標準賞与額 caps) | 厚生年金保険法第24条の4; 健康保険法第45条 | b | 12M as 3M salary + 9M bonus: 305,975 ✓L `bonus_shift_12m`; 7.2M as 4.8M + 2.4M: 32,737 |
| C23 | part-timer: bonus outside the 88,000 test | 健康保険法第3条第1項第9号ロ ("賞与...を除く") | b | 1,255,988 as 87,999/month + 200,000 bonus vs 104,666/month: 168,170 ✓L `bonus_escapes_106` |
| C24 | 認定NPO: 税額控除 instead of 所得控除 | 措置法第41条の18の3 | b | 100,000 gift: 3,370 / 20,012 / 7,005 more at 3M / 8M / 20M |
| C25 | 児童手当: count a supported 19–22 child for birth order | 児童手当法 (2024 reform) | a | children 12, 8 plus a 20-year-old: +240,000 benefit and 99,153 less tax (特定扶養) |
| C26 | marry by 31 December | 第85条第1項 | a | 6M / 0 couple: 71,798 |
| C27 | claim a parent aged 70+ (老人扶養親族) | 第84条 | a (relative entered as a household member) | parent 75, no income: 104,875 at 7M |
| C28 | iDeCo for the non-earning spouse (pitfall) | 第75条 (own income only) | b | 276,000: saves 0 (vs 55,679 for the earner) |
| C29 | declare listed gains to use idle deductions | 措置法第37条の11; 所得税法第87条 (R5) | a | retiree, pension 1M, gains 2M: 151,272 (raises 合計所得, so 国保 etc. would rise; not modelled) |
| C30 | 所得金額調整控除 for both parents | 措置法第41条の3の11 (F13) | a | already established in F13; not re-run |

## Out of scope (c): 15

| id | technique | why |
|---|---|---|
| X1 | 退職金: 一時金 vs 年金 (iDeCo exit) | 退職所得 (第30条) is a separate income kind, multi-year comparison |
| X2 | 純損失・譲渡損失の繰越控除 | 第70条, 措置法第37条の12の2第5項: multi-year |
| X3 | マイクロ法人 / 法人成り, 役員報酬設計 | corporate tax |
| X4 | 暦年贈与, 相続時精算課税, 教育資金一括贈与 | 贈与税・相続税 |
| X5 | 居住用財産 3,000万円特別控除 | 措置法第35条: real-estate 譲渡所得 not modelled |
| X6 | 定時決定: low pay in April–June | 健康保険法第41条: needs monthly pay; model has 12 equal months |
| X7 | 医療費・経費の年末 timing | multi-year |
| X8 | 借上げ社宅, 非課税通勤手当 | 所得税基本通達36-40 ff., 第9条第1項第5号: needs separate tax and social wage bases (> 60 lines) |
| X9 | 同居老親等 580,000 | 措置法第41条の16: cohabitation of a parent not representable beyond C27 |
| X10 | 勤労学生控除 | 第82条: the child's own tax is not computed |
| X11 | 所得税 総合 / 住民税 申告不要 split for dividends | closed from 令和6年度 (F16) |
| X12 | 特定支出控除 | 第57条の2: low payoff (a few thousand users), not added |
| X13 | 一時所得 (保険満期, 50万 + 1/2) | income kind not modelled |
| X14 | 国民年金 付加・前納, 国保 under-reporting | self-employed social insurance not modelled |
| X15 | 障害者控除 | not added: no planning margin beyond the deduction itself |

Counts: 45 catalogued; 30 recreated (29 run + C30 from F13); 15 out of scope; 6 kernel-checked theorems + 2 novel.
