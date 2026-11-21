# KR (South Korea, 2025): progress

Status: **done** (all 7 CONTRACT20 steps). Updated 2026-11-19 ~06:10 UTC.

## Done / total: 7 / 7
1. Model + `krtax` exe + OECD validation — done
2. Proofs — done (51 theorems, no sorry, no native_decide; `#print axioms` shows only propext/Classical.choice/Quot.sound)
3. Known loopholes — done (`CATALOGUE.md`: 18 catalogued, 10 recreated, 3 modelled only, 5 not modelled)
4. New loopholes — done (kernel scanners `results/search/SUMMARY.md` + owner-manager script; F9-F11, F15)
5. Government errors — done (F1, F2, F5, F6, F8 gov-error; F3, F4 statute-fault). Priority item 간이세액표 vs statute:
   F8, all 7,106 cells checked by the kernel.
6. USEFUL.md — done (with draft notes to 기획재정부/국세청, 법제처, the OECD; none sent)
7. HOWWRITTEN.md — done

## Layout
- `lean/` Lake project `KrTax`, requires `~/cmp20/kernel` (TaxKernel) by path. Build: `export PATH=$HOME/.elan/bin:$PATH;
  cd lean; lake build` (about 25 s from clean files of this project) → `lean/.lake/build/bin/krtax`.
  Files: Basic (parameters + citations), IncentiveData / WithholdingData (machine-extracted tables; regenerate with
  `scripts/gen_incentive_data.py`, `scripts/gen_wht_data.py`, which add `set_option maxRecDepth`), Incentive, Social,
  Person, Household, Out, Main, Theorems, IncentiveProofs, Withholding, Walls.
- Korea-only input fields: `krClaimant` (0/1/"best"), `krStandard` ("auto"/"itemise"/"standard"), `krNoIncentives`,
  `krHomeCare` (양육수당), `krConvention: "oecd"` (validation only). `elections.json`: krClaimant 0/1 for the harness.
- `employeeSocial` includes the NHI premium on non-wage income (직장: above 2천만원; 지역: all, 이자·배당 only above 1천만원).
- scripts: `lawgo.py` (law.go.kr: hangul address → lsiSeq → POST LSW/lsInfoR.do; the DRF API refuses unregistered IPs),
  `retext.py`, `art.py`, `byl.py` (별표 PDFs), `parse_incentive.py`, `parse_wht.py`, `wht_fit.py`, `wht_model.py`
  (exact-fraction twin of Withholding.lean), `oecd_variant.py`, `owner_manager.py [--rental]`, `leanstats.py`.
- refs: `refs/lawgo/*` official texts by 공포번호 (소득세법 12169/19933/20615/current, 조특법 20617/21138, decrees),
  `refs/pdf/` 별표 PDFs + text, `refs/img/` (§55 and 2014 §59 table images), `refs/oecd/taxben.txt` (OECD TaxBEN Korea
  2025), `refs/krlaw` (shallow clone of github.com/lexifina/south-korea-law).

## Validation
- OECD TW 2025, harness children (6 and 11): 56 cases, 5 exact, 42 within 1 %; every difference explained (F1 children,
  F6/F7 social rounding).
- OECD with its own Korean conventions (children 6 and 7 at home, no 1,000-won truncation, LTC 12.95 %): 56 cases,
  49 exact, 56 within 1 % (max 3 won) — `results/oecd_check_variant.json`.
- Statute tables: 근로소득 간이세액표 7,098 / 7,106 cells = recovered rule (8 differ by 10 won); 근로장려금 산정표: every
  단독/맞벌이 cell = rule, 42 홑벌이 cells not; 자녀장려금 산정표: every cell = rule (kernel-checked).
- Not done: NTS 연말정산 worked examples / NTS calculators (not reached; the 간이세액표 check stands in for the official
  withholding computation).

## Spot runs cited in FINDINGS (krtax, single unless stated)
T40/T20/T0: wages 56,749,797 with dividends 40M/20M/0: net 79,604,711 / 64,286,351 / 47,366,351 (F15). PC9: same wages,
연금계좌 9M: tax 2,328,837 vs 3,678,837. L70a/b, L12a/b: wages 70.0M/70.32M, 120.0M/120.6M: net 57,499,205/57,567,767,
92,042,758/92,068,283 (F10).

## Open
- 신용카드 소득공제, 의료비/교육비/보험료 credits, 월세, 주택자금: no contract inputs (CATALOGUE K13-K16).
- 8 withholding cells (10 won) unexplained; the 지역 health premium's property part; 산재 premium in the owner script.
- The kernel's generic Contribution has no "floor raises the base" and no two ceilings per year (kernel_gaps).

## Web searches used: 4 of 6
