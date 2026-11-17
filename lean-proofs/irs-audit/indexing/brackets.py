"""Extract §1(j) rate-table thresholds (TABLE 1-5) from each year's Rev. Proc., 2019-2027."""
import re, json, sys, io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    from docs import DOCS
    from extract import text, norm
ST = ['mfj', 'hoh', 'single', 'mfs', 'est']
out = {}
for ty in range(2018, 2028):
    p = DOCS[ty][-1]; t = norm(text(p)[0])
    # restrict to the tax-rate-table section for this year
    i = t.find('Tax Rate Tables'); i = i if i >= 0 else t.find('TABLE 1')
    segs = re.split(r'TABLE (\d)\b', t[i:i + 20000])
    res = {}
    for k in range(1, len(segs) - 1, 2):
        n = int(segs[k])
        if 1 <= n <= 5 and ST[n - 1] not in res:
            ov = sorted({int(x.replace(',', '')) for x in re.findall(r'Over \$([\d,]+)', segs[k + 1])})
            if ov: res[ST[n - 1]] = ov
    out[ty] = dict(doc=p, br=res)
    print(ty, p, {k: v for k, v in res.items()})
json.dump(out, open('brackets.json', 'w'), indent=1)
