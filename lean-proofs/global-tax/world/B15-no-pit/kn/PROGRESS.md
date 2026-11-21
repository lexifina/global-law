# KN progress

**Status (2026-11-20 02:07 UTC): built** (access tier A). Lean model `kn/lean` (`kntax`, kernel 1.3.0 TaxKernel.World, worldMain), 99 lines, 6 theorems, 0 sorry. Next: software phase (test role), then datasets.

Steps: 1 statute (done), 2 validation (deferred: build-only phase, no referee values seen), 3 proofs (done: Theorems.lean), 4-6 generic scanners (see results/search/SUMMARY.md where present), 7 USEFUL (done).

## Sources read (dated)
- Law Commission: Income Tax Act Cap. 20.22 (RE 2017) s. 3(3); Act 12 of 2021 (s. 3A, companies)
- Housing and Social Development Levy Act Cap. 20.21 (RE 2017) s. 2-5; Act 1 of 2024; Act 14 of 2025
- Social Security Act Cap. 22.10 and Regulations (RE 2017): Schedule 1 Part I, Schedule 2

## Registry correction (fold back)
PIT N verified: Income Tax Act Cap. 20.22 s. 3(3). Levies: HSDL Act s. 3(2) (threshold $23,400 from Feb 2024, $27,040 from Jul 2025; 3.5/10/12 %) + Social Security 5 % up to $6,500 a month.

## Not modelled (`unsupported`)
- self-employed contributions

Rebuild: `cd /home/lean/cmp20/world/B15-no-pit/kn/lean && lake build`; smoke: `echo '{"adults":[{"wages":60000}]}' | .lake/build/bin/kntax`.
