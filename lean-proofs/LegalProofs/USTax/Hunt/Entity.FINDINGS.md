# Entity: how an owner-worker takes money out of a business

File: `LegalProofs/USTax/Hunt/Entity.lean` (run: `lake env lean LegalProofs/USTax/Hunt/Entity.lean`, about 25 s).
Raw output of the last run: `tools/hunt/out/Entity/run3.txt`.

**Result in one line: nothing novel survived.** The blind search rediscovered the standard playbook, and the two
2025-law items it surfaced (§45F for a one-owner business, §128 for an owner's family) turned out to be already
published or already addressed by proposed regulations.

## Setting

Married couple filing jointly, spouse with no other income, one child under 18, standard deduction. Business profit
$150k / $400k / $1M a year before anything paid to or for the family. Fixed household costs paid in every case:
health premiums $24,000, home office $6,000, licensed day care $20,000. Value of services actually rendered: spouse
$30,000, child $12,000, owner $120,000 (or half the profit if lower). Objective: all federal tax paid by the
corporation and the family (income, SE/FICA, additional Medicare, NIIT, corporate, accumulated earnings), plus 22% of
money left in pre-tax plans and Trump accounts. Baseline: sole proprietorship, no moves.

2026 figures, from memory and not re-checked against Rev. Proc. 2025-32: standard deduction $32,200, joint brackets,
wage base $184,500, §199A threshold $403,500, §402(g) $24,500, §415(c) $72,000, 0%/15% capital gain breakpoints
$98,900 / $613,700.

## Provisions encoded (text read with `tools/hunt/sec.py`)

§1 (brackets, (h) incl. (h)(4),(7) 28% gain, (h)(11)); §11; §38(c)(1); §45F (2025); §62(a)(2)(A),(c); §63(c)(5);
§105(b),(g), §106(a); §128 (2025) with §530A limit; §162(a)(1),(a)(3),(l); §164(f); §199A(a)–(e) with the 2026
$150,000 range, SSTB, W-2 limit; §280A(c)(1),(g); §301/§316 dividends; §351; §401(a)(17), §401(c)(2), §402(g),
§404(a)(3),(a)(8), §415(c); §531, §533, §535(c); §1202(a),(b),(c),(d),(e),(i) as amended 2025; §1362(a),(d),(g);
§1366–§1368; §1372; §1401, §1402(a),(a)(12),(a)(13),(b); §1411(a)–(c); §3101, §3111, §3121(a)(2),(a)(5),(a)(18),
(b)(3),(d)(1),(v)(1).

Read but left out, with the reason: §127(b)(3) and §129(d)(4) (owner-family share capped at 5% / 25%, impossible
with a family-only workforce); §119, §132 (no tax difference from an ordinary business expense); §125 (no separate
effect once the underlying benefit is modelled); §§541–547 (no investment income in the model; §543(a)(7) personal
service contracts noted as a risk for a one-person service C corporation); §461(l) (no losses with positive profit);
§1374 (a stock sale does not trigger it); §224, §225 (see gaps).

Two switches separate the Code's text from doctrine: `rcFloor` (a corporation must pay the owner-worker at least the
value of his services: Rev. Rul. 74-44 and case law, applied to S and C alike) and `lpLiteral` ("limited partner" in
§1402(a)(13) means a state-law limited partner even if he works). Default: floor on, literal off.

## Search size

Nine searches, about 280,000 positions and 37,500 complete plans, up to 1,100 families (set of move kinds used) per
search. One-year searches are exhaustive over every order of 13 move kinds with amounts taken from limits and
thresholds. Five-year searches use entity change, salary, dividend/retain and sale only, keeping the cheapest position
per carried state (retained cash in $10,000 bands, per family).

## Plans that beat the baseline

Dollar effect is per year at $400k profit unless stated; "floor" = owner salary at least $120,000.

| # | Plan (moves) | Effect vs baseline | Provisions combined | Class | What could defeat it | Checked |
|---|---|---|---|---|---|---|
| 1 | S election, salary at floor, distribute the rest | +$9,280 with health plan; $20,980 over 5 years salary-only | §1366, §1402(a), §3121, §199A | KNOWN: S-corp reasonable-salary split | Reasonable-compensation recharacterisation; at $1M service field the §199A loss narrows it | – |
| 2 | Business rents the home 14 days | +$2,150 to +$4,017 | §162(a)(3), §280A(g) | KNOWN: Augusta rule | Rent above fair value, no business purpose (Sinopoli) | – |
| 3 | Accountable plan for home office after incorporating | +$1,152 to +$2,152 | §62(a)(2)(A),(c) | KNOWN | Substantiation | – |
| 4 | Child on payroll | +$644 (corp) to +$2,796; $4,802 as sole prop at $1M | §162, §63(c)(5), §3121(b)(3)(A) | KNOWN | Wage above value of services | – |
| 5 | Corporation pays the family premiums | +$8,605 in a C corp; in an S corp it only restores the §162(l) deduction | §106, §1372, §162(l) | KNOWN | – | – |
| 6 | Sole prop: spouse-employee family health plan | +$780 net of the cost of hiring | §105(b), §106, §162 | KNOWN: "§105 plan" | Spouse not a real employee; spouse as co-owner | – |
| 7 | Owner 401(k) deferral / profit sharing | −$3,400 to +$8,700 depending on bracket and the 22% assumption | §402(g), §404, §415(c), §199A | KNOWN: solo 401(k) | – | – |
| 8 | C corp from year 1, salary $250k, retain within the §535(c) credit, sell after 5 years | +$55,780 over 5 years (non-service field, $1M goodwill) | §11, §535(c), §1202 (2025), §1411 | KNOWN: QSBS | Buyer wants assets, not stock; §1202(e) asset tests; service fields excluded (then S corp wins, C corp loses) | – |
| 9 | No salary floor: S corp with $24,500 salary | +$30,650 | text of §§1366, 3121 | KNOWN, and defeated by reasonable-compensation doctrine | Rev. Rul. 74-44, Radtke, Watson | – |
| 10 | Limited partnership, no guaranteed payment, plus spouse-employee health plan | +$30,505 ($48,049 at $1M service field) | §1402(a)(13), §1411(c)(2), §105/§106, §199A | KNOWN core (Sirius Solutions, 5th Cir., 16 Jan 2026, 2–1); the health-plan pairing is a VARIANT | Tax Court's Soroban test outside the 5th Circuit; en banc petition filed April 2026; guaranteed-payment recharacterisation (§707(c)) | 1 search |
| 11 | Business contracts with the licensed day-care centre for its employee's own child, 50% credit | +$4,354 (S corp); +$4,385 as sole prop through a $10,000 spouse-employee | §45F(a)(1),(c)(1)(A)(iii),(c)(4),(f)(2) (2025), §38(c), §1372 does not reach a credit | VARIANT, already published | §45F(c)(2)(B)(iii) discrimination test when every employee is highly compensated; guidance under §45F(g); sources disagree whether owner-only use qualifies | 1 search: a 2026 practitioner post describes exactly this; another site says no |
| 12 | Proprietor's child-employee (and spouse-employee) gets a Trump account contribution | +$11 a year at a 22% later rate, +$311 at 10% ($561 less tax now on $2,500 deferred) | §128, §530A, §162, §3121(b)(3)(A) | VARIANT, immaterial | Total pay must stay reasonable; §129(d)(2),(3),(8) tests as applied by REG-101355-26 | 3 searches: proposed regs (Aug 2026) already confirm no owner cap, no FICA exclusion, and exclude proprietors, partners and 2% S shareholders |

CANDIDATE: none.

## Traps the search exposed

- Putting the spouse on payroll loses money in every family except where it unlocks #6 or #11: −$160 to −$1,864 at
  $400k (a second set of FICA with no offsetting saving).
- S corp without the health-plan move: the $24,000 premium deduction disappears entirely (§162(l) needs the
  corporation to pay and wages to cover it). Same in a limited partnership with no guaranteed payment: earned income is
  zero, so no §162(l) deduction and no retirement-plan room.
- At $150k profit a 401(k) deferral is a net loss under the 22% assumption (−$2,400 to −$3,400): it also shrinks the
  §199A deduction.
- C corp then S election: worse than never incorporating (−$18,367 over 5 years); it also ends §1202 eligibility.
- §1202(e)(6): after two years working capital can count for at most half the assets, so a corporation whose value is
  mostly retained cash fails the 80% test; retention only works alongside real goodwill.
- §128 and §45F at the edge: adding them when salary is already at the §162 ceiling pushes the plan out of the allowed
  set (the large negative "adding" figures in the output are this, not a tax cost).

## Drafting gaps noticed

- §1401(b)(2)(B) refers to wages taxed under "section 3121(b)(2)"; the additional Medicare tax on wages is §3101(b)(2).
- §128(c) imports §129(d)(2),(3),(6),(7),(8) but not (d)(4), the owner-concentration cap; §3121(a)(18) was not
  amended to list §128, so the contribution is excluded from income but not from FICA wages. Both now acknowledged
  in the proposed regulations.
- §128(b)(1) limits by employee, §530A by account: two employed parents reach the $5,000 account limit pre-tax.
- §1372 reaches "employee fringe benefits" only, so a 2% S shareholder is not an employee for §128 but is one for
  §45F; and §1372(b) attribution makes the owner's spouse and child 2% shareholders too, which a sole proprietorship
  has no counterpart for.
- §401(c)(2)(A)(vi) subtracts the §164(f) deduction from net earnings that §1402(a)(12) has already reduced "in lieu
  of" it; read literally the half-SE-tax adjustment is taken twice (practice follows Pub. 560, once).
- §1366(e) authorises reasonable-compensation adjustments only for a family member of a shareholder; nothing in the
  Code sets a salary floor for a sole shareholder.
- §199A SSTB list drops engineering and architecture; §1202(e)(3)(A) and §535(c)(2)(B) keep them: an engineering
  firm gets the full §199A deduction but neither QSBS nor the $250,000 credit.
- Not modelled: §225 overtime deduction for a family employee (turns on FLSA coverage, Title 29); §224 tips for an
  owner-operator; state pass-through entity tax; §543(a)(7).
- The local text of §461(l)(1) reads "before January 1, 2027"; worth checking against the 2025 amendment.

## Model limits that matter

No investment return on retained cash; unused §45F credit is dropped rather than carried; the sale is stacked on a
year like the last; total-compensation reasonableness is checked per move, not across fringe benefits; Social
Security benefit accrual, child tax credit phase-out, AMT and state tax are ignored.

## Sources checked (5 of 6 searches)

- https://www.currentfederaltaxdevelopments.com/blog/2026/1/16/fifth-circuit-vacates-tax-court-in-sirius-solutions-a-return-to-statutory-text-for-section-1402a13
- https://www.everycrsreport.com/reports/LSB11425.html
- https://getirshelp.com/blog/how-one-owner-businesses-can-win-big-with-the-new-50-employer-childcare-credit-in-2026/
- https://www.irs.gov/businesses/small-businesses-self-employed/employer-provided-child-care-credit-tax-year-2026-and-later
- https://taxnews.ey.com/news/2026-1779-employer-contribution-rules-for-trump-accounts-would-clarify-nondiscrimination-requirements-and-cafeteria-plan-administration
- https://www.journalofaccountancy.com/news/2026/aug/trump-account-prop-regs-clarify-2500-limit-for-workers/
- https://www.mayerbrown.com/en/insights/publications/2026/08/irs-issues-proposed-regulations-on-employer-contributions-to-trump-accounts-and-nondiscrimination-rules-for-dependent-care-assistance-programs
