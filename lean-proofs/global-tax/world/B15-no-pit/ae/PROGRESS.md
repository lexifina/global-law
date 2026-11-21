# AE progress

**Status (2026-11-20 02:07 UTC): built** (access tier B). Lean model `ae/lean` (`aetax`, kernel 1.3.0 TaxKernel.World, worldMain), 126 lines, 6 theorems, 0 sorry. Next: software phase (test role), then datasets.

Steps: 1 statute (done), 2 validation (deferred: build-only phase, no referee values seen), 3 proofs (done: Theorems.lean), 4-6 generic scanners (see results/search/SUMMARY.md where present), 7 USEFUL (done).

## Sources read (dated)
- MoF consolidated English text of Federal Decree-Law No. 47 of 2022 (Corporate Tax) art. 11(3)(c), 11(6), 12(2) (mof.gov.ae, Jan 2026 consolidation)
- FTA page 'Basis of Taxation - Natural Person' (tax.gov.ae, updated 2024-05-06; official secondary): wages are not Business
- GPSSA English text of FDL No. 57 of 2023 and its amendments, art. 1, 2, 3, 4, 5 (pap-web-content.gpssa.gov.ae)
- GPSSA English text of Federal Law No. 7 of 1999 (2022 edition, scanned; OCR), art. 1, 2
- FDL No. 13 of 2022 on unemployment insurance (iloe.ae copy, unofficial translation) art. 3, 4; premiums from iloe.ae (official secondary)

## Registry correction (fold back)
PIT N verified. Statute: Federal Decree-Law 57/2023 (insured from 31 Oct 2023: 11 %, AED 3,000-70,000 a month) and Federal Law 7/1999 (earlier insured: 5 %, up to 50,000); add the ILOE premium (FDL 13/2022, AED 5/10 a month, all workers). Absence of PIT: FDL 47/2022 art. 11-12 + FTA natural-person page. Abu Dhabi nationals: own scheme (not modelled).

## Not modelled (`unsupported`)
- Abu Dhabi pension scheme
- UAE Corporate Tax on a natural person's business (self-employment)
- GCC nationals (home-state law)
- VAT on the ILOE premium (not a contribution)

Rebuild: `cd /home/lean/cmp20/world/B15-no-pit/ae/lean && lake build`; smoke: `echo '{"adults":[{"wages":60000}]}' | .lake/build/bin/aetax`.
