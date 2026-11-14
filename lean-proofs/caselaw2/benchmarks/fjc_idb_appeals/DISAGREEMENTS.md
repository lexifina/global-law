# Disagreements read (round6 `final2`, primary population)

Sample: 30 cases drawn with seed 20261113 from the round6 per-case file, primary (`cited`) population only. 18 are
misses: IDB says `NEG` (OUTCOME 2), the model is not `NEG_HIST`, from 2,830 such cases. 12 are false positives: IDB
says `CLEAN` (OUTCOME 1), the model is `NEG_HIST`, from 119 such cases. Both halves are mixed in the sample, and
nothing was tuned afterwards.

Three Claude sub-agents read the corpus texts (`r6lib.py text`) of the appellate opinion, the district decision and
the model's actor. I re-checked the four `source_wrong` quotes against the texts myself. Per-case verdicts with
quotes and IDB fields are in `work/disagree/verdicts_all.tsv`; the sample is in `work/disagree/sample.tsv`.

## Counts

| cause | misses (18) | false positives (12) | all (30) |
|---|---|---|---|
| model missing | 11 | – | 11 |
| model wrong | 3 | 6 | 9 |
| source wrong (IDB code) | 1 | 3 | 4 |
| link error | 2 | 1 | 3 |
| mapping artefact | 1 | 2 | 3 |

## Misses

- **Model missing (11): 1, 4, 5, 6, 7, 8, 9, 10, 13, 16, 17.** In each case the appellate opinion plainly reverses
  or vacates the linked ruling. Examples:
  - #5: "Its judgment must be reversed and the case remanded with directions to dismiss the complaint. REVERSED AND
    REMANDED." (306428).
  - #7: "We REVERSE the district court's grant of summary judgment and REMAND" (375362).
  - #17: "we will vacate its order, remand the case to the District Court" (721209).

  The model has no history row for most of these. The text-wide diagnostic agrees: 2,389 of the 2,830 primary misses
  have no history row of any kind targeting the district decision, even though the appellate opinion cites it. Two
  cases suggest causes:
  - #8: the caption changed (Loftus → Acevedo).
  - #9: the reversal came in an opinion issued after a certified question.
- **Model wrong (3): 2, 12, 14.** The model has the right history row but puts the decision in `UNK_HIST`
  (partial scope) when the whole decision was reversed or vacated:
  - #12: "The decision of the district court is VACATED and Appellant's appeal is DISMISSED."
  - #14: "dismissed all counts … We reverse."
  - #2: the linked decision is a downward-departure order that was reversed in full. The opinion as a whole reads
    "AFFIRMED in part; REVERSED … in part".

  The lenient recall (`recall_lenient`, 55.2%) counts these.
- **Source wrong (1): 11**, Rhode Island v. Narragansett. IDB has OUTCOME 2, but the opinion says "The district
  court's issuance of a mandatory injunction … is affirmed. The declaratory judgment … shall, however, be modified".
- **Link error (2): 3, 15.** The docket is right but the published ruling is not the one the appeal disturbed:
  - #15: "The district court's pre-trial denial of the motion to dismiss … was correct"; what was reversed was the
    later JNOV ruling.
  - #3: the vacated-in-part ruling is an unpublished later punitive-damages ruling.
- **Mapping artefact (1): 0**, Cheeseman v. Carey. Reversed with directions to dismiss on the merits. The district
  court had dismissed on abstention, so the outcome for the plaintiffs is the same and only the ground changed.

## False positives

- **Model wrong (6): 20, 21, 22, 23, 26, 27.**
  - #22: bad extraction. The actor's opinion ends "Affirmed."
  - #26: reversal credited to a citing case. The actor reversed a Tax Court decision in another case. The linked
    appeal says "We affirm on the basis of the well-reasoned opinion of the district court".
  - #21: reversal of a later jury verdict credited to the earlier pleadings ruling.
  - #23: a partial vacatur applied to the part that was affirmed: "affirmed insofar as it dismisses Pickett's suit
    but vacated insofar as it dismisses the counterclaim".
  - #27: a panel vacatur that was itself vacated on rehearing en banc. The en banc court ends "Affirmed."
  - #20 (Dukes v. Wal-Mart): the actor (Ninth Circuit panel) affirmed. The Supreme Court did later undo the
    certification, but the model's row does not point to that.
- **Source wrong (3): 18, 24, 25.** IDB has OUTCOME 1 (affirmed), but the opinions say:
  - #18: "Reversed, and remanded" (Beth Israel Hospital v. Heckler, 734 F.2d 90).
  - #24: "REVERSED AND REMANDED" (Wren v. Jones, 635 F.2d 1277).
  - #25: "Affirmed in part, reversed in part, and remanded" (Pariser, 816 F.2d 1248). For #25 the model's full
    `NEG_HIST` also overstates.
- **Link error (1): 28** (Bernard v. Gulf Oil). The IDB record is the third appeal, from the judgment after remand.
  The linked 643 F.Supp. 1494 was reviewed by an earlier appeal, so the date-window rule did not exclude it.
- **Mapping artefact (2): 19, 29.**
  - #19: IDB recorded the first affirmance. The Supreme Court then "vacated our judgment", and on remand "the
    decision of the district court is reversed". The model is right as of today.
  - #29: one district decision decided two prisoners' petitions. The IDB record is Parker's appeal (affirmed), while
    Pierce's grant was reversed.

## What this says about the figures

- Recall is limited mainly by the model, not the key. In 11 of 18 misses the reversal is plainly in a corpus
  opinion that cites the decision, and 3 more are a scope labelling problem. A rough read: of the 2,830 primary
  misses, perhaps three quarters are true model misses. The sample is small; this is not a corrected estimate.
- IDB's own coding error rate is visible: 4 of 30 disagreements, 3 of 12 false positives. Precision against IDB
  (89.3%) is therefore a lower bound. Of the 12 false positives, 3 are IDB errors and 2 are later same-case events.
- The docket link is sound at the district-docket level. Its weakness is several published rulings in one docket
  across successive appeals (3 of 30).
