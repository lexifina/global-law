### Running Congress's amending instructions

An Act of Congress does not print the new law. It gives instructions: "Section 2243(c) of title 18 is amended in
paragraph (1) by striking '(1) In a' and inserting 'In a'". The Law Revision Counsel carries them out by hand to keep
the Code. Each instruction is a small program, so we ran them.

GovInfo publishes every public law since 2013 in USLM, an XML that marks each amending instruction and the words it
quotes. That covers 812 laws, the 113th Congress to the 119th, every law the record credits with a change in those
years. Older laws are not published that way, so they are left out. A parser built for the US Code record read
48,762 instructions in them, 50,010 operations once an instruction such as "by striking 'X' and inserting 'Y'; and by
adding at the end" is split.

A third Lean model treats striking and inserting as a function on a provision's words. Lean proves three facts about
it:

- If the struck words occur once in the provision named, the result is fixed.
- If they do not occur, the instruction does nothing. This is the same rule as the failed amendments in our earlier
  model of German law.
- If they occur twice and the instruction does not say "each place it appears", there are two possible results.
  Lean proves the two differ whenever the new words begin differently from the old ones.

The Python side only reads the Acts and the record. For each law and section it gives Lean the section as it stood the
day before, as lines labelled "(c)(1)(A)", and that law's instructions in order. Lean carries them out one by one and
classifies each. It then checks whether the record's next version shows the edit.

#### What happened

We counted the 39,666 operations on sections where the record credits the law with a change, in 11,294 pairs of law
and section. The rest hit a whole chapter, a section the record does not hold, or a section the record changes only
in a later edition.

| Outcome (Lean) | Operations | Share |
|---|---:|---:|
| Carried out, and the record shows the edit | 30,325 | 76.5% |
| Carried out, but the record reads differently there | 3,709 | 9.4% |
| The provision named is not in the section | 1,582 | 4.0% |
| The struck words are nowhere in the section | 1,198 | 3.0% |
| The words occur more than once, and the instruction does not say where | 404 | 1.0% |
| The words are in the section, but not in the provision named | 260 | 0.7% |
| A form the model does not cover (whole-section repeal, sentence rewrites, unparsed) | 2,083 | 5.3% |
| Carried out, nothing to compare | 105 | 0.3% |

Replaying all of a law's instructions on a section gives exactly the record's next version in 6,075 of the 11,294
pairs (54%).

The Code itself is the law in 27 of its titles. In the rest it is an editor's arrangement of the Acts. That split
shows. In the 27 titles, 83.5% of operations go through and match the record, and 1.2% cannot find their words. In
the others the figures are 72.1% and 4.1%.

#### What the failures are

We drew 20 operations from each class and read the Act and the record for each.

- **Carried out and matching:** all 40 we read, in two rounds, were right.
- **Record reads differently:** 12 of 20 are real. Ten are the Code's editorial style: "the date of enactment of this
  Act" printed as "September 22, 2023", or an Act's section number printed as a section "of this title". Two are gaps
  in our record. The other 8 are our check failing.
- **Words not found:** 18 of 20 are real, but 16 of those are the same editorial style. The Act strikes "section 6",
  and the Code prints "section 2605 of this title". One is a drafting error, and one is a gap in the record.
- **Wrong provision:** 9 of 20 are real. Six are drafting errors. The rest are our parser.
- **More than one place:** 7 of 20 are real drafting ambiguities. In each, the record and the Law Revision Counsel
  took the reading the context points to. The rest are our parser missing words such as "after the semicolon".
- **Provision not found:** 4 of 20 are real, 2 of them drafting errors. Most are our parser losing track of an
  earlier redesignation.

Scaled up, roughly 440 of the operations are drafting errors that cannot be carried out as written. Because the
samples are small, the true number could be anywhere from about 170 to 1,100.

The Law Revision Counsel's notes give an independent check. For 86 pairs of law and section in our run, the notes in
the 2023 and 2024 editions say an amendment "could not be executed". Lean flags a failure in 69 of them (80%).

Some examples, each checked against the Act and the note:

- Two sections of the National Defense Authorization Act for 2021 both strike "and" at the end of 6 U.S.C.
  § 652(c)(10). A law enacted five days earlier had already removed it. Lean: the words are not where named. The note:
  "could not be executed".
- Two appropriations Acts, of January and December 2014, make the same change to 49 U.S.C. § 47124(b)(3). A 2011 law had already
  rewritten the words. Lean: not found, both times. The note: "could not be executed because of the prior amendment".
- The 2022 Violence Against Women Act's §1202 renames § 2243(c) of title 18 as (d) and inserts a new (c). Its
  §1312 then amends "section 2243(c)", paragraph (1). The new (c) has no paragraph (1). The Code applied it to (d),
  "to reflect the probable intent of Congress".
- In 22 U.S.C. § 9303, the defense authorization Act for 2023 renumbers paragraphs and then amends "paragraph (7), as redesignated". The
  words are in (8).
- In 10 U.S.C. § 115(d), a 2021 instruction targets "the third sentence". The words are in the fourth.

#### What a bill would change

The same parser reads bills. A bill in GPO's bill format translated to USLM gives the same instructions as the law it
became. We tested this on the Bipartisan Safer Communities Act, where 61 of 62 instructions are identical and the other
differs only in a heading's punctuation. We took five bills of the 119th Congress that amend heavily cited sections and
ran their instructions on the Code as it stood on 3 November 2026. All 30 operations go through cleanly. The only ones
not run are two that add a new section to a chapter. For each target we also list the Code sections whose text cites
it and the decisions that cite it.

| Bill | Amends | Dry run | Code sections citing the target | Decisions citing the target (Supreme Court) |
|---|---|---|---|---|
| H.R. 18, Bipartisan Background Checks Act of 2025 | 18 U.S.C. § 922 (adds (aa)); § 924(a)(5) | 2 of 2 | 34 cite § 922 | § 922: 29,044 (87); § 924(a): 5,710 (8) |
| H.R. 3602, Ending Qualified Immunity Act | 42 U.S.C. § 1983 (makes the text (a), adds (b)) | 2 of 2 | 3 | 83,646 (302) |
| S. 477, Fairness in Fentanyl Sentencing Act of 2025 | 21 U.S.C. § 841(b)(1)(A)(vi), (B)(vi); § 960(b)(1)(F), (2)(F) | 12 of 12 | 13 cite § 841(b); 5 cite § 960(b) | § 841(b): 5,472 (18); (b)(1)(A): 2,189 (8) |
| H.R. 8549, Second Look Act of 2026 | 18 U.S.C. § 3582(c); a new section in chapter 229 | 3 of 3 | 1 (28 U.S.C. § 994) | § 3582(c): 12,706 (11); (c)(2): 7,668 (7) |
| S. 3959, Smarter Sentencing Act of 2026 | 21 U.S.C. § 841(b)(1)(A), (B); § 960(b); § 802 | 11 of 11 | 13 / 5 / 98 | § 841(b)(1)(A): 2,189 (8); (B): 773 |

The fentanyl bill would lower the 400-gram threshold in § 841(b)(1)(A)(vi) to 20 grams. Few decisions cite that
clause (13), but 2,189 cite subparagraph (b)(1)(A), among them *Hughes v. United States* (2018), *Dorsey v. United
States* (2012) and *Burgess v. United States* (2008). The
Second Look Act adds to § 3582(c), the sentence-reduction subsection behind *Koons*, *Hughes* and *Chavez-Meza* (all
2018) and *Terry v. United States* (2021).

The dry run's value is in the negatives. Each of the five would apply as written today. Each words the change
narrowly. Its "40" or "10" occurs once in the clause it names, matched as a whole word.

#### Limits

- **Coverage.** Only laws since 2013. GovInfo's enrolled-bill XML for earlier Congresses exists for some laws and not
  others, so we left them out rather than mix sources.
- **Small audit samples.** The real error rates come from 20 operations per class, and the intervals are wide. The
  audits of "words not found" and "provision not found" were done on an earlier run. That run differed in matching
  whole words and in reading "in the heading" and "in the second sentence".
- **The parser is the weak part.** It still misses "after the semicolon" and "before the semicolon" when the
  provision ends "; and". It misses redesignations hidden in parentheticals and renamings made throughout a title. It
  reads a capitalised phrase such as "The Secretary" as a heading and ignores case there, which can make it look
  ambiguous. Our designation labels misplace some provisions printed inline. Whole sections added to a chapter, whole
  sections repealed, and sentence rewrites are not modelled.
- **Editorial style.** Outside the 27 positive-law titles, the Code rewrites an Act's own references and dates, so an
  instruction can be right and still not match the Code. Lean reports these as "not found", and only reading the
  Act tells them from errors.
- **Bills.** We dry-run against today's text only. We did not model what earlier sections of the same bill change,
  beyond running them in order. We found the bills by search and believe all five are still in committee, but did not
  confirm their status on congress.gov.
- **Inbound references** are found by searching the text for "section N", lists such as "sections 1981, 1983, and
  1985", and "N U.S.C. N". References the Code makes only through an Act's own section numbers are missed.
