import PTTax.Years

/-!
# One household, 2025: from the contract household to the IRS, social contributions and abono de família

Order of the CIRS: gross income by category → deduções específicas (arts 25, 31, 53) → IRS Jovem exemption
(art. 12-B, exempt income kept for the rate, art. 22 n.º 4 and 7) → mínimo de existência abatimento (art. 70) →
rendimento coletável (art. 22) → taxas gerais with the quociente conjugal (arts 68, 69) → taxa adicional de
solidariedade (art. 68-A) → deduções à coleta in the order of art. 78 (dependentes art. 78-A, despesas gerais
art. 78-B), never below zero (art. 78-A n.º 1 "até ao seu montante") → autonomous / liberatory rates on income not
englobed (arts 71, 72), with the englobamento option per category (art. 22 n.º 3 b) and n.º 5, arts 71 n.º 6,
72 n.º 13).

Household mapping (contract): investment income split equally between two adults (`half1`/`half2`); every listed
child is a dependent (art. 13; children over 18 assumed students under 25); `selfEmployment` = categoria B,
regime simplificado, professional services of the art. 151 table (coefficient 0,75); `rentalIncome` = housing
lease of less than five years (art. 72 n.º 2, 25 %); `capitalGains` = listed shares held > 365 days (art. 72
n.º 1 c), 28 %). A married couple takes the cheaper of joint and separate taxation (art. 13 n.º 2 / art. 59: an
option); each income category's englobamento is taken when it lowers the household's IRS. Extra input fields:
`pt_jovemYear1`, `pt_jovemYear2` (the n-th year of income for IRS Jovem, 1-10, with age ≤ 35),
`pt_despesasGerais` (euros of invoices qualifying for art. 78-B, household), `pt_unit` ("joint"/"separate").
-/

namespace PTTax
open TaxKernel

/-- One taxpayer's own income (cents). -/
structure Person where
  wages : Int := 0
  selfEmp : Int := 0
  pension : Int := 0
  age : Nat := 40
  jovemYear : Int := 0
  interest : Int := 0
  dividends : Int := 0
  gains : Int := 0
  rent : Int := 0
  deriving Repr, Inhabited

/-- Which categories the household englobes (art. 22 n.º 5: all income of the category or none). -/
structure Englob where
  capital : Bool := false   -- categoria E: interest and dividends (art. 71 n.º 6)
  gains : Bool := false     -- categoria G: capital gains (art. 72 n.º 13)
  rent : Bool := false      -- categoria F: rental income (art. 72 n.º 13)
  deriving Repr, Inhabited, DecidableEq

def bpOf (rate x : Int) : Int := divR .halfUp (rate * x) 10000
def pctOf (p x : Int) : Int := divR .halfUp (p * x) 100

/-- Employee contribution, Código Contributivo art. 53 (11 %, no ceiling). -/
def ssEmployee (w : Int) : Int := bpOf tsuEmployee (pos w)
/-- Independent contribution, Código Contributivo arts 162 n.º 1 a) and 168 n.º 1: 21,4 % of 70 % of services. -/
def ssIndependent (s : Int) : Int := divR .halfUp (tsuIndependent * independentBasePct * pos s) 1000000

/-- One person's figures before the household is assembled. -/
structure PersonCalc where
  ss : Int
  exempt : Int        -- IRS Jovem exempt income (art. 12-B)
  dedEsp : Int        -- deduções específicas (arts 25, 31, 53) as art. 70 n.º 5 b) counts them
  netWork : Int       -- categories A, B, H after deduções específicas and the exemption
  englobed : Int      -- capital income englobed (E at 50 % for dividends, G, F)
  rb : Int            -- rendimentos brutos of art. 70 n.º 5 a) (all categories, exempt included)
  liberatoria : Int   -- income taxed at the art. 71 taxa liberatória (not englobed)
  autonomous : Int    -- tax at the art. 71/72 rates on income not englobed (cents)
  meEligible : Bool   -- predominantly A / B professional / H (art. 70 n.º 2)
  deriving Repr, Inhabited

def personCalc (p : Person) (e : Englob) (y : YP := y2025) : PersonCalc :=
  let ssA := ssEmployee p.wages
  let ss := ssA + ssIndependent p.selfEmp
  let bTax := pctOf coefProfessional (pos p.selfEmp)              -- art. 31 n.º 1 b)
  -- art. 12-B: exemption on A and B income, capped at 55 × IAS
  let pct := if y.jovem && decide (p.age ≤ jovemMaxAge) then jovemPct p.jovemYear else 0
  let exTotal := min (pctOf pct (pos p.wages + bTax)) jovemCap
  let exA := min exTotal (pos p.wages)
  let exB := exTotal - exA
  let wA := pos p.wages - exA
  -- art. 25 n.º 1 a) and n.º 2: the greater of 8,54 × IAS and the contributions, "até à sua concorrência"
  let deA := min wA (max y.dedEsp ssA)
  let deH := min (pos p.pension) y.dedEsp                    -- art. 53 n.º 1-2
  let netWork := (wA - deA) + (bTax - exB) + (pos p.pension - deH)
  let eCap := if e.capital then p.interest + pctOf dividendEnglobPct p.dividends else 0
  let eG := if e.gains then p.gains else 0
  let eF := if e.rent then p.rent else 0
  let lib := if e.capital then 0 else p.interest + p.dividends
  let auto := (if e.capital then 0 else bpOf rateLiberatoria (p.interest + p.dividends))
    + (if e.gains then 0 else bpOf rateGains (pos p.gains)) + (if e.rent then 0 else bpOf rateRentHousing (pos p.rent))
  let rb := pos p.wages + pos p.selfEmp + pos p.pension + p.interest + p.dividends + pos p.gains + pos p.rent
  { ss, exempt := exTotal, dedEsp := deA + (pos p.selfEmp - bTax) + deH, netWork, englobed := eCap + eG + eF,
    rb, liberatoria := lib, autonomous := auto,
    meEligible := decide (rb < 2 * (pos p.wages + pos p.selfEmp + pos p.pension)) }

/-- Ages in descending order (insertion sort: structural, so `decide` can evaluate it). -/
def insDesc (a : Nat) : List Nat → List Nat
  | [] => [a]
  | b :: l => if a ≥ b then a :: b :: l else b :: insDesc a l

def sortDesc : List Nat → List Nat
  | [] => []
  | a :: l => insDesc a (sortDesc l)

/-- Art. 78-A for the household's dependents (ages at 31 December): 600 € each; + 126 € if ≤ 3 years; + 300 €
for the second and later dependents ≤ 6 years, "independentemente da idade do primeiro" (the eldest is the first);
n.º 4: the two additions are not cumulative (the larger applies). -/
def dependentsDeduction (ages : List Nat) (y : YP := y2025) : Int :=
  let sorted := sortDesc ages
  (sorted.zipIdx.map fun (a, i) =>
    let b126 := if a ≤ 3 then dedUnder3 else 0
    let b300 := if i ≥ 1 then (if a ≤ 3 then y.depSecUnder3 else if a ≤ 6 then y.depSec4to6 else 0) else 0
    dedDependent + max b126 b300).foldl (· + ·) 0

/-- Art. 78-B: general family expenses (cents of qualifying invoices) for `nSP` taxpayers. -/
def despesasGeraisDed (amount : Int) (nSP : Int) (mono : Bool) : Int :=
  if mono then min (pctOf despGeraisRateMono amount) despGeraisCapMono
  else min (pctOf despGeraisRate amount) (limDespesasGerais * nSP)

/-- The IRS of one declaration (one or two taxpayers) with divisor `n` (1 or 2, art. 69). -/
structure DeclCalc where
  coletavel : Int
  meAbate : Int
  coleta68 : Int
  solidarity : Int
  deductions : Int
  autonomous : Int
  irs : Int            -- art. 68 + 68-A − deductions (≥ 0) + autonomous taxes
  deriving Repr, Inhabited

def declCalc (ps : List PersonCalc) (n : Int) (depDed despGer : Int) (bands : Bool := false)
    (y : YP := y2025) (famLimit : Int := 0) : DeclCalc :=
  let nSP : Int := ps.length
  let sumRB := (ps.map (·.rb)).foldl (· + ·) 0
  let sumLib := (ps.map (·.liberatoria)).foldl (· + ·) 0
  -- art. 70 n.º 4: no abatimento for anyone when the household passes either limit
  let excluded := decide (sumRB > 22 * 14 * y.ias / 10 * nSP) || decide (sumLib > 14 * y.ias * nSP)
  let abates := ps.map fun p => if p.meEligible && !excluded then meAbateY y p.rb p.dedEsp else 0
  let abate := abates.foldl (· + ·) 0
  let rc := pos ((ps.map fun p => p.netWork + p.englobed).foldl (· + ·) 0 - abate)
  let ex := (ps.map (·.exempt)).foldl (· + ·) 0
  -- art. 22 n.º 4 and 7: exempt income counts for the rate applied to the rest
  let coleta0 := if ex = 0 then divR .halfUp (art68ScaledByY y bands n rc) 100000
    else divR .halfUp (art68ScaledByY y bands n (rc + ex) * rc) ((rc + ex) * 100000)
  -- income 2022-2023 (Lei 114/2017 wording of art. 70): n.º 2-3 no art. 68 tax for 3-4 / 5+ dependents up to
  -- the limit (`famLimit`, halved per spouse when not taxed jointly); n.º 1 and 4: the art. 68 tax may not leave a
  -- titular whose income is predominantly A, B (Portaria 1011/2001) or H less than the floor `y.meRef`
  let coleta1 := if !y.meNew && famLimit > 0 && rc ≤ famLimit then 0 else coleta0
  let earners := ps.filter (·.rb > 0)
  let coleta := if !y.meNew && !earners.isEmpty && earners.all (·.meEligible) then
      min coleta1 (pos (sumRB - y.meRef * (earners.length : Int)))
    else coleta1
  let sol := solidarityCents n rc
  let ded := min (coleta + sol) (depDed + despGer)
  let auto := (ps.map (·.autonomous)).foldl (· + ·) 0
  { coletavel := rc, meAbate := abate, coleta68 := coleta, solidarity := sol, deductions := ded,
    autonomous := auto, irs := coleta + sol - ded + auto }

/-- All the choices a household can make. -/
def englobOptions : List Englob :=
  [false, true].flatMap fun a => [false, true].flatMap fun b => [false, true].map fun c =>
    { capital := a, gains := b, rent := c }

structure HouseCalc where
  unit : String
  englob : Englob
  decls : List DeclCalc
  irs : Int
  solidarity : Int
  ss : Int
  ps : List PersonCalc
  deriving Inhabited

/-- Assess the household under one unit ("joint", "separate", "single") and one englobamento choice. -/
def houseCalc (persons : List Person) (ages : List Nat) (despGer : Int) (unit : String) (e : Englob)
    (bands : Bool := false) (y : YP := y2025) (despGer2 : Int := 0) : HouseCalc :=
  let ps := persons.map (personCalc · e y)
  let ss := (ps.map (·.ss)).foldl (· + ·) 0
  let dep := dependentsDeduction ages y
  let fam (k : Nat) (half : Bool) : Int :=
    let v := if k ≥ 5 then y.famEx5 else if k ≥ 3 then y.famEx34 else 0
    if half then v / 2 else v
  let nk := ages.length
  let mono := persons.length == 1 && !ages.isEmpty
  let decls :=
    if unit == "joint" then [declCalc ps 2 dep (despesasGeraisDed despGer 2 false) bands y (fam nk false)]
    else if persons.length == 1 then [declCalc ps 1 dep (despesasGeraisDed despGer 1 mono) bands y (fam nk false)]
    else if unit == "separate" then
      -- married, separate: each spouse half of the dependants' deductions (art. 78 n.º 9) and expenses
      ps.map fun p => declCalc [p] 1 (dep / 2) (despesasGeraisDed (despGer / 2) 1 false) bands y (fam nk true)
    else
      -- two unmarried adults: the children are in the first adult's agregado; `despGer2` is the second adult's own
      -- art. 78-B invoices (0 unless a convention flag gives them, see Country.lean)
      ps.zipIdx.map fun (p, i) =>
        declCalc [p] 1 (if i = 0 then dep else 0) (despesasGeraisDed (if i = 0 then despGer else despGer2) 1 (i = 0 && !ages.isEmpty)) bands y
          (if i = 0 then fam nk false else 0)
  { unit, englob := e, decls, irs := (decls.map (·.irs)).foldl (· + ·) 0,
    solidarity := (decls.map (·.solidarity)).foldl (· + ·) 0, ss, ps }

/-! ## Abono de família para crianças e jovens (DL 176/2003; Portaria 112/2025/1) -/

def nthD (l : List Int) (i : Nat) : Int := l.getD i 0

/-- The escalão (1-5) of reference income `income / div` (cents/year; compared exactly, no rounding): DL 176/2003 art. 14 n.º 2-3, limits × 14 × IAS. -/
def abonoEscalao (income div : Int) (y : YP := y2025) : Nat :=
  let lims := abonoLimitsTenths.map fun t => t * 14 * y.ias
  1 + (lims.filter fun l => decide (l * div < 10 * income)).length

/-- Annual abono for the household: `income` = the agregado's total income (cents), children's ages, monoparental.
Ages: ≤ 2 = "≤ 36 meses", 3-5 = "36-72 meses", ≥ 6 = "> 72 meses" (age in whole years during most of the year).
Titulares: children under 24 (art. 11 n.º 2; those over 16 assumed in education). -/
def abono (income : Int) (ages : List Nat) (mono : Bool) (annualRound : Bool := false) (y : YP := y2025) : Int × Nat :=
  let tit := sortDesc (ages.filter (· < 24))
  let nT := tit.length
  if nT = 0 then (0, 0) else
  let esc := abonoEscalao income (nT + 1) y         -- art. 9 n.º 1 a): divided by titulares + 1
  if esc ≥ 5 then (0, esc) else
  let i := esc - 1
  let row := y.abonoM.getD i (0, 0, 0)
  let monthly := tit.zipIdx.map fun (a, k) =>
    let base := if a ≤ 2 then row.1 else if a ≤ 5 then row.2.1 else row.2.2
    let maj := if k ≥ 1 ∧ a ≤ 2 then (if nT = 2 then nthD y.abonoMaj2 i else nthD y.abonoMajN i) else 0
    let m := base + maj
    let m := if mono && !annualRound then m + pctOf abonoMonoPct m else m
    -- art. 15: 1.º escalão, aged 6-16, an extra month in September
    let extra := if esc = 1 ∧ 6 ≤ a ∧ a ≤ 16 then m else 0
    let y := 12 * m + extra
    if mono && annualRound then y + pctOf abonoMonoPct y else y
  (monthly.foldl (· + ·) 0, esc)

end PTTax
