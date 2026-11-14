# Round 8: the own-act queue, docket links, rehearing, multi-case acts, state courts, new held-out keys

Design and contract. Lead: one agent; started 14 Nov 2026 00:11. Log: `LOG.md`. State: `PROGRESS.md`.
Base: the round-7 frozen build `round7/stage/v3` (data) and `round7/out/v3` (Lean output). Decisions D8-n (section 9).

## 0. Binding rules (every agent; read this section before anything else)

1. **Rules, never rows.** A fix is a general rule of a reader, linker or candidate generator that runs over the whole
   corpus (6.9 million decisions). No list of cases, no special-casing of a citation, party, docket, label.
2. **Answer keys are for scorers only.** No reader, linker, candidate generator, brief writer or auditor may read any
   answer-key field. Keys: `round5/gold_fresh/` (dev or sealed), `gold/`, `round6/shepardized/`,
   `round6/history/split/`, SCDB / CRS files under `eval/` or `data_src`, `round5/tests/split/holdout*`,
   `events_v3/reports.tsv`, `lean-in-v3/reports.tsv`, `round7/heldout/` (time split: never run again), and
   **everything under `benchmarks/`**. Sanctioned exceptions: (a) the feed side of the notes through `round5/recog/`
   tooling only, as in rounds 5–7; (b) diagnosis agents named in their brief may read `benchmarks/<name>/SOURCE.md`,
   `MAPPING.md`, `DISAGREEMENTS.md` and the **h0-only** files the `infra` agent writes under `round8/bench_h0/` and
   `round8/results/<variant>/bench/` (per-case h0 outcomes). Never open `benchmarks/<name>/key.tsv`, `key_nodes.tsv`,
   `links.tsv`, `work/`, `raw/`, `results/` directly (they hold both halves); only `infra` reads `key*.tsv`, by a script
   that keeps half = h0 and never prints a row. A diagnosis turns into a *general rule*; a key row is never an input of
   a reader, linker or candidate generator, and no rule may test membership in any key.
3. **Dev only.** Old keys: dev halves only (`round5/gold_fresh/dev/`, Shepardized `--split dev`). New keys: h0 only.
   The h1 halves, the fresh-list sealed half and the Shepardized sealed half are scored once, by the lead, after
   `round8/FREEZE.md`. The round-7 time split (`round7/heldout/`) is not run again.
4. **Evidence = the acting court's own words** (overrulings: the overruling court, or a later court with power for
   `recognised`; history: the acting court or the target's own text).
5. **No external model.** All reading and auditing is by local Claude sub-agents (readers and auditors: `model: "opus"`).
   No Azure / OpenAI / API calls.
6. **Do not touch:** `data/`, `out/`, round-4…7 output folders and tables (write new files under `round8/`),
   `benchmarks/` (only `infra` copies scorer code from it, and only the lead runs its scorers, once, at the end),
   blog/website folders, other sessions' files (`LegalProofs/USTax/**`, `USTax/Hunt/`, `tools/hunt/`,
   `tools/taxcode/**`). Nothing is committed or pushed. Stop only processes you started.
7. **One writer on the Lean tree** (`global-law-lean/lean-proofs/LegalProofs/CaseLaw2/**`, `tools/caselaw2/cues/`,
   `CueTable.lean`, `audit/statements.lock`, `STATEMENTS.log`): the agent `lean8`. Others ask the lead. The Python
   reference (`tools/caselaw2/ref/`) has one writer: the agent `ref8`, who never reads the Lean sources.
8. Lean runs only in WSL Ubuntu: `MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash -lc '…'`. Do not change Windows security
   settings. Python files are written with the Write tool, LF endings. 24 cores are shared by many agents: big scans
   use `--procs 10` (not 22). Reuse the round-6 cache `round6/history/cache` (`round6/history/r6scan.py`, `r6lib.py`:
   zones, citation windows, disposition sentences for every decision) before rescanning.
9. Every agent works in its own folder `round8/agents/<name>/`, keeps a `NOTES.md` there (what was done, counts, files,
   open points; truthful clock times from `date`), and makes its work resumable. Copies of anything changed outside
   `round8/` go to `round8/pre/` first (`pre_round8`). An agent reports to the lead (its final message), not to anyone
   else.
10. Track agents may spawn their own reader sub-agents (`model: "opus"`), each with a written brief file and its own
    answer file. Blind audits are run only through `round8/audit/` (agent `audit8` or the lead): auditors get the
    acting text and the target's identity, never the rule, class, expected answer or why the item was picked.

## 1. Rows and certifying

Reader / linker rows use the round-7 JSON row format (`round7/DESIGN7.md` §4) and are certified with
`round7/certify7.py` (or the round-5 certifiers for recognised / operative rows), writing a delta folder under the
agent's folder. A rule that needs something the round-7 Lean cannot check (a new evidence type, a new relation, a
relaxed check) is written as a short spec (`round8/agents/<name>/LEAN_REQUEST.md`: the rule, the check, the effect,
the theorem it needs) and sent to the lead; the lead decides and passes it to `lean8`. **Round-8 mode by presence:
when no round-8 table / claim / column is present, the Lean output is byte-identical to `round7/out/v3`.**

## 2. Building and scoring a variant (agent `infra` provides the scripts)

- `python -X utf8 round8/stage8.py <name> --delta DIR … [--remove FILE] [--drop FILE] [--replace FILE]` →
  `round8/stage/<name>/` (base `round7/stage/v3`).
- `wsl/r8_run.sh <name> [ref]` → `round8/out/<name>/`.
- `bash round8/score8.sh <name>` → `round8/results/<name>/`: fresh dev (two date views), no-leak, holdout notes,
  Shepardized dev, old lists (burned, non-blind) and the four new keys on **h0 only** (FJC IDB appeals, Shadow Docket,
  SCDB disposition, state overruled tables). Never the time split, never a sealed half, never h1.

## 3. Audits

Blind, ≥ 80 items per new class (or all when fewer), stratified (federal/state, decade), decoys ≥ 10% of each pack.
Wilson 95%. A status-changing class below about 90% (point estimate) is not installed; the interval is reported.

## 4. Bridge evidence for history rows (D8-3; request `agents/orderdock/LEAN_REQUEST.md`)

A Supreme Court order O names only its own docket; the decision below X is identified by a third text W whose
subsequent-history clause cites X and then the order ("X, 123 F.3d 456 (5th Cir. 2015), cert. denied, 577 U.S. 1001").
New optional table `history_bridge.tsv` (no header, tab-separated, LF): `id`, `w_node`, `b_start`, `b_end`,
`b_quote`, `src` (6 columns). Joined to a history row like `history_anchor` (first line per id; repeats counted
`bridge_duplicates`; unknown id `bridge_unknown_ids`; malformed line `bad_rows history_bridge n`).

**Presence:** when `history_bridge.tsv` is absent or empty the runner's and the reference's output is byte-identical
to `round7/out/v3` (and every earlier regression stays byte-identical).

`checkBridge` on a history row with a bridge line (first failure is the reason; no fall-back to the plain check):
1. `bridgeMismatch` — the quote is non-empty, `b_start < b_end`, `b_end − b_start ≤ 600` (`bridge_max_len` in the cue
   table JSON), and is the text of a usable window of W's own text at that offset (hash-consistent, as `quoteOk`;
   W's windows are supplied in `cert_text.tsv` / `window_sha.tsv` like any text);
2. `bridgeDate` — date(W) ≥ date(O) (O = the row's acting node; dates from decisions2; 0 fails);
3. `bridgeClause` — the quote (normalised) contains no ";";
4. `bridgeTarget` — the compact quote contains a compact citation that the cite index maps to X (the row's target),
   at position p1 (the first such);
5. `bridgeCue` — after p1, the quote (normalised, lower-cased) contains a phrase of the new list `bridge_cue` for the
   row's kind (certDenied: "cert. denied", "certiorari denied", "cert denied"; vacated: "vacated", "judgment vacated",
   "vacated and remanded"; reversed: "rev'd", "reversed"; affirmed: "aff'd", "affirmed"; reviewDismissed:
   "cert. dismissed", "certiorari dismissed", "appeal dismissed"), at position p2 > p1 (kinds without a list fail);
5b. `bridgeChain` (D8-9) — between the end of X's citation (p1 + its length) and p2 no index key starts (no other
   citation; this refuses chains such as "X, aff'd, Y, cert. denied, O", where O acted on Y, not X);
6. `bridgeActor` — after p2, the first compact citation of the quote is one the cite index maps to O;
7. then the row's own check (plain, or orderHead with its claim, unchanged) with the target evidence taken as given
   (`selfText := true`, as the joined check of DESIGN7 §2.1): hash, window, quote, cue, disqualifiers, part, date
   order, authority.
Effect: that of the row's kind (no change to the status rules). Theorems (stated in `round8/LEAN8.md` before
proving): `bridge_sound` (admitted ⇒ 1–6 hold and the own check with `selfText` admits), `bridge_admitted_iff`,
`bridge_order` (p1 < p2 < position of O's citation), `no_bridge_no_change`. Mutants: drop the length bound; drop the
";" test; accept O's citation before X's; drop the cue; accept a citation mapping to another node; drop the date test.

## 5. Wider anchor cues, claim-gated (D8-5; request `agents/scdb8/LEAN_REQUEST.md`)

New history claim value `anchorWide` in `history_claim.tsv` (DESIGN7 §3). For an anchored history row WITH this claim,
the anchor-cue test uses the `anchor` list **plus** the new list `anchor_wide`: "circuit", "(ca1", "(ca2", "(ca3",
"(ca4", "(ca5", "(ca6", "(ca7", "(ca8", "(ca9", "(cadc", "(cafc", "c.a.", "judicial court", "court of errors",
"case below" (substring test on the normalised, lower-cased anchor quote, as the existing list). Every other check
unchanged (disqualify_anchor, evidence, part, order, conflict). Without the claim the cue list is unchanged, so the
round-7 output does not move (as D7-3 for `setAside`). A claim `anchorWide` on a row with no anchor line has no effect
(counted `hclaim_anchorwide_unused` if convenient). Theorems: `anchorWide_no_claim` (without the claim the anchored
check is the round-7 one), `anchorWide_sound` (admitted anchored row with the claim ⇒ its anchor quote has a cue of
`anchor ++ anchor_wide`, and every other anchored check holds). Mutant: apply the wide list without the claim.

## 6. Old circuits, claim-gated (D8-12; request `agents/fjc8/LEAN_REQUEST.md`)

New history claim value `oldCircuit` in `history_claim.tsv`. For a history row WITH this claim, the authority check
(`canChangeStatus`, higher-court branch) also accepts: the acting court B is a federal court of appeals of circuit 5,
the target X's court is a federal district (or bankruptcy) court whose epoch circuit is 11, and date(B) < 19811001
(Fifth Circuit Court of Appeals Reorganization Act of 1980, effective 1 Oct 1981); or B of circuit 8, X's circuit 10,
date(B) < 19290301 (Act of 28 Feb 1929). Dates from decisions2 (0 fails). Constants in the cue-table JSON
(`old_circuit`: list of [acting circuit, target circuit, before-date]). Every other check unchanged; without the claim
the authority check is the round-7 one (round-7 output unchanged). History rows only (a claim on a treatments id is
unknown, counted). Theorems: `oldCircuit_no_claim`, `oldCircuit_sound` (an admitted claimed row that the round-7
authority check refuses satisfies one listed triple with the date premise). Mutants: drop the date test; accept
the claim on a treatments row's authority.

## 9. Decisions (running list; the lead adds to it)

- D8-1 Base = round-7 `v3`; round-8 mode by presence (absent ⇒ `round7/out/v3` byte for byte).
- D8-2 New keys: tune on h0 only; h1 scored once after the freeze with `--label round8` (record in `SEALED_LOG.md`).
  Fresh-list sealed (4th use) and Shepardized sealed (3rd use) are reported but burned: they certify nothing alone.
- D8-3 (00:48) Bridge evidence (section 4) accepted for the Lean (agents `lean8`, `ref8`): it turns the orderdock
  linker's bridge note into a checked link. Docket-number evidence dropped: the corpus gives an order only its own
  docket (about 200 subsequent-history strings use an SC docket number). Rows are measured and audited meanwhile with
  the round-7 checker (`name:` / `cite:` evidence); installation decided by the blind audit either way.
- D8-4 (00:31) Contradiction replacement rule not installed (r8c01 27/40). Doctrine dominance not built (≤ 15 rows).
- D8-5 (00:52) scdb8's wider anchor cues accepted claim-gated (section 5: claim `anchorWide`, list `anchor_wide`;
  "(ca" narrowed to "(ca1".."(ca9", "(cadc", "(cafc" so "(Cal." does not match). Base output unchanged.
- D8-6 (00:52) rehear8: keep the 121 `reinstated` rows (variant with all of N). They are right as text (audited);
  dropping them because the Shepardized dev key scores them worse would be fitting the key.
- D8-7 (00:58) Bridge lines in strict mode only (DESIGN8 §4 as written); no index lines for shared reporter pages.
- D8-8 (00:58) ownact class installed after the stated cut (act verb for operative rows; caption check for citation evidence); fresh audit r8o02 77/80.
- D8-9 (01:01) Bridge chain rule (§4 step 5b) added after lean8's observation that §4 admitted "X, aff'd, Y, cert.
  denied, O" as O acting on X. lean8's readings L8-6 (first citation = first position after p2 where an index key
  starts, longest key) and L8-15 accepted; ref8 told.
- D8-10 (01:01) state8 BENCH-3 (three-judge court sitting as the whole court; a decisions2 data change) not staged
  this round: ~30 rows, no benchmark effect, and decisions2 is not a staged table. Later round.
- D8-11 (01:06) Q8-13: bridgeChain literal — any index key between X's citation and the cue fails, X's own parallel citations included.
- D8-12 (01:13) fjc8's old-circuit power accepted as Lean option 2, claim-gated (section 6, claim `oldCircuit`); the
  courts2 epoch split (option 1) is not used (it would move vertical precedent too).
- D8-13 (01:12) Position convention for §4 = ref8's Q8-4 (all comparisons in offsets of the normalised lower-cased quote; compact index i ↦ pos[i]).
- D8-14 (01:27) scdb8 D2/D2b modal sub-class installed on its near-census audit (44/48 of 49 rows); the split from D1–D5 was made after r8b01 and no fresh sample was possible (1 row left). Flagged in the report.
- D8-15 (01:40) Q8-16: ambiguous index keys are not index keys (dropped at load) for 5b and step 6; reference aligned with Lean.
