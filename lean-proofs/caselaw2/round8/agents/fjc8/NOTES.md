# fjc8 notes (round 8): FJC IDB appeals h0 diagnosis + rules

- 00:18 Started. Read DESIGN8, COMMON, BRIEF. bench_h0/READY and INFRA_READY absent. Studying round-6
  below_other / guard and round-7 b4sc meanwhile.
- 00:21 Studied round-6 below_other (link.py, RULES.md), guard RULES, round-7 b4sc NOTES (R1-R3), certify7 history
  checks (anchor: cue + evidence in quote + no disqualifier; main quote: hist cue). Wrote `diag.py trace`
  (per (district, appellate) pair: cache presence, cw records, first failing below_other step, base v3 history rows
  + Lean verdicts). Self-test on 5 below_other rows: all `row`. Waiting for bench_h0/READY.
- 00:29 bench_h0/READY. v3 h0 FJC (cited): recall 1,418/2,832 = 50.1%, precision 1,418/1,576 = 90.0%, clean
  6,087/6,229 = 97.7%, part 561/1,489 = 37.7%. Misses 1,414 (GOOD 1,291, UNK_HIST 122, UNK_OTHER 1); 1,220 have
  no history row at all on the district node.
- 00:31 `diag.py trace` over all 1,414 misses (1,529 (district, appellate) pairs; best stage per case):
  no_court_phrase 405 (cap2 331, cap1 74); named_other_case 282 (cap1 231 = one caption side shared, cap0 51);
  linker row exists 139 (mostly scope unknown -> UNK_HIST ~95; reversed/all rows not live ~22; affirmed ~18);
  later_events 92; earlier_proceeding 63; signal 67; no_design_cue 56; interlocutory 55; no own disposition found
  80; no cw record 38; opinion not in cache 31; one_side_caption 29; bare_no_caption 24; two candidates 13;
  other 30. Corpus funnel (`funnel.py`, 546,328 CA opinions, 113,096 with a negative judgment line; 17,953 with a
  trial-court candidate and no row) has the same shape: cap-2 no_court_phrase is the largest cap-2 loss.
- 00:33 Peeks: the citation sentence often follows a quote / description whose subject is "the district court"
  2-3 sentences earlier; the reader's sentence splitter cuts at abbreviations ("Fin.", "U.S.C.", quoted periods),
  so "previous sentence" is often a fragment. Some are real exclusions (earlier appeal reviewed it; later order).
- 00:35 Stratified sample of 40 misses (decade x civil/criminal-by-caption, seed 20261114: `work/sample40.tsv`)
  sent to 4 opus readers (`read1/BRIEF.md`, items_k / answers_k).
- 00:40 Readers back (read1/answers_*.jsonl). 40 h0 misses: 31 YES/REV (the opinion reverses/vacates THIS ruling),
  2 YES/PART, 1 YES/AFF (the cited ruling was affirmed; another part vacated), 1 YES/NONE (appeal dismissed as moot),
  1 YES/UNSURE (certified question), 4 EARLIER (an earlier ruling of the same docket; the appeal reviews a later
  one). So ~33/40 are true model misses. Loss points of the 33: caption changed on one side (substituted officer,
  other lead party, spelling) 9; citation sentence does not name the court (court named 1-3 sentences earlier, after
  a quote, in a footnote) 11; round-6 earlier/later/interlocutory word guards firing on the decision under review's
  own narrative 8; signal 1; no citation (caption-only) 1; not in cache / no disposition found 3.
- 00:42 Lean refusals among misses: 14 h0 misses have a reversed/vacated `all` row refused `noAuthority`: old Fifth
  Circuit (ca5) over Alabama/Georgia/Florida district courts before 1 Oct 1981 (courts2 gives those districts
  circuit 11 for all dates). Corpus: 615 history rows ca5 -> ca11-district refused noAuthority. -> LEAN_REQUEST.
- 00:44 `fjc_link.py` rules F1 (cap-2 extended anchor), F2 (cap-1 with a distinctive shared token), F3 (head-matter
  name anchor, small): 4,402 rows corpus-wide; certify8 4,401 admitted (1 conflictBase); round-6 guard (gfeat8 /
  guard8 = b4sc copies) drops 130 -> `delta_f12/` 4,271 rows. Proxy on h0: +245 NEG units newly NEG_HIST, 12 PART,
  5 CLEAN, 26 REMAND, 2 OTHER.
- 00:47 stage8 fjc8_a (--delta delta_f12); Lean NOBUILD run started.
- 00:51 fjc8_a scored (F1+F2 unrestricted + F3): FJC h0 recall 1,658/2,832 = 58.6%, precision 90.5%, clean 97.5%
  (6,070), part 44.3%; Shepardized dev, SCDB h0, fresh dev unchanged. Read the 17 CLEAN losses: 2 disposition
  misreads (act word inside a condition/quote: "may be reversed only when", "unless that award must be vacated";
  round 6 tests only text before the reader's match start), 1 authority citation of another litigation with one
  shared side (Mackey/Murphy v. Arlington), rest partial dispositions (unknown, fine) or plausible IDB coding.
- 00:55-01:03 Fixes (general): disposition sanity (round-6 own_disposition + condition words tested up to the act
  word); F2 restricted: the non-shared caption side must be the same name spelt otherwise (similarity >= 0.8) or a
  public officer / body (officer word in either caption side, or after the party's name in the acting head matter);
  F2 citation introduced by "See/Cf./e.g." needs the court named within 400 chars before it. Rule S1 (scope,
  `fjc_scope.py`): a consequence dismissal ("the petition is dismissed", "with instructions to dismiss") is not a
  second act. `cycle.sh b` -> rows 3,344, certify8 3,343 admitted, guard drops 70 -> `delta_b/` 3,273 rows.
- 01:07 fjc8_b scored: FJC h0 recall 1,624/2,832 = 57.3% (55.5-59.2), precision 1,624/1,796 = 90.4%, clean
  6,075/6,229 = 97.5% (v3 6,087), part 639/1,489 = 42.9%. Shepardized dev NEG 140/254, precision 140/149, CLEAN
  9,695/9,704: unchanged. SCDB h0 unchanged. Lean: 3,225 ok, 48 noAuthority (old Fifth Circuit).
- 01:05 `scope_base.py` (S1 on base round-6 below_other rows, federal CAs): 1,364 reversed/vacated unknown rows,
  29 become `all` (`scope_replace.tsv`); the rest stay unknown for other reasons (partial words, mixed end zone).
- 01:11 Blind audits (2 opus readers per pack, strict, decoys 18/18 each):
  r8f01 F1 neg (delta_b, Lean ok, pop 761): right 71/80 = 88.7% [80.0-94.0], link 75/80, corpus-weighted 95.4%.
  r8f02 F2 neg (pop 448): right 62/80 = 77.5% [67.2-85.3] -> F2 NOT installed (off by default, FJC8_F2=1).
  r8f03 S1 base scope rewrite (all 29): right+extent 24/29 = 82.8% [65.4-92.4] -> NOT installed.
  F1 errors (9): earlier ruling of the same docket (2), another suit same caption / authority (2), appeal limited to
  part (4), bankruptcy order reviewed via BAP (1).
- 01:13 Lead D8-12: old circuits accepted as claim `oldCircuit` (DESIGN8 section 6). `oldcircuit.py` selects by rule
  (CA5 before 1981-10-01 on circuit-11 district/bankruptcy targets; CA8 before 1929-03-01 on circuit 10):
  base `oldcircuit_base_claims.tsv` 614 claims (183 reversed/vacated/modified); own rows 26 claims
  (`delta_c/history_claim_delta.tsv`). Simulation `sim_oc.py` (FJC h0, v3): base claims +14 NEG units to NEG_HIST,
  1 CLEAN to NEG_HIST, 1 CLEAN + 2 PART to UNK_HIST.
- 01:14 Fixes for F1 (general): bankruptcy-court targets out (reached via district court/BAP); ruling-type test
  (dismiss / summary judgment / injunction / trial-sentence / fees / remand-to-state named at the citation vs in the
  judgment line must overlap). `cycle.sh c`: 2,107 rows, certify8 2,107 admitted, guard drops 26 -> `delta_c/`
  2,081 rows (+26 claim lines); `delta_c_noclaim/` = same without claims (for staging before LEAN_READY).
- 01:18 fjc8_c (delta_c_noclaim) scored: FJC h0 recall 1,534/2,832 = 54.2% (52.3-56.0) [v3 50.1%], precision
  1,534/1,699 = 90.3% [v3 90.0%], clean 6,081/6,229 = 97.6% [v3 97.7%, -6], part 610/1,489 = 41.0% [v3 37.7%];
  h0 cases gained 166, lost 6, model changed 33. Shepardized dev / SCDB h0 / fresh dev unchanged. Lean: 2,055 ok,
  26 noAuthority (= the 26 oldCircuit-claimed rows; simulation with claims: +2 NEG to NEG_HIST, 1 CLEAN to UNK).
- 01:19 Re-audits: r8f05 F1 neg (delta_c, pop 757, excludes r8f01 sample): right 73/80 = 91.2% [83.0-95.7],
  link+effect 75/80 = 93.8%, corpus-weighted 90.3%; decoys 16/18 (pack 1 both readers missed one decoy).
  -> F1 meets the bar (point estimate >= 90%). r8f04 oldCircuit base rows (pop 183): right 63/80 = 78.7%
  [68.6-86.3], link 72/80; by source r6:below 34/39, hist-regex-v2 29/41 -> base claims NOT installable (the base
  rows' own quality; the claim itself only lets Lean check them).
