"""Cumulative Bulletins: text extraction (pdftotext; OCR not used) and an inventory of what each volume contains."""
import os, re, glob, json, subprocess, collections
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit')); C = H + '/cache/www.govinfo.gov/content/pkg'; T = H + '/src/govinfo/text'
os.makedirs(T, exist_ok=True)
pk = {}
for line in open(H + '/src/govinfo/cb_packages.tsv'):
    p = [x.strip() for x in line.split('\t')]
    if len(p) >= 3: pk[p[2]] = (p[0][:4], p[1])
inv = {}
# only packages whose download finished (a "CB <year> <pkg> ..." line in a harvest log); text by up to 8 pdftotext processes
complete = set()
for lg in ('queue_A.log', 'govinfo_cb.log', 'queue.log'):
    if os.path.exists(H + '/logs/' + lg):
        for l in open(H + '/logs/' + lg):
            w = l.split()
            if len(w) >= 4 and w[0] == 'CB' and w[3] in ('whole', 'parts') and not (w[3] == 'parts' and w[4] == '0'): complete.add(w[2])
from concurrent.futures import ThreadPoolExecutor
def _ptt(f):
    o = f[:-4] + '.txt.tmp'
    if not os.path.exists(f[:-4] + '.ptt'):
        subprocess.run(['nice', '-n', '10', 'pdftotext', '-layout', f, o]); os.replace(o, f[:-4] + '.ptt')
    if not os.path.exists(f[:-4] + '.raw'):
        subprocess.run(['nice', '-n', '10', 'pdftotext', f, f[:-4] + '.raw.tmp']); os.replace(f[:-4] + '.raw.tmp', f[:-4] + '.raw')
    return f
_todo = [f for pkg in pk if pkg in complete for f in glob.glob('%s/%s/pdf/*.pdf' % (C, pkg))
         if not os.path.exists('%s/%s_%s.txt' % (T, pk[pkg][0], pkg[-8:])) or not os.path.exists('%s/../raw/%s_%s.txt' % (T, pk[pkg][0], pkg[-8:]))]
with ThreadPoolExecutor(8) as ex: list(ex.map(_ptt, _todo))
PAT = {'Rev. Rul.': r'Rev\. ?Rul\. \d', 'Rev. Proc.': r'Rev\. ?Proc\. \d', 'T.D.': r'T\. ?D\. \d', 'Notice': r'Notice \d{2,4}[-–]\d',
       'Announcement': r'Announcement \d{2,4}[-–]\d', 'G.C.M.': r'G\. ?C\. ?M\. \d', 'I.T.': r'I\. ?T\. \d', 'S.M.': r'S\. ?M\. \d',
       'Mim.': r'Mim\. \d', 'O.D.': r'O\. ?D\. \d', 'A.R.R.': r'A\. ?R\. ?R\. \d', 'Ct. D.': r'Ct\. ?D\. \d', 'action on decision': r'(?i)acquiescence|nonacquiescence'}
for pkg, (year, title) in sorted(pk.items(), key=lambda kv: kv[1]):
    pdfs = sorted(glob.glob('%s/%s/pdf/*.pdf' % (C, pkg)), key=lambda f: int(re.search(r'-(\d+)\.pdf$', f).group(1)) if re.search(r'-(\d+)\.pdf$', f) else 0)
    if not pdfs or pkg not in complete: continue
    out = '%s/%s_%s.txt' % (T, year, pkg[-8:])
    if not os.path.exists(out):
        parts = []
        for f in pdfs:
            parts.append(open(f[:-4] + '.ptt', errors='replace').read())
        open(out, 'w').write('\n'.join(parts))
    rawo = T + '/../raw/%s_%s.txt' % (year, pkg[-8:]); os.makedirs(os.path.dirname(rawo), exist_ok=True)
    if not os.path.exists(rawo) and all(os.path.exists(f[:-4] + '.raw') for f in pdfs):
        open(rawo, 'w').write(chr(10).join(open(f[:-4] + '.raw', errors='replace').read() for f in pdfs))
    t = open(out, errors='replace').read()
    pages = sum(int(re.search(r'Pages:\s+(\d+)', subprocess.run(['pdfinfo', f], capture_output=True, text=True).stdout).group(1)) for f in pdfs)
    words = len(t.split())
    inv[pkg] = dict(year=year, title=title, files=len(pdfs), pages=pages, words=words, words_per_page=round(words / max(pages, 1)),
                    counts={k: len(re.findall(v, t)) for k, v in PAT.items()}, text=os.path.relpath(out, H))
    print(year, title[:40], 'files', len(pdfs), 'pages', pages, 'words/page', inv[pkg]['words_per_page'], {k: v for k, v in inv[pkg]['counts'].items() if v}, flush=True)
json.dump(inv, open(H + '/src/govinfo/cb_inventory.json', 'w'), indent=1)
