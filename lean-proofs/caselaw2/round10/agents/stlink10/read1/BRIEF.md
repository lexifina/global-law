# Reader brief (stlink10 read1)

You read US court opinions and answer questions about two decisions per item. Work only from the opinion texts
(commands below). Do not open any other file in this folder or elsewhere except your pack `items_<k>.md` and the
texts printed by the commands. Do not use the web.

Working folder: `~\Documents\us-caselaw-lean-work\caselaw-lean-2` (Git Bash:
`cd ~/Documents/us-caselaw-lean-work/caselaw-lean-2`).

- Print an opinion's text: `python -X utf8 round6/history/r6lib.py text <node>` (add `<start> <end>` for a slice of
  characters). Texts can be long: pipe to a file in your scratch space and search it (grep -n for the other decision's
  reporter citation, party names, "Court of Appeals", "Appellate Division", "reversed", "affirmed", ...).
- Print a node's facts: `python -X utf8 round6/history/r6lib.py row <node>`.

Each item names an opinion D of a state court of last resort and an earlier decision T of the same state's
intermediate appellate court (with T's reporter citations). For each item answer:

1. `same_case`: is T a decision in the same case (same litigation) as D? YES / NO / UNSURE.
2. `under_review`: is T the very decision that D reviews (the judgment brought up to D's court in this appeal /
   petition)? YES / EARLIER_ROUND (same case, but an earlier decision, not the one now under review) /
   LATER_OR_OTHER (same case but another ruling, e.g. a companion appeal) / NO (other case) / UNSURE.
3. `ref`: how D's text refers to T: CITED (D prints one of T's citations) / NAMED_ONLY (D speaks of the intermediate
   court's decision without printing T's citation) / NONE. Give `ref_quote`: the sentence where D first refers to T
   (max ~300 characters, verbatim).
4. `disp`: D's own judgment line, verbatim (max ~300 characters; the majority / per curiam's final disposition).
5. `effect_on_T`: what D's own judgment does to T: REVERSED / VACATED / MODIFIED / PARTLY (reversed or vacated in
   part, affirmed in part) / AFFIRMED / NONE (D acts only on another decision, e.g. only the trial court's judgment,
   and says nothing of T) / UNSURE. When D's line acts on the trial court's judgment, say in `trial_note` what T had
   done to that trial judgment (affirmed / reversed / ...) and whether D's judgment therefore in effect undoes T
   (`in_effect_undoes_T`: YES / NO / UNSURE).
6. `distance`: roughly how many characters separate D's sentence naming the intermediate court ("the Court of
   Appeals", "the Appellate Division", ...) from T's citation (0 if in the same sentence; NONE if not named).
7. `why_hard`: one or two short phrases on what would make it hard for a pattern-based program to tie T to D's
   judgment (e.g. "citation far from the court name", "citation only in head matter", "several earlier rounds of the
   case cited", "judgment line names the trial court", "T cited only as authority", "remand / earlier-proceeding
   words near the citation", "caption differs", "T not cited").

Write your answers as JSON lines, one object per item, to `round10/agents/stlink10/read1/answers_<k>.jsonl`
(k = your pack number), with keys: `item`, `same_case`, `under_review`, `ref`, `ref_quote`, `disp`, `effect_on_T`,
`trial_note`, `in_effect_undoes_T`, `distance`, `why_hard`, `note`. Write the file with your file-writing tool,
UTF-8. Finish every item; when unsure, say UNSURE and why in `note`.
