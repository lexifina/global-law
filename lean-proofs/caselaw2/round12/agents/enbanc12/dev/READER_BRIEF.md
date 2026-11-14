# Reader brief (enbanc12 development check)

Root folder: `~\Documents\us-caselaw-lean-work\caselaw-lean-2\round12\agents\enbanc12\` (pack paths are
relative to it). Read only this brief, your pack and the files it names.

Each item: an acting decision A (file), a target decision T (file), and character offsets of a passage in A's file
(count characters of the file as read, with CRLF as one newline; the offsets are approximate guides - search A for
words like "vacat", "withdr", "panel").

For each item answer:
1. `same_case`: is T the panel decision in the same appeal that A (an en banc court, or its order) reheard? yes / no /
   unclear. (no if T is an order, another appeal, another case, or a different panel opinion than the one the
   passage speaks of)
2. `acted`: did A's court itself (en banc, by A or by the grant of rehearing en banc A reports) vacate / withdraw T?
   yes / no / unclear. no when the passage is about another court, a party's request, a rule in general, another
   case, or a dissent's or concurrence's words.
3. `kind`: what happened to T: vacated / withdrawn / reinstated / partly_vacated / unaffected / unclear.
4. `whole`: did the act reach T as a whole (yes) or only part (no)?
5. `later_reinstated`: does A reinstate or adopt T (or its judgment) as a whole after all? yes / no.
6. One-line note with the deciding words (<= 200 characters).

Write a TSV at the path your task gives with header
`item	same_case	acted	kind	whole	later_reinstated	note` (tabs between fields; none inside a field). Answer every item.
