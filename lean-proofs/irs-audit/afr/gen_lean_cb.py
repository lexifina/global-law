import json, os
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit'))
d = json.load(open(H + '/afr/afr_cb.json'))
def bp(x):
    if x is None: return None
    a, _, b = x.partition('.')
    if len(b) > 2: return None
    b = (b + '00')[:2]
    return int(a or 0) * 100 + int(b)
def tenths(x):
    if x is None: return None
    a, _, b = x.partition('.')
    if len(b) == 2 and b[1] == '0': b = b[0]
    if len(b) != 1: return None
    return int(a or 0) * 10 + int(b)
def opt(v): return 'none' if v is None else f'some {v}'
def row(t):
    v = [bp(x) for x in t]
    if None in v: return None
    return '⟨%d, %d, %d, %d⟩' % tuple(v)
lines = []
seen = set()
for r in d:
    key = (r['year'], r['month'])
    t1 = [row(t) for t in r['table1']]; t2 = [row(t) for t in r['table2']]
    if None in t1 or None in t2: t1 = [x for x in t1 if x]; t2 = [x for x in t2 if x]
    lines.append('  { item := "%s", y := %d, mo := %d, t1 := [%s], t2 := [%s], adjLt := %s, ltEx := %s, l70 := %s, l30 := %s, r7520 := %s, deemed := %s }' % (
        r['item'], r['year'], r['month'], ', '.join(t1), ', '.join(t2), opt(bp(r['adj_lt'])), opt(bp(r['lt_exempt'])),
        opt(bp(r['lihtc70'])), opt(bp(r['lihtc30'])), opt(tenths(r['r7520'])), opt(tenths(r['deemed']))))
main = r'''
open AFR

@@DATA@@

def findR (y m : Nat) : Option Ruling := rulings.find? (fun r => r.y == y && r.mo == m)
def back (y m k : Nat) : Nat × Nat := let t := y * 12 + (m - 1) - k; (t / 12, t % 12 + 1)
def b2s (b : Bool) : String := if b then "pass" else "FAIL"
def out (r : Ruling) (chk : String) (i : Nat) (ok : Bool) (det : String) : IO Unit :=
  IO.println s!"{r.item}\t{r.y}-{r.mo}\t{chk}\t{i}\t{b2s ok}\t{det}"

def pcts : List Nat := [100, 110, 120, 130, 100, 110, 120, 130, 150, 175, 100, 110, 120, 130]
def bases : List Nat := [0, 0, 0, 0, 4, 4, 4, 4, 4, 4, 10, 10, 10, 10]

def main : IO Unit := do
  for r in rulings do
    let rows := r.t1 ++ r.t2
    let mut i := 0
    for row in rows do
      out r "conv" i (conv row) s!"{row.a} {row.s} {row.q} {row.m}"
      i := i + 1
    if r.t1.length == 14 then
      let mut j := 0
      for row in r.t1 do
        let p := pcts.getD j 100
        if p != 100 then
          let b := r.t1.getD (bases.getD j 0) row
          out r "mult_semi" j (mult p b.s row.s) s!"{p}% of semi {b.s}: printed semi {row.s}"
          out r "mult_annual" j (mult p b.a row.a) s!"{p}% of annual {b.a}: printed annual {row.a}"
        j := j + 1
      let mid := r.t1.getD 4 ⟨0,0,0,0⟩
      let lng := r.t1.getD 10 ⟨0,0,0,0⟩
      match r.r7520 with
      | some t => do
          out r "s7520" 0 (s7520 mid.a t) s!"mid annual {mid.a} -> printed {t}"
          out r "s7520_semi" 0 (s7520 mid.s t) s!"mid semi {mid.s} -> printed {t}"
          let m120 := r.t1.getD 6 ⟨0,0,0,0⟩
          out r "s7520_row120" 0 (t % 2 == 0 && 10 * t ≤ m120.a + 10 && m120.a ≤ 10 * t + 10) s!"printed 120% mid annual {m120.a} -> printed {t}"
      | none => pure ()
      match r.l70, r.l30 with
      | some p7, some p3 => do
          out r "s42_70" 0 (s42 7 mid.a lng.a p7) s!"mid {mid.a} long {lng.a} -> printed {p7}"
          out r "s42_30" 0 (s42 3 mid.a lng.a p3) s!"mid {mid.a} long {lng.a} -> printed {p3}"
      | _, _ => pure ()
    if r.t1.length == 9 || r.t1.length == 11 then
      let pc : List Nat := if r.t1.length == 9 then [100, 110, 120, 100, 110, 120, 100, 110, 120] else [100, 110, 120, 100, 110, 120, 150, 175, 100, 110, 120]
      let bs : List Nat := if r.t1.length == 9 then [0, 0, 0, 3, 3, 3, 6, 6, 6] else [0, 0, 0, 3, 3, 3, 3, 3, 8, 8, 8]
      let mut j := 0
      for row in r.t1 do
        let p := pc.getD j 100
        if p != 100 then
          let b := r.t1.getD (bs.getD j 0) row
          out r "mult_semi" j (mult p b.s row.s) s!"{p}% of semi {b.s}: printed semi {row.s}"
          out r "mult_annual" j (mult p b.a row.a) s!"{p}% of annual {b.a}: printed annual {row.a}"
        j := j + 1
      let mid := r.t1.getD 3 ⟨0,0,0,0⟩
      let lng := r.t1.getD (if r.t1.length == 9 then 6 else 8) ⟨0,0,0,0⟩
      match r.l70, r.l30 with
      | some p7, some p3 => do
          out r "s42_70" 0 (s42 7 mid.a lng.a p7) s!"mid {mid.a} long {lng.a} -> printed {p7}"
          out r "s42_30" 0 (s42 3 mid.a lng.a p3) s!"mid {mid.a} long {lng.a} -> printed {p3}"
      | _, _ => pure ()
    if r.t2.length == 3 then
      let lt := r.t2.getD 2 ⟨0,0,0,0⟩
      match r.adjLt with
      | some v => out r "s382_adj_eq_table2" 0 (v == lt.a) s!"table3 {v} table2 annual {lt.a} semi {lt.s}"
      | none => pure ()
    match r.ltEx, r.adjLt with
    | some e, some _ => do
        let ms := [0, 1, 2].map (fun k => back r.y r.mo k)
        let vs := ms.map (fun (yy, mm) => (findR yy mm).bind (fun x => x.adjLt))
        if vs.all Option.isSome then
          let mx := (vs.map (fun o => o.getD 0)).foldl max 0
          out r "s382_max3" 0 (e == mx) s!"printed {e}; adj LT rates {vs.map (fun o => o.getD 0)}"
        else out r "s382_max3" 0 true s!"NA: missing month"
    | _, _ => pure ()
    match r.deemed with
    | some dd => do
        let yrs := [r.y - 3, r.y - 2, r.y - 1]
        let sums := yrs.map (fun yy => (List.range 12).map (fun k => (findR yy (k + 1)).bind (fun x => x.r7520)))
        if sums.all (fun l => l.all Option.isSome) then
          let tot := sums.map (fun l => (l.map (fun o => o.getD 0)).foldl (· + ·) 0)
          let best := tot.foldl max 0
          out r "s642" 0 (s642 best dd) s!"printed {dd}; yearly sums of monthly 7520 rates (tenths) {tot}"
        else out r "s642" 0 true s!"NA: missing months"
    | none => pure ()
'''
src = open(H + '/lean/afr/Checker.lean').read()
NL = chr(10)
byy = {}
for l, r in zip(lines, d): byy.setdefault(r['year'], []).append(l)
chunks = []
for y in sorted(byy):
    chunks.append('def r%d : List Ruling := [' % y + NL + (',' + NL).join(byy[y]) + NL + ']')
chunks.append('def rulings : List Ruling := ' + ' ++ '.join('r%d' % y for y in sorted(byy)))
open(H + '/lean/afr/RunCB.lean', 'w').write(src + main.replace('@@DATA@@', (NL + NL).join(chunks)))
print(len(lines))
