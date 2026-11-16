# Next steps, and how to start a round

Written on 16 November 2026, after round 13. Use this file as the starting point for further work on the case-law
model: it gives the state of the work, the open questions, the plan for round 14, and the working rules that kept the
scores honest.

## Where things stand

- The model is the frozen round-13 build `v13a`:
  - 305 theorems with locked statements (`audit/statements.lock`);
  - 89 mutants, each caught by the properties;
  - 0 disagreements with the Python reference.
- Its outputs are in `../data/caselaw2/out_v13a/`, and the scores on the twelve blind answer keys are in
  `README.md` ("Rounds 5 to 13"). The scores of every build are in `benchmarks/graph/rows.tsv`.
- Precision is high on every key: 89–97% on the database keys, 75% on the unopened overruling lists. Recall is the
  weak side. A decision is marked bad only with a certificate: the quoted words of a court with power, tied to that
  decision. The main reasons for misses:
  - no citation links the later ruling to the decision;
  - no caption tie between the two;
  - the overruling was never announced;
  - the later ruling is not in the corpus.

## Open questions (decide before building on them)

1. **Reinstated decisions.** 38 decisions from 2005 were vacated and then reinstated by their circuit. What status
   should they have after reinstatement? This is a question about the meaning of status, not a linking problem.
2. **46 unlinked 2005 Supreme Court list entries.** No principled name-form rule was found: relaxing middle names and
   hyphens scored 0.69 on the development half.
3. **139 identity lines** of DESIGN §5.2, held since round 11.
4. **47 Supreme Court orders dated January–June 2026** (October Term 2025): they are still in the build.
5. **Data hygiene:**
   - 41 Federal Circuit rows marked "affirmed" that are wrong;
   - one CCPA decision held twice (nodes 2044572 and 1927432);
   - 16 non-strict ties in the U2 linker.
6. **Court attribution for New Jersey,** and the overlap between the Songer and Shepardized keys.
7. **Lindquist's state supreme court data** sits behind an "I agree" click-through (`benchmarks/lindquist/SOURCE.md`).
   It has not been used. Using it needs someone with authority to accept those terms.
8. **Three classes installed below the audit bar** in round 13 (state T4, SCDB R2 v3, en banc EB12 v6), on an
   explicit decision. They are marked as such in `round13/ROUND13.md`. Keep them separate in any write-up.

## Round 14 plan (not started)

**Goal:** raise recall by linking decisions from the opinion text alone, and add a separate "probably overruled"
tier.

**Out of scope:** court dockets from CourtListener, PACER or any other outside record of the judgment. The answer keys
are compiled from those records, so linking through them would score the model against its own input. Every link
must come from the text of the opinions in the corpus.

### Track A: the "which ruling" reader (FJC appeals, Songer, unpublished FJC)

- **Gap:** 1,495 of the 2,832 FJC development-half misses never cite the district decision.
- **Rule:**
  1. Read the appeals opinion's head line, "Appeal from the United States District Court for …, No. X": the docket
     number and court, and sometimes the judge and the date of the order appealed.
  2. Match it to the district decisions in the corpus with that court and docket number. The district docket index
     built for the FJC key (`benchmarks/fjc_idb_appeals/link.py`) comes from the corpus's own docket lines and can be
     reused.
  3. If the docket has several rulings, choose the last one dated before the appeal that decides what the appeal is
     about: the final judgment for a merits appeal, or the order named in an interlocutory appeal.
  4. If more than one candidate remains, make no link.
- **Certificate:** both quotes (the head line and the district decision's caption or docket line), plus the appellate
  judgment words.
- **Lean:** a new link kind with its own guard, and theorems that a docket link never crosses courts and never points
  forward in time.
- **First step:** count how many FJC and Songer misses have a head line at all. The Federal Circuit has almost none,
  so it is left out.

### Track B: docket links for en banc and the Shadow Docket

- **B1, en banc.** Extend EB12 to:
  - cases where the en banc opinion carries the panel's docket number but does not cite the panel decision;
  - re-selecting the next opinion when the docket's latest node is the grant order (about 55 pairs).
- **B2, Shadow Docket.**
  1. Start with a diagnostic on the roughly 3,200 orders with no natural-person caption side. Count how many lower
     decisions lack a docket number, against how many have one but fail the caption tie.
  2. For the second group only: link on lower court, lower docket number and decision date, with no caption tie, if
     exactly one corpus decision fits.

### Track C: a "probably overruled" tier

This tier is reported separately. It never enters the certified tier or the theorems.

- **Signals:**
  - the model's existing "at risk" finding;
  - rejection wording by a court with power ("rejected", "cannot survive", "abrogated", "no longer good law",
    "repudiated") with the decision named in the same passage;
  - a later court saying the decision was overruled, even when that court has no power over it.
- **Scores:** two for every overruling key, "certified" (unchanged) and "certified or probable". The second gets its
  own precision from a blind audit of the probable rows.
- **Lean:** the tier is data only, with a theorem that a probable row never changes a holding's status.
- **Caveat:** the third signal uses later courts' notes, which today form the held-out notes key. Split those notes by
  hash first, use only one half as a signal, keep the other half as the blind test, and report the smaller key.

### Order of work, and how to keep it cheap

| Step | What |
|---|---|
| 1 | Diagnostics: head-line count (A), docket coverage for the Shadow leftovers (B2) |
| 2 | B1 and B2 |
| 3 | C |
| 4 | A |
| 5 | Freeze, Lean check, Python reference, sealed run, fold the scores, redraw the figure |

**How to keep it cheap:**
- Develop on the candidates only, not the whole corpus. Read only the first ~2 KB of an appeals opinion for the head
  line.
- Prefilter files with ripgrep before Python opens them.
- Each track starts with its diagnostic. Stop a track whose ceiling is under about one point on its key.
- Stage only new or changed rows (hard links to the previous build), and rebuild Lean once at the end.
- During development, score only the keys that moved.
- After the freeze, run the frozen rules once over the whole corpus, so no rule is judged only on its own candidates.

## How a round runs

This is the protocol of rounds 5–13. `benchmarks/CONTRACT.md` is the binding version for the answer keys.

1. **Design first.** Write `roundN/DESIGNn.md`: each rule, the classes it adds, what it must never do.
2. **Build on development halves only.** Every key is split by hash into `h0` (development) and `h1` (sealed), and
   model-building work never opens the sealed half. Agents that build the model do not read `benchmarks/` beyond
   `graph/`.
3. **Audit before admission.** A rule enters the certified tier only after a blind audit of a fresh sample scores
   0.90 or better (Wilson interval reported). Earlier audit samples are excluded by identity. Decoys are mixed in.
4. **Self-test.** With no new rows, the round's tools must reproduce the previous frozen build byte for byte.
5. **Freeze.** Hash every file of the build into `FREEZE.md` before any sealed score.
6. **Check:**
   - `lake build LegalProofs.CaseLaw2`;
   - `python3 caselaw2/audit/audit.py check` (statement lock, no `sorry`, `axiom` or `native_decide`);
   - the Python reference (`tools/caselaw2/ref/precedent_ref.py`) with 0 disagreements in every table.
7. **Sealed run once,** logged in `SEALED_LOG.md`. Nothing is re-tuned afterwards.
8. **Write up** in `ROUNDn.md`: scores before and after with n, what moved and why, what was left.

**Working layout.** The round scripts expect a working folder `~/Documents/us-caselaw-lean-work/caselaw-lean-2/`
beside the global-law clone, with the bulk tables in `data/` and each round's staging in `roundN/stage/`. Rebuild the
bulk tables from the corpus first (`README.md`, "What is not in the repository"). On Windows machines where
Application Control blocks `lean.exe`, run Lean under WSL (`README.md`, "Build and run").

**Keep the working folder out of git except what cannot be rebuilt:**
- code, notes, audits and agent readings, answer keys, scores, the latest frozen build.

**Ignore:**
- caches (`work/`, `*_work/`, `cache/`);
- staging and reference mirrors (`stage/`, `ref/`, `snap*/`, `base_*/`);
- earlier rounds' frozen outputs;
- candidate scans (`*.jsonl.gz`, `scan/`);
- per-case scoring rows (`*.cases.tsv`);
- downloaded datasets (`raw/`);
- `.lake/`.

A full round of working files runs to tens of gigabytes. The part worth keeping was about 2 GB after round 13.

Publishing a round: [PUBLISHING.md](PUBLISHING.md).
