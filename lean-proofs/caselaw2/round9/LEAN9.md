# Round 9, Lean: part zones (§4)

Contract: `DESIGN9.md` §4 (D9-3). Written by the agent `lean9`, 14 Nov 2026 (started 02:10). Sections 0 and 1 were
written **before** any code or proof (02:13–02:15): the statements are the target; a statement that proves false is
refuted and reported, never weakened silently. Sections 2–4 are written after the build.

Backup of everything changed: `round9/pre/` (`CaseLaw2/`, `CaseLaw2.lean`, `tools_caselaw2/` (cue table, generator,
generated `cue_table.py` copies), `audit/statements.lock`, `STATEMENTS.log`, `run_lean*.sh`, `runner/` sources, `wsl/`,
`ref/` and `fuzz/` copies; `SHA1SUMS.txt`). `round9/pre/CaseLaw2` is the round-8 final state.

## 0. Readings of points DESIGN9 §4 leaves open

| # | point | what the Lean does |
|---|---|---|
| L9-1 | "the row's acting node" (whose zones apply) | **as ruled in D9-4 (1)** (02:18; my first reading, 02:15, gave a selfText history row no zone): the node whose text the main quote is from (the text owner): a treatments row → `by`, or the witness W for a row with a `treatment_witness.tsv` line; a history row → the target when the row's `text_sha` is the target's text hash (`selfText`, round 4), else `by` (none when `by = -1`: no zone, counted missing). Joined quotes: the same text owner. (v8e: 0 of 184,798 history rows are selfText.) |
| L9-2 | "the row's part" | the CERT `part` column of the row (`treatments.tsv` / `history.tsv` col. 12), as the round-4 checks read it; a joined line's is its `j_part` (`joined.tsv`). Spellings: exactly the seven strings of DESIGN9 §4 (`majority`, `plurality`, `perCuriam`, `concurrence`, `dissent`, `headmatter`, `other`), case-sensitive; equality is string equality |
| L9-3 | offsets | `z_start`, `z_end`, `start`, `end` are compared as numbers in the row's offset space (no translation); a zone is the half-open `[z_start, z_end)`; "inside" = `z_start ≤ start ∧ end ≤ z_end` (DESIGN9's formula). A quote whose span is empty never reaches the test (the round-4 check refuses it first) |
| L9-4 | "overlap" | two zones of a node overlap when neither ends at or before the other's start (`¬(a.end ≤ b.start ∨ b.end ≤ a.start)`); touching zones (`a.end = b.start`) do not overlap. Two identical lines of a well-formed zone overlap (the node loses its zones) |
| L9-5 | malformed line | **as ruled in D9-4 (4)**: a line that is not UTF-8, has ≠ 5 fields, or whose node / `z_start` / `z_end` is not a natural number is a bad line: ignored, counted (`bad_rows part_zone.tsv n`, the loader's round-4 counter, and `zone_bad_rows`), and does not poison its node. A parsed line with `z_start ≥ z_end` or a part outside the seven poisons its node (all its zones dropped) |
| L9-6 | which checks the zone test follows | it wraps the row's verdict under each rule set (full and S/L) and the row's text check (power taken as given), so a row refused by the zone test has no event, no class `recognised`, and its certificate is not the evidence of a `laterCourtSays:` supersession (round 4's `treatOkText`, the plain check of the row, D9-4 (3)). "After the row's own checks pass" (D9-4 (2)): only an admitted round-8 verdict (`ok`, `okUnverifiedBy`, `okRecognised…`) can turn into `partZone`; any failure (including `targetLater`, `noAuthority`, `doctrineAmbiguous`) keeps its reason. The doctrine-uniqueness table is decided on the round-8 text checks, zones not consulted ("a zone failure never removes an ambiguity", D9-4 (2)) |
| L9-7 | witness rows | a witness row's verdict is an `RResult`: an admitted one (recognised or witness-ok) whose quote is outside every zone of its part becomes `witness (fail partZone)`; written `partZone` |
| L9-8 | which quotes | the main quote of every treatments / history row (plain, operative, doctrine, witness, recognised, anchored, bridged, claimed); each joined line of a treatments row with its `j_part`. Never: an anchor quote, a bridge quote (DESIGN9), a holding's certificate (not a treatments or history row) |
| L9-9 | counters (`summary.tsv`, only when `part_zone.tsv` has a line, well formed or not; D9-4 (4) names) | `zone_nodes` (nodes that keep zones), `zone_lines` (their zone lines), `zone_bad_nodes` (poisoned nodes), `zone_bad_rows` (bad lines), `zone_checked_rows` (treatments + history rows whose full-rule-set round-8 verdict admits — they reach the zone check — and whose text owner keeps zones), `zone_failed_rows` (rows whose full-rule-set verdict is `partZone`), `zone_missing_rows` (rows that reach the check and whose text owner keeps no zone) |
| L9-10 | presence | absent or empty file: every zone list is `[]` and every wrapper is the identity (`no_zone_no_change`); the summary has no zone counter; the loader adds no `Problems` entry for an absent file, so `round8/out/v8e` is reproduced byte for byte |

Questions for the lead (`round9/agents/lean9/QUESTIONS.md`): Q1 (L9-1) and Q2 (L9-6) answered 02:18 (INBOX, D9-4);
Q3 (whether D9-4 (2) "verdict is `ok`" means every admitted verdict) and Q4 (the 02:18 answer "no doctrine-uniqueness
entry" against D9-4 (2) "a zone failure never removes an ambiguity": the Lean follows D9-4) are open, continuing on
the readings above.

## 1. Definitions and theorems (stated first)

Checker definitions in `LegalProofs/CaseLaw2/Certificate.lean` (namespace `CaseLaw2.Cert`, a new round-9 section after
round 8's). No cue-table change.

### 1.1 Definitions

```lean
-- reason appended to `Reason`
  | partZone

structure Zone where
  start : Nat
  stop : Nat
  part : String
  deriving Repr, DecidableEq, Inhabited

def zoneParts : List String := ["majority", "plurality", "perCuriam", "concurrence", "dissent", "headmatter", "other"]
def zoneWellFormed (z : Zone) : Bool := decide (z.start < z.stop) && zoneParts.contains z.part
def zonesDisjoint (a b : Zone) : Bool := decide (a.stop ≤ b.start) || decide (b.stop ≤ a.start)
def noOverlap : List Zone → Bool
  | [] => true
  | z :: zs => zs.all (zonesDisjoint z) && noOverlap zs
def zonesValid (zs : List Zone) : Bool := zs.all zoneWellFormed && noOverlap zs
/-- the zones a node keeps: all its lines, or none when one is malformed or two overlap -/
def nodeZones (zs : List Zone) : List Zone := if zonesValid zs then zs else []

def inZone (s e : Nat) (p : String) (z : Zone) : Bool := decide (z.start ≤ s) && decide (e ≤ z.stop) && z.part == p
def zoneHas (zs : List Zone) (s e : Nat) (p : String) : Bool := zs.any (inZone s e p)
/-- the main quote, and every joined quote, inside a zone of its own part -/
def partZoneOk (zs : List Zone) (c : Input) (js : List Joined) : Bool :=
  zoneHas zs c.start c.stop c.part && js.all (fun j => zoneHas zs j.start j.stop j.part)
/-- **checkPartZone**: after the row's own verdict `r` (the first failure keeps its reason). -/
def zoneThen (zs : List Zone) (c : Input) (js : List Joined) (r : Result) : Result :=
  if zs.isEmpty then r else if r.admitted && !partZoneOk zs c js then .fail .partZone else r
/-- the same on a witness row's verdict -/
def zoneR (zs : List Zone) (c : Input) (v : RResult) : RResult :=
  if zs.isEmpty then v else if v.admitted && !partZoneOk zs c [] then .witness (.fail .partZone) else v

/-- **The runner's steps in round 9** (`zs` = the zones the row's zone node keeps, `nodeZones` of its lines). -/
def checkHistory9 (zs : List Zone) (c : Input) (a? : Option Anchor) (b? : Option Bridge) (h : HClaims) : Result :=
  zoneThen zs c [] (checkHistory8 c a? b? h)
def checkTreatment9 (zs : List Zone) (c : Input) (e : Bool) (cl : TClaim) (js : List Joined) : Result :=
  zoneThen zs c js (checkTreatment c e cl js)
def checkRecognised9 (zs : List Zone) (c : Input) (w : Witness) : RResult := zoneR zs c (checkRecognised c w)
```

(The runner applies `zoneThen` after the doctrine-uniqueness verdict `doctrineFinal`, L9-6, so a doctrine row keeps
`doctrineAmbiguous`.)

### 1.2 Theorems (4 stated, as DESIGN9 names them)

```lean
/-- **No zone line, no change**: with no zone the three round-9 steps are round 8's (and the wrappers are the
identity on any verdict). -/
theorem no_zone_no_change (c : Input) (a? : Option Anchor) (b? : Option Bridge) (h : HClaims) (e : Bool) (cl : TClaim)
    (js : List Joined) (w : Witness) (r : Result) (v : RResult) :
    checkHistory9 [] c a? b? h = checkHistory8 c a? b? h ∧ checkTreatment9 [] c e cl js = checkTreatment c e cl js ∧
      checkRecognised9 [] c w = checkRecognised c w ∧ zoneThen [] c js r = r ∧ zoneR [] c v = v

/-- **Zone soundness**: an admitted row whose node has zones has its main quote inside a zone of the row's part and
every joined quote inside a zone of its own part, and the round-8 verdict admits and is the verdict. -/
theorem partZone_sound (zs : List Zone) (c : Input) (js : List Joined) (r : Result) (hz : zs ≠ [])
    (hadm : (zoneThen zs c js r).admitted = true) :
    r.admitted = true ∧ zoneThen zs c js r = r ∧
      (∃ z ∈ zs, z.start ≤ c.start ∧ c.stop ≤ z.stop ∧ z.part = c.part) ∧
      ∀ j ∈ js, ∃ z ∈ zs, z.start ≤ j.start ∧ j.stop ≤ z.stop ∧ z.part = j.part

/-- **Zone uniqueness**: in non-overlapping zones at most one zone contains a non-empty quote. -/
theorem partZone_unique (zs : List Zone) (hv : noOverlap zs = true) (s e : Nat) (hse : s < e) (z1 z2 : Zone)
    (h1 : z1 ∈ zs) (h2 : z2 ∈ zs) (i1 : z1.start ≤ s ∧ e ≤ z1.stop) (i2 : z2.start ≤ s ∧ e ≤ z2.stop) : z1 = z2

/-- **A bad node is ignored**: a node with a malformed zone or two overlapping zones keeps none, and its rows get
the round-8 verdict. -/
theorem zone_bad_node_ignored (zs : List Zone)
    (hb : (∃ z ∈ zs, zoneWellFormed z = false) ∨ noOverlap zs = false)
    (c : Input) (js : List Joined) (r : Result) (v : RResult) :
    nodeZones zs = [] ∧ zoneThen (nodeZones zs) c js r = r ∧ zoneR (nodeZones zs) c v = v
```

Instances and helpers expected (locked as additions): `partZone_sound_witness` (the same for `zoneR`: the round-8
witness verdict admits and is the verdict; the main quote inside a zone of the row's part), `checkHistory9_sound`
(an admitted round-9 history row with zones: `checkHistory8` admits, and the quote is inside a zone of its part),
`checkTreatment9_sound` (likewise with every joined line), `zoneThen_fail_keeps` (a failing verdict is unchanged:
`r.admitted = false → zoneThen zs c js r = r`), `nodeZones_valid` (`zonesValid (nodeZones zs) = true`),
`noOverlap_pairwise` (`noOverlap zs = true → ∀ a ∈ zs, ∀ b ∈ zs, a ≠ b → zonesDisjoint a b = true`, if needed).

### 1.3 Mutants (3; `Mutants.lean`, properties `properties9`)

New `Impl` field `partZone : List Cert.Zone → Cert.Input → List Cert.Joined → Cert.Result → Cert.Result`, default
`fun raw c js r => Cert.zoneThen (Cert.nodeZones raw) c js r` (the runner's composition: a node's lines, then the
check). The mutants replace `inZone` or `nodeZones` in `zoneThenWith inZ keep`.

| mutant | breaks | killed by property |
|---|---|---|
| M64 zone straddles a boundary | `inZ` = the quote overlaps a zone of its part (`z.start < e ∧ s < z.stop`) | `partZone_sound: inside one zone` (a quote across the majority/dissent boundary) |
| M65 zone of another part | `inZ` ignores the part | `partZone_sound: the row's part` (a majority row inside a dissent zone) |
| M66 keep the zones of an overlapping node | `keep := id` | `zone_bad_node_ignored` (an overlapping node's row keeps its round-8 `ok`) |

Guards: the 3 new mutants and 3 new properties form a diagonal; no new mutant is caught by an earlier property and
no earlier mutant by a new property; the count guard becomes `(27, 8, 6, 13, 10, 3, 66)`. Examples: `#guard`s on
zone lists (inside, straddling, other part, touching zones, overlapping / malformed node, no zone, joined line, witness
row, doctrineAmbiguous kept, failure reason kept).

### 1.4 Fixture `round9/fixtures/partzone`

Built from `round8/fixtures/bridge` (or a small own stage): treatments + history rows over zones of their acting
nodes: inside (ok), straddling (partZone), other part (partZone), a round-8 failure kept, a node with overlapping zones
(round-8 verdict, `zone_bad_nodes`), a malformed line, a non-numeric node line (bad row), a row with no zone
(`zone_missing_rows`), a joined line outside its part, unknown node lines; expected certs and counters, and the same
stage without `part_zone.tsv` = the round-8 output.

## 5. Batch 2: far joined antecedents (DESIGN9 §5, claim `joinedFar`) and implicit rejection (§7, claim `implicitReject`)

D9-5 (02:25). Stated here before any code of this batch (written 02:37–02:38, after the §4 code and before the §4
lock). Both are claim-gated: without a `joinedFar` / `implicitReject` line the output is round 8's (and §4's).

### 5.0 Readings

| # | point | what the Lean does |
|---|---|---|
| L9-11 | the claim lines | `joinedFar` and `implicitReject` are class-line claims of `treatment_class.tsv` like `doctrine` (the first valid line for an id wins; the claim column of `classes.tsv` shows them; `class_rows` counts them). A `joinedFar` row's main quote is read in plain mode |
| L9-12 | the gap | `gap = start − j_end` of an `antecedent` line (main quote's start, joined quote's end). **Revised 02:46 (D9-7, Q9-12 as ruled 02:40):** a line passing round 7's relation is unchanged; a failing `antecedent` line with `j_end ≤ start` and `gap > joined_gap_max` (300) gets the far tests; any other failing line is `joinedRelation`; the first failing line in file order gives the reason |
| L9-13 | order of the far reasons (Q9-12) | `joinedFarGap` (gap > `joined_far_max`), `joinedFarWindow`, `joinedFarKey`, then the anaphor and kind cue of the main quote (`joinedRelation`) |
| L9-14 | the window | a usable window (well formed, hash-consistent: round 4's `usable`) of the row's own text with `start0 ≤ j_end` and `start ≤ stop0`; the first such in the list (every usable window is the corpus text, so the choice does not matter; the theorem states "some usable window") |
| L9-15 | "no newline" | **dropped by D9-7** (read 02:45): no paragraph test, no `joinedFarPara`. (Observation: the v8e windows hold no `'\n'` — 0 of 100,002 sampled; 8 hold the two characters `\` `n` of a header — so the test could not have failed on this corpus) |
| L9-16 | "no index key starts in `[j_end, start)` that maps to another node" | positions over the lower-cased (ASCII) alphanumeric characters of the window text from `j_end` to the window's end (as bridges, L8-1/L8-2); a key of any length of the index (its distinct key lengths, longest first, as `Bridge.lens`) that begins at an alphanumeric character at relative position `< gap` and maps to a node ≠ the row's target fails the test. Keys the data gives two nodes are not keys (round 4). No index supplied: no key, the test passes |
| L9-17 | soft kinds (§7) | the kinds with `softNegative = true`: `limited`, `questioned`, `criticized`, `declinedToFollow` (= Q9-16). Any other kind with the claim fails `implicitBadKind` (`implicitReject_soft`), before the witness path (Q9-18) |
| L9-18 | §7 check | `implicitBadKind` first; then, a row without joined lines: round 4's `check` with the cue test `hasCue ∨ an implicit_reject phrase` (all else unchanged: hash, window, quote, disqualifiers, evidence, part, date order, power — soft kinds are given power, as today); a claimed soft row with joined lines keeps its round-8 joined check (the claim widens only the plain check) |
| L9-19 | step order of a treatments row | doctrine claim → `checkDoctrine` (round 7); `implicitReject` claim → §7; witness line → `checkRecognised`; else the treatment step, with the far relation under a `joinedFar` claim. Then the §4 zone test on the verdict |
| L9-20 | counters | none new (`class_rows` counts the claim lines; the verdicts are in `certs.tsv`) |

### 5.1 Definitions (Certificate.lean, a round-9 batch-2 section; cue table: `joined_far_max` 1200 → `joinedFarMax`, `implicit_reject` (18 phrases) → `implicitRejectCues`)

```lean
-- reasons appended: joinedFarGap | joinedFarWindow | joinedFarKey | implicitBadKind   (02:46: no joinedFarPara, D9-7)
def farInput (c : Input) (j : Joined) : Input := { c with start := j.stop, stop := c.start }
def farWindow (c : Input) (j : Joined) : Option Window := c.windows.find? (usable (farInput c j))
def farAlnum (c : Input) (j : Joined) (w : Window) : List (Char × Nat) :=
  alnumPos ((w.text.toList.drop (j.stop - w.start0)).map Char.toLower) 0
def farKeyOk (lens : List Nat) (c : Input) (j : Joined) (w : Window) : Bool :=
  match c.citeIndex with
  | none => true
  | some m => allSuffix (fun s => match headPos s with
      | some p => !decide (p < c.start - j.stop) || lens.all (fun L => (citeOf m s L).all (· == c.target))
      | none => true) (farAlnum c j w)
def farReasonWith (maxGap : Nat) (keyOk : Input → Joined → Window → Bool) (ana : Input → Bool) (c : Input)
    (j : Joined) : Option Reason :=
  if maxGap < c.start - j.stop then some .joinedFarGap
  else match farWindow c j with
    | none => some .joinedFarWindow
    | some w => if !keyOk c j w then some .joinedFarKey else if !ana c then some .joinedRelation else none
def farRelWith (fr : Input → Joined → Option Reason) (cl : TClaim) (c : Input) (j : Joined) : Option Reason :=
  if relationOk cl c j then none
  else if j.rel == .antecedent && decide (j.stop ≤ c.start) && decide (joinedGapMax < c.start - j.stop) then fr c j
  else some .joinedRelation
def checkJoinedFarWith (fr : Input → Joined → Option Reason) (c : Input) (explicit : Bool) (cl : TClaim)
    (js : List Joined) : Result :=
  if !(joinedCountOk js && js.all (joinedQuoteOk c)) then .fail .joinedMismatch
  else if !js.all joinedPartOk then .fail .joinedPart
  else if js.any (joinedDisqualified c) then .fail .joinedDisqualified
  else match js.findSome? (farRelWith fr cl c) with
    | some r => .fail r
    | none => if !js.any (joinedResolves c) then .fail .joinedUnresolved
      else mainCheck { c with selfText := true } explicit cl
def farReason (lens : List Nat) := farReasonWith joinedFarMax (farKeyOk lens) (fun c => anaphorCue c.quote && kindCue c)
def checkJoinedFar (lens : List Nat) := checkJoinedFarWith (farReason lens)
/-- the runner's treatment step under the `joinedFar` claim (`far`) -/
def checkTreatmentF (far : Bool) (lens : List Nat) : Input → Bool → TClaim → List Joined → Result :=
  if far then checkTreatmentWith (checkJoinedFar lens) else checkTreatment

-- §7
def implicitSoft : Kind → Bool
  | .treat .limited | .treat .questioned | .treat .criticized | .treat .declinedToFollow => true
  | _ => false
def implicitCue (c : Input) : Bool := implicitRejectCues.any (hasSub (norm c.quote).toLower)
def plainPart (c : Input) : Option Reason := if partOk c then none else some .partNotMajority
def checkImplicitWith (kindOk : Kind → Bool) (cue : Input → Bool) (c : Input) (e : Bool) (js : List Joined) : Result :=
  if !kindOk c.kind then .fail .implicitBadKind
  else if js.isEmpty then checkBy cue plainPart c else checkTreatment c e .plain js
def checkImplicit := checkImplicitWith implicitSoft (fun c => hasCue c || implicitCue c)
/-- the runner's step under the `implicitReject` claim (`imp`) -/
def checkTreatmentI (imp : Bool) (c : Input) (e : Bool) (cl : TClaim) (js : List Joined) : Result :=
  if imp then checkImplicit c e js else checkTreatment c e cl js
```

### 5.2 Theorems

```lean
theorem joinedFar_no_claim (lens : List Nat) : checkTreatmentF false lens = checkTreatment
/-- every row admitted without the claim is admitted with it, with the same verdict -/
theorem joinedFar_extends (lens : List Nat) (c : Input) (e : Bool) (cl : TClaim) (js : List Joined)
    (h : (checkTreatment c e cl js).admitted = true) : checkTreatmentF true lens c e cl js = checkTreatment c e cl js
/-- an admitted claimed row's antecedent line: before the main quote, within `joinedFarMax`, an anaphor and a kind
cue in the main quote; beyond `joinedGapMax`, a usable window of the row's text covers the gap, in which no index key
of another node begins (02:46: the newline clause removed with D9-7) -/
theorem antecedentFar_gap (lens : List Nat) (c : Input) (e : Bool) (cl : TClaim) (js : List Joined)
    (h : (checkTreatmentF true lens c e cl js).admitted = true) (j : Joined) (hj : j ∈ js) (hr : j.rel = .antecedent) :
    j.stop ≤ c.start ∧ c.start - j.stop ≤ joinedFarMax ∧ anaphorCue c.quote = true ∧ kindCue c = true ∧
      (c.start - j.stop ≤ joinedGapMax ∨
        ∃ w ∈ c.windows, usable (farInput c j) w = true ∧
          ∀ m, c.citeIndex = some m → ∀ s, s <:+ farAlnum c j w → ∀ p, headPos s = some p → p < c.start - j.stop →
            ∀ L ∈ lens, ∀ n, citeOf m s L = some n → n = c.target)
theorem implicitReject_no_claim (c : Input) (e : Bool) (cl : TClaim) (js : List Joined) :
    checkTreatmentI false c e cl js = checkTreatment c e cl js
theorem implicitReject_soft (c : Input) (e : Bool) (js : List Joined) (h : (checkImplicit c e js).admitted = true) :
    implicitSoft c.kind = true
-- Examples.lean (it needs `Spec`): soft means `softNegative`, and the effects are none
theorem implicitSoft_softNegative (k : TKind) : Cert.implicitSoft (.treat k) = k.softNegative
theorem implicitReject_never_neg (c : Cert.Input) (e : Bool) (js : List Cert.Joined) (k : TKind)
    (hk : c.kind = .treat k) (h : (Cert.checkImplicit c e js).admitted = true) (bh : List HEvent) (tr : TEvent)
    (htk : tr.kind = k) (l : List Effect) (n : Nat) (t u : Date) :
    treatEffect bh tr = none ∧ status ((treatEffect bh tr).toList ++ l) n t u = status l n t u
```

### 5.3 Mutants (5; new `Impl` fields `checkTreatmentF`, `checkTreatmentI`)

| mutant | breaks | killed by property |
|---|---|---|
| M67 far antecedent past another citation | `keyOk := true` | `antecedentFar_gap: no other key` |
| M68 far antecedent at any distance | `maxGap` huge | `antecedentFar_gap: bound` |
| M69 far antecedent without an anaphor (D9-7) | `ana := kindCue` | `antecedentFar_gap: anaphor` |
| M70 implicitReject on an overruled row | `kindOk := true` | `implicitReject_soft` |
| M71 implicit cues without the claim | `checkTreatmentI false` uses the widened cue on a soft row | `implicitReject_no_claim` |

Diagonal guarded as before (the count guard: see §6.3).

## 6. Batch 2 (continued): New Jersey successor courts (DESIGN9 §6, D9-6; data only)

Stated 02:50, before any code of it. No change to the checker or the runner: the rule is carried by the data rows
`round9/nj/adoption.tsv` / `round9/nj/succession.tsv` (two adoption rows `1099 ← 1095`, `1222 ← 1206`, upTo 19480914,
all, binding, S; retags). The Lean adds two general theorems about the existing `Spec.canChangeStatus`, a New Jersey
fixture of `#guard`s in `Examples.lean`, and two mutants.

### 6.0 Readings

| # | point | what the Lean does |
|---|---|---|
| L9-21 | the fixture | a second environment `njEnv` in `Examples.lean` with the six New Jersey courts as `courts2.tsv` has them (system 30: E&A 1094 L to 19480914; old Supreme Court 1095 A to 19480914; Supreme Court 1096 L from 19480915; Appellate Division 1099 A from 19480915; Court of Chancery 1206 S to 19480914; Chancery Division 1222 S), plus a Law Division as a synthetic trial court of system 30 (no court id in the data: id 10011), the succession rows of `round9/nj/succession.tsv`, the three adoption rows (`1096 ← 1094`, `1099 ← 1095`, `1222 ← 1206`), and the system rule `30 horizontal none` |
| L9-22 | "no earlier branch applies" (`adoptedSameTier_power`) | stated as hypotheses on the epochs: the acting court is not the Supreme Court of the United States (`B.scotus = false`), not a court of last resort (`B.tier ≠ .last`), not the target's court, and not above the target in the same system (`¬(B.system = X.system ∧ X.tier.rank < B.tier.rank)`) |
| L9-23 | `adopted_lowerTier_noPower` | holds for any pair, adoption or not: a court ranked below the target's dated tier (and not the Supreme Court of the United States) never has power. The hypotheses are only those it needs |
| L9-24 | mutant fixture | `mutAdoptAnyTier` is shown by an environment with the extra adoption row `1099 ← 1094` (Appellate Division over the E&A), as nj9's request says |

### 6.1 Theorems (`Spec/AuthorityThms.lean`, namespace `CaseLaw2.Spec`)

```lean
/-- An adopter of the target's dated tier or above, not of last resort, holds the adopted decision as its own: under
a soft or no horizontal rule it has power (successor of like jurisdiction, *In re Estate of Johnson*). -/
theorem adoptedSameTier_power (L : Lookups) (b x : Decision) (dom? : Option Domain) (B X : CourtEpoch)
    (hB : L.epochAt b.court b.date = some B) (hX : L.epochAt x.court x.date = some X) (hd : x.date ≤ b.date)
    (hs : B.scotus = false) (hl : B.tier ≠ .last) (hc : B.court ≠ X.court)
    (hh : ¬(B.system = X.system ∧ X.tier.rank < B.tier.rank))
    (ha : (adoptionsOf L x).any (·.adopter == b.court) = true) (ht : X.tier.rank ≤ B.tier.rank)
    (hr : L.rules.horizontal B.court B.system x.date = some .none ∨
      L.rules.horizontal B.court B.system x.date = some .soft) :
    canChangeStatus L b x dom? = some (true, .sameCourtSoft)

/-- A court ranked below the target's dated tier has no power over it (adoption or not), unless it is the Supreme
Court of the United States (the Appellate Division under the Court of Errors and Appeals; Kentucky 1976). -/
theorem adopted_lowerTier_noPower (L : Lookups) (b x : Decision) (dom? : Option Domain) (B X : CourtEpoch)
    (hB : L.epochAt b.court b.date = some B) (hX : L.epochAt x.court x.date = some X) (hs : B.scotus = false)
    (hlow : B.tier.rank < X.tier.rank) :
    (canChangeStatus L b x dom?).map (·.1) = some false
```

### 6.2 Guards (`Examples.lean`, `njL := (ExecEnv.build njEnv).lookups`, `njpw b x := (canChangeStatus njL b x none).map (·.1)`)

`njpw appDiv1962 oldSup1948 = some true`, `njpw appDiv1977 ea1924 = some false`, `njpw chanDiv1949 chancery1937 =
some true`, `njpw lawDiv1964 oldSup1944 = some false`, `njpw sup1993 ea1922 = some true`, `njpw sup1954 oldSup1924 =
some true`; without the two new adoption rows the first and third are `some false` (the round-8 tables).

### 6.3 Mutants (2; `Impl.canChange`)

| mutant | breaks | killed by property |
|---|---|---|
| M72 `mutAdoptAnyTier` | the adoption branch without `X.tier.rank ≤ B.tier.rank` | `adopted_lowerTier_noPower` (App. Div. 1977 over the E&A 1924 with an adoption row `1099 ← 1094`) |
| M73 `mutNoAdoptPower` | the adoption branch removed (`(false, .noPower)`) | `adoptedSameTier_power` (App. Div. 1962 over the old Supreme Court 1948) |

Count guard after batch 2: see §8 (properties9b holds the five §5/§7 properties, the two §6 ones and §8's).

## 8. Batch 2 (continued): judge-form anchor cues under `anchorWide` (DESIGN9 §8, D9-9)

**Order, stated truthfully:** under the 02:50 timeline this section's code and proofs were drafted (02:52–02:55)
before this text was written (02:55); the statements follow DESIGN9 §8 word for word and none was changed after the
build. The round-8 statement `anchorWide_sound` is unchanged (`checkHistory8` is unchanged); the runner uses the new
step `checkHistory8J`.

| # | point | what the Lean does |
|---|---|---|
| L9-25 | the list | cue table key `anchor_wide9` = ["district judge", "magistrate judge", "trial judge"] → Lean `anchorWide9Cues`, Python `ANCHOR_WIDE9`; `anchor_wide` is unchanged (DESIGN9 §8's split) |
| L9-26 | the step | `checkHistory8J := checkHistory8With anchorCueOk9 bridgeFail`, `anchorCueOk9 h a := if h.anchorWide then (anchor ++ anchor_wide ++ anchor_wide9) any-substring on the normalised lower-cased anchor quote else anchorHasCue a`; runner: `checkHistory9J zs := zoneThen zs c [] (checkHistory8J …)` |

```lean
theorem anchorWide9_no_claim (c : Input) (a? : Option Anchor) (b? : Option Bridge) (h : HClaims) (zs : List Zone)
    (hw : h.anchorWide = false) :
    checkHistory8J c a? b? h = checkHistory8 c a? b? h ∧ checkHistory9J zs c a? b? h = checkHistory9 zs c a? b? h
theorem anchorWide9_sound (c : Input) (a : Anchor) (h : HClaims) (hw : h.anchorWide = true)
    (hadm : (checkHistory8J c (some a) none h).admitted = true) :
    (anchorCues ++ anchorWideCues ++ anchorWide9Cues).any (hasSub (norm a.quote).toLower) = true ∧
      anchorQuoteOk c a = true ∧ anchorDisqualified a = false ∧ anchorResolves c a = true ∧ anchorPartOk a = true ∧
      (checkClaimedWith orderHeadOk claimCueOk h { c with selfText := true }).admitted = true
```

Mutant M74 (new `Impl` field `checkHistory8J`): the judge strings accepted without the claim, killed by
`anchorWide9_no_claim` (an anchor "(Smith, District Judge)" passes with the claim and fails `anchorNoCue` without).
Final count guard of batch 2: `(27, 8, 6, 13, 10, 3, 8, 74)` (properties9b: 3 far, 2 implicit, 2 New Jersey, 1 §8).

## 9. Part zones (§4): tables, loader, runner (as built)

- Every statement of §1.2 (and the six helpers) proved exactly as written; the definitions are §1.1's, spelled as
  there. No cue-table change.
- **`Data.lean`**: `ZoneRow` (5 fields; node and offsets natural numbers, else a bad row of the file) from the
  optional `part_zone.tsv` (`Tables.zones`; a `Problems` entry only when the file exists).
- **`Run.lean`**: `zoneTable` groups the lines by node and keeps `Cert.nodeZones` of each (counting poisoned nodes);
  `ZoneTab.summary` writes, only when the file has a line, `zone_nodes`, `zone_lines`, `zone_bad_nodes`,
  `zone_bad_rows`, `zone_checked_rows`, `zone_failed_rows`, `zone_missing_rows` (D9-4 names; checked / missing count
  the rows whose full-rule-set round-8 verdict admits, i.e. the rows that reach the test). History: the text owner is
  the target for a selfText row, else `by` (none for `by = -1`); the verdict is `Cert.checkHistory9`. Treatments: the
  text owner is `textNode` (W for a witness row, else `by`); `Cert.zoneThen` after `fin` (doctrine ambiguity) for a
  doctrine row, `Cert.checkRecognised9` for a witness row, `Cert.checkTreatment9` otherwise; the same wrappers on the
  text check (`textOk`, events), `recOk` (recognition), and the plain check of `treatOkText` (`laterCourtSays:`
  evidence). The doctrine-uniqueness table is unchanged (D9-4 (2)).
- **Scripts** (new): `wsl/r9_lean.sh` (sync + build), `wsl/r9_zone_fixture.sh`, `wsl/r9_r8fixture.sh` /
  `wsl/r9_r7fixture.sh` (copies of the round-8/7 fixture scripts that write nothing back into round8/ or round7/),
  `wsl/r9_final.sh`; `wsl/lock_reason.txt` holds the round-9 reason (round 8's in `round9/pre/wsl/`).

## 10. Results (§4)

- Build green; runner sha1 `65bbc36dc26635cdd27922b7a997cbb60500d148` (`~/caselaw2/r9_bin/caselaw2_lean9`; the
  §4-only copy is kept as `caselaw2_lean9_s4`).
- Audit: before the lock 255 theorems, 10 changes all `new`, 0 problems; locked 02:39; after the lock 255 theorems,
  0 changes, 0 problems. Against `round9/pre/audit/statements.lock`: **245 → 255, 0 removed, 0 changed, 10 added**.
- Mutants 63 → 66 (properties 64 → 67; 3×3 diagonal; no new mutant caught by an earlier property, no earlier mutant by
  a new one; count guard `(27, 8, 6, 13, 10, 3, 66)`); `#guard`s Examples 365 → 397, Mutants 14 → 17.
- Fixture `round9/fixtures/partzone` (`make_partzone_fixture.py`, `wsl/r9_zone_fixture.sh`): j (from the round-7
  joined fixture): 4 refusals (a joined quote in a dissent zone, an okUnverifiedBy row in a concurrence zone, a quote
  across two touching majority zones, head matter in a majority zone); kept: targetUnresolved, partNotMajority,
  doctrineAmbiguous; dropped nodes: overlapping, empty zone, unknown part `Majority`; 3 bad lines that poison
  nothing; an unknown node; counters as expected; b (from the round-8 bridge fixture): the bridge text W all dissent
  and an anchor in a dissent zone are not checked, a bridged quote across a boundary is refused. Without
  `part_zone.tsv`, and with an empty one, every output file equals the earlier fixture's stored output.
- Round-8 and round-7 fixtures green; regressions a, a2, b, c byte-identical (see the log).
- Real data (`round9/stage/lean9_z` = v8e + calpart9's `zone_delta`, 582,968 zones, 208,557 nodes): exactly 223 rows
  `ok → partZone` (220 history, 3 treatments, both rule sets), the same 223 ids as calpart9's `refused.tsv`; every
  other verdict as v8e; 0 bad nodes, 0 bad rows, 220,452 checked, 0 missing.
- Log: `round9/agents/lean9/r9_final.log`.

## 11. Batch 2 as built (§5, §6, §7, §8)

- Every statement of §5.2 (as revised 02:46 for D9-7), §6.1 and §8 proved exactly as written; no `sorry`, no new
  axiom, no `native_decide`. Helpers locked as additions: `farWindow_some`, `farKeyOk_spec`, `findSome_farRel_none`,
  `checkJoinedFar_eq`, `checkJoinedFarWith_rel`, `farRel_none`.
- Built first in a staging copy (`round9/agents/lean9/b2/tree`, assembled by `assemble_batch2.py` from the pieces,
  `patch_batch2.py` (cue table + generator), `patch_batch2_run.py` (runner); WSL copy `~/caselaw2/b2`,
  `wsl/r9_b2build.sh`, `wsl/r9_b2runner.sh`) while §4's gates ran, then copied into the tree (`apply_batch2.sh`).
- **Cue table** (appended; the JSON text up to its last line, `CueTable.lean` up to `end CaseLaw2.Cert` and
  `reader/cue_table.py` are byte-identical prefixes): `_note_round9`, `joined_far_max` 1200, `implicit_reject` (18),
  `anchor_wide9` (3) → Lean `joinedFarMax`, `implicitRejectCues`, `anchorWide9Cues`; Python `JOINED_FAR_MAX`,
  `IMPLICIT_REJECT`, `ANCHOR_WIDE9`. `gen_cues.py --skip-ref` (ref/ is ref9's).
- **Runner**: `treatment_class.tsv` claims `joinedFar` and `implicitReject` accepted (as `doctrine`: the first line
  for an id); `lensF` = the index's key lengths, only when a row claims `joinedFar`; the treatment step:
  doctrine → implicitReject (`Cert.checkTreatmentI true`) → witness → `Cert.checkTreatmentF claimF lensF`, each under
  §4's zone test; the history step is `Cert.checkHistory9J` (§8). Without the claims every step is §4's
  (`joinedFar_no_claim`, `implicitReject_no_claim`, `anchorWide9_no_claim`).
- **§6** adds no checker or runner code: `Spec/AuthorityThms.lean` (the two theorems), `Examples.lean` (`njEnvWith`,
  `njL`, `njL8`, `njLx`, 11 `#guard`s), `Mutants.lean` (`canChangeAdopt`, M72, M73).
- Fixture `round9/fixtures/farimplicit` (`make_farimplicit_fixture.py`, `wsl/r9_farimplicit_fixture.sh`): 11
  treatments rows (far ok, far past another citation, far beyond 1,200, far without a covering window, near under the
  claim, far without the claim; implicit ok, on an overruled row, questioned with its own cue, a dissent, no claim);
  without the claim lines the round-8 verdicts; the soft target stays good, findings `atRisk soft:<kind>` only.

## 12. Results (batch 2)

- Tree build 03:05 (reusing the staging build products), runner sha1 `22bab5cdc71237876c807a8c9354cad7a47c6e1f`
  (= the staging runner: the build is deterministic); `~/caselaw2/r9_bin/caselaw2_lean9` (§4's `65bbc36d…` kept as
  `caselaw2_lean9_s4`).
- Audit: before the lock 272 theorems, 17 changes all `new`, 0 problems; locked 03:06; after the lock 272 theorems,
  0 changes, 0 problems. Round 9 in all: **245 → 272, 0 removed, 0 changed, 27 added**.
- Mutants 66 → 74 (properties 67 → 75; 8×8 diagonal; no new mutant caught by an earlier property, no earlier mutant
  by a new one; count guard `(27, 8, 6, 13, 10, 3, 8, 74)`); `#guard`s Examples 397 → 441, Mutants 17 → 20.
- Fixtures (r9_final2): batch-2 fixture `round9/fixtures/farimplicit` green (with the claims, and without them = the
  round-8 verdicts; the soft target stays good); zone fixture, round-8 and round-7 fixtures green.
- Regressions (r9_final2, parallel, PAR=4): a and b byte-identical; v8e reproduced byte for byte with the batch-2
  binary (round9/out/lean9_base, RUN.txt sha1 22bab5cd). a2 and c were cut off at 03:21 when C: filled and the WSL
  filesystem went read-only (NOTES 03:21, QUESTIONS Q6); rerun after the WSL restart (r9_final2_rest.sh, 03:25-03:31):
  every file byte-identical (a2 certs 68f6fb621957, status 96888c8b4381; c certs 0c9ef2f16764).
- Batch-2 LEAN_READY written after all gates passed (time in round9/LEAN_READY; copy agents/lean9/LEAN_READY_b2).
- §6 on real data needs no Lean change: the lead's `round9/out/nj_test` (v8e + `round9/nj` tables, frozen binary)
  changes exactly nj9's three rows.
