import LegalProofs.CaseLaw2.Tsv

/-!
# caselaw-lean-2: raw rows of the SCHEMA files (design-neutral infrastructure)

One structure per file of `caselaw-lean-2/SCHEMA.md`, column for column, in the order the schema gives. Fields stay as
the schema writes them (enumerations as their strings), so these types fix nothing about the Lean model; the model
modules translate rows into their own types. Exceptions, for memory only: `decisions2.tsv` (one row per node, 6.9M)
is loaded column-wise, with its enumerations as one-byte codes (index into the schema's value list, 255 = a value
the schema does not list) and `text_sha` kept only for the nodes a caller asks for.
-/

namespace CaseLaw2.Data
open CaseLaw2.Tsv Std

/-- The six CERT columns. -/
structure Cert where
  textSha : String
  start : Nat
  stop : Nat
  quote : String
  evidence : String
  part : String
  deriving Repr, Inhabited

def Cert.parse (f : Array String) (i : Nat) : Option Cert := do
  let start ← nat? f[i+1]!
  let stop ← nat? f[i+2]!
  some { textSha := f[i]!, start, stop, quote := f[i+3]!, evidence := f[i+4]!, part := f[i+5]! }

/-! ## Courts -/

structure CourtRow where
  court : Nat
  epochFrom : Nat
  epochTo : Nat
  name : String
  system : Nat
  tier : String
  lastResortFor : String
  circuit : Nat
  unit : Nat
  src : String
  tag : String
  deriving Repr, Inhabited

def CourtRow.parse (f : Array String) : Option CourtRow := do
  some { court := ← nat? f[0]!, epochFrom := ← nat? f[1]!, epochTo := ← nat? f[2]!, name := f[3]!,
         system := ← nat? f[4]!, tier := f[5]!, lastResortFor := f[6]!, circuit := ← nat? f[7]!,
         unit := ← nat? f[8]!, src := f[9]!, tag := f[10]! }

structure SuccessionRow where
  old : Nat
  new : Nat
  date : Nat
  kind : String
  src : String
  tag : String
  deriving Repr, Inhabited

def SuccessionRow.parse (f : Array String) : Option SuccessionRow := do
  some { old := ← nat? f[0]!, new := ← nat? f[1]!, date := ← nat? f[2]!, kind := f[3]!, src := f[4]!, tag := f[5]! }

structure AdoptionRow where
  adopter : Nat
  source : Nat
  upTo : Nat
  filter : String
  force : String
  src : String
  tag : String
  deriving Repr, Inhabited

def AdoptionRow.parse (f : Array String) : Option AdoptionRow := do
  some { adopter := ← nat? f[0]!, source := ← nat? f[1]!, upTo := ← nat? f[2]!, filter := f[3]!, force := f[4]!,
         src := f[5]!, tag := f[6]! }

/-- `system` is a system index, or `-court_id` for a court-level rule. -/
structure RuleRow where
  system : Int
  rule : String
  value : String
  dateFrom : Nat
  dateTo : Nat
  src : String
  tag : String
  deriving Repr, Inhabited

def RuleRow.parse (f : Array String) : Option RuleRow := do
  some { system := ← int? f[0]!, rule := f[1]!, value := f[2]!, dateFrom := ← nat? f[3]!, dateTo := ← nat? f[4]!,
         src := f[5]!, tag := f[6]! }

/-! ## Decisions (column-wise) -/

def benchValues : Array String :=
  #["panel", "division", "enBanc", "limitedEnBanc", "circulated", "conflictPanel", "wholeCourt", "unknown"]
def publicationValues : Array String :=
  #["published", "unpublished", "table", "summaryOrder", "memorandum", "unknown"]
def formValues : Array String :=
  #["full", "perCuriam", "summaryAffirmance", "equallyDivided", "certifiedAnswer", "plurality", "memorandum", "unknown"]

def code (vals : Array String) (s : String) : UInt8 :=
  match vals.idxOf? s with
  | some i => i.toUInt8
  | none => 255

structure Decisions where
  /-- `none` marks a node with no row. -/
  court : Array Nat
  date : Array Nat
  unit : Array Nat
  bench : ByteArray
  publication : ByteArray
  form : ByteArray
  present : ByteArray
  /-- `text_sha` for the requested nodes only. -/
  sha : HashMap Nat String
  duplicates : Nat
  outOfRange : Nat

def Decisions.has (d : Decisions) (n : Nat) : Bool := n < d.present.size && d.present.get! n != 0

/-- Load `decisions2.tsv` for nodes `0 … size-1`, keeping `text_sha` where `wantSha` holds. -/
def loadDecisions (path : System.FilePath) (size : Nat) (wantSha : Nat → Bool) : IO (Decisions × Problems) := do
  let p0 : Problems := { file := "decisions2.tsv" }
  let d0 : Decisions :=
    { court := Array.replicate size 0, date := Array.replicate size 0, unit := Array.replicate size 0,
      bench := ⟨Array.replicate size 255⟩, publication := ⟨Array.replicate size 255⟩,
      form := ⟨Array.replicate size 255⟩, present := ⟨Array.replicate size 0⟩, sha := {}, duplicates := 0,
      outOfRange := 0 }
  let ((d, p), _) ← foldLines path (d0, p0) fun (d, p) n l =>
    let f := fields l
    let p := { p with rows := p.rows + 1 }
    -- exactly 9 fields (FB-L1: a tab inside text_sha or src must not go unnoticed)
    if f.size != 9 then (d, p.note n s!"{f.size} fields ≠ 9" l) else
    match nat? f[0]!, nat? f[1]!, nat? f[2]!, nat? f[3]! with
    | some node, some court, some date, some unit =>
      if node ≥ size then ({ d with outOfRange := d.outOfRange + 1 }, p.note n "node out of range" l)
      else
        let dup := d.present.get! node != 0
        ({ d with court := d.court.set! node court, date := d.date.set! node date, unit := d.unit.set! node unit,
                  bench := d.bench.set! node (code benchValues f[4]!),
                  publication := d.publication.set! node (code publicationValues f[5]!),
                  form := d.form.set! node (code formValues f[6]!),
                  present := d.present.set! node 1,
                  sha := if wantSha node then d.sha.insert node f[7]! else d.sha,
                  duplicates := d.duplicates + (if dup then 1 else 0) },
         if dup then p.note n "duplicate node" l else p)
    | _, _, _, _ => (d, p.note n "unparseable" l)
  return (d, p)

/-! ## Same-case history and treatments -/

structure HistoryRow where
  /-- the reader's row id (SCHEMA does not type it; the reader writes e.g. `h:<n>:<j>:<kind>`) -/
  id : String
  target : Nat
  /-- -1 unknown -/
  by_ : Int
  date : Nat
  kind : String
  scope : String
  cert : Cert
  src : String
  deriving Repr, Inhabited

def HistoryRow.parse (f : Array String) : Option HistoryRow := do
  some { id := f[0]!, target := ← nat? f[1]!, by_ := ← int? f[2]!, date := ← nat? f[3]!, kind := f[4]!,
         scope := f[5]!, cert := ← Cert.parse f 6, src := f[12]! }

/-- `history_anchor.tsv` (round 6, `round6/history/DESIGN6.md` §4): the history row `id` carries a second quote, the
anchor, from the same text as its certificate: `id, a_start, a_end, a_quote, a_part, src`. -/
structure AnchorRow where
  id : String
  start : Nat
  stop : Nat
  quote : String
  part : String
  src : String
  deriving Repr, Inhabited

def AnchorRow.parse (f : Array String) : Option AnchorRow := do
  some { id := f[0]!, start := ← nat? f[1]!, stop := ← nat? f[2]!, quote := f[3]!, part := f[4]!, src := f[5]! }

/-- `joined.tsv` (round 7, `round7/DESIGN7.md` §1–2): the row `id` of `table` (`treatments` | `history`) carries a
further quote of the same text as its certificate, with a relation (`antecedent` | `doctrineTie`) to its main quote:
`id, table, rel, j_start, j_end, j_quote, j_part, label, src`. An unknown table or relation, or a non-numeric offset,
makes the line a bad row. -/
structure JoinedRow where
  id : String
  table : String
  rel : String
  start : Nat
  stop : Nat
  quote : String
  part : String
  label : String
  src : String
  deriving Repr, Inhabited

def JoinedRow.parse (f : Array String) : Option JoinedRow := do
  if !(f[1]! == "treatments" || f[1]! == "history") then none
  if !(f[2]! == "antecedent" || f[2]! == "doctrineTie") then none
  some { id := f[0]!, table := f[1]!, rel := f[2]!, start := ← nat? f[3]!, stop := ← nat? f[4]!, quote := f[5]!,
         part := f[6]!, label := f[7]!, src := f[8]! }

/-- `history_claim.tsv` (round 7, §3): the history row `id` claims `orderHead` or `setAside`: `id, claim, src`. An
unknown claim makes the line a bad row. -/
structure HClaimRow where
  id : String
  claim : String
  src : String
  deriving Repr, Inhabited

def HClaimRow.parse (f : Array String) : Option HClaimRow :=
  -- round 8 (`round8/DESIGN8.md` §5–6): `anchorWide`, `oldCircuit`
  -- round 10 (`round10/DESIGN10.md` §6): `trialBridge`
  -- round 11 (`round11/DESIGN11.md` §5.1): `anchorTribunal`
  if f[1]! == "orderHead" || f[1]! == "setAside" || f[1]! == "anchorWide" || f[1]! == "oldCircuit" ||
      f[1]! == "trialBridge" || f[1]! == "anchorTribunal" then
    some { id := f[0]!, claim := f[1]!, src := f[2]! }
  else none

/-- `history_bridge.tsv` (round 8, `round8/DESIGN8.md` §4): the history row `id` is linked to its target by a quote of
a third decision W: `id, w_node, b_start, b_end, b_quote, src`. A non-numeric node or offset makes the line a bad
row. -/
structure BridgeRow where
  id : String
  w : Nat
  start : Nat
  stop : Nat
  quote : String
  src : String
  deriving Repr, Inhabited

def BridgeRow.parse (f : Array String) : Option BridgeRow := do
  some { id := f[0]!, w := ← nat? f[1]!, start := ← nat? f[2]!, stop := ← nat? f[3]!, quote := f[4]!, src := f[5]! }

/-- `part_zone.tsv` (round 9, `round9/DESIGN9.md` §4): a zone `[z_start, z_end)` of the text of `node`, of one part:
`node, z_start, z_end, part, src`. A non-numeric node or offset makes the line a bad row (it poisons no node, D9-4);
the part is checked by the runner (`Cert.zoneWellFormed`). -/
structure ZoneRow where
  node : Nat
  start : Nat
  stop : Nat
  part : String
  src : String
  deriving Repr, Inhabited

def ZoneRow.parse (f : Array String) : Option ZoneRow := do
  some { node := ← nat? f[0]!, start := ← nat? f[1]!, stop := ← nat? f[2]!, part := f[3]!, src := f[4]! }

/-- `history_remand.tsv` (round 10, `round10/DESIGN10.md` §4, D10-5, D10-7): the remand decision B of a history row
`id`, a quote `[b_start, b_end)` of B's text, a docket token, its spans `[bd_start, bd_end)` of B's text and
`[t_start, t_end)` of the target's text, a reason-case tie string and a span `[o_start, o_end)` of the order's text:
`id, b_node, b_start, b_end, docket, bd_start, bd_end, t_start, t_end, tie, o_start, o_end`. A non-numeric node or
offset makes the line a bad row; an empty docket or tie is a good line (it fails that test). -/
structure RemandRow where
  id : String
  b : Nat
  start : Nat
  stop : Nat
  docket : String
  bdStart : Nat
  bdStop : Nat
  tStart : Nat
  tStop : Nat
  tie : String
  oStart : Nat
  oStop : Nat
  deriving Repr, Inhabited

/-- `history_tbridge.tsv` (round 10, `round10/DESIGN10.md` §6, D10-8): the span `[t_start, t_end)` of the target T's
text that a `trialBridge` row quotes: `id, t_start, t_end`. A non-numeric offset makes the line a bad row. -/
structure TBridgeRow where
  id : String
  start : Nat
  stop : Nat
  deriving Repr, Inhabited

def TBridgeRow.parse (f : Array String) : Option TBridgeRow := do
  some { id := f[0]!, start := ← nat? f[1]!, stop := ← nat? f[2]! }

/-- `history_identity.tsv` (round 11, `round11/DESIGN11.md` §5.2, D11-5): an identity tie of the history row `id`:
`id, form, token, d_start, d_end, t_start, t_end` (`form`: docket, cite or date; `[d_start, d_end)` a span of the acting
node D's text, `[t_start, t_end)` of the target T's). A non-numeric offset or another form makes the line a bad row. -/
structure IdentityRow where
  id : String
  form : String
  token : String
  dStart : Nat
  dStop : Nat
  tStart : Nat
  tStop : Nat
  deriving Repr, Inhabited

def IdentityRow.parse (f : Array String) : Option IdentityRow := do
  if !(f[1]! == "docket" || f[1]! == "cite" || f[1]! == "date") then none
  else some { id := f[0]!, form := f[1]!, token := f[2]!, dStart := ← nat? f[3]!, dStop := ← nat? f[4]!,
              tStart := ← nat? f[5]!, tStop := ← nat? f[6]! }

def RemandRow.parse (f : Array String) : Option RemandRow := do
  some { id := f[0]!, b := ← nat? f[1]!, start := ← nat? f[2]!, stop := ← nat? f[3]!, docket := f[4]!,
         bdStart := ← nat? f[5]!, bdStop := ← nat? f[6]!, tStart := ← nat? f[7]!, tStop := ← nat? f[8]!,
         tie := f[9]!, oStart := ← nat? f[10]!, oStop := ← nat? f[11]! }

structure TreatmentRow where
  /-- the reader's row id (e.g. `t:<by>:<target>:<start>`) -/
  id : String
  by_ : Nat
  target : Nat
  date : Nat
  kind : String
  scope : String
  temporal : String
  explicit : Bool
  cert : Cert
  reader : String
  /-- parts per million -/
  confidence : Nat
  deriving Repr, Inhabited

/-- A 0/1 flag; anything else rejects the row (FB-L5: no silent default). -/
def flag01? (s : String) : Option Bool :=
  match s with
  | "1" => some true
  | "0" => some false
  | _ => none

def TreatmentRow.parse (f : Array String) : Option TreatmentRow := do
  some { id := f[0]!, by_ := ← nat? f[1]!, target := ← nat? f[2]!, date := ← nat? f[3]!, kind := f[4]!,
         scope := f[5]!, temporal := f[6]!, explicit := ← flag01? f[7]!, cert := ← Cert.parse f 8,
         reader := f[14]!, confidence := ← ppm? f[15]! }

/-- `treatment_witness.tsv` (round 4): the treatments row `id` is an implicit overruling stated by the later
decision `node` (W); `byEvidence` names the by-decision Y in W's text. -/
structure WitnessRow where
  id : String
  node : Nat
  byEvidence : String
  src : String
  deriving Repr, Inhabited

def WitnessRow.parse (f : Array String) : Option WitnessRow := do
  some { id := f[0]!, node := ← nat? f[1]!, byEvidence := f[2]!, src := f[3]! }

/-- `treatment_class.tsv` (round 5, DESIGN5 §1): the treatments row `id` claims a class (`recognised` on a witness
row, `operativeWords` on an explicit row); `fieldLimit` and `doctrine` are display text. The file's presence turns
round-5 output on. -/
structure ClassRow where
  id : String
  claim : String
  fieldLimit : String
  doctrine : String
  src : String
  deriving Repr, Inhabited

def ClassRow.parse (f : Array String) : Option ClassRow :=
  some { id := f[0]!, claim := f[1]!, fieldLimit := f[2]!, doctrine := f[3]!, src := f[4]! }

structure CertTextRow where
  textSha : String
  start0 : Nat
  stop0 : Nat
  window : String
  deriving Repr, Inhabited

def CertTextRow.parse (f : Array String) : Option CertTextRow := do
  some { textSha := f[0]!, start0 := ← nat? f[1]!, stop0 := ← nat? f[2]!, window := f[3]! }

/-! ## Holdings, issues, Marks -/

structure IssueRow where
  key : String
  label : String
  domain : String
  usc : String
  question : String
  src : String
  deriving Repr, Inhabited

def IssueRow.parse (f : Array String) : Option IssueRow :=
  some { key := f[0]!, label := f[1]!, domain := f[2]!, usc := f[3]!, question := f[4]!, src := f[5]! }

structure HoldingRow where
  id : String
  node : Nat
  issue : String
  proposition : String
  answer : String
  role : String
  cert : Cert
  reader : String
  confidence : Nat
  deriving Repr, Inhabited

def HoldingRow.parse (f : Array String) : Option HoldingRow := do
  some { id := f[0]!, node := ← nat? f[1]!, issue := f[2]!, proposition := f[3]!, answer := f[4]!, role := f[5]!,
         cert := ← Cert.parse f 6, reader := f[12]!, confidence := ← ppm? f[13]! }

structure MarksRow where
  node : Nat
  issue : String
  author : String
  proposition : String
  src : String
  tag : String
  deriving Repr, Inhabited

def MarksRow.parse (f : Array String) : Option MarksRow := do
  some { node := ← nat? f[0]!, issue := f[1]!, author := f[2]!, proposition := f[3]!, src := f[4]!, tag := f[5]! }

/-! ## Law changes -/

structure LawChangeRow where
  id : String
  law : String
  uscBlock : String
  enacted : Nat
  effective : Nat
  retroactiveTo : Nat
  src : String
  deriving Repr, Inhabited

def LawChangeRow.parse (f : Array String) : Option LawChangeRow := do
  some { id := f[0]!, law := f[1]!, uscBlock := f[2]!, enacted := ← nat? f[3]!, effective := ← nat? f[4]!,
         retroactiveTo := ← nat? f[5]!, src := f[6]! }

structure SupersessionRow where
  id : String
  target : Nat
  issue : String
  lawchange : String
  evidence : String
  score : Nat
  explicit : Bool
  src : String
  deriving Repr, Inhabited

def SupersessionRow.parse (f : Array String) : Option SupersessionRow := do
  some { id := f[0]!, target := ← nat? f[1]!, issue := f[2]!, lawchange := f[3]!, evidence := f[4]!,
         score := ← ppm? f[5]!, explicit := ← flag01? f[6]!, src := f[7]! }

/-! ## Everything but decisions -/

structure Tables where
  courts : Array CourtRow := #[]
  succession : Array SuccessionRow := #[]
  adoption : Array AdoptionRow := #[]
  rules : Array RuleRow := #[]
  history : Array HistoryRow := #[]
  /-- round 6: anchor lines of history rows (optional `history_anchor.tsv`; absent or empty = no anchored row) -/
  anchors : Array AnchorRow := #[]
  /-- round 7: joined lines (optional `joined.tsv`) and history claims (optional `history_claim.tsv`) -/
  joined : Array JoinedRow := #[]
  hclaims : Array HClaimRow := #[]
  /-- round 8: bridge lines of history rows (optional `history_bridge.tsv`) -/
  bridges : Array BridgeRow := #[]
  /-- round 9: the part zones of acting nodes' texts (optional `part_zone.tsv`) -/
  zones : Array ZoneRow := #[]
  /-- round 10: the remand lines of history rows (optional `history_remand.tsv`) -/
  remands : Array RemandRow := #[]
  /-- round 11 §5.2: the identity lines of history rows (optional `history_identity.tsv`) -/
  identities : Array IdentityRow := #[]
  /-- round 10 §6: T's quote spans of `trialBridge` rows (optional `history_tbridge.tsv`) -/
  tbridges : Array TBridgeRow := #[]
  treatments : Array TreatmentRow := #[]
  witness : Array WitnessRow := #[]
  /-- round 5: class claims; `round5` = the file exists (round-5 output mode) -/
  classes : Array ClassRow := #[]
  round5 : Bool := false
  certText : Array CertTextRow := #[]
  issues : Array IssueRow := #[]
  holdings : Array HoldingRow := #[]
  marks : Array MarksRow := #[]
  lawchanges : Array LawChangeRow := #[]
  supersessions : Array SupersessionRow := #[]
  problems : Array Problems := #[]
  deriving Inhabited

/-- Load every SCHEMA file except `decisions2.tsv` from `dir`. A missing file loads as empty (and is reported). -/
def loadTables (dir : System.FilePath) : IO Tables := do
  let mut ps : Array Problems := #[]
  let (courts, p) ← loadRows (dir / "courts2.tsv") 11 CourtRow.parse; ps := ps.push p
  let (succession, p) ← loadRows (dir / "succession.tsv") 6 SuccessionRow.parse; ps := ps.push p
  let (adoption, p) ← loadRows (dir / "adoption.tsv") 7 AdoptionRow.parse; ps := ps.push p
  let (rules, p) ← loadRows (dir / "system_rules.tsv") 7 RuleRow.parse; ps := ps.push p
  let (history, p) ← loadRows (dir / "history.tsv") 13 HistoryRow.parse; ps := ps.push p
  let (treatments, p) ← loadRows (dir / "treatments.tsv") 16 TreatmentRow.parse; ps := ps.push p
  let (certText, p) ← loadRows (dir / "cert_text.tsv") 4 CertTextRow.parse; ps := ps.push p
  -- optional (round 4): witness rows; absent = every treatments row is an old-format row
  let witFile := dir / "treatment_witness.tsv"
  let mut witness : Array WitnessRow := #[]
  if ← witFile.pathExists then
    let (ws, p) ← loadRows witFile 4 WitnessRow.parse
    witness := ws
    ps := ps.push p
  -- optional (round 5): class claims; absent = round-4 output, byte for byte
  let clsFile := dir / "treatment_class.tsv"
  let mut classes : Array ClassRow := #[]
  let round5 ← clsFile.pathExists
  if round5 then
    let (cs, p) ← loadRows clsFile 5 ClassRow.parse
    classes := cs
    ps := ps.push p
  -- optional (round 6): anchor lines of history rows; absent or empty = every history row is checked as before
  let ancFile := dir / "history_anchor.tsv"
  let mut anchors : Array AnchorRow := #[]
  if ← ancFile.pathExists then
    let (ars, p) ← loadRows ancFile 6 AnchorRow.parse
    anchors := ars
    ps := ps.push p
  -- optional (round 7): joined lines and history claims; absent or empty = round-6 output, byte for byte
  let jnFile := dir / "joined.tsv"
  let mut joined : Array JoinedRow := #[]
  if ← jnFile.pathExists then
    let (jrs, p) ← loadRows jnFile 9 JoinedRow.parse
    joined := jrs
    ps := ps.push p
  let hcFile := dir / "history_claim.tsv"
  let mut hclaims : Array HClaimRow := #[]
  if ← hcFile.pathExists then
    let (hrs, p) ← loadRows hcFile 3 HClaimRow.parse
    hclaims := hrs
    ps := ps.push p
  -- optional (round 8): bridge lines of history rows; absent or empty = round-7 output, byte for byte
  let brFile := dir / "history_bridge.tsv"
  let mut bridges : Array BridgeRow := #[]
  if ← brFile.pathExists then
    let (brs, p) ← loadRows brFile 6 BridgeRow.parse
    bridges := brs
    ps := ps.push p
  -- optional (round 9): part zones; absent or empty = round-8 output, byte for byte
  let zFile := dir / "part_zone.tsv"
  let mut zones : Array ZoneRow := #[]
  if ← zFile.pathExists then
    let (zrs, p) ← loadRows zFile 5 ZoneRow.parse
    zones := zrs
    ps := ps.push p
  -- optional (round 10): remand lines of history rows; absent or empty = round-9 output, byte for byte
  let rmFile := dir / "history_remand.tsv"
  let mut remands : Array RemandRow := #[]
  if ← rmFile.pathExists then
    let (rrs, p) ← loadRows rmFile 12 RemandRow.parse
    remands := rrs
    ps := ps.push p
  -- optional (round 10 §6): T's quote spans of trialBridge rows; absent or empty = no line
  let tbFile := dir / "history_tbridge.tsv"
  let mut tbridges : Array TBridgeRow := #[]
  if ← tbFile.pathExists then
    let (tbs, p) ← loadRows tbFile 3 TBridgeRow.parse
    tbridges := tbs
    ps := ps.push p
  -- optional (round 11 §5.2): identity lines of history rows; absent or empty = round-11 §5.1 output, byte for byte
  let idFile := dir / "history_identity.tsv"
  let mut identities : Array IdentityRow := #[]
  if ← idFile.pathExists then
    let (irs, p) ← loadRows idFile 7 IdentityRow.parse
    identities := irs
    ps := ps.push p
  -- the holdings agent ships its windows separately (D4, 2026-11-12); a missing file loads as empty
  let (certTextH, p) ← loadRows (dir / "holdings_cert_text.tsv") 4 CertTextRow.parse; ps := ps.push p
  let certText := certText ++ certTextH
  let (issues, p) ← loadRows (dir / "issues.tsv") 6 IssueRow.parse; ps := ps.push p
  let (holdings, p) ← loadRows (dir / "holdings.tsv") 14 HoldingRow.parse; ps := ps.push p
  let (marks, p) ← loadRows (dir / "marks.tsv") 6 MarksRow.parse; ps := ps.push p
  let (lawchanges, p) ← loadRows (dir / "lawchanges.tsv") 7 LawChangeRow.parse; ps := ps.push p
  let (supersessions, p) ← loadRows (dir / "supersessions.tsv") 8 SupersessionRow.parse; ps := ps.push p
  return { courts, succession, adoption, rules, history, anchors, joined, hclaims, bridges, zones, remands, tbridges, identities, treatments, witness, classes, round5,
           certText, issues, holdings, marks, lawchanges, supersessions, problems := ps }

/-- Nodes whose `text_sha` the certificate checks need: every by/target node of a treatment or history row and every
holding's node. -/
def Tables.certNodes (t : Tables) : HashMap Nat Unit := Id.run do
  let mut s : HashMap Nat Unit := {}
  for r in t.treatments do s := (s.insert r.by_ ()).insert r.target ()
  for r in t.witness do s := s.insert r.node ()
  for r in t.history do
    s := s.insert r.target ()
    if r.by_ ≥ 0 then s := s.insert r.by_.toNat ()
  for r in t.holdings do s := s.insert r.node ()
  -- round 8: the bridge texts W (their hash; none without `history_bridge.tsv`)
  for r in t.bridges do s := s.insert r.w ()
  -- round 10: the remand decisions B (their hash; none without `history_remand.tsv`)
  for r in t.remands do s := s.insert r.b ()
  return s

end CaseLaw2.Data
