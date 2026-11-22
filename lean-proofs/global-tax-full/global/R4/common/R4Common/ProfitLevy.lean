import R4Common.Stamp

/-! # R4Common: a levy at a flat rate on a company's profit (twelfth pass, P7 "high" items).

One charge (event `year`) on the company line's `profit` (the input's profit before tax; losses brought forward are not
deducted), at `rateBp`, when the company's turnover exceeds `minTurnover` and its profit exceeds `minProfit` (−1: no
condition). Household entities: nothing. Used for GH Growth and Sustainability Levy (Act 1095, category C: 2,5 % of
profit before tax), NG tertiary education tax (TETFund Act 2011 s. 1 (2): 3 % of assessable profit), MU fair share
contribution on companies (VAT Act Part XC s. 53N: 5 % of chargeable income above Rs 24 m supplies and income). -/

namespace R4
open TaxKernel TaxKernel.Global

def profitLevyFamily (oecd : Oecd) (name : String) (rateBp : Int) (statute : String)
    (minTurnover : Int := -1) (minProfit : Int := -1) (level : Level := .central) : Family :=
  { name := s!"{oecd.code} {name}", covers := [oecd],
    run := fun _ g _ =>
      if g.entity != .company then [] else
      let co := g.company
      if decide (co.turnover ≤ minTurnover) || decide (co.profit ≤ minProfit) then [] else
      [charge oecd name co.profit id (fun x => divR .down (rateBp * pos x) BP) (event := "year") (level := level)
        (statute := statute)] }

def tPL (t p : Int) : CanonGlobal := { id := "c", entity := .company, household := { id := "c" }, company := { turnover := t, profit := p } }
#guard ((profitLevyFamily .cit "t" 500 "s" 24000000 24000000).run [] (tPL 30000000 25000000) []).map (·.due) == [1250000]
#guard ((profitLevyFamily .cit "t" 500 "s" 24000000 24000000).run [] (tPL 30000000 24000000) []).map (·.due) == []
#guard ((profitLevyFamily .cit "t" 250 "s").run [] (tPL 0 1000000) []).map (·.due) == [25000]
#guard ((profitLevyFamily .cit "t" 250 "s").run [] { id := "h", household := { id := "h" } } []).map (·.due) == []

end R4
