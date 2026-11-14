# Reader brief (shadow10, round 10)

You read one pack file (`pack_<k>.md` in this folder). Each item shows a United States Supreme Court order (its own
text: caption, docket number, the court it reviews, the disposition) and up to 10 candidate decisions from the corpus
(title, court, date, opening of the text). The candidates were gathered automatically by party-name words and court;
none, one or several may be the decision the Supreme Court acted on.

For each item decide:
1. Which candidate (letter) is the decision the Supreme Court order acted on (the judgment it vacated / reversed),
   or `none` if no candidate is it, or `unsure`.
2. The evidence in the TEXTS that identifies it, as a list of short tags with a one-line quote each. Useful tags:
   `caption_both_sides` (both parties match), `full_name` (the person's full given + family name in the candidate's
   caption), `abbrev_name` (the names match only through abbreviation, e.g. "Or. Bureau of Labor & Indus."),
   `court_named` (the order names that court), `date_fit` (decided shortly before the petition), `docket_below`
   (the order prints the docket of the case below), `order_cites_below` (the order text cites the decision below),
   `latest_on_docket`, `other` (say what).
3. Why the other plausible candidates are NOT it (one line each, only for candidates with matching names).
4. If you see a general pattern that would let a program pick the right decision from these texts (without any
   outside knowledge), say it in one sentence.

Work only from the pack text. Do not look anything up elsewhere and do not open other files in this folder or
outside it. Write your answers as JSON lines to `ans_<k>.jsonl` in this folder (one object per item):
`{"item": "1.3", "pick": "B"|"none"|"unsure", "evidence": [["tag", "quote"], ...], "others": "...", "pattern": "...", "confidence": "high"|"medium"|"low"}`
Then reply with one line: the number of items written.
