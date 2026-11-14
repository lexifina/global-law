# Round 11, Lean: claim `anchorTribunal` (§5.1)

Contract: `DESIGN11.md` §5.1 (D11-4). Written by the agent `lean11`, 14 Nov 2026 (started 05:20). Sections 0 and 1
were written **before** any code or proof (05:23–05:27; statements fixed at the time logged in `STATEMENTS.log`,
entry "round 11 section 5.1 STATED"): the statements are the target; a statement that proves false is refuted and
reported, never weakened silently. Sections 2–3 are written after the build.

Backup of everything changed: `round11/pre/` (round 10's file list plus the `wsl/r10_*` scripts; `SHA1SUMS.txt`, 121
files). `round11/pre/CaseLaw2` is the round-10 final state (binary e7e32592).

## 0. Readings of points DESIGN11 §5.1 leaves open

These agree with ref11's `REF_QUESTIONS11.md` Q11-1..4 (read for alignment; ref11 never reads the Lean).

| # | point | what the Lean does |
|---|---|---|
| L11-1 | claim value (Q11-1) | `HClaimRow.parse` accepts `anchorTribunal` (a line with it was a bad line before; v10d has none). A kept line puts its id in the claimed rows (`hclaim_rows`, `hclaim_admitted`, `hclaim_rejected` count it), like `anchorWide`; a repeated (id, `anchorTribunal`) is `hclaim_duplicates`; an id of no history row is `hclaim_unknown_ids` (the "claim on a non-history row": no other effect) |
| L11-2 | cue test (Q11-2) | with the claim, check 2 of the anchored check is `(anchor ++ anchor_wide ++ anchor_wide9 ++ anchor_tribunal).any (hasSub (norm a.quote).toLower)` (`anchorTribunalCue`); with both `anchorWide` and `anchorTribunal` the same union; without `anchorTribunal` round 10's `anchorCueOk9` (anchor_wide lists under `anchorWide`, else `anchor`) |
| L11-3 | which checks (Q11-3) | the anchor-cue test of every anchored check of a history row without a bridge line, including the anchored check of a counted `trialBridge` row (round 10 §6 shares `anchoredBy`); never the disposition quote's cue, the bridge, the zone, the remand check or checks 1, 3–6 of the anchored check |
| L11-4 | counters (Q11-4) | only when some kept line has the claim: `hclaim_anchortribunal` (ids with a kept claim line), `hclaim_anchortribunal_unused` (of those, rows with no anchor line or with a bridge line — the `hclaim_anchorwide_unused` definition), at the end of the history-claim block (after the `oldCircuit` counters) |
| L11-5 | cue table (appended; earlier lines byte-identical) | `_note_round11`, `anchor_tribunal` ["court of international trade", "customs court", "court of federal claims", "claims court", "veterans court", "court of veterans appeals"] → Lean `anchorTribunalCues`, Python `ANCHOR_TRIBUNAL`; `gen_cues.py --skip-ref` (ref/ is ref11's) |
| L11-6 | presence | no line with the claim ⇒ every row's `HClaims.anchorTribunal = false` ⇒ the step is round 10's (`anchorTribunal_no_claim`) and no new counter is written ⇒ `round10/out/v10d`, `round9/out/v9c`, `round8/out/v8e` and the regressions byte for byte |
| L11-7 | runner | the history step is `Cert.checkHistory11` = `remandThen rm? (checkHistory9A tb? zs …)`; the zone counters read the round-9-level verdict (`checkHistory9A`) as in round 10; every other counter the final verdict |

Questions for the lead: none open.

## 1. Definitions and theorems (stated first)

Checker definitions in `LegalProofs/CaseLaw2/Certificate.lean` (namespace `CaseLaw2.Cert`, a new round-11 section at
the end).

### 1.1 Definitions

```lean
-- HClaims: a new field (round-10 and earlier functions ignore it)
  anchorTribunal : Bool := false

/-- §5.1: the anchor cue under an `anchorTribunal` claim (the union of the four lists). -/
def anchorTribunalCue (a : Anchor) : Bool :=
  (anchorCues ++ anchorWideCues ++ anchorWide9Cues ++ anchorTribunalCues).any (hasSub (norm a.quote).toLower)
def anchorCueOk11 (h : HClaims) (a : Anchor) : Bool :=
  if h.anchorTribunal then anchorTribunalCue a else anchorCueOk9 h a

/-- The anchored row's last step (check 6): the trial check of a counted `trialBridge` claim (a reversed / vacated
row with a TBridge), else the claimed check. -/
def anchorTail (t? : Option TBridge) (h : HClaims) (c : Input) : Input → Result :=
  match t? with
  | some t => if trialKind c.kind then checkTrialWith trialBridgeDOk (trialFailWith trialBridgeTOk trialBridgeDateOk) h t
              else checkClaimedWith orderHeadOk claimCueOk h
  | none => checkClaimedWith orderHeadOk claimCueOk h

/-- The round-10 history step (`checkHistory8T`) with the anchor-cue test as a parameter (for the mutants). -/
def checkHistory8AWith (acue : HClaims → Anchor → Bool) (t? : Option TBridge) (c : Input) (a? : Option Anchor)
    (b? : Option Bridge) (h : HClaims) : Result :=
  match b?, a? with
  | some b, _ => bridgeThen (bridgeFail c b) (checkClaimedWith orderHeadOk claimCueOk h) c
  | none, some a => anchoredBy (acue h) (anchorTail t? h c) c a
  | none, none => checkClaimedWith orderHeadOk claimCueOk h c
def checkHistory8A : Option TBridge → Input → Option Anchor → Option Bridge → HClaims → Result :=
  checkHistory8AWith anchorCueOk11
def checkHistory9A (t? : Option TBridge) (zs : List Zone) (c : Input) (a? : Option Anchor) (b? : Option Bridge)
    (h : HClaims) : Result := zoneThen zs c [] (checkHistory8A t? c a? b? h)
/-- **The runner's history step in round 11.** -/
def checkHistory11 (t? : Option TBridge) (rm? : Option Remand) (zs : List Zone) (c : Input) (a? : Option Anchor)
    (b? : Option Bridge) (h : HClaims) : Result := remandThen rm? c (checkHistory9A t? zs c a? b? h)
```

### 1.2 Theorems (4 stated: DESIGN11's three and a characterisation for the second mutant)

```lean
/-- **No claim, no change** (§5.1): without the claim the cue test is round 10's, and the round-11 steps are
round 10's (`checkHistory8T`, `checkHistory10T`). -/
theorem anchorTribunal_no_claim (t? : Option TBridge) (rm? : Option Remand) (zs : List Zone) (c : Input)
    (a? : Option Anchor) (b? : Option Bridge) (h : HClaims) (ht : h.anchorTribunal = false) :
    anchorCueOk11 h = anchorCueOk9 h ∧ checkHistory8A t? c a? b? h = checkHistory8T t? c a? b? h ∧
      checkHistory11 t? rm? zs c a? b? h = checkHistory10T t? rm? zs c a? b? h

/-- **Tribunal anchor soundness** (§5.1): an admitted anchored row (no bridge line) with the claim has a cue of
`anchor ++ anchor_wide ++ anchor_wide9 ++ anchor_tribunal` in its anchor quote, and every other anchored check holds
(the anchor quote at its offset, no anchor disqualifier, the target named in the anchor quote, the anchor part, and
the row's last step — the claimed check, or the trial check of a counted trialBridge claim — admits). -/
theorem anchorTribunal_sound (t? : Option TBridge) (c : Input) (a : Anchor) (h : HClaims)
    (ht : h.anchorTribunal = true) (hadm : (checkHistory8A t? c (some a) none h).admitted = true) :
    (anchorCues ++ anchorWideCues ++ anchorWide9Cues ++ anchorTribunalCues).any (hasSub (norm a.quote).toLower) = true ∧
      anchorQuoteOk c a = true ∧ anchorDisqualified a = false ∧ anchorResolves c a = true ∧ anchorPartOk a = true ∧
      (anchorTail t? h c { c with selfText := true }).admitted = true

/-- **Tribunal anchor, exactly** (§5.1): with the claim, an anchored row without a bridge line is checked by the
round-10 anchored check with the union cue list (whatever `anchorWide` says). -/
theorem anchorTribunal_eq (t? : Option TBridge) (c : Input) (a : Anchor) (h : HClaims)
    (ht : h.anchorTribunal = true) :
    checkHistory8A t? c (some a) none h = anchoredBy anchorTribunalCue (anchorTail t? h c) c a

/-- **Presence** (§5.1): the claim has no effect on a row with no anchor line or with a bridge line (the bridge takes
the row): the round-11 steps are round 10's whatever the claims. -/
theorem no_tribunal_claim_no_change (t? : Option TBridge) (rm? : Option Remand) (zs : List Zone) (c : Input)
    (a? : Option Anchor) (b? : Option Bridge) (h : HClaims) (hu : a? = none ∨ b?.isSome = true) :
    checkHistory8A t? c a? b? h = checkHistory8T t? c a? b? h ∧
      checkHistory11 t? rm? zs c a? b? h = checkHistory10T t? rm? zs c a? b? h
```

Helpers expected (locked as additions): `checkHistory8AWith_cue9` (`checkHistory8AWith anchorCueOk9 t? c a? b? h =
checkHistory8T t? c a? b? h`: the parametrised step at round 10's cue test is round 10's step), `anchorTail_none`
(`anchorTail none h c = checkClaimedWith orderHeadOk claimCueOk h`).

### 1.3 Mutants (3; `Mutants.lean`, properties `properties11`)

New `Impl` field `checkHistory8A : Option Cert.TBridge → Cert.Input → Option Cert.Anchor → Option Cert.Bridge →
Cert.HClaims → Cert.Result := Cert.checkHistory8A`; each mutant is `Cert.checkHistory8AWith acue` with one cue test.

| mutant | breaks | killed by property |
|---|---|---|
| M84 tribunal cues without the claim | `acue h a := anchorCueOk11 h a ‖ anchorTribunalCues.any …` | `anchorTribunal_no_claim` (an unclaimed anchored row whose only anchor cue is "the court of international trade" stays `anchorNoCue`; an unclaimed "district court" anchor is ok) |
| M85 tribunal list dropped with the claim | `acue h a := if h.anchorTribunal then anchorWideCue9 a else anchorCueOk9 h a` | `anchorTribunal_eq` (a claimed "court of international trade" anchor is ok) |
| M86 no anchor-cue test under the claim | `acue h a := if h.anchorTribunal then true else anchorCueOk9 h a` | `anchorTribunal_sound` (a claimed anchor with no cue of any of the four lists is not admitted) |

Guards: the 3 new mutants and 3 new properties form a diagonal (M84 keeps the claimed behaviour, M85 and M86 keep the
unclaimed one; M84 and M86 admit the claimed tribunal row; M84 and M85 reject the claimed no-cue row); no new mutant
is caught by an earlier property (they change only the new field) and no earlier mutant by a new property; count
guard `(27, 8, 6, 13, 10, 3, 8, 5, 4, 3, 86)`. Examples: `#guard`s on each tribunal phrase with the claim (ok) and
without (anchorNoCue); `anchorWide` alone does not accept a tribunal phrase; both claims; a claimed row with the
tribunal cue but an anchor disqualifier / unresolved target / wrong part (the other checks still bite); a claimed
bridged row (bridge verdict); a claimed row without an anchor line (round-10 verdict); a claimed trialBridge row (the
trial check after the union cue).

### 1.4 Fixture `round11/fixtures/tribunal`

A small stage built from the round-10 tbridge fixture data: anchored history rows whose anchor quote's only cue is a
tribunal phrase, with and without the claim (ok / anchorNoCue), with both claims, a claimed row failing another
anchored check, a claimed row without an anchor line and a claimed bridged row (unused, counted), a duplicate claim
line, an unknown id; expected certs and counters; the same data without the claim lines = the round-10 binary's
output byte for byte.

## 2. Section 5.1 as built (tables, loader, runner)

- Every statement of §1.2 proved exactly as written (the Lean text is the §1.2 text); no `sorry`, no new axiom, no
  `native_decide` (the added theorems use `propext`, `Quot.sound`, `Classical.choice` only). Helpers locked as
  additions: `anchorTail_none`, `checkHistory8AWith_cue9`. The definitions are §1.1's.
- **Cue table** (appended; the JSON text up to its last list, `CueTable.lean` up to `end CaseLaw2.Cert` and
  `reader/cue_table.py` are byte-identical prefixes of the round-10 files): `_note_round11`, `anchor_tribunal` (the six
  DESIGN11 phrases) → Lean `anchorTribunalCues`, Python `ANCHOR_TRIBUNAL`. `gen_cues.py --skip-ref` (ref/ is ref11's).
- **Certificate.lean**: `HClaims.anchorTribunal : Bool := false` (round-10 and earlier functions ignore it); a round-11
  section at the end (`anchorTribunalCue`, `anchorCueOk11`, `anchorTail`, `checkHistory8AWith`, `checkHistory8A`,
  `checkHistory9A`, `checkHistory11`, the theorems).
- **Data.lean**: `HClaimRow.parse` accepts `anchorTribunal`.
- **Run.lean**: `HClaimTab.tribunal` (a kept line joins `byId` like `anchorWide`; a repeat is a duplicate);
  `HClaims.anchorTribunal` set from it; the history step is `Cert.checkHistory9A tb? zs …` then `Cert.remandThen`
  (= `Cert.checkHistory11`); the zone and remand counters read `checkHistory9A`'s verdict as round 10 read
  `checkHistory9T`'s; `nTribUnused` counts claimed rows with no anchor line or with a bridge line; `HClaimTab.summary`
  writes `hclaim_anchortribunal`, `hclaim_anchortribunal_unused` after the `oldCircuit` counters, only when the
  tribunal set is non-empty.
- **Examples.lean**: 31 new `#guard`s (548 → 579; Mutants 26 → 29) (each tribunal phrase with / without the claim / under `anchorWide` alone / both
  claims; the union lists under the claim; no cue of any list; the other anchored checks under the claim
  (disqualifier, unresolved, part, mismatch, noCue, noAuthority, targetLater); unused claims (no anchor, bridge);
  round-10 replays; a counted trialBridge claim with a tribunal anchor; `checkHistory11`).
- **Mutants.lean**: `Impl.checkHistory8A`, M84–M86, `properties11` (`anchorTribunal_no_claim`, `anchorTribunal_eq`,
  `anchorTribunal_sound`); the 3×3 round-11 matrix is the diagonal (guarded), no cross-kills with earlier properties
  (guarded both ways); count guard `(27, 8, 6, 13, 10, 3, 8, 5, 4, 3, 86)`.
- **Fixture** `round11/fixtures/tribunal` (`make_tribunal_fixture.py`, `wsl/r11_tribunal_fixture.sh`): 15 rows: ok
  ×6 (one per phrase; row 4 with anchorWide too), anchorNoCue ×3 (no claim; anchorWide alone; no cue of any list),
  anchorDisqualified, anchorPart, a plain anchor cue under the claim (ok), a counted trialBridge claim with the
  tribunal anchor (ok), unused ×2 (no anchor line; a bridge line); a duplicate line, an unknown id. Counters
  `hclaim_rows 14, unknown 1, duplicates 1, admitted 10, rejected 4, anchorwide 2 / unused 0, anchortribunal 13 /
  unused 2`. `data_noclaim` (no anchorTribunal line): round-10 verdicts, no tribunal counter, and every output equals
  the frozen round-10 binary's (e7e32592) byte for byte.
- **Scripts** (new): `wsl/r11_lean.sh` (sync + build), `wsl/r11_tribunal_fixture.sh`, `wsl/r11_repro.sh` (=
  r10_repro.sh on round-11 run slots), `wsl/r11_r10tbridge_fixture.sh` / `wsl/r11_r10remand_fixture.sh` (copies that
  write nothing into round10/), `wsl/r11_final.sh` (all gates, one Lean run at a time, mirror source sha1 before and
  after); `wsl/lock_reason.txt` holds the round-11 reason (round 10's in `round11/pre/wsl/`).

## 3. Results (§5.1)

- Runner sha1 `a1cc4296022b1bd07401cc64b04e50449d0de9b3` (`~/caselaw2/r11_bin/caselaw2_lean11`, also kept as
  `~/caselaw2/r11_bin/caselaw2_lean11_s51`).
- Audit: locked 05:34 (292 → 298 theorems; 6 new, 0 changed, 0 problems); against round 10's lock
  (`round11/pre/audit/statements.lock`): 0 removed, 0 changed, 6 added (axioms of the added: propext, Quot.sound,
  Classical.choice). Statements fixed 05:24:10 (STATEMENTS.log "round 11 section 5.1 STATED"), before any code.
- Mutants 83 → 86 (M84–M86; properties 83 → 86, `properties11`); 3×3 diagonal, no cross-kills (guards).
  `#guard`s: Examples 548 → 579, Mutants 26 → 29.
- Gates (`wsl/r11_final.sh`, log `agents/lean11/r11_final_s51.log`, 05:35–06:11, one Lean run at a time): build,
  audit check 298/0/0, fixtures green (round11 tribunal; round-10 tbridge and remand, round-9 farimplicit and zone,
  round-8 bridge, round-7 joined — copies that write nothing back), regressions a a2 (16 files) and b c (15 files)
  byte-identical, `round10/out/v10d`, `round9/out/v9c`, `round8/out/v8e` reproduced byte for byte (every table;
  summary timing lines aside); the mirror's source sha1 unchanged from the gates' start to their end, and the Windows
  tree's sha1s unchanged (`agents/lean11/tree_sha1_s51.txt`). Also `round10/out/v10d` reproduced through infra11's
  `wsl/r11_run.sh` (`R11BIN=…caselaw2_lean11_s51 NOBUILD=1`, stage `lean11_v10d` = stage11 with no delta; 8 tables
  byte for byte, 06:13; cleaned with clean11.sh).
- Slip: none (no tree edit while a gate ran; §5.2 drafted in my scratchpad only).

## 5. Identity-tie evidence, `history_identity.tsv` (DESIGN11 §5.2, D11-5, D11-8) — stated 06:14, before its code

### 5.0 Readings

These agree with ref11's Q11-5..Q11-10 (binding on both sides by D11-8, 05:58).

| # | point | what the Lean does |
|---|---|---|
| L11-10 | the table | optional `history_identity.tsv`, 7 fields `id, form, token, d_start, d_end, t_start, t_end`; a line that is not UTF-8, has ≠ 7 fields, a non-digit offset, or a `form` other than `docket` / `cite` / `date` is a bad line (the loader's `bad_rows history_identity.tsv n` and `identity_bad_rows`); a good line whose id is no history row is ignored (L11-15); a later good line for a kept id is `identity_dup_rows`; an empty token is a good line (it fails the test) |
| L11-11 | the spans | `[d_start, d_end)` of D's own text (the row's `by`: its decisions2 hash and the windows of that hash), `[t_start, t_end)` of T's own text (the target's hash and windows), each read like round 10's spans (`spanText`: the first usable covering window, normalised tab / CR / LF → space), non-empty, ≤ `identity_span_max` (200), ASCII lower-cased (`identitySpan`); `by = -1` or no hash: unreadable ⇒ the test fails |
| L11-12 | docket / cite | `compact(token)` (Lean's `compact`: lower-case, keep `[0-9a-z]`) has ≥ 4 characters and a digit (`docketTokenOk`), and is a substring of `compact(D span)` and of `compact(T span)` |
| L11-13 | date (Q11-7) | the token is 8 ASCII digits, its number equals date(T) (decisions2), date(T) is a calendar date (`validDate`; 0 / unknown / non-calendar fails: "a non-calendar date has no form"), and each lower-cased span holds one of `dateForms date(T)` (round 10's two forms) as a substring |
| L11-14 | where | after the row's complete round-11 verdict (`checkHistory11`: round 10's remand step included) admits; a failing verdict keeps its reason and is not counted as checked. Failure ⇒ `identityTie` (a new `Reason`) |
| L11-15 | counters (only when the file has a line, good or bad), after the tbridge counters | `identity_lines` (ids kept), `identity_checked_rows` (rows with a line whose full-rule-set verdict admits), `identity_failed_rows` (of those, rows whose full-rule-set verdict becomes `identityTie`), `identity_dup_rows`, `identity_bad_rows`. an unknown id is not a bad line and is in no summary counter (Q-L11-1, settled by D11-8 05:58 with ref11's Q11-5..10) |
| L11-16 | cue table (appended) | `identity_span_max` 200 → Lean `identitySpanMax`, Python `IDENTITY_SPAN_MAX` |
| L11-17 | presence | absent or empty file: every row's identity line is `none` and `identityThen none` is the identity (`no_identity_line_no_change`); no counter, no `Problems` entry for an absent file ⇒ round-11 §5.1 output (and v10d etc.) byte for byte. `certNodes` asks for nothing new (D and T are already every history row's nodes) |

### 5.1 Definitions (Certificate.lean, a round-11 §5.2 section)

```lean
-- reason appended: | identityTie
structure Identity where
  form : String
  token : String
  dSha : String                -- D's text hash (decisions2; "" unknown) and windows
  dWindows : List Window
  dStart : Nat
  dStop : Nat
  tSha : String                -- T's text hash and windows
  tWindows : List Window
  tStart : Nat
  tStop : Nat
  tDate : Nat := 0             -- decisions2 date of T (0 unknown)

/-- A span of a node's own text, lower-cased (`spanText` with the bound `n`). -/
def identitySpanN (n : Nat) (c : Input) (sha : String) (ws : List Window) (s e : Nat) : Option String :=
  (spanText c sha ws s e n).map String.toLower
def identitySpan (c : Input) (sha : String) (ws : List Window) (s e : Nat) : Option String :=
  identitySpanN identitySpanMax c sha ws s e
def dateTokenOk (k : String) (d : Nat) : Bool :=
  validDate d && decide (k.length = 8) && k.all Char.isDigit && decide (k.toNat? = some d)
/-- The form's condition on D's span `d` and T's span `t`. -/
def identityFormOk (i : Identity) (d t : String) : Bool :=
  if i.form == "docket" || i.form == "cite" then
    docketTokenOk (compact i.token) && hasSub (compact d) (compact i.token) && hasSub (compact t) (compact i.token)
  else if i.form == "date" then
    dateTokenOk i.token i.tDate && (dateForms i.tDate).any (hasSub d) && (dateForms i.tDate).any (hasSub t)
  else false
def identityOkWith (n : Nat) (formOk : Identity → String → String → Bool) (c : Input) (i : Identity) : Bool :=
  match identitySpanN n c i.dSha i.dWindows i.dStart i.dStop, identitySpanN n c i.tSha i.tWindows i.tStart i.tStop with
  | some d, some t => formOk i d t
  | _, _ => false
def identityOk : Input → Identity → Bool := identityOkWith identitySpanMax identityFormOk
/-- **identityTie**, after the row's complete round-11 verdict `res` (a failure keeps its reason). -/
def identityThenWith (ok : Input → Identity → Bool) (i? : Option Identity) (c : Input) (res : Result) : Result :=
  match i? with
  | none => res
  | some i => if res.admitted then (if ok c i then res else .fail .identityTie) else res
def identityThen : Option Identity → Input → Result → Result := identityThenWith identityOk
/-- **The runner's history step in round 11 (§5.1 + §5.2).** -/
def checkHistory11I (i? : Option Identity) (t? : Option TBridge) (rm? : Option Remand) (zs : List Zone) (c : Input)
    (a? : Option Anchor) (b? : Option Bridge) (h : HClaims) : Result :=
  identityThen i? c (checkHistory11 t? rm? zs c a? b? h)
```

### 5.2 Theorems (3, as DESIGN11 names them)

```lean
/-- **No identity line, no change** (§5.2): without a line the step is §5.1's, and the wrapper is the identity. -/
theorem no_identity_line_no_change (t? : Option TBridge) (rm? : Option Remand) (zs : List Zone) (c : Input)
    (a? : Option Anchor) (b? : Option Bridge) (h : HClaims) (res : Result) :
    checkHistory11I none t? rm? zs c a? b? h = checkHistory11 t? rm? zs c a? b? h ∧ identityThen none c res = res

/-- **A failing verdict keeps its reason** (§5.2). -/
theorem identityThen_fail_keeps (i? : Option Identity) (c : Input) (res : Result) (h : res.admitted = false) :
    identityThen i? c res = res

/-- **Identity-tie soundness** (§5.2): an admitted row with a line has an admitted round-11 verdict (which is the
verdict); D's span and T's span are each non-empty, at most `identitySpanMax` characters, the lower-cased text of a
usable window of that node's own text; and the form's condition holds on the two spans: for `docket` / `cite` the
compact token (≥ 4 characters, a digit) is in both compact spans; for `date` the token is the 8 digits of date(T)
(known) and both spans hold a date form of it. -/
theorem identityTie_sound (i : Identity) (t? : Option TBridge) (rm? : Option Remand) (zs : List Zone) (c : Input)
    (a? : Option Anchor) (b? : Option Bridge) (h : HClaims)
    (hadm : (checkHistory11I (some i) t? rm? zs c a? b? h).admitted = true) :
    (checkHistory11 t? rm? zs c a? b? h).admitted = true ∧
      checkHistory11I (some i) t? rm? zs c a? b? h = checkHistory11 t? rm? zs c a? b? h ∧
      i.dStart < i.dStop ∧ i.dStop - i.dStart ≤ identitySpanMax ∧ i.tStart < i.tStop ∧ i.tStop - i.tStart ≤ identitySpanMax ∧
      ∃ d t, identitySpan c i.dSha i.dWindows i.dStart i.dStop = some d ∧
        identitySpan c i.tSha i.tWindows i.tStart i.tStop = some t ∧
        (∃ w ∈ i.dWindows, usable (spanInput c i.dSha i.dWindows i.dStart i.dStop) w = true ∧
          d = (slice (norm w.text) (i.dStart - w.start0) (i.dStop - i.dStart)).toLower) ∧
        (∃ w ∈ i.tWindows, usable (spanInput c i.tSha i.tWindows i.tStart i.tStop) w = true ∧
          t = (slice (norm w.text) (i.tStart - w.start0) (i.tStop - i.tStart)).toLower) ∧
        (((i.form = "docket" ∨ i.form = "cite") ∧ 4 ≤ (compact i.token).length ∧
            (compact i.token).any Char.isDigit = true ∧ hasSub (compact d) (compact i.token) = true ∧
            hasSub (compact t) (compact i.token) = true) ∨
          (i.form = "date" ∧ validDate i.tDate = true ∧ i.token.length = 8 ∧ i.token.all Char.isDigit = true ∧
            i.token.toNat? = some i.tDate ∧ (dateForms i.tDate).any (hasSub d) = true ∧
            (dateForms i.tDate).any (hasSub t) = true))
```

Helpers expected (additions): `identitySpan_some` (from `spanText_some`), `identityOk_spec`, `identityFormOk_spec` (the form's condition from
`identityOk = true`), `identityThen_some_admitted` (the general form on any verdict `res`).

### 5.3 Mutants (3; new `Impl` field `identityThen`; properties `properties11b`)

| mutant | breaks | killed by property |
|---|---|---|
| M87 token in D's span only | `identityFormOk` without the T-span test (docket / cite) | `identityTie_sound: token in T's span` (a docket line whose token is in D's span only) |
| M88 date token ≠ date(T) | date form: the forms of the token's own date, no `token = date(T)` test | `identityTie_sound: date of T` (token 20150930, both spans "september 30, 2015", date(T) 20150101) |
| M89 span over 200 accepted | `identityOkWith 1000000000 identityFormOk` | `identityTie_sound: span bound` (a docket line with a 260-character D span holding the token) |

Each property also admits the good docket line. Guards: 3×3 diagonal, no cross-kills with earlier properties; count
guard `(27, 8, 6, 13, 10, 3, 8, 5, 4, 3, 3, 89)`. Examples: each form ok; each failure (token missing in D / in T;
short token; no digit; date token ≠ date(T); date(T) unknown; non-digit / 7-digit token; a span missing a date form;
both date forms; a span > 200 / empty / no window / wrong hash; an unknown form); a failing verdict kept; no line.

### 5.4 Fixture `round11/fixtures/identity`

Built on the tribunal fixture's data: history rows with an identity line (docket, cite, date ok; each failure; a
failing verdict kept; a bad line of each kind; an unknown id; a duplicate) with expected certs and counters; without
the table and with an empty one = §5.1's output byte for byte (and = the round-10 binary's on data without claims).

## 6. Section 5.2 as built

- Every statement of §5.2 proved exactly as written (one proof — `identityThen_some_admitted`, a helper — rewritten
  after the first build; no statement touched); no `sorry`, no new axiom, no `native_decide`. Helpers locked as
  additions: `identitySpan_some`, `identityOk_spec`, `identityFormOk_spec`, `identityThen_some_admitted`.
- Definitions as §5.1 of this section (L11-13 per Q11-7: `dateTokenOk` requires `validDate date(T)`), reason
  `identityTie` appended to `Reason`.
- **Cue table** (appended): `_note_round11_s52`, `identity_span_max` 200 → Lean `identitySpanMax`, Python
  `IDENTITY_SPAN_MAX` (`gen_cues.py --skip-ref`; `--check` clean).
- **Data.lean**: `IdentityRow` (7 fields; a form other than docket / cite / date or a non-digit offset ⇒ bad row) from
  the optional `history_identity.tsv` (`Tables.identities`; a `Problems` entry only when the file exists).
- **Run.lean**: `identityTable` / `IdentityTab.summary` (D11-8: unknown ids in no counter; `identity_lines`,
  `identity_checked_rows`, `identity_failed_rows`, `identity_dup_rows`, `identity_bad_rows` after the tbridge
  counters, only when the file has a line); the history step: `checkHistory9A`, `remandThen` (= `checkHistory11`), then
  `Cert.identityThen` with the row's `Cert.Identity` (D = `by`'s hash and windows, T = the target's, date(T) from
  decisions2) (= `checkHistory11I`); the remand counters read the §5.1 verdict, the identity counters the §5.1 verdict
  (checked) and the final one (failed); every other counter the final verdict.
- **Examples.lean** 579 → 607 `#guard`s; **Mutants.lean** M87–M89, `properties11b`, 3×3 diagonal guarded both ways,
  count guard `(27, 8, 6, 13, 10, 3, 8, 5, 4, 3, 3, 89)` (29 → 32 `#guard`s).
- **Fixture** `round11/fixtures/identity` (`make_identity_fixture.py`, `wsl/r11_identity_fixture.sh`): 10 rows: ok
  ×3 (docket, cite, date with the two date forms), identityTie ×4 (token in D's span only; wrong citation; a date token
  other than date(T); a D span of 248 characters), a failing verdict kept (anchorNoCue, not counted), a bridged row
  with a good line (ok), a row without a line; a duplicate, an unknown id, three bad lines. Counters lines 9, checked 8,
  failed 4, dup 1, bad 3 (and `bad_rows history_identity.tsv 3`); every other counter = data_noident's (verdict-dependent
  ones aside). `data_noident` = the §5.1 binary's (a1cc4296) output byte for byte; an empty table = none.
- Audit: locked 06:23 (298 → 305; 7 new, 0 changed); against round 10's lock: 0 removed, 0 changed, 13 added (axioms
  propext, Quot.sound, Classical.choice). Statements fixed 06:14:05 (STATEMENTS.log "round 11 section 5.2 STATED").
- `wsl/r11_final.sh` now builds into `~/caselaw2/r11_bin/caselaw2_lean11_cand` and promotes it to `caselaw2_lean11`
  only when every gate passes.
- Gates (`r11_final_s52.log`, 06:23–06:49): build, audit 305/0/0, 8 fixtures green, regressions a a2 (16 files) b c (15
  files) byte-identical, v10d (06:45), v9c (06:47), v8e (06:49) reproduced byte for byte; mirror sources unchanged during
  the gates; Windows tree sha1s unchanged (`tree_sha1_s52.txt`). Binary `ea2e1d7e` (`caselaw2_lean11`, also
  `caselaw2_lean11_s52`). LEAN_READY rewritten 06:50. The lead froze the round at 06:50 on the §5.1 binary
  (`caselaw2_lean11_s51`, a1cc4296), which was not touched. Slip: none.
