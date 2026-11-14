# Brief: where the IRS form and the statute disagree

A formal model of the 2025 individual return found that Schedule 8812 refunds more than §24(h)(5) allows, and an
audit found the Schedule A State-and-local-tax worksheet applies §164(b)(6)–(7) in an order secondary sources had
wrong. Forms written for a new law are where such differences are least likely to have been noticed. Your job: for
the forms named in your task, compare the form's and instructions' computation, line by line, with the statute's
words, and report every place they differ, in either direction.

Rules: work only in `~\Documents\global-law-lean\lean-proofs`; write only
`tools/hunt/out/forms/<Name>.md`, `<Name>.json` and scratch under `tools/hunt/out/forms/<Name>/`. Statute text:
`python -I tools/hunt/sec.py <section> [subdivisions…]` (current through Pub. L. 119-138). Fetch the forms and
instructions from irs.gov (the 2025 revisions; drafts at irs.gov/draftforms for 2026 where posted) with WebFetch.
At most 4 web searches (standard mode), only to locate a document or check whether a difference you found is already
written about. No subagents. Do not touch any other file.

Method: for each form, write the statute's computation and the form's computation as two short Python functions
from their own texts, independently; then compare them over a grid of inputs (income, filing status, amounts, number
of dependents, ages) and print every input where they differ, with both results. A difference that only comes from
rounding rules the instructions state is not a finding. For each real difference: the lines and the statutory words;
which way it goes (form gives more / statute gives more); the size in dollars and who is affected; whether a
regulation or notice explains it; whether it is already written about.

Deliver `<Name>.json`: `{"forms":[…],"grid_points":N,"differences":[{"form_line":…,"statute":…,"direction":"form
gives more|statute gives more","example":…,"dollars":…,"explained_by":…,"published":…,"confidence":…}],
"not_retrieved":[…]}` and `<Name>.md`. Reply in at most 250 words: the differences, largest first, then what you
could not retrieve. Say plainly if there are none.
