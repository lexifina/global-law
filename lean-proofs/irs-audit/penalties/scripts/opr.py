#!/usr/bin/env python3
"""OPR (Circular 230) disciplinary announcements in the IRB corpus: count sanctions, types, stated grounds, and test
the one mechanical trigger the rules fix: an expedited suspension under §10.82 for a pattern of not filing returns
requires failure to file for 4 of the 5 tax years preceding the proceeding (31 C.F.R. §10.82(b)(6)(i), from 2011;
§10.82(b)(5)-(6) earlier wording to the same effect)."""
import os, re, glob, json, collections
G = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/src/irs-guidance/announcement')
files = [f for f in sorted(glob.glob(G + '/*/*.md'))
         if re.search(r'Disciplinary Actions Involving|disciplinary sanctions|Disciplinary Proceedings', open(f, errors='ignore').read(), re.I)]
KIND = [('reinstated', r'reinstat'), ('disbarred', r'disbar'), ('suspended', r'suspen'), ('censured', r'censur|reprimand'),
        ('monetary penalty', r'monetary penalty'), ('disqualified appraiser', r'disqualif')]
GROUND = [('conviction', r'convict|guilty|plea'), ('license lost (state discipline)', r'(?:disbarment|revocation|suspension|revoked|suspended)[^|]{0,60}(?:license|certificate|in [A-Z][a-z]+|by the|attorney)|attorney disbarment|license'),
          ('injunction', r'enjoin|injunction'), ('own returns not filed/paid', r'fail\w* to (?:timely )?(?:file|pay)'),
          ('due diligence / false returns', r'due diligence|10\.22|10\.34|false|fraudulent'), ('other / not stated', r'.')]
rows = []; years = collections.Counter()
for f in files:
    yr = re.search(r'/(\d{4})/', f).group(1)
    section = None
    for ln in open(f, errors='ignore'):
        cells = [c.strip() for c in ln.split('|')]
        if len(cells) < 4:
            h = ln.strip()
            if 0 < len(h) < 120 and re.search(r'(?:Suspension|Disbarment|Censure|Reinstatement|Resignation|Reprimand)s?\b', h) and not h.startswith('Announcement'):
                section = next((n for n, p in KIND if re.search(p, h, re.I)), None)
                if re.search(r'resignation', h, re.I) and not section: section = 'resigned'
            continue
        txt = ' | '.join(cells)
        k = next((n for n, p in KIND if re.search(p, txt, re.I)), None)
        if not k and section and re.search(r'(?:19|20)\d\d\s*$', cells[-1]) and not re.search(r'^Name$', cells[0]):
            k = section; txt = txt + ' | [section: %s; ground not stated]' % section
        if not k or re.search(r'Disciplinary Sanction|Professional Designation', txt):
            continue
        if k in ('reinstated', 'resigned'):
            g = 'n/a'
        elif 'ground not stated' in txt:
            g = 'not stated (pre-2008 format)'
        else:
            g = next(n for n, p in GROUND if re.search(p, txt, re.I))
        rows.append(dict(file=os.path.relpath(f, G), year=yr, kind=k, ground=g, expedited=bool(re.search(r'expedited|10\.82', txt)), text=txt[:600]))
        years[yr] += 1
print('announcements', len(files), 'sanction rows', len(rows), 'years', min(years), '-', max(years))
print(collections.Counter(r['kind'] for r in rows).most_common())
print(collections.Counter(r['ground'] for r in rows if r['kind'] != 'reinstated').most_common())
print('expedited (10.82)', sum(r['expedited'] for r in rows))
# 4-of-5 trigger: expedited suspensions whose stated ground is not filing; years must be stated to check
chk = []
for r in rows:
    if r['expedited'] and re.search(r'fail\w* to (?:timely )?file', r['text'], re.I):
        ys = set()
        for a, b in re.findall(r'((?:19|20)\d\d)\s*[–—-]\s*((?:19|20)\d\d)', r['text']):
            ys |= set(range(int(a), int(b) + 1))
        ys |= {int(y) for y in re.findall(r'(?<![\d–-])((?:19|20)\d\d)(?![\d–-])', r['text'])}
        chk.append(dict(r, years=sorted(ys)))
print('expedited suspensions for not filing:', len(chk))
for c in chk:
    print(' ', c['file'], c['years'], c['text'][:400])
json.dump(dict(rows=rows, nonfiling_expedited=chk), open(os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/penalties/data/opr.json'), 'w'), indent=0)
