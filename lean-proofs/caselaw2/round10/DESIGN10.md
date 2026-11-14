# Round 10: syllabus re-cuts, a state-court review linker, FJC named-other-case, SCDB bare citations, Shadow Docket remand bridge in Lean, one new held-out key

Design and contract. Lead: one agent; started 14 Nov 2026 03:42. Log: `LOG.md`. State: `PROGRESS.md`.
Base: the round-9 frozen build `round9/stage/v9c` (data) and `round9/out/v9c` (Lean output, binary 22bab5cd).
Decisions D10-n (section 9).

## 0. Binding rules (every agent; read this section before anything else)

1. **Rules, never rows.** A fix is a general rule of a reader, linker or candidate generator that runs over the whole
   corpus. No list of cases, no special-casing of a citation, party, docket, label.
2. **Answer keys are for scorers only.** No reader, linker, candidate generator, brief writer or auditor may read any
   answer-key field. Keys: `round5/gold_fresh/` (dev or sealed), `gold/`, `round6/shepardized/`,
   `round6/history/split/`, SCDB / CRS files under `eval/` or `data_src`, `round5/tests/split/holdout*`,
   `events_v3/reports.tsv`, `lean-in-v3/reports.tsv`, `round7/heldout/` (never run again), and **everything under
   `benchmarks/`**. Sanctioned exceptions, as in round 9: (a) the feed side of the notes through `round5/recog/`
   tooling only; (b) diagnosis agents named in their brief may read `benchmarks/<key>/SOURCE.md`, `MAPPING.md`,
   `DISAGREEMENTS.md` of the four round-8 keys (fjc_idb_appeals, shadow_docket, scdb_disposition,
   state_overruled_tables) and the **h0-only** per-case files `round9/results/v9c/bench/<key>.h0.cases.tsv` and
   `round10/results/<variant>/bench/` (written by `round8/bench_h0/score_h0.py`). Never open
   `benchmarks/<key>/key.tsv`, `key_nodes.tsv`, `links.tsv`, `work/`, `raw/`, `results/` directly (they hold both
   halves). A diagnosis turns into a *general rule*; a key row is never an input of a reader, linker or candidate
   generator, and no rule may test membership in any key.
3. **The two round-9 keys `benchmarks/songer_treat/` and `benchmarks/brace_hall_state/` are closed to every
   model-building agent** (track agents, `lean10`, `ref10`, readers, auditors: no open, list, grep, mention in a brief;
   not even SOURCE.md / MAPPING.md). Only the dataset agent `bench10` may read their SOURCE.md / MAPPING.md / link.py /
   score.py as a model for building its own key (never key.tsv, key_nodes.tsv, work/, results/). Nobody tunes on them. They are scored
   once more (second use), by the lead, after `round10/FREEZE.md`. The state-court review linker (agent `stlink10`)
   is diagnosed only on corpus text, the dev scorers and the h0 keys.
4. **Dev only.** Old keys: dev halves only (`round5/gold_fresh/dev/`, Shepardized `--split dev`). Round-8 keys: h0
   only. Their h1 halves (third use), the fresh-list sealed half (sixth use) and the Shepardized sealed half (fifth
   use) are burned or worn; they are scored once, by the lead, after `round10/FREEZE.md`; nothing is certified on them
   alone.
5. **A new fresh held-out key** (built by the dataset agent `bench10` only, in its own new `benchmarks/<new>/`) is
   never opened, listed, grepped or mentioned by any other agent, never scored before the freeze, and scored once by
   the lead after the freeze (v9c and the frozen round-10 build together). `bench10` never reads the round-10 tracks'
   folders and never talks to them.
6. **Evidence = the acting court's own words** (overrulings: the overruling court, or a later court with power for
   `recognised`; history: the acting court or the target's own text). Syllabus / head matter is the reporter's words,
   not the court's (round 9 part zones).
7. **No external model.** All reading and auditing is by local Claude sub-agents (`model: "opus"`). No Azure / OpenAI
   / API calls.
8. **Do not touch:** `data/`, `out/`, round-4…9 output folders and tables (write new files under `round10/`),
   `benchmarks/` (only `bench10` writes its own new folder; only the lead runs scorers, on the final output, `--label
   round10`; `benchmarks/graph/` belongs to another agent), blog/website folders, other sessions' files
   (`LegalProofs/USTax/**` incl. `Entity*`, `USTax/Hunt/`, `tools/hunt/`, `tools/taxcode/**` incl. `loopholes/entity_*`).
   Nothing is committed or pushed. Stop only processes you started.
9. **One writer on the Lean tree** (`global-law-lean/lean-proofs/LegalProofs/CaseLaw2/**`, `tools/caselaw2/cues/`,
   `CueTable.lean`, `audit/statements.lock`, `STATEMENTS.log`, runner sources): the agent `lean10`. Others ask the lead.
   The Python reference (`tools/caselaw2/ref/`) has one writer: the agent `ref10`, who never reads the Lean sources.
10. **DISK IS TIGHT (binding).** C: had ~27 GB free at the start and other sessions write to it; round 9 filled it
    once (WSL root went read-only). Run `df -h /c` before every stage, Lean run or big scan; **under 8 GB: stop, tell
    the lead, delete your own intermediates**. No copy of the corpus, of `round6/history/cache`, or of a full stage
    folder. Keep your folder under ~1.5 GB. Delete your own stage/out/WSL data folders as soon as a variant is scored
    and superseded (results/ is kept). Never delete anything outside `round10/` (and in `round10/` only your own files).
11. Lean runs only in WSL Ubuntu: `MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash -lc '…'`. Do not change Windows
    security settings; never `wsl --shutdown` / `--terminate` (ask the lead). Python files are written with the Write
    tool, LF endings. 24 cores, 62 GB shared: big scans `--procs 8` at most; one Lean run per agent at a time (the run
    script admits two machine-wide). Reuse the round-6 cache (`round6/history/r6scan.py`, `r6lib.py`) and the round-8/9
    agents' scanners and work files before rescanning.
12. Every agent works in `round10/agents/<name>/`, keeps a `NOTES.md` there (what was done, counts, files, open
    points; truthful clock times from `date`; a line at least every 15 minutes while working), and makes its work
    resumable. Copies of anything changed outside `round10/` go to `round10/pre/` first. An agent reports to the lead
    (its final message), not to anyone else.
13. Track agents may spawn reader sub-agents (`model: "opus"`), each with a written brief file and its own answer
    file. Blind audits only through `round10/audit/` (HOWTO there): auditors get the acting text and the target's
    identity, never the rule, class, expected answer or why the item was picked; two auditors per pack; decoys ≥ 10%.

## 1. Rows and certifying

Round-7 JSON row format (`round7/DESIGN7.md` §4), certified with `round10/certify10.py` (= certify9 with ids `t10:` /
`h10:`, base `round9/stage/v9c`) or the round-9 certifier copies. A rule that needs something the round-9 Lean cannot
check is written as `round10/agents/<name>/LEAN_REQUEST.md` (the rule, the check, the effect, the theorem it needs);
the agent tells the lead in NOTES.md; the lead decides (D10-n) and passes it to `lean10` as a section of this file.
**Round-10 mode by presence: when no round-10 table / claim / column is present, the Lean output is byte-identical to
`round9/out/v9c`** (and `round8/out/v8e` and every earlier regression stays byte-identical).

## 2. Building and scoring a variant (agent `infra10`; marker `round10/INFRA_READY`)

- `python -X utf8 round10/stage10.py <name> --delta DIR … [--remove FILE] [--drop FILE] [--replace FILE] [--table NAME=FILE]`
  → `round10/stage/<name>/` (base `round9/stage/v9c`; unchanged tables are not copied).
- `MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash -lc 'NOBUILD=1 bash /mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/wsl/r10_run.sh <name>'`
  → `round10/out/<name>/` (NOBUILD = the frozen round-9 binary 22bab5cd).
- `bash round10/score10.sh <name>` → `round10/results/<name>/`: fresh dev (two views), no-leak, holdout notes,
  Shepardized dev, old lists (burned), the four round-8 keys on **h0 only**. Never a sealed half, never h1, never
  Songer / Brace & Hall / the new key.
- `bash round10/clean10.sh <name>` deletes a variant's stage, out and WSL data folders (results kept).

## 3. Audits

Blind, ≥ 80 items per new class (or all when fewer), stratified (federal/state, decade), decoys ≥ 10% of each pack,
two opus auditors per pack, Wilson 95%. A status-changing class below about 90% (point estimate) is not installed.
One fresh sample per decision; a re-audit after a cut excludes every earlier sample of the class (and a cut designed
on an audit's errors needs a fresh sample, D9-11). Every new rule class gets a corpus-wide audit (sample drawn from the
whole certified class, not from key cases). Run names `round10/audit/r10<letter><nn>/`.

## 4. Remand bridge evidence, optional table `history_remand.tsv` (move 5; D9-10 taken up; agent `shadow10` data, `lean10` code)

Spec from `round9/agents/shadow9/LEAN_REQUEST.md`, settled here before any code. New optional table
`history_remand.tsv` (no header, tab-separated, LF): `id`, `b_node`, `b_start`, `b_end`, `docket` (5 columns). `id` is
a history row id; `b_node` the remand decision B; `[b_start, b_end)` a quote of B's own text (B's text hash supplied
in `cert_text.tsv` / `window_sha.tsv` as for bridge quotes, round 8); `docket` a normalised docket token. First line
per id; repeats counted (`remand_dup_rows`); bad lines (≠ 5 fields, non-numeric node/offsets, not UTF-8) ignored and
counted.

**Presence:** absent or empty file ⇒ byte-identical to `round9/out/v9c`. A row WITHOUT a line: unchanged.

Check `remandBridge`, on a history row WITH a line, after the row's complete round-9 verdict admits (a failing verdict
keeps its reason; as D9-4 (2) for zones):
1. `remandCourt`: court(B) = court(target); `remandDate`: date(order) ≤ date(B) ≤ date(order) + 1,826 days and
   date(target) < date(order) (order = the row's acting node `by`).
2. `remandDocket`: `docket` is a docket token of both B and the target (the docket field the runner already loads
   for nodes; tokens normalised as the loader normalises; if the runner has no docket field, `lean10` asks the lead).
3. `remandCue`: B's quote, normalised and lower-cased, holds the cue-table phrase "supreme court" and one of the new
   cue-table list `remand_cue` ("vacat", "remand", "in light of", "further consideration"); length ≤ 600
   (`remand_quote_max`).
4. `remandTie`: B's quote holds a tie to the order: the order's compact citation key, or the order's docket token,
   or the order's date as printed (the runner's date forms).
Failure ⇒ that reason (the row is not admitted). Effect of an admitted row: as today (the evidence only moves the
link from "audit" to "checked"; status unchanged). Counters (only when the table has a line): `remand_lines`,
`remand_checked_rows`, `remand_failed_rows`, `remand_dup_rows`, `remand_bad_rows`.
Theorems (state in `round10/LEAN10.md` before proving): `no_remand_line_no_change`, `remandBridge_sound` (admitted
row with a line ⇒ B and the target share court and docket token, date(order) ≤ date(B) ≤ +1,826, cue in B's quote,
tie in B's quote, and the round-9 verdict admits), `remandThen_fail_keeps`. Mutants: B before the order; B of another
court; a docket token of B only; no tie.

**§4 amendment (D10-5, 03:50; shadow10 found the runner loads no docket per node):** `history_remand.tsv` has **9
columns**: `id`, `b_node`, `b_start`, `b_end`, `docket`, `bd_start`, `bd_end`, `t_start`, `t_end`. `[bd_start, bd_end)`
is a span of B's text, `[t_start, t_end)` a span of the target's text (both supplied in `cert_text.tsv` /
`window_sha.tsv` like bridge quotes; each span non-empty and ≤ 200 characters, `remand_docket_span_max`). Check 2
`remandDocket` becomes: let `compact(s)` = the lower-cased string with every non-alphanumeric character removed;
`compact(docket)` has ≥ 4 characters and at least one digit, and is a substring of `compact(B span)` and of
`compact(target span)`. Check 4's "the order's docket token" means `compact(docket)` found in `compact(B's quote)`.
A line with ≠ 9 fields is a bad line. Everything else in §4 unchanged. Theorem `remandBridge_sound` states the
docket clause as: compact(docket) has ≥ 4 chars incl. a digit and is a substring of both compact spans.

## 5. Further Lean sections

Added by the lead from track agents' LEAN_REQUEST.md files (D10-n), lowest priority after §4.

**§4 amendment 2 (D10-7, 04:07; `agents/shadow10/LEAN_REQUEST.md`):** `history_remand.tsv` has **12 columns**: the 9 of
D10-5 + `tie`, `o_start`, `o_end`. `[o_start, o_end)` is a span (non-empty, ≤ 300 chars, `remand_order_span_max`) of
the ORDER's own text (the row's `by`; window-hashed like the other spans). `remandTie` passes when (a) (an
unambiguous cite-index key of the order inside compact(B quote)) or (c) (a D10-6 date form of date(order) inside B's
lower-cased quote) or **(c2)**: lower(norm(O span)) holds "in light of", compact(tie) has ≥ 8 characters, and
compact(tie) is a substring of compact(O span) and of compact(B quote). **Tie (b) is dropped** (B's own docket is in
B's text by construction; it does not tie B to the order). An empty `tie` field with `o_start`/`o_end` = 0 is a good
line whose (c2) fails. A page key shared by several orders stays ambiguous (no tie). Theorem `remandBridge_sound` states
the tie as (a) ∨ (c) ∨ (c2); mutant: a tie string found in B only. shadow10 supplies lines only for rows its
pre-check passes (others stay audited, unchanged).

## 6. Trial-judgment bridge, claim `trialBridge` (move 2; `agents/stlink10/LEAN_REQUEST.md`; D10-8)

A state court of last resort D whose own judgment line acts only on the TRIAL court's judgment ("The judgment of the
district court is reversed"), reviewing a case in which the intermediate court's decision T (cited in D) had affirmed
that judgment: D's judgment undoes T. New history claim value `trialBridge` (`history_claim.tsv`). A history row (by D,
target T, kind reversed | vacated, scope as D's line) WITH the claim is checked as an anchored row (its anchor: T's
citation + an anchor cue, as today) whose main quote is D's judgment line, with the main-quote kind-cue test replaced
by **`trialBridgeD`**: the main quote holds a `hist` cue of the row's kind and a phrase of the new cue-table list
`trial_court_names` ("trial court", "district court", "circuit court", "superior court", "county court", "court of
common pleas", "chancery court", "probate court", "court below"), and none of the new list `intermediate_court_names`
("court of appeal", "appellate", "court of special appeals", "court of civil appeals", "court of criminal appeals",
"commonwealth court", "district court of appeal"); plus **`trialBridgeT`**: a second quote of T's own text, given in
the new optional table `history_tbridge.tsv` (`id`, `t_start`, `t_end`; ≤ 600 chars, `tbridge_quote_max`;
window-hashed like bridge quotes; first line per id, dups / bad lines counted), that holds the cue "affirm" and none of
"reversed", "reverse", "vacate", "set aside", "remand" (`tbridge_negative`); and **`trialBridgeDate`**: date(T) <
date(D) ≤ date(T) + 1,826 days and court(T) ≠ court(D). Every other check of the anchored row unchanged (zones, part,
power, disqualifiers). Without the claim: the round-9 check (output unchanged); a claimed row with no
`history_tbridge.tsv` line fails `trialBridgeT`. Effect: as an admitted reversed / vacated row on T.
Theorems: `trialBridge_no_claim` (without the claim the round-9 step), `trialBridge_sound` (admitted claimed row ⇒
D's quote has a kind cue + a trial-court name and no intermediate-court name, T's quote affirms with no negative cue,
dates/courts as above, the anchored checks admit), presence (`no_tbridge_table_no_change` for unclaimed rows).
Mutants: T's quote reverses; D's quote names an intermediate court; T dated after D; the claim's cue test applied
without the claim. Priority: after §4 and its amendments.

## 9. Decisions (running list; the lead adds to it)

- D10-1 Base = round-9 `v9c`; round-10 mode by presence (absent ⇒ `round9/out/v9c` byte for byte; `round8/out/v8e`
  and regressions a/a2/b/c still byte-identical).
- D10-2 Protocol: tune on the round-8 keys' h0 halves and the old dev halves only. After `round10/FREEZE.md`, once:
  the round-8 keys' h1 halves (third use), Songer and Brace & Hall (second use; both halves; label `round10`), the new
  key if built (first use; v9c as `round9v9c` and the frozen build as `round10`), fresh sealed (6th use, burned),
  Shepardized sealed (5th use, burned). Every sealed run logged in `round10/SEALED_LOG.md`.
- D10-3 Brace & Hall: no tuning split is carved (user option (b)); the state-court review linker is built blind to it.
- D10-4 Move 6 (state tables implicit misses) skipped unless capacity is idle.
- D10-5 (03:50) §4 docket evidence: the runner loads no per-node docket; shadow10's option taken — two text spans
  (B's, the target's) holding the compact docket token, in a 9-column `history_remand.tsv` (amendment after §4).
- D10-6 (03:52) §4 readings (ref10's Q10-1..10, binding on Lean and reference): Q10-2..Q10-9 accepted as ref10 wrote
  them (`round10/agents/ref10/REF_QUESTIONS10.md`): B's quote / docket spans read from a usable covering window of that
  node's own text (as bridge quotes), tab/CR/LF → space one for one, ASCII lower-case; check order court, date,
  docket, cue, tie (first failure is the reason); court = decisions2 raw court id, equal, a missing row fails
  `remandCourt`; dates from decisions2, a 0 / missing / non-calendar date fails `remandDate`, +1,826 calendar days,
  target strictly before the order; cue = plain substrings "supreme court" + a `remand_cue` phrase; tie = (a) a
  compact cite-index key mapping (unambiguously) to the order inside compact(B quote), or (b) compact(docket) inside
  compact(B quote), or (c) a date form of date(order) inside the lower-cased B quote; bad lines / unknown ids / dups /
  counters as Q10-9. **Q10-1 date forms (exactly two):** `<month> <d>, <yyyy>` with the full lower-case month name and
  the day without a leading zero ("january 5, 2015"), and `<abbr> <d>, <yyyy>` with abbr in `jan. feb. mar. apr. aug.
  sept. sep. oct. nov. dec.` (May, June, July have only the full form); new cue-table list `remand_months_abbr` if the
  Lean keeps lists there. **Q10-10:** a row whose round-9 verdict is not admitted (incl. noAuthority) keeps its verdict
  and is not counted as checked; if its remand line fails, its findings are dropped (as D9-13 for zones).
- D10-7 (04:07) §4 amendment 2: reason-case tie (c2) with an order span; tie (b) dropped (circular). Evidence only.
- D10-8 (04:07) §6 `trialBridge` accepted for the Lean (stlink10 class T, ~1,800 rows estimated); installation of rows
  still decided by a blind audit (≥ 80, fresh sample, item type B: did D's judgment undo T).
- D10-9 (04:10) readings Q10-11..Q10-17 (`agents/ref10/REF_QUESTIONS10.md`) accepted as written, binding on Lean and
  reference: (c2) failure folds into `remandTie`; a `trialBridge` claim counts only on a reversed / vacated history row
  with an anchor line and no bridge line, elsewhere it is ignored (round-9 check); check order anchored steps 1–5, then
  the plain check with `trialBridgeD` in the kind-cue's place, then `trialBridgeT`, then `trialBridgeDate`, then the
  round-9 tail (targetLater, zones, power); counters `tbridge_lines`, `tbridge_dup_rows`, `tbridge_bad_rows` (+ any
  checked/failed counter lean10 adds, named in LEAN10.md). Cue-table key names are lean10's (ref10 reads them from
  cue_table.json).
- D10-10 (04:20) Installed classes so far: syl10 RO treatments (3 rows, r10y02 3/3; `cert_ro_treat` + its remove file);
  scdb10 a10 (75 rows, r10b01 70/75 = 0.933); shadow10 C6 (126 rows, r10k01 77/80 = 0.963). Not installed: syl10
  RO history (r10y01 6/9) and RO-strict (cut designed on that audit's errors, whole class read: D9-11 applies, even
  though all 6 remaining rows were read right), scdb10 a10t (0.875) / a10n (0.825), shadow10 C2 (0.625).
- D10-11 (04:31) stlink10 s1 (1,014 rows, r10t01 0.925) and g2 (1,648 rows, r10t02 0.950) installed. Class T4
  (§6 trialBridge, 245 rows) NOT installed: r10t04 (fresh sample after the T-noTransfer cut) right 68/80 = 0.850
  [0.756, 0.912] below the bar; link+effect 0.925 (12 of 12 kind errors are reversed-vs-vacated, same status effect).
  The round-9 bar is the "right" measure (G2 0.838 / link+effect 0.875 not installed); a decision for the user. §6
  stays in the Lean as a capability (no claimed rows in the frozen build).
- D10-12 (04:50) scdb10 s10 scope rule (DESIGN7 §6 scope rule on base SC decision-below rows whose judgment quote gives
  each court's judgment its own verb; 9 rows of 323 candidates, `--replace agents/scdb10/replace_s10.tsv`) installed:
  r10b04 whole class 9/9 = 1.000 [0.701, 1.000].
- D10-13 (04:55) stlink10 rule D (judgment lines naming the intermediate court where round 6 found no disposition;
  34 rows, `delta_d2`) installed: r10t06 whole class 34/34 = 1.000 [0.898, 1.000]. Rule U (uncited, court-named-only;
  1,343 rows) NOT installed: r10t05 59/80 = 0.738 (same-surname different cases).
- D10-14 (04:55) shadow10 C9 (57 rows) NOT installed: r10k03 40/57 = 0.702.
- D10-15 (05:00) fjc10b rule N form h + rule P (1,317 rows, `agents/fjc10b/delta_n2h`) installed: r10f13 (fresh
  sample after P, which was designed on r10f11's errors) right 73/80 = 0.912 [0.830, 0.957]. FJC h0 clean drops 3 of
  6,229 (97.6 → 97.5%) while precision rises (90.4 → 90.5%); accepted as within the class's audited error rate
  (decision for the user). Not installed: form h without P (r10f11 0.887), forms x+s (r10f12 0.713). fjc10 went silent
  at 03:54 (stopped by the coordinator 04:44); fjc10b resumed from its files.
