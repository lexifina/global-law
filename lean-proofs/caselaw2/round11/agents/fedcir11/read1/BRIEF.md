# Reader brief (fedcir11 read1)

You read pairs of court decisions from a local corpus and answer from the texts only. Do not use the web or any
other file than the decision texts printed by the command below.

Each line of your items file (`items_<k>.tsv` in this folder) gives an acting decision (an appellate opinion) and a
target decision (an earlier decision of a lower tribunal), by node id, with their captions.

Print a decision's text (Git Bash, from `~/Documents/us-caselaw-lean-work/caselaw-lean-2`):

    python -X utf8 round6/history/r6lib.py text <node>             (whole text; the front matter gives court, date,
                                                                    docket, citations)
    python -X utf8 round6/history/r6lib.py text <node> <start> <end>   (a slice)

Read the acting decision (the opinion of the court, its judgment line) and enough of the target (front matter,
opening, ending) to answer, for each item:

1. `rel`: what is the target to the acting decision?
   - `UNDER_REVIEW`: the acting court reviews this very decision of the lower tribunal in this appeal (the judgment /
     ruling appealed from, or a ruling merged into it that the appeal reviews);
   - `EARLIER`: an earlier ruling of the same case that this appeal does not review (an earlier remand order, an
     earlier decision reviewed in an earlier appeal, an interlocutory ruling not before the court);
   - `LATER_OR_OTHER_RULING`: another ruling of the same litigation (later, or on another matter) that this appeal
     does not review;
   - `OTHER_CASE`: a different case (cited as authority, a companion or parallel case);
   - `UNSURE`.
2. `act` (only when UNDER_REVIEW): what the acting court itself did to it in its judgment: `REVERSED`, `VACATED`,
   `MODIFIED`, `AFFIRMED`, `PART` (affirmed in part and reversed / vacated in part), `DISMISSED` (appeal dismissed),
   `OTHER`.
3. `how`: how the acting text identifies the target: `CITE` (cites it by reporter citation), `NAME` (names it /
   its date / docket without a citation), `NONE` (does not identify it; the link is only the caption).
4. `where`: the acting text's words that tie the target to this appeal (<= 300 characters, verbatim), and the
   judgment line (verbatim, <= 200 characters).
5. `tribunal_words`: the words the acting court uses for the lower tribunal in that tie sentence (e.g. "the Court of
   International Trade", "the trial court", "the Claims Court", "the Veterans Court", "the court below").
6. `confidence`: high / medium / low; `note`: one sentence.

Write one JSON object per item, one per line, to `answers_<k>.jsonl` in this folder:
{"item": 3, "rel": "...", "act": "...", "how": "...", "where": "...", "judgment": "...", "tribunal_words": "...",
 "confidence": "...", "note": "..."}
Answer every item of your file. Keep reading time per item short (a few minutes).
