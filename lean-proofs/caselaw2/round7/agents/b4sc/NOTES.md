# b4sc (round 7, track B4 items a + e): unlinked Supreme Court opinions, shared reporter pages

Agent b4sc. Started 23:11, finished 23:46 (clock: `date`, GMT). Writes only in this folder. No answer key read: the
only dev look is `round6/history/score_rows.py` stdout (aggregate lines; never `--out`, no per-case file). Nothing
committed. All processes were my own and have exited.

## Log
- 23:11 read DESIGN7 (§0, §4, §7), ROUND6, DESIGN6, STAGE_NOTES, LOG6, below_sc NOTES/RULES/link.py/weak2.py,
  below_other NOTES/RULES/link.py (process), guard RULES/vx_guard/gfeat, r6lib, r6scan (cw records), certify7
  (history path), make_packs7, score_rows.
- 23:14 baseline `final2_rows.py`: final2 history as rows (171,756). Proxy final2: NEG 106/254, sc_reversed 67/129,
  sc_vacated 31/71, PART 4/11, CLEAN negatives 6/9,704, MOD 1/16.
- 23:15-23:25 `sc7.py` (R1-R3 below), `tokdf.py` (caption token frequencies, institutional tokens), `select7.py`.
- 23:26 first certify7 (all admitted); 23:27 round-6 guard over new rows (copies `gfeat7.py`, `guard7.py`; rules
  unchanged).
- 23:28-23:33 `bo7.py` (B4 e for the other reviewing courts): key map, re-pointing, name anchors.
- 23:34-23:44 own reading found 3 defects, each fixed by a general rule: an anchor cut from the YAML front matter
  (anchor must lie inside one part of its label, after the front matter); a mandamus side proceeding taken as the
  decision under review (anchor/citation sentence naming mandamus or prohibition -> no row); a conditional sentence
  read as the judgment ("if the lower court's decision is affirmed ...", "petitioners contend ... must be reversed"
  -> no row). `cycle.sh` reruns everything (about 2 minutes).

## Rules (code: `sc7.py` docstring; `bo7.py` docstring)

Base: round 6's `below_sc/link.py` and `below_other/link.py` imported unchanged (every round-6 guard stays: signal /
other case name / former-prior-first-earlier appeal / "see also" / rehearing denied / later proceeding of the same
court (on remand, en banc, rehearing, second appeal) / printed year / 4-year window (6 before 1925) / one decision
under review per court / trial court only on direct review / syllabus cross-check / anchor disqualifiers).

- **R3 sole litigation decision (B4 a).** When round 6's anchor rules give no row for a Supreme Court opinion, the
  decision under review is taken from the citations: the one cited decision of the reviewed court (head-matter court
  line; else the courts the judgment names; else the highest court cited) whose caption passes the caption test,
  cited (head matter or before the judgment quote; or, as a bare citation, in the footnotes CAP prints after the
  opinion) without a signal, another case name or an earlier-proceeding mark; the opinion cites no other decision of
  that court sharing a party token, and no decision of any court sharing a party token dated after it.
  Caption test: a shared party token that is not institutional (not in a two-or-more-token caption side printed in
  >= 300 titles: agencies, boards, "National Labor Relations Board", "Commissioner of Internal Revenue") and is
  printed in <= 5,000 titles; or a shared token on every named side of the target's caption (round 6's cap 2).
  Outside the procedural history (after "we granted certiorari") the citation's sentence must name a court that may
  be the target's. Round 6's weak anchor types (A1w, HM_A1, A2, A3) are kept when they pass this test instead of
  round 6's W1 (judgment sentence names the court). Rule ids `below:sc7_l_<hm|zone|body|nozone|fn>`,
  `below:sc7_weak_r3`.
- **R2 modal judgment line (B4 a).** An opinion of the Court whose only judgment sentences are "must / should / will
  be reversed ..." takes the last such sentence of the last opinion-of-the-Court part when it opens with the
  judgment as subject (or "the judgment ... must be vacated") and has no argument / condition word, and "It is so
  ordered" follows within 600 characters, or at most 600 characters follow, or it ends its paragraph in the last 35%
  of the part (CAP footnotes follow). Rule ids `below:sc7_modal_*` and `_modal` suffixes.
- **Conditional judgment sentence (guard, all new rows).** No row when the judgment quote is a condition over a
  passive disposition ("if ... is affirmed") or a party's statement (contends, argues, urges, insists, asserts,
  states that).
- **Side proceeding (guard, all new rows).** No row when the anchor (or the citation sentence) speaks of mandamus or
  prohibition.
- **R1 shared reporter page (B4 e).** A citation key that graph/nodes.tsv gives to several decisions is re-pointed
  to the one holder whose caption the acting caption picks out (SC: the only holder sharing a party token, and it
  passes the caption test above; other courts: round 6's `shared_cite.py` test, `cap_rel` = 2, unique), never the
  index node and never a guess when none or several qualify. The re-pointed citation then goes through the whole
  round-6 selection unchanged. Evidence is `name:<the target's caption tokens the acting caption shares>` (the
  compact `cite:` key resolves to the other holder) in an anchor quote holding those tokens, an anchor cue and no
  anchor disqualifier, inside one part of its label: the round-6 anchor extended back (SC 3 sentences / 1,400
  characters; other courts 10 sentences / 2,500 characters) or the acting decision's head-matter caption lines
  (<= 700 characters; never the title line or the front matter). Rule ids `below:sc7_rp_*`, `below:o7_rp_*`.
- Skips: an SC opinion that already has a review-kind row in final2 gets nothing new; an other-court row whose acting
  decision has a final2 row for another decision of the same court is dropped (one decision under review per
  court). The round-6 guard's kept groups (unchanged) run over all new rows (drops 16 + 4).

Slip-opinion chunking: the reader already chunks CourtListener "Combined" slip opinions into `majority~` /
`dissent~` parts (`part_map2`); R1-R3 run on those texts unchanged (2010s-2020s rows exist, e.g. 2025, 2026
opinions). No separate rule was needed.

## Counts (corpus, final; `delta_a/`, `delta_e/`)

| class | rows | reversed | vacated | modified | affirmed | dismissed |
|---|---|---|---|---|---|---|
| B4 a R3 (`sc7_l_*`) | 766 | 371 | 50 | 10 | 307 | 28 |
| B4 a weak+R3 / R2 modal (`sc7_weak_r3*`, `sc7_modal_*`) | 613 | 265 | 28 | 4 | 299 | 17 |
| B4 e SC (`sc7_rp_*`) | 57 | 27 | 2 | 1 | 25 | 2 |
| B4 e other courts (`o7_rp_*`) | 341 | 152 | 9 | 17 | 155 | 8 |

R2 modal rows (any class): 72. Scope unknown: delta_a 71 of 1,379; delta_e 79 of 398.
certify7 (base `round6/history/stage/final2`): cert_a 1,394/1,394 admitted (123 via alias keys), cert_e 58/58,
cert_e_other 345 of 437 (91 already in the base, 1 conflictBase). Guard drops: 16 (a + SC e), 4 (other e).
History ids `h7:<by>:<target>:<kind>`, src `r7:<rule>`.

### B4 e: shared reporter pages
- SC opinions: round 6 dropped 3,210 citations of lower-court decisions on shared pages (`collisions` in its diag).
  408 had exactly one holder sharing a party token: 365 re-pointed (43 fail the caption test), giving 58 + 40 rows
  (40 in opinions already linked in final2, not added); 57 after the guard. Unlinkable: 2,689 (no holder shares the
  acting caption), 113 (several do).
- Other reviewing courts: 429,507 cache citations sit on shared pages; 21,810 already resolve to the caption's
  holder; 36,599 re-pointed; 371,051 stay unlinkable (no holder or several holders carry the acting caption); 47 out
  of scope. Round 6's selection on the re-pointed citations: 846 rows; 442 have an anchor holding the caption
  tokens (400 unlinkable as certificates: no allowed part holds the tokens, mostly one-line orders whose only
  caption is the title line); 437 after the same-court filter; 345 certified new, 341 after the guard.
- Round 6's own `shared_cite.py` drops (31 rows): 0 recovered (none has a unique caption holder).

## Proxy dev (score_rows.py stdout only; final2 rows + new rows)
NEG 106 -> 128/254 (50.4%, 44.3-56.5); sc_reversed 67 -> 88/129; sc_vacated 31 -> 32/71; panel/en banc unchanged;
PART 4/11 unchanged; CLEAN negatives 6/9,704 unchanged (the new rows add none); MOD 1/16 unchanged. The new rows
alone: 0 CLEAN, 0 MOD, 0 AMBIG negative rows. (Before the two late guards: 129/254; they cost one dev hit.)

## Own reading (blind to dev; `peek7.py`)
30 rows drawn after the first fixes (10 R3, 10 weak/modal, 10 shared page): 29 right (link and kind); 1 wrong (a
conditional sentence read as the judgment: Jago v. Van Curen, "if the lower court's decision is affirmed"), now
removed by the conditional guard (so 29/29 of the 30 that remain; not an independent estimate for the guard).
Earlier exploratory reading (27 rows): 1 wrong link (mandamus side proceeding, now guarded), 1 right link with an
anchor cut from the front matter (now refused by the part test).

## For the lead: blind audits (status-changing rows: reversed, vacated, modified; 80 each)
make_packs7 writes only under `round7/audit/`, so the lead builds them (dry runs checked: populations 431 / 297 /
208, 80 sampled each):
```
python -X utf8 round7/audit/make_packs7.py --class b4a_r3 --cert round7/agents/b4sc/delta_a --match "src=sc7_l_" --match "kind=reversed|vacated|modified" --n 80 --out round7/audit/<run1>
python -X utf8 round7/audit/make_packs7.py --class b4a_w --cert round7/agents/b4sc/delta_a --match "src=sc7_(weak|modal)" --match "kind=reversed|vacated|modified" --n 80 --out round7/audit/<run2> --exclude round7/audit/<run1>/sample.tsv
python -X utf8 round7/audit/make_packs7.py --class b4e_rp --cert round7/agents/b4sc/delta_e --match "src=rp" --match "kind=reversed|vacated|modified" --n 80 --out round7/audit/<run3> --exclude round7/audit/<run1>/sample.tsv --exclude round7/audit/<run2>/sample.tsv
```
Install a class only if it clears ~90% (DESIGN7 §7). If R3 fails, `sc7_l_body` / `sc7_l_fn` / `sc7_l_nozone` are
the weakest sub-classes (fewest procedural cues) and can be dropped by rule id. Stage: `--delta
round7/agents/b4sc/delta_a --delta round7/agents/b4sc/delta_e`.

## Base rows contradicted by a new two-quote row (count + proposal; NOT applied)
Round 6 certify6 rejected new rows contradicting a base row (`conflictBase`): below_other 466, below_sc 9, rehear 7
(482). below_other's comparison (`disagreements.tsv`, 991 opposite-polarity or kind pairs): of the 466 rejected,
381 are new scope unknown vs base all, 49 all/all, 6 all/unknown; the new judgment quote lies AFTER the base quote
in 436 (the base row quoted an earlier sentence), before it in 8, no base span 13. The other 525 pairs are kept both
(both scope unknown 466, or a neutral kind).
Proposed general rule ("the final judgment line decides"): for a (by, target) pair with a base row and a new
anchored row of opposite polarity, the new row replaces the base row (base row removed through a rule script's
`--remove` list, new row admitted) when (i) the new row passes every check, (ii) its judgment quote is the acting
opinion's final own disposition and lies after the base row's quote in the same text, and (iii) if the scopes differ,
the new one is `unknown` (a mixed judgment read as a whole-case act is the costlier error). Otherwise the base row
stands (current behaviour). It would resolve about 436 below_other pairs (10 of 12 read in round 6 favoured the new
row). Before installing: a blind audit of ~40 pairs showing both quotes, asking which act the court took.

## Files
`sc7.py`, `select7.py`, `tokdf.py`, `final2_rows.py` (B4 a + SC e); `bo7.py`, `work/filt_eo.py` (other-court e);
`mkguard.py` -> `gfeat7.py`, `guard7.py` (round-6 guard copies, paths only); `deltas.py`; `peek7.py`; `cycle.sh`
(whole pipeline). Rows: `rows_a.jsonl`, `rows_e.jsonl`, `rows_e_other.jsonl`; certify7 outputs `cert_a/`,
`cert_e/`, `cert_e_other/`; final deltas `delta_a/` (B4 a), `delta_e/` (B4 e); diagnostics in `work/`
(`run_stats.json`, `select_stats.json`, `bo_stats.json`, `bo_ev_stats.json`, `guard/*_GUARD.md`).

## Open
- 380+ remaining SC opinions in 1925-1999 that cite a court-of-appeals decision but get no row are mostly authority
  citations (no caption share); others: DC local court chains, NLRB/agency captions (refused by the caption test on
  purpose), conflict cases citing several circuits.
- Shared-page rows of one-line orders whose only caption is the title line stay unlinkable until Lean allows a
  title-part anchor (a contract change, not proposed here).
