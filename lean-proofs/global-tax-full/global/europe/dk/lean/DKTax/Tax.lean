import DKTax.Person

/-!
# The tax computation (PSL §§ 5-13, 19; kommuneskat and kirkeskat)

All taxes are computed exactly in *ticks* (kroner × basis points, `BP` = 10 000 ticks per krone; municipal and
church tax with the rate in 10⁻⁷ are converted to ticks by `/ 1000`, half up). The statute prescribes no rounding of
the taxes themselves; Skatteministeriet's worked examples print them in øre. Output lines are rounded half up to
whole kroner at the very end.

Order of the statute (PSL § 9, § 11, § 12, § 13):
1. gross taxes: bundskat (§ 6), topskat on personal income (§ 7, stk. 3/7) and on positive nettokapitalindkomst
   (§ 7, stk. 4/8-11) with the rate cut of the skatteloft (§ 19), aktieindkomstskat (§ 8 a: the 27 pct. part is a
   final tax, the 42 pct. part enters slutskatten), kommuneskat and kirkeskat on skattepligtig indkomst;
2. § 13: a deficit in skattepligtig indkomst goes to the spouse's taxable income, then its tax value (municipal +
   church rate) is set against bundskat, topskat and § 8 a, stk. 2 tax (own, then spouse's); rest carried forward;
3. § 9/§ 12: personfradrag — the state value (bundskat rate) against bundskat, then topskat and § 8 a, stk. 2; the
   local value (municipal + church rate) against kommune- and kirkeskat; whatever is left of either against the
   other taxes (§ 12, stk. 2); what is still left goes to the spouse (§ 10, stk. 3);
4. § 11: 8 pct. of negative nettokapitalindkomst up to 50.000 kr. (100.000 kr. for spouses), against the taxes in
   the order bundskat, topskat, § 8 a stk. 2, kommuneskat, kirkeskat; unused part to the spouse (stk. 4);
5. § 8 a, stk. 5-6: negative aktieindkomst gives a negative tax set against slutskatten (own, then spouse's); the
   rest is carried forward (reported, not paid).
-/

namespace DKTax
open TaxKernel

/-- Household options: municipality, church membership, OECD conventions. -/
structure Opts where
  munRate7 : Int
  churchRate7 : Int := 0
  church : Bool := false
  oecd : Bool := false
  deriving Repr

/-- A person's taxes in ticks, in the statute's order. -/
structure TaxVec where
  bund : Int := 0
  top : Int := 0
  ak42 : Int := 0
  mun : Int := 0
  ch : Int := 0
  deriving Repr, Inhabited

def TaxVec.total (t : TaxVec) : Int := t.bund + t.top + t.ak42 + t.mun + t.ch

/-- Set what is left of a reduction `r` against one tax `t` (down to no less than 0): the tax after, and the rest. -/
def take1 (t r : Int) : Int × Int :=
  let u := min (pos t) (pos r)
  (t - u, r - u)

/-- State taxes first (bundskat, topskat, § 8 a stk. 2), then local (kommune-, kirkeskat); returns the rest. -/
def absorbStateFirst (v : TaxVec) (r : Int) : TaxVec × Int :=
  let a := take1 v.bund r
  let b := take1 v.top a.2
  let c := take1 v.ak42 b.2
  let d := take1 v.mun c.2
  let e := take1 v.ch d.2
  ({ bund := a.1, top := b.1, ak42 := c.1, mun := d.1, ch := e.1 }, e.2)

/-- State taxes only. -/
def absorbState (v : TaxVec) (r : Int) : TaxVec × Int :=
  let a := take1 v.bund r
  let b := take1 v.top a.2
  let c := take1 v.ak42 b.2
  ({ v with bund := a.1, top := b.1, ak42 := c.1 }, c.2)

/-- Local taxes first, then state. -/
def absorbLocalFirst (v : TaxVec) (r : Int) : TaxVec × Int :=
  let d := take1 v.mun r
  let e := take1 v.ch d.2
  let a := take1 v.bund e.2
  let b := take1 v.top a.2
  let c := take1 v.ak42 b.2
  ({ bund := a.1, top := b.1, ak42 := c.1, mun := d.1, ch := e.1 }, c.2)

/-- PSL § 19: the topskat rate after the skatteloft, in 10⁻⁷ (`cap` in bp: 5207 or 4200). -/
def topRate7 (P : Params) (o : Opts) (cap : Int) : Int :=
  let sum7 := P.bundRate * 1000 + P.topRate * 1000 + o.munRate7
  P.topRate * 1000 - pos (sum7 - cap * 1000)

/-- rate7 × kroner → ticks (half up). -/
def r7 (rate7 x : Int) : Int := divR .halfUp (rate7 * x) 1000

/-- Topskat tick schedules (kernel `Schedule.flatAbove`): 15 pct. above the bundfradrag. -/
def topSched (P : Params) : Schedule := Schedule.flatAbove P.topThreshold P.topRate

/-- Aktieindkomst schedule (kernel `Schedule.ofList`) for a progressionsgrænse `lim`: 27 pct. then 42 pct. -/
def aktieSched (P : Params) (lim : Int) : Schedule := Schedule.ofList [(0, P.aktieLow), (lim, P.aktieHigh)]

/-- Everything computed for one person (ticks unless stated). -/
structure PRes where
  b : PBase
  taxable : Int            -- kroner, after § 13 transfer
  bundBase : Int           -- kroner
  topBase : Int            -- kroner: personal income + capital over grundbeløb (the "topskattegrundlag")
  gross : TaxVec           -- before any reduction
  bundGross : Int
  topPersonal : Int
  topCapital : Int
  ak27 : Int
  ak42 : Int
  aktieCredit : Int        -- negative tax (§ 8 a, stk. 5)
  final : TaxVec           -- after all reductions
  pfState : Int            -- value of personfradrag at the bundskat rate used against this person's taxes
  pfUsed : Int
  deficitValue : Int
  nedslag11 : Int
  carryForward : Int
  deriving Repr, Inhabited

/-! ## The computation as pure functions (kernel-reducible, so concrete households are theorems by `decide`) -/

def locRate7 (o : Opts) : Int := o.munRate7 + (if o.church then o.churchRate7 else 0)

/-- Topskat (2025; § 7 mellemskat from 2026) on personal income after the skatteloft cut, plus the 2026 § 7 a topskat
and § 8 toptopskat (no skatteloft). -/
def topPers (P : Params) (o : Opts) (b : PBase) : Int :=
  (topSched P).ticks b.personal * topRate7 P o P.skatteloft / (P.topRate * 1000)
    + (P.extraBands.map fun (t, r) => (Schedule.flatAbove t r).ticks b.personal).foldl (· + ·) 0

/-- § 7, stk. 4: topskat on an unmarried person's positive nettokapitalindkomst, after the § 19, stk. 2 cut. -/
def topCapSingle (P : Params) (o : Opts) (b : PBase) : Int :=
  let base := b.personal + pos (b.kapital - P.kapGrund)
  ((topSched P).ticks base - (topSched P).ticks b.personal) * topRate7 P o P.kapLoft / (P.topRate * 1000)

/-- § 7, stk. 5, 8-11: spouses' combined positive nettokapitalindkomst, taxed at the spouse with the higher
stk. 7 base against twice the grundbeløb, shared by each spouse's capital income over the grundbeløb. -/
def topCapCouple (P : Params) (o : Opts) (b1 b2 : PBase) : Int × Int :=
  let kapC := pos (b1.kapital + b2.kapital)
  let hi2 := decide (b2.personal > b1.personal)
  let bh := if hi2 then b2 else b1
  let base := bh.personal + pos (kapC - 2 * P.kapGrund)
  let t := ((topSched P).ticks base - (topSched P).ticks bh.personal) * topRate7 P o P.kapLoft / (P.topRate * 1000)
  let ex1 := pos (b1.kapital - P.kapGrund)
  let ex2 := pos (b2.kapital - P.kapGrund)
  if ex1 + ex2 = 0 then (if hi2 then (0, t) else (t, 0))
  else (t * ex1 / (ex1 + ex2), t - t * ex1 / (ex1 + ex2))

/-- Gross taxes of one person (`posKap`: positive nettokapitalindkomst in the bundskat base after § 6, stk. 3;
`tc`: topskat on capital; `ak`: aktieindkomst after § 8 a, stk. 6; `lim`, `negLim`: its thresholds). -/
def grossRes (P : Params) (o : Opts) (b : PBase) (ti posKap tc ak lim negLim : Int) : PRes :=
  let bundGross := P.bundRate * pos (b.personal + posKap)
  let tp := topPers P o b
  let akT := (aktieSched P lim).ticks (pos ak)
  let ak27 := P.aktieLow * min (pos ak) lim
  let ak42 := akT - ak27
  let akCredit := if ak < 0 then (aktieSched P negLim).ticks (-ak) else 0
  let mun := r7 o.munRate7 (pos ti)
  let ch := if o.church then r7 o.churchRate7 (pos ti) else 0
  let g : TaxVec := { bund := bundGross, top := tp + tc, ak42, mun, ch }
  { b, taxable := ti, bundBase := b.personal + posKap, topBase := b.personal + pos (b.kapital - P.kapGrund),
    gross := g, bundGross, topPersonal := tp, topCapital := tc, ak27, ak42, aktieCredit := akCredit, final := g,
    pfState := 0, pfUsed := 0, deficitValue := 0, nedslag11 := 0, carryForward := 0 }

/-- § 13, stk. 1: the tax value of a deficit against the person's own state taxes; returns what is left. -/
def stepDeficit (o : Opts) (r : PRes) : PRes × Int :=
  let dv := r7 (locRate7 o) (pos (-r.taxable))
  let vr := absorbState r.final dv
  ({ r with final := vr.1, deficitValue := dv }, vr.2)

/-- §§ 9, 12: own personfradrag; returns the unused state-rate and municipal-rate values. -/
def stepPf (P : Params) (o : Opts) (r : PRes) : PRes × Int × Int :=
  let vs := P.bundRate * P.pf
  let vk := r7 (locRate7 o) P.pf
  let a1 := absorbState r.final vs
  let a2 := absorbLocalFirst a1.1 vk
  let a3 := absorbLocalFirst a2.1 a1.2
  let a4 := absorbStateFirst a3.1 a2.2
  ({ r with final := a4.1, pfState := vs - a1.2, pfUsed := r.final.total - a4.1.total }, a3.2, a4.2)

/-- § 10, stk. 3: the spouse's unused personfradrag values (state-rate value against state taxes first, municipal
value against kommune- and kirkeskat first). -/
def stepPfIn (r : PRes) (ls lk : Int) : PRes :=
  let st (v : TaxVec) := v.bund + v.top + v.ak42
  let v1 := (absorbStateFirst r.final ls).1
  let v2 := (absorbLocalFirst v1 lk).1
  { r with final := v2, pfUsed := r.pfUsed + (r.final.total - v2.total), pfState := r.pfState + (st r.final - st v1) }

/-- § 11: nedslag `8 pct. × min(neg, limit)` against the taxes in the statute's order. -/
def stepNed (P : Params) (r : PRes) (neg limit : Int) : PRes × Int :=
  let ned := P.negKapRate * min neg limit
  let vr := absorbStateFirst r.final ned
  ({ r with final := vr.1, nedslag11 := ned }, vr.2)

/-- Set an amount against the taxes (state first); returns what is left. -/
def stepAbsorb (r : PRes) (x : Int) : PRes × Int :=
  let vr := absorbStateFirst r.final x
  ({ r with final := vr.1 }, vr.2)

def stepAbsorbState (r : PRes) (x : Int) : PRes × Int :=
  let vr := absorbState r.final x
  ({ r with final := vr.1 }, vr.2)

def addCarry (r : PRes) (x : Int) : PRes := { r with carryForward := r.carryForward + x }

/-- An unmarried person (or a person whose partner is not a spouse in law). -/
def single (P : Params) (o : Opts) (b : PBase) : PRes :=
  let r0 := grossRes P o b b.taxable (pos b.kapital) (topCapSingle P o b) b.aktie P.aktieLimit P.aktieLimit
  let s1 := stepDeficit o r0
  let r1 := addCarry s1.1 s1.2
  let r2 := (stepPf P o r1).1
  let r3 := (stepNed P r2 (pos (-b.kapital)) P.negKapLimit).1
  let s4 := stepAbsorb r3 r3.aktieCredit
  addCarry s4.1 s4.2

/-- § 13, stk. 2: a deficit in taxable income first reduces the spouse's taxable income. -/
def deficitTransfer (t1 t2 : Int) : Int × Int :=
  if t1 < 0 ∧ t2 > 0 then (t1 + min (-t1) t2, t2 - min (-t1) t2)
  else if t2 < 0 ∧ t1 > 0 then (t1 - min (-t2) t1, t2 + min (-t2) t1) else (t1, t2)

/-- Spouses living together at the end of the year (PSL §§ 6 stk. 3, 7 stk. 5-11, 8 a stk. 4/6, 10 stk. 3,
11 stk. 3-4, 13 stk. 2). -/
def couple (P : Params) (o : Opts) (b1 b2 : PBase) : PRes × PRes :=
  let tt := deficitTransfer b1.taxable b2.taxable
  -- § 6, stk. 3
  let pk1 := pos (b1.kapital + min 0 b2.kapital)
  let pk2 := pos (b2.kapital + min 0 b1.kapital)
  let tc := topCapCouple P o b1 b2
  -- § 8 a, stk. 6 (offset) and stk. 4 (threshold transfer)
  let aa := deficitTransfer b1.aktie b2.aktie
  let A := P.aktieLimit
  let lim1 := A + min A (pos (A - aa.2))
  let lim2 := A + min A (pos (A - aa.1))
  let n1 := pos (-aa.1)
  let n2 := pos (-aa.2)
  let both := decide (n1 > 0 ∧ n2 > 0)
  let nl1 := if both then 2 * A * n1 / (n1 + n2) else 2 * A
  let nl2 := if both then 2 * A * n2 / (n1 + n2) else 2 * A
  let g1 := grossRes P o b1 tt.1 pk1 tc.1 aa.1 lim1 nl1
  let g2 := grossRes P o b2 tt.2 pk2 tc.2 aa.2 lim2 nl2
  -- § 13: deficit values, own then spouse's
  let d1 := stepDeficit o g1
  let d2 := stepDeficit o g2
  let x2 := stepAbsorbState d2.1 d1.2
  let x1 := stepAbsorbState d1.1 d2.2
  let c1 := addCarry x1.1 x2.2
  let c2 := addCarry x2.1 x1.2
  -- personfradrag, own then the spouse's unused values
  let p1 := stepPf P o c1
  let p2 := stepPf P o c2
  let q2 := stepPfIn p2.1 p1.2.1 p1.2.2
  let q1 := stepPfIn p1.1 p2.2.1 p2.2.2
  -- § 11 with stk. 3 (offset and limit transfer) and stk. 4 (unused nedslag to the spouse)
  let ng1 := pos (-(b1.kapital) - pos b2.kapital)
  let ng2 := pos (-(b2.kapital) - pos b1.kapital)
  let e1 := stepNed P q1 ng1 (P.negKapLimit + pos (P.negKapLimit - ng2))
  let e2 := stepNed P q2 ng2 (P.negKapLimit + pos (P.negKapLimit - ng1))
  let f2 := (stepAbsorb e2.1 e1.2).1
  let f1 := (stepAbsorb e1.1 e2.2).1
  -- § 8 a, stk. 5-6: negative tax on aktieindkomst, own then spouse's slutskat
  let h1 := stepAbsorb f1 f1.aktieCredit
  let h2 := stepAbsorb f2 f2.aktieCredit
  let k2 := stepAbsorb h2.1 h1.2
  let k1 := stepAbsorb h1.1 h2.2
  (addCarry k1.1 k2.2, addCarry k2.1 k1.2)

/-- Results for one or two persons. -/
def computeTaxes (P : Params) (o : Opts) (married : Bool) (bs : List PBase) : List PRes :=
  match bs with
  | [b] => [single P o b]
  | [b1, b2] => if married then [(couple P o b1 b2).1, (couple P o b1 b2).2] else [single P o b1, single P o b2]
  | l => l.map (single P o)

end DKTax
