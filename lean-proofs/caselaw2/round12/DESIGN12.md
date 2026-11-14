# Round 12: a small targeted round — Shadow Docket order nodes, en banc vacatur of the court's own panel, Federal Circuit district / other-target reviews, Brace & Hall third tie

Design and contract. Lead: one agent; started 14 Nov 2026 07:00. Log: `LOG.md`. State: `PROGRESS.md`.
Base: the round-11 frozen build `round11/stage/v11d` (data, incl. 1,045 order nodes) and `round11/out/v11d` (Lean
output, binary s51 sha1 a1cc4296, `~/caselaw2/r11_bin/caselaw2_lean11_s51` in WSL). Decisions D12-n (section 9).
Round-11 analysis that sets this round's scope: `round11/ROUND11.md` (plateau analysis, ranked moves).
**Out of scope this round:** SCDB disposition work, the state overruled tables, the FJC "which ruling" reader.
**Not installed this round (pending user decisions):** state T4 (§6 trial bridge), SCDB R2 v3 (88 rows), the §5.2
identity lines (139). Nobody stages them into a round-12 candidate.

## 0. Binding rules (every agent; read this section before anything else)

1. **Rules, never rows.** A fix is a general rule of a reader, linker or candidate generator that runs over the whole
   corpus. No list of cases, no special-casing of a citation, party, docket, label.
2. **Answer keys are for scorers only.** No reader, linker, candidate generator, brief writer or auditor may read any
   answer-key field. Keys: `round5/gold_fresh/` (dev or sealed), `gold/`, `round6/shepardized/`,
   `round6/history/split/`, SCDB / CRS files under `eval/` or `data_src`, `round5/tests/split/holdout*`,
   `events_v3/reports.tsv`, `lean-in-v3/reports.tsv`, `round7/heldout/`, and **everything under `benchmarks/`**.
   Sanctioned exceptions (as rounds 9–11): (a) the feed side of the notes through `round5/recog/` tooling only;
   (b) diagnosis agents named in their brief may read `benchmarks/<key>/SOURCE.md`, `MAPPING.md`, `DISAGREEMENTS.md`
   of the four round-8 keys (fjc_idb_appeals, shadow_docket, scdb_disposition, state_overruled_tables) and the
   **h0-only** per-case files `round11/results/v11d/bench/<key>.h0.cases.tsv` (and `round12/results/<variant>/bench/`).
   Never open `benchmarks/<key>/key.tsv`, `key_nodes.tsv`, `links.tsv`, `work/`, `raw/`, `results/` directly (they
   hold both halves). No rule may test membership in any key.
3. **Closed keys.** `benchmarks/songer_treat/`, `benchmarks/brace_hall_state/`, `benchmarks/fedcir_dataset/` and
   `benchmarks/bhk_enbanc/` are closed to every model-building agent (track agents, readers, auditors, any Lean /
   reference agent): no open, list, grep, glob, or mention in a brief — not even SOURCE.md / MAPPING.md / REPORT.md.
   The en banc, Federal Circuit and state linkers are diagnosed only on corpus text and the dev scorers / h0 keys.
   A round-12 fresh key (built by `bench12` only) is likewise never opened, listed, grepped or mentioned by any other
   agent; nobody reads `round12/FRESH_KEYS.txt` or `round12/agents/bench12/` except the lead's sealed script.
4. **Dev only.** Old keys: dev halves only. Round-8 keys: h0 only. h1 halves (fifth use), Songer and Brace & Hall
   (fourth use), Federal Circuit (third use), bhk_enbanc (second use), a round-12 fresh key (first use), the
   fresh-list sealed half and the Shepardized sealed half (burned) are scored once, by the lead, after
   `round12/FREEZE.md`; nothing is certified on them.
5. **Evidence = the acting court's own words** (history: the acting court or the target's own text). Syllabus / head
   matter is the reporter's words (round-9 part zones). Order-list nodes: the Journal entry is the Court's own text.
6. **No external model.** All reading and auditing is by local Claude sub-agents (`model: "opus"`).
7. **Do not touch:** `data/`, `out/`, round-4…11 output folders and tables (write under `round12/`; copy what you
   change), `benchmarks/` (only `bench12` writes its own new folder; only the lead runs scorers on final output,
   `--label round12`; `benchmarks/graph/` belongs to another agent), blog/website folders, other sessions' files
   (`LegalProofs/USTax/**`, `tools/hunt/`, `tools/taxcode/**`). Nothing is committed or pushed. Stop only processes
   you started.
8. **One writer on the Lean tree** (`global-law-lean/lean-proofs/LegalProofs/CaseLaw2/**`, `tools/caselaw2/cues/`,
   `CueTable.lean`, `audit/statements.lock`, `STATEMENTS.log`, runner sources). No Lean change is planned this round.
   A rule that needs one is written as `round12/agents/<you>/LEAN_REQUEST.md` (rule, check, effect, theorem) and noted
   in NOTES.md; the lead decides (D12-n) and then starts a single Lean agent and a separate reference agent.
9. **DISK IS TIGHT (binding).** C: had ~20 GB free at the start; other sessions write to it; WSL's disk lives on C:.
   `df -h /c` before every stage, Lean run or big scan; **under 8 GB: stop, tell the lead (NOTES.md), delete your own
   intermediates**. No copy of the corpus, of `round6/history/cache`, or of a full stage folder. Keep your folder
   under ~1 GB. **One live variant per agent**: `bash round12/clean12.sh <name>` as soon as it is scored (results
   kept). Only variants staged with `--nodes` write a new decisions2 (~870 MB + ~1.2 GB in WSL): only `shadow12` and
   the lead stage with `--nodes`, one at a time. Never delete anything outside `round12/` (in it only your own files).
10. Lean runs only in WSL Ubuntu: `MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash -lc '…'`. Never change Windows
    security settings; never `wsl --shutdown` / `--terminate`. Python files written with the Write tool, LF endings.
    24 cores / 62 GB shared: big scans `--procs 8` at most; one Lean run per agent at a time (two machine-wide).
11. Every agent works in `round12/agents/<name>/` with a `NOTES.md` (truthful clock times from `date`; **a line at
    least every 10 minutes while working**; the lead replaces agents whose folder is silent ~20 minutes). Copies of
    anything changed outside `round12/` go to `round12/pre/` first. Report to the lead (final message) only. Do not go
    idle waiting on background work without a deadline: poll with a short loop and a stated deadline, and log what
    you wait for.
12. Readers: sub-agents `model: "opus"`, each with a brief file and its own answer file. Blind audits only through
    `round12/audit/` (HOWTO there): auditors see the acting text and the target's identity, never the rule, class,
    expected answer or why the item was picked; two auditors per pack; decoys ≥ 10%.

## 1. Rows and certifying
Round-7 JSON row format (`round7/DESIGN7.md` §4), certified with `round12/certify12.py` (= certify11 with ids
`t12:` / `h12:`, base `round11/stage/v11d`, node overlay `round12/nodes12.py`). **Round-12 mode by presence: with no
round-12 row / table present, the frozen round-11 binary on the staged data reproduces `round11/out/v11d` byte for
byte** (and the round-11 tools still reproduce `round10/out/v10d`, `round9/out/v9c`, `round8/out/v8e`).

## 2. Building and scoring a variant (agent `infra12`; marker `round12/INFRA_READY`)
- `python -X utf8 round12/stage12.py <name> --delta DIR … [--remove FILE] [--drop FILE] [--replace FILE]
  [--table NAME=FILE] [--nodes DIR]` → `round12/stage/<name>/` (base `round11/stage/v11d`, which already holds the
  1,045 round-11 order nodes; unchanged tables are hard links; no `--nodes` ⇒ v11d's decisions2 / nodes hard-linked).
- `MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash -lc 'NOBUILD=1 bash /mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/wsl/r12_run.sh <name>'`
  → `round12/out/<name>/` (NOBUILD = the frozen round-11 binary s51 a1cc4296).
- `bash round12/score12.sh <name> [noold]` → `round12/results/<name>/`: fresh dev, no-leak, holdout notes,
  Shepardized dev, old lists (burned), the four round-8 keys on **h0 only**. Never a sealed half, h1, or a closed key.
  Effects are measured against v11d (`round11/results/v11d/`).
- `bash round12/clean12.sh <name>` deletes a variant's stage, out and WSL data folders (results kept).

## 3. Audits
Blind, ≥ 80 items per new class (or all when fewer), stratified, decoys ≥ 10% of each pack, two opus auditors per
pack, Wilson 95%. **Measure: "right" = same case, the acting court itself disposed of the target, exact kind
(reversed / vacated / modified / affirmed) and scope**; link and link+effect are reported too. A status-changing
class below about 0.90 (point estimate) is not installed. One fresh sample per decision; a re-audit after a cut
excludes every earlier sample of the class, and a cut designed on an audit's errors needs a fresh sample (D9-11).
Samples are drawn from the whole certified class corpus-wide (never from key cases). **Exclusion of earlier samples
matches by (table, by, target, kind) from the start** (round 11's bug: id-only matching across h10/h11/h12 ids
excluded nothing); `make_packs12 --exclude` accepts any earlier round's `sample.tsv` and the self-test proves it.
Run names `round12/audit/r12<letter><nn>/` (letters: shadow12 k, enbanc12 e, fedcir12 c, stlink12 t, orders12 o,
lead a, infra12 x).

## 4. Order nodes, round 12 (agents `orders12` data, `infra12` plumbing, `shadow12` rows)
`round12/data_orders/` = round 11's 1,045 nodes (same local ids, same order, first in the file) + appended nodes,
same FORMAT (`round11/data_orders/FORMAT.md`). Node ids are assigned in file order from N = 6,892,454, so the 1,045
round-11 nodes keep their ids. Appended: Journal terms not yet held (OT2010–13, OT2015, OT2017–18) under round 11's
rule (an entry of a node class becomes a node when one of its dockets has no corpus S. Ct. node within ±10 days),
and — if `orders12` and `shadow12` find it is what blocks the 2005 misses — per-entry nodes for entries whose corpus
node is a multi-docket long list (a stated rule, its own `src` tag). The dropped "fi"/"ff"/"fl" ligature in the later
Journals' extraction is repaired if it affects parsing or caption names, by a documented rule (re-extraction with a
glyph-aware method, or a normalisation rule checked on the corpus vocabulary); every node whose text changes is listed
in `round12/data_orders/CHANGED.tsv` (old sha1, new sha1). Rows by changed nodes are re-certified by `shadow12` (the
v11d rows of the same rules are then dropped with `--drop` / replaced; never two rows of one rule for one pair).
Fetching: supremecourt.gov public documents only, ≥ 3 s between requests, one connection, a generic user agent, no
WAF / CAPTCHA / login bypass (a 403 / 429 / challenge = stop that source and report), every URL + time + status +
bytes + sha256 in `round12/data_orders/SOURCES.tsv`, PDFs deleted after conversion.

## 5. Lean sections
None planned. Added here by the lead only from a LEAN_REQUEST.md (theorems stated before code; no `sorry` / new
axiom / `native_decide`; existing statements unchanged; lock + `audit.py check` green; a mutant per new rule; Python
reference by a separate agent that never reads the Lean; differential test; the real tree is never patched during
gates).

## 9. Decisions (running list; the lead adds to it)
- D12-1 Base = round-11 `v11d` (binary s51 a1cc4296); round-12 mode by presence.
- D12-2 Protocol: tune on round-8 h0 halves and old dev halves only. After `round12/FREEZE.md`, once: h1 halves
  (fifth use), Songer and Brace & Hall (fourth use), Federal Circuit (third use), bhk_enbanc (second use; v11d
  figures exist as `round11`), a round-12 fresh key if built (first use; v11d as `round11v11d`, frozen as `round12`),
  fresh sealed and Shepardized sealed (burned). Every sealed run logged in `round12/SEALED_LOG.md`.
- D12-3 Pending user decisions are not installed: T4, SCDB R2 v3, §5.2 identity lines. An en banc class may overlap
  SCDB R2 v3's population; it is installed only on its own fresh ≥ 80-item audit excluding r11b03 / r11b04 samples.
- D12-4 (07:31) A class cut on an audit's errors is installable only on a fresh audit of >= 80 items (or of the whole class when it has <= 80 rows); a fresh "whole remainder" of fewer items does not qualify. EB12 v6 (101 rows; fresh remainder 26/27, biased items 64/67) is therefore not installed and goes to the user.
- D12-5 (07:32) stlink12 u2t (delta_u2t3, 402 rows) installed: r12t01 0.950, r12t02 0.938.
- D12-6 (07:38) shadow12 cert_c8 + cert_newnodes + cert_recert (--drop drop_recert) with --nodes round12/data_orders installed; cert_sub not.
- D12-7 (07:38) fedcir12 form L other-target (26 rows; 9/10 in a post-hoc split of r12c01) not installed; nothing from fedcir12 installed.
