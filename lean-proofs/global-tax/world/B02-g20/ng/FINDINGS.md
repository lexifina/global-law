# Nigeria (NG) findings, B02-g20 (2026-11-20T01:50Z)

Built from the statute only (no referee values seen). Leads from the B02 generic scan (`results/search/b02scan.md`).

### F1 'Gross income' defined twice
- kind: statute-fault
- The Sixth Schedule sets CRA = 200,000 + 20 % of gross income and a minimum tax of 1 % of 'Gross Income', while s. 33 (1) (2011) says 200,000 'subject to a minimum of 1 percent of gross income whichever is higher' and the Finance Act 2020 defines gross income 'for the purposes of this Section' only (s. 33). Which gross income the Schedule's minimum tax uses is a reading; the model uses the s. 33 (2) definition.
- provisions: PITA s. 33, Sixth Schedule; FA 2020 s. 29
- Lean: NgTax.person
- status: reading

### F2 Minimum-wage exemption from minimum tax not applied
- kind: model-fix
- FA 2020 s. 30 (s. 37 proviso): the National Minimum Wage amount was not read; low earners may be charged 1 % minimum tax wrongly (flagged).
- provisions: s. 37
- Lean: NgTax
- status: open

### F3 Generic scan: no notch, max METR 25.7 %
- kind: model-fix
- b02scan.
- provisions: -
- Lean: results/search/b02scan.md
- status: scan done


## Round W2 (improvement agent, 2026-11-20): W1 software-grid dev failures settled from the statute

### W2-1 CRA base: the model's reading is the statute's; both referees are wrong (software errors)
- kind: software-error
- PITA s. 33 (2) as substituted by the Finance Act 2020 s. 29 defines gross income "for the purposes of this Section"
  as income less "tax-exempt items listed in paragraph (2) of the Sixth Schedule", which include "(d) National Pension
  Scheme" (PITA (Amendment) Act 2011 s. 34). The CRA of s. 33 (1) is therefore 200,000 (or 1 %) plus 20 % of pay net of
  the 8 % pension. PolicyEngine-NG deducts no pension and takes the CRA on gross pay (model ~11 % lower); TaxWiz deducts
  the pension but takes the CRA on gross pay (model ~3 % higher; case 0585: the CRA base explains all 79,456).
- provisions: PITA s. 33 (1), (2); Sixth Schedule paras. 1-2; PRA 2014 s. 4 (1) (b)
- Lean: NgTax.person
- status: recorded in software/ISSUES.md (W2)

### W2-2 Minimum-wage exemption added as an optional input (F2 closed in form, amount still not read)
- kind: model-fix
- Finance Act 2020 s. 33 (Third Schedule para. 33: "The income of a person from an employment where such person earns
  gross income of National Minimum Wage or less from such employment") and s. 30 (s. 37 proviso: the minimum tax "under
  this section or as provided for under the Sixth Schedule ... shall not apply" to such a person). The model now exempts
  that employment income and drops the minimum tax when `ngMinWageMonthly` (naira a month) is given; the amount (the
  National Minimum Wage Act as amended) was not reached in an official text this round (State House press releases only;
  NASS bill pages are script-rendered; Global law holds only the 2025 Tax Act's definition), so without the input the
  model is unchanged and says so in `unsupported`. #guards: with 70,000 a month, 840,000 pays 0 and 840,001 pays 34,006
  (a notch); without it 100,000 pays the 1 % minimum (920). The low-income W1 failures are the minimum-tax base: both
  referees take 1 % of gross pay, the model 1 % of the s. 33 (2) gross income (F1, a reading); under the statute an
  employee at or below the minimum wage pays nothing at all.
- provisions: FA 2020 ss. 29-31, 33; PITA s. 37 proviso, s. 108, Third Schedule para. 33
- Lean: NgTax.earnsMinWageOrLess, NgTax.person (#guard)
- status: model changed (no effect on the W1 grids, which do not pass the input)

### W5S-1 nigeria-paye (orionsoft): CRA on gross before the exempt pension (reading) (W5 review pass 2, 2026-11-20)
- kind: software-error
- `ng_open_nigeria_paye_orionsoft_grid`: oldLawMonthlyPaye computes the consolidated relief allowance on the annual gross; the model computes it on gross income net of the tax-exempt pension contribution (PITA s. 33 as amended by FA 2020, the model's reading), so the tool's tax is lower by ~2.5-3 %. The below-minimum-wage cases are a mapping matter (input `ngMinWageMonthly`, rebuild requested).
- status: recorded (world/IMPROVE_W5.md pass 2)

### W5S-2 wronglaw grids: iamagbacoder, hilinksnetworks, jedee (W5 review pass 2, 2026-11-20)
- kind: software-error
- tax-calculator (iamAgbaCoder): invented bands (200,000 free, 10 / 15 / 20 %) and no CRA; ng-paye-calculator (hilinksnetworks): duplicate PHP array keys drop the 7 % and 15 % bands; naija-payroll (jedee): a 0 % first band of 300,000, a CRA without the 20 % of gross, and the repealed children's relief. Each confirmed on its dev cases against PITA s. 33 (1A) and the Sixth Schedule (7 / 11 / 15 / 19 / 21 / 24 %).
- status: recorded (world/IMPROVE_W5.md pass 2, wronglaw table)

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | lead | 'Gross income' defined twice (CRA base): reading; W2-1 found the model's reading is the statute's. |
| F2 | explained | Minimum-wage exemption: now an optional input (W2-2). |
| F3 | explained | Superseded by the L1 rescan 2026-11-20 22:44 CET (world/tools/scan_world.py --full, current exe; results/search/SUMMARY.md): no notch. |
| W2-1, W2-2, W5S-1, W5S-2 | explained (record of model/test work, not a loophole; kept as written) |  |
| Leads | explained | Rescan: nothing beyond model gaps. |

<!-- L1-VERIFICATION END -->
