# Round 3 item 2: reader queue (agent `queue`, resumed, then stopped)

Status: item dropped for this round by the coordinator shortly after the resume started. No further installs.

## State found at resume
- Queue snapshot: 31,803 unread candidate items in 398 packs of 80 (`work/round3/queue/packs/`, order = predecessor's
  priority order in `queue_snapshot.tsv`).
- Answered by the predecessor: 141 packs, all complete (`check.py`: bad = []). Packs 000-092, 095-127, 129-131,
  133-137, 141, 145, 149-151, 153, 154.
- Certified at the cut-off (`cert/stats.json`, 22:53:16): 10,353 answers, 2,367 rows. Installed: 2,363 rows
  (`delta/installed_treatments.tsv`), all still present in live `data/treatments.tsv` (34,820 rows).
- About 14 answer files were written after the last certify run (22:53:17-22:53:48), so they were answered but not
  certified or installed.

## Done in the resume
- One `install.py` run (certify2.py unchanged, window recut, delta under the lock). It finished before the stop
  message arrived. Certified 2,535 rows over 11,232 answers (141 packs). Added to live data:
  treatments +165, treatments_items +165, cert_text +142, window_sha +141, reader_rejects +738, cite_index +80.
  Live `data/treatments.tsv` is now 34,985 rows (treatments_items 34,985). No `.tmp` file, lock released.
- Totals installed by this item (predecessor + resume): 2,528 treatment rows, 9,240 reader_rejects lines
  (`delta/installed_*.tsv`). Main reject reasons: model not-own-act 7,872; no valid target 478; cue missing 506.
- 12 readers were launched for packs 093, 094, 128, 132, 138, 139, 140, 142, 143, 144, 146, 147 just before the
  stop, and were told to stop. Most had already finished: complete answer files (80 items each) now exist for 093,
  094, 128, 132, 138, 139, 140, 143, 144, 146, 147; `ans_142.jsonl` is partial (59 of 80). None of
  these is certified or installed (0 installed rows come from these packs). A later round can certify the eleven
  complete ones with `install.py` after deleting or finishing `ans_142.jsonl` (`check.py` must print bad = []).

## Blind audit E (predecessor's pack, 30 installed rows, scored here, nothing removed)
- `audit/E_pack.txt`, `E_key.tsv`, `E_ans.jsonl`.
- Own act right 29/30 (Wilson 95%: 83%-99%). Target right 30/30 (89%-100%). Kind equal 20/30 (49%-81%): in 9 rows
  the reader says `overruled` and the auditor says `disapproved` ("disapproved to the extent", "language is
  disavowed"); 1 row is the failed act. Scope agreed except one declinedToFollow row (all vs partial).
- Row the audit shows wrong and that is STILL INSTALLED (stopped before removal): `t:6865583:6852906:48056`
  ("we now abandon the terminology of the Angelier rule", not an overruling). Remove it from treatments.tsv and
  treatments_items.tsv and add a reader_rejects line (`audit`, `not-own-act`).
- The 165 rows installed in the resume were not audited.

## Not done / next round
- Answered and installed: 141 packs (11,280 items). Answered, not certified: 11 packs (880 items). Unread: 246 packs
  (about 19,600 items), including 142.
- Overruled-vs-disapproved kind choice for "disapproved to the extent" sentences: 9 of 30 audited rows.
- `measure.py` (before/after recall on private copies) was not run.
