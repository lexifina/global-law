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
  deriving Repr, DecidableEq, Inhabited

/-- Round 5 (DESIGN5 §2.2, §3.2): how the text checks read a certificate. `plain`: the round-4 checks. `recog`: a
later court's statement that X was overruled by Y (recognition cues and disqualifiers; the names resolve in the
quote itself). `operative`: the court's own operative words other than the terms of art (operative cues, the
round-4 disqualifiers and the operative ones; the target resolves in the quote itself). -/
inductive Mode where
  | plain | recog | operative
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

/-- The disqualifiers the quote is tested against. In `recog` mode a reported history ("overruled by") is the
normal form, so only the recognition disqualifiers apply. -/
def disqList (c : Input) : List (String × String) :=
  match c.mode with
  | .plain => disqualifiers c.kind
  | .recog => recognisedDisqualifiers.map (·, "")
  | .operative => disqualifiers c.kind ++ operativeDisqualifiers.map (·, "")

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

/-- The four classes of a status-changing treatments row (DESIGN5 §5), least first. -/
inductive OClass where
  | selfAnnounced | operativeWords | recognised | atRiskWitness
  deriving Repr, DecidableEq, Inhabited

def OClass.idx : OClass → Nat
  | .selfAnnounced => 0 | .operativeWords => 1 | .recognised => 2 | .atRiskWitness => 3

def OClass.toString : OClass → String
  | .selfAnnounced => "selfAnnounced" | .operativeWords => "operativeWords" | .recognised => "recognised"
  | .atRiskWitness => "atRiskWitness"

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

end CaseLaw2.Cert
