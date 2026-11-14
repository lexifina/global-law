# Round 7, Lean: joined certificates, doctrine rows, history claims

Contract: `DESIGN7.md` §1–3. Written by the `lean` agent, 13 Nov 2026 (started 22:43). Section 1 was written
**before** any proof (the statements are the target; a statement that proves false is refuted and reported, never
weakened silently). Sections 2–4 were written after the build. `round7/LEAN_READY` was created at the end (14 Nov, 00:00) when all of section 3 was green.

Backup of everything changed: `round7/pre/` (`CaseLaw2/`, `CaseLaw2.lean`, `tools_caselaw2/` (cue table, generator,
both generated `cue_table.py`), `audit/statements.lock`, `STATEMENTS.log`, `run_lean.sh`, `run_lean_wsl.sh`, `wsl/`,
`runner/` sources; `SHA1SUMS.txt`).

## 0. Deviations from DESIGN7, and readings of points it leaves open

The lead rules on each; the reference agent should read the same way (or say so).

| # | point | what the Lean does |
|---|---|---|
| L7-1 | joined lines on a **witness row** (`treatment_witness.tsv`): §2.1 names the modes plain / operative / doctrine only | ignored and counted (`joined_witness_ignored`); the witness row is checked exactly as in round 6 |
| L7-2 | a **doctrine claim on a witness row** | checked as a doctrine row: `doctrineBadRow` (explicit = 0, §2.4 as written; round 5 *ignored* an operativeWords claim on a witness row, round 7 does not do the same for doctrine) |
| L7-3 | which D the tie and the uniqueness use | D is the joined line's `label` column. The class line's `doctrine` column stays display text (`classes.tsv`), as in round 5. The uniqueness key of a row is the set of compact labels (`compact`: letters and digits, lower case) of its `doctrineTie` lines |
| L7-4 | uniqueness "if two rows that pass": under which rule set | decided once, on the **text check** (the doctrine check with the acting court's power taken as verified, the round-5 `textOk`): the collision set is the doctrine rows whose text check passes; a row with a label that two of them tie to different targets fails `doctrineAmbiguous` under both rule sets and has no effect. (Per rule set it could happen that a row is `ok` yet has no event; this way "admitted ⇒ text passes" stays true.) |
| L7-5 | "the kind's disqualifier list (as for the main quote)" for a joined quote | the plain list of the row's kind (`disqualifiers kind`: `disqualify_treat` for a status-changing kind), not the operative / doctrine additions of the main quote's mode; plus `disqualify_joined` |
| L7-6 | `checkJoined` given 0 or more than 2 lines | fails `joinedMismatch` (the runner never passes such a list; it keeps the first two lines) |
| L7-7 | several `history_claim.tsv` lines for one id | a row's claims are the set of claim words of its lines (it may carry `orderHead` and `setAside`); a repeated `(id, claim)` line is ignored and counted (`hclaim_duplicates`) |
| L7-8 | `orderHead` facts | court: the acting decision's court epoch is the Supreme Court's (`CourtEpoch.scotus`: system 0, tier last; in the court table that is court 2906 only), under the rule set's tables; date: the acting decision's date in `decisions2.tsv` (0 = unknown fails), never the row's date column (as DESIGN5 §9 ruled for date(Y)); length: `quote.length` (characters) ≤ 400 |
| L7-9 | constant 400 | also in the cue table JSON (`order_head_max_len` = 400), next to `joined_gap_max` and `order_head_from` (data in one place; same value) |
| L7-10 | class of a doctrine row | `doctrine` for every treatments row with a doctrine claim, kind `disapproved` and `explicit = 1`, whatever its verdict (`classes.tsv` shows the verdict beside it); any other row is classed as in round 5 |
| L7-11 | a `setAside` claim on a kind other than `vacated` | no effect at all (the cue list is the kind's); not a bad row |
| L7-12 | a `history` joined line whose id is no history row | counted `joined_unknown_ids` (the unknown-id test comes first for both tables); a `history` line with a known id: `joined_history_ignored` |
| L7-13 | `antecedent` on an `operativeWords` row | §2.2 as written: the main quote needs a cue of the kind's **plain** list (`disapprov` for `disapproved`), so an operative act without it fails `joinedRelation`. **Ruled D7-10 (lead): keep as written** (the reference reads it the same way, its Q7-15) |

Lead rulings received during the work (data and one definition; no statement changed):

- **D7-8 (anaphor list).** `anaphor` extended with every phrase of `round7/agents/antecedent/anaphor_proposal.json`
  (39 → 70 phrases; the 31 not already present are appended in the proposal's order). Data only.
- **D7-9 (order-line form).** An `order_line` entry with the separator `" ... "` means "a, followed later by b"
  (`hasInOrder`, as the (a, b) disqualifier pairs); an entry without it keeps plain substring meaning. Six entries
  added: certDenied "petition for writ of certiorari to the ... denied", "petition for a writ of certiorari to the ...
  denied", "petitions for writs of certiorari to the ... denied"; reviewDismissed the same three with "... dismissed".
  Lean: `orderLineCue` reads each entry through the new `orderLineHit` (below). `orderHead_sound` names
  `orderLineCue`, so its statement is unchanged (nothing was locked at the time either).
- **D7-10.** L7-13 kept as written.
- **D7-12 (doctrine lists).** `doctrine_reject` += "depart from", "departing from", "unsound", "overrule",
  "abolish", "expressly reject", "therefore reject", "accordingly reject", "hereby reject", "be rejected", "no proper
  place", "recede from", "decline to follow", "renounce", "jettison", "cannot survive", "not the law" (18 → 35);
  `doctrine_tie` += "test of", "adopted by", "established by", "first adopted", "principle of", "presumption of"
  (25 → 31). Data only (appended). Build, audit, fixture and regressions were re-run after it (section 3).

## 1. Definitions and theorems (stated first)

All checker definitions in `LegalProofs/CaseLaw2/Certificate.lean` (namespace `CaseLaw2.Cert`, after the round-6
section); the effect definitions in `Spec/Recognised.lean` (namespace `CaseLaw2.Spec`; `Spec/Status.lean` is not
changed); the cue lists in the generated `CueTable.lean`.

### 1.1 Cue table (generated from `tools/caselaw2/cues/cue_table.json`)

New keys (every earlier key and list byte-identical; the generator appends):

| JSON key | Lean | Python |
|---|---|---|
| `anaphor` | `anaphorCues : List String` | `ANAPHOR` |
| `doctrine_tie` | `doctrineTieCues` | `DOCTRINE_TIE` |
| `doctrine_reject` | `doctrineRejectCues` | `DOCTRINE_REJECT` |
| `disqualify_joined` | `joinedDisqualifiers` | `DISQUALIFY_JOINED` |
| `order_line` (kind → list) | `orderLineCues : HKind → List String` (`[]` for a kind not in the map) | `ORDER_LINE` (dict) |
| `set_aside` | `setAsideCues` | `SET_ASIDE` |
| `joined_gap_max` (300) | `joinedGapMax : Nat` | `JOINED_GAP_MAX` |
| `order_head_from` (20130101) | `orderHeadFrom : Nat` | `ORDER_HEAD_FROM` |
| `order_head_max_len` (400) | `orderHeadMaxLen : Nat` | `ORDER_HEAD_MAX_LEN` |

### 1.2 Definitions

```lean
-- eight reason codes appended to `Reason` (as rounds 5 and 6 appended theirs)
  | joinedMismatch | joinedPart | joinedDisqualified | joinedRelation | joinedUnresolved
  | doctrineBadRow | doctrineAmbiguous | orderHeadNotAllowed
-- one text mode appended to `Mode`; `cueList` / `disqList` gain one arm each
  | doctrine
  cueList  .doctrine = doctrineRejectCues
  disqList .doctrine = disqualifiers c.kind ++ operativeDisqualifiers.map (·, "")   -- disqualify_treat + disqualify_operative
-- (`resolves` is unchanged: in a mode other than plain the name must be in the quote itself)
-- one class appended to `OClass`; tie order selfAnnounced 0 < operativeWords 1 < recognised 2 < doctrine 3 <
-- atRiskWitness 4 (`idx` of atRiskWitness moves from 3 to 4; only the order is used); toString "doctrine"

inductive JRel where | antecedent | doctrineTie
structure Joined where
  rel : JRel
  start : Nat
  stop : Nat
  quote : String
  part : String
  label : String

/-- The joined quote read over the row's own text (hash, windows, index, evidence of `c`; span, quote, part of `j`). -/
def Joined.input (j : Joined) (c : Input) : Input := { c with start := j.start, stop := j.stop, quote := j.quote, part := j.part }
def Joined.toAnchor (j : Joined) : Anchor := { start := j.start, stop := j.stop, quote := j.quote, part := j.part }

/-- The mode the row's main quote is checked in. -/
inductive TClaim where | plain | operative | doctrine
def TClaim.apply : TClaim → Input → Input
  | .plain, c => c | .operative, c => { c with mode := .operative } | .doctrine, c => { c with mode := .doctrine }

def joinedCountOk (js : List Joined) : Bool := 1 ≤ js.length && js.length ≤ 2                         -- check 1
def joinedQuoteOk (c : Input) (j : Joined) : Bool := quoteOk (j.input c)                               -- check 1
def joinedPartOk (j : Joined) : Bool := j.part == "majority" || j.part == "plurality" || j.part == "perCuriam" -- 2
def joinedDisqualified (c : Input) (j : Joined) : Bool :=                                              -- check 3
  let q := (norm j.quote).toLower
  (disqualifiers c.kind).any (fun (a, b) => if b.isEmpty then hasSub q a else hasInOrder q a b) ||
    joinedDisqualifiers.any (hasSub q)
def kindCue (c : Input) : Bool := (cues c.kind).any (hasSub (norm c.quote).toLower)       -- the plain list
def anaphorCue (q : String) : Bool := anaphorCues.any (hasSub (norm q).toLower)
def antecedentOk (c : Input) (j : Joined) : Bool :=
  j.stop ≤ c.start && c.start - j.stop ≤ joinedGapMax && anaphorCue c.quote && kindCue c
def labelNorm (s : String) : String := (norm s).toLower
def labelOk (s : String) : Bool :=
  decide (2 ≤ (((labelNorm s).splitOn " ").filter (· ≠ "")).length) && decide (8 ≤ (labelNorm s).length)
def labelIn (q label : String) : Bool := hasSub (norm q).toLower (labelNorm label)
def tieCue (q : String) : Bool := doctrineTieCues.any (hasSub (norm q).toLower)
def tieOk (cl : TClaim) (c : Input) (j : Joined) : Bool :=
  cl == .doctrine && labelOk j.label && labelIn c.quote j.label && labelIn j.quote j.label && tieCue j.quote
def relationOk (cl : TClaim) (c : Input) (j : Joined) : Bool :=                                         -- check 4
  match j.rel with
  | .antecedent => antecedentOk c j
  | .doctrineTie => tieOk cl c j
def joinedResolves (c : Input) (j : Joined) : Bool := anchorResolves c j.toAnchor                       -- check 5

/-- The row's own check on its main quote, in its mode (check 6 is this on `{ c with selfText := true }`). -/
def mainCheck (c : Input) (explicit : Bool) : TClaim → Result
  | .plain => check c
  | .operative => checkOperative c explicit
  | .doctrine => check { c with mode := .doctrine }

/-- **The joined checker** (first failure = reason). -/
def checkJoined (c : Input) (explicit : Bool) (cl : TClaim) (js : List Joined) : Result :=
  if !(joinedCountOk js && js.all (joinedQuoteOk c)) then .fail .joinedMismatch
  else if !js.all joinedPartOk then .fail .joinedPart
  else if js.any (joinedDisqualified c) then .fail .joinedDisqualified
  else if !js.all (relationOk cl c) then .fail .joinedRelation
  else if !js.any (joinedResolves c) then .fail .joinedUnresolved
  else mainCheck { c with selfText := true } explicit cl

def doctrineRowOk (c : Input) (explicit : Bool) (js : List Joined) : Bool :=
  c.kind == .treat .disapproved && explicit && js.any (·.rel == .doctrineTie)
/-- **The doctrine checker** (DESIGN7 §2.4): `doctrineBadRow`, then the joined check in doctrine mode. -/
def checkDoctrine (c : Input) (explicit : Bool) (js : List Joined) : Result :=
  if !doctrineRowOk c explicit js then .fail .doctrineBadRow else checkJoined c explicit .doctrine js

/-- **The runner's treatment step** for a row that is not a witness row (mutants replace `cj`). -/
def checkTreatmentWith (cj : Input → Bool → TClaim → List Joined → Result)
    (c : Input) (explicit : Bool) (cl : TClaim) (js : List Joined) : Result :=
  match cl, js with
  | .doctrine, js => if !doctrineRowOk c explicit js then .fail .doctrineBadRow else cj c explicit .doctrine js
  | .plain, [] => check c
  | .operative, [] => checkOperative c explicit
  | cl, js => cj c explicit cl js
def checkTreatment : Input → Bool → TClaim → List Joined → Result := checkTreatmentWith checkJoined

/-- Doctrine uniqueness inside the table (DESIGN7 §2.4). One record per doctrine row. -/
structure DoctrineRow where
  target : Nat
  /-- the compact labels of its `doctrineTie` lines -/
  labels : List String
  /-- its check passed with the acting court's power taken as verified (the text check) -/
  text : Bool
def tieLabels (js : List Joined) : List String := (js.filter (·.rel == .doctrineTie)).map (fun j => compact j.label)
def labelTargets (rows : List DoctrineRow) (l : String) : List Nat :=
  (rows.filter (fun r => r.text && r.labels.contains l)).map (·.target)
def ambiguousLabel (rows : List DoctrineRow) (l : String) : Bool :=
  match labelTargets rows l with
  | [] => false
  | t :: ts => ts.any (· != t)
def doctrineAmbiguous (rows : List DoctrineRow) (r : DoctrineRow) : Bool := r.labels.any (ambiguousLabel rows)
/-- The final verdict of a doctrine row under a rule set, from its verdict `v` there. -/
def doctrineFinal (rows : List DoctrineRow) (r : DoctrineRow) (v : Result) : Result :=
  if v.admitted && doctrineAmbiguous rows r then .fail .doctrineAmbiguous else v

/-- The class of a row in round 7: `doctrine` for a doctrine row (`doctrine` = claim doctrine and kind
disapproved), else round 5's `classOf`. -/
def classOf7 (explicit recognised doctrine : Bool) (quote : String) : OClass :=
  if doctrine && explicit && !recognised then .doctrine else classOf explicit recognised quote

-- history claims (DESIGN7 §3)
structure HClaims where
  orderHead : Bool := false
  setAside : Bool := false
  /-- the acting decision's court is the Supreme Court of the United States -/
  scotus : Bool := false
  /-- the acting decision's date (`decisions2.tsv`; 0 unknown) -/
  date : Nat := 0
def orderHeadKinds : List HKind := [.certDenied, .vacated, .reversed, .affirmed, .reviewDismissed]
def orderHeadKind : Kind → Bool | .hist k => orderHeadKinds.contains k | .treat _ => false
def orderLine : Kind → List String | .hist k => orderLineCues k | .treat _ => []
/-- (D7-9) an entry `a ... b`: a, then b later (`hasInOrder`); any other entry: a substring. -/
def orderLineHit (q p : String) : Bool :=
  match p.splitOn " ... " with
  | [a, b] => hasInOrder q a b
  | _ => hasSub q p
def orderLineCue (c : Input) : Bool := (orderLine c.kind).any (orderLineHit (norm c.quote).toLower)
def orderHeadOk (h : HClaims) (c : Input) : Bool :=
  h.scotus && orderHeadFrom ≤ h.date && orderHeadKind c.kind && orderLineCue c && c.quote.length ≤ orderHeadMaxLen
def setAsideCue (c : Input) : Bool := setAsideCues.any (hasSub (norm c.quote).toLower)
def claimCueOk (h : HClaims) (c : Input) : Bool := hasCue c || (h.setAside && c.kind == .hist .vacated && setAsideCue c)
def claimPart (ohOk : HClaims → Input → Bool) (h : HClaims) (c : Input) : Option Reason :=
  if partOk c then none
  else if c.part == "headmatter" && h.orderHead then (if ohOk h c then none else some .orderHeadNotAllowed)
  else some .partNotMajority

/-- `check` with the cue test and the part test as parameters (the other seven tests are `check`'s). -/
def checkBy (cueOk : Input → Bool) (partRes : Input → Option Reason) (c : Input) : Result :=
  if !shaOk c then .fail .shaUnknown
  else if !(c.windows.any (wellFormed c)) then .fail .noWindow
  else if !(c.windows.any (usable c)) then .fail .windowHash
  else if !quoteOk c then .fail .quoteMismatch
  else if !cueOk c then .fail .noCue
  else if disqualified c then .fail .disqualified
  else if !resolves c then .fail .targetUnresolved
  else match partRes c with
    | some r => .fail r
    | none => if !c.ordered then .fail .targetLater
      else match c.authority with
        | some true => .ok | some false => .fail .noAuthority | none => .okUnverifiedBy
/-- `checkAnchored` with its last step (check 6) as a parameter. -/
def anchoredThen (fin : Input → Result) (c : Input) (a : Anchor) : Result :=
  if !anchorQuoteOk c a then .fail .anchorMismatch
  else if !anchorHasCue a then .fail .anchorNoCue
  else if anchorDisqualified a then .fail .anchorDisqualified
  else if !anchorResolves c a then .fail .anchorUnresolved
  else if !anchorPartOk a then .fail .anchorPart
  else fin { c with selfText := true }
def checkClaimedWith (ohOk cueOk : HClaims → Input → Bool) (h : HClaims) (c : Input) : Result :=
  checkBy (cueOk h) (claimPart ohOk h) c
def checkHistory7With (ohOk cueOk : HClaims → Input → Bool) (c : Input) (a? : Option Anchor) (h : HClaims) : Result :=
  match a? with
  | some a => anchoredThen (checkClaimedWith ohOk cueOk h) c a
  | none => checkClaimedWith ohOk cueOk h c
/-- **The runner's history step in round 7.** -/
def checkHistory7 : Input → Option Anchor → HClaims → Result := checkHistory7With orderHeadOk claimCueOk
```

`Spec/Recognised.lean`:

```lean
/-- The event of an admitted doctrine row: its scope demoted (DESIGN5 §3.3, DESIGN7 §2.4). -/
def doctrineEvent (tr : TEvent) : TEvent := { tr with scope := demote tr.scope }
def doctrineEffects (byHist : List HEvent) (tr : TEvent) : List Effect := treatEffects byHist (doctrineEvent tr)
```

The runner applies `Spec.doctrineEvent` to every event a doctrine row yields (after the round-4 issue/power
splitting, exactly where round 5 demotes an operative row), so `effectsOf` gives that event `doctrineEffects`
(the reach mapping changes no scope).

### 1.3 Theorems (22)

```lean
/-- Admission is exactly the six checks (with the count bound in check 1). -/
theorem checkJoined_admitted_iff (c : Input) (e : Bool) (cl : TClaim) (js : List Joined) :
    (checkJoined c e cl js).admitted = true ↔
      (joinedCountOk js = true ∧ (∀ j ∈ js, joinedQuoteOk c j = true) ∧ (∀ j ∈ js, joinedPartOk j = true) ∧
        (∀ j ∈ js, joinedDisqualified c j = false) ∧ (∀ j ∈ js, relationOk cl c j = true) ∧
        (∃ j ∈ js, joinedResolves c j = true) ∧ (mainCheck { c with selfText := true } e cl).admitted = true)

/-- **Joined soundness.** -/
theorem checkJoined_sound (c : Input) (e : Bool) (cl : TClaim) (js : List Joined)
    (h : (checkJoined c e cl js).admitted = true) :
    (∀ j ∈ js, ∃ w, coveringWindow (j.input c) = some w ∧ w ∈ c.windows ∧ usable (j.input c) w = true ∧
        quoteAt (j.input c) w = true) ∧
      (∀ j ∈ js, joinedPartOk j = true) ∧ (∀ j ∈ js, joinedDisqualified c j = false) ∧
      (∀ j ∈ js, relationOk cl c j = true) ∧ (∃ j ∈ js, joinedResolves c j = true) ∧
      (mainCheck { c with selfText := true } e cl).admitted = true ∧
      checkJoined c e cl js = mainCheck { c with selfText := true } e cl

/-- One or two joined lines. -/
theorem checkJoined_bounded (c : Input) (e : Bool) (cl : TClaim) (js : List Joined)
    (h : (checkJoined c e cl js).admitted = true) : 1 ≤ js.length ∧ js.length ≤ 2

/-- With a citation index and `cite:` evidence, the index maps the citation to the row's target. -/
theorem checkJoined_cite_index (c : Input) (e : Bool) (cl : TClaim) (js : List Joined)
    (h : (checkJoined c e cl js).admitted = true) (hc : c.evidence.startsWith "cite:" = true)
    (m : Std.HashMap String Nat) (hm : c.citeIndex = some m) :
    m.get? (compact (c.evidence.drop 5).toString) = some c.target

/-- Every joined quote's window: well formed, its SHA-1 the recorded one, recorded when the hash file is supplied. -/
theorem checkJoined_window_hash (c : Input) (e : Bool) (cl : TClaim) (js : List Joined)
    (h : (checkJoined c e cl js).admitted = true) :
    ∀ j ∈ js, ∃ w, coveringWindow (j.input c) = some w ∧ quoteAt (j.input c) w = true ∧
      wellFormed (j.input c) w = true ∧ (∀ s, w.hash = some s → Sha1.hex w.text = s) ∧
      (c.hashRequired = true → w.hash.isSome = true)

/-- Every joined quote is non-empty, at a non-empty span. -/
theorem checkJoined_quote_nonempty (c : Input) (e : Bool) (cl : TClaim) (js : List Joined)
    (h : (checkJoined c e cl js).admitted = true) : ∀ j ∈ js, j.quote ≠ "" ∧ j.start < j.stop

/-- The main quote of an admitted joined row: every conjunct of `checkCert_sound` except `resolves`, read in the
row's mode. -/
theorem checkJoined_disposition (c : Input) (e : Bool) (cl : TClaim) (js : List Joined)
    (h : (checkJoined c e cl js).admitted = true) :
    shaOk c = true ∧ (∃ w, coveringWindow c = some w ∧ quoteAt c w = true) ∧ hasCue (cl.apply c) = true ∧
      disqualified (cl.apply c) = false ∧ partOk c = true ∧ c.ordered = true

/-- **Antecedent**: the joined quote ends before the main quote, at most `joinedGapMax` (300) characters before it;
the main quote has an anaphor and a cue of the row's kind. -/
theorem antecedent_gap (c : Input) (e : Bool) (cl : TClaim) (js : List Joined)
    (h : (checkJoined c e cl js).admitted = true) (j : Joined) (hj : j ∈ js) (hr : j.rel = .antecedent) :
    j.stop ≤ c.start ∧ c.start - j.stop ≤ joinedGapMax ∧ anaphorCue c.quote = true ∧ kindCue c = true

/-- **Doctrine tie**: only on a doctrine row; the label is a phrase of two words or more and eight characters or
more, in both quotes; the joined quote has a tie cue. -/
theorem doctrineTie_label (c : Input) (e : Bool) (cl : TClaim) (js : List Joined)
    (h : (checkJoined c e cl js).admitted = true) (j : Joined) (hj : j ∈ js) (hr : j.rel = .doctrineTie) :
    cl = .doctrine ∧ labelOk j.label = true ∧ labelIn c.quote j.label = true ∧ labelIn j.quote j.label = true ∧
      tieCue j.quote = true

/-- **Doctrine rows**: explicit, `disapproved`, a tie line, the joined check in doctrine mode (a doctrine-reject cue,
no treatment or operative disqualifier in the main quote). -/
theorem checkDoctrine_sound (c : Input) (e : Bool) (js : List Joined) (h : (checkDoctrine c e js).admitted = true) :
    c.kind = .treat .disapproved ∧ e = true ∧ (∃ j ∈ js, j.rel = .doctrineTie) ∧
      (checkJoined c e .doctrine js).admitted = true ∧ hasCue { c with mode := .doctrine } = true ∧
      disqualified { c with mode := .doctrine } = false

/-- The step with joined lines is the joined check (for a doctrine row, the joined check in doctrine mode). -/
theorem checkTreatment_joined (c : Input) (e : Bool) (cl : TClaim) (js : List Joined) (hj : js ≠ [])
    (h : (checkTreatment c e cl js).admitted = true) : (checkJoined c e cl js).admitted = true

/-- Admitted under a rule set ⇒ admitted with power taken as verified (the text check). -/
theorem checkTreatment_text (c : Input) (e : Bool) (cl : TClaim) (js : List Joined)
    (h : (checkTreatment c e cl js).admitted = true) :
    (checkTreatment { c with authority := some true } e cl js).admitted = true

/-- **Doctrine uniqueness**: two admitted doctrine rows that share a compact label have the same target. -/
theorem doctrine_unique (rows : List DoctrineRow) (r1 r2 : DoctrineRow) (h1 : r1 ∈ rows) (h2 : r2 ∈ rows)
    (v1 v2 : Result) (a1 : (doctrineFinal rows r1 v1).admitted = true) (a2 : (doctrineFinal rows r2 v2).admitted = true)
    (t1 : v1.admitted = true → r1.text = true) (t2 : v2.admitted = true → r2.text = true)
    (l : String) (hl1 : l ∈ r1.labels) (hl2 : l ∈ r2.labels) : r1.target = r2.target

/-- The runner decides a label's ambiguity on the rows that carry it (a bucket); that is the same answer. -/
theorem ambiguousLabel_filter (rows : List DoctrineRow) (l : String) :
    ambiguousLabel (rows.filter (fun r => r.labels.contains l)) l = ambiguousLabel rows l

/-- **No joined line, no claim: no change** (treatments and history steps are round 6's). -/
theorem no_joined_no_change (c : Input) (e : Bool) (a? : Option Anchor) (h : HClaims)
    (ho : h.orderHead = false) (hs : h.setAside = false) :
    checkTreatment c e .plain [] = check c ∧ checkTreatment c e .operative [] = checkOperative c e ∧
      checkHistory7 c a? h = checkHistory c a?

/-- Without a doctrine row the class is round 5's. -/
theorem classOf7_no_doctrine (e r : Bool) (q : String) : classOf7 e r false q = classOf e r q

/-- **orderHead**: an admitted history row whose quote is head matter has the claim, a Supreme Court acting
decision dated on or after `orderHeadFrom` (20130101), a listed kind, an order-line cue of its kind, and at most
`orderHeadMaxLen` (400) characters. -/
theorem orderHead_sound (c : Input) (a? : Option Anchor) (h : HClaims)
    (hadm : (checkHistory7 c a? h).admitted = true) (hp : c.part = "headmatter") :
    h.orderHead = true ∧ h.scotus = true ∧ orderHeadFrom ≤ h.date ∧ orderHeadKind c.kind = true ∧
      orderLineCue c = true ∧ c.quote.length ≤ orderHeadMaxLen

/-- Without the claim, head matter fails as before. -/
theorem orderHead_no_claim (c : Input) (a? : Option Anchor) (h : HClaims) (ho : h.orderHead = false)
    (hp : c.part = "headmatter") : (checkHistory7 c a? h).admitted = false

/-- **setAside**: an admitted row without a cue of its kind is a `vacated` row with the claim and a set-aside
phrase. -/
theorem setAside_only_vacated (c : Input) (a? : Option Anchor) (h : HClaims)
    (hadm : (checkHistory7 c a? h).admitted = true) (hc : hasCue c = false) :
    h.setAside = true ∧ c.kind = .hist .vacated ∧ setAsideCue c = true

/-- Without the claim the cue list is the kind's. -/
theorem setAside_no_claim (c : Input) (a? : Option Anchor) (h : HClaims) (hs : h.setAside = false)
    (hadm : (checkHistory7 c a? h).admitted = true) : hasCue c = true
```

`Spec/Recognised.lean`:

```lean
/-- Every effect of a doctrine row has a demoted scope. -/
theorem doctrine_effects_demoted (byHist : List HEvent) (tr : TEvent) :
    ∀ e ∈ doctrineEffects byHist tr, ∃ s, e.scope = demote s

/-- **A doctrine row never makes a status negative**; alone it gives at most `unknown partialScope`. -/
theorem doctrine_never_neg (byHist : List HEvent) (tr : TEvent) (l : List Effect) (k : Nat) (t u : Date) :
    (∀ n, status (doctrineEffects byHist tr ++ l) k t u = .neg n → status l k t u = .neg n) ∧
      (status (doctrineEffects byHist tr) k t u = .good ∨
        status (doctrineEffects byHist tr) k t u = .unknown .partialScope)
```

Existing statements: none changed (`audit.py check` must list additions only).

### 1.4 Mutants (13; `Mutants.lean`, properties `properties7`)

New `Impl` fields: `checkTreatment`, `doctrineEffects`, `doctrineFinal`, `checkHistory7` (defaults: the real
functions). Joined mutants are `Cert.checkTreatmentWith (joinedWith …)` with one test replaced (`joinedWith` with the
real tests is `Cert.checkJoined` by `rfl`); history mutants are `Cert.checkHistory7With` with one test replaced.

| mutant | breaks | killed by property |
|---|---|---|
| M41 antecedent without the gap bound | `c.start - j.stop ≤ joinedGapMax` dropped | `antecedent_gap: gap` |
| M42 antecedent without an anaphor | anaphor test dropped | `antecedent_gap: anaphor` |
| M43 evidence in the main quote's window | check 5 reads the main quote and its windows (plain context), not a joined quote | `checkJoined_sound: evidence in a joined quote` |
| M44 tie without a tie cue | tie-cue test dropped | `doctrineTie_label: tie cue` |
| M45 tie without the label in both quotes | label-in-both test dropped | `doctrineTie_label: label in both quotes` |
| M46 doctrine row not demoted | `doctrineEffects` = `treatEffects` | `doctrine_never_neg` |
| M47 no doctrine uniqueness | `doctrineFinal` = the verdict | `doctrine_unique` |
| M48 a third joined line | count bound dropped | `checkJoined_bounded` |
| M49 joined quote from another text | check 1 reads another text's windows too | `checkJoined_sound: joined quote in the row's text` |
| M50 orderHead without the court test | `scotus` not tested | `orderHead_sound: court` |
| M51 orderHead without the date test | date not tested | `orderHead_sound: date` |
| M52 orderHead without the order-line cue | order-line cue not tested | `orderHead_sound: order line` |
| M53 setAside on any kind | the set-aside list added to every kind | `setAside_only_vacated` |

Guards (as round 6): the 13 new mutants and 13 new properties form a diagonal; no new mutant is caught by an earlier
property and no earlier mutant by a new property (so the earlier matrix is unchanged); the round-6 guards that
said "the mutants after 34" become "the six mutants after 34"; the count guard becomes `(27, 8, 6, 13, 53)`.

Definitions as built differ from 1.2 only in spelling: the Bool comparisons are written with an explicit `decide`
(`decide (1 ≤ js.length) && …`), which is what Lean elaborates `1 ≤ js.length && …` to; `orderLineHit` is D7-9.
Every statement of 1.3 is proved exactly as written there.

## 2. Tables, loader, runner

- **Cue table** (`tools/caselaw2/cues/cue_table.json`, generator `gen_cues.py`): keys `anaphor` (70 phrases after
  D7-8), `doctrine_tie` (31 after D7-12), `doctrine_reject` (35 after D7-12), `disqualify_joined` (13), `order_line` (certDenied 11,
  vacated 6, reversed 4, affirmed 4, reviewDismissed 12; entries with `" ... "` per D7-9), `set_aside` (5), and the
  constants `joined_gap_max` 300, `order_head_from` 20130101, `order_head_max_len` 400. The generator appends:
  `CueTable.lean` lines 1–85 and the first 5,799 bytes of both `cue_table.py` are byte-identical to `round7/pre/`.
  Python names: `ANAPHOR`, `DOCTRINE_TIE`, `DOCTRINE_REJECT`, `DISQUALIFY_JOINED`, `SET_ASIDE`, `ORDER_LINE` (dict
  kind → tuple), `JOINED_GAP_MAX`, `ORDER_HEAD_FROM`, `ORDER_HEAD_MAX_LEN`.
- **`Data.lean`**: `JoinedRow` (9 fields; `table` ∈ treatments | history and `rel` ∈ antecedent | doctrineTie
  checked by the parser, offsets numeric) and `HClaimRow` (3 fields; `claim` ∈ orderHead | setAside), loaded from the
  optional `joined.tsv` and `history_claim.tsv` into `Tables.joined` / `Tables.hclaims`. A line with a wrong field
  count, a non-numeric offset or an unknown word is not a line and is counted (`bad_rows joined.tsv n`,
  `bad_rows history_claim.tsv n`); with no file nothing is loaded or written.
- **`Run.lean`** (helpers outside `main`: `joinedTable`, `JoinedTab.summary`, `hclaimTable`, `HClaimTab.summary`,
  `doctrineAmbiguousLabels`; `main` carries `set_option maxHeartbeats 1000000 in`, since round 7 put it past the
  default compile budget LEAN6 §4 warned about; no proof is affected):
  - joined lines: a `history` line → `joined_history_ignored` (an unknown history id → `joined_unknown_ids`); a
    treatments line whose id is no treatments row → `joined_unknown_ids`; on a witness row →
    `joined_witness_ignored` (L7-1); a third line for an id → `joined_extra`; the first two are kept in file order;
  - a `doctrine` class line is now a claim (`class_rows` counts it; before round 7 it was a `class_bad_rows` line);
  - doctrine rows: before the treatments loop, each row with a doctrine claim is text-checked
    (`Cert.checkTreatment … (some true) … .doctrine js`), and `doctrineAmbiguousLabels` computes the labels the
    passing rows tie to two targets (`Cert.ambiguousLabel` per label bucket; `Cert.ambiguousLabel_filter`); a row
    carrying such a label gets `doctrineAmbiguous` instead of an admitted verdict (`Cert.doctrineFinal`), under both
    rule sets and in its text check (L7-4);
  - each non-witness treatments row is checked by `Cert.checkTreatment (inp auth) explicit mode js` (mode doctrine /
    operative / plain from the claim); a witness row exactly as in round 6, unless it carries a doctrine claim (then
    `doctrineBadRow`, L7-2); without joined lines and doctrine claim this is `check` / `checkOperative`
    (`Cert.no_joined_no_change`);
  - a doctrine row's events are mapped through `Spec.doctrineEvent` (demoted, after the issue/power splitting); its
    class is `doctrine` (`Cert.classOf7`, which is `classOf` without a doctrine row);
  - each history row is checked by `Cert.checkHistory7 inp anchor? claims` with `claims` from `history_claim.tsv`
    (orderHead, setAside), `scotus` = the acting decision's court epoch at its date is the Supreme Court's
    (`CourtEpoch.scotus`, under the rule set's tables), `date` = the acting decision's `decisions2.tsv` date; a row
    without claims gets `checkHistory`'s verdict (`Cert.no_joined_no_change`);
  - `summary.tsv`, each block only when its table has a line: `joined_rows`, `joined_lines`, `joined_unknown_ids`,
    `joined_extra`, `joined_history_ignored`, `joined_witness_ignored`, `joined_admitted`, `joined_rejected`;
    `hclaim_rows`, `hclaim_unknown_ids`, `hclaim_duplicates`, `hclaim_admitted`, `hclaim_rejected`; and, when a
    class line has claim doctrine, `doctrine_rows`, `doctrine_admitted`, `doctrine_ambiguous` (admitted = full rule
    set);
  - `certs.tsv`: new verdicts `joinedMismatch`, `joinedPart`, `joinedDisqualified`, `joinedRelation`,
    `joinedUnresolved`, `doctrineBadRow`, `doctrineAmbiguous`, `orderHeadNotAllowed`; `classes.tsv`: class
    `doctrine`, claim `doctrine`, with the class line's field limit and doctrine columns (as round 5).
- `run_lean.sh` is unchanged (it already merges `classes.tsv` and adds `oclass` in round-5 mode).
- WSL scripts (new; none changed): `wsl/r7_lean.sh` (sync + build, errors only), `wsl/r7_lean_base.sh` (the
  byte-identical regressions of section 3), `wsl/r7_joined_fixture.sh` (the fixture).

## 3. Results (13 Nov 2026; Linux Lean 4.35.0 in WSL Ubuntu)

- **Build** (`wsl/r7_lean.sh all`: `lake build LegalProofs.CaseLaw2 LegalProofs.CaseLaw2.Run` and the native runner
  `caselaw2`): green. The 22 theorems of 1.3 are proved as stated (none changed after stating). No `sorry`, no new
  axiom, no `native_decide` (`audit.py` hygiene: 0 problems). Final run with the final cue table (after D7-12):
  build 23:43, `audit.py check` 23:44 (220 theorems, 0 changes, 0 problems), fixture 23:45, regressions 23:45–00:00,
  all green (`agents/lean/r7_final.log`).
- **Audit:** `audit.py check` before the lock: 220 theorems, 37 statement changes, all `new`, 0 problems. Locked
  with the reason in `wsl/lock_reason.txt` (`STATEMENTS.log`, 23:26). `audit.py check` after the lock and rebuild:
  220 theorems, 0 changes, 0 problems. Against `round7/pre/audit/statements.lock`: **0 removed, 0 changed (statement
  or axioms), 37 added** (the 22 of 1.3 and 15 helper lemmas: `checkJoined_admitted_bool`, `joinedQuoteOk_window`,
  `mainCheck_check`, `check_text`, `mainCheck_text`, `checkJoined_text`, `checkBy_check`, `checkBy_cue_part`,
  `anchoredThen_fin`, `checkHistory7_claims`; `Spec.Status.partially_rank_le`, `Spec.treatEffect_scope`,
  `Spec.treatEffects_scope`, `Spec.demoted_contrib_le`, `Spec.demoted_status_le`).
- **Counts:** theorems 183 → 220; mutants 40 → 53; properties 41 → 54 (`properties7`, 13); `#guard`s in
  `Examples` 223 → 308 (85 replays of joined, doctrine and claim rows), in `Mutants` 8 → 11; `example`s by `rfl` in
  `Mutants` 1 → 4 (`joinedWith`, `treatWith` and `checkHistory7With` with the real tests are the real checkers). The
  13 new mutants and 13 new properties form a diagonal (guarded); no new mutant is caught by an earlier property and
  no earlier mutant by a new property, so the earlier kill matrix is unchanged (`#eval killMatrix`).
- **Changed guards in `Mutants.lean`** (not theorems): the round-6 guard `(mutants.drop 34)` became
  `((mutants.drop 34).take 6)`; the count guard is `(27, 8, 6, 13, 53)`.
- **Fixture** (`round7/fixtures/joined/`, `make_joined_fixture.py`, run by `wsl/r7_joined_fixture.sh`): 25 synthetic
  treatments rows and 14 history rows, each in its own acting text, windows cut a few characters around each quote
  (so a citation in another sentence is outside the one-quote certificate). `certs.tsv` = `expected_certs.tsv` (39
  lines); the round-7 counters of `summary.tsv` = `expected_summary.tsv`; the doctrine / operative lines of
  `classes.tsv` = `expected_classes.tsv`. Without the round-7 tables (`data_nojoined/`: no `joined.tsv`, no
  `history_claim.tsv`, no doctrine class line) `certs.tsv` = `expected_certs_nojoined.tsv` and no round-7 counter is
  written. Output kept in `out/` and `out_nojoined/`. Run after D7-12 (final lists): green.

  | row | what | verdict | without the round-7 tables |
  |---|---|---|---|
  | `t7:10` | "In Smith v. Jones, 100 U. S. 1, … ." two sentences before "That case is overruled." | `ok` | `targetUnresolved` |
  | `t7:11` | the same, its only joined lines malformed (bad offset, unknown rel) | `targetUnresolved` | same |
  | `t7:12`, `t7:13`, `t7:14` | joined offset +3; joined window with a wrong hash; joined quote and offset of another text | `joinedMismatch` | `targetUnresolved` |
  | `t7:15` | joined part `dissent` | `joinedPart` | `targetUnresolved` |
  | `t7:16` | "As the dissent notes, …" | `joinedDisqualified` | `targetUnresolved` |
  | `t7:17` | the cases' sentence 497 characters before the act | `joinedRelation` | `targetUnresolved` |
  | `t7:18` | act without an anaphor ("The tax rule of the mails is overruled.") | `joinedRelation` | `targetUnresolved` |
  | `t7:19` | the citation in the act's window, not in the joined quote | `joinedUnresolved` | `ok` |
  | `t7:20` | two lines (the second has the citation); a third line ignored (`joined_extra`) | `ok` | `targetUnresolved` |
  | `t7:21` | the act is a dissent's | `partNotMajority` | `targetUnresolved` |
  | `t7:22` | acting court without an epoch | `okUnverifiedBy` | `targetUnresolved` |
  | `t7:23` | operativeWords claim, act "Those decisions are disapproved and are no longer good law." | `ok` | `targetUnresolved` |
  | `t7:24` | operativeWords claim, act without "disapprov" (L7-13, D7-10) | `joinedRelation` | `targetUnresolved` |
  | `t7:30` | Brown: "the doctrine of 'separate but equal' has no place", tie sentence naming Plessy | `ok` (class `doctrine`; Plessy `unknown:partialScope` from 17 May 1954, never negative) | `noCue` |
  | `t7:31`, `t7:32` | doctrine claim without a tie line; kind `overruled` | `doctrineBadRow` | `noCue` |
  | `t7:33`, `t7:34` | tie sentence without a tie cue; without the label | `joinedRelation` | `noCue` |
  | `t7:35` | act "The argument that … has no place is rejected." | `disqualified` | `noCue` |
  | `t7:36`, `t7:37` | "clear and present danger" tied to Schenck by one row and to Abrams by another | `doctrineAmbiguous` (both) | `noCue` |
  | `t7:38` | a tie line on a row without a doctrine claim | `joinedRelation` | `noCue` |
  | `t7:39` | witness row with a joined line (ignored, `joined_witness_ignored`) | `witnessBadRow` | same |
  | `h7:50` | SCOTUS 2014 order, "Certiorari denied." head matter, `orderHead` | `ok` | `partNotMajority` |
  | `h7:51` | "Petition for writ of certiorari to the United States Court of Appeals for the Fifth Circuit denied." (D7-9) | `ok` | `partNotMajority` |
  | `h7:52`, `h7:53`, `h7:54`, `h7:55`, `h7:59` | dated 2012; acting court the Fifth Circuit; "Motion for leave … denied."; a 467-character quote; kind `modified` | `orderHeadNotAllowed` | `partNotMajority` |
  | `h7:56`, `h7:58` | head matter without the claim; claim on a dissent | `partNotMajority` | same |
  | `h7:57` | anchored (round 6) and `orderHead` | `ok` | `partNotMajority` |
  | `h7:60` | `vacated`, "The judgment … is set aside.", `setAside` | `ok` | `noCue` |
  | `h7:61`, `h7:62` | the same quote as `reversed` with the claim; as `vacated` without it | `noCue` | same |
  | `h7:63` | `vacated` "is vacated" with both claims | `ok` | same |

  Table rules: `joined_unknown_ids 1`, `joined_extra 1`, `joined_history_ignored 1`, `joined_witness_ignored 1`,
  `bad_rows joined.tsv 2`; `hclaim_unknown_ids 1`, `hclaim_duplicates 1`, `bad_rows history_claim.tsv 1`; counters
  `joined_rows 22`, `joined_admitted 5`, `hclaim_rows 12`, `hclaim_admitted 5`, `doctrine_rows 8`,
  `doctrine_admitted 1`, `doctrine_ambiguous 2`.
- **Regression, no round-7 table** (`wsl/r7_lean_base.sh`; every output file compared byte for byte, `summary.tsv`
  without its two timing lines). Run twice: before D7-12 (`agents/lean/r7_lean_base_before_D7-12.log`) and after
  it with the final cue table (`agents/lean/r7_final.log`); both all byte-identical:
  - (a) the round-6 frozen build `round6/history/stage/final2` (assembled as `wsl/r6_run.sh` does: the round-5 final
    mirror plus the five staged tables; the four MANIFEST hashes checked, and every table of the stage compared byte
    for byte with the assembled one; no `joined.tsv`, no `history_claim.tsv`, no doctrine class line) against
    `round6/history/out/final2`: certs (473,582 lines, `68f6fb621957…` = the FREEZE hash), classes, findings,
    horty, splits, status (648,899 lines, `96888c8b4381…` = FREEZE), status_lines, summary: **all byte-identical**;
  - (a2) the same with **empty** `joined.tsv` and `history_claim.tsv`: all byte-identical;
  - (b) the round-5 frozen build (`round5/stage/final`, MANIFEST checked) against `round5/out/final`: certs,
    classes, findings, horty, splits, status, status_lines, summary: **all byte-identical**;
  - (c) the round-4 tables (`data_r4`) against the round-4 final output (`difftest/real20/lean`): certs, findings,
    horty, splits, status, status_lines, summary: **all byte-identical**.

## 4. Notes for the other agents

- **Reference engine.** `tools/caselaw2/ref/precedent_ref.py` was not touched (the reference has its own writer and
  is written from DESIGN7). `ref/cue_table.py` and `reader/cue_table.py` are regenerated (section 2 names). Until
  the reference implements section 1, a `ref` diff on a variant with round-7 tables differs on those rows.
- **`certify7.py` must match section 1 exactly**, in particular: every joined quote's window must be listed in
  `cert_text.tsv` (and `window_sha.tsv`) under the **row's own** `text_sha`, and the window must cover the joined
  span (a window that does not cover a quote is not usable for it); the target evidence must be inside a joined
  quote (compact citation as a substring of the compact quote, and the index maps it to the target; name tokens of
  3+ characters as whole words); joined parts majority / plurality / perCuriam only; an `antecedent` line ends at or
  before the main quote's start and at most 300 characters before it, the main quote has an anaphor **and** a cue of
  the kind's plain list (D7-10); a `doctrineTie` line only on a doctrine row (explicit, `disapproved`), its label
  (normalised, lower-cased; two words, eight characters) in both quotes and a tie cue in the joined quote; a doctrine
  row's main quote is checked with `doctrine_reject` cues and `disqualify_treat` + `disqualify_operative`.
- **Order lines (D7-9).** An entry of `ORDER_LINE` that splits on `" ... "` into exactly two parts a, b matches when
  a occurs in the lower-cased quote and b occurs after its first occurrence (the disqualifier pairs' `hasInOrder`);
  any other entry is a substring.
- **Doctrine uniqueness (L7-4)** is decided once, on the text check, over all doctrine rows of the table (labels
  compacted: letters and digits, lower case); `doctrineAmbiguous` replaces an admitted verdict under both rule sets.
- A malformed joined or claim line is not a line: its row is then checked as if it had none.
- `Run.main` now has a raised compile budget (`set_option maxHeartbeats 1000000 in`); further additions should
  still go into helpers.
