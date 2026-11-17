"""Usability test of the Cumulative Bulletin text layers (per volume): pages, pages without text (need OCR), words/page,
share of word tokens found in a vocabulary built from the 2004-2026 IRB corpus (OCR cleanliness), OCR number artifacts
('9. 11%', '6, 25%'), item headings that start a line (Rev. Rul./Rev. Proc./T.D./I.T./O.D./G.C.M.) -> src/govinfo/usability.json"""
import os, re, glob, json, collections
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit')); C = H + '/cache/www.govinfo.gov/content/pkg'
voc = collections.Counter()
for f in glob.glob(H + '/src/irs-guidance/rev-rul/20[12]*/*.md')[:600]:
    voc.update(w.lower() for w in re.findall(r'[A-Za-z]{3,}', open(f, errors='replace').read()))
V = {w for w, c in voc.items() if c >= 2}
pk = {}
for line in open(H + '/src/govinfo/cb_packages.tsv'):
    p = [x.strip() for x in line.split('\t')]
    if len(p) >= 3: pk[p[2]] = p[0][:4]
HEAD = re.compile(r'^\s{0,6}(Rev\. ?Rul\.|Rev\. ?Proc\.|T\. ?D\.|I\. ?T\.|O\. ?D\.|G\. ?C\. ?M\.|S\. ?M\.|Mim\.|A\. ?R\. ?R\.)\s*\d[\d\-–]*\s*$', re.M)
res = {}
for pkg, y in sorted(pk.items(), key=lambda kv: kv[1]):
    ptts = sorted(glob.glob('%s/%s/pdf/*.ptt' % (C, pkg)))
    if not ptts: continue
    pages = []; 
    for f in ptts: pages += open(f, errors='replace').read().split('\f')
    pages = [p for p in pages if p is not None]
    wc = [len(p.split()) for p in pages]
    toks = [w.lower() for p in pages[::7] for w in re.findall(r'[A-Za-z]{3,}', p)]
    known = sum(1 for w in toks if w in V) / max(1, len(toks))
    allt = '\f'.join(pages)
    art = len(re.findall(r'\d\s?[.,]\s\d{2}\s*%', allt)); pct = len(re.findall(r'\d\.\d{2}\s*%', allt))
    heads = collections.Counter(re.sub(r'[\s.]', '', m.group(1)) for m in HEAD.finditer(allt))
    res[y + '_' + pkg[-8:]] = dict(year=y, pages=len(pages), empty_pages=sum(1 for w in wc if w < 30), words_per_page=round(sum(wc) / max(1, len(wc))),
        vocab_share=round(known, 3), pct_numbers=pct, pct_artifacts=art, item_headings=dict(heads))
    print(y, res[y + '_' + pkg[-8:]], flush=True)
json.dump(res, open(H + '/src/govinfo/usability.json', 'w'), indent=1)
