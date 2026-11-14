# Reader brief (fedcir12 read1)

You read court decisions from a local corpus and answer from the texts only. Do not use the web or any file other
than the decision texts printed by the command below (and your items file).

Each line of your items file (`items_<k>.tsv` in this folder) gives an acting decision (an opinion of the Federal
Circuit / its predecessor) by node id and caption, and one or more candidate target decisions (decisions of a lower
tribunal: a district court, the Claims Court / Court of Federal Claims, the Court of International Trade, the
Veterans Court), each as `node|date (yyyymmdd)|caption`, separated by ` ;; `.

Print a decision's text (Git Bash, from `~/Documents/us-caselaw-lean-work/caselaw-lean-2`):

    python -X utf8 round6/history/r6lib.py text <node>                 (whole text; the front matter gives court, date,
                                                                        docket, citations)
    python -X utf8 round6/history/r6lib.py text <node> <start> <end>   (a slice, by character offsets)

Read the acting decision (its head matter, especially an "Appeal from the United States District Court for ... in
No. ..., Judge ..." line; the opening paragraph saying what is appealed; the judgment line at the end) and enough of
each candidate (front matter: court, date, docket, judge; opening; ending) to answer, for EACH candidate of an item:

1. `rel`: what is this candidate to the acting decision?
   - `UNDER_REVIEW`: the acting court reviews this very decision in this appeal (the judgment / ruling appealed from,
     or a ruling merged into the final judgment that the appeal reviews and the acting court rules on);
   - `EARLIER`: an earlier ruling of the same case that this appeal does not review (reviewed in an earlier appeal,
     an earlier remand order, a ruling not before the court);
   - `LATER_OR_OTHER_RULING`: another ruling of the same litigation that this appeal does not review;
   - `OTHER_CASE`: a different case;
   - `UNSURE`.
2. `act` (only when UNDER_REVIEW): what the acting court itself did to it: `REVERSED`, `VACATED`, `MODIFIED`,
   `AFFIRMED`, `PART` (affirmed in part and reversed / vacated in part, or the acting court disturbed only part of it),
   `DISMISSED` (appeal dismissed), `OTHER`.
3. `how`: how the acting text ties it to this appeal: `CITE` (cites it), `HEAD` (the head-matter appeal-from line
   gives its docket / judge / date and it matches the candidate's front matter), `NAME` (names its date / docket in
   the body without a citation), `NONE`.
4. `where`: the acting text's words that tie the candidate to this appeal (<= 300 characters, verbatim) and the
   judgment line (verbatim, <= 200 characters, once per item).
5. `confidence`: high / medium / low; `note`: one sentence (say what the candidate is, e.g. "the final judgment after
   trial", "the earlier claim-construction order", "a summary-judgment ruling reviewed in the 2005 appeal").

Write one JSON object per candidate, one per line, to `answers_<k>.jsonl` in this folder:
{"item": 3, "target": 1234567, "rel": "...", "act": "...", "how": "...", "where": "...", "judgment": "...",
 "confidence": "...", "note": "..."}
Answer every candidate of every item of your file. Keep reading time per item short (a few minutes).
