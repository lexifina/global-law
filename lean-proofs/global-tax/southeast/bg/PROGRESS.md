# Bulgaria (BG): PROGRESS

Updated: 2026-11-19 (milestone 4: all 7 steps done; status done)

Status: done 7/7. Next step (optional): EUROMOD BG country report as a second referee; 2024 parameters to validate the 2024
Eurostat lines; harness integration once `"BG"` is in `~/cmp20/harness/common20.py` (rerun the shared scanners).

## Files
- Model: `lean/` (lib BgTax, exe `bgtax`; Params, Social, Tax, Benefit, Household, Main, Theorems, Tests, Findings).
  701 lines, 73 definitions, 36 theorems/examples, 0 sorry. Money in stotinki; output leva with 2 decimals (PT-style writer).
- Validation: `harness/eurostat_check.py` -> `results/validation_eurostat_2025.json`: Eurostat earn_nt_net 2025 (EU-OECD
  tax-benefit model), 13 household types x 4 lines (SOC, TAX, FAM, NET) = 52; exact (<= 1 лв.) 44, within 1 % 50. The 8 others
  are explained: F1 (Eurostat uses the April ceiling 4 130 лв. for January-March: AW125, AW167) and F2 (Eurostat uses the April
  allowance limit 760 лв. for January-March: one-earner couple with 2 children). Eurostat's BG "NAC" series is in EUR (identical
  to its EUR series): converted at 1.95583.
- Searches: `harness/scan.py` (metr, unit, owner, second, timing, selfmin) -> `results/search/*.json`.
- FINDINGS.md (F1-F12), CATALOGUE.md (K1-K9), USEFUL.md, results/summary.json, elections.json (empty: no election changes the
  tax; the child relief is shared, proved `splitRelief_total`).

## Modelling choices (all in the Lean docstrings)
- Individual taxation, 10 % flat (ЗДДФЛ чл. 48); bases per source (чл. 24-25, 29-30, 31-32); reliefs чл. 19 (10 %), чл. 22 (5 %),
  child relief 6 000/12 000/18 000 лв. (ЗДБРБ 2025 ПЗР § 3), shared by the parents (чл. 22в, ал. 4).
- Dividends 5 % final (чл. 38, 46); EU bank interest and regulated-market gains exempt (чл. 13, ал. 1, т. 8, т. 3); pensions exempt (т. 6).
- Employee contributions 13.78 % per month, monthly ceilings 3 750 лв. (Jan-Mar) / 4 130 лв. (Apr-Dec) (ЗБДОО 2025 чл. 9),
  per fund half up to the stotinka; born before 1960: 8.78 % pension, no UPF (same total).
- Free profession: 25 % statutory expenses; self-insured 27.8 % on the year's taxable income clamped to [12 492, 48 420] лв.
  within the room left by employment (КСО чл. 6, ал. 8, 9, 11); GIM optional, not taken; pensioners not insured (чл. 4, ал. 6).
- Child allowance (ЗСПД чл. 7, ЗДБРБ 2025 чл. 64): steady-state income test per member, 710/760 full and 810/860 80 % limits,
  month by month; school grants 300 лв. (grades 1-4, grade 8; universal). Canonical child age = age on 1 Jan 2025.

## Company side for the owner-manager scan (proposed entry; INBOX line appended)
CIT 10 % (ЗКПО чл. 20: "Данъчната ставка на корпоративния данък е 10 на сто"); dividend tax 5 % final, withheld (ЗДДФЛ чл. 38,
ал. 1, чл. 46, ал. 3; ЗКПО чл. 194, 200 for companies); employer contributions 18.92 % up to the employee ceiling (pension 8.22,
UPF 2.8, GIM 2.1, unemployment 0.6, work accident 0.4-1.1 (0.4 used), health 4.8; ГВРС 0 % in 2025, ЗБДОО 2025 чл. 15, ал. 1);
the owner's dividend reaches bgtax as `dividends` (5 % final, outside the annual base). A working owner must be insured
(КСО чл. 4, ал. 3, т. 2: self-insured, minimum 12 492 лв. a year, 27.8 %) or under a management contract (чл. 4, ал. 1, т. 7).

## Sources (saved)
- `law/zddfl_ciela_2026-11.txt` (ЗДДФЛ consolidated, Ciela free zone, https://www.ciela.net/svobodna-zona-normativi/view/2135538631/;
  2025 wording read from the dated amendment notes); `law/kso_082026.txt` (КСО, NRA docx 08/2026); `law/zzo_*`, `law/zspd_*`,
  `law/zkpo_*` (Ciela); `law/zdbrb2025_pzr.txt` (ЗДБРБ 2025 ПЗР); `law/zdbrb2025_art64_family.txt`.
- Corpus (github.com/lexifina/bulgaria-law, sparse clone `refs/bglaw`): ЗБДОО 2025 `zakon/2025/dv025-166102` (чл. 9, 14, 15),
  ЗБНЗОК 2025 `zakon/2025/dv025-166101` (чл. 2: 8 %), ЗДБРБ 2022-2026 `zakon/2022/dv018-164015`, `zakon/2023/dv066-164945`,
  `zakon/2023/dv108-165235`, `zakon/2025/dv026-166100`, `zakon/2026/dv069-167157`; extension acts `zakon/2025/dv006-165937`,
  `zakon/2025/dv113-166772`, `zakon/2026/dv052-167015`, `zakon/2026/dv057-167035`; euro act `zakon/2024/dv070-165589` (§ 35:
  ЗДДФЛ чл. 48, ал. 8 "всеки пълен лев" -> "всяко пълно евро"); ПМС 359/2024 `postanovlenie/2024/dv090-229729` (1 077 лв.).
- Global law: ЗДДФЛ only as promulgated (FINDINGS F12); the gl.py calls returned HTTP 429 (shared rate limit) early on, so the
  public corpus repository was read directly.
- Referee: `refs/eurostat/earn_nt_net.json` (https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/earn_nt_net?geo=BG),
  flattened `refs/eurostat/eurostat_bg.json`.

## Budget
Web searches used: 1/3 (owner-manager / known schemes, CATALOGUE sources S1-S5).
