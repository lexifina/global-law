# Somalia (SO) findings, B10-anglophone-africa (2026-11-20T06:19Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory band threshold, so 1 'AW' there is that amount, not an average wage).

### F1 The new federal income tax table prints $1,788 at $18,000 where its own bands give $1,728: a $60 jump at $18,001
- kind: statute-fault
- Law No. 37/2025 First Schedule para. 1(1): row 3 '$288 USD plus 12% of the excess over $6000' (288 = 6 % x 4,800, consistent), row 4 '$1,788 USD plus 18%' of the excess over $18,000; 288 + 12 % x 12,000 = 1,728. Read as printed, a taxpayer with $18,001 pays $60.18 more than one with $18,000; every taxpayer above $18,000 pays $60 more than the bands imply. Kernel cumJumps proves the jump ([0, 0, 0, 60]). Model default: the printed table; input soBandReading gives the band reading.
- provisions: Law No. 37/2025 First Schedule para. 1(1)
- Lean: SoTax.printedTicks, SoTax.printedRows (#guard cumJumps)
- status: statute fault; scanner notch

### F2 Residents under 18 are taxed at a flat 20 % from the first dollar while adults have a $1,200 zero band
- kind: loophole-known
- Para. 1(2): taxable income of a resident under eighteen is taxed at 'boqolkiiba labaatan (20%) oo ah boqolleey siman' (a flat 20 %) unless the Ministry is satisfied the amounts meet the arm's length standard (art. 37). An anti-income-splitting rule; not modelled (the contract's adults are 18+).
- provisions: Law No. 37/2025 First Schedule para. 1(2)
- Lean: -
- status: catalogued

### F3 Gains and lump-sum retirement payments above $18,000 are taxed at 15 % instead of 18 %
- kind: loophole-known
- Para. 1(3): where taxable income includes gains or a lump-sum retirement payment, the part above $18,000 bears 15 % up to the amount of the gain or payment, the rest 18 %.
- provisions: Law No. 37/2025 First Schedule para. 1(3)
- Lean: -
- status: catalogued

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Take income as a gain or lump-sum retirement payment (15 % above $18,000) | not modelled | First Schedule para. 1(3) |
| K2 | Shift income to children (blocked: under-18 flat 20 %) | not modelled: anti-avoidance rule | First Schedule para. 1(2) |
| K3 | Keep taxable income at $18,000 rather than just above (printed-table notch) | recreated: F1 | First Schedule para. 1(1) |

## Step 5: what was searched

- kernel scanners with scale $18,000
- printed column checked with kernel cumJumps
- the Law's schedules located through its table of contents (JADWALLADA)

## Literature not checked (no web-search budget this session)

- OECD/ATAF/AUC 'Revenue Statistics in Africa' country notes (KE UG RW GH ET among the covered countries)
- IMF Article IV and technical-assistance reports (tax policy diagnostics) for each country
- African Tax Administration Forum (ATAF) and East African Community harmonisation papers on PAYE and social contributions
- Big-four worldwide personal tax guides (EY, PwC, KPMG, Deloitte) for each country
- Academic work on PAYE design, minimum contributions and informal-sector presumptive taxes in anglophone Africa
- ICTD / UNU-WIDER working papers (UNU-WIDER refuses scripts; SOUTHMOD not verifiable)

Novelty: every finding above is reported as 'not found in the statute texts and official pages read for this country (listed in PROGRESS.md)'; none of the literature above was searched, so none is claimed new.

## Round D6 (improvement agent, 2026-11-20): holdout gaps checked against the statute (aggregates only)

### D6-1 Gains on chargeable investment assets now taxed (First Schedule para. 1(3)): model fix
- kind: model-fix
- Law No. 37 of 2025, First Schedule para. 1(3) (OCR p. 138): when a resident individual's taxable income includes gains
  from disposing of chargeable investment assets (or a lump-sum retirement payment), taxable income up to $18,000 is
  taxed at para. 1's rates, and above $18,000 "(i) boqolkiiba shan iyo toban (15%), iyada oo aysan ka badan karin cadadka
  dhabta ah ee kororka faa'ido" (15 %, on no more than the actual gain) and "(ii) wixii dakhli ah ee intaas kabadan ...
  (18%)". Art. 6 (4): such gains (shares, non-resident trust interests, immovable property) are taxed on disposal;
  art. 14 counts them in investment income. The model ignored `capitalGains` (flagged), which explains a lower result
  on every manual example (employment plus a gain). Now `SoTax.taxWithGain`: the gain enters taxable income with the
  15 % slice; #guards (12,000 + 10,000 gain: 2,328; 30,000 + 5,000: 4,638). Without gains the model is unchanged (0 of
  300 random households differ). Lump-sum retirement payments are not a contract line (not modelled).
- status: model changed

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/SoTax/Verify.lean` (imported by the `SoTax` library and built; each guard evaluates `SoTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/SO.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | confirmed | The First Schedule prints $1,788 at $18,000 where its own bands give $1,728: one dollar above $18,000 costs $59 of net, and every taxpayer above pays $60 more than the bands. G: f1_printed_1788. S: law/law37_ocr.txt:5898 ('Dakhliga ka badan $18,000 USD $1,788 USD oo lagu daray'). |
| F2 | lead | Flat 20 % for residents under 18: not modelled (adults only). |
| F3 | lead | Gains and lump sums at 15 %: not modelled. |
| D6-1 | explained (record of model/test work, not a loophole; kept as written) |  |
| Leads | explained | Rescan notches of 59 at 18,000 (single) and 30,000 / 45,001 (two earners) = F1. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F1: The First Schedule prints $1,788 at $18,000 where its bands give $1,728 | cliff or notch | **new**: Nothing found (no PwC page for the country; OpenAlex not answered); a web search found the Ministry's Income Tax Manual (2025) and IMF reports but not the $1,788 figure. | 2026-11-20: OpenAlex queries 'Somalia income tax law 2025 rates federal'; 'Somalia personal income tax' not answered (free daily budget exhausted; search reduced); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries: no page for this country; Crossref IMF prefix 10.5089 'Somalia domestic revenue mobilization' (778 records, titles only); web search: WebSearch 2026-11-20 'Somalia income tax law 2025 rates $1,788 $18,000': archive.mof.gov.so Income Tax Manual (Nov 2025), sominvest.gov.so, IMF CR 2025; no $1,788 figure. Record: world/loopholes/africa_mena/search/SO-F1.json |

<!-- L1-VERIFICATION END -->
