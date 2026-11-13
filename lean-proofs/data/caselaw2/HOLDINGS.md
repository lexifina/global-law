# Holdings, issues, Marks rows and circuit-split data (agent: holdings)

Written 2026-11-12. Scripts: `~\Documents\global-law-lean\lean-proofs\tools\caselaw2\holdings\`.
Working files: `data/holdings_work/` (raw model outputs, split windows, clusters, validation sets, verdicts).

## Files (SCHEMA)

| file | rows | notes |
|---|---|---|
| `issues.tsv` | 255,981 | 244k decision-local issues `d<node>.i<k>`; 11,996 split questions `usc:<title>:<section>(<sub>):q<n>` with a canonical yes/no `question`; Marks-only issues `d<node>.m<k>` |
| `holdings.tsv` | 260,054 | 243,258 decision holdings (ids `H<node>.<k>`), 16,796 split holdings (ids `S<node>.<usc>.<k>`, answer yes/no) |
| `marks.tsv` | 751 | 326 fragmented SCOTUS decisions; tag U (model reading, never a premise) |
| `holdings_cert_text.tsv` | one row per certificate window | text_sha, start0 = max(0, start−400), end0 = min(len, end+400), window = normalised text[start0:end0] |
| `holdings_reach.tsv` | extra (not in SCHEMA) | by_node, target_node, scope (all, issues:k1,k2 or partialUnknown), src, confidence: which target holdings a v1 overruling act reaches, for acts whose words limit their scope |

- **Quotes and certificates.**
  - Every quote is a sentence span cut by our splitter from the court's own opinion part. The model only picks a sentence number, so it never types a quote.
  - `assemble.py` re-reads every decision from git HEAD. It checks sha1(bytes) = text_sha, and that the quote equals normalised text[start:end] (\r\n→\n, tab/newline→space).
  - `check_certs.py` repeats the check independently, including each window against text[start0:end0]: 0 failures (see `holdings_work/check_certs.json`).
- **Roles.**
  - `part` = `role`. It is `majority` by default and `perCuriam` from the opinion heading or the courts agent's form.
  - It is `plurality` when decisions2.tsv or the syllabus line ("announced the judgment …") says plurality. Exception: the Marks reader lists that issue as joined by a majority (630 relabelled).
  - For Combined (CourtListener) texts, the opinion is cut at the first "…, dissenting/concurring" line.
- **target_evidence.** It is `cite:<title> U.S.C. § <sub>` when the quote names the section, else `name:-`. A holding has no target decision.
- **Domain.** It comes from the model's `law` field and the court's system: federalGeneral, federalPatent (title 35), federalTax (title 26), stateLaw:<system>. It is `unknown` for state law read in federal courts (Erie).

## What was read (coverage)

| stream | decisions | read | gaps |
|---|---|---|---|
| SCOTUS full opinions (opinion text ≥ 1,000 chars) | 30,286 | 28,952 | 1,265 had under 600 chars of opinion text after removing head matter; 69 were blocked by the Azure content filter |
| Treatment decisions: both sides of every v1 act (`events_v3/acts.tsv`), minus 2,266 acts where a lower court "overrules" SCOTUS | 44,229 (+368 that are SCOTUS full opinions) | 43,537 | 485 had no opinion text; 145 were blocked by the content filter; 62 were unfinished when the final was written (gpt-6-luna stragglers) |
| Split citations: (subsection, court of appeals or SCOTUS decision) | 12,823 | 12,823 | 4 of 297 subsections could not be clustered (content filter) |

- **Models.**
  - gpt-5.4-mini read 187,893 decision holdings and all split extractions.
  - gpt-6-luna read 55,365 decision holdings: half of the SCOTUS and treat queues after 17:38. The `reader` column says which model read each row.
  - gpt-6.1-sol did the clustering, the second reading of split holdings, and Marks.
- **Holdings yield.** 78,617 decisions have ≥ 1 holding; the mean is 3.3 per decision.
- **Treatments.**
  - The reader's `treatments.tsv` did not exist when this ran, so the treatment set is v1 acts only. Rerunning `extract_holdings.py` on new targets plus `reach.py --treatments` extends it.
  - Decisions in acts whose words limit scope ("to the extent", "in part", "on other grounds", …) were read first.
- **Marks.**
  - 555 SCOTUS decisions were flagged as fragmented: decisions2 plurality, or a syllabus "announced the judgment" / "delivered an opinion in which" line.
  - 326 have Marks rows. The rest had a majority on every issue, or no narrowest ground was found.
  - Rows with no logical-subset narrowest ground start "[no common denominator: result only]".

## Method

1. **Holdings** (`extract_holdings.py`).
   - Sentences of the court's own opinion are split with offsets.
   - A cue score (we hold/conclude/think, accordingly, plain meaning, …; citation strings dropped) picks 14 candidates, or 16 for SCOTUS, plus up to 3 "question presented" context sentences.
   - The model returns holdings by sentence id with issue label, proposition (≤ 300 chars), kind (holding, alternative or application), law, usc and confidence.
   - Dropped: confidence < 0.5, bare dispositions, non-candidate ids.
2. **Splits** (`splits_select.py` → `splits_windows.py` → `splits_extract.py` → `splits_cluster.py` → `split_verify.py`).
   - The 300 subsections are the most-cited by courts-of-appeals decisions since 1995 in `rows_out.tsv` (18:3553(a) … 234 decisions at rank 300).
   - For each of 441,943 (subsection, decision) pairs: mentions in the court's part, a ±4-sentence window, and an interpretive-cue score (meaning, construe, plain language, lenity, sister circuits, split, …). Unpublished decisions are penalised.
   - Up to 40 courts-of-appeals decisions per subsection are taken round-robin across circuits, plus 12 SCOTUS decisions.
   - gpt-5.4-mini says whether the court interprets the subsection, and gives yes/no questions with answers. 80% of the chosen decisions were judged interpretive.
   - gpt-6.1-sol clusters each subsection's questions into canonical questions with polarity, so circuits line up on one issue_key.
   - gpt-6.1-sol then reads every split holding on an issue that ≥ 2 courts answered, in its ±400-char window. It rejected 2,955 of 8,214 (not this court's holding on that question) and corrected 103 answers.
3. **Split candidates** (`splits_report.py` → `holdings_work/split_candidates.tsv`).
   - A candidate is two different circuits whose latest published holdings on the issue_key give opposite answers at some date, with confidence ≥ 0.6.
   - Lean's own test (neither binds the other, both good law on the date) is decided by the runner. This is the data-side count.
4. **Reach** (`reach.py`). For 13,638 acts with limiting words, gpt-5.4-mini maps the act's window onto the target's numbered holdings.
   - `holdings_reach.tsv` has 13,629 rows: 8,546 name specific issue keys (12,959 keys, all present in issues.tsv), 400 reach the whole decision, and 4,683 are limited but match no listed holding (`partialUnknown`).
   - These rows are not audited.

## Results

- **Split candidates: 190**, over 11,996 canonical questions on 293 subsections.
- **Resolved later by SCOTUS: 27.** SCOTUS answered the same issue_key after the split began.
- **Three examples:**
  1. **42 U.S.C. § 1997e(a):** does "prison conditions" cover particular incidents such as excessive force?
     - Yes: *Booth v. Churner*, 206 F.3d 289 (3d Cir. 2000).
     - No: *Nussle v. Willette*, 224 F.3d 95 (2d Cir. 2000).
     - Resolved yes by *Porter v. Nussle*, 534 U.S. 516 (2002), which our SCOTUS row answers yes on the same issue_key.
  2. **31 U.S.C. § 3730(b)(5):** does the first-to-file bar cease once the earlier action is no longer pending?
     - Yes: *U.S. ex rel. Chovanec v. Apria Healthcare*, 606 F.3d 361 (7th Cir. 2010).
     - No: *United States v. Cellco P'ship*, 748 F.3d 338 (D.C. Cir. 2014).
     - Resolved yes by *Kellogg Brown & Root Servs. v. U.S. ex rel. Carter*, 575 U.S. 650 (2015).
  3. **28 U.S.C. § 2255(e):** does the saving clause allow § 2241 challenges to sentences, not only convictions?
     - Yes: *Webster v. Daniels*, 784 F.3d 1123 (7th Cir. 2015 en banc), and the 4th and 9th Circuits.
     - No: *Reminsky v. United States*, 523 F. App'x 327 (6th Cir. 2013; unpublished, so the published-only Lean test may not count that side).
     - Jones v. Hendrix (2023) is not in the selected SCOTUS set, so it shows as unresolved here.

## Validation (blind; judges saw only the text window and the claim, not the model, confidence or group)

Judges were Claude subagents reading `holdings_work/val/*.md`. Verdicts are in `val/judged_*.jsonl` and scores in `val/scores.json`. Intervals are Wilson 95%.

| measure | result | 95% CI |
|---|---|---|
| Holdings, is a holding (not dicta) | 50/60 = 0.83 | 0.72–0.91 |
| Holdings, proposition faithful | 49/60 = 0.82 | 0.70–0.89 |
| Holdings, both | 43/60 = 0.72 | 0.59–0.82 |
| — SCOTUS | 20/24 = 0.83 | 0.64–0.93 |
| — treatment decisions | 19/24 = 0.79 | 0.60–0.91 |
| — split holdings before second reading | 4/12 = 0.33 | 0.14–0.61 |
| Split pairs before second reading: genuine split (same question, opposite, both holdings) | 11/30 = 0.37 | 0.22–0.55 |
| **Split pairs after second reading (final data): same question** | 27/30 = 0.90 | 0.74–0.97 |
| **… same question and opposite answers** | 25/30 = 0.83 | 0.66–0.93 |
| **… genuine split (also both are holdings)** | 21/30 = 0.70 | 0.52–0.83 |

- **Split holdings and the second reading.** Of the 12 split holdings judged before the second reading:
  - the verifier rejected 4, and all 4 had failed;
  - the 8 it kept passed in 4 of 8.
  - So split holdings that are not on a split pair are still noisy. Use them for split detection only together with `confidence`.
- **Two "genuine" pairs share a circuit.** In the verified 30, 2 genuine pairs were within one circuit, from the validation sampler's choice of example. `splits_report.py` now picks different circuits.
- **Known-split cases in the verified 30:** Booth/Nussle; the 3d vs 11th Cir. FTCA proviso for TSOs; 2255(e); first-to-file; 1252(d) issue exhaustion; 924(c) multiple convictions; 3553(f) MDLEA.
- **Recall of the split detector against SCOTUS-resolved splits.**
  - **Gold:** SCOTUS decisions in the 300 subsections that say they resolve a conflict among the courts of appeals. There are 302 conflict questions, each clustered onto an issue_key.
  - Where ≥ 2 circuits in our data had ruled on that issue_key before the SCOTUS decision, the detector found opposite answers in **20/51 = 0.39 (0.27–0.53)**.
  - Over all 302 it is 20/302 = 0.07 (0.04–0.10). Most misses are coverage: only 40 decisions per subsection were read, rows_out starts in 1995, and the split may have been on a narrower question.
- **Not validated:** gpt-6-luna holdings (55,365 rows) were not in the blind sample, which was drawn before luna started, and Marks rows and reach rows were not audited. Treat luna rows' precision as unmeasured.

## Tokens and cost

- **Tokens: 163.5M in total**, over the 150M budget by 9%. The coordinator asked for maximum speed, which added the gpt-6-luna stream.
  - gpt-5.4-mini: 101.1M.
  - gpt-6-luna: 52.5M (reasoning tokens make it about 2× mini per call).
  - gpt-6.1-sol: 9.8M.
- **Cost about $346 at assumed list prices** (see `holdings_usage.json` for the prices used). gpt-6-luna is priced as mini there, because its price was unknown.
- Usage is logged per call to `holdings_usage.jsonl`. About 35 lines were lost to interleaved writes from parallel processes, an undercount of under 0.1%.

## Gaps

- 62 treatment decisions are unfinished, and 214 decisions plus 4 split subsections are blocked by the Azure content filter (mostly sexual-offence and violent-crime texts).
- The reader's `treatments.tsv` is not yet joined (v1 acts only). Holdings of new targets need one more `extract_holdings.py` pass.
- Plurality vs majority is per decision, refined only by the Marks reader's majority_issues. "Opinion of the Court with respect to Parts …" decisions are majority unless the Marks reader said otherwise.
- Split coverage is bounded: 300 subsections and ≤ 40 circuit decisions each, chosen by cue score, from 1995 on.
- Issue labels of decision-local holdings are not clustered across decisions. Only split questions share issue_keys across courts.
- Validation used n = 60 and n = 30, so intervals are wide.

## Round 2 additions (agent: splits, 2026-11-12)

Log: `round2/splits.md`. Scripts: `tools/caselaw2/holdings/round2/`. Reader: Claude subagents (`claude-subagent`).

- **Supreme Court resolution links: 62 holdings** under existing split-question keys (ids `S<node>.<usc>.r[n]`).
  - Candidates: Supreme Court opinions after the earliest side that cite the question's US Code section or a side decision; cut by word overlap with the decision's recorded holdings; screened, then read in the opinion text from git.
  - The reader picks a sentence id; the quote is cut by offset. Syllabus sentences are excluded (`syl.py`).
  - List: `round2/splits_resolved_links.tsv`. 60 of 332 as-of split rows (26 questions) are resolved by them.
- **New split questions: 115** (`usc:<usc>:x<n>`, src `splits2:claude-subagent`) with 233 holdings (ids `S<node>.<usc>.x<n>`).
  - Source: reader treatments where a court of appeals declines to follow another circuit's decision, with a US Code cite near the quote (327 pairs read, 118 accepted).
- **Blind validation:** links 36/37 = 0.97 (0.86–0.995); new split pairs 42/42 (0.92–1.0; decoys were easy). The 26 links on the new questions were not audited.
- **Certificates:** same columns and windows as `assemble.py`. Hash rows for the new windows are in `window_sha.splits_round2.tsv`; they must be merged into `window_sha.tsv` (or `window_sha.py` rerun) for the rows to be admitted.
- No issue key was renamed or merged. Backups: `*.pre_round2.tsv`.
