# DISAGREEMENTS — state overruled tables (round6; round4 gives the same outcome on every case)

Sample: 32 cases where the model does not show the listed pair (`results/round6.cases.tsv`, outcome `nothing` or
`other_actor`), chosen by a fixed hash per table (12 Georgia, 6 Greenleaf, 5 Desty, 4 Benjamin, 3 Labatt) plus the two
`other_actor` cases (`scripts/disagree_sample.py`, `scripts/disagree_window.py`; outputs `work/disagree_round6*.txt`).
For each, the overruling decision's corpus text was read around its mention of the overruled decision. Two sampled
cases (Rose v. Himely / Hudson v. Guestier, Sands' Case / Lucas v. Morris) turned out to be federal pairs; this led to
the `federal_court` pair check in `scripts/link.py` (33 rows dropped from the state key, scores re-run) and they are
not counted below. That leaves **30 classified**.

| Cause | n | Cases |
|---|---|---|
| **model missing** — the overruling decision says so (explicitly) | 9 | Carter v. Howell (39 Ga. 658: "we think that decision is overruled by the case of Parker vs. Beeman"); Dobbs v. State (22 Ga. App. 797: "Any holding in Dobbs v. State ... is, on review thereof, overruled"); Overstreet v. Sullivan, Smith v. McWhorter, Seaboard A. L. Ry. v. Simmerville (all three in 148 Ga. 376: "are overruled in so far as they hold ..."); Judge v. State (115 Ga. 222: "the decision in the Judge case is distinctly disapproved"); Rhodes Furniture v. Jenkins (18 Ga. App. 578, on rehearing: "is, on review, expressly overruled"); McFarlin v. Breves (18 Ga. App. 705: "hereby expressly overruled"); Burgoyne v. Supervisors (34 Cal. 520, a review of the line: "the very erroneous conclusion ... was due to the rule in Burgoyne's Case") |
| **model missing** — rejection without the word (implicit but plain) | 7 | Toothaker v. Cornwall (8 Cal. 626: "in direct conflict with the law"); Howe v. Scannell (23 Cal. 444: "We think the exception thus made is not sustained by the authorities"); Glidden v. Lucas (19 Cal. 64 rejects the "technical factor" limitation); People v. Whitman (8 Cal. 412: the earlier decision "was predicated upon" a misprint); Payne v. Treadwell (16 Cal. 220, same case on a later appeal: "the opinion cannot be sustained"); Ford & Pruett v. Thomason (143 Ga. 30: Court of Appeals rulings "not binding upon the Supreme Court", dismissal "erroneous"); Branch v. Levy (104 N.Y. 394: "We do not believe ... that the rule goes to any such length") |
| **source wrong** (table overstates or misattributes) | 9 | Watson v. Bourne, Tappen v. Kain, Suydam v. Keys, Shepherd v. Watson (Greenleaf: Y treats X as dictum / limits / doubts / lists it "pro and con"); Griswold v. Sharpe (Desty: Y distinguishes it by a statute change); Sharp v. State (Georgia: reasoning criticised, result "may be sustained on another ground"); Williams v. Williams (Benjamin: Y says "not followed in the extent to which it went", "yet most undoubted authority"); Reynolds v. West (Labatt: Y describes X approvingly; probable); Latourette v. Clark (Benjamin names 130 N.Y. 436, which follows Burdick v. Freeman, 120 N.Y. 420 — the model's actor: "must be regarded as overruled") |
| **mapping artefact** | 3 | Kane v. Sanger (19 Abb. N. Cas. 123 reports that X's dictum "has been overruled in the above cases" — Y is a reporter of other overrulings); McKnight v. Kellett (the linked Y, 20 Ga. 531, applies the earlier overruling in 14 Ga. 318, which failed the link check); Salter v. Weiner (18 Abb. N. Cas. 310 reports that X was reversed by the general term — same-case history, not overruling) |
| **link error** | 1 | Pitts v. McWhorter, 3 Ga. 5: Y (23 Ga. 82) discusses "Pitts vs. Bullard, 3 Kelly, 17"; the name check passed on "McWhorter", but the table's case is probably the one at 3 Kelly 17 |
| **model wrong** | 0 | |
| **OCR error** | 0 in this sample | (OCR errors found elsewhere: `source_errors.tsv` rows r00627, r01338, r01575) |
| **not determined** | 1 | Carlisle v. Callahan (78 Ga. 320): the model has it `unknown:partialScope` by a 1945 decision; the window read in 112 Ga. 923 describes X but the overruling sentence was not found in the part read |

## What this says

- Of 30 read, **16 are real model misses** (9 explicit, 7 implicit). All 16 are overruling statements the round-6 reader
  could have read; the 9 explicit ones use forms the reader's patterns apparently do not catch: a list of several
  overruled cases in one sentence ("The rulings in A, B, and C ... are overruled in so far as"), "is overruled by the
  case of Y" (a third case as overruler), "Any holding in X which may be contrary ... is overruled", "distinctly
  disapproved", and rehearing sections.
- **10 of 30 are the table's fault** (9 source wrong + 1 not a real overruling relation, Salter) — old compilers used
  "overruled" broadly (doubted, limited, dictum disposed of). Greenleaf 1838 is the loosest: 4 of its 4 sampled
  in-key misses were overstatements.
- Recall here is therefore a lower bound on the model's miss rate for **explicit** overrulings and an upper bound
  on the share of table rows that are true overrulings.
- The model's only disagreement on actor (Latourette v. Clark) is a source attribution error, not a model error.
