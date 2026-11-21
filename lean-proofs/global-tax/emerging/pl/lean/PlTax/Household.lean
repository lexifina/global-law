import PlTax.Scale
import PlTax.Social

/-!
# Persons and households

Choices (each a statutory default or a stated assumption):
* **Ages** are completed years on 1 January 2025. An adult aged 25 turns 26 during 2025 and is exempt under art. 21
  ust. 1 pkt 148 only on pay received before the birthday: modelled as the whole year, reported as unsupported. A child
  aged 6 turns 7 in 2025 and starts school in September (Dobry start); aged 17 turns 18 in 2025 (800+ and the art. 27f
  relief for part of the year: modelled as the whole year, reported).
* **Business income** (`selfEmployment`) is income after costs and before ZUS; the optional `plSeRevenue` is revenue
  (default: equal to income, a service business without costs). Fundusz Pracy is a cost under skala and liniowy.
* **Regime** per adult (`plRegime`): skala (the statutory default, art. 9a ust. 1), liniowy (art. 30c), ryczałt (rate
  `plRyczaltBp`, default 12 %, art. 12 ust. 1 pkt 2b). ZUS per adult (`plZus`): standard (default), preferential, none.
* **Spouses** (married = true, two adults) file jointly when that costs less (art. 6 ust. 2, a choice made in the
  return) and when neither uses liniowy or ryczałt (art. 6 ust. 8). **One unmarried adult with children** is a single
  parent (art. 6 ust. 4c, no other parent bringing them up, ust. 4f) and splits (ust. 4d) when that costs less. Two
  unmarried adults: separate, the relief to whichever parent gains most.
* **Child relief** (art. 27f): minors (age ≤ 17); spouses share it in any proportion (ust. 4), so it is pooled against
  their combined art. 27 tax; the unused part is paid out up to the contributions of ust. 9 (spouses' combined, ust. 10).
* **Zero-PIT exemptions**: under 26 (pkt 148, wages), returning (pkt 152, optional `plReturning`), 4+ children (pkt 153:
  households with four or more children aged ≤ 24, adult ones taken to be in school), working seniors not drawing a
  pension (pkt 154: 60 for women, 65 for men; `plSex` "F"/"M", default "M"); one 85 528 zł limit (ust. 44), wages first.
  Contributions on exempt revenue are not deductible (art. 26 ust. 1 pkt 2, 2a "z wyjątkiem"): taken proportionally.
* **Investment income**: interest and dividends 19 % (art. 30a), gains 19 % (art. 30b); rental income ryczałt 8,5 % /
  12,5 % above 100 000 zł per person (ryczałt art. 12 ust. 1 pkt 4), split equally between spouses (art. 12 ust. 6)
  unless `plRentalOnePerson`.
* **pensionContributions** = IKZE (art. 26 ust. 1 pkt 2b), first adult first, each up to the 2025 limit; **charitable**
  gifts (art. 26 ust. 1 pkt 9 lit. a) up to 6 % of income after social contributions, to the adult with the larger
  income first (skala only; the reading of "dochodu" as after contributions follows the PIT/O form).
-/

namespace PlTax

structure PersonIn where
  age : Int := 40
  wages : Int := 0
  se : Int := 0
  seRevenue : Int := 0
  pension : Int := 0
  regime : Regime := .skala
  zus : ZusKind := .standard
  ryczaltBp : Int := ryczaltDefaultBp
  female : Bool := false
  commuter : Bool := false
  returning : Bool := false
  /-- tax year (2024 or 2025; tests round 2) -/
  year : Int := 2025
  deriving Repr, Inhabited

structure Household where
  id : String := ""
  year : Int := 2025
  adults : List PersonIn := []
  married : Bool := false
  children : List Int := []
  interest : Int := 0
  dividends : Int := 0
  capitalGains : Int := 0
  rentalIncome : Int := 0
  charitable : Int := 0
  pensionContributions : Int := 0
  rentalOnePerson : Bool := false
  filing : String := "best"
  /-- `pltax --fy-start` (convention mode only; Eurostat earn_net ESMS 3.4: "Income tax and social security
  contributions parameters refer to the beginning of the fiscal year, i.e. changes occurring later during the year are
  ignored"). In the years modelled (2022–2025) the only mid-year change of a tax or contribution parameter for skala
  taxpayers is the 1 July 2022 reform (Dz.U. 2022 poz. 1265: 12 % scale, no ulga dla pracowników). With the flag, 2022
  is taxed for the whole year by the rules in force on 1 January 2022: the 17 % / 32 % scale with the 5 100 zł reduction
  and the art. 26 ust. 4a ulga dla pracowników (`scaleTaxOld`, `hypBase`, the same functions as the art. 26 refund
  comparison), with no comparison against the 12 % tax. 2023–2025 are unchanged (no mid-year change). -/
  fyStart : Bool := false
  deriving Repr, Inhabited

/-- Stage one: everything that does not depend on how deductions are shared. -/
structure Stage1 where
  p : PersonIn
  emp : EmpSocial
  seSocial : Int
  seFP : Int
  seHealth : Int
  pensionHealth : Int
  exemptW : Int
  exemptS : Int
  kup : Int
  socialDed : Int
  skalaIncome : Int
  flatIncome : Int
  liniowyHealthDed : Int
  refundContrib : Int
  childIncome : Int
  flat : Bool
  deriving Repr

def ratio (x num den : Int) : Int := if den ≤ 0 then x else x * num / den

def stage1 (p : PersonIn) (fourPlus : Bool) (gainsShare : Int) : Stage1 :=
  let g := p.wages * 100
  let emp := empSocial p.wages (ceilingY3 p.year)
  let hasSe := p.se ≠ 0 || p.seRevenue ≠ 0
  let (sSoc, sFP0) := if hasSe then seZus p.zus p.year else (0, 0)
  let sFP := if p.regime == .ryczalt then sFP0 else sFP0
  let rev := (if p.seRevenue > 0 then p.seRevenue else pos p.se) * 100
  let young := p.age ≤ 25
  let senior := p.pension = 0 && p.age ≥ (if p.female then 60 else 65)
  let other := fourPlus || senior || p.returning
  let exW := if young || other then min g zeroPitLimit else 0
  let exS := if other then min rev (zeroPitLimit - exW) else 0
  let wt := g - exW
  let kup := if g > 0 then min wt (if p.commuter then kupCommuterAnnual else kupAnnual) else 0
  let socW := ratio emp.total wt g
  -- business income after costs and FP (FP is a cost under skala and liniowy; under ryczałt it is not deductible)
  let inc := p.se * 100 - (if p.regime == .ryczalt then 0 else sFP)
  let incT := ratio inc (rev - exS) rev
  let socS := ratio sSoc (rev - exS) rev
  let health := if hasSe then seHealth p.regime (inc - sSoc) (rev - sSoc) p.year else 0
  let ph := pctGr (p.pension * 100) healthRate
  match p.regime with
  | .skala =>
    { p, emp, seSocial := sSoc, seFP := sFP, seHealth := health, pensionHealth := ph, exemptW := exW, exemptS := exS,
      kup, socialDed := socW + (if hasSe then socS else 0),
      skalaIncome := pos (wt - kup) + p.pension * 100 + (if hasSe then incT else 0),
      flatIncome := 0, liniowyHealthDed := 0,
      refundContrib := emp.total + emp.health + ph + sSoc + health,
      childIncome := pos (wt - kup) + p.pension * 100 + incT - socW - socS + gainsShare,
      flat := false }
  | .liniowy =>
    let hd := min health (liniowyHealthCapY p.year)
    { p, emp, seSocial := sSoc, seFP := sFP, seHealth := health, pensionHealth := ph, exemptW := exW, exemptS := exS,
      kup, socialDed := socW, skalaIncome := pos (wt - kup) + p.pension * 100,
      flatIncome := (if hasSe then pos (incT - socS - hd) else 0), liniowyHealthDed := hd,
      refundContrib := emp.total + emp.health + ph,
      childIncome := pos (wt - kup) + p.pension * 100 - socW + (if hasSe then incT - socS - hd else 0) + gainsShare,
      flat := hasSe }
  | .ryczalt =>
    { p, emp, seSocial := sSoc, seFP := sFP, seHealth := health, pensionHealth := ph, exemptW := exW, exemptS := exS,
      kup, socialDed := socW, skalaIncome := pos (wt - kup) + p.pension * 100,
      flatIncome := (if hasSe then pos (rev - exS - socS - health / 2) else 0), liniowyHealthDed := 0,
      refundContrib := emp.total + emp.health + ph,
      childIncome := pos (wt - kup) + p.pension * 100 - socW + gainsShare,
      flat := hasSe }

/-- Stage two: a person's taxes once the IKZE and gift deductions are placed. -/
structure Stage2 where
  s : Stage1
  ikzeSkala : Int
  ikzeFlat : Int
  gift : Int
  baseZl : Int
  flatBaseZl : Int
  flatTax : Int
  deriving Repr

def stage2 (s : Stage1) (ikzeS ikzeF gift : Int) : Stage2 :=
  let baseZl := zl (pos (s.skalaIncome - s.socialDed - ikzeS - gift))
  let fb := zl (pos (s.flatIncome - ikzeF))
  let ft := match s.p.regime with
    | .skala => 0
    | .liniowy => if s.flat then zl (fb * 100 * flatRate / 10000) * 100 else 0
    | .ryczalt => if s.flat then zl (pctGr (fb * 100) s.p.ryczaltBp) * 100 else 0
  { s, ikzeSkala := ikzeS, ikzeFlat := ikzeF, gift, baseZl, flatBaseZl := fb, flatTax := ft }

/-- Child relief for `n` minors, annual, grosze (art. 27f ust. 2). -/
def childRelief (n : Nat) : Int :=
  (List.range n).foldl (fun acc k => acc + 12 * (if k < 2 then childMonthly12 else if k = 2 then childMonthly3
    else childMonthly4)) 0

/-- Relief used against tax `t` and paid out up to `cap`: (used, refund). -/
def reliefSplit (r t cap : Int) : Int × Int :=
  let used := min r (pos t)
  (used, min (r - used) (pos cap))

def rentTax (g : Int) : Int := pctGr (min g rentThreshold) rentLow + pctGr (pos (g - rentThreshold)) rentHigh

structure Result where
  persons : List Stage2
  filing : String
  skalaTax : Int
  relief : Int
  reliefUsed : Int
  reliefRefund : Int
  skalaNet : Int
  flatTaxes : Int
  investTax : Int
  gainsTax : Int
  rentalTax : Int
  incomeTax : Int
  employeeSocial : Int
  benefits : Int
  benefit800 : Int
  dobryStartTotal : Int
  unsupported : List String
  deriving Repr

def allocIkze (ss : List Stage1) (total : Int) : List (Int × Int) :=
  let rec go : List Stage1 → Int → List (Int × Int)
    | [], _ => []
    | s :: rest, rem =>
      let lim := if s.p.se ≠ 0 then ikzeLimitSelf else ikzeLimit
      let a := min (pos rem) (min lim (pos (s.skalaIncome - s.socialDed)))
      let b := min (pos (rem - a)) (min (lim - a) s.flatIncome)
      (a, b) :: go rest (rem - a - b)
  go ss total

def giftCap (s : Stage1) (ikze : Int) : Int := pctGr (pos (s.skalaIncome - s.socialDed - ikze)) giftCapBp

def compute (h : Household) : Result :=
  let minors := h.children.filter (fun a => a ≤ 17)
  let deps := h.children.filter (fun a => a ≤ 24)
  let fourPlus := deps.length ≥ 4
  let nA : Int := h.adults.length
  let gains := h.capitalGains * 100
  let gShare := if nA = 0 then 0 else gains / nA
  let s1 := h.adults.map (fun p => stage1 { p with year := h.year } fourPlus gShare)
  let ik := allocIkze s1 (h.pensionContributions * 100)
  -- gifts: to the adult with the larger room first
  let caps := (s1.zip ik).map (fun (s, (a, _)) => giftCap s a)
  let gTot := h.charitable * 100
  let gifts : List Int := match caps with
    | [c1, c2] => if c1 ≥ c2 then [min gTot c1, min (pos (gTot - min gTot c1)) c2]
                  else [min (pos (gTot - min gTot c2)) c1, min gTot c2]
    | [c1] => [min gTot c1]
    | _ => caps.map (fun _ => 0)
  let s2 := ((s1.zip ik).zip gifts).map (fun ((s, (a, b)), gf) => stage2 s a b gf)
  let anyFlat := s2.any (fun x => x.s.flat)
  let bases := s2.map (fun x => x.baseZl)
  -- 2022 (Dz.U. 2022 poz. 1265 art. 26): each tax is the smaller of the 12 % tax and the hypothetical Polski Ład tax,
  -- for a taxpayer whose revenue A is within the art. 26 ust. 2 band
  let y22 := h.year = 2022
  let aRev : List Int := s2.map (fun x => pos (x.s.p.wages * 100 - x.s.exemptW) / 100
    + (if x.s.p.regime == .skala then pos x.s.p.se else 0))
  let perTax := (bases.zip aRev).map (fun (b, a) =>
    if y22 && h.fyStart then scaleTaxOld (100 * hypBase b a)
    else if y22 && refund2022Eligible a then min (scaleTax (100 * b)) (scaleTaxOld (100 * hypBase b a)) else scaleTax (100 * b))
  let sepT := perTax.foldl (· + ·) 0
  let n := minors.length
  let r0 := childRelief n
  let caps27f := s2.map (fun x => x.s.refundContrib)
  let capSum := caps27f.foldl (· + ·) 0
  let incSum := (s2.map (fun x => x.s.childIncome)).foldl (· + ·) 0
  let twoMarried := h.married && nA = 2
  let singleParent := nA = 1 && !h.married && deps.length > 0
  -- one child: income limit (art. 27f ust. 2 pkt 1)
  let r := if n = 1 then
      (if twoMarried || singleParent then (if incSum ≤ oneChildLimitCouple then r0 else 0)
       else r0)  -- unmarried couple / single: checked per claimant below
    else r0
  -- options (filing name, art. 27 tax, used, refund)
  let opts : List (String × Int × Int × Int) :=
    if twoMarried then
      let (u, f) := reliefSplit r sepT capSum
      let sep := ("separate (art. 6 ust. 1)", sepT, u, f)
      match bases with
      | [a, b] =>
        if anyFlat then [sep]
        else
          let jt0 := jointTax a b
          let halfA := (aRev.foldl (· + ·) 0) / 2
          let jtOld := 2 * scaleTaxOld (50 * zl (pos (100 * (a + b) - 2 * ulgaKS halfA)))
          let jt := if y22 && h.fyStart then jtOld
            else if y22 && refund2022Eligible halfA then min jt0 jtOld else jt0
          let (u2, f2) := reliefSplit r jt capSum
          [sep, ("joint (art. 6 ust. 2)", jt, u2, f2)]
      | _ => [sep]
    else if nA = 1 then
      let lim := if singleParent then oneChildLimitCouple else oneChildLimitSingle
      let rr := if n = 1 && incSum > lim then 0 else r
      let (u, f) := reliefSplit rr sepT capSum
      let sep := ("individual", sepT, u, f)
      match bases with
      | [a] =>
        if singleParent && !anyFlat then
          let st0 := splitTax a
          let a1 := aRev.headD 0
          let st := if y22 && h.fyStart then 2 * scaleTaxOld (50 * hypBase a a1)
            else if y22 && refund2022Eligible a1 then min st0 (2 * scaleTaxOld (50 * hypBase a a1)) else st0
          let (u2, f2) := reliefSplit rr st capSum
          [sep, ("single parent (art. 6 ust. 4d)", st, u2, f2)]
        else [sep]
      | _ => [sep]
    else
      -- unmarried adults: the relief to the one parent who gains most
      let cands := (s2.zip perTax).map (fun (x, t) =>
        let rr := if n = 1 && x.s.childIncome > oneChildLimitSingle then 0 else r
        let (u, f) := reliefSplit rr t x.s.refundContrib
        u + f)
      let best := cands.foldl max 0
      let usedPart := min best (pos sepT)
      [("individual (unmarried adults)", sepT, usedPart, best - usedPart)]
  let net (o : String × Int × Int × Int) : Int := o.2.1 - o.2.2.1 - o.2.2.2
  let chosen := match h.filing with
    | "separate" => opts.head!
    | "joint" => (opts.getLast?).getD opts.head!
    | _ => opts.foldl (fun b o => if net o < net b then o else b) opts.head!
  let flatT := (s2.map (fun x => x.flatTax)).foldl (· + ·) 0
  let invT := zl (pctGr ((h.interest + h.dividends) * 100) flatRate) * 100
  let gainsT := zl (pctGr gains flatRate) * 100
  let rentG := h.rentalIncome * 100
  let rentT := if twoMarried && !h.rentalOnePerson then
      2 * (zl (rentTax (rentG / 2)) * 100)
    else zl (rentTax rentG) * 100
  let skalaNet := net chosen
  let incomeTaxZl := zl skalaNet + (flatT + invT + gainsT + rentT) / 100
  let soc := (s2.map (fun x => x.s.emp.total + x.s.emp.health + x.s.pensionHealth + x.s.seSocial + x.s.seFP
    + x.s.seHealth)).foldl (· + ·) 0
  let b800 := benefitChildAnnual h.year * minors.length
  let ds := 300 * (h.children.filter (fun a => 6 ≤ a && a ≤ 19)).length
  let uns : List String :=
    (if h.year = 2024 then ["tax year 2024: SUS ceiling 234 720 zł (M.P. 2023 poz. 1342); IKZE limits are the 2025 values"] else if h.year = 2023 then ["tax year 2023: SUS ceiling 208 050 zł (M.P. 2022 poz. 1014), 500 zł świadczenie wychowawcze; IKZE limits are the 2025 values"] else if h.year = 2022 then ["tax year 2022: 12 % scale with the art. 26 refund of Dz.U. 2022 poz. 1265 (hypothetical Polski Ład tax with the ulga dla pracowników), SUS ceiling 177 660 zł (M.P. 2021 poz. 1056), 500 zł świadczenie wychowawcze; IKZE limits and the January-June withholding are not modelled"] else if h.year ≠ 2025 then [s!"tax year {h.year} not modelled: the 2025 law was applied"] else []) ++
    (if h.adults.any (fun p => p.age = 25) then ["art. 21 ust. 1 pkt 148: an adult aged 25 turns 26 during 2025; exemption taken for the whole year"] else []) ++
    (if h.children.any (fun a => a = 17) then ["a child aged 17 turns 18 during 2025: 800+ and art. 27f taken for the whole year"] else []) ++
    (if h.children.any (fun a => 18 ≤ a && a ≤ 24) then ["children aged 18-24 taken to be in school (art. 6 ust. 4c pkt 3); art. 27f ust. 6 relief for them not modelled"] else []) ++
    (if h.adults.any (fun p => 0 < p.wages && p.wages < 15000) then ["Zdrowotna art. 83 ust. 1 cap of the health contribution at the 2021-law advance not modelled (binds below about 1 250 zł a month)"] else []) ++
    (if (s2.map (fun x => x.gift)).foldl (· + ·) 0 < gTot then ["charitable gifts above the 6 % limit (or by liniowy/ryczałt taxpayers) not deducted"] else []) ++
    (if (s2.map (fun x => x.ikzeSkala + x.ikzeFlat)).foldl (· + ·) 0 < h.pensionContributions * 100 then ["pensionContributions above the IKZE limits or income not deducted"] else []) ++
    (if nA > 2 then ["more than two adults: treated as separate taxpayers"] else [])
  { persons := s2, filing := chosen.1, skalaTax := chosen.2.1, relief := r, reliefUsed := chosen.2.2.1,
    reliefRefund := chosen.2.2.2, skalaNet, flatTaxes := flatT, investTax := invT, gainsTax := gainsT,
    rentalTax := rentT, incomeTax := incomeTaxZl, employeeSocial := zl soc, benefits := b800 + ds,
    benefit800 := b800, dobryStartTotal := ds, unsupported := uns }

end PlTax
