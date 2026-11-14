# Agent `stlink11` (round 11): state review of UNCITED decisions below — identity by docket + full party names + date + court (move 1)

Read `round11/DESIGN11.md` (§0 — rule 3: `benchmarks/brace_hall_state/`, `songer_treat/`, `fedcir_dataset/` are
CLOSED to you: never open, list or grep them, not even their docs) and `round11/agents/COMMON.md`. Folder
`round11/agents/stlink11/` (NOTES.md, a line every 10 minutes). Audit letter `t`.

## Where round 10 left it (read `round10/agents/stlink10/NOTES.md`, BRIEF.md, and its scripts: `pop.py`,
`stlink.py`, `ulink.py`, `tbridge.py`, `cycle.sh`, `deltas.py`, `sample.py`, `read1/`, `work/pop/`)
- Installed: s1 (F1/W port, 1,014 rows, 0.925), g2 (guard words exempted, 1,648, 0.950), D (34, 1.000).
- **Rule U NOT installed** (r10t05: 59/80 = 0.738): uncited intermediate decision named only by court, linked by a
  unique distinctive same-caption decision of the state's `-appellate` repo 0..5 y before D with one shared name token
  per caption side. All 21 failures: another case of people sharing a surname, or another proceeding of the same
  party. Population: **9,459 opinions** of courts of last resort whose judgment line acts on the intermediate court
  and that cite no decision of it, with a unique cap-2 same-caption candidate (93 marked); read sample: ~half truly
  under review (`read1`: 7/14 under review, 5 reversed + 1 partly + 1 vacated).
- Not installed either: T4 (trial-judgment reversals via §6 trialBridge; 0.850 right) — leave it.

## Do
1. **Identity rule U2 (corpus-wide over every state court-of-last-resort opinion D):** the decision under review T
   is an uncited decision of the state's intermediate court, accepted only when ALL of: (a) court: T's court is the
   intermediate court D names as acting (incl. district/division numbers when D prints them); (b) date: T dated
   before D, within the window, and the LATEST decision of that court in the same case before D (no sibling decision
   of the same parties in between — siblings ⇒ no row); (c) **full party names**: every named side of T's caption
   matches D's caption with the given name + surname (people) or the whole organisation name (organisations;
   frequent litigants — the State, the Commonwealth, the People, cities, counties, agencies, insurers, banks, unions —
   do NOT count as a tie: they need the other side's full name), checked on both D's and T's own text, not only the
   graph titles; and (d) a **second independent tie**: a docket number of T printed in D (head matter or opinion:
   "No. A-1234", "Court of Appeals No. …"; compact token ≥ 4 chars incl. a digit, found in T's own text) or the date
   of T's decision printed in D, or T's reporter citation in D's head matter (a citation the round-6 readers ignored
   because it sits outside the history zone). Measure each tie's yield and its agreement with the others on the
   corpus before choosing; write which combination you use and why in NOTES.md.
   The anchor quote / judgment line follow round 10's U / s1 machinery (D's majority sentence naming T's court acting;
   negative judgment line; round-6 guards), so rows stay checkable by the round-10 Lean (anchor / anchorWide claims).
   If a docket / date tie should be **checked** rather than audited, write `LEAN_REQUEST.md` (an optional table of
   identity spans like DESIGN10 §4's remandDocket: a D span and a T span holding the same compact docket token) —
   the lead decides; do not wait for it.
2. Read a stratified diagnosis sample first (~40 U-population pairs by state × decade × tie form) with opus readers
   (corpus text only) to learn which ties separate same-case from same-surname pairs; then fix the rule; then certify
   (`round11/certify11.py`), stage, run (NOBUILD), score (`noold`): Shepardized dev precision / CLEAN, holdout
   history and the h0 keys must not drop.
3. **Blind corpus-wide audit** (≥ 80, stratified, decoys, two opus auditors; item type B: same case? did the acting
   court itself dispose of the target? exact kind? whole?). The sample is drawn from the whole certified class and
   must exclude r10t05's items. Install bar ~0.90 on "right". If a cut is designed on an audit's errors, re-audit on a
   fresh sample (D9-11).
4. If time remains: the cited misses round 10 left (v9c: 10,824 unmarked cited pairs; s1+g2+D took ~2,700; left:
   no_court_phrase, earlier_proceeding, named_other_case, later_events) — one more general rule, same protocol.
Report: population (by state / era), how many U2 links per tie form, audits with intervals, delta folders, the h0/dev
effect vs v10d, and the headroom left (how many of the 9,459 remain unlinked and why).
