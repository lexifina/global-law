# caselaw-lean-2: trust inventory (DESIGN D6, seL4-style)

**Headline.**
- **Where it ran:** Windows Application Control blocks the Windows Lean toolchain and the compiled `caselaw2.exe`
  on this machine, so the build, the statement audit and every run reported here were made under **Linux Lean
  4.35.0 in WSL Ubuntu** (elan's official toolchain, `x86_64-unknown-linux-gnu`), with the runner compiled as a
  native Linux executable (`run_lean_wsl.sh`; LEAN.md "Running under WSL"). The sources are the Windows tree,
  copied unchanged. The trust in the Lean compiler (below) is therefore trust in the Linux toolchain's compiler.
- **Proved:** 141 kernel-checked theorems, each statement locked. Axioms stay within {propext, Classical.choice,
  Quot.sound}; 4 theorems use none. No `sorry`, `axiom` or `native_decide` anywhere.
- **Refinement:** every runner verdict is computed by the Spec's functions through hash indexes proved equal to the
  Spec's list scans.
- **Certificates:** every admitted row passed a checker with a soundness theorem. The checker runs compiled, so
  admission trusts the Lean compiler.
- **Trusted base:** about 1,900 lines of Spec and type definitions, which must be read against doctrine.md, plus the
  doctrine tables (data).
- **Unverified glue:** TSV parsing and output, about 1,480 lines (`Run`, `Data`, `Tsv`). Fuzzed against a SCHEMA
  oracle and the reference: parsing, round trip and quote-at-offset in code points (FUZZ.md). The nine bugs the
  fuzzer found are fixed and verified (FUZZ_BUGS.md).

## Proved (kernel)

These are `lake build LegalProofs.CaseLaw2`, `audit/audit.py check` and `LegalProofs/CaseLaw2/Audit.lean`.

- 141 theorems, all listed in `Registry.lean` and in LEAN.md (4 for witness rows in round 4, 6 added in the five-limits pass, 1 for fuzz bug
  FB-L2, 9 for the hunt fixes, 14 in `Hunt.lean`, 23 in `Spec/Lines.lean` for round 2; each logged in
  `STATEMENTS.log`; no earlier statement changed). Last checked 12 Nov 23:25 under WSL: `audit.py check` reports
  141 theorems, 4 with no axioms, 0 statement changes, 0 problems.
- Each statement and axiom list is locked by `#guard_msgs` in `Audit.lean`, which is part of the build. A changed
  statement stops the build. `audit.py lock --reason` is the only way to accept a change, and it logs the change in
  `STATEMENTS.log`.
- **Spec theorems:**
  - authority §9 22(a)–(d);
  - power (no panel overrules a panel under a strong rule; no lower court over a higher; only SCOTUS over SCOTUS;
    no cross-system power; no power over later decisions);
  - status (order independence, partial scope, prospectivity, supersession, monotonicity with the revival
    counterexample, soft and inferred treatments inert);
  - resolver and splits (soundness, SCOTUS resolves);
  - Horty (consistency closed under removal, forcing, result ⊑ reason, answer embedding);
  - findings sanity;
  - certificate soundness, window hashes (`checkCert_window_hash`) and citation-index resolution
    (`checkCert_cite_index`);
  - the new atRisk families (`claimRisk_needs_no_power`, `soft_claim_disjoint`, `contraryBinding_needs_binding`).
- **Refinement theorems:** `exec_lookups_eq_spec`, `exec_eventLookups_eq_spec`, `exec_force_eq_spec`,
  `exec_canChangeStatus_eq_spec` and `exec_status_eq_spec`. All rest on one generic lemma, `index_getD`.

## Proved by computation (`#guard`, evaluated by the compiler at build time)

- **211 `#guard`s:**
  - 133 real-case replays in `Examples.lean` (35 of them for round 2);
  - 44 in `Hunt.lean`;
  - 16 SHA-1 vectors;
  - 14 Horty examples;
  - 3 mutation-matrix guards in `Mutants.lean`;
  - 1 registry count.
- **Mutation (D3):** 26 properties against 26 mutants. Every property holds of the Spec, every property is killed by
  at least one mutant, and every mutant is caught. The matrix is in LEAN.md.
- `#guard` trusts the compiler, unlike `decide`. The concrete theorem `revival_counterexample` uses kernel `decide`.

## Certificate-checked (compiled checker; trusts the Lean compiler)

- **Treatment and history rows:** admitted only when `Cert.check` returns `ok` or `okUnverifiedBy`.
  `checkCert_sound` proves admission implies every condition:
  - known text hash;
  - covering window;
  - the quote at the stated character offset;
  - a cue of the asserted kind;
  - no disqualifier;
  - target evidence present, and, when `cite_index.tsv` is supplied, a `cite:` evidence resolves through the index
    to the row's target node (`checkCert_cite_index`: `index(compact cite) = target`);
  - majority, plurality or per curiam part;
  - date order;
  - power (`ok`) or an unknown deciding court (`okUnverifiedBy`).
- **Holdings' sentences:** checked for hash and quote at offset.
- **What this does not certify:** that the reading is legally right. It only certifies that these words, at this
  place, in this part of this court's opinion, warrant the row (prior_art §5.6).
- **Window hashes are checked inside Lean** (five-limits pass). When `window_sha.tsv` is supplied, every window the
  checker uses (for the quote and for the target context) must have a recorded digest, and the checker computes the
  SHA-1 of the window text itself (`Sha1.hex`, pure Lean, no FFI; 16 `#guard` test vectors from Python `hashlib`) and
  compares. `checkCert_window_hash` proves: an admitted row's quote sits in a well-formed window whose computed SHA-1
  equals the recorded digest. Each digest is computed once per run and cached in a `Thunk` that `Window.digest_eq`
  pins to `Sha1.hex text`.
- What stays outside Lean: `window_sha.tsv` is written by `tools/caselaw2/window_sha.py`, which reads each decision
  from git HEAD, checks that the file's SHA-1 equals `text_sha`, and hashes the normalised cut `[start0, end0)`. So
  Lean checks *window text = audit copy's window*; that the audit copy's window is the corpus text at `text_sha`
  rests on that script (on snap5 all 336,242 windows matched their corpus cut).

## Tested only

- **Glue:** the runner's TSV translation and output, `Run.lean`, `Data.lean` and `Tsv.lean` (about 860 lines). It is
  exercised by `fixtures/` (all 13 SCHEMA files, every output kind) and a full-scale load and citation pass on
  synthetic decisions (6.89M nodes, 6.04M citations).
- **Glue fuzzing** (FUZZ.md, `tools/caselaw2/fuzz/`):
  - Run A, 300 cases with Lean: the loaders reject and log every row SCHEMA rejects and parse every other row to the
    oracle's values; a re-serialised row loads back identically; `Cert.quoteOk` and its slice match Python's
    code-point slicing.
  - Run B: 5,000 cases against the reference only. Its Lean half awaits Application Control.
  - Every real certificate (346,835 rows) was recomputed in Python; there are 0 disagreements with the runner.
  - The open Lean bugs FB-L1 to FB-L8 are in FUZZ_BUGS.md.
- The Horty check in the runner (`factors.tsv`) has not been exercised on fixtures.
- **Differential testing (D4)** against the independent Python reference: done, see `DIFFTEST.md`. The final sweep of
  5,000 fresh generated universes leaves a residual of under 0.01% of compared keys, all triaged. The real data run
  so far (supersessions on all 6.9M decisions) shows no disagreement.
- The `split` rows are decided in the runner glue (DESIGN layer 5 pairwise test) and are tested only. The Spec's
  `split`/`scotus_resolves_split` back the `conflict` rows.

## Assumed

- **The doctrine tables:** `courts2`, `succession`, `adoption` and `system_rules`, with their S/L/U tags.
  - Theorems never assume a row.
  - Verdicts carry `firm = 1` when the S/L-only tables agree with the tables including U rows.
- **The readers:** holdings text, issue keys, answers and Marks rows (held back by certificates for treatments and
  history; holdings only partly).
- The departures listed in `DEVIATIONS.md`.
- **The Lean compiler,** for compiled runs (`runner/`, lean_exe `caselaw2`) and `#guard`.
- **Windows Application Control** blocks the locally built `caselaw2.exe` (since 12 Nov), so every run since then
  is interpreted: `run_lean.sh` falls back to `lake env lean --run`, and generated differential testing uses
  `runner/RunBatch.lean` (the built `Run` module, imported once per batch) through `ref/drt.py`. On 12 Nov at 19:32
  the policy also began blocking the toolchain's `lean.exe` (unsigned), which stops every build and run until it is
  allowed again.

## Line counts (lean-proofs `LegalProofs/CaseLaw2/`)

| Layer | Files | Lines |
|---|---|---|
| Trusted Spec + types | Basic, Courts, Holdings, Events, Spec/RuleId, Spec/Authority, Spec/Status, Spec/Splits, Spec/Findings, Spec/Horty, Spec/Lines | 2,570 (incl. ~620 lines of proofs inside Status/Splits/Horty/Findings/Lines) |
| Trusted checker | Certificate, Sha1 | 345 + 586 |
| Statement lock | Registry (generated), Audit (generated) | 152 + 1,443 |
| Proofs | Spec/AuthorityThms | 288 |
| Exec (proved equal to Spec) | Exec/Index, Exec/Env, Exec/Verdicts | 229 |
| Tests and search predicates | Examples, Mutants, Hunt | 424 + 250 + 327 |
| Unverified glue | Run, Data, Tsv, Core, CaseLaw2.lean | ≈ 1,560 |
| Total | | 8,168 |

## What the hunt fixes add to each class (12 Nov, evening)

- **Proved:** a division of a court of last resort with a strong court-level rule cannot overrule the court
  (`division_cannot_overrule`); the division reading changes no force outside a court of last resort
  (`forceDiv_eq_force`); an overruling that does not reach an heir leaves the status in that heir's line unchanged,
  and an heir's overruling stays in its line (`adopted_status_per_heir`, `heir_overruling_stays_in_line`); with no
  line-limited effect, status does not depend on the court asking (`statusFor_all`); a superseded-holding finding
  needs a known conduct date and a holding-level match (`appliesSuperseded_needs_conduct`,
  `conductUnknown_not_finding`); a panel departure needs a known panel and a rule in force when it departed
  (`panelDeparts_needs_panel_and_rule`).
- **Tested only:** which lines an overruling reaches (`reachOf`) and which line a citing court is in (`inLine`) are
  definitions read against doctrine F10, checked by `#guard`s on the *Bonner* and *M.A.P.* cases and by the
  differential runs; they are not theorems about the law. Horty rows are findings over reader data (factors, family
  keys), checked against `tools/caselaw2/factors/horty_py.py`.
- **Assumed:** the two dated Ohio and Louisiana rule rows and the 1 September 1948 en banc date (tag L, from memory).

## What round 2 adds to each class (12 Nov, night; DEVIATIONS 73–79)

- **Proved** (`Spec/Lines.lean`, 23 theorems):
  - a court standing in one pure line reads exactly that line's status row (`lineStatus_heir_agrees`,
    `lineStatus_orig_agrees`); status in a line depends only on which effects reach the court (`statusFor_congr`);
  - an overruling that does not reach a line changes neither the holdings that count there nor the resolver's
    answer (`goodIn_ignores_unreaching`, `heldIn_ignores_unreaching`, `conflict_in_line_ignores_unreaching`);
  - the Horty base of a line holds a precedent iff it binds there and is good law in that line
    (`mem_lineBase_iff`);
  - with no line-limited effect all of these are the old union definitions, and a decision has no per-line rows
    (`lineStatus_all`, `linesOf_all`, `goodIn_all`, `heldIn_all`, `lineBase_all`);
  - the union status of `status.tsv` is at least as severe as any line's, what is good law in the union is good law
    in every line, and an inconsistent union base is inconsistent in every line (`statusFor_le_status`,
    `good_in_every_line`, `heldUnion_sub_heldIn`, `lineBase_consistent_union`).
- **What the proofs do not cover.** They speak of `statusFor`, `heldIn` and `lineBase` for a given view. Which
  lines an overruling reaches (`reachOf`) and which line a court is in (`inLine`) remain definitions read against
  doctrine F10. That the runner calls these functions with the right court, date and effects is glue.
- **Tested only:**
  - the runner's per-line rows, the per-line split test (each side in its own court's line; a holding binds the
    other court only if good law there; the resolver in both lines) and the examined courts of a Horty family are
    glue, checked by `#guard` replays (*Bonner*, *Salinas* / *Adamson*, *M.A.P.*, the Federal Circuit and the CCPA)
    and by the differential runs (DIFFTEST.md §9). The reference now computes per-line status rows, per-line
    splits and conflicts, and Horty binding bases independently, from DEVIATIONS 74–78 alone;
  - "the original court is gone" (an adopter then speaks for the original line) and decisions dated outside their
    court's epoch, which the dated epochs of `courts2.tsv` now make live on the real data.
- **Assumed:** the Alabama reading (DEVIATIONS 73). The Court of Criminal Appeals row rests on the 1969 opinion's
  words and the court's own later practice (tag S). No source was found for the Court of Civil Appeals; its row
  stays U.

## Round 5 addendum (13 Nov 2026)

- Proved: the 34 round-5 theorems (list in `round5/ROUND5.md` and the report). Certificate-checked: every recognised
  row (the later court's quote, both names in it, its power). Tested: Lean against the reference on 118 regression
  universes (0), 600 new universes (status 0; one old cause differs on verdicts) and the real data (2 rows).
- Assumed, new: the opinion-part map's "majority" label for the later court's sentence; the reader's judgment that a
  sentence states the overruling as fact; the scope it assigns. Measured by blind audit at 94-97% right.
- Not covered: the fuzzer does not yet generate `treatment_class.tsv`.

## Round 6 addendum (13 Nov 2026): anchored history rows

- **Proved** (8 theorems, `Certificate.lean`): an admitted anchored history row has (1) the anchor quote at its
  stated offset in a well-formed window of the **same text** as the row's certificate, whose SHA-1, recomputed by the
  checker, is the recorded one (required when `window_sha.tsv` is supplied); (2) an anchor cue and no anchor
  disqualifier; (3) the target evidence inside the anchor quote itself, and with `cite_index.tsv` the citation
  resolving through the index to the row's target; (4) an allowed anchor part; (5) the disposition quote passing every
  check of `check` except target resolution (hash, window, quote at offset, cue of the kind, no disqualifier, part,
  date order, authority). Both quotes are non-empty. A row without an anchor line gets `check`'s verdict
  (`checkHistory_no_anchor`; also shown byte-identical on the round-5 and round-4 data).
- **Not proved:** that the decision the anchor cites is the decision under review (rather than, say, a related
  decision cited in the same head matter), and that the disposition sentence is about that decision. Both quotes are in
  the acting court's text, but tying one to the other is the linker's rule (`round6/history/rules/*/RULES.md`),
  measured by the blind audit (`DESIGN6.md` §5), not a theorem. The cue lists are substring tests (data, not
  doctrine). The reference engine does not yet implement the anchored check.
