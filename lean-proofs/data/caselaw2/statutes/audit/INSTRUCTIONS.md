# Audit: did Congress override this decision?

Each item pairs a court decision with a later Act of Congress that rewrote the words of a US Code section linked to
the decision (a section the decision cited, or a section the law amends near the place where the law or its report
names the decision). You get: the decision's opening and the passages around its citations of the section;
the cited words as the court read them and as the law left them, with the changes; the law's own text where it amends
the section (when found); and, when found, the passage of the law or of a committee report on the law that names a
case. You may read more of the decision with
`git -C ~/Documents/us-caselaw-repos/<court_repo> show HEAD:<path>` if needed (paths are not in the packet;
you can search the repo with `git -C <repo> grep -l "<case name>" HEAD -- decisions/` only if really needed; usually the
packet is enough). Do not fetch anything from the web.

For each item decide:

- `label`, one of:
  - `override_express`: the law changes the rule the decision applied on the point it decided, and the law or its
    committee report says it is responding to this decision or to this litigation (names it, or names the Supreme Court
    decision in the same case).
  - `override_implicit`: the law changes exactly the rule the decision adopted on the point it decided (a court applying
    the new words would decide that point the other way, or the decision's reasoning no longer works), but nothing in the
    packet shows Congress was responding to it.
  - `codifies`: the law writes the decision's holding into the statute or names it approvingly (Congress agrees).
  - `related`: the law changes the cited words, on the same subject, but not on the point the decision relied on, or not
    in a way that would change its result on that point.
  - `unrelated`: the change has nothing to do with what the decision did with the section (cited in passing,
    renumbering, cross-references, a different paragraph of a large subsection).
- `name_check` (only when a law or report passage names a case): `same_decision` (it names this very decision),
  `same_litigation` (another decision in the same case, e.g. the Supreme Court decision on review of this one),
  `different_case` (a different case that happens to share a party name), or `none`.
- `point`: one sentence, what the decision held or did with the cited words.
- `change`: one sentence, what the law changed in those words.
- `why`: one or two sentences for the label.
- `confidence`: high / medium / low.

Be strict: `override_*` needs the law to change the rule on the decision's own point, not merely to amend the same
section. A law can name a case and still only codify it, or only mention it in passing; label what the law does.

Write the results as a JSON list of objects with keys `id, label, name_check, point, change, why, confidence` to the
output file you were given (UTF-8). Reply with only a count of labels.
