import LegalProofs.CaseLaw2.Exec.Env
import LegalProofs.CaseLaw2.Spec.Findings
import LegalProofs.CaseLaw2.Spec.Splits
import LegalProofs.CaseLaw2.Spec.Lines

/-!
# Exec: verdicts for one citation, one decision, one issue

Glue shared by `Examples.lean` and the runner: the question a citing decision asks (`queryFor`), the force of a cited
holding on it (`forceOn`), the most severe live effect (the status's witness, for the justification path), whether
the negating decision binds the citing court, and the `CiteFacts` the findings read. Everything here is a function of
the Spec's `force`, `canChangeStatus` and `status`, read through any `Lookups`/`EventLookups` (the runner passes the
hash-indexed ones, which `Exec/Env.lean` proves equal to the Spec's).
-/

namespace CaseLaw2.Exec
open CaseLaw2 CaseLaw2.Spec

/-- The question a decision asks: its court at its date, its unit, its *Golsen* circuit and TRAP 41.3 transferor. -/
def queryFor (L : Lookups) (c : Decision) : Option Query :=
  (L.epochAt c.court c.date).map fun D =>
    { dst := D, dstUnit := c.unit <|> D.unit, dstCircuit := c.appealVenue.getD D.circuit,
      dstTransferFrom := c.transferFrom, t := c.date }

/-- Force of holding `h` of `x` on the court of citing decision `c`, on `c`'s date. -/
def forceOn (L : Lookups) (E : EventLookups) (x : Decision) (h : Holding) (c : Decision) :
    Option (Force × List RuleId) :=
  -- S-TX-3: a writ/petition-refused notation promotes only a state intermediate court's opinion (D4 triage: on any
  -- other court it is a data error and must not demote, e.g., a circuit's binding force on its district courts)
  let promoted := promotedAt E x.id c.date &&
    (L.epochAt x.court x.date).any (fun S => S.system != 0 && S.tier == .appellate)
  -- the court as it ordinarily sits (hunt H6): `forceDiv` is `force` except for a division of a court of last
  -- resort asking about that court's own decisions (`forceDiv_eq_force`)
  (queryFor L c).bind fun q => forceDiv L x h promoted q

/-- The last epoch of court `c` that ended before `t` (round 3, DEVIATIONS 80): how a ceased court last sat. -/
def lastEpoch (eps : List CourtEpoch) (c : Nat) (t : Date) : Option CourtEpoch :=
  (eps.filter fun e => e.court == c && e.dateTo < t).foldl
    (fun m e => match m with | some m' => if m'.dateTo < e.dateTo then some e else some m' | none => some e) none

/-- `forceOn` on a court with no epoch on `t`, asked as it last sat (`D`, from `lastEpoch`), with unit `u`
(DEVIATIONS 80). Used only to decide displacement among conflict candidates. -/
def forceOnAs (L : Lookups) (E : EventLookups) (x : Decision) (h : Holding) (D : CourtEpoch) (u : Option Nat)
    (t : Date) : Option (Force × List RuleId) :=
  let promoted := promotedAt E x.id t &&
    (L.epochAt x.court x.date).any (fun S => S.system != 0 && S.tier == .appellate)
  forceDiv L x h promoted { dst := D, dstUnit := u <|> D.unit, dstCircuit := D.circuit, t := t }

def isNeg : Status → Bool
  | .neg _ => true
  | _ => false

/-- The most severe live effect on issue `k` (first in list order among the most severe): the status's witness. -/
def witness (effs : List Effect) (k : Nat) (t u : Date) : Option Effect :=
  let s := status effs k t u
  effs.find? (fun e => e.contrib k t u == s && s != .good)

/-- Some live negative effect on `k` comes from a decision that binds the citing court (or from a statute, or from
the same case's history). -/
def negByBinding (L : Lookups) (E : EventLookups) (dec : Nat → Option Decision) (effs : List Effect) (k : Nat)
    (c : Decision) : Bool :=
  (effs.filter (fun e => isNeg (e.contrib k c.date c.date))).any fun e =>
    match e.rule, e.actor with
    | .history, _ => true
    | _, none => true
    | _, some a =>
      match dec a with
      | some ad => (forceOn L E ad (Holding.anon ad) c).map (·.1) == some .binding
      | none => false

/-- The court had a strong or within-unit horizontal rule on the date (H3b); for a court of last resort, the
court-level row (H6). -/
def strongRuleAt (L : Lookups) (b : Decision) : Bool :=
  (L.epochAt b.court b.date).any fun B =>
    let r := if B.tier == .last then L.rules.horizontalCourt B.court b.date
             else L.rules.horizontal B.court B.system b.date
    (r == some .strong || r == some .withinUnitOnly) &&
      -- a federal court of appeals had no en banc procedure before the 1948 Judicial Code
      !(B.system == 0 && B.tier == .appellate && b.date < enBancStatuteDate)

/-- Everything the findings read about citation `c → x` on issue `h`, for conduct date `u` (`none` = unknown, H2),
read through the citing court's line of authority (`effectsFor`, H4). `holdingMatch`: the citing decision decides
the cited holding's question (H2). -/
def citeFacts (L : Lookups) (E : EventLookups) (dec : Nat → Option Decision) (effs : List Effect) (x : Decision)
    (h : Holding) (c : Decision) (u : Option Date) (followed : Bool) (holdingMatch : Bool := true) : CiteFacts :=
  let effs := effectsFor L c effs
  { status := status effs h.issue c.date c.date
    statusAtConduct := u.map (status effs h.issue c.date)
    holdingMatch
    negByBinding := negByBinding L E dec effs h.issue c
    pub := x.pub
    force := forceOn L E x h c
    followed
    pluralityNoMarks := (h.role == some .plurality || x.form == some .plurality) && !h.marks }

def Status.toString : Status → String
  | .good => "good"
  | .unknown r => "unknown:" ++ (reprStr r).replace "CaseLaw2.Spec.Unk." ""
  | .neg n => "neg:" ++ (reprStr n).replace "CaseLaw2.Spec.Neg." ""

/-- The three classes of DESIGN D5. -/
def Status.cls : Status → String
  | .good => "noneAdmitted"
  | .unknown _ => "unknown"
  | .neg _ => "negativeAdmitted"

/-- A candidate for the resolver: holding `h` of `x`, good law on `c`'s date, with its force on `c`'s court. -/
def candFor (L : Lookups) (E : EventLookups) (x : Decision) (h : Holding) (c : Decision) : Option Cand := do
  let a ← h.answer
  let (f, path) ← forceOn L E x h c
  let S ← L.epochAt x.court x.date
  let tierPrec (T : CourtEpoch) : Nat := if T.scotus then scotusPrec else if T.tier == .last then 3
    else if T.tier == .appellate then 2 else 1
  -- a decision held by adoption ranks as the adopter's (an adopted Texas Commission opinion as the Supreme Court's,
  -- H4; the old Fifth Circuit's as the Eleventh's), and at least as an appellate court's
  let adoptPrec := (adoptionsOf L x).foldl (fun m a =>
    max m ((L.epochAt a.adopter c.date).map tierPrec |>.getD 2)) 2
  -- round 4 (DEVIATIONS 82): a decision promoted by a Texas "writ refused" notation ranks as the court of last
  -- resort's, as `forceOn` already treats it (S-TX-3)
  let S' := if path.contains .TXpromoted then { S with tier := .last } else S
  let prec := if path.contains .adopted then max (tierPrec S') adoptPrec else tierPrec S'
  some { holding := h.id, answer := a, force := f, prec, date := x.date,
         ownUnit := x.unit.isSome && x.unit == (c.unit <|> (L.epochAt c.court c.date).bind (·.unit)) }

/-- Power for a same-case history row (§5.1A): the deciding court is the court itself (withdrawal, substitution,
rehearing, at any bench), its successor, a higher court of its system that reviews it, or SCOTUS. In the federal
system the reviewing court of appeals is the target's own circuit, or the Federal Circuit (appeals from every
district court and the Court of Federal Claims) (D4 triage, DIFFTEST.md). `none` = an epoch unknown. -/
def histPower (L : Lookups) (b x : Decision) : Option Bool :=
  match L.epochAt b.court b.date, L.epochAt x.court x.date with
  | some B, some X =>
    some (B.court == X.court || L.sameOrSuccessor X.court B.court || B.scotus ||
      (B.system == X.system && X.tier.rank < B.tier.rank &&
        (B.system != 0 || (B.circuit == 13 && B.tier == .appellate) || (B.circuit == X.circuit && B.circuit != 0))))
  | _, _ => none

end CaseLaw2.Exec
