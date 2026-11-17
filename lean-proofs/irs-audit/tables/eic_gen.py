import json, os
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit'))
E = json.load(open(H + '/tables/eic.json'))
CP = {0: 765, 1: 3400, 2: 4000, 3: 4500}; PP = {0: 765, 1: 1598, 2: 2106, 3: 2106}
IDX = {1: 0, 2: 1, 3: 2, 0: 3}
defs, names = [], []
for y, d in sorted(E.items()):
    p = d['params']
    if not p or len(d["rows"]) < 900: continue
    cols = []
    for c in range(8):
        k = c % 4; j = c >= 4; i = IDX[k]
        if y == '2021' and k == 0: cols.append('none'); continue   # Pub. L. 117-2 changed the no-child credit for 2021
        thr = p['thr_j'][i] if j else p['thr_s'][i]; co = p['co_j'][i] if j else p['co_s'][i]
        cols.append('some (%d, %d, %d, %d, %d, %d)' % (CP[k], PP[k], p['eia'][i], thr, p['mx'][i], co))
    rows = d['rows']; parts = []
    for n in range(0, len(rows), 100):
        parts.append('e%s_%d' % (y, n // 100))
        defs.append('def e%s_%d : List (Int × Int × List Int) := [%s]' % (y, n // 100, ', '.join('(%d, %d, [%s])' % (lo, hi, ', '.join('-1' if v is None else str(v) for v in vs)) for lo, hi, vs in rows[n:n + 100])))
    defs.append('def y%s : EYear := { y := %s, cols := [%s], rows := %s }' % (y, y, ', '.join(cols), ' ++ '.join(parts)))
    names.append('y' + y)
lean = '''/- EIC Table (Form 1040 instructions) 2010-2023 against §32(a)-(b): statutory credit and phase-out percentages, the year's
   Rev. Proc. amounts, and the table rule of the earlier 2025 proof (TaxCode.Individual.D.eicTab): credit at the band
   midpoint, published maximum credit, a band containing a kink shows the maximum, zero from the completed phase-out. -/
def eicTab (cp pp eia thr mx co : Int) (x : Int) : Int :=
  if x ≤ 0 ∨ co ≤ x then 0 else
  let a := x / 50 * 50
  let b := min (a + 50) co
  if (a < eia ∧ eia < b) ∨ (a < thr ∧ thr < b) then mx else
  let m := a + b
  let v := max 0 (min (cp * m) (20000 * mx - pp * max 0 (m - 2 * thr)))
  (v + 10000) / 20000
/-- the same with the statute's exact maximum (credit percentage x earned income amount) in the phase-out -/
def eicTabExact (cp pp eia thr mx co : Int) (x : Int) : Int :=
  if x ≤ 0 ∨ co ≤ x then 0 else
  let a := x / 50 * 50
  let b := min (a + 50) co
  if (a < eia ∧ eia < b) ∨ (a < thr ∧ thr < b) then mx else
  let m := a + b
  let v := max 0 (min (cp * m) (2 * cp * eia - pp * max 0 (m - 2 * thr)))
  (v + 10000) / 20000
structure EYear where
  y : Nat
  cols : List (Option (Int × Int × Int × Int × Int × Int))
  rows : List (Int × Int × List Int)
@@DEFS@@
def years : List EYear := [@@NAMES@@]
def main : IO Unit := do
  for e in years do
    let mut n := 0
    let mut bad : List String := []
    for (lo, hi, vs) in e.rows do
      let mut c := 0
      for v in vs do
        match e.cols.getD c none with
        | some (cp, pp, eia, thr, mx, co) =>
          if v != -1 then
            n := n + 1
            let w1 := eicTab cp pp eia thr mx co lo
            let w2 := eicTab cp pp eia thr mx co (hi - 1)
            let x1 := eicTabExact cp pp eia thr mx co lo
            let x2 := eicTabExact cp pp eia thr mx co (hi - 1)
            if (v != w1 || v != w2) && (v != x1 || v != x2) then bad := bad ++ [s!"{lo}-{hi} col{c} printed {v} rule {w1}/{w2} exact {x1}/{x2}"]
        | none => pure ()
        c := c + 1
    IO.println s!"{e.y}@{if bad.isEmpty then "pass" else "FAIL"}@{n} cells, {bad.length} differ@{bad.take 10}"
'''
open(H + '/lean/Audit/EicTables.lean', 'w').write(lean.replace('@@DEFS@@', '\n'.join(defs)).replace('@@NAMES@@', ', '.join(names)))
print(names)
