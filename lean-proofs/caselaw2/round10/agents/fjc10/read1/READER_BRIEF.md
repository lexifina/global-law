# Reader brief (fjc10 read1)

You read court texts only. Your pack is a JSON file of 10 items. Each item has:
- `appellate`: a published U.S. court of appeals opinion (caption, docket, date, the first 1,800 characters of its text);
- `cited_decision`: a published U.S. district court decision (caption, court folder, date, docket, citation, opening text);
- `citations_in_appellate_opinion`: up to 3 places where the appellate opinion cites that district decision (the
  citation is marked `[[CITED: ...]]`, with surrounding text).

For each item decide:
1. `under_review`: is the cited district decision the ruling that THIS appeal reviews (the judgment / order appealed
   from in this appeal)?
   - `REV`  yes, it is the ruling appealed from (or one of them in a consolidated appeal);
   - `PART` it is a ruling of the same case that is part of what is reviewed (e.g. an earlier order merged into the
     final judgment that is appealed, and the appeal addresses it);
   - `EARLIER` an earlier / interim ruling of the same case that is not what this appeal reviews;
   - `LATER` a later ruling (e.g. on remand) of the same case;
   - `OTHER` a different case (cited as authority, a related suit, a companion case not under review here);
   - `UNSURE`.
2. `ties`: which things in the texts tie the cited decision to this appeal (list any): `court_phrase` (the citation
   sentence or a nearby one says "the district court ..." about it), `caption` (the appellate caption / head matter
   names the cited decision's parties), `docket` (the district docket number appears in the appellate text),
   `judge` (the district judge is named in both), `date` (the ruling's date is printed in the appellate text),
   `appeal_from` (the appellate text says "appeal from ..." this ruling), `none`.
3. `why_name_differs`: why the cited decision's caption differs from the appellate caption (one short phrase:
   e.g. "public officer substituted", "abbreviation", "consolidated appeal", "different case", "party dropped").
4. `quote`: the shortest phrase of the appellate text that settles your answer (<= 200 characters).

Write your answers as a JSON list to your answer file: `[{"item": "i03", "under_review": "REV", "ties": [...],
"why_name_differs": "...", "quote": "..."}, ...]`, one object per item, in pack order. Nothing else in the file.
