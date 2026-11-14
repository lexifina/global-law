# Reader brief (fjc8, read1): how does a court of appeals opinion treat a district-court decision?

You read US court decisions from a local corpus and report facts with exact quotes. You do not edit any file except
your answer file. No web access is needed or allowed.

Get a decision's full text (Git Bash):
```
cd ~/Documents/us-caselaw-lean-work/caselaw-lean-2
python -X utf8 round6/history/r6lib.py text <node>        # whole text
python -X utf8 round6/history/r6lib.py row <node>         # court, date, citation, caption
```
Search inside a text by piping to `grep -n -i` or reading it fully (texts can be long; read the opening, the
procedural history, every place the district decision is cited, and the end of the majority opinion).

Your items are in `read1/items_<k>.tsv` (k given in your task): each line is an appellate opinion (a federal court of
appeals) and a district-court (or bankruptcy-court) decision. For each item answer:

1. `cited`: how the appellate opinion cites the district decision (by its reporter citation, e.g. "699 F.Supp.2d
   1092", or by caption only, or not at all). Quote the citation sentence (exact, up to ~300 characters) and say
   whether it is in the body, a footnote, the head matter, or a quotation.
2. `court_phrase`: the nearest sentence (before or after the citation) that names the court below ("the district
   court", "the bankruptcy court", "Judge X", "the court below", "the trial court"…). Quote it, and say how many
   sentences away it is from the citation sentence (0 = the same sentence).
3. `under_review`: is THIS district decision the judgment/order that the appeal reviews? `YES` (it is the decision
   appealed from), `EARLIER` (an earlier ruling in the same litigation; the appeal reviews a later ruling or final
   judgment), `LATER`, `OTHER_CASE` (a different litigation cited as authority), `UNSURE`. Give the reason in a
   sentence, with a quote when possible (e.g. "appeal from the final judgment entered after trial").
4. `act`: what the appellate court does to the decision reviewed by the appeal, from its own judgment line:
   `REV` (whole reversal or vacatur), `PART` (affirmed in part and reversed/vacated in part), `AFF`, `DISMISS`
   (appeal dismissed), `OTHER`. Quote the judgment line exactly (e.g. "REVERSED AND REMANDED.").
5. `act_on_this`: what that act does to THIS district decision: `REV`, `PART`, `AFF`, `NONE` (the act concerns a
   different ruling), `UNSURE`.
6. `caption_note`: do the two captions name the same parties (same on both sides / one side only / different)?
7. `note`: anything else that explains why an automatic reader could miss the link (the citation is a parallel
   cite, the caption changed, two district rulings are cited, an en banc or later proceeding, consolidated appeals…).

Write your answers to `read1/answers_<k>.jsonl`, one JSON object per item, keys: `item`, `cited`, `cite_quote`,
`cite_place`, `court_phrase_quote`, `court_phrase_dist`, `under_review`, `under_review_why`, `act`, `judgment_quote`,
`act_on_this`, `caption_note`, `note`. Use exact quotes from the texts (copy, do not paraphrase). Finish every item;
if a text is missing, say so in `note` with `under_review` = `UNSURE`. Reply with one line per item:
`item under_review act act_on_this`.
