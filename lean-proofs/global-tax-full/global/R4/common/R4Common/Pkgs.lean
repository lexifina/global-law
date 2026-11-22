import R4Common.P3

/-! # R4Common P3-P7 helpers (second pass): capped employer levies, flat gains taxes, transfer duties, flat
inheritance and gift duties by relationship. Used by the modules that `R4/tools/gen_pkgs.py` writes. -/

namespace R4
open TaxKernel TaxKernel.Global

/-- An employer levy on wages up to an annual ceiling per employee (`capAnnual < 0`: no ceiling). Household: each
adult's wages, borne by the employer; company: the payroll, capped at `employees × capAnnual` when employees are given. -/
def payrollCapFamily (oecd : Oecd) (name : String) (rateBp capAnnual : Int) (statute : String) (level : Level := .social) : Family :=
  { name := s!"{oecd.code} {name}", covers := [oecd],
    run := fun _ g _ =>
      let capOf : Int → Int := fun w => if capAnnual < 0 then w else min w capAnnual
      if g.entity == .company then
        (if g.company.payroll ≤ 0 then [] else
          let b := if capAnnual < 0 || g.company.employees == 0 then g.company.payroll
                   else min g.company.payroll (capAnnual * g.company.employees)
          [charge oecd name b id (fun x => divR .down (rateBp * pos x) BP) (event := "payroll")
            (level := level) (statute := statute)])
      else
        (g.household.adults.zipIdx.filter (fun (a, _) => a.wages > 0)).map fun (a, i) =>
          charge oecd name (capOf a.wages) id (fun x => divR .down (rateBp * pos x) BP) (event := s!"adult {i + 1}")
            (level := level) (bearer := .employer) (statute := statute) }

/-- A flat tax on the gain of each household disposal of the listed kinds (gain = proceeds − cost − costs, floored at
zero; a main home is skipped when `mainHomeExempt`). -/
def gainsFamily (name : String) (rateBp : Int) (kinds : List AssetKind) (statute : String)
    (mainHomeExempt : Bool := false) (onProceeds : Bool := false) : Family :=
  { name := s!"1100 {name}", covers := [],
    run := fun _ g _ =>
      if g.entity == .company then [] else
      (g.disposals.zipIdx.filter (fun (d, _) => kinds.contains d.kind && !(mainHomeExempt && d.mainHome))).map fun (d, i) =>
        charge .pit name (if onProceeds then d.proceeds else pos d.gain) id (fun y => divR .down (rateBp * pos y) BP)
          (event := s!"disposal {i + 1}") (statute := statute) }

/-- A transfer (registration / stamp) duty at a flat rate on each purchase of the listed kinds, on the higher of the
price and the assessed value. -/
def transferDutyFamily (name : String) (rateBp : Int) (kinds : List AssetKind) (statute : String) (level : Level := .central) : Family :=
  { name := s!"4400 {name}", covers := [.transactions],
    run := fun _ g _ =>
      (g.purchases.zipIdx.filter (fun (p, _) => kinds.contains p.kind)).map fun (p, i) =>
        charge .transactions name (max p.price p.assessed) id (fun y => divR .down (rateBp * pos y) BP)
          (event := s!"purchase {i + 1}") (level := level) (statute := statute) }

/-- Rate for a relationship from a table, with a default for relationships not listed. -/
def relRate (table : List (Relation × Int)) (dflt : Int) (r : Relation) : Int :=
  ((table.find? (·.1 == r)).map (·.2)).getD dflt

/-- Inheritance and gift duty at flat rates by relationship on each transfer received (statutory value less a
per-transfer allowance). Separate tables for inheritances and gifts. -/
def estateFlatFamily (name : String) (inh gift : List (Relation × Int)) (inhDflt giftDflt allowance : Int) (statute : String) : Family :=
  { name := s!"4300 {name}", covers := [.estate],
    run := fun _ g _ =>
      g.transfers.zipIdx.map fun (t, i) =>
        let r := if t.kind == .gift then relRate gift giftDflt t.relation else relRate inh inhDflt t.relation
        charge .estate name t.statutoryValue (fun v => pos (v - allowance)) (fun y => divR .down (r * pos y) BP)
          (event := s!"transfer {i + 1} ({if t.kind == .gift then "gift" else "inheritance"})") (statute := statute) }

def tG (xs : List Transfer) : CanonGlobal := { id := "t", household := { id := "t" }, transfers := xs }

#guard ((estateFlatFamily "t" [(.child, 300)] [] 1000 500 0 "s").run [] (tG [{ kind := .inheritance, value := 100000, relation := .child },
  { kind := .gift, value := 100000, relation := .sibling }]) []).map (·.due) == [3000, 5000]
def tD : CanonGlobal := { id := "x", household := { id := "x" }, disposals := [{ kind := .listedShares, proceeds := 500000, cost := 300000 }, { kind := .home, proceeds := 1, cost := 0 }] }
#guard ((gainsFamily "t" 1000 [.listedShares] "s").run [] tD []).map (·.due) == [20000]
def tP : CanonGlobal := { id := "x", household := { id := "x" }, purchases := [{ kind := .home, price := 1000000, assessed := 1200000 }] }
#guard ((transferDutyFamily "t" 500 [.home, .land] "s").run [] tP []).map (·.due) == [60000]

/-- Marginal tariff in ticks (rate in bp × amount): `bands` are (upper bound, rate) in increasing order, `top` the
rate above the last bound. -/
def bandTicks : List (Int × Int) → Int → Int → Int → Int
  | [], top, lo, x => top * pos (x - lo)
  | (u, r) :: rest, top, lo, x => r * pos (min x u - lo) + bandTicks rest top u x

def classOf (classes : List (List Relation × List (Int × Int) × Int)) (dflt : List (Int × Int) × Int) (r : Relation) :
    List (Int × Int) × Int :=
  ((classes.find? (·.1.contains r)).map (·.2)).getD dflt

/-- Inheritance and gift duty on each transfer received by marginal tariffs per relationship class, after a
per-transfer allowance for the listed relationships (gifts get it only when `giftAllowance`). -/
def estateBandFamily (name : String) (classes : List (List Relation × List (Int × Int) × Int))
    (dflt : List (Int × Int) × Int) (allowRels : List Relation) (allowance : Int) (giftAllowance : Bool) (statute : String)
    (onlyKind : Option TransferKind := none) : Family :=
  { name := s!"4300 {name}", covers := [.estate],
    run := fun _ g _ =>
      (g.transfers.zipIdx.filter (fun (t, _) => onlyKind.all (· == t.kind))).map fun (t, i) =>
        let c := classOf classes dflt t.relation
        let al := if allowRels.contains t.relation && (t.kind == .inheritance || giftAllowance) then allowance else 0
        charge .estate name t.statutoryValue (fun v => pos (v - al)) (fun y => divR .down (bandTicks c.1 c.2 0 y) BP)
          (event := s!"transfer {i + 1} ({if t.kind == .gift then "gift" else "inheritance"})") (statute := statute) }

#guard bandTicks [(100, 200), (300, 400)] 1000 0 500 == 200 * 100 + 400 * 200 + 1000 * 200

/-- An employer levy whose rate depends on the monthly wage (whole-amount notch): `lowBp` when the monthly wage is at
most `monthlyLimit`, else `highBp`. Household: each adult's annual wages / 12; company: the average monthly wage
(payroll / 12 / employees; with no employee count, the high rate). -/
def payrollNotchFamily (oecd : Oecd) (name : String) (lowBp highBp monthlyLimit : Int) (statute : String) (level : Level := .social) : Family :=
  { name := s!"{oecd.code} {name}", covers := [oecd],
    run := fun _ g _ =>
      let rateOf : Int → Int := fun monthly => if monthly ≤ monthlyLimit then lowBp else highBp
      if g.entity == .company then
        (if g.company.payroll ≤ 0 then [] else
          let r := if g.company.employees == 0 then highBp else rateOf (g.company.payroll / 12 / g.company.employees)
          [charge oecd name g.company.payroll id (fun x => divR .down (r * pos x) BP) (event := "payroll")
            (level := level) (statute := statute)])
      else
        (g.household.adults.zipIdx.filter (fun (a, _) => a.wages > 0)).map fun (a, i) =>
          charge oecd name a.wages id (fun x => divR .down (rateOf (a.wages / 12) * pos x) BP) (event := s!"adult {i + 1}")
            (level := level) (bearer := .employer) (statute := statute) }

/-- A net wealth tax on the household's assets (statutory value less debt, summed) by a marginal tariff whose rates
are in units of `1 / den` (e.g. `den = 100000` for rates in thousandths of a per cent). -/
def wealthBandFamily (name : String) (bands : List (Int × Int)) (top den : Int) (statute : String) : Family :=
  { name := s!"4200 {name}", covers := [.wealth],
    run := fun _ g _ =>
      if g.entity == .company || g.assets.isEmpty then [] else
      let net := (g.assets.map fun a => a.statutoryValue - a.debt).foldl (· + ·) 0
      [charge .wealth name net id (fun y => divR .down (bandTicks bands top 0 y) den) (event := "year") (statute := statute)] }

end R4
