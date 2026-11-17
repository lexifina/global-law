import FrTax.Income

/-!
# Parts, the scale, the cap on the quotient familial, the décote

Parts are counted in quarters (`Int`), so one part is 4 and the married base of two parts is 8.
-/

namespace FrTax

/-! ## Number of parts (art. 194, 195, 196, 196 A bis) -/

structure Family where
  /-- Children wholly in the household's charge: minors or disabled (0CF), attached adult children (0DJ),
  disabled people living under the roof (0CR, art. 196 A bis). -/
  excl : Int
  /-- Of those, holders of the disability card (0CG, and every 0CR person): art. 195, 2. -/
  exclDisabled : Int
  /-- Children in shared residence (0CH), and of those the disabled (0CI). -/
  alt : Int
  altDisabled : Int
  deriving Repr

def family (d : Decl) : Family where
  excl := d.get "0CF" + d.get "0DJ" + d.get "0CR"
  exclDisabled := d.get "0CG" + d.get "0CR"
  alt := d.get "0CH"
  altDisabled := d.get "0CI"

def Family.any (f : Family) : Bool := f.excl + f.alt > 0

/-- **art. 194, I.** Quarters for children: a half part (2) for each of the first two, a whole part (4)
from the third; children in shared residence count after the others, at half those amounts. -/
def childQuarters (f : Family) : Int :=
  let e := f.excl
  let ex := if e ≤ 2 then 2 * e else 4 + 4 * (e - 2)
  -- shared-residence children rank from e + 1
  let firstTwo := max 0 (min f.alt (2 - min e 2))
  ex + firstTwo + 2 * (f.alt - firstTwo)

/-- Single parent living alone (box T, art. 194, II): a half part more with a child wholly in charge, a
quarter part with children only in shared residence. -/
def singleParentQuarters (d : Decl) (f : Family) : Int :=
  -- "contribuables célibataires ou divorcés": not a widow(er), whose child already brings the couple's two parts
  if d.couple || d.widowed || !d.has "0BT" then 0
  else if f.excl > 0 then 2
  -- "la majoration est de 0,25 pour un seul enfant et de 0,5 si les enfants sont au moins deux"
  else if f.alt ≥ 2 then 2 else if f.alt = 1 then 1 else 0

/-- "âgé de plus de 74 ans" (art. 195, 1, f and 6), on 31 December of the income year: born in the year
minus 74 or before (M: AGV + 1 − 74 > 0). -/
def over74 (d : Decl) (box : String) : Bool :=
  let b := d.get box
  b > 0 && b ≤ (d.year : Int) - 74

/-- Box L (art. 195, 1, a, b, e) requires that the taxpayer "vivent seuls"; box N says they do not, and cancels
it (as M does: V_0AL × (1 − V_0AN); the DGFiP's simulator agrees). -/
def caseL (d : Decl) : Bool := d.has "0AL" && !d.has "0AN"

/-- Box W counts only when its age condition holds. -/
def veteran (d : Decl) : Bool := d.has "0AW" && over74 d "0DA"

/-- art. 195, 1: single, divorced or widowed with no child in charge: one half part (once) when any of
a, b, e (box L: brought up a child alone for five years), c, d, d bis (disabled: P; war widow: G) or f
(war veteran over 74: W) applies. -/
def art195_1 (d : Decl) (f : Family) : Bool :=
  !d.couple && !f.any && (caseL d || d.has "0AP" || d.has "0AG" || veteran d)

/-- Of art. 195, 1, is it only case L (a, b, e), with its own cap (art. 197, I, 2, third paragraph)? -/
def art195_1_onlyL (d : Decl) (f : Family) : Bool :=
  art195_1 d f && caseL d && !(d.has "0AP" || d.has "0AG" || veteran d)

/-- Quarters added by art. 195, 2 to 6 (disability, veterans), outside art. 195, 1. -/
def art195_other (d : Decl) (f : Family) : Int :=
  let disabledKids := 2 * f.exclDisabled + f.altDisabled         -- 195, 2
  let coupleDis : Int :=
    if d.couple then
      (if d.has "0AP" && d.has "0AF" then 4                         -- 195, 4
       else if d.has "0AP" || d.has "0AF" then 2                    -- 195, 3
       else if d.has "0AS" && (over74 d "0DA" || over74 d "0DB") then 2 else 0)   -- 195, 6
    else if f.any && d.has "0AP" then 2 else 0                      -- 195, 5
  disabledKids + coupleDis

/-- The base: one part, or two for a couple; a widow(er) with a child in charge has the couple's two
parts (art. 194, I, "Marié ou veuf ayant ..."). -/
def baseQuarters (d : Decl) (f : Family) : Int :=
  if d.couple then 8 else if d.widowed && f.any then 8 else 4

def quarters (d : Decl) : Int :=
  let f := family d
  baseQuarters d f + childQuarters f + singleParentQuarters d f + (if art195_1 d f then 2 else 0)
    + art195_other d f

/-! ## The scale (art. 197, I, 1; art. 193) -/

/-- **art. 193, 197, I, 1.** The tax on income `r` with `q` quarters of part: the tax on one part of income,
`r / (q/4)`, times the number of parts. Exactly, in 1/400 euro:
`Σ rate% * max(0, min(4r, q*hi) - q*lo)` for the slices `[lo, hi)`. Rounded to the euro (art. 1657). -/
def scaleTax (p : Params) (r q : Int) : Int :=
  let s (rate lo : Int) (hi : Option Int) : Int :=
    let top := match hi with | some h => min (4 * r) (q * h) | none => 4 * r
    rate * pos (top - q * lo)
  rnd (s 11 p.b1 (some p.b2) + s 30 p.b2 (some p.b3) + s 41 p.b3 (some p.b4) + s 45 p.b4 none) 400

/-! ## The cap on the quotient familial (art. 197, I, 2) -/

structure Capped where
  full : Int        -- tax with all the parts
  ref : Int         -- tax with the base part(s)
  cap : Int         -- most the extra parts may save
  capped : Int      -- max full (ref - cap)
  complement : Int  -- complementary reduction (paras 4 and 5), at most capped - full
  tax : Int         -- capped - complement
  deriving Repr

def capped (p : Params) (d : Decl) (r : Int) : Capped :=
  let f := family d
  let q := quarters d
  let refQ : Int := if d.couple then 8 else 4
  let full := scaleTax p r q
  let ref := scaleTax p r refQ
  let extra := q - refQ
  -- quarters with a special cap
  let tQ := singleParentQuarters d f
  -- caps in half-euros (a quarter part may save half of `qfHalf`)
  -- the larger cap is "au titre du premier enfant à charge": a child (0CF, 0DJ), not a disabled person under
  -- the roof (0CR); its shared-residence variant needs "uniquement des enfants" in shared residence
  let kidsExcl : Int := d.get "0CF" + d.get "0DJ"
  let (spQ, spCap2) : Int × Int :=
    if tQ > 0 && kidsExcl > 0 then (4, 2 * p.qfFirstChildSingle)   -- T + first child: one whole part
    else if tQ > 0 && f.excl = 0 then                              -- shared residence only: each of the
      let k := min f.alt 2                                         -- first two children's half part
      (2 * k, k * p.qfFirstChildSingle)                            -- (0.25 + 0.25 of T) at half the cap
    else (0, 0)
  let lQ : Int := if art195_1_onlyL d f then 2 else 0
  let normalQ := extra - spQ - lQ
  -- The cap is an amount of reduction, rounded to the euro (art. 1657, 1); M: PLAQAR = arr(...).
  let cap := rnd (spCap2 + (if lQ > 0 then 2 * p.qfCaseL else 0) + normalQ * p.qfHalf) 2
  let cappedTax := max full (ref - cap)
  -- complementary reductions
  -- Only half parts capped under the *first* paragraph earn the complement ("lorsque la réduction de leur
  -- cotisation d'impôt est plafonnée en application du premier alinéa"): case L alone (195, 1, a, b, e) is
  -- capped under the third paragraph, so it earns none.
  let halfParts195 : Int :=                                        -- in quarters
    (if art195_1 d f && lQ = 0 then 2 else 0) + art195_other d f
  let widowQ : Int := if !d.couple && d.widowed && f.any then 1 else 0
  -- a quarter part earns half the complement; the amount is rounded (art. 1657, 1; M: arr(PLAF_PLACOMP/2 * V_0CI))
  let compl := rnd (halfParts195 * p.qfComplement) 2 + widowQ * p.qfWidow
  let c := if cappedTax > full then min compl (cappedTax - full) else 0
  { full, ref, cap, capped := cappedTax, complement := c, tax := cappedTax - c }

/-! ## The décote (art. 197, I, 4, a) -/

def decote (p : Params) (d : Decl) (t : Int) : Int :=
  let base := if d.couple then p.decCouple else p.decSingle
  -- the décote is "la différence entre 889 € et 45,25 % de son montant": the difference is rounded
  min t (pos (rnd (base * 10000 - 4525 * t) 10000))

end FrTax

namespace FrTax

/-! ## The DGFiP's printed scale ("barème de l'impôt", brochure pratique, chapter "Calcul de l'impôt")

The brochure prints the tax after the cap and the décote for income `r` and `q` quarters of part, in five
situations. `tableTax` computes a cell from the statute alone, for any number of parts, including those no
household reaches without other effects (e.g. 2.5 parts for a single person without box T).
Situations: 0 single (box T not ticked), 1 single with box L (1.5 parts), 2 single parent (box T),
3 widow(er) with a child, 4 married or in a civil partnership. -/
def tableTax (p : Params) (situation : Nat) (q r : Int) : Int :=
  let refQ : Int := if situation = 4 then 8 else 4
  let full := scaleTax p r q
  let ref := scaleTax p r refQ
  let extra := q - refQ
  let cap2 : Int :=                                                        -- in half-euros
    if situation = 1 then 2 * p.qfCaseL
    else if situation = 2 then 2 * p.qfFirstChildSingle + (extra - 4) * p.qfHalf
    else extra * p.qfHalf
  let capped := max full (ref - rnd cap2 2)
  let compl := if situation = 3 && capped > full then min p.qfWidow (capped - full) else 0
  let t := capped - compl
  let base := if situation = 4 then p.decCouple else p.decSingle
  t - min t (pos (rnd (base * 10000 - 4525 * t) 10000))

end FrTax
