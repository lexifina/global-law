# Round 11: state review of uncited decisions below, a Federal Circuit linker, Supreme Court order lists as staged data, FJC two-tie identity, SCDB rehearing / en banc targets

Design and contract. Lead: one agent; started 14 Nov 2026 05:06. Log: `LOG.md`. State: `PROGRESS.md`.
Base: the round-10 frozen build `round10/stage/v10d` (data) and `round10/out/v10d` (Lean output, binary e7e32592,
`~/caselaw2/r10_bin/run_v10d` in WSL). Decisions D11-n (section 9).

## 0. Binding rules (every agent; read this section before anything else)

1. **Rules, never rows.** A fix is a general rule of a reader, linker or candidate generator that runs over the whole
   corpus. No list of cases, no special-casing of a citation, party, docket, label.
2. **Answer keys are for scorers only.** No reader, linker, candidate generator, brief writer or auditor may read any
   answer-key field. Keys: `round5/gold_fresh/` (dev or sealed), `gold/`, `round6/shepardized/`,
   `round6/history/split/`, SCDB / CRS files under `eval/` or `data_src`, `round5/tests/split/holdout*`,
   `events_v3/reports.tsv`, `lean-in-v3/reports.tsv`, `round7/heldout/`, and **everything under `benchmarks/`**.
   Sanctioned exceptions (as rounds 9–10): (a) the feed side of the notes through `round5/recog/` tooling only;
   (b) diagnosis agents named in their brief may read `benchmarks/<key>/SOURCE.md`, `MAPPING.md`, `DISAGREEMENTS.md`
   of the four round-8 keys (fjc_idb_appeals, shadow_docket, scdb_disposition, state_overruled_tables) and the
   **h0-only** per-case files `round10/results/v10d/bench/<key>.h0.cases.tsv` and `round11/results/<variant>/bench/`.
   Never open `benchmarks/<key>/key.tsv`, `key_nodes.tsv`, `links.tsv`, `work/`, `raw/`, `results/` directly (they
   hold both halves). No rule may test membership in any key.
3. **Closed keys.** `benchmarks/songer_treat/`, `benchmarks/brace_hall_state/` and `benchmarks/fedcir_dataset/` are
   closed to every model-building agent (track agents, lean11, ref11, readers, auditors): no open, list, grep, or
   mention in a brief — not even SOURCE.md / MAPPING.md. The state linker (`stlink11`) and the Federal Circuit linker
   (`fedcir11`) are diagnosed only on corpus text (and, for side effects, the dev scorers and the h0 keys).
   A round-11 fresh key (built by `bench11` only) is likewise never opened, listed, grepped or mentioned by any other
   agent; nobody reads `round11/FRESH_KEYS.txt` or `round11/agents/bench11/` except the lead's sealed script.
4. **Dev only.** Old keys: dev halves only. Round-8 keys: h0 only. h1 halves (fourth use), Songer and Brace & Hall
   (third use), Federal Circuit (second use), the fresh-list sealed half and the Shepardized sealed half (burned)
   are scored once, by the lead, after `round11/FREEZE.md`; nothing is certified on them.
5. **Evidence = the acting court's own words** (history: the acting court or the target's own text). Syllabus / head
   matter is the reporter's words (round-9 part zones). For order-list nodes (§4) the order list is the Court's own
   text.
6. **No external model.** All reading and auditing is by local Claude sub-agents (`model: "opus"`).
7. **Do not touch:** `data/`, `out/`, round-4…10 output folders and tables (write under `round11/`), `benchmarks/`
   (only `bench11` writes its own new folder; only the lead runs scorers on final output, `--label round11`;
   `benchmarks/graph/` belongs to another agent), blog/website folders, other sessions' files
   (`LegalProofs/USTax/**` incl. `Entity*`, `USTax/Hunt/`, `tools/hunt/`, `tools/taxcode/**` incl.
   `loopholes/entity_*`). Nothing is committed or pushed. Stop only processes you started.
8. **One writer on the Lean tree** (`global-law-lean/lean-proofs/LegalProofs/CaseLaw2/**`, `tools/caselaw2/cues/`,
   `CueTable.lean`, `audit/statements.lock`, `STATEMENTS.log`, runner sources): the agent `lean11` (started only if a
   §5 section is decided). The Python reference (`tools/caselaw2/ref/`): `ref11` only, who never reads the Lean.
   A rule that needs a Lean change is written as `round11/agents/<you>/LEAN_REQUEST.md` (rule, check, effect,
   theorem) and noted in NOTES.md; the lead decides (D11-n).
9. **DISK IS TIGHT (binding).** C: had ~24 GB free at the start; other sessions write to it; round 9 filled it once.
   `df -h /c` before every stage, Lean run or big scan; **under 8 GB: stop, tell the lead (NOTES.md), delete your own
   intermediates**. No copy of the corpus, of `round6/history/cache`, or of a full stage folder. Keep your folder
   under ~1.5 GB. **One live variant per agent**: `bash round11/clean11.sh <name>` as soon as it is scored and
   superseded (results/ is kept). Never delete anything outside `round11/` (and in `round11/` only your own files).
10. Lean runs only in WSL Ubuntu: `MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash -lc '…'`. Never change Windows
    security settings; never `wsl --shutdown` / `--terminate`. Python files written with the Write tool, LF endings.
    24 cores / 62 GB shared: big scans `--procs 8` at most; one Lean run per agent at a time (two machine-wide).
    Reuse the round-6 cache (`round6/history/r6scan.py`, `r6lib.py`) and earlier agents' scanners and work files.
11. Every agent works in `round11/agents/<name>/` with a `NOTES.md` (truthful clock times from `date`; **a line at
    least every 10 minutes while working** — the lead replaces agents whose folder is silent for ~20 minutes). Copies
    of anything changed outside `round11/` go to `round11/pre/` first. Report to the lead (final message) only.
12. Readers: sub-agents `model: "opus"`, each with a brief file and its own answer file. Blind audits only through
    `round11/audit/` (HOWTO there): auditors see the acting text and the target's identity, never the rule, class,
    expected answer or why the item was picked; two auditors per pack; decoys ≥ 10%.

## 1. Rows and certifying

Round-7 JSON row format (`round7/DESIGN7.md` §4), certified with `round11/certify11.py` (= certify10 with ids `t11:`
/ `h11:`, base `round10/stage/v10d`, and the §4 node overlay). **Round-11 mode by presence: with no round-11 row /
table present, the round-10 binary on the staged data reproduces `round10/out/v10d` byte for byte** (and
`round9/out/v9c`, `round8/out/v8e` and every earlier regression stay byte-identical with their own stages).

## 2. Building and scoring a variant (agent `infra11`; marker `round11/INFRA_READY`)

- `python -X utf8 round11/stage11.py <name> --delta DIR … [--remove FILE] [--drop FILE] [--replace FILE]
  [--table NAME=FILE] [--nodes DIR]` → `round11/stage/<name>/` (base `round10/stage/v10d`; unchanged tables are hard
  links). `--nodes DIR` adds order-list nodes (§4).
- `MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash -lc 'NOBUILD=1 bash /mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/wsl/r11_run.sh <name>'`
  → `round11/out/<name>/` (NOBUILD = the frozen round-10 binary e7e32592).
- `bash round11/score11.sh <name> [noold]` → `round11/results/<name>/`: fresh dev, no-leak, holdout notes,
  Shepardized dev, old lists (burned), the four round-8 keys on **h0 only**. Never a sealed half, h1, or a closed key.
- `bash round11/clean11.sh <name>` deletes a variant's stage, out and WSL data folders (results kept).

## 3. Audits

Blind, ≥ 80 items per new class (or all when fewer), stratified (state/federal, decade), decoys ≥ 10% of each pack,
two opus auditors per pack, Wilson 95%. **Measure: "right" = same case, the acting court itself disposed of the
target, exact kind (reversed / vacated / modified / affirmed) and scope**, as rounds 9–10; link and link+effect are
reported too. A status-changing class below about 90% (point estimate) is not installed. One fresh sample per
decision; a re-audit after a cut excludes every earlier sample of the class, and a cut designed on an audit's errors
needs a fresh sample (D9-11). Samples are drawn from the whole certified class corpus-wide (never from key cases).
Run names `round11/audit/r11<letter><nn>/` (letters: stlink11 t, fedcir11 c, shadow11 k, orders11 o, fjc11 f,
scdb11 b, lead a, infra11 x).

## 4. Supreme Court order lists as staged nodes (agents `orders11` data, `infra11` plumbing, `shadow11` rows)

The corpus lacks most order lists of 2006–09 and 2020–25 (round 9 `shadow9` gap count: ~26.5% of the Shadow Docket
h0 NEG orders). `orders11` obtains them from a lawful public source (supremecourt.gov order lists — public-domain
government documents — or the Journal of the Supreme Court): polite pacing (≥ 3 s between requests, one connection,
a generic user agent naming no person), no WAF / CAPTCHA / login bypass (a 403/429/challenge page = stop that source
and report), every URL + sha256 + byte count in `round11/data_orders/SOURCES.tsv`. PDFs are converted to text and
deleted (or kept only while converting); `round11/data_orders/` holds compact text only.

Shape (settled with `infra11`; `orders11` writes, `infra11` loads):
- `round11/data_orders/nodes.tsv` — one row per order-list entry that disposes of a case (one node per docket
  entry, the way the S. Ct. reporter prints a memorandum order: GVR, vacated and remanded, reversed, affirmed, cert
  denied may be skipped): local id, docket number(s), order date (yyyymmdd), caption as printed, disposition words,
  the list file + line span. `text/<local id>.txt`: the node's own text = the list's caption line + the entry's
  disposition sentence(s) verbatim (and the list's date heading), UTF-8, LF.
- `infra11` maps local ids to node ids N, N+1, … above the corpus node count, writes the decisions2 rows (court id
  of the Supreme Court as the corpus uses it, date, unit/bench/publication/kind as the corpus's S. Ct. memorandum
  orders, text sha1 of the text file), and gives every round-11 tool (certify11, zones11, audit packs, more_text, the
  r6lib text accessor used by linkers) one overlay module `round11/nodes11.py` that returns node metadata
  (court, date, name, docket) and text for the new ids. Present only when a variant is staged with `--nodes`; absent
  ⇒ round-10 output byte for byte.
- Rows (`shadow11`): history rows with `by` = the new order node and target = the decision below, by the round-8–10
  Shadow rules (C6 full-name caption; remand-bridge / remandtext; "reported below" if printed), certified like any
  row. Each new class gets its corpus-wide blind audit.
If the source is unreachable or blocked, `orders11` writes `round11/data_orders/FEASIBILITY.md`: exactly what failed
(URL, status, date), what was tried, and what it would take.

## 5. Lean sections (added by the lead from LEAN_REQUEST.md files)

### §5.1 Claim `anchorTribunal` (D11-4, 05:22; `agents/fedcir11/LEAN_REQUEST.md`)
A Federal Circuit / CCPA opinion names the decision under review by its tribunal ("The Court of International Trade
sustained …", "the Court of Federal Claims granted summary judgment …"). New history claim value `anchorTribunal` in
`history_claim.tsv` (DESIGN7 §3 claim mechanism, as `anchorWide`). For an anchored history row WITH this claim, the
anchor-cue test (check 2 of the anchored check) uses the union of the lists `anchor`, `anchor_wide`, `anchor_wide9`
(i.e. what `anchorWide` uses) and a NEW cue-table list `anchor_tribunal` = "court of international trade",
"customs court", "court of federal claims", "claims court", "veterans court", "court of veterans appeals"
(substring test on the normalised, lower-cased anchor quote, as today). Every other check unchanged
(disqualify_anchor, target evidence inside the anchor quote, anchor part / zones, the disposition quote's cue /
disqualifier / part, date order, authority, power). A claim on a row with no anchor line, or on a non-history row,
has no effect (counted: `hclaim_anchortribunal`, `hclaim_anchortribunal_unused`). A row with both `anchorWide` and
`anchorTribunal` uses the union. No existing list changes. Without the claim nothing changes (v10d, v9c, v8e and
regressions byte-identical).
Theorems (state in `round11/LEAN11.md` before code): `anchorTribunal_no_claim` (without the claim the anchored check
is the round-10 one), `anchorTribunal_sound` (an admitted anchored row with the claim has an anchor cue of the union
list and every other anchored check holds), presence (`no_tribunal_claim_no_change`). Mutants: the new list applied
without the claim; the new list dropped with the claim (claimed tribunal row admitted ⇒ killed by soundness only if
the cue is present; guard the diagonal).

### §5.2 Identity-tie evidence, optional table `history_identity.tsv` (D11-5, 05:40; `agents/stlink11/LEAN_REQUEST.md`; modelled on DESIGN10 §4's remandDocket)
An uncited decision below T is picked by identity ties (a docket number, citation or date of T printed in D); today
only the audit covers them. New optional table `history_identity.tsv` (no header, tab-separated, LF; 7 columns):
`id`, `form` (`docket` | `cite` | `date`), `token`, `d_start`, `d_end`, `t_start`, `t_end`. `[d_start, d_end)` is a
span of the acting node D's (`by`) own text, `[t_start, t_end)` a span of the target T's own text, each read from a
usable covering window of that node's text (supplied in `cert_text.tsv` / `window_sha.tsv` like bridge quotes;
tab/CR/LF → space one for one; ASCII lower-case), each non-empty and ≤ 200 characters (`identity_span_max`). First
line per id; repeats counted (`identity_dup_rows`); bad lines (≠ 7 fields, non-numeric offsets, unknown form, not
UTF-8) ignored and counted (`identity_bad_rows`); unknown ids counted.
**Presence:** absent or empty file ⇒ byte-identical to round 10. A row WITHOUT a line: unchanged.
Check `identityTie`, on a history row WITH a line, after the row's complete round-10 verdict admits (a failing verdict
keeps its reason and is not counted as checked; as D10-6 Q10-10):
- `docket` / `cite`: `compact(s)` = lower-cased string with every non-alphanumeric character removed;
  compact(token) has ≥ 4 characters and at least one digit, and is a substring of compact(D span) and of
  compact(T span).
- `date`: token is `yyyymmdd`, equals the decisions2 date of T (0 / missing fails), and both lower-cased spans hold a
  date form of it (exactly the two D10-6 Q10-1 forms: full month name, or the `remand_months_abbr` abbreviations,
  `<d>, <yyyy>` with the day without a leading zero).
Failure ⇒ reason `identityTie` (the row is not admitted; its findings dropped). Effect of a passing row: as today
(evidence only). Counters (only when the table has a line): `identity_lines`, `identity_checked_rows`,
`identity_failed_rows`, `identity_dup_rows`, `identity_bad_rows`.
Theorems (state in LEAN11.md before code): `no_identity_line_no_change`, `identityTie_sound` (admitted row with a
line ⇒ the round-10 verdict admits and the form's condition holds on the two spans), `identityThen_fail_keeps`.
Mutants: a token found in D's span only; a date token ≠ date(T); a span over 200 characters accepted.
Priority: after §5.1's gates are green and LEAN_READY for §5.1 is written.

## 9. Decisions (running list; the lead adds to it)

- D11-1 Base = round-10 `v10d`; round-11 mode by presence (absent ⇒ `round10/out/v10d` byte for byte).
- D11-2 Protocol: tune on the round-8 keys' h0 halves and old dev halves only. After `round11/FREEZE.md`, once: h1
  halves (fourth use), Songer and Brace & Hall (third use), Federal Circuit (second use), a round-11 fresh key if
  built (first use; v10d as `round10v10d` and the frozen build as `round11`), fresh sealed and Shepardized sealed
  (burned). Every sealed run logged in `round11/SEALED_LOG.md`.
- D11-3 The Federal Circuit linker is built blind to `fedcir_dataset` (no tuning split carved).
- D11-4 (05:22) §5.1 claim `anchorTribunal` accepted for the Lean (fedcir11: ~316 rows whose only anchor cue is a
  tribunal name, ~110 status-changing). `lean11` and `ref11` started. Rows installed only after their blind audit.
- D11-5 (05:40) §5.2 identity-tie evidence table accepted (stlink11 U2: docket 95 / date 88 / cite 421 lines on 543
  rows). Evidence only; after §5.1. U2 (r11t01 0.963) is installable without it.
- D11-6 (05:51) Installed so far: stlink11 U2 (`delta_u2c`, 543 rows, r11t01 0.963); scdb11 R1 (`cert_r1` 42 rows +
  `--remove remove_r1.txt` 45 rows, r11b01 0.976 / r11b02 1.000). Not installed: scdb11 R2 v3 (r11b04 44/49 = 0.898,
  below the bar and under 80 items), R2 v2 (0.512), R3 (0.500); stlink11 u2n (0.800), u2e (0.863); fjc11 X2b (0.850);
  fedcir11 lean-cue class (0.841), rule R (0.883); shadow11 C11 (0.850). fedcir11 tribunal class (r11c02 0.912)
  installs with the §5.1 binary.
- D11-7 (05:55) stlink11 u2w (`delta_u2w`, 149 rows, r11t05 0.963) installed.
- D11-8 (05:58) §5.2 readings: lean11 Q-L11-1 and ref11 Q11-5..Q11-10 (`agents/ref11/REF_QUESTIONS11.md`) accepted as written and binding on both sides: an identity line whose id is no history row is ignored and written in NO summary counter ("unknown ids counted" in §5.2 means only internally / the loader's line count); the five named counters only, written only when the file has a line; date token = exactly 8 ASCII digits equal to T's non-zero decisions2 date; `cite` tested exactly as `docket`.
- D11-9 (06:02) scdb11 R4 (a higher state court's refusal of review is not the judgment under review; `cert_r4` 4 rows + `--remove remove_r4.txt` 5 rows; whole class read: r11b06 4/4, r11b07 removals 5/5) installed.
- D11-10 (06:03) shadow11 order-list rows installed (`cert_olist`, 431 vacated rows on the §4 order nodes, staged with `--nodes round11/data_orders`): olist-C6 395 rows r11k02 80/80 = 1.000 [0.954, 1.000]; olist-K9 (remand bridge) 36 rows r11k03 whole class 35/36 = 0.972 [0.858, 0.995]. shadow11 C11 (r11k01 17/20 = 0.850) not installed.
- D11-11 (06:28) shadow11 cert_olist2 (28 rows on the 65 appended order nodes; same rules; whole class r11k04 27/28 = 0.964 [0.823, 0.994]) installed.
