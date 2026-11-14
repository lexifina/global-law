# Agent `enbanc12` (round 12): an en banc court vacating / superseding its own panel's opinion (move 2)

Read `round12/DESIGN12.md` (§0 — rule 3: `benchmarks/bhk_enbanc/` (and `songer_treat/`, `brace_hall_state/`,
`fedcir_dataset/`) is CLOSED to you: never open, list, glob or grep it, not even its docs; you diagnose on corpus
text and the dev / h0 keys only) and `round12/agents/COMMON.md`. Folder `round12/agents/enbanc12/` (NOTES.md, a line
every 10 minutes). Audit letter `e`. You may read `benchmarks/scdb_disposition/` and `benchmarks/shadow_docket/`
SOURCE.md / MAPPING.md / DISAGREEMENTS.md and their h0 per-case files under `round11/results/v11d/bench/` — for side
effects only.

## The relation
A court of appeals (or any court that sits en banc / in banc, state courts included) grants rehearing en banc of a
panel decision P. In most circuits the grant itself vacates P (by the order's words, or the en banc decision says so:
"We granted rehearing en banc and vacated the panel opinion, 512 F.3d 1000"; "the panel opinion is vacated"; "On
rehearing en banc … the judgment of the panel is vacated"). The en banc court is the acting court; P should carry a
negative history status (vacated / superseded) at the as-of date when the corpus holds the acting text. When the en
banc court **reinstates** the panel opinion, or the panel's judgment survives, nothing negative (or the right kind).

## What exists (read first)
- Round 11 `scdb11` (`round11/agents/scdb11/`: NOTES.md 05:26–05:51, `r2scan11.py`, `cert_r2`, `cert_r2v3`, `work/`):
  R2 = en banc decision's own statement / subsequent-history note naming the panel → row on the panel. Scan: 12,139
  en banc decisions, 1,252 evidence citations, ~228 rows. Audits: R2 v2 r11b03 41/80 = 0.512 (36 of 39 errors: the
  cited target was the ORDER granting rehearing en banc, not the panel opinion); R2 v3 r11b04 44/49 = 0.898 (errors:
  en banc reinstated / affirmed parts of the panel, 4 kind; 1 scope; 1 link). **R2 v3 is a pending user decision: do
  not stage or install `cert_r2v3`.** You may build a new, better-founded class; it is installed only on its own fresh
  ≥ 80-item audit that excludes r11b03 and r11b04 samples (`make_packs12 --exclude round11/audit/r11b03/sample.tsv
  --exclude round11/audit/r11b04/sample.tsv`), and you report its overlap with cert_r2v3 (pairs) so the lead can state
  it.
- Round 6's rehearing rule (`round6/history/`, rule c-reh / `rehearingEnBancGranted`) and how the Lean treats
  rehearing-en-banc and vacated rows (read `tools/caselaw2/` docs / `round7/DESIGN7.md` and v11d `certs.tsv` /
  `status.tsv` for existing en banc rows — read-only).

## Do
1. **Corpus diagnosis (no key).** Population: panel decisions P in the corpus later reheard en banc by the same court
   (en banc decision E of the same case: same docket, caption, cite of P in E; and / or a published order O granting
   rehearing en banc that is itself a corpus node). Measure in v11d what share of such P already carry a negative
   history status, and trace the unmarked ones: no acting text in the corpus? statement present but not parsed? the
   order O is a corpus node whose own words vacate P (then O is the acting node — a strong, direct class)? the row
   targets O instead of P? Count by circuit and decade. Read a stratified diagnosis sample (~40) with opus readers.
2. **Rules** (general, corpus-wide): candidates — (a) O → P: a corpus order granting rehearing en banc whose own text
   vacates the panel opinion / judgment (identity: same docket, or O cites P, or same caption + date order); (b) E → P:
   E's own statement that the panel opinion was vacated / superseded (scdb11's E2 statements, with the target forced
   to P and never to O: identify O by its text / short length / order form); (c) where the court's rule makes the grant
   vacate P and E says rehearing en banc was granted, only if E's own words say the panel opinion is vacated or
   superseded (no row from a circuit rule alone — evidence = the acting court's words). Kind: vacated (or the kind E
   states); E reinstating / adopting the panel → no negative row (and no row from E's affirmance of the district
   court). Use the existing history kinds and anchor cues the frozen Lean (s51) accepts; if a row needs a Lean change,
   write `LEAN_REQUEST.md` at once and continue with what certifies.
3. Certify (`certify12.py`), stage, run NOBUILD, `score12.sh noold` vs v11d: Shepardized dev precision / CLEAN,
   holdout notes history, SCDB h0 precision / clean must not drop. Blind corpus-wide audit per status-changing class
   (≥ 80, two opus auditors, decoys; exclusions as above); install bar 0.90 on "right" (exact kind + scope).
Report: population and miss anatomy (counts), rules, rows per class, audits with intervals, delta folders, overlap with
cert_r2v3, side effects vs v11d, headroom (what cannot be linked and why).
