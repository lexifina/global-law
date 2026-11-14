# lean-in-testing film: where every on-screen fact comes from

Film: `video/lean_in_testing_film.html`, data `video/lean_in_testing_data.json`, built by
`python video/render_lean_in_testing.py --build-data`, which re-reads the files below and stops if a fact is missing or
disagrees with `eval/score_final.txt`. Round-4 final outputs only; `caselaw-lean-2/round5/` was not opened.

`C` = `~/Documents/us-caselaw-lean-work/caselaw-lean-2`, `L` = `lean-proofs/LegalProofs/CaseLaw2`,
`N` = `~/Documents/us-caselaw-lean-work/graph/nodes.tsv`. Line numbers are 1-based, as the files stood on 13 Nov 2026.

## Scene 1: a sentence goes in (2.5–8.5 s)

| On screen | Source |
|---|---|
| "Bowers v. Hardwick should be and now is overruled." | `C/data/treatments.tsv` line 28204, row `t:6218081:6102809:37764`, column 12 (quote); the same words at offset 400 of the window in `C/data/cert_text.tsv` line 39658 |
| Lawrence v. Texas; Bowers v. Hardwick, 478 U.S. 186 | `N` lines 6218082 and 6102810 (name, first citation) |
| Supreme Court | `C/data/decisions2.tsv` court of node 6218081 → `C/data/courts2.tsv` line 2703 ("Supreme Court of the United States") |
| 26 June 2003 | treatments row, column 4 (20030626) |
| majority opinion | treatments row, column 14 (part = majority) |
| kind overruled; characters 37,764–37,814; evidence name:Hardwick | treatments row, columns 5, 10–11, 13 |
| "What a reader claims · untrusted until Lean checks it" | `L/Certificate.lean` lines 7–10 ("the checker that admits untrusted rows"; "A treatment or history row from the reader is a claim. It is admitted only if its certificate passes every check") |

## Scenes 2 and 3: the certificate (8.5–22.5 s)

| On screen | Source |
|---|---|
| The ten reason codes and their order: shaUnknown, noWindow, windowHash, quoteMismatch, noCue, disqualified, targetUnresolved, partNotMajority, targetLater, noAuthority | `L/Certificate.lean` lines 231–244 (`def check`), read by the build script in that order; described in lines 12–27 |
| "The first failure is the row's reason code." | `L/Certificate.lean` line 10 |
| text hash 7f0d9d8f9bf1ee50c4c9a23870cd8eaec499c1d4 | treatments row, column 9 |
| window 37,364 to 38,214; quote span 37,764–37,814 | `C/data/cert_text.tsv` line 39658 (start0, end0); treatments columns 10–11 |
| window SHA-1 aec8dd9cbe726030269a6820c507f7a443a9ff2a, "Lean computes" = "audit copy" | `C/data/window_sha.tsv` line 166371 (recorded). The build script recomputes SHA-1 of the window text and gets the same digest; that Lean computes and compares it is `L/Certificate.lean` lines 160–165 (`hashOk`) and `checkCert_window_hash` (line 297) |
| cue word "overrul" | `L/CueTable.lean` line 12 (cues of `.overruled`); the first cue found in the quote |
| no disqualifier | `L/CueTable.lean` line 43 (`treatDisqualifiers`); none occurs in the quote (checked by the build script) |
| names its target "Hardwick" | treatments column 13 (`name:Hardwick`); name-token rule at `L/Certificate.lean` lines 223–225 |
| target is earlier, 1986 ≤ 2003; 30 June 1986 | `N` line 6102810 (19860630); treatments column 4 |
| court has the power | `L/Spec/Authority.lean` line 285 (`canChangeStatus`: the Supreme Court over a federal decision); the verdict itself is the next row |
| Admitted; certs.tsv: ok | `C/out/certs.tsv` line 185724 (`treatment  t:6218081:6102809:37764  ok  ok`) |
| "checkCert_sound: an admitted row satisfies every condition." | `L/Certificate.lean` lines 246–247 |

## Scene 4: a rejected row (22.5–29.5 s)

| On screen | Source |
|---|---|
| "This is the only element of the Tinker v. Colwell holding to be overruled." | `C/data/treatments.tsv` line 2051, row `t:280701:5952856:16930`, column 12; also at its offset in `C/data/cert_text.tsv` line 59370 |
| In re Friedenberg, 12 B.R. 901 | `N` line 280702 ("Citibank N. A. v. Friedenberg (In re Friedenberg)", shown by its short title) |
| US Bankruptcy Court, S.D.N.Y. | `C/data/courts2.tsv` line 160 ("United States Bankruptcy Court for the Southern District of New York"), abbreviated |
| 29 July 1981; majority opinion | treatments row, columns 4 and 14 |
| Tinker v. Colwell, 193 U.S. 473, Supreme Court, 1904 | `N` line 5952857; `C/data/courts2.tsv` line 2703 |
| nine checks pass, then noAuthority | `C/out/certs.tsv` line 138622 (`noAuthority  noAuthority`); the reason is the first failing check (`check`, lines 231–244), so the nine before it passed. The build script re-checks window, window hash, offset, cue, disqualifiers, part and dates |
| "A bankruptcy court has no power over a Supreme Court decision." | `L/Spec/Authority.lean` lines 279–306: no branch of `canChangeStatus` gives a lower federal court power over a Supreme Court decision (falls to `(false, .noPower)`) |

## Scene 5: the event becomes a status (29.5–36 s)

| On screen | Source |
|---|---|
| good law until 25 June 2003; overruled from 26 June 2003 | `C/out/status.tsv` lines 76628–76629 (node 6102809: `0 20030625 good`; `20030626 20261112 neg:overruled`, witness row `t:6218081:6102809:37764`) |
| the bar starts at 30 June 1986 and ends at 12 November 2026 | `N` line 6102810; `status.tsv` line 76629 column 5 (the run date) |
| "Lawrence v. Texas, admitted" | `status.tsv` line 76629, columns 9–10 (witness row, actor 6218081) |
| `#guard st 2 0 20030625 20030625 == .good` and `… 20030626 20030626 == .neg .overruled` | `L/Examples.lean` lines 165–166 (decisions 2 and 3 are `bowers` and `lawrence`, lines 88–89) |
| "re-checked on every build" | `C/TRUST.md` line 47 ("`#guard`, evaluated by the compiler at build time") |

## Scene 6: the order of events does not matter (36–42.5 s)

| On screen | Source |
|---|---|
| "status = the join of every admitted effect" | `L/Spec/Status.lean` lines 139–141 (`status`: the fold of `join` over the effects) |
| "join keeps the more severe of two" | `L/Spec/Status.lean` lines 60–61 |
| `theorem status_perm (h : l₁.Perm l₂) : status l₁ k t u = status l₂ k t u` | `L/Spec/Status.lean` lines 178–180 (the binders `{l₁ l₂ : List Effect}`, `(k : Nat) (t u : Date)` are left out on screen) |
| "Bowers has one admitted effect." | `C/data/treatments.tsv` has one row with target 6102809; `status.tsv` line 76629 |
| the three cards reviewPending, superseded, overruled and their severity dots | constructors of `Neg`, "least severe first", `L/Spec/Status.lean` lines 23–25. They illustrate the theorem on a list of three effects; they are not events on Bowers, and the subtitle says so |

## Scene 7: findings (42.5–49 s)

| On screen | Source |
|---|---|
| 178 citesOverruled findings | `C/out/findings.tsv`: 178 rows with finding = citesOverruled and cited = 6102809 (first at line 2988, last at line 184723), from 176 citing decisions |
| each dot's year | the citing decision's date in `C/data/decisions2.tsv` (streamed); all are after 26 June 2003 (first 29 August 2003, last 15 June 2020) |
| Summerlin v. Stewart 2003; Latta v. Otter 2014; Bostock v. Clayton County 2020 | three of those citing decisions; names from `N` |
| "a flag for the reader, not a claim of error" | `L/Spec/Findings.lean` lines 6–7 ("None is an error claim: they are counts of conditions a reader of the citing opinion would want flagged") |

## Scene 8: against lists the model never read (49–55 s)

| On screen | Source |
|---|---|
| Lawrence v. Texas overruled Bowers v. Hardwick, from 26 June 2003 | `certs.tsv` line 185724; `status.tsv` line 76629 |
| Supreme Court Database: usCite 539 U.S. 558, precedentAlteration 1 | `C/gold/scdb.tsv` line 27571 (caseId 2002-083) |
| Constitution Annotated table: Bowers v. Hardwick, 478 U.S. 186, overruled by Lawrence v. Texas, 539 U.S. 558 | `C/gold/crs_overruled.tsv` line 306 (in_current = 1) |
| "Both lists are kept for the test. The model does not read them." | `C/gold/README.md` line 1 ("evaluation only; never read by the reader or holdings agents"); `C/SCHEMA.md` line 60 |

## Scene 9: the whole list (55–62 s)

| On screen | Source |
|---|---|
| 278 squares, 141 found | `C/eval/score_final.txt` lines 130–131 (`flagged_decisions` 278, `flagged_with_admitted_overruling` 141). The squares are the 278 rows of `C/gold/scdb.tsv` with precedentAlteration = 1, in date order; each is green when the decision has an admitted overruling of a Supreme Court decision (rule of `tools/caselaw2/eval/score.py`, `score_scdb_crs`). The build script recomputes 278 / 141 / 152 and stops if they differ from `score_final.txt` |
| 141 of the 152 decisions the model names are on the list | `C/eval/score_final.txt` lines 133–134 |
| 1810, 2026 | dates of the first and last flagged rows of `C/gold/scdb.tsv` |
| the ringed square, Lawrence v. Texas | `C/gold/scdb.tsv` line 27571; found |

## Scene 10: checked three ways (62–69.5 s)

| On screen | Source |
|---|---|
| 141 theorems, checked by Lean's kernel | `C/TRUST.md` line 9 ("141 kernel-checked theorems"); `C/ROUND4.md` line 25 |
| 0 differences; an independent Python reference; 350,651 certificates, 398,482 status rows, 168,276 findings | `C/DIFFTEST.md` line 3 and line 629 (real data `real20`: certs 0/350,651, status 0/398,482, findings 0/168,276) |
| 27 of 27 broken rules caught | `C/LEAN.md` line 25 ("27 properties against 27 mutants, all killed"); `C/ROUND4.md` line 25 (141 / 27) |
| "a checker that accepts dissents" | `L/Mutants.lean` line 279 (M7 "cert accepts dissents"), caught by the property at line 99 |

## Left out because it could not be sourced

- "The target resolves to exactly one decision": this row's evidence is a name (`name:Hardwick`), which the checker
  tests as name tokens in the quote or window; the citation index is used only for `cite:` evidence. The film says
  "names its target".
- The rule id under which Lawrence has power over Bowers (the runner writes no rule id for it, and Lean was not run).
  The film says only "court has the power".
- A real decision with several admitted effects to shuffle: Bowers has one. The shuffle is shown on three constructors
  of `Neg` and labelled as an illustration of the theorem.
- The Supreme Court Database's own case name for Lawrence (it is the full party caption); the film shows its citation
  and flag instead.
