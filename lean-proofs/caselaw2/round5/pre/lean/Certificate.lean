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

def hasCue (c : Input) : Bool := (cues c.kind).any (hasSub (norm c.quote).toLower)

def disqualified (c : Input) : Bool :=
  let q := (norm c.quote).toLower
  (disqualifiers c.kind).any (fun (a, b) => if b.isEmpty then hasSub q a else hasInOrder q a b)

/-- The citation resolves through the index to the row's target (true when no index is supplied). -/
def citeResolves (c : Input) (cite : String) : Bool :=
  match c.citeIndex with
  | some m => m.get? (compact cite) == some c.target
  | none => true

def resolves (c : Input) : Bool :=
  -- the target may be named in the quote or in any usable window covering it (several windows can cover one
  -- quote; all of them are the context, D4 real data)
  let ctx := (norm c.quote) ++ " " ++ " ".intercalate ((c.windows.filter (usable c)).map fun w => norm w.text)
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


end CaseLaw2.Cert
