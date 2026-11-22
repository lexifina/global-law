import PlTax.Household

/-!
# Advances withheld by the employer, PIT art. 32, against the annual tax

art. 32 ust. 2: "12 % dochodu uzyskanego w danym miesiącu" while the income from that payer since January does not
exceed 120 000 zł, 32 % above; ust. 4: income = pay less the monthly costs of art. 22 ust. 2 pkt 1 (250 zł) or pkt 3
(300 zł) and the social contributions withheld that month; art. 31/32 with the PIT-2 statement (art. 32 ust. 3 and
the payer's duty quoted at line 8177 of t.j. 2025 poz. 163): each advance is reduced by "1/12 kwoty zmniejszającej
podatek" = 300 zł. Ordynacja art. 63 § 1: base and advance in whole złoty. Twelve equal monthly payments of the annual
wage (rounded to the grosz, the last month taking the remainder); the exemption of art. 21 ust. 1 pkt 148 applies to the
first pay received up to 85 528 zł (art. 32 ust. 6 lets the employee waive it, not modelled).
-/

namespace PlTax

structure WhState where
  cumWage : Int := 0       -- grosze, since January
  cumCapped : Int := 0     -- base used for emerytalne/rentowe
  cumExempt : Int := 0
  cumIncome : Int := 0     -- whole złoty, taxable income since January
  advances : Int := 0      -- whole złoty
  deriving Repr

/-- One month's advance. -/
def whMonth (young : Bool) (pit2 : Bool) (commuter : Bool) (st : WhState) (pay : Int) : WhState :=
  let capRoom := pos (ceiling - st.cumCapped)
  let cb := min pay capRoom
  let soc := pctGr cb eeEmerytalne + pctGr cb eeRentowe + pctGr pay eeChorobowe
  let ex := if young then min pay (pos (zeroPitLimit - st.cumExempt)) else 0
  let taxable := pay - ex
  let socDed := ratio soc taxable pay
  let kup := if taxable > 0 then min taxable (if commuter then kupCommuterMonthly else kupMonthly) else 0
  let incZl := zl (pos (taxable - kup - socDed))
  let before := st.cumIncome
  let after := before + incZl
  let low := pos (min after 120000 - before)
  let high := incZl - low
  let taxGr := low * 12 + high * 32
  let adv := if taxable > 0 then zl (pos (taxGr - (if pit2 then 30000 else 0))) else 0
  { cumWage := st.cumWage + pay, cumCapped := st.cumCapped + cb, cumExempt := st.cumExempt + ex,
    cumIncome := after, advances := st.advances + adv }

/-- The year's advances in whole złoty for an annual wage in złoty. -/
def withheld (p : PersonIn) (pit2 : Bool := true) : Int :=
  let g := p.wages * 100
  let m := g / 12
  let pays := (List.replicate 11 m) ++ [g - 11 * m]
  (pays.foldl (whMonth (p.age ≤ 25) pit2 p.commuter) {}).advances

/-- The annual tax of an employee filing alone with no reliefs (whole złoty). -/
def annualAlone (p : PersonIn) : Int :=
  (compute { adults := [p] }).incomeTax

end PlTax
