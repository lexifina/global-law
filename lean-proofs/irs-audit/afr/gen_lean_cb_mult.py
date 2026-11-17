"""Labelled multiples check for the CB AFR tables: each p% row (110/120/130/150/175) against the AFR row of the same term
(semiannual, s1274(b)(2)(B) and the ruling's own statement), rows identified by their printed label, not position."""
import json, os
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit')); d = json.load(open(H + '/afr/afr_cb.json'))
def bp(x):
    a, _, b = x.partition('.'); return int(a or 0) * 100 + int((b + '00')[:2])
L = []
for r in d:
    base = {}
    for (term, pct), row in zip(r.get('labels', []), r['table1']):
        if term is None: continue
        if pct == 100:
            if term not in base: base[term] = row
            continue
        elif term in base:
            L.append('("%s", %d, %d, "%s", %d, %d, %d, %d, %d)' % (r['item'], r['year'], r['month'], term, pct, bp(base[term][1]), bp(row[1]), bp(base[term][0]), bp(row[0])))
S42 = []
for r in d:
    base = {}
    for (t, pc), row in zip(r.get('labels', []), r['table1']):
        if pc == 100 and t and t not in base: base[t] = row
    if len(r['table1']) < 6: continue
    if 'mid' in base and 'long' in base and r['lihtc70'] and r['lihtc30']:
        S42.append('("%s", %d, %d, %d, %d, %d, %d)' % (r['item'], r['year'], r['month'], bp(base['mid'][0]), bp(base['long'][0]), bp(r['lihtc70']), bp(r['lihtc30'])))
src = open(H + '/lean/afr/Checker.lean').read()
main = '''
open AFR
def cases : List (String × Nat × Nat × String × Nat × Nat × Nat × Nat × Nat) := [
''' + ',\n'.join(L) + '''
]
def s42cases : List (String × Nat × Nat × Nat × Nat × Nat × Nat) := [
''' + (','+chr(10)).join(S42) + '''
]
def main : IO Unit := do
  for (it, y, mo, mid, lng, p7, p3) in s42cases do
    IO.println s!"{it}\\t{y}-{mo}\\ts42_labelled\\t{if s42 7 mid lng p7 && s42 3 mid lng p3 then "pass" else "FAIL"}\\tmid {mid} long {lng} -> 70% {p7} 30% {p3}"
  for (it, y, mo, term, p, bs, vs, ba, va) in cases do
    IO.println s!"{it}\t{y}-{mo}\tmult_semi_{term}_{p}\t{if mult p bs vs then "pass" else "FAIL"}\t{p}% of semi {bs}: printed {vs}; annual {ba} -> {va}"
'''
open(H + '/lean/afr/RunCBMult.lean', 'w').write(src + main); print(len(L), 'labelled multiples')
