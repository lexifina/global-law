import ESTax.Assess

/-!
# The contract household → Spanish declaraciones (Comunidad de Madrid resident, ejercicio 2025)

Mapping (`~/cmp/shared/CONTRACT.md`; choices stated here and in FINDINGS "model notes"):
* wages = rendimientos íntegros del trabajo (contrato indefinido, Régimen General); pension = art. 17.2 a) 1.º;
  selfEmployment = rendimiento neto de actividades económicas (own RETA cuotas assumed already deducted; no
  contributions computed).
* interest + dividends + capitalGains = base del ahorro (art. 46), split equally between two adults (first gets the odd
  cent); rentalIncome = rendimiento neto del capital inmobiliario, split equally, reduced by `rentalReductionPct`
  (art. 23.2, 50/60/70/90) if the input gives it; pensionContributions and charitable split equally.
* children: every child aged under 25 is a descendant giving the mínimo (art. 58; no own income); in a two-adult
  household both adults are the parents (art. 61 1.ª: prorated "por partes iguales").
* the "mother" for art. 81 (maternidad, women only) is adult 2 in a couple, the adult in a one-adult household; an input
  field `"mother": 1|2` overrides. Children under 3 give the Madrid birth deduction (art. 4: year of birth and the two
  following).
* married → the couple may file jointly (art. 82 1.ª); one adult with minor children, not married → joint
  monoparental (art. 82 2.ª, art. 84.2 4.º). The model computes every allowed option and keeps the cheapest (as the
  AEAT's Renta Web shows both); `--separate` / `--joint` or `"filing": "separate"|"joint"` force one.
* Amounts in the input may have cents (read from the raw JSON); the kernel's `Canon` keeps whole euros.
-/

namespace ESTax
open TaxKernel Lean

/-- A JSON number as cents, half up. -/
def numCents (n : JsonNumber) : Int :=
  let d : Int := (10 : Int) ^ n.exponent
  (2 * 100 * n.mantissa + d) / (2 * d)

def centsField (j : Json) (k : String) : Int :=
  match j.getObjVal? k with
  | .ok (.num n) => numCents n
  | _ => 0

def rawAdults (c : Canon) : List Json :=
  match c.raw.getObjVal? "adults" with
  | .ok (.arr a) => a.toList
  | _ => []

/-- The household after mapping: members without the shared income, and the household totals in cents. -/
structure HH where
  ages : List Nat
  wages : List Int
  pensions : List Int
  selfEmp : List Int
  savings : Int
  rental : Int
  pensionContrib : Int
  charitable : Int
  married : Bool
  kids : List Nat     -- ages of descendants (under 25), oldest first
  mother : Nat        -- 0-based index
  /-- ejercicio (round 5): `c.year`; 2022-2025 have their own `YP` -/
  year : Nat := 2025
  deriving Repr, Inhabited

def insertDesc (x : Nat) : List Nat → List Nat
  | [] => [x]
  | y :: ys => if x ≥ y then x :: y :: ys else y :: insertDesc x ys

def sortDesc (l : List Nat) : List Nat := l.foldl (fun acc x => insertDesc x acc) []

def toHH (c : Canon) : HH :=
  let ra := rawAdults c
  let n := c.adults.length
  let ages := c.adults.map (·.age)
  let fld (k : String) : List Int := (List.range n).map fun i => centsField (ra.getD i Json.null) k
  let pct := (c.int? "rentalReductionPct").getD 0
  let rental := centsField c.raw "rentalIncome"
  let rentalNet := if rental > 0 then rental - mulDiv rental pct 100 else rental
  let mother := match c.int? "mother" with
    | some 1 => 0
    | some 2 => (if n == 2 then 1 else 0)
    | _ => (if n == 2 then 1 else 0)
  { ages, wages := fld "wages", pensions := fld "pension", selfEmp := fld "selfEmployment",
    savings := centsField c.raw "interest" + centsField c.raw "dividends" + centsField c.raw "capitalGains",
    rental := rentalNet, pensionContrib := centsField c.raw "pensionContributions",
    charitable := centsField c.raw "charitable", married := c.married,
    kids := sortDesc ((c.children.map (·.age)).filter (· < 25)), mother, year := c.year }

def HH.n (h : HH) : Nat := h.ages.length
def HH.yp (h : HH) : YP := ypFor h.year

/-- Share `x` of adult `i` among `n` adults (first gets the odd cent). -/
def share (n i : Nat) (x : Int) : Int := if n ≤ 1 then x else if i == 0 then half1 x else half2 x

def HH.member (h : HH) (i : Nat) : Member :=
  { age := h.ages.getD i 40, wages := h.wages.getD i 0, pension := h.pensions.getD i 0,
    selfEmp := h.selfEmp.getD i 0, rental := share h.n i h.rental, savings := share h.n i h.savings,
    pensionContrib := share h.n i h.pensionContrib, charitable := share h.n i h.charitable, year := h.year }

/-! ## Mínimos -/

def minPersonal (age : Nat) : Int :=
  minContribuyente + (if age > 65 then minMas65 else 0) + (if age > 75 then minMas75 else 0)
def minPersonalMad (age : Nat) : Int :=
  minContribuyenteMad + (if age > 65 then minMas65Mad else 0) + (if age > 75 then minMas75Mad else 0)
def minPersonalMadY (yp : YP) (age : Nat) : Int :=
  yp.minContribuyenteMad + (if age > 65 then yp.minMas65Mad else 0) + (if age > 75 then yp.minMas75Mad else 0)

/-- Mínimo por descendientes for the whole family (art. 58 / Madrid art. 2 bis). -/
def minDescTotal (amts : List Int) (under3 : Int) (kids : List Nat) : Int :=
  sumL ((List.range kids.length).map (ordinal amts)) + under3 * (kids.filter (· < 3)).length

def HH.descEst (h : HH) : Int := minDescTotal minDesc minDescMenor3 h.kids
def HH.descMad (h : HH) : Int := minDescTotal h.yp.minDescMad h.yp.minDescMenor3Mad h.kids
def HH.under3 (h : HH) : Nat := (h.kids.filter (· < 3)).length
def HH.minors (h : HH) : Nat := (h.kids.filter (· < 18)).length

/-! ## Refundable deductions (art. 81, 81 bis) -/

def HH.worker (h : HH) (i : Nat) : Bool := h.wages.getD i 0 + h.selfEmp.getD i 0 > 0
def HH.entitled81bis (h : HH) (i : Nat) : Bool := h.worker i || h.pensions.getD i 0 > 0

/-- art. 81 bis.1 c): (part subject to the art. 81 bis.2 limit, part outside it) for the family. -/
def HH.famNumParts (h : HH) : Int × Int :=
  let k := h.kids.length
  if k ≥ 5 then (famNum, famNum + famNumHijoExtra * (k - 5))
  else if k ≥ 3 then (famNum, famNumHijoExtra * (k - 3))
  else if k == 2 && h.n == 1 && !h.married then (famNum, 0)
  else (0, 0)

/-- Adult `i`'s art. 81 bis amount: an equal share among the entitled adults; the limited part capped by the adult's
total contributions (employee + employer lower bound) when the adult is an employee. -/
def HH.famNumOf (h : HH) (i : Nat) : Int :=
  let ent := (List.range h.n).filter h.entitled81bis
  if !(ent.contains i) then 0 else
  let k : Int := ent.length
  let (lim, extra) := h.famNumParts
  let limShare := lim / k
  let w := h.wages.getD i 0
  let cap := if w > 0 then ssEmployeeY h.yp w + ssEmployerLBY h.yp w else limShare
  min limShare cap + extra / k

def HH.maternidadOf (h : HH) (i : Nat) : Int :=
  if i == h.mother && h.worker i then maternidad * h.under3 else 0

/-! ## Madrid deductions (DLeg 1/2010 arts. 4, 14, 18) -/

def HH.biOf (h : HH) (i : Nat) : Int := (h.member i).biAlone
def HH.biSum (h : HH) : Int := sumL ((List.range h.n).map h.biOf)

def HH.fam2 (h : HH) : Bool := h.kids.length ≥ 2 && h.biSum ≤ h.yp.madFam2Lim

/-- Art. 4 for an individual return of adult `i` (prorated "por partes iguales" when both parents live with the
child); art. 18.1 limits. -/
def HH.nacInd (h : HH) (i : Nat) : Int :=
  let full := h.yp.madNacimiento * h.under3
  if h.biOf i ≤ h.yp.madLimInd && h.biSum ≤ h.yp.madLimUnidad then share h.n i full else 0

def HH.nacJoint (h : HH) : Int :=
  if h.biSum ≤ h.yp.madLimConj && h.biSum ≤ h.yp.madLimUnidad then h.yp.madNacimiento * h.under3 else 0

/-! ## The declaraciones -/

def HH.separateRets (h : HH) : List Ret :=
  (List.range h.n).map fun i =>
    { members := [h.member i],
      minEst := minPersonal (h.ages.getD i 40) + share h.n i h.descEst,
      minMad := minPersonalMadY h.yp (h.ages.getD i 40) + share h.n i h.descMad,
      madNac := h.nacInd i, madFam2 := h.fam2,
      maternidad := h.maternidadOf i, famNum := h.famNumOf i, year := h.year }

/-- The joint declaración, if the household may file one: married (art. 82 1.ª, reduction 3.400 €) or one
unmarried adult with minor children (art. 82 2.ª, reduction 2.150 €). One mínimo del contribuyente (art. 84.2 2.º),
the age increases of each spouse, the full mínimo por descendientes. -/
def HH.ageExtraEst (h : HH) : Int := sumL (h.ages.map (fun a => minPersonal a - minContribuyente))
def HH.ageExtraMad (h : HH) : Int := sumL (h.ages.map (fun a => minPersonalMadY h.yp a - h.yp.minContribuyenteMad))

def HH.jointBase (h : HH) : Ret :=
  let idx := List.range h.n
  { members := idx.map h.member,
    minEst := minContribuyente + h.ageExtraEst + h.descEst,
    minMad := h.yp.minContribuyenteMad + h.ageExtraMad + h.descMad,
    madNac := h.nacJoint, madFam2 := h.fam2,
    maternidad := sumL (idx.map h.maternidadOf), famNum := sumL (idx.map h.famNumOf), year := h.year }

def HH.jointRet? (h : HH) : Option Ret :=
  if h.married then some { h.jointBase with redJoint := redConjunta }
  else if h.n == 1 && h.minors > 0 then some { h.jointBase with redJoint := redMonoparental }
  else none

inductive Filing where | separate | joint
  deriving Repr, DecidableEq, Inhabited

def Filing.name : Filing → String
  | .separate => "individual"
  | .joint => "conjunta"

structure Result where
  filing : Filing
  liqs : List Liq
  sepTotal : Int
  jointTotal : Option Int
  ss : Int
  deriving Repr, Inhabited

def totalOf (ls : List Liq) : Int := sumL (ls.map Liq.total)

/-- Compute every allowed filing and keep the cheapest (or the forced one if allowed). -/
def assess (h : HH) (force : Option Filing := none) : Result :=
  let sep := h.separateRets.map liquidate
  let st := totalOf sep
  let ss := sumL (h.wages.map (ssEmployeeY h.yp))
  match h.jointRet? with
  | none => { filing := .separate, liqs := sep, sepTotal := st, jointTotal := none, ss }
  | some jr =>
    let jl := liquidate jr
    let jt := jl.total
    let useJoint := match force with
      | some .joint => true
      | some .separate => false
      | none => jt < st
    if useJoint then { filing := .joint, liqs := [jl], sepTotal := st, jointTotal := some jt, ss }
    else { filing := .separate, liqs := sep, sepTotal := st, jointTotal := some jt, ss }

end ESTax
