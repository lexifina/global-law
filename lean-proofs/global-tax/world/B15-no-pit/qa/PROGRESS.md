# QA progress

**Status (2026-11-20 02:07 UTC): built** (access tier A). Lean model `qa/lean` (`qatax`, kernel 1.3.0 TaxKernel.World, worldMain), 76 lines, 2 theorems, 0 sorry. Next: software phase (test role), then datasets.

Steps: 1 statute (done), 2 validation (deferred: build-only phase, no referee values seen), 3 proofs (done: Theorems.lean), 4-6 generic scanners (see results/search/SUMMARY.md where present), 7 USEFUL (done).

## Sources read (dated)
- MoJ API: Law 24/2018 (Income Tax Law): issuing art. 2(3) as amended 2022, law art. 3, 4(2), 4(4), 4(12)
- MoJ API: Law 1/2022 (Social Insurance Law): art. 1, 2, 3, 11, 12, 13; issuing art. 4 (commencement)
- Global law qatar/national/acts/cabinet-decision-2025-3 (executive regulations) art. 16 (2025-07-01)

## Registry correction (fold back)
PIT N verified: Law 24/2018 issuing art. 2(3) excludes salaries and wages. Contributions: Law 1/2022 art. 11, 7 % up to QAR 100,000 a month (Qataris).

## Not modelled (`unsupported`)
- non-Qatari business and real-estate income (taxable; rate not read)
- GCC nationals (Law 4/2007)
- grandfathered contribution salaries above 100,000 (art. 13)

Rebuild: `cd /home/lean/cmp20/world/B15-no-pit/qa/lean && lake build`; smoke: `echo '{"adults":[{"wages":60000}]}' | .lake/build/bin/qatax`.
