/-!
# Form 8889 (2025) line 3 against §223(b)(2) and (b)(8)(A)

Form text (2025 Instructions for Form 8889, p. 4, Line 3): "2. If the last-month rule ... applies, you are considered
an eligible individual for the entire year. You are treated as having the same HDHP coverage for the entire year as
you had on the first day of the last month of your tax year. ... 4. If you were, or were considered, an eligible
individual for the entire year and you changed your type of coverage during the year, enter on line 3 ... the greater
of: a. The limitation shown on the last line of the Line 3 Limitation Chart and Worksheet ..., or b. The maximum
amount that can be contributed based on the type of HDHP coverage you had on the first day of the last month of your
tax year." TIP: "If you had family coverage on the first day of the last month, you do not need to use the worksheet;
enter $8,550 on line 3." Chart (p. 5): a month in which you were not an eligible individual on the first day is "-0-".
This is Notice 2008-52 (pp. 1-2: the limit is "the greater of" the sum of monthly limits "based on eligibility and
HDHP coverage on the first day of each month" and the full amount for the December coverage; Example 3).

Statute: §223(b)(2) monthly limit 1/12 of the self-only ($4,300) or family ($8,550) amount "as of the first day of
such month"; §223(b)(8)(A): an individual eligible in the last month is treated "(i) as having been an eligible
individual during each of the months in such taxable year, and (ii) as having been enrolled, during each of the months
such individual is treated as an eligible individual solely by reason of clause (i), in the same high deductible
health plan in which the individual was enrolled for the last month".

Model (calendar year, eligible on December 1, no catch-up, no Medicare month): among January-November, `s` months
actually eligible with self-only cover, `f` months actually eligible with family cover, `n` months not eligible
(s + f + n = 11). Amounts are ×12 (twelfths of a dollar).
-/

namespace TaxCode.Big.Form8889

def S : Int := 4300
def F : Int := 8550

/-- Statute ×12: actual months at their own coverage; months eligible "solely by reason of clause (i)" at the
December coverage; December itself. -/
def stat12 (decFamily : Bool) (s f n : Int) : Int :=
  let dec := if decFamily then F else S
  S * s + F * f + dec * n + dec

/-- Form ×12: greater of the chart (ineligible months 0) and twelve months of the December amount. -/
def form12 (decFamily : Bool) (s f _n : Int) : Int :=
  let dec := if decFamily then F else S
  max (S * s + F * f + dec) (12 * dec)

/-- **Family cover on December 1: the form exceeds the statute by exactly $4,250/12 for every earlier month of
actual self-only eligibility.** -/
theorem family_gap (s f n : Int) (hs : 0 ≤ s) (hf : 0 ≤ f) (hn : 0 ≤ n) (h : s + f + n = 11) :
    form12 true s f n - stat12 true s f n = 4250 * s := by
  unfold form12 stat12 S F; simp; omega

/-- Max $3,895.83 (= 46,750/12): eligible all year with self-only cover January-November. -/
theorem family_gap_le (s f n : Int) (hs : 0 ≤ s) (hf : 0 ≤ f) (hn : 0 ≤ n) (h : s + f + n = 11) :
    form12 true s f n - stat12 true s f n ≤ 46750 := by
  rw [family_gap s f n hs hf hn h]; omega

example : form12 true 11 0 0 = 102600 ∧ stat12 true 11 0 0 = 55850 := by decide  -- $8,550 v $4,654.17

/-- **Self-only cover on December 1: the statute exceeds the form by min($4,300 × n, $4,250 × f)/12** — months
treated as eligible only by the last-month rule count at the self-only rate under the statute, but at zero on the
chart, while the "greater of" alternative is only $4,300. -/
theorem self_gap (s f n : Int) (hs : 0 ≤ s) (hf : 0 ≤ f) (hn : 0 ≤ n) (h : s + f + n = 11) :
    stat12 false s f n - form12 false s f n = min (4300 * n) (4250 * f) := by
  unfold form12 stat12 S F; simp; omega

/-- Max $1,791.67 (= 21,500/12), at n = 5 ineligible months and f = 6 family months. -/
theorem self_gap_le (s f n : Int) (hs : 0 ≤ s) (hf : 0 ≤ f) (hn : 0 ≤ n) (h : s + f + n = 11) :
    stat12 false s f n - form12 false s f n ≤ 21500 := by
  rw [self_gap s f n hs hf hn h]; omega

example : stat12 false 0 6 5 - form12 false 0 6 5 = 21500 := by decide

/-- Exact affected sets: form more iff December family and s > 0; statute more iff December self-only, n > 0 and
f > 0; equal otherwise. -/
theorem affected (dec : Bool) (s f n : Int) (hs : 0 ≤ s) (hf : 0 ≤ f) (hn : 0 ≤ n) (h : s + f + n = 11) :
    (form12 dec s f n > stat12 dec s f n ↔ dec = true ∧ 0 < s) ∧
    (form12 dec s f n < stat12 dec s f n ↔ dec = false ∧ 0 < n ∧ 0 < f) := by
  unfold form12 stat12 S F; cases dec <;> simp <;> omega

end TaxCode.Big.Form8889

#print axioms TaxCode.Big.Form8889.affected
#print axioms TaxCode.Big.Form8889.self_gap
