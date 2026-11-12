# Draft subsection: When Congress answers a court

<!-- For section 7 ("A foray into the statute book") of formalizing-all-us-case-law-in-lean, after "Does the change
matter?". Every number below is in uses/overrides/results.json, recall.json, per_congress.tsv or confirmed.tsv. -->

## When Congress answers a court

Sometimes Congress rewrites a statute because of one decision. In 2007 the Supreme Court held in *Ledbetter v.
Goodyear* that Lilly Ledbetter had filed her claim of pay discrimination too late: the time to file ran from the
decision setting her pay, not from each paycheck. Twenty months later the Lilly Ledbetter Fair Pay Act added a paragraph to
42 U.S.C. § 2000e-5(e). Its findings name the case: "The Supreme Court in Ledbetter v. Goodyear Tire & Rubber Co.,
550 U.S. 618 (2007), significantly impairs statutory protections". Scholars call this an override. They find
overrides by reading laws and reports by hand. The best list, by Christiansen and Eskridge, counts 275 overrides of
Supreme Court decisions from 1967 to 2011.

Our record holds what is needed to look for them automatically. For every citation, we know the words the court read
and every later version of them, each dated and credited to the law that made it.

### The first law to rewrite the words a court read

For each of the 1,931,153 citations, Lean walks the versions of the section after the decision and finds the first one
whose cited words differ from those the court read. In 596,692 citations the words have changed since. A law made the
first change in 421,897 of them; in the rest it was an edition of the Code. In 365,853 citations the first law came
within ten years of the decision.

That first law is not usually an answer to the court. Most are routine amendments. So we look for evidence that
Congress had the decision in mind:

- **The law names it.** We fetched the text of all 1,324 laws involved from the Government Publishing Office. Only 85
  of them name any case at all, in the form "X v. Y".
- **A committee report names it.** Each law lists the committee reports on its bill. For the laws that rewrote words
  cited by the Supreme Court or a court of appeals, we fetched 1,159 reports, covering 719 laws.
- **The court quoted words the law struck.** The decision quotes a phrase of the statute, the phrase is gone from the
  new text, and the law speaks of courts or decisions somewhere in its text.

A citation is a candidate when its first rewriting law came within ten years and one of these holds. Lean decides
this for every citation. It finds 6,069 decision–law pairs: 30 where the law names the decision, 279 where a report
does, and 5,760 where only the quoted words point to it. 101 are Supreme Court decisions, 2,392 decisions of the courts
of appeals, and the rest from district, specialised and state courts. We also rank the pairs. The score adds the
evidence, the time between decision and law, how often the decision cites the section, and the court.

Lean proves what the definition promises. A candidate's law amended the section after the decision and inside the
window. Its words of the cited block differ from those the court read. No version between the decision and that law
changed them, so it really is the first. There is at most one such law for each citation. Widening the window never
loses a candidate. And there is no candidate without evidence. Lean and an independent script agree on the first
rewriting law for all 421,897 citations.

### How many are real?

We had agents read 155 pairs, 135 candidates and 20 that are not: the decision's passages around the citation, the words before and after, the law
where it amends the section, and any passage that names a case. They did not know why an item was picked. They were
told to be strict. A law can name a case and only agree with it, or name it in passing.

| Evidence | Read | Overrides | Share |
|---|---|---|---|
| The law names the decision (all of them) | 30 | 11 | 37% |
| A committee report names it (random sample) | 40 | 8 | 20% |
| Only quoted words struck (random sample) | 45 | 5 | 11% |
| Top 10 of the ranking | 10 | 7 | 70% |
| Top 30 of the ranking | 30 | 15 | 50% |
| Not candidates, as a baseline (random sample) | 20 | 0 | 0% |

Naming is not answering. Of the 30 laws that name the decision, 6 write its holding into the statute instead. In
4 the law names a different case that shares a party's name, such as another *Alaska v. Babbitt*. The quoted-words
signal is weak on its own: it is right in 4 of 25 appellate and Supreme Court decisions and 1 of 20 others. Scaled to
the candidates, that suggests about 600 overrides among them, with a wide range (215 to 1,730).

The readers are strict too. We gave them 11 known overrides from the published list without saying so; with the 9
already in the samples, they recognised 15 of the 20. Two misses were our fault: the packet showed a section the
decision cited, not the one the law changed.

### Do we find the known ones?

Christiansen and Eskridge, and Hasen, list 36 overrides of Supreme Court decisions made since 1995 by laws of 2011 or
earlier. We find 20 of them (56%).

The other 16 fall out at a known step:

- 3 decisions (*Schlup v. Delo*, *Thompson v. Keohane*, *Oklahoma Tax Commission v. Jefferson Lines*) have no
  citation of the Code that our earlier reader matched.
- 4 overriding laws changed no section the decision cites in our record. *Rasul v. Bush* was answered by the
  Detainee Treatment Act, which Congress enacted twice, in two laws a week apart; our record credits the change to the
  other one.
- 5 laws amended a section the decision cites, but not the first time its cited words changed, or not in the block it
  cited. In *United States v. Santos* the Court read "proceeds" in § 1956(a); the 2009 law answered by defining
  the word in a new § 1956(c)(9), a block the Court never cited.
- 4 have the right law but no evidence. *Koon* and *Muscarello* are among them.

So of the 24 that our record can reach, the method finds 20 (83%).

### What the lists do not have

The audit confirmed 34 overrides; 15 are on the published lists. The other 19 are new to them. 15 answer a lower
court, which the lists do not cover. 2 came after 2011. And 2 are Supreme Court decisions the lists leave out:
*Lorillard Tobacco v. Reilly*, whose pre-emption ruling the 2009 tobacco law undid (the law names the decision, but
only on another point), and *Ashcroft v.
Free Speech Coalition*, a constitutional ruling that Congress answered by rewriting the definitions the Court struck
down.

*The Fraud Enforcement and Recovery Act of 2009.* Its Senate report says it "amends the FCA to clarify and correct
erroneous interpretations of the law that were decided in Allison Engine Co. v. United States ex rel. Sanders". It
answered more than the Supreme Court. The same report names district court decisions on Iraqi reconstruction funds
(*Custer Battles*), on conspiracy (*Huangyan Import & Export*) and on presentment to a federal officer (*Atkins v.
McInteer*). It also answers the Seventh Circuit's reading of "proceeds" in the *Santos* case. Lean finds each of them,
because each cited the words the law rewrote.

*United States v. Nagarwala.* In November 2018 a federal district court in Michigan held that the federal ban on female
genital mutilation, 18 U.S.C. § 116, was beyond Congress's power. In January 2021 a new law rewrote § 116 with links to
interstate commerce. Its text says "the United States District Court for the Eastern District of Michigan erred in
invalidating the prior version of such section 116".

*Harvey v. Veneman.* In January 2005 the First Circuit held that the organic foods law barred any synthetic ingredient
in processed organic food. Ten months later an appropriations act inserted "not appearing on the National List" into
7 U.S.C. § 6510(a)(1). The same act names the decision.

The overrides cluster. 23 of the 34 confirmed came from the 109th to 111th Congresses (2005–2011): the Voting Rights
Act reauthorisation, the ADA Amendments Act, the Ledbetter Act and the fraud act. That partly reflects what we read, but
the candidates cluster too: 3,744 of the 6,069 come from laws of the 108th to 111th Congresses (2003–2011), and
601 from laws of 2017 or later.

<!-- figure: uses/overrides/overrides.svg -->
*Each arc runs from a decision to the law that rewrote the words it read, for the 34 overrides our readers
confirmed.*

### Limits

- The definition needs the court to have cited the block Congress rewrote. A law that adds a new definition elsewhere
  in the section, or a new section, is missed (*Santos* at the Supreme Court).
- Committee reports come from the law's own legislative-history note. Reports on companion bills, or on an earlier
  bill that became part of an omnibus, are missed. For multi-part reports we read only part 1.
- The quoted-words signal finds candidates without names, at about one in ten. It needs a model reading each one.
- The precision figures rest on 155 readings by agents, not lawyers, and the samples are small: 8 of 40 has a 95%
  interval of 10% to 35%.
- The published lists stop in 2011 and cover only the Supreme Court. For later and lower-court overrides we have only
  our own readings.
