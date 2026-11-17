import json, os
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit'))
pub = json.load(open(H + '/cola/published.json'))
SPEC = [('415b', '§415(b)(1)(A) $160,000, base quarter Jul-Sep 2001, increase down to $5,000 (§415(d)(1),(3)(A),(4)(A))', 160000, 2001, 5000, 2002),
 ('415c', '§415(c)(1)(A) $40,000, base Q3 2001, down to $1,000 (§415(d)(3)(D),(4)(B))', 40000, 2001, 1000, 2002),
 ('402g', '§402(g)(1)(B) $15,000, base Q3 2005, down to $500 (§402(g)(4))', 15000, 2005, 500, 2007),
 ('401a17', '§401(a)(17) $200,000, base Q3 2001, down to $5,000 (§401(a)(17)(B))', 200000, 2001, 5000, 2002),
 ('416i', '§416(i)(1)(A)(i) $130,000, base Q3 2001, down to $5,000', 130000, 2001, 5000, 2003),
 ('414q', '§414(q)(1)(B) $80,000, base quarter beginning Oct 1 1996? (tested: Q3 1996), down to $5,000', 80000, 1996, 5000, 1998),
 ('414v', '§414(v)(2)(C) $5,000, base Q3 2005, down to $500', 5000, 2005, 500, 2007),
 ('408p', '§408(p)(2)(E) $10,000, base Q3 2004, down to $500', 10000, 2004, 500, 2006)]
lines = []
for k, cite, base, by, m, first in SPEC:
    for y in sorted(pub, key=int):
        if int(y) >= first and k in pub[y]:
            lines.append('  ⟨"%s", %s, %d, %d, %d, %d, %d⟩' % (k, y, base, by, m, first, pub[y][k][0]))
lean = '''import Audit.Formula
import Audit.CPI
open TaxCode.Indexing
/-- CPI-U sum for July-September of year y (the base "calendar quarter beginning July 1"). -/
def q3 (s : Series) (y : Nat) : Nat := (s.get? y 7).getD 0 + (s.get? y 8).getD 0 + (s.get? y 9).getD 0
def adj (base by_ cy m : Nat) : Nat := adjustND base (q3 cpiu (cy - 1)) (q3 cpiu by_) (.incDown m)
/-- Reg. 1.415(d)-1: a limit is never reduced; statute value = the largest adjusted amount of any year from `first`. -/
def ratchet (base by_ first cy m : Nat) : Nat := ((List.range (cy + 1 - first)).map (fun k => adj base by_ (first + k) m)).foldl max base
structure It where
  key : String
  y : Nat
  base : Nat
  by_ : Nat
  m : Nat
  first : Nat
  pub : Nat
def its : List It := [
@@
]
def main : IO Unit := do
  for i in its do
    let s := ratchet i.base i.by_ i.first i.y i.m
    let raw := adj i.base i.by_ i.y i.m
    IO.println s!"{i.key}\t{i.y}\t{if s == i.pub then "pass" else "FAIL"}\tstatute {s} (this year's formula {raw}) published {i.pub}"
'''
open(H + '/lean/Audit/ColaRun.lean', 'w').write(lean.replace('@@', ',\n'.join(lines)).replace('\\t', '\t'))
print(len(lines))
