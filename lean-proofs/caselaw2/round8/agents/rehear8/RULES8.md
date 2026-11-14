# Round 8 rehear rules (agent rehear8): grant orders -> panel opinion; no-date docket rows

Code: `r8rehear.py`. Base: the round-6 `rehear` reader (claims cache of the whole corpus, 752k decisions read, 36,090
records with a claim), the round-6 docket index (`rehear_link.docket_index`), the round-7 b4rehear candidates and
text facts (`r7rehear.py`: `t_facts` order / en banc tests, `latest_opinion`, R7-C1 `SC_ACTOR`, R7-D2 `OBJ_BAD`).
Every rule runs over the whole corpus; none names a case, citation, party, docket or label. No answer key read.

## G. Orders granting rehearing that act on the panel opinion — `r8rehear:order:<var>-<how>`

Acting decision O = the order itself (its own words). Target T = the panel opinion it acts on.

- G-1 **Population**: every record of the claims cache whose text is short (< 7,000 characters of body) and that
  either (a) has a sentence granting rehearing en banc (round-6 GRANT forms; not inside a motion "that ... be
  reheard"), or (b) grants rehearing (round-6 REHGRANT / on-rehearing mark) and states a present act (p1 / p2 / p3
  / p4, vacated or withdrawn) on an opinion / decision / judgment of this court ("the panel opinion", "the opinion
  filed ...", "our ...", "the court's ...", "the prior / original ... opinion").
- G-1b O is an order: round-7 `order_like` (body < 6,000 characters with a grant / denial / reargument phrase, or an
  ORDER heading with rehearing words), or (b) with body < 6,000 characters.
- G-2 **Candidates for T**: same court, a docket number of O's identical docket-number set, strictly earlier than
  O, at most **548 days** before O (the round-7 installed grant-order rows: delay median 134, p99 478, max 546
  days), not an order about rehearing / reargument and not an en banc decision (round-7 R7-E1 text facts).
- G-3 **Act sentence and kind**: an explicit present act of O on this court's opinion -> its kind (`vacated` /
  `withdrawn`); else the grant of rehearing en banc -> `rehearingEnBancGranted` (as round-7 c-order). No row for a
  panel-rehearing grant without act words (no status change). Act sentences refused: R7-C1 another court the
  actor; R7-D2 object a stay / mandate / motion / order granting ...; a recital (N-4); "reinstat" in the sentence
  (R7-E5); another court's decree inside the act span (N-7). G-3b a grant sentence whose grant words belong to a
  motion about the petition ("motion to withdraw the petition ... is GRANTED") is not a grant; G-3c a grant
  sentence about another case ("the Lee case", "X v. Y", "In re", "in No.") is not a grant; G-3d a vote of named
  judges ("Judges X and Y voted to rehear the case en banc") reports a minority, not the grant.
- G-4 **Denied / failed poll**: no row when O denies rehearing en banc ("rehearing en banc ... is (also) denied",
  "petition for rehearing en banc ... denied") or reports a failed poll ("voted against", "failed to produce /
  receive a majority", "the suggestion fails", "did not vote in favor"), unless O also says a majority voted to
  rehear.
- G-5 **Which opinion**: if the act / grant sentence names a date, T is the unique candidate within 3 days of it
  (none or several: no row); else T is the latest candidate, unique at its date, and no candidate of another
  docket-number set of the same docket is later than T. G-5b a same-court earlier citation in O that is not T: no
  row.
- G-6 **Evidence** `name:<tokens>`: party-name tokens shared by O's title / parties and T's title (at least two, or
  all of T's when it has fewer: the round-6 docket test), anchored in O's caption (head matter to the court line,
  with an anchor cue); an order with no such caption (state reporters, CourtListener texts): unanchored, the
  tokens standing within 400 characters of the act sentence (certifier window).
- G-7 **Adoption**: no row when O, in the court's own part, adopts / adheres to / reinstates the panel / original
  decision (round-6 ADOPT, ADHERE; round-7 ADOPT2; not negated).
- Scope: `unknown` when the act is partial (round-6 PARTIAL2, or the object is a part of the opinion, N-8) or O
  limits the rehearing (round-7 LIMIT); a partial withdrawal gives no row. Rows already in the base (same by and
  target) are not re-emitted; an order that already has a base row to another target gives no row.

## N. Docket-linked acts on the court's own earlier opinion that name no date — `r8rehear:docket:<var>-nodate|redate`

Candidates: the round-7 b4rehear docket candidates (round-6 docket link: same court, identical docket set, caption
tokens, window 1,154 days) that round 7 dropped for R7-D1 (no date named, or a date of another decision).

- N-1 **No date named**: T must be the latest earlier same-court decision sharing a docket number with D that is not
  an order about rehearing / reargument and not an en banc decision (round-7 `latest_opinion`), with no other such
  decision at T's date, and T's docket set identical to D's: no other opinion of the docket between T and D.
- N-2 = R7-D2 (object this court's opinion / decision / judgment; not a stay, mandate, motion, order granting ...;
  T not an order).
- N-3 a `judgment` object counts only when its own noun phrase marks it as this court's ("our judgment", "the prior
  judgment", "the judgment of this court"), not when "our" stands elsewhere in the sentence.
- N-4 no row for a recital of an earlier ruling ("we reiterate ...", "reaffirm", "in our initial opinion ... that",
  "as we held", "the Supreme Court ... having reversed ...").
- N-5 **Another date named**: re-point to the unique same-docket earlier decision within 3 days of the named date
  (not an order, not en banc), with name evidence in D's caption; else no row.
- N-6 = R7-D3, plus: a reinstatement that excepts a part or remands a sentence ("remainder", "except",
  "resentencing", "portion", "in part") gives no row.
- N-7 the act's own span (object .. verb) names another court ("the judgment of the district court is vacated"),
  unless that court is what this court's judgment acted on ("our judgment reversing the district court is
  vacated"): no row.
- N-8 the object is a part of the opinion ("any expression in our former opinion", "that portion of our opinion"):
  withdrawn / superseded / reinstated -> no row; vacated -> scope `unknown`.
