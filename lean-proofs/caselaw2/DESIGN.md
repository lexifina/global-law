# caselaw-lean-2: the most ambitious version (draft, to be refined by research/)

v1 formalised the mechanical shell of precedent: court hierarchy and whole-decision overruling validity (56 declarations).
v2 formalises what courts actually do with precedent, at the level of holdings, with every verdict carrying a checkable
certificate, joined to the statute record, and evaluated against courts' own statements.

## Layers (Lean namespace `CaseLaw2`, lean-proofs/LegalProofs/CaseLaw2/)

1. **Authority** (`Authority.lean`): courts as nodes with system, tier, circuit/district/division, panel vs en banc,
   publication status, successor/predecessor relations with dates, dual high courts; a typed `Authority` relation
   (binding / persuasive / none) computed per (citing court, cited decision, date) from rules with sources
   (doctrine.md). Theorems: SCOTUS binds all on federal law; Erie (federal courts bound by state high court on state
   law); prior-panel rule (panel cannot overrule panel; en banc can); successor inheritance; no cross-system overruling;
   unpublished never binds; vacated never binds; plurality → Marks narrowest ground.
2. **Holdings** (`Holdings.lean`): a decision = list of holdings {issue, proposition, basis: statute/constitution/
   common law, statute cites (title, section, subsection), disposition}; opinion parts (majority/plurality/concurrence/
   dissent) — only majority/plurality holdings carry authority.
3. **Treatment** (`Treatment.lean`): typed edges between holdings (or whole decisions): overrules, overrules-in-part
   (scope = set of holdings or an issue), abrogates, receded-from, disapproves, limits, questions, distinguishes,
   follows; subsequent history (reversed/vacated/affirmed) of the same case; abrogation by statute (from StatuteText /
   Overrides: law + effective date + cited block rewritten). Status of a holding on a date = fold over valid events;
   theorems: monotonicity, partial overruling leaves other holdings, statute abrogation is prospective (conduct before
   effective date keeps the old rule), reversal on the same case vs overruling distinction, idempotence/order
   independence of same-day events.
4. **Certificates** (`Certificate.lean`): every treatment the reader asserts carries the quoted words, their offsets and
   the SHA of the decision text; Lean checks (string-level, decidable): the quote occurs at the offsets (hash supplied
   for audit), it contains a treatment verb of the asserted kind, it names the target (case name tokens or a citation
   that resolves to the target), and it is in the majority/plurality part. A treatment without a passing certificate
   is not admitted. So part of the reader moves inside the proof.
5. **Status & splits** (`Status.lean`, `Splits.lean`): good-law status per holding per date per court (binding vs
   persuasive vs overruled); circuit splits on a statutory question = two holdings, by courts neither of which binds
   the other, on the same (section, question) with opposite answers, both good law on the date; theorem: a later
   binding SCOTUS holding on the question resolves the split for all lower courts.
6. **Runner** (`Run.lean`): sharded, as v1.

## Data / reader (tools/caselaw2/)
- court table v2 (districts, divisions, successors, en banc/panel per decision, publication status)
- treatment extraction: regex candidates over full text → LLM reader (Azure gpt-5.4-mini US, gpt-6-sol for hard) emitting
  typed treatments + quote spans; certificate builder.
- holdings extraction: Supreme Court + every decision that is a treatment target/source + statutory decisions in the
  overrides set; questions normalised per US Code subsection for split detection.
- statute abrogation join: overrides/confirmed + StatuteText rewrite events.

## Evaluation (held back from the reader)
- later courts' notes ("overruled in part by", "abrogated by", "superseded by statute as stated in") as v1 did;
- SCDB precedentAlteration / CRS table; published lists of overrides (Christiansen–Eskridge, Hasen);
- blind audits of each layer; frozen-reader holdout; certificate failure analysis.

## Output
- work: ~/Documents/us-caselaw-lean-work/caselaw-lean-2/
- report: ~/Documents/html-reports/caselaw-lean-2.html

## Build (launched 2026-11-12)
Research done: research/{doctrine,prior_art,data_audit}.md. Contract: SCHEMA.md. Six parallel agents:
- lean (LegalProofs/CaseLaw2/*, LEAN.md, run_lean.sh) · courts (data/courts2, decisions2, system_rules…, COURTS.md)
- reader (data/treatments, history, cert_text, READER.md; never reads later-court notes) · holdings (issues, holdings,
  marks, splits; HOLDINGS.md) · statutes (lawchanges, supersessions; STATUTES.md) · eval (gold/, eval/score.py)
Then: Lean full run → eval → ~/Documents/html-reports/caselaw-lean-2.html.

---
# REVISED DESIGN (2026-11-12, after research/formalisms_{python,google,industrial}.md) — this supersedes the layer list above where they differ

Sources: AlphaProof Code (comparator, locked statements, trust inventory, spec-deviation log), the broyojo Python
formalization (registry + Audit.lean, refute-don't-weaken, mutation "would a broken version pass?", differential runs vs
the real system), AWS Cedar (small readable spec, DRT vs implementation, generic lemmas), seL4/CompCert (layered
refinement, prose assumption list), Catala (default calculus: exceptions, conflicts as errors → for us, as findings),
verified-checker pattern (untrusted solver + small checker), OpenFisca (no silent defaults).

## D1. Three layers, one trust boundary
1. **Spec** (`CaseLaw2/Spec/*`): short, readable, propositional definitions of precedent — force, canChangeStatus,
   goodLaw (two-date), split — written as Catala-style *labelled default trees* (each rule a default with named
   exceptions: Erie, Marks, adoption, unpublished, en banc, succession…), parameterised by an abstract `Rules` structure.
   Every rule carries the doctrine.md id it implements. Target: a lawyer can read it next to doctrine.md.
2. **Exec** (`CaseLaw2/Exec/*`): decidable, efficient functions over Array/HashMap with **proved equivalence**
   (`exec_force_eq_spec`, `exec_status_eq_spec`, `checkCert_sound`, …). Generic lemmas proved once: status is a fold over
   events; same-day events on distinct holdings commute; partial events touch only their holdings; revival.
3. **Untrusted** (Python + LLM readers, data tables): may be wrong; nothing it produces is believed unless an Exec
   checker admits it with a certificate. Ship certificates as files anyone can re-check.

## D2. Statement lock (comparator-style)
- `CaseLaw2/Registry.lean`: every public theorem by name with its *statement*; `tools/caselaw2/audit/audit.py` (or
  Lean `#guard_msgs`-based Audit.lean) checks each registered theorem's type is exactly the locked statement and its
  axioms ⊆ {propext, Classical.choice, Quot.sound}. No `sorry`, `axiom`, `native_decide` in theorems. Statement changes
  go through a logged change request (`STATEMENTS.log`): weakening = escalate as probable data/spec bug; a false
  property is *refuted* (counterexample kept as a #guard), never silently weakened.
- Doctrine as **hypotheses/parameters**, never axioms; U-tagged rows never premises (two Rules instances: `firm` S/L only,
  `all` incl. U; output rows carry firm=1 when both agree).

## D3. Falsifiability (mutation + replay)
- ~15 deliberately broken variants of force/status/checkCert (e.g. Erie both ways, panel overrules panel, ignore
  unpublished, ignore partial scope, statute supersession retroactive, revival ignored, cert accepts dissents) — each
  registered theorem/property must FAIL on ≥1 mutant (checked by #guard counterexamples on small instances); each rule
  must have ≥1 real decision that exercises it; known episodes replay (Betts/Gideon, Bowers/Lawrence, Kentucky 1976,
  Bonner, South Corp, Ledbetter, a California CoA conflict, a partial overruling).

## D4. Differential testing
- An independent Python reference implementation of force/status (written from doctrine.md by a different agent, not
  from the Lean) run on all real data + generated inputs; every disagreement triaged (Lean spec, Python ref, data).
- External oracles scored separately: later courts' typed notes, SCDB precedentAlteration, CRS table, Congress
  override lists, SCOTUS split resolutions. Every disagreement with an oracle is OUR error until triaged into: reader
  wrong / checker too strict / oracle wrong / genuinely contested.

## D5. No silent defaults
- Unknown = `Option`/explicit `unknown` constructors in Lean (TSV 0 parses to none). Three-valued status outputs:
  negative-treatment-admitted / none-admitted / unknown(reason).

## D6. Spec-deviation log + trust inventory
- `DEVIATIONS.md`: every place the Lean rules differ from doctrine.md (simplifications, U rows, unmodelled states).
- `TRUST.md` (seL4-style prose list): what is proved (kernel), proved-by-computation, certificate-checked (compiled
  checker, trusts the Lean compiler), tested (differential/oracle), assumed (doctrine tables, reader for holdings text),
  with trusted line counts (Spec + statement registry) vs untrusted.

## D7. Coverage reported honestly
- Pinned corpus manifest (all 6.9M nodes, repo commits); per layer: accepted / written / not started; per-court and
  per-decade coverage; which method produced each finding (rule, reader, oracle).

## D8. Explanations
- Every verdict row carries a justification tree id (rule path through the default tree + certificate ids), rendered
  s(CASP)-style in the report for samples.

## D9. Build/run
- Approved: separate Lake package `caselaw-lean-2/runner/` requiring lean-proofs by path, compiled `lean_exe` (state in
  TRUST.md that checks run compiled). No Mathlib (Lean 4.35, no Finset): lists with decidable membership; Nat keys
  interned by the runner; string checks only in certificate checkers with structural soundness proofs.
- Approved SCHEMA additions: optional `factors.tsv` (holding_id, factor, side, inReason) for Horty reasons;
  system rules for CA review-granted force; Tax Court appeal venue (Golsen) and Texas TRAP 41.3 transfer source as
  per-decision optional columns `appeal_venue`, `transfer_from` in an optional `decisions2_extra.tsv`.
