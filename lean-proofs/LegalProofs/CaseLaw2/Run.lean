import LegalProofs.CaseLaw2.Core

/-!
# caselaw-lean-2 runner

    caselaw2 <data-dir> <edges-dir> <shard k> <shards N> <out-dir> <nodes> [asOf]
    (or: lake env lean --run LegalProofs/CaseLaw2/Run.lean … ; compiled: caselaw-lean-2/runner, `lake build`)

Reads the SCHEMA files of `<data-dir>` (plus the optional `decisions2_extra.tsv` and `factors.tsv`) and v1's citation
shards `<edges-dir>/edges-NN.tsv` (citing, cited; shard `k` reads files with `NN % N = k`), and writes, for this shard:

* `status-k.tsv`   node, issue, holding, from, to, status, class, firm, witness_row, actor, path
  (one row per interval of constant status, for every node with an admitted event or a holding, `node % N = k`);
  the union status: negative if negative in any line of authority;
* `status_lines-k.tsv` the same columns plus `line` (`orig` or an heir's court id): for a decision with a
  line-limited effect, its status in each pure line (DEVIATIONS 75);
* `horty-k.tsv`    family, court, verdict (consistent|inconsistent), cases, firm: one row per distinct binding base
  (DEVIATIONS 78; empty without `factors.tsv`);
* `findings-k.tsv` finding, citing, cited, issue, detail, firm, path;
* `certs-k.tsv`    table, row id, result (all rules), result (firm rules)   (rows with `id % N = k`); a history row
  with a line in the optional `history_anchor.tsv` is checked by `Cert.checkAnchored` (round 6);
* `splits-k.tsv`   kind (split|conflict), issue, court1, court2, answers1, answers2, holdings1, holdings2, asOf, firm
  (issues `% N = k`; courts as `court[/unit]`);
* `summary-k.tsv`  counters.

Every verdict is computed by the Spec's functions (`force`, `canChangeStatus`, `statusOf`, `resolve`, `Cert.check`)
through the hash-indexed lookups that `Exec/Env.lean` proves equal to the Spec's list scans; each row carries its
justification path (D8) and `firm` = 1 when the S/L-only tables give the same verdict as the tables with U rows (D2).
-/

open CaseLaw2 CaseLaw2.Spec CaseLaw2.Exec CaseLaw2.Data CaseLaw2.Tsv Std

namespace CaseLaw2.Run

def pad2 (j : Nat) : String := if j < 10 then s!"0{j}" else toString j

/-! ## Translating rows -/

/-- 28 U.S.C. § 41: the circuit each state or territory lies in (longest names first, so that "West Virginia" is
found before "Virginia"). Used to give a state system's courts their circuit for E3 `stateFollowsCircuit` rows. -/
def stateCircuits : List (String × Nat) := [
  ("Northern Mariana Islands", 9),
  ("District of Columbia", 12),
  ("Virgin Islands", 3),
  ("North Carolina", 4),
  ("South Carolina", 4),
  ("Massachusetts", 1),
  ("New Hampshire", 1),
  ("West Virginia", 4),
  ("Rhode Island", 1),
  ("Pennsylvania", 3),
  ("North Dakota", 8),
  ("South Dakota", 8),
  ("Puerto Rico", 1),
  ("Connecticut", 2),
  ("Mississippi", 5),
  ("New Jersey", 3),
  ("California", 9),
  ("Washington", 9),
  ("New Mexico", 10),
  ("Louisiana", 5),
  ("Tennessee", 6),
  ("Wisconsin", 7),
  ("Minnesota", 8),
  ("New York", 2),
  ("Delaware", 3),
  ("Maryland", 4),
  ("Virginia", 4),
  ("Kentucky", 6),
  ("Michigan", 6),
  ("Illinois", 7),
  ("Arkansas", 8),
  ("Missouri", 8),
  ("Nebraska", 8),
  ("Colorado", 10),
  ("Oklahoma", 10),
  ("Vermont", 2),
  ("Indiana", 7),
  ("Arizona", 9),
  ("Montana", 9),
  ("Wyoming", 10),
  ("Alabama", 11),
  ("Florida", 11),
  ("Georgia", 11),
  ("Alaska", 9),
  ("Hawaii", 9),
  ("Nevada", 9),
  ("Oregon", 9),
  ("Kansas", 10),
  ("Maine", 1),
  ("Texas", 5),
  ("Idaho", 9),
  ("Ohio", 6),
  ("Iowa", 8),
  ("Guam", 9),
  ("Utah", 10)]

/-- The state named in a court's name, as whole words. -/
def stateIn (name : String) : Option Nat :=
  let clean := " " ++ String.map (fun c => if c.isAlpha then c else ' ') name ++ " "
  (stateCircuits.find? fun (st, _) => (clean.splitOn (" " ++ st ++ " ")).length > 1).map (·.2)

/-- Each state system's circuit: the state most of its courts' names give (as the reference votes). -/
def systemCircuits (rows : Array CourtRow) : HashMap Nat Nat := Id.run do
  let mut votes : HashMap (Nat × Nat) Nat := {}
  for r in rows do
    if r.system != 0 then
      if let some c := stateIn r.name then votes := votes.insert (r.system, c) (votes.getD (r.system, c) 0 + 1)
  let mut best : HashMap Nat (Nat × Nat) := {}
  for ((sys, c), n) in votes do
    match best.get? sys with
    | some (_, m) => if n > m then best := best.insert sys (c, n)
    | none => best := best.insert sys (c, n)
  return best.fold (fun m sys (c, _) => m.insert sys c) {}

def epochOf (circ : HashMap Nat Nat) (r : CourtRow) : Option CourtEpoch := do
  some { court := r.court, dateFrom := r.epochFrom, dateTo := if r.epochTo == 0 then forever else r.epochTo,
         system := r.system, tier := ← Tier.ofString? r.tier,
         lastResortFor := (LastResortFor.ofString? r.lastResortFor).getD .notLast,
         circuit := if r.system != 0 && r.circuit == 0 then circ.getD r.system 0 else r.circuit,
         unit := optNat r.unit, firm := Tag.firmStr r.tag }

/-- `adoption.tsv` force, with H4's `resultOnly` (a commission opinion whose judgment only was adopted): the opinion
carries no adopted reasoning, so it is read as persuasive (DEVIATIONS.md). -/
def forceOrResultOnly (s : String) : Option Force :=
  if s == "resultOnly" then some .persuasive else Force.ofString? s

/-- The state systems whose courts' names say Texas (S-TX-3 promotion is a Texas rule). -/
def texasSystems (rows : Array CourtRow) : List Nat :=
  (rows.toList.filterMap fun r =>
    let clean := " " ++ String.map (fun c => if c.isAlpha then c else ' ') r.name ++ " "
    if r.system != 0 && (clean.splitOn " Texas ").length > 1 then some r.system else none).eraseDups

/-- S-TX-3 (doctrine §4.2 S-TX, F3): a `writRefused` row promotes the target only when
* the target is a Texas intermediate (appellate-tier) decision;
* the notation is "writ ref'd"/"writ refused" (writ era, before 1 Sept 1997) or "pet. ref'd"/"petition refused"
  (petition era, from 1 Sept 1997), never "n.r.e." (no approval of the reasoning);
* the case is civil: a known refusing decision is the civil (or sole) court of last resort's; when it is unknown,
  only a writ-era notation counts (the writ of error was civil only; a petition-era "pet. ref'd" may be a criminal
  PDR refusal, which adds no approval).
The date is the notation's (the row's date; the target's when unknown). -/
def writPromotes (L : Lookups) (tx : List Nat) (quote : String) (date : Date) (x : Decision) (b? : Option Decision) :
    Bool :=
  let q := quote.toLower
  let has (p : String) := (q.splitOn p).length > 1
  -- notations that add no approval: n.r.e., denied, dismissed (w.o.j.), and the criminal PDR (S-TX; sweep seed
  -- 51925: "pet. ref'd (PDR)" promoted an opinion that the reference, rightly, left alone)
  let nre := has "n.r.e" || has "n. r. e" || has "no reversible error" || has "denied" || has "den." ||
    has "dism" || has "w.o.j" || has "woj" || has "pdr" || has "discretionary review"
  let d := if date == 0 then x.date else date
  let wording := if d < 19970901 then has "writ ref" || has "writ refused"
    else has "pet. ref" || has "petition refused" || has "pet. refused"
  let target := (L.epochAt x.court x.date).any fun X => tx.contains X.system && X.tier == .appellate
  -- the writ of error was civil only, so a "writ ref'd" is civil whoever is named; a "pet. ref'd" is civil only when
  -- the refusing decision is known to be the civil court of last resort's (a criminal PDR refusal reads the same)
  let civilCourt := match b? with
    | some b => (L.epochAt b.court b.date).any fun B =>
        tx.contains B.system && B.tier == .last && (B.lastResortFor == .civil || B.lastResortFor == .all)
    | none => d < 19970901
  target && wording && !nre && civilCourt

def envOf (t : Tables) : Env :=
  { epochs := t.courts.toList.filterMap (epochOf (systemCircuits t.courts))
    successions := t.succession.toList.filterMap fun r => do
      some { old := r.old, new := r.new, date := r.date, kind := ← SuccessionKind.ofString? r.kind,
             firm := Tag.firmStr r.tag }
    adoptions := t.adoption.toList.filterMap fun r => do
      some { adopter := r.adopter, source := r.source, upTo := if r.upTo == 0 then forever else r.upTo,
             filter := ← AdoptFilter.ofString? r.filter, force := ← forceOrResultOnly r.force, firm := Tag.firmStr r.tag }
    rules := t.rules.toList.map fun r =>
      { key := r.system, rule := r.rule, value := r.value, dateFrom := r.dateFrom,
        dateTo := if r.dateTo == 0 then forever else r.dateTo, firm := Tag.firmStr r.tag } }

def decode {α} (vals : Array String) (parse : String → Option α) (b : UInt8) : Option α :=
  if b.toNat < vals.size then parse vals[b.toNat]! else none

structure World where
  dec : Decisions
  venue : HashMap Nat Nat
  transfer : HashMap Nat Nat
  /-- H4: commission notations (`commission.tsv`, optional) -/
  commission : HashMap Nat Notation := {}

def World.decision (w : World) (n : Nat) : Option Decision :=
  if w.dec.has n then
    some { id := n, court := w.dec.court[n]!, date := w.dec.date[n]!, unit := optNat w.dec.unit[n]!,
           bench := decode benchValues Bench.ofString? (w.dec.bench.get! n),
           pub := decode publicationValues Publication.ofString? (w.dec.publication.get! n),
           -- H4: an opinion whose judgment only was adopted ("Judgment adopted") carries result-only weight: read
           -- as a memorandum (capped at persuasive) on every court (DEVIATIONS 63)
           form := if w.commission.get? n == some .judgmentAdopted then some .memorandum
             else decode formValues Form.ofString? (w.dec.form.get! n),
           appealVenue := w.venue.get? n, transferFrom := w.transfer.get? n, commission := w.commission.get? n }
  else none

/-- Issue keys interned to `Nat` (0 = anonymous). -/
structure Issues where
  idx : HashMap String Nat := {}
  keys : Array String := #[""]
  dom : Array (Option Domain) := #[none]
  question : Array Bool := #[false]

def Issues.intern (is : Issues) (k : String) : Issues × Nat :=
  match is.idx.get? k with
  | some i => (is, i)
  | none => ({ idx := is.idx.insert k is.keys.size, keys := is.keys.push k, dom := is.dom.push none,
               question := is.question.push false }, is.keys.size)

def parseScope (is : Issues) (s : String) : Issues × Scope :=
  if s == "all" then (is, .all)
  else if s.startsWith "issues:" then
    let ks := ((s.drop 7).toString.splitOn ",").filter (· ≠ "")
    let (is, ns) := ks.foldl (fun (is, acc) k => let (is, i) := is.intern k; (is, acc ++ [i])) (is, [])
    (is, .issues ns)
  else (is, .someIssue)

/-! ## Certificates -/

/-- What every certificate check is given besides its row: the windows by text hash (each with the digest the audit
copy recorded, `window_sha.tsv`), whether that hash file was supplied, and the citation index (`cite_index.tsv`). -/
structure CertCtx where
  wins : HashMap String (List Cert.Window) := {}
  hashRequired : Bool := false
  citeIndex : Option (HashMap String Nat) := none

def certInput (kind : Cert.Kind) (c : Data.Cert) (shas : List String) (cx : CertCtx) (target : Nat)
    (ordered : Bool) (auth : Option Bool) : Cert.Input :=
  { kind, textSha := c.textSha, start := c.start, stop := c.stop, quote := c.quote, evidence := c.evidence,
    part := c.part, shas, windows := cx.wins.getD c.textSha [], ordered, authority := auth,
    hashRequired := cx.hashRequired, target, citeIndex := cx.citeIndex }

/-- The citation index keyed by `Cert.compact` citation; a key that two nodes share (after compacting) is left out:
it is ambiguous and resolves to nothing. -/
def buildCiteIndex (rows : Array (String × Nat)) : HashMap String Nat := Id.run do
  let mut m : HashMap String Nat := {}
  let mut amb : HashMap String Unit := {}
  for (c, n) in rows do
    let k := Cert.compact c
    match m.get? k with
    | some n' => if n' != n then amb := amb.insert k ()
    | none => m := m.insert k n
  return amb.fold (fun m k _ => m.erase k) m

def shaOf (w : World) (n : Nat) : List String := (w.dec.sha.get? n).toList

/-- Round 6 (`round6/history/DESIGN6.md` §4): the anchor lines of `history_anchor.tsv`, by history row id. -/
structure Anchors where
  /-- the anchor of a history row id (the first line for the id) -/
  byId : HashMap String Cert.Anchor := {}
  /-- lines whose id is no history row (ignored) -/
  unknown : Nat := 0
  /-- later lines for an id that already has one (ignored) -/
  duplicates : Nat := 0
  /-- history rows that have an anchor -/
  anchored : Nat := 0
  /-- lines in the file, well formed or not: the anchor counters are written only when there is one -/
  lines : Nat := 0

/-- The first line for a history id wins; a later line for the same id and a line whose id is no history row are
ignored and counted. With no line the table is empty (and the history ids are not even collected). -/
def anchorTable (t : Tables) : Anchors := Id.run do
  let lines := (t.problems.filter (·.file.endsWith "history_anchor.tsv")).foldl (fun n p => n + p.rows) 0
  if t.anchors.isEmpty then return { lines }
  let ids : HashMap String Unit := t.history.foldl (fun m r => m.insert r.id ()) {}
  let mut tab : Anchors := { lines }
  for a in t.anchors do
    if !ids.contains a.id then tab := { tab with unknown := tab.unknown + 1 }
    else if tab.byId.contains a.id then tab := { tab with duplicates := tab.duplicates + 1 }
    else tab := { tab with byId := tab.byId.insert a.id { start := a.start, stop := a.stop, quote := a.quote, part := a.part } }
  let byId := tab.byId
  return { tab with anchored := t.history.foldl (fun n r => if byId.contains r.id then n + 1 else n) 0 }

/-- The anchor counters of `summary.tsv`: none unless `history_anchor.tsv` has a line. `ignored`: anchored rows
that carry a bridge line (round 8; their anchor is not used, so they are neither admitted nor rejected here). -/
def Anchors.summary (a : Anchors) (admitted : Nat) (ignored : Nat := 0) : List String :=
  if a.lines == 0 then []
  else [s!"anchor_rows\t{a.byId.size}", s!"anchor_unknown_ids\t{a.unknown}", s!"anchor_duplicates\t{a.duplicates}",
        s!"anchored_admitted\t{admitted}", s!"anchored_rejected\t{a.anchored - admitted - ignored}"]

/-- Round 7 (`round7/DESIGN7.md` §1–2, `LEAN7.md`): the joined lines of `joined.tsv`, by treatments row id. -/
structure JoinedTab where
  /-- the joined lines of a treatments row (the first two valid lines for the id, in file order) -/
  byId : HashMap String (List Cert.Joined) := {}
  /-- lines whose id is no row of the named table (ignored) -/
  unknown : Nat := 0
  /-- lines for an id that already has two (ignored) -/
  extra : Nat := 0
  /-- `history` lines (reserved this round: ignored) -/
  historyIgnored : Nat := 0
  /-- lines on a witness row (`treatment_witness.tsv`; ignored, LEAN7 L7-1) -/
  witnessIgnored : Nat := 0
  /-- lines in the file, well formed or not: the counters are written only when there is one -/
  lines : Nat := 0

/-- Read the joined lines: a line whose id is no row of its table, a `history` line, a line on a witness row and a
third line for an id are ignored and counted. With no line the table is empty. -/
def joinedTable (t : Tables) (witIds : HashMap String Unit) : JoinedTab := Id.run do
  let lines := (t.problems.filter (·.file.endsWith "joined.tsv")).foldl (fun n p => n + p.rows) 0
  if t.joined.isEmpty then return { lines }
  let tids : HashMap String Unit := t.treatments.foldl (fun m r => m.insert r.id ()) {}
  let hids : HashMap String Unit := t.history.foldl (fun m r => m.insert r.id ()) {}
  let mut tab : JoinedTab := { lines }
  for j in t.joined do
    if j.table == "history" then
      if hids.contains j.id then tab := { tab with historyIgnored := tab.historyIgnored + 1 }
      else tab := { tab with unknown := tab.unknown + 1 }
    else if !tids.contains j.id then tab := { tab with unknown := tab.unknown + 1 }
    else if witIds.contains j.id then tab := { tab with witnessIgnored := tab.witnessIgnored + 1 }
    else
      let cur := tab.byId.getD j.id []
      if cur.length ≥ 2 then tab := { tab with extra := tab.extra + 1 }
      else
        let jl : Cert.Joined := { rel := if j.rel == "doctrineTie" then .doctrineTie else .antecedent,
                                  start := j.start, stop := j.stop, quote := j.quote, part := j.part, label := j.label }
        tab := { tab with byId := tab.byId.insert j.id (cur ++ [jl]) }
  return tab

/-- The joined counters of `summary.tsv`: none unless `joined.tsv` has a line. -/
def JoinedTab.summary (j : JoinedTab) (admitted : Nat) : List String :=
  if j.lines == 0 then []
  else [s!"joined_rows\t{j.byId.size}", s!"joined_lines\t{j.byId.fold (fun n _ l => n + l.length) 0}",
        s!"joined_unknown_ids\t{j.unknown}", s!"joined_extra\t{j.extra}",
        s!"joined_history_ignored\t{j.historyIgnored}", s!"joined_witness_ignored\t{j.witnessIgnored}",
        s!"joined_admitted\t{admitted}", s!"joined_rejected\t{j.byId.size - admitted}"]

/-- Round 7 (§3): the claims of `history_claim.tsv`, by history row id: (orderHead, setAside). -/
structure HClaimTab where
  byId : HashMap String (Bool × Bool) := {}
  /-- round 8 (`round8/DESIGN8.md` §5): the rows with an `anchorWide` claim -/
  wide : HashMap String Unit := {}
  /-- round 8 (§6): the rows with an `oldCircuit` claim -/
  old : HashMap String Unit := {}
  /-- round 10 (`round10/DESIGN10.md` §6): the rows with a `trialBridge` claim -/
  trial : HashMap String Unit := {}
  /-- round 11 (`round11/DESIGN11.md` §5.1): the rows with an `anchorTribunal` claim -/
  tribunal : HashMap String Unit := {}
  /-- lines whose id is no history row (ignored) -/
  unknown : Nat := 0
  /-- a repeated (id, claim) line (ignored) -/
  duplicates : Nat := 0
  lines : Nat := 0

def hclaimTable (t : Tables) : HClaimTab := Id.run do
  let lines := (t.problems.filter (·.file.endsWith "history_claim.tsv")).foldl (fun n p => n + p.rows) 0
  if t.hclaims.isEmpty then return { lines }
  let hids : HashMap String Unit := t.history.foldl (fun m r => m.insert r.id ()) {}
  let mut tab : HClaimTab := { lines }
  for c in t.hclaims do
    if !hids.contains c.id then tab := { tab with unknown := tab.unknown + 1 }
    else if c.claim == "anchorWide" then
      if tab.wide.contains c.id then tab := { tab with duplicates := tab.duplicates + 1 }
      else tab := { tab with byId := tab.byId.insert c.id (tab.byId.getD c.id (false, false)),
                             wide := tab.wide.insert c.id () }
    else if c.claim == "trialBridge" then
      if tab.trial.contains c.id then tab := { tab with duplicates := tab.duplicates + 1 }
      else tab := { tab with byId := tab.byId.insert c.id (tab.byId.getD c.id (false, false)),
                             trial := tab.trial.insert c.id () }
    else if c.claim == "anchorTribunal" then
      if tab.tribunal.contains c.id then tab := { tab with duplicates := tab.duplicates + 1 }
      else tab := { tab with byId := tab.byId.insert c.id (tab.byId.getD c.id (false, false)),
                             tribunal := tab.tribunal.insert c.id () }
    else if c.claim == "oldCircuit" then
      if tab.old.contains c.id then tab := { tab with duplicates := tab.duplicates + 1 }
      else tab := { tab with byId := tab.byId.insert c.id (tab.byId.getD c.id (false, false)),
                             old := tab.old.insert c.id () }
    else
      let (oh, sa) := tab.byId.getD c.id (false, false)
      if (if c.claim == "orderHead" then oh else sa) then tab := { tab with duplicates := tab.duplicates + 1 }
      else tab := { tab with byId := tab.byId.insert c.id (if c.claim == "orderHead" then (true, sa) else (oh, true)) }
  return tab

/-- The history-claim counters of `summary.tsv`: none unless `history_claim.tsv` has a line; the `anchorWide`
counters (round 8) only when a row carries that claim; likewise the `anchorTribunal` counters (round 11, after the
`oldCircuit` ones). -/
def HClaimTab.summary (h : HClaimTab) (admitted : Nat) (wideUnused : Nat := 0) (oldUsed : Nat := 0)
    (tribunalUnused : Nat := 0) : List String :=
  if h.lines == 0 then []
  else [s!"hclaim_rows\t{h.byId.size}", s!"hclaim_unknown_ids\t{h.unknown}", s!"hclaim_duplicates\t{h.duplicates}",
        s!"hclaim_admitted\t{admitted}", s!"hclaim_rejected\t{h.byId.size - admitted}"] ++
    (if h.wide.isEmpty then []
     else [s!"hclaim_anchorwide\t{h.wide.size}", s!"hclaim_anchorwide_unused\t{wideUnused}"]) ++
    (if h.old.isEmpty then []
     else [s!"hclaim_oldcircuit\t{h.old.size}", s!"hclaim_oldcircuit_used\t{oldUsed}"]) ++
    (if h.tribunal.isEmpty then []
     else [s!"hclaim_anchortribunal\t{h.tribunal.size}", s!"hclaim_anchortribunal_unused\t{tribunalUnused}"])

/-- Round 8 (`round8/DESIGN8.md` §4): the bridge lines of `history_bridge.tsv`, by history row id. -/
structure Bridges where
  /-- the bridge line of a history row id (the first line for the id) -/
  byId : HashMap String BridgeRow := {}
  /-- lines whose id is no history row (ignored) -/
  unknown : Nat := 0
  /-- later lines for an id that already has one (ignored) -/
  duplicates : Nat := 0
  /-- lines in the file, well formed or not: the counters are written only when there is one -/
  lines : Nat := 0

/-- The first line for a history id wins; a later line for the id and a line whose id is no history row are ignored
and counted. With no line the table is empty. -/
def bridgeTable (t : Tables) : Bridges := Id.run do
  let lines := (t.problems.filter (·.file.endsWith "history_bridge.tsv")).foldl (fun n p => n + p.rows) 0
  if t.bridges.isEmpty then return { lines }
  let ids : HashMap String Unit := t.history.foldl (fun m r => m.insert r.id ()) {}
  let mut tab : Bridges := { lines }
  for b in t.bridges do
    if !ids.contains b.id then tab := { tab with unknown := tab.unknown + 1 }
    else if tab.byId.contains b.id then tab := { tab with duplicates := tab.duplicates + 1 }
    else tab := { tab with byId := tab.byId.insert b.id b }
  return tab

/-- The bridge counters of `summary.tsv`: none unless `history_bridge.tsv` has a line. -/
def Bridges.summary (b : Bridges) (admitted anchorIgnored : Nat) : List String :=
  if b.lines == 0 then []
  else [s!"bridge_rows\t{b.byId.size}", s!"bridge_unknown_ids\t{b.unknown}", s!"bridge_duplicates\t{b.duplicates}",
        s!"bridge_anchor_ignored\t{anchorIgnored}", s!"bridge_admitted\t{admitted}",
        s!"bridge_rejected\t{b.byId.size - admitted}"]

/-- The distinct key lengths of the citation index, longest first (LEAN8 L8-3). -/
def keyLengths (m : HashMap String Nat) : List Nat :=
  let ls : HashMap Nat Unit := m.fold (fun s k _ => s.insert k.length ()) {}
  (ls.fold (fun l n _ => n :: l) []).mergeSort (fun a b => b ≤ a)

/-- Round 9 (`round9/DESIGN9.md` §4, D9-4): the part zones of `part_zone.tsv`, by node. A node keeps all its zones,
or none when one of its lines is malformed or two overlap (`Cert.nodeZones`). -/
structure ZoneTab where
  /-- the zones each node keeps (only nodes that keep some) -/
  byNode : HashMap Nat (List Cert.Zone) := {}
  /-- zone lines of the kept nodes -/
  kept : Nat := 0
  /-- nodes whose zones were dropped (a malformed line, or two overlapping zones) -/
  badNodes : Nat := 0
  /-- lines that did not parse (also `bad_rows part_zone.tsv n`) -/
  badRows : Nat := 0
  /-- lines in the file, well formed or not: the counters are written only when there is one -/
  lines : Nat := 0

def zoneTable (t : Tables) : ZoneTab := Id.run do
  let ps := t.problems.filter (·.file.endsWith "part_zone.tsv")
  let lines := ps.foldl (fun n p => n + p.rows) 0
  let badRows := ps.foldl (fun n p => n + p.bad) 0
  if t.zones.isEmpty then return { lines, badRows }
  let mut raw : HashMap Nat (Array Cert.Zone) := {}
  for z in t.zones do
    raw := raw.insert z.node ((raw.getD z.node #[]).push { start := z.start, stop := z.stop, part := z.part })
  let mut tab : ZoneTab := { lines, badRows }
  for (n, zs) in raw do
    let kept := Cert.nodeZones zs.toList
    if kept.isEmpty then tab := { tab with badNodes := tab.badNodes + 1 }
    else tab := { tab with byNode := tab.byNode.insert n kept, kept := tab.kept + kept.length }
  return tab

/-- The zone counters of `summary.tsv` (D9-4 names): none unless `part_zone.tsv` has a line. -/
def ZoneTab.summary (z : ZoneTab) (checked failed missing : Nat) : List String :=
  if z.lines == 0 then []
  else [s!"zone_nodes	{z.byNode.size}", s!"zone_lines	{z.kept}", s!"zone_bad_nodes	{z.badNodes}",
        s!"zone_bad_rows	{z.badRows}", s!"zone_checked_rows	{checked}", s!"zone_failed_rows	{failed}",
        s!"zone_missing_rows	{missing}"]

/-- Round 10 (`round10/DESIGN10.md` §4, D10-5, D10-6 / Q10-9): the remand lines of `history_remand.tsv`, by history
row id. A bad line takes no id (it is counted by the loader); a good line whose id is no history row is ignored and
counted nowhere; a later good line for a kept id is a duplicate. -/
structure RemandTab where
  /-- the remand line of a history row id (the first good line for the id) -/
  byId : HashMap String RemandRow := {}
  /-- later good lines for a kept id (ignored) -/
  duplicates : Nat := 0
  /-- lines that did not parse (also `bad_rows history_remand.tsv n`) -/
  badRows : Nat := 0
  /-- lines in the file, good or bad: the counters are written only when there is one -/
  lines : Nat := 0

def remandTable (t : Tables) : RemandTab := Id.run do
  let ps := t.problems.filter (·.file.endsWith "history_remand.tsv")
  let lines := ps.foldl (fun n p => n + p.rows) 0
  let badRows := ps.foldl (fun n p => n + p.bad) 0
  if t.remands.isEmpty then return { lines, badRows }
  let ids : HashMap String Unit := t.history.foldl (fun m r => m.insert r.id ()) {}
  let mut tab : RemandTab := { lines, badRows }
  for r in t.remands do
    if !ids.contains r.id then continue
    else if tab.byId.contains r.id then tab := { tab with duplicates := tab.duplicates + 1 }
    else tab := { tab with byId := tab.byId.insert r.id r }
  return tab

/-- Round 10 §6 (D10-8, D10-9 / Q10-17): the T-quote lines of `history_tbridge.tsv`, by history row id (bad lines
take no id; unknown ids are ignored, not counted; a later line for a kept id is a duplicate). -/
structure TBridgeTab where
  byId : HashMap String TBridgeRow := {}
  duplicates : Nat := 0
  badRows : Nat := 0
  lines : Nat := 0

def tbridgeTable (t : Tables) : TBridgeTab := Id.run do
  let ps := t.problems.filter (·.file.endsWith "history_tbridge.tsv")
  let lines := ps.foldl (fun n p => n + p.rows) 0
  let badRows := ps.foldl (fun n p => n + p.bad) 0
  if t.tbridges.isEmpty then return { lines, badRows }
  let ids : HashMap String Unit := t.history.foldl (fun m r => m.insert r.id ()) {}
  let mut tab : TBridgeTab := { lines, badRows }
  for r in t.tbridges do
    if !ids.contains r.id then continue
    else if tab.byId.contains r.id then tab := { tab with duplicates := tab.duplicates + 1 }
    else tab := { tab with byId := tab.byId.insert r.id r }
  return tab

/-- Round 11 §5.2 (`round11/DESIGN11.md` §5.2, D11-5; LEAN11 L11-10, L11-15): the identity lines of
`history_identity.tsv`, by history row id (bad lines take no id; unknown ids are ignored, in no counter; a later good
line for a kept id is a duplicate). -/
structure IdentityTab where
  byId : HashMap String IdentityRow := {}
  duplicates : Nat := 0
  badRows : Nat := 0
  lines : Nat := 0

def identityTable (t : Tables) : IdentityTab := Id.run do
  let ps := t.problems.filter (·.file.endsWith "history_identity.tsv")
  let lines := ps.foldl (fun n p => n + p.rows) 0
  let badRows := ps.foldl (fun n p => n + p.bad) 0
  if t.identities.isEmpty then return { lines, badRows }
  let ids : HashMap String Unit := t.history.foldl (fun m r => m.insert r.id ()) {}
  let mut tab : IdentityTab := { lines, badRows }
  for r in t.identities do
    if !ids.contains r.id then continue
    else if tab.byId.contains r.id then tab := { tab with duplicates := tab.duplicates + 1 }
    else tab := { tab with byId := tab.byId.insert r.id r }
  return tab

/-- The identity counters of `summary.tsv` (DESIGN11 §5.2 names): none unless `history_identity.tsv` has a line. -/
def IdentityTab.summary (t : IdentityTab) (checked failed : Nat) : List String :=
  if t.lines == 0 then []
  else [s!"identity_lines\t{t.byId.size}", s!"identity_checked_rows\t{checked}", s!"identity_failed_rows\t{failed}",
        s!"identity_dup_rows\t{t.duplicates}", s!"identity_bad_rows\t{t.badRows}"]

/-- The T-quote counters of `summary.tsv` (Q10-17): none unless `history_tbridge.tsv` has a line. -/
def TBridgeTab.summary (t : TBridgeTab) : List String :=
  if t.lines == 0 then []
  else [s!"tbridge_lines	{t.byId.size}", s!"tbridge_dup_rows	{t.duplicates}", s!"tbridge_bad_rows	{t.badRows}"]

/-- The remand counters of `summary.tsv` (DESIGN10 §4 names): none unless `history_remand.tsv` has a line. -/
def RemandTab.summary (t : RemandTab) (checked failed : Nat) : List String :=
  if t.lines == 0 then []
  else [s!"remand_lines	{t.byId.size}", s!"remand_checked_rows	{checked}", s!"remand_failed_rows	{failed}",
        s!"remand_dup_rows	{t.duplicates}", s!"remand_bad_rows	{t.badRows}"]

/-- Round 7 (§2.4): the labels the table's doctrine rows tie to two targets, decided on the rows whose text check
passed: `Cert.ambiguousLabel` on each label's bucket (the rows carrying it, in table order), which is the table's
answer (`Cert.ambiguousLabel_filter`). -/
def doctrineAmbiguousLabels (rows : Array Cert.DoctrineRow) : HashMap String Unit := Id.run do
  let mut buckets : HashMap String (Array Cert.DoctrineRow) := {}
  for r in rows do
    for l in r.labels.eraseDups do
      buckets := buckets.insert l ((buckets.getD l #[]).push r)
  let mut amb : HashMap String Unit := {}
  for (l, b) in buckets do
    if Cert.ambiguousLabel b.toList l then amb := amb.insert l ()
  return amb

/-- Round 4 (DEVIATIONS 84): the words a `panelDepartsWithoutEnBanc` finding needs in the certified quote: the
panel's own overruling, disapproval or receding. -/
def panelOwnWords : List String :=
  ["overrul", "disapprov", "recede from", "receded from", "recedes from", "receding from"]

/-- Power of `b` over `x` when the issue's domain is unknown: decided on every domain the issue could have (each
court's home domain, federal law, patent law when the Federal Circuit is involved); `none` when they disagree or an
epoch is unknown (D5). -/
def powerAnyDomain (L : Lookups) (b x : Decision) : Option Bool :=
  match L.epochAt b.court b.date, L.epochAt x.court x.date with
  | some B, some X =>
    let ds := ([X.home, B.home, Domain.federalGeneral] ++
      (if B.circuit == 13 || X.circuit == 13 then [Domain.federalPatent] else [])).eraseDups
    let rs := ds.map fun d => (canChangeStatus L b x (some d)).map (·.1)
    if rs.all (· == some true) then some true else if rs.all (· == some false) then some false else none
  | _, _ => none

/-- The domains an unextracted issue of `x` could have, asked from `c`'s court: each court's home domain, federal
law, and patent law when the Federal Circuit is involved. -/
def domainsOf (L : Lookups) (x c : Decision) : List Domain :=
  match L.epochAt x.court x.date, L.epochAt c.court c.date with
  | some X, some C => ([X.home, C.home, Domain.federalGeneral] ++
      (if C.circuit == 13 || X.circuit == 13 then [Domain.federalPatent] else [])).eraseDups
  | _, _ => []

/-- On a named holding every unknown is one class (`partialScope` is a class of its own only on ⊤). -/
def unknownAsOne : Status → Status
  | .unknown _ => .unknown .enBancRuleUnknown
  | s => s

/-- D2 `firm`: the S/L-only tables give the same verdict (D5 class, and the negative kind); two unknowns agree
whatever their reasons. -/
def sameVerdict : Status → Status → Bool
  | .unknown a, .unknown b => (a == .partialScope) == (b == .partialScope)
  | a, b => a == b

/-! ## Output helpers -/

/-- The `line` column of `status_lines.tsv` (DEVIATIONS 75). -/
def lineName : Line → String
  | .orig => "orig"
  | .heir a => toString a

def boolS (b : Bool) : String := if b then "1" else "0"
def optS {α} [ToString α] : Option α → String
  | some a => toString a
  | none => "-"

-- `main` is past Lean's default compile budget since round 7 (LEAN6 §4 noted it was close): the budget is raised
-- for this one definition; no proof is affected
set_option maxHeartbeats 1000000 in
def main (args : List String) : IO UInt32 := do
  let (dataDir, edgesDir, k, nShards, outDir, nodes, asOf) ← match args with
    | [a, b, c, d, e, f] => pure (a, b, c.toNat!, d.toNat!, e, f.toNat!, 20261112)
    | [a, b, c, d, e, f, g] => pure (a, b, c.toNat!, d.toNat!, e, f.toNat!, g.toNat!)
    | _ => do
      IO.eprintln "usage: caselaw2 <data-dir> <edges-dir> <shard k> <shards N> <out-dir> <nodes> [asOf yyyymmdd]"
      return 2
  let data := System.FilePath.mk dataDir
  let out := System.FilePath.mk outDir
  IO.FS.createDirAll out
  let t0 ← IO.monoMsNow
  let tables ← loadTables data
  let want := tables.certNodes
  let (decs, pd) ← loadDecisions (data / "decisions2.tsv") nodes (fun n => want.contains n)
  let (extra, pe) ← loadRows (data / "decisions2_extra.tsv") 3 fun f => do
    some (← nat? f[0]!, nat? f[1]!, nat? f[2]!)
  let mut venue : HashMap Nat Nat := {}
  let mut transfer : HashMap Nat Nat := {}
  for (n, v, tf) in extra do
    if let some v := v then if v != 0 then venue := venue.insert n v
    if let some tf := tf then if tf != 0 then transfer := transfer.insert n tf
  -- FACTORS_NEEDS 1: optional family case map (holding_id, node, family, issue key, outcome yes|no, date, factor count, reason ids, in_factors, reader, family: 11 columns)
  let (famRows, pfc) ← loadRows (data / "factor_cases.tsv") 11 fun f => do
    let out ← (match f[4]! with | "yes" => some true | "no" => some false | _ => none)
    some (f[0]!, f[3]!, out)
  let (factorRows, pf) ← loadRows (data / "factors.tsv") 4 fun f => do
    some (f[0]!, ← nat? f[1]!, f[2]!, (natD f[3]!) == 1)
  -- H4: commission.tsv (node, court_id, notation, evidence), optional
  let (commRows, pc) ← loadRows (data / "commission.tsv") 4 fun f => do
    some (← nat? f[0]!, ← Notation.ofString? f[2]!)
  let commission : HashMap Nat Notation := commRows.foldl (fun m (n, v) => m.insert n v) {}
  let w : World := { dec := decs, venue, transfer, commission }
  let decF := w.decision
  -- environments: all rows, and S/L rows only
  let envAll := envOf tables
  let tx := texasSystems tables.courts
  let envFirm := envAll.firm
  let LA := (ExecEnv.build envAll).lookups
  let LF := (ExecEnv.build envFirm).lookups
  -- issues
  let mut is : Issues := {}
  for r in tables.issues do
    let (is', i) := is.intern r.key
    is := { is' with dom := is'.dom.set! i (Domain.ofString? r.domain),
                     question := is'.question.set! i (r.question != "-" && r.question != "") }
  -- certificate windows
  -- window hashes recorded by the audit copy (`window_sha.tsv`: text_sha, start0, end0, sha1, src; optional): when
  -- supplied, the checker recomputes every window's SHA-1 and uses only windows that match (TRUST.md)
  let hashFile := data / "window_sha.tsv"
  let hashRequired ← hashFile.pathExists
  let (shaRows, pw) ← loadRows hashFile 5 fun f => do some ((f[0]!, ← nat? f[1]!, ← nat? f[2]!), f[3]!)
  let winSha : HashMap (String × Nat × Nat) String := shaRows.foldl (fun m (k, h) => m.insert k h) {}
  let wins : HashMap String (List Cert.Window) := tables.certText.foldl (fun m r =>
    m.insert r.textSha ({ start0 := r.start0, stop0 := r.stop0, text := r.window,
                          hash := winSha.get? (r.textSha, r.start0, r.stop0) } :: m.getD r.textSha [])) {}
  -- the citation index (`cite_index.tsv`: normalised citation, node; optional): `cite:` evidence must resolve to the
  -- row's target through it
  let idxFile := data / "cite_index.tsv"
  let hasIdx ← idxFile.pathExists
  let (idxRows, pi) ← loadRows idxFile 2 fun f => do some (f[0]!, ← nat? f[1]!)
  let cx : CertCtx := { wins, hashRequired, citeIndex := if hasIdx then some (buildCiteIndex idxRows) else none }
  -- holdings: admitted only when the sentence stating them passes its certificate (hash, quote at offset, a
  -- majority/plurality/per curiam role); a rejected holding is not used anywhere (DESIGN D1)
  let holdingCert (r : HoldingRow) : String :=
    let c := certInput (.treat .followed) r.cert (shaOf w r.node) cx r.node true (some true)
    if !Cert.shaOk c then "shaUnknown"
    else if c.windows.any (Cert.wellFormed c) && !(c.windows.any (Cert.usable c)) then "windowHash"
    else if !Cert.quoteOk c then "quoteMismatch"
    -- the certificate's own part (FB-L4): the sentence must be from the majority, a plurality or per curiam
    else if !Cert.partOk c then "partNotMajority"
    else if (Role.ofString? r.role).isNone then "badRole" else "ok"
  let marks : HashMap (Nat × String) Unit := tables.marks.foldl (fun m r => m.insert (r.node, r.issue) ()) {}
  let marksNodes : HashMap Nat Unit := tables.marks.foldl (fun m r => m.insert r.node ()) {}
  let mut holdingsOf : HashMap Nat (Array Holding) := {}
  let mut holdingKey : Array String := #[""]
  for r in tables.holdings do
    if holdingCert r != "ok" then continue
    let (is', i) := is.intern r.issue
    is := is'
    let h : Holding := { id := holdingKey.size, node := r.node, issue := i, domain := is.dom[i]!,
                         role := Role.ofString? r.role, answer := Answer.ofString? r.answer,
                         marks := marks.contains (r.node, r.issue) }
    holdingKey := holdingKey.push r.id
    holdingsOf := holdingsOf.insert r.node ((holdingsOf.getD r.node #[]).push h)
  -- history: admit through certificates
  let mut histA : Array HEvent := #[]
  let mut histF : Array HEvent := #[]
  let mut certLines : Array String := #[]
  let mut nAdm := 0
  let mut nRej := 0
  -- row ids are the reader's strings; events carry the 1-based row index (`histIds`/`treatIds`/`superIds` map back)
  let histIds : Array String := #["-"] ++ tables.history.map (·.id)
  let treatIds : Array String := #["-"] ++ tables.treatments.map (·.id)
  let superIds : Array String := #["-"] ++ tables.supersessions.map (·.id)
  -- round 6 (round6/history/DESIGN6.md §4): anchor lines (`history_anchor.tsv`, optional; `anchorTable`). With no
  -- line the table is empty and every row below is checked by `Cert.check` (`Cert.checkHistory_no_anchor`)
  let anchors := anchorTable tables
  -- round 7 (round7/DESIGN7.md §3): history claims (`history_claim.tsv`, optional; `hclaimTable`). A row without a
  -- claim gets `Cert.checkHistory`'s verdict (`Cert.no_joined_no_change`)
  let hct := hclaimTable tables
  -- round 8 (round8/DESIGN8.md §4): bridge lines (`history_bridge.tsv`, optional; `bridgeTable`). A row without one
  -- and without an `anchorWide` claim gets round 7's verdict (`Cert.no_bridge_no_change`)
  let bridges := bridgeTable tables
  let lens : List Nat := if bridges.byId.isEmpty then [] else match cx.citeIndex with
    | some m => keyLengths m
    | none => []
  let mut nAncAdm := 0
  let mut nHcAdm := 0
  let mut nBrAdm := 0
  let mut nBrAncIgn := 0
  let mut nWideUnused := 0
  let mut nOldUsed := 0
  -- round 11 (DESIGN11 §5.1): rows with an `anchorTribunal` claim and no anchor line, or with a bridge line
  let mut nTribUnused := 0
  -- round 9 (DESIGN9 §4, D9-4): part zones (`part_zone.tsv`, optional; `zoneTable`). With no zone every wrapper below
  -- is the identity (`Cert.no_zone_no_change`)
  let zt := zoneTable tables
  let zonesOf (n : Nat) : List Cert.Zone := zt.byNode.getD n []
  let mut nZChecked := 0
  let mut nZFailed := 0
  let mut nZMissing := 0
  -- round 10 (DESIGN10 §4, D10-5, D10-6): remand lines (`history_remand.tsv`, optional; `remandTable`). A row without
  -- one gets the round-9 verdict (`Cert.no_remand_line_no_change`)
  let rmt := remandTable tables
  let lensR : List Nat := if rmt.byId.isEmpty then [] else match cx.citeIndex with
    | some m => keyLengths m
    | none => []
  let mut nRChecked := 0
  -- round 10 §6 (D10-8): the trial-judgment bridge (`trialBridge` claim; `history_tbridge.tsv`, optional). A row
  -- without the claim gets the round-9 step (`Cert.trialBridge_no_claim`)
  let tbt := tbridgeTable tables
  let mut nRFailed := 0
  -- round 11 §5.2 (D11-5): identity lines (`history_identity.tsv`, optional; `identityTable`). A row without one gets
  -- the round-11 §5.1 verdict (`Cert.no_identity_line_no_change`)
  let idt := identityTable tables
  let mut nIChecked := 0
  let mut nIFailed := 0
  let mut ri := 0
  for r in tables.history do
    ri := ri + 1
    let (is', sc) := parseScope is r.scope
    is := is'
    match HKind.ofString? r.kind, decF r.target with
    | some kind, some x =>
      let bdec? := if r.by_ ≥ 0 then decF r.by_.toNat else none
      let shas := shaOf w r.target ++ (if r.by_ ≥ 0 then shaOf w r.by_.toNat else [])
      let ordered := match bdec? with | some b => decide (x.date ≤ b.date) | none => true
      let selfText := (shaOf w r.target).contains r.cert.textSha
      -- round 6: a row with an anchor line is checked by `Cert.checkAnchored`, any other row by `Cert.check`
      let anc? := anchors.byId.get? r.id
      -- round 7: the row's claims, with the acting decision's court (the Supreme Court?) and date (decisions2)
      let hc? := hct.byId.get? r.id
      let wide := hct.wide.contains r.id
      -- round 11 (DESIGN11 §5.1): the `anchorTribunal` claim (without it the step is round 10's,
      -- `Cert.anchorTribunal_no_claim`)
      let trib := hct.tribunal.contains r.id
      let hcl (L : Lookups) : Cert.HClaims := match hc? with
        | some (oh, sa) => { orderHead := oh, setAside := sa,
                             scotus := bdec?.any (fun b => (L.epochAt b.court b.date).any (·.scotus)),
                             date := (bdec?.map (·.date)).getD 0, anchorWide := wide, anchorTribunal := trib }
        | none => {}
      -- round 8: the row's bridge line, with W's text (its hash and windows) and the dates of W and O (decisions2)
      let bridge? : Option Cert.Bridge := (bridges.byId.get? r.id).map fun bl =>
        let ws := (shaOf w bl.w).headD ""
        { w := bl.w, wSha := ws, windows := if ws.isEmpty then [] else cx.wins.getD ws [], start := bl.start,
          stop := bl.stop, quote := bl.quote, wDate := ((decF bl.w).map (·.date)).getD 0,
          oDate := (bdec?.map (·.date)).getD 0, actor := (bdec?.map (·.id)).getD 0, lens }
      -- round 8 (§6): the authority under an `oldCircuit` claim (`Exec.histPower8`; without it `histPower`,
      -- `Exec.oldCircuit_no_claim`)
      let oc := hct.old.contains r.id
      -- round 9: the zones of the text owner (the target for a row quoting its own text, else the acting node;
      -- D9-4 (1)); the zone test follows the round-8 verdict (`Cert.checkHistory9`)
      let zs : List Cert.Zone := if selfText then zonesOf r.target else if r.by_ ≥ 0 then zonesOf r.by_.toNat else []
      let inp (L : Lookups) : Cert.Input := { certInput (.hist kind) r.cert shas cx r.target ordered
        (bdec?.bind fun b => histPower8 L b x oc) with selfText }
      -- round 10: the row's remand line, with B's, the target's and the order's texts (hashes and windows), the courts
      -- of B and the target and the dates of the order, B and the target (decisions2)
      let remand? : Option Cert.Remand := (rmt.byId.get? r.id).map fun rl =>
        let bs := (shaOf w rl.b).headD ""
        let ts := (shaOf w r.target).headD ""
        let bd? := decF rl.b
        let os := if r.by_ ≥ 0 then (shaOf w r.by_.toNat).headD "" else ""
        { b := rl.b, bSha := bs, bWindows := if bs.isEmpty then [] else cx.wins.getD bs [], tSha := ts,
          tWindows := if ts.isEmpty then [] else cx.wins.getD ts [], start := rl.start, stop := rl.stop,
          docket := rl.docket, bdStart := rl.bdStart, bdStop := rl.bdStop, tStart := rl.tStart, tStop := rl.tStop,
          bCourt := bd?.map (·.court), tCourt := some x.court, oDate := (bdec?.map (·.date)).getD 0,
          bDate := (bd?.map (·.date)).getD 0, tDate := x.date, order := bdec?.map (·.id), lens := lensR,
          tie := rl.tie, oSha := os, oWindows := if os.isEmpty then [] else cx.wins.getD os [], oStart := rl.oStart,
          oStop := rl.oStop }
      -- round 10 §6: a claimed row's trial-bridge facts (T's text and line, the dates and courts of T and D); the
      -- step decides whether the claim counts (a reversed / vacated anchored row without a bridge line)
      let tb? : Option Cert.TBridge := if !hct.trial.contains r.id then none else
        let ts := (shaOf w r.target).headD ""
        some { tSha := ts, tWindows := if ts.isEmpty then [] else cx.wins.getD ts [],
               line := (tbt.byId.get? r.id).map (fun l => (l.start, l.stop)), tDate := x.date,
               dDate := (bdec?.map (·.date)).getD 0, tCourt := some x.court, dCourt := bdec?.map (·.court) }
      -- the round-9 verdict (with the trial bridge and, round 11, the `anchorTribunal` cue test), then the remand
      -- check (`Cert.checkHistory11` = `Cert.remandThen` after `Cert.checkHistory9A`)
      let ra9 := Cert.checkHistory9A tb? zs (inp LA) anc? bridge? (hcl LA)
      let rf9 := Cert.checkHistory9A tb? zs (inp LF) anc? bridge? (hcl LF)
      let ra10 := Cert.remandThen remand? (inp LA) ra9
      let rf10 := Cert.remandThen remand? (inp LF) rf9
      -- round 11 §5.2: the row's identity line, with D's and T's texts (hashes and windows) and T's date (decisions2);
      -- checked after the verdict above (`Cert.checkHistory11I` = `Cert.identityThen` after `Cert.checkHistory11`)
      let ident? : Option Cert.Identity := (idt.byId.get? r.id).map fun il =>
        let ds := if r.by_ ≥ 0 then (shaOf w r.by_.toNat).headD "" else ""
        let ts := (shaOf w r.target).headD ""
        { form := il.form, token := il.token, dSha := ds, dWindows := if ds.isEmpty then [] else cx.wins.getD ds [],
          dStart := il.dStart, dStop := il.dStop, tSha := ts, tWindows := if ts.isEmpty then [] else cx.wins.getD ts [],
          tStart := il.tStart, tStop := il.tStop, tDate := x.date }
      let ra := Cert.identityThen ident? (inp LA) ra10
      let rf := Cert.identityThen ident? (inp LF) rf10
      -- the row reached the zone test (its round-8 verdict admits: `Cert.partZone_sound`, `Cert.zoneThen_fail_keeps`)
      if zt.lines > 0 && (ra9.admitted || ra9 == .fail .partZone) then
        if zs.isEmpty then nZMissing := nZMissing + 1 else nZChecked := nZChecked + 1
        if ra9 == .fail .partZone then nZFailed := nZFailed + 1
      -- round 10: the row reached the remand check (its round-9 verdict admits: `Cert.remandBridge_sound`,
      -- `Cert.remandThen_fail_keeps`)
      if remand?.isSome && ra9.admitted then
        nRChecked := nRChecked + 1
        if !ra10.admitted then nRFailed := nRFailed + 1
      -- round 11 §5.2: the row reached the identity check (its round-11 §5.1 verdict admits: `Cert.identityTie_sound`,
      -- `Cert.identityThen_fail_keeps`)
      if ident?.isSome && ra10.admitted then
        nIChecked := nIChecked + 1
        if !ra.admitted then nIFailed := nIFailed + 1
      if anc?.isSome && bridge?.isNone && ra.admitted then nAncAdm := nAncAdm + 1
      if anc?.isSome && bridge?.isSome then nBrAncIgn := nBrAncIgn + 1
      if bridge?.isSome && ra.admitted then nBrAdm := nBrAdm + 1
      if wide && (anc?.isNone || bridge?.isSome) then nWideUnused := nWideUnused + 1
      if trib && (anc?.isNone || bridge?.isSome) then nTribUnused := nTribUnused + 1
      if oc && ra.admitted && (bdec?.bind fun b => histPower LA b x) != some true then nOldUsed := nOldUsed + 1
      if hc?.isSome && ra.admitted then nHcAdm := nHcAdm + 1
      -- S-TX-3: whether a writ/petition notation promotes is read from its certified quote (`writPromotes`); the
      -- firm run reads the same courts (U epochs aside)
      let ev : HEvent := { id := ri, target := r.target, by_ := bdec?.map (·.id), date := r.date, kind, scope := sc,
                           promotes := kind != .writRefused || writPromotes LA tx r.cert.quote r.date x bdec? }
      if ra.admitted then histA := histA.push ev
      if rf.admitted then histF := histF.push ev
      if ra.admitted then nAdm := nAdm + 1 else nRej := nRej + 1
      if ri % nShards == k then certLines := certLines.push s!"history\t{r.id}\t{ra.toString}\t{rf.toString}"
    | _, _ =>
      nRej := nRej + 1
      if ri % nShards == k then certLines := certLines.push s!"history\t{r.id}\tbadRow\tbadRow"
  -- treatments
  -- round 4: witness rows (`treatment_witness.tsv`): the certificate text is the witness decision's, not the
  -- by-decision's (`Cert.checkWitness`)
  let witOf : HashMap String WitnessRow := tables.witness.foldl (fun m r => m.insert r.id r) {}
  let textNode (r : Data.TreatmentRow) : Nat := match witOf.get? r.id with | some wr => wr.node | none => r.by_
  -- round 5 (DESIGN5 §1): class claims. The file's presence turns round-5 output on (`r5`); a claim with an unknown
  -- word or an id that is no treatments row is ignored and counted; the first line for an id wins
  let r5 := tables.round5
  let treatIdSet : HashMap String Unit := tables.treatments.foldl (fun m r => m.insert r.id ()) {}
  let mut clsOf : HashMap String Data.ClassRow := {}
  let mut nClsBad := (tables.problems.filter (·.file.endsWith "treatment_class.tsv")).foldl (fun n p => n + p.bad) 0
  for c in tables.classes do
    -- round 7: `doctrine` is a claim (DESIGN7 §2.4); round 9: `joinedFar` (DESIGN9 §5), `implicitReject` (§7)
    if (c.claim == "recognised" || c.claim == "operativeWords" || c.claim == "doctrine" || c.claim == "joinedFar" ||
        c.claim == "implicitReject") && treatIdSet.contains c.id then
      -- a second line for an id is ignored, and is not a bad row (the first valid line wins)
      if !clsOf.contains c.id then clsOf := clsOf.insert c.id c
    else nClsBad := nClsBad + 1
  -- the class of each treatments row (index = row number; `none`: not a status-changing kind, or a bad row), and
  -- the rows recognised under the full rule set
  -- round 7 (round7/DESIGN7.md §2): joined lines (`joined.tsv`, optional; `joinedTable`); doctrine rows (claim
  -- `doctrine`): their uniqueness is decided over the table on the text check before the rows are checked
  let witIds : HashMap String Unit := tables.witness.foldl (fun m r => m.insert r.id ()) {}
  let jt := joinedTable tables witIds
  let nDocClaims := clsOf.fold (fun n _ c => if c.claim == "doctrine" then n + 1 else n) 0
  let dRows : Array Cert.DoctrineRow := if nDocClaims == 0 then #[] else
    tables.treatments.filterMap fun r =>
      if (clsOf.get? r.id).map (·.claim) != some "doctrine" then none else
      match TKind.ofString? r.kind, Temporal.ofString? r.temporal, decF r.by_, decF r.target with
      | some kind, some _, some b, some x =>
        let js := jt.byId.getD r.id []
        let c := certInput (.treat kind) r.cert (shaOf w (textNode r)) cx r.target (decide (x.date ≤ b.date)) (some true)
        some { target := r.target, labels := Cert.tieLabels js,
               text := (Cert.checkTreatment c r.explicit .doctrine js).admitted }
      | _, _, _, _ => none
  let ambLabels := doctrineAmbiguousLabels dRows
  -- round 9 (DESIGN9 §5): the key lengths of the index for the far-antecedent key test (only when a row claims
  -- `joinedFar`; without the claim the step is round 7's, `Cert.joinedFar_no_claim`)
  let lensF : List Nat := if !(clsOf.fold (fun b _ c => b || c.claim == "joinedFar") false) then [] else
    match cx.citeIndex with
    | some m => keyLengths m
    | none => []
  let mut nJAdm := 0
  let mut nDocAdm := 0
  let mut nDocAmb := 0
  let mut rowCls : Array (Option Cert.OClass) := #[none]
  let mut recRows : HashMap Nat Unit := {}
  let mut classLines : Array String := #[]
  let mut nRecog := 0
  let mut nOper := 0
  let mut treatA : Array TEvent := #[]
  let mut treatF : Array TEvent := #[]
  let mut followed : HashMap (Nat × Nat) Unit := {}
  let mut treatInfo : Array (Data.TreatmentRow × TKind × Scope × Nat) := #[]
  -- treatment-level findings read only rows whose text certificate passed (a rejected row asserts nothing)
  ri := 0
  for r in tables.treatments do
    ri := ri + 1
    let (is', sc) := parseScope is r.scope
    is := is'
    match TKind.ofString? r.kind, Temporal.ofString? r.temporal, decF r.by_, decF r.target with
    | some kind, some tm, some b, some x =>
      let dom := match sc with | .issues [i] => is.dom[i]! | _ => none
      -- power over the target's issue (T1(b)): on the issue's domain when known; otherwise on every domain the issue
      -- could have (each court's home domain, federal law, patent law when the Federal Circuit is involved).
      -- Disagreeing candidates leave the power unknown (D5): admitted unverified, effect `unknown powerUnknown`
      let powerOn (L : Lookups) (d? : Option Domain) : Option Bool :=
        match d? with
        | some d => (canChangeStatus L b x (some d)).map (·.1)
        | none =>
          match L.epochAt b.court b.date, L.epochAt x.court x.date with
          | some B, some X =>
            let ds := ([X.home, B.home, Domain.federalGeneral] ++
              (if B.circuit == 13 || X.circuit == 13 then [Domain.federalPatent] else [])).eraseDups
            let rs := ds.map fun d => (canChangeStatus L b x (some d)).map (·.1)
            if rs.all (· == some true) then some true else if rs.all (· == some false) then some false else none
          | _, _ => none
      let inp (auth : Option Bool) := certInput (.treat kind) r.cert (shaOf w (textNode r)) cx r.target
        (decide (x.date ≤ b.date)) auth
      -- a witness row: W known, explicit = 0, a status-changing kind; Y ≤ W in date (0 = unknown); W's court is X's
      -- court or has power over X (both under the tables given)
      -- round 5: the row's claim. `recognised` counts only on a witness row, `operativeWords` only on another row
      let claim := (clsOf.get? r.id).map (·.claim)
      let claimR := claim == some "recognised" && witOf.contains r.id
      let claimO := claim == some "operativeWords" && !witOf.contains r.id
      let wit (L : Lookups) (wr : WitnessRow) : Cert.Witness :=
        let wd? := decF wr.node
        { known := wd?.isSome, explicit := r.explicit, changes := kind.changesStatus, byEvidence := wr.byEvidence,
          by_ := r.by_,
          witnessOrdered := match wd? with
            | some wd => b.date == 0 || wd.date == 0 || decide (b.date ≤ wd.date)
            | none => false,
          standing := match wd? with
            | some wd => wd.court == x.court || powerAnyDomain L wd x == some true
            | none => false,
          -- round 5: the claim, W's power over X (not mere standing), and the three dates known
          claim := claimR,
          power := match wd? with
            | some wd => powerAnyDomain L wd x == some true
            | none => false,
          datesKnown := match wd? with
            | some wd => x.date != 0 && b.date != 0 && wd.date != 0
            | none => false }
      -- round 7: a doctrine claim (on any row: a witness row fails `doctrineBadRow`, LEAN7 L7-2), the joined lines,
      -- the main quote's mode; a doctrine row whose label the table ties to two targets fails (`Cert.doctrineFinal`)
      let claimD := claim == some "doctrine"
      -- round 9: the far-antecedent (§5) and implicit-rejection (§7) claims (without them: round 8's step,
      -- `Cert.joinedFar_no_claim`, `Cert.implicitReject_no_claim`)
      let claimF := claim == some "joinedFar"
      let claimI := claim == some "implicitReject"
      let js := jt.byId.getD r.id []
      let tcl : Cert.TClaim := if claimD then .doctrine else if claimO then .operative else .plain
      let ambD := claimD && (Cert.tieLabels js).any ambLabels.contains
      let fin (v : Cert.Result) : Cert.Result := if v.admitted && ambD then .fail .doctrineAmbiguous else v
      -- round 9: the zones of the text owner (W for a witness row, else `by`; D9-4 (1)), after the round-8 verdict
      -- (after `fin`: a doctrine row keeps `doctrineAmbiguous`, D9-4 (2))
      let zs := zonesOf (textNode r)
      -- without a claim `checkRecognised` is `checkWitness` (`Cert.checkRecognised_no_claim`); without joined lines
      -- and a doctrine claim `checkTreatment` is `check` / `checkOperative` (`Cert.no_joined_no_change`)
      let res (L : Lookups) : String × Bool :=
        let auth := if kind.changesStatus then powerOn L dom else some true
        if claimD then
          let v := Cert.zoneThen zs (inp auth) js (fin (Cert.checkTreatment (inp auth) r.explicit .doctrine js))
          (v.toString, v.admitted)
        else if claimI then
          let v := Cert.zoneThen zs (inp auth) js (Cert.checkTreatmentI true (inp auth) r.explicit tcl js)
          (v.toString, v.admitted)
        else match witOf.get? r.id with
        | some wr => let v := Cert.checkRecognised9 zs (inp auth) (wit L wr); (v.toString, v.admitted)
        | none =>
          let v := Cert.zoneThen zs (inp auth) js (Cert.checkTreatmentF claimF lensF (inp auth) r.explicit tcl js)
          (v.toString, v.admitted)
      let ra := res LA
      let rf := res LF
      let textOk := if claimD then
          (Cert.zoneThen zs (inp (some true)) js (fin (Cert.checkTreatment (inp (some true)) r.explicit .doctrine js))).admitted
        else if claimI then
          (Cert.zoneThen zs (inp (some true)) js (Cert.checkTreatmentI true (inp (some true)) r.explicit tcl js)).admitted
        else match witOf.get? r.id with
        | some wr => (Cert.checkRecognised9 zs (inp (some true)) (wit LA wr)).admitted
        | none =>
          (Cert.zoneThen zs (inp (some true)) js (Cert.checkTreatmentF claimF lensF (inp (some true)) r.explicit tcl js)).admitted
      -- recognised under a rule set: the text, the dates, W's standing and W's power (Y's power is decided per issue
      -- below, as for an explicit row)
      let recOk (L : Lookups) : Option Recog :=
        match witOf.get? r.id, (witOf.get? r.id).bind (fun wr => decF wr.node) with
        | some wr, some wd =>
          Cert.recogOf (Cert.checkRecognised9 zs (inp (some true)) (wit L wr)) wd.id wd.date
        | _, _ => none
      let ev : TEvent := { id := ri, by_ := r.by_, target := r.target, date := b.date, kind, scope := sc,
                           temporal := tm, explicit := r.explicit }
      -- an operative-words row that does not dispose of the case as a whole: every event's scope is demoted
      let demoteO := claimO && !Cert.wholeCase r.cert.quote
      -- the events admitted: power is decided per issue reached (each holding on its own domain; the anonymous
      -- issue 0 on the unknown domain), and the issues are grouped by verdict (`.issues` may hold 0 = ⊤)
      let events (L : Lookups) : List TEvent :=
        let ev := { ev with recog := recOk L }
        -- round 7: a doctrine row's events are always demoted (`Spec.doctrineEvent`, `Spec.doctrine_never_neg`)
        (fun (es : List TEvent) => if demoteO then es.map (fun e => { e with scope := demote e.scope })
          else if claimD then es.map doctrineEvent else es) <|
        if !textOk then []
        else if !kind.changesStatus then [ev]
        else
          let keys : Option (List Nat) := match sc with
            | .all => some (0 :: ((holdingsOf.getD x.id #[]).toList.map (·.issue)).eraseDups)
            | .issues ks => some ks
            | _ => none
          match keys with
          | none =>
            -- some issue, unknown which: ⊤ on the unknown domain, each holding on its own domain
            let hk := ((holdingsOf.getD x.id #[]).toList.map (·.issue)).eraseDups
            let v (key : Nat) := powerOn L (if key == 0 then none else is.dom[key]!)
            let v0 := powerOn L none
            let yes := hk.filter (v · == some true)
            let unk := hk.filter (v · == none)
            (if v0 == some true || !yes.isEmpty then [{ ev with scope := .someOf yes }] else []) ++
            (if v0 == none || !unk.isEmpty then [{ ev with scope := .someOf unk, powerKnown := false }] else [])
          | some ks =>
            let v (key : Nat) := powerOn L (if key == 0 then none else is.dom[key]!)
            let yes := ks.filter (v · == some true)
            let unk := ks.filter (v · == none)
            (if yes.isEmpty then [] else [{ ev with scope := .issues yes }]) ++
            (if unk.isEmpty then [] else [{ ev with scope := .issues unk, powerKnown := false }])
      treatA := treatA ++ (events LA).toArray
      treatF := treatF ++ (events LF).toArray
      if zt.lines > 0 && (ra.2 || ra.1 == "partZone") then
        if zs.isEmpty then nZMissing := nZMissing + 1 else nZChecked := nZChecked + 1
        if ra.1 == "partZone" then nZFailed := nZFailed + 1
      if ra.2 && kind == .followed then followed := followed.insert (r.by_, r.target) ()
      if ra.2 then nAdm := nAdm + 1 else nRej := nRej + 1
      if textOk then treatInfo := treatInfo.push (r, kind, sc, ri)
      if ri % nShards == k then certLines := certLines.push s!"treatment\t{r.id}\t{ra.1}\t{rf.1}"
      -- round 5: the row's class (DESIGN5 §5)
      -- recognised = the full verdict (`okRecognised…`): text, dates, W's power AND Y's power not shown absent
      let isRec := ra.1.startsWith "okRecognised"
      -- round 7: a doctrine row is classed `doctrine` (`Cert.classOf7`; without one it is `classOf`)
      let cls := if kind.changesStatus then
        some (Cert.classOf7 r.explicit isRec (claimD && kind == .disapproved) r.cert.quote) else none
      rowCls := rowCls.push cls
      if isRec then
        recRows := recRows.insert ri ()
        nRecog := nRecog + 1
      if claimO && ra.2 then nOper := nOper + 1
      if !js.isEmpty && ra.2 then nJAdm := nJAdm + 1
      if claimD && ra.2 then nDocAdm := nDocAdm + 1
      if claimD && ra.1 == "doctrineAmbiguous" then nDocAmb := nDocAmb + 1
      if r5 && ri % nShards == k then
        if let some c := cls then
          let cr := clsOf.get? r.id
          let dash (s : String) := if s.isEmpty then "-" else s
          classLines := classLines.push (s!"{r.id}\t{c.toString}\t{optS claim}\t{ra.1}\t" ++
            s!"{dash ((cr.map (·.fieldLimit)).getD "-")}\t{dash ((cr.map (·.doctrine)).getD "-")}\t" ++
            s!"{optS ((witOf.get? r.id).map (·.node))}")
    | _, _, _, _ =>
      nRej := nRej + 1
      rowCls := rowCls.push none
      if ri % nShards == k then certLines := certLines.push s!"treatment\t{r.id}\tbadRow\tbadRow"
  -- holdings' own certificates (the sentence stating the holding)
  let mut hi := 0
  for r in tables.holdings do
    hi := hi + 1
    if hi % nShards == k then
      let res := holdingCert r
      certLines := certLines.push s!"holding\t{r.id}\t{res}\t{res}"
  -- supersessions joined to law changes (explicit only change status)
  let lcs : HashMap String LawChangeRow := tables.lawchanges.foldl (fun m r => m.insert r.id r) {}
  let uscOf : HashMap String String := tables.issues.foldl (fun m r => m.insert r.key r.usc) {}
  let uscMatch (a b : String) : Bool :=
    a != "" && b != "" && a != "-" && b != "-" && (a == b || a.startsWith (b ++ "(") || b.startsWith (a ++ "("))
  -- a supersession whose evidence is a later court's words needs that treatment row's certificate (DESIGN D1)
  let treatOkText : HashMap String Unit := Id.run do
    let mut m : HashMap String Unit := {}
    for r in tables.treatments do
      match TKind.ofString? r.kind, decF r.by_, decF r.target with
      | some kind, some _, some _ =>
        -- round 9: the row's plain check, zone-checked (D9-4 (3))
        let c := certInput (.treat kind) r.cert (shaOf w (textNode r)) cx r.target true (some true)
        let res := Cert.zoneThen (zonesOf (textNode r)) c [] (Cert.check c)
        if res.admitted then m := m.insert r.id ()
      | _, _, _ => pure ()
    return m
  let mut supers : Array SEvent := #[]
  -- supersession event id -> the US Code block its law change rewrote (H2 holding-level match)
  let mut superUsc : HashMap Nat String := {}
  let mut inferredSup : Array Nat := #[]
  let mut si := 0
  for r in tables.supersessions do
    si := si + 1
    if r.evidence.startsWith "laterCourtSays:" && !treatOkText.contains (r.evidence.drop 15).toString then continue
    match lcs.get? r.lawchange with
    | some lc =>
      let mut scope : Scope := .someIssue
      if r.issue != "-" then
        let (is', i) := is.intern r.issue
        is := is'
        scope := .issues [i]
      else
        let ks := ((holdingsOf.getD r.target #[]).toList.filter fun h =>
          uscMatch (uscOf.getD is.keys[h.issue]! "-") lc.uscBlock).map (·.issue)
        if !ks.isEmpty then scope := .issues ks.eraseDups
      -- retroactive_to = 1 (SCHEMA): the law governs cases pending on its effective date, whatever the conduct
      -- date. Pending-ness is not in the data, so it is approximated (DEVIATIONS.md) as: known from the effective
      -- date (question date t >= effective), reaching all conduct (retroactive to 0)
      let pending := lc.retroactiveTo == 1
      let ev : SEvent := { id := si, target := r.target, scope,
                           enacted := if pending && lc.effective != 0 then lc.effective else lc.enacted,
                           effective := lc.effective,
                           retroactiveTo := if pending then some 0 else optNat lc.retroactiveTo,
                           explicit := r.explicit }
      superUsc := superUsc.insert si lc.uscBlock
      if r.explicit then supers := supers.push ev else inferredSup := inferredSup.push r.target
    | none => pure ()
  let recA : Record := { dec := decF, hist := histA.toList, treat := treatA.toList, supers := supers.toList }
  let recF : Record := { dec := decF, hist := histF.toList, treat := treatF.toList, supers := supers.toList }
  let EA := (ExecRecord.build recA).lookups
  let EF := (ExecRecord.build recF).lookups
  -- effects for every node with an admitted event
  let mut targets : HashMap Nat Unit := {}
  for e in histA do targets := targets.insert e.target ()
  for e in treatA do targets := targets.insert e.target ()
  -- (the firm run's targets too: a row admitted only under the S/L tables still changes the firm verdict)
  for e in histF do targets := targets.insert e.target ()
  for e in treatF do targets := targets.insert e.target ()
  for e in supers do targets := targets.insert e.target ()
  let mut effA : HashMap Nat (List Effect) := {}
  let mut effF : HashMap Nat (List Effect) := {}
  for (n, _) in targets do
    effA := effA.insert n (effectsOf LA EA decF n)
    effF := effF.insert n (effectsOf LF EF decF n)
  let t1 ← IO.monoMsNow
  -- ===== status =====
  let sh ← IO.FS.Handle.mk (out / s!"status-{pad2 k}.tsv") .write
  let mut subjects : HashMap Nat Unit := targets
  for (n, _) in holdingsOf do subjects := subjects.insert n ()
  let mut nStatus := 0
  let rowId (e : Effect) : String := match e.rule with
    | .history => histIds.getD e.src "-"
    | .supersession => superIds.getD e.src "-"
    | _ => treatIds.getD e.src "-"
  -- round 2 (DEVIATIONS 75): for a decision with a line-limited effect, one block of rows per pure line (the
  -- original line, each heir) in `status_lines-k.tsv`; `status-k.tsv` stays the union status, unchanged
  -- round 5 (DESIGN5 §5.1): `oclass`, the least class among the treatment effects that make a status
  let effClass (e : Effect) : Option Cert.OClass :=
    match e.rule with
    | .recognised => some .recognised
    | .treatment | .prospective => (rowCls.getD e.src none)
    | _ => none
  let oclassOf (effs : List Effect) (iss : Nat) (t u : Date) : String :=
    let s := status effs iss t u
    if s == .good then "-"
    else
      let cs := effs.filterMap fun e => if e.contrib iss t u == s then effClass e else none
      match cs.foldl (fun (m : Option Cert.OClass) c => match m with
          | none => some c
          | some m => some (if c.idx < m.idx then c else m)) none with
      | some c => c.toString
      | none => "-"
  let slh ← IO.FS.Handle.mk (out / s!"status_lines-{pad2 k}.tsv") .write
  let mut nLineRows := 0
  for (n, _) in subjects do
    if n % nShards != k then continue
    let ea0 := effA.getD n []
    let ef0 := effF.getD n []
    let issues := (Holding.anon ⟨n, 0, 0, none, none, none, none, none, none, none⟩) ::
      ((holdingsOf.getD n #[]).toList)
    -- on the diagonal t = u the status changes where an effect starts, lapses, or starts reaching conduct
    -- (the firm run's dates too, so that each row's firm flag holds over the whole row)
    let dates := (((ea0 ++ ef0).flatMap fun e => [e.start, e.conductFrom] ++ e.lapse.toList).filter (· ≤ asOf)).mergeSort (· ≤ ·)
    let dates := (dates.foldl (fun acc d => if acc.head? == some d then acc else d :: acc) []).reverse
    let blocks : List (Option Line) := none :: (linesOf ea0).map some
    for ln in blocks do
      -- `status (heirEffects ln.view ea0)` is `lineStatus ln ea0` (Spec/Lines)
      let ea := match ln with | none => ea0 | some l => heirEffects l.view ea0
      let ef := match ln with | none => ef0 | some l => heirEffects l.view ef0
      for h in issues do
        let pts := if dates.isEmpty then [0] else (if dates.head? == some 0 then dates else 0 :: dates)
        let mut i := 0
        for d in pts do
          let next := (pts.drop (i + 1)).head?.map (· - 1) |>.getD asOf
          i := i + 1
          let sA := status ea h.issue d d
          let sF := status ef h.issue d d
          let wit := witness ea h.issue d d
          let key := if h.issue == 0 then "-" else is.keys[h.issue]!
          let hk := if h.id == 0 then "-" else holdingKey[h.id]!
          let path := match wit with
            | some e => pathString [e.rule]
            | none => "-"
          let row := s!"{n}\t{key}\t{hk}\t{d}\t{next}\t{Status.toString sA}\t{Status.cls sA}\t{boolS (if h.issue == 0 then sameVerdict sA sF else sameVerdict (unknownAsOne sA) (unknownAsOne sF))}\t{optS (wit.map rowId)}\t{optS (wit.bind (·.actor))}\t{path}"
          let oc := if r5 then "\t" ++ oclassOf ea h.issue d d else ""
          match ln with
          | none =>
            sh.putStrLn (row ++ oc)
            nStatus := nStatus + 1
          | some l =>
            slh.putStrLn (row ++ "\t" ++ lineName l ++ oc)
            nLineRows := nLineRows + 1
  slh.flush
  sh.flush
  -- ===== findings =====
  let fh ← IO.FS.Handle.mk (out / s!"findings-{pad2 k}.tsv") .write
  let mut nFind := 0
  let emit (kind : String) (i j : Nat) (issue detail : String) (firm : Bool) (path : String)
      (oc : String := "-") : IO Unit :=
    fh.putStrLn (s!"{kind}\t{i}\t{j}\t{issue}\t{detail}\t{boolS firm}\t{path}" ++ (if r5 then "\t" ++ oc else ""))
  let rowOc (rj : Nat) : String := match rowCls.getD rj none with | some c => c.toString | none => "-"
  -- treatment-level findings (rows with id % N = k)
  for (r, kind, _, rj) in treatInfo do
    if rj % nShards != k then continue
    match decF r.by_, decF r.target with
    | some b, some x =>
      let facts (L : Lookups) (E : EventLookups) (effs : List Effect) : TreatFacts :=
        { kind, power := canChangeStatus L b x none,
          -- H3b: a bench known to be a panel or a division (an unknown bench, or an opinion circulated to the full
          -- court, makes no finding), under a rule the court had on the treating date as well
          panel := b.bench == some .panel || b.bench == some .division,
          ruleAtDeparture := strongRuleAt L b,
          -- round 2 (DEVIATIONS 76): the target's status in the treating court's line
          force := forceOn L E x (Holding.anon x) b, status := status (effectsFor L b effs) 0 b.date b.date }
      let fa := facts LA EA (effA.getD x.id [])
      let ff := facts LF EF (effF.getD x.id [])
      let path := pathString ((fa.force.map (·.2)).getD [] ++ (fa.power.map (·.2)).toList)
      -- a departure only from precedent that is still good law on the treating date (D4 triage)
      -- round 4: a witness row (the words are a later court's) yields only `inferredRejection`
      let wrow := witOf.contains r.id
      -- round 4 (DEVIATIONS 84): the panel finding needs the panel's own overruling words. "X is no longer good
      -- law" after an intervening decision of a higher court is the recognised exception to the prior-panel rule
      let ownWords := panelOwnWords.any (Cert.hasSub (Cert.norm r.cert.quote).toLower)
      if !wrow && ownWords && panelDepartsWithoutEnBanc fa && fa.status == .good then
        emit "panelDepartsWithoutEnBanc" b.id x.id "-" ((reprStr kind).replace "CaseLaw2.TKind." "")
          (panelDepartsWithoutEnBanc ff && ff.status == .good) path (rowOc rj)
        nFind := nFind + 1
      -- on every domain the unextracted issue could have, with power decided on all of them (D5)
      let ibu (L : Lookups) (E : EventLookups) (f : TreatFacts) : Bool :=
        let ds := domainsOf L x b
        !ds.isEmpty && ds.all fun d =>
          ignoresBindingInUnit { f with power := (powerAnyDomain L b x).map (·, RuleId.noPower),
                                        force := forceOn L E x { Holding.anon x with domain := some d } b }
      if !wrow && ibu LA EA fa then
        emit "ignoresBindingInUnit" b.id x.id "-" ((reprStr kind).replace "CaseLaw2.TKind." "") (ibu LF EF ff) path
          (rowOc rj)
        nFind := nFind + 1
      if kind == .followed then
        -- F6: a plurality decision with no Marks row, followed by a court it would bind as a majority opinion
        let plur (L : Lookups) (E : EventLookups) := x.form == some .plurality && !marksNodes.contains x.id &&
          !(domainsOf L x b).isEmpty && (domainsOf L x b).all fun d =>
            (forceOn L E { x with form := some .full } { Holding.anon x with domain := some d } b).map (·.1)
              == some .binding
        if plur LA EA then
          emit "pluralityTreatedAsBinding" b.id x.id "-" "followed" (plur LF EF) path; nFind := nFind + 1
        -- the issue's domain is unknown: the finding holds under every domain it could have (D5)
        let cfs (L : Lookups) (E : EventLookups) := (domainsOf L x b).map fun d =>
          citeFacts L E decF [] x { Holding.anon x with domain := some d } b none true
        let cf := citeFacts LA EA decF [] x (Holding.anon x) b none true
        if (cfs LA EA).all citesUnpublishedAsBinding && !(cfs LA EA).isEmpty then
          let cff := (cfs LF EF).all citesUnpublishedAsBinding && !(cfs LF EF).isEmpty
          emit "citesUnpublishedAsBinding" b.id x.id "-" (optS (cf.force.map (·.1))) cff path
          nFind := nFind + 1
      -- atRisk soft / claim (T1, T2): a soft negative treatment, or a status-changing one by a court shown to lack
      -- power, of a target not already wholly negative on the treating date (source = treating, subject = target)
      let tr (L : Lookups) (st : Status) : TreatRisk := { kind, power := powerAnyDomain L b x, targetNeg := isNeg st }
      let kname := (reprStr kind).replace "CaseLaw2.TKind." ""
      if softRisk (tr LA fa.status) then
        emit "atRisk" b.id x.id "-" ("soft:" ++ kname) (softRisk (tr LF ff.status)) path; nFind := nFind + 1
      if !wrow && claimRisk (tr LA fa.status) then
        emit "atRisk" b.id x.id "-" ("claim:" ++ kname) (claimRisk (tr LF ff.status)) path (rowOc rj)
        nFind := nFind + 1
      -- an inferred rejection by a court not shown to lack power, while the target is not already negative
      -- round 5: a recognised row's status rows carry it; it makes no `inferredRejection`
      if !r.explicit && kind.changesStatus && powerAnyDomain LA b x != some false && !isNeg fa.status &&
          !recRows.contains rj then
        emit "atRisk" x.id b.id "-" "inferredRejection" (powerAnyDomain LF b x != some false && !isNeg ff.status) path
          (rowOc rj)
        nFind := nFind + 1
    | _, _ => pure ()
  for n in inferredSup do
    if n % nShards == k then
      emit "atRisk" n (-1 : Int).toNat "-" "inferredSupersession" true "supersession"; nFind := nFind + 1
  -- citation-level findings
  let files ← (System.FilePath.mk edgesDir).readDir
  let mut nEdges := 0
  -- edge lines that are not two digit-only fields (FB-L7): counted and reported, not silently dropped
  let mut nBadEdges := 0
  for jf in [0:100] do
    if jf % nShards != k then continue
    let f := System.FilePath.mk edgesDir / s!"edges-{pad2 jf}.tsv"
    if !(files.any (·.path.fileName == f.fileName)) then continue
    let h ← IO.FS.Handle.mk f .read
    repeat
      let l ← h.getLine
      if l.isEmpty then break
      nEdges := nEdges + 1
      match (chomp l).splitOn "\t" with
      | [a, b] =>
        match nat? a, nat? b with
        | some i, some j =>
          let hasEff := effA.contains j || effF.contains j
          let unpub := w.dec.has j && w.dec.publication.get! j != 0 && w.dec.publication.get! j != 255
          if hasEff || unpub then
            match decF i, decF j with
            | some ci, some x =>
              let fol := followed.contains (i, j)
              let fa := citeFacts LA EA decF (effA.getD j []) x (Holding.anon x) ci none fol
              let path := pathString ((fa.force.map (·.2)).getD [])
              -- the citation findings one rules instance makes, by either route (the whole decision, or each cited
              -- holding on an issue the citing decision decides): (finding, issue, status)
              let rowsOf (L : Lookups) (E : EventLookups) (ej0 : List Effect) :
                  List (String × String × String × String) :=
                Id.run do
                  -- H4: the cited decision's status in the citing court's line of authority
                  let ej := effectsFor L ci ej0
                  -- H2: SCHEMA has no conduct date for a citing decision (`none`); its own date is not one
                  let f := citeFacts L E decF ej x (Holding.anon x) ci none fol
                  -- the cited status is the citing decision's own doing: every live effect making it is by `i`
                  let selfCaused (iss : Nat) : Bool :=
                    let st := status ej iss ci.date ci.date
                    let es := ej.filter fun e => st != .good && e.contrib iss ci.date ci.date == st
                    !es.isEmpty && es.all (·.actor == some i)
                  let mut out : List (String × String × String × String) := []
                  if !selfCaused 0 then
                    for (name, pr) in [("citesOverruled", citesOverruled), ("citesVacated", citesVacated),
                        ("citesWithdrawn", citesWithdrawn), ("citesNotCitable", citesNotCitable),
                        ("appliesSupersededHolding", appliesSupersededHolding)] do
                      if pr f then out := out ++ [(name, "-", Status.toString f.status, oclassOf ej 0 ci.date ci.date)]
                    -- round 5 (DESIGN5 §2.5): between an unannounced overruling and its recognition
                    if citedRecognisedLater f then out := out ++ [("atRisk", "-", "recognisedLater", "recognised")]
                  -- per holding (issue-aware), only when the whole decision's status does not already make it
                  let hsj := holdingsOf.getD j #[]
                  let citingIssues := (holdingsOf.getD i #[]).map (·.issue)
                  let citingUsc := (holdingsOf.getD i #[]).toList.map fun hc => uscOf.getD is.keys[hc.issue]! "-"
                  let allNeg := hsj.all fun hd => isNeg (status ej hd.issue ci.date ci.date) && !selfCaused hd.issue
                  for hd in (if isNeg f.status && !selfCaused 0 then #[] else hsj) do
                    if selfCaused hd.issue then continue
                    -- H2 holding-level match: the citing decision decides this issue, or an issue on the US Code
                    -- block rewritten by a supersession in force on this holding
                    let blocks := (ej.filter fun e => e.rule == .supersession &&
                      isNeg (e.contrib hd.issue ci.date ci.date)).filterMap fun e => superUsc.get? e.src
                    let hmatch := citingIssues.contains hd.issue || citingUsc.any fun u => blocks.any (uscMatch u)
                    let fh := citeFacts L E decF ej x hd ci none fol hmatch
                    if citingIssues.contains hd.issue || (citingIssues.isEmpty && allNeg) then
                      for (name, pr) in [("citesOverruled", citesOverruled), ("citesVacated", citesVacated),
                          ("citesWithdrawn", citesWithdrawn), ("appliesSupersededHolding", appliesSupersededHolding),
                          ("citesNotCitable", fun c => c.status == .neg .depublished)] do
                        if pr fh then out := out ++ [(name, is.keys[hd.issue]!, Status.toString fh.status,
                          oclassOf ej hd.issue ci.date ci.date)]
                    if supersededConductUnknown fh then
                      out := out ++ [("atRisk", is.keys[hd.issue]!, "supersededConductUnknown:" ++ is.keys[hd.issue]!, "-")]
                  return out
              let rA := rowsOf LA EA (effA.getD j [])
              let rF := rowsOf LF EF (effF.getD j [])
              -- D2 firm (DIFFTEST seed 30984): a finding is firm when the S/L-only tables make the same finding (the
              -- same kind on the same status) by any route, whole decision or holding by holding
              for (name, iss, st, oc) in rA do
                emit name i j iss st (rF.any fun (n', _, s', _) => n' == name && s' == st) path oc
                nFind := nFind + 1
              -- atRisk: the cited decision has since been negated (wholly, on asOf; not on the citing date) by a
              -- decision whose court binds the citing court, asked on that decision's date; a supersession or an
              -- event whose deciding decision is unknown, or is the citing decision itself, is no such decision (D4
              -- reading, DEVIATIONS 66)
              let lateNeg (L : Lookups) (E : EventLookups) (ea0 : List Effect) : Option Status :=
                let ea := effectsFor L ci ea0     -- H4: in the citing court's line
                let now := status ea 0 asOf asOf
                let bindsCiting (e : Effect) : Bool :=
                  match e.actor.bind decF with
                  | some ad =>
                    -- binding on every domain the unextracted issue could have (D5)
                    let cAt := { ci with date := ad.date }
                    let ds := domainsOf L ad cAt
                    e.rule != .supersession && ad.id != ci.id && !ds.isEmpty && ds.all fun d =>
                      (forceOn L E ad { Holding.anon ad with domain := some d } cAt).map (·.1) == some .binding
                  | none => false
                if isNeg now && !(isNeg (status ea 0 ci.date ci.date)) &&
                    (ea.filter fun e => isNeg (e.contrib 0 asOf asOf)).any bindsCiting then some now else none
              if let some now := lateNeg LA EA (effA.getD j []) then
                emit "atRisk" i j "-" ("citesLaterNegated:" ++ Status.toString now)
                  ((lateNeg LF EF (effF.getD j [])).isSome) "-"
                  (oclassOf (effectsFor LA ci (effA.getD j [])) 0 asOf asOf)
                nFind := nFind + 1
            | _, _ => pure ()
        | _, _ => nBadEdges := nBadEdges + 1
      | _ => nBadEdges := nBadEdges + 1
  fh.flush
  -- ===== splits =====
  let sph ← IO.FS.Handle.mk (out / s!"splits-{pad2 k}.tsv") .write
  let mut nSplit := 0
  let mut onIssue : HashMap Nat (Array (Decision × Holding)) := {}
  for (n, hs) in holdingsOf do
    if let some x := decF n then
      for h in hs do
        if h.answer.isSome && is.question[h.issue]! then
          onIssue := onIssue.insert h.issue ((onIssue.getD h.issue #[]).push (x, h))
  let factorsOf : HashMap String (List (Nat × String × Bool)) :=
    factorRows.foldl (fun m (hid, f, side, inR) => m.insert hid ((f, side, inR) :: m.getD hid [])) {}
  -- the firm run reads only S/L-tagged Marks rows (D2)
  let firmMarks : HashMap (Nat × String) Unit :=
    tables.marks.foldl (fun m r => if Tag.firmStr r.tag then m.insert (r.node, r.issue) () else m) {}
  for (iss, hs0) in onIssue do
    if iss % nShards != k then continue
    -- the bound courts examined: every (court, unit) that holds on the issue, and one trial court per system and
    -- circuit involved (with each unit seen), so that intra-court conflicts (CA, IL, NY, FL) show as `conflict`
    -- (the holdings that count for splits and conflicts: dated by asOf, and a plurality holding only with a Marks row)
    let qual (l : Array (Decision × Holding)) := l.filter fun (x, h) =>
      0 < x.date && x.date ≤ asOf && !(h.role == some .plurality && !h.marks)
    let hs := qual hs0
    let hsF := qual (hs0.map fun (x, h) => (x, { h with marks := h.marks && firmMarks.contains (x.id, is.keys[iss]!) }))
    let holders := (hs.toList.map fun (x, _) => (x.court, x.unit)).eraseDups
    let systems := (hs.toList.filterMap fun (x, _) => (LA.epochAt x.court x.date).map fun e => (e.system, e.circuit)).eraseDups
    let trials := systems.flatMap fun (sys, circ) =>
      match envAll.epochs.find? (fun e => e.system == sys && e.tier == .trial && (sys != 0 || e.circuit == circ) &&
          e.dateFrom ≤ asOf && asOf ≤ e.dateTo) with
      | some e => (holders.map (·.2)).eraseDups.map fun u => (e.court, u)
      | none => []
    let dsts := (holders ++ trials).eraseDups
    let resolveAt (hs : Array (Decision × Holding)) (L : Lookups) (E : EventLookups) (eps : List CourtEpoch)
        (effs : Nat → List Effect) (c : Nat × Option Nat) : Option (List Cand) := do
      let D ← L.epochAt c.1 asOf
      let synth : Decision := { id := 0, court := c.1, date := asOf, unit := c.2 }
      -- round 2 (DEVIATIONS 77): good law in the line of the bound court (`heldVia`, Spec/Lines)
      let goodHs := heldVia (effectsFor L synth) asOf
        (hs.toList.map fun (x, h) => { item := (x, h), issue := h.issue, effs := effs x.id })
      -- a good-law holding whose force here is unknown (an unknown court epoch) might bind: the bound court's
      -- answer set is then undecided (D5), not decided without it
      guard (!(goodHs.any fun (x, h) => (forceOn L E x h synth).isNone))
      let xc := goodHs.filterMap fun (x, h) => (candFor L E x h synth).map (x, ·)
      -- F7 first-in-time is the rule of the court whose panels conflict (§1.2): within the counting candidates of one
      -- source court whose `firstInTimeControls` is 1 on asOf (its strictly binding ones, if any), only the earliest
      -- stay (DEVIATIONS 67); the resolver's own first-in-time step is then not used
      -- vertical displacement (F1, H1, §4.1 V): a counting candidate whose deciding court another counting candidate
      -- binds (on the asOf date), without binding it in turn, gives way to it (SCOTUS over a circuit on federal law,
      -- a court of last resort over its intermediate court, the successor court of last resort over its
      -- predecessor's decisions). A decision held by binding adoption is displaced only by a holding that also binds
      -- its adopter (DEVIATIONS 67)
      let hOf : HashMap Nat Holding := hs.foldl (fun m (_, h) => m.insert h.id h) {}
      -- round 3 (DEVIATIONS 80; Bonner, 661 F.2d at 1209-11): a deciding court with no epoch on asOf has ceased; it
      -- is asked as it last sat (`lastEpoch`, `forceOnAs`), so a holding that bound the old court and binds the
      -- adopter in whose line the bound court stands displaces the inherited decision
      let bindsAt (a : Decision × Cand) (ct : Nat) (u : Option Nat) : Bool :=
        let f : Option (Force × List RuleId) := match L.epochAt ct asOf, lastEpoch eps ct asOf with
          | none, some D0 => forceOnAs L E a.1 (hOf.getD a.2.holding default) D0 u asOf
          | _, _ => forceOn L E a.1 (hOf.getD a.2.holding default) { id := 0, court := ct, date := asOf, unit := u }
        f.map (·.1) == some Force.binding
      let binds (a b : Decision × Cand) : Bool :=
        bindsAt a b.1.court b.1.unit &&
          -- (only an adopter in whose line the bound court stands, `inLine`: at a court outside it the adoption is
          -- not what the decision's force rests on; sweep seeds 52060 ff.)
          ((adoptionsOf L b.1).filter fun ad => ad.force == .binding && inLine L synth ad.adopter).all fun ad =>
            bindsAt a ad.adopter none
      let cnt := xc.filter (·.2.counts)
      let xc := xc.filter fun b => !b.2.counts ||
        !(cnt.any fun a => a.2.holding != b.2.holding && binds a b && !binds b a)
      let courts := (xc.map (·.1.court)).eraseDups
      let keep := courts.foldl (fun acc ct =>
        let grp := (xc.filter fun (x, cd) => x.court == ct && cd.counts)
        let grp := if grp.any (·.2.force == .binding) then grp.filter (·.2.force == .binding) else grp
        let ft := (L.epochAt ct asOf).bind (fun E' => L.rules.firstInTime ct E'.system asOf) == some true
        if ft && !grp.isEmpty && !(agree (grp.map (·.2))) then
          let d0 := minDate (grp.map (·.2))
          acc.filter fun (x, cd) => !(x.court == ct && cd.counts) || (grp.any (·.2 == cd) && cd.date == d0)
        else acc) xc
      -- the trial-scope rule (§4.1 V) is the intermediate court's (a court-level row overrides its system's), and it
      -- is already in each candidate's force: own-unit decisions bind, others bind absent conflict
      -- (`ownUnitThenAny`, so `preferBinding` keeps the own unit) or are persuasive (`ownUnitOnly`). The resolver's
      -- own unit step, keyed on the bound court, is therefore not used (DEVIATIONS 67)
      let _ := D
      some (resolve false none (keep.map (·.2)))
    let rA := dsts.map fun c => (c, resolveAt hs LA EA envAll.epochs (fun n => effA.getD n []) c)
    let rF := dsts.map fun c => (c, resolveAt hsF LF EF envFirm.epochs (fun n => effF.getD n []) c)
    -- the permissible answers, as a set (sorted, each once)
    let ans (r : List Cand) := ",".intercalate
      ((if r.any (·.answer == .no) then ["no"] else []) ++ (if r.any (·.answer == .yes) then ["yes"] else []))
    let hids (r : List Cand) := ",".intercalate (r.map fun c => holdingKey[c.holding]!)
    let cs (c : Nat × Option Nat) := s!"{c.1}" ++ (match c.2 with | some u => s!"/{u}" | none => "")
    let mixed (r : List Cand) := r.any (·.answer == .yes) && r.any (·.answer == .no)
    for (c, r) in rA do
      if let some r := r then
        if mixed r then
          let firm := match (rF.find? (·.1 == c)).bind (·.2) with | some f => mixed f | none => false
          sph.putStrLn s!"conflict	{is.keys[iss]!}	{cs c}	-	{ans r}	-	{hids r}	-	{asOf}	{boolS firm}"
          nSplit := nSplit + 1
    -- splits (DESIGN layer 5, D4 triage): two holdings on the question with opposite answers, both good law on
    -- `asOf`, by courts (court, unit) neither of which binds the other (force known and below bindingAbsentConflict
    -- both ways), with no good-law holding of a non-trial court, dated by `asOf`, binding both courts (the
    -- resolution, e.g. a later SCOTUS holding). One row per issue and pair of courts.
    let splitPairs (hs : Array (Decision × Holding)) (L : Lookups) (E : EventLookups) (effs : Nat → List Effect) :
        List ((Nat × Option Nat) × (Nat × Option Nat) × String × String) := Id.run do
      let synth (c : Nat) (u : Option Nat) : Decision := { id := 0, court := c, date := asOf, unit := u }
      -- round 2 (DEVIATIONS 77): a holding counts for its court when it is good law in that court's line; it binds
      -- another court only if it is good law in that court's line; a resolver must be good law in both lines
      let goodAt (x : Decision) (h : Holding) (c : Nat) (u : Option Nat) : Bool :=
        goodVia (effectsFor L (synth c u)) (effs x.id) h.issue asOf
      let dated := hs.toList.filter fun (x, h) => 0 < x.date && x.date ≤ asOf && h.answer.isSome &&
        !(h.role == some .plurality && !h.marks)
      let good := dated.filter fun (x, h) => goodAt x h x.court x.unit
      let fOn (x : Decision) (h : Holding) (c : Nat) (u : Option Nat) : Option Force :=
        (forceOn L E x h (synth c u)).map (·.1)
      let below (f : Option Force) (goodThere : Bool) : Bool := match f with
        | some f => f.rank < Force.bindingAbsentConflict.rank || !goodThere
        | none => false
      let resolvers := dated.filter fun (x, _) => (L.epochAt x.court x.date).any (·.tier != .trial)
      let mut out := []
      for (xa, ha) in good do
        for (xb, hb) in good do
          if ha.answer == some .yes && hb.answer == some .no &&
              !(xa.court == xb.court && xa.unit == xb.unit) then
            let key := if xa.court < xb.court || (xa.court == xb.court && xa.unit.getD 0 ≤ xb.unit.getD 0)
              then ((xa.court, xa.unit), (xb.court, xb.unit), s!"yes	no	{holdingKey[ha.id]!}", holdingKey[hb.id]!)
              else ((xb.court, xb.unit), (xa.court, xa.unit), s!"no	yes	{holdingKey[hb.id]!}", holdingKey[ha.id]!)
            if out.any (fun (c1, c2, _, _) => c1 == key.1 && c2 == key.2.1) then continue
            if below (fOn xa ha xb.court xb.unit) (goodAt xa ha xb.court xb.unit) &&
                below (fOn xb hb xa.court xa.unit) (goodAt xb hb xa.court xa.unit) &&
                !(resolvers.any fun (xr, hr) => goodAt xr hr xa.court xa.unit && goodAt xr hr xb.court xb.unit &&
                    fOn xr hr xa.court xa.unit == some .binding &&
                    fOn xr hr xb.court xb.unit == some .binding) then
              out := out ++ [key]
      return out
    let spA := splitPairs hs LA EA (fun n => effA.getD n [])
    let spF := splitPairs hsF LF EF (fun n => effF.getD n [])
    for (c1, c2, h1, h2) in spA do
      let firm := spF.any fun (d1, d2, _, _) => d1 == c1 && d2 == c2
      sph.putStrLn s!"split	{is.keys[iss]!}	{cs c1}	{cs c2}	{h1}	{h2}	{asOf}	{boolS firm}"
      nSplit := nSplit + 1
  sph.flush
  -- ===== Horty (factors.tsv; FACTORS_NEEDS.md) =====
  -- Factors are uncertain data, never premises: these rows are findings. A holding with factor rows enters the base of
  -- its family issue with its outcome (`factor_cases.tsv`: holding_id, node, family, issue key, outcome yes|no, …;
  -- optional), or else of its own issue with its yes/no answer. Only holdings good law on asOf count.
  -- * binding base: at each examined court (every holder's (court, unit); one trial court per system and circuit of
  --   the holders, crossed with their units; for federal holders, the first federal court of appeals), the cases whose
  --   force there is at least bindingAbsentConflict (`Cand.counts`, the set the resolver works on);
  -- * self base (informational): each holder court's own cases, whether or not it is bound by them.
  -- An inconsistent base names its first conflicting pair (`h1,h2`); consistent bases are reported too, and counted.
  let mut hortyBases := 0
  let mut hortyInconsistent := 0
  let mut hortySelf := 0
  let mut hortySelfInconsistent := 0
  -- round 2 (DEVIATIONS 78): one row per distinct binding base: family, court, verdict, cases (sorted ids), firm
  let hh ← IO.FS.Handle.mk (out / s!"horty-{pad2 k}.tsv") .write
  if !factorsOf.isEmpty then
    let byKey : HashMap String (Decision × Holding) := Id.run do
      let mut m : HashMap String (Decision × Holding) := {}
      for (n, hs) in holdingsOf do
        if let some x := decF n then
          for h in hs do m := m.insert holdingKey[h.id]! (x, h)
      return m
    let fam : HashMap String (String × Bool) := famRows.foldl (fun m (hid, key, out) => m.insert hid (key, out)) {}
    let mk (side : String) (f : Nat) : Horty.Factor := { id := f, side := if side == "pi" then .pi else .delta }
    -- family key -> cases (decision, holding, its FCase)
    let mut fams : HashMap String (Array (Decision × Holding × Horty.FCase)) := {}
    for (hid, fs) in factorsOf do
      if let some (x, h) := byKey.get? hid then
        let keyOut : Option (String × Bool) := match fam.get? hid with
          | some ko => some ko
          | none => h.answer.map fun a => (is.keys[h.issue]!, a == .yes)
        if let some (key, yes) := keyOut then
          if 0 < x.date && x.date ≤ asOf then
            let facts := fs.map fun (f, side, _) => mk side f
            let reason := (fs.filter (·.2.2)).map fun (f, side, _) => mk side f
            let fc : Horty.FCase := ⟨facts, reason, if yes then .pi else .delta⟩
            fams := fams.insert key ((fams.getD key #[]).push (x, h, fc))
    let firstPair (cs : List (Decision × Holding × Horty.FCase)) : String := Id.run do
      for (_, h1, c1) in cs do
        for (_, h2, c2) in cs do
          if Horty.conflict c1 c2 then
            let a := holdingKey[h1.id]!
            let b := holdingKey[h2.id]!
            return (if a ≤ b then a ++ "," ++ b else b ++ "," ++ a)
      return "-"
    for (key, cs0) in fams do
      if key.hash.toNat % nShards != k then continue
      -- round 2 (DEVIATIONS 78): a case is live when it is good law in at least one of its decision's pure lines
      -- (with no line-limited effect: good law); each base then reads the line of the court examined
      let good (effs : Nat → List Effect) := cs0.toList.filter fun (x, h, _) =>
        liveSomewhere (effs x.id) h.issue asOf
      let csA := good (fun n => effA.getD n [])
      let csF := good (fun n => effF.getD n [])
      -- examined courts
      let holders := (csA.map fun (x, _, _) => (x.court, x.unit)).eraseDups
      let systems := (csA.filterMap fun (x, _, _) =>
        (LA.epochAt x.court x.date).map fun e => (e.system, e.circuit)).eraseDups
      let units := (holders.map (·.2)).eraseDups
      let trials := systems.flatMap fun (sys, circ) =>
        match envAll.epochs.find? (fun e => e.system == sys && e.tier == .trial && (sys != 0 || e.circuit == circ) &&
            e.dateFrom ≤ asOf && asOf ≤ e.dateTo) with
        | some e => units.map fun u => (e.court, u)
        | none => []
      let fedApp : List (Nat × Option Nat) := if systems.any (·.1 == 0) then
          match envAll.epochs.find? (fun e => e.system == 0 && e.tier == .appellate && 0 < e.circuit &&
              e.circuit ≤ 12 && e.dateFrom ≤ asOf && asOf ≤ e.dateTo) with
          | some e => [(e.court, none)]
          | none => []
        else []
      let dsts := (holders ++ trials ++ fedApp).eraseDups
      -- the binding base at a court: the cases that bind there and are good law in its line (`heldVia`; for a
      -- court whose line is known this is `lineBase`, Spec/Lines)
      let baseAt (L : Lookups) (E : EventLookups) (effs : Nat → List Effect)
          (cs : List (Decision × Holding × Horty.FCase)) (c : Nat × Option Nat) :
          List (Decision × Holding × Horty.FCase) :=
        let synth : Decision := { id := 0, court := c.1, date := asOf, unit := c.2 }
        heldVia (effectsFor L synth) asOf (cs.map fun (x, h, fc) =>
          { item := (x, h, fc), issue := h.issue, effs := effs x.id,
            binds := match forceOn L E x h synth with
              | some (f, _) => decide (Force.bindingAbsentConflict.rank ≤ f.rank)
              | none => false })
      let mut seen : HashMap (List String) Unit := {}
      for c in dsts do
        let bA := baseAt LA EA (fun n => effA.getD n []) csA c
        if bA.length < 2 then continue
        -- one row per distinct base (two units of one court with the same base give one row)
        let ids := (bA.map fun (_, h, _) => holdingKey[h.id]!).mergeSort (· ≤ ·)
        if seen.contains ids then continue
        seen := seen.insert ids ()
        let bF := baseAt LF EF (fun n => effF.getD n []) csF c
        let incF := !Horty.consistent (bF.map (·.2.2))
        let idList := ",".intercalate ids
        hortyBases := hortyBases + 1
        if !Horty.consistent (bA.map (·.2.2)) then
          hortyInconsistent := hortyInconsistent + 1
          emit "inconsistentBindingBase" c.1 0 key (firstPair bA) incF "Horty"
          hh.putStrLn s!"{key}\t{c.1}\tinconsistent\t{idList}\t{boolS incF}"
        else
          emit "hortyConsistentBase" c.1 0 key s!"{bA.length} cases" (!incF && bF.length ≥ 2) "Horty"
          hh.putStrLn s!"{key}\t{c.1}\tconsistent\t{idList}\t{boolS (!incF && bF.length ≥ 2)}"
        nFind := nFind + 1
      -- self bases (informational): each holder court's own good-law cases, bound by them or not
      for ct in (csA.map fun (x, _, _) => x.court).eraseDups do
        let inOwn (L : Lookups) (effs : Nat → List Effect) (x : Decision) (h : Holding) : Bool :=
          x.court == ct && goodVia (effectsFor L { id := 0, court := ct, date := asOf, unit := x.unit }) (effs x.id)
            h.issue asOf
        let own := csA.filter fun (x, h, _) => inOwn LA (fun n => effA.getD n []) x h
        if own.length < 2 then continue
        let ownF := csF.filter fun (x, h, _) => inOwn LF (fun n => effF.getD n []) x h
        hortySelf := hortySelf + 1
        if !Horty.consistent (own.map (·.2.2)) then
          hortySelfInconsistent := hortySelfInconsistent + 1
          emit "hortySelfInconsistent" ct 0 key (firstPair own) (!Horty.consistent (ownF.map (·.2.2))) "Horty"
          nFind := nFind + 1
  hh.flush
  -- ===== atRisk contraryBinding (F14, T1(c)) =====
  -- for each holding x with a yes/no answer: the earliest later contrary holding y (by date, then holding id) of a
  -- non-trial court that binds x's court and unit on y's date; reported when x is still good law then and y is good
  -- law on its own date; the search stops at the first binding contrary holding by whose date x is no longer good
  let mut answered : HashMap Nat (Array (Decision × Holding)) := {}
  for (n, hs) in holdingsOf do
    if let some x := decF n then
      if x.date != 0 then
        for h in hs do
          if h.answer.isSome then answered := answered.insert h.issue ((answered.getD h.issue #[]).push (x, h))
  for (iss, hs) in answered do
    if iss % nShards != k then continue
    if !(hs.any (·.2.answer == some .yes) && hs.any (·.2.answer == some .no)) then continue
    let contrary (hs : Array (Decision × Holding)) (L : Lookups) (E : EventLookups) (effs : Nat → List Effect) :
        List (Nat × Nat × Nat) := Id.run do
      let ups := (hs.toList.filter fun (y, _) => (L.epochAt y.court y.date).any (·.tier != .trial)).mergeSort
        fun (a, ha) (b, hb) => a.date < b.date || (a.date == b.date && holdingKey[ha.id]! ≤ holdingKey[hb.id]!)
      let xs := hs.toList.mergeSort fun (_, ha) (_, hb) => holdingKey[ha.id]! ≤ holdingKey[hb.id]!
      let mut out := []
      for (x, hx) in xs do
        let mut done := false
        for (y, hy) in ups do
          if done then break
          if hy.answer == hx.answer || y.date ≤ x.date then continue
          let t := y.date
          let synth : Decision := { id := 0, court := x.court, date := t, unit := x.unit }
          -- binding on the issue's domain, or on every domain an unknown one could have (D5)
          let ds := match hy.domain with | some d => [d] | none => domainsOf L y synth
          let binds := !ds.isEmpty && ds.all fun d =>
            (forceOn L E y { hy with domain := some d } synth).map (·.1) == some .binding
          if !binds then continue
          -- round 2 (DEVIATIONS 76): both read in the line of the holder's court on that date
          let hg := goodVia (effectsFor L synth) (effs x.id) hx.issue t
          let cg := goodVia (effectsFor L synth) (effs y.id) hy.issue t
          let f : ContraryFacts := { opposite := true, later := true, binds, holderGood := hg, contraryGood := cg }
          if !f.holderGood then
            done := true
            continue
          if !f.contraryGood then continue
          if contraryBinding f then
            out := out ++ [(y.id, x.id, hy.id)]
            done := true
      return out
    let cA := contrary hs LA EA (fun n => effA.getD n [])
    let hsF := hs.map fun (x, h) => (x, { h with marks := h.marks && firmMarks.contains (x.id, is.keys[iss]!) })
    let cF := contrary hsF LF EF (fun n => effF.getD n [])
    for (yn, xn, hid) in cA do
      emit "atRisk" yn xn "-" ("contraryBinding:" ++ holdingKey[hid]!) (cF.any fun (a, b, _) => a == yn && b == xn) "F14"
      nFind := nFind + 1
  fh.flush
  -- certs
  IO.FS.writeFile (out / s!"certs-{pad2 k}.tsv") ("\n".intercalate certLines.toList ++ (if certLines.isEmpty then "" else "\n"))
  let t2 ← IO.monoMsNow
  let problems := (tables.problems.push pd |>.push pe |>.push pf |>.push pc |>.push pw |>.push pi |>.push pfc).filter (·.bad > 0)
  let summ := [s!"shard\t{k}/{nShards}", s!"asOf\t{asOf}", s!"rows_admitted\t{nAdm}", s!"rows_rejected\t{nRej}",
    s!"status_rows\t{nStatus}", s!"status_line_rows\t{nLineRows}", s!"findings\t{nFind}", s!"splits\t{nSplit}", s!"edges\t{nEdges}", s!"bad_edges\t{nBadEdges}", s!"horty_bases\t{hortyBases}", s!"horty_inconsistent\t{hortyInconsistent}",
    s!"horty_self_bases\t{hortySelf}", s!"horty_self_inconsistent\t{hortySelfInconsistent}",
    s!"load_ms\t{t1 - t0}", s!"run_ms\t{t2 - t1}"] ++ problems.toList.map (fun p => s!"bad_rows\t{p.file}\t{p.bad}") ++
    (if r5 then [s!"class_rows\t{clsOf.size}", s!"class_bad_rows\t{nClsBad}", s!"recognised_rows\t{nRecog}",
      s!"operative_rows\t{nOper}"] else []) ++
    -- round 6: anchor counters, only when `history_anchor.tsv` has a line
    anchors.summary nAncAdm nBrAncIgn ++
    -- round 7: joined, history-claim and doctrine counters, each only when its table has a line
    jt.summary nJAdm ++ hct.summary nHcAdm nWideUnused nOldUsed nTribUnused ++
    (if nDocClaims == 0 then [] else
      [s!"doctrine_rows\t{nDocClaims}", s!"doctrine_admitted\t{nDocAdm}", s!"doctrine_ambiguous\t{nDocAmb}"]) ++
    -- round 8: bridge counters, only when `history_bridge.tsv` has a line
    bridges.summary nBrAdm nBrAncIgn ++
    -- round 9: zone counters, only when `part_zone.tsv` has a line
    zt.summary nZChecked nZFailed nZMissing ++
    -- round 10: remand counters, only when `history_remand.tsv` has a line
    rmt.summary nRChecked nRFailed ++
    -- round 10 §6: T-quote counters, only when `history_tbridge.tsv` has a line
    tbt.summary ++
    -- round 11 §5.2: identity counters, only when `history_identity.tsv` has a line
    idt.summary nIChecked nIFailed
  -- round 5: the class of every status-changing treatments row
  if r5 then
    IO.FS.writeFile (out / s!"classes-{pad2 k}.tsv")
      ("\n".intercalate classLines.toList ++ (if classLines.isEmpty then "" else "\n"))
  IO.FS.writeFile (out / s!"summary-{pad2 k}.tsv") ("\n".intercalate summ ++ "\n")
  IO.println s!"shard {k}/{nShards}: admitted {nAdm}, rejected {nRej}; status {nStatus}; findings {nFind}; splits {nSplit}; edges {nEdges}; load {t1 - t0} ms, run {t2 - t1} ms"
  return 0

end CaseLaw2.Run

def main (args : List String) : IO UInt32 := CaseLaw2.Run.main args
