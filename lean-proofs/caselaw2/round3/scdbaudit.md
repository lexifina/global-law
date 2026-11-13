# scdbaudit: the 12 Supreme Court decisions with an admitted overruling that SCDB does not flag (round 3)

Started 22:40, 12 Nov 2026. No external model. Twelve Claude subagents, one per decision, read the full opinion
text blind: no row, no SCDB, no CRS. Gold was opened only after the audit, to measure.

## List

Recomputed with `score.py`'s own logic (`load_model` + `score_scdb_crs`) on the live data and `out/certs.tsv`.
The list is the same 12 ids as in `eval/score_final.txt`. They carry 17 admitted rows on Supreme Court targets.

## Result

| | decisions | rows |
|---|---|---|
| Row correct, SCDB does not flag it (keep) | 9 | 14 |
| Row kept, scope corrected (`all` to `partialUnknown`) | 2 | 2 |
| Row removed (report of earlier decisions) | 1 | 1 |

SCDB precision: before 113/125 = 90.4%. After the delta 113/124 = 91.1% (one decision leaves the denominator;
recall 113/278 unchanged). The other 11 decisions are real acts of the Court that SCDB does not code, so the
remaining gap is a difference of definition, not reader error: 6 disavow or recede from dicta only, 3 are partial
"insofar as / to the extent" overrulings without the word "overrule", 1 is a supersession by a rule of evidence,
1 is a conditional disapproval of 1876.

No pair is in `gold/crs_overruled.tsv`, and CRS lists none of the 17 targets as overruled by any decision.

## Table

Blind class: H holding of the majority, D own act on dictum or language only, R report of an earlier decision,
S superseded by statute or rule, N conditional words.

| id | Decision | Target(s) | Blind class | Verdict | Quote | Action |
|---|---|---|---|---|---|---|
| 5945277 | Ex parte Flippin, 94 U.S. 348 (1876) | McCargo v. Chapman, 20 How. 555 | N (else D), majority; syllabus repeats "so far as it conflicts ... disapproved" | (a) with scope error. Conditional, partial disapproval. SCDB: conditional, 1876 | "If there is any thing in the case of McCargo v. Chapman, 20 How. 555, to the contrary of this, it is disapproved." | scope `all` to `partialUnknown` |
| 6044406 | Hensley v. Municipal Court, 411 U.S. 345 (1973) | Stallings v. Splain; Johnson v. Hoy; Baker v. Grice; Wales v. Whitney | H partial ×4, majority footnote | (a) correct. Auditor: a database should flag it. SCDB likely misses it: footnote, no "overrule" | "Insofar as former decisions, Stallings v. Splain ...; Johnson v. Hoy ...; Baker v. Grice ...; Wales v. Whitney ..., may indicate a narrower reading of the custody requirement, they may no longer be deemed controlling." | keep 4 rows |
| 6045070 | NLRB v. Boeing Co., 412 U.S. 67 (1973) | NLRB v. Allis-Chalmers; Scofield v. NLRB | D ×2, majority | (a) correct as `recededFrom` / `partialUnknown`. SCDB: dicta only, holdings stand | "Being squarely presented with the issue in this case, we recede from the implications of the dicta in these earlier cases." | keep 2 rows |
| 6053152 | Aberdeen & Rockfish R. Co. v. SCRAP, 422 U.S. 289 (1975) | United States v. Griffin, 303 U.S. 226 | R, majority footnote | (b) wrong. The sentence is followed by "United States v. Jones, 336 U. S. 641, 647 (1949); Rochester Tel. Corp. v. United States, 307 U. S. 125, 145 (1939)": it reports what those decisions did | "Insofar as it rested on the negative-order doctrine of Procter & Gamble Co. v. United States, 225 U. S. 282 (1912), Griffin is no longer the law." | row removed |
| 6107658 | Bourjaily v. United States, 483 U.S. 171 (1987) | Glasser v. United States, 315 U.S. 60 | S partial, majority | (a) correct (`supersededByEnactment`, issue-scoped). SCDB does not code supersession by a rule as precedent alteration | "To the extent that Glasser meant that courts could not look to the hearsay statements themselves for any purpose, it has clearly been superseded by Rule 104(a)." | keep |
| 6129345 | Estelle v. McGuire, 502 U.S. 62 (1991) | Cage v. Louisiana; Yates v. Evatt | D ×2, majority footnote | (a) correct (`disapproved` / `partialUnknown`). SCDB: language only, footnote | "So that we may once again speak with one voice on this issue, we now disapprove the standard of review language in Cage and Yates, and reaffirm the standard set out in Boyde." | keep 2 rows |
| 6149775 | Hawaiian Airlines, Inc. v. Norris, 512 U.S. 246 (1994) | Elgin, J. & E. R. Co. v. Burley, 325 U.S. 711 | D, majority (unanimous) | (a) act and target correct; kind `overruled` overstates a disavowal of dicta (see pattern) | "Nonetheless, to avoid any confusion, we expressly disavow any language in Burley suggesting that minor disputes encompass state-law claims that exist independent of the CBA." | keep |
| 6164047 | Romer v. Evans, 517 U.S. 620 (1996) | Davis v. Beason, 133 U.S. 333 | H partial (R possible: Brandenburg is cited after it), majority | (a) correct. Brandenburg does not name Davis; the statement is the Court's own. SCDB: no "overrule", reply to the dissent | "To the extent Davis held that persons advocating a certain practice may be denied the right to vote, it is no longer good law." | keep |
| 6164051 | Quackenbush v. Allstate Ins. Co., 517 U.S. 706 (1996) | Thermtron Products v. Hermansdorfer, 423 U.S. 336 | H partial, majority (unanimous) | (a) correct. Auditor: a database should flag it; the Court concedes the disavowed point was necessary to Thermtron | "To the extent Thermtron would require us to ignore the implications of our later holding in Moses H. Cone, however, we disavow it." | keep |
| 6169041 | Atherton v. FDIC, 519 U.S. 213 (1997) | Briggs v. Spaulding, 141 U.S. 132 | H partial, majority | (a) with scope error. Only the federal common-law standard of care is displaced, as a consequence of Erie. SCDB: no overruling words | "We conclude that the ciated in cases such as Briggs did not survive this . Court's later decision in Erie v. Tompkins." (OCR gaps as in the file) | scope `all` to `partialUnknown` |
| 6239868 | Puckett v. United States, 556 U.S. 129 (2009) | Mabry v. Johnson, 467 U.S. 504 | D, majority footnote | (a) act and target correct; kind `overruled` overstates (dictum) | "We disavow any aspect of the Mabry dictum that contradicts our holding today." | keep |
| 6239875 | 14 Penn Plaza LLC v. Pyett, 556 U.S. 247 (2009) | Alexander v. Gardner-Denver Co., 415 U.S. 36 | D, majority footnote | (a) act and target correct; kind `overruled` overstates (dicta; "does not contradict the holding of Gardner-Denver") | "And it is why we disavow the antiarbitration dicta of Gardner-Denver and its progeny today." | keep |

Things the auditors found that we do not carry (not added; out of this task's scope): Bourjaily also says Rule
104(a) prevails over United States v. Nixon's passing statement; Quackenbush says the transfer function of Gulf
Oil v. Gilbert "has been superseded by statute" (§ 1404(a)); Pyett's "progeny" covers Barrentine and McDonald;
Atherton's "cases such as Briggs" covers Martin v. Webb.

## Installed delta

Under `data/.install.lock`, by key, with `*.pre_round3.tsv` backups written first (none existed):

- `data/treatments.tsv`: 32,458 to 32,457 rows. Removed `t:6053152:5972524:59287`. Scope `all` to
  `partialUnknown` on `t:5945277:5942657:6968` and `t:6169041:5949320:24176`.
- `data/treatments_items.tsv`: the removed row's line deleted (32,458 to 32,457).
- `data/reader_rejects.tsv`: appended `6053152:59287 / audit / report-of-earlier-overruling:scdbaudit-round3`.
- `cert_text.tsv` and `window_sha.tsv` not touched. The removed row's window stays as an unused line.

Certificates: the two rescoped rows keep all six CERT columns unchanged; both are `ok` in `out/certs.tsv`, and
scope is not an input of `check_cert`. No new certificate was written. The reference engine was not re-run by me
(a scope change on two rows changes those two targets from whole to partial negative status; the coordinator's
integration run will show it).

Delta files: `work/round3/scdbaudit/delta.json`, `install.py` (idempotent), `prep.py` (list, rows, texts),
`pattern.py`, `rows.json`, `audit/<id>.json` (12 blind answers), `texts/<id>.md`.

## Systematic patterns

1. **Report shape "X is no longer the law. <citations of later decisions>"** (the Griffin error; the round-2 scan
   family `v2:no-longer-law`). Among all admitted status-changing rows, 2 have a quote ending "no longer the/good
   law" directly followed by a citation: Griffin (removed) and Romer/Davis (kept: the cited case does not name the
   target). The pattern is not widespread. Not fixed mechanically: the trailing citation does not by itself tell a
   report from an own act.
2. **Disavowal of dicta or language labelled `overruled`.** 36 admitted rows (3 with the Supreme Court as the
   treating court: Hawaiian Airlines, Puckett, Pyett) have a quote with "disavow" plus dicta / language /
   statement / suggest and kind `overruled`. Some of the 36 are mixed sentences ("overrule and disavow") and are
   right. For the pure dicta ones the act and target are right, the scope is already `partialUnknown`, and only
   the kind is too strong. `disapproved` would fit, but its cue list is only "disapprov", so the relabel would
   fail the certificate. Not changed. List: `work/round3/scdbaudit/pattern.json` key `disavow`.
3. **Conditional "If there is anything ... to the contrary" with scope `all`:** 1 admitted row (Flippin), fixed.

## Requests and text for docs I do not own

- For `requests_to_lean.md` (not filed as a blocking request; nothing here depends on it): consider adding
  "disavow" to the `disapproved` cue list in `Certificate.lean` and the reference, so that disavowals of dicta
  can be relabelled `disapproved`.
- For DEVIATIONS.md: "SCDB precision counts every Supreme Court decision with an admitted status-changing row on
  a Supreme Court target, including supersession by rule, disapproval of language and disavowal of dicta. SCDB's
  precedentAlteration is narrower. A blind audit of the 12 unflagged decisions found 11 real acts and 1 reader
  error (removed)."
- `score.py` could report SCDB precision a second time restricted to kind `overruled` with scope `all` or
  `issues:`; not changed here.

## Left

- The 36 "disavow" rows were counted, not audited one by one.
- The Griffin overruling belongs to Rochester Tel. Corp. v. United States (1939) if it is to be carried at all;
  no row was written for it (it needs a quote from Rochester's own text).
