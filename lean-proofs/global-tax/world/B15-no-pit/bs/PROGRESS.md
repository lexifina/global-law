# BS progress

**Status (2026-11-20 02:07 UTC): built** (access tier B). Lean model `bs/lean` (`bstax`, kernel 1.3.0 TaxKernel.World, worldMain), 73 lines, 2 theorems, 0 sorry. Next: software phase (test role), then datasets.

Steps: 1 statute (done), 2 validation (deferred: build-only phase, no referee values seen), 3 proofs (done: Theorems.lean), 4-6 generic scanners (see results/search/SUMMARY.md where present), 7 USEFUL (done).

## Sources read (dated)
- Bahamas Laws On-line point-in-time index of Acts at 2025-07-01 (letter I): no income tax act
- Department of Inland Revenue site (taxes administered; official secondary)
- NI (Contributions) Regulations S.I. 68/1984 (LRO 1/2017) reg. 2, 52
- NI (Contributions) (Amendment) Regulations 2024, S.I. 37/2024: Fifth Schedule, reg. 23(1A)

## Registry correction (fold back)
PIT N (no income tax act in force; DIR tax list). Contributions: NI (Contributions) Regs Fifth Schedule (S.I. 37/2024) 3.9 % + reg. 23(1A) 0.75 % = 4.65 % on basic wages up to the ceiling (2025 value not in law).

## Not modelled (`unsupported`)
- 2025 ceiling on insurable wages (administrative, RPI + 2 % biennially)
- employed persons 65+ (rate depends on retirement benefit)
- self-employed

Rebuild: `cd /home/lean/cmp20/world/B15-no-pit/bs/lean && lake build`; smoke: `echo '{"adults":[{"wages":60000}]}' | .lake/build/bin/bstax`.
