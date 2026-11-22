import BETax.Years

/-!
# Belgium 2025 (AI 2026): the computation, provision by provision

Household → per adult: ONSS 13,07 % less the social work bonus (loi 20.12.1999) → net remuneration → forfait art. 51
→ professional income → quotient conjugal art. 87-88 (joint returns) → art. 130 tariff → exempt sum art. 131-134
(own tariff, transfers between spouses, refundable child credit) = impôt Etat → LSF art. 5/2 impôt Etat réduit →
Brussels centimes (32,591 %) → municipal tax art. 466 on federal + regional → federal credits (fiscal work bonus
art. 289ter/1, child credit art. 134 § 3) → CSSS (loi 30.03.1994 art. 108) → Famiris family allowances.
Everything in cents; output in whole euros (half-up), cents in `detail`.
-/

namespace BETax
open TaxKernel

/-- Round half up to the cent: `n / d`. -/
def hu (n d : Int) : Int := divR .halfUp n d
/-- `rate` bp of `x` cents, half-up to the cent. -/
def pctBp (rate x : Int) : Int := hu (rate * x) 10000
/-- A schedule's tax in cents (ticks are cents × bp). -/
def schedTax (s : Schedule) (x : Int) : Int := hu (s.ticks (pos x)) 10000

/-! ## Social -/

/-- Volet A of the work bonus for monthly reference wage `s` (cents). -/
def WorkBonus.ra (w : WorkBonus) (s : Int) : Int :=
  if s ≤ w.thrA then w.maxA else if s ≤ w.endA then pos (w.maxA - hu (w.coefA * (s - w.thrA)) 10000) else 0
/-- Volet B. -/
def WorkBonus.rb (w : WorkBonus) (s : Int) : Int :=
  if s ≤ w.thrB then w.maxB else if s ≤ w.thrA then pos (w.maxB - hu (w.coefB * (s - w.thrB)) 10000) else 0
/-- One month: (P_A, P_B) after "écrêtement ... sur le calcul basé sur le volet B et ensuite ... volet A" so that the
bonus never exceeds the personal contributions due. -/
def WorkBonus.month (w : WorkBonus) (s : Int) : Int × Int :=
  let due := pctBp onssBp s
  let a := w.ra s
  let b := w.rb s
  let excess := pos (a + b - due)
  (a - pos (excess - b), pos (b - excess))

/-- A pre-April-2024 table: R rounded to the cent ("R est arrondi arithmétiquement à l'unité la plus proche"). -/
def WbOld.r (w : WbOld) (s : Int) : Int :=
  if s ≤ w.thr then w.max
  else if s ≤ w.mid then pos (w.max - hu (w.coef1 * (s - w.thr)) 10000)
  else if s ≤ w.stop then pos (w.max2 - hu (w.coef2 * (s - w.thr)) 10000) else 0

/-- One month's (P_A, P_B). Before April 2024 there is one reduction (P = R, at most the personal contributions
due); it is booked as volet A because art. 289ter/1 credits it at 33,14 %, the volet-A rate (versions before the
replacement of al. 2 by Lprog 22.12.2023 art. 19, 1°, applicable to reductions granted from 01.04.2024). -/
def WbSpec.month : WbSpec → Int → Int × Int
  | .old w, s => (min (w.r s) (pctBp onssBp s), 0)
  | .ab w, s => w.month s

/-- Annual employee social security of one wage earner (12 equal months, each on that month's work-bonus table;
for 2025 January on the January 2025 table, February-December on the table from 1 February 2025). Returns (ONSS
gross, bonus A, bonus B). -/
def onssYear (wage : Int) (P : YearP := p2025) : Int × Int × Int :=
  if wage ≤ 0 then (0, 0, 0) else
  let s := hu wage 12
  let due := pctBp onssBp s
  let ms := P.wbMonths.map fun m => m.month s
  (12 * due, sumInts (ms.map (·.1)), sumInts (ms.map (·.2)))

/-- Art. 289ter/1: the fiscal work bonus (cap per income year). -/
def fiscalWorkBonus (a b : Int) (P : YearP := p2025) : Int :=
  min P.wbFiscalCap (hu (wbFiscalA * a) 100000 + hu (wbFiscalB * b) 100000)

/-! ## Income tax -/

/-- Art. 51: professional income after the flat-rate expenses (wages and profits are separate categories, each
with its own cap). `net` = gross less personal contributions. -/
def afterForfait (net : Int) (P : YearP := p2025) : Int := net - min P.forfaitCap (pctBp forfaitRate (pos net))

/-- Art. 132: the supplements for `n` children of which `u3` under 3. -/
def childSupp (n u3 : Nat) (P : YearP := p2025) : Int :=
  familyTotal P.childTotals P.childExtra n + P.under3Supp * (u3 : Int)

/-- Art. 133 al. 2-3: the single parent's additional supplement (taxable income `t`, net professional income `p`). -/
def spExtra (t p : Int) (P : YearP := p2025) : Int :=
  if t ≥ P.spExtraTo ∨ p < P.spExtraMinProf then 0
  else if t ≤ P.spExtraFrom then P.spExtraFull
  else hu (P.spExtraFull * (P.spExtraTo - t)) (P.spExtraTo - P.spExtraFrom)

/-- One taxpayer's position after art. 134: the layers of the exempt sum (art. 134 § 3 al. 4, 1°: "censée être
constituée consécutivement" of the base and art. 133 supplements, then the child supplements, then the art. 133 al. 2
extra supplement). -/
structure Exempt where
  nonchild : Int
  child : Int
  extra : Int := 0
  deriving Repr

def Exempt.total (e : Exempt) : Int := e.nonchild + e.child + e.extra

/-- Tax of one taxpayer after the exempt sum: art. 130 tax less the art. 134 § 2 tax on the exempt sum, not below 0. -/
def taxAfterExempt (t : Int) (e : Exempt) (P : YearP := p2025) : Int :=
  pos (schedTax P.art130 t - schedTax P.art134 e.total)

/-- Art. 134 § 3: the part of the tax on the exempt sum that cannot be set off and that relates to the child
supplements (and, al. 5, to the extra supplement); "il n'est pas tenu compte de la partie de la quotité ... qui excède
le revenu imposable et qui n'est pas constituée des suppléments". Returns (child part, extra part), before the cap. -/
def unusedParts (t : Int) (e : Exempt) (P : YearP := p2025) : Int × Int :=
  let a := min e.nonchild (pos t)
  let base := max (schedTax P.art130 t) (schedTax P.art134 a)
  let top := schedTax P.art134 (a + e.child + e.extra)
  let unused := pos (top - base)
  let taxEx := schedTax P.art134 (a + e.child + e.extra) - schedTax P.art134 (a + e.child)
  let taxCh := schedTax P.art134 (a + e.child) - schedTax P.art134 a
  let uEx := min unused taxEx
  (min (unused - uEx) taxCh, uEx)

/-- The tax position of the household's income-tax unit(s). -/
structure Position where
  taxable : List Int      -- art. 130 taxable income per return/spouse (after quotient)
  basic : Int             -- Σ art. 130 tax
  exemptTax : Int         -- Σ art. 134 tax on the exempt sums (as used)
  impotEtat : Int         -- Σ tax after the exempt sums (LSF art. 5/2 § 2, 3°-4°)
  childCredit : Int       -- art. 134 § 3 refundable credit
  quotient : Int          -- amount attributed under art. 87-88
  childrenTo : Nat        -- index of the spouse/adult carrying the art. 132 supplements
  deriving Repr

/-- A single taxpayer (or a cohabitant taxed separately). -/
def single (t p : Int) (nKids u3 : Nat) (claimsKids : Bool) (P : YearP := p2025) : Position :=
  let n := if claimsKids then nKids else 0
  let sp := claimsKids && nKids > 0
  let e : Exempt := { nonchild := P.exemptBase + (if sp then P.singleParentSupp else 0),
                      child := childSupp n (if claimsKids then u3 else 0) P,
                      extra := if sp then spExtra t p P else 0 }
  let (uc, ue) := unusedParts t e P
  let credit := min uc (P.childCreditCap * (n : Int)) + ue
  { taxable := [t], basic := schedTax P.art130 t, exemptTax := schedTax P.art134 e.total,
    impotEtat := taxAfterExempt t e P, childCredit := credit, quotient := 0, childrenTo := 0 }

/-- Two separately taxed adults (cohabitants): the sum of their positions. -/
def combine (a b : Position) (ts : List Int) (kidsTo : Nat) : Position :=
  { taxable := ts, basic := a.basic + b.basic, exemptTax := a.exemptTax + b.exemptTax,
    impotEtat := a.impotEtat + b.impotEtat, childCredit := a.childCredit + b.childCredit, quotient := 0,
    childrenTo := kidsTo }

/-- Art. 134 § 4: joint taxation with the child supplements at spouse `h` (taxable `th`), the other `l`. -/
def jointExempt (th tl : Int) (nKids u3 : Nat) (P : YearP := p2025) : Exempt × Exempt :=
  let exemptBase := P.exemptBase
  let ec := childSupp nKids u3 P
  let eh := exemptBase + ec
  let el := exemptBase
  -- 4°: "la totalité de l'excèdent" of the spouse without the supplements goes to the other spouse
  let lToH := if tl < el then el - tl else 0
  -- 3°: the excess of the spouse with the supplements, "limité ... à la différence positive entre le revenu imposable
  -- et la quotité ... de l'autre conjoint"
  let hToL := if th < eh then min (eh - th) (pos (tl - el)) else 0
  -- al. 2, 1°: the transferred part "est censée être constituée en priorité du montant de base"
  let movedBase := min hToL exemptBase
  let movedChild := hToL - movedBase
  ({ nonchild := exemptBase + lToH - movedBase, child := ec - movedChild },
   { nonchild := exemptBase - lToH + movedBase, child := movedChild })

def jointPosition (th tl : Int) (nKids u3 : Nat) (q : Int) (hIdx : Nat) (P : YearP := p2025) : Position :=
  let (eh, el) := jointExempt th tl nKids u3 P
  let (ch, _) := unusedParts th eh P
  let (cl, _) := unusedParts tl el P
  -- 6°: the credit "ne peut excéder le montant maximum ... pour les deux conjoints ensemble"
  let credit := min (ch + cl) (P.childCreditCap * (nKids : Int))
  { taxable := if hIdx = 0 then [th, tl] else [tl, th],
    basic := schedTax P.art130 th + schedTax P.art130 tl,
    exemptTax := schedTax P.art134 eh.total + schedTax P.art134 el.total,
    impotEtat := taxAfterExempt th eh P + taxAfterExempt tl el P, childCredit := credit, quotient := q,
    childrenTo := hIdx }

/-- Joint return of spouses with professional incomes p1, p2 (and no other global income): the four readings the
statute allows and their choice rules: art. 87-88 quotient "sauf si l'impôt Etat ... s'en trouve majoré"; art. 134
§ 4 al. 3 supplements to the lower-income spouse "si de ce fait l'impôt Etat ... s'en trouve diminué". -/
def joint (p1 p2 : Int) (nKids u3 : Nat) (P : YearP := p2025) : Position :=
  let (hi, lo, hiIdx) := if p1 ≥ p2 then (p1, p2, 0) else (p2, p1, 1)
  let q := attributedAmount hi lo quotientPct P.quotientCap
  let variants : List (Int × Int × Int) := [(hi, lo, 0), (hi - q, lo + q, q)]
  let cands := variants.foldr (fun (th, tl, qq) acc =>
      -- spouse with the higher taxable income carries the supplements by default (2°); the other on request (al. 3)
      let h := jointPosition th tl nKids u3 qq hiIdx P
      let l := jointPosition tl th nKids u3 qq (1 - hiIdx) P
      h :: l :: acc) []
  -- the default (no quotient, supplements at the higher income) unless another reading lowers the impôt Etat;
  -- ties keep the earlier (default) reading; equal tax prefers the larger refundable credit
  cands.foldl (fun best c =>
      if c.impotEtat - c.childCredit < best.impotEtat - best.childCredit then c else best)
    (cands.headD (single 0 0 0 0 false))

/-! ## Regional and municipal -/

/-- LSF art. 5/2 § 1: impôt Etat réduit. -/
def reduit (etat : Int) : Int := etat - hu (etat * autonomyPcm) 100000
/-- Brussels centimes additionnels on the impôt Etat réduit (LSF art. 5/1 § 1, 1°). -/
def regionalTax (red : Int) : Int := hu (red * brusselsCentimesPcm) 100000

/-! ## Family allowances (Famiris) -/

/-- Social-supplement amount per child (art. 9) for one month's barème. -/
def famSocial (b : FamBareme) (income : Int) (n : Nat) (mono : Bool) (age : Nat) : Int :=
  let pick := fun (p : Int × Int) => if age ≤ 11 then p.1 else p.2
  if income < b.plafond1 then
    if n = 1 then pick b.soc1 else if n = 2 then (if mono then pick b.soc2mono else pick b.soc2)
    else (if mono then pick b.soc3mono else pick b.soc3)
  else if income < b.plafond2 then (if n = 1 then 0 else if n = 2 then b.mid2 else b.mid3)
  else 0

/-- The Brussels regime (art. 7, 9, 35) for one month. -/
def famNewMonth (b : FamBareme) (income : Int) (ages : List Nat) (mono : Bool) (y0 : Nat := 6) : Int :=
  let n := ages.length
  let anySoc := ages.any fun a => famSocial b income n mono a > 0
  sumInts (ages.map fun a =>
    let soc := famSocial b income n mono a
    -- "Enfant unique qui ne bénéficie d'aucun des suppléments": the 0-11 amount at every age
    let base := if a ≤ 11 || (n = 1 && !anySoc) then b.base011 else b.base1217
    -- born before 01/12/2019 (art. 35, until 31/12/2025): aged at least `y0` = income year − 2019 at its end
    let ded := if a ≥ y0 then b.deduct else 0
    if a ≥ 25 then 0 else base - ded + soc)

/-- LGAF age-supplement tier for age `a` (0 = none). -/
def ageTier (a : Nat) : Nat := if a ≤ 5 then 0 else if a ≤ 11 then 1 else if a ≤ 17 then 2 else 3

/-- The transitional LGAF amounts (art. 35 ordonnance; barème part "MONTANTS LOI GÉNÉRALE"), for a family whose
children all had rights in December 2019. `frozen`: footnote (3): "le supplément d'âge de décembre 2019 ne [peut] à
aucun moment augmenter après le 31 décembre 2019" (the tier of age − 6). -/
def famOldMonth (b : FamBareme) (income : Int) (ages : List Nat) (mono : Bool) (frozen : Bool) (y0 : Nat := 6) :
    Int :=
  let sorted := (ages.toArray.qsort (· > ·)).toList   -- rank 1 = eldest
  let monoOk := mono && income ≤ b.plafond1
  let rec go (l : List Nat) (rank : Nat) : Int :=
    match l with
    | [] => 0
    | a :: rest =>
      let amt := b.old.getD rank (b.old.getLastD 0)
      let ms := if monoOk then b.oldMono.getD rank (b.oldMono.getLastD 0) else 0
      let tier := if frozen then min (ageTier a) (ageTier (a - y0)) else ageTier a
      let firstOrd := rank = 0 && ms = 0
      let agesupp := if tier = 0 then 0 else
        (if firstOrd then b.ageFirst else b.ageOther).getD (tier - 1) 0
      (if a ≥ 25 then 0 else amt + ms + agesupp) + go rest (rank + 1)
  go sorted 0

/-- The art. 15 July supplement for age `age` from a year's amounts [0-5, 6-11, 12-24]. -/
def julyAgeSuppOf (amts : List Int) (age : Nat) : Int :=
  if age ≤ 5 then amts.getD 0 0 else if age ≤ 11 then amts.getD 1 0 else if age ≤ 24 then amts.getD 2 0 else 0

/-- Annual Brussels family allowances: the twelve monthly barèmes of the income year (2025: January + 11 × February)
+ the July age supplement; the family gets the higher of the Brussels and the transitional amounts ("Famiris vous
verse toujours le montant le plus élevé"). Children with rights in December 2019 (born before 01/12/2019) are those
aged at least `y0` = year − 2019 at the end of the income year. -/
def famiris (income : Int) (ages : List Nat) (mono : Bool) (frozen : Bool) (P : YearP := p2025) : Int × Bool :=
  let ages := ages.filter (· < 25)
  if ages.isEmpty then (0, false) else
  let y0 : Nat := P.year - 2019
  let newY := sumInts (P.famMonths.map fun b => famNewMonth b income ages mono y0)
  let oldOk := ages.all (· ≥ y0)
  let oldY := if oldOk then sumInts (P.famMonths.map fun b => famOldMonth b income ages mono frozen y0)
              else 0
  let july := sumInts (ages.map (julyAgeSuppOf P.julyAmts))
  if oldY > newY then (oldY + july, true) else (newY + july, false)

/-! ## The household -/

structure Opts where
  /-- `none`: the City of Brussels' rate for the income year (`YearP.communeBp`), or with `--oecd` the OECD's
  (`YearP.oecdCommuneBp`) -/
  communeBp : Option Int := none
  frozenAge : Bool := true
  oecd : Bool := false
  janTable : Bool := false
  /-- `--eurostat`: ESMS 3.4, `YearP.startOfYear` -/
  eurostat : Bool := false
  /-- `--euromod` (convention, not statute): EUROMOD J2.0+'s documented municipal surcharge for a Brussels resident
  (`euromodBxlBp`) and its 30 June reference date for the work-bonus table and the Famiris barème (`YearP.atJune`) -/
  euromod : Bool := false
  deriving Repr

/-- EUROMOD J2.0+ convention (round 14; not statute): EUROMOD applies the average local surcharge of the region instead
of a named commune's rate. Methodology: EUROMOD Country Report Belgium 2022-2025 (JRC, 2026; `software/euromod/
country_reports/Y16_CR_BE.pdf`, sha256 f8b61921...), section 2.7.5.1.1 "Municipality taxes (tinmu_be)": "these tax
rates are calculated taking the weighted average of all local tax rates in each region (with weighting factor the
population numbers per municipality)"; Table 2.68 "Average local tax rate per region in % [2022-2025]", row
"Brussels: 6.3% (2022), 6.2% (2023), 6.2% (2024), 6.2% (2025)". The same values are in EUROMOD policy parameters
J2.0+.xlsx, sheet BE, row 31.1.1 `$tinmu_Bxl_rate`, and the model's BE.xml policy `tinmu_be`. In basis points of
the tax base (federal after reductions + regional, as `commune` below and EUROMOD's `tin_s * $tinmu_Bxl_rate`). -/
def euromodBxlBp (y : Nat) : Int := if y ≤ 2022 then 630 else 620

theorem euromodBxlBp_values : euromodBxlBp 2022 = 630 ∧ euromodBxlBp 2023 = 620 ∧ euromodBxlBp 2024 = 620 ∧
    euromodBxlBp 2025 = 620 := by decide

def parseOpts (args : List String) : Opts :=
  args.foldl (fun o a =>
    if a == "--oecd" then { o with oecd := true, communeBp := none, frozenAge := false }
    else if a == "--jan-table" then { o with janTable := true }
    else if a == "--eurostat" then { o with eurostat := true }
    else if a == "--euromod" then { o with euromod := true }
    else if a.startsWith "--commune-bp=" then
      { o with communeBp := match (toString (a.drop 13)).toInt? with | some n => some n | none => o.communeBp }
    else if a == "--unfrozen-age" then { o with frozenAge := false }
    else o) {}

def cents (x : Int) : Int := 100 * x
def euros (c : Int) : Int := hu c 100

def compute (o : Opts) (c : Canon) : Out :=
  let P0 := yearP c.year
  let P0' := if o.euromod then P0.atJune else P0
  let P1 := if o.eurostat then P0'.startOfYear else P0'
  let P := if o.janTable then P1.janOnly else P1
  let communeBp := o.communeBp.getD
    (if o.oecd then P.oecdCommuneBp else if o.euromod then euromodBxlBp c.year else P.communeBp)
  let ads := c.adults
  let joint? := c.isCouple && c.married
  let cohab := c.isCouple && !c.married && (c.bool? "cohabiting").getD false
  -- social security and professional income per adult
  let per := ads.map fun a =>
    let w := cents a.wages
    let (onss, ba, bb) := onssYear w P
    let ssc := onss - ba - bb
    let profW := afterForfait (w - ssc) P
    let profS := afterForfait (cents a.selfEmployment) P
    (w, onss, ba, bb, ssc, profW + profS + cents a.pension)
  let profs := per.map fun (_, _, _, _, _, p) => p
  let nK := c.nChildren
  let u3 := c.childrenUnder 3
  -- income tax position
  let pos0 : Position :=
    if joint? then joint (profs.getD 0 0) (profs.getD 1 0) nK u3 P
    else match profs with
      | [p] => single p p nK u3 true P
      | [p1, p2] =>
        -- separately taxed adults: the children are declared by the one who runs the household; both readings
        let a := single p1 p1 nK u3 true P
        let b := single p2 p2 nK u3 false P
        let a' := single p1 p1 nK u3 false P
        let b' := single p2 p2 nK u3 true P
        let s1 := combine a b [p1, p2] 0
        let s2 := combine a' b' [p1, p2] 1
        if s2.impotEtat - s2.childCredit < s1.impotEtat - s1.childCredit then s2 else s1
      | _ => single 0 0 0 0 false
  let etat := pos0.impotEtat
  let red := reduit etat
  let reg := regionalTax red
  -- separately taxed movable income (art. 171): dividends above the art. 21, 14° exemption per taxpayer, interest
  let nTaxpayers : Int := if ads.length = 2 then 2 else 1
  let divTaxable := pos (cents c.dividends - P.dividendExempt * nTaxpayers)
  let movable := pctBp movableRate (divTaxable + cents c.interest)
  -- federal credits
  let wbf := sumInts (per.map fun (_, _, ba, bb, _, _) => fiscalWorkBonus ba bb P)
  let federal := red + movable - wbf - pos0.childCredit
  -- municipal tax (art. 466): on the "impôt total" (federal + regional), less the tax on movable income (al. 2)
  let commune := pctBp communeBp (red + reg)
  -- CSSS (loi 30.03.1994 art. 108): household income = Σ taxable income, joint or individual scale
  let hhIncome := sumInts pos0.taxable
  let hasWage := per.any fun (w, _, _, _, _, _) => w > 0
  let csss := if !hasWage then 0
    else if joint? then csssJoint hhIncome
    else sumInts ((pos0.taxable.zip per).map fun (t, (w, _, _, _, _, _)) => if w > 0 then csssIndividual t else 0)
  let onssTot := sumInts (per.map fun (_, _, _, _, ssc, _) => ssc)
  -- family allowances
  let mono := ads.length = 1 || (c.isCouple && !c.married && !cohab)
  let (fam, oldReg) := famiris hhIncome (c.children.map (·.age)) mono o.frozenAge P
  let unsupported : List String :=
    (if c.rentalIncome ≠ 0 then ["rentalIncome (taxed on indexed cadastral income, art. 7-13: not modelled)"] else []) ++
    (if ads.any (·.pension > 0) then ["pension: taxed as professional income without the art. 147 reduction"] else []) ++
    (if ads.any (·.selfEmployment > 0) then ["self-employed social contributions (INASTI) not modelled"] else []) ++
    (if c.charitable ≠ 0 || c.pensionContributions ≠ 0 then ["federal tax reductions (gifts art. 145/33, pension savings art. 145/16) not modelled"] else []) ++
    (if c.capitalGains ≠ 0 then ["capitalGains: shares held privately, normal management (art. 90, 1°): 0 in 2025"] else []) ++
    (if supportedYear c.year then [] else
      ["income year " ++ toString c.year ++ " not implemented: computed with the parameters of income year " ++ toString P.year]) ++
    (if o.euromod then ["--euromod (EUROMOD J2.0+ convention, not statute): municipal surcharge at EUROMOD's average for Brussels (EUROMOD Country Report Belgium 2022-2025, 2.7.5.1.1 Table 2.68: 6.3 % 2022, 6.2 % 2023-2025) instead of the City of Brussels' rate; ONSS work-bonus table and Famiris barème of 30 June for all twelve months (EUROMOD reference date, Nowcasting prices note Feb 2025, 1.3-1.4)"] else []) ++
    (if c.year = 2022 && o.communeBp.isNone && !o.oecd && !o.euromod then
      ["income year 2022 (AI 2023): City of Brussels municipal rate 6 % carried back from the AI 2024 list (AI 2023 list not reachable)"] else []) ++
    (if o.eurostat then ["--eurostat (Eurostat earn_net ESMS 3.4): ONSS work-bonus table of January for all twelve months; family allowances: the Brussels and transitional amounts are the same for every age 6-11, so the most-generous-within-6-11 rule changes nothing"] else []) ++
    (if c.year = 2022 then
      ["income year 2022: the January-February Famiris barème deducts the art. 35 amount for children born before 01/01/2020 (later barèmes: 01/12/2019); one cut-off used"] else [])
  Out.make c "BE" "EUR" (euros federal) (surtaxes := [("regionalBrussels", euros reg)])
    (localIncomeTax := euros commune) (employeeSocial := euros (onssTot + csss)) (benefits := euros fam)
    (detail := [Out.d "taxableIncome" (euros hhIncome), Out.d "taxableIncomeCents" hhIncome,
      Out.d "taxBeforeCredits" (euros pos0.basic), Out.d "basicTaxCents" pos0.basic,
      Out.d "exemptSumTaxCents" pos0.exemptTax, Out.d "impotEtatCents" etat, Out.d "impotEtatReduitCents" red,
      Out.d "regionalCents" reg, Out.d "municipalCents" commune, Out.d "movableTaxCents" movable,
      Out.d "fiscalWorkBonusCents" wbf, Out.d "childCreditCents" pos0.childCredit,
      Out.d "quotientCents" pos0.quotient, Out.d "childrenToAdult" pos0.childrenTo,
      Out.d "onssCents" (sumInts (per.map fun (_, o, _, _, _, _) => o)),
      Out.d "workBonusACents" (sumInts (per.map fun (_, _, a, _, _, _) => a)),
      Out.d "workBonusBCents" (sumInts (per.map fun (_, _, _, b, _, _) => b)),
      Out.d "csssCents" csss, Out.d "familyAllowanceCents" fam, Out.dBool "famirisTransitional" oldReg,
      Out.d "federalCents" federal, Out.d "communeBp" communeBp,
      Out.dStr "note" (if P.year = 2025 then "Income year 2025, exercice d'imposition 2026; resident of the City of Brussels"
        else "Income year " ++ toString P.year ++ ", exercice d'imposition " ++ toString (P.year + 1) ++
          "; resident of the City of Brussels")])
    (unsupported := unsupported)

def out (c : Canon) : Out := compute {} c

def country : Country :=
  { code := "BE", name := "Belgium (federal + Brussels-Capital Region + City of Brussels), income year 2025 (AI 2026)",
    currency := "EUR", year := "2025", compute := out, computeWith := fun args c => compute (parseOpts args) c }

end BETax
