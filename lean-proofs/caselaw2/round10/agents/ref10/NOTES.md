# Round 10, agent `ref10`: the Python reference for round-10 rules (remand bridge, DESIGN10 §4; later by INBOX)

Written from `round10/DESIGN10.md` and the round-9 reference / harness (`round9/agents/ref9/`). No `.lean` file, nothing
under `LegalProofs/`, not `round10/LEAN10.md`, not LEAN9/LEAN8 §1-2 is opened. Open readings: `REF_QUESTIONS10.md`.

## Log (clock times from `date`)

- 03:48 started; read BRIEF, COMMON, DESIGN10, INBOX (03:48: start with §4), round-9 ref9 NOTES / NOTES2. df: 27 GB free.
- 03:48 backup: `tools/caselaw2/ref/*.py`, `REF_NOTES.md`, `labels.json` -> `round10/pre/ref/` (precedent_ref.py sha1
  7432cbed, the round-9 final).
- 03:49-03:50 D10-5 (9-column table, docket spans) read; REF_QUESTIONS10.md Q10-1..Q10-10 written, lead pinged.
  03:50 D10-6 rules them: Q10-2..9 as written; Q10-1 exactly two date forms (full month; abbr jan. feb. mar. apr.
  aug. sept. sep. oct. nov. dec.; May/June/July full only); Q10-10 noAuthority rows muted like D9-13.
- 03:50-03:53 implemented in tools/caselaw2/ref: precedent_ref.py (REMAND_* constants from cue_table.json else
  DESIGN10, `date_forms`, `day_number`; Data loads history_remand.tsv (bad / unknown / dup); Engine.node_span,
  Engine.check_remand (court, date, docket, cue, tie); admit: after the round-9 verdict (targetLater, zones), power
  gate = lean_cert_passes; remand_mute (Q10-10); ref_stats remand_* only when the file has a line); labels.json (five
  reasons); diff.py SUMMARY_KEYS10 + `bad_rows history_remand.tsv`.
- 03:53-03:54 check_regress10.sh regress10a (new check_regress10.py: current vs round-9 final reference, bytes):
  543 universes (534 r8ref + 9 round-9 kept): 543/543 the same as the round-9 reference; 534/534 the same as the
  stored round-8 reference output; canonical vs stored round-8 Lean: the 12 known W universes only. results/regress10a.txt.
- 03:55-03:58 cue_table.json already has lean10's round-10 keys (remand_court, remand_cue, remand_months,
  remand_months_abbr as 12 per-month lists, remand_quote_max, remand_docket_span_max, remand_days_max): the
  reference reads them (JSON first, DESIGN10 values as fallback; date_forms per month).
- 03:55-03:59 generator `make_r10.py` (new file; imports round9's make_r9 unchanged): a round-9 universe + new B
  decisions (own sha, court / date relative to the order), B windows (quote + docket span; unicode prefix, CR,
  upper case), far target-text windows (offset >= 8,000,000) for the target's docket span, fresh cite_index lines
  for orders (only when the file exists), history_remand.tsv with 46 designed cases (pass via cite / docket /
  full date / abbr incl. sep. & sept. / bounds 0 and 1,826 days / span 200 / quote 600; each failure reason
  incl. hash, missing window, empty span, B with no decisions2 row, B = the order, fake abbreviations, leading
  zero; check-order pairs), lines on rows without power and with failing round-9 verdicts, duplicates, an unknown
  id, bad lines (8/10 fields, non-digit, negative, non-UTF-8, full-width), CRLF / BOM / no final newline; fuzz
  mode (byte mutations). Expectations from the generator's OWN model of §4 (not the reference's code) on top of the
  reference's verdicts without the table; `cases10.tsv` designed vs model reason (differences explained by the
  row's own dates / no window_sha.tsv). Drivers gen10.sh, kept10.sh.
- 03:59 kept universes `universes/` (r100000-100003 main, q100100-100102 probe, f100200-100201 fuzz K=6; 5.1 MB):
  self-check main 1,824 expectations / 20 counters 0 differ; probe 875 / 15, 0 differ; `empty` (table absent /
  empty / blank vs round10/pre/ref bytes; bad + unknown-id lines only: all files but ref_stats the same): 4
  universes, 0 differing files. (make_r9's own round-9 case check prints one known-generator line on q100102
  pr_imp_witness, expected implicitBadKind|badRow got witnessBadRow: a round-9 generator artefact, unchanged ref.)
- 04:00 started real data: the current reference on the v9c mirror (data_r9_v9c) vs round9/out/v9c (realv9c.sh).
- 04:01 check_regress10.sh regress10b (reference 3aa34d40, per-month abbreviation lists): 543/543 bytes the same as
  the round-9 reference; 534/534 as the stored round-8 reference output; 12 known W universes vs stored Lean.
  REF_NOTES.md round-10 section written.
- 04:02-04:03 differential harness for a compiled runner binary (`bin_drt10.py`, `difftest10.sh` kept / sweep /
  regress / dirs; BIN= default ~/caselaw2/r10_bin/caselaw2_lean10, copied aside, sha1 logged). Harness test with
  the frozen round-9 binary 22bab5cd on the 9 kept universes (`results/h9kept.txt`): every disagreement is the
  remand class (the round-9 binary ignores history_remand.tsv: remand* rows ok there, plus their status / findings
  knock-ons and the five counters) - the harness reads the binary's shards correctly. fail/h9kept deleted.
- 04:03 wider self-check `wide` (20 main seeds 101000-101019, WSL scratch): 9,107 expectations / 100 counters, 0
  differ; designed-vs-model differences 118, all explained by the row's own dates / verdict / power; 0 unexplained.
- 04:00-04:04 REAL DATA v9c (realv9c.sh; reference 3aa34d40 on the WSL mirror data_r9_v9c, edges lean-in-v3) vs
  round9/out/v9c (frozen round-9 Lean): diff.txt 0 disagreements in every file (status 526,350 keys, findings
  321,152, certs 491,540, splits 348, conflicts 90, lines 325, horty 43, classes 37,448, summary 32); reference 3m24s.
  results/real_v9c.diff.txt. Big ref output deleted.
- 04:04-04:05 cross-check on shadow10's remand delta (round10/agents/shadow10/cert_remand, 03:55; remand_verdicts10.py
  via realremand.sh: v9c + the delta's tables, Data + admit only): 241 lines, dup 0, bad 0, unknown 0; checked
  241, failed 8 (all remandCue); shadow10's precheck.tsv: same 233, different 8. The 8: B's quote ends at
  "...Supreme Court vaca" (the next chars are "ted ..."): b_end is one character short of the cue "vacat", so
  remandCue is right under D10-6; shadow10's builder cuts the quote end (told the lead 04:06).
  results/rv_shadow_0355.{txt,tsv}.
- 04:07 kept universes regenerated (same seeds; cases10 'why' column marks hash cases in universes without window_sha.tsv); self-check unchanged (0 differ). Waiting for round10/LEAN_READY (monitor on LEAN_READY + INBOX).
- 04:07 lead: D10-7 (§4 amendment 2: 12 columns, tie (c2) via a span of the order's text holding "in light of" and
  the reason case, tie (b) dropped) and D10-8 (§6 trialBridge). 04:08 readings Q10-11..Q10-17 written; 04:08 D10-9:
  accepted as written (claim ignored on other rows; order anchored 1-5, step 6 with trialBridgeD in the cue's
  place, then T, then Date; counters tbridge_lines / tbridge_dup_rows / tbridge_bad_rows; cue keys as lean10 writes).
- 04:08-04:09 reference: D10-7 (12-column loader, (c2), (b) dropped; keys remand_order_span_max / remand_order_cue /
  remand_tie_min, else 300 / "in light of" / 8); §6 (HCLAIMS + trialBridge; history_tbridge.tsv loader;
  check_cert(tbridge=) replaces the kind-cue test with trialBridgeD; check_anchored(tbridge=); check_tbridge (T,
  Date); admit: claimed reversed / vacated rows with an anchor line and no bridge line; counters; keys
  trial_court_names / intermediate_court_names / tbridge_quote_max / tbridge_cue / tbridge_negative /
  tbridge_days_max else DESIGN10's). labels.json (+3 reasons), diff.py (SUMMARY_KEYS10 + tbridge, bad_rows map).
  precedent_ref.py now a1bd9485.
- 04:09-04:14 make_r10.py: 12-column lines, (c2) cases (pass, span 300, upper case; short tie, no "in light of",
  tie in B only (the D10-7 mutant), in O only, span 301, no window, empty tie, span in the target's text), B's
  docket as tie now expected remandTie; §6 cases: new T / D decision pairs (courts from history pairs with
  same_case_power yes), history rows + anchor / claim / tbridge lines: pass (reversed / vacated, 1,826 days,
  upper case), D fails (no trial name, intermediate names incl. "court of appeal", DCA, no kind cue), T fails
  (reverse / remand / vacate / no affirm / 601 chars / no line / no window / hash / dup first bad), Date fails
  (after, +1,827, same court, date 0), claim ignored (kind affirmed, no anchor line, bridge line), no claim,
  anchorNoCue, D-before-T order; tbridge bad / unknown / dup lines; fuzz mutates both tables. Own model of §6.
- 04:13-04:15 kept universes regenerated (same seeds, round10/agents/ref10/universes, 5.4 MB): main 1,896
  expectations / 32 counters, probe 962 / 24, 0 differ; designed-vs-model unexplained 0; empty (tables absent /
  empty / blank, trialBridge claims dropped vs round10/pre/ref; bad + unknown lines only): 0 differing files.
  regress10c (no round-10 table): 543/543 bytes = round-9 reference; 12 known W universes vs stored Lean.
- 04:15 started real data v9c again with the current reference (realv9c.sh v9c_b).
- 04:15 note: a tail of round10/LOG.md (read to check infra state) showed a line naming the new held-out key; nothing about it was opened or used. REF_NOTES.md: D10-7 and §6 lines added.
- 04:18 real data v9c_b (current reference, D10-7 + §6): 0 disagreements in every file vs round9/out/v9c (same key counts as 04:04). results/real_v9c_b.diff.txt. Waiting for LEAN_READY.
- 04:27 wider self-check with the D10-7 / §6 generator: wide2 (20 main, 102000-102019) 9,382 expectations / 160 counters 0 differ; wide2q (10 probe, 103000-) 3,114 / 80, 0 differ; designed-vs-model unexplained 0.
- 04:36 waiting for LEAN_READY (none yet); INBOX unchanged since 04:08.
- 04:46 cue_table.json (bcb2acc2) now has every round-10 key under the names the reference reads (remand_order_cue / _span_max / remand_tie_min, trial_court_names, intermediate_court_names, tbridge_cue / _negative / _quote_max / _days_max): all read from JSON (R7_CUE_SOURCE). WSL mirror reference = Windows (a1bd9485). Still no LEAN_READY.
- 04:54 LEAN_READY (runner e7e32592, ~/caselaw2/r10_bin/caselaw2_lean10; §4 + D10-5/6/7 + §6). Differential starts.
- 04:54-04:56 DIFFERENTIAL (runner e7e32592, reference a1bd9485, cue_table bcb2acc2; bin_drt10.py / difftest10.sh):
  | tag | universes | disagreeing | what |
  |---|---|---|---|
  | r10kept1 (9 kept) | 9 | 1 | r100000 tr2: W class (witness row, Lean ok / ref witnessNoStanding; atRisk:inferred, zone_missing 1) |
  | r10sw1 main 104000-104019 | 20 | 2 | r104001 (W row partZone/witnessNoStanding, zone counters), r104015 (atRisk:inferred of witness row tr3) |
  | r10sw1p probe 105000-105009 | 10 | 0 | - |
  | r10sw1f fuzz K=8 106000-106009 | 10 | 1 | f106008 tr0: W row (Lean noAuthority / ref partZone), zone counters |
  Every remand row (all five reasons, (c2), duplicates, bad / unknown lines, noAuthority mute) and every trialBridge
  row (D / T / Date, ignored claims, tbridge counters) agrees. The W disagreements are pre-existing: the same rows
  disagree with the frozen ROUND-9 binary 22bab5cd on the same universes stripped of every round-10 input
  (strip10.sh; results/r9bin_sw1fail.txt, r9bin_sw1ffail.txt). Self-checks: r10sw1 9,367 expectations / 160
  counters 0 differ; r10sw1p 3,144 / 80, 0 differ.
- 04:56 started regress r10reg1 (543 earlier universes, no round-10 table) with the round-10 runner.
- 04:56-04:57 regress r10reg1 (round-10 runner e7e32592, 543 earlier universes, no round-10 table): 13 universes
  disagree, all the known W class (the 12 round-8 W universes + round-9 kept z90001 tr1, exactly round 9's list):
  certs witnessNoStanding 10, classes 9, atRisk:inferred / citesLaterNegated knock-ons; status / splits / summary 0.
- 04:57 real data: stage round10/stage/ref10_v10c = hard-link copy of the lead's v10c (0 bytes); started
  `R10BIN=caselaw2_lean10 NOBUILD=1 r10_run.sh ref10_v10c ref` (own difftest folder difftest/r10_ref10_v10c).
- 04:57-05:00 REAL DATA v10c (lead's stage: v10a + shadow10's 316-line 12-column remand table, D10-7 format) as
  `ref10_v10c` (round-10 runner e7e32592 + reference a1bd9485): diff.txt 0 disagreements in every file (status
  529,122 keys, findings 325,817, certs 494,437, splits 348, conflicts 90, lines 325, horty 43, classes 37,448,
  summary 40 incl. remand_lines 316 / checked 316 / failed 0 / dup 0 / bad 0). Same as the lead's own 04:59 run.
  results/real_ref10_v10c.{diff.txt,RUN.txt,summary.tsv}, log results/r10run_ref10_v10c.log. clean10.sh
  ref10_v10c done (stage was hard links; v10c itself was cleaned by the lead, v10d is the freeze candidate). No
  real-data trialBridge rows exist yet (v10d has no trialBridge claim, no history_tbridge.tsv): §6 is checked on
  universes only.
- 05:01 WSL scratch trimmed (~/caselaw2/r10ref 277 MB -> 15 MB). Folder 19 MB. Final report to the lead.
