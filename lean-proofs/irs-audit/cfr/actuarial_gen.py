import json, os
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit'))
A = json.load(open(H + '/cfr/actuarial.json'))['title-26-part-0020/sec-2031-0007.md']
B = A['B']; J = A['J']; K = A['K']
chunks = [B[i:i + 300] for i in range(0, len(B), 300)]
defs = ['def b%d : List (Nat × Nat × Nat) := [%s]' % (n, ', '.join('(%d, %d, %d)' % tuple(x) for x in ch)) for n, ch in enumerate(chunks)]
lean = '''/- 26 CFR 20.2031-7(d)(6): Table B (term-certain remainder factors), Table J and Table K (annuity adjustment factors),
   recomputed from the formulas of 20.2031-7(d)(2): remainder (1+i)^-n to six decimals; end-of-interval adjustment
   i / (p((1+i)^(1/p) - 1)) and beginning-of-interval i / (p(1 - (1+i)^(-1/p))) to four decimals. Rates r in tenths of
   a percent (i = r/1000); interval tests in exact Nat arithmetic (no roots). -/
@@DEFS@@
def tB : List (Nat × Nat × Nat) := @@BL@@
/-- v^n within half a unit of the sixth decimal of f -/
def bOk (r n f : Nat) : Bool := (2 * f - 1) * (1000 + r) ^ n ≤ 2000000 * 1000 ^ n && 2000000 * 1000 ^ n ≤ (2 * f + 1) * (1000 + r) ^ n
def ps : List Nat := [1, 2, 4, 12, 52]
/-- K = i/(p(R-1)) in [k-1/2, k+1/2] x 1e-4  ⇔  ((p(2k+1)+20r)/(p(2k+1)))^p ≤ 1+i ≤ ((p(2k-1)+20r)/(p(2k-1)))^p -/
def kOk (r p k : Nat) : Bool :=
  let a := p * (2 * k - 1); let b := p * (2 * k + 1)
  (1000 + r) * a ^ p ≤ 1000 * (a + 20 * r) ^ p && 1000 * (b + 20 * r) ^ p ≤ (1000 + r) * b ^ p
/-- J = i/(p(1-R^-1)) in [k-1/2, k+1/2] x 1e-4  ⇔  (b/(b-20r))^p ≤ 1+i ≤ (a/(a-20r))^p -/
def jOk (r p k : Nat) : Bool :=
  let a := p * (2 * k - 1); let b := p * (2 * k + 1)
  20 * r < a && (1000 + r) * (a - 20 * r) ^ p ≤ 1000 * a ^ p && 1000 * b ^ p ≤ (1000 + r) * (b - 20 * r) ^ p
def tJ : List (Nat × List Nat) := [@@J@@]
def tK : List (Nat × List Nat) := [@@K@@]
def main : IO Unit := do
  let badB := tB.filter (fun (r, n, f) => !bOk r n f)
  IO.println s!"TableB@{tB.length} factors@{badB.length} off@{badB.take 20}"
  let mut nj := 0
  let mut badJ : List (Nat × Nat × Nat) := []
  for (r, ks) in tJ do
    for (p, k) in ps.zip ks do
      nj := nj + 1
      if !(jOk r p k) then badJ := badJ ++ [(r, p, k)]
  IO.println s!"TableJ@{nj} factors@{badJ.length} off@{badJ.take 20}"
  let mut nk := 0
  let mut badK : List (Nat × Nat × Nat) := []
  for (r, ks) in tK do
    for (p, k) in ps.zip ks do
      nk := nk + 1
      if !(kOk r p k) then badK := badK ++ [(r, p, k)]
  IO.println s!"TableK@{nk} factors@{badK.length} off@{badK.take 20}"
'''
lean = lean.replace('@@DEFS@@', '\n'.join(defs)).replace('@@BL@@', ' ++ '.join('b%d' % n for n in range(len(chunks))))
lean = lean.replace('@@J@@', ', '.join('(%d, [%s])' % (r, ', '.join(map(str, v))) for r, v in J)).replace('@@K@@', ', '.join('(%d, [%s])' % (r, ', '.join(map(str, v))) for r, v in K))
open(H + '/lean/Audit/Actuarial.lean', 'w').write(lean)
print('ok', len(B), len(J), len(K))
