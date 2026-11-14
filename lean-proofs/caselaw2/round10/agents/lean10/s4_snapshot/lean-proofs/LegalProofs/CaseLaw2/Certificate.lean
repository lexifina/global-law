import LegalProofs.CaseLaw2.Events
import LegalProofs.CaseLaw2.CueTable
import LegalProofs.CaseLaw2.Sha1
import Std.Data.HashMap

/-!
# Certificates: the checker that admits untrusted rows (DESIGN D1 layer 3; prior_art §5.6, §7.1 item 1)

A treatment or history row from the reader is a claim. It is admitted only if its certificate passes every check,
in this order (the first failure is the row's reason code):

1. `shaUnknown`   the certificate's text hash is the treating decision's (treatments) or a party's (history);
2. `noWindow`     a supplied, well-formed window of that text covers the quoted span;
   `windowHash`   and it is consistent with the audit copy: when `window_sha.tsv` is supplied (`hashRequired`), the
                  window has a recorded SHA-1 and the checker's own SHA-1 of the window text (`Sha1.hex`) equals it;
3. `quoteMismatch` the quote is the window's text at the stated offset (characters; tabs/newlines as spaces);
4. `noCue`        the quote contains a cue phrase of the asserted kind;
5. `disqualified` the quote contains no disqualifier: procedural "overruled" (objection, motion, point of error,
   assignment of error…), reported history ("overruled by", "as stated in"…), declining to overrule, a dissent's or
   concurrence's words;
6. `targetUnresolved` the target evidence resolves in the quote or window: the citation (spacing and case ignored),
   or every name token; and, when the citation index (`cite_index.tsv`) is supplied, the cited citation resolves
   through it to the row's target node;
7. `partNotMajority` the part is majority, plurality or per curiam;
8. `targetLater`  the target is not later than the treating decision;
9. `noAuthority`  the treating decision has power (`canChangeStatus`); a history row whose deciding court is unknown
   is admitted as `okUnverifiedBy`.

`checkCert_sound` proves admission implies each condition; `checkCert_window_hash` and `checkCert_cite_index` spell out
the hash and index conditions. The checker runs compiled in the runner (TRUST.md).
-/

namespace CaseLaw2.Cert
open CaseLaw2

/-! ## String helpers -/

def norm (s : String) : String := s.map (fun c => if c == '\t' || c == '\n' || c == '\r' then ' ' else c)

/-- `pat` occurs in `s` (`pat` nonempty). -/
def hasSub (s pat : String) : Bool := !pat.isEmpty && (s.splitOn pat).length > 1

/-- `a` occurs, and `b` occurs after it. -/
def hasInOrder (s a b : String) : Bool :=
  match s.splitOn a with
  | _ :: rest@(_ :: _) => hasSub ("".intercalate rest) b
  | _ => false

/-- The characters `[i, i+n)` of `s`. -/
def slice (s : String) (i n : Nat) : String := String.ofList ((s.toList.drop i).take n)

/-- Lowercase letters and digits only: citation matching. SCHEMA's `cite:<normalised citation>` is the reader's
normalisation (`575 F.3d 432` → `cite:575 f3d 432`), so punctuation and spaces are dropped on both sides (D4). -/
def compact (s : String) : String := String.ofList (s.toLower.toList.filter Char.isAlphanum)

/-- Lowercase words of letters and digits, padded with spaces: whole-word name matching. -/
def words (s : String) : String := " " ++ String.map (fun c => if c.isAlphanum then c else ' ') s.toLower ++ " " 

/-! ## Phrase tables (data the checker uses; listed in DEVIATIONS.md) -/

inductive Kind where
  | treat (k : TKind) | hist (k : HKind)
  deriving Repr, DecidableEq, Inhabited

/-- The cue phrases of a kind. The table is generated (`CueTable.lean`, from `tools/caselaw2/cues/cue_table.json`):
the reference engine and the reader read the same table (round 4). -/
def cues : Kind → List String
  | .treat k => treatCues k
  | .hist k => histCues k

/-- Disqualifiers: `(a, b)` = `a` followed later by `b` (`b = ""`: `a` alone). The phrases are in the generated
table: a procedural "overruled" (point of error, assignment of error…), a reported history ("overruled by", "as
stated in"…), a refusal to overrule; for history, a separate opinion's would-be disposition. (A quote that mentions
a dissent or concurrence is not their words: the `part` column decides that; D4.) -/
def disqualifiers : Kind → List (String × String)
  | .treat k => if k.changesStatus then treatDisqualifiers.map (·, "") else []
  | .hist _ => histDisqualifiers.map (·, "")

/-! ## The checker -/

inductive Reason where
  | shaUnknown | noWindow | windowHash | quoteMismatch | noCue | disqualified | targetUnresolved | partNotMajority
  | targetLater | noAuthority
  /-- round 5: an `operativeWords` claim on a row that is not an explicit `disapproved` row -/
  | operativeBadRow
  /-- round 6 (anchored history rows): the anchor quote is not at its offset in a usable window of the text; it has
  no anchor cue; it has an anchor disqualifier; the target evidence does not resolve inside it; its part is not
  allowed -/
  | anchorMismatch | anchorNoCue | anchorDisqualified | anchorUnresolved | anchorPart
  /-- round 7 (joined treatments rows, `round7/DESIGN7.md` §2): a joined quote is not at its offset in a usable
  window of the row's text (or the row has not one or two joined lines); its part is not allowed; it has a
  disqualifier; its relation to the main quote does not hold; the target evidence is in no joined quote -/
  | joinedMismatch | joinedPart | joinedDisqualified | joinedRelation | joinedUnresolved
  /-- round 7 (doctrine rows): not an explicit `disapproved` row with a `doctrineTie` line; a label the table ties
  to two targets -/
  | doctrineBadRow | doctrineAmbiguous
  /-- round 7 (history claims, §3.1): head matter under an `orderHead` claim whose conditions do not all hold -/
  | orderHeadNotAllowed
  /-- round 8 (bridge evidence of history rows, `round8/DESIGN8.md` §4): the bridge quote is not at its offset in a
  usable window of W's text (or is empty or longer than `bridgeMaxLen`); date(W) < date(O) or a date is unknown; the
  quote has a ";"; no citation of the target; no bridge cue of the kind after it; the first citation after the cue
  is not the acting decision's -/
  | bridgeMismatch | bridgeDate | bridgeClause | bridgeTarget | bridgeCue | bridgeActor
  /-- round 8 (D8-9, step 5b): a key of the index begins between the end of the target's citation and the cue -/
  | bridgeChain
  /-- round 9 (part zones, `round9/DESIGN9.md` §4): the row's acting node has zones and its main quote (or a joined
  quote) is inside no zone of its own part -/
  | partZone
  /-- round 9 batch 2 (`round9/DESIGN9.md` §5, D9-7): a far antecedent joined quote (`joinedFar` claim) beyond
  `joinedFarMax`; no usable window of the row's text covers the gap; an index key of another node begins in the gap -/
  | joinedFarGap | joinedFarWindow | joinedFarKey
  /-- round 9 batch 2 (§7): an `implicitReject` claim on a kind that is not soft -/
  | implicitBadKind
  /-- round 10 (remand bridge evidence, `round10/DESIGN10.md` §4, D10-5, D10-6): B is of another court than the
  target; a date is unknown or out of order (the target before the order, B from the order to 1,826 days after); the
  docket token is not in both docket spans; B's quote is unreadable or has no "supreme court" + remand cue; B's quote
  has no tie to the order -/
  | remandCourt | remandDate | remandDocket | remandCue | remandTie
  deriving Repr, DecidableEq, Inhabited

/-- Round 5 (DESIGN5 §2.2, §3.2): how the text checks read a certificate. `plain`: the round-4 checks. `recog`: a
later court's statement that X was overruled by Y (recognition cues and disqualifiers; the names resolve in the
quote itself). `operative`: the court's own operative words other than the terms of art (operative cues, the
round-4 disqualifiers and the operative ones; the target resolves in the quote itself). Round 7 `doctrine`: the main
quote of a doctrine row (doctrine-reject cues; the round-4 and operative disqualifiers; DESIGN7 §2.4). -/
inductive Mode where
  | plain | recog | operative | doctrine
  deriving Repr, DecidableEq, Inhabited

def Reason.toString (r : Reason) : String := (reprStr r).replace "CaseLaw2.Cert.Reason." ""

inductive Result where
  | ok | okUnverifiedBy | fail (r : Reason)
  deriving Repr, DecidableEq, Inhabited

def Result.toString : Result → String
  | .ok => "ok" | .okUnverifiedBy => "okUnverifiedBy" | .fail r => r.toString

def Result.admitted : Result → Bool
  | .ok | .okUnverifiedBy => true
  | .fail _ => false

structure Window where
  start0 : Nat
  stop0 : Nat
  text : String
  /-- the window's SHA-1 recorded by the audit copy (`window_sha.tsv`: the corpus text cut at `[start0, stop0)`) -/
  hash : Option String := none
  /-- the checker's own SHA-1 of `text`, computed at most once per window and shared by every check that uses it
  (a cache: `digest_eq` pins it to `Sha1.hex text`) -/
  digest : Thunk String := Thunk.mk fun _ => Sha1.hex text
  digest_eq : digest.get = Sha1.hex text := by rfl

instance : Inhabited Window := ⟨{ start0 := 0, stop0 := 0, text := "" }⟩

/-- One certificate with everything the checker needs. -/
structure Input where
  kind : Kind
  textSha : String
  start : Nat
  stop : Nat
  quote : String
  evidence : String
  part : String
  /-- the text hashes the quote may come from -/
  shas : List String
  /-- the windows supplied for this hash -/
  windows : List Window
  /-- target date ≤ treating date (true when unknown) -/
  ordered : Bool
  /-- `canChangeStatus`; `none` = the treating decision is unknown -/
  authority : Option Bool
  /-- the quote is from the target's own text (a history row such as "the opinion is withdrawn"): the text is the
  target, so no target evidence is needed (D4 triage, DIFFTEST.md) -/
  selfText : Bool := false
  /-- `window_sha.tsv` was supplied: every window used must carry a recorded hash -/
  hashRequired : Bool := false
  /-- the row's target node (for citation-index resolution) -/
  target : Nat := 0
  /-- the citation index (`cite_index.tsv`), keyed by `compact` citation; a key the data gives two nodes is left out
  (ambiguous: resolves to nothing). `none` = no index supplied. -/
  citeIndex : Option (Std.HashMap String Nat) := none
  /-- round 5: the text mode (`plain` = round 4) -/
  mode : Mode := .plain
  deriving Inhabited

def shaOk (c : Input) : Bool := c.shas.contains c.textSha

/-- A supplied window that covers the quoted span and is well formed (its text is exactly `[start0, stop0)`, as
SCHEMA's cert_text says; a malformed window is skipped, not used to misplace the quote; D4 real-data triage). -/
def wellFormed (c : Input) (w : Window) : Bool :=
  w.start0 ≤ c.start && c.stop ≤ w.stop0 && w.text.length == w.stop0 - w.start0

/-- The window agrees with the audit copy: its SHA-1, computed here, is the recorded one; with no recorded hash it is
usable only when no hash file was supplied. -/
def hashOk (c : Input) (w : Window) : Bool :=
  match w.hash with
  | some h => w.digest.get == h
  | none => !c.hashRequired

/-- A window the checker may use: well formed and hash-consistent. -/
def usable (c : Input) (w : Window) : Bool := wellFormed c w && hashOk c w

/-- The quote is the window's text at the stated offset, and is not empty (FB-L2: an empty quote at an empty span
must not pass). -/
def quoteAt (c : Input) (w : Window) : Bool :=
  c.start < c.stop && c.quote != "" &&
    slice (norm w.text) (c.start - w.start0) (c.stop - c.start) == norm c.quote

/-- The first usable window in which the quote is found. Any usable window may carry the quote: the verdict does not
depend on the order of the windows (FB-L3; with `window_sha.tsv`, every usable window is the corpus text anyway). -/
def coveringWindow (c : Input) : Option Window :=
  c.windows.find? (fun w => usable c w && quoteAt c w)

def quoteOk (c : Input) : Bool :=
  match coveringWindow c with
  | some w => quoteAt c w
  | none => false

/-- The cue phrases the quote is tested against: the kind's (round 4), or the mode's (round 5). -/
def cueList (c : Input) : List String :=
  match c.mode with
  | .plain => cues c.kind
  | .recog => recognisedCues
  | .operative => operativeCues
  | .doctrine => doctrineRejectCues

/-- The disqualifiers the quote is tested against. In `recog` mode a reported history ("overruled by") is the
normal form, so only the recognition disqualifiers apply. -/
def disqList (c : Input) : List (String × String) :=
  match c.mode with
  | .plain => disqualifiers c.kind
  | .recog => recognisedDisqualifiers.map (·, "")
  | .operative => disqualifiers c.kind ++ operativeDisqualifiers.map (·, "")
  | .doctrine => disqualifiers c.kind ++ operativeDisqualifiers.map (·, "")

def hasCue (c : Input) : Bool := (cueList c).any (hasSub (norm c.quote).toLower)

def disqualified (c : Input) : Bool :=
  let q := (norm c.quote).toLower
  (disqList c).any (fun (a, b) => if b.isEmpty then hasSub q a else hasInOrder q a b)

/-- The citation resolves through the index to the row's target (true when no index is supplied). -/
def citeResolves (c : Input) (cite : String) : Bool :=
  match c.citeIndex with
  | some m => m.get? (compact cite) == some c.target
  | none => true

def resolves (c : Input) : Bool :=
  -- the target may be named in the quote or in any usable window covering it (several windows can cover one
  -- quote; all of them are the context, D4 real data)
  -- round 5: in `recog` and `operative` mode the name must be in the quote itself
  let ctx := if c.mode == .plain then
      (norm c.quote) ++ " " ++ " ".intercalate ((c.windows.filter (usable c)).map fun w => norm w.text)
    else norm c.quote
  if c.selfText then true
  else if c.evidence.startsWith "cite:" then
    hasSub (compact ctx) (compact (c.evidence.drop 5).toString) && citeResolves c (c.evidence.drop 5).toString
  else if c.evidence.startsWith "name:" then
    let toks := (((c.evidence.drop 5).toString.toLower.splitOn " ").map compact).filter (fun t => t.length ≥ 3)
    !toks.isEmpty && toks.all (fun t => hasSub (words ctx) (" " ++ t ++ " "))
  else false

def partOk (c : Input) : Bool := c.part == "majority" || c.part == "plurality" || c.part == "perCuriam"

/-- **The checker.** -/
def check (c : Input) : Result :=
  if !shaOk c then .fail .shaUnknown
  else if !(c.windows.any (wellFormed c)) then .fail .noWindow
  else if !(c.windows.any (usable c)) then .fail .windowHash
  else if !quoteOk c then .fail .quoteMismatch
  else if !hasCue c then .fail .noCue
  else if disqualified c then .fail .disqualified
  else if !resolves c then .fail .targetUnresolved
  else if !partOk c then .fail .partNotMajority
  else if !c.ordered then .fail .targetLater
  else match c.authority with
    | some true => .ok
    | some false => .fail .noAuthority
    | none => .okUnverifiedBy

/-- **Certificate soundness**: an admitted row satisfies every condition, and `ok` also has verified power. -/
theorem checkCert_sound (c : Input) (h : (check c).admitted = true) :
    shaOk c = true ∧ (∃ w, coveringWindow c = some w ∧ quoteAt c w = true) ∧ hasCue c = true ∧
      disqualified c = false ∧ resolves c = true ∧ partOk c = true ∧ c.ordered = true ∧
      (check c = .ok → c.authority = some true) ∧ (check c = .okUnverifiedBy → c.authority = none) := by
  unfold check at h ⊢
  by_cases h1 : shaOk c <;> simp only [h1, Bool.not_true, Bool.not_false, Bool.false_eq_true, ↓reduceIte] at h ⊢
  · by_cases h2 : c.windows.any (wellFormed c) <;>
      simp only [h2, Bool.not_true, Bool.not_false, Bool.false_eq_true, ↓reduceIte] at h ⊢
    · by_cases h2u : c.windows.any (usable c) <;>
        simp only [h2u, Bool.not_true, Bool.not_false, Bool.false_eq_true, ↓reduceIte] at h ⊢
      · cases hw : coveringWindow c with
        | none => simp [quoteOk, hw, Result.admitted] at h
        | some w =>
          have hq : quoteOk c = quoteAt c w := by simp [quoteOk, hw]
          by_cases h3 : quoteAt c w <;> simp only [hq, h3, Bool.not_true, Bool.not_false, Bool.false_eq_true, ↓reduceIte] at h ⊢
          · by_cases h4 : hasCue c <;> simp only [h4, Bool.not_true, Bool.not_false, Bool.false_eq_true, ↓reduceIte] at h ⊢
            · by_cases h5 : disqualified c <;> simp only [h5, Bool.false_eq_true, ↓reduceIte] at h ⊢
              · simp [Result.admitted] at h
              · by_cases h6 : resolves c <;> simp only [h6, Bool.not_true, Bool.not_false, Bool.false_eq_true, ↓reduceIte] at h ⊢
                · by_cases h7 : partOk c <;> simp only [h7, Bool.not_true, Bool.not_false, Bool.false_eq_true, ↓reduceIte] at h ⊢
                  · by_cases h8 : c.ordered <;> simp only [h8, Bool.not_true, Bool.not_false, Bool.false_eq_true, ↓reduceIte] at h ⊢
                    · cases ha : c.authority with
                      | none => simp_all
                      | some b => cases b <;> simp_all [Result.admitted]
                    · simp [Result.admitted] at h
                  · simp [Result.admitted] at h
                · simp [Result.admitted] at h
            · simp [Result.admitted] at h
          · simp [Result.admitted] at h
      · simp [Result.admitted] at h
    · simp [Result.admitted] at h
  · simp [Result.admitted] at h

/-- **Non-empty quote** (FB-L2): an admitted row quotes at least one character, at a non-empty span. -/
theorem checkCert_quote_nonempty (c : Input) (h : (check c).admitted = true) :
    c.quote ≠ "" ∧ c.start < c.stop := by
  obtain ⟨_, ⟨w, _, hq⟩, _⟩ := checkCert_sound c h
  unfold quoteAt at hq
  refine ⟨?_, ?_⟩
  · intro he
    simp [he] at hq
  · rcases Nat.lt_or_ge c.start c.stop with hlt | hge
    · exact hlt
    · exfalso
      have hn : ¬ c.start < c.stop := Nat.not_lt.mpr hge
      simp [hn] at hq

/-- **Window hash** (TRUST.md): an admitted row's quote sits in a well-formed window whose SHA-1, computed by the
checker itself (`Sha1.hex`), equals the digest the audit copy recorded for that window; when the hash file is
supplied, a digest must have been recorded. -/
theorem checkCert_window_hash (c : Input) (h : (check c).admitted = true) :
    ∃ w, coveringWindow c = some w ∧ quoteAt c w = true ∧ wellFormed c w = true ∧
      (∀ s, w.hash = some s → Sha1.hex w.text = s) ∧ (c.hashRequired = true → w.hash.isSome = true) := by
  obtain ⟨_, ⟨w, hw, hq⟩, _⟩ := checkCert_sound c h
  have hu' := List.find?_some hw
  have hu : usable c w = true := by
    simp only [Bool.and_eq_true] at hu'
    exact hu'.1
  simp only [usable, Bool.and_eq_true] at hu
  obtain ⟨hwf, hh⟩ := hu
  refine ⟨w, hw, hq, hwf, ?_, ?_⟩
  · intro s hs
    simp only [hashOk, hs, beq_iff_eq] at hh
    rw [← w.digest_eq]
    exact hh
  · intro hr
    cases hwh : w.hash with
    | some _ => rfl
    | none => simp [hashOk, hwh, hr] at hh

/-- **Citation-index resolution**: when the citation index is supplied, an admitted row whose target evidence is a
citation (and whose quote is not the target's own text) cites a citation that the index resolves to the row's
target node: `index(cite) = target`. -/
theorem checkCert_cite_index (c : Input) (h : (check c).admitted = true) (hs : c.selfText = false)
    (hc : c.evidence.startsWith "cite:" = true) (m : Std.HashMap String Nat) (hm : c.citeIndex = some m) :
    m.get? (compact (c.evidence.drop 5).toString) = some c.target := by
  have hr := (checkCert_sound c h).2.2.2.2.1
  simp only [resolves, hs, hc, Bool.false_eq_true, ↓reduceIte, Bool.and_eq_true] at hr
  have h2 := hr.2
  simp only [citeResolves, hm, beq_iff_eq] at h2
  exact h2

/-- Each rejection names the first failing condition: a rejected row carries exactly one reason code. -/
theorem check_fail_reason (c : Input) (r : Reason) (h : check c = .fail r) :
    (r = .shaUnknown ↔ shaOk c = false) := by
  unfold check at h
  by_cases h1 : shaOk c <;> simp [h1] at h ⊢
  · repeat' split at h
    all_goals (try cases h)
    all_goals simp
  · exact h.symm

/-! ## Witness rows: an implicit overruling stated by a later court (round 4; `round3/implicit_schema.md`)

"Decision X was overruled / abrogated by decision Y", where Y does not say so itself: a later decision W says it.
The row names Y as the by-decision; the certificate's hash, offsets, quote and window are W's. Such a row is
`explicit = 0`: it never changes a status (`Spec.inferred_treatment_no_effect`), and yields one `atRisk` finding
naming Y. The checks, in order (the first failure is the reason):

1. `witnessBadRow`      W is a known decision, the row is `explicit = 0`, the kind is status-changing;
2. the text checks of `check` on W's window, with X as the target (`shaUnknown` … `partNotMajority`);
3. `byUnresolved`       the by-evidence names Y in the quote or its window (a citation resolves through the index);
4. `targetLater`        date(X) ≤ date(Y);  `witnessEarlier`  date(Y) ≤ date(W);
5. `witnessNoStanding`  W's court is X's court, or a court with power to overrule X;
6. Y's power over X, as for every status-changing row (`noAuthority` / `okUnverifiedBy`). -/

/-- What a witness row adds to its certificate input (`treatment_witness.tsv`). In the `Input`, `shas` are W's,
`target` is X, `ordered` is date(X) ≤ date(Y) and `authority` is Y's power over X. -/
structure Witness where
  /-- the witness node W is a known decision -/
  known : Bool
  /-- the row's `explicit` flag (must be false) -/
  explicit : Bool
  /-- the row's kind changes status -/
  changes : Bool
  /-- `cite:` / `name:` evidence naming Y -/
  byEvidence : String
  /-- the by-decision Y (for citation-index resolution) -/
  by_ : Nat
  /-- date(Y) ≤ date(W) (true when unknown) -/
  witnessOrdered : Bool
  /-- W's court is X's court, or has power to overrule X -/
  standing : Bool
  /-- round 5: the row claims the `recognised` class (`treatment_class.tsv`) -/
  claim : Bool := false
  /-- round 5: W's court has power to overrule X (not mere standing) -/
  power : Bool := false
  /-- round 5: date(X), date(Y) and date(W) are all known -/
  datesKnown : Bool := false
  deriving Inhabited

def Witness.rowOk (w : Witness) : Bool := w.known && !w.explicit && w.changes

/-- The by-evidence names Y in the quote or a usable window (the same test as the target's, on Y). -/
def byResolves (c : Input) (w : Witness) : Bool :=
  resolves { c with evidence := w.byEvidence, target := w.by_, selfText := false }

/-- The text part of the certificate: every check of `check` that reads W's text. -/
def textCheck (c : Input) : Result := check { c with ordered := true, authority := some true }

inductive WResult where
  | ok | okUnverifiedBy | fail (r : Reason) | witnessBadRow | byUnresolved | witnessEarlier | witnessNoStanding
  deriving Repr, DecidableEq, Inhabited

def WResult.toString : WResult → String
  | .ok => "ok" | .okUnverifiedBy => "okUnverifiedBy" | .fail r => r.toString
  | .witnessBadRow => "witnessBadRow" | .byUnresolved => "byUnresolved" | .witnessEarlier => "witnessEarlier"
  | .witnessNoStanding => "witnessNoStanding"

def WResult.admitted : WResult → Bool
  | .ok | .okUnverifiedBy => true
  | _ => false

/-- The checks after the text checks. -/
def witnessTail (c : Input) (w : Witness) : WResult :=
  if !byResolves c w then .byUnresolved
  else if !c.ordered then .fail .targetLater
  else if !w.witnessOrdered then .witnessEarlier
  else if !w.standing then .witnessNoStanding
  else match c.authority with
    | some true => .ok
    | some false => .fail .noAuthority
    | none => .okUnverifiedBy

/-- **The witness checker.** -/
def checkWitness (c : Input) (w : Witness) : WResult :=
  if !w.rowOk then .witnessBadRow
  else match textCheck c with
    | .fail r => .fail r
    | _ => witnessTail c w

theorem witnessTail_sound (c : Input) (w : Witness) (h : (witnessTail c w).admitted = true) :
    byResolves c w = true ∧ c.ordered = true ∧ w.witnessOrdered = true ∧ w.standing = true := by
  unfold witnessTail at h
  by_cases h1 : byResolves c w = true
  · by_cases h2 : c.ordered = true
    · by_cases h3 : w.witnessOrdered = true
      · by_cases h4 : w.standing = true
        · exact ⟨h1, h2, h3, h4⟩
        · simp [h1, h2, h3, h4, WResult.admitted] at h
      · simp [h1, h2, h3, WResult.admitted] at h
    · simp [h1, h2, WResult.admitted] at h
  · simp [h1, WResult.admitted] at h

/-- **Witness soundness**: an admitted witness row is `explicit = 0` with a status-changing kind and a known
witness; W's text passes every text check with X as the target; Y is named; the dates are ordered X ≤ Y ≤ W; and W
has standing. -/
theorem checkWitness_sound (c : Input) (w : Witness) (h : (checkWitness c w).admitted = true) :
    w.known = true ∧ w.explicit = false ∧ w.changes = true ∧ (textCheck c).admitted = true ∧
      byResolves c w = true ∧ c.ordered = true ∧ w.witnessOrdered = true ∧ w.standing = true := by
  unfold checkWitness at h
  by_cases h0 : w.rowOk = true
  · have hr : w.known = true ∧ w.explicit = false ∧ w.changes = true := by
      simpa [Witness.rowOk, Bool.and_eq_true, and_assoc] using h0
    simp only [h0, Bool.not_true, Bool.false_eq_true, ↓reduceIte] at h
    cases ht : textCheck c with
    | fail r => simp [ht, WResult.admitted] at h
    | ok =>
      simp only [ht] at h
      exact ⟨hr.1, hr.2.1, hr.2.2, rfl, witnessTail_sound c w h⟩
    | okUnverifiedBy =>
      simp only [ht] at h
      exact ⟨hr.1, hr.2.1, hr.2.2, rfl, witnessTail_sound c w h⟩
  · simp [h0, WResult.admitted] at h

/-- **A witness row is never explicit**: an admitted witness row carries `explicit = false`, so the event built from
it has no status effect (with `Spec.inferred_treatment_no_effect`: `Examples.witness_row_no_effect`). -/
theorem checkWitness_inferred (c : Input) (w : Witness) (h : (checkWitness c w).admitted = true) :
    w.explicit = false := (checkWitness_sound c w h).2.1

/-! ## Round 5: recognised overrulings, operative words, classes (DESIGN5.md)

A witness row may claim the `recognised` class: W, a decision of a court that itself has **power** to overrule X,
says in a majority sentence that X was overruled by Y. The claim is checked on top of the round-4 witness checks,
read in `recog` mode (a recognition cue, no recognition disqualifier, X and Y both named in the quote itself), with
W's power and known dates. A claim that fails leaves the row exactly where round 4 put it. -/

/-- The verdict on a witness row in round 5. -/
inductive RResult where
  /-- recognised; `unverifiedBy`: Y's power over X is unknown (the effect is then `unknown powerUnknown`) -/
  | recognised (unverifiedBy : Bool)
  /-- not recognised: the round-4 witness verdict -/
  | witness (r : WResult)
  deriving Repr, DecidableEq, Inhabited

def RResult.toString : RResult → String
  | .recognised false => "okRecognised"
  | .recognised true => "okRecognisedUnverifiedBy"
  | .witness r => r.toString

def RResult.admitted : RResult → Bool
  | .recognised _ => true
  | .witness r => r.admitted

def RResult.isRecognised : RResult → Bool
  | .recognised _ => true
  | .witness _ => false

/-- The evidence naming Y is not the evidence naming X. -/
def distinctEvidence (c : Input) (w : Witness) : Bool :=
  compact (c.evidence.drop 5).toString != compact (w.byEvidence.drop 5).toString

/-- **The recognised checker** (DESIGN5 §2.2). `c` is the row's certificate input in `plain` mode. -/
def checkRecognised (c : Input) (w : Witness) : RResult :=
  if !(w.claim && w.power && w.datesKnown && distinctEvidence c w) then .witness (checkWitness c w)
  else match checkWitness { c with mode := .recog } w with
    | .ok => .recognised false
    | .okUnverifiedBy => .recognised true
    | _ => .witness (checkWitness c w)

/-- **Recognition soundness**: a recognised row made the claim; W has power over X; the three dates are known; the
two names differ; and the row passes every witness check read in `recog` mode: it is `explicit = 0` with a
status-changing kind, W's text passes the text checks (recognition cue, no recognition disqualifier, X named in the
quote, majority part), Y is named in the quote, the dates are ordered X ≤ Y ≤ W, and W has standing. -/
theorem checkRecognised_sound (c : Input) (w : Witness) (h : (checkRecognised c w).isRecognised = true) :
    w.claim = true ∧ w.power = true ∧ w.datesKnown = true ∧ distinctEvidence c w = true ∧
      w.known = true ∧ w.explicit = false ∧ w.changes = true ∧
      (textCheck { c with mode := .recog }).admitted = true ∧ byResolves { c with mode := .recog } w = true ∧
      c.ordered = true ∧ w.witnessOrdered = true ∧ w.standing = true := by
  unfold checkRecognised at h
  by_cases h0 : (w.claim && w.power && w.datesKnown && distinctEvidence c w) = true
  · simp only [h0, Bool.not_true, Bool.false_eq_true, ↓reduceIte] at h
    have h0' := h0
    simp only [Bool.and_eq_true] at h0'
    obtain ⟨⟨⟨hc, hp⟩, hd⟩, he⟩ := h0'
    have ha : (checkWitness { c with mode := .recog } w).admitted = true := by
      cases hw : checkWitness { c with mode := .recog } w <;> simp_all [RResult.isRecognised, WResult.admitted]
    exact ⟨hc, hp, hd, he, checkWitness_sound _ w ha⟩
  · simp [h0, RResult.isRecognised] at h

/-- **Never without W's power**: a witness row whose W lacks power over X is never recognised. -/
theorem checkRecognised_needs_power (c : Input) (w : Witness) (h : w.power = false) :
    (checkRecognised c w).isRecognised = false := by
  cases hr : (checkRecognised c w).isRecognised with
  | false => rfl
  | true => have := (checkRecognised_sound c w hr).2.1; simp [h] at this

/-- **Fallback**: a row that is not recognised has exactly its round-4 witness verdict. -/
theorem checkRecognised_fallback (c : Input) (w : Witness) (h : (checkRecognised c w).isRecognised = false) :
    checkRecognised c w = .witness (checkWitness c w) := by
  unfold checkRecognised at h ⊢
  by_cases h0 : (w.claim && w.power && w.datesKnown && distinctEvidence c w) = true
  · simp only [h0, Bool.not_true, Bool.false_eq_true, ↓reduceIte] at h ⊢
    cases hw : checkWitness { c with mode := .recog } w <;> simp_all [RResult.isRecognised]
  · simp [h0]

/-- **No claim, no change**: without a `recognised` claim the verdict is the round-4 witness verdict. -/
theorem checkRecognised_no_claim (c : Input) (w : Witness) (h : w.claim = false) :
    checkRecognised c w = .witness (checkWitness c w) := by
  simp [checkRecognised, h]

/-- What the runner writes on the event of a witness row: the recognition (W, date(W)) when the verdict is
recognised, nothing otherwise. Every `Recog` the runner makes comes from here. -/
def recogOf (v : RResult) (witness : Nat) (date : Date) : Option Recog :=
  if v.isRecognised then some { witness, date, power := true } else none

/-- An event carries a recognition only when the recognised check passed. -/
theorem recogOf_isSome (v : RResult) (witness : Nat) (date : Date) :
    (recogOf v witness date).isSome = v.isRecognised := by
  unfold recogOf; cases v.isRecognised <;> simp

/-- The quote disposes of the case as a whole (DESIGN5 §3.3): it contains a whole-case phrase and no limiting
phrase ("to the extent", "insofar as", "in the field of" …). -/
def wholeCase (quote : String) : Bool :=
  operativeWhole.any (hasSub (norm quote).toLower) && !operativeLimit.any (hasSub (norm quote).toLower)

/-- **The operative-words checker** (DESIGN5 §3.2): an explicit `disapproved` row, checked in `operative` mode. A
failed claim is not admitted (the plain check is not tried). -/
def checkOperative (c : Input) (explicit : Bool) : Result :=
  if !(c.kind == .treat .disapproved && explicit) then .fail .operativeBadRow
  else check { c with mode := .operative }

/-- **Operative-words soundness**: an admitted operative-words row is an explicit `disapproved` row whose quote has
an operative cue and none of the round-4 or operative disqualifiers, names the target in the quote itself, and
passes every other check of `check`. -/
theorem checkOperative_sound (c : Input) (explicit : Bool) (h : (checkOperative c explicit).admitted = true) :
    c.kind = .treat .disapproved ∧ explicit = true ∧ (check { c with mode := .operative }).admitted = true ∧
      hasCue { c with mode := .operative } = true ∧ disqualified { c with mode := .operative } = false ∧
      resolves { c with mode := .operative } = true := by
  unfold checkOperative at h
  by_cases h0 : (c.kind == .treat .disapproved && explicit) = true
  · simp only [h0, Bool.not_true, Bool.false_eq_true, ↓reduceIte] at h
    have h0' := h0
    simp only [Bool.and_eq_true, beq_iff_eq] at h0'
    have hs := checkCert_sound _ h
    exact ⟨h0'.1, h0'.2, h, hs.2.2.1, hs.2.2.2.1, hs.2.2.2.2.1⟩
  · simp [h0, Result.admitted] at h

/-- The classes of a status-changing treatments row (DESIGN5 §5; round 7 adds `doctrine`, DESIGN7 §2.4). The tie
order is `idx`: selfAnnounced < operativeWords < recognised < doctrine < atRiskWitness. -/
inductive OClass where
  | selfAnnounced | operativeWords | recognised | atRiskWitness | doctrine
  deriving Repr, DecidableEq, Inhabited

def OClass.idx : OClass → Nat
  | .selfAnnounced => 0 | .operativeWords => 1 | .recognised => 2 | .doctrine => 3 | .atRiskWitness => 4

def OClass.toString : OClass → String
  | .selfAnnounced => "selfAnnounced" | .operativeWords => "operativeWords" | .recognised => "recognised"
  | .atRiskWitness => "atRiskWitness" | .doctrine => "doctrine"

/-- The quote uses a term of art (overrule, disapprove, recede, abrogate). -/
def selfAnnounced (quote : String) : Bool := selfAnnouncedCues.any (hasSub (norm quote).toLower)

/-- **The class of a row**: recognised (the recognised check passed); otherwise at-risk witness when the row is
not explicit; otherwise by the words of the certified quote. -/
def classOf (explicit recognised : Bool) (quote : String) : OClass :=
  if recognised then .recognised
  else if !explicit then .atRiskWitness
  else if selfAnnounced quote then .selfAnnounced else .operativeWords

/-- A row is classed `recognised` exactly when the recognised check passed. -/
theorem classOf_recognised_iff (explicit recognised : Bool) (quote : String) :
    classOf explicit recognised quote = .recognised ↔ recognised = true := by
  unfold classOf
  cases recognised <;> cases explicit <;> simp <;> split <;> simp

/-! ## Round 6: anchored history rows (`round6/history/DESIGN6.md` §4, `LEAN6.md`)

A reviewing court's judgment line ("The judgment of the Court of Appeals is reversed.") is often far from the
sentence that says which decision is under review ("Certiorari to … Reported below: 856 F. 2d 1214."). Such a
history row carries two quotes of the acting decision's text: its certificate (the disposition) and an **anchor**
(`history_anchor.tsv`). The checks, in order (the first failure is the reason):

1. `anchorMismatch`      the anchor quote is the text of a usable window of the certificate's own text at its
                         offset, and is not empty;
2. `anchorNoCue`         it contains an anchor cue;
3. `anchorDisqualified`  it contains no anchor disqualifier (an earlier proceeding: "former appeal", "see also" …);
4. `anchorUnresolved`    the row's target evidence resolves inside the anchor quote alone: the citation (and, with
                         a citation index, through it to the row's target), or every name token;
5. `anchorPart`          its part is majority, plurality, per curiam or head matter;
6. every check of `check` on the disposition quote, the target evidence taken as given (`selfText := true`).

What this proves and what it does not is in TRUST.md: both quotes are in the acting decision's text and the citation
resolves to the target; that the cited decision is the one under review is the linker's rule, not a theorem. -/

/-- The anchor of a history row: a second quote from the same text as the row's certificate. -/
structure Anchor where
  start : Nat
  stop : Nat
  quote : String
  part : String
  deriving Repr, Inhabited

/-- The anchor read over the certificate's own text: the certificate's hash, windows, hash requirement and index;
the anchor's span, quote and part. (The anchor has no hash of its own: a window of another text cannot carry it.) -/
def Anchor.input (a : Anchor) (c : Input) : Input :=
  { c with start := a.start, stop := a.stop, quote := a.quote, part := a.part }

/-- Check 1: the anchor quote is the text of a usable window of the certificate's text at its offset. -/
def anchorQuoteOk (c : Input) (a : Anchor) : Bool := quoteOk (a.input c)

/-- Check 2: the anchor quote contains an anchor cue. -/
def anchorHasCue (a : Anchor) : Bool := anchorCues.any (hasSub (norm a.quote).toLower)

/-- Check 3 fails when the anchor quote contains a mark of an earlier proceeding. -/
def anchorDisqualified (a : Anchor) : Bool := anchorDisqualifiers.any (hasSub (norm a.quote).toLower)

/-- Check 4: the row's target evidence resolves inside the anchor quote alone (never its window). -/
def anchorResolves (c : Input) (a : Anchor) : Bool :=
  if c.evidence.startsWith "cite:" then
    hasSub (compact (norm a.quote)) (compact (c.evidence.drop 5).toString) &&
      citeResolves c (c.evidence.drop 5).toString
  else if c.evidence.startsWith "name:" then
    let toks := (((c.evidence.drop 5).toString.toLower.splitOn " ").map compact).filter (fun t => t.length ≥ 3)
    !toks.isEmpty && toks.all (fun t => hasSub (words (norm a.quote)) (" " ++ t ++ " "))
  else false

/-- Check 5: the anchor's part. Head matter is allowed (it names the court and the decision below). -/
def anchorPartOk (a : Anchor) : Bool :=
  a.part == "majority" || a.part == "plurality" || a.part == "perCuriam" || a.part == "headmatter"

/-- **The anchored checker.** -/
def checkAnchored (c : Input) (a : Anchor) : Result :=
  if !anchorQuoteOk c a then .fail .anchorMismatch
  else if !anchorHasCue a then .fail .anchorNoCue
  else if anchorDisqualified a then .fail .anchorDisqualified
  else if !anchorResolves c a then .fail .anchorUnresolved
  else if !anchorPartOk a then .fail .anchorPart
  else check { c with selfText := true }

/-- The runner's history step: a row with an anchor line is checked by `checkAnchored`, any other row by `check`. -/
def checkHistory (c : Input) (a? : Option Anchor) : Result :=
  match a? with
  | some a => checkAnchored c a
  | none => check c

/-- **Admission is exactly the six checks**: an anchored row is admitted if and only if the anchor passes its five
checks and the disposition quote passes `check` with the target evidence taken as given. -/
theorem checkAnchored_admitted_iff (c : Input) (a : Anchor) :
    (checkAnchored c a).admitted = true ↔
      (anchorQuoteOk c a = true ∧ anchorHasCue a = true ∧ anchorDisqualified a = false ∧
        anchorResolves c a = true ∧ anchorPartOk a = true ∧ (check { c with selfText := true }).admitted = true) := by
  unfold checkAnchored
  by_cases h1 : anchorQuoteOk c a = true
  · by_cases h2 : anchorHasCue a = true
    · by_cases h3 : anchorDisqualified a = true
      · simp [h1, h2, h3, Result.admitted]
      · by_cases h4 : anchorResolves c a = true
        · by_cases h5 : anchorPartOk a = true
          · simp [h1, h2, h3, h4, h5]
          · simp [h1, h2, h3, h4, h5, Result.admitted]
        · simp [h1, h2, h3, h4, Result.admitted]
    · simp [h1, h2, Result.admitted]
  · simp [h1, Result.admitted]

/-- **Anchored soundness**: an admitted anchored row has the anchor quote at its offset in a usable window of the
certificate's own text, an anchor cue, no anchor disqualifier, the target evidence resolved inside the anchor quote,
an allowed anchor part, and passes `check` with the target evidence taken as given; its verdict is that check's. -/
theorem checkAnchored_sound (c : Input) (a : Anchor) (h : (checkAnchored c a).admitted = true) :
    (∃ w, coveringWindow (a.input c) = some w ∧ w ∈ c.windows ∧ usable (a.input c) w = true ∧
        quoteAt (a.input c) w = true) ∧
      anchorHasCue a = true ∧ anchorDisqualified a = false ∧ anchorResolves c a = true ∧ anchorPartOk a = true ∧
      (check { c with selfText := true }).admitted = true ∧ checkAnchored c a = check { c with selfText := true } := by
  obtain ⟨h1, h2, h3, h4, h5, h6⟩ := (checkAnchored_admitted_iff c a).mp h
  refine ⟨?_, h2, h3, h4, h5, h6, ?_⟩
  · unfold anchorQuoteOk quoteOk at h1
    cases hw : coveringWindow (a.input c) with
    | none => simp [hw] at h1
    | some w =>
      have hf : (a.input c).windows.find? (fun w => usable (a.input c) w && quoteAt (a.input c) w) = some w := hw
      have hp := List.find?_some hf
      simp only [Bool.and_eq_true] at hp
      exact ⟨w, rfl, List.mem_of_find?_eq_some hf, hp.1, hp.2⟩
  · simp [checkAnchored, h1, h2, h3, h4, h5]

/-- **The disposition quote of an anchored row**: every conjunct of `checkCert_sound` except `resolves` (the anchor
carries the target evidence): a known hash, the quote at its offset in a usable window, a cue of the kind, no
disqualifier, an allowed part, the date order, and `ok` only with verified power. -/
theorem checkAnchored_disposition (c : Input) (a : Anchor) (h : (checkAnchored c a).admitted = true) :
    shaOk c = true ∧ (∃ w, coveringWindow c = some w ∧ quoteAt c w = true) ∧ hasCue c = true ∧
      disqualified c = false ∧ partOk c = true ∧ c.ordered = true ∧
      (checkAnchored c a = .ok → c.authority = some true) ∧
      (checkAnchored c a = .okUnverifiedBy → c.authority = none) := by
  obtain ⟨_, _, _, _, _, h6, he⟩ := checkAnchored_sound c a h
  obtain ⟨s1, s2, s3, s4, _, s6, s7, s8, s9⟩ := checkCert_sound { c with selfText := true } h6
  rw [he]
  exact ⟨s1, s2, s3, s4, s6, s7, s8, s9⟩

/-- **Citation index**: with a citation index and `cite:` evidence, an admitted anchored row's citation is one the
index resolves to the row's target node. -/
theorem checkAnchored_cite_index (c : Input) (a : Anchor) (h : (checkAnchored c a).admitted = true)
    (hc : c.evidence.startsWith "cite:" = true) (m : Std.HashMap String Nat) (hm : c.citeIndex = some m) :
    m.get? (compact (c.evidence.drop 5).toString) = some c.target := by
  have hr := (checkAnchored_sound c a h).2.2.2.1
  simp only [anchorResolves, hc, ↓reduceIte, Bool.and_eq_true] at hr
  have h2 := hr.2
  simp only [citeResolves, hm, beq_iff_eq] at h2
  exact h2

/-- **Anchor window hash**: an admitted anchored row's anchor sits in a well-formed window whose SHA-1, computed by
the checker itself, equals the recorded digest; when the hash file is supplied, a digest must have been recorded. -/
theorem checkAnchored_window_hash (c : Input) (a : Anchor) (h : (checkAnchored c a).admitted = true) :
    ∃ w, coveringWindow (a.input c) = some w ∧ quoteAt (a.input c) w = true ∧ wellFormed (a.input c) w = true ∧
      (∀ s, w.hash = some s → Sha1.hex w.text = s) ∧ (c.hashRequired = true → w.hash.isSome = true) := by
  obtain ⟨⟨w, hw, _, hu, hq⟩, _⟩ := checkAnchored_sound c a h
  simp only [usable, Bool.and_eq_true] at hu
  obtain ⟨hwf, hh⟩ := hu
  refine ⟨w, hw, hq, hwf, ?_, ?_⟩
  · intro s hs
    simp only [hashOk, hs, beq_iff_eq] at hh
    rw [← w.digest_eq]
    exact hh
  · intro hr
    have hr' : (a.input c).hashRequired = true := hr
    cases hwh : w.hash with
    | some _ => rfl
    | none => simp [hashOk, hwh, hr'] at hh

/-- **Both quotes are non-empty**: an admitted anchored row quotes at least one character for the anchor and for
the disposition, each at a non-empty span. -/
theorem checkAnchored_quote_nonempty (c : Input) (a : Anchor) (h : (checkAnchored c a).admitted = true) :
    a.quote ≠ "" ∧ a.start < a.stop ∧ c.quote ≠ "" ∧ c.start < c.stop := by
  obtain ⟨⟨w, _, _, _, hq⟩, _, _, _, _, h6, _⟩ := checkAnchored_sound c a h
  have hd := checkCert_quote_nonempty { c with selfText := true } h6
  have ha : a.quote ≠ "" ∧ a.start < a.stop := by
    unfold quoteAt at hq
    have hq' : (decide (a.start < a.stop) && a.quote != "" &&
        slice (norm w.text) (a.start - w.start0) (a.stop - a.start) == norm a.quote) = true := hq
    simp only [Bool.and_eq_true, decide_eq_true_eq, bne_iff_ne, ne_eq] at hq'
    exact ⟨hq'.1.2, hq'.1.1⟩
  exact ⟨ha.1, ha.2, hd.1, hd.2⟩

/-- **No anchor, no change**: a history row without an anchor line gets `check`'s verdict. -/
theorem checkHistory_no_anchor (c : Input) : checkHistory c none = check c := rfl

/-- A history row with an anchor line gets `checkAnchored`'s verdict. -/
theorem checkHistory_anchored (c : Input) (a : Anchor) : checkHistory c (some a) = checkAnchored c a := rfl

/-! ## Round 7: joined certificates, doctrine rows, history claims (`round7/DESIGN7.md` §2–3, `LEAN7.md`)

**Joined certificates.** A treatments row may carry one or two further quotes of the same text as its certificate
(`joined.tsv`), each with a relation to the row's main quote: `antecedent` (an overruling stated across two adjacent
sentences: "In Smith v. Jones … we held … . Those cases are overruled.") or `doctrineTie` (a doctrine target: "the
doctrine of 'separate but equal' … Plessy v. Ferguson" tied to "the doctrine of 'separate but equal' has no
place"). The checks, in order (the first failure is the reason):

1. `joinedMismatch`     one or two lines; each joined quote is the text of a usable window of the row's own text at
                        its offset, and is not empty;
2. `joinedPart`         each is from the majority, a plurality or per curiam;
3. `joinedDisqualified` none has a disqualifier of the row's kind or of `disqualify_joined`;
4. `joinedRelation`     each relation holds (`antecedentOk`, `tieOk`);
5. `joinedUnresolved`   the row's target evidence resolves inside one joined quote alone;
6. the row's own check on its main quote in its mode (plain, operative, doctrine), the evidence taken as given.

**Doctrine rows** (`treatment_class.tsv` claim `doctrine`): `doctrineBadRow` unless explicit, `disapproved` and with
a `doctrineTie` line; then the joined check in doctrine mode; then, over the table, `doctrineAmbiguous` when two rows
tie one label to two targets. Their effects are always demoted (`Spec.doctrineEffects`).

**History claims** (`history_claim.tsv`): `orderHead` lets head matter pass the part test for a Supreme Court order
list entry dated from 2013 with an order-line cue of its kind and at most 400 characters (else
`orderHeadNotAllowed`); `setAside` adds "set aside" to the cue list of a `vacated` row. Without a claim nothing
changes (`no_joined_no_change`). -/

/-- The relation a joined quote claims to the row's main quote. -/
inductive JRel where
  | antecedent | doctrineTie
  deriving Repr, DecidableEq, Inhabited

/-- A joined line (`joined.tsv`): a further quote of the row's own text. `label` is the doctrine phrase of a
`doctrineTie` line. -/
structure Joined where
  rel : JRel
  start : Nat
  stop : Nat
  quote : String
  part : String
  label : String
  deriving Repr, Inhabited

/-- The joined quote read over the row's own text: the row's hash, windows, hash requirement, index and evidence;
the joined line's span, quote and part. -/
def Joined.input (j : Joined) (c : Input) : Input :=
  { c with start := j.start, stop := j.stop, quote := j.quote, part := j.part }

/-- The joined quote as an anchor (for the evidence test, which is the anchor's). -/
def Joined.toAnchor (j : Joined) : Anchor := { start := j.start, stop := j.stop, quote := j.quote, part := j.part }

/-- The mode of a treatments row's main quote: plain (an explicit row), operative (`operativeWords` claim),
doctrine (`doctrine` claim). -/
inductive TClaim where
  | plain | operative | doctrine
  deriving Repr, DecidableEq, Inhabited

/-- The input the main check reads in that mode. -/
def TClaim.apply : TClaim → Input → Input
  | .plain, c => c
  | .operative, c => { c with mode := .operative }
  | .doctrine, c => { c with mode := .doctrine }

/-- Check 1: one or two joined lines. -/
def joinedCountOk (js : List Joined) : Bool := decide (1 ≤ js.length) && decide (js.length ≤ 2)

/-- Check 1: the joined quote is the text of a usable window of the row's text at its offset. -/
def joinedQuoteOk (c : Input) (j : Joined) : Bool := quoteOk (j.input c)

/-- Check 2: the joined quote is the opinion of the court (never head matter, never a separate opinion). -/
def joinedPartOk (j : Joined) : Bool := j.part == "majority" || j.part == "plurality" || j.part == "perCuriam"

/-- Check 3 fails when the joined quote has a disqualifier of the row's kind or of `disqualify_joined`. -/
def joinedDisqualified (c : Input) (j : Joined) : Bool :=
  let q := (norm j.quote).toLower
  (disqualifiers c.kind).any (fun (a, b) => if b.isEmpty then hasSub q a else hasInOrder q a b) ||
    joinedDisqualifiers.any (hasSub q)

/-- The main quote has a cue of the row's kind (the plain list). -/
def kindCue (c : Input) : Bool := (cues c.kind).any (hasSub (norm c.quote).toLower)

/-- The quote refers back ("those cases", "it is overruled" …). -/
def anaphorCue (q : String) : Bool := anaphorCues.any (hasSub (norm q).toLower)

/-- Relation `antecedent`: the joined quote ends before the main quote, at most `joinedGapMax` characters before
it; the main quote has an anaphor and a cue of the row's kind. -/
def antecedentOk (c : Input) (j : Joined) : Bool :=
  decide (j.stop ≤ c.start) && decide (c.start - j.stop ≤ joinedGapMax) && anaphorCue c.quote && kindCue c

/-- A doctrine label, normalised and lower-cased. -/
def labelNorm (s : String) : String := (norm s).toLower

/-- A doctrine label of two words or more and eight characters or more. -/
def labelOk (s : String) : Bool :=
  decide (2 ≤ (((labelNorm s).splitOn " ").filter (· ≠ "")).length) && decide (8 ≤ (labelNorm s).length)

/-- The label occurs in the quote (both normalised, lower-cased). -/
def labelIn (q label : String) : Bool := hasSub (norm q).toLower (labelNorm label)

/-- The quote ties a doctrine to its origin ("doctrine of", "announced in" …). -/
def tieCue (q : String) : Bool := doctrineTieCues.any (hasSub (norm q).toLower)

/-- Relation `doctrineTie` (only on a doctrine row): the label is in the main quote and in the joined quote, and the
joined quote has a tie cue. -/
def tieOk (cl : TClaim) (c : Input) (j : Joined) : Bool :=
  cl == .doctrine && labelOk j.label && labelIn c.quote j.label && labelIn j.quote j.label && tieCue j.quote

/-- Check 4: the line's relation holds. -/
def relationOk (cl : TClaim) (c : Input) (j : Joined) : Bool :=
  match j.rel with
  | .antecedent => antecedentOk c j
  | .doctrineTie => tieOk cl c j

/-- Check 5: the row's target evidence resolves inside the joined quote alone (as an anchor's). -/
def joinedResolves (c : Input) (j : Joined) : Bool := anchorResolves c j.toAnchor

/-- The row's own check on its main quote, in its mode. -/
def mainCheck (c : Input) (explicit : Bool) : TClaim → Result
  | .plain => check c
  | .operative => checkOperative c explicit
  | .doctrine => check { c with mode := .doctrine }

/-- **The joined checker.** -/
def checkJoined (c : Input) (explicit : Bool) (cl : TClaim) (js : List Joined) : Result :=
  if !(joinedCountOk js && js.all (joinedQuoteOk c)) then .fail .joinedMismatch
  else if !js.all joinedPartOk then .fail .joinedPart
  else if js.any (joinedDisqualified c) then .fail .joinedDisqualified
  else if !js.all (relationOk cl c) then .fail .joinedRelation
  else if !js.any (joinedResolves c) then .fail .joinedUnresolved
  else mainCheck { c with selfText := true } explicit cl

/-- A doctrine row: an explicit `disapproved` row with a `doctrineTie` line. -/
def doctrineRowOk (c : Input) (explicit : Bool) (js : List Joined) : Bool :=
  c.kind == .treat .disapproved && explicit && js.any (·.rel == .doctrineTie)

/-- **The doctrine checker** (DESIGN7 §2.4). -/
def checkDoctrine (c : Input) (explicit : Bool) (js : List Joined) : Result :=
  if !doctrineRowOk c explicit js then .fail .doctrineBadRow
  else checkJoined c explicit .doctrine js

/-- The runner's treatment step for a row that is not a witness row, with the joined checker as a parameter. -/
def checkTreatmentWith (cj : Input → Bool → TClaim → List Joined → Result)
    (c : Input) (explicit : Bool) (cl : TClaim) (js : List Joined) : Result :=
  match cl, js with
  | .doctrine, js => if !doctrineRowOk c explicit js then .fail .doctrineBadRow else cj c explicit .doctrine js
  | .plain, [] => check c
  | .operative, [] => checkOperative c explicit
  | cl, js => cj c explicit cl js

/-- **The runner's treatment step** (round 7): a doctrine row by `checkDoctrine`; a row with joined lines by
`checkJoined`; any other row as in round 6. -/
def checkTreatment : Input → Bool → TClaim → List Joined → Result := checkTreatmentWith checkJoined

/-- What the doctrine uniqueness test needs of a doctrine row. -/
structure DoctrineRow where
  target : Nat
  /-- the compact labels of its `doctrineTie` lines -/
  labels : List String
  /-- its check passed with the acting court's power taken as verified (the text check) -/
  text : Bool
  deriving Repr, Inhabited

/-- The compact labels of a row's `doctrineTie` lines. -/
def tieLabels (js : List Joined) : List String :=
  (js.filter (·.rel == .doctrineTie)).map (fun j => compact j.label)

/-- The targets the table ties to a label (rows whose text check passed). -/
def labelTargets (rows : List DoctrineRow) (l : String) : List Nat :=
  (rows.filter (fun r => r.text && r.labels.contains l)).map (·.target)

/-- The table ties the label to two different targets. -/
def ambiguousLabel (rows : List DoctrineRow) (l : String) : Bool :=
  match labelTargets rows l with
  | [] => false
  | t :: ts => ts.any (· != t)

def doctrineAmbiguous (rows : List DoctrineRow) (r : DoctrineRow) : Bool := r.labels.any (ambiguousLabel rows)

/-- The final verdict of a doctrine row under a rule set, from its verdict `v` there. -/
def doctrineFinal (rows : List DoctrineRow) (r : DoctrineRow) (v : Result) : Result :=
  if v.admitted && doctrineAmbiguous rows r then .fail .doctrineAmbiguous else v

/-- The class of a row in round 7: `doctrine` for a doctrine row (`doctrine`: the row has a doctrine claim and kind
`disapproved`), else round 5's `classOf`. -/
def classOf7 (explicit recognised doctrine : Bool) (quote : String) : OClass :=
  if doctrine && explicit && !recognised then .doctrine else classOf explicit recognised quote

/-- The claims of a history row (`history_claim.tsv`) and the facts the `orderHead` claim is checked against. -/
structure HClaims where
  orderHead : Bool := false
  setAside : Bool := false
  /-- the acting decision's court is the Supreme Court of the United States (court table) -/
  scotus : Bool := false
  /-- the acting decision's date (`decisions2.tsv`; 0 = unknown) -/
  date : Nat := 0
  /-- round 8 (`round8/DESIGN8.md` §5): the anchor-cue test also accepts `anchor_wide` (round 7's functions ignore
  this field) -/
  anchorWide : Bool := false
  deriving Repr, Inhabited

/-- The kinds of a Supreme Court order-list entry. -/
def orderHeadKinds : List HKind := [.certDenied, .vacated, .reversed, .affirmed, .reviewDismissed]

def orderHeadKind : Kind → Bool
  | .hist k => orderHeadKinds.contains k
  | .treat _ => false

def orderLine : Kind → List String
  | .hist k => orderLineCues k
  | .treat _ => []

/-- One order-line entry against a lower-cased quote: an entry `a ... b` (one separator " ... ") means `a`, followed
later by `b` (`hasInOrder`, as the disqualifier pairs; "petition for writ of certiorari to the … denied" with the
court's name between); any other entry is a plain substring (lead ruling D7-9). -/
def orderLineHit (q p : String) : Bool :=
  match p.splitOn " ... " with
  | [a, b] => hasInOrder q a b
  | _ => hasSub q p

/-- The quote has an order-list / judgment-line form of its kind. -/
def orderLineCue (c : Input) : Bool := (orderLine c.kind).any (orderLineHit (norm c.quote).toLower)

/-- The conditions under which an `orderHead` claim admits head matter. -/
def orderHeadOk (h : HClaims) (c : Input) : Bool :=
  h.scotus && decide (orderHeadFrom ≤ h.date) && orderHeadKind c.kind && orderLineCue c &&
    decide (c.quote.length ≤ orderHeadMaxLen)

def setAsideCue (c : Input) : Bool := setAsideCues.any (hasSub (norm c.quote).toLower)

/-- The cue test under the claims: the kind's cues, and "set aside" for a `vacated` row with a `setAside` claim. -/
def claimCueOk (h : HClaims) (c : Input) : Bool :=
  hasCue c || (h.setAside && c.kind == .hist .vacated && setAsideCue c)

/-- The part test under the claims: head matter only under an `orderHead` claim whose conditions hold. -/
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
    | none =>
      if !c.ordered then .fail .targetLater
      else match c.authority with
        | some true => .ok
        | some false => .fail .noAuthority
        | none => .okUnverifiedBy

/-- `checkAnchored` with its last step (check 6) as a parameter. -/
def anchoredThen (fin : Input → Result) (c : Input) (a : Anchor) : Result :=
  if !anchorQuoteOk c a then .fail .anchorMismatch
  else if !anchorHasCue a then .fail .anchorNoCue
  else if anchorDisqualified a then .fail .anchorDisqualified
  else if !anchorResolves c a then .fail .anchorUnresolved
  else if !anchorPartOk a then .fail .anchorPart
  else fin { c with selfText := true }

/-- A history row's check under its claims (the `orderHead` and cue tests as parameters, for the mutants). -/
def checkClaimedWith (ohOk cueOk : HClaims → Input → Bool) (h : HClaims) (c : Input) : Result :=
  checkBy (cueOk h) (claimPart ohOk h) c

def checkHistory7With (ohOk cueOk : HClaims → Input → Bool) (c : Input) (a? : Option Anchor) (h : HClaims) :
    Result :=
  match a? with
  | some a => anchoredThen (checkClaimedWith ohOk cueOk h) c a
  | none => checkClaimedWith ohOk cueOk h c

/-- **The runner's history step** (round 7): `checkHistory` under the row's claims. -/
def checkHistory7 : Input → Option Anchor → HClaims → Result := checkHistory7With orderHeadOk claimCueOk

/-! ### Theorems: joined certificates -/

/-- The six checks as booleans (the form the other theorems unpack). -/
theorem checkJoined_admitted_bool (c : Input) (e : Bool) (cl : TClaim) (js : List Joined) :
    (checkJoined c e cl js).admitted = true ↔
      ((joinedCountOk js && js.all (joinedQuoteOk c)) = true ∧ js.all joinedPartOk = true ∧
        js.any (joinedDisqualified c) = false ∧ js.all (relationOk cl c) = true ∧
        js.any (joinedResolves c) = true ∧ (mainCheck { c with selfText := true } e cl).admitted = true) := by
  unfold checkJoined
  by_cases h1 : (joinedCountOk js && js.all (joinedQuoteOk c)) = true
  · by_cases h2 : js.all joinedPartOk = true
    · by_cases h3 : js.any (joinedDisqualified c) = true
      · simp only [h1, h2, h3, Bool.not_true, Bool.false_eq_true, ↓reduceIte, Result.admitted]
        simp
      · have h3' : js.any (joinedDisqualified c) = false := by simpa using h3
        by_cases h4 : js.all (relationOk cl c) = true
        · by_cases h5 : js.any (joinedResolves c) = true
          · simp only [h1, h2, h3', h4, h5, Bool.not_true, Bool.false_eq_true, ↓reduceIte, true_and]
          · have h5' : js.any (joinedResolves c) = false := by simpa using h5
            simp only [h1, h2, h3', h4, h5', Bool.not_true, Bool.not_false, Bool.false_eq_true, ↓reduceIte,
              Result.admitted]
            simp
        · have h4' : js.all (relationOk cl c) = false := by simpa using h4
          simp only [h1, h2, h3', h4', Bool.not_true, Bool.not_false, Bool.false_eq_true, ↓reduceIte,
            Result.admitted]
          simp
    · have h2' : js.all joinedPartOk = false := by simpa using h2
      simp only [h1, h2', Bool.not_true, Bool.not_false, Bool.false_eq_true, ↓reduceIte, Result.admitted]
      simp
  · have h1' : (joinedCountOk js && js.all (joinedQuoteOk c)) = false := by simpa using h1
    simp only [h1', Bool.not_false, ↓reduceIte, Result.admitted]
    simp

/-- **Admission is exactly the six checks** (with the count bound in check 1). -/
theorem checkJoined_admitted_iff (c : Input) (e : Bool) (cl : TClaim) (js : List Joined) :
    (checkJoined c e cl js).admitted = true ↔
      (joinedCountOk js = true ∧ (∀ j ∈ js, joinedQuoteOk c j = true) ∧ (∀ j ∈ js, joinedPartOk j = true) ∧
        (∀ j ∈ js, joinedDisqualified c j = false) ∧ (∀ j ∈ js, relationOk cl c j = true) ∧
        (∃ j ∈ js, joinedResolves c j = true) ∧ (mainCheck { c with selfText := true } e cl).admitted = true) := by
  rw [checkJoined_admitted_bool]
  simp only [Bool.and_eq_true, List.all_eq_true, List.any_eq_true, List.any_eq_false, Bool.not_eq_true, and_assoc]

/-- A joined quote that passes check 1 sits in a usable window of the row's own text. -/
theorem joinedQuoteOk_window (c : Input) (j : Joined) (h : joinedQuoteOk c j = true) :
    ∃ w, coveringWindow (j.input c) = some w ∧ w ∈ c.windows ∧ usable (j.input c) w = true ∧
      quoteAt (j.input c) w = true := by
  unfold joinedQuoteOk quoteOk at h
  cases hw : coveringWindow (j.input c) with
  | none => simp [hw] at h
  | some w =>
    have hf : (j.input c).windows.find? (fun w => usable (j.input c) w && quoteAt (j.input c) w) = some w := hw
    have hp := List.find?_some hf
    simp only [Bool.and_eq_true] at hp
    exact ⟨w, rfl, List.mem_of_find?_eq_some hf, hp.1, hp.2⟩

/-- **Joined soundness**: every joined quote at its offset in a usable window of the row's own text, from the
opinion of the court, without disqualifier, its relation holding; the evidence in one joined quote; the main check
with the evidence taken as given admits, and its verdict is the row's. -/
theorem checkJoined_sound (c : Input) (e : Bool) (cl : TClaim) (js : List Joined)
    (h : (checkJoined c e cl js).admitted = true) :
    (∀ j ∈ js, ∃ w, coveringWindow (j.input c) = some w ∧ w ∈ c.windows ∧ usable (j.input c) w = true ∧
        quoteAt (j.input c) w = true) ∧
      (∀ j ∈ js, joinedPartOk j = true) ∧ (∀ j ∈ js, joinedDisqualified c j = false) ∧
      (∀ j ∈ js, relationOk cl c j = true) ∧ (∃ j ∈ js, joinedResolves c j = true) ∧
      (mainCheck { c with selfText := true } e cl).admitted = true ∧
      checkJoined c e cl js = mainCheck { c with selfText := true } e cl := by
  obtain ⟨_, hq, hp, hd, hr, hv, hm⟩ := (checkJoined_admitted_iff c e cl js).mp h
  obtain ⟨b1, b2, b3, b4, b5, _⟩ := (checkJoined_admitted_bool c e cl js).mp h
  refine ⟨fun j hj => joinedQuoteOk_window c j (hq j hj), hp, hd, hr, hv, hm, ?_⟩
  unfold checkJoined
  simp only [b1, b2, b3, b4, b5, Bool.not_true, Bool.false_eq_true, ↓reduceIte]

/-- **One or two joined lines.** -/
theorem checkJoined_bounded (c : Input) (e : Bool) (cl : TClaim) (js : List Joined)
    (h : (checkJoined c e cl js).admitted = true) : 1 ≤ js.length ∧ js.length ≤ 2 := by
  have h1 := ((checkJoined_admitted_iff c e cl js).mp h).1
  simp only [joinedCountOk, Bool.and_eq_true, decide_eq_true_eq] at h1
  exact h1

/-- **Citation index**: with a citation index and `cite:` evidence, an admitted joined row's citation is one the
index resolves to the row's target node. -/
theorem checkJoined_cite_index (c : Input) (e : Bool) (cl : TClaim) (js : List Joined)
    (h : (checkJoined c e cl js).admitted = true) (hc : c.evidence.startsWith "cite:" = true)
    (m : Std.HashMap String Nat) (hm : c.citeIndex = some m) :
    m.get? (compact (c.evidence.drop 5).toString) = some c.target := by
  obtain ⟨j, _, hr⟩ := (checkJoined_sound c e cl js h).2.2.2.2.1
  simp only [joinedResolves, anchorResolves, hc, ↓reduceIte, Bool.and_eq_true] at hr
  have h2 := hr.2
  simp only [citeResolves, hm, beq_iff_eq] at h2
  exact h2

/-- **Joined window hash**: every joined quote sits in a well-formed window whose SHA-1, computed by the checker,
is the recorded digest; when the hash file is supplied a digest must have been recorded. -/
theorem checkJoined_window_hash (c : Input) (e : Bool) (cl : TClaim) (js : List Joined)
    (h : (checkJoined c e cl js).admitted = true) :
    ∀ j ∈ js, ∃ w, coveringWindow (j.input c) = some w ∧ quoteAt (j.input c) w = true ∧
      wellFormed (j.input c) w = true ∧ (∀ s, w.hash = some s → Sha1.hex w.text = s) ∧
      (c.hashRequired = true → w.hash.isSome = true) := by
  intro j hj
  obtain ⟨w, hw, _, hu, hq⟩ := (checkJoined_sound c e cl js h).1 j hj
  simp only [usable, Bool.and_eq_true] at hu
  obtain ⟨hwf, hh⟩ := hu
  refine ⟨w, hw, hq, hwf, ?_, ?_⟩
  · intro s hs
    simp only [hashOk, hs, beq_iff_eq] at hh
    rw [← w.digest_eq]
    exact hh
  · intro hr
    have hr' : (j.input c).hashRequired = true := hr
    cases hwh : w.hash with
    | some _ => rfl
    | none => simp [hashOk, hwh, hr'] at hh

/-- **Joined quotes are non-empty**, each at a non-empty span. -/
theorem checkJoined_quote_nonempty (c : Input) (e : Bool) (cl : TClaim) (js : List Joined)
    (h : (checkJoined c e cl js).admitted = true) : ∀ j ∈ js, j.quote ≠ "" ∧ j.start < j.stop := by
  intro j hj
  obtain ⟨w, _, _, _, hq⟩ := (checkJoined_sound c e cl js h).1 j hj
  unfold quoteAt at hq
  have hq' : (decide (j.start < j.stop) && j.quote != "" &&
      slice (norm w.text) (j.start - w.start0) (j.stop - j.start) == norm j.quote) = true := hq
  simp only [Bool.and_eq_true, decide_eq_true_eq, bne_iff_ne, ne_eq] at hq'
  exact ⟨hq'.1.2, hq'.1.1⟩

/-- The main check admits only if `check` admits the main quote read in the row's mode. -/
theorem mainCheck_check (c : Input) (e : Bool) (cl : TClaim) (h : (mainCheck c e cl).admitted = true) :
    (check (cl.apply c)).admitted = true := by
  cases cl with
  | plain => exact h
  | operative => exact (checkOperative_sound c e h).2.2.1
  | doctrine => exact h

/-- **The main quote of an admitted joined row**: every conjunct of `checkCert_sound` except `resolves` (a joined
quote carries the target evidence), read in the row's mode: a known hash, the quote at its offset in a usable window,
a cue, no disqualifier, an allowed part, the date order. -/
theorem checkJoined_disposition (c : Input) (e : Bool) (cl : TClaim) (js : List Joined)
    (h : (checkJoined c e cl js).admitted = true) :
    shaOk c = true ∧ (∃ w, coveringWindow c = some w ∧ quoteAt c w = true) ∧ hasCue (cl.apply c) = true ∧
      disqualified (cl.apply c) = false ∧ partOk c = true ∧ c.ordered = true := by
  have hm := mainCheck_check _ e cl (checkJoined_sound c e cl js h).2.2.2.2.2.1
  cases cl with
  | plain =>
    obtain ⟨s1, s2, s3, s4, _, s6, s7, _⟩ := checkCert_sound _ hm
    exact ⟨s1, s2, s3, s4, s6, s7⟩
  | operative =>
    obtain ⟨s1, s2, s3, s4, _, s6, s7, _⟩ := checkCert_sound _ hm
    exact ⟨s1, s2, s3, s4, s6, s7⟩
  | doctrine =>
    obtain ⟨s1, s2, s3, s4, _, s6, s7, _⟩ := checkCert_sound _ hm
    exact ⟨s1, s2, s3, s4, s6, s7⟩

/-- **Antecedent**: an admitted row's `antecedent` quote ends before the main quote and at most `joinedGapMax`
(300, cue table) characters before it; the main quote has an anaphor and a cue of the row's kind. -/
theorem antecedent_gap (c : Input) (e : Bool) (cl : TClaim) (js : List Joined)
    (h : (checkJoined c e cl js).admitted = true) (j : Joined) (hj : j ∈ js) (hr : j.rel = .antecedent) :
    j.stop ≤ c.start ∧ c.start - j.stop ≤ joinedGapMax ∧ anaphorCue c.quote = true ∧ kindCue c = true := by
  have h4 := (checkJoined_sound c e cl js h).2.2.2.1 j hj
  simp only [relationOk, hr, antecedentOk, Bool.and_eq_true, decide_eq_true_eq] at h4
  exact ⟨h4.1.1.1, h4.1.1.2, h4.1.2, h4.2⟩

/-- **Doctrine tie**: an admitted row's `doctrineTie` line is on a doctrine row; its label has two words or more and
eight characters or more and occurs in both quotes; the joined quote has a tie cue. -/
theorem doctrineTie_label (c : Input) (e : Bool) (cl : TClaim) (js : List Joined)
    (h : (checkJoined c e cl js).admitted = true) (j : Joined) (hj : j ∈ js) (hr : j.rel = .doctrineTie) :
    cl = .doctrine ∧ labelOk j.label = true ∧ labelIn c.quote j.label = true ∧ labelIn j.quote j.label = true ∧
      tieCue j.quote = true := by
  have h4 := (checkJoined_sound c e cl js h).2.2.2.1 j hj
  simp only [relationOk, hr, tieOk, Bool.and_eq_true, beq_iff_eq] at h4
  exact ⟨h4.1.1.1.1, h4.1.1.1.2, h4.1.1.2, h4.1.2, h4.2⟩

/-- **Doctrine rows**: an admitted doctrine row is an explicit `disapproved` row with a `doctrineTie` line that
passes the joined check in doctrine mode: its main quote has a doctrine-reject cue and none of the treatment and
operative disqualifiers. -/
theorem checkDoctrine_sound (c : Input) (e : Bool) (js : List Joined) (h : (checkDoctrine c e js).admitted = true) :
    c.kind = .treat .disapproved ∧ e = true ∧ (∃ j ∈ js, j.rel = .doctrineTie) ∧
      (checkJoined c e .doctrine js).admitted = true ∧ hasCue { c with mode := .doctrine } = true ∧
      disqualified { c with mode := .doctrine } = false := by
  unfold checkDoctrine at h
  by_cases h0 : doctrineRowOk c e js = true
  · simp only [h0, Bool.not_true, Bool.false_eq_true, ↓reduceIte] at h
    have h0' := h0
    simp only [doctrineRowOk, Bool.and_eq_true, beq_iff_eq, List.any_eq_true] at h0'
    obtain ⟨⟨hk, he⟩, j, hj, hjr⟩ := h0'
    have hd := checkJoined_disposition c e .doctrine js h
    exact ⟨hk, he, ⟨j, hj, hjr⟩, h, hd.2.2.1, hd.2.2.2.1⟩
  · simp [h0, Result.admitted] at h

/-- **A row with joined lines is the joined check's**: under the round-7 treatment step, an admitted row with
joined lines passes `checkJoined` (a doctrine row in doctrine mode). -/
theorem checkTreatment_joined (c : Input) (e : Bool) (cl : TClaim) (js : List Joined) (hj : js ≠ [])
    (h : (checkTreatment c e cl js).admitted = true) : (checkJoined c e cl js).admitted = true := by
  cases cl with
  | doctrine =>
    have h' : (checkDoctrine c e js).admitted = true := h
    exact (checkDoctrine_sound c e js h').2.2.2.1
  | plain =>
    cases js with
    | nil => exact absurd rfl hj
    | cons j js => exact h
  | operative =>
    cases js with
    | nil => exact absurd rfl hj
    | cons j js => exact h

/-- `check` admits with the power taken as verified whenever it admits. -/
theorem check_text (c : Input) (h : (check c).admitted = true) :
    (check { c with authority := some true }).admitted = true := by
  obtain ⟨h1, ⟨w, hw, hq⟩, h3, h4, h5, h6, h7, _, _⟩ := checkCert_sound c h
  have hp := List.find?_some hw
  simp only [Bool.and_eq_true] at hp
  have hmem : w ∈ c.windows := List.mem_of_find?_eq_some hw
  have hu : usable c w = true := hp.1
  have hwf : wellFormed c w = true := by
    simp only [usable, Bool.and_eq_true] at hu
    exact hu.1
  have hq' : quoteOk c = true := by simp [quoteOk, hw, hq]
  have hwa : c.windows.any (wellFormed c) = true := List.any_eq_true.mpr ⟨w, hmem, hwf⟩
  have hua : c.windows.any (usable c) = true := List.any_eq_true.mpr ⟨w, hmem, hu⟩
  have e : check { c with authority := some true } = .ok := by
    show (if !shaOk c then Result.fail .shaUnknown
      else if !(c.windows.any (wellFormed c)) then .fail .noWindow
      else if !(c.windows.any (usable c)) then .fail .windowHash
      else if !quoteOk c then .fail .quoteMismatch
      else if !hasCue c then .fail .noCue
      else if disqualified c then .fail .disqualified
      else if !resolves c then .fail .targetUnresolved
      else if !partOk c then .fail .partNotMajority
      else if !c.ordered then .fail .targetLater
      else Result.ok) = .ok
    simp [h1, hwa, hua, hq', h3, h4, h5, h6, h7]
  rw [e]; rfl

/-- The main check admits with the power taken as verified whenever it admits. -/
theorem mainCheck_text (c : Input) (e : Bool) (cl : TClaim) (h : (mainCheck c e cl).admitted = true) :
    (mainCheck { c with authority := some true } e cl).admitted = true := by
  cases cl with
  | plain => exact check_text c h
  | doctrine => exact check_text { c with mode := .doctrine } h
  | operative =>
    unfold mainCheck checkOperative at h ⊢
    by_cases h0 : (c.kind == .treat .disapproved && e) = true
    · have h0' : ({ c with authority := some true }.kind == .treat .disapproved && e) = true := h0
      simp only [h0, Bool.not_true, Bool.false_eq_true, ↓reduceIte] at h
      simp only [h0', Bool.not_true, Bool.false_eq_true, ↓reduceIte]
      exact check_text { c with mode := .operative } h
    · simp [h0, Result.admitted] at h

/-- The joined check admits with the power taken as verified whenever it admits. -/
theorem checkJoined_text (c : Input) (e : Bool) (cl : TClaim) (js : List Joined)
    (h : (checkJoined c e cl js).admitted = true) :
    (checkJoined { c with authority := some true } e cl js).admitted = true := by
  obtain ⟨b1, b2, b3, b4, b5, b6⟩ := (checkJoined_admitted_bool c e cl js).mp h
  exact (checkJoined_admitted_bool { c with authority := some true } e cl js).mpr
    ⟨b1, b2, b3, b4, b5, mainCheck_text { c with selfText := true } e cl b6⟩

/-- **The text check**: a treatments row admitted under a rule set is admitted with the acting court's power taken
as verified (so the doctrine collision set, which is read on the text check, holds every admitted doctrine row). -/
theorem checkTreatment_text (c : Input) (e : Bool) (cl : TClaim) (js : List Joined)
    (h : (checkTreatment c e cl js).admitted = true) :
    (checkTreatment { c with authority := some true } e cl js).admitted = true := by
  cases cl with
  | doctrine =>
    have h' : (checkDoctrine c e js).admitted = true := h
    show (checkDoctrine { c with authority := some true } e js).admitted = true
    unfold checkDoctrine at h' ⊢
    by_cases h0 : doctrineRowOk c e js = true
    · have h0' : doctrineRowOk { c with authority := some true } e js = true := h0
      simp only [h0, Bool.not_true, Bool.false_eq_true, ↓reduceIte] at h'
      simp only [h0', Bool.not_true, Bool.false_eq_true, ↓reduceIte]
      exact checkJoined_text c e .doctrine js h'
    · simp [h0, Result.admitted] at h'
  | plain =>
    cases js with
    | nil => exact check_text c h
    | cons j js => exact checkJoined_text c e .plain (j :: js) h
  | operative =>
    cases js with
    | nil => exact mainCheck_text c e .operative h
    | cons j js => exact checkJoined_text c e .operative (j :: js) h

/-! ### Theorems: doctrine uniqueness -/

/-- **Doctrine uniqueness**: two doctrine rows admitted after the table's uniqueness test, each admitted only when
its text check passed, that share a compact label have the same target. -/
theorem doctrine_unique (rows : List DoctrineRow) (r1 r2 : DoctrineRow) (h1 : r1 ∈ rows) (h2 : r2 ∈ rows)
    (v1 v2 : Result) (a1 : (doctrineFinal rows r1 v1).admitted = true) (a2 : (doctrineFinal rows r2 v2).admitted = true)
    (t1 : v1.admitted = true → r1.text = true) (t2 : v2.admitted = true → r2.text = true)
    (l : String) (hl1 : l ∈ r1.labels) (hl2 : l ∈ r2.labels) : r1.target = r2.target := by
  have fin : ∀ (r : DoctrineRow) (v : Result), (doctrineFinal rows r v).admitted = true →
      v.admitted = true ∧ doctrineAmbiguous rows r = false := by
    intro r v hv
    unfold doctrineFinal at hv
    by_cases hb : (v.admitted && doctrineAmbiguous rows r) = true
    · rw [if_pos hb] at hv
      exact absurd hv (by simp [Result.admitted])
    · rw [if_neg hb] at hv
      refine ⟨hv, ?_⟩
      cases hd : doctrineAmbiguous rows r
      · rfl
      · simp [hv, hd] at hb
  obtain ⟨v1a, n1⟩ := fin r1 v1 a1
  obtain ⟨v2a, _⟩ := fin r2 v2 a2
  have hn : ambiguousLabel rows l = false := by
    unfold doctrineAmbiguous at n1
    rw [List.any_eq_false] at n1
    simpa using n1 l hl1
  have mem : ∀ r ∈ rows, r.text = true → l ∈ r.labels → r.target ∈ labelTargets rows l := by
    intro r hr ht hl
    unfold labelTargets
    exact List.mem_map.mpr ⟨r, List.mem_filter.mpr ⟨hr, by simp [ht, hl]⟩, rfl⟩
  have m1 := mem r1 h1 (t1 v1a) hl1
  have m2 := mem r2 h2 (t2 v2a) hl2
  unfold ambiguousLabel at hn
  generalize hL : labelTargets rows l = L at m1 m2 hn
  cases L with
  | nil => simp at m1
  | cons t ts =>
    have hn2 : ts.any (· != t) = false := hn
    have hall : ∀ x ∈ ts, x = t := by
      intro x hx
      have := List.any_eq_false.mp hn2 x hx
      simpa using this
    have e1 : r1.target = t := by
      rcases List.mem_cons.mp m1 with h | h
      · exact h
      · exact hall _ h
    have e2 : r2.target = t := by
      rcases List.mem_cons.mp m2 with h | h
      · exact h
      · exact hall _ h
    rw [e1, e2]

/-- The runner decides a label's ambiguity on the rows that carry it (a bucket per label); that is the same answer
as on the whole table. -/
theorem ambiguousLabel_filter (rows : List DoctrineRow) (l : String) :
    ambiguousLabel (rows.filter (fun r => r.labels.contains l)) l = ambiguousLabel rows l := by
  have e : labelTargets (rows.filter (fun r => r.labels.contains l)) l = labelTargets rows l := by
    unfold labelTargets
    rw [List.filter_filter]
    congr 1
    apply List.filter_congr
    intro r _
    simp only [Bool.and_assoc, Bool.and_self]
  unfold ambiguousLabel
  rw [e]

/-! ### Theorems: no change without joined lines or claims; classes -/

/-- `checkBy` with the kind's cues and the plain part test is `check`. -/
theorem checkBy_check (c : Input) :
    checkBy hasCue (fun c => if partOk c then none else some .partNotMajority) c = check c := by
  unfold checkBy check
  by_cases hp : partOk c = true <;> simp [hp]

/-- **No joined line, no claim: no change.** A treatments row without joined lines (no doctrine claim) gets the
round-6 verdict (`check`, or `checkOperative` for an operative-words claim); a history row without claims gets
`checkHistory`'s (plain or anchored). -/
theorem no_joined_no_change (c : Input) (e : Bool) (a? : Option Anchor) (h : HClaims)
    (ho : h.orderHead = false) (hs : h.setAside = false) :
    checkTreatment c e .plain [] = check c ∧ checkTreatment c e .operative [] = checkOperative c e ∧
      checkHistory7 c a? h = checkHistory c a? := by
  have hcl : checkClaimedWith orderHeadOk claimCueOk h = check := by
    funext x
    have e1 : claimCueOk h = hasCue := by
      funext y; simp [claimCueOk, hs]
    have e2 : claimPart orderHeadOk h = (fun c => if partOk c then none else some .partNotMajority) := by
      funext y; simp [claimPart, ho]
    unfold checkClaimedWith
    rw [e1, e2]
    exact checkBy_check x
  refine ⟨rfl, rfl, ?_⟩
  cases a? with
  | none =>
    show checkClaimedWith orderHeadOk claimCueOk h c = check c
    rw [hcl]
  | some a =>
    show anchoredThen (checkClaimedWith orderHeadOk claimCueOk h) c a = checkAnchored c a
    rw [hcl]
    rfl

/-- **Without a doctrine row the class is round 5's.** -/
theorem classOf7_no_doctrine (e r : Bool) (q : String) : classOf7 e r false q = classOf e r q := by
  simp [classOf7]

/-! ### Theorems: history claims -/

/-- An admitted `checkBy` row passed the cue test it was given and the part test it was given. -/
theorem checkBy_cue_part (cueOk : Input → Bool) (partRes : Input → Option Reason) (c : Input)
    (h : (checkBy cueOk partRes c).admitted = true) : cueOk c = true ∧ partRes c = none := by
  unfold checkBy at h
  by_cases h1 : shaOk c = true
  · by_cases h2 : c.windows.any (wellFormed c) = true
    · by_cases h3 : c.windows.any (usable c) = true
      · by_cases h4 : quoteOk c = true
        · by_cases h5 : cueOk c = true
          · by_cases h6 : disqualified c = true
            · simp [h1, h2, h3, h4, h5, h6, Result.admitted] at h
            · by_cases h7 : resolves c = true
              · refine ⟨h5, ?_⟩
                cases hp : partRes c with
                | none => rfl
                | some r => simp [h1, h2, h3, h4, h5, h6, h7, hp, Result.admitted] at h
              · simp [h1, h2, h3, h4, h5, h6, h7, Result.admitted] at h
          · simp [h1, h2, h3, h4, h5, Result.admitted] at h
        · simp [h1, h2, h3, h4, Result.admitted] at h
      · simp [h1, h2, h3, Result.admitted] at h
    · simp [h1, h2, Result.admitted] at h
  · simp [h1, Result.admitted] at h

/-- An admitted `anchoredThen` row passed its last step on the row's input with the evidence taken as given. -/
theorem anchoredThen_fin (fin : Input → Result) (c : Input) (a : Anchor) (h : (anchoredThen fin c a).admitted = true) :
    (fin { c with selfText := true }).admitted = true := by
  unfold anchoredThen at h
  by_cases h1 : anchorQuoteOk c a = true
  · by_cases h2 : anchorHasCue a = true
    · by_cases h3 : anchorDisqualified a = true
      · simp [h1, h2, h3, Result.admitted] at h
      · by_cases h4 : anchorResolves c a = true
        · by_cases h5 : anchorPartOk a = true
          · simpa [h1, h2, h3, h4, h5] using h
          · simp [h1, h2, h3, h4, h5, Result.admitted] at h
        · simp [h1, h2, h3, h4, Result.admitted] at h
    · simp [h1, h2, Result.admitted] at h
  · simp [h1, Result.admitted] at h

/-- **What a history row's claims let through**: an admitted row passed the cue test under its claims, and its part
is the opinion of the court or head matter under an `orderHead` claim whose conditions hold. -/
theorem checkHistory7_claims (c : Input) (a? : Option Anchor) (h : HClaims)
    (hadm : (checkHistory7 c a? h).admitted = true) :
    claimCueOk h c = true ∧ (partOk c = true ∨ (c.part = "headmatter" ∧ h.orderHead = true ∧ orderHeadOk h c = true)) := by
  have key : ∀ x : Input, (checkClaimedWith orderHeadOk claimCueOk h x).admitted = true →
      claimCueOk h x = true ∧ (partOk x = true ∨ (x.part = "headmatter" ∧ h.orderHead = true ∧ orderHeadOk h x = true)) := by
    intro x hx
    obtain ⟨hc, hp⟩ := checkBy_cue_part _ _ x hx
    refine ⟨hc, ?_⟩
    unfold claimPart at hp
    by_cases h1 : partOk x = true
    · exact Or.inl h1
    · right
      by_cases h2 : (x.part == "headmatter" && h.orderHead) = true
      · have h2' := h2
        simp only [Bool.and_eq_true, beq_iff_eq] at h2'
        simp only [h1, h2, Bool.false_eq_true, ↓reduceIte] at hp
        by_cases h3 : orderHeadOk h x = true
        · exact ⟨h2'.1, h2'.2, h3⟩
        · simp [h3] at hp
      · simp [h1, h2] at hp
  cases a? with
  | none => exact key c hadm
  | some a => exact key { c with selfText := true } (anchoredThen_fin _ c a hadm)

/-- **orderHead**: an admitted history row whose quote is head matter has the `orderHead` claim, a Supreme Court
acting decision dated on or after `orderHeadFrom` (20130101), a listed kind, an order-line cue of its kind, and at
most `orderHeadMaxLen` (400) characters. -/
theorem orderHead_sound (c : Input) (a? : Option Anchor) (h : HClaims)
    (hadm : (checkHistory7 c a? h).admitted = true) (hp : c.part = "headmatter") :
    h.orderHead = true ∧ h.scotus = true ∧ orderHeadFrom ≤ h.date ∧ orderHeadKind c.kind = true ∧
      orderLineCue c = true ∧ c.quote.length ≤ orderHeadMaxLen := by
  have hpo : partOk c = false := by simp [partOk, hp]
  rcases (checkHistory7_claims c a? h hadm).2 with h1 | ⟨_, ho, hok⟩
  · rw [hpo] at h1; exact absurd h1 Bool.false_ne_true
  · simp only [orderHeadOk, Bool.and_eq_true, decide_eq_true_eq] at hok
    exact ⟨ho, hok.1.1.1.1, hok.1.1.1.2, hok.1.1.2, hok.1.2, hok.2⟩

/-- **No claim, no head matter**: without an `orderHead` claim a head-matter quote fails as before. -/
theorem orderHead_no_claim (c : Input) (a? : Option Anchor) (h : HClaims) (ho : h.orderHead = false)
    (hp : c.part = "headmatter") : (checkHistory7 c a? h).admitted = false := by
  cases hx : (checkHistory7 c a? h).admitted with
  | false => rfl
  | true =>
    exfalso
    have hpo : partOk c = false := by simp [partOk, hp]
    rcases (checkHistory7_claims c a? h hx).2 with h1 | ⟨_, h2, _⟩
    · rw [hpo] at h1; exact Bool.false_ne_true h1
    · rw [ho] at h2; exact Bool.false_ne_true h2

/-- **setAside only on vacated rows**: an admitted history row whose quote has no cue of its kind is a `vacated`
row with a `setAside` claim and a set-aside phrase. -/
theorem setAside_only_vacated (c : Input) (a? : Option Anchor) (h : HClaims)
    (hadm : (checkHistory7 c a? h).admitted = true) (hc : hasCue c = false) :
    h.setAside = true ∧ c.kind = .hist .vacated ∧ setAsideCue c = true := by
  have h1 := (checkHistory7_claims c a? h hadm).1
  simp only [claimCueOk, hc, Bool.false_or, Bool.and_eq_true, beq_iff_eq] at h1
  exact ⟨h1.1.1, h1.1.2, h1.2⟩

/-- **No claim, no set aside**: without a `setAside` claim an admitted history row has a cue of its kind. -/
theorem setAside_no_claim (c : Input) (a? : Option Anchor) (h : HClaims) (hs : h.setAside = false)
    (hadm : (checkHistory7 c a? h).admitted = true) : hasCue c = true := by
  have h1 := (checkHistory7_claims c a? h hadm).1
  simpa [claimCueOk, hs] using h1

/-! ## Round 8: bridge evidence for history rows, wide anchor cues (`round8/DESIGN8.md` §4–5, `LEAN8.md`)

**Bridge evidence** (§4). A Supreme Court order O names only its own docket; the decision below X is identified by a
third text W whose subsequent-history clause cites X and then the order ("X, 123 F.3d 456 (5th Cir. 2015), cert.
denied, 577 U.S. 1001"). A history row with a line in `history_bridge.tsv` is checked in order (the first failure
is the reason; no fall-back to the plain check):

1. `bridgeMismatch` the bridge quote is the text of a usable window of W's own text at its offset, non-empty, at most
                    `bridgeMaxLen` (600) characters;
2. `bridgeDate`     date(O) and date(W) are known and date(O) ≤ date(W);
3. `bridgeClause`   the quote (normalised) has no ";";
4. `bridgeTarget`   a key of the citation index that maps to X occurs in the quote's alphanumeric characters; p1 is
                    the position of the first such;
5. `bridgeCue`      a bridge cue of the row's kind begins at a position p2 > p1 (the first such);
5b. `bridgeChain`   (D8-9) no key of the index begins between the end of X's citation and p2 (no other citation:
                    "X, aff'd, Y, cert. denied, O" is refused, O acted on Y);
6. `bridgeActor`    the first key that begins after p2 (the longest key at that position) maps to O;
7. the row's own check under its claims, the target evidence taken as given (`selfText := true`).

Positions are characters of the normalised, lower-cased quote (LEAN8 L8-1). **Wide anchor cues** (§5): an anchored
row with the claim `anchorWide` passes the anchor-cue test with `anchor ++ anchor_wide`. -/

/-- The first suffix of `l` (longest first) that satisfies `p`. -/
def firstSuffix {α : Type} (p : List α → Bool) : List α → Option (List α)
  | [] => none
  | a :: t => if p (a :: t) then some (a :: t) else firstSuffix p t

/-- `p` holds of every suffix of `l` (`[]` included). -/
def allSuffix {α : Type} (p : List α → Bool) : List α → Bool
  | [] => p []
  | a :: t => p (a :: t) && allSuffix p t

/-- The alphanumeric characters of `s` with their positions in `s` (counting from `i`). -/
def alnumPos : List Char → Nat → List (Char × Nat)
  | [], _ => []
  | ch :: t, i => if ch.isAlphanum then (ch, i) :: alnumPos t (i + 1) else alnumPos t (i + 1)

/-- The bridge line of a history row (`history_bridge.tsv`) with the facts it is checked against. -/
structure Bridge where
  /-- the bridge text's node W -/
  w : Nat
  /-- W's text hash (`decisions2.tsv`; "" unknown) -/
  wSha : String
  /-- the windows supplied for W's text -/
  windows : List Window
  start : Nat
  stop : Nat
  quote : String
  /-- date(W), date(O) (`decisions2.tsv`; 0 = unknown) -/
  wDate : Nat := 0
  oDate : Nat := 0
  /-- the row's acting node O -/
  actor : Nat := 0
  /-- the key lengths of the citation index, longest first (LEAN8 L8-3) -/
  lens : List Nat := []
  deriving Inhabited

/-- The bridge quote read over W's text: W's hash and windows; the bridge span and quote. -/
def Bridge.input (b : Bridge) (c : Input) : Input :=
  { c with textSha := b.wSha, shas := [b.wSha], windows := b.windows, start := b.start, stop := b.stop,
           quote := b.quote }

/-- Step 1. -/
def bridgeQuoteOk (c : Input) (b : Bridge) : Bool := decide (b.stop - b.start ≤ bridgeMaxLen) && quoteOk (b.input c)
/-- Step 2. -/
def bridgeDateOk (b : Bridge) : Bool := decide (0 < b.oDate) && decide (0 < b.wDate) && decide (b.oDate ≤ b.wDate)
/-- Step 3. -/
def bridgeClauseOk (b : Bridge) : Bool := !hasSub (norm b.quote) ";"

/-- The normalised, lower-cased bridge quote. -/
def bridgeText (b : Bridge) : List Char := (norm b.quote).toLower.toList
/-- Its alphanumeric characters with their positions (their string is the compact quote). -/
def bridgeAlnum (b : Bridge) : List (Char × Nat) := alnumPos (bridgeText b) 0
def headPos (s : List (Char × Nat)) : Option Nat := s.head?.map (·.2)

/-- The node the index gives the key made of the first `L` characters of `s` (none: no such key). -/
def citeOf (m : Std.HashMap String Nat) (s : List (Char × Nat)) (L : Nat) : Option Nat :=
  if 0 < L ∧ (s.take L).length = L then m.get? (String.ofList ((s.take L).map (·.1))) else none

/-- The citation that begins at the head of `s`: the first length (longest first) that is a key. -/
def citeFirst (m : Std.HashMap String Nat) (lens : List Nat) (s : List (Char × Nat)) : Option Nat :=
  lens.findSome? (citeOf m s)

/-- The step-4 test on a suffix: some key at its head maps to X. -/
def xHere (m : Std.HashMap String Nat) (c : Input) (b : Bridge) (s : List (Char × Nat)) : Bool :=
  b.lens.any (fun L => citeOf m s L == some c.target)

/-- Step 4: the position of the first key that maps to X. -/
def bridgeP1 (c : Input) (b : Bridge) : Option Nat :=
  match c.citeIndex with
  | none => none
  | some m => (firstSuffix (xHere m c b) (bridgeAlnum b)).bind headPos

/-- The position after the last character of the key of length `L` at the head of `s`. -/
def keyEnd (s : List (Char × Nat)) (L : Nat) : Nat := ((s.take L).getLast?.map (·.2 + 1)).getD 0

/-- Step 5b: the end of X's citation (the longest key at p1 that maps to X). -/
def bridgeXEnd (c : Input) (b : Bridge) : Option Nat :=
  match c.citeIndex with
  | none => none
  | some m =>
    match firstSuffix (xHere m c b) (bridgeAlnum b) with
    | none => none
    | some s => (b.lens.find? (fun L => citeOf m s L == some c.target)).map (keyEnd s)

/-- Step 5b: no key begins at a position in `[e, p2)`. -/
def noKeyBetween (c : Input) (b : Bridge) (e p2 : Nat) : Bool :=
  match c.citeIndex with
  | none => false
  | some m => allSuffix (fun s =>
      match headPos s with
      | some p => !(decide (e ≤ p) && decide (p < p2)) || (citeFirst m b.lens s).isNone
      | none => true) (bridgeAlnum b)

def bridgeChainOk (c : Input) (b : Bridge) (p2 : Nat) : Bool :=
  match bridgeXEnd c b with
  | some e => noKeyBetween c b e p2
  | none => false

def bridgeCue : Kind → List String
  | .hist k => bridgeCues k
  | .treat _ => []

/-- A bridge cue of kind `k` begins at the head of `q`. -/
def cueHere (k : Kind) (q : List Char) : Bool := (bridgeCue k).any (fun ph => !ph.isEmpty && ph.toList.isPrefixOf q)

/-- The first position `i > p1` (walking `q` from position `i`) at which a cue begins. -/
def firstCue (k : Kind) (p1 : Nat) : List Char → Nat → Option Nat
  | [], _ => none
  | ch :: t, i => if decide (p1 < i) && cueHere k (ch :: t) then some i else firstCue k p1 t (i + 1)

/-- Step 5. -/
def bridgeP2 (c : Input) (b : Bridge) (p1 : Nat) : Option Nat := firstCue c.kind p1 (bridgeText b) 0

/-- The first citation (position, node) that begins at a position satisfying `ok`. -/
def actorCiteWhere (c : Input) (b : Bridge) (ok : Nat → Bool) : Option (Nat × Nat) :=
  match c.citeIndex with
  | none => none
  | some m =>
    match firstSuffix (fun s => (headPos s).any ok && (citeFirst m b.lens s).isSome) (bridgeAlnum b) with
    | none => none
    | some s =>
      match headPos s, citeFirst m b.lens s with
      | some p, some n => some (p, n)
      | _, _ => none

/-- Step 6: the first citation after p2. -/
def bridgeActorCite (c : Input) (b : Bridge) (p2 : Nat) : Option (Nat × Nat) :=
  actorCiteWhere c b (fun p => decide (p2 < p))

/-- Steps 1–6 with their tests as parameters (for the mutants); `none` = all hold. -/
def bridgeFailWith (qOk : Input → Bridge → Bool) (dateOk clauseOk : Bridge → Bool)
    (p1 : Input → Bridge → Option Nat) (p2 : Input → Bridge → Nat → Option Nat) (chain : Input → Bridge → Nat → Bool)
    (actor : Input → Bridge → Nat → Option (Nat × Nat)) (c : Input) (b : Bridge) : Option Reason :=
  if !qOk c b then some .bridgeMismatch
  else if !dateOk b then some .bridgeDate
  else if !clauseOk b then some .bridgeClause
  else match p1 c b with
    | none => some .bridgeTarget
    | some q1 => match p2 c b q1 with
      | none => some .bridgeCue
      | some q2 =>
        if !chain c b q2 then some .bridgeChain
        else if (actor c b q2).map (·.2) == some b.actor then none else some .bridgeActor

def bridgeFail : Input → Bridge → Option Reason :=
  bridgeFailWith bridgeQuoteOk bridgeDateOk bridgeClauseOk bridgeP1 bridgeP2 bridgeChainOk bridgeActorCite

/-- The first failing step, else step 7 with the target evidence taken as given. -/
def bridgeThen (r : Option Reason) (fin : Input → Result) (c : Input) : Result :=
  match r with
  | some r => .fail r
  | none => fin { c with selfText := true }

/-- **The bridge checker** (DESIGN8 §4). -/
def checkBridge (c : Input) (b : Bridge) (h : HClaims) : Result :=
  bridgeThen (bridgeFail c b) (checkClaimedWith orderHeadOk claimCueOk h) c

/-- §5: the anchor cue under an `anchorWide` claim. -/
def anchorWideCue (a : Anchor) : Bool := (anchorCues ++ anchorWideCues).any (hasSub (norm a.quote).toLower)
def anchorCueOk (h : HClaims) (a : Anchor) : Bool := if h.anchorWide then anchorWideCue a else anchorHasCue a

/-- `anchoredThen` with the anchor-cue test as a parameter. -/
def anchoredBy (cue : Anchor → Bool) (fin : Input → Result) (c : Input) (a : Anchor) : Result :=
  if !anchorQuoteOk c a then .fail .anchorMismatch
  else if !cue a then .fail .anchorNoCue
  else if anchorDisqualified a then .fail .anchorDisqualified
  else if !anchorResolves c a then .fail .anchorUnresolved
  else if !anchorPartOk a then .fail .anchorPart
  else fin { c with selfText := true }

/-- The round-8 history step with the anchor-cue test and the bridge steps as parameters. -/
def checkHistory8With (acue : HClaims → Anchor → Bool) (bf : Input → Bridge → Option Reason)
    (c : Input) (a? : Option Anchor) (b? : Option Bridge) (h : HClaims) : Result :=
  match b? with
  | some b => bridgeThen (bf c b) (checkClaimedWith orderHeadOk claimCueOk h) c
  | none =>
    match a? with
    | some a => anchoredBy (acue h) (checkClaimedWith orderHeadOk claimCueOk h) c a
    | none => checkClaimedWith orderHeadOk claimCueOk h c

/-- **The runner's history step** (round 8): a row with a bridge line by `checkBridge`; otherwise round 7's step,
with the wide anchor cues under an `anchorWide` claim. -/
def checkHistory8 : Input → Option Anchor → Option Bridge → HClaims → Result :=
  checkHistory8With anchorCueOk bridgeFail

/-! ### Theorems: bridge evidence, wide anchor cues -/

theorem firstSuffix_some {α : Type} (p : List α → Bool) :
    ∀ (l s : List α), firstSuffix p l = some s → s <:+ l ∧ p s = true
  | [], s, h => by simp [firstSuffix] at h
  | a :: t, s, h => by
    unfold firstSuffix at h
    by_cases hp : p (a :: t) = true
    · simp only [hp, ↓reduceIte, Option.some.injEq] at h
      subst h
      exact ⟨List.suffix_refl _, hp⟩
    · simp only [hp, Bool.false_eq_true, ↓reduceIte] at h
      obtain ⟨h1, h2⟩ := firstSuffix_some p t s h
      exact ⟨h1.trans (List.suffix_cons a t), h2⟩

theorem allSuffix_spec {α : Type} (p : List α → Bool) :
    ∀ (l : List α), allSuffix p l = true → ∀ s, s <:+ l → p s = true
  | [], h, s, hs => by
    rw [List.suffix_nil] at hs
    subst hs
    simpa [allSuffix] using h
  | a :: t, h, s, hs => by
    simp only [allSuffix, Bool.and_eq_true] at h
    rcases List.suffix_cons_iff.mp hs with he | ht
    · subst he
      exact h.1
    · exact allSuffix_spec p t h.2 s ht

theorem firstCue_some (k : Kind) (p1 : Nat) :
    ∀ (q : List Char) (i j : Nat), firstCue k p1 q i = some j →
      i ≤ j ∧ p1 < j ∧ cueHere k (q.drop (j - i)) = true
  | [], i, j, h => by simp [firstCue] at h
  | ch :: t, i, j, h => by
    unfold firstCue at h
    by_cases hc : (decide (p1 < i) && cueHere k (ch :: t)) = true
    · simp only [hc, ↓reduceIte, Option.some.injEq] at h
      subst h
      simp only [Bool.and_eq_true, decide_eq_true_eq] at hc
      exact ⟨Nat.le_refl _, hc.1, by simpa using hc.2⟩
    · simp only [hc, Bool.false_eq_true, ↓reduceIte] at h
      obtain ⟨h1, h2, h3⟩ := firstCue_some k p1 t (i + 1) j h
      refine ⟨by omega, h2, ?_⟩
      have he : j - i = (j - (i + 1)) + 1 := by omega
      rw [he, List.drop_succ_cons]
      exact h3

theorem bridgeP1_some (c : Input) (b : Bridge) (p1 : Nat) (h : bridgeP1 c b = some p1) :
    ∃ m, c.citeIndex = some m ∧
      ∃ s, s <:+ bridgeAlnum b ∧ headPos s = some p1 ∧ ∃ L ∈ b.lens, citeOf m s L = some c.target := by
  unfold bridgeP1 at h
  cases hm : c.citeIndex with
  | none => simp [hm] at h
  | some m =>
    simp only [hm] at h
    cases hs : firstSuffix (xHere m c b) (bridgeAlnum b) with
    | none => simp [hs] at h
    | some s =>
      simp only [hs, Option.bind_some] at h
      obtain ⟨h1, h2⟩ := firstSuffix_some _ _ s hs
      simp only [xHere, List.any_eq_true, beq_iff_eq] at h2
      exact ⟨m, rfl, s, h1, h, h2⟩

theorem bridgeP2_some (c : Input) (b : Bridge) (p1 p2 : Nat) (h : bridgeP2 c b p1 = some p2) :
    p1 < p2 ∧ cueHere c.kind ((bridgeText b).drop p2) = true := by
  obtain ⟨_, h2, h3⟩ := firstCue_some c.kind p1 (bridgeText b) 0 p2 h
  exact ⟨h2, by simpa using h3⟩

/-- Step 4 and 5b read the same suffix: X's key at p1 ends at `e`. -/
theorem bridgeX_some (c : Input) (b : Bridge) (p1 e : Nat) (h1 : bridgeP1 c b = some p1)
    (h2 : bridgeXEnd c b = some e) :
    ∃ m, c.citeIndex = some m ∧ ∃ s, s <:+ bridgeAlnum b ∧ headPos s = some p1 ∧
      ∃ L ∈ b.lens, citeOf m s L = some c.target ∧ keyEnd s L = e := by
  unfold bridgeP1 at h1
  unfold bridgeXEnd at h2
  cases hm : c.citeIndex with
  | none => simp [hm] at h1
  | some m =>
    simp only [hm] at h1 h2
    cases hs : firstSuffix (xHere m c b) (bridgeAlnum b) with
    | none => simp [hs] at h1
    | some s =>
      simp only [hs, Option.bind_some] at h1 h2
      obtain ⟨hsuf, _⟩ := firstSuffix_some _ _ s hs
      cases hf : b.lens.find? (fun L => citeOf m s L == some c.target) with
      | none => simp [hf] at h2
      | some L =>
        simp only [hf, Option.map_some, Option.some.injEq] at h2
        have hp := List.find?_some hf
        simp only [beq_iff_eq] at hp
        exact ⟨m, rfl, s, hsuf, h1, L, List.mem_of_find?_eq_some hf, hp, h2⟩

/-- Step 5b: no key begins at a position in `[e, p2)`. -/
theorem noKeyBetween_spec (c : Input) (b : Bridge) (e p2 : Nat) (h : noKeyBetween c b e p2 = true) :
    ∃ m, c.citeIndex = some m ∧
      ∀ s, s <:+ bridgeAlnum b → ∀ p, headPos s = some p → e ≤ p → p < p2 → ∀ L ∈ b.lens, citeOf m s L = none := by
  unfold noKeyBetween at h
  cases hm : c.citeIndex with
  | none => simp [hm] at h
  | some m =>
    simp only [hm] at h
    refine ⟨m, rfl, fun s hs p hp he hlt L hL => ?_⟩
    have hx := allSuffix_spec _ _ h s hs
    simp only [hp, Bool.or_eq_true, Bool.not_eq_true', Bool.and_eq_false_iff, decide_eq_false_iff_not,
      Option.isNone_iff_eq_none] at hx
    rcases hx with (hx | hx) | hx
    · exact absurd he hx
    · exact absurd hlt hx
    · exact List.findSome?_eq_none_iff.mp hx L hL

theorem bridgeChainOk_some (c : Input) (b : Bridge) (p2 : Nat) (h : bridgeChainOk c b p2 = true) :
    ∃ e, bridgeXEnd c b = some e ∧ noKeyBetween c b e p2 = true := by
  unfold bridgeChainOk at h
  cases he : bridgeXEnd c b with
  | none => simp [he] at h
  | some e =>
    simp only [he] at h
    exact ⟨e, rfl, h⟩

theorem actorCiteWhere_some (c : Input) (b : Bridge) (ok : Nat → Bool) (p n : Nat)
    (h : actorCiteWhere c b ok = some (p, n)) :
    ∃ m, c.citeIndex = some m ∧ ok p = true ∧
      ∃ s, s <:+ bridgeAlnum b ∧ headPos s = some p ∧ citeFirst m b.lens s = some n ∧
        ∃ L ∈ b.lens, citeOf m s L = some n := by
  unfold actorCiteWhere at h
  cases hm : c.citeIndex with
  | none => simp [hm] at h
  | some m =>
    simp only [hm] at h
    cases hs : firstSuffix (fun s => (headPos s).any ok && (citeFirst m b.lens s).isSome) (bridgeAlnum b) with
    | none => simp [hs] at h
    | some s =>
      simp only [hs] at h
      obtain ⟨h1, h2⟩ := firstSuffix_some _ _ s hs
      cases hp : headPos s with
      | none => simp [hp] at h
      | some p' =>
        cases hn : citeFirst m b.lens s with
        | none => simp [hp, hn] at h
        | some n' =>
          simp only [hp, hn, Option.some.injEq, Prod.mk.injEq] at h
          obtain ⟨rfl, rfl⟩ := h
          simp only [hp, Option.any_some, Bool.and_eq_true] at h2
          obtain ⟨L, hL, hc⟩ := List.exists_of_findSome?_eq_some hn
          exact ⟨m, rfl, h2.1, s, h1, hp, hn, L, hL, hc⟩

theorem bridgeActorCite_some (c : Input) (b : Bridge) (p2 pO n : Nat) (h : bridgeActorCite c b p2 = some (pO, n)) :
    ∃ m, c.citeIndex = some m ∧ p2 < pO ∧
      ∃ s, s <:+ bridgeAlnum b ∧ headPos s = some pO ∧ citeFirst m b.lens s = some n ∧
        ∃ L ∈ b.lens, citeOf m s L = some n := by
  obtain ⟨m, hm, hok, rest⟩ := actorCiteWhere_some c b _ pO n h
  exact ⟨m, hm, by simpa using hok, rest⟩

/-- Steps 1–6 all hold exactly when the bridge steps report no failure. -/
theorem bridgeFail_none_iff (c : Input) (b : Bridge) :
    bridgeFail c b = none ↔
      (bridgeQuoteOk c b = true ∧ bridgeDateOk b = true ∧ bridgeClauseOk b = true ∧
        ∃ p1 p2, bridgeP1 c b = some p1 ∧ bridgeP2 c b p1 = some p2 ∧ bridgeChainOk c b p2 = true ∧
          (bridgeActorCite c b p2).map (·.2) = some b.actor) := by
  constructor
  · intro hn
    unfold bridgeFail bridgeFailWith at hn
    by_cases h1 : bridgeQuoteOk c b = true
    · by_cases h2 : bridgeDateOk b = true
      · by_cases h3 : bridgeClauseOk b = true
        · simp only [h1, h2, h3, Bool.not_true, Bool.false_eq_true, ↓reduceIte] at hn
          cases h4 : bridgeP1 c b with
          | none => simp only [h4, reduceCtorEq] at hn
          | some q1 =>
            simp only [h4] at hn
            cases h5 : bridgeP2 c b q1 with
            | none => simp only [h5, reduceCtorEq] at hn
            | some q2 =>
              simp only [h5] at hn
              by_cases h7 : bridgeChainOk c b q2 = true
              · by_cases h6 : ((bridgeActorCite c b q2).map (·.2) == some b.actor) = true
                · exact ⟨h1, h2, h3, q1, q2, rfl, h5, h7, by simpa using h6⟩
                · simp [h7, h6] at hn
              · simp [h7] at hn
        · simp [h1, h2, h3] at hn
      · simp [h1, h2] at hn
    · simp [h1] at hn
  · rintro ⟨h1, h2, h3, p1, p2, e1, e2, e3, e4⟩
    unfold bridgeFail bridgeFailWith
    simp [h1, h2, h3, e1, e2, e3, e4]

/-- The verdict of a bridged row: a failing step's reason, else step 7. -/
theorem checkBridge_admitted (c : Input) (b : Bridge) (h : HClaims) :
    (checkBridge c b h).admitted = true ↔
      (bridgeFail c b = none ∧ (checkClaimedWith orderHeadOk claimCueOk h { c with selfText := true }).admitted = true) := by
  unfold checkBridge bridgeThen
  cases bridgeFail c b <;> simp [Result.admitted]

/-- **Admission is exactly steps 1–6 and the row's own check.** -/
theorem bridge_admitted_iff (c : Input) (b : Bridge) (h : HClaims) :
    (checkBridge c b h).admitted = true ↔
      (bridgeQuoteOk c b = true ∧ bridgeDateOk b = true ∧ bridgeClauseOk b = true ∧
        (∃ p1 p2, bridgeP1 c b = some p1 ∧ bridgeP2 c b p1 = some p2 ∧ bridgeChainOk c b p2 = true ∧
          (bridgeActorCite c b p2).map (·.2) = some b.actor) ∧
        (checkClaimedWith orderHeadOk claimCueOk h { c with selfText := true }).admitted = true) := by
  rw [checkBridge_admitted, bridgeFail_none_iff]
  constructor
  · rintro ⟨⟨a1, a2, a3, a4⟩, a5⟩
    exact ⟨a1, a2, a3, a4, a5⟩
  · rintro ⟨a1, a2, a3, a4, a5⟩
    exact ⟨⟨a1, a2, a3, a4⟩, a5⟩

/-- **Order**: X's citation, then the cue (with no key between X's citation and the cue), then O's citation. -/
theorem bridge_order (c : Input) (b : Bridge) (h : HClaims) (hadm : (checkBridge c b h).admitted = true) :
    ∃ p1 e p2 pO, bridgeP1 c b = some p1 ∧ bridgeXEnd c b = some e ∧ bridgeP2 c b p1 = some p2 ∧
      bridgeActorCite c b p2 = some (pO, b.actor) ∧ p1 < p2 ∧ p2 < pO ∧ noKeyBetween c b e p2 = true := by
  obtain ⟨_, _, _, ⟨p1, p2, e1, e2, e4, e3⟩, _⟩ := (bridge_admitted_iff c b h).mp hadm
  obtain ⟨e, he, hk⟩ := bridgeChainOk_some c b p2 e4
  cases hA : bridgeActorCite c b p2 with
  | none => simp [hA] at e3
  | some pn =>
    obtain ⟨pO, n⟩ := pn
    simp only [hA, Option.map_some, Option.some.injEq] at e3
    subst e3
    obtain ⟨_, _, hlt, _⟩ := bridgeActorCite_some c b p2 pO b.actor hA
    exact ⟨p1, e, p2, pO, e1, he, e2, hA, (bridgeP2_some c b p1 p2 e2).1, hlt, hk⟩

/-- A quote accepted by `quoteOk` sits in a usable window of the input's windows. -/
theorem quoteOk_window (c : Input) (h : quoteOk c = true) :
    ∃ w, coveringWindow c = some w ∧ w ∈ c.windows ∧ usable c w = true ∧ quoteAt c w = true := by
  unfold quoteOk at h
  cases hw : coveringWindow c with
  | none => simp [hw] at h
  | some w =>
    have hf : c.windows.find? (fun w => usable c w && quoteAt c w) = some w := hw
    have hp := List.find?_some hf
    simp only [Bool.and_eq_true] at hp
    exact ⟨w, rfl, List.mem_of_find?_eq_some hf, hp.1, hp.2⟩

/-- **Bridge soundness** (DESIGN8 §4, steps 1–7). -/
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
      checkBridge c b h = checkClaimedWith orderHeadOk claimCueOk h { c with selfText := true } := by
  obtain ⟨hq, hd, hcl, _, hfin⟩ := (bridge_admitted_iff c b h).mp hadm
  obtain ⟨p1, e, p2, pO, e1, he, e2, e3, _, _, hk⟩ := bridge_order c b h hadm
  have hnone : bridgeFail c b = none := ((checkBridge_admitted c b h).mp hadm).1
  -- step 1
  simp only [bridgeQuoteOk, Bool.and_eq_true, decide_eq_true_eq] at hq
  obtain ⟨hlen, hqo⟩ := hq
  obtain ⟨w, hw, hmem, hu, hqa⟩ := quoteOk_window (b.input c) hqo
  have hqa' := hqa
  unfold quoteAt at hqa'
  have hqa'' : (decide (b.start < b.stop) && b.quote != "" &&
      slice (norm w.text) (b.start - w.start0) (b.stop - b.start) == norm b.quote) = true := hqa'
  simp only [Bool.and_eq_true, decide_eq_true_eq, bne_iff_ne, ne_eq] at hqa''
  -- steps 2, 3
  simp only [bridgeDateOk, Bool.and_eq_true, decide_eq_true_eq] at hd
  simp only [bridgeClauseOk, Bool.not_eq_true'] at hcl
  -- steps 4–6
  obtain ⟨m, hm, s1, hs1, hh1, L1, hL1, hc1, hend⟩ := bridgeX_some c b p1 e e1 he
  obtain ⟨m3, hm3, hnk⟩ := noKeyBetween_spec c b e p2 hk
  rw [hm] at hm3
  cases hm3
  obtain ⟨hlt12, hcue⟩ := bridgeP2_some c b p1 p2 e2
  obtain ⟨m', hm', hlt2O, s2, hs2, hh2, _, L2, hL2, hc2⟩ := bridgeActorCite_some c b p2 pO b.actor e3
  rw [hm] at hm'
  cases hm'
  refine ⟨⟨hqa''.1.2, hqa''.1.1, hlen, w, hw, hmem, hu, hqa⟩, ⟨hd.1.1, hd.1.2, hd.2⟩, hcl,
    ⟨m, hm, p1, e, p2, pO, ⟨s1, hs1, hh1, L1, hL1, hc1, hend⟩, hlt12, hcue, hnk, hlt2O,
      ⟨s2, hs2, hh2, L2, hL2, hc2⟩⟩, hfin, ?_⟩
  simp [checkBridge, bridgeThen, hnone]

/-- The key `citeOf` looks up: `L ≥ 1` consecutive alphanumeric characters of the quote. -/
theorem citeOf_key (m : Std.HashMap String Nat) (s : List (Char × Nat)) (L n : Nat) (h : citeOf m s L = some n) :
    0 < L ∧ (s.take L).length = L ∧ m.get? (String.ofList ((s.take L).map (·.1))) = some n := by
  unfold citeOf at h
  by_cases hc : 0 < L ∧ (s.take L).length = L
  · rw [if_pos hc] at h
    exact ⟨hc.1, hc.2, h⟩
  · rw [if_neg hc] at h
    cases h

/-- The bridge steps do not read the acting court's power (the runner decides them once per row). -/
theorem bridgeFail_authority (c : Input) (b : Bridge) (a : Option Bool) :
    bridgeFail { c with authority := a } b = bridgeFail c b := rfl

/-- A row with a bridge line gets `checkBridge`'s verdict (an anchor line is not used). -/
theorem checkHistory8_bridge (c : Input) (a? : Option Anchor) (b : Bridge) (h : HClaims) :
    checkHistory8 c a? (some b) h = checkBridge c b h := rfl

/-- **No bridge line, no claim `anchorWide`: no change** (the round-7 history step). -/
theorem no_bridge_no_change (c : Input) (a? : Option Anchor) (h : HClaims) (hw : h.anchorWide = false) :
    checkHistory8 c a? none h = checkHistory7 c a? h := by
  cases a? with
  | none => rfl
  | some a =>
    simp only [checkHistory8, checkHistory8With, checkHistory7, checkHistory7With, anchoredBy, anchoredThen,
      anchorCueOk, hw, Bool.false_eq_true, ↓reduceIte]

/-- §5: **without the claim** the anchor-cue test and the anchored check are round 7's. -/
theorem anchorWide_no_claim (c : Input) (a : Anchor) (h : HClaims) (hw : h.anchorWide = false) :
    anchorCueOk h a = anchorHasCue a ∧ checkHistory8 c (some a) none h = checkHistory7 c (some a) h := by
  refine ⟨by simp [anchorCueOk, hw], no_bridge_no_change c (some a) h hw⟩

/-- §5: an admitted anchored row **with the claim** has a cue of `anchor ++ anchor_wide`, and every other anchored
check holds. -/
theorem anchorWide_sound (c : Input) (a : Anchor) (h : HClaims) (hw : h.anchorWide = true)
    (hadm : (checkHistory8 c (some a) none h).admitted = true) :
    (anchorCues ++ anchorWideCues).any (hasSub (norm a.quote).toLower) = true ∧ anchorQuoteOk c a = true ∧
      anchorDisqualified a = false ∧ anchorResolves c a = true ∧ anchorPartOk a = true ∧
      (checkClaimedWith orderHeadOk claimCueOk h { c with selfText := true }).admitted = true := by
  simp only [checkHistory8, checkHistory8With, anchoredBy, anchorCueOk, hw, ↓reduceIte] at hadm
  by_cases h1 : anchorQuoteOk c a = true
  · by_cases h2 : anchorWideCue a = true
    · by_cases h3 : anchorDisqualified a = true
      · simp [h1, h2, h3, Result.admitted] at hadm
      · by_cases h4 : anchorResolves c a = true
        · by_cases h5 : anchorPartOk a = true
          · simp only [h1, h2, h3, h4, h5, Bool.not_true, Bool.false_eq_true, ↓reduceIte] at hadm
            exact ⟨h2, h1, by simpa using h3, h4, h5, hadm⟩
          · simp [h1, h2, h3, h4, h5, Result.admitted] at hadm
        · simp [h1, h2, h3, h4, Result.admitted] at hadm
    · simp [h1, h2, Result.admitted] at hadm
  · simp [h1, Result.admitted] at hadm

/-! ## Round 9: part zones (`round9/DESIGN9.md` §4, `round9/LEAN9.md`)

The part map (`part_zone.tsv`: node, z_start, z_end, part, src) cuts the text of an acting node into zones, each
`[z_start, z_end)` of one part (majority, plurality, perCuriam, concurrence, dissent, headmatter, other). A node whose
lines include a malformed zone (`z_start ≥ z_end`, an unknown part) or two overlapping zones keeps none (`nodeZones`).
After a treatments or history row's own verdict admits (so a failure keeps its round-8 reason), its main quote must lie
inside one zone whose part is the row's `part`, and each joined quote inside one zone of its `j_part`; else `partZone`.
An anchor or bridge quote is not zone-checked. A row whose node has no zone is unchanged. -/

/-- One zone of a node's text: `[start, stop)` of one part. -/
structure Zone where
  start : Nat
  stop : Nat
  part : String
  deriving Repr, DecidableEq, Inhabited

/-- The part names a zone may carry (DESIGN9 §4). -/
def zoneParts : List String := ["majority", "plurality", "perCuriam", "concurrence", "dissent", "headmatter", "other"]

/-- A well-formed zone: non-empty, of a known part. -/
def zoneWellFormed (z : Zone) : Bool := decide (z.start < z.stop) && zoneParts.contains z.part

/-- Two zones do not overlap (touching is not overlapping, LEAN9 L9-4). -/
def zonesDisjoint (a b : Zone) : Bool := decide (a.stop ≤ b.start) || decide (b.stop ≤ a.start)

/-- No two zones of the list overlap. -/
def noOverlap : List Zone → Bool
  | [] => true
  | z :: zs => zs.all (zonesDisjoint z) && noOverlap zs

def zonesValid (zs : List Zone) : Bool := zs.all zoneWellFormed && noOverlap zs

/-- The zones a node keeps: all its lines, or none when one is malformed or two overlap. -/
def nodeZones (zs : List Zone) : List Zone := if zonesValid zs then zs else []

/-- The span `[s, e)` with part `p` lies inside the zone, of the same part. -/
def inZone (s e : Nat) (p : String) (z : Zone) : Bool := decide (z.start ≤ s) && decide (e ≤ z.stop) && z.part == p

def zoneHas (zs : List Zone) (s e : Nat) (p : String) : Bool := zs.any (inZone s e p)

/-- The main quote, and every joined quote, inside a zone of its own part. -/
def partZoneOk (zs : List Zone) (c : Input) (js : List Joined) : Bool :=
  zoneHas zs c.start c.stop c.part && js.all (fun j => zoneHas zs j.start j.stop j.part)

/-- **checkPartZone** (DESIGN9 §4), after the row's own verdict `r`: no zone, no change; a failure keeps its reason. -/
def zoneThen (zs : List Zone) (c : Input) (js : List Joined) (r : Result) : Result :=
  if zs.isEmpty then r else if r.admitted && !partZoneOk zs c js then .fail .partZone else r

/-- The same on a witness row's verdict (LEAN9 L9-7). -/
def zoneR (zs : List Zone) (c : Input) (v : RResult) : RResult :=
  if zs.isEmpty then v else if v.admitted && !partZoneOk zs c [] then .witness (.fail .partZone) else v

/-- **The runner's history step in round 9** (`zs`: the zones the acting node keeps). -/
def checkHistory9 (zs : List Zone) (c : Input) (a? : Option Anchor) (b? : Option Bridge) (h : HClaims) : Result :=
  zoneThen zs c [] (checkHistory8 c a? b? h)

/-- **The runner's treatment step in round 9** (a row that is not a witness row). -/
def checkTreatment9 (zs : List Zone) (c : Input) (e : Bool) (cl : TClaim) (js : List Joined) : Result :=
  zoneThen zs c js (checkTreatment c e cl js)

/-- **The runner's witness step in round 9.** -/
def checkRecognised9 (zs : List Zone) (c : Input) (w : Witness) : RResult := zoneR zs c (checkRecognised c w)

/-! ### Theorems: part zones -/

theorem zoneHas_spec (zs : List Zone) (s e : Nat) (p : String) (h : zoneHas zs s e p = true) :
    ∃ z ∈ zs, z.start ≤ s ∧ e ≤ z.stop ∧ z.part = p := by
  unfold zoneHas at h
  obtain ⟨z, hz, hin⟩ := List.any_eq_true.mp h
  simp only [inZone, Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq] at hin
  exact ⟨z, hz, hin.1.1, hin.1.2, hin.2⟩

/-- A failing verdict is never changed by the zone test (the first failure keeps its reason). -/
theorem zoneThen_fail_keeps (zs : List Zone) (c : Input) (js : List Joined) (r : Result) (h : r.admitted = false) :
    zoneThen zs c js r = r := by
  simp [zoneThen, h]

/-- The zones a node keeps are valid. -/
theorem nodeZones_valid (zs : List Zone) : zonesValid (nodeZones zs) = true := by
  unfold nodeZones
  split
  · assumption
  · rfl

/-- **No zone line, no change**: with no zone the three round-9 steps are round 8's (and the wrappers are the
identity on any verdict). -/
theorem no_zone_no_change (c : Input) (a? : Option Anchor) (b? : Option Bridge) (h : HClaims) (e : Bool) (cl : TClaim)
    (js : List Joined) (w : Witness) (r : Result) (v : RResult) :
    checkHistory9 [] c a? b? h = checkHistory8 c a? b? h ∧ checkTreatment9 [] c e cl js = checkTreatment c e cl js ∧
      checkRecognised9 [] c w = checkRecognised c w ∧ zoneThen [] c js r = r ∧ zoneR [] c v = v := by
  simp [checkHistory9, checkTreatment9, checkRecognised9, zoneThen, zoneR]

/-- **Zone soundness**: an admitted row whose node has zones has its main quote inside a zone of the row's part and
every joined quote inside a zone of its own part, and the round-8 verdict admits and is the verdict. -/
theorem partZone_sound (zs : List Zone) (c : Input) (js : List Joined) (r : Result) (hz : zs ≠ [])
    (hadm : (zoneThen zs c js r).admitted = true) :
    r.admitted = true ∧ zoneThen zs c js r = r ∧
      (∃ z ∈ zs, z.start ≤ c.start ∧ c.stop ≤ z.stop ∧ z.part = c.part) ∧
      ∀ j ∈ js, ∃ z ∈ zs, z.start ≤ j.start ∧ j.stop ≤ z.stop ∧ z.part = j.part := by
  have hne : zs.isEmpty = false := by
    cases zs with
    | nil => exact absurd rfl hz
    | cons _ _ => rfl
  by_cases hr : r.admitted = true
  · by_cases hok : partZoneOk zs c js = true
    · have heq : zoneThen zs c js r = r := by simp [zoneThen, hne, hr, hok]
      simp only [partZoneOk, Bool.and_eq_true, List.all_eq_true] at hok
      exact ⟨hr, heq, zoneHas_spec zs _ _ _ hok.1, fun j hj => zoneHas_spec zs _ _ _ (hok.2 j hj)⟩
    · have hok' : partZoneOk zs c js = false := by simpa using hok
      have hf : zoneThen zs c js r = .fail .partZone := by
        simp only [zoneThen, hne, hr, hok', Bool.not_false, Bool.and_self, Bool.false_eq_true, ↓reduceIte]
      rw [hf] at hadm
      simp [Result.admitted] at hadm
  · rw [zoneThen_fail_keeps zs c js r (by simpa using hr)] at hadm
    exact absurd hadm hr

/-- Zone soundness on a witness row: the round-8 witness verdict admits and is the verdict, and the main quote lies
inside a zone of the row's part. -/
theorem partZone_sound_witness (zs : List Zone) (c : Input) (v : RResult) (hz : zs ≠ [])
    (hadm : (zoneR zs c v).admitted = true) :
    v.admitted = true ∧ zoneR zs c v = v ∧ ∃ z ∈ zs, z.start ≤ c.start ∧ c.stop ≤ z.stop ∧ z.part = c.part := by
  have hne : zs.isEmpty = false := by
    cases zs with
    | nil => exact absurd rfl hz
    | cons _ _ => rfl
  by_cases hr : v.admitted = true
  · by_cases hok : partZoneOk zs c [] = true
    · have heq : zoneR zs c v = v := by simp [zoneR, hne, hr, hok]
      simp only [partZoneOk, Bool.and_eq_true] at hok
      exact ⟨hr, heq, zoneHas_spec zs _ _ _ hok.1⟩
    · have hok' : partZoneOk zs c [] = false := by simpa using hok
      have hf : zoneR zs c v = .witness (.fail .partZone) := by
        simp only [zoneR, hne, hr, hok', Bool.not_false, Bool.and_self, Bool.false_eq_true, ↓reduceIte]
      rw [hf] at hadm
      simp [RResult.admitted, WResult.admitted] at hadm
  · have heq : zoneR zs c v = v := by simp [zoneR, hr]
    rw [heq] at hadm
    exact absurd hadm hr

/-- An admitted round-9 history row whose node has zones: round 8 admits it, with the same verdict, and its quote lies
inside a zone of its part. -/
theorem checkHistory9_sound (zs : List Zone) (c : Input) (a? : Option Anchor) (b? : Option Bridge) (h : HClaims)
    (hz : zs ≠ []) (hadm : (checkHistory9 zs c a? b? h).admitted = true) :
    (checkHistory8 c a? b? h).admitted = true ∧ checkHistory9 zs c a? b? h = checkHistory8 c a? b? h ∧
      ∃ z ∈ zs, z.start ≤ c.start ∧ c.stop ≤ z.stop ∧ z.part = c.part :=
  let p := partZone_sound zs c [] _ hz hadm
  ⟨p.1, p.2.1, p.2.2.1⟩

/-- An admitted round-9 treatments row whose node has zones: round 7's step admits it, with the same verdict; its
main quote and every joined quote lie inside a zone of their parts. -/
theorem checkTreatment9_sound (zs : List Zone) (c : Input) (e : Bool) (cl : TClaim) (js : List Joined)
    (hz : zs ≠ []) (hadm : (checkTreatment9 zs c e cl js).admitted = true) :
    (checkTreatment c e cl js).admitted = true ∧ checkTreatment9 zs c e cl js = checkTreatment c e cl js ∧
      (∃ z ∈ zs, z.start ≤ c.start ∧ c.stop ≤ z.stop ∧ z.part = c.part) ∧
      ∀ j ∈ js, ∃ z ∈ zs, z.start ≤ j.start ∧ j.stop ≤ z.stop ∧ z.part = j.part :=
  partZone_sound zs c js _ hz hadm

/-- **Zone uniqueness**: in non-overlapping zones at most one zone contains a non-empty quote. -/
theorem partZone_unique (zs : List Zone) (hv : noOverlap zs = true) (s e : Nat) (hse : s < e) (z1 z2 : Zone)
    (h1 : z1 ∈ zs) (h2 : z2 ∈ zs) (i1 : z1.start ≤ s ∧ e ≤ z1.stop) (i2 : z2.start ≤ s ∧ e ≤ z2.stop) : z1 = z2 := by
  induction zs with
  | nil => simp at h1
  | cons z t ih =>
    simp only [noOverlap, Bool.and_eq_true, List.all_eq_true] at hv
    have dis : ∀ y ∈ t, y.start ≤ s → e ≤ y.stop → z.start ≤ s → e ≤ z.stop → False := by
      intro y hy a1 a2 a3 a4
      have hd := hv.1 y hy
      simp only [zonesDisjoint, Bool.or_eq_true, decide_eq_true_eq] at hd
      rcases hd with hd | hd <;> omega
    rcases List.mem_cons.mp h1 with e1 | h1t <;> rcases List.mem_cons.mp h2 with e2 | h2t
    · rw [e1, e2]
    · subst e1
      exact (dis z2 h2t i2.1 i2.2 i1.1 i1.2).elim
    · subst e2
      exact (dis z1 h1t i1.1 i1.2 i2.1 i2.2).elim
    · exact ih hv.2 h1t h2t

/-- **A bad node is ignored**: a node with a malformed zone or two overlapping zones keeps none, and its rows get
the round-8 verdict. -/
theorem zone_bad_node_ignored (zs : List Zone)
    (hb : (∃ z ∈ zs, zoneWellFormed z = false) ∨ noOverlap zs = false)
    (c : Input) (js : List Joined) (r : Result) (v : RResult) :
    nodeZones zs = [] ∧ zoneThen (nodeZones zs) c js r = r ∧ zoneR (nodeZones zs) c v = v := by
  have hv : zonesValid zs = false := by
    unfold zonesValid
    rcases hb with ⟨z, hz, hw⟩ | ho
    · cases ha : zs.all zoneWellFormed
      · rfl
      · have := List.all_eq_true.mp ha z hz
        rw [hw] at this
        exact absurd this (by decide)
    · rw [ho, Bool.and_false]
  have hn : nodeZones zs = [] := by simp [nodeZones, hv]
  rw [hn]
  exact ⟨rfl, by simp [zoneThen], by simp [zoneR]⟩


/-! ## Round 9, batch 2: far joined antecedents (`round9/DESIGN9.md` §5, claim `joinedFar`) and implicit rejection
(§7, claim `implicitReject`); `round9/LEAN9.md` §5 (D9-5, D9-7)

**Far antecedents.** Under a `joinedFar` claim an `antecedent` joined quote before the main quote whose gap
`start − j_end` is beyond `joinedGapMax` is accepted when the gap is at most `joinedFarMax` (`joinedFarGap`), a usable
window of the row's text covers it (`joinedFarWindow`), no index key of a node other than the target begins in it
(`joinedFarKey`), and the main quote has round 7's anaphor and kind cue (`joinedRelation`). No paragraph test (D9-7).
Every other step of `checkJoined` is unchanged.

**Implicit rejection.** Under an `implicitReject` claim a soft row (`limited`, `questioned`, `criticized`,
`declinedToFollow`) also accepts the cue phrases `implicitRejectCues`; any other kind fails `implicitBadKind`. Soft
rows never change status (`Examples.implicitReject_never_neg`). -/

/-- The gap `[j_end, start)` as a span of the row's text. -/
def farInput (c : Input) (j : Joined) : Input := { c with start := j.stop, stop := c.start }

/-- A usable window of the row's text that covers the gap. -/
def farWindow (c : Input) (j : Joined) : Option Window := c.windows.find? (usable (farInput c j))

/-- The alphanumeric characters of the window from `j_end` on, lower-cased, with their positions from `j_end`. -/
def farAlnum (c : Input) (j : Joined) (w : Window) : List (Char × Nat) :=
  alnumPos ((w.text.toList.drop (j.stop - w.start0)).map Char.toLower) 0

/-- No key of the index that maps to a node other than the target begins in the gap (no index: no key). -/
def farKeyOk (lens : List Nat) (c : Input) (j : Joined) (w : Window) : Bool :=
  match c.citeIndex with
  | none => true
  | some m => allSuffix (fun s => match headPos s with
      | some p => !decide (p < c.start - j.stop) || lens.all (fun L => (citeOf m s L).all (· == c.target))
      | none => true) (farAlnum c j w)

/-- The far tests of one line (ref9 Q9-12 order: bound, window, other key, then the main quote's anaphor and kind
cue), with the bound, the key test and the anaphor test as parameters (for the mutants). -/
def farReasonWith (maxGap : Nat) (keyOk : Input → Joined → Window → Bool) (ana : Input → Bool) (c : Input)
    (j : Joined) : Option Reason :=
  if maxGap < c.start - j.stop then some .joinedFarGap
  else match farWindow c j with
    | none => some .joinedFarWindow
    | some w => if !keyOk c j w then some .joinedFarKey else if !ana c then some .joinedRelation else none

/-- Check 4 of a claimed row, for one line: round 7's relation, or the far tests for an antecedent line before the
main quote whose gap is beyond `joinedGapMax`. -/
def farRelWith (fr : Input → Joined → Option Reason) (cl : TClaim) (c : Input) (j : Joined) : Option Reason :=
  if relationOk cl c j then none
  else if (j.rel == .antecedent && decide (j.stop ≤ c.start) && decide (joinedGapMax < c.start - j.stop)) then
    fr c j
  else some .joinedRelation

/-- `checkJoined` with check 4 by `farRelWith`. -/
def checkJoinedFarWith (fr : Input → Joined → Option Reason) (c : Input) (explicit : Bool) (cl : TClaim)
    (js : List Joined) : Result :=
  if !(joinedCountOk js && js.all (joinedQuoteOk c)) then .fail .joinedMismatch
  else if !js.all joinedPartOk then .fail .joinedPart
  else if js.any (joinedDisqualified c) then .fail .joinedDisqualified
  else match js.findSome? (farRelWith fr cl c) with
    | some r => .fail r
    | none => if !js.any (joinedResolves c) then .fail .joinedUnresolved
      else mainCheck { c with selfText := true } explicit cl

def farReason (lens : List Nat) : Input → Joined → Option Reason :=
  farReasonWith joinedFarMax (farKeyOk lens) (fun c => anaphorCue c.quote && kindCue c)

def checkJoinedFar (lens : List Nat) : Input → Bool → TClaim → List Joined → Result := checkJoinedFarWith (farReason lens)

/-- **The runner's treatment step under a `joinedFar` claim** (`far`; `lens`: the index's key lengths). -/
def checkTreatmentF (far : Bool) (lens : List Nat) : Input → Bool → TClaim → List Joined → Result :=
  if far then checkTreatmentWith (checkJoinedFar lens) else checkTreatment

/-- §7: the soft kinds (`TKind.softNegative`, `Examples.implicitSoft_softNegative`). -/
def implicitSoft : Kind → Bool
  | .treat .limited | .treat .questioned | .treat .criticized | .treat .declinedToFollow => true
  | _ => false

def implicitCue (c : Input) : Bool := implicitRejectCues.any (hasSub (norm c.quote).toLower)

/-- `check`'s part test. -/
def plainPart (c : Input) : Option Reason := if partOk c then none else some .partNotMajority

/-- The implicit-rejection checker with the kind test and the cue test as parameters. -/
def checkImplicitWith (kindOk : Kind → Bool) (cue : Input → Bool) (c : Input) (e : Bool) (js : List Joined) :
    Result :=
  if !kindOk c.kind then .fail .implicitBadKind
  else if js.isEmpty then checkBy cue plainPart c else checkTreatment c e .plain js

/-- **The implicit-rejection checker** (DESIGN9 §7). -/
def checkImplicit : Input → Bool → List Joined → Result :=
  checkImplicitWith implicitSoft (fun c => hasCue c || implicitCue c)

/-- **The runner's step under an `implicitReject` claim** (`imp`). -/
def checkTreatmentI (imp : Bool) (c : Input) (e : Bool) (cl : TClaim) (js : List Joined) : Result :=
  if imp then checkImplicit c e js else checkTreatment c e cl js

/-! ### Theorems: far antecedents, implicit rejection -/

theorem farWindow_some (c : Input) (j : Joined) (w : Window) (h : farWindow c j = some w) :
    w ∈ c.windows ∧ usable (farInput c j) w = true :=
  ⟨List.mem_of_find?_eq_some h, List.find?_some h⟩

theorem farKeyOk_spec (lens : List Nat) (c : Input) (j : Joined) (w : Window) (h : farKeyOk lens c j w = true) :
    ∀ m, c.citeIndex = some m → ∀ s, s <:+ farAlnum c j w → ∀ p, headPos s = some p → p < c.start - j.stop →
      ∀ L ∈ lens, ∀ n, citeOf m s L = some n → n = c.target := by
  intro m hm s hs p hp hlt L hL n hn
  unfold farKeyOk at h
  rw [hm] at h
  have hx := allSuffix_spec _ _ h s hs
  simp only [hp] at hx
  simp only [Bool.or_eq_true, Bool.not_eq_true', decide_eq_false_iff_not, List.all_eq_true] at hx
  rcases hx with h1 | h1
  · exact absurd hlt h1
  · have h2 := h1 L hL
    rw [hn] at h2
    simpa using h2

theorem findSome_farRel_none (fr : Input → Joined → Option Reason) (cl : TClaim) (c : Input) (js : List Joined)
    (h : js.all (relationOk cl c) = true) : js.findSome? (farRelWith fr cl c) = none := by
  rw [List.findSome?_eq_none_iff]
  intro j hj
  simp [farRelWith, List.all_eq_true.mp h j hj]

/-- A row the joined check admits gets the same verdict from the far check. -/
theorem checkJoinedFar_eq (fr : Input → Joined → Option Reason) (c : Input) (e : Bool) (cl : TClaim)
    (js : List Joined) (h : (checkJoined c e cl js).admitted = true) :
    checkJoinedFarWith fr c e cl js = checkJoined c e cl js := by
  obtain ⟨h1, h2, h3, h4, h5, _⟩ := (checkJoined_admitted_bool c e cl js).mp h
  have hn := findSome_farRel_none fr cl c js h4
  simp [checkJoinedFarWith, checkJoined, h1, h2, h3, h4, h5, hn]

theorem checkJoinedFarWith_rel (fr : Input → Joined → Option Reason) (c : Input) (e : Bool) (cl : TClaim)
    (js : List Joined) (h : (checkJoinedFarWith fr c e cl js).admitted = true) :
    js.findSome? (farRelWith fr cl c) = none := by
  unfold checkJoinedFarWith at h
  by_cases h1 : (joinedCountOk js && js.all (joinedQuoteOk c)) = true
  · by_cases h2 : js.all joinedPartOk = true
    · by_cases h3 : js.any (joinedDisqualified c) = true
      · simp [h1, h2, h3, Result.admitted] at h
      · cases hf : js.findSome? (farRelWith fr cl c) with
        | none => rfl
        | some r => simp [h1, h2, h3, hf, Result.admitted] at h
    · simp [h1, h2, Result.admitted] at h
  · simp [h1, Result.admitted] at h

theorem farRel_none (lens : List Nat) (cl : TClaim) (c : Input) (j : Joined) (hr : j.rel = .antecedent)
    (h : farRelWith (farReason lens) cl c j = none) :
    j.stop ≤ c.start ∧ c.start - j.stop ≤ joinedFarMax ∧ anaphorCue c.quote = true ∧ kindCue c = true ∧
      (c.start - j.stop ≤ joinedGapMax ∨
        ∃ w ∈ c.windows, usable (farInput c j) w = true ∧
          ∀ m, c.citeIndex = some m → ∀ s, s <:+ farAlnum c j w → ∀ p, headPos s = some p → p < c.start - j.stop →
            ∀ L ∈ lens, ∀ n, citeOf m s L = some n → n = c.target) := by
  have hm : joinedGapMax ≤ joinedFarMax := by decide
  unfold farRelWith at h
  by_cases hrel : relationOk cl c j = true
  · simp only [relationOk, hr, antecedentOk, Bool.and_eq_true, decide_eq_true_eq] at hrel
    obtain ⟨⟨⟨h1, h2⟩, h3⟩, h4⟩ := hrel
    exact ⟨h1, by omega, h3, h4, Or.inl h2⟩
  · simp only [hrel, Bool.false_eq_true, ↓reduceIte] at h
    by_cases hg : (j.rel == .antecedent && decide (j.stop ≤ c.start) && decide (joinedGapMax < c.start - j.stop)) = true
    · simp only [hg, ↓reduceIte] at h
      simp only [Bool.and_eq_true, decide_eq_true_eq] at hg
      obtain ⟨⟨_, g1⟩, _⟩ := hg
      unfold farReason farReasonWith at h
      by_cases hmx : joinedFarMax < c.start - j.stop
      · simp [hmx] at h
      · simp only [hmx, ↓reduceIte] at h
        cases hw : farWindow c j with
        | none => simp [hw] at h
        | some w =>
          simp only [hw] at h
          by_cases hk : farKeyOk lens c j w = true
          · by_cases ha : (anaphorCue c.quote && kindCue c) = true
            · obtain ⟨hwm, hwu⟩ := farWindow_some c j w hw
              simp only [Bool.and_eq_true] at ha
              exact ⟨g1, by omega, ha.1, ha.2, Or.inr ⟨w, hwm, hwu, farKeyOk_spec lens c j w hk⟩⟩
            · simp [hk, ha] at h
          · simp [hk] at h
    · simp [hg] at h

/-- **No claim, no change** (§5). -/
theorem joinedFar_no_claim (lens : List Nat) : checkTreatmentF false lens = checkTreatment := rfl

/-- **The claim only extends** (§5): every row admitted without the claim is admitted with it, with the same verdict. -/
theorem joinedFar_extends (lens : List Nat) (c : Input) (e : Bool) (cl : TClaim) (js : List Joined)
    (h : (checkTreatment c e cl js).admitted = true) : checkTreatmentF true lens c e cl js = checkTreatment c e cl js := by
  change checkTreatmentWith (checkJoinedFar lens) c e cl js = checkTreatmentWith checkJoined c e cl js
  change (checkTreatmentWith checkJoined c e cl js).admitted = true at h
  cases cl with
  | doctrine =>
    unfold checkTreatmentWith at h ⊢
    by_cases hd : doctrineRowOk c e js = true
    · simp only [hd, Bool.not_true, Bool.false_eq_true, ↓reduceIte] at h ⊢
      exact checkJoinedFar_eq _ c e .doctrine js h
    · simp [hd]
  | plain =>
    cases js with
    | nil => rfl
    | cons a t => exact checkJoinedFar_eq _ c e .plain (a :: t) h
  | operative =>
    cases js with
    | nil => rfl
    | cons a t => exact checkJoinedFar_eq _ c e .operative (a :: t) h

/-- **Far antecedents** (§5): an admitted claimed row's `antecedent` line is before the main quote and within
`joinedFarMax`, the main quote has an anaphor and a cue of its kind, and beyond `joinedGapMax` a usable window of the
row's text covers the gap, in which no index key of another node begins. -/
theorem antecedentFar_gap (lens : List Nat) (c : Input) (e : Bool) (cl : TClaim) (js : List Joined)
    (h : (checkTreatmentF true lens c e cl js).admitted = true) (j : Joined) (hj : j ∈ js) (hr : j.rel = .antecedent) :
    j.stop ≤ c.start ∧ c.start - j.stop ≤ joinedFarMax ∧ anaphorCue c.quote = true ∧ kindCue c = true ∧
      (c.start - j.stop ≤ joinedGapMax ∨
        ∃ w ∈ c.windows, usable (farInput c j) w = true ∧
          ∀ m, c.citeIndex = some m → ∀ s, s <:+ farAlnum c j w → ∀ p, headPos s = some p → p < c.start - j.stop →
            ∀ L ∈ lens, ∀ n, citeOf m s L = some n → n = c.target) := by
  change (checkTreatmentWith (checkJoinedFar lens) c e cl js).admitted = true at h
  have hjs : js ≠ [] := by
    rintro rfl
    simp at hj
  have hc : ∃ cl', (checkJoinedFar lens c e cl' js).admitted = true := by
    cases cl with
    | doctrine =>
      unfold checkTreatmentWith at h
      by_cases hd : doctrineRowOk c e js = true
      · simp only [hd, Bool.not_true, Bool.false_eq_true, ↓reduceIte] at h
        exact ⟨_, h⟩
      · simp [hd, Result.admitted] at h
    | plain =>
      cases js with
      | nil => exact absurd rfl hjs
      | cons a t => exact ⟨.plain, h⟩
    | operative =>
      cases js with
      | nil => exact absurd rfl hjs
      | cons a t => exact ⟨.operative, h⟩
  obtain ⟨cl', hc⟩ := hc
  have hn := checkJoinedFarWith_rel _ c e cl' js hc
  rw [List.findSome?_eq_none_iff] at hn
  exact farRel_none lens cl' c j hr (hn j hj)

/-- **No claim, no change** (§7): without the claim the treatment step (and its cue test) is round 8's. -/
theorem implicitReject_no_claim (c : Input) (e : Bool) (cl : TClaim) (js : List Joined) :
    checkTreatmentI false c e cl js = checkTreatment c e cl js := rfl

/-- **Soft kinds only** (§7): an admitted claimed row is of a soft kind. -/
theorem implicitReject_soft (c : Input) (e : Bool) (js : List Joined) (h : (checkImplicit c e js).admitted = true) :
    implicitSoft c.kind = true := by
  cases hk : implicitSoft c.kind with
  | true => rfl
  | false => simp [checkImplicit, checkImplicitWith, hk, Result.admitted] at h

/-! ### Round 9 §8 (D9-9): judge-form anchor cues under an `anchorWide` claim

The round-8 history step `checkHistory8` and its theorems are unchanged; the runner uses `checkHistory8J`, which is
`checkHistory8` with `anchorWide9Cues` added to the cue list of a claimed anchor (`anchorWide9_no_claim`). -/

def anchorWideCue9 (a : Anchor) : Bool :=
  (anchorCues ++ anchorWideCues ++ anchorWide9Cues).any (hasSub (norm a.quote).toLower)

def anchorCueOk9 (h : HClaims) (a : Anchor) : Bool := if h.anchorWide then anchorWideCue9 a else anchorHasCue a

/-- **The runner's round-8 history step with the judge forms** (DESIGN9 §8). -/
def checkHistory8J : Input → Option Anchor → Option Bridge → HClaims → Result := checkHistory8With anchorCueOk9 bridgeFail

/-- **The runner's history step in round 9** (with the judge forms; zones after it). -/
def checkHistory9J (zs : List Zone) (c : Input) (a? : Option Anchor) (b? : Option Bridge) (h : HClaims) : Result :=
  zoneThen zs c [] (checkHistory8J c a? b? h)

/-- **No claim, no change** (§8): without an `anchorWide` claim the step is round 8's, and the round-9 history step is
`checkHistory9`. -/
theorem anchorWide9_no_claim (c : Input) (a? : Option Anchor) (b? : Option Bridge) (h : HClaims) (zs : List Zone)
    (hw : h.anchorWide = false) :
    checkHistory8J c a? b? h = checkHistory8 c a? b? h ∧ checkHistory9J zs c a? b? h = checkHistory9 zs c a? b? h := by
  have e : checkHistory8J c a? b? h = checkHistory8 c a? b? h := by
    cases b? with
    | some b => rfl
    | none =>
      cases a? with
      | none => rfl
      | some a =>
        have hc : anchorCueOk9 h = anchorCueOk h := by
          funext a'
          simp [anchorCueOk9, anchorCueOk, hw]
        simp only [checkHistory8J, checkHistory8, checkHistory8With, hc]
  exact ⟨e, by simp only [checkHistory9J, checkHistory9, e]⟩

/-- **Judge-form cues** (§8): an admitted anchored row with the claim has a cue of `anchor ++ anchor_wide ++
anchor_wide9` in its anchor quote, and every other anchored check holds. -/
theorem anchorWide9_sound (c : Input) (a : Anchor) (h : HClaims) (hw : h.anchorWide = true)
    (hadm : (checkHistory8J c (some a) none h).admitted = true) :
    (anchorCues ++ anchorWideCues ++ anchorWide9Cues).any (hasSub (norm a.quote).toLower) = true ∧
      anchorQuoteOk c a = true ∧ anchorDisqualified a = false ∧ anchorResolves c a = true ∧ anchorPartOk a = true ∧
      (checkClaimedWith orderHeadOk claimCueOk h { c with selfText := true }).admitted = true := by
  simp only [checkHistory8J, checkHistory8With, anchoredBy, anchorCueOk9, hw, ↓reduceIte] at hadm
  by_cases h1 : anchorQuoteOk c a = true
  · by_cases h2 : anchorWideCue9 a = true
    · by_cases h3 : anchorDisqualified a = true
      · simp [h1, h2, h3, Result.admitted] at hadm
      · by_cases h4 : anchorResolves c a = true
        · by_cases h5 : anchorPartOk a = true
          · simp only [h1, h2, h3, h4, h5, Bool.not_true, Bool.false_eq_true, ↓reduceIte] at hadm
            exact ⟨h2, h1, by simpa using h3, h4, h5, hadm⟩
          · simp [h1, h2, h3, h4, h5, Result.admitted] at hadm
        · simp [h1, h2, h3, h4, Result.admitted] at hadm
    · simp [h1, h2, Result.admitted] at hadm
  · simp [h1, Result.admitted] at hadm

/-! ## Round 10: remand bridge evidence for history rows (`round10/DESIGN10.md` §4, D10-5, D10-6; `LEAN10.md`)

A Supreme Court order O (the row's acting node) vacates and remands; the target X is the decision below. A history
row with a line in `history_remand.tsv` names the remand decision B (the court below deciding the case again) and is
checked, **after its complete round-9 verdict admits** (a failing verdict keeps its reason), in order (the first
failure is the reason; `remandFail`):

1. `remandCourt`  B and X have the same decisions2 court id;
   `remandDate`   date(X) < date(O) ≤ date(B) ≤ date(O) + `remandDaysMax` days (all three calendar dates);
2. `remandDocket` the compact docket token (≥ 4 characters, a digit) is in a span of B's text and in a span of X's
                  text (each the text of a usable window of that node's own hash, non-empty, ≤ `remandDocketSpanMax`);
3. `remandCue`    B's quote (a usable window's text of B, ≤ `remandQuoteMax`, lower-cased) holds "supreme court" and a
                  remand cue;
4. `remandTie`    B's quote ties to O: a key of the citation index that maps to O, O's date printed in one of the two
                  forms (`dateForms`), or (D10-7) a reason case named after "in light of" in a span of O's own text
                  and in B's quote (`reasonTie`). -/

/-- The remand line of a history row (`history_remand.tsv`) with the facts it is checked against. -/
structure Remand where
  /-- the remand decision B -/
  b : Nat
  /-- B's text hash (decisions2; "" unknown) and the windows supplied for it -/
  bSha : String
  bWindows : List Window
  /-- the target's text hash and windows -/
  tSha : String
  tWindows : List Window
  /-- B's quote `[b_start, b_end)` -/
  start : Nat
  stop : Nat
  /-- the docket token (normalised by the data; compacted here) -/
  docket : String
  /-- the docket spans `[bd_start, bd_end)` of B's text and `[t_start, t_end)` of the target's text -/
  bdStart : Nat
  bdStop : Nat
  tStart : Nat
  tStop : Nat
  /-- the decisions2 court ids of B and the target (`none`: no row) -/
  bCourt : Option Nat := none
  tCourt : Option Nat := none
  /-- the decisions2 dates of the order (`by`), B and the target (0: unknown) -/
  oDate : Nat := 0
  bDate : Nat := 0
  tDate : Nat := 0
  /-- the order node (the row's acting node; `none` for `by = -1`) -/
  order : Option Nat := none
  /-- the key lengths of the citation index, longest first -/
  lens : List Nat := []
  /-- (D10-7) the reason-case tie string, and the span `[o_start, o_end)` of the order's text (its hash and windows) -/
  tie : String := ""
  oSha : String := ""
  oWindows : List Window := []
  oStart : Nat := 0
  oStop : Nat := 0
  deriving Inhabited

/-- A span of a node's text read as a quote over that node's hash and windows. -/
def spanInput (c : Input) (sha : String) (ws : List Window) (s e : Nat) : Input :=
  { c with textSha := sha, shas := [sha], windows := ws, start := s, stop := e }

/-- The normalised text at `[s, e)` of the first usable window covering it (non-empty, at most `maxLen`). -/
def spanText (c : Input) (sha : String) (ws : List Window) (s e maxLen : Nat) : Option String :=
  if sha.isEmpty || !decide (s < e) || !decide (e - s ≤ maxLen) then none
  else (ws.find? (usable (spanInput c sha ws s e))).map fun w => slice (norm w.text) (s - w.start0) (e - s)

/-- B's quote, lower-cased. -/
def remandQuote (c : Input) (r : Remand) : Option String :=
  (spanText c r.bSha r.bWindows r.start r.stop remandQuoteMax).map String.toLower

/-- Step 1: the court. -/
def remandCourtOk (r : Remand) : Bool := r.bCourt.isSome && r.bCourt == r.tCourt

def leapYear (y : Nat) : Bool := (y % 4 == 0 && y % 100 != 0) || y % 400 == 0
/-- The days of month `m` of year `y` (0 for a month outside 1–12). -/
def monthDays (y m : Nat) : Nat :=
  match m with
  | 1 | 3 | 5 | 7 | 8 | 10 | 12 => 31
  | 4 | 6 | 9 | 11 => 30
  | 2 => if leapYear y then 29 else 28
  | _ => 0
def dateYear (d : Nat) : Nat := d / 10000
def dateMonth (d : Nat) : Nat := d / 100 % 100
def dateDay (d : Nat) : Nat := d % 100
/-- A calendar date `yyyymmdd` (proleptic Gregorian, year > 0). -/
def validDate (d : Nat) : Bool :=
  decide (0 < dateYear d) && decide (1 ≤ dateDay d) && decide (dateDay d ≤ monthDays (dateYear d) (dateMonth d))
/-- The day number of a date: days since 0001-01-01, plus one. -/
def dayNum (d : Nat) : Nat :=
  let y := dateYear d - 1
  365 * y + y / 4 - y / 100 + y / 400 +
    ((List.range (dateMonth d - 1)).map (fun i => monthDays (dateYear d) (i + 1))).sum + dateDay d

/-- Step 1: the dates. -/
def remandDateOk (r : Remand) : Bool :=
  validDate r.oDate && validDate r.bDate && validDate r.tDate && decide (r.tDate < r.oDate) &&
    decide (r.oDate ≤ r.bDate) && decide (dayNum r.bDate ≤ dayNum r.oDate + remandDaysMax)

/-- A docket token: at least four characters, one a digit. -/
def docketTokenOk (k : String) : Bool := decide (4 ≤ k.length) && k.any Char.isDigit

/-- The span `[s, e)` of a node's text holds the compact token `k`. -/
def spanHas (c : Input) (sha : String) (ws : List Window) (s e : Nat) (k : String) : Bool :=
  match spanText c sha ws s e remandDocketSpanMax with
  | some t => hasSub (compact t) k
  | none => false

/-- Step 2: the docket token in both spans. -/
def remandDocketOk (c : Input) (r : Remand) : Bool :=
  docketTokenOk (compact r.docket) && spanHas c r.bSha r.bWindows r.bdStart r.bdStop (compact r.docket) &&
    spanHas c r.tSha r.tWindows r.tStart r.tStop (compact r.docket)

/-- Step 3 (on the lower-cased quote). -/
def remandCueOk (q : String) : Bool := remandCourtCues.any (hasSub q) && remandCues.any (hasSub q)

/-- Step 4 (a): a key of the index that maps to the order begins at an alphanumeric position of the quote. -/
def keyTie (c : Input) (r : Remand) (q : String) : Bool :=
  match c.citeIndex, r.order with
  | some m, some o =>
    (firstSuffix (fun s => r.lens.any (fun L => citeOf m s L == some o)) (alnumPos q.toList 0)).isSome
  | _, _ => false

/-- Step 4 (c): the two printed forms of a date (D10-6): `<month> <d>, <yyyy>` and `<abbr> <d>, <yyyy>`. -/
def dateForms (d : Nat) : List String :=
  let tail := " " ++ toString (dateDay d) ++ ", " ++ toString (dateYear d)
  if dateMonth d = 0 then []
  else ((remandMonths[dateMonth d - 1]?).toList ++ (remandMonthsAbbr[dateMonth d - 1]?).getD []).map (· ++ tail)

/-- Step 4 (c2) (D10-7): the reason case: the order's span holds "in light of", and the compact tie string (at least
`remandTieMin` characters) is in the compact order span and in the compact quote. -/
def reasonTie (c : Input) (r : Remand) (q : String) : Bool :=
  match spanText c r.oSha r.oWindows r.oStart r.oStop remandOrderSpanMax with
  | some o => remandOrderCues.any (hasSub o.toLower) && decide (remandTieMin ≤ (compact r.tie).length) &&
      hasSub (compact o) (compact r.tie) && hasSub (compact q) (compact r.tie)
  | none => false

/-- Step 4 (D10-7: the docket is no tie). -/
def remandTieOk (c : Input) (r : Remand) (q : String) : Bool :=
  keyTie c r q || (dateForms r.oDate).any (hasSub q) || reasonTie c r q

/-- Steps 1–4 with their tests as parameters (for the mutants); `none` = all hold. -/
def remandFailWith (courtOk dateOk : Remand → Bool) (docketOk : Input → Remand → Bool) (cueOk : String → Bool)
    (tieOk : Input → Remand → String → Bool) (c : Input) (r : Remand) : Option Reason :=
  if !courtOk r then some .remandCourt
  else if !dateOk r then some .remandDate
  else if !docketOk c r then some .remandDocket
  else match remandQuote c r with
    | none => some .remandCue
    | some q => if !cueOk q then some .remandCue else if !tieOk c r q then some .remandTie else none

def remandFail : Input → Remand → Option Reason :=
  remandFailWith remandCourtOk remandDateOk remandDocketOk remandCueOk remandTieOk

/-- **remandBridge** after the row's complete round-9 verdict `res`: no line, no change; a failing verdict keeps its
reason; an admitted one fails with the first failing step. -/
def remandThenWith (rf : Input → Remand → Option Reason) (rm? : Option Remand) (c : Input) (res : Result) : Result :=
  match rm? with
  | none => res
  | some r => if res.admitted then (match rf c r with | some e => .fail e | none => res) else res

def remandThen : Option Remand → Input → Result → Result := remandThenWith remandFail

/-- **The runner's history step in round 10.** -/
def checkHistory10 (rm? : Option Remand) (zs : List Zone) (c : Input) (a? : Option Anchor) (b? : Option Bridge)
    (h : HClaims) : Result :=
  remandThen rm? c (checkHistory9J zs c a? b? h)

/-! ### Theorems: remand bridge evidence -/

theorem spanText_some (c : Input) (sha : String) (ws : List Window) (s e n : Nat) (t : String)
    (h : spanText c sha ws s e n = some t) :
    s < e ∧ e - s ≤ n ∧ ∃ w ∈ ws, usable (spanInput c sha ws s e) w = true ∧
      t = slice (norm w.text) (s - w.start0) (e - s) := by
  unfold spanText at h
  by_cases h0 : (sha.isEmpty || !decide (s < e) || !decide (e - s ≤ n)) = true
  · simp only [h0, ↓reduceIte] at h; cases h
  · simp only [h0, Bool.false_eq_true, ↓reduceIte] at h
    simp only [Bool.or_eq_true, Bool.not_eq_true', decide_eq_false_iff_not, not_or, Decidable.not_not] at h0
    cases hf : ws.find? (usable (spanInput c sha ws s e)) with
    | none => simp [hf] at h
    | some w =>
      simp only [hf, Option.map_some, Option.some.injEq] at h
      exact ⟨h0.1.2, h0.2, w, List.mem_of_find?_eq_some hf, List.find?_some hf, h.symm⟩

theorem keyTie_spec (c : Input) (r : Remand) (q : String) (h : keyTie c r q = true) :
    ∃ m o, c.citeIndex = some m ∧ r.order = some o ∧
      ∃ s, s <:+ alnumPos q.toList 0 ∧ ∃ L ∈ r.lens, citeOf m s L = some o := by
  unfold keyTie at h
  cases hm : c.citeIndex with
  | none => simp [hm] at h
  | some m =>
    cases ho : r.order with
    | none => simp [hm, ho] at h
    | some o =>
      simp only [hm, ho, Option.isSome_iff_exists] at h
      obtain ⟨s, hs⟩ := h
      obtain ⟨h1, h2⟩ := firstSuffix_some _ _ s hs
      simp only [List.any_eq_true, beq_iff_eq] at h2
      obtain ⟨L, hL, hc⟩ := h2
      exact ⟨m, o, rfl, rfl, s, h1, L, hL, hc⟩

theorem reasonTie_spec (c : Input) (r : Remand) (q : String) (h : reasonTie c r q = true) :
    ∃ o, spanText c r.oSha r.oWindows r.oStart r.oStop remandOrderSpanMax = some o ∧
      remandOrderCues.any (hasSub o.toLower) = true ∧ remandTieMin ≤ (compact r.tie).length ∧
      hasSub (compact o) (compact r.tie) = true ∧ hasSub (compact q) (compact r.tie) = true := by
  unfold reasonTie at h
  cases ho : spanText c r.oSha r.oWindows r.oStart r.oStop remandOrderSpanMax with
  | none => simp [ho] at h
  | some o =>
    simp only [ho, Bool.and_eq_true, decide_eq_true_eq] at h
    exact ⟨o, rfl, h.1.1.1, h.1.1.2, h.1.2, h.2⟩

theorem spanHas_some (c : Input) (sha : String) (ws : List Window) (s e : Nat) (k : String)
    (h : spanHas c sha ws s e k = true) :
    ∃ t, spanText c sha ws s e remandDocketSpanMax = some t ∧ hasSub (compact t) k = true := by
  unfold spanHas at h
  cases ht : spanText c sha ws s e remandDocketSpanMax with
  | none => simp [ht] at h
  | some t => simp only [ht] at h; exact ⟨t, rfl, h⟩

/-- **What `remandFail = none` means**: every step holds. -/
theorem remandFail_none (c : Input) (r : Remand) (h : remandFail c r = none) :
    remandCourtOk r = true ∧ remandDateOk r = true ∧ remandDocketOk c r = true ∧
      ∃ q, remandQuote c r = some q ∧ remandCueOk q = true ∧ remandTieOk c r q = true := by
  unfold remandFail remandFailWith at h
  by_cases h1 : remandCourtOk r = true
  · by_cases h2 : remandDateOk r = true
    · by_cases h3 : remandDocketOk c r = true
      · simp only [h1, h2, h3, Bool.not_true, Bool.false_eq_true, ↓reduceIte] at h
        cases hq : remandQuote c r with
        | none => simp [hq] at h
        | some q =>
          simp only [hq] at h
          by_cases h4 : remandCueOk q = true
          · by_cases h5 : remandTieOk c r q = true
            · exact ⟨h1, h2, h3, q, rfl, h4, h5⟩
            · simp [h4, h5] at h
          · simp [h4] at h
      · simp [h1, h2, h3] at h
    · simp [h1, h2] at h
  · simp [h1] at h

/-- **No remand line, no change**: without a line the round-10 step is the round-9 step (and the wrapper is the
identity on any verdict). -/
theorem no_remand_line_no_change (zs : List Zone) (c : Input) (a? : Option Anchor) (b? : Option Bridge)
    (h : HClaims) (res : Result) :
    checkHistory10 none zs c a? b? h = checkHistory9J zs c a? b? h ∧ remandThen none c res = res :=
  ⟨rfl, rfl⟩

/-- **A failing verdict keeps its reason.** -/
theorem remandThen_fail_keeps (rm? : Option Remand) (c : Input) (res : Result) (h : res.admitted = false) :
    remandThen rm? c res = res := by
  cases rm? with
  | none => rfl
  | some r => simp [remandThen, remandThenWith, h]

/-- An admitted verdict after a line: the verdict before it admits and is kept, and every step holds. -/
theorem remandThen_some_admitted (r : Remand) (c : Input) (res : Result)
    (h : (remandThen (some r) c res).admitted = true) :
    res.admitted = true ∧ remandFail c r = none ∧ remandThen (some r) c res = res := by
  by_cases ha : res.admitted = true
  · cases hf : remandFail c r with
    | none => exact ⟨ha, rfl, by simp [remandThen, remandThenWith, ha, hf]⟩
    | some e =>
      simp only [remandThen, remandThenWith, ha, ↓reduceIte, hf] at h
      simp [Result.admitted] at h
  · have hf : res.admitted = false := by simpa using ha
    simp [remandThen, remandThenWith, hf] at h

/-- **Remand bridge soundness** (DESIGN10 §4, D10-5, D10-7): an admitted row with a line has an admitted round-9
verdict (which is the verdict); B and the target share the court; the target is before the order, B from the order to
`remandDaysMax` days after it (three calendar dates); the compact docket token (≥ 4 characters, a digit) is in a span
of B's text and in a span of the target's text; B's quote holds "supreme court" and a remand cue, and a tie to the
order: a key of the order, the order's date as printed, or a reason case named after "in light of" in a span of the
order's text and in B's quote. -/
theorem remandBridge_sound (r : Remand) (zs : List Zone) (c : Input) (a? : Option Anchor) (b? : Option Bridge)
    (h : HClaims) (hadm : (checkHistory10 (some r) zs c a? b? h).admitted = true) :
    (checkHistory9J zs c a? b? h).admitted = true ∧
      checkHistory10 (some r) zs c a? b? h = checkHistory9J zs c a? b? h ∧
      r.bCourt.isSome = true ∧ r.bCourt = r.tCourt ∧
      validDate r.oDate = true ∧ validDate r.bDate = true ∧ validDate r.tDate = true ∧
      r.tDate < r.oDate ∧ r.oDate ≤ r.bDate ∧ dayNum r.bDate ≤ dayNum r.oDate + remandDaysMax ∧
      4 ≤ (compact r.docket).length ∧ (compact r.docket).any Char.isDigit = true ∧
      (∃ s, spanText c r.bSha r.bWindows r.bdStart r.bdStop remandDocketSpanMax = some s ∧
        hasSub (compact s) (compact r.docket) = true) ∧
      (∃ s, spanText c r.tSha r.tWindows r.tStart r.tStop remandDocketSpanMax = some s ∧
        hasSub (compact s) (compact r.docket) = true) ∧
      ∃ q, remandQuote c r = some q ∧ remandCourtCues.any (hasSub q) = true ∧ remandCues.any (hasSub q) = true ∧
        (keyTie c r q = true ∨ (dateForms r.oDate).any (hasSub q) = true ∨
          ∃ o, spanText c r.oSha r.oWindows r.oStart r.oStop remandOrderSpanMax = some o ∧
            remandOrderCues.any (hasSub o.toLower) = true ∧ remandTieMin ≤ (compact r.tie).length ∧
            hasSub (compact o) (compact r.tie) = true ∧ hasSub (compact q) (compact r.tie) = true) := by
  obtain ⟨ha, hf, he⟩ := remandThen_some_admitted r c _ hadm
  obtain ⟨h1, h2, h3, q, hq, h4, h5⟩ := remandFail_none c r hf
  simp only [remandCourtOk, Bool.and_eq_true, beq_iff_eq] at h1
  simp only [remandDateOk, Bool.and_eq_true, decide_eq_true_eq] at h2
  simp only [remandDocketOk, docketTokenOk, Bool.and_eq_true, decide_eq_true_eq] at h3
  simp only [remandCueOk, Bool.and_eq_true] at h4
  simp only [remandTieOk, Bool.or_eq_true] at h5
  obtain ⟨⟨⟨hk1, hk2⟩, hb⟩, ht⟩ := h3
  obtain ⟨⟨⟨⟨⟨v1, v2⟩, v3⟩, d1⟩, d2⟩, d3⟩ := h2
  exact ⟨ha, he, h1.1, h1.2, v1, v2, v3, d1, d2, d3, hk1, hk2, spanHas_some _ _ _ _ _ _ hb,
    spanHas_some _ _ _ _ _ _ ht, q, hq, h4.1, h4.2, by
      rcases h5 with (h5 | h5) | h5
      · exact Or.inl h5
      · exact Or.inr (Or.inl h5)
      · exact Or.inr (Or.inr (reasonTie_spec c r q h5))⟩

end CaseLaw2.Cert
