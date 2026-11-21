# AG progress

**Status (2026-11-20 02:07 UTC): built** (access tier B). Lean model `ag/lean` (`agtax`, kernel 1.3.0 TaxKernel.World, worldMain), 90 lines, 3 theorems, 0 sorry. Next: software phase (test role), then datasets.

Steps: 1 statute (done), 2 validation (deferred: build-only phase, no referee values seen), 3 proofs (done: Theorems.lean), 4-6 generic scanners (see results/search/SUMMARY.md where present), 7 USEFUL (done).

## Sources read (dated)
- laws.gov.ag: Unincorporated Business Tax Act 2016 s. 46-47 (repeal of the Personal Income Tax Act 2005 from 1 July 2016)
- Personal Income Tax Act 2005 s. 8-9; amendments 2014 (No. 5) and 2016 (No. 8)
- Social Security (Collection of Contributions) Regulations 2013 reg. 4; amendment S.I. 60 of 2016 (scanned; OCR) reg. 4(1)(b), Schedule 1, Schedule 2
- Medical Benefits Regulations 2011 (S.I. 27 of 2011) reg. 17

## Registry correction (fold back)
PIT N verified: Personal Income Tax Act 2005 repealed from 1 July 2016 by the Unincorporated Business Tax Act 2016 s. 47. Contributions: SS 7 % up to $6,500/month (S.I. 60/2016, 2025 row), Medical Benefits 3.5 % (S.I. 27/2011 reg. 17); education levy: no accessible text found.

## Not modelled (`unsupported`)
- education levy (no accessible text found)
- social security at and after pensionable age
- Unincorporated Business Tax (self-employment)

Rebuild: `cd /home/lean/cmp20/world/B15-no-pit/ag/lean && lake build`; smoke: `echo '{"adults":[{"wages":60000}]}' | .lake/build/bin/agtax`.
