import TaxCode.Individual.Form1040

/-!
# A non-grantor trust's income tax, tax year 2025 (§§1(e), 1(h), 641–643, 661–663, 1411(a)(2))

A domestic complex trust (no income required to be distributed; the trustee may distribute income or corpus to the
beneficiaries) holding investments, written from the statute (OLRC 119-138; `statute.py 643 a`, `661`, `662`, `642 b`,
`1411 a 2`):

* §641(b): the trust's taxable income is computed as for an individual, except as Part I provides.
* §642(b)(2)(A): a $100 deduction in lieu of personal exemptions.
* §643(a): distributable net income (DNI) is taxable income without the distribution deduction (1) or the exemption
  (2), excluding capital gains allocated to corpus and not paid, credited or required to be distributed (3), and
  including tax-exempt interest (5).
* §661(a), (c): the distribution deduction is the amount properly paid, credited or required to be distributed,
  capped at DNI, less the part that consists of tax-exempt interest (§661(b) gives distributions the character of DNI
  in proportion).
* §662(a)(2), (b): each beneficiary includes its distribution, scaled down pro rata if all distributions exceed DNI,
  with the same proportion of each class of income as DNI.
* §1(e) with §1(j)(2)(E): the 2025 table (Rev. Proc. 2024-40 §2.01 Table 5): 10% to $3,150; $315 plus 24% to $11,450;
  $2,307 plus 35% to $15,650; $3,777 plus 37% above. §1(h) with the trust amounts of §1(j)(5)(B)(i)(IV) and (ii)(IV):
  0% on net capital gain up to $3,250 of taxable income, 15% up to $15,900, 20% above (Rev. Proc. 2024-40 §2.03).
* §1411(a)(2): 3.8% of the lesser of undistributed net investment income and AGI (§67(e)) over $15,650, the start of
  the top §1(e) bracket.

Whether gains are "allocated to corpus" is the governing instrument's and local law's question
(Treas. Reg. §1.643(a)-3(b)); here it is an input (`gainsInDni`), fixed when the trust is made. Not modelled: trustee
fees and other deductions (so §67(e) and the deduction-allocation rules of §1.652(b)-3 are idle), the trust's AMT,
the 65-day election of §663(b) (in a model where each year's distribution is chosen with the year's income known, it
changes nothing), the separate-share rule, throwback (§665–668 no longer reach domestic trusts' accumulations, §665(c)),
and §643(f) aggregation of trusts (one trust per family here).
-/

namespace Legal.USTax.Family
open TaxCode.Individual

/-- §1(e) as indexed for 2025, in cents on whole-dollar taxable income. -/
def trustScheduleCents (x : Int) : Int :=
  if x ≤ 0 then 0
  else if x ≤ 3150 then 10 * x
  else if x ≤ 11450 then 31500 + 24 * (x - 3150)
  else if x ≤ 15650 then 230700 + 35 * (x - 11450)
  else 377700 + 37 * (x - 15650)

/-- §1(h)(1) for a trust with taxable income `ti` and net capital gain (with qualified dividends, §1(h)(11)) `g`,
in cents; the same shape as `C.split`, with the trust's 0% and 15% amounts ($3,250 and $15,900). -/
def trustTaxCents (ti g : Int) : Int :=
  let g := max 0 g
  let ti := max 0 ti
  let a := max 0 (ti - g)
  let gain := min g ti
  let b := min gain (max 0 (min ti 3250 - a))
  let c := min (gain - b) (max 0 (min ti 15900 - (a + b)))
  let d := gain - b - c
  if 0 < g then min (trustScheduleCents ti) (trustScheduleCents a + 15 * c + 20 * d) else trustScheduleCents ti

def trustTax (ti g : Int) : Int := roundDollar (trustTaxCents ti g) 100

/-- One year of a trust's income. Every amount is whole dollars and non-negative; `ltGain` is net long-term capital
gain realised in the year. -/
structure TrustIncome where
  interest : Int := 0
  ordDiv : Int := 0       -- ordinary dividends, qualified ones included
  qualDiv : Int := 0
  ltGain : Int := 0
  taxExempt : Int := 0
  deriving Repr, DecidableEq

/-- §643(a): distributable net income. -/
def dni (gainsInDni : Bool) (t : TrustIncome) : Int :=
  t.interest + t.ordDiv + t.taxExempt + (if gainsInDni then t.ltGain else 0)

/-- What one beneficiary includes (§662(a)(2)) and its character (§662(b)). -/
structure Carry where
  interest : Int := 0
  nonqualDiv : Int := 0
  qualDiv : Int := 0
  ltGain : Int := 0
  taxExempt : Int := 0
  deriving Repr, DecidableEq

def Carry.taxable (c : Carry) : Int := c.interest + c.nonqualDiv + c.qualDiv + c.ltGain
def Carry.total (c : Carry) : Int := c.taxable + c.taxExempt

/-- §662(a)(2): a beneficiary paid `d` out of total distributions `total` includes `d`, or, if `total` exceeds DNI,
its pro-rata share of DNI. -/
def inclusion (dniAmt total d : Int) : Int := if total ≤ dniAmt then d else if total ≤ 0 then 0 else dniAmt * d / total

/-- §662(b): split an inclusion `x` among the classes of DNI in proportion. Rounding goes to the last class
(tax-exempt interest first, then the others), so the classes add up to `x` exactly. -/
def character (gainsInDni : Bool) (t : TrustIncome) (x : Int) : Carry :=
  let D := dni gainsInDni t
  if D ≤ 0 then {} else
  let te := t.taxExempt * x / D
  let i := t.interest * x / D
  let q := t.qualDiv * x / D
  let g := (if gainsInDni then t.ltGain else 0) * x / D
  ⟨i, x - te - i - q - g, q, g, te⟩

structure TrustReturn where
  dni : Int
  distributionDeduction : Int
  taxableIncome : Int
  regularTax : Int
  niit : Int
  carries : List Carry
  deriving Repr

/-- The trust's return for a year with income `t` and distributions `ds` (one per beneficiary). -/
def trustReturn (gainsInDni : Bool) (t : TrustIncome) (ds : List Int) : TrustReturn :=
  let D := dni gainsInDni t
  let total := ds.sum
  let carries := ds.map fun d => character gainsInDni t (inclusion D total d)
  let distTaxable := (carries.map Carry.taxable).sum          -- §661(c): the tax-exempt part is not deductible
  let gross := t.interest + t.ordDiv + t.ltGain
  let ti := max 0 (gross - distTaxable - 100)               -- §641(b), §661(a), §642(b)(2)(A)
  let qd := t.qualDiv - (carries.map (·.qualDiv)).sum
  let lg := t.ltGain - (carries.map (·.ltGain)).sum
  let tax := trustTax ti (qd + lg)
  -- §1411(a)(2): undistributed NII; AGI per §67(e) (gross income less the §§642(b), 661 deductions)
  let unii := max 0 (gross - distTaxable)
  let agi := gross - distTaxable - 100
  let niit := roundDollar (38 * min unii (max 0 (agi - 15650))) 1000
  ⟨D, distTaxable, ti, tax, niit, carries⟩

def TrustReturn.total (r : TrustReturn) : Int := r.regularTax + r.niit

/-- Add a beneficiary's §662 inclusion to their household (character kept, §662(b)). Tax-exempt interest goes to
`taxExemptInterest`. -/
def addCarry (h : Household) (c : Carry) : Household :=
  { h with taxableInterest := h.taxableInterest + c.interest,
           ordinaryDividends := h.ordinaryDividends + c.nonqualDiv + c.qualDiv,
           qualifiedDividends := h.qualifiedDividends + c.qualDiv,
           longTermGains := h.longTermGains + c.ltGain,
           taxExemptInterest := h.taxExemptInterest + c.taxExempt }

end Legal.USTax.Family
