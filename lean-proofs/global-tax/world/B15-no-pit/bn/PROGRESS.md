# BN progress

**Status (2026-11-20 02:07 UTC): built** (access tier A). Lean model `bn/lean` (`bntax`, kernel 1.3.0 TaxKernel.World, worldMain), 62 lines, 3 theorems, 0 sorry. Next: software phase (test role), then datasets.

Steps: 1 statute (done), 2 validation (deferred: build-only phase, no referee values seen), 3 proofs (done: Theorems.lean), 4-6 generic scanners (see results/search/SUMMARY.md where present), 7 USEFUL (done).

## Sources read (dated)
- AGC: Income Tax Act Cap. 35 Revised Edition 2024 s. 8(1)(b), 34, 35, Schedule 2
- MOFE Revenue Division corporate tax FAQ (official secondary)
- TAP copy of the National Retirement Scheme Act Cap. 273 Revised Edition 2024 s. 2, 10, Schedule 2

## Registry correction (fold back)
PIT N verified: ITA Cap. 35 s. 34 + empty Schedule 2. Contributions: National Retirement Scheme Act Cap. 273 (2023) s. 10(2) 8.5 % (citizens and PRs; SCP/TAP merged into SPK).

## Not modelled (`unsupported`)
- minimum retirement age test (Retirement Age Act Cap. 270 not read)

Rebuild: `cd /home/lean/cmp20/world/B15-no-pit/bn/lean && lake build`; smoke: `echo '{"adults":[{"wages":60000}]}' | .lake/build/bin/bntax`.
