import json, os
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit'))
q = json.load(open(H + '/q6621/q.json')); afr = json.load(open(H + '/afr/afr.json'))
def bp(x):
    a, _, b = x.partition('.'); return int(a or 0) * 100 + int((b + '00')[:2])
def tenth(x):
    a, _, b = x.partition('.'); return int(a or 0) * 10 + int((b + '0')[:1])
NL = chr(10)
st = {}
for r in afr:
    if r['table1']:
        try: st[(r['year'], r['month'])] = [bp(v) for v in r['table1'][0]]
        except Exception: pass
afrl = ',\n'.join('  (%d, %d, ⟨%d, %d, %d, %d⟩)' % (y, m, *v) for (y, m), v in sorted(st.items()))
recs, tabs = [], []
for i, r in enumerate(q):
    if 'fst' not in r: continue
    def o(k): return 'some %d' % tenth(r[k]) if r.get(k) else 'none'
    qq = r.get('quarter', [0, 0])
    recs.append('  { item := "%s", fy := %d, fm := %d, qy := %d, qm := %d, fst := %d, over := %s, overCorp := %s, under := %s, over10k := %s, large := %s }' % (
        r['item'], r['fst_month'][0], r['fst_month'][1], qq[0], qq[1], tenth(r['fst']), o('over'), o('over_corp'), o('under'), o('over_10k'), o('large_corp')))
for r in q:
    for t in r['tables']:
        rows = ', '.join('(%d, %s)' % (d, int(v.replace('.', ''))) for d, v in t['rows'])
        tabs.append('def tab%d : FTable := { item := "%s", ydays := %d, rt := %d, rows := [%s] }' % (len(tabs), r['item'], t['year_days'], tenth(t['rate']), rows))
src = open(H + '/lean/afr/Checker.lean').read()
body = '''
namespace Q6621
open AFR

/-- one AFR short-term row per (year, month) -/
def afrShort : List (Nat × Nat × Row) := [
@@AFR@@
]

structure QR where
  item : String
  fy : Nat
  fm : Nat
  qy : Nat
  qm : Nat
  fst : Nat            -- tenths of a percent
  over : Option Nat
  overCorp : Option Nat
  under : Option Nat
  over10k : Option Nat
  large : Option Nat

def qrs : List QR := [
@@Q@@
]

structure FTable where
  item : String
  ydays : Nat
  rt : Nat                       -- rate, tenths of a percent
  rows : List (Nat × Nat)        -- (days, factor in units of 1e-9)

@@T@@

def tables : List FTable := [@@TL@@]

/-- effective-yield interval of a printed AFR row (each bound as num/den) -/
def yieldLo (r : Row) : Nat × Nat :=
  [(1, r.a), (2, r.s), (4, r.q), (12, r.m)].foldl (fun acc (k, v) =>
    let g := growth k (2 * v - 1); if acc.1 * g.2 < g.1 * acc.2 then g else acc) (1, 1)
def yieldHi (r : Row) : Nat × Nat :=
  [(1, r.a), (2, r.s), (4, r.q), (12, r.m)].foldl (fun acc (k, v) =>
    let g := growth k (2 * v + 1); if g.1 * acc.2 < acc.1 * g.2 then g else acc) (10, 1)

/-- (1 + h/73000)^365: daily compounding of the annual rate h/200 percent (h = twice the percent) -/
def daily (h : Nat) : Nat × Nat := ((73000 + h) ^ 365, 73000 ^ 365)

/-- §6621(b)(3): X is the rounding (ties up) of the daily-compounded rate d for every / some yield in [lo, hi].
    d ≥ X - 1/2  ⇔  Y ≥ daily(2X - 1);  d < X + 1/2  ⇔  Y < daily(2X + 1).  X in whole percent. -/
def roundAll (lo hi : Nat × Nat) (X : Nat) : Bool :=
  let a := daily (2 * X - 1); let b := daily (2 * X + 1)
  (X == 0 || a.1 * lo.2 ≤ lo.1 * a.2) && hi.1 * b.2 < b.1 * hi.2
def roundSome (lo hi : Nat × Nat) (X : Nat) : Bool :=
  let a := daily (2 * X - 1); let b := daily (2 * X + 1)
  (X == 0 || a.1 * hi.2 ≤ hi.1 * a.2) && lo.1 * b.2 < b.1 * lo.2

/-- the factor (1 + rt/(1000·ydays))^n − 1, printed to 9 decimals as f -/
def factorOk (ydays rt n f : Nat) : Bool :=
  let den := (1000 * ydays) ^ n
  let num := (1000 * ydays + rt) ^ n
  (2 * f - 1) * den ≤ 2000000000 * (num - den) && 2000000000 * (num - den) ≤ (2 * f + 1) * den

def statAdd (qy : Nat) : Nat × Nat × Nat × Nat × Nat :=
  -- (over noncorporate, over corporate, under, over >$10k corporate, large corporate) in tenths; Pub. L. 105-206
  -- §3301 (noncorporate overpayments +3 from the quarter beginning Jan. 1, 1999)
  if qy ≥ 1999 then (30, 20, 30, 5, 50) else (20, 20, 30, 5, 50)

end Q6621

open Q6621 in
def main : IO Unit := do
  for r in qrs do
    let ym := if r.fm == 12 then (r.fy + 1, 1) else (r.fy, r.fm + 1)
    match afrShort.find? (fun x => x.1 == ym.1 && x.2.1 == ym.2) with
    | none => IO.println s!"{r.item}\tfst\tNA\tno AFR ruling for {ym.1}-{ym.2}"
    | some (_, _, row) =>
      let X := r.fst / 10
      let lo := yieldLo row; let hi := yieldHi row
      let res := if r.fst % 10 != 0 then "FAIL" else if roundAll lo hi X then "pass" else if roundSome lo hi X then "ambiguous" else "FAIL"
      IO.println s!"{r.item}\tfst\t{res}\tdetermined {r.fy}-{r.fm}, AFR for {ym.1}-{ym.2} short {row.a}/{row.s}/{row.q}/{row.m} bp, printed {X}%"
    let (o, oc, u, o10, lg) := statAdd r.qy
    let chk := fun (nm : String) (v : Option Nat) (add : Nat) => match v with
      | some x => IO.println s!"{r.item}\t{nm}\t{if x == r.fst + add then "pass" else "FAIL"}\tquarter {r.qy}-{r.qm}: printed {x} tenths, statute {r.fst + add}"
      | none => pure ()
    chk "over" r.over o; chk "over_corp" r.overCorp oc; chk "under" r.under u; chk "over_10k" r.over10k o10; chk "large_corp" r.large lg
  for t in tables do
    let bad := t.rows.filter (fun (n, f) => !factorOk t.ydays t.rt n f)
    IO.println s!"{t.item}\tfactors_{t.ydays}_{t.rt}\t{if bad.isEmpty then "pass" else "FAIL"}\t{t.rows.length} rows, {bad.length} off: {bad.take 5}"
'''
body = body.replace('@@AFR@@', afrl).replace('@@Q@@', ',\n'.join(recs)).replace('@@T@@', '\n'.join(tabs)).replace('@@TL@@', ', '.join('tab%d' % i for i in range(len(tabs))))
body = body.replace('\\t', '\t')
open(H + '/lean/q6621/Run.lean', 'w').write(src + body)
print(len(recs), len(tabs))
