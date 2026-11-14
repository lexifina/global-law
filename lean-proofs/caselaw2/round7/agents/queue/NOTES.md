# round7/agents/queue: the queued reading for the recognised-overruling class (B1, preparation)

Agent `queue`, round 7 (DESIGN7 §0 binding). Started 13 Nov 2026 22:45 (`date`). Writes only in this folder.
No readers spawned (the lead does). No answer key read: the holdout side of `round5/tests/split/` is never opened;
`gold/reports_typed.tsv` is read only through `round5/recog/recog_common.typed_rows` (feed ids only).

## Log
- 22:45 read DESIGN7 §0, DESIGN5 §2/§7, round5/recog NOTES/brief/builders/certifiers, tests/TESTS.md, LOG, PROGRESS.
- 22:47 found where "246 unread packs" comes from: `round4/queue.md` ("246 unread packs (incl. 142)") = the round-3
  own-act queue `work/round3/queue/packs` (398 packs, 152 answered). That is the explicit (own-act) class, not B1.
- 22:50-22:56 `build_dropped.py`: round-5 candidate build reproduced exactly (10,567 ids, 0/0 difference); 1,899
  statements beyond the 3-earliest cut -> `items_dropped.jsonl.gz`, `dropped_stats.json`.
- 22:57 `build_queue.py`: inventory (`inventory.json`, `inventory_packs.tsv`), 131 packs / 6,219 items in `packs/`,
  `packs/index.tsv`, `packs/items_index.tsv`, `items_queue.jsonl.gz`, `SHARDS.md` (33 shards), leak check 0 failures.
- 22:58 smoke test of `certify_recog.py` (copy, paths only) on one hand-made answer in the scratchpad: 1 row staged
  (`tw:173168:172862:4741:215673`), 48 no-answer rejects as expected. `ans/` and `cert/` here are empty.
- 22:59 INVENTORY.md, SHARDS.md written. DONE.

## Files
| file | what |
|---|---|
| `INVENTORY.md` | the inventory and reconciliation (the report) |
| `build_dropped.py` | items of the statements dropped by the 3-earliest cut (round-5 build_candidates logic, unchanged) |
| `build_queue.py` | inventory + queue + leak check + shards; re-runnable (rewrites `packs/`) |
| `packs/` | `pack_<P>_<SRC>_<nnn>.md` (round-5 item format), `index.tsv`, `items_index.tsv` |
| `items_queue.jsonl.gz` | all 6,219 queued items (for the certifier) |
| `READER_BRIEF_RECOG.md` | round-5 brief; only the answer path changed |
| `certify_recog.py`, `certify.sh` | round-5 certifier, paths only changed (items, index, answers, out; live tables = final2) |
| `leak_check.json`, `leak_check_failures.tsv` | per-item feed / power check |

## Open points
- P2/P3 "other grounds" items (CUT 1,829 + OG 1,014 + ...) add at most a second partial row to a pair that already
  has one; a lead may stop after P1. The CUT other-grounds statements could also go through `certify_pattern.py`'s
  strict form with no reader (not done: that script reads only round-5 items).
- `verify_recog.py` and `check_no_leak.py` have round-5 paths; run them on `cert/` after staging (lead).
- The 246 own-act packs (20,443 items) need a round-7 port of `work/round3/queue` tooling before reading.
