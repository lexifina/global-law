# Belize (BZ) findings, B13-caribbean (2026-11-20T07:27Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory amount (official secondary where marked), so 1 'AW' there is that amount, not an average wage).

### F1 A total income of exactly BZ$29,000 is chargeable with no basic deduction: tax BZ$7,250, against BZ$0 at 28,999 and BZ$1 at 29,001
- kind: statute-fault
- Act 40 of 2024 s. 4: the basic deduction is allowed when total income 'exceeds twenty-nine thousand dollars', and s. 16(2) exempts total income 'less than twenty nine thousand dollars'. Exactly 29,000 is in neither clause, so 25 % falls on the whole 29,000. Read literally (the model): net income 28,022 at 28,999, 20,773 at 29,000, 28,023 at 29,001 (exe). One word ('or equal to') fixes it.
- provisions: I&BT Act s. 16(1),(2) as replaced by Act 40 of 2024 s. 4
- Lean: BzTax.taxCents (#guard 29,000 -> 725,000 cents)
- status: modelled; scanner notch 7,249 at 28,999

### F2 Between BZ$29,000 and BZ$32,000 of income every extra dollar is taxed at 100 %
- kind: loophole-known
- The phase-in credit (2,250 less 75 % of the excess over 29,000) withdraws 75 cents per dollar on top of the 25 % rate: tax 1 at 29,001, 1,000 at 30,000, 3,000 at 32,000; net income stays at BZ$28,023 across the band (exe). The design avoids a notch at 29,000 but leaves a 3,000-dollar band where a raise is worth nothing (Social Security aside).
- provisions: I&BT Act s. 16(1) proviso (Act 40 of 2024 s. 4)
- Lean: BzTax.phase_in_100 (theorem)
- status: modelled; scanner bands above top rate

### F3 Wives are taxed as part of their husbands' income unless both elect: aggregation would cost one basic deduction
- kind: loophole-known
- s. 19(1): 'The income of a married woman living with her husband shall ... be deemed to be the income of the husband', unless 'she and her husband so jointly elect' (s. 19(3)(a)). Aggregated, a two-earner couple gets one 20,000 deduction. The model takes the election (separate) by default; input bzJoint aggregates.
- provisions: I&BT Act s. 19(1), (3)(a)
- Lean: BzTax.out (bzJoint)
- status: modelled as an election

### F4 Since 2025 the self-employed pay no income tax on chargeable income, only business tax on receipts
- kind: loophole-known
- New s. 6(2): 'no tax shall be charged upon the chargeable income of any person other than an employed person'. Employment versus self-employment is the first choice that matters for tax in Belize (business tax not modelled).
- provisions: I&BT Act s. 6(2) (Act 40 of 2024 s. 3)
- Lean: -
- status: catalogued

### F5 The Social Security employee share falls as a percentage of pay: 1.69 % at the bottom, 3.91 % at the top class, the employer paying the rest
- kind: model-fix
- Collection of Contributions Regulations Schedule Table 2 column (7): employed person's rate 1.69 % for weekly earnings under $140, rising to 3.91 % for $460 and over; insurable earnings stop at $480 a week. The table only steps: earnings inside a row pay the row's fixed amount.
- provisions: SS (Collection of Contributions) Regs reg. 6, Schedule Table 2
- Lean: BzTax.ssWeek
- status: modelled

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Be self-employed rather than employed (business tax on receipts instead of 25 % income tax) | not modelled: F4 | I&BT Act s. 6(2) |
| K2 | Keep total income just below 29,000 or leave the 29,000-32,000 band entirely | recreated: F1, F2 | I&BT Act s. 16 |
| K3 | Married couples elect separate assessment (two basic deductions) | recreated: input bzJoint | I&BT Act s. 19(3)(a) |
| K4 | Interest on savings is exempt; the 5 % final tax on time deposits was repealed | not modelled | I&BT Act s. 8(1)(m); Act 40 of 2024 s. 5 |
| K5 | Pensions and Government gratuities exempt | not modelled | I&BT Act s. 8(1)(q),(t) |

## Step 5: what was searched

- kernel scanners with scale 29,000 (s. 16(2) threshold)
- exe checks at 28,999 / 29,000 / 29,001 / 32,000
- every Act of 2021-2026 in the Global law record whose title names a tax or social security (list in PROGRESS)
- statutory instruments 2020-2026 for a notice declaring the Table 3 period (none found)

## Literature not checked (no web-search budget this session)

- IMF Article IV staff reports and technical-assistance reports for the Caribbean (tax policy diagnostics, CARTAC papers)
- CARICOM / OECS / ECCB papers on income-tax harmonisation and social-security reform in the Eastern Caribbean
- Big-four worldwide personal tax guides (EY, PwC, KPMG, Deloitte) for each country
- Inter-American Development Bank and CIAT/ECLAC (CEPAL) studies of personal income tax in Latin America and the Caribbean
- Academic work on Caribbean PAYE design, social-security contribution ceilings and the effect of thresholds on low earners
- Official tax calculators and withholding tables (referee material for the dataset phase: deliberately not read)

Novelty: every finding above is reported as 'not found in the statute texts and official pages read for this country (listed in PROGRESS.md)'; none of the literature above was searched, so none is claimed new.

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | statute-fault | confirmed | 7,250 BZD of tax at exactly 29,000 (0 at 28,999, 1 at 29,001). exe and #guard L1BZ.F1; re-found by the fresh scan. Evidence: exe + Lean `L1BZ.F1` (`world/loopholes/rest/lean/L1BZ.lean`, 2 #guard): tot(b)-tot(a) = 7250; tot(c)-tot(a) = 1; statute re-read: `law/gl_act_2024_40.txt`. Known/new: **new**: The 29,000 threshold and phase-in are published (San Pedro Sun, The Reporter, Belize Tax Service calculator, Act 40 of 2024); no hit notes that exactly 29,000 falls in neither clause; web search 15. |
| F2 | loophole | model-proved | 2,999 BZD of tax on 2,999 more income between 29,001 and 32,000 (100 %). exe and #guard L1BZ.F2; model theorem. Evidence: exe + Lean `L1BZ.F2` (`world/loopholes/rest/lean/L1BZ.lean`, 1 #guard): it(b)-it(a) = 2999; model Lean: BzTax.phase_in_100. Known/new: **known**: The Belize Tax Service calculator (found by web search 15) states that net salary is kept at no less than 29,000 across the band: the 100 % band, described. |
| F3 | loophole | confirmed | 5,000 BZD more tax for a 40,000 + 40,000 couple if aggregated. exe and #guard L1BZ.F3. Evidence: exe + Lean `L1BZ.F3` (`world/loopholes/rest/lean/L1BZ.lean`, 1 #guard): it(b)-it(a) = 5000; statute re-read: `law/gl_cap55_8_16_19_21.txt`. Known/new: **unclear**: Separate assessment by election is the Act's own rule; not searched further. |
| F4 | loophole | explained | Self-employed outside income tax (s. 6 (2)); business tax not modelled. |
| F5 | fact | explained | SS table steps: the fresh scan's 106-113 notches. |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/BZ.json`): METR 5,000 % and notch 7,249 = F1 (also at 72,498 for couples); band 130 % above the top = F2; notches 106-113 = the SS weekly table steps (F5); timing 14,355 (49.5 % of the scale) = F1.
