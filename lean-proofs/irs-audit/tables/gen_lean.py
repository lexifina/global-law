import json, os
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit'))
T = json.load(open(H + '/tables/tables.json'))
def rt(r): a, _, b = r.partition('.'); return int(a) * 10 + int((b + '0')[:1])
def cents(b): a, _, c = b.partition('.'); return int(a) * 100 + int((c + '00')[:2])
defs, names = [], []
for y, d in sorted(T.items()):
    if not d['sched'] or len(d['sched']) < 4: continue
    sch = []
    for st in ('X', 'Y-1', 'Y-2', 'Z'):
        s = d['sched'][st]
        sch.append('[%s]' % ', '.join('(%d, %d, %d)' % (o, rt(r), cents(b)) for o, b, r in s))
    rr = d['rows']; parts = []
    for k in range(0, len(rr), 100):
        defs.append('def r%s_%d : List (Nat × Nat × Nat × Nat × Nat × Nat) := [%s]' % (y, k // 100, ', '.join('(%d, %d, %d, %d, %d, %d)' % tuple(r) for r in rr[k:k + 100])))
        parts.append('r%s_%d' % (y, k // 100))
    defs.append('def y%s : Year := { y := %s, sched := [%s], rows := %s }' % (y, y, ', '.join(sch), ' ++ '.join(parts)))
    names.append('y' + y)
lean = '''/-
  Form 1040 Tax Table (taxable income under $100,000) against the Tax Rate Schedules of the same year, 1995-2024.
  §3(a) lets the Secretary prescribe tables; the instructions state each entry is the tax, by the schedule, on the
  midpoint of the row's income range (rounded to the dollar). The schedules use the statutory rates of §1 for the year
  (thresholds from that year's revenue procedure). Each schedule row: (over, rate in tenths of a percent, printed base
  tax in cents). Each table row: (at least, less than, single, joint, separate, head of household).
-/
structure Year where
  y : Nat
  sched : List (List (Nat × Nat × Nat))
  rows : List (Nat × Nat × Nat × Nat × Nat × Nat)

/-- tax ×2000 (units of 1/2000 dollar) on income given in half-dollars `x2`. -/
def tax2000 (s : List (Nat × Nat × Nat)) (x2 : Nat) : Nat :=
  let rec go : List (Nat × Nat × Nat) → Nat
    | [] => 0
    | [(o, r, _)] => r * (x2 - 2 * o)
    | (o, r, _) :: (o2, r2, b2) :: t => r * (min x2 (2 * o2) - min x2 (2 * o)) + go ((o2, r2, b2) :: t)
  go s
/-- printed base amounts equal the tax at each threshold (×1000 to stay exact: cents × 10 = rate_tenths × dollars) -/
def baseOk (s : List (Nat × Nat × Nat)) : List (Nat × Nat × Nat) :=
  s.filter (fun (o, _, b) => tax2000 s (2 * o) != 20 * b)   -- tax2000 at 2o = rate·2o... = 2000·tax; 20·cents = 2000·tax
def roundHalfUp (t2000 : Nat) : Nat := (t2000 + 1000) / 2000

@@DEFS@@

def years : List Year := [@@NAMES@@]

def main : IO Unit := do
  for yr in years do
    let mut bad : List String := []
    let mut n := 0
    for (lo, hi, a, b, c, d) in yr.rows do
      let m2 := lo + hi
      let vals := [a, b, c, d]
      let mut k := 0
      for s in yr.sched do
        let want := roundHalfUp (tax2000 s m2)
        let got := vals.getD k 0
        n := n + 1
        if want != got then bad := bad ++ [s!"{lo}-{hi} col{k} printed {got} schedule {want}"]
        k := k + 1
    let sb := yr.sched.map baseOk
    IO.println s!"{yr.y}\t{if bad.isEmpty then "pass" else "FAIL"}\t{n} entries, {bad.length} differ\t{bad.take 12}\tschedule base mismatches {sb.map List.length}"
'''
open(H + '/lean/Audit/TaxTables.lean', 'w').write(lean.replace('@@DEFS@@', '\n\n'.join(defs)).replace('@@NAMES@@', ', '.join(names)).replace(chr(9), chr(92) + 't'))
print(len(names), 'years')
