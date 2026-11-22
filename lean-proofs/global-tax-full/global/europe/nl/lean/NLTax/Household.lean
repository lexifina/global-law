import NLTax.Withholding

/-!
# NLTax.Household: the contract household through the Dutch assessment

Mapping of the canonical household (`cmp/shared/CONTRACT.md`) to Dutch law, stated once:

* **Fiscal partners** (art. 1.2 Wet IB; toeslagpartner, Awir art. 3): two adults who are married, or who live
  together with a child (art. 1.2 lid 1 counts unmarried cohabitants with a child as partners). Two unmarried adults
  without children are assessed separately and the household's investment items are split equally.
* **wages** are loon. `pensionContributions` (household total) are read as employee contributions to an
  occupational pension scheme, which are not part of loon (Wet LB 1964 art. 11 lid 1 c), shared out in proportion to
  wages. Under `--oecd` an adult's contribution is the OECD's own convention (`Params.oecdPensionRate`).
* **selfEmployment** is winst uit onderneming; the urencriterium is taken as met (extension `nlUrencriterium`);
  zelfstandigenaftrek (art. 3.76, no starters' increase), MKB-winstvrijstelling (art. 3.79a), Zvw 5,26 %.
  Arbeidsinkomen (art. 8.1 e) is taken as the winst after ondernemersaftrek and MKB-winstvrijstelling (reading).
* **pension** (AOW and other pensions) is box-1 income that is not arbeidsinkomen; Zvw 5,26 % is withheld from it.
* **interest, dividends, capitalGains, rentalIncome** are *not* the Dutch tax base: box 3 taxes a deemed return on
  wealth at 1 January (art. 5.2). Wealth is given by the extension fields `nlBank`, `nlOtherAssets`, `nlDebts`
  (household totals, euros). `nlBox2` is income from a substantial interest (aanmerkelijk belang, box 2).
* **charitable** = andere giften (art. 6.39), a persoonsgebonden aftrek.
* **Joint items** of partners (art. 2.17 lid 2, 5: box-2 income, box-3 grondslag, persoonsgebonden aftrek) are
  allocated as the partners choose: the model chooses the allocation with the lowest combined tax and premie (a grid
  of 5 % steps), or half each (art. 2.17 lid 3) under `--split-half`.
* Ages are one number for the year: AOW age 67 (art. 7a AOW, 2025), born before 1946 = 80 or more, born before 1963
  (art. 8.9) = 63 or more. Children's ages are constant over the year (as in the OECD's Taxing Wages).
-/

namespace NLTax
open TaxKernel Lean

structure Opts where
  oecd : Bool := false
  bandSum : Bool := false
  splitHalf : Bool := false
  /-- Belastingjaar (round 3). -/
  year : Nat := 2025
  /-- `--june30` (EUROMOD convention, round 14): the AKW amounts in force on 30 June for the whole year ("Legislative
  parameters of the tax system are referred in EM to 30 June", EUROMOD technical note on nowcasting excise prices,
  JRC 2025, section 1.4), i.e. the Q1-Q2 amount in all four quarters; the statute pays Q3-Q4 at the 1 July amount. -/
  june30 : Bool := false
  deriving Repr

structure PIn where
  age : Nat
  wages : Int
  pensionContrib : Int
  pension : Int
  winst : Int
  uren : Bool
  deriving Repr

def PIn.loon (p : PIn) : Int := p.wages - p.pensionContrib
/-- Arbeidsinkomen before the ondernemersaftrek: computed in `eval`. -/

structure PRes where
  za : Int
  mkb : Int
  belWinst : Int
  box1 : Int
  box2 : Int
  box3 : Int
  pga : Int
  vi : Int
  ai : Int
  t1 : Int
  t2 : Int
  t3 : Int
  prem : Int
  zvw : Int
  ahk : Int
  ak : Int
  iack : Int
  ok : Int
  aok : Int
  split : Split
  taxDue : Int
  premDue : Int
  deriving Repr

/-- One person's assessment. `b2` box-2 income, `b3` box-3 voordeel, `pga` persoonsgebonden aftrek (cents), all
after allocation; `iackOk` = the conditions of art. 8.14a lid 1 b-c hold; `single` = no partner. -/
def eval (o : Opts) (p : PIn) (b2 b3 pga : Int) (iackOk single : Bool) : PRes :=
  let y := ypFor o.year
  let aowAged := decide (p.age ≥ aowAge)
  let pre1946 := decide (p.age ≥ 80)
  -- art. 3.76 lid 2, 4, 5
  let za := if p.winst > 0 && p.uren then min (if aowAged then zelfstandigenaftrek / 2 else zelfstandigenaftrek) p.winst
            else 0
  -- art. 3.79a: 12,7 % of the winst after ondernemersaftrek (only when positive, art. 2.10 lid 3 b)
  let mkb := mkbRate * p0 (p.winst - za) / 100000
  let bw := p.winst - za - mkb
  let box1 := p.loon + p.pension + bw - pga
  -- art. 2.18: verzamelinkomen (a box-1 loss is carried, not set off against boxes 2 and 3: not modelled)
  let vi := p0 box1 + b2 + b3
  let ai := p0 (p.loon + bw)
  let tbl := if pre1946 then y.t210a else y.t210
  let t1 := box1Tax tbl o.bandSum box1 + grondslagExtra box1 (za + mkb + pga) y
  let t2 := (if o.bandSum then box2BandTicks b2 y else box2Ticks b2 y) / 10000
  let t3 := y.box3Rate * b3 / 10000
  let prem := premie aowAged pre1946 box1 y
  let zvw := y.zvwRate * min (p0 (bw + p.pension)) y.zvwMax / 10000
  let ahk := ofPcm (ahkNum (if y.ahkOnVi then vi else p0 box1) y)
  let ak := if ai > 0 then ofPcm (akNum ai y) else 0
  let ik := if iackOk && ai > y.iackStart then ofPcm (iackNum ai y) else 0
  let ok := if aowAged then ofPcm (okNum vi y) else 0
  let aok := if aowAged && single then y.aokAmount else 0
  let s := split (ahk + ak + ik) (ok + aok) (!aowAged) y
  let (td, pd) := setOff (t1 + t2 + t3) prem s.ib s.prem
  { za, mkb, belWinst := bw, box1, box2 := b2, box3 := b3, pga, vi, ai, t1, t2, t3, prem, zvw, ahk, ak, iack := ik,
    ok, aok, split := s, taxDue := td, premDue := pd }

/-- What the korting actually took off the levy (art. 8.8 cap applied). -/
def PRes.creditUsed (r : PRes) : Int := (r.t1 + r.t2 + r.t3 + r.prem) - (r.taxDue + r.premDue)

/-- Art. 8.9: the partner whose korting art. 8.8 capped below the toetsniveau has it raised to that level, at most by
what the other partner pays after their own korting. Returns the payout (cents).
* 2023-2025 (lid 1 as in force on 1 January 2023, 2024 and 2025): only "de belastingplichtige die geboren is vóór
  1 januari 1963", toetsniveau = the algemene heffingskorting.
* 2022 (round 15; lid 1 and 2 as in force on 1 January 2022, law/hist/wib_2022-01-01.txt): every partner, toetsniveau
  "6 2/3% van het totaal van de voor de belastingplichtige geldende algemene heffingskorting, arbeidskorting en
  inkomensafhankelijke combinatiekorting", and for the one born before 1963 "de algemene heffingskorting voor 100% in
  aanmerking genomen".
Born before 1 January 1963 = reaching `year - 1962` or more in the year (63 in 2025; round 15: was 63 in every
year). -/
def toets89 (r : PRes) (age : Nat) (y : YP := y2025) : Int :=
  let born := age + 1962 ≥ y.year
  if y.year ≤ 2022 then (if born then r.ahk else r.ahk / 15) + (r.ak + r.iack) / 15
  else if born then r.ahk else 0

def payout89 (r other : PRes) (age : Nat) (y : YP := y2025) : Int :=
  let t := toets89 r age y
  if r.creditUsed < t then min (t - r.creditUsed) (other.taxDue + other.premDue) else 0

structure HRes where
  people : List PRes
  payouts : List Int
  /-- percent of the joint box-2 income / box-3 voordeel booked on adult 1; gifts on adult 1? -/
  share2 : Int
  share3 : Int
  giftsOn1 : Bool
  box3 : Box3
  giftDeduction : Int
  kb : Int
  kgb : Int
  partner : Bool
  deriving Repr

def HRes.levy (h : HRes) : Int :=
  h.people.foldl (fun a r => a + r.taxDue + r.premDue) 0 - h.payouts.foldl (· + ·) 0

def ext (c : Canon) (k : String) : Int := eur ((c.int? k).getD 0)

/-- Extension: an adult's `wagesExact` (euros with cents) replaces `wages` (so the OECD's unrounded wages can be fed
in); returns cents. -/
def wagesCents (c : Canon) (i : Nat) (a : Adult) : Int :=
  match c.raw.getObjVal? "adults" with
  | .ok (.arr xs) =>
    match xs[i]? with
    | some j => match j.getObjVal? "wagesExact" with
      | .ok (.num n) => (n.mantissa * 100 * 2 + (10 : Int) ^ n.exponent) / (2 * (10 : Int) ^ n.exponent)
      | _ => eur a.wages
    | none => eur a.wages
  | _ => eur a.wages

/-- The person inputs from the household. -/
def people (o : Opts) (c : Canon) : List PIn :=
  let ws := (List.range c.adults.length).zip c.adults |>.map fun (i, a) => wagesCents c i a
  let totalW := ws.foldl (· + ·) 0
  let pc := c.pensionContributions
  let uren := (c.bool? "nlUrencriterium").getD true
  (ws.zip c.adults).map fun (w, a) =>
    let contrib :=
      if o.oecd && pc = 0 then oecdPensionRate * p0 (w - oecdPensionFranchise) / 10000
      else if totalW > 0 then eur pc * w / totalW else 0
    { age := a.age, wages := w, pensionContrib := contrib, pension := eur a.pension,
      winst := eur a.selfEmployment, uren }

/-- Art. 6.39 lid 1, 4: deductible andere giften (cents) given the (joint) verzamelinkomen before the
persoonsgebonden aftrek. -/
def giftDeduction (gifts viBefore : Int) : Int :=
  let thr := max giftFloor (viBefore / 100)
  min (p0 (gifts - thr)) (p0 viBefore / 10)

def assess (o0 : Opts) (c : Canon) : HRes :=
  let o := { o0 with year := c.year }
  let y := ypFor c.year
  let ps := people o c
  let kids := c.children.map (·.age)
  let partner := ps.length == 2 && (c.married || !kids.isEmpty)
  let bank := ext c "nlBank"
  let other := ext c "nlOtherAssets"
  let debts := ext c "nlDebts"
  let box2Total := ext c "nlBox2"
  let gifts := eur c.charitable
  let kb := kinderbijslag kids (if o.june30 then { y with kbQ3 := y.kbQ1 } else y)
  let iackKids := kids.any (· < 12)
  match ps with
  | [p] =>
    let b3 := box3 bank other debts 1 y
    let r0 := eval o p box2Total b3.voordeel 0 iackKids true
    let gd := giftDeduction gifts r0.vi
    let r := eval o p box2Total b3.voordeel gd iackKids true
    let k := kgb kids false r.vi b3.rg y
    { people := [r], payouts := [0], share2 := 100, share3 := 100, giftsOn1 := true, box3 := b3,
      giftDeduction := gd, kb, kgb := k, partner := false }
  | [p, q] =>
    if !partner then
      let b3a := box3 (half1 bank) (half1 other) (half1 debts) 1 y
      let b3b := box3 (half2 bank) (half2 other) (half2 debts) 1 y
      let ra0 := eval o p (half1 box2Total) b3a.voordeel 0 false true
      let rb0 := eval o q (half2 box2Total) b3b.voordeel 0 false true
      let ga := giftDeduction (half1 gifts) ra0.vi
      let gb := giftDeduction (half2 gifts) rb0.vi
      let ra := eval o p (half1 box2Total) b3a.voordeel ga false true
      let rb := eval o q (half2 box2Total) b3b.voordeel gb false true
      { people := [ra, rb], payouts := [0, 0], share2 := 50, share3 := 50, giftsOn1 := true,
        box3 := b3a, giftDeduction := ga + gb, kb, kgb := 0, partner := false }
    else
      let b3 := box3 bank other debts 2 y
      -- art. 8.14a lid 1 c, lid 3: the partner with the lower arbeidsinkomen; equal: the older (then adult 1)
      let aiP := (eval o p 0 0 0 false false).ai
      let aiQ := (eval o q 0 0 0 false false).ai
      let iackP := iackKids && (aiP < aiQ || (aiP == aiQ && p.age ≥ q.age))
      let iackQ := iackKids && !iackP
      -- gift threshold on the joint verzamelinkomen before the persoonsgebonden aftrek (art. 6.39 lid 4)
      let viBefore := (eval o p box2Total 0 0 false false).vi + (eval o q 0 b3.voordeel 0 false false).vi
      let gd := giftDeduction gifts viBefore
      let try_ (s2 s3 : Int) (g1 : Bool) : HRes :=
        let b2p := box2Total * s2 / 100
        let (b3p, b3q) := box3Shares b3 s3
        let gp := if g1 then gd else 0
        let rp := eval o p b2p b3p gp iackP false
        let rq := eval o q (box2Total - b2p) b3q (gd - gp) iackQ false
        let pp := payout89 rp rq p.age y
        let pq := payout89 rq rp q.age y
        { people := [rp, rq], payouts := [pp, pq], share2 := s2, share3 := s3, giftsOn1 := g1, box3 := b3,
          giftDeduction := gd, kb, kgb := kgb kids true (rp.vi + rq.vi) b3.rg y, partner := true }
      if o.splitHalf then
        -- art. 2.17 lid 3: "voor de helft" when no choice is made
        let (h3p, h3q) := box3Shares b3 50
        let rp := eval o p (box2Total / 2) h3p (gd / 2) iackP false
        let rq := eval o q (box2Total - box2Total / 2) h3q (gd - gd / 2) iackQ false
        { people := [rp, rq], payouts := [payout89 rp rq p.age y, payout89 rq rp q.age y], share2 := 50, share3 := 50,
          giftsOn1 := false, box3 := b3, giftDeduction := gd, kb, kgb := kgb kids true (rp.vi + rq.vi) b3.rg y,
          partner := true }
      else
        let grid2 : List Int := if box2Total = 0 then [50] else (List.range 21).map (fun (i : Nat) => (5 * (i : Int)))
        let grid3 : List Int := if b3.voordeel = 0 then [50] else (List.range 21).map (fun (i : Nat) => (5 * (i : Int)))
        let gridG : List Bool := if gd = 0 then [true] else [true, false]
        let cands := grid2.flatMap fun s2 => grid3.flatMap fun s3 => gridG.map fun g => try_ s2 s3 g
        cands.foldl (fun best h => if h.levy < best.levy then h else best) (try_ 50 50 true)
  | _ => { people := [], payouts := [], share2 := 0, share3 := 0, giftsOn1 := true, box3 := box3 0 0 0 1,
           giftDeduction := 0, kb := 0, kgb := 0, partner := false }

/-! ## Output (contract, euros with cents) -/

def jc (x : Int) : Json := Json.num ⟨x, 2⟩

def personJson (r : PRes) (payout : Int) : Json :=
  Json.mkObj [("box1", jc r.box1), ("box2", jc r.box2), ("box3", jc r.box3), ("verzamelinkomen", jc r.vi),
    ("arbeidsinkomen", jc r.ai), ("zelfstandigenaftrek", jc r.za), ("mkbWinstvrijstelling", jc r.mkb),
    ("persoonsgebondenAftrek", jc r.pga),
    ("taxBox1BeforeCredits", jc r.t1), ("taxBox2", jc r.t2), ("taxBox3", jc r.t3), ("premieVolksverzekeringen", jc r.prem),
    ("algemeneHeffingskorting", jc r.ahk), ("arbeidskorting", jc r.ak), ("iack", jc r.iack),
    ("ouderenkorting", jc r.ok), ("alleenstaandeOuderenkorting", jc r.aok),
    ("kortingIB", jc r.split.ib), ("kortingPremie", jc r.split.prem),
    ("incomeTaxDue", jc r.taxDue), ("premieDue", jc r.premDue), ("zvwBijdrage", jc r.zvw),
    ("payout89", jc payout)]

/-- The art. 8.9 verhoging raises the gecombineerde heffingskorting, so it is split like any korting (art. 8.3:
IB part in the ratio of the first-bracket tax rate to the combined rate; art. 8.4-8.6 the premium parts; round 15:
before, the whole payout was booked against the income tax). The AOW part only for an AOW-insured person (the
person's own korting has an AOW part). Returns (IB part, premium part). -/
def payoutParts (r : PRes) (pay : Int) (y : YP := y2025) : Int × Int :=
  let s := split pay 0 (r.split.aow > 0 || r.split.total == 0) y
  (s.ib, pay - s.ib)

def outJson (o : Opts) (c : Canon) : Json :=
  let h := assess o c
  let y := ypFor c.year
  let rows := h.people.zip h.payouts
  let it := rows.foldl (fun a (r, pay) => a + r.taxDue - (payoutParts r pay y).1) 0
  let soc := rows.foldl (fun a (r, pay) => a + r.premDue + r.zvw - (payoutParts r pay y).2) 0
  let ben := h.kb + h.kgb
  let unsup : List String :=
    (if c.interest + c.dividends + c.capitalGains + c.rentalIncome ≠ 0 && (c.int? "nlBank").isNone
        && (c.int? "nlOtherAssets").isNone then
      ["box 3 taxes a deemed return on wealth at 1 January (Wet IB art. 5.2), not interest/dividends/gains/rent: "
        ++ "give nlBank, nlOtherAssets, nlDebts (euros) to tax it; the flows given are not taxed here"] else []) ++
    (if c.adults.length > 2 then ["more than 2 adults"] else []) ++
    ["toeslagen (zorgtoeslag, huurtoeslag, kinderopvangtoeslag) not modelled",
     "box-3 tegenbewijs (actual return lower than deemed) not modelled",
     "starters' zelfstandigenaftrek, jonggehandicaptenkorting, groene beleggingen, lijfrente jaarruimte not modelled"]
  Json.mkObj [("id", Json.str c.id), ("country", Json.str "NL"), ("currency", Json.str "EUR"),
    ("incomeTax", jc it), ("surtaxes", Json.mkObj []), ("localIncomeTax", jc 0),
    ("employeeSocial", jc soc), ("benefits", jc ben),
    ("detail", Json.mkObj [
      ("partners", Json.bool h.partner),
      ("persons", Json.arr (rows.map fun (r, pay) => personJson r pay).toArray),
      ("CGTC", jc (h.people.foldl (fun a r => a + r.box1) 0)),
      ("CGITLETC", jc (h.people.foldl (fun a r => a + r.t1) 0)),
      ("TC", jc (h.people.foldl (fun a r => a + min r.split.ib (r.t1 + r.t2 + r.t3)) 0)),
      ("premieVolksverzekeringenDue", jc (h.people.foldl (fun a r => a + r.premDue) 0)),
      ("zvwBijdrage", jc (h.people.foldl (fun a r => a + r.zvw) 0)),
      ("kinderbijslag", jc h.kb), ("kindgebondenBudget", jc h.kgb),
      ("box3", Json.mkObj [("rendementsgrondslag", jc h.box3.rg), ("grondslag", jc h.box3.grondslag),
         ("voordeel", jc h.box3.voordeel)]),
      ("giftenaftrek", jc h.giftDeduction),
      ("shareBox2Adult1Pct", Json.num ⟨h.share2, 0⟩), ("shareBox3Adult1Pct", Json.num ⟨h.share3, 0⟩),
      ("giftsOnAdult1", Json.bool h.giftsOn1),
      ("employeePensionContributions", jc ((people o c).foldl (fun a p => a + p.pensionContrib) 0)),
      ("loonheffingAnnual", Json.arr ((people o c).map fun p =>
          if decide (p.age ≥ aowAge) || p.pension != (0 : Int) || p.winst != (0 : Int) then Json.null
          else match lbAnnualMonthly (p.loon / 100) with | some v => jc v | none => Json.null).toArray),
      ("mode", Json.str (if o.oecd then "oecd" else if o.bandSum then "band-sum" else "statute"))]),
    ("unsupported", Json.arr (unsup.map Json.str).toArray)]

end NLTax
