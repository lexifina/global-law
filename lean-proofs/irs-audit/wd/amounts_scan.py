"""Statutory amounts quoted in written determinations / counsel documents: s2503(b) annual exclusion, s2631 GST exemption
and s2010 basic exclusion amounts as stated near their names; each amount must be one the statute ever set (any year
1996-2026, from indexing/published.json + statutory fixed amounts), and not exceed the amount in force at the document's
release year. -> wd/amounts_scan.json (candidates for hand review)."""
import os, re, glob, json, collections
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit')); P = json.load(open(H + '/indexing/published.json'))
ann = {int(y): d['gift_excl']['v'][0] for y, d in P.items() if 'gift_excl' in d}
for y in range(1982, 1999): ann.setdefault(y, 10000)
bex = {int(y): d['basic_excl']['v'][0] for y, d in P.items() if 'basic_excl' in d}
# statutory (unindexed) estate / GST exemption history: s2010(c) and s2631 (EGTRRA schedule)
for y, v in {1997: 600000, 1998: 625000, 1999: 650000, 2000: 675000, 2001: 675000, 2002: 1000000, 2003: 1000000, 2004: 1500000, 2005: 1500000, 2006: 2000000, 2007: 2000000, 2008: 2000000, 2009: 3500000, 2010: 5000000}.items(): bex.setdefault(y, v)
GST = dict(bex); GST.update({1996: 1000000, 1997: 1000000, 1998: 1000000, 1999: 1010000, 2000: 1030000, 2001: 1060000, 2002: 1100000, 2003: 1120000})
K = [('annual exclusion', r'(?:annual (?:gift tax )?exclusion|§ ?2503\(b\))', ann), ('GST exemption', r'GST exemption', GST), ('basic exclusion', r'(?:basic exclusion amount|applicable exclusion amount|unified credit)', bex)]
res = collections.Counter(); cands = []
for f in glob.glob(H + '/wd/text/*.txt'):
    t = ' '.join(open(f, errors='replace').read().split())
    if len(t) < 300: continue
    m = re.search(r'Release Date:\s*\d{1,2}/\d{1,2}/(\d{4})', t); ry = int(m.group(1)) if m else None
    for name, rx, tab in K:
        for mm in re.finditer(rx + r'[^$.;]{0,60}\$ ?([\d,]{5,})(?! million)', t):
            v = int(mm.group(1).replace(',', '')); res[name] += 1
            ok_any = v in set(tab.values()); ok_year = ry is None or v <= max(tab.get(y, 0) for y in range(1996, ry + 1))
            if not (ok_any and ok_year): cands.append(dict(doc=os.path.basename(f), release=ry, item=name, amount=v, ctx=t[max(0, mm.start() - 120): mm.end() + 80]))
json.dump(dict(summary=res, candidates=cands), open(H + '/wd/amounts_scan.json', 'w'), indent=0)
print(dict(res), len(cands))
for c in cands[:25]: print(c['doc'], c['release'], c['item'], c['amount'], '|', c['ctx'][60:260])
