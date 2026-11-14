# Disagreements read (round 6, as of 20261112)

How the sample was drawn: `dis_dump.py --label round6 --seed 13` (fixed seed, drawn after scoring; both halves):
16 `NEG` cases the model shows clean, 4 `NEG` cases the model shows `UNK_HIST`, 8 `CLEAN` cases the model shows
`NEG_HIST`, 2 `PART` cases the model shows clean. For each case the reading used our corpus text only: the citation
context of the decision below in our Supreme Court opinion, the disposition sentences of that opinion (`dispo.py`),
and every `history.tsv` row targeting the decision below (kind, by, quote). Dump: `work/dis_round6.txt`.

## Result of the 30-case sample

| cause | n | cases |
|---|---|---|
| model missing (SC text states the disposition; no history row by the SC opinion) | 16 | #1–4, #6–16, #29 |
| model wrong | 7 | #17, #18, #20, #21, #24, #28, #30 |
| source wrong (SCDB code contradicts the Court's stated disposition) | 5 | #22, #23, #25, #26, #27 |
| link error (our link picked a decision that is not the one reviewed) | 1 | #5 |
| mapping artefact | 1 | #19 |

| # | caseId | SCDB | model | reading | cause |
|---|---|---|---|---|---|
| 1 | 1946-038 Patterson v. Lamb | 3 | GOOD | "Reversed." ending the majority; no row | model missing |
| 2 | 1900-176 Detroit v. Parker | 4 | GOOD | "The decree of the Circuit Court is reversed, and the cause is remanded…"; no row | model missing |
| 3 | 1990-098 Johnson v. Home State Bank | 4 | GOOD | "The judgment of the Court of Appeals is reversed, and the case is remanded…"; the only row is a cert denial by an unrelated memorandum order (r6 memo cap-2t) | model missing |
| 4 | 1954-092 Carroll v. Lanza | 3 | GOOD | "Reversed." | model missing |
| 5 | 1914-241 Illinois Central v. Fuentes | 4 | GOOD | linked to *Thompson v. Railroad Comm'n*, 198 F. 691 (1912), cited in counsel's list; the decision reviewed was a 1914 dismissal (not in our text as a citation). Name match on generic tokens | link error |
| 6 | 1967-098 In re Ruffalo | 3 | GOOD | "Reversed." | model missing |
| 7 | 1932-005 Sgro v. United States | 3 | GOOD | "Judgment reversed." | model missing |
| 8 | 1999-011 LAPD v. United Reporting | 3 | GOOD | "Reversed." | model missing |
| 9 | 1976-083 Alexander v. Fioto | 3 | GOOD | "The judgment of the District Court is reversed." | model missing |
| 10 | 1973-153 CIR v. Idaho Power | 3 | GOOD | "The judgment of the Court of Appeals is reversed." | model missing |
| 11 | 1948-066 Fountain v. Filson | 3 | GOOD | "The judgment of the Court of Appeals is, therefore, reversed…" | model missing |
| 12 | 1990-070 Int'l Primate Protection League | 4 | GOOD | "We therefore reverse the decision of the Court of Appeals and remand…" | model missing |
| 13 | 1946-133 SEC v. Chenery | 3 | GOOD | "Reversed." | model missing |
| 14 | 1917-115 U.S. v. Whited & Wheless | 3 | GOOD | "The judgment of the Circuit Court of Appeals is Reversed." | model missing |
| 15 | 2012-042 Bullock v. BankChampaign | 5 | GOOD | "we vacate the judgment of the Court of Appeals and remand" | model missing |
| 16 | 1962-005 U.S. v. Loew's | 5 | GOOD | direct appeal; "The judgments are vacated and the causes are remanded to the District Court" | model missing |
| 17 | 1943-006 SEC v. Joiner | 3 | UNK_HIST | rows: reversed ("The judgment is Reversed.") and affirmed from "Mr. Justice Roberts is of the opinion that the judgment should be affirmed" (a dissent note) → conflict → unknown | model wrong |
| 18 | 1917-199 Fuller v. Otis Elevator | 3 | UNK_HIST | "Judgment reversed. Judgment of Supreme Court affirmed." read as reversed with scope unknown | model wrong |
| 19 | 1972-164 Keyes v. School Dist. No. 1 | 5 | UNK_HIST | "The judgment of the Court of Appeals is modified to vacate instead of reverse the parts of the Final Decree…, and the case is remanded" — a modification, partly negative; SCDB 5 | mapping artefact |
| 20 | 1908-028 U.S. v. Keitel | 4 | UNK_HIST | "Reversed and remanded…" read with scope unknown | model wrong |
| 21 | 1953-020 U.S. v. Morgan | 2 | NEG_HIST | the row's quote is a quoted historical passage ("…it may be reversed in the same court, by writ of error coram nobis"); the Court affirmed | model wrong |
| 22 | 1940-084 Olsen v. Nebraska | 2 | NEG_HIST | "The judgment is reversed and the cause is remanded to the Supreme Court of Nebraska…" | source wrong |
| 23 | 1907-018 Pa. Coal & Coke v. Cassatt | 9 | NEG_HIST | "the judgment is reversed, and the cause remanded with a direction to dismiss the writ of error" | source wrong |
| 24 | 1987-121 Liljeberg | 2 | NEG_HIST | the row's quote narrates the court of appeals' reasoning ("…whether a judgment should be vacated…"); the Court affirmed | model wrong |
| 25 | 1936-060 De Jonge v. Oregon | 2 | NEG_HIST | "The judgment of conviction is reversed…" | source wrong |
| 26 | 1936-059 U.S. v. Madigan | 2 | NEG_HIST | "Reversed." | source wrong |
| 27 | 1922-070 Mason v. United States | 2 | NEG_HIST | "The decrees of the Circuit Court of Appeals are reversed and those of the District Court are affirmed…" (SCDB coded the effect on the trial decree) | source wrong |
| 28 | 1936-100 Senn v. Tile Layers | 2 | NEG_HIST | Court affirmed ("Affirmed."); the model's negative row is "Reversed." from a different 1938 SC decision (node 5972536) attached to 222 Wis. 383 | model wrong |
| 29 | 1976-173 Dothard v. Rawlinson | 7 | GOOD | "affirmed in part and reversed in part, and the case is remanded"; no row | model missing |
| 30 | 1957-103 U.S. v. McNinch | 7 | GOOD | "affirmed in McNinch and reversed in Cato and Toepleman" (one court-of-appeals opinion for three cases); the model kept only "affirmed" | model wrong |

Reading of the misses: in 15 of the 16 `NEG`→clean cases the Supreme Court opinion states the disposition in plain
words ("Reversed.", "The judgment … is reversed") and the decision below is cited in the opening procedural history
with a reporter citation, yet the model has **no history row at all** from that Supreme Court opinion. The recall gap
is therefore mostly unread or unattached dispositions, not missing texts.

## All 64 `CLEAN`→`NEG_HIST` cases (round 6), read in full

Because 5 of the 8 sampled false positives were SCDB errors, every one of the 64 linked `CLEAN` cases the model shows
`NEG_HIST` was read (disposition sentences of the majority / per curiam / combined section; `work/clean_neg_dispo.txt`).

| cause | n | notes |
|---|---|---|
| source wrong | 43 | SCDB 2 or 9 where our text of the opinion says the judgment under review is reversed (41 of them in the legacy file, 1907–1944; modern: 2002-009 *Howsam*, 2014-059 *Sheehan* reversed in part). Listed with verbatim quotes in `source_errors.tsv`. |
| mapping artefact | 7 | the same decision below was reviewed by two Supreme Court decisions (one dismissed/affirmed, the other reversed or vacated): 1896-184, 1917-002, 1927-005, 1931-014, 1940-109 (companion *U.S. v. Ryerson*), 1979-063 (earlier GVR in *Vitek*); 1919-081 reversed as to two appellants, dismissed as to one |
| model wrong | 9 | quoted or narrated words (1953-020, 1984-105, 1987-121, 1966-128 "Reversed on other grounds" in a citation), dissent in a combined section (2014-033, 2022-008), a different SC decision attached (1936-100, 1944-148, 1975-084) |
| link error | 4 | 1917-146 and 1919-124 (both linked to *Towne v. Eisner*, a related but different case), 1935-104 (an earlier Georgia decree), 2003-090 (*ACLU v. Reno* 2000 instead of the 2003 decision) |
| not verified | 1 | 1950-031 (*Rogers*; the actor *Blau v. U.S.* cites the same 179 F.2d 559) |

So the measured `precision` (0.976) and `clean` (0.980) are lower bounds: about two thirds of the model's apparent
false positives are SCDB coding errors. The mapping was not changed (MAPPING.md); the key keeps SCDB's codes.

The same check was not possible in the other direction for all `NEG` misses (1,825 cases), but none of the 16 sampled
`NEG` misses was a source error.
