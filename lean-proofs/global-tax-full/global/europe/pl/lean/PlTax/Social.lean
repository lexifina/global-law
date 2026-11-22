import PlTax.Params

/-!
# Social insurance and health contributions

Employees (SUS art. 16 ust. 1, 1b; art. 22 ust. 1; art. 19 ust. 1): 9,76 % emerytalne + 1,5 % rentowe on wages up to the
ceiling, 2,45 % chorobowe on all wages. Health (Zdrowotna art. 79 ust. 1, art. 81 ust. 1, 5): 9 % of wages less those
social contributions. Computed on the annual wage, to the grosz (payroll computes it monthly; the difference is at most
a few grosze a year for a constant monthly wage). The art. 83 ust. 1 cap of the health contribution at the advance
computed under the 2021 law binds only below about 1 250 zł a month and is not modelled (reported as unsupported).

Self-employed (SUS art. 18 ust. 8, art. 18a; art. 22): contributions on a declared monthly base (standard 60 % of
8673 zł; preferential 30 % of 4666 zł), with voluntary chorobowe taken (the ZUS default table), plus the Fundusz Pracy
2,45 % on the standard base. Health by tax regime (Zdrowotna art. 79, 79a, 81 ust. 2, 2e) on the annual figures; the
health year runs February–January, here taken as the calendar year.
-/

namespace PlTax

structure EmpSocial where
  emerytalne : Int
  rentowe : Int
  chorobowe : Int
  total : Int
  subkonto : Int
  health : Int
  deriving Repr

/-- Employee contributions on an annual wage in złoty. -/
def empSocial (wZl : Int) (cap : Int := ceiling) : EmpSocial :=
  let g := wZl * 100
  let c := capped g cap
  let e := pctGr c eeEmerytalne
  let r := pctGr c eeRentowe
  let ch := pctGr g eeChorobowe
  let t := e + r + ch
  { emerytalne := e, rentowe := r, chorobowe := ch, total := t, subkonto := pctGr c subkontoEe,
    health := pctGr (pos (g - t)) healthRate }

inductive ZusKind | standard | preferential | none
  deriving Repr, BEq, DecidableEq, Inhabited

/-- Self-employed social contributions for the year: (social insurance, Fundusz Pracy), in grosze. Each month's
contribution is rounded to the grosz, as ZUS publishes them (standard: 1015,78 + 416,30 + 86,90 + 127,49 = 1646,47 zł,
FP 127,49 zł). -/
def seZus (k : ZusKind) (y : Int := 2025) : Int × Int :=
  match k with
  | .standard =>
    let b := seBaseStandardY y
    (12 * (pctGr b seEmerytalne + pctGr b seRentowe + pctGr b seWypadkowe + pctGr b seChorobowe),
     12 * pctGr b funduszPracy)
  | .preferential =>
    let one (b : Int) : Int := pctGr b seEmerytalne + pctGr b seRentowe + pctGr b seWypadkowe + pctGr b seChorobowe
    let b := seBasePreferential
    (if y ≥ 2025 then 12 * one b else ((List.range 12).map (fun i => one (seBasePreferentialM y (i + 1)))).foldl (· + ·) 0, 0)
  | .none => (0, 0)

inductive Regime | skala | liniowy | ryczalt
  deriving Repr, BEq, DecidableEq, Inhabited

def Regime.name : Regime → String
  | .skala => "skala (art. 27)"
  | .liniowy => "liniowy 19% (art. 30c)"
  | .ryczalt => "ryczałt od przychodów ewidencjonowanych"

/-- Health contribution of the self-employed for the year (grosze). `income` is business income after costs (incl.
Fundusz Pracy) and after the social contributions paid (Zdrowotna art. 81 ust. 2, 2b); `revenue` the ryczałt revenue
after those contributions (art. 81 ust. 2g). -/
def seHealth (r : Regime) (income revenue : Int) (y : Int := 2025) : Int :=
  match r with
  | .skala => max (pctGr (pos income) healthRate) (12 * healthMinMonthlyY y)
  | .liniowy => max (pctGr (pos income) healthLiniowyRate) (12 * healthMinMonthlyY y)
  | .ryczalt =>
    if revenue ≤ ryczBand1 then 12 * ryczHealthY y 1
    else if revenue ≤ ryczBand2 then 12 * ryczHealthY y 2
    else 12 * ryczHealthY y 3

end PlTax
