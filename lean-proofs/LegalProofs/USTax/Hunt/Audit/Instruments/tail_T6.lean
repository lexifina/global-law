-- T6 (part 1): the plan, the baseline and the closed-gap result replayed through the kernel on the full rules.
-- The trades are applied directly (openLong / sellLong / advance), not through `expand`, so no strings are reduced.
def pick (s : St) (i d : Nat) : Lot :=
  match s.lots.find? (fun x => x.inst == i && x.opened == d) with
  | some l => l
  | none => { inst := 99, long := true, opened := 0, basis := 0, hp := 0 }

def scK (fix : Bool) : Sc := { exDate 50000 "K" with taintFix := fix }

/-- buy GainFund day 129; ex-date 130: buy a second lot, sell the first; day 162: sell the second, buy FundA. -/
def runPlan (sc : Sc) : St :=
  let s := init sc
  let s := sellLong sc s (pick s 0 5)
  let s := openLong sc s 1
  let s := advance sc s            -- to day 130 (ex-date)
  let s := openLong sc s 1
  let s := sellLong sc s (pick s 1 129)
  let s := advance sc s            -- to day 131
  let s := advance sc s            -- to day 162
  let s := sellLong sc s (pick s 1 130)
  let s := openLong sc s 0
  let s := advance sc s            -- to day 330
  let s := advance sc s            -- to day 364
  let s := advance sc s            -- year end, to day 729
  liquidate sc s

def runHold (sc : Sc) : St :=
  let s := init sc
  let s := advance sc s
  let s := advance sc s
  let s := advance sc s
  let s := advance sc s
  let s := advance sc s
  let s := advance sc s
  liquidate sc s

-- compiled cross-check: the direct sequence is the labelled plan
#eval (bestTax (scK false) (runPlan (scK false)), replay (scK false) PLAN, bestTax (scK false) (runHold (scK false)),
       bestTax (scK true) (runPlan (scK true)), replay (scK true) PLAN)
#eval yearFigures (scK false) (runPlan (scK false))
#eval yearFigures (scK true) (runPlan (scK true))
#eval yearFigures (scK false) (runHold (scK false))

/-- Year figures of the plan under the statute as encoded: year 1 short-term 50,000 − 10,000, long-term +10,000. -/
theorem plan_figures : (yearFigures (scK false) (runPlan (scK false)) ==
    [(40000, 10000, 0, 0, 0, 0, 0), (50000, 5000, 0, 0, 0, 0, 0)]) = true := by decide +kernel

theorem hold_figures : (yearFigures (scK false) (runHold (scK false)) ==
    [(50000, 0, 0, 0, 0, 0, 0), (50000, 5000, 0, 0, 0, 0, 0)]) = true := by decide +kernel

/-- Closed-gap rule: the loss on the replacement share is long-term; the year figures are the baseline's. -/
theorem closed_figures : (yearFigures (scK true) (runPlan (scK true)) ==
    [(50000, 0, 0, 0, 0, 0, 0), (50000, 5000, 0, 0, 0, 0, 0)]) = true := by decide +kernel

theorem plan_tax : bestTax (scK false) (runPlan (scK false)) = 41038 := by decide +kernel
theorem hold_tax : bestTax (scK false) (runHold (scK false)) = 42806 := by decide +kernel
theorem closed_tax : bestTax (scK true) (runPlan (scK true)) = 42806 := by decide +kernel

#print axioms plan_figures
#print axioms hold_figures
#print axioms closed_figures
#print axioms plan_tax
#print axioms hold_tax
#print axioms closed_tax
