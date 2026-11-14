# Reader brief (diagnosis): which lower-court decision did the Supreme Court's order act on?

You read a pack of items. Each item is one entry of a United States Supreme Court order list (its own words: date,
docket number, caption, disposition such as "Judgment vacated, and case remanded to the United States Court of Appeals
for the ... Circuit for further consideration in light of ..."), followed by up to 12 candidate decisions of the court
below (node id, title, docket, date, and the opening of the text).

For each item decide, from the texts in the pack only:

1. `pick`: the candidate node id that is the judgment the Supreme Court's order acted on (the decision under review),
   or `none` if no candidate is it, or `unsure`.
2. `why`: one short sentence.
3. `category` for the case: one of
   - `same_name_other_person` (candidates are other people of the same surname; the right one is absent or unclear),
   - `name_form` (the right candidate prints the party name differently: compound surname, middle names, aliases,
     initials, a typo, "In re", substituted officer),
   - `several_on_docket` (several decisions on the right docket; you can tell which one is the judgment),
   - `later_entry` (a later decision on the docket, after the petition, is printed too),
   - `not_present` (the decision under review is not among the candidates),
   - `other`.
4. `confidence`: high / medium / low.

Write one JSON object per line, one line per item in pack order, to the answer file named in your prompt:
`{"item": <n>, "pick": "<node id>|none|unsure", "category": "...", "confidence": "...", "why": "..."}`.
Use the Write tool. Do not read any other file than the pack and this brief.
