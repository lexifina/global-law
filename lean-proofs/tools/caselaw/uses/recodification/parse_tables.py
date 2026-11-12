"""Extract the disposition tables from the govinfo US Code HTML (cached) into data/dispo_rows.tsv.
Columns: title (restated), src_title (former location title), table_caption, left, right."""
import re, html, sys, os
C = os.path.join(os.path.dirname(__file__), '..', 'cache')
OUT = os.path.join(os.path.dirname(__file__), '..', 'data', 'dispo_rows.tsv')
SRC = [(36, 'USCODE-1998-title36.htm'), (40, 'USCODE-2002-title40.htm'), (46, 'USCODE-2006-title46.htm'),
       (51, 'USCODE-2011-title51.htm'), (41, 'USCODE-2011-title41.htm'), (54, 'USCODE-2014-title54.htm')]


def clean(s):
    # govinfo writes an italic ell as "<BEL>g025<em>l</em>"; drop the marker and control characters
    s = re.sub(r'[\x00-\x1f]?g025', '', s)
    s = re.sub(r'[\x00-\x08\x0b-\x1f]', '', s)
    s = re.sub(r'</?(em|i|cap-smallcap|sup)>', '', s)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = s.replace('&mdash;', ' to ')
    s = html.unescape(s).replace('–', '-').replace('—', '-').replace('\xa0', ' ')
    s = re.sub(r'\s+', ' ', s).strip()
    s = re.sub(r'\(\s*([a-z0-9]+)\s*\)', r'(\1)', s)
    s = re.sub(r'(\d) (?!to\b|or\b)([a-z]{1,2})\b', r'\1\2', s)
    s = re.sub(r'(\d[a-z]{1,2}) -(\d)', r'\1-\2', s)
    return s


rows = []
for title, fn in SRC:
    t = open(os.path.join(C, fn), encoding='utf-8').read()
    for m in re.finditer(r'<table class="(uscdispo2col|usc2colnohead)"[^>]*>(.*?)</table>', t, re.S):
        body = m.group(2)
        cap = clean((re.search(r'<caption>(.*?)</caption>', body, re.S) or [None, ''])[1])
        if 'isposition' not in cap:
            continue
        src = str(title)
        mm = re.search(r'Title (\d+)\)?$', cap)
        if mm and title == 51:
            src = mm.group(1)
        for l, r in re.findall(r'<td class="left">(.*?)</td>\s*<td class="right">(.*?)</td>', body, re.S):
            rows.append((title, src, cap, clean(l), clean(r)))
with open(OUT, 'w', newline='\n', encoding='utf-8') as f:
    for r in rows:
        f.write('\t'.join(map(str, r)) + '\n')
from collections import Counter
print(Counter((r[0], r[1]) for r in rows))
