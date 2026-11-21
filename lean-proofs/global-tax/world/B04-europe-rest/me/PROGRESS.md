# ME progress

**Status (2026-11-20 02:40 UTC): built** — Lean model `me/lean` (`metax`, kernel `TaxKernel.World`, worldMain), 128 lines, 7 theorems, 0 sorry. Next: software phase, then datasets (coordinator / test role).

Access tier B. Steps: 1 statute (done), 2 validation (statute's own printed amounts checked in Lean; official checks deferred: build-only phase), 3 proofs (done), 4-6 generic scanners (done, statutory scale), 7 USEFUL (done).

## Sources read (dated)

- Global law montenegro/national/acts/zakon/2001/348771 (Zakon o porezu na dohodak fizičkih lica 65/2001, as enacted) + amending acts zakon/2019/338016, 2021/293530, 2021/334044, 2022/334487, 2025/386428
- sluzbenilist.me/propisi/373333 (Zakon 88/2024, in force 2025-01-01; NOT in Global law; page images OCR'd, me/src/sl88/)
- Global law zakon/2007/334167 (Zakon o doprinosima 13/07) + zakon/2021/334055 (145/2021), zakon/2024/373700 (94/2024)
- Global law uputstvo/2022/336447, uputstvo/2024/374308 (Ministry instruction on payroll tax and contributions)
- Global law odluka/2018/310754 (Odluka o prirezu, Opština Žabljak, 13 %)

## Registry correction

Correct (progressive monthly tax with municipal surtax). The corpus is as enacted; the PIT amendment 88/2024 (in force 2025-01-01) is missing from Global law.

## Resume

`cd ~/cmp20/world/B04-europe-rest/me/lean && lake build`; scanners: `python3 ~/cmp20/world/tools/scan_world.py ME` (scale: 18 000 EUR = 12 × 1 500, `scale.json`).
