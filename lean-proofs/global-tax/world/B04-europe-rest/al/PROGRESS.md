# AL progress

**Status (2026-11-20 02:40 UTC): built** — Lean model `al/lean` (`altax`, kernel `TaxKernel.World`, worldMain), 163 lines, 10 theorems, 0 sorry. Next: software phase, then datasets (coordinator / test role).

Access tier A. Steps: 1 statute (done), 2 validation (statute's own printed amounts checked in Lean; official checks deferred: build-only phase), 3 proofs (done), 4-6 generic scanners (done, statutory scale), 7 USEFUL (done).

## Sources read (dated)

- Global law albania/national/acts/ligj/2023/29 (Ligj 29/2023 për tatimin mbi të ardhurat) as in force 2025-07-01; https://qbz.gov.al/eli/ligj/2023/03/30/29
- Ligj 7703/1993 për sigurimet shoqërore neni 10 (consolidated text of 2023-07-21)
- Ligj 126/2013 amending Ligj 10383/2011 (health contribution 3,4 % split equally)
- VKM 434/2023 pika 4 (minimum wage 40 000 per VKM 113/2023; maximum wage 176 416); VKM 776/2025 pika 5 (repeals VKM 113/2023 from 2026-01-01)

## Registry correction

Correct (Law 29/2023, progressive, individual). Add: the personal deduction depends on the income bracket (600 000 / 420 000 / 360 000 lekë), which makes two notches; investment income is taxed at flat rates (8 % dividends, 15 % other); 2025 minimum wage 40 000 (VKM 113/2023).

## Resume

`cd ~/cmp20/world/B04-europe-rest/al/lean && lake build`; scanners: `python3 ~/cmp20/world/tools/scan_world.py AL` (scale: 960 000 ALL = 2 × 12 × minimum wage 40 000, `scale.json`).
- 2026-11-20 round D7: AL instruction example checked: 2025 law (neni 69 (1)(dh), Ligj 9/2025) gives 0 % on gross business income up to 14 M; no change.
