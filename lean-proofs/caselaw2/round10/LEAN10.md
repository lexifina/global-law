# Round 10, Lean: remand bridge evidence (§4)

Contract: `DESIGN10.md` §4 with the D10-5 amendment (9 columns, docket spans) and D10-6 (ref10's Q10-1..10 readings,
binding on Lean and reference). Written by the agent `lean10`, 14 Nov 2026 (started 03:48). Sections 0 and 1 were
written **before** any code or proof (03:53–03:58): the statements are the target; a statement that proves false is
refuted and reported, never weakened silently. Sections 2–3 are written after the build.

Backup of everything changed: `round10/pre/` (round 9's file list; `SHA1SUMS.txt`, 106 files). `round10/pre/CaseLaw2`
is the round-9 final state (binary 22bab5cd).

## 0. Readings of points DESIGN10 §4 leaves open

| # | point | what the Lean does |
|---|---|---|
| L10-1 | the docket field | the runner loads no docket per node (decisions2 has none): D10-5's spans. `[bd_start, bd_end)` of B's text and `[t_start, t_end)` of the target's text are read like B's quote (L10-2), each non-empty and ≤ `remandDocketSpanMax` (200). `compact` = Lean's `Cert.compact` (ASCII lower-case, keep `Char.isAlphanum`, i.e. `[0-9a-z]`) |
| L10-2 | B's quote (no quote column) | D10-6 / Q10-2: the text at `[b_start, b_end)` of the **first** usable window (well formed and hash-consistent: round 4's `usable`) of B's own text (B's hash from decisions2, the windows cert_text gives that hash), normalised (`norm`: tab / CR / LF → space one for one) and ASCII lower-cased; `b_end ≤ b_start`, a span longer than `remandQuoteMax` (600) or no usable covering window ⇒ `remandCue`. A node with no hash (no decisions2 row, or "") has no usable window. (With `window_sha.tsv` every usable window is the corpus text, so "first" does not matter) |
| L10-3 | order of the checks | court, date, docket, cue, tie; the first failure is the reason (Q10-4) |
| L10-4 | court | decisions2 raw court id of B and of the target, equal; B without a decisions2 row ⇒ `remandCourt` (Q10-5) |
| L10-5 | dates | decisions2 dates (`yyyymmdd`) of the order (`by`), B and the target; each must be a calendar date (year > 0, month 1–12, day 1–days of the month, proleptic Gregorian leap years); else `remandDate` (an order `by = -1` has date 0). Then `date(target) < date(order) ≤ date(B)` (as numbers: order-preserving on calendar dates) and `dayNum(B) ≤ dayNum(order) + remandDaysMax` (1,826) with `dayNum` = the day count from 0001-01-01 (Q10-6) |
| L10-6 | cue | the lower-cased quote (L10-2) holds a `remand_court` phrase ("supreme court") and a `remand_cue` phrase as plain substrings (`hasSub`; any order, overlap allowed) (Q10-7) |
| L10-7 | tie | any of (a) a key of the citation index that maps (unambiguously; the loader drops ambiguous keys) to the order node is a substring of `compact(quote)` — positions over the quote's alphanumeric characters, a key of any of the index's key lengths (`keyLengths`) at any alphanumeric position (equivalently a substring of the compact quote); no index or no order node: no key; (b) `compact(docket)` is a substring of `compact(quote)`; (c) a date form of date(order) is a substring of the lower-cased quote (Q10-8) |
| L10-8 | date forms (Q10-1, exactly two) | `<month> <d>, <yyyy>` with the full lower-case month name (`remand_months`) and the day without a leading zero ("january 5, 2015"), and `<abbr> <d>, <yyyy>` with the abbreviations of `remand_months_abbr` (jan. feb. mar. apr. aug. sept. sep. oct. nov. dec.; May, June, July have none). New cue-table keys (L10-12) |
| L10-9 | which rows are checked | a history row with a line whose complete round-9 verdict (`checkHistory9J`: round-8 step, judge forms, zone test) is admitted (`ok` or `okUnverifiedBy`); a failing verdict (incl. `noAuthority`, `partZone`) keeps its reason (`remandThen_fail_keeps`). Both rule sets (full, S/L) get the same wrapper. A non-admitted history row feeds nothing in the runner (history events are pushed only for admitted rows), so Q10-10's "findings dropped" holds without extra code |
| L10-10 | loading (Q10-9) | `history_remand.tsv` optional, 9 fields; a line that is not UTF-8, has ≠ 9 fields, or whose `b_node`, `b_start`, `b_end`, `bd_start`, `bd_end`, `t_start`, `t_end` is not ASCII digits is a bad line (the loader's `bad_rows history_remand.tsv n` and `remand_bad_rows`); a good line whose id is no history row's id is ignored and counted nowhere; a later good line for a kept id is `remand_dup_rows`; an empty docket is a good line (it fails `remandDocket`) |
| L10-11 | counters (only when the file has a line, good or bad) | `remand_lines` (ids kept), `remand_checked_rows` (rows with a line whose full-rule-set round-9 verdict admits), `remand_failed_rows` (of those, rows whose full-rule-set verdict becomes a remand failure), `remand_dup_rows`, `remand_bad_rows`, in that order after the zone counters. The zone counters keep reading the round-9 verdict (a row refused by the remand check did reach the zone test) |
| L10-12 | cue table (appended; earlier lines byte-identical) | `_note_round10`, `remand_court` ["supreme court"], `remand_cue` ["vacat", "remand", "in light of", "further consideration"], `remand_months` (12), `remand_months_abbr` (12 lists), `remand_quote_max` 600, `remand_docket_span_max` 200, `remand_days_max` 1826 → Lean `remandCourtCues`, `remandCues`, `remandMonths`, `remandMonthsAbbr`, `remandQuoteMax`, `remandDocketSpanMax`, `remandDaysMax`; Python (reader copy) `REMAND_COURT`, `REMAND_CUE`, `REMAND_MONTHS`, `REMAND_MONTHS_ABBR`, `REMAND_QUOTE_MAX`, `REMAND_DOCKET_SPAN_MAX`, `REMAND_DAYS_MAX`. `gen_cues.py --skip-ref` (ref/ is ref10's) |
| L10-13 | presence | absent or empty file: every row's remand line is `none` and `remandThen none` is the identity (`no_remand_line_no_change`); no counter, no `Problems` entry for an absent file; `certNodes` asks for no extra hash. So `round9/out/v9c` (and `round8/out/v8e`, regressions) are reproduced byte for byte |

Questions for the lead: none open (the docket question was settled by D10-5 before I asked; D10-6 settles the rest).

## 1. Definitions and theorems (stated first)

Checker definitions in `LegalProofs/CaseLaw2/Certificate.lean` (namespace `CaseLaw2.Cert`, a new round-10 section at
the end).

### 1.1 Definitions

```lean
-- reasons appended to `Reason`
  | remandCourt | remandDate | remandDocket | remandCue | remandTie

/-- The remand line of a history row (`history_remand.tsv`) with the facts it is checked against. -/
structure Remand where
  b : Nat
  bSha : String                 -- B's text hash (decisions2; "" unknown) and the windows of that hash
  bWindows : List Window
  tSha : String                 -- the target's text hash and windows
  tWindows : List Window
  start : Nat                   -- B's quote [b_start, b_end)
  stop : Nat
  docket : String
  bdStart : Nat                 -- [bd_start, bd_end) of B's text
  bdStop : Nat
  tStart : Nat                  -- [t_start, t_end) of the target's text
  tStop : Nat
  bCourt : Option Nat := none   -- decisions2 raw court ids (none: no row)
  tCourt : Option Nat := none
  oDate : Nat := 0              -- decisions2 dates of the order (`by`), B, the target (0: unknown)
  bDate : Nat := 0
  tDate : Nat := 0
  order : Option Nat := none    -- the order node (`by`; none for -1)
  lens : List Nat := []         -- the index's key lengths, longest first

/-- A span of a node's text read as a certificate quote over that node's windows (hash, windows, span). -/
def spanInput (c : Input) (sha : String) (ws : List Window) (s e : Nat) : Input :=
  { c with textSha := sha, shas := [sha], windows := ws, start := s, stop := e }
/-- The normalised text at `[s, e)` of the first usable window covering it (non-empty, at most `maxLen`). -/
def spanText (c : Input) (sha : String) (ws : List Window) (s e maxLen : Nat) : Option String :=
  if sha.isEmpty || !decide (s < e) || !decide (e - s ≤ maxLen) then none
  else (ws.find? (usable (spanInput c sha ws s e))).map fun w => slice (norm w.text) (s - w.start0) (e - s)

def remandQuote (c : Input) (r : Remand) : Option String :=
  (spanText c r.bSha r.bWindows r.start r.stop remandQuoteMax).map String.toLower

-- 1. court, date
def remandCourtOk (r : Remand) : Bool := r.bCourt.isSome && r.bCourt == r.tCourt
def leapYear (y : Nat) : Bool := (y % 4 == 0 && y % 100 != 0) || y % 400 == 0
def monthDays (y m : Nat) : Nat   -- 31/30/28-29; 0 for a month outside 1–12
def dateYear (d : Nat) : Nat := d / 10000
def dateMonth (d : Nat) : Nat := d / 100 % 100
def dateDay (d : Nat) : Nat := d % 100
def validDate (d : Nat) : Bool :=
  decide (0 < dateYear d) && decide (1 ≤ dateDay d) && decide (dateDay d ≤ monthDays (dateYear d) (dateMonth d))
/-- days since 0001-01-01 (proleptic Gregorian), +1 -/
def dayNum (d : Nat) : Nat :=
  let y := dateYear d - 1
  365 * y + y / 4 - y / 100 + y / 400 +
    ((List.range (dateMonth d - 1)).map (fun i => monthDays (dateYear d) (i + 1))).sum + dateDay d
def remandDateOk (r : Remand) : Bool :=
  validDate r.oDate && validDate r.bDate && validDate r.tDate && decide (r.tDate < r.oDate) &&
    decide (r.oDate ≤ r.bDate) && decide (dayNum r.bDate ≤ dayNum r.oDate + remandDaysMax)
-- 2. docket
def docketTokenOk (k : String) : Bool := decide (4 ≤ k.length) && k.any Char.isDigit
def spanHas (c : Input) (sha : String) (ws : List Window) (s e : Nat) (k : String) : Bool :=
  match spanText c sha ws s e remandDocketSpanMax with
  | some t => hasSub (compact t) k
  | none => false
def remandDocketOk (c : Input) (r : Remand) : Bool :=
  docketTokenOk (compact r.docket) && spanHas c r.bSha r.bWindows r.bdStart r.bdStop (compact r.docket) &&
    spanHas c r.tSha r.tWindows r.tStart r.tStop (compact r.docket)
-- 3. cue (on the lower-cased quote)
def remandCueOk (q : String) : Bool := remandCourtCues.any (hasSub q) && remandCues.any (hasSub q)
-- 4. tie
def keyTie (c : Input) (r : Remand) (q : String) : Bool :=
  match c.citeIndex, r.order with
  | some m, some o => (firstSuffix (fun s => r.lens.any (fun L => citeOf m s L == some o)) (alnumPos q.toList 0)).isSome
  | _, _ => false
def dateForms (d : Nat) : List String :=
  let tail := " " ++ toString (dateDay d) ++ ", " ++ toString (dateYear d)
  if dateMonth d = 0 then [] else
    ((remandMonths[dateMonth d - 1]?).toList ++ (remandMonthsAbbr[dateMonth d - 1]?).getD []).map (· ++ tail)
def remandTieOk (c : Input) (r : Remand) (q : String) : Bool :=
  keyTie c r q || hasSub (compact q) (compact r.docket) || (dateForms r.oDate).any (hasSub q)

/-- The five steps with their tests as parameters (for the mutants); `none` = all hold. -/
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

/-- **remandBridge**, after the row's complete round-9 verdict `res` (a failure keeps its reason). -/
def remandThenWith (rf : Input → Remand → Option Reason) (rm? : Option Remand) (c : Input) (res : Result) : Result :=
  match rm? with
  | none => res
  | some r => if res.admitted then (match rf c r with | some e => .fail e | none => res) else res
def remandThen : Option Remand → Input → Result → Result := remandThenWith remandFail

/-- **The runner's history step in round 10.** -/
def checkHistory10 (rm? : Option Remand) (zs : List Zone) (c : Input) (a? : Option Anchor) (b? : Option Bridge)
    (h : HClaims) : Result :=
  remandThen rm? c (checkHistory9J zs c a? b? h)
```

### 1.2 Theorems (3 stated, as DESIGN10 names them)

```lean
/-- **No remand line, no change**: without a line the round-10 step is the round-9 step (and the wrapper is the
identity on any verdict). -/
theorem no_remand_line_no_change (zs : List Zone) (c : Input) (a? : Option Anchor) (b? : Option Bridge)
    (h : HClaims) (res : Result) :
    checkHistory10 none zs c a? b? h = checkHistory9J zs c a? b? h ∧ remandThen none c res = res

/-- **A failing verdict keeps its reason.** -/
theorem remandThen_fail_keeps (rm? : Option Remand) (c : Input) (res : Result) (h : res.admitted = false) :
    remandThen rm? c res = res

/-- **Remand bridge soundness**: an admitted row with a line has an admitted round-9 verdict (which is the verdict);
B and the target share the court; the target is before the order, B between the order and 1,826 days after it (all
three calendar dates); the compact docket token (≥ 4 characters, a digit) is in a span of B's text and in a span of
the target's text; B's quote holds "supreme court" and a remand cue, and a tie to the order. -/
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
        (keyTie c r q = true ∨ hasSub (compact q) (compact r.docket) = true ∨ (dateForms r.oDate).any (hasSub q) = true)
```

Helpers expected (locked as additions): `spanText_some` (a read span is the text of a usable window of that hash's
windows covering it, non-empty, within the bound: `spanText c sha ws s e n = some t → s < e ∧ e - s ≤ n ∧ ∃ w ∈ ws,
usable (spanInput c sha ws s e) w = true ∧ t = slice (norm w.text) (s - w.start0) (e - s)`), `keyTie_spec` (`keyTie c r q
= true → ∃ m o, c.citeIndex = some m ∧ r.order = some o ∧ ∃ s, s <:+ alnumPos q.toList 0 ∧ ∃ L ∈ r.lens, citeOf m s L =
some o`), `remandFail_none` (the five tests hold when `remandFail c r = none`), `remandThen_some_admitted` (the general
form of the soundness on any verdict `res`), `remand_order` (`remandFail` = the first failing test, for the guards).

### 1.3 Mutants (4; `Mutants.lean`, properties `properties10`)

New `Impl` field `remandThen : Option Cert.Remand → Cert.Input → Cert.Result → Cert.Result := Cert.remandThen`; each
mutant is `Cert.remandThenWith (Cert.remandFailWith …)` with one test replaced.

| mutant | breaks | killed by property |
|---|---|---|
| M75 B before the order | `dateOk` without `date(order) ≤ date(B)` | `remandBridge_sound: B after the order` (B dated between the target and the order) |
| M76 B of another court | `courtOk := bCourt.isSome` | `remandBridge_sound: same court` (B of another court id) |
| M77 a docket token of B only | `docketOk` tests B's span only | `remandBridge_sound: docket in the target's text` (the target's span lacks the token) |
| M78 no tie | `tieOk := true` | `remandBridge_sound: tie` (B's quote names no citation, docket or date of the order) |

Guards: the 4 new mutants and 4 new properties form a diagonal; no new mutant is caught by an earlier property and
no earlier mutant by a new property; the count guard becomes `(27, 8, 6, 13, 10, 3, 8, 4, 78)`. Examples: `#guard`s on
a remand line (each reason; each tie form: key, docket, both date forms; dates: leap day, the 1,826-day bound,
non-calendar dates; a span over the 200 / 600 bound; a hash-required window with a wrong hash; a failing round-9
verdict kept; no line).

### 1.4 Fixture `round10/fixtures/remand`

A small stage built from the round-8 bridge fixture (`round8/fixtures/bridge`) data: history rows with a remand line
(admitted; each of the five reasons; a failing round-9 verdict with a failing line kept; a bad line; an unknown id; a
duplicate line), expected certs and counters; the same data without `history_remand.tsv`, and with an empty one, =
the fixture's output without the table byte for byte.

## 1b. D10-7 (§4 amendment 2): the reason-case tie (stated 04:08, before its code)

The §1 code was built, proved and locked (04:05) on the 9-column table; D10-7 (04:07) then changed the tie. The
statement of `remandBridge_sound` changes (a round-10 statement, locked 04:05 and not yet released: the next lock
shows it as changed; against round 9's lock the round is additions only).

| # | point | what the Lean does |
|---|---|---|
| L10-14 | the table | 12 fields: the 9 of D10-5 + `tie`, `o_start`, `o_end` (`o_start`, `o_end` ASCII digits, else a bad line; any other field count is a bad line). An empty `tie` with `o_start` = `o_end` = 0 is a good line whose (c2) fails |
| L10-15 | the order span | `[o_start, o_end)` of the order's own text (the row's `by`: its decisions2 hash, the windows of that hash), read as the other spans (`spanText`: first usable covering window, normalised), non-empty, ≤ `remandOrderSpanMax` (300); `by = -1` or no hash: unreadable, (c2) fails |
| L10-16 | tie (c2) | the lower-cased O span holds a `remand_order_cue` phrase ("in light of"), `compact(tie)` has ≥ `remandTieMin` (8) characters, and `compact(tie)` is a substring of `compact(O span)` and of `compact(B quote)` |
| L10-17 | the tie test | `remandTieOk = keyTie ∨ dateForms ∨ reasonTie`; tie (b) (the docket in B's quote) is gone. The docket test (step 2) is unchanged |
| L10-18 | cue table (appended after §4's keys) | `remand_order_cue` ["in light of"], `remand_order_span_max` 300, `remand_tie_min` 8 → Lean `remandOrderCues`, `remandOrderSpanMax`, `remandTieMin`; Python `REMAND_REASON_CUE`, `REMAND_ORDER_SPAN_MAX`, `REMAND_TIE_MIN` |

```lean
-- Remand: new fields
  tie : String := ""
  oSha : String := ""          -- the order's text hash (decisions2) and windows
  oWindows : List Window := []
  oStart : Nat := 0
  oStop : Nat := 0
/-- Step 4 (c2): the reason case named in the order's span and in B's quote. -/
def reasonTie (c : Input) (r : Remand) (q : String) : Bool :=
  match spanText c r.oSha r.oWindows r.oStart r.oStop remandOrderSpanMax with
  | some o => remandOrderCues.any (hasSub o.toLower) && decide (remandTieMin ≤ (compact r.tie).length) &&
      hasSub (compact o) (compact r.tie) && hasSub (compact q) (compact r.tie)
  | none => false
def remandTieOk (c : Input) (r : Remand) (q : String) : Bool :=
  keyTie c r q || (dateForms r.oDate).any (hasSub q) || reasonTie c r q
```

`remandBridge_sound` (revised; every other conjunct as §1.2): the last conjunct becomes

```lean
      ∃ q, remandQuote c r = some q ∧ remandCourtCues.any (hasSub q) = true ∧ remandCues.any (hasSub q) = true ∧
        (keyTie c r q = true ∨ (dateForms r.oDate).any (hasSub q) = true ∨
          ∃ o, spanText c r.oSha r.oWindows r.oStart r.oStop remandOrderSpanMax = some o ∧
            remandOrderCues.any (hasSub o.toLower) = true ∧ remandTieMin ≤ (compact r.tie).length ∧
            hasSub (compact o) (compact r.tie) = true ∧ hasSub (compact q) (compact r.tie) = true)
```

Helper (addition): `reasonTie_spec` (the third disjunct from `reasonTie = true`).

Mutant M79 (a tie string found in B only: (c2) without the O-span tests), killed by `remandBridge_sound: reason case
in the order's text` (the tie string in B's quote, not in O's span). M78 (no tie) is killed by both tie properties
(any tie mutant is weaker than "no tie"), so the round-10 guard states the 5×5 kill matrix exactly: the diagonal plus
(M78, reason-case property). Count guard `(27, 8, 6, 13, 10, 3, 8, 5, 79)`.

## 6. Trial-judgment bridge, claim `trialBridge` (DESIGN10 §6, D10-8, D10-9 = ref10's Q10-12..17) — stated 04:20, before its code

### 6.0 Readings

| # | point | what the Lean does |
|---|---|---|
| L10-20 | which rows take the claim (Q10-12) | `trialBridge` is a new value of `history_claim.tsv` (a line with it was a bad line before; v9c has none). It counts only on a history row of kind `reversed` or `vacated` WITH an anchor line and WITHOUT a bridge line; on any other row it is ignored (the round-9 step). Like `anchorWide`, a kept claim line puts its id in the claimed rows (`hclaim_rows`, `hclaim_admitted`, `hclaim_rejected` count it); its repeats are `hclaim_duplicates` |
| L10-21 | order of the checks (Q10-13) | anchored steps 1–5 (round 9's, with the `anchorWide` judge forms under that claim), then D's main quote by `checkBy` with the kind-cue test replaced by `trialBridgeD` (reason `trialBridgeD` in `noCue`'s place), the disqualifiers, the target evidence (given: anchored), the part rule (`claimPart`), then `trialBridgeT`, then `trialBridgeDate`, then `targetLater` and the power; then the zone test and the remand test as for every history row |
| L10-22 | `trialBridgeD` (Q10-14) | `claimCueOk h c` (the kind's cues; "set aside" on a vacated row with a `setAside` claim) and a `trial_court_names` phrase and no `intermediate_court_names` phrase, plain substrings of the normalised lower-cased main quote |
| L10-23 | `trialBridgeT` (Q10-15) | T's quote `[t_start, t_end)` of T's own text (the target's decisions2 hash, the windows of that hash; `spanText`: first usable covering window, normalised), non-empty, ≤ `tbridge_quote_max` (600), lower-cased; holds a `tbridge_cue` phrase ("affirm") and no `tbridge_negative` phrase; no line, no window, too long ⇒ `trialBridgeT` |
| L10-24 | `trialBridgeDate` (Q10-16) | date(T) and date(D) calendar dates (`validDate`), `date(T) < date(D)`, `dayNum(D) ≤ dayNum(T) + tbridge_days_max` (1,826); court(T), court(D) known (decisions2 raw ids) and different |
| L10-25 | loading (Q10-17) | optional `history_tbridge.tsv`, 3 fields `id, t_start, t_end`; not UTF-8, ≠ 3 fields, non-digit offsets ⇒ bad line (`bad_rows history_tbridge.tsv n`, `tbridge_bad_rows`); unknown id ignored, not counted; a later line for a kept id ⇒ `tbridge_dup_rows`; `tbridge_lines` = ids kept; the three counters (after the remand counters) only when the file has a line. No other new counter |
| L10-26 | cue table (appended) | `trial_court_names` (9), `intermediate_court_names` (7), `tbridge_cue` ["affirm"], `tbridge_negative` ["reversed", "reverse", "vacate", "set aside", "remand"], `tbridge_quote_max` 600, `tbridge_days_max` 1826 → Lean `trialCourtNames`, `intermediateCourtNames`, `tbridgeCues`, `tbridgeNegative`, `tbridgeQuoteMax`, `tbridgeDaysMax`; Python upper-case keys |
| L10-27 | presence | a row without the claim (or where the claim does not count) gets `t? = none`: the step is the round-9 step (`trialBridge_no_claim`), whatever `history_tbridge.tsv` holds. Without claim lines and without the table the output is §4's (and v9c's) byte for byte |

### 6.1 Definitions (Certificate.lean, a round-10 §6 section)

```lean
-- reasons appended: | trialBridgeD | trialBridgeT | trialBridgeDate
structure TBridge where
  tSha : String                       -- T's text hash (decisions2; "" unknown) and windows
  tWindows : List Window
  line : Option (Nat × Nat) := none   -- [t_start, t_end) of history_tbridge.tsv (none: no line)
  tDate : Nat := 0                    -- decisions2 dates of T and D (0 unknown)
  dDate : Nat := 0
  tCourt : Option Nat := none         -- decisions2 court ids of T and D
  dCourt : Option Nat := none
def trialKind : Kind → Bool
  | .hist .reversed | .hist .vacated => true
  | _ => false
def dQuote (c : Input) : String := (norm c.quote).toLower
def trialBridgeDOk (h : HClaims) (c : Input) : Bool :=
  claimCueOk h c && trialCourtNames.any (hasSub (dQuote c)) && !intermediateCourtNames.any (hasSub (dQuote c))
def tbridgeQuote (c : Input) (t : TBridge) : Option String :=
  t.line.bind fun (s, e) => (spanText c t.tSha t.tWindows s e tbridgeQuoteMax).map String.toLower
def trialBridgeTOk (c : Input) (t : TBridge) : Bool :=
  match tbridgeQuote c t with
  | some q => tbridgeCues.any (hasSub q) && !tbridgeNegative.any (hasSub q)
  | none => false
def trialBridgeDateOk (t : TBridge) : Bool :=
  validDate t.tDate && validDate t.dDate && decide (t.tDate < t.dDate) &&
    decide (dayNum t.dDate ≤ dayNum t.tDate + tbridgeDaysMax) && t.tCourt.isSome && t.dCourt.isSome &&
    t.tCourt != t.dCourt
/-- `checkBy` with the cue failure's reason and an extra test after the part rule as parameters. -/
def checkByX (cueOk : Input → Bool) (cueFail : Reason) (partRes : Input → Option Reason)
    (extra : Input → Option Reason) (c : Input) : Result   -- = checkBy's steps; `extra` between part and targetLater
def trialFailWith (tOk : Input → TBridge → Bool) (dateOk : TBridge → Bool) (t : TBridge) (c : Input) : Option Reason :=
  if !tOk c t then some .trialBridgeT else if !dateOk t then some .trialBridgeDate else none
def checkTrialWith (dOk : HClaims → Input → Bool) (tf : TBridge → Input → Option Reason) (h : HClaims) (t : TBridge) :
    Input → Result :=
  checkByX (dOk h) .trialBridgeD (claimPart orderHeadOk h) (tf t)
def checkHistory8TWith (dOk : HClaims → Input → Bool) (tf : TBridge → Input → Option Reason) (t? : Option TBridge)
    (c : Input) (a? : Option Anchor) (b? : Option Bridge) (h : HClaims) : Result :=
  match t?, a?, b? with
  | some t, some a, none =>
    if trialKind c.kind then anchoredBy (anchorCueOk9 h) (checkTrialWith dOk tf h t) c a else checkHistory8J c a? b? h
  | _, _, _ => checkHistory8J c a? b? h
def checkHistory8T := checkHistory8TWith trialBridgeDOk (trialFailWith trialBridgeTOk trialBridgeDateOk)
def checkHistory9T (t? : Option TBridge) (zs : List Zone) (c : Input) (a? : Option Anchor) (b? : Option Bridge)
    (h : HClaims) : Result := zoneThen zs c [] (checkHistory8T t? c a? b? h)
/-- **The runner's history step in round 10 (§4 + §6).** -/
def checkHistory10T (t? : Option TBridge) (rm? : Option Remand) (zs : List Zone) (c : Input) (a? : Option Anchor)
    (b? : Option Bridge) (h : HClaims) : Result := remandThen rm? c (checkHistory9T t? zs c a? b? h)
```

### 6.2 Theorems

```lean
/-- **No claim, no change** (§6): without a counted claim the step is round 9's, and the round-10 step is §4's. -/
theorem trialBridge_no_claim (zs : List Zone) (rm? : Option Remand) (c : Input) (a? : Option Anchor)
    (b? : Option Bridge) (h : HClaims) :
    checkHistory8T none c a? b? h = checkHistory8J c a? b? h ∧ checkHistory9T none zs c a? b? h = checkHistory9J zs c a? b? h ∧
      checkHistory10T none rm? zs c a? b? h = checkHistory10 rm? zs c a? b? h

/-- **Presence** (§6): a claimed row (reversed / vacated, anchored, no bridge line) without a `history_tbridge.tsv`
line is not admitted; rows without the claim are unchanged whatever the table holds (`trialBridge_no_claim`). -/
theorem no_tbridge_table_no_change (t : TBridge) (ht : t.line = none) (c : Input) (a : Anchor) (h : HClaims)
    (hk : trialKind c.kind = true) : (checkHistory8T (some t) c (some a) none h).admitted = false

/-- **Trial bridge soundness** (§6): an admitted claimed row passed the anchored checks; D's quote has a cue of its
kind (under its claims), a trial-court name and no intermediate-court name; T's quote (of T's own text) affirms and
has no negative cue; T is before D by at most `tbridgeDaysMax` days, the courts differ; and the round-9 tail of the
anchored row (D's quote at its offset, no disqualifier, part, order, power) admits. -/
theorem trialBridge_sound (t : TBridge) (c : Input) (a : Anchor) (h : HClaims)
    (hadm : (checkHistory8T (some t) c (some a) none h).admitted = true) (hk : trialKind c.kind = true) :
    anchorQuoteOk c a = true ∧ anchorCueOk9 h a = true ∧ anchorDisqualified a = false ∧ anchorResolves c a = true ∧
      anchorPartOk a = true ∧
      claimCueOk h c = true ∧ trialCourtNames.any (hasSub (dQuote c)) = true ∧
      intermediateCourtNames.any (hasSub (dQuote c)) = false ∧
      (∃ q, tbridgeQuote c t = some q ∧ tbridgeCues.any (hasSub q) = true ∧ tbridgeNegative.any (hasSub q) = false) ∧
      validDate t.tDate = true ∧ validDate t.dDate = true ∧ t.tDate < t.dDate ∧
      dayNum t.dDate ≤ dayNum t.tDate + tbridgeDaysMax ∧ t.tCourt.isSome = true ∧ t.dCourt.isSome = true ∧
      t.tCourt ≠ t.dCourt ∧
      (checkClaimedWith orderHeadOk claimCueOk h { c with selfText := true }).admitted = true
```

Helpers expected (additions): `checkByX_none` (`checkByX cue .noCue part (fun _ => none) = checkBy cue part`),
`checkByX_admitted` (an admitted `checkByX` passed `cueOk`, `extra = none`, and `checkBy cueOk partRes` admits),
`tbridgeQuote_some` (T's quote is the text of a usable window of T's text), `trialFail_none`.

### 6.3 Mutants (4; new `Impl` field `checkHistory8T`; properties `properties10b`)

| mutant | breaks | killed by property |
|---|---|---|
| M80 T's quote reverses | `tOk` without the negative test | `trialBridge_sound: T affirmed` (T's quote "affirmed in part and reversed in part") |
| M81 D names the intermediate court | `dOk` without the intermediate-name test | `trialBridge_sound: trial court only` (D's quote "the judgment of the court of appeals and of the district court is reversed") |
| M82 T dated after D | `dateOk` without `date(T) < date(D)` | `trialBridge_sound: T before D` |
| M83 the claim's cue test without the claim | `checkHistory8T none` applies `trialBridgeD` to anchored reversed / vacated rows | `trialBridge_no_claim` (an anchored "The judgment of the Court of Appeals is reversed." row, ok in round 9, keeps ok without the claim) |

Guards: 4×4 diagonal, no cross-kills with earlier properties; count guard `(27, 8, 6, 13, 10, 3, 8, 5, 4, 83)`.
Fixture: `round10/fixtures/tbridge` (ok; each reason; claim ignored on a certDenied row and on a bridged row; a claimed
row without a line; table rules), without claims/table = round-9 verdicts.

## 2. Section 4 as built (tables, loader, runner)

- Every statement of §1.2 (as revised in §1b for D10-7) proved exactly as written; no `sorry`, no new axiom, no
  `native_decide` (the added theorems use `propext`, `Quot.sound`, `Classical.choice` only). Helpers locked as
  additions: `spanText_some`, `keyTie_spec`, `reasonTie_spec`, `spanHas_some`, `remandFail_none`,
  `remandThen_some_admitted`.
- **Cue table** (appended; the JSON text up to its last line, `CueTable.lean` up to `end CaseLaw2.Cert` and
  `reader/cue_table.py` are byte-identical prefixes of the round-9 files): `_note_round10`, `remand_court`,
  `remand_cue`, `remand_months`, `remand_months_abbr`, `remand_quote_max` 600, `remand_docket_span_max` 200,
  `remand_days_max` 1826, `remand_order_cue` ["in light of"] (ref10's Q10-11 name; my first name
  `remand_reason_cue` was renamed before LEAN_READY), `remand_order_span_max` 300, `remand_tie_min` 8.
  `gen_cues.py --skip-ref` (ref/ is ref10's: `tools/caselaw2/ref/cue_table.py` is left stale on purpose; ref10 reads
  cue_table.json).
- **Data.lean**: `RemandRow` (12 fields; node / offsets ASCII digits, else a bad row) from the optional
  `history_remand.tsv` (`Tables.remands`; a `Problems` entry only when the file exists); `certNodes` also asks for
  B's text hash (only when the file has lines).
- **Run.lean**: `remandTable` / `RemandTab.summary` (Q10-9 rules; counters `remand_lines`, `remand_checked_rows`,
  `remand_failed_rows`, `remand_dup_rows`, `remand_bad_rows` after the zone counters, only when the file has a line);
  the history step computes the round-9 verdict (`checkHistory9J`) and then `Cert.remandThen` with the row's
  `Cert.Remand` (B's, the target's and the order's hashes and windows, decisions2 courts / dates, the order node, the
  index's key lengths); the zone counters read the round-9 verdict, every other counter the final one.
- **Scripts** (new): `wsl/r10_lean.sh` (sync + build), `wsl/r10_remand_fixture.sh`, `wsl/r10_repro.sh` (reproduce
  a frozen output from a verified base mirror with a given binary; one run slot; deletes its output when identical),
  `wsl/r10_r9zone_fixture.sh` / `wsl/r10_r9farimplicit_fixture.sh` (copies of the round-9 fixture scripts that write
  nothing into round9/), `wsl/r10_final.sh`, `wsl/r10_peek.sh`, `wsl/r10_stage_size.sh`, `wsl/r10_s6build.sh`
  (builds the tree in a separate WSL copy without syncing the mirror); `wsl/lock_reason.txt` holds the round-10 reason
  (round 9's in `round10/pre/wsl/`).

## 3. Results (§4)

- Runner sha1 `43efb9942340bdb1664c2428631007a94bca66f5` (`~/caselaw2/r10_bin/caselaw2_lean10_s4`).
- Audit: first lock 04:05 (9-column §4: 272 → 280, 8 new); D10-7 relock 04:12 (281: `reasonTie_spec` new,
  `remandBridge_sound` restated — a round-10 statement, before any LEAN_READY); after: 281 / 0 changes / 0 problems.
  Against round 9's lock (`round10/pre/audit/statements.lock`): 0 removed, 0 changed, 9 added.
- Mutants 74 → 79 (M75–M79; properties 75 → 80); the 5×5 round-10 matrix is the diagonal plus (M78, reason-case
  property), stated exactly by the guard; no cross-kills with earlier properties. `#guard`s Examples 441 → 514,
  Mutants 20 → 23.
- Fixture `round10/fixtures/remand` (18 rows; counters lines 17, checked 16, failed 12, dup 1, bad 3; without the
  table = round-9 verdicts and no counter; an empty table = byte-identical to none); round-9 / round-8 / round-7
  fixtures green.
- Regressions a, a2, b, c byte-identical; `round9/out/v9c` and `round8/out/v8e` reproduced byte for byte (every
  table; summary timing lines aside) — log `round10/agents/lean10/r10_final_s4.log`.
- Slip, stated: at 04:22 my §6 patch script, meant for a staging copy, wrote the §6 code into the real Windows tree
  while these gates ran. The gates read only the WSL mirror (synced at their start, 04:17) and the copied binary, so
  they are unaffected; the §4 source is kept in `round10/agents/lean10/s4_snapshot/`.

## 7. Section 6 as built and results

- Every statement of §6.2 proved exactly as written. Helpers locked as additions (they differ from §6.2's expected
  list in name only where noted): `checkByX_none`, `checkBy_cue_eq`, `checkByX_admitted`, `anchoredBy_admitted`
  (general form of the anchored unpacking), `tbridgeQuote_selfText`, `tbridgeQuote_some`, `trialFail_none`,
  `checkHistory8T_claimed`.
- Cue table (appended): `_note_round10_s6`, `trial_court_names`, `intermediate_court_names`, `tbridge_cue`,
  `tbridge_negative`, `tbridge_quote_max` 600, `tbridge_days_max` 1826.
- Data: `HClaimRow.parse` accepts `trialBridge`; `TBridgeRow` from optional `history_tbridge.tsv` (3 fields).
  Run: `HClaimTab.trial` (the id joins the claimed rows like `anchorWide`), `tbridgeTable` / `TBridgeTab.summary`
  (`tbridge_lines`, `tbridge_dup_rows`, `tbridge_bad_rows`, after the remand counters); the history step is
  `Cert.checkHistory9T tb?` then `Cert.remandThen` (`= checkHistory10T`); `tb?` is built for every row with the claim
  (T's hash and windows, its line, dates and courts); the Lean step decides whether the claim counts.
- Audit: 281 → 292 (11 new), locked; against round 9's lock: 0 removed, 0 changed, 20 added (axioms of the added:
  propext, Quot.sound, Classical.choice).
- Mutants 79 → 83 (M80–M83, 4×4 diagonal; count guard `(27, 8, 6, 13, 10, 3, 8, 5, 4, 83)`); `#guard`s Examples
  514 → 548, Mutants 23 → 26.
- Fixture `round10/fixtures/tbridge` (`make_tbridge_fixture.py`, `wsl/r10_tbridge_fixture.sh`): 16 rows: ok
  (reversed; vacated; "set aside" under setAside), trialBridgeD ×2, trialBridgeT ×3 (reverses, no affirm, no line),
  trialBridgeDate ×3 (T after D, beyond 1,826 days, same court), anchorPart first, claim ignored (no anchor,
  certDenied, bridged row), no claim; data_notable (claims, no table): every counted claim fails trialBridgeT;
  data_noclaim: round-9 verdicts, and every output equals the frozen round-9 binary's on the same data.
