import Std.Data.HashMap

/-!
# caselaw-lean-2: TSV reading (design-neutral infrastructure)

Streaming line readers and field parsers for the interchange files of `caselaw-lean-2/SCHEMA.md`: UTF-8, LF,
tab-separated, no header. Fuzzed against the Python reference (`tools/caselaw2/fuzz/`, caselaw-lean-2/FUZZ.md). Lines are read one at a time (no whole-file strings), so the 6.9M-row `decisions2.tsv`
and the 48M citation edges stream in constant memory per line.

A malformed line is never fatal: loaders count it and keep the first few in a `Problems` log, which the runner
writes out.
-/

namespace CaseLaw2.Tsv

/-- Strip a trailing `\n` and every trailing `\r` (so `\r\n` and a stray `\r\r\n` both end a line cleanly; the
reference does the same; fuzz). -/
def chomp (s : String) : String :=
  let s := (s.dropSuffix "\n").toString
  String.ofList ((s.toList.reverse.dropWhile (· == '\r')).reverse)

@[inline] def fields (l : String) : Array String := (l.splitOn "\t").toArray

/-- A SCHEMA integer field: ASCII digits only, nonempty. No sign, spaces, `_` separators or other scripts' digits
(`String.toNat?` alone accepts `1_000`; fuzz). -/
@[inline] def isDigits (s : String) : Bool := !s.isEmpty && s.all (fun c => '0' ≤ c && c ≤ '9')

@[inline] def nat? (s : String) : Option Nat := if isDigits s then s.toNat? else none

@[inline] def natD (s : String) (d : Nat := 0) : Nat := (nat? s).getD d

/-- Integers such as `-1` (unknown node) and negative system ids (court-level rules): an optional `-`, then digits. -/
@[inline] def int? (s : String) : Option Int :=
  if s.startsWith "-" then (nat? (s.drop 1).toString).map (fun n => -(n : Int)) else (nat? s).map Int.ofNat

/-- Decimal confidence/score in [0,1] as parts-per-million (`0.99` ↦ 990000); unparseable ↦ none. -/
def ppm? (s : String) : Option Nat :=
  match s.splitOn "." with
  | [a] => (nat? a).map (· * 1000000)
  | [a, b] =>
    if a.isEmpty && b.isEmpty then none
    else if !(a.isEmpty || isDigits a) || !(b.isEmpty || isDigits b) then none
    else
      let b6 := (b ++ "000000").take 6
      some ((natD a) * 1000000 + (natD b6.toString))
  | _ => none

/-- Problems found while loading one file. -/
structure Problems where
  file : String
  rows : Nat := 0
  bad : Nat := 0
  samples : Array String := #[]
  deriving Inhabited

def Problems.note (p : Problems) (lineNo : Nat) (why : String) (l : String) : Problems :=
  { p with bad := p.bad + 1,
           samples := if p.samples.size < 5 then p.samples.push s!"{p.file}:{lineNo}: {why}: {(l.take 160).toString}"
                      else p.samples }

/-- What `foldLines` passes for a line that is not valid UTF-8: one field that no row parser accepts, so the line
is rejected and logged (never decoded lossily; fuzz). -/
def invalidUtf8Line : String := "\u0000<invalid UTF-8>"

/-- One raw line (without its `\n`): drop every trailing `\r` and, on the first line, a UTF-8 byte-order mark. -/
def decodeLine (bs : ByteArray) (first : Bool) : String := Id.run do
  let mut e := bs.size
  while e > 0 && bs.get! (e - 1) == 13 do e := e - 1
  let s0 := if first && e ≥ 3 && bs.get! 0 == 0xEF && bs.get! 1 == 0xBB && bs.get! 2 == 0xBF then 3 else 0
  match String.fromUTF8? (bs.extract s0 e) with
  | some s => s
  | none => invalidUtf8Line

/-- Fold over the non-empty lines of a file, streaming in 1 MiB chunks: lines end at `\n` only (a lone `\r` is
data), trailing `\r`s and a leading BOM are dropped, and a line that is not valid UTF-8 arrives as
`invalidUtf8Line`. Missing file ↦ the initial state and `false`. -/
partial def foldLines {α} (path : System.FilePath) (init : α) (f : α → Nat → String → α) : IO (α × Bool) := do
  if !(← path.pathExists) then return (init, false)
  let h ← IO.FS.Handle.mk path .read
  let step (acc : α) (n : Nat) (bs : ByteArray) : α :=
    let l := decodeLine bs (n == 0)
    if l.isEmpty then acc else f acc (n + 1) l
  let rec go (acc : α) (n : Nat) (carry : ByteArray) : IO α := do
    let chunk ← h.read 1048576
    if chunk.isEmpty then
      return (if carry.isEmpty then acc else step acc n carry)
    let buf := carry ++ chunk
    let mut acc := acc
    let mut n := n
    let mut s := 0
    for i in [carry.size:buf.size] do
      if buf.get! i == 10 then
        acc := step acc n (buf.extract s i)
        n := n + 1
        s := i + 1
    go acc n (buf.extract s buf.size)
  return (← go init 0 ByteArray.empty, true)

/-- Load a file of rows with a row parser. A row must have exactly `nFields` fields (SCHEMA fixes every file's
columns; a missing or extra field, e.g. a tab inside a quote, would shift the columns: fuzz) and be valid UTF-8;
other rows are logged. -/
def loadRows {α} (path : System.FilePath) (nFields : Nat) (parse : Array String → Option α) :
    IO (Array α × Problems) := do
  let p0 : Problems := { file := path.fileName.getD path.toString }
  let ((rows, p), _) ← foldLines path ((#[] : Array α), p0) fun (acc, p) n l =>
    let f := fields l
    let p := { p with rows := p.rows + 1 }
    if l == invalidUtf8Line then (acc, p.note n "invalid UTF-8" l)
    else if f.size != nFields then (acc, p.note n s!"{f.size} fields ≠ {nFields}" l)
    else match parse f with
      | some r => (acc.push r, p)
      | none => (acc, p.note n "unparseable" l)
  return (rows, p)

end CaseLaw2.Tsv
