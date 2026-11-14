# b4rehear: round 7, track B4 (b) en banc / docket-linked rehearing, (d) "set aside" as a vacatur cue

Agent `b4rehear`. Folder: `round7/agents/b4rehear/` (writes only here; nothing committed; only my own processes).
Started Fri 13 Nov 2026 23:19 (clock of `date`), last step 23:53.
Rules in plain words: `RULES7.md`. No Shepardized, gold, split, heldout or reports file was opened; the proxy scorer
`round6/history/score_rows.py` was run on the dev split for aggregate counts only (stdout, no `--out`).

## Files

| file | what |
|---|---|
| `r6_audit_by_rule.py` -> `r6_audit_items.tsv` | round-6 blind-audit results (r1, a3) of the rehear classes per linker rule (audit outputs only) |
| `r7rehear.py` | (b) `cands` (round-6 rehear claims cache, read only -> `work/cands.jsonl`), `feats` (git texts -> `work/feats.json`), `rows` -> `rows_enbanc.jsonl`, `rows_docket.jsonl`, `rows_setaside_rehear.jsonl`, `rows_stats.json`, `work/dropped.tsv` |
| `r7setaside_bo.py` | (d) round-6 below_other linker imported, one step changed; `run` (all non-SCOTUS shards, 22 procs -> `work/bo/`), `rows` -> `rows_setaside_bo.jsonl` |
| `r7setaside_base.py` | (d) base history rows (rounds 4-5) of kind vacated that the round-6 Lean run rejects `noCue` and that say "set aside" -> `rows_setaside_base.jsonl` (setAside claims on base ids) |
| `merge_setaside.py` | -> `rows_setaside.jsonl` (one row per pair; base rows decided by the base rules) |
| `rows_enbanc_{act,order,silent}.jsonl` | `rows_enbanc.jsonl` split by sub-class |
| `cert_enbanc_act/`, `cert_enbanc_order/`, `cert_enbanc_silent/`, `cert_docket/`, `cert_setaside/` | **delta folders** (`round7/certify7.py`, base `round6/history/stage/final2`) |
| `counts7.py` -> `counts7.json` | counts by sub-class, court group, kind, court, decade |
| `audit_spec.py` -> `audit/ids_<sub>.txt`, `audit/read_by_agent_<sub>.txt` | audit populations (round-6 audited pairs removed) |
| `peek7.py`, `read_ids.txt` | development reading (every pair I looked at) |

Resume: `python -X utf8 r7rehear.py cands|feats|rows`; `python -X utf8 r7setaside_bo.py run|rows`;
`python -X utf8 r7setaside_base.py`; `python -X utf8 merge_setaside.py`; then certify7 per rows file (below).

## Log
- 23:19 start; read DESIGN7 §0/3/4/7, LEAN7 §0-1, ROUND6, DESIGN6 (D6-4/13/14), rules/rehear, audits.
- 23:22 `r6_audit_by_rule.py`: round-6 failures by rule (RULES7 §0). Main kind: en banc rows linked to the **order
  granting rehearing en banc** cited after "we granted rehearing en banc" (27 of 55 failures), then partial /
  limited en banc, adoption of the panel decision, docket links to the wrong decision of a docket.
- 23:25 `r7rehear.py cands` (36,090 claim records, docket index 125,562 nodes) -> 4,712 candidates; `feats` (6,794
  texts). Rules R7-C1, R7-E1..E5, R7-D1..D3. Certified; read samples; added E5 (vacate + reinstate, partial
  reinstatement), E6 (recital whose actor is another panel), narrowed C1 (a state supreme court naming itself).
- 23:30 (d): found that no round-6 `cert*/rejects.tsv` holds a `noCue` line — the linkers drop "set aside" before
  certification (rehear `skip_nocue_vacated` 1,031; below_other `no_cue_word` 522; below_sc / memo have no
  set-aside disposition form at all). So (d) = re-run rehear + below_other with set-aside admitted, plus the 421
  base rows that the frozen Lean run rejects `noCue` with "set aside" in the quote. Rules R7-S1..S11 + rehear
  R7-S8..S10, tightened over four reading rounds (precision 0.83 -> 0.93 on fresh samples).
- 23:50 final certify, proxy dev, audit specs.

## Counts (admitted by certify7; all rejects 0)

| sub-class | delta folder | rows | federal / state | kinds |
|---|---|---|---|---|
| enbanc-act (en banc court's own words vacate / withdraw / reverse / reinstate the panel decision) | `cert_enbanc_act` | 437 | 435 / 2 | vacated 378, withdrawn 38, reinstated 18, reversed 2, modified 1 |
| enbanc-order (order granting rehearing en banc) | `cert_enbanc_order` | 423 | 423 / 0 | rehearingEnBancGranted 423 |
| enbanc-silent (D6-4, panel decision cited) | `cert_enbanc_silent` | 86 | 79 / 7 | rehearingEnBancGranted 86 |
| docket (panel acts on its own earlier opinion named by date) | `cert_docket` | 267 | 267 / 0 | vacated 126, withdrawn 118, modified 11, reinstated 11, substitutedBy 1 |
| setaside (claim `setAside`, kind vacated) | `cert_setaside` | 97 | 16 / 81 | 40 claims on base rows (La. Sup. Ct. 27, Court of Military Appeals 8, Tex. Sup. Ct. 4, CA4 1) + 35 new below_other rows (La. 18, Tex. 14, Ind. 1, Ala. 1, Tex. App. 1) + 22 rehear rows (Neb. 7, Fla. DCA 4, CA5 4, CA4 2, Tex. CCA 2, CA8 1, Kan. 1, Tex. 1) |

Courts (en banc / docket): CA5 301, CA9 190, CA11 174, CA8 72 ... (en banc); CA9 82, CA8 30, CA5 28, CA3 24, D.C. 22 ...
(docket); `counts7.json`. 3 + 7 rows were already in the base (skipped).

## Proxy dev (aggregate, `score_rows.py`, rows alone, before Lean)
- en banc + docket rows (1,223): NEG hits 14/254 (enbanc_different 11/27, panel_withdrawn 3/27); CLEAN cases with a
  negative row 3/9,704; MOD 0/16; AMBIG 2/34. (Round 6 with the uninstalled classes: 122 vs 105 NEG at 93.1%.)
- set-aside rows (97): NEG 2/254 (panel_withdrawn 1, sc_reversed 1); CLEAN 0; MOD 0.

## Own sample precision (link + same status effect, read by me; fresh = not seen before the last rule change)
- enbanc-act: first 33 read: 28 right, 5 wrong (partial reinstatements, vacate-and-reinstate) -> R7-E5; fresh 30
  (seed 301): 28/30, status rows 26/27 (the wrong one: "the second panel vacated ..." -> R7-E6 added after).
- enbanc-order: 30/30 (seeds 73, 601).
- enbanc-silent: 30 distinct read (seeds 71, 91): 30/30 (one I could not settle: Murdock, target caption differs).
- docket: 30/30 (seed 74), no rule changed after.
- setaside: rounds of 12-30 drove R7-S4..S11; last fresh 30 (seed 501): 28/30 (one partial award set aside on a
  base row with scope `all`; one narrated district-court order -> R7-S4 extended after). Every one of the 97 final
  rows was seen by me at some stage (so a census audit is the honest measure).

## Audit spec for the lead (fresh blind audit, DESIGN7 §7; measure = link + same status effect, D6-13)

Populations: `audit/ids_<sub>.txt` (round-6 audited pairs, v1/v2/r1/a3 real + decoys, removed: make_packs7
`--exclude` cannot do it because round-6 ids are `h6:` and these are `h7:`). Pairs I read are NOT removed (listed in
`audit/read_by_agent_<sub>.txt`): the audit measures the rows that would be installed. Dry runs passed.

```
python -X utf8 round7/audit/make_packs7.py --class rehear7/enbanc-act    --cert round7/agents/b4rehear/cert_enbanc_act    --ids round7/agents/b4rehear/audit/ids_enbanc-act.txt    --out round7/audit/<run>/ --n 80
python -X utf8 round7/audit/make_packs7.py --class rehear7/enbanc-order  --cert round7/agents/b4rehear/cert_enbanc_order  --ids round7/agents/b4rehear/audit/ids_enbanc-order.txt  --out round7/audit/<run>/ --n 80
python -X utf8 round7/audit/make_packs7.py --class rehear7/enbanc-silent --cert round7/agents/b4rehear/cert_enbanc_silent --ids round7/agents/b4rehear/audit/ids_enbanc-silent.txt --out round7/audit/<run>/ --n 80   # census: 55 fresh rows
python -X utf8 round7/audit/make_packs7.py --class rehear7/docket        --cert round7/agents/b4rehear/cert_docket        --ids round7/agents/b4rehear/audit/ids_docket.txt        --out round7/audit/<run>/ --n 80
python -X utf8 round7/audit/make_packs7.py --class setaside7 --cert round7/agents/b4rehear/cert_setaside --cert round6/history/stage/final2 --ids round7/agents/b4rehear/audit/ids_setaside.txt --out round7/audit/<run>/ --n 97   # census
```
(populations: act 364, order 384, silent 55 (31 more were audited in round 6), docket 240, setaside 97 (40 are base
ids `h:`, found through `--cert round6/history/stage/final2`).) enbanc-act and enbanc-order may be pooled into one
class of 80 if reading time is short (order rows were 34/35 in round 6 and 30/30 here); silent must stay separate.
Scoring note: for `rehearingEnBancGranted` the round-6 COMPAT accepts rehearing_en_banc_only / vacated / withdrawn;
"the court en banc reverses the panel" rows are emitted as kind `reversed` (2 rows).

## Left out, and why
- Silent en banc linked by docket only (round-6 c-reh-docket, 6/11 in round 6): the brief asks for the panel
  decision identified by citation; 77 candidates dropped.
- Non-en-banc docket rows whose act sentence names no date (589) or a date of another decision (30): R7-D1.
- en banc rows whose cited target is an order about rehearing (154) or an en banc decision (28): R7-E1. A second
  hop (grant order -> the panel opinion it vacates) would recover some; not done.
- set aside in below_sc (Supreme Court opinions) and memo (orders): their disposition reader has no "set aside"
  form; adding it touches several round-6 rules and needs its own re-audit. Not done. "Quashed" / "annulled" alone
  are not on the DESIGN7 `set_aside` list (only rows that also say "set aside" are in).
- The round-6 guard (`rules/guard`, D6-10) was not run over the 35 new below_other set-aside rows (it writes into
  its own folder); the lead may run its kept rules over `cert_setaside` before staging.
- Proxy CLEAN false positives (3, en banc rows) were not looked at per case (dev answer key).
- Could a sub-class miss 90%? I expect all four (b) sub-classes above 90% on link + effect. Set-aside is the
  weakest (0.93 on my last fresh 30, with base-row link quality inherited from the old reader); its audit decides.
