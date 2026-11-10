import TaxCode.Individual.Form1040

/-!
# §1(g): the tax on a child's unearned income, tax year 2025

Written from 26 U.S.C. §1(g) (OLRC release point 119-138; print it with
`python -I tools/taxcode/loopholes/statute.py 1 g`), §59(j) and §63(c)(5), with the 2025 amounts of Rev. Proc. 2024-40.
The household model in `TaxCode/Individual` computes the child's own return (its standard deduction already follows
§63(c)(5)); this file adds what that model leaves out:

* who §1(g) applies to (§1(g)(2)): under 18 at the close of the year; or 18, or a full-time student under 24, whose
  earned income does not exceed one-half of their support; with a parent alive; not filing jointly;
* net unearned income (§1(g)(4)): the part of AGI not attributable to earned income, less $1,350 and the greater of
  $1,350 or directly connected itemized deductions (children here do not itemize), capped at taxable income;
* the tax (§1(g)(1), (3)): the greater of the child's own tax and the tax on taxable income less net unearned income
  plus the child's share of the allocable parental tax — the parent's tax on taxable income plus the net unearned
  income of all the parent's §1(g) children, over the parent's own tax, shared in proportion to each child's net
  unearned income. Form 8615 lines 1–18 compute exactly this; the line numbers are cited below;
* the child's AMT exemption cap (§59(j)): earned income plus $9,550;
* the parent's election (§1(g)(7), Form 8814): a child whose gross income is only interest and dividends, more than
  $1,350 and less than $13,500, is treated as having no gross income; the parent includes the excess over $2,700 and
  pays 10% of the lesser of $1,350 or the excess over $1,350.

The child's qualified dividends and net capital gain are shared between net unearned income and the rest in proportion
(Form 8615 instructions, line 9 and line 15 worksheets: the child's qualified dividends and capital gain "included on
line 5" are those amounts times line 5 ÷ line 1).

All amounts whole dollars. 2025 amounts: §63(c)(5)(A) $1,350; §59(j)(1)(B) $9,550 (Rev. Proc. 2024-40 §3.12).
-/

namespace Legal.USTax.Family
open TaxCode.Individual

deriving instance Inhabited for TaxCode.Individual.Line

/-- §63(c)(5)(A) as indexed for 2025, the amount §1(g)(4)(A)(ii)(I) and §1(g)(7) refer to. -/
def depBase : Int := 1350
/-- §59(j)(1)(B) as indexed for 2025. -/
def childAmtAddOn : Int := 9550

/-- The facts §1(g)(2) reads about a child. `earned` is §911(d)(2) earned income; `support` the total support of the
child for the year (§152(c)(1)(D) with §152(f)(5)). -/
structure ChildFacts where
  age : Nat
  student : Bool := false
  earned : Int := 0
  support : Int := 0
  parentAlive : Bool := true
  joint : Bool := false
  deriving Repr, DecidableEq, Inhabited

/-- §1(g)(2): the child to whom the subsection applies. (ii)(I) points at the age test of §152(c)(3) without its
disability rule: under 19, or a student under 24. -/
def ChildFacts.subject (c : ChildFacts) : Bool :=
  (decide (c.age < 18) ||
    ((decide (c.age < 19) || (c.student && decide (c.age < 24))) && decide (2 * c.earned ≤ c.support))) &&
  c.parentAlive && !c.joint

/-- §1(g)(4)(A)(i): the portion of AGI not attributable to earned income (Form 8615 line 1). For the items the
household model carries this is gross income other than wages and self-employment income, with capital losses limited
by §1211(b). -/
def unearnedIncome (h : Household) : Int :=
  h.taxableInterest + h.ordinaryDividends + A.capitalGainLine h + h.iraDistributions + h.pensions + h.unemployment +
    h.otherIncome

/-- §1(g)(4): net unearned income (Form 8615 lines 1–5), for a child who does not itemize. -/
def netUnearned (h : Household) (ti : Int) : Int := max 0 (min ti (unearnedIncome h - 2 * depBase))

/-- The child's qualified dividends and net capital gain, and the part of them that is in net unearned income. -/
def childQdcg (h : Household) : Int := B.netCapitalGain h
def nuiQdcg (h : Household) (nui : Int) : Int :=
  let u := unearnedIncome h
  if u ≤ 0 then 0 else min (childQdcg h) (childQdcg h * nui / u)

/-- One §1(g) child as the parental-tax computation sees it: taxable income, net unearned income, and the qualified
dividends and capital gain inside it. -/
structure ChildLine where
  ti : Int
  nui : Int
  cg : Int      -- all the child's qualified dividends and net capital gain
  nuiCg : Int   -- the part of `cg` in net unearned income
  deriving Repr, DecidableEq, Inhabited

/-- §1(g)(3)(A): the allocable parental tax for a parent with filing status `pf`, taxable income `pti` and qualified
dividends and capital gain `pcg`, and all of that parent's §1(g) children (Form 8615 lines 6–11). -/
def allocableParentalTax (pf : Filing) (pti pcg : Int) (kids : List ChildLine) : Int :=
  let n := (kids.map (·.nui)).sum
  let g := (kids.map (·.nuiCg)).sum
  max 0 (C.regularTax pf (pti + n) (pcg + g) - C.regularTax pf pti pcg)

/-- §1(g)(1): the child's tax under §1 (Form 8615 lines 12–18). `all` is every §1(g) child of the parent, this child
included. -/
def kiddieTax (pf : Filing) (pti pcg : Int) (all : List ChildLine) (c : ChildLine) : Int :=
  let own := C.regularTax .single c.ti c.cg                                          -- line 17
  if c.nui ≤ 0 then own else
  let total := (all.map (·.nui)).sum
  let share := if total ≤ 0 then 0 else allocableParentalTax pf pti pcg all * c.nui / total   -- lines 11–13
  let rest := C.regularTax .single (c.ti - c.nui) (c.cg - c.nuiCg)                   -- lines 14–15
  max (share + rest) own                                                              -- lines 16–18

/-- §59(j): tentative minimum tax of a §1(g) child, whose exemption may not exceed earned income plus $9,550.
The exemption is first figured as usual (§55(d), single), then capped. Same units and rounding as `C.tentativeMinimumTax`. -/
def childTmt (amti ti g earned : Int) : Int :=
  let f := Filing.single
  let a := C.amtiQ f amti
  let ex := min (C.exemptionQ f a) (16 * max 0 (earned + childAmtAddOn))
  let te := max 0 (a - ex)
  let q := if 0 < g then min (C.rate2628 f te) (C.tmtCapGainQ f te ti g) else C.rate2628 f te
  roundDollar q 1600

/-- What a child's return owes. `line` is the household model's return for the child (a dependent, single). If §1(g)
applies, the §1 tax is replaced by `kiddie` and the AMT is recomputed against it with the §59(j) exemption. -/
def childTotal (h : Household) (line : Line) (subject : Bool) (kiddie : Int) : Int :=
  if !subject then line.netTax else
  let std := line.standardDeduction
  let amti := C.amtiBase line.taxableIncome 0 std 0
  let amt := max 0 (childTmt amti line.taxableIncome (childQdcg h) (B.earnedIncome h) - kiddie)
  line.netTax - line.regularTax - line.amt + kiddie + amt

/-! ## §1(g)(7): the parent's election (Form 8814) -/

/-- §1(g)(7)(A): the child's gross income is only interest and dividends (capital gain distributions count as
dividends; a sale of property does not), more than $1,350 and less than $13,500. -/
def form8814Eligible (c : ChildFacts) (h : Household) : Bool :=
  let gross := h.taxableInterest + h.ordinaryDividends + h.longTermGains
  -- the household model has no separate field for capital gain distributions; any gain is treated as a sale
  c.subject && h.wages = 0 && h.seIncome = 0 && h.shortTermGains = 0 && h.longTermGains = 0 &&
    h.iraDistributions = 0 &&
    h.pensions = 0 && h.otherIncome = 0 && h.unemployment = 0 &&
    decide (depBase < gross) && decide (gross < 10 * depBase)

/-- §1(g)(7)(B)(ii)(II): 10% of the lesser of $1,350 or the excess of gross income over $1,350 (Form 8814 lines 13–15). -/
def form8814Tax (gross : Int) : Int := min depBase (max 0 (gross - depBase)) / 10

/-- §1(g)(7)(B)(i): the parent includes the child's gross income over $2,700 (Form 8814 lines 1–12), keeping the
character of each item in proportion (Form 8814 lines 6–9: qualified dividends and capital gain distributions are
carried at their share of the included amount). Returns the parent's household with the items added. -/
def form8814Include (parent child : Household) : Household :=
  let gross := child.taxableInterest + child.ordinaryDividends + child.longTermGains
  let inc := max 0 (gross - 2 * depBase)
  if gross ≤ 0 then parent else
  let i := child.taxableInterest * inc / gross
  let d := child.ordinaryDividends * inc / gross
  let q := child.qualifiedDividends * inc / gross
  let g := inc - i - d
  { parent with taxableInterest := parent.taxableInterest + i,
                ordinaryDividends := parent.ordinaryDividends + d,
                qualifiedDividends := parent.qualifiedDividends + q,
                longTermGains := parent.longTermGains + g }

end Legal.USTax.Family
