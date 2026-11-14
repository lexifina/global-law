# Round 7 rehear rules (agent b4rehear): en banc, docket-linked, "set aside"

Code: `r7rehear.py` (b: en banc + docket; rehear set-aside rows), `r7setaside_bo.py` (d: decision under review).
Base: the round-6 `rehear` linker (`round6/history/rules/rehear/RULES.md`, its claims cache and its citation /
docket linking, unchanged) and the round-6 `below_other` linker (imported; one step changed). Every rule below runs
over the whole corpus; none names a case, citation, party or docket.

## 0. Why round 6 failed (blind audits r1 + a3, status rows, link + same status effect; `r6_audit_items.tsv`)

| round-6 rule | n | right |
|---|---|---|
| c-vac-cite-sent (en banc recital + citation in the sentence) | 45 | 23 |
| c-reh-cite-sent (silent en banc, citation in the sentence) | 19 | 6 |
| c-reh-cite-ctx | 42 | 34 |
| c-vac-cite-ctx | 33 | 28 |
| c-order-cite-* | 10 | 7 |
| c-order-docket (grant order, docket link) | 35 | 34 |
| c-vac-docket | 19 | 17 |
| c-reh-docket (silent en banc, docket link) | 11 | 6 |
| a/b-docket (not en banc) | 55 | 46 |

Failure kinds (55 status rows read):
1. **The cited decision is the order granting rehearing en banc, not the panel opinion** (27): "We granted
   rehearing en banc. X v. Y, 795 F.3d 1188" — the citation after the recital is the published grant order.
2. **Other litigation / same reporter page** (7, all in r1, before the round-6 r2 docket gate).
3. **Limited or partial en banc / partial act** (8): rehearing limited to one issue or some appellants; "that
   portion of the panel opinion"; "insofar as".
4. **The en banc court adopts / reinstates the panel decision** (4): "for the reasons set forth in the original
   majority opinion", "the mandate is reinstated".
5. **Docket link to the wrong decision of the docket** (5): remand decision that only reports a Supreme Court
   vacatur; an order (denying intervention, setting reargument, granting en banc) taken for the opinion; an opinion
   of another date ("the opinion issued on August 3, 2018 is withdrawn" linked to the June 18 opinion).
6. **Kind**: "the court en banc reverses the panel decision" labelled rehearingEnBancGranted; "suggestions are
   denied" read as a grant; the suspension of a judgment vacated (not the judgment).

## 1. Common to every row (R7-C)

- R7-C1 The act sentence must not report another court's act: no row when it says "certiorari", "by the (United
  States) Supreme Court", "the Supreme Court vacated / reversed / remanded / granted", "United States Supreme
  Court", "remanded from / by" (a state supreme court naming itself is not caught).

## 2. En banc (D is the court en banc, or its order granting rehearing en banc) — `r7rehear:enbanc:*`

- R7-E1 **T is the panel's opinion**: T's own text is not an order about rehearing en banc / rehearing /
  reargument (body < 6,000 characters and a grant phrase, a denial phrase, a reargument phrase, or an ORDER
  heading with rehearing / en banc words), and T is not itself an en banc decision (en banc in its head matter or
  opening, outside a petition phrase). [kind 1]
- R7-E2 **Same appeal, latest opinion**: T shares a docket number with D and is the latest earlier same-court
  decision of that docket after removing the orders of R7-E1 and en banc decisions; identical docket sets, or the
  sentence says "the panel opinion in this case" (round-6 r2 gate kept). [kinds 1, 2, 5]
- R7-E3 **Silent en banc opinion** (D6-4, kind `rehearingEnBancGranted`, variant c-reh): only when the panel
  decision is identified by citation (cite-sent / cite-ctx / cite-head; not by docket alone), D nowhere adopts,
  reaffirms, reinstates or affirms the panel decision (round-6 adopt / adhere / improvident notes + `ADOPT2`:
  "adopt … panel opinion", "reinstat… panel / mandate / original opinion", "for the reasons set forth in the
  original / panel (majority) opinion", "affirm the judgment of the panel"), and no sentence of D about the
  rehearing limits it (`LIMIT`: "limited to", "sole issue", "only as to", "as to appellant(s)", "on the issue
  of", "insofar as", "in part", "portion(s) of", "Part / Section N", "to the extent"). When D says "the court en
  banc reverses the panel decision" (or "we reverse the panel"), the row is that sentence with kind `reversed`.
  [kinds 3, 4, 6]
- R7-E4 **Grant order** (c-order): no row when the order denies a petition / suggestion (short text with a
  denial phrase); a limited grant gets scope `unknown`. [kind 6]
- R7-E5 **Explicit act** (c-vac: the en banc court's own words vacate / withdraw the panel decision, present or
  past): a recital (not a present-tense order) gives no row when D adopts / reinstates the panel decision; a
  negative act whose sentence also reinstates (part of) it gives no row; a partial reinstatement ("Part B", "the
  remainder", "other than", partial words) gives no row; a partial or limited withdrawal gives no row; a partial or
  limited vacatur gets scope `unknown`. [kinds 3, 4]

## 3. Docket-linked rows of a panel acting on its own earlier opinion (not en banc) — `r7rehear:docket:*`

- R7-D1 **Date named**: the act sentence names a date; T's date is within 3 days of a named date; T is the only
  earlier same-court decision of D's identical docket set with such a date (plus the round-6 docket + caption +
  window gates). [kind 5]
- R7-D2 **The object is the opinion itself**: "opinion" / "decision", or "judgment" marked as this court's
  ("our", "this court", "herein", "in this case"); no row when the object or the words around it name a
  suspension, stay, mandate, motion, petition, an order granting / denying / dismissing / staying / recalling, a
  certificate or remittitur; T is not an order of R7-E1. [kinds 5, 6]
- R7-D3 **Partial**: a partial vacatur gets scope `unknown`; a partial withdrawal / supersession / reinstatement
  gives no row. [kind 3]
Rows linked by citation (panel-cite) were installed in round 6 and are not re-emitted (only their set-aside rows,
section 4).

## 4. "Set aside" as a vacatur cue (DESIGN7 3.2, claim `setAside`) — `r7setaside:*`

Round 6 dropped every disposition whose only negative act word was "set aside" (rehear: `skip_nocue_vacated`;
below_other: `no_cue_word`; none of them reached a `rejects.tsv`, which is why the certify rejects files hold no
`noCue` line). Round 7:
- rehear: a claim of kind `vacated` whose verb is "set aside" and whose sentence has no "vacat" keeps the round-6
  object rules (an opinion / judgment of this court; lower court, agency, jury, conviction, sentence, default,
  consent, final judgment refused) and the rules of sections 1-3 for its link; claim `setAside`.
- below_other: a clause naming the target's court whose only negative act word is "set aside" (not quashed /
  annulled) gives `vacated` (scope by the round-6 rules); then R7-S1 the set-aside phrase has a judgment / decree
  / order / decision / ruling / determination as its object (passive "the judgment … is … set aside", active
  "we set aside the judgment"); R7-S2 no row when the noun phrase or the words up to "set aside" name a verdict,
  sentence, default, award, finding, assessment, sale, deed, contract, tax, an agency / board / commission /
  referee / master / arbitrator / magistrate, a plea, bond, lien, service, settlement, consent, summary
  judgment etc., or when "set aside" is an infinitive ("to set aside", "motion to set aside"); R7-S3 the round-6
  shared reporter page guard. Only rows round 6 did not emit are kept.
- below_sc and memo: not done (section "left out" in NOTES.md).
