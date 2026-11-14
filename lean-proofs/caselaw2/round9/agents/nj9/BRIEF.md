# Agent `nj9` (round 9): New Jersey successor-court authority (move 6)

Read `round9/DESIGN9.md` §0 and `round9/agents/COMMON.md`. Folder `round9/agents/nj9/` (NOTES.md). You do NOT edit
the Lean tree or the Python reference; you settle the legal rule and write it down for the lead.

## Background
Since round 5 the one Lean/reference difference class: rows where a New Jersey court acts on a decision of a
predecessor court of the pre-1948 system. Examples (real v8e): treatments witness rows
`tw:3991335:4086271:4616:4089451`, `tw:4018149:4006682:13821:4061823`, and ownact operative row
`t8:4058244:4016514:17127` (acting court 1099, NJ Superior Court Appellate Division, 1962, on target 4016514 of
court 1095, the old NJ Supreme Court, 1948). The Lean's `canChangeStatus` gives a successor the power only between
courts of last resort (refuses: `noAuthority`); the reference admits through the `succession.tsv` line 1095 → 1099
tagged `U`. Read `round8/agents/ref8/NOTES.md` (end), `round5/ROUND5.md` (successor courts), the data tables
`round8/stage/v8e/succession.tsv`, `courts2.tsv`, `court_alias.tsv` (New Jersey lines), and the authority rules in the
Lean (`global-law-lean/lean-proofs/LegalProofs/CaseLaw2/` — read only; grep `canChangeStatus`, `succession`) and in
the reference (`tools/caselaw2/ref/precedent_ref.py`, read only).

## Do
1. Research the actual rule from primary sources (web; at most 20 searches; fetch pages directly): the 1844 and 1947
   New Jersey Constitutions (1947 Art. VI on the judicial article; Art. XI §IV transition: which old courts' powers,
   jurisdiction, pending cases and decisions passed to which new courts — Court of Errors and Appeals → Supreme Court;
   old Supreme Court, Chancery, Prerogative Court, circuit courts → Superior Court and its Appellate Division / Law /
   Chancery Divisions), and NJ decisions stating whether the Appellate Division (or Law/Chancery Division) is bound by,
   or may depart from, decisions of the former Supreme Court / Court of Errors and Appeals / Court of Chancery; whether
   the new Supreme Court treats the old Court of Errors and Appeals' decisions as its own precedents (it may overrule
   them) and the old Supreme Court's decisions as those of an inferior court. Quote the operative text with URLs.
2. List every New Jersey row of the v8e build that the rule decides (treatments and history whose acting court is a
   post-1947 NJ court and target court a pre-1948 NJ court, and the reverse), with current Lean verdict and
   reference verdict, and say what the researched rule gives for each (by court pair, not by case).
3. Write `round9/agents/nj9/RULE.md`: the rule as a table (acting court → target court → may change status? which
   effect, horizontal vs vertical) with the sources, and a `LEAN_REQUEST.md` (the check, which tables, the theorem
   to state, e.g. `njSuccessor_sound`, and the mutant) plus what the reference must change (if anything), so both
   implementations give the same answer and the differential becomes clean. Prefer a general rule stated over the
   `succession.tsv` tag semantics (what "U" should mean) over a New Jersey special case, if the sources support it.
Report: the rule with quotes and URLs, the affected rows by court pair, the request.
