# Algeria (DZ) findings, B06-mena (2026-11-20T05:30Z)

Built from the statute only (no referee values seen). Catalogue built from the statute's own features (no literature search: the session's web-search budget is zero); 'known' = a planning route the statute itself creates and that advisers in any system use; novelty is not claimed.

### F1 Rent notch at 1,800,000 DA: one dinar more costs 310,800
- kind: loophole-new
- Art. 104 II.2 (LF 2023 art. 5): gross rents up to 1,800,000 a year are taxed 7 % final; above, 7 % is only a prepayment on the global barème. 1,800,000 -> 126,000; 1,800,001 -> 436,800 (probe, barème on the whole rent). Landlords split leases between spouses (each has the threshold) or keep rents at 1.8 M.
- provisions: art. 104 II.2
- Lean: DzTax.rentIRG, probe
- status: measured

### F2 The 30,000-35,000 smoothing band: 62 % marginal rate
- kind: loophole-new
- Art. 104 II.3.a: pay up to 30,000 a month is exempt; from 30,000 to 35,000 IRG = IRG x 137/51 - 27,925/8, which phases the tax in at 23 % x 137/51 = 61.8 % (63.3 % in the scan, single, 1.0-1.166 AW). Continuous (no notch) but a narrow high-METR band for low earners; timing scan: bunching gain up to 12,384 DA.
- provisions: art. 104 II.3.a
- Lean: DzTax.monthlyIRG, results/search
- status: measured

### F3 Retired workers' formula to 42,500
- kind: loophole-known
- A second formula (93/61 - 81,213/41) for retirees of the general scheme and disabled workers between 30,000 and 42,500: same pattern, lower slope.
- provisions: art. 104 II.3.a
- Lean: DzTax.monthlyIRG
- status: modelled (retirees)

### F4 Monthly withholding with abatement floor and cap
- kind: loophole-known
- The 40 % abatement is at least 1,000 and at most 1,500 a month, so it is worth more to irregular earners spread over more months.
- provisions: art. 104 II.3.a
- Lean: -
- status: catalogued

### F5 Re-enactment by 'sans changement'
- kind: statute-fault
- LF 2023 and LF 2025 rewrite art. 104 with most paragraphs as '(sans changement)': the in-force text must be assembled from LF 2022 + LF 2023 + LF 2025; no official consolidation for 2025 was reachable (the DGI's 2025 code PDF was not archived).
- provisions: art. 104
- Lean: -
- status: recorded

### F6 Share capital gains 15 % final, 5 % if reinvested
- kind: loophole-known
- Art. 104 II.5.b (LF 2025 art. 8): gains on shares 15 % libératoire, 5 % with a reinvestment undertaking: owner-managers can take value as gains rather than salary at up to 35 %. Catalogued from the statute; not in the canonical household.
- provisions: art. 104 II.5.b
- Lean: not modelled
- status: catalogued

### F7 Family home sale: 50 % reduction
- kind: loophole-known
- Art. 104 II.5.a (LF 2025 art. 8): the gain on the sale of a sole main home is taxed at half. Catalogued from the statute; not in the canonical household.
- provisions: art. 104 II.5.a
- Lean: not modelled
- status: catalogued

### Generic scan (scale 360000, `results/search/SUMMARY.md`)
- kind: model-fix
- single: max METR 63.3 %, 0 bands > 100 %; couple_1earner_2: max METR 63.3 %, 0 bands > 100 %; couple_2earner_2: max METR 45.0 %, 0 bands > 100 %; second_earner_2: max METR 63.3 %, 0 bands > 100 %

### W5A-1 Employee contribution added (W5 pattern A, second sweep, 2026-11-20)
- kind: model gap fixed (statute (JORADP))
- provisions: Décret exécutif n° 06-339 du 25 septembre 2006 modifiant le décret exécutif n° 94-187 (JO n° 60 of 27 September 2006, p. 16), arts. 1-2 (worker 9 % = 1,5 + 6,75 + 0,5 + 0,25, from 1 October 2006)
- CNAS worker 9 % of the contribution base (no ceiling), reported; NOT deducted from the IRG base (CIDTA not reached). Before W5 the model booked no such contribution (rate not reached); the W5 sweep flagged it (IMPROVE_W5 pattern A, w5/pa/SWEEP.md). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Not covered: CNAS 9 % deduction from the IRG base: CIDTA article not reached (mfdgi.gov.dz did not answer); later amendments of décret 94-187 not checked. Sources under `law/w5/` with SHA256SUMS.
- status: fixed

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/DzTax/Verify.lean` (imported by the `DzTax` library and built; each guard evaluates `DzTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/DZ.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | confirmed | One dinar of rent above 1,800,000 costs 310,799 of net income (7 % final -> barème on the whole rent). G: f1_rent_notch. S: law/jo/lf2023.txt:222-237 (LF 2023, art. 104 II.2: 'inférieur ou égal à 1.800.000 DA ... imposition' at 7 %; 'supérieur à 1.800.000 DA ... imposition provisoire au taux de 7% qui s'impute sur l'imposition définitive du revenu global'). |
| F2 | confirmed (amount corrected) | The x 137/51 smoothing formula taxes the first 12,000 a year above 360,000 at 7,044 (58.7 %; 67.7 % with the W5 CNAS 9 %), against a 35 % top barème rate. W5: the claim's 61.8 % / 63.3 % predate the CNAS line; the scanner now shows 72.4 % peak METR (avg 50.4 %) on 360,000-419,760. G: f2_phase_in_band. S: law/jo/lf2022.txt:680-687 ('IRG = IRG (selon le premier abattement) x (137/51) - (27 925/8)'). |
| F3 | explained | Retirees' second formula (93/61 - 81,213/41) to 42,500 a month: same pattern, lower slope. S: law/jo/lf2022.txt:688-690. Not separately guarded. |
| F4 | lead | Abatement floor 1,000 / cap 1,500 a month: the claimed advantage to irregular earners is not modelled (one even year). |
| F5 | explained | Re-enactment by '(sans changement)': visible in law/jo/lf2023.txt:232 ('sans changement jusqu'à'). |
| F6 | explained | Catalogued statute route (share gains 15 % / 5 %); not modelled, no money proved. |
| F7 | explained | Catalogued statute route (main-home gain halved); not modelled. |
| Generic scan | explained | Superseded by the L1 rescan 2026-11-20 22:44 CET (world/tools/scan_world.py --full, current exe; results/search/SUMMARY.md). |
| W5A-1 | explained (record of model/test work, not a loophole; kept as written) | CNAS 9 % present in the current exe (32,400 at 360,000). |
| Leads | explained | Rescan: bands above the top rate on 360,000-419,760 = F2; timing gain 12,444 (couple, two earners) = F2's band; split gain 106,800 at 4 'AW' = individual taxation; income-type wedges for interest/dividends/gains are model gaps (types untaxed in the model), not findings. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F1: Rent of 1,800,000 DA: 7 % final; one dinar more puts the whole rent on the barème | cliff or notch | **new**: No description found: no PwC page for the country; OpenAlex specific queries 0-2 unrelated records, 75 broad records on Algerian income tax none on rents. Whole-income thresholds are known in kind (Kleven and Waseem (2013), QJE 128(2), doi 10.1093/qje/qjt004 (whole-income rates and notches, Pakistan)). | 2026-11-20: OpenAlex specific queries 'Algeria rental income tax 1,800,000 dinars final 7%'; 'Algérie IRG revenus locatifs 1 800 000 DA imposition libératoire' (2 hits, titles checked); OpenAlex broad 'Algeria personal income tax', 'Algeria income tax wages', 'Algeria tax system reform' (75 records, titles and abstracts grepped, 1 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries: no page for this country; Crossref IMF prefix 10.5089 'Algeria tax policy personal income tax' (9158 records, titles only). Record: world/loopholes/africa_mena/search/DZ-F1.json |
| F2: The 30,000-35,000 DA a month smoothing formula (x 137/51) taxes the first slice at 58.7 % (67.7 % with CNAS) against a 35 % top rate | rate above the top rate | **new**: No description of the 58.7 % slice found (no PwC page for the country; OpenAlex: nothing on the 30,000-35,000 DA formula). | 2026-11-20: OpenAlex specific queries 'Algeria IRG wage exemption 30,000 dinars abatement marginal rate'; 'Algérie IRG salaires 30 000 35 000 abattement supplémentaire' (2 hits, titles checked); OpenAlex broad 'Algeria personal income tax', 'Algeria income tax wages', 'Algeria tax system reform' (75 records, titles and abstracts grepped, 1 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries: no page for this country; Crossref IMF prefix 10.5089 'Algeria tax policy personal income tax' (9158 records, titles only). Record: world/loopholes/africa_mena/search/DZ-F2.json |

<!-- L1-VERIFICATION END -->

## L1-S correction (2026-11-21)

F1 re-read against CIDTA art. 85 as rewritten by Loi n° 21-16 (LF 2022) art. 28 (`law/jo/lf2022.txt`): "Bénéficient
d'un abattement de 25%, les revenus fonciers issus de la location à usage d'habitation à retenir dans l'assiette de
l'impôt sur le revenu global" (art. 85 not amended by LF 2023, 2024 or 2025 on disk). The model put the whole rent on the
barème above 1,800,000; it now applies the barème to 75 % of it (`DzTax.rentIRG`, #guard `rentIRG 1800001 = 301800`;
`checks/DZ.json` and `Verify.lean` regenerated, `lake build` OK). F1's notch is **175,799 DA** of net income for one
dinar (126,000 -> 301,800 of IRG), not 310,799; still the region's largest per unit. Backups:
`world/loopholes/strengthen/backup/DzTax_*.bak-S1`.

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- **DZ-R1 (lead)** Model taxes salaries (monthly IRG) and BIC (annual barème) each on its own: 106,800 DZD less on 720,000 split. Money: 106,800 DZD in the model. Lean: `world/loopholes/round2/v/lean/R2DZ.lean` (R2DZ.R1 (4 #guard on the model)); exe check `round2/v/out/DZ.json`. Provision: CIDTA art. 104 I and II.1 (law/jo/lf2022.txt:626-655): BIC tax 'constitue un crédit d'impôt qui s'impute sur l'imposition du revenu global'. Status: lead: likely a model simplification, statute reading needed before any fix (for the strengthening agent). Known/new: not searched as a loophole (`round2/v/novelty/`).
- mix.py (wage vs fee split): lead, possible model error: art. 104 I taxes the global income on one barème and art. 104 II.1 makes the BIC tax a credit against it; the model taxes salaries and BIC each on its own.
<!-- R2-SCANNERS:END -->
