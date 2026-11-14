# Charity: findings

File: `LegalProofs/USTax/Hunt/Charity.lean` (runs in about 95 s with `lake env lean`). Output of the last run:
`tools/hunt/out/Charity/run_final.txt`. Earlier runs: `run_A_all_moves.txt` (every move at once, profile A, 108 s),
`run2.txt`, `run3.txt`.

**Bottom line: nothing novel.** Every plan the search ranked above baseline is a known technique or a known technique
under the 2025 Act. No CANDIDATE survived. Two traps and four drafting gaps are worth keeping.

## Provisions encoded (text read with `sec.py`)

| Provision | What the model does with it |
|---|---|
| §170(b)(1)(A),(B),(C),(D),(G),(H) | Four classes of gift (cash to public charity/DAF, cash to private foundation, stock to public charity/DAF, stock to private foundation) with the 60/50/30/20% limits and their interaction formulas |
| §170(b)(1)(I) (2025 Act) | 0.5% floor, absorbed in the statutory order D, C, B, A, G |
| §170(d)(1)(A),(C) | Carryovers per class; floor amount carried only from a year whose own gifts exceed a limit (narrow reading) |
| §170(p), §63(b)(4) (2025 Act) | Non-itemizer deduction, $2,000 joint, cash, not to a DAF, no floor |
| §63(e), §68 (2025 Act) | Itemize or not, whichever is lower; 2/37 reduction above the 37% threshold |
| §170(e)(1), (e)(5) | Long-term stock at value to a public charity; qualified appreciated stock at value to a private foundation |
| §170(f)(18), §4966(d) | DAF gift deductible like a public-charity gift; excluded from §170(p) and from QCDs |
| §25F (2025 Act) | 100% credit, $1,700, years after 2026, no §170 deduction for the credited gift; $1,700 for each other family taxpayer |
| §408(d)(8)(A)–(E),(G) | QCD up to $111,000 (2026), excluded, counts toward the RMD; (C) "entire distribution" test applied to an IRA payment to an SGO |
| §1(h), §1(j), §1411 | 2026 joint brackets, capital gain rates, NIIT |
| §§641(b), 642(b), 642(c)(1), 1(e), 1411(a)(2), 1015, 2501/2505 | Non-grantor trust for the children: funded with stock, sells, pays gross income to charity, deduction without limit; §68 applied to it (conservative) |
| §664(b),(c),(d)(1), §170(f)(2)(A) | Two-year annuity trust at 5% or 45% payout, 10% remainder test, gain-first character of payments, remainder deduction |
| §170(b)(2)(A), (d)(2) (2025 Act) | Corporate gift: 1% floor, 10% cap, floor carried only from an over-10% year; 21% rate |
| §1001 | Sale of stock |

Read but not modelled (noted under gaps where relevant): §408(d)(8)(F) one-time split-interest election, §170(b)(1)(C)(iii)
election, §170(b)(1)(E)–(F), §170(f)(2)(B) lead trusts, §642(c)(5) pooled funds, §§4940/4942/4967, §2501(a)(6),
§1011(b), §§2055/2522, §§512–514.

Figures: 2026 (Rev. Proc. 2025-32) for all three years. §7520 rate set to 0 because no asset in the model grows.
End wealth is measured as if everything were sold: stock less the family's gain rate, IRA less its ordinary rate.

## Search size

Three taxable years (2026–2028), 15 kinds of move, amounts from the target (thirds or sixths), what is left of it,
each statutory cap, and 30% of base. Fifteen runs over six profiles; about 2.2 million year-plans tried in the final
file, the largest run 774,000 year-plans and 114,000 kept positions. Positions are kept per family of moves, so the
runner-up families print as well as the winner.

## Plans that beat plain annual cash gifts

Dollar effect is end wealth against the baseline of equal cash gifts each year, same total to charity.

| # | Plan (as the search printed it) | Profile | Effect | Provisions combined | Class | What could defeat it |
|---|---|---|---|---|---|---|
| 1 | QCD for most of the gift, $1,700 a year to an SGO, optionally $2,000 cash in a non-itemizing year | A: AGI $200k, does not itemize, $36k over 3 years | +$9,252 (baseline tax $75,522) | §408(d)(8), §25F, §170(p) | VARIANT: QCD (known) stacked with the two 2025 non-itemizer benefits | State must opt in to §25F and list the SGO; state credit reduces it; QCD needs age 70½ |
| 2 | All stock in one year, $1,700 SGO in another | D: as A, no IRA | +$8,155 | §170(e)(1), §63(e), §25F | KNOWN: bunching appreciated stock (DAF or foundation) | Nothing; substantiation rules |
| 3 | $298,300 of stock in one year, split public charity / foundation, SGO in another year | B: AGI $1.3M, $300k over 3 years | +$58,902 (baseline tax $1,048,314) | §170(e)(1),(e)(5), (b)(1)(C),(D),(I), §68 | KNOWN: appreciated stock plus bunching. About $53.5k is the unrealized gain given away, about $4.5k is paying the floor once instead of three times | Nothing |
| 4 | Plan 3 with adult children each giving $1,700 a year to an SGO from money the parents give them | E | +$1,603 over plan 3 | §25F(b)(1) "any taxpayer", §2503(b) | VARIANT: per-taxpayer cap with no family aggregation | Each child needs $1,700 of own tax; step transaction if the gift to the child is conditioned on the contribution; SGO capacity; state opt-in |
| 5 | QCD at the $111,000 cap every year plus stock up to 30% of base | C: AGI $150k, $450k over 3 years | +$50,630 | §408(d)(8), §170(b)(1)(C) | KNOWN: QCD above the RMD when the percentage limits bind | Nothing |
| 6 | Plan 5, last $27,000 through the children's trust: trust sells $36,000 of stock and pays the $27,000 gain to charity | C | +$2,947 over the same plan without the trust | §642(c)(1), §641(b), §1015, §68 | VARIANT: non-grantor trust charitable deduction (known), used here because it has no percentage limit and no 0.5% floor, and because the whole payment is gain so the family keeps clean basis | Part of the edge is the model's horizon (an unused $46,500 carryover is valued at zero). Reg. §1.642(c)-3(b): the instrument's ordering must have economic effect apart from tax. §§671–677 if the couple keep any power or interest. §68 if it applies costs about 1.1% of the payment (modelled). Gift uses §2505 exemption |
| 7 | Children's trust sells $16,000–$133,000 of stock a year, no charity involved | A, B, D, F | +$1,500 to +$5,800 | §1(e), §1(h), §641 | KNOWN: a trust is a separate taxpayer with its own 0%/15% gain bands. Not a charitable plan; it appears because the search is blind | §643(f) multiple trusts; the money now belongs to the children |
| 8 | Two-year annuity trust, 5% payout, with stock gifts | B | −$658 against plan 3 | §664 | KNOWN, and it loses here | — |
| 9 | Corporate cash gifts | E | never in the best ten | §170(b)(2) | KNOWN, and it loses to a personal stock gift | — |

Checked and not better than the plain route: an IRA payment straight to an SGO (ties with paying cash, because under
the reading encoded it is not a QCD), the 45% annuity trust, cash to a private foundation, selling stock to give cash.

## Traps (rules that cost money)

1. **IRA payment to an SGO.** §408(d)(8)(C) treats a distribution as a QCD only if a §170 deduction "for the entire
   distribution" would be allowable. §25F(e) says a contribution for which the credit is allowed is not a charitable
   contribution for §170. Read together, an IRA cheque to an SGO for which the credit is taken is fully taxable, and
   if the cheque is larger than $1,700 the whole of it loses the exclusion, not just $1,700. I found no commentary
   and nothing in the summaries of T.D. 10057 on this. Safe course: QCDs and SGO gifts from separate money.
2. **§68 and trusts.** New §68 has no exception for estates and trusts (old §68(e) is gone). A §642(c) deduction is
   an itemized deduction, and a trust reaches the 37% bracket at $16,000, so 2/37 of nearly every charitable payment
   by a lead trust or an estate would be taxed. Already debated (JCT says it applies; AICPA and NYSBA ask for relief).
3. **Carryover used in a non-itemizing year.** Under the regulation a carryover is consumed as if the couple had
   itemized. Bunching above a limit and then taking the standard deduction wastes it. In profile C $46,500 of
   carryover is still unused at the end of the horizon.
4. **Stock to a private foundation after 30% to public charities.** The (D) limit is the lesser of 20% and 30% less
   the (C) gifts, so it falls to zero and the foundation gift is only a carryover (profile C: $300,000 stranded).
5. **Floor lost every year.** Equal annual gifts lose 0.5% of AGI each year; the same total in one year loses it once.

## Drafting gaps noticed (not modelled, or not isolated by the search)

- **§25F cap "to any taxpayer".** No joint-return rule in the statute. Commenters ask for $3,400 on a joint return.
  The model uses $1,700.
- **§170(d)(1)(C).** The floor amount is carried forward from a year "from which an excess is carried forward under
  any carryover rule". Read literally, an excess in one class rescues floor amounts taken from another class, and
  the floor is taken first from class (D). A donor already at 30% in stock to public charities has a zero (D) limit,
  so one further dollar of stock to a private foundation makes the year an excess year. Already written about
  (Tax Adviser July 2026, FPA Journal October 2026, CBIZ). The search did not isolate it: profile F ties with even
  giving.
- **§68 marginal value is not monotone.** The reduction is 2/37 of the lesser of itemized deductions or income over
  the 37% threshold. Once itemized deductions exceed that excess, the next 2/37 × excess dollars of deduction are
  worth a full 37% before the 35% bracket starts. Small, and I did not find it discussed.
- **QCD and §170(p) recipients.** Both exclude DAFs and supporting organizations but not private foundations
  described in §170(b)(1)(F) (operating, conduit, common-fund), and a private foundation cannot be a DAF sponsor
  (§4966(d)(1)(B)). A QCD to the donor's own conduit foundation is allowed by the text. Known for operating and
  conduit foundations.
- **§408(d)(8)(F) with a term-of-years trust.** The $55,000 one-time QCD to a remainder trust need not be a life
  trust; a short term at a high payout would satisfy an RMD now and return most of it as ordinary income later.
  Not modelled (no bracket variation across years in the model).
- **Corporate floor, §170(d)(2)(C).** The same "only from an over-limit year" rule as for individuals.

## Sources checked (5 searches)

- [Current Federal Tax Developments: new §68 and trusts, JCT footnote 102](https://www.currentfederaltaxdevelopments.com/blog/2026/6/6/the-application-of-new-section-68-to-trusts-and-estates-analyzing-jct-footnote-102-and-unresolved-ambiguities)
- [NYSBA Tax Section draft report on §68 and trusts](https://nysba.org/wp-content/uploads/2025/12/NYSBATS-report-draft-on-section-68-impact-on-trusts-and-estates-4929-8009-6109-10-002-002.pdf)
- [Greenleaf Trust: The 2/37th debate](https://greenleaftrust.com/wp-content/uploads/2025/10/The-2.37th-Debate.pdf)
- [The Tax Adviser, July 2026: planning for new charitable contribution limits](https://www.thetaxadviser.com/issues/2026/jul/planning-for-new-charitable-contribution-limits/)
- [FPA Journal, October 2026: the floor's sorting rule](https://www.financialplanningassociation.org/learning/publications/journal/OCT26-charitable-floor-sorting-rule-and-sort-decides-who-loses-OPEN)
- [CBIZ: charitable carryovers after the 2025 Act](https://www.cbiz.com/insights/article/charitable-contribution-carryovers-in-a-post-obbba-world)
- [FPA Journal, October 2026: trusts and estates under the 2025 Act](https://www.financialplanningassociation.org/learning/publications/journal/OCT26-higher-taxes-trusts-and-estates-under-one-big-beautiful-bill-act-OPEN)
- [Federal Register: federal scholarship tax credit regulations](https://www.federalregister.gov/documents/2026/10/02/2026-20277/federal-scholarship-tax-credit)
- [Current Federal Tax Developments: T.D. 10057 analysis](https://www.currentfederaltaxdevelopments.com/blog/2026/10/1/federal-scholarship-tax-credit-regulations-comprehensive-technical-analysis-of-temporary-td-10057-and-proposed-reg-117199-25-under-section-25f)
- [JFNA comments on Notice 2025-70](https://cdn.fedweb.org/fed-1/1/JFNA%2520Comments%2520IRS%2520Notice%25202025-70%252012-30-2025%2520%25281%2529.pdf)

I read search summaries, not the documents themselves, so "not discussed" means not found in five searches.

## Limits of the model

No growth, so nothing that depends on beating the §7520 rate (lead trusts, long remainder trusts, pooled funds) can
win. Three years, so carryovers left at the end count for nothing. One stock lot. No state tax. No estate tax
(§2055) leg. The liquidation valuation is what makes stock gifts rank so high; a family that will hold to death and
take a §1014 step-up would rank QCDs first throughout.
