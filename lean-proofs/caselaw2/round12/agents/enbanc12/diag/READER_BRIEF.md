# Reader brief (enbanc12 diagnosis)

You read court opinions from text files. Root folder:
`~\Documents\us-caselaw-lean-work\caselaw-lean-2\round12\agents\enbanc12\` (paths in your pack are
relative to it). Read only the files your pack names (and this brief). Do not open any other file or folder.

Each item names: a decision P (an earlier decision of a court), a later decision E of the same court that sat
en banc / in banc (or that our metadata says did), and sometimes one or more short orders of the same court between
them. Files start with a front-matter block (caption, date, docket, citations) between `---` lines; then the text.
Long texts: read the front matter, the opening pages, the passages that mention rehearing / en banc / panel /
vacate / reinstate (search the text), and the closing disposition.

For each item answer:
1. `same_case`: is E a rehearing (en banc / in banc) of the same appeal that P decided? (yes / no / unclear)
   "no" when E is another appeal, another case, a first-instance en banc hearing with no panel decision P, or P is not
   the panel's decision on the merits that E reheard (e.g. P is only a motions order, a different earlier appeal).
2. `p_is_order`: is P itself only an order (e.g. an order granting or denying rehearing en banc) rather than the
   panel's opinion? (yes / no)
3. `en_banc_sitting`: is E an en banc rehearing of a panel decision (yes), or a court that ordinarily sits "in banc"
   as its normal full bench / a first-instance en banc hearing (no)?
4. `who_says`: whose own words say what happened to P? one of: `E` (E's text says P / the panel opinion was
   vacated, withdrawn, superseded, set aside), `O` (an order file in the item vacates the panel opinion in its own
   words), `E_and_O`, `none` (no text in the item says it), `E_reinstates` (E reinstates / adopts / affirms the panel
   opinion or its judgment as a whole), `E_partial` (E reinstates or vacates only part of P).
5. `status_of_P`: after E, P's status as the en banc court's act: `vacated`, `withdrawn`, `superseded`,
   `reinstated`, `partly_vacated`, `unaffected`, `unclear`.
6. `quote`: the shortest exact sentence(s) (<= 300 characters) from E or the order that support 4/5, and which file.
7. `cite_target`: if the quoted sentence carries a citation, does that citation name P itself, an order (granting
   rehearing en banc), or something else? (P / order / other / none)
8. One-line note.

Write your answers as a TSV file at the path your task gives: header
`item	same_case	p_is_order	en_banc_sitting	who_says	status_of_P	cite_target	quote_file	quote	note`
one line per item, tabs between fields, no tabs or newlines inside a field. Answer every item.
