# Accounts: tax-favoured savings accounts beyond the retirement search

File: `LegalProofs/USTax/Hunt/Accounts.lean` (rules, then search). Run: `lake env lean LegalProofs/USTax/Hunt/Accounts.lean`
(about 50 s for all 15 scenarios). Last output: `tools/hunt/out/Accounts/final-run.txt`.

**Bottom line: nothing clearly novel.** Two results are known techniques carried into the 2025 Trump-account law
(VARIANT); the rest are known. No CANDIDATE survived.

## Provisions encoded (text read from the local release point)

| Area | Provisions | Notes |
|---|---|---|
| HSA | §223(a), (b)(1)–(3), (b)(4)(C), (b)(6), (b)(7), (b)(8) last-month rule and testing period, (f)(2), (f)(4) | 2025: $4,300 / $8,550, +$1,000 at 55. Coverage per year is a scenario fact. |
| IRA → HSA | §408(d)(9) incl. (C)(ii)(II) second transfer, (D) testing period, (E) includible-first | once per lifetime |
| QCD | §408(d)(8)(A) incl. the post-70½ deduction cut, (B), (D) includible-first | $108,000 (2025) |
| Roth IRA | §408A(c)(2)–(3), (c)(3)(E), (c)(5)(B), (d)(2) 5-year rule, (d)(3)(F) 5-year conversion rule, (d)(4) ordering | one conversion layer (conservative) |
| Early distributions | §72(t)(1), (2)(A)(i); §4974(c) (no §457(b) plan) | exceptions (B)–(N) read, not modelled |
| 529 | §529(c)(3)(A), (c)(3)(C)(i)(III) ABLE rollover, (c)(3)(E) Roth transfer, (c)(6) | 15-year / 5-year clocks, $35,000 |
| ABLE | §529A(b)(2)(B), (b)(6), (c)(1), (e)(1) | $19,000 (2025) |
| Trump account | §530A(a), (b)(1)(C), (c)(1)–(3), (d)(1)–(4), (h)(1), (h)(3), (h)(4) | $5,000 statutory (2026) |
| Workplace | §402(g)(1), §402A(a)(1)–(3), (c)(4), §414(v)(2), (3), (7), §415(c)(1), §457(b)(2), (c), (e)(18), §404(a)(3) | 2025: $23,500, $7,500 / $11,250, $70,000 |
| Roll-in | §408(d)(3)(A)(ii), (H) | only from the Trump account (the retirement search already has the IRA case) |

Read but not modelled: Coverdell §530 (read (b)(1), (c)); §128 employer contributions; §457(b)(3); SEPP; spouses'
HSAs (§223(b)(5)); FICA.

## Search

Breadth-first over every allowed sequence, each position once; 34 move kinds; amounts are what the position offers for
that move (room left under its limit, the balance, its pre-tax part, its basis). 15 scenarios, depth 6–10, **240,816
positions** in all. Objective: worth after embedded tax, with a 25% premium for money whose future growth is sheltered
(Roth, HSA, ABLE at 1.25; pre-tax at 1.25 × (1 − later rate); cash and basis at par). Baseline: best plan using only
the plain moves (ordinary contributions).

## Plans that beat the baseline

| # | Scenario | Plan found | vs baseline | Provisions combined | Class | What could defeat it |
|---|---|---|---|---|---|---|
| 1 | S4: adult high earner, $100,000 rollover IRA, still has the Trump account from childhood | Non-deductible $7,000 a year into the Trump account, convert the Trump account | +$3,500 over 2 years ($7,000 a year reaches Roth at no tax); S4b without the account: nothing | §530A(a), (h)(4); §408(o); §408A(d)(3)(C) | **VARIANT** (backdoor Roth without the pro-rata rule) | See below |
| 2 | S3k: 18-year-old taxed at parents' 35% (§1(g)), not a dependent, on parents' family HDHP, job with a plan | Trump account → HSA $8,550; roll the other $11,450 of growth into the employer plan; convert the $40,000 basis | +$12,565; zero tax on the whole account | §408(d)(9)(B), (E); §408(d)(3)(A)(ii), (H); §530A(h)(4); §408A(d)(3) | **VARIANT** (basis isolation + adult-child family HSA limit, on a Trump account) | See below |
| 3 | S3: 17→19, child's own 10% rate | Convert the Trump account at 18 | +$9,500 to +$15,250 | §530A(a), §408A(d)(3) | KNOWN ("Trump account Roth conversion at 18"; Fidelity, Kiplinger) | kiddie tax (S3m: still +$7,000 at 35%, all from the basis) |
| 4 | S3b: ABLE-eligible child | Whole Trump account to ABLE at 17 | +$16,000 to +$17,250 | §530A(d)(4), §529A(b)(2)(B), (b)(6) | KNOWN (the statute's own route) | must be the year of the 17th birthday, entire balance |
| 5 | S1b / S1c: HSA-eligible, short of cash | IRA → HSA funding distribution | +$2,130 | §408(d)(9) | KNOWN (QHFD) | 12-month testing period; S1 shows it loses to a cash HSA contribution when cash is available |
| 6 | S1 | Non-deductible IRA + convert everything | +$3,550 | — | KNOWN (backdoor Roth; already in Retirement/) | — |
| 7 | S2: age 72, IRA with basis | QCD takes the pre-tax money, convert the remaining basis | +$1,180 | §408(d)(8)(D), §408A(d)(3) | KNOWN (QCD comes from pre-tax first) | — |
| 8 | S5 / S5b: old 529 | 529 → Roth $7,000 a year | +$688 to +$1,848; high earner +$8,106 (beats the backdoor's +$5,250 because 529 earnings come along) | §529(c)(3)(E), §408A(c)(3)(E) | KNOWN (SECURE 2.0 §126) | 15-year rule after a beneficiary change is unsettled; needs compensation |
| 9 | S6: age 61, 401(k) + governmental 457(b) + second business | Two deferral limits, two catch-ups, pre-tax catch-up through the second employer's plan, after-tax + in-plan Roth in the second plan | +$17,388 to +$19,125 | §457(c), (e)(18); §414(v)(7)(A); §415(c), (f) | KNOWN (457 double deferral; per-employer wage test; second-plan mega backdoor) | controlled-group rules §414(b), (c), (m) |
| 10 | S7: $60,000 needed at 58 | Convert, wait 5 years, withdraw; or 457(b) first; or Roth contributions first | +$6,000 (the whole 10%) | §408A(d)(3)(F), (d)(4); §72(t)(1) | KNOWN (conversion ladder; 457(b) has no 10%) | — |

### Plan 1, attacked

- Text: §530A(h)(1), (h)(3) and (h)(5) are each limited to years before the 18th birthday; (h)(4) ("Section 408(d)(2)
  shall be applied separately with respect to Trump Accounts and other individual retirement plans") is not. Proposed
  Reg. REG-117270-25 (9 Mar 2026): after the growth period the §408 rules apply "except as provided in section
  530A(h)" and "the contribution limits of section 408(a)(1) generally apply". So it is not a model artifact.
- Already published: the non-aggregation itself (Slott Report / Ian Berger: "can never be aggregated with other IRAs";
  rothirahub.com). Not found in 3 searches: using it for post-18 non-deductible contributions.
- Defeaters: §530A(a) lets Treasury depart from IRA treatment by regulation, and the post-18 rules are still
  "reserved"; only people who had an account before 18 qualify (first usable 2027, material only once they are high
  earners with pre-tax IRAs); lost if the account is moved into an ordinary IRA; step-transaction risk as for any
  backdoor Roth; the same result is already available to anyone whose employer plan takes roll-ins.

### Plan 2, attacked

- Each piece is known (basis isolation by roll-in; QHFD is includible-first; a non-dependent adult child on a family
  HDHP has the family limit). The combination on a Trump account was not found in 1 search.
- Defeaters: most 18-year-olds are dependents, and the model then closes the HSA moves (S3m: only the taxable
  conversion remains); a teenager's employer plan rarely takes roll-ins; one QHFD per lifetime; 12-month testing
  period; §408(d)(9)(E) aggregates "all individual retirement plans" while §530A(h)(4) separates only §408(d)(2), so
  the ordering between the two is my reading.

## Traps found

- **Failing the last-month rule is cheap (S1d).** HDHP only in December, none next year: the search still prefers the
  full $9,550 (+$1,790) to the pro-rated $795 (+$477 by the same formula). §223(b)(8)(B) takes back the deduction plus
  10%, but the money stays in the HSA and is not an excess contribution. Known among HSA specialists.
- **QCD after deductible contributions (S2).** §408(d)(8)(A) cuts the exclusion by every §219 deduction since 70½; the
  search never combines the two.
- **529 → Roth annual cap double-counts traditional IRA contributions.** §529(c)(3)(E)(ii)(I): the §408A(c)(2) amount
  (already net of non-Roth IRA contributions) "reduced by" contributions to all individual retirement plans. Encoded
  literally; a $2,000 traditional contribution costs $4,000 of transfer room.
- **QHFD uses HSA room at half the value of cash (S1).** Worth it only when cash is short.

## Drafting gaps noticed (not modelled unless stated)

- §457(e)(18)(A)(ii) as amended in 2022: the governmental 457(b) age-50 increase is "the lesser of any designated Roth
  contributions … or" the catch-up amount, for every participant, not only those above $145,000. Encoded literally;
  S6 always makes that catch-up as Roth.
- §402(g)(1) no longer has the subparagraph (C) that raised the limit for catch-ups (the known SECURE 2.0 §603 error).
- §223(b)(6) denies a dependent the "deduction" but does not set the limitation to zero (contrast (b)(7)); §408(d)(9)
  is an exclusion measured by "the annual limitation under section 223(b)". A dependent's QHFD is arguably open. The
  model closes it.
- §530A has no gift-tax rule like §529(c)(2); contributions locked until 18 may be future interests.
- §529(c)(3)(E) does not say how the transferred earnings sit in the Roth ordering rules of §408A(d)(4).
- §402A(a)(2)–(3) employer Roth contributions are income but not FICA wages (§3121(a)(5)); FICA is outside the model.

## Sources checked (4 searches, 3 pages)

- REG-117270-25, Trump Accounts, proposed rule (Federal Register 2026-04533), §1.530A-1(b)(2)–(3).
- cgmwealthadvisors.com, "How Trump accounts work" (Ian Berger) — via search summary; the page itself failed to load.
- rothirahub.com/trump-accounts — non-aggregation rule; nothing on post-18 non-deductible contributions.
- Fidelity, Kiplinger, Carson, Morningstar (search summaries) — conversion at 18 and kiddie tax; Morningstar says
  "basis aggregation" applies after 18, which contradicts §530A(h)(4).
