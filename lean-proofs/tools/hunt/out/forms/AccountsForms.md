# AccountsForms: forms against statute (Trump accounts, HSAs, IRAs, 529/ABLE)

Statute text from `tools/hunt/sec.py` (through Pub. L. 119-138). Forms from irs.gov: 2025 revisions and the 2026 early-release drafts. Model: `AccountsForms/model.py` (statute and form written separately, 5306 grid points; results in `AccountsForms/grid_result.json`). Extracted form text is in `AccountsForms/txt/`.

## Differences, largest first

### 1. Form gives more: up to 3,895.83 more deduction for 2025 (3,987.50 on 2026 limits); tax worth roughly 400-1,400. Anyone who moves from self-only to family cover during the year and is covered on Dec 1.

- **Form:** Form 8889 line 3 (2025 instructions, rules 2 and 4 and the TIP: "If you had family coverage on the first day of the last month ... enter $8,550"); same wording in the 2026 draft
- **Statute:** s.223(b)(8)(A)(ii): December's plan is attributed only to "each of the months such individual is treated as an eligible individual solely by reason of clause (i)". A month in which the person really was eligible keeps its own coverage type under s.223(b)(2).
- **Example:** Eligible all 12 months of 2025, self-only Jan-Nov, family from Dec 1: statute 11/12 x 4,300 + 1/12 x 8,550 = 4,654.17; form 8,550. 704 coverage/age/marital grid points differ, all the same way.
- **Explained by:** Notice 2008-52 (limit is the greater of the monthly sum or the full-year amount for the Dec 1 coverage; its own example gives 5,800 against a monthly sum of 3,142). The form follows the notice, not the "solely by reason" words.
- **Already written about:** The greater-of rule is widely described; one search found nothing noting that it exceeds the statute's text.
- **Confidence:** high that form and text differ; the notice is long-standing IRS position

### 2. Form gives more: 1,000 per child

- **Form:** Form 4547 Part III line 7 and instructions ("anticipated to be the qualifying child of the authorized individual for the year in which the election is made")
- **Statute:** s.6434(a),(c): election "with respect to an eligible child of the individual"; eligible child "means a qualifying child (as defined in section 152(c))".
- **Example:** Parent elects in March expecting the child to live with them; child fails the s.152(c) residency test for the year. Statute: not an eligible child of that individual. Form/notice: the $1,000 stands.
- **Explained by:** Notice 2025-68 Q&A B-1 (election "will not be rendered ineffective solely" because the child later is not a qualifying child). The form face itself still says "must be a qualifying child".
- **Already written about:** not searched
- **Confidence:** medium (deliberate administrative reading)

### 3. Form gives more: up to 513 a year (573 with the age-55 amount) per person making the once-in-a-lifetime transfer

- **Form:** Form 5329 Part VII lines 43 and 47 with Form 8889 lines 10-13 (2025 and 2026 draft): a qualified HSA funding distribution only uses up limit; it is never itself an excess contribution
- **Statute:** s.4973(g)(1): excess contributions are amounts contributed "neither excludable from gross income under section 106(d) nor allowable as a deduction under section 223". A funding distribution is excluded by s.408(d)(9), and s.223(b)(4)(C) says it "shall not be allowed as a deduction", so read literally all of it is an excess contribution (same words in s.223(f)(3)(B)); s.4973(g)(2)(B) also counts it twice.
- **Example:** Family cover, 8,550 funding distribution, nothing else: literal statute 6% x 8,550 = 513 a year until absorbed; form 0. 30 grid points differ, all with a funding distribution.
- **Explained by:** No text fixes it. Notice 2008-51 treats the transfer as counting against the limit only; s.4973(g) was not conformed when s.408(d)(9) was added in 2006.
- **Already written about:** one search found no discussion
- **Confidence:** medium: the words say this; the result is plainly unintended and the form's reading is the sensible one

### 4. Statute gives more: up to 420 (480 if 50 or older) for an IRA, up to 573 for an HSA, first year only; accounts empty or nearly empty at year-end that receive a prior-year excess contribution the next spring

- **Form:** Form 5329 lines 17, 25, 33, 41, 49: 6% of the smaller of the excess or the account value "on December 31, 2025 (including 2025 contributions made in 2026)"
- **Statute:** s.4973(a): tax "shall not exceed 6 percent of the value of the account ... (determined as of the close of the taxable year)". s.219(f)(3) deems a later contribution made on the last day of the year only "For purposes of this section" (s.219); s.223(d)(4)(B) likewise for s.223.
- **Example:** IRA opened March 2026 with 7,000 designated for 2025 by someone with no compensation; value at 31 Dec 2025 is 0. Statute ceiling 0; form 420. 8 grid points differ.
- **Explained by:** none found (no regulation extends the deeming rule to s.4973)
- **Already written about:** not searched
- **Confidence:** medium

### 5. Statute gives more: at most 6% of the undistributed excess; rare

- **Form:** 2026 draft Form 5329 Part X line 61: "Enter 6% (0.06) of line 60" with no account-value ceiling (every other excess-contribution part has one)
- **Statute:** s.4973(a) ceiling of 6% of the value of the account at the close of the taxable year applies to every account in (a)(1)-(6); a Trump account is a s.408(a) account and s.530A(h)(5) changes only the definition of excess contributions.
- **Example:** 2,500 excess left in the account, whole balance moved to an ABLE account in the year the child turns 17, value at year-end 0: statute 0, form 150. 24 grid points differ, all with year-end value below the excess.
- **Explained by:** none; draft form
- **Already written about:** no
- **Confidence:** medium-low (draft; narrow facts)

## Checked, no difference

- Form 8606 2026 draft: "traditional IRA ... does not include Trump accounts" keeps them out of lines 2, 6, 7, matching s.530A(h)(4) and Notice 2025-68 G-1 (0 grid points differ). No Trump account can be past its growth period in 2026 (s.530A(b)(2)(A): born 2009 or later), so the form's silence costs nothing for 2026.
- Age cut-offs: Form 4547 ("under age 18 at the end of the year", "born after December 31, 2008"), draft 5329 Parts III/X ("has not attained age 18 by the end of 2026"), the growth period in Notice 2025-68, pilot birth window 2025-2028: all match s.530A(b)(2)(A), (c)(2), (h)(5) and s.6434(c)(1) for calendar-year taxpayers (0 grid points differ).
- Draft 5329 Part X lines 56-60 and Part XI (100% of earnings) match s.530A(h)(5) and (d)(5)(C); exempt contributions are left out of the 5,000 test as in s.530A(c)(2).
- Form 8889 Part III (last-month rule and funding-distribution testing periods, 10%) matches s.223(b)(8)(B) and s.408(d)(9)(D); the 20% tax exceptions match s.223(f)(4).
- Form 5329 Part VIII (ABLE: current-year excess only, no carry-over) matches s.4973(h).
- Forms 1099-Q and 5498-QA are information returns with no limit computation; 5498-QA box 8 matches s.530A(d)(4)(B).

## Gaps and loose ends (not counted as differences)

- No form or instruction yet computes the separate s.408(d)(2) ratio for a Trump account after the growth period, or carries its basis; the 2026 Form 8606 instructions say Trump accounts "are not discussed". First needed for 2027 (children born in 2009).
- 2025 Form 8889 line 3: the Note ("If you are married and had family coverage at any time during the year, the additional contribution amount is figured on line 7 and is not included on line 3") conflicts with the Line 3 chart, which adds 1,000 to self-only months for anyone 55 or older. Following the Note drops up to 1,000 x self-only months / 12; following the chart matches s.223(b)(3).
- Pub. 590-A's section on s.529(c)(3)(E) transfers (read only through a summary) says the account must be open "more than 15 years" and that the yearly cap is the Roth contribution limit; the statute's reduction for contributions "made during the taxable year" to any IRA was not visible. Not verified word for word.
- Instructions for Form 1099-Q (Rev. 4-2025) predate the 2025 Act's s.529 changes and tell payers to tick box 4a (trustee-to-trustee) for 60-day rollovers to ABLE accounts.

## Form 8606 and Trump accounts

The 2025 form and instructions never mention Trump accounts (none existed). The 2026 draft form's header note and the draft instructions' What's New both take Trump accounts out of "traditional IRA" for the whole form, so lines 6-13 compute the ratio on other IRAs alone, as s.530A(h)(4) and Notice 2025-68 G-1 require. After the beneficiary turns 18 the draft does nothing: it says Trump accounts "are not discussed", and no line holds the account's own basis or ratio. Draft Form 5329 Part I does pick up post-growth-period distributions for the 10% tax.

## Not retrieved

- Notice 2026-5 (HSA changes): cited by the 8889 draft, not fetched
- Notices 2008-51 and 2008-52: known from search summaries only
- Pub. 590-A and Pub. 590-B full text (590-A QTP section seen only in summary); Pub. 970
- 2026 Form 1099-R / 5498 instructions (box 7d earnings on Trump account excess)
- Any 2026 revision of Form 1099-Q or its instructions (latest posted is Rev. April 2025)
