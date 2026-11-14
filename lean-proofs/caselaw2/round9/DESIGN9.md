# Round 9: the FJC no-court-phrase pool, SCDB judgment lines, the part map in Lean, Shadow Docket GVRs, state implicit overruling, New Jersey successor authority, a new fresh held-out key

Design and contract. Lead: one agent; started 14 Nov 2026 02:04. Log: `LOG.md`. State: `PROGRESS.md`.
Base: the round-8 frozen build `round8/stage/v8e` (data) and `round8/out/v8e` (Lean output). Decisions D9-n (section 9).

## 0. Binding rules (every agent; read this section before anything else)

1. **Rules, never rows.** A fix is a general rule of a reader, linker or candidate generator that runs over the whole
   corpus (6.9 million decisions). No list of cases, no special-casing of a citation, party, docket, label.
2. **Answer keys are for scorers only.** No reader, linker, candidate generator, brief writer or auditor may read any
   answer-key field. Keys: `round5/gold_fresh/` (dev or sealed), `gold/`, `round6/shepardized/`,
   `round6/history/split/`, SCDB / CRS files under `eval/` or `data_src`, `round5/tests/split/holdout*`,
   `events_v3/reports.tsv`, `lean-in-v3/reports.tsv`, `round7/heldout/` (never run again), and **everything under
   `benchmarks/`**. Sanctioned exceptions: (a) the feed side of the notes through `round5/recog/` tooling only, as in
   rounds 5–8; (b) diagnosis agents named in their brief may read `benchmarks/<key>/SOURCE.md`, `MAPPING.md`,
   `DISAGREEMENTS.md` of the four round-8 keys (fjc_idb_appeals, shadow_docket, scdb_disposition,
   state_overruled_tables) and the **h0-only** per-case files: `round8/results/v8e/bench/<key>.h0.cases.tsv` and
   `round9/results/<variant>/bench/` (written by `round8/bench_h0/score_h0.py`). Never open `benchmarks/<key>/key.tsv`,
   `key_nodes.tsv`, `links.tsv`, `work/`, `raw/`, `results/` directly (they hold both halves). A diagnosis turns into
   a *general rule*; a key row is never an input of a reader, linker or candidate generator, and no rule may test
   membership in any key.
3. **Dev only.** Old keys: dev halves only (`round5/gold_fresh/dev/`, Shepardized `--split dev`). Round-8 keys: h0
   only. The h1 halves (second use), the fresh-list sealed half and the Shepardized sealed half (burned) are scored
   once, by the lead, after `round9/FREEZE.md`.
4. **The new fresh held-out keys of round 9** (`benchmarks/<new>/`, built by the dataset agents `bench_bh` and
   `bench_songer` only) are never opened, listed, grepped or mentioned by any other agent, never scored on any build
   before the freeze, and scored once by the lead after the freeze (v8e and the frozen round-9 build together).
   Dataset agents never read the round-9 tracks' folders and never talk to them.
5. **Evidence = the acting court's own words** (overrulings: the overruling court, or a later court with power for
   `recognised`; history: the acting court or the target's own text).
6. **No external model.** All reading and auditing is by local Claude sub-agents (readers and auditors: `model: "opus"`).
   No Azure / OpenAI / API calls.
7. **Do not touch:** `data/`, `out/`, round-4…8 output folders and tables (write new files under `round9/`),
   `benchmarks/` (only the dataset agents write their own new folder; only the lead runs scorers, once, at the end),
   blog/website folders, other sessions' files (`LegalProofs/USTax/**`, `USTax/Hunt/`, `tools/hunt/`,
   `tools/taxcode/**`). Nothing is committed or pushed. Stop only processes you started.
8. **One writer on the Lean tree** (`global-law-lean/lean-proofs/LegalProofs/CaseLaw2/**`, `tools/caselaw2/cues/`,
   `CueTable.lean`, `audit/statements.lock`, `STATEMENTS.log`, runner sources): the agent `lean9`. Others ask the lead.
   The Python reference (`tools/caselaw2/ref/`) has one writer: the agent `ref9`, who never reads the Lean sources.
9. Lean runs only in WSL Ubuntu: `MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash -lc '…'`. Do not change Windows
   security settings. Python files are written with the Write tool, LF endings. 24 cores, 62 GB shared by ~10 tracks:
   big scans `--procs 8` at most; one Lean run per agent at a time (`wsl/r9_run.sh` admits two runs machine-wide and
   queues the rest). Reuse the round-6 cache `round6/history/cache` (`round6/history/r6scan.py`, `r6lib.py`) and the
   round-8 agents' scanners and work files before rescanning.
10. Every agent works in its own folder `round9/agents/<name>/`, keeps a `NOTES.md` there (what was done, counts,
    files, open points; truthful clock times from `date`), and makes its work resumable. Copies of anything changed
    outside `round9/` go to `round9/pre/` first (`pre_round9`). An agent reports to the lead (its final message),
    not to anyone else. Write a line to NOTES.md at least every 15 minutes while working (the lead restarts silent
    agents).
11. Track agents may spawn reader sub-agents (`model: "opus"`), each with a written brief file and its own answer file.
    Blind audits only through `round9/audit/` (HOWTO there): auditors get the acting text and the target's identity,
    never the rule, class, expected answer or why the item was picked; two auditors per pack; decoys ≥ 10%.

## 1. Rows and certifying

Round-7 JSON row format (`round7/DESIGN7.md` §4), certified with `round9/certify9.py` (= certify8 with ids `t9:` /
`h9:`, base `round8/stage/v8e`) or the round-5 certifier copies. A rule that needs something the round-8 Lean cannot
check is written as `round9/agents/<name>/LEAN_REQUEST.md` (the rule, the check, the effect, the theorem it needs)
and the agent tells the lead in NOTES.md; the lead decides (D9-n) and passes it to `lean9` as a section of this file.
**Round-9 mode by presence: when no round-9 table / claim / column is present, the Lean output is byte-identical to
`round8/out/v8e`** (and every earlier regression stays byte-identical).

## 2. Building and scoring a variant (agent `infra9` provides the scripts; marker `round9/INFRA_READY`)

- `python -X utf8 round9/stage9.py <name> --delta DIR … [--remove FILE] [--drop FILE] [--replace FILE]` →
  `round9/stage/<name>/` (base `round8/stage/v8e`).
- `MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash -lc 'NOBUILD=1 bash /mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/wsl/r9_run.sh <name>'`
  → `round9/out/<name>/` (NOBUILD = the frozen round-8 binary 3b8d3e4d).
- `bash round9/score9.sh <name>` → `round9/results/<name>/`: fresh dev (two views), no-leak, holdout notes,
  Shepardized dev, old lists (burned), the four round-8 keys on **h0 only**. Never a sealed half, never h1, never
  the round-9 fresh keys.

## 3. Audits

Blind, ≥ 80 items per new class (or all when fewer), stratified (federal/state, decade), decoys ≥ 10% of each pack,
two opus auditors per pack, Wilson 95%. A status-changing class below about 90% (point estimate) is not installed.
One fresh sample per decision; a re-audit after a cut excludes every earlier sample of the class. Every new rule
class gets a corpus-wide audit (sample drawn from the whole certified class, not from key cases).

## 4. Part zones (move 3; Lean; stated here before any code; readings by `lean9` in `round9/LEAN9.md` §0)

New optional table `part_zone.tsv` (no header, tab-separated, LF): `node`, `z_start`, `z_end`, `part`, `src`
(5 columns; node and offsets numeric; offsets in the same offset space as the rows' `start`/`end` of that node's
text; `part` one of the row part names `majority`, `plurality`, `perCuriam`, `concurrence`, `dissent`, `headmatter`,
`other`). Built by the part map (agent `calpart9`) for every acting node of a staged row.

**Presence:** when `part_zone.tsv` is absent or empty, the output is byte-identical to `round8/out/v8e`.

Loading: zones per node; a node whose zones overlap or are malformed (`z_start ≥ z_end`, unknown part) loses ALL its
zones (counted `zone_bad_nodes`; its rows are checked as without zones); unknown nodes are harmless.

`checkPartZone` for a treatments or history row whose acting node has ≥ 1 zone (after the row's own checks pass, so
the first failure keeps its round-8 reason): the main quote `[start, end)` lies inside one zone (`z_start ≤ start`,
`end ≤ z_end`) whose `part` equals the row's `part` field; every joined quote likewise with its `j_part`; an anchor
or bridge quote is not zone-checked (it is evidence from another sentence of the same or another text). Failure
reason `partZone`. A row whose node has no zone: unchanged, counted `zone_missing_rows`.
Theorems (state in LEAN9.md before proving): `no_zone_no_change` (no zone line ⇒ the round-8 step);
`partZone_sound` (admitted row whose node has zones ⇒ its main quote lies inside a zone of the row's part, and the
round-8 check admits); `partZone_unique` (non-overlapping zones ⇒ at most one zone contains a non-empty quote);
`zone_bad_node_ignored`. Mutants: accept a quote that straddles a zone boundary; accept a zone of another part;
keep the zones of an overlapping node.

**Readings settled (D9-4, 02:15; from ref9's Q9-1..Q9-10; binding on Lean and reference):**
(1) The zones looked up are those of the node **whose text the main quote is from** (the text owner): the row's acting
node `by` normally; the witness W for a treatments row with a `treatment_witness.tsv` line; the target for a history
row whose certificate is the target's own text. Joined quotes: the same text owner as the main quote.
(2) `partZone` runs only on a row whose complete round-8 verdict is `ok` (after badRow, targetLater, the doctrine
ambiguity pass, the power check); any other round-8 verdict is kept. A zone failure never removes an ambiguity.
(3) A witness/recognised row and the plain check of an operativeWords row are zone-checked like any row (under (1)).
(4) Bad lines (not exactly 5 fields, non-digit node/offsets, not UTF-8): ignored, counted `bad_rows part_zone.tsv n`,
they do not poison their node. A parsed line with `z_start ≥ z_end` or a part outside the seven names (case-
sensitive) poisons its node. Overlap: [a,b) and [c,d) overlap iff a < d and c < b (touching zones do not; identical
lines do). Unknown nodes keep their zones. `zone_missing_rows` = rows that reach the zone check whose text owner has
no kept zone. Counters written only when `part_zone.tsv` has a line: zone_nodes, zone_lines, zone_bad_nodes,
zone_bad_rows, zone_checked_rows, zone_failed_rows, zone_missing_rows.

## 5. Far joined antecedents, claim `joinedFar` (move 5 B; request `agents/state9/LEAN_REQUEST.md` R-B; D9-5)

New treatments class-line claim value `joinedFar` (`treatment_class.tsv`, as `doctrine`). DESIGN7 §2.2 relation
`antecedent` keeps `start − j_end ≤ 300` (`joined_gap_max`). A row WITH the claim may instead have
`300 < start − j_end ≤ joined_far_max` (new cue-table constant, value 1200 unless the lead changes it before LEAN_READY)
if all hold, on the row's own text (a usable window of the same text covering `[j_end, start)` is supplied in
`cert_text.tsv` / `window_sha.tsv`; else `joinedFarWindow`):
1. (dropped by D9-7: no paragraph test; acts usually open a new paragraph after the discussion naming X)
2. `joinedFarKey` — no index key starts in `[j_end, start)` that the cite index maps to a node other than the row's
   target (ambiguous keys are not keys, D8-15);
3. the main quote holds an `anaphor` phrase and a cue of the row's kind (as §2.2);
4. every other `checkJoined` step unchanged. Gap above the bound: `joinedFarGap`.
Effect: as an `antecedent` row of its kind and scope. Without the claim: the round-8 check (output unchanged).
Theorems: `antecedentFar_gap` (admitted with the claim ⇒ `j_end ≤ start`, gap ≤ joined_far_max, no newline and no
other index key in the gap, anaphor + kind cue in the main quote), `joinedFar_no_claim`, `joinedFar_extends` (every
row admitted without the claim is admitted with it). Mutants: drop the other-key test; accept a gap above the bound;
drop the anaphor test for far gaps.

## 6. New Jersey successor-court authority (move 6; `agents/nj9/RULE.md`, `LEAN_REQUEST.md` option A; D9-6)

Rule (primary sources in RULE.md: NJ Const. 1947 art. XI §IV ¶¶3, 8, 14; *In re Estate of Johnson*, 240 N.J. Super.
134 (App. Div. 1990); *Hagaman*, 112 N.J. Super. 221 (Ch. Div. 1970); *Collopy*, 27 N.J. 29 (1958); *Gruschow*, 56 N.J.
Super. 146 (App. Div. 1959)): a successor court of like jurisdiction holds its predecessor's decisions at the tier
they were decided, as its own; the ordinary power rules then decide. Appellate Division over the old Supreme Court:
power (as over its own panels); Chancery Division over the Court of Chancery: power; Appellate Division / trial
divisions under the Court of Errors and Appeals: bound, no power; new Supreme Court over all three: power.
**Data, not code:** two adoption rows (`1099 ← 1095`, `1222 ← 1206`, upTo 19480914, all, binding, tag S) and retags
(adoption `1096 ← 1094` L→S; succession `1095 → 1099` U→S, `1206 → 1222` L→S), in `round9/nj/adoption.tsv` and
`round9/nj/succession.tsv` (staged by `stage9.py --table`). The Lean code and the reference code are unchanged; the
Lean adds the general theorems `adoptedSameTier_power` and `adopted_lowerTier_noPower` (statements in
`agents/nj9/LEAN_REQUEST.md`), the six `#guard`s on a four-court New Jersey fixture, and the mutants `mutAdoptAnyTier`
and `mutNoAdoptPower`. Known limit: 1,607 decisions filed under the old Supreme Court carry the Court of Errors and
Appeals' vote roll (court attribution in decisions2, not staged); no status-changing row of the round may hit one
without the lead checking it.

## 7. Implicit rejection, at-risk only, claim `implicitReject` (move 5 A; request `agents/state9/LEAN_REQUEST.md` R-A; D9-5)

New treatments class-line claim value `implicitReject`. A treatments row of a soft kind (`declinedToFollow`,
`questioned`; `kind.softNegative = true`, `changesStatus = false`) WITH the claim uses, for its cue test, the kind's
plain cue list plus the new cue-table list `implicit_reject` ("cannot agree", "do not agree", "unpersuaded", "not
convinced", "wrongly decided", "incorrectly decided", "erroneously decided", "unsound", "erroneous", "incorrect",
"mistaken", "undermined", "eroded", "discredited", "called into question", "contrary to", "depart from", "departs
from"). Every other check unchanged. A row with the claim and a status-changing kind fails `implicitBadKind`.
Effect: none on status (findings `atRisk soft:<kind>` only, as today's soft rows). Theorems:
`implicitReject_never_neg` (an admitted claimed row's effects leave every status unchanged), `implicitReject_soft`,
`implicitReject_no_claim`. Mutants: the claim admitted on an `overruled` row; the implicit cues accepted without the
claim.

## 8. Judge-form wide anchor cues (fjc9 `LEAN_REQUEST.md`; D9-9)

Under the existing claim `anchorWide` (DESIGN8 §5) the list `anchor_wide` gains "district judge", "magistrate judge",
"trial judge" (substring test on the normalised, lower-cased anchor quote). Nothing else changes; without the claim
the cue list is unchanged; every v8e `anchorWide` row passes today, so v8e output is unchanged. Theorem:
`anchorWide_sound` restated over the extended list is NOT a change of an existing statement: add
`anchorWide9_sound` (admitted anchored row with the claim ⇒ the anchor quote has a cue of `anchor ++ anchor_wide`
with the three strings) and keep the round-8 statement as it is (it must still hold; if the round-8 statement names
the old list literally, the list is split: `anchor_wide` unchanged + new list `anchor_wide9`, both used under the
claim). Mutant: the judge strings accepted without the claim.

## 9. Decisions (running list; the lead adds to it)

- D9-1 Base = round-8 `v8e`; round-9 mode by presence (absent ⇒ `round8/out/v8e` byte for byte).
- D9-2 Round-8 keys: tune on h0 only; h1 scored a second time after `round9/FREEZE.md` with `--label round9`
  (record in `SEALED_LOG.md`, say "second use"). Fresh-list sealed (fifth use) and Shepardized sealed (fourth use)
  reported, burned. New round-9 fresh keys: built blind by the dataset agents (MAPPING.md before any scoring, 50/50
  hash split via `benchlib.split_half`), scored once after the freeze on v8e and the frozen round-9 build.
- D9-3 Part zones (section 4) are the round's Lean change for move 3; `lean9` starts with it.
- D9-4 (02:15) §4 readings settled (text owner's zones; after the full round-8 verdict; bad-line/overlap rules; counters).
- D9-5 (02:25) state9's R-A (`implicitReject`, §7) and R-B (`joinedFar`, §5) accepted for the Lean, claim-gated; installation of rows still decided by their blind audits. R-C (doctrine own-tie) withdrawn by state9 (3 new pairs).
- D9-6 (02:33) New Jersey: nj9's option A (data rows + retags, §6); reference unchanged; Lean adds theorems/guards/mutants
  over the existing adoption semantics. Option B (implicit adoption from every non-split succession) not taken: it
  moves every state's successions.
- D9-7 (02:33) §5 joinedFar without the same-paragraph test (state9's reading: 32 of 75 kept with it); bound 1200.
- D9-8 (02:33) Part zones: calpart9's facts accepted with no Lean change (straddling quotes refused as intended; 137
  re-cut rows + 14 part replacements on the data side, audited with calpart9's classes; 9 syllabus quotes refused).
- D9-9 (02:37) fjc9's judge-form anchor cues accepted (§8), lowest Lean priority (after §4, §5, §7, §6).
- D9-10 (02:37) shadow9's optional `history_remand.tsv` evidence (remandBridge) deferred to a later round: its rows are
  admitted by the round-8 checks and audited (r9k01/r9k02); the evidence would only move the link from audit to
  check, and the Lean queue is full this round.
- D9-11 (02:53) scdb9 judgment readings (dfix/j/multi9, 46 rows) not installed: whole-class audit r9b01 0.867; the cut that fixes it was designed on that audit's errors and no fresh sample exists (contrast D8-14, flagged then). a9/r4w/wfix (4 rows, 4/4) installed with the 1-row remove.
- D9-12 (02:58) state9 A v2 (implicit rejection, at-risk only) installed on r9s03 72/72 (fresh sample after the v1 failure r9s02 0.694; measure = the acting court itself rejects/departs from X); calpart9 PJT/PJR/re-cut/relabel installed, PJH not (0.722).
- D9-13 (03:34) ref9's question (synthetic universes only; 0 real rows in v9a/v9b): a row whose round-8 verdict is not ok (e.g. noAuthority) keeps that verdict, but if its main quote fails the zone test it feeds no findings (atRisk:claim, panelDepartsWithoutEnBanc, ...): a quote outside its claimed part asserts nothing (as answered to lean9 Q2 at 02:18). The Lean's behaviour stands; the reference aligns.
