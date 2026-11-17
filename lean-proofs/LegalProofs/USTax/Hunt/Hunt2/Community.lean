import Std

/-!
# Community property and separate returns

Rules:
* Community property (AZ, CA, ID, LA, NV, NM, TX, WA, WI): each spouse's wages and income from community property
  are owned half by each, so on separate returns each spouse reports half (Poe v. Seaborn, 282 U.S. 101 (1930);
  Pub. 555). §66(a) undoes the split only for spouses who live apart all year. §1402(a)(5)(A): self-employment
  income stays with the spouse carrying on the business for the self-employment tax (`sec.py 1402 a 5`).
* §1(j)(2)(A), (D) for 2026 (Rev. Proc. 2025-32 Tables 1 and 4): every joint bracket edge is exactly twice the
  separate one (24,800/12,400 ... 768,700/384,350); §63(c)(2) separate standard deduction is half the joint one.
* §163(h)(4)(C)(i): qualified passenger vehicle loan interest "shall not exceed $10,000" per taxpayer, with no
  halving for a separate return and no joint-return requirement; (C)(ii) phase-down $200 per $1,000 (or part) of
  modified AGI over $100,000 ($200,000 joint).
* §1411(b): threshold $250,000 joint, $125,000 separate (half).

Results (kernel-checked below):
1. `split_neutral`: with income split equally, two separate returns pay exactly the joint tax (2026 schedule).
   So in a community-property State separate filing costs nothing in rates; in a common-law State it costs the
   bracket difference whenever the spouses' incomes differ.
2. `car_cap_doubles`: a couple with $20,000 of qualifying interest, splitting community interest and income equally,
   deducts $20,000 on two separate returns against $10,000 on a joint return, at any income where the joint
   deduction is not phased down; the taxable income of the pair falls by $10,000 more.
3. `niit_split_kills`: the known plan of putting the investment income on one separate return and the wages on the
   other cannot work for community income: each return gets half of each, and with half the threshold the tax is
   exactly half the joint tax.
-/

namespace Legal.USTax.Hunt.Hunt2.Community

/-- 2026 separate-return schedule, tax in cents (rate in percent x dollars) -/
def taxMFS (t : Int) : Int :=
  10 * max 0 (min t 12400) + 12 * max 0 (min t 50400 - 12400) + 22 * max 0 (min t 105700 - 50400)
  + 24 * max 0 (min t 201775 - 105700) + 32 * max 0 (min t 256225 - 201775)
  + 35 * max 0 (min t 384350 - 256225) + 37 * max 0 (t - 384350)

/-- 2026 joint schedule, tax in cents -/
def taxMFJ (t : Int) : Int :=
  10 * max 0 (min t 24800) + 12 * max 0 (min t 100800 - 24800) + 22 * max 0 (min t 211400 - 100800)
  + 24 * max 0 (min t 403550 - 211400) + 32 * max 0 (min t 512450 - 403550)
  + 35 * max 0 (min t 768700 - 512450) + 37 * max 0 (t - 768700)

#guard taxMFJ 100800 = 1160000   -- $11,600, Rev. Proc. 2025-32 Table 1
#guard taxMFS 384350 = 10329175  -- $103,291.75, Table 4

/-- Result 1: equal split, two separate returns = one joint return, for every taxable income. -/
theorem split_neutral (t : Int) : 2 * taxMFS t = taxMFJ (2 * t) := by
  unfold taxMFS taxMFJ
  omega

/-- §163(h)(4)(C): deduction for interest `i` at modified AGI `m`, per return; `thr` = 100,000 or 200,000.
"$200 for each $1,000 (or portion thereof)": the number of started thousands is `(m - thr + 999) / 1000`. -/
def carDed (i m thr : Int) : Int :=
  max 0 (min i 10000 - 200 * max 0 ((m - thr + 999) / 1000))

/-- Result 2: equal split of $20,000 interest and of modified AGI `2m` (each spouse `m`). -/
theorem car_cap_doubles (m : Int) (hm : 0 ≤ m) (hlow : m ≤ 100000) :
    carDed 20000 (2 * m) 200000 = 10000 ∧ carDed 10000 m 100000 + carDed 10000 m 100000 = 20000 := by
  unfold carDed
  constructor <;> omega

/-- With the deduction taken before the schedule, the separate pair pays less than the joint return by the
schedule's value of the extra $10,000: here at least 10% of it. -/
theorem car_cap_saves (t : Int) (ht : 10000 ≤ t) :
    2 * taxMFS (t - 10000) + 100000 ≤ taxMFJ (2 * t - 10000) := by
  unfold taxMFS taxMFJ
  omega

/-- §1411(a)(1): 3.8% of the lesser of net investment income `n` and MAGI `m` over the threshold (in tenths of a
percent x dollars). -/
def niit (n m thr : Int) : Int := 38 * max 0 (min n (m - thr))

/-- Result 3: community income split equally - two separate returns owe exactly half the joint tax each,
whatever the mix of wages and investment income. -/
theorem niit_split_kills (n w : Int) (hn : 0 ≤ n) (hw : 0 ≤ w) :
    niit n (n + w) 250000 = 2 * niit (n / 2) (n / 2 + w / 2) 125000 ∨
    niit n (n + w) 250000 ≤ 2 * niit (n / 2) (n / 2 + w / 2) 125000 + 76 := by
  unfold niit
  omega

end Legal.USTax.Hunt.Hunt2.Community

open Legal.USTax.Hunt.Hunt2.Community in
#print axioms split_neutral
open Legal.USTax.Hunt.Hunt2.Community in
#print axioms car_cap_doubles
open Legal.USTax.Hunt.Hunt2.Community in
#print axioms car_cap_saves
open Legal.USTax.Hunt.Hunt2.Community in
#print axioms niit_split_kills
