# Reader brief (stlink11 read2)

You read US court opinions and answer questions about two decisions per item. Work only from the opinion texts
(commands below). Do not open any other file in this folder or elsewhere except your pack `items_<k>.md` and the
texts printed by the commands. Do not use the web.

Working folder: `~\Documents\us-caselaw-lean-work\caselaw-lean-2` (Git Bash:
`cd ~/Documents/us-caselaw-lean-work/caselaw-lean-2`).

- Print an opinion's text: `python -X utf8 round6/history/r6lib.py text <node>` (add `<start> <end>` for a slice of
  characters). Texts can be long: write them to a file in your scratch space and search it (grep -n for party names,
  docket numbers, dates, "Court of Appeals", "Appellate Division", "reversed", "affirmed", ...). The text begins with
  a front-matter block (court, docket, decided, citations, parties, cites_cases) printed by the reporter.
- Print a node's facts: `python -X utf8 round6/history/r6lib.py row <node>`.

Each item names an opinion D of a state court of last resort and an earlier decision T of the same state's
intermediate appellate court (with T's reporter citations). For each item answer:

1. `same_case`: is T a decision in the same case (same litigation, same parties) as D? YES / NO / UNSURE.
2. `under_review`: is T the very decision that D reviews (the judgment brought up to D's court in this appeal /
   petition)? YES / EARLIER_ROUND (same case, an earlier decision, not the one now under review) / OTHER_RULING
   (same case or same parties, another ruling or another proceeding, e.g. a companion appeal, a separate suit between
   the same parties, a habeas proceeding) / NO (other case) / UNSURE.
3. `effect_on_T`: what D's own judgment does to T: REVERSED / VACATED / MODIFIED / PARTLY (reversed or vacated in
   part, affirmed in part) / AFFIRMED / NONE (D does not act on T) / UNSURE.
4. `ties`: which of these tie D to T, as printed in the texts (list all that hold): `docket` (a docket / case number
   of T printed in D), `citation` (T's reporter citation printed in D, anywhere incl. the front matter `cites_cases`),
   `date` (T's decision date printed in D), `full_names` (the given name + surname of the individual parties, or the
   whole organisation name, are the same in both), `facts` (same underlying facts / trial / charge), `court_named`
   (D speaks of the intermediate court's decision in this case).
5. `evidence`: one short verbatim quote from D (max ~250 characters) that best shows the relation (or its absence).
6. `why`: one or two short phrases (e.g. "same surname, different defendant", "earlier appeal in same case",
   "D reviews the Court of Appeals' decision on the same conviction").

Write your answers as JSON lines, one object per item, to
`round11/agents/stlink11/read2/answers_<k>.jsonl` (k = your pack number), keys: `item`, `same_case`,
`under_review`, `effect_on_T`, `ties`, `evidence`, `why`, `note`. Write the file with your file-writing tool, UTF-8.
Finish every item; when unsure, say UNSURE and why in `note`.
