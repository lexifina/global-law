# China (CN) findings, B02-g20 (2026-11-20T01:50Z)

Built from the statute only (no referee values seen). Leads from the B02 generic scan (`results/search/b02scan.md`).

### F1 Business income of a person with wages gets no 60,000 deduction
- kind: loophole-known
- 实施条例 art. 15: the 60,000 deduction against 经营所得 applies only to a person 'without 综合所得'; a person with both uses it once against wages. Income type matters: 300,000 of business income alone pays 37,500; as wages it pays 31,080 (before social insurance; both measured on the exe).
- provisions: IIT Law art. 6 (1), (3); 实施条例 art. 15
- Lean: CnTax.person
- status: modelled

### F2 Flat 20 % on dividends, rent and gains beside a 45 % top rate
- kind: loophole-known
- art. 3 (3): interest, dividends, rent and transfers at 20 % flat; income-type conversion from wages (up to 45 %) to dividends pays.
- provisions: art. 3
- Lean: CnTax.person
- status: modelled; preferential notices not applied

### F3 Generic scan: no notch, max METR 45 %
- kind: model-fix
- b02scan.
- provisions: -
- Lean: results/search/b02scan.md
- status: scan done


## Round W2 (improvement agent, 2026-11-20): pointers from the new software probes (coordinator)

### W2-1 The 专项附加扣除 are statutory for 2025 (delegated); standards not reached, no change
- kind: statute-note
- 个人所得税法 art. 6 (2018; cn/law/iit_law_2018.txt l. 46): "专项附加扣除，包括子女教育、继续教育、大病医疗、
  住房贷款利息或者住房租金、赡养老人等支出，具体范围、标准和实施步骤由国务院确定，并报全国人民代表大会常务委员会备案".
  The State Council's standards are therefore law for 2025 by delegation (they are filed with the NPCSC), not a
  convention: child education and infant care at 2,000 a month per child (the aaa-mvc probe) are the standards the
  model should apply. Not done: the notices (国发〔2018〕41号, 〔2022〕8号, 〔2023〕13号) were not reached in an
  official text this round (gov.cn paths guessed 404; Global law's China corpus holds no State Council notice on them).
  Modelling once read: children from `Canon.children` ages (under 3: 婴幼儿照护; 3 and over in education: 子女教育;
  the 18-24 student case needs a flag), each 100 % to one parent (the model's higher earner) or 50/50 as an election;
  elderly support, housing loan interest / rent, continuing education and serious illness as optional household inputs.
- provisions: 个人所得税法 art. 6; State Council notices (not read)
- Lean: CnTax.person (unchanged)
- status: open, for B02 with the notices' text

## Round W4 (improvement agent, 2026-11-20): W3 dev failures settled from the statute

### W4-1 专项扣除 (employee social insurance and housing fund) now deductible through inputs; Beijing's 2025 notice not reached
- kind: model-fix
- 个人所得税法 art. 6 (1) and para. 2: "专项扣除，包括居民个人按照国家规定的范围和标准缴纳的基本养老保险、基本医疗保险、失业保险等
  社会保险费和住房公积金等". Rates and contribution-base limits are local. Beijing HRSS (rsj.beijing.gov.cn) was read for a
  default city: its 10 June 2025 notice on declaring 2025 bases (law/w4/bj_2025_base_declare.html) says "2025年度各项社会
  保险缴费基数上下限将另行公布", and the separate 2025 notice was not found in the HRSS notice list (pages 1-30); the 2026
  notice (京人社发〔2026〕7号, 21 August 2026; law/w4/bj_2026_limits.html) sets 36,348 / 7,270 a month only "自2026年7月起".
  No cited 2025 default is possible, so the deduction is implemented with optional inputs `cnSocialRate`,
  `cnHousingFundRate` (basis points), `cnBaseCapMonthly`, `cnBaseFloorMonthly`; nothing deducted without them (as before);
  employeeSocial reports them. #guards. Dev unchanged (aaa-mvc 434 / 503; shinyChen 19 / 19, which deducts Beijing's
  contributions). Gap recorded: the 2025 Beijing (or another city's) base notice and the employee rates.
- provisions: 个人所得税法 art. 6
- Lean: CnTax.Special, CnTax.special (#guard)
- status: model changed (inputs); default city open

### W5R-1 专项附加扣除 for children (education and infant care) applied (W5 review pass 2, 2026-11-20)
- kind: model-fix
- Pointer (not the reason): 30 W5 CN grids had every miss above the tool by 24,000 x a marginal rate per child
  (10,800 / 21,600 / 32,400 = 45 % x 24,000 x 1-3 children). The tools' adapters enter 2,000 yuan a month per child; the
  model had flagged the State Council standards as not reached. Cause: model gap.
- Texts (gov.cn, fetched 2026-11-20, `law/w5/`): 个人所得税专项附加扣除暂行办法 (国发〔2018〕41号, content_5351181.htm, sha256
  328e8a38…) 第五条 "纳税人的子女接受全日制学历教育的相关支出，按照每个子女每月1000元的标准定额扣除 ... 年满3岁至小学入学前处于
  学前教育阶段的子女，按本条第一款规定执行", 第六条 "父母可以选择由其中一方按扣除标准的100%扣除，也可以选择由双方分别按扣除标准的
  50%扣除", 第二十五条 (claimed by submitting the information); 国发〔2022〕8号 (content_5682013.htm, sha256 e37186ad…) 一、二
  (3岁以下婴幼儿照护 per child, same election, from 2022-01-01); 国发〔2023〕13号 (content_6901206.htm, sha256 e357548e…) 一、二
  ("由每个婴幼儿每月1000元提高到2000元", "由每个子女每月1000元提高到2000元"), 五 ("自2023年1月1日起实施").
- Change: 24,000 a year per child aged 0-17 (under 3: infant care; 3+: education, taken as in education); the 第六条 election
  is the household's least-tax allocation (all to one adult, the other, or halves for a married couple); input
  `cnChildAlloc` (0 / 1 / 2) fixes it; input `cnChildDeduction` = false (default true) models a household that claims none
  (第二十五条). For a person with no 综合所得 the amount reduces 经营所得 (实施条例 art. 15). #guards (300,000 with two
  children: 21,480; without: 31,080). Elderly support etc. still not applied (no inputs).
- Checks: on 36,856 households (300 random + every W5 CN dev case) the outputs change only where there are children (0
  changes without children), never upwards; with `cnChildDeduction: false` all 36,856 equal the pre-fix exe. Rescanned
  (`world/tools/scan_world.py CN`, no notch or >100 % band); world/data/inputs.json refreshed (tools/world_meta.py).
- Local dev rerun (W5b frozen exe -> current exe, statute, exact / covered): most flagged grids ~40 % -> ~100 % (e.g.
  tax_calculator_pro 411 -> 1,046 / 1,049; avimitin 452 -> 1,029 / 1,029; tax_calc_d9g 478 -> 1,081 / 1,081; aaamvc (W1)
  434 -> 1,050 / 1,052). **Regressions (reported, test-side):** payroll_kit_zhiyilang 1,064 -> 399, taxcalcpy_ynkcc 1,042 ->
  430, taxcalculate_lauok 1,044 -> 433: their adapters enter no children (the tools have no such input), so they now
  measure the tools' lack of the deduction; rebuild requests with `cnChildDeduction: false` (software/world/w5_extra/
  MAPPING_W5_EXTRA.md). pytax 19 -> 30, pay_cal_hc2088 22 -> 28: the remaining misses are the tools' fixed 3-yuan monthly
  critical-illness item (declared). beijing kinoward 30 -> 39: declared partial line (two half-year base bounds, the 3 yuan,
  one child per group).
- provisions: 个人所得税法 art. 6; 国发〔2018〕41号 第五条, 第六条, 第二十五条; 国发〔2022〕8号; 国发〔2023〕13号
- Lean: CnTax.childMonthly, childAnnual, person (extra), out (allocation) (#guard)
- status: model changed

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | loophole | confirmed | 6,420 CNY on 300,000 (37,500 as business income vs 31,080 as wages). exe and #guard L1CN.F1. Evidence: exe + Lean `L1CN.F1` (`world/loopholes/rest/lean/L1CN.lean`, 2 #guard): it(a) = 37500; it(b) = 31080; statute re-read: `law/iit_reg_2018.txt`. Known/new: **unclear**: Crossref only; the rule is in 实施条例 art. 15 and is likely in Chinese practitioner guides, not searched. |
| F2 | loophole | confirmed | 200,000 CNY of tax on 1 M of dividends vs 243,080 on 1 M of wages. exe and #guard L1CN.F2. A published flat rate: the pattern is the dual/schedular income tax. Evidence: exe + Lean `L1CN.F2` (`world/loopholes/rest/lean/L1CN.lean`, 2 #guard): it(a) = 200000; it(b)-it(a) = 43080; statute re-read: `law/iit_law_2018.txt`. Known/new: **known**: pattern: flat or final tax on capital income beside a progressive labour tax (Dual Income Taxes: A Nordic Tax System, 10.4337/9781849804998.00012); the rates are published. |
| F3 | record | explained | Record (model-fix): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W2-1 | record | explained | Record (statute-note): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W4-1 | record | explained | Record (model-fix): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W5R-1 | loophole | confirmed | 9,600 CNY a year for a couple 300,000 + 50,000 with two children when the lower earner claims. exe and #guard L1CN.W5R1: the model takes the least-tax allocation; the wrong one costs 9,600. A choice the statute offers (claimant election). Evidence: exe + Lean `L1CN.W5R1` (`world/loopholes/rest/lean/L1CN.lean`, 1 #guard): tot(b)-tot(a) = 9600; statute re-read: `law/w5/content_5351181.htm`. |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/CN.json`): income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings (= F2).
