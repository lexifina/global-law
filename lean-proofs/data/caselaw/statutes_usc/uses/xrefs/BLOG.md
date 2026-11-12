<!-- Draft subsection for "Formalizing all US case law in Lean", section 7. Numbers from uses/xrefs (run of
2026-11-12, record through 2026-11-03). Counts are references: one (referring section, target section, designation)
triple; "subparagraph (A), (B), (C), or (D)" is four. -->

### Does the Code point at itself correctly?

The Code is full of references to itself: "section 2244 of this title", "subsection (c)(1) of section 924 of title
18", "paragraph (2) of subsection (a)". A reference is only as good as its target. When Congress repeals a section or
reletters its subsections, every reference into it should be changed too. We checked whether that happens.

We read every version of every section since 1995 for references that name their target outright: a section of a
title, a designation inside it, or a subsection of the same section. We left out the ones that need context to
resolve, such as a bare "paragraph (2)", "such section" or "chapter 5". Then a third Lean model judged each one
against the Code as it stood on each day: does the target section exist, and does it have that designation? Lean
proves that a reference can change status only on a day when the referring section or its target has a new version,
so it only needs to look on those days. It also proves that whether a reference dangles depends on that day's Code
alone, not on how the Code got there.

Today the Code makes 152,597 such references. 3,278 of them (2.1%) point at nothing. In 1996 the share was 2.2% (2,113
of 94,776). The Code has grown by half and the share has barely moved. In 1,311 the target section is there but
lacks the designation. In 1,293 the section has been repealed, transferred or removed. In 573 it is not in the
record at all, usually because it was repealed before 1995. The other 101 point at a subsection that has been
repealed.

[FIGURE xrefs.svg: references that newly dangle each year, broken later vs written so, and the number dangling at
each year end.]

### Who breaks them?

Since the record starts in 1995, 3,566 references that worked have been broken by a later change to their target while their own words
stood still. 300 different laws did it. Most are mended: the median broken reference is fixed within a year (343
days), nearly always by rewriting the reference. 1,269 are still broken today.

The biggest single break was the law that created title 54 in December 2014. It moved the National Park Service laws
out of title 16 and broke 726 references in one day. The Code's editors rewrote 693 of them 17 days later, in the
next edition; 32 are still broken. Others take longer. The Dodd-Frank Act of 2010 repealed, among others, the section
on the Resolution Trust Corporation (12 U.S.C. § 1441a); 32 references it broke are still broken. The 2017 tax law repealed sections such as 199 and 902; 29
references to them remain. The Affordable Care Act left 24, the 2014 Farm Bill 23.

Other references are wrong from the day they are written. 2,928 times a law or an edition wrote a reference that did
not resolve; most were put right later (median 187 days), but 845 still stand. Dodd-Frank wrote the most that are
still wrong (26).

### An example

The federal Anti-Riot Act, 18 U.S.C. § 2101, makes it a crime to cross state lines with intent to incite a riot,
and then to commit an overt act "for any purpose specified in subparagraph (A), (B), (C), or (D)". In 1996 the
Economic Espionage Act tidied the section. It turned subparagraphs (A) to (D) of paragraph (a)(1) into paragraphs
(1) to (4) of subsection (a). It did not change the two places that refer to them. Subsection (b) still speaks of
"the overt acts described in subparagraph (A), (B), (C), or (D) of paragraph (1) of subsection (a)". Lean finds the
version of 1994 in which those subparagraphs exist, and the law of October 11, 1996, from which they do not. The
words have pointed at nothing for 30 years. The official Code marks both places "So in original". Our reader finds
the one in subsection (b). It misses the one in subsection (a), which says "of this paragraph" and needs context to
resolve.

### Duplicate designations

Congress also adds a subsection (e) to a section that already has one. Today 151 sections have 181 designations
that appear twice among siblings. We drew 20 and read them: 13 were real. Seven were the record printing a clause
at the wrong indent. Most real ones come from two laws adding the same letter, as in 26 U.S.C. § 45Y(b)(1), where a
law of July 2025 added a second subparagraph (E). We count 642 duplicates that have come and gone since 1995.

### How good is the reader?

Precision matters more than coverage here: a false claim that the law is broken is worse than a missed one. We drew
60 dangling references at random and had agents read each one against the text of both sections and the official
Code. 37 were real. The other 23 were our errors: 13 were designations the reader missed because the record prints
them at the wrong indent, 9 were references it misread, and one was the repealing provision itself. We fixed the
general causes (a check that reads designations in order whatever their indent, and four parsing rules). Of the 43
references in that sample the final reader still flags, 35 are real.

Those fixes were chosen by reading the sample, so we froze the reader and drew 40 new references. 27 are real (68%,
between 52% and 80%). If the sample is representative, about 2,200 of the 3,278 are real errors in the law (between
1,700 and 2,600). The reader is good at references to other sections: 24 of 29 were real. It is poor at bare
"subsection (a)": 3 of 11 were real. Most of the rest named a subsection of another section mentioned earlier in the
sentence, as in "section 413 of the Controlled Substances Act, with the exception of subsections (a) and (d)".

Real errors are mostly not news to the Code's editors. Of the 64 real ones in the two samples, the official Code
explains 53 in a note, usually "References in Text", and marks 2 "So in original". Nine carry no mark at all. One is
26 U.S.C. § 857, which since 1999 has cited "section 856(d)(8)(F)", though § 856(d)(8) has no (F); the rule meant is
in (d)(9)(F). Another is 18 U.S.C. § 3742(e), which since 2003 has spoken of "subsection (3)(A) or (3)(B)" in a
section with no subsection (3).

We also read 20 references the model says were broken later. In all 20 the reference had worked the day before. In 18
the law the model names made the change. In 4 the break is an artifact of dating: one law changed both sections, but
the record dates the two changes on different days, so the reference looks broken for a while.

### Limits

- The reader takes only references that name their target. Relative ones ("paragraph (2)", "of this paragraph",
  "such section"), chapters and references to other Acts are not checked.
- A reference counts once per designation it names, so "subparagraph (A), (B), (C), or (D)" is four. The 3,278 today
  come from 2,811 pairs of sections and 2,220 referring sections.
- The record's indentation is sometimes wrong. The reader repairs what it can and gives a reference the benefit of
  the doubt, which hides some real errors: two real ones in the first sample were lost to the fixes.
- The record has no files for sections repealed before 1995, and it deletes some sections the editors omit later, so
  "not in the record" and "removed" stand in for "repealed" or "omitted". One heading rule is wrong: sections whose
  heading starts with "Transferred" (26 U.S.C. § 6901, "Transferred assets"; 22 U.S.C. § 3671) are read as moved
  away, so all 8 references counted as pointing at a transferred section today are our error.
- 1,164 of today's dangling references were already dangling when the record starts, so their cause is unknown.
- Before 2017 the record dates a change on the day the law was enacted, not the day it took effect.
- Saying the words point at nothing does not mean the law cannot be read. Courts and agencies follow notes like "So
  in original. Probably should be ...". Some references to repealed sections are kept on purpose, for older years.
