# Agent `syl10` (round 10): syllabus / head-matter quotes refused by the zone check (move 1)

Read `round10/DESIGN10.md` and `round10/agents/COMMON.md` first. Folder `round10/agents/syl10/` (NOTES.md). Audit
letter `y`. No benchmark file is needed for this move; you may read the h0 per-case files
`round9/results/v9c/bench/*.h0.cases.tsv` (h0 only) to measure effect.

## Background
Round 9 added part zones to the Lean (`round9/DESIGN9.md` §4, `round9/LEAN9.md`): a treatments/history row's main
(and joined) quote must lie inside one zone of the row's part, in the text owner's offsets. On v9c it refuses 72
admitted quotes (`zone_failed_rows`; verdict `partZone` in `round9/out/v9c/certs.tsv`): 63 head-matter-only straddles
and 9 syllabus quotes (the Supreme Court syllabus is the reporter's words, not the Court's). These are right refusals
of the evidence, but in several cases the opinion itself states the same act and no row quotes it: e.g. an overruling
quoted only from the syllabus, with no other row on the target. Measured cost: FJC h0 −2, SCDB h0 −1, burned old
lists −2/−1, fresh sealed −1. The part map and zone builder: `round9/agents/calpart9/` (NOTES.md, `partzone.py`,
`build_zones.py`, `recut.py` — round 9 re-cut 137 straddling quotes; reuse it), zones `round9/lead/zones_all/`.

## Do
1. List every v9c row with verdict `partZone` (and, corpus-wide, every row of the round-5…9 reader outputs whose only
   quote for its (by, target, kind) lies in a `headmatter` zone or the syllabus — candidates the zone check would
   refuse in future builds; count them).
2. Rule (general): for such a row, look in the SAME acting decision's opinion zones (majority / plurality /
   perCuriam; never dissent/concurrence for a majority act) for a sentence that states the same act on the same
   target — the target's citation key (or a caption / anaphor tie usable by the round-9 Lean: plain, joined,
   anchored, `joinedFar`) plus a cue of the row's kind (or a kind the text supports) — and re-cut the row onto it
   (the `--replace` / `--remove` mechanics of calpart9's `recut.py`; new ids `t10:` / `h10:` via certify10). Where no
   such opinion sentence exists, the row stays refused (do not weaken the zone check, do not quote the syllabus).
   Check every re-cut quote against the zone table (the same zone logic as `checkPartZone`).
3. Certify (`round10/certify10.py` once INFRA_READY; until then prepare with certify9 copies in your folder), stage,
   run (NOBUILD), score (`noold` off once: the burned old lists are where most of these show). Precision / clean /
   Shepardized dev must not drop.
4. Blind audit the **whole class** of re-cut rows (≤ 80 → all; else a sample of 80) with two opus auditors and decoys:
   did the acting court itself, in the quoted sentence, do <kind> to the target; extent. Install at ≥ ~90%.
5. If a re-cut needs something the round-9 Lean cannot check (e.g. the act stated in a sentence that names the target
   only by short name far away), write `LEAN_REQUEST.md`; don't stall on it.
Report: counts by cause, rule, re-cut rows, audit with interval, delta folder + remove/replace files, measured effect.
Time box ~90 minutes.
