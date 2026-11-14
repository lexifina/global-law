import LegalProofs.USTax.Entity.Corp

/-!
# The entity rules against the regulations' own examples

Each test restates an example from the Treasury regulations (or, where none exists, a computation read straight off
the statute) and checks the rule in `Partnership.lean` / `Corp.lean` gives the regulation's figures.
-/

set_option maxRecDepth 20000

namespace Legal.USTax.Entity.Tests
open Legal.USTax.Entity TaxCode.Individual

/-! ## Reg. §1.704-3(b)(2) Example 1: the traditional method and the ceiling rule
A contributes property, basis $4,000, book $10,000, 10 years left (straight line); B contributes $10,000 cash; 50/50.
Book depreciation $1,000 ($500 each), tax $400, all to B. At the start of year 2, a sale for $9,000 gives A all $5,400
of gain; a sale for $10,000 gives A $5,400 plus half the $1,000 book gain, B the other $500. -/
def ex1 : Contributed := ⟨10000, 4000, 10, 10⟩
theorem trad_year1 : yearAlloc .traditional ex1 5000 0 0 = ⟨0, -400, -500, -500⟩ := by decide
theorem trad_capital : 4000 + (yearAlloc .traditional ex1 5000 0 0).cTax = 4000 ∧
    10000 + (yearAlloc .traditional ex1 5000 0 0).nTax = 9600 := by decide
theorem trad_sale_9000 : (saleAlloc .traditional ex1 5000 0 1 9000).cTax = 5400 ∧
    (saleAlloc .traditional ex1 5000 0 1 9000).nTax = 0 := by decide
theorem trad_sale_10000 : (saleAlloc .traditional ex1 5000 0 1 10000).cTax = 5900 ∧
    (saleAlloc .traditional ex1 5000 0 1 10000).nTax = 500 := by decide

/-! ## Reg. §1.704-3(b)(2) Example 2: the unreasonable use of the traditional method
C contributes equipment, basis $1,000, book $10,000, one year left; D contributes $10,000 cash; 50/50. Year 1: book
depreciation $10,000 ($5,000 each), tax $1,000 all to D. Year 2: sale for $10,000, $5,000 of gain to each. Of C's
$9,000 precontribution gain C reports $5,000 and D, net, $4,000: "$4,000 of [C's] precontribution gain" shifted. -/
def ex2 : Contributed := ⟨10000, 1000, 1, 1⟩
theorem ex2_shift :
    (yearAlloc .traditional ex2 5000 0 0).cTax + (saleAlloc .traditional ex2 5000 0 1 10000).cTax = 5000 ∧
    (yearAlloc .traditional ex2 5000 0 0).nTax + (saleAlloc .traditional ex2 5000 0 1 10000).nTax = 4000 := by decide
/-- Under the remedial method (a 10-year new life for the $9,000 excess) D's tax deductions equal its $5,000 of book
depreciation, and C, net of its $1,000 of basis, takes $4,000 of income: C's tax capital ends equal to its book
capital, so no precontribution gain is left for a sale to shift. -/
theorem ex2_remedial :
    sumTo (fun t => (yearAlloc .remedial ⟨10000, 1000, 1, 10⟩ 5000 0 t).cTax) 10 = 4000 ∧
    sumTo (fun t => (yearAlloc .remedial ⟨10000, 1000, 1, 10⟩ 5000 0 t).nTax) 10 = -5000 := by decide

/-! ## Reg. §1.704-3(c)(4) Example 1: curative allocations
E contributes equipment, basis $4,000, book $10,000, 10 years left; F's $10,000 buys inventory sold for $10,700 ($700 of
income); 50/50. Traditional: tax capital E $4,350, F $9,950. A reasonable curative allocation of $100 of the
inventory income to E: E $4,450, F $9,850. -/
theorem curative_trad : 4000 + (yearAlloc .traditional ex1 5000 700 0).cTax = 4350 ∧
    10000 + (yearAlloc .traditional ex1 5000 700 0).nTax = 9950 := by decide
theorem curative_cure : 4000 + (yearAlloc .curative ex1 5000 700 0).cTax = 4450 ∧
    10000 + (yearAlloc .curative ex1 5000 700 0).nTax = 9850 ∧
    10000 + (yearAlloc .curative ex1 5000 700 0).nBook = 9850 := by decide

/-! ## Reg. §1.704-3(d)(7) Example 1: the remedial method
L contributes property, basis $4,000, value $10,000, 4 years left of a 10-year period; M contributes $10,000; 50/50.
Years 1–4: book $1,600 ($800 each); tax $1,000: $800 to M, $200 to L. End of year 4: tax capital L $3,200, M $6,800.
Years 5–10: book $600; no tax depreciation; $300 remedial deduction to M and $300 remedial income to L each year.
End of year 5: L $3,500, M $6,500; end of year 10: $5,000 each. -/
def ex4 : Contributed := ⟨10000, 4000, 4, 10⟩
theorem remedial_y1 : yearAlloc .remedial ex4 5000 0 0 = ⟨-200, -800, -800, -800⟩ := by decide
theorem remedial_y4 : 4000 + sumTo (fun t => (yearAlloc .remedial ex4 5000 0 t).cTax) 4 = 3200 ∧
    10000 + sumTo (fun t => (yearAlloc .remedial ex4 5000 0 t).nTax) 4 = 6800 := by decide
theorem remedial_y5 : 4000 + sumTo (fun t => (yearAlloc .remedial ex4 5000 0 t).cTax) 5 = 3500 ∧
    10000 + sumTo (fun t => (yearAlloc .remedial ex4 5000 0 t).nTax) 5 = 6500 := by decide
theorem remedial_y10 : 4000 + sumTo (fun t => (yearAlloc .remedial ex4 5000 0 t).cTax) 10 = 5000 ∧
    10000 + sumTo (fun t => (yearAlloc .remedial ex4 5000 0 t).nTax) 10 = 5000 ∧
    bookValue .remedial ex4 10 = 0 := by decide

/-! ## Reg. §1.737-1(e) Examples 1 and 2
1: A contributed Property A (value $30,000, basis $20,000; at the end of 1997 book $21,000, tax $14,000) and receives
Property B ($30,000) in liquidation; A's basis $20,000. Excess distribution $10,000; net precontribution gain $7,000;
gain $7,000. 2: A's basis after liability shifts is $11,000, Property B is worth $9,000: no gain. -/
theorem s737_ex1 : gain737 3 30000 20000 0 (gain704c1B 3 21000 21000 14000) = 7000 := by decide
theorem s737_ex2 : gain737 4 9000 11000 0 6000 = 0 := by decide
/-- After seven years neither rule reaches the distribution. -/
theorem s737_after7 : gain737 7 30000 20000 0 7000 = 0 ∧ gain704c1B 7 21000 21000 14000 = 0 := by decide

/-! ## Reg. §1.743-1(d)(3) Example 1
A sells its one-third interest to T for $22,000; liabilities $10,000; assets worth $76,000 with basis $55,000.
T's basis $25,333; previously taxed capital $15,000; share of basis $18,333; adjustment $7,000. -/
theorem s743_ex1 : adj743 22000 10000 1 3 76000 55000 = 7000 := by decide

/-! ## Reg. §1.1368-3 Examples 1 and 2 -/
/-- Example 1 (1996 order): basis $10, income $50, losses $26, distribution $38: $34 tax-free, $4 gain, basis $0. -/
theorem s1368_ex1 : (sYear true 10 0 0 ⟨50, 26, 0, 38⟩).taxFree = 34 ∧ (sYear true 10 0 0 ⟨50, 26, 0, 38⟩).gain = 4 ∧
    (sYear true 10 0 0 ⟨50, 26, 0, 38⟩).basisAfter = 0 := by decide
/-- Example 2 (after 1996): basis $10, AAA $100, income $50, losses $20, nondeductible $6, distribution $38: all $38
tax-free, basis $0, $4 of loss suspended. -/
theorem s1368_ex2 : sYear false 10 100 0 ⟨50, 20, 6, 38⟩ = ⟨38, 0, 0, 0, 4, 92⟩ := by decide
/-- §1368(c): with $20 of AAA and $30 of accumulated E&P, a $70 distribution on $100 of basis is $20 under (b), a $30
dividend, and $20 more under (b). -/
theorem s1368_c : let r := sYear false 100 20 30 ⟨0, 0, 0, 70⟩; r.taxFree = 40 ∧ r.dividend = 30 ∧ r.basisAfter = 60 := by
  decide

/-! ## §1374, §11, §531 (read off the statute) -/
theorem s1374 : bigTax 4 1000000 3000000 600000 = 126000 ∧ bigTax 5 1000000 3000000 600000 = 0 ∧
    bigTax 0 1000000 400000 5000000 = 84000 := by decide
/-- $1,000,000 of taxable income, nothing paid out, no reasonable needs shown, no earlier E&P: tax $210,000; the
$250,000 minimum credit; accumulated taxable income $540,000; accumulated earnings tax $108,000. -/
theorem s531 : corpTax 1000000 = 210000 ∧ aet false 1000000 0 0 0 0 = 108000 ∧ aet false 1000000 0 790000 0 0 = 0 ∧
    aet true 1000000 0 0 0 0 = 128000 := by decide
/-- Reasonable needs of $600,000, none accumulated: the credit is $600,000; with $600,000 already accumulated the need
is met, and only the minimum credit ($250,000 less E&P, here nothing) is left. -/
theorem s535_needs : aet false 1000000 0 0 600000 0 = 38000 ∧ aet false 1000000 0 0 600000 600000 = 158000 := by decide

/-! ## §1202 (statute) -/
/-- A $20,000,000 gain on stock with $1,000,000 basis: the limit is the greater of $15,000,000 and 10 × $1,000,000.
At 5 years $15,000,000 is excluded and $5,000,000 is ordinary long-term gain; at 3 years half the $15,000,000 is
excluded and half is §1202 gain at 28 percent; under 3 years nothing is excluded. -/
theorem qsbs_5 : qsbsSplit { gain := 20000000, heldYears := 5, basisSold := 1000000 } = ⟨15000000, 0, 5000000, 15000000⟩ := by decide
theorem qsbs_3 : qsbsSplit { gain := 20000000, heldYears := 3, basisSold := 1000000 } = ⟨7500000, 7500000, 5000000, 15000000⟩ := by decide
theorem qsbs_4 : qsbsSplit { gain := 20000000, heldYears := 4, basisSold := 1000000 } = ⟨11250000, 3750000, 5000000, 15000000⟩ := by decide
theorem qsbs_2 : qsbsSplit { gain := 20000000, heldYears := 2, basisSold := 1000000 } = ⟨0, 0, 20000000, 0⟩ := by decide
/-- (b)(1)(B): $3,000,000 of basis sold makes the limit $30,000,000. (b)(4)(B): $15,000,000 used before leaves no dollar
limit, so only the 10× prong remains. (b)(3)(A): a separate return halves the dollar limit. Old stock: more than 5
years, $10,000,000. -/
theorem qsbs_limits :
    (qsbsSplit { gain := 40000000, heldYears := 6, basisSold := 3000000 }).excluded = 30000000 ∧
    (qsbsSplit { gain := 5000000, heldYears := 6, basisSold := 100000, priorUsed := 15000000 }).excluded = 1000000 ∧
    (qsbsSplit { gain := 20000000, heldYears := 6, basisSold := 0, separate := true }).excluded = 7500000 ∧
    (qsbsSplit { gain := 20000000, heldYears := 6, basisSold := 0, newStock := false }).excluded = 10000000 ∧
    (qsbsSplit { gain := 20000000, heldYears := 5, basisSold := 0, newStock := false }).excluded = 0 := by decide

/-- §1(h) with 28-percent gain: none of it, the ordinary schedule-and-worksheet tax; all of a joint return's
$1,000,000 of taxable income §1202 gain: the 10–24 percent rows on the first $394,600, then 28 percent. -/
theorem s1h_28 : taxWith28 .mfj 1000000 0 0 = C.regularTax .mfj 1000000 0 ∧
    taxWith28 .mfj 1000000 0 1000000 = C.line16Tax .mfj 394600 + (1000000 - 394600) * 28 / 100 := by decide

/-! ## Reg. §1.302-3(b): substantially disproportionate redemptions
400 shares, 100 each for A, B, C, D (unrelated). The corporation redeems 55 from A, 25 from B and 20 from C. To
qualify a shareholder must own less than 20 percent (80 percent of 25) of the 300 shares left: A owns 45 (15
percent), B 75 (25), C 80 (26⅔). Only A's redemption is substantially disproportionate. -/
def m : List Holder := [⟨100, []⟩, ⟨100, []⟩, ⟨100, []⟩, ⟨100, []⟩]
def mAfter : List Holder := [⟨45, []⟩, ⟨75, []⟩, ⟨80, []⟩, ⟨100, []⟩]
/-- The regulation measures every shareholder after all three redemptions; our function measures one at a time, so
each is checked against the 300 shares outstanding after all of them. -/
theorem s302_example :
    (decide (2 * 45 < 300) && decide (10 * 45 * 400 < 8 * 100 * 300)) = true ∧
    (decide (2 * 75 < 300) && decide (10 * 75 * 400 < 8 * 100 * 300)) = false ∧
    (decide (2 * 80 < 300) && decide (10 * 80 * 400 < 8 * 100 * 300)) = false ∧
    owned mAfter 0 = 45 := by decide
/-- §318(a)(1): a parent with 60 of 100 shares whose two children own 20 each owns all 100. Redeeming all 60 is not
substantially disproportionate (the parent still owns 40 of 40) and terminates the interest only with the §302(c)(2)
waiver. -/
def fam : List Holder := [⟨60, [1, 2]⟩, ⟨20, [0]⟩, ⟨20, [0]⟩]
theorem s318_family : owned fam 0 = 100 ∧ substantiallyDisproportionate fam 0 60 = false ∧
    redemptionIsExchange fam 0 60 false = false ∧ redemptionIsExchange fam 0 60 true = true := by decide

end Legal.USTax.Entity.Tests
