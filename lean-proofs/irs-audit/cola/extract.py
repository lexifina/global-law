import re, json, os, glob
G = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/src/irs-guidance')
N = {2005:'notice/2004/2004-072.md',2007:'notice/2006/2006-098.md',2008:'notice/2007/2007-087.md',2009:'notice/2008/2008-102.md',
 2010:'notice/2009/2009-094.md',2011:'notice/2010/2010-078.md',2012:'notice/2011/2011-090.md',2013:'notice/2012/2012-067.md',
 2015:'notice/2014/2014-070.md',2016:'notice/2015/2015-075.md',2017:'notice/2016/2016-062.md',2018:'notice/2017/2017-064.md',
 2019:'notice/2018/2018-083.md',2020:'notice/2019/2019-059.md',2021:'notice/2020/2020-079.md',2022:'notice/2021/2021-061.md',
 2023:'notice/2022/2022-055.md',2024:'notice/2023/2023-075.md',2025:'notice/2024/2024-080.md',2026:'notice/2025/2025-067.md'}
SEC = {'415b': r'415\(b\)\(1\)\(A\)', '415c': r'415\(c\)\(1\)\(A\)', '402g': r'402\(g\)\(1\)', '401a17': r'401\(a\)\(17\)',
       '416i': r'416\(i\)\(1\)\(A\)\(i\)', '414q': r'414\(q\)\(1\)\(B\)', '414v': r'414\(v\)\(2\)\(B\)\(i\)', '408p': r'408\(p\)\(2\)\(E\)'}
out = {}
for y, f in N.items():
    t = ' '.join(open(G + '/' + f).read().split())
    i = max(t.find('Effective January 1'), t.find('Cost-of-Living Adjusted Limits'))
    body = t[i:] if i > 0 else t
    src = re.search(r'source: "([^"]+)"', t).group(1)
    out[y] = {'doc': f, 'src': src}
    for k, s in SEC.items():
        m = re.search(r'(?:§§?|[Ss]ections?) ?(?:[\d()A-Za-z]+,? (?:and )?)*' + s + r'[^$]{0,320}?(?:from \$[\d,]+ to|unchanged(?: for \d{4})? at|increased(?: in \d{4})? (?:from \$[\d,]+ )?to|increases to|remains|is) \$([\d,]+)', body)
        if m: out[y][k] = [int(m.group(1).replace(',', '')), body[m.start():m.end()][-200:]]
json.dump(out, open(os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/cola/published.json'), 'w'), indent=1)
for y in sorted(out): print(y, ' '.join('%s=%s' % (k, out[y][k][0] if k in out[y] else '-') for k in SEC))
