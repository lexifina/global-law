# Round 3 item 1: splitter (resumed 23:03, 12 Nov 2026)

## State found at resume (23:03)
- Predecessor finished: hard-wrap splitter (`reader/scan.py` HW_MODE, `scan3.py`, `run_scan3.py`, `test_hardwrap.py`,
  `common.py` dehyphen), `Ctx3` in `resolve2.py` (text citations for decisions with no graph edges), `find_quote_hw`
  in `certify2.py`, `READER_BRIEF3.md`. Rescan of 21 repos done (`run_scan3b.log` ALLDONE 22:51), `data/reader_work/res3` written.
- Gold-directed attempt: `gold_items.py` -> 183 decisions, 245 pairs, 170 items (`gold_res/gold.items.jsonl.gz`,
  `gold_trail.tsv`), 150 packed in `gpacks/pack_000..004`.
- `gpacks/ans_000.jsonl` holds 150 answers, but they were written by the predecessor itself from `gold_answers.py`
  ("subagent limit was reached"), not by subagents. `gcert/` = certify2 run on those: 35 new rows, 1 cert fail.
- Whether anything was installed: checked below.
- Before score: `work/round3/splitter/score_before.txt`.

## Stage 1 (23:05): subagent re-read of the 5 gold packs
- Packs copied to `work/round3/splitter/gsub/`; one Claude subagent per pack writes `gsub/ans_NNN.jsonl`.
- Result (23:05): 5 subagents, 150 items, 37 own acts (predecessor's own read: 31; the subagents agree on all 31
  and add 6). Predecessor's `gpacks/ans_000.jsonl` and `gcert/` are superseded and were NOT installed.
- Nothing of this item was in the live `treatments.tsv` at resume (0 of 35 ids or keys).

## Stage 2 (23:06): Loper Bright part-map fix
- "Chevron is overruled." (offset 105931) was labelled `dissent~`: the prose line "   The dissent ends by quoting
  Chevron: “ `Judges are not" was taken as a separate-opinion heading. Fix in `reader/common.py` `BAD_SEP` (used by
  `part_map2` only): a heading line has no quotation mark and does not start "The dissent / The concurrence".
  Backup: `work/round3/splitter/pre/common.resume_2305.py`. `test_hardwrap.py` passes.
- `gold_items2.py` (Loper Bright only, no 3-item cap) -> 4 more items, `gsub/pack_005.txt`, read by a sixth subagent:
  1 own act ("Chevron is overruled.").
- The other 182 gold decisions were not re-scanned after this fix (next round).

## Stage 3 (23:08): certify and install
- `install.py` (copy of `queue/install.py`): `certify2.py --answers gsub --res gold_res --base data/treatments.tsv
  --reader claude-subagent:gold-directed`, window recut against git HEAD, delta under `data/.install.lock`.
- 154 items read, 41 own acts -> 37 new certified rows, all 37 kept after recut. Not rows: 3 already in base,
  1 certificate fail (`disqualifier-in-quote`, 5958109:22402), 3 with no valid target.
- By kind/scope: overruled|all 16, overruled|partialUnknown 19, disapproved|all 1, disapproved|partialUnknown 1.
- Installed (appended): treatments.tsv +37 (34,984 -> 35,021), treatments_items.tsv +37, cert_text.tsv +31,
  window_sha.tsv +27 (4 lines already present), reader_rejects.tsv +123, cite_index.tsv +6. All treatments rows
  have 16 columns; no .tmp, lock released.
- Delta files: `work/round3/splitter/delta/` (`installed_*.tsv` = what was appended).

## The 14 named cases
| Case | Row installed | Detail |
|---|---|---|
| Dobbs (6323819) | read | 2 rows |
| Wayfair (6313043) | read | rows for Quill and Bellas Hess |
| Loper Bright (6324015) | read | 1 row, after the part-map fix |
| Roe (6043646) | yes | Dobbs, overruled, all, 20220624, "We hold that Roe and Casey must be overruled." |
| Casey (6135647) | yes | same sentence |
| Quill (6134289) | yes | Wayfair, overruled, all, 20180621 |
| Chevron (6093129) | yes | Loper Bright, overruled, all, 20240628, "Chevron is overruled." |
| Logan Valley (6026123) | yes | Hudgens, overruled, all, 19760303 ("the rationale of Logan Valley did not survive") |
| Halper (6117253) | yes, partial | Hudson, overruled, partialUnknown, 19971210 ("in large part disavow the method of analysis"): expect partly negative, not fully |
| Swift (5941675) | yes, as disapproved | Erie, disapproved, all, 19380425 ("the doctrine of Swift v. Tyson is ... an unconstitutional assumption of powers"). Erie has no "overruled" sentence |
| Wolf (5988307) | no | Mapp: 2 candidate sentences, both read as not an own act (they report what counsel urged). No express sentence. Only the implicit row from 1966 exists (explicit 0) |
| Ohio v. Roberts (6074209) | no | Crawford: target cited, no candidate sentence (abrogation by reasoning). Only an implicit row from 2006 |
| Lochner (5953289) | no | Ferguson v. Skrupa: one candidate, about Adkins, read as a report. Sub silentio. Pair is not in the CRS table, so only the SCDB route tried it |
| Plessy (5950738) | no | Brown: pair not in the current CRS table, so not attempted; Brown's scan has no candidate sentence for its two CRS targets either. "Any language in Plessy ... contrary to this finding is rejected" was not checked |

## Not done
- No reference run: "admitted" here means certify2 passed and the window recut matched the corpus text. The
  coordinator's final run decides the status.
- No blind audit of the 37 rows. Packs are ready: `work/round3/splitter/audit/audit_pack_a.txt`, `audit_pack_b.txt`.
- The 6 rows the subagents found and the predecessor did not are the least certain:
  5960629:13956, 6036456:48502, 6055309:19211 (Logan Valley), 6110797:30917, 6157463:24790 (6015468:34011 was already in base).

## Next round
- Re-run `gold_items.py` for all 183 decisions with the `BAD_SEP` fix and without the 3-item cap; rerun `run_scan3.py`
  (res3 was built before the fix). The res3 items outside the gold packs were not read (scope cut by the coordinator).
- Plessy: add the hunt list pairs to `gold_items.py` (it reads only CRS current + SCDB) and read Brown's "rejected" sentence.
- Wolf, Roberts, Lochner need the implicit tier keyed on the overruling decision (witness format, not supported yet).

## Text for DEVIATIONS / READER.md
- Hard-wrapped texts: sentences are split after unwrapping; line-end hyphenation is tolerated in quotes
  (`find_quote_hw`); cited decisions of a text with no graph edges come from its own citations (`Ctx3`).
- Reader label `claude-subagent:gold-directed`: gold chose which decision was read; the reader saw only the opinion
  text. These 37 rows should be reported apart from held-out recall.
