# Morocco (MA) findings, B06-mena (2026-11-20T05:30Z)

Built from the statute only (no referee values seen). Catalogue built from the statute's own features (no literature search: the session's web-search budget is zero); 'known' = a planning route the statute itself creates and that advisers in any system use; novelty is not claimed.

### F1 Notch at 78,000 dirhams of gross pay: one dirham more costs 780
- kind: loophole-new
- Art. 59-I-A gives 35 % professional expenses when gross annual taxable pay does not exceed 78,000 and 25 % (cap 35,000) above: the deduction falls from 27,300 to 19,500 at 78,001, so taxable income jumps by 7,800 and tax by 780 (Lean #guard taxOn (netSalary 78000) = 1070, 78001 -> 1850). Net pay falls until gross reaches about 85,800; generic scan: METR 507 % at 1.0 AW, notch 779 (single), 349 (one-earner couple), the same at 195,001 for a two-earner couple. Avoid: keep gross at 78,000 and take the rest as exempt allowances or in kind (excluded from the 35 % base).
- provisions: art. 59-I-A (LF 50-22 for 2023)
- Lean: MaTax.fraisPro, #guard
- status: proved

### F2 Bunching around the 78,000 notch
- kind: loophole-new
- Timing scan: moving pay between two years so that one year stays at 78,000 saves up to 780 (1.0 % AW).
- provisions: art. 59-I-A
- Lean: results/search/timing.md
- status: measured

### F3 Family reduction for the wife even when she earns
- kind: statute-fault
- Art. 74-II-A lists 'son épouse' as a dependant without the income condition the article sets for children; read literally a husband claims 500 for an earning wife, who also has her own return. Modelled literally (reading).
- provisions: art. 74-II
- Lean: MaTax.out
- status: reading

### F4 Non-refundable family reduction is lost at low pay
- kind: loophole-known
- The 500-3,000 reduction is deducted from the tax; with tax below it the rest is lost (kernel applyCredits_waste pattern).
- provisions: art. 74-I
- Lean: MaTax.out
- status: recorded

### F5 Schedular rents and capital income
- kind: loophole-known
- Art. 73-II taxes rents (10 %/15 %) and dividends/interest at flat rates apart from the 37 % barème: income-type choice for owner-managers (not modelled).
- provisions: art. 73-II
- Lean: -
- status: catalogued

### F6 Supplementary pension contributions deductible
- kind: loophole-known
- Art. 59-II: contributions to Moroccan retirement schemes are deducted from salary (salary sacrifice into pensions). Catalogued from the statute; not in the canonical household.
- provisions: art. 59-II
- Lean: not modelled
- status: catalogued

### F7 Social-housing loan repayments deductible
- kind: loophole-known
- Art. 59-V: principal and interest (or Mourabaha/Ijara margins) on a social home deducted from salary. Catalogued from the statute; not in the canonical household.
- provisions: art. 59-V
- Lean: not modelled
- status: catalogued

### Generic scan (scale 78000, `results/search/SUMMARY.md`)
- kind: model-fix
- single: max METR 507.1 %, 1 bands > 100 %, notch 779 at 78,000 (1.0 AW); couple_1earner_2: max METR 231.4 %, 1 bands > 100 %, notch 349 at 78,000 (1.0 AW); couple_2earner_2: max METR 516.0 %, 2 bands > 100 %, notch 779 at 195,001 (2.50001 AW); second_earner_2: max METR 507.1 %, 1 bands > 100 %, notch 779 at 78,000 (1.0 AW)

## Round D6 (improvement agent, 2026-11-20): holdout gaps checked against the statute (aggregates only)

### D6-1 Pensions: art. 60-I abatement and the 2025 transitional 50 % reduction (model fix)
- kind: model-fix
- CGI 2025 art. 60-I: pensions and life annuities after "un abattement forfaitaire de : - 70% sur le montant brut qui ne
  dépasse pas annuellement 168 000 dirhams ; - 40% pour le surplus"; art. 57-27° (exemption of basic-scheme pensions,
  LF n° 60-24 for 2025) applies to pensions acquired from 1 January 2026 (LF 60-24 art. 8-III-8°), with the transitional
  rule for 2025: basic-scheme pensions "bénéficient d'une réduction de 50% du montant de l'impôt dû au titre desdites
  pensions ... acquises au titre de l'année 2025". Art. 73-I's 2025 schedule (exempt to 40 000) was already in the model.
  The model taxed no pension at all (flagged), hence 0 on the circular's 240 000 example.
- Change: `netPension` (art. 60-I) enters net income with salaries (art. 56); `pensionReduction` takes 50 % of the
  pension's share of the tax due (after family reductions), for basic-scheme pensions unless `maPensionComplementary`;
  #guards: 240 000 -> abatement 146 400, net 93 600, tax 10 080, after the 2025 reduction 5 040.
- Residual against the circular's 3 820 (sealed; not traced): the pensioner's art. 59 III / IV contributions (AMO and
  similar) are deducted before the abatement under art. 60-I and are not modelled (their rates were not read); a base
  about 13 500 lower would give 3 820 with no dependants. Next: read the pensioners' AMO rate.
- status: model changed; contributions open

## Round D7 (improvement agent, 2026-11-20)

### D7-1 Pension example residual: no further statute basis found in the CGI
- kind: test-note
- Re-read: art. 60-I (70 % to 168 000, 40 % above; LF 70-19 / 50-22 for the 70 %), art. 73-I (2025 schedule), art. 74
  (family reductions), LF 60-24 art. 8-III-8° (2025 50 % reduction) - all applied (model 5 040 on the 240 000 example).
  Art. 60-I deducts "les cotisations et primes visées à l'article 59 (III et IV)" before the abatement: the pensioner's
  compulsory health insurance (AMO) and similar contributions. Their rates are not in the CGI (AMO law 65-00 and its
  decrees; not in Global law's Morocco corpus, not reached this round). The circular's 3 820 back-solves to a
  pre-abatement base of about 226 450 (contributions of about 5,6 % of 240 000), which fits such contributions, but no
  dated rate could be cited, so no change. Next: the AMO decree's pensioner rate (CNSS / CMR / RCAR).
- status: open

### W5S-1 salary-simulator (justsimpletools; wronglaw grid): IR never positive (W5 review pass 3, 2026-11-20)
- kind: software-error
- `ma_open_salary_simulator_justsimpletools_grid`: calculateIR returns Math.min(0, ir), so the IR is 0 or negative for every household (59,156: -3,776.43; above about 200,000: 0 against the model's 36,474 and more); 296 / 1,062 exact (all zero-tax cases).
- provisions: CGI art. 73-I barème (LF 60-24 art. 8)
- status: recorded (world/IMPROVE_W5.md pass 3, wronglaw table)

### W5A-1 Employee contribution added (W5 pattern A, second sweep, 2026-11-20)
- kind: model gap fixed (official secondary)
- provisions: CNSS page "Paiement de vos cotisations sociales", section "Barèmes et taux de cotisation" (Internet Archive capture 2025-03-25) and notice "AMO Ajustement des taux de cotisation" (AMO 2,26 % from 1 January 2016); official secondary (décret 2-01-2723 as amended and the AMO décrets not reached); CGI 2025 art. 59
- CNSS employee 0,52 % + 3,96 % on wages up to 6 000 MAD a month and AMO 2,26 % on the whole wage, all deducted (CGI art. 59-II-A, III). Before W5 the model booked no such contribution (rate not reached); the W5 sweep flagged it (IMPROVE_W5 pattern A, w5/pa/SWEEP.md). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Not covered: CNSS / AMO rates from the CNSS page (official secondary; the décrets not reached). Sources under `law/w5/` with SHA256SUMS.
- status: fixed

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/MaTax/Verify.lean` (imported by the `MaTax` library and built; each guard evaluates `MaTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/MA.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | confirmed (dead zone corrected) | One dirham above 78,000 of gross costs 779 of net (frais 35 % -> 25 %), single or one-earner couple; net is back above its 78,000 level by about 78,880 (not 85,800 as written: W5 contributions and the 10 % band make the recovery quick). G: f1_notch_78000, f1_notch_couple, f1_notch_recovered. S: law/cgi2025fr.txt:4398-4407 (art. 59-I-A: '35% ... dont le revenu brut annuel imposable n'excède pas soixante dix huit mille (78 000) dirhams. Ce taux est fixé à 25% ... supérieur ... sans que cette déduction puisse excéder trente-cinq mille (35 000) dirhams'). |
| F2 | confirmed | Timing consequence of F1: rescan bunching gain 798 (1.02 % of the 78,000 scale) single at 1.002 +- 0.112 'AW'. Same statute and guard as F1. |
| F3 | lead | Reading (wife as dependant without an income test, art. 74-II); modelled literally; rescan marriage bonus 500 at 1.0 'AW' is this reading. |
| F4 | explained | Non-refundable reduction wasted at low pay: the kernel's applyCredits_waste pattern; not a loophole. |
| F5 | explained | Schedular rents/capital income: not modelled (rescan wedges for these types are model gaps). |
| F6 | explained | Catalogued (pension contributions deductible). |
| F7 | explained | Catalogued (social-housing loan). |
| Generic scan | explained | Superseded by the L1 rescan 2026-11-20 22:44 CET (world/tools/scan_world.py --full, current exe; results/search/SUMMARY.md). |
| D6-1, D7-1, W5S-1, W5A-1 | explained (record of model/test work, not a loophole; kept as written) | W5 CNSS/AMO present in the current exe (4,987 at 78,000). |
| Leads | explained | Rescan notches at 78,000 (single) and 195,001 (two earners) = F1; nothing else above 0.05 % of scale. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F1: Professional expenses fall from 35 % to 25 % at 78,000 MAD of gross pay | cliff or notch | **new**: PwC Morocco (Deductions) prints the rule ('MAD 35,000 for individuals whose gross annual taxable income does not exceed MAD 78,000 ... 25% ... exceeds MAD 78,000') but not the 779-dirham notch or the dead zone; OpenAlex: nothing. | 2026-11-20: OpenAlex specific queries 'Morocco professional expenses deduction 35% 78,000 dirhams'; 'Maroc frais professionnels 35% 78 000 dirhams impôt sur le revenu seuil' (12 hits, titles checked); OpenAlex broad 'Morocco personal income tax', 'Morocco income tax wages', 'Morocco tax system reform' (75 records, titles and abstracts grepped, 0 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries (morocco, 5 individual pages): 2 passages with the item's terms; Crossref IMF prefix 10.5089 'Morocco tax reform personal income tax' (3593 records, titles only). Record: world/loopholes/africa_mena/search/MA-F1.json |

<!-- L1-VERIFICATION END -->

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- mix.py (wage vs fee split): lead: the salary professional-expense deduction (capped) makes a partial salary worth more; small.
- ceilings.py: ceiling at 0.93 AW (contribution rate 6.7 -> 2.3 %, combined marginal 12 -> 9 %) (only with the W5 contributions). Lead (statutory ceiling/minimum base; known pattern). `results/search/ceilings.md`.
<!-- R2-SCANNERS:END -->
