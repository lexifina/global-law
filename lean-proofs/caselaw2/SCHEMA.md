# caselaw-lean-2 interchange schema (contract between the data agents and the Lean runner)

All files: UTF-8, LF, tab-separated, no header line unless stated; dates yyyymmdd as integers (0 = unknown); decision ids
are v1 node ids from ~/Documents/us-caselaw-lean-work/graph/nodes.tsv; court ids extend lean-in-v3/courts.tsv (keep v1 ids,
append new ids ≥ 10000). Root: ~/Documents/us-caselaw-lean-work/caselaw-lean-2/data/. Every row that asserts a legal fact
carries `src` (where it came from: rule id, file, or reader id) and, for doctrine-derived rows, `tag` S|L|U
(research/doctrine.md: S checked, L leading case from memory, U uncertain). Rows tagged U are data, never premises of a
theorem.

## Courts and decisions (agent: courts)
- `courts2.tsv`: court_id, epoch_from, epoch_to, name, system (0 federal, else v1 state index), tier
  (L last|A appellate|B bap|T trial|S special|D appellate-division-of-trial), last_resort_for (all|civil|criminal|-),
  circuit (federal 1–13, 0 else), unit (district/division/department id within an intermediate system, 0 none), src, tag.
  One row per court epoch (a court whose name/role changed has several rows).
- `succession.tsv`: old_court, new_court, date, kind (rename|replace|split|absorb), src, tag.
- `adoption.tsv`: adopter_court, source_court, up_to_date, filter (all|unitB|…), force, src, tag.
- `system_rules.tsv`: system, rule, value, from, to, src, tag. rule ∈ horizontal (strong|soft|none|withinUnitOnly),
  trialScope (statewide|statewideChooseOnConflict|ownUnitThenAny|ownUnitOnly), unpubForce (Force), stateFollowsCircuit
  (Force), firstInTimeControls (0/1), circulationCountsAsEnBanc (0/1), enBancGrantVacatesPanel (0/1). court-level rules
  use `system` = -court_id.
- `decisions2.tsv`: node, court_id, date, unit, bench (panel|division|enBanc|limitedEnBanc|circulated|conflictPanel|
  wholeCourt|unknown), publication (published|unpublished|table|summaryOrder|memorandum|unknown), form (full|perCuriam|
  summaryAffirmance|equallyDivided|certifiedAnswer|plurality|memorandum|unknown), text_sha (sha1 of the decision file
  bytes at HEAD), src. Every node of graph/nodes.tsv appears exactly once.

## Same-case history and treatments (agent: reader)
- `history.tsv`: id, target_node, by_node (-1 unknown), date, kind (affirmed|reversed|vacated|modified|remanded|certDenied|
  reviewGranted|reviewDismissed|depublished|withdrawn|substitutedBy|rehearingEnBancGranted|reinstated|writRefused|other),
  scope (all|issues:k1,k2|unknown), CERT, src.
- `treatments.tsv`: id, by_node, target_node, date (of by_node), kind (overruled|disapproved|recededFrom|abrogated|
  supersededByEnactment|limited|questioned|criticized|distinguished|followed|declinedToFollow), scope (all|issues:k1,k2|
  partialUnknown|otherGrounds), temporal (retroactive|prospectiveFrom:yyyymmdd|pureProspective|unknown), explicit (1 the
  by-decision states it itself; 0 inferred), CERT, reader (regex-v2|<model id>), confidence (0–1).
- `treatment_witness.tsv` (optional; round 4): treatment_id, witness_node (W), by_evidence (`cite:`|`name:` naming the
  by-decision Y in W's text), src. A treatments row listed here is an implicit overruling stated by the later decision
  W: its by_node is Y, explicit is 0, and its CERT (hash, offsets, quote, window) is W's. Checks and effect:
  `round3/implicit_schema.md`, DEVIATIONS 83. It never changes a status; it yields `atRisk X Y inferredRejection`.
- CERT = 6 columns: text_sha, start, end (character offsets into the decision file text as read from git HEAD, UTF-8
  decoded, \r\n normalised to \n), quote (the exact substring, tabs/newlines replaced by spaces — Lean re-checks it with the
  same normalisation), target_evidence (cite:<normalised citation>|name:<tokens>), part (majority|plurality|perCuriam|
  concurrence|dissent|unknown).
- `texts/` is NOT shipped to Lean in full; for every certificate the reader writes `cert_text.tsv`: text_sha, start0, end0,
  window (the text from start-400 to end+400, normalised), so Lean can check quote ⊆ window at the right offset and that
  the window hashes are consistent with the audit copy.
- Held-out: the reader never reads events_v3/reports.tsv or any "overruled by"/"abrogated by" note written by a LATER
  court about the target. Those are the evaluation's gold.

## Holdings, issues, splits (agent: holdings)
- `issues.tsv`: issue_key, label, domain (federalGeneral|federalPatent|federalTax|stateLaw:<system>|unknown), usc
  (title:section(sub) or -), question (one yes/no question for split detection or -), src.
- `holdings.tsv`: holding_id, node, issue_key, proposition (≤ 300 chars), answer (yes|no|- for split questions), role
  (majority|plurality|perCuriam), CERT (the sentence stating it), reader, confidence.
- `marks.tsv`: node, issue_key, narrowest_opinion_author, proposition, src, tag.

## Law changes (agent: statutes)
- `lawchanges.tsv`: id, law (Pub. L. …), usc_block (title:section(sub)), enacted, effective, retroactive_to (0 none; 1 = applies to cases pending on the effective date whatever the conduct date, no earlier bound stated; else a yyyymmdd date), src.
- `supersessions.tsv`: id, target_node, issue_key (or -), lawchange_id, evidence (lawNamesDecision|reportNamesDecision|
  quotedWordsStruck|laterCourtSays:<treatment id>), score, explicit (1 only if a law/report/court states it), src.

## Gold (agent: eval; never read by reader/holdings)
- `gold/*.tsv` with their own README.

## Lean output (runner)
- `out/status.tsv`, `out/findings.tsv`, `out/certs.tsv` (cert id, ok/failure reason), `out/splits.tsv` — see Lean
  module docs.
