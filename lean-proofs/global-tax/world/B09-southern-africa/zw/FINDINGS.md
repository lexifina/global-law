# Zimbabwe (ZW): findings, B09 build phase (2026-11-20T06:18Z)

Zimbabwe built from the 2024 Finance (No. 2) Act: ZiG employment bands 0-40 % plus a 3 % AIDS levy (41.2 % top), while individuals' trade income pays a flat 25 % (ZiG 2 m of trade income costs 515 000 vs 708 063 as wages); the rate table cites a paragraph (vii) that s. 14 (2) (a) does not have.

Scale for scanner numbers: 336,000 ZWG = threshold of the 30 % band (income earned in ZiG) (Finance Act Cap. 23:04 s. 14 (2) (a) (iv) as substituted by Finance (No. 2) Act 7 of 2024 s. 4); a statutory threshold, not an average wage.

### F1 Rate table cites a paragraph that does not exist
- kind: statute-fault
- Finance Act 13/2023 s. 3 (a) and Finance (No. 2) Act 7/2024 s. 5 print the top row as '14(2)(a)(vii) ZiG1 008 001 and more 40', while s. 14 (2) (a) as substituted by s. 4 of the 2024 Act has items (i)-(vi) only ('(vi) so much as exceeds one million eight thousand ZiG'). The same slip is in both years' tables: on a literal reading the 40 % rate is attached to no paragraph of s. 14 (2) (a).
- provisions: Finance Act Cap. 23:04 s. 14 (2) (a) and Schedule Part II (Acts 13/2023, 7/2024)
- Lean: ZwTax.sched
- status: found by reading

### F2 Trade income of individuals at a flat 25 % beside employment bands up to 40 %
- kind: loophole-known
- 14 (2) (b) 'Taxable income of individuals from trade or investment 25' (Act 13/2023). ZiG 2 000 000 as wages: 708 063 (tax + levy); as trade income: 515 000. Scanner (scale ZiG 336 000): self-employment +9.3 % of income at 5 x scale, but -13.4 % at 0.25 x scale (no zero band for trade income).
- provisions: Finance Act s. 14 (2) (a), (b)
- Lean: ZwTax.personTax
- status: recreated

### F3 AIDS levy makes the top marginal rate 41.2 %
- kind: fact
- 3 % of the income tax (Cap. 23:04 s. 14, 2018 consolidation); scanner peak METR 41.2 %.
- provisions: Cap. 23:04 s. 14
- Lean: ZwTax.out
- status: modelled

## Step 4: known loopholes, catalogued from the statute (blind to referees)

- trade/investment income at 25 % vs employment bands to 40 %: recreated
- two currencies: USD bands vs ZiG bands (choice of currency of pay): not modelled
- final residents' tax on interest: not modelled
- Part I credits for elderly / disabled: not modelled
- IMTT (money-transfer tax) as a cost of electronic pay: not modelled

Literature not checked (no web-search budget this session): IMF Article IV / FAD reports, ATAF African Tax Outlook, ICTD/ITC working papers, World Bank PER chapters, Big-4 country tax guides, academic papers on the country's PIT; the catalogue above is therefore limited to what the statute and the official pages read here make visible.

## Step 5: searches run
- `tools/scan.py` (fine grid 0-2.5 x scale, single / couple 1 earner + 2 children / couple 60-40 + 2 children): {"single": {"maxMETR": 0.3619, "netIncomeFalls": 0}, "couple1earner2kids": {"maxMETR": 0.3619, "netIncomeFalls": 0}, "couple60_40_2kids": {"maxMETR": 0.2905, "netIncomeFalls": 0}}
- `world/tools/scan_world.py ZW` (METR, phase-outs, timing, edges, filing unit, income type): `results/search/SUMMARY.md`. Scanner gains for income types the model marks unsupported are artefacts, not loopholes.

## Unsupported (listed in every output line where it applies)
- USD-earned income bands
- Part I credits (elderly, blind, disabled)
- NSSA contributions
- residents' tax on interest and shareholders' tax

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/ZwTax/Verify.lean` (imported by the `ZwTax` library and built; each guard evaluates `ZwTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/ZW.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | explained | Top row cites a non-existent paragraph: statute fault. |
| F2 | confirmed | Trade income of individuals at a flat 25 % beside employment bands to 40 %: ZiG 2 M as trade income keeps 193,063 more than as wages (AIDS levy included); below the zero band the flat rate costs more. G: f2_trade_flat_25. S: law/node6808.txt:208 ('14(2)(b) Taxable income of individuals from trade or investment 25'). |
| F3 | explained | AIDS levy 3 %: design. |
| Leads | explained | Rescan self-employment wedge +9.3 % at 5 'AW' = F2. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F2: Individuals' trade income at a flat 25 % against employment bands to 40 % | income-type gap | **unclear**: Search reduced: no PwC page for the country and OpenAlex not answered (budget exhausted). | 2026-11-20: OpenAlex specific queries 'Zimbabwe individuals trade income 25% employment income 40% tax'; 'Zimbabwe personal income tax self-employed flat rate' (14391 hits, titles checked); OpenAlex broad 'Zimbabwe personal income tax', 'Zimbabwe income tax wages', 'Zimbabwe tax system reform' (0 records, titles and abstracts grepped, 0 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries: no page for this country; Crossref IMF prefix 10.5089 'Zimbabwe tax policy' (8264 records, titles only). Record: world/loopholes/africa_mena/search/ZW-F2.json |

<!-- L1-VERIFICATION END -->
