# Djibouti (DJ) findings, B08-central-africa-fr (2026-11-20T04:05Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory band threshold, so 1 'AW' there is that amount, not an average wage).

### F1 Monthly tax with no annual reconciliation: paying the year's salary unevenly can more than double the tax
- kind: loophole-known
- CGI art. 15 applies the barème to each month's pay. 2 400 000 FD paid as 200 000 a month: 348 000; paid in one month: 776 000 (#guard). A 45 % top band from 2 M a month makes bonuses expensive. The generic timing scanner spreads each annual amount evenly over the months, so it cannot see this effect; the #guard proves it.
- provisions: CGI art. 15
- Lean: DjTax.itsMonth (#guard)
- status: proved by #guard

### F2 The 2022 rewrite dropped the rule that only monthly pay above 50 000 FD is taxed
- kind: statute-fault
- LF 2021 art. 6 made art. 15 apply 'aux rémunérations mensuelles imposables, supérieures à 50.000 FD'; LF 2022 art. 7 'modifié comme suit' lists only the rates. Read literally, every franc of pay is now taxed from 2 %; if the 2021 sentence still applies, 50 000 a month is tax-free and 50 001 pays 3 000 (a notch). The model takes the literal 2022 text; input itsThreshold50000 gives the other reading.
- provisions: CGI art. 15 (LF 2021 art. 6, LF 2022 art. 7)
- Lean: DjTax.itsMonth (#guard both readings)
- status: reading recorded

### F3 The top rate rose from 40 % to 45 % in 2022 and the 20 % band was split into 22 % and 25 %
- kind: model-fix
- Compare LF 2021 art. 6 and LF 2022 art. 7.
- provisions: CGI art. 15
- Lean: DjTax.sched
- status: recorded

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Smooth pay across months (no annual reconciliation) | recreated: #guard, F1 (not by the annual timing scanner) | CGI art. 15 |
| K2 | Severance pay: 1 500 000 FD abatement | not modelled | CGI art. 5 al. 5 (LF 2022 art. 6) |
| K3 | Split income with a spouse (individual monthly tax) | recreated: split-gain scanner | CGI art. 15 |

## Step 5: what was searched

- kernel scanners via scan_world.py (scale 7.2 M = 600 000 x 12)
- finance laws 2017-2026 on journalofficiel.dj for 'traitements et salaires' / art. 15
- bunching (#guard)

## Literature not checked (no web-search budget this session)

- OECD/ATAF/AUC 'Revenue Statistics in Africa' country notes (CM CG CD MG among the covered countries)
- IMF Article IV and technical-assistance reports on the CEMAC members, DRC, Madagascar, Burundi, Djibouti, Comoros
- CEMAC directives on the harmonisation of direct taxation (IRPP/IS) and the CIMA/CIPRES social-security rules
- Big-four worldwide personal tax guides (EY, PwC, KPMG, Deloitte) for each country
- droit-afrique.com and juriafrique compilations (droit-afrique answered 403 to scripts and the laptop; not bypassed)
- Academic work on family quotients in francophone Africa and on informal-sector minimum taxes

Novelty: every finding above is reported as 'not found in the statute texts and official pages read for this country (listed in PROGRESS.md)'; none of the literature above was searched, so none is claimed new.

### W5A-1 Employee contribution added (W5 pattern A, second sweep, 2026-11-20)
- kind: model gap fixed (official secondary)
- provisions: CNSS page "Déclaration et versement des cotisations" (cnss.dj, published 04/12/2016, Internet Archive capture 2024-07-13); official secondary. The same page also calls the soins contributions employer-only; the specific 5 % / 2 % sentence is followed
- CNSS salarié 4 % retraite + 2 % soins = 6 % of all remuneration, reported, not deducted (CGI arts. 1-14 not reached); input cnssEmployee still overrides. Before W5 the model booked no such contribution (rate not reached); the W5 sweep flagged it (IMPROVE_W5 pattern A, w5/pa/SWEEP.md). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Not covered: CNSS soins 2 % worker share: the CNSS page is internally inconsistent (also "à la charge exclusive de l'employeur"); CGI deductibility not reached; 20 000 FD plancher not applied. Sources under `law/w5/` with SHA256SUMS.
- status: fixed

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/DjTax/Verify.lean` (imported by the `DjTax` library and built; each guard evaluates `DjTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/DJ.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | confirmed | Monthly ITS with no annual reconciliation: 2.4 M paid as 12 x 200,000 bears 348,000, in one month 776,000. G: f1_monthly_final (model #guard). S: CGI art. 15 (LF 2022 art. 7) as cited by the model; law/lf2025.txt:467 (withholding 'à la source' on monthly pay). Rescan timing_monthly: 4 'AW' in one month costs 3,344,000 more. |
| F2 | lead | Whether the 50,000 FD monthly threshold of LF 2021 survives LF 2022: reading (input itsThreshold50000; under it a 3,000 notch at 50,001). |
| F3 | explained | Rate changes 2022: record. |
| W5A-1 | explained (record of model/test work, not a loophole; kept as written) |  |
| Leads | explained | Rescan annual scans flat; F1 is in timing_monthly. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F1: Monthly ITS without annual reconciliation | timing or bunching | **new**: Nothing found (no PwC page for the country; OpenAlex: nothing on Djibouti's ITS). | 2026-11-20: OpenAlex specific queries 'Djibouti impôt sur les traitements et salaires barème mensuel'; 'Djibouti personal income tax wages' (1199 hits, titles checked); OpenAlex broad 'Djibouti personal income tax', 'Djibouti income tax wages', 'Djibouti tax system reform' (75 records, titles and abstracts grepped, 2 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries: no page for this country; Crossref IMF prefix 10.5089 'Djibouti tax policy' (8204 records, titles only). Record: world/loopholes/africa_mena/search/DJ-F1.json |

<!-- L1-VERIFICATION END -->
