# RED: Accounts, scenario S4 ("VARIANT 1")

Plan attacked: an adult who still holds a childhood Trump account puts $7,000 a year of non-deductible money into it
and converts that account alone to a Roth IRA, with nothing included in income despite $100,000 of pre-tax money in
another traditional IRA. Claimed gain: +$3,500 over two years against a baseline of 125,000.

**Verdict: holds on the text.** I could not break the legal reading, and the IRS's own notice states it. What I did
break is the size and the novelty of the claim: the +$3,500 is a valuation premium, not tax saved; it vanishes in
four ordinary variations of the facts; and the search contributed nothing a reader of §530A(h)(4) would not see.

All files are in this folder. `gen.py` builds every `Red*.lean` from `RedRules.txt` (lines 1–639 of the original,
unedited) so each file is self-contained; run with `lake env lean LegalProofs/USTax/Hunt/Audit/Accounts/<file>`.
Outputs are the `red*.out` files. The original files were not edited.

## Tests

### T1 Text fidelity: partial

Read against §530A (all), §408(a)(1), (d)(1)–(3), (o), §408A(d)(3), (e), §219(b)(5), (g), §4973(b).

What the plan needs, and what the words say:

| Step in the encoding | Statute | Finding |
|---|---|---|
| `taAdult`: contributions to the Trump account from the year of the 18th birthday, under the ordinary IRA limit, shared with other IRAs | §530A(b)(1)(C)(i)(II), (c)(1)–(2), (h)(3) all stop at that year; §530A(a) then applies §408(a)(1) | Faithful. The contribution counts against the one $7,000 limit (`iraYr`), as (h)(3)'s age limit requires. |
| The account is still a "Trump account" | §530A(b)(1)(B) designation is made once; (d)(6)(B) is the only "cease to be a Trump account" rule | Faithful. |
| `taConvert`: ratio over the Trump account alone | §530A(h)(4), no age limit; §408A(d)(3)(C) | Faithful. |
| Ratio taken at the moment of the move | §408(d)(2)(C): year-end value plus the year's distributions | Not generous: a later contribution in the same year can only raise the basis share. Same result for this plan (account empty at year end). |

Missing restrictions and scenario facts that carry the result (none is a misreading of §530A, all change the figure):

1. **The gain is the objective's 25% premium and nothing else.** `beta := 0` gives "nothing beats the baseline"
   (T1-d). No tax is saved against doing nothing; the tax avoided against the same contributions through the
   ordinary IRA is $4,298 (35% of $12,281).
2. **The baseline leaves out the known alternative.** The model has no move that rolls the ordinary IRA into an
   employer plan (§408(d)(3)(A)(ii)); only the Trump account gets one. With the $100,000 already in a plan the
   baseline itself reaches 128,500 and the plan adds nothing (T1-f). The findings file admits this in a subordinate
   clause.
3. **`iraDeductible := false` with `has401k := false` is an odd pair.** §219(g) denies the deduction only to an
   active participant in an employer plan. If the deduction is allowed, the baseline rises to 129,200 and the plan
   adds nothing (T1-e).
4. **Equal rates now and later:** the baseline converts the whole IRA and the plan adds nothing (T1-g).
5. **"Empty Trump account" is a fact, not law.** A real account holds seed money and growth, which §530A(d)(2)
   keeps out of basis. $5,000 of it: +$3,250 (T1-a). $70,000 of it: nothing (T1-c). Break-even is where 5% of the
   pre-tax balance equals $3,500.
6. **Survival of the account is assumed.** `hasTA` never switches off. Under Notice 2025-68 Q&A A-10 the governing
   instrument may move everything to an ordinary IRA at 18; under §1.530A-1T(c)(6) a trustee may close an unfunded
   account; an auto account claimed after 18 goes to a non-Trump IRA (§1.530A-1T(f)). Any of these ends the plan.
7. `taAdult` exists only for this plan and S3's families. It is one move away from the result: with the three move
   kinds the plan uses the whole search is 14 positions (T3-E).
8. Stale citation: the findings rely on REG-117270-25, withdrawn on 30 Sep 2026 and replaced by T.D. 10056 and
   CC-00226466-26. The replacement says the same thing on this point.

Strict re-run: with every fact above set against the plan one at a time, the plan survives only (a) with a funded
account (+$3,250, +$12,500 of which $9,000 is the already-known conversion at 18, T1-b) and (b) as the original.

### T2 Close the gap: pass

Words added to §530A(h)(4): "**For any taxable year beginning before the first day of the calendar year in which the
account beneficiary attains age 18,** section 408(d)(2) shall be applied separately…". Encoded as `aggTake` in
`RedT2.lean` (one pooled contract from that year on). All 15 scenarios re-run (64 s):

- S4: "nothing beats the baseline" (was +3,500).
- All 15 baselines identical to `final-run.txt`.
- S3's best stays +15,250. S3 gains new families (+13,822, +12,576) in which a non-deductible ordinary IRA
  contribution lends basis to the Trump-account conversion: the ordinary consequence of pooling, not a leak.

### T3 Ablation: pass

| Run | Result |
|---|---|
| A original move set | +3,500, 566 positions |
| B without Trump contribution (18+) | nothing |
| C without Trump → Roth conversion | nothing |
| D without next-year | +1,750 (scale only: one year instead of two) |
| E only the plan's three kinds | +3,500, 14 positions |
| F all 35 kinds, depth 6 | +3,500, 1,690 positions |

### T4 Earlier law: pass

`RedT4.lean`: the Code without §530A (every Trump-account move undefined). S4 move set: nothing above 125,000 (443
positions). All move kinds, depth 6: nothing (1,334 positions). Matches S4b.

### T5 Free lunch: pass

`RedT5.lean`, unmodified rules, every position reached:

- S4 (566 positions; all kinds, 1,690): pre-tax dollars inside + dollars taxed − dollars deducted = 100,000 in every
  position; no deduction anywhere; no position where pre-tax money left with zero tax; untaxed Roth money never
  above 2 × $7,000; worth never above 128,500.
- All 15 scenarios (240,816 positions in total at their own move sets): 0 conservation violations (assets less
  pledges constant), 0 positions with basis above balance, 0 with the IRA limit exceeded.

The plan creates no money and removes no pre-tax dollar; it only keeps new basis away from old pre-tax money.

### T6 Kernel: pass

`RedT6open.lean` (unmodified `step`), `by decide`, full state, no cut:

- `red_plan_replay`: the four moves are legal and end at cash 16,000, IRA 100,000, Roth untaxed 14,000, income 0.
- `red_plan_worth` = 128,500; `red_start_worth` = 125,000.
- `red_ordinary_backdoor`: same dollars through the ordinary IRA: income 12,281.

`RedT6closed.lean` (closed rule):

- `red_closed_replay`: same four moves, income 12,281; `red_closed_worth` = 124,815.
- `red_closed_no_free_conversion`, `red_closed_plan_unreachable`: **for every move sequence**, any amounts, any
  horizon, any contribution limit, from S4's start, nothing is converted without income being recognised. Proved by
  induction on the list over a cut-down model of my own (five move kinds, pooled basis), not over the original
  `step`. The cut-down agrees with the full closed `step` on all 4,243 (position, move) pairs of the S4 search (1,323
  positions, 0 disagreements), but that agreement is a compiled `#eval`, not a proof.

Axioms: replays `[propext]`; universal theorems `[propext, Classical.choice, Quot.sound]`. No `sorryAx`, no
`Lean.ofReduceBool`, no axioms of mine. "Nothing beats the baseline" under the closed rule for the full model is
`#eval` only.

### T7 Independent arithmetic: pass

`red_t7.py`, written from §72(e)(8), §408(d)(2)(C), §408(o), §530A(h)(4): plan income 0; ordinary route income
$12,280.70 (Lean 12,281); baseline 125,000; plan 128,500; gain 3,500; gain with no premium 0; seeded account +3,250.
All agree.

### T8 Outside the statute: pass (authority supports; nothing closes it; the pieces are published, the plan is not)

8 searches, 3 primary documents read in full text (PDF), 4 practitioner pages.

- **Notice 2025-68** (IRS, 2 Dec 2025), https://www.irs.gov/pub/irs-drop/n-25-68.pdf
  - Overview: "a Trump account continues to be a Trump account after the growth period… an account initially
    established as a Trump account can never be aggregated with other individual retirement arrangements when
    allocating basis related to a distribution from either the Trump account or another individual retirement
    arrangement."
  - Q&A G-1: "at all times, Trump accounts are disregarded for purposes of determining the portion of a distribution
    from a traditional individual retirement arrangement that is not a Trump account that is allocated to basis."
    Then: "The Treasury Department and the IRS anticipate issuing additional guidance with respect to this tax
    treatment".
  - Q&A A-9: "after the end of the growth period, the limit on contributions is governed by section 408(a)(1)."
  - Overview: after the growth period the §408 rules apply, "such as the rules related to contributions,
    distributions, required minimum distributions, rollovers, Roth conversions".
  - Q&A A-10: the instrument may provide that "immediately after the growth period, all of the assets of the Trump
    account will be transferred to a traditional IRA … that is not a Trump account".
- **T.D. 10056**, temporary §1.530A-1T (30 Sep 2026, expires 30 Sep 2029),
  https://public-inspection.federalregister.gov/2026-20026.pdf: (c)(4)(ii) "the rules under section 408 that apply
  to other traditional IRAs are generally applicable to Trump accounts, except as provided in section 530A(h)";
  (c)(6) "an unfunded Trump account that is not an auto account may be closed by the trustee if provided by the
  terms of the written governing instrument". Nothing on post-18 basis.
- **CC-00226466-26** (same day), https://public-inspection.federalregister.gov/2026-20027.pdf: withdraws
  REG-117270-25; silent on this.
- Practitioner: rothirahub.com/trump-accounts (updated 15 Oct 2026) states the separation "is preserved on Roth
  conversion", that "A retained Trump Account generally follows ordinary IRA contribution timing and eligibility
  rules", and that moving to a non-Trump IRA "ends this special separation". Kitces (24 Dec 2025): "Starting in the
  year the beneficiary turns 18, the contribution limit for standard IRAs applies". back9ins (28 Jul 2026):
  non-aggregation confirmed. None joins the two into an adult backdoor Roth that sidesteps other pre-tax IRAs.

Not retrieved: Form 8606 instructions for 2026 (whether the form has a separate Trump-account computation); the
Slott Report mailbag on cgmwealthadvisors.com (TLS error; the irahelp.com copy is from Aug 2025 and is about
eligibility only); the final text of 91 FR for T.D. 10056 (read the public-inspection copy); federalregister.gov HTML
(blocked). No committee report searched.

## Weaknesses, ranked

1. **The search is decoration.** The result is one reading of one sentence, entered as two moves (`taAdult`,
   `taConvert`); 14 positions find it. It is not circular (the moves follow the text and the Notice), but "the blind
   search found it" overstates what happened.
2. **The dollar figure is the objective, not the Code.** +$3,500 is 25% × $14,000. Zero premium, zero gain.
3. **Narrow facts.** No gain if the deduction is allowed, if the employer plan takes roll-ins, if rates are equal,
   or if the account holds about $70,000 of untaxed seed money and growth. The baseline omits the roll-in route.
4. **The account must survive to adulthood as a Trump account.** Treasury has already blessed instruments that end
   it at 18, and trustees may close empty ones. First usable by people turning 18 in 2027 or later.
5. **Treasury can end it without Congress.** §530A(a) lets regulations depart from IRA treatment, and G-1 announces
   more guidance on exactly this treatment.
6. **Half-published.** Non-aggregation "at all times" and post-18 contributions under §408(a)(1) are both in Notice
   2025-68 and in practitioner pages. The combination was not found in 8 searches, which is weak evidence of
   novelty.
7. The universal kernel theorem is over my cut-down model; its link to the full model is tested, not proved.
8. The findings cite a withdrawn proposed regulation.
