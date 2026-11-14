# Round 8, Lean: bridge evidence for history rows (§4), claim-gated wide anchor cues (§5)

Contract: `DESIGN8.md` §4 (D8-3) and §5 (D8-5). Written by the agent `lean8`, 14 Nov 2026 (started 00:47).
Sections 0 and 1 were written **before** any code or proof (00:57–01:02; step 5b `bridgeChain`, D8-9, added to
§1 at 01:02, before its code): the statements are the target; a statement
that proves false is refuted and reported, never weakened silently. Sections 2–4 are written after the build.

Backup of everything changed: `round8/pre/` (`CaseLaw2/`, `CaseLaw2.lean`, `tools_caselaw2/` (cue table, generator,
generated `cue_table.py` copies), `audit/statements.lock`, `STATEMENTS.log`, `run_lean.sh`, `runner/` sources, `wsl/`,
`ref/` and `fuzz/` copies; `SHA1SUMS.txt`, 90 files).

## 0. Readings of points DESIGN8 §4–5 leaves open

None of these changes an effect the design states; L8-4, L8-5 and L8-6 define what §4 calls "the first such" and
"the first compact citation" (the lead should check that `ref8` reads them the same way).

| # | point | what the Lean does |
|---|---|---|
| L8-1 | coordinates of p1, p2 and O's position | all three are character positions in the normalised, lower-cased bridge quote `q = (norm b_quote).toLower`. A citation is matched on the quote's alphanumeric characters (`alnumPos q`: each alphanumeric character with its position in `q`; the string of these characters is `compact b_quote`); its position is the position in `q` of its first character. Positions of alphanumeric characters keep their order, so "p2 > p1" means the same in compact or in `q` coordinates |
| L8-2 | "a compact citation" | a key of the supplied citation index (`cite_index.tsv`, after round 4's rule: a key the data gives two nodes is left out and resolves to nothing): L consecutive alphanumeric characters of `q` (L ≥ 1) whose string is a key. The index is sparse (only the citations the stage supplies), so a citation that is not a key is not seen by step 4 or step 6 |
| L8-3 | the key lengths | the runner passes the distinct key lengths of the index, longest first (`Bridge.lens`); the soundness statements hold for any list |
| L8-4 | step 4, p1 "the first such" | the position of the first alphanumeric character (in order) at which some key of some length maps to X (no boundary test, as `resolves` / `anchorResolves` read `cite:` evidence: "the compact quote contains") |
| L8-5 | step 5, p2 | the first position `i > p1` of `q` at which a phrase of `bridge_cue` for the row's kind begins (plain prefix test on `q.drop i`; an empty phrase never matches); a kind without a list fails `bridgeCue` |
| L8-6 | step 6, "after p2, the first compact citation" | the first alphanumeric character at a position `> p2` at which some key begins; at that character the citation is the **longest** key that begins there (lengths longest first, L8-3: "577 U.S. 1001" is read as 577us1001, not as the key 577us100 of another case). It must map to O |
| L8-7 | O, date(O), date(W) | O = the row's acting node (`by`); dates from `decisions2.tsv` (0 = unknown, fails `bridgeDate`); a row with no acting node has date(O) = 0 and fails `bridgeDate` |
| L8-8 | W's text | the windows supplied in `cert_text.tsv` (and `window_sha.tsv`) under W's own `text_sha` (`decisions2.tsv`); W without a hash has no window and fails `bridgeMismatch`. The bridge nodes are added to the nodes whose hash is loaded (`certNodes`; dates are loaded for every node anyway) |
| L8-9 | no citation index | `bridgeTarget` fails (step 4 needs the index) |
| L8-10 | a row with both a bridge line and an anchor line | the bridge decides; the anchor line is ignored and counted (`bridge_anchor_ignored`); step 7 is the row's own (not anchored) check under its claims. `anchored_admitted` / `anchored_rejected` count only rows checked anchored |
| L8-11 | step 7 "the row's own check (plain, or orderHead with its claim)" | `checkClaimedWith orderHeadOk claimCueOk h { c with selfText := true }`: the round-7 history check under all the row's claims (orderHead, setAside) |
| L8-12 | malformed bridge line | 6 fields, offsets and `w_node` numeric; else not a line, counted `bad_rows history_bridge.tsv n` (the loader's spelling of DESIGN's `bad_rows history_bridge n`) |
| L8-13 | §5 `anchorWide` on a bridged row or a row with no anchor line | no effect; counted `hclaim_anchorwide_unused` (with `hclaim_anchorwide`, the rows carrying the claim), written only when an `anchorWide` line exists, so a round-7 `history_claim.tsv` writes no new counter |
| L8-14 | §5 cue test | `(anchor ++ anchor_wide).any` substring on `(norm a_quote).toLower`, exactly as `anchorHasCue` |
| L8-16 | step 5b (D8-9) "the end of X's citation (p1 + its length)" | the key at p1 that maps to X is the longest such (lengths longest first); its end is the position in `q` after its last alphanumeric character (`keyEnd`). "No index key starts" between it and p2: no alphanumeric character at a position `e ≤ p < p2` begins a key of any length (any node). Keys that begin inside X's own citation are not tested |
| L8-15 | generated `tools/caselaw2/ref/cue_table.py` | `ref/` has one writer (`ref8`): the generator gets `--skip-ref`; `lean8` regenerates the Lean file and `reader/cue_table.py` only (the new keys are appended; `ref8` reads them from the JSON or runs the generator itself) |

Observation for the lead (01:00; ruled D8-9 at 01:01: step 5b `bridgeChain` added, see L8-16): §4 admitted a chain "X, 123 F.3d 456, aff'd, 200 F.3d 9, cert. denied,
577 U.S. 1001" as a cert denial of X, although O acted on the affirming decision 200 F.3d 9 (the first `cert. denied`
after X's citation is followed by O's citation). A rule "no other key between X's citation and p2" would close it.

## 1. Definitions and theorems (stated first)

Checker definitions in `LegalProofs/CaseLaw2/Certificate.lean` (namespace `CaseLaw2.Cert`, a new round-8 section after
round 7's); cue lists in the generated `CueTable.lean`.

### 1.1 Cue table (`tools/caselaw2/cues/cue_table.json`; the generator appends)

| JSON key | Lean | Python |
|---|---|---|
| `bridge_cue` (kind → list; DESIGN8 §4 step 5) | `bridgeCues : HKind → List String` (`[]` for a kind not in the map) | `BRIDGE_CUE` (dict) |
| `bridge_max_len` (600) | `bridgeMaxLen : Nat` | `BRIDGE_MAX_LEN` |
| `anchor_wide` (16 phrases, §5) | `anchorWideCues : List String` | `ANCHOR_WIDE` |

### 1.2 Definitions

```lean
-- reasons appended to `Reason`
  | bridgeMismatch | bridgeDate | bridgeClause | bridgeTarget | bridgeCue | bridgeActor | bridgeChain
-- HClaims gains `anchorWide : Bool := false` (round 7's functions ignore it)

def firstSuffix (p : List α → Bool) : List α → Option (List α)        -- the first (longest) suffix with p
def alnumPos : List Char → Nat → List (Char × Nat)                   -- alphanumeric characters with positions
structure Bridge where
  w : Nat; wSha : String; windows : List Window; start : Nat; stop : Nat; quote : String
  wDate : Nat := 0; oDate : Nat := 0; actor : Nat := 0; lens : List Nat := []
def Bridge.input (b : Bridge) (c : Input) : Input :=
  { c with textSha := b.wSha, shas := [b.wSha], windows := b.windows, start := b.start, stop := b.stop, quote := b.quote }
def bridgeQuoteOk (c : Input) (b : Bridge) : Bool := decide (b.stop - b.start ≤ bridgeMaxLen) && quoteOk (b.input c)
def bridgeDateOk (b : Bridge) : Bool := decide (0 < b.oDate) && decide (0 < b.wDate) && decide (b.oDate ≤ b.wDate)
def bridgeClauseOk (b : Bridge) : Bool := !hasSub (norm b.quote) ";"
def bridgeText (b : Bridge) : List Char := (norm b.quote).toLower.toList
def bridgeAlnum (b : Bridge) : List (Char × Nat) := alnumPos (bridgeText b) 0
def headPos (s : List (Char × Nat)) : Option Nat := s.head?.map (·.2)
/-- the key of the first `L` characters of `s` through the index -/
def citeOf (m : Std.HashMap String Nat) (s : List (Char × Nat)) (L : Nat) : Option Nat :=
  if 0 < L ∧ (s.take L).length = L then m.get? (String.ofList ((s.take L).map (·.1))) else none
def citeFirst (m) (lens : List Nat) (s) : Option Nat := lens.findSome? (citeOf m s)   -- the longest key (L8-6)
def bridgeP1 (c : Input) (b : Bridge) : Option Nat :=                                  -- step 4 (L8-4)
  match c.citeIndex with
  | none => none
  | some m => (firstSuffix (fun s => b.lens.any (fun L => citeOf m s L == some c.target)) (bridgeAlnum b)).bind headPos
def keyEnd (s : List (Char × Nat)) (L : Nat) : Nat := ((s.take L).getLast?.map (·.2 + 1)).getD 0
def bridgeXEnd (c : Input) (b : Bridge) : Option Nat :=                                -- step 5b: end of X's citation
  match c.citeIndex with
  | none => none
  | some m => match firstSuffix (… the step-4 test …) (bridgeAlnum b) with
    | none => none
    | some s => (b.lens.find? (fun L => citeOf m s L == some c.target)).map (keyEnd s)
def noKeyBetween (c : Input) (b : Bridge) (e p2 : Nat) : Bool :=                      -- no key begins in [e, p2)
  match c.citeIndex with
  | none => false
  | some m => (bridgeAlnum b).tails.all (fun s => match headPos s with
      | some p => !(decide (e ≤ p) && decide (p < p2)) || (citeFirst m b.lens s).isNone
      | none => true)
def bridgeChainOk (c : Input) (b : Bridge) (p2 : Nat) : Bool :=
  match bridgeXEnd c b with | some e => noKeyBetween c b e p2 | none => false
def bridgeCue : Kind → List String | .hist k => bridgeCues k | .treat _ => []
def cueHere (k : Kind) (q : List Char) : Bool := (bridgeCue k).any (fun ph => !ph.isEmpty && ph.toList.isPrefixOf q)
def firstCue (k : Kind) (p1 : Nat) : List Char → Nat → Option Nat                      -- first i > p1 with a cue
def bridgeP2 (c : Input) (b : Bridge) (p1 : Nat) : Option Nat := firstCue c.kind p1 (bridgeText b) 0   -- step 5
def actorCiteWhere (c : Input) (b : Bridge) (ok : Nat → Bool) : Option (Nat × Nat)    -- first key at an ok position
def bridgeActorCite (c : Input) (b : Bridge) (p2 : Nat) : Option (Nat × Nat) :=       -- step 6: (position, node)
  actorCiteWhere c b (fun p => decide (p2 < p))
def bridgeFailWith (qOk) (dateOk clauseOk) (p1) (p2) (chain) (actor) (c : Input) (b : Bridge) : Option Reason :=
  if !qOk c b then some .bridgeMismatch else if !dateOk b then some .bridgeDate
  else if !clauseOk b then some .bridgeClause
  else match p1 c b with
    | none => some .bridgeTarget
    | some q1 => match p2 c b q1 with
      | none => some .bridgeCue
      | some q2 => if !chain c b q2 then some .bridgeChain
        else if (actor c b q2).map (·.2) == some b.actor then none else some .bridgeActor
def bridgeFail := bridgeFailWith bridgeQuoteOk bridgeDateOk bridgeClauseOk bridgeP1 bridgeP2 bridgeChainOk bridgeActorCite
def bridgeThen (r : Option Reason) (fin : Input → Result) (c : Input) : Result :=
  match r with | some r => .fail r | none => fin { c with selfText := true }
/-- **The bridge checker** (DESIGN8 §4). -/
def checkBridge (c : Input) (b : Bridge) (h : HClaims) : Result :=
  bridgeThen (bridgeFail c b) (checkClaimedWith orderHeadOk claimCueOk h) c

-- §5
def anchorWideCue (a : Anchor) : Bool := (anchorCues ++ anchorWideCues).any (hasSub (norm a.quote).toLower)
def anchorCueOk (h : HClaims) (a : Anchor) : Bool := if h.anchorWide then anchorWideCue a else anchorHasCue a
def anchoredBy (cue : Anchor → Bool) (fin : Input → Result) (c : Input) (a : Anchor) : Result  -- anchoredThen, cue as parameter
/-- **The runner's history step in round 8.** -/
def checkHistory8With (acue : HClaims → Anchor → Bool) (bf : Input → Bridge → Option Reason)
    (c : Input) (a? : Option Anchor) (b? : Option Bridge) (h : HClaims) : Result :=
  match b? with
  | some b => bridgeThen (bf c b) (checkClaimedWith orderHeadOk claimCueOk h) c
  | none => match a? with
    | some a => anchoredBy (acue h) (checkClaimedWith orderHeadOk claimCueOk h) c a
    | none => checkClaimedWith orderHeadOk claimCueOk h c
def checkHistory8 := checkHistory8With anchorCueOk bridgeFail
```

### 1.3 Theorems (6 stated; step 5b added to `bridge_admitted_iff`, `bridge_sound`, `bridge_order` at 01:02)

```lean
/-- Admission is exactly steps 1–6 and the row's own check. -/
theorem bridge_admitted_iff (c : Input) (b : Bridge) (h : HClaims) :
    (checkBridge c b h).admitted = true ↔
      (bridgeQuoteOk c b = true ∧ bridgeDateOk b = true ∧ bridgeClauseOk b = true ∧
        (∃ p1 p2, bridgeP1 c b = some p1 ∧ bridgeP2 c b p1 = some p2 ∧ bridgeChainOk c b p2 = true ∧
          (bridgeActorCite c b p2).map (·.2) = some b.actor) ∧
        (checkClaimedWith orderHeadOk claimCueOk h { c with selfText := true }).admitted = true)

/-- **Bridge soundness**: 1. W's quote at its offset in a usable window of W's text, non-empty, at most
`bridgeMaxLen` (600); 2. date(O) and date(W) known, date(O) ≤ date(W); 3. no ";"; 4. a key at p1 that the index maps
to X, ending at e; 5. a bridge cue of the row's kind at p2 > p1; 5b. no key begins at a position in [e, p2); 6. a key at
pO > p2 that the index maps to O; 7. the row's own
check with the target evidence taken as given admits, and is the verdict. -/
theorem bridge_sound (c : Input) (b : Bridge) (h : HClaims) (hadm : (checkBridge c b h).admitted = true) :
    (b.quote ≠ "" ∧ b.start < b.stop ∧ b.stop - b.start ≤ bridgeMaxLen ∧
      ∃ w, coveringWindow (b.input c) = some w ∧ w ∈ b.windows ∧ usable (b.input c) w = true ∧
        quoteAt (b.input c) w = true) ∧
    (0 < b.oDate ∧ 0 < b.wDate ∧ b.oDate ≤ b.wDate) ∧
    hasSub (norm b.quote) ";" = false ∧
    (∃ m, c.citeIndex = some m ∧ ∃ p1 e p2 pO,
      (∃ s, s <:+ bridgeAlnum b ∧ headPos s = some p1 ∧ ∃ L ∈ b.lens, citeOf m s L = some c.target ∧ keyEnd s L = e) ∧
      p1 < p2 ∧ cueHere c.kind ((bridgeText b).drop p2) = true ∧
      (∀ s, s <:+ bridgeAlnum b → ∀ p, headPos s = some p → e ≤ p → p < p2 → ∀ L ∈ b.lens, citeOf m s L = none) ∧
      p2 < pO ∧ (∃ s, s <:+ bridgeAlnum b ∧ headPos s = some pO ∧ ∃ L ∈ b.lens, citeOf m s L = some b.actor)) ∧
    (checkClaimedWith orderHeadOk claimCueOk h { c with selfText := true }).admitted = true ∧
      checkBridge c b h = checkClaimedWith orderHeadOk claimCueOk h { c with selfText := true }

/-- **Order**: X's citation, then the cue (with no key between X's citation and the cue), then O's citation. -/
theorem bridge_order (c : Input) (b : Bridge) (h : HClaims) (hadm : (checkBridge c b h).admitted = true) :
    ∃ p1 e p2 pO, bridgeP1 c b = some p1 ∧ bridgeXEnd c b = some e ∧ bridgeP2 c b p1 = some p2 ∧
      bridgeActorCite c b p2 = some (pO, b.actor) ∧ p1 < p2 ∧ p2 < pO ∧ noKeyBetween c b e p2 = true

/-- **No bridge line, no claim `anchorWide`: no change** (the round-7 history step). -/
theorem no_bridge_no_change (c : Input) (a? : Option Anchor) (h : HClaims) (hw : h.anchorWide = false) :
    checkHistory8 c a? none h = checkHistory7 c a? h

/-- §5: without the claim the anchor-cue test and the anchored check are round 7's. -/
theorem anchorWide_no_claim (c : Input) (a : Anchor) (h : HClaims) (hw : h.anchorWide = false) :
    anchorCueOk h a = anchorHasCue a ∧ checkHistory8 c (some a) none h = checkHistory7 c (some a) h

/-- §5: an admitted anchored row with the claim has a cue of `anchor ++ anchor_wide`, and every other anchored check
holds. -/
theorem anchorWide_sound (c : Input) (a : Anchor) (h : HClaims) (hw : h.anchorWide = true)
    (hadm : (checkHistory8 c (some a) none h).admitted = true) :
    (anchorCues ++ anchorWideCues).any (hasSub (norm a.quote).toLower) = true ∧ anchorQuoteOk c a = true ∧
      anchorDisqualified a = false ∧ anchorResolves c a = true ∧ anchorPartOk a = true ∧
      (checkClaimedWith orderHeadOk claimCueOk h { c with selfText := true }).admitted = true
```

Helpers expected (locked as additions): `firstSuffix_some`, `firstCue_some`, `bridgeP1_some`, `bridgeP2_some`,
`bridgeActorCite_some`, `bridgeFail_none_iff`, `checkHistory8_bridge` (`checkHistory8 c a? (some b) h =
checkBridge c b h`), `bridgeFail_authority` (the bridge steps do not read the acting court's power).

### 1.4 Mutants (8; `Mutants.lean`, properties `properties8`)

New `Impl` field `checkHistory8` (default the real function). Bridge mutants are `Cert.checkHistory8With
Cert.anchorCueOk (Cert.bridgeFailWith …)` with one test replaced.

| mutant | breaks | killed by property |
|---|---|---|
| M54 bridge without the length bound | `qOk := quoteOk (b.input c)` | `bridge_sound: length` |
| M55 bridge without the ";" test | `clauseOk := true` | `bridge_sound: one clause` |
| M56 O's citation before X's | O's citation searched anywhere in the quote (`actorCiteWhere c b (fun _ => true)`) | `bridge_order` |
| M57 bridge without the cue | `p2 := p1` (no cue sought) | `bridge_sound: cue` |
| M58 a citation of another node | step 6 accepts the first citation after p2 whatever node it maps to | `bridge_sound: O's citation` |
| M59 bridge without the date test | `dateOk := true` | `bridge_sound: date` |
| M61 bridge without the chain test (D8-9) | `chain := true` | `bridge_sound: no citation between X's and the cue` |
| M60 wide anchor cues without the claim | `acue := fun _ a => anchorWideCue a` | `anchorWide_no_claim` |

(M61 is listed after M60 in `Mutants.lean`.) Guards: the 8 new mutants and 8 new properties form a diagonal; no new mutant is caught by an earlier property and
no earlier mutant by a new property; the count guard becomes `(27, 8, 6, 13, 8, 61)`.

### 1.5 §6 old circuits (D8-12), stated 01:13 before its code

Readings: **L8-17** "federal court of appeals": acting epoch `system = 0` and tier `appellate`; "federal district (or
bankruptcy) court": target epoch `system = 0` and tier `trial` (district) or `special` (the bankruptcy courts are
tier S in `courts2.tsv`); circuits are the epochs' (rule set's tables), date(B) from `decisions2.tsv` (0 fails).
**L8-18** the history authority is the runner's `Exec.histPower` (round 4; not `canChangeStatus`, which treatments
use); the claim changes only a `some false` of it into `some true`; `none` (an unknown epoch) stays `none`.
**L8-19** counters `hclaim_oldcircuit` (rows with the claim) and `hclaim_oldcircuit_used` (rows whose authority the
rule turned true under the full rule set), written only when an `oldCircuit` line exists.

Cue table: `old_circuit` = `[[5, 11, 19811001], [8, 10, 19290301]]` → Lean `oldCircuitRules : List (Nat × Nat × Nat)`,
Python `OLD_CIRCUIT`.

```lean
-- Exec/Verdicts.lean (namespace CaseLaw2.Exec)
def oldCircuitOk (B X : CourtEpoch) (bDate : Nat) : Bool :=
  B.system == 0 && B.tier == .appellate && X.system == 0 && (X.tier == .trial || X.tier == .special) &&
    Cert.oldCircuitRules.any (fun t => B.circuit == t.1 && X.circuit == t.2.1 && decide (0 < bDate) && decide (bDate < t.2.2))
def histPower8With (ok : CourtEpoch → CourtEpoch → Nat → Bool) (L : Lookups) (b x : Decision) (claim : Bool) : Option Bool :=
  match histPower L b x with
  | some false =>
    if claim && (match L.epochAt b.court b.date, L.epochAt x.court x.date with
      | some B, some X => ok B X b.date | _, _ => false) then some true else some false
  | r => r
def histPower8 := histPower8With oldCircuitOk      -- the runner's history authority (claim = the row has `oldCircuit`)

theorem oldCircuit_no_claim (L : Lookups) (b x : Decision) : histPower8 L b x false = histPower L b x
/-- an admitted claimed row that the round-7 authority refuses satisfies one listed triple with the date premise -/
theorem oldCircuit_sound (L : Lookups) (b x : Decision) (h : histPower8 L b x true = some true)
    (hr : histPower L b x ≠ some true) :
    histPower L b x = some false ∧ ∃ B X, L.epochAt b.court b.date = some B ∧ L.epochAt x.court x.date = some X ∧
      B.system = 0 ∧ B.tier = .appellate ∧ X.system = 0 ∧ (X.tier = .trial ∨ X.tier = .special) ∧
      ∃ t ∈ Cert.oldCircuitRules, B.circuit = t.1 ∧ X.circuit = t.2.1 ∧ 0 < b.date ∧ b.date < t.2.2
```

Mutants (new `Impl` field `histPower`, default `Exec.histPower8`): **M62** old circuit without the date test
(`histPower8With (fun B X _ => oldCircuitOk B X 1)`), killed by `oldCircuit_sound: date`; **M63** the old-circuit
power on a treatments row (`canChange` = `canChangeStatus` with a `false` turned `true` when `oldCircuitOk`), killed
by `oldCircuit: history rows only`. The count guard becomes `(27, 8, 6, 13, 10, 63)`.

### 1.6 As built (differences in spelling only; every statement of 1.3 and 1.5 proved exactly as written)

- `xHere m c b s` names step 4's suffix test (`bridgeP1` and `bridgeXEnd` share it, so p1 and e come from the same
  suffix); `noKeyBetween` walks the suffixes with `allSuffix` (Lean 4.35 core has no `List.tails`).
- `bridge_admitted_iff` and `bridgeFail_none_iff` carry step 5b as `bridgeChainOk c b p2 = true` inside the
  existential (stated so at 01:02).
- The M63 property (`oldCircuit: history rows only`) tests that `canChange` never returns `some (true, .higherCourt)`
  for the CA5-1975 / N.D. Ga. pair: the round-4 mutant M15 ("no power check") turns every refusal into power under
  its own rule id, so a property on the truth value alone would also be M15's and break the diagonal.
- Helpers locked as additions (17): `firstSuffix_some`, `allSuffix_spec`, `firstCue_some`, `bridgeP1_some`,
  `bridgeP2_some`, `bridgeX_some`, `noKeyBetween_spec`, `bridgeChainOk_some`, `actorCiteWhere_some`,
  `bridgeActorCite_some`, `bridgeFail_none_iff`, `checkBridge_admitted`, `quoteOk_window`, `citeOf_key`,
  `bridgeFail_authority`, `checkHistory8_bridge`, `Exec.histPower8_keeps`.

## 2. Tables, loader, runner

- **Cue table** (`cue_table.json`, `gen_cues.py`): new keys `_note_round8`, `bridge_cue` (kind → list, 5 kinds),
  `bridge_max_len` 600, `anchor_wide` (16), `old_circuit` `[[5, 11, 19811001], [8, 10, 19290301]]`; the JSON text up to
  its last line and `CueTable.lean` up to `end CaseLaw2.Cert`, `reader/cue_table.py` in full are byte-identical
  prefixes of the new files. Lean names `anchorWideCues`, `bridgeCues`, `bridgeMaxLen`, `oldCircuitRules`; Python
  `ANCHOR_WIDE`, `BRIDGE_CUE`, `BRIDGE_MAX_LEN`, `OLD_CIRCUIT`. `gen_cues.py --skip-ref` (used by lean8) leaves
  `tools/caselaw2/ref/cue_table.py` to `ref8` (L8-15); it is unchanged since round 7.
- **`Data.lean`**: `BridgeRow` (6 fields; node and offsets numeric) from the optional `history_bridge.tsv`
  (`Tables.bridges`); a malformed line is counted `bad_rows history_bridge.tsv n`. `HClaimRow.parse` accepts
  `anchorWide` and `oldCircuit` (before round 8 such a line was a bad row; no round-7 table has one). `certNodes` adds
  the bridge nodes W (their hashes; empty without the table).
- **`Exec/Verdicts.lean`**: `oldCircuitOk`, `histPower8With`, `histPower8` (imports `CueTable`).
- **`Run.lean`**:
  - `bridgeTable` (first line per id; `bridge_unknown_ids`, `bridge_duplicates`), `Bridges.summary`, `keyLengths`
    (the distinct key lengths of the index after the ambiguity rule, longest first; computed only when the bridge
    table has a line);
  - `HClaimTab` gains `wide` and `old` (an `anchorWide` / `oldCircuit` line on a history id; repeated →
    `hclaim_duplicates`; on a non-history id → `hclaim_unknown_ids`);
  - each history row: `Cert.checkHistory8 inp anchor? bridge? claims` with `claims.anchorWide` from the table,
    `bridge?` built from the row's bridge line (W's hash from `decisions2.tsv`, W's windows `cert_text.tsv` under that
    hash, date(W), date(O), O = the row's `by`, `lens`), and the input's authority
    `Exec.histPower8 L b x (row has oldCircuit)`; without a bridge line and without the two claims this is round 7's
    `checkHistory7` with `histPower` (`no_bridge_no_change`, `oldCircuit_no_claim`);
  - `summary.tsv`: `bridge_rows`, `bridge_unknown_ids`, `bridge_duplicates`, `bridge_anchor_ignored`,
    `bridge_admitted`, `bridge_rejected` (only when `history_bridge.tsv` has a line); `hclaim_anchorwide`,
    `hclaim_anchorwide_unused` (only when an `anchorWide` line exists); `hclaim_oldcircuit`, `hclaim_oldcircuit_used`
    (only when an `oldCircuit` line exists); `anchored_rejected` no longer counts bridged rows (`- ignored`, 0 without
    the bridge table);
  - `certs.tsv`: new verdicts `bridgeMismatch`, `bridgeDate`, `bridgeClause`, `bridgeTarget`, `bridgeCue`,
    `bridgeChain`, `bridgeActor`.
- WSL scripts (new): `wsl/r8_lean.sh` (sync + build, errors only), `wsl/r8_bridge_fixture.sh` (the fixture),
  `wsl/r8_final.sh` (build, audit check, both fixtures, regressions, v3 reproduction). `wsl/lock_reason.txt` holds
  the round-8 lock reason (round 7's is in `round8/pre/wsl/`).

## 3. Results (14 Nov 2026; Linux Lean 4.35.0 in WSL Ubuntu; log `agents/lean8/r8_final.log`)

- **Build** (`wsl/r8_lean.sh all`; `do.sh build`): green; runner sha1 `3b8d3e4d45fb60a84c5cfb00c2f6729ebc2bfa6b`.
  Every statement of 1.3 and 1.5 proved as written; no `sorry`, no new axiom, no `native_decide`.
- **Audit**: before the lock 245 theorems, 25 changes all `new`, 0 problems; locked (01:20, reason in
  `wsl/lock_reason.txt`, `STATEMENTS.log`); after the lock and rebuild 245 theorems, 0 changes, 0 problems. Against
  `round8/pre/audit/statements.lock`: **220 → 245, 0 removed, 0 changed, 25 added**.
- **Counts**: mutants 53 → 63, properties 54 → 64 (`properties8`, 10; diagonal guarded; no new mutant caught by an
  earlier property, no earlier mutant by a new one); `#guard`s Examples 308 → 365, Mutants 11 → 14; `example`s by
  `rfl` in Mutants 4 → 6. Changed guard (not a theorem): the count guard is `(27, 8, 6, 13, 10, 63)`.
- **Fixture** `round8/fixtures/bridge` (`make_bridge_fixture.py`, `wsl/r8_bridge_fixture.sh`): 20 history rows;
  certs = `expected_certs.tsv`, counters = `expected_summary.tsv`; without the round-8 tables and claims certs =
  `expected_certs_nor8.tsv` and no round-8 counter. One row per verdict: `ok` (plain; anchor line ignored; head matter
  under orderHead), `bridgeMismatch` (offset +2; W without a window; 696-character quote), `bridgeDate`,
  `bridgeClause`, `bridgeTarget`, `bridgeCue` ("aff'd" on a certDenied row), `bridgeChain` ("X, aff'd, Y, cert.
  denied, O"), `bridgeActor` (576 U.S. 900 after the cue; O cited before X), `partNotMajority` (step 7); anchorWide
  `ok` / `anchorNoCue` without the claim / no effect without an anchor line; oldCircuit CA5 1978 over N.D. Ga. `ok`,
  1982 `noAuthority`, no claim `noAuthority`; table rules counted (duplicate, unknown id, malformed bridge line, a
  repeated claim, an oldCircuit claim on a non-history id).
- **Round-7 fixture** (`wsl/r7_joined_fixture.sh`): green.
- **Regressions** (`wsl/r7_lean_base.sh a a2 b c`, new binary): (a) round-6 final2, (a2) the same with empty round-7
  tables, (b) round-5 final, (c) round-4 tables: every output file byte-identical (certs `68f6fb621957`, status
  `96888c8b4381` = FREEZE hashes).
- **v3 reproduction**: stage `round8/stage/lean8_v3` (hard-linked copy of `round8/stage/base`), `r8_run.sh` with
  `R8BIN` = the new binary → `round8/out/lean8_v3`: certs, classes, findings, horty, splits, status, status_lines
  byte-identical to `round7/out/v3`, summary identical but for its timing lines.
- `round8/LEAN_READY` written 01:38.

## 4. Notes for the other agents

- `history_bridge.tsv`: `id, w_node, b_start, b_end, b_quote, src`; W's windows go in `cert_text.tsv` /
  `window_sha.tsv` under **W's** `text_sha` (decisions2), and the index (`cite_index.tsv`) must hold X's and O's
  citations (a key two nodes share resolves to nothing). Every index key is a "citation" for steps 5b and 6: an
  index line for another decision cited between X and the cue makes the row fail `bridgeChain`.
- Position convention = ref8's Q8-4 (D8-13); `String.toLower` and `Char.isAlphanum` are ASCII-only in Lean (as
  `compact` always was): a Python port must lower-case and test alphanumerics in ASCII only, or offsets can drift on
  non-ASCII quotes.
- Claims: `anchorWide` (anchored rows only), `oldCircuit` (history rows only; turns `histPower`'s `some false` into
  `some true` for the two listed triples).
