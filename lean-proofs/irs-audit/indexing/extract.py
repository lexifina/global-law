"""Extract published inflation-adjusted amounts from each year's Rev. Proc. into published.json."""
import re, os, json, sys
sys.path.insert(0, os.path.dirname(__file__))
from docs import DOCS
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit')); G = H + '/src/irs-guidance'
def text(p):
    if p.startswith('EXT:'):
        return open(H + '/cache/www.irs.gov/pub/irs-drop/%s.flow.txt' % p[4:], encoding='utf-8', errors='replace').read(), 'https://www.irs.gov/pub/irs-drop/%s.pdf' % p[4:]
    t = open(G + '/' + p, encoding='utf-8').read()
    src = re.search(r'^source: "([^"]+)"', t, re.M).group(1)
    return t, src
def norm(t):
    t = re.sub(r'(\w)[-–]\s*\n\s*(\w)', r'\1\2', t)
    t = t.replace('‘‘', '"').replace('’’', '"').replace('“', '"').replace('”', '"').replace('’', "'")
    return ' '.join(t.split())
D = r'\$\s?([\d,]+)'
PAT = {
 'pers_exempt': [r'personal exemption amount (?:under § ?151\(d\) )?(?:for (?:taxable years beginning in|calendar year) \d{4} )?is ' + D,
                 r'For (?:taxable years beginning in|calendar year) \d{4},? the (?:personal )?exemption amount (?:under § ?151\(d\) )?is ' + D],
 'gift_excl': [r'first ' + D + r' of gifts to any person'],
 's2032A': [r'aggregate decrease in the value of qualified real property[^$]{0,200}?(?:not exceed|exceed) ' + D],
 's6601j': [r'2[- ]percent portion"?[^$]{0,200}?is ' + D],
 'feie': [r'foreign earned income exclusion amount[^$]{0,80}?is ' + D],
 'inv_income': [r'investment income (?:exceeds|exceeding) ' + D, r'disqualified income[^$]{0,120}?(?:exceeds|exceed|is) ' + D],
 'aged_blind': [r'additional standard deduction amounts? (?:under § ?63\(f\) )?for the aged (?:or|and) (?:for )?the blind (?:is|are) ' + D + r'[^$]{0,160}?increased to ' + D],
 'dep_std': [r'(?:claimed as a dependent|dependency exemption)[^$]{0,300}?greater of (?:\(1\) )?' + D + r',? or (?:\(2\) )?the sum of ' + D],
 'trust_exempt': [r'deduction under § ?642\(b\)\(2\)\(C\)\(i\) is ' + D],
 'levy_wage': [r'amount determined under § ?6334\(d\)\(4\)\(B\) is ' + D],
 'basic_excl': [r'basic exclusion amount (?:is|of) ' + D],
 'std_mfj': [r'Standard Deduction (?:Amount )?\|? ?Married Individuals Filing Joint(?:ly)? (?:Returns )?and Surviving Spouses (?:\(§ ?1(?:\(j\)\(2\))?\(A\)\) |\(§ ?1\(a\)\) )?\|? ?' + D],
 'std_hoh': [r'Standard Deduction (?:Amount )?\|? ?Married[^$]{0,120}?' + D + r' \|? ?Heads? of Households? (?:\(§ ?1(?:\(j\)\(2\))?\(B\)\) |\(§ ?1\(b\)\) )?\|? ?' + D],
 'std_single': [r'Standard Deduction (?:Amount )?\|? ?Married[^$]{0,120}?\$[\d,]+[^$]{0,60}?\$[\d,]+ \|? ?Unmarried Individuals \(other than Surviving Spouses and Heads of Households?\) (?:\(§ ?1(?:\(j\)\(2\))?\(C\)\) |\(§ ?1\(c\)\) )?\|? ?' + D],
 'std_mfs': [r'Standard Deduction (?:Amount )?\|? ?Married[^$]{0,400}?Married Individuals Filing Separate(?:ly)? (?:Returns )?(?:\(§ ?1(?:\(j\)\(2\))?\(D\)\) |\(§ ?1\(d\)\) )?\|? ?' + D],
}
out = {}
for ty, docs in sorted(DOCS.items()):
    out[ty] = {}
    for p in docs:
        raw, src = text(p); t = norm(raw)
        for k, pats in PAT.items():
            for pat in pats:
                ms = list(re.finditer(pat, t))
                m = (ms[-1] if k.startswith('std_') else ms[0]) if ms else None
                if m:
                    out[ty][k] = dict(v=[int(g.replace(',', '')) for g in m.groups()], doc=p, src=src,
                                      quote=t[max(0, m.start()-60): m.end()+20])
                    break
json.dump(out, open(H + '/indexing/published.json', 'w'), indent=1)
keys = list(PAT)
print('ty   ' + ' '.join('%-12s' % k[:12] for k in keys))
for ty in sorted(out):
    print(ty, ' '.join('%-12s' % ('/'.join(str(x) for x in out[ty][k]['v']) if k in out[ty] else '-') for k in keys))
