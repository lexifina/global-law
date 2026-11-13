"""Shared paths and law-text helpers for the caselaw-lean-2 statutes pipeline.
Reuses the overrides work's parsers (uses/overrides/scripts/lawtext.py, names.py) read-only."""
import html, os, re, sys
W = os.path.expanduser('~/Documents/us-caselaw-lean-work')
R2 = f'{W}/caselaw-lean-2'
D = f'{R2}/data'                 # contract files
S = f'{R2}/statutes'             # work dir and caches
OV = f'{W}/uses/overrides'
for d in (f'{S}/cache/plaw', f'{S}/cache/crpt', f'{S}/llm', f'{S}/audit'):
    os.makedirs(d, exist_ok=True)
sys.path.insert(0, f'{OV}/scripts')
import lawtext as LT   # noqa: E402
import names as N      # noqa: E402

def law_parts(lab):
    m = re.fullmatch(r'Pub\. L\. (\d+)-(\d+)', lab)
    return m.groups() if m else None

def plaw_file(lab):
    p = law_parts(lab)
    if not p: return None
    for d in (f'{S}/cache/plaw', f'{OV}/cache/plaw'):
        fn = f'{d}/PLAW-{p[0]}publ{p[1]}.htm'
        if os.path.exists(fn): return fn
    return None

def report_file(base):
    for d in (f'{S}/cache/crpt', f'{OV}/cache/crpt'):
        for k in (base, base + '-pt1'):
            fn = f'{d}/{k}.htm'
            if os.path.exists(fn): return fn
    return None

def raw_law(lab):
    fn = plaw_file(lab)
    return open(fn, encoding='utf-8', errors='replace').read() if fn else None

def clean(s):
    s = html.unescape(re.sub(r'<[^>]+>', ' ', s))
    s = re.sub(r'\[\[Page [^\]]*\]\]', ' ', s)
    s = re.sub(r'<<NOTE:[^>]*>>', ' ', s)
    s = s.replace('``', '"').replace("''", '"')
    s = re.sub(r'-\s*\n\s*', '-', s)
    return re.sub(r'\s+', ' ', s)

def text(lab):
    r = raw_law(lab)
    return clean(r) if r is not None else None

def lines(lab):
    """Law text keeping line breaks (for section structure)."""
    r = raw_law(lab)
    if r is None: return None
    s = html.unescape(re.sub(r'<[^>]+>', '', r))
    s = re.sub(r'\[\[Page [^\]]*\]\]', '', s)
    s = re.sub(r'<<NOTE:[^>]*>>', '', s)
    return s.replace('``', '"').replace("''", '"')

def reports(t):
    return LT.reports(clean(t) if '<' in t[:2000] else t)

def report_text(key):
    fn = report_file(key)
    return clean(open(fn, encoding='utf-8', errors='replace').read()) if fn else None

def norm_cite_key(c):
    """'550 U.S. 618' -> '550 us 618' (graph/cite_index.tsv key)."""
    m = re.match(r'\s*(\d+) (.+?) (\d+)\s*$', c)
    if not m: return None
    return f'{m.group(1)} {re.sub(r"[ .]", "", m.group(2).lower())} {m.group(3)}'

def day(s):
    """'2009-01-29' or 'January 29, 2009' -> 20090129."""
    import datetime
    for fmt in ('%Y-%m-%d', '%B %d, %Y', '%B %d %Y'):
        try:
            return int(datetime.datetime.strptime(s.strip(), fmt).strftime('%Y%m%d'))
        except ValueError:
            pass
    return 0

def wtsv(path, rows, header=None):
    with open(path, 'w', encoding='utf-8', newline='\n') as fo:
        if header: fo.write('\t'.join(header) + '\n')
        for r in rows:
            fo.write('\t'.join(str(x).replace('\t', ' ').replace('\n', ' ').replace('\r', ' ') for x in r) + '\n')
