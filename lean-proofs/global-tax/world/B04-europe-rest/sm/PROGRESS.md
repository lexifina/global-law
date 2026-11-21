# SM progress

**Status (2026-11-20 02:40 UTC): built** — Lean model `sm/lean` (`smtax`, kernel `TaxKernel.World`, worldMain), 168 lines, 6 theorems, 0 sorry. Next: software phase, then datasets (coordinator / test role).

Access tier B. Steps: 1 statute (done), 2 validation (statute's own printed amounts checked in Lean; official checks deferred: build-only phase), 3 proofs (done), 4-6 generic scanners (done, statutory scale), 7 USEFUL (done).

## Sources read (dated)

- Global law san-marino/national/acts/imposta-generale-sui-redditi/legge-2013-166 (Legge 166/2013 IGR), publisher's current text of 2025-12-22 (current-only record; earlier wording in its footnotes)
- art. 148 c. 8 (2025 wording of arts. 13, 16, 17, 25, 102-104: files art-16--2.md, art-17--2.md, art-25--2.md)
- Allegato C art. C1 c. 1 (2013 text, unchanged), c. 3 (2013 text from footnote 93; abrogated by Legge 141/2025 art. 55)
- art. 24 c. 4 (2013 text), art. 26, art. 14 (pre-141/2025 wording from its footnote)
- Global law san-marino/national/acts/legge-che-istituisce-un-sistema-obbligatorio-di (Legge 42/1955): employer contributions only; the employee pension/ISS rates are not in the record

## Registry correction

Correct (Legge 166/2013 IGR, progressive). The record holds only the text of 2025-12-22, which already includes Legge 141/2025 (2026 reform); the 2025 wording comes from art. 148 c. 8 and the footnotes.

## Resume

`cd ~/cmp20/world/B04-europe-rest/sm/lean && lake build`; scanners: `python3 ~/cmp20/world/tools/scan_world.py SM` (scale: 40 000 EUR = the end of the Allegato C C1 c. 3 deduction taper, `scale.json`).
