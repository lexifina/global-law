# Agent `stlink10` (round 10): state-court review linker — the FJC linker's analogue for state courts of last resort (move 2)

Read `round10/DESIGN10.md` (§0 — note rule 3: `benchmarks/brace_hall_state/` and `benchmarks/songer_treat/` are
CLOSED to you: never open, list or grep them, not even their docs) and `round10/agents/COMMON.md`. Folder
`round10/agents/stlink10/` (NOTES.md). Audit letter `t`.

## The relation
A state court of last resort (state supreme court; Texas/Oklahoma also their courts of criminal appeals; New York
Court of Appeals; Maryland Court of Appeals; …) reviews a decision of its state's intermediate appellate court (Court
of Appeals, Appellate Division, Appellate Court, Superior Court, Court of Civil/Criminal Appeals, Commonwealth Court,
District Court of Appeal, …) — or sometimes a trial court — and reverses, vacates, modifies, or affirms it. When it
reverses/vacates, the decision below should carry a `neg:*` history status (path `history`) at the as-of date; when
it affirms, nothing negative. Corpus: `graph/nodes.tsv` (node, repo, path, court, date, citations, name); state repos
`<slug>` (court of last resort), `<slug>-appellate` (intermediate), `<slug>-other-courts`. The round-6 history readers
(`round6/history/`, `data/READER.md`) emit a history row when the reviewing opinion's own judgment line disposes of a
decision it cites. How many state reversals of an intermediate decision present in the corpus go unmarked, and why,
you measure yourself on the corpus (below), never on any key.

The federal analogue is the FJC linker (CoA reviewing a district decision): `round8/agents/fjc8/` (NOTES.md,
`fjc_link.py`, `guard8.py`, `gfeat8.py`, `diag.py`, `funnel.py`) and `round9/agents/fjc9/` (NOTES.md, `fjc9_link.py`
with rules F1, W (anchor widened to the court named up to 4,000 chars back in the same part, audited 0.900) and J
(judge-form anchors "district/magistrate/trial judge" under claim `anchorWide`, 0.900), `certify9j.py`; G/G2 guard
exceptions NOT installed (0.81/0.84: the wrong ruling under review, partial scope, affirmed)). The Lean's anchor list
already holds the state court names ("court of appeals", "appellate division", "appellate court", "superior court",
"court of civil appeals", "court of criminal appeals", "commonwealth court", "trial court", "court below", …;
`anchor_wide` adds "case below", "judicial court", "court of errors"; cue table
`global-law-lean/lean-proofs/tools/caselaw2/cues/cue_table.json`).

## Do
1. **Corpus-intrinsic diagnosis (no key).** Build the population: state court-of-last-resort opinions in the corpus
   whose own judgment line (majority / per curiam zone) reverses / vacates / modifies the decision of the state's
   intermediate court (or "the court below", "the Court of Appeals", "the Appellate Division" …), and that cite or
   caption-match a decision of that state's `-appellate` repo dated before them (5-year window, same party tokens).
   Measure in v9c (`round9/out/v9c/status.tsv`, `certs.tsv`, `round9/stage/v9c/history.tsv`) what share of the
   candidate decisions below have a history row from that reviewing opinion. Read a stratified sample (~60 pairs:
   state × decade × cited/uncited × marked/unmarked) with opus readers (corpus text only) to learn why the unmarked
   ones are missed (no citation of the decision below in the history zone; judgment line names the court not the
   case; "the decision of the Court of Appeals is reversed" far from the citation; caption-only links; several
   earlier rounds of the same case; review of the trial court with the intermediate decision in between; …) and how
   often a reversal of the TRIAL court's judgment by the supreme court is really a reversal of the intermediate
   affirmance (and vice versa). You may also use the dev scorers (Shepardized dev, holdout history notes) and the h0
   per-case files of the four round-8 keys to check precision effects.
2. **Rules** (general, corpus-wide over all state court-of-last-resort opinions): port F1 / W / J to state courts —
   anchor = the intermediate court as named in the opinion (the list above, state-specific court names), the
   decision below identified by citation in the opinion or by caption + date + docket against the state's
   `-appellate` repo, the judgment line of the acting opinion as disposition, the round-6 earlier/later/
   interlocutory guards, and a test of WHICH ruling is under review (the latest decision below in the same case
   before the opinion; the intermediate court vs the trial court; a citation-level test — what the FJC G rule lacked).
   Effects: reversed/vacated → neg history rows of the right scope (`unknown`/partial when "affirmed in part",
   "in all other respects", "modified"); affirmed → no row. Keep rows checkable by the round-9 Lean (anchor /
   anchorWide claims, the anchor-quote rules); anything else → `LEAN_REQUEST.md`.
3. Certify (`round10/certify10.py` once INFRA_READY), stage, run (NOBUILD), score (`noold`): precision on h0 keys,
   Shepardized dev precision and CLEAN, holdout history must not drop.
4. Blind audit each status-changing class (≥ 80, two opus auditors, decoys; item type B: same case? did the acting
   court itself dispose of the target? how? whole?). Install at ≥ ~90%; report link-only and link+effect.
5. Report also what you could not link and why (decision below not in corpus, caption ambiguous, several rounds), as
   a share of the step-1 population — the lead uses it as the headroom estimate.
Report: population and miss anatomy (counts), rules, rows per class, audits with intervals, delta folders, effect.
Time box ~100 minutes; report what is ready.
