# KW progress

**Status (2026-11-20 02:07 UTC): built** (access tier B). Lean model `kw/lean` (`kwtax`, kernel 1.3.0 TaxKernel.World, worldMain), 92 lines, 4 theorems, 0 sorry. Next: software phase (test role), then datasets.

Steps: 1 statute (done), 2 validation (deferred: build-only phase, no referee values seen), 3 proofs (done: Theorems.lean), 4-6 generic scanners (see results/search/SUMMARY.md where present), 7 USEFUL (done).

## Sources read (dated)
- PIFSS legislative guide book 1 (16-9-2021): SIL 61/1976 art. 2 (ceiling 1,500, Law 9/2011), art. 11 (5 %), issuing decree art. 2 (Kuwaitis)
- Law 25/2001 art. 8 and table (pension increase fund, 2.5 % from the tenth year)
- Law 110/2014 art. 3-4 (2.5 % on salary up to 1,500)
- DL 128/1992 art. 1(3), 4(a) (supplementary insurance 5 %, maximum 1,250; decisions 1/2005, 6/2019)
- DL 101/2013 art. 3 (unemployment 0.5 %)

## Registry correction (fold back)
PIT N. Contributions (Kuwaitis only): SIL 61/1976 art. 11 5 % + Law 25/2001 2.5 % + Law 110/2014 2.5 % + unemployment DL 101/2013 0.5 % up to KWD 1,500 a month; supplementary DL 128/1992 5 % (+0.5 %) on 1,500-2,750.

## Not modelled (`unsupported`)
- amendments and ministerial decisions after September 2021
- minimum salary floor
- GCC nationals
- Kuwait income tax decree (corporate) not read

Rebuild: `cd /home/lean/cmp20/world/B15-no-pit/kw/lean && lake build`; smoke: `echo '{"adults":[{"wages":60000}]}' | .lake/build/bin/kwtax`.

- 2026-11-20 D9 review: `world_kw_issa_contribution_rates_2025` (ratio 1.3125 = 10.5 / 8) is a referee omission of one 2.5 % component (increase fund or end-of-contribution reward): FINDINGS D9S-1; model unchanged. world/IMPROVE_D9.md.
