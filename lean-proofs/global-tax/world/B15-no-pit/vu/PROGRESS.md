# VU progress

**Status (2026-11-20 02:07 UTC): built** (access tier A). Lean model `vu/lean` (`vutax`, kernel 1.3.0 TaxKernel.World, worldMain), 58 lines, 3 theorems, 0 sorry. Next: software phase (test role), then datasets.

Steps: 1 statute (done), 2 validation (deferred: build-only phase, no referee values seen), 3 proofs (done: Theorems.lean), 4-6 generic scanners (see results/search/SUMMARY.md where present), 7 USEFUL (done).

## Sources read (dated)
- VNPF Act Cap. 189 Consolidated Edition 2026 (VNPF's copy): s. 1 (employee), s. 25(1), (1A), (2)
- VNPF employers page (official secondary): expatriates covered

## Registry correction (fold back)
PIT N (no act found). Contributions: VNPF Act Cap. 189 s. 25 6 % employee (no ceiling, none below VT 3,000 a month), expatriates included.

## Not modelled (`unsupported`)
- absence of an income tax rests on no act found (Global law holds only the Constitution)

Rebuild: `cd /home/lean/cmp20/world/B15-no-pit/vu/lean && lake build`; smoke: `echo '{"adults":[{"wages":60000}]}' | .lake/build/bin/vutax`.
