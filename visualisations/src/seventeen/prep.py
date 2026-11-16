"""Seventeen countries, one at a time: the numbers behind seventeen-countries-one-at-a-time.html.

Reads, for each of the seventeen "<country> law in 20 charts" pages, the folder that holds it (its README.en.md and
src/.build/data.json, the numbers its own page draws), and writes seventeen-data.json beside this script. It reads those
folders only and writes nothing into them. Every number on the page comes from here; the rules that pick, group and
label them are in this file.

    python prep.py                    # folders under ~/law8 (or $LAW8)

Folder layout read (each a visualisations/ folder of a country repository, built from that repository alone):
    <LAW8>/serbia/viz/serbia-law/visualisations, <LAW8>/czechia/viz/czechia-law/visualisations,
    <LAW8>/viz/<country>-law/visualisations for the other fifteen.
"""
import json
import os
import re
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAW8 = Path(os.environ.get('LAW8', Path.home() / 'law8'))
OUT = HERE / 'seventeen-data.json'

# id, English name, ISO 3166 numeric (world-atlas ids), the page's languages (first is the default), English page title
COUNTRIES = [
    ('serbia', 'Serbia', '688', ['sr', 'en']),
    ('czechia', 'Czechia', '203', ['cs', 'en']),
    ('turkey', 'Türkiye', '792', ['tr', 'en']),
    ('bulgaria', 'Bulgaria', '100', ['bg', 'en']),
    ('albania', 'Albania', '008', ['sq', 'en']),
    ('belgium', 'Belgium', '056', ['nl', 'fr', 'en']),
    ('france', 'France', '250', ['fr', 'en']),
    ('japan', 'Japan', '392', ['ja', 'en']),
    ('spain', 'Spain', '724', ['es', 'en']),
    ('vietnam', 'Vietnam', '704', ['vi', 'en']),
    ('moldova', 'Moldova', '498', ['ro', 'en']),
    ('bosnia-and-herzegovina', 'Bosnia and Herzegovina', '070', ['bs', 'en']),
    ('greece', 'Greece', '300', ['el', 'en']),
    ('croatia', 'Croatia', '191', ['hr', 'en']),
    ('algeria', 'Algeria', '012', ['fr', 'en']),
    ('andorra', 'Andorra', '020', ['ca', 'en']),
    ('montenegro', 'Montenegro', '499', ['cnr', 'en']),
]
NAME = {c[0]: c[1] for c in COUNTRIES}
LANG_NAME = {'sr': 'Serbian', 'cs': 'Czech', 'tr': 'Turkish', 'bg': 'Bulgarian', 'sq': 'Albanian', 'nl': 'Dutch', 'fr': 'French',
             'ja': 'Japanese', 'es': 'Spanish', 'vi': 'Vietnamese', 'ro': 'Romanian', 'bs': 'Bosnian', 'el': 'Greek', 'hr': 'Croatian',
             'ca': 'Catalan', 'cnr': 'Montenegrin', 'en': 'English'}


def folder(c):
    if c in ('serbia', 'czechia'):
        return LAW8 / c / 'viz' / f'{c}-law' / 'visualisations'
    return LAW8 / 'viz' / f'{c}-law' / 'visualisations'


_cache = {}


def data(c):
    """The country's src/.build/data.json: {'profile': ..., 'charts': ...}."""
    if c not in _cache:
        _cache[c] = json.loads((folder(c) / 'src' / '.build' / 'data.json').read_text(encoding='utf-8'))
    return _cache[c]


def ch(c, k):
    return data(c)['charts'][k]


def pf(c):
    return data(c)['profile']


def readme(c, native=False):
    return (folder(c) / ('README.md' if native else 'README.en.md')).read_text(encoding='utf-8')


def readme_data_rows(c):
    """The rows of the README's Data table: (dataset, records cell, [integers in the records cell])."""
    m = re.search(r'\n## Data\n(.*?)\n## ', readme(c), re.S)
    rows = []
    for line in m.group(1).split('\n'):
        if not line.startswith('|') or re.match(r'\|\s*(---|Dataset|Data)\s*\|', line):
            continue
        cells = [x.strip() for x in line.strip().strip('|').split('|')]
        rows.append((cells[0], cells[2], [int(x.replace(',', '')) for x in re.findall(r'\d[\d,]*', cells[2])]))
    return rows


def readme_records(c, dataset, i=0):
    for name, cell, nums in readme_data_rows(c):
        if name.startswith(dataset):
            return nums[i]
    raise KeyError((c, dataset))


def page_file(c):
    return next(p.name for p in folder(c).glob('*.html'))


def pct(a, b, d=0):
    return round(100 * a / b, d) if b else None


def median(xs):
    return statistics.median(xs) if xs else None


# ------------------------------------------------------------------ records each page drew on
# Each dataset of a page's Data table counted once, by kind. Git histories (commits) are left out: they carry the acts
# and versions already counted. So are lists that repeat records counted on another row (registers of the same acts,
# dates, the texts read, folders), and what a page lists but does not chart. 'src' says where the number is read.
KINDS = {
    'acts': 'Acts and other official texts',
    'versions': 'Versions and recorded changes',
    'decisions': 'Court decisions',
    'parliament': 'Bills, votes, sittings and elections',
    'admin': 'Administrative records',
}


def records_spec():
    R = lambda c, ds, i=0: readme_records(c, ds, i)
    P = lambda c, k: pf(c)[k]
    return {
        'serbia': [
            ('acts', 'Acts in force in the register', R('serbia', 'Register acts'), 'README'),
            ('acts', 'Acts in the Official Gazette of the City of Belgrade', R('serbia', 'Belgrade Official Gazette'), 'README'),
            ('decisions', 'Constitutional Court decisions', R('serbia', 'Constitutional Court'), 'README'),
            ('parliament', 'Bills', R('serbia', 'Bills'), 'README'),
            ('admin', 'Appeals to the Commissioner for Information', R('serbia', 'Appeals to the Commissioner'), 'README'),
            ('admin', 'State Audit Institution recommendations', R('serbia', 'SAI recommendations'), 'README'),
        ],
        'czechia': [
            ('acts', 'Items of the Collection of Laws', R('czechia', 'Collection of Laws'), 'README'),
            ('acts', 'Decrees of the Official Journal', R('czechia', 'Official Journal'), 'README'),
            ('acts', 'Treaty notices', R('czechia', 'Collection of International Treaties'), 'README'),
            ('acts', 'Municipal and regional ordinances', R('czechia', 'Local acts'), 'README'),
            ('versions', 'Commits carrying versions of acts', P('czechia', 'law_commits'), 'data.json profile.law_commits'),
            ('parliament', 'Chamber prints', R('czechia', 'Chamber prints and votes', 0), 'README'),
            ('parliament', 'Chamber votes', R('czechia', 'Chamber prints and votes', 2), 'README'),
            ('parliament', 'Individual MPs’ votes', R('czechia', 'Chamber prints and votes', 3), 'README'),
        ],
        'turkey': [
            ('acts', 'Laws in the law index', R('turkey', 'Law index', 1), 'README'),
            ('acts', 'Items of the Resmî Gazete index', R('turkey', 'Resmî Gazete index'), 'README'),
            ('acts', 'Metropolitan council decisions', R('turkey', 'Metropolitan councils'), 'README'),
            ('versions', 'Amendment notes in the laws in force', R('turkey', 'Amendment notes'), 'README'),
            ('decisions', 'Constitutional Court individual-application decisions', R('turkey', 'Individual-application index'), 'README'),
            ('parliament', 'Plenary minutes', R('turkey', 'Plenary minutes index'), 'README'),
            ('parliament', 'Assembly decisions', R('turkey', 'Assembly decisions'), 'README'),
        ],
        'bulgaria': [
            ('acts', 'Acts of the State Gazette with text', R('bulgaria', 'Acts with text'), 'README'),
            ('acts', 'Acts held back, known by title', R('bulgaria', 'Held-back acts'), 'README'),
            ('versions', 'Amendments listed in the laws’ citations', P('bulgaria', 'amend_events'), 'data.json profile.amend_events'),
        ],
        'albania': [
            ('acts', 'Laws', R('albania', 'Laws'), 'README'),
            ('acts', 'Normative acts with the force of law (with text)', R('albania', 'Normative acts'), 'README'),
            ('acts', 'Decisions of the Council of Ministers', R('albania', 'Decisions of the Council'), 'README'),
            ('acts', 'Decisions of other bodies', R('albania', 'Decisions of other bodies'), 'README'),
            ('acts', 'Instructions and orders', R('albania', 'Instructions and orders'), 'README'),
            ('acts', 'Acts held back, known by number and title', R('albania', 'Acts held back'), 'README'),
            ('versions', 'New versions after the first', P('albania', 'versions_after_first'), 'data.json profile.versions_after_first'),
            ('decisions', 'Court decisions', R('albania', 'Court decisions'), 'README'),
        ],
        'belgium': [
            ('acts', 'Amending acts', R('belgium', 'Amending acts'), 'README'),
            ('acts', 'Acts of 2025', R('belgium', 'Acts of 2025'), 'README'),
            ('acts', 'Federal laws of 2026', R('belgium', 'Federal laws of 2026'), 'README'),
            ('versions', 'Versions of the Constitution, codes and laws', R('belgium', 'Constitution, codes and laws'), 'README'),
            ('decisions', 'Court of Cassation decisions', R('belgium', 'Court of Cassation'), 'README'),
            ('decisions', 'Council of State judgments', R('belgium', 'Council of State'), 'README'),
        ],
        'france': [
            ('acts', 'Text records', R('france', 'Text records'), 'README'),
            ('versions', 'Article versions', R('france', 'Git history', 1), 'README'),
        ],
        'japan': [
            ('acts', 'Laws in force', R('japan', 'Laws in force'), 'README'),
            ('versions', 'Versions in e-Gov’s revision record', R('japan', 'Revisions'), 'README'),
            ('versions', 'Supplementary provisions of amending laws', R('japan', 'Supplementary provisions'), 'README'),
        ],
        'spain': [
            ('acts', 'State norms', R('spain', 'Status of each norm'), 'README'),
            ('versions', 'Changes of one norm by another', R('spain', 'History', 1), 'README'),
            ('parliament', 'Notes on the Congreso’s vote on decree-laws', R('spain', 'BOE notes'), 'README'),
        ],
        'vietnam': [
            ('acts', 'Acts of the National Assembly', R('vietnam', 'Acts and articles'), 'README'),
            ('versions', 'Versions in force', R('vietnam', 'Versions'), 'README'),
        ],
        'moldova': [
            ('acts', 'Laws, National Bank regulations and a treaty', pf('moldova')['laws'] + pf('moldova')['bnm'] + pf('moldova')['treaty'], 'data.json profile.laws + bnm + treaty'),
            ('decisions', 'Supreme Court of Justice decisions', R('moldova', 'Supreme Court of Justice'), 'README'),
            ('decisions', 'Judgments of 12–13 November 2026', R('moldova', 'The courts'), 'README'),
            ('decisions', 'Constitutional Court opinions and judgment', pf('moldova')['cc'], 'data.json profile.cc'),
            ('admin', 'Competition Council decisions', R('moldova', 'Competition Council'), 'README'),
        ],
        'bosnia-and-herzegovina': [
            ('acts', 'Acts in the Gazette’s issue lists', R('bosnia-and-herzegovina', 'Issue lists'), 'README'),
            ('acts', 'Acts with text', R('bosnia-and-herzegovina', 'Acts with text'), 'README'),
            ('decisions', 'Constitutional Court decisions', R('bosnia-and-herzegovina', 'Constitutional Court decisions'), 'README'),
            ('decisions', 'Court of Bosnia and Herzegovina cases', R('bosnia-and-herzegovina', 'Court of BiH cases'), 'README'),
            ('parliament', 'Bills not adopted', R('bosnia-and-herzegovina', 'Bills'), 'README'),
        ],
        'greece': [
            ('acts', 'Laws', R('greece', 'Laws'), 'README'),
            ('acts', 'Presidential decrees', R('greece', 'Presidential decrees'), 'README'),
            ('decisions', 'Areios Pagos decisions', R('greece', 'Areios Pagos'), 'README'),
            ('admin', 'Diavgeia postings', R('greece', 'Diavgeia'), 'README'),
        ],
        'croatia': [
            ('acts', 'Acts of the official part of Narodne novine', R('croatia', 'Acts of the official part'), 'README'),
            ('acts', 'Laws of the earlier build', R('croatia', 'Laws of the earlier build'), 'README'),
            ('acts', 'Acts held back, known by number and title', R('croatia', 'Acts held back'), 'README'),
            ('acts', 'Treaty acts', R('croatia', 'International treaties'), 'README'),
            ('acts', 'Corrections', R('croatia', 'Corrections'), 'README'),
            ('decisions', 'Constitutional Court repeals (operative points)', R('croatia', 'Constitutional Court repeals'), 'README'),
            ('parliament', 'Election results', R('croatia', 'Election results'), 'README'),
        ],
        'algeria': [
            ('acts', 'Texts', R('algeria', 'Folders'), 'README'),
            ('versions', 'Versions', R('algeria', 'Versions'), 'README'),
        ],
        'andorra': [
            ('acts', 'Texts under “Lleis” and the Constitution', R('andorra', 'Laws and Constitution') + 1, 'README (1,040 texts and the Constitution)'),
            ('versions', 'Changes stated by later laws', R('andorra', 'Stated changes'), 'README'),
        ],
        'montenegro': [
            ('acts', 'Acts in force in the register', R('montenegro', 'Register of acts in force'), 'README'),
            ('acts', 'Decrees on ambassadors', R('montenegro', 'Decrees on ambassadors'), 'README'),
        ],
    }


def records():
    spec = records_spec()
    rows = []
    for c, *_ in COUNTRIES:
        for kind, label, n, src in spec[c]:
            rows.append({'c': c, 'kind': kind, 'label': label, 'n': n, 'src': src})
    by = {c: {k: sum(r['n'] for r in rows if r['c'] == c and r['kind'] == k) for k in KINDS} for c, *_ in COUNTRIES}
    return {'kinds': KINDS, 'rows': rows, 'by': by,
            'total': sum(r['n'] for r in rows), 'by_kind': {k: sum(r['n'] for r in rows if r['kind'] == k) for k in KINDS}}


# ------------------------------------------------------------------ the calendar of entry into force
MDAYS = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def cal_grid(pairs):
    """[(month, day, n)] -> 12 lists of day counts (29 February kept)."""
    g = [[0] * MDAYS[m] for m in range(12)]
    for m, d, n in pairs:
        g[m - 1][d - 1] += n
    return g


def calendars():
    out = []
    f = ch('france', 'c07')
    out.append({'c': 'france', 'what': 'article versions', 'years': f['years'], 'grid': cal_grid(f['cal'])})
    s = ch('spain', 'c16')
    out.append({'c': 'spain', 'what': 'changes of one norm by another', 'years': [s['y0'], s['y1']],
                'grid': cal_grid([(int(k[:2]), int(k[3:]), v) for k, v in s['md'].items()])})
    j = ch('japan', 'c09')
    out.append({'c': 'japan', 'what': 'versions that change a law’s text', 'years': [2018, 2025], 'grid': cal_grid(j['cal'])})
    b = ch('belgium', 'c14')
    out.append({'c': 'belgium', 'what': 'changes to the codes and laws', 'years': b['years'],
                'grid': cal_grid([(int(k[:2]), int(k[3:]), v) for k, v in b['cal'].items()])})
    v = ch('vietnam', 'c03')
    out.append({'c': 'vietnam', 'what': 'versions of the acts', 'years': [2000, 2026], 'grid': cal_grid(v['inforce'])})
    for o in out:
        g = o['grid']
        n = sum(map(sum, g))
        top = max(((m, d) for m in range(12) for d in range(MDAYS[m])), key=lambda p: g[p[0]][p[1]])
        o.update(n=n, jan1=g[0][0], top=[top[0] + 1, top[1] + 1, g[top[0]][top[1]]],
                 first=sum(g[m][0] for m in range(12)))
    return out


# ------------------------------------------------------------------ the rule's day: how many laws take effect on it
DELAY_KEYS = ['before', 'same', 'between', 'rule', 'later']


def _acc(rows, mapping):
    o = dict.fromkeys(DELAY_KEYS, 0)
    for r in rows:
        for k, v in r.items():
            if k in mapping:
                o[mapping[k]] += v
    return o


def default_day():
    out = []
    # Serbia: new laws by year of publication; early = 2nd to 7th day
    m = {'same': 'same', 'next': 'between', 'early': 'between', 'eighth': 'rule', 'later': 'later'}
    zs = ch('serbia', 'c08')['by']['zakon']
    out.append({'c': 'serbia', 'rule': '8th day after publication', 'basis': 'Constitution, art. 196', 'span': [zs[0]['y'], zs[-1]['y']],
                'all': _acc(zs, m), 'recent': _acc([r for r in zs if r['y'] >= 2020], m), 'what': 'new laws'})
    # Croatia: laws by five-year period and by year
    m = {'d0': 'same', 'd1': 'between', 'd2': 'between', 'd8': 'rule', 'jan1': 'later', 'm1': 'later', 'later': 'later'}
    c7 = ch('croatia', 'c07')
    out.append({'c': 'croatia', 'rule': '8th day after publication', 'basis': 'Constitution, art. 90', 'span': [1990, 2026],
                'all': _acc([p[1] for p in c7['periods']], m), 'recent': _acc([y[1] for y in c7['years'] if y[0] >= 2020], m), 'what': 'laws'})
    # Montenegro: laws in force
    m = {'neg': 'before', 'd0': 'same', 'd1': 'between', 'd27': 'between', 'd8': 'rule', 'late': 'later'}
    mo = ch('montenegro', 'c04')
    out.append({'c': 'montenegro', 'rule': '8th day after publication', 'basis': 'Constitution, art. 146', 'span': [1992, 2026],
                'all': _acc([mo['groups']['zakon']], m), 'recent': _acc([v for y, v in mo['lawyear'].items() if int(y) >= 2020], m),
                'what': 'laws in force'})
    # Bosnia and Herzegovina: laws with text (2010-2026); 'later' is any other later day
    m = {'before': 'before', 'same': 'same', 'next': 'between', 'eighth': 'rule', 'later': 'later'}
    zb = next(r for r in ch('bosnia-and-herzegovina', 'c03') if r['k'] == 'zakon')
    out.append({'c': 'bosnia-and-herzegovina', 'rule': '8th day after publication', 'basis': 'the laws’ own final provisions',
                'span': [2010, 2026], 'all': _acc([zb], m), 'recent': None, 'what': 'laws with text'})
    # Bulgaria: laws 2003-2026; d12 = 1-2 days after, m1 = 4-31 days
    m = {'before': 'before', 'same': 'same', 'd12': 'between', 'd3': 'rule', 'm1': 'later', 'later': 'later'}
    zg = next(r for r in ch('bulgaria', 'c16')['rows'] if r['k'] == 'law')
    out.append({'c': 'bulgaria', 'rule': '3rd day after promulgation', 'basis': 'Constitution, art. 5(5)', 'span': [2003, 2026],
                'all': _acc([zg], m), 'recent': None, 'what': 'laws'})
    # Belgium: laws changing the codes, by year; d1 = 1-9 days after
    m = {'before': 'before', 'same': 'same', 'd1': 'between', 'd10': 'rule', 'd11': 'later', 'later': 'later'}
    bl = ch('belgium', 'c09')['rows']
    out.append({'c': 'belgium', 'rule': '10th day after publication', 'basis': 'law of 31 May 1961, art. 4', 'span': [bl[0]['y'], bl[-1]['y']],
                'all': _acc(bl, m), 'recent': _acc([r for r in bl if r['y'] >= 2020], m), 'what': 'laws changing the codes'})
    # Spain: laws (Ley), all periods; the 20 days of the Civil Code
    m = {'before': 'before', 'same': 'same', 'next': 'between', 'short': 'between', 'twenty': 'rule', 'month': 'later', 'half': 'later', 'long': 'later'}
    per = ch('spain', 'c15')['per']
    out.append({'c': 'spain', 'rule': '20 days after publication', 'basis': 'Civil Code, art. 2.1', 'span': None,
                'all': _acc([v for k, v in per.items() if k.startswith('L|')], m), 'recent': _acc([per['L|2020']], m),
                'periods': {k[2:]: _acc([v], m) for k, v in per.items() if k.startswith('L|')}, 'what': 'laws'})
    # Andorra: laws; 'gen' = the law says nothing and the general rule (15 days) applies; 'short' = 2 days to a month set by the law
    m = {'pre': 'same', 'same': 'same', 'next': 'between', 'short': 'between', 'gen': 'rule', 'long': 'later'}
    ay = ch('andorra', 'c10')['years']
    out.append({'c': 'andorra', 'rule': '15 days after publication, when the law is silent', 'basis': 'Administration Code of 1989, art. 9',
                'span': [1989, 2026], 'all': _acc(ay.values(), m), 'recent': _acc([v for y, v in ay.items() if int(y) >= 2020], m), 'what': 'laws'})
    for o in out:
        o['n'] = sum(o['all'].values())
    return out


# ------------------------------------------------------------------ weekdays (Monday first) and months
def weekdays():
    rows = []
    add = lambda grp, c, what, wd, span: rows.append({'grp': grp, 'c': c, 'what': what, 'wd': list(wd), 'n': sum(wd), 'span': span})
    add('voted', 'albania', 'laws, by the day the Assembly adopted them', ch('albania', 'c02')['wd'], '1991–2026')
    add('voted', 'andorra', 'laws, by the day the Consell General approved them', ch('andorra', 'c08')['dow'], '1989–2026')
    cz = [0] * 7
    for w, h, n in ch('czechia', 'c07')['grid']:
        cz[w] += n
    add('voted', 'czechia', 'votes in the Chamber of Deputies', cz, '1993–2026')
    sp = ch('spain', 'c13')['wd']
    per = lambda a, b: [sum(sp[str(y)][i] for y in range(a, b + 1) if str(y) in sp) for i in range(7)]
    add('signed', 'spain', 'royal decrees and decree-laws, by their date, 1986–2019', per(1986, 2019), '1986–2019'); rows[-1]['nl'] = '1986–2019'
    add('signed', 'spain', 'royal decrees and decree-laws, by their date, 2020–2024', per(2020, 2024), '2020–2024'); rows[-1]['nl'] = '2020–2024'
    add('signed', 'spain', 'royal decrees and decree-laws, by their date, 2026', per(2026, 2026), '2026'); rows[-1]['nl'] = '2026'
    bg = [0] * 7
    for r in ch('bulgaria', 'c14'):
        for i, n in enumerate(r['wd']):
            bg[i] += n
    add('published', 'bulgaria', 'issues of the State Gazette', bg, '2003–2026')
    add('published', 'france', 'texts in force, by their day in the Journal officiel', ch('france', 'c07')['wd_pub'], 'texts in force')
    add('published', 'spain', 'norms that made the changes of 2000–2025, by BOE day', ch('spain', 'c16')['wd_pub'], '2000–2025')
    add('published', 'japan', 'versions of 2018–2025, by promulgation day', ch('japan', 'c09')['wd_pub'], '2018–2025')
    add('effect', 'france', 'article versions of 2000–2025, by the day they took effect', ch('france', 'c07')['wd_inf'], '2000–2025')
    add('effect', 'spain', 'changes of 2000–2025, by the day they took effect', ch('spain', 'c16')['wd_inf'], '2000–2025')
    add('effect', 'japan', 'versions of 2018–2025, by the day they took effect', ch('japan', 'c09')['wd_in'], '2018–2025')
    md = {r['db']: r for r in ch('moldova', 'c07')['rows']}
    add('decided', 'moldova', 'Supreme Court of Justice, civil college, by decision date', md['col_civil']['wd'], '2013–2014'); rows[-1]['nl'] = 'civil'
    add('decided', 'moldova', 'Supreme Court of Justice, criminal plenum, by decision date', md['plen_penal']['wd'], '2003–2017'); rows[-1]['nl'] = 'criminal'
    gr = [0] * 7
    for w, h, n in ch('greece', 'c10')['grid']:
        gr[w] += n
    add('decided', 'greece', 'administrative acts, by the day posted on Diavgeia', gr, '2010–2019')
    return rows


def months():
    rows = []
    def add(grp, c, what, m, span):
        rows.append({'grp': grp, 'c': c, 'what': what, 'm': list(m), 'n': sum(m), 'span': span})
    def by_month(triples, y0=None, y1=None):
        m = [0] * 12
        for y, mo, n in triples:
            if (y0 is None or y >= y0) and (y1 is None or y <= y1):
                m[mo - 1] += n
        return m
    a = ch('albania', 'c02')['grid']
    add('laws', 'albania', 'laws adopted', by_month(a), f"{min(r[0] for r in a)}–{max(r[0] for r in a)}")
    b = ch('bulgaria', 'c02')['cells']
    add('laws', 'bulgaria', 'laws adopted', by_month(b), f"{min(r[0] for r in b)}–{max(r[0] for r in b)}")
    hr = [0] * 12
    for y, ms in ch('croatia', 'c04'):
        for i, n in enumerate(ms):
            hr[i] += n
    add('laws', 'croatia', 'laws published', hr, '1990–2026')
    add('laws', 'spain', 'laws and organic laws, by their date', ch('spain', 'c09')['months'], '2004–2025')
    add('laws', 'andorra', 'laws approved', ch('andorra', 'c08')['month'], '1989–2026')
    mn = [0] * 12
    for r in ch('montenegro', 'c05')['laws']:
        mn[int(r[0][5:7]) - 1] += 1
    add('laws', 'montenegro', 'laws in force, by the day they were voted', mn, '2009–2026')
    sr = [0] * 12
    for r in ch('serbia', 'c02')['days']:
        sr[int(r['d'][5:7]) - 1] += r['n']
    add('laws', 'serbia', 'laws passed', sr, '2004–2026')
    vm = ch('vietnam', 'c03')['adopt_months']
    add('laws', 'vietnam', 'laws and resolutions adopted', [vm[str(i)] for i in range(1, 13)], '2000–2026')
    add('laws', 'japan', 'Acts promulgated', by_month(ch('japan', 'c14')['cells']), '1947–2026')
    add('laws', 'belgium', 'laws changing the codes, by their date', by_month(ch('belgium', 'c08')['grid']), '1995–2026')
    al = [0] * 12
    for r in ch('algeria', 'c04'):
        al[int(r['e'][5:7]) - 1] += 1
    add('laws', 'algeria', 'laws, organic laws and ordinances, by their date', al, '2002–2026')
    o = [r for r in ch('algeria', 'c04') if r['i'] == 'ordonnance']
    rows[-1]['ordinances'] = [sum(1 for r in o if r['e'][5:7] in ('07', '08')), len(o)]
    add('courts', 'greece', 'Areios Pagos decisions published', by_month(ch('greece', 'c15')['grid']), '2007–2019')
    return rows


# ------------------------------------------------------------------ from a text's date to its publication, by year
def to_gazette(min_n=5):
    """Median days from the date of a text (its signature or adoption) to its publication, for years with min_n texts."""
    panels = []
    f = ch('france', 'c09')
    ser = lambda rows: [[r[0], r[2], r[1]] for r in rows if r[1] >= min_n]
    panels.append({'c': 'france', 'gazette': 'Journal officiel', 'series': [
        {'k': 'Ministerial orders', 'main': True, 'pts': ser(f['Arrete'])},
        {'k': 'Decrees', 'pts': ser(f['Decret'])},
        {'k': 'Laws', 'pts': ser(f['Loi'])}],
        'from': 'the date of the text', 'note': 'texts still in force'})
    s = ch('spain', 'c14')
    sp = lambda g: [[y, s['med'][g][i], s['n'][g][i]] for i, y in enumerate(s['years']) if s['med'][g][i] is not None and s['n'][g][i] >= min_n]
    panels.append({'c': 'spain', 'gazette': 'BOE', 'series': [
        {'k': 'Royal decrees', 'main': True, 'pts': sp('RD')},
        {'k': 'Ministerial orders', 'pts': sp('O')},
        {'k': 'Laws', 'pts': sp('L')}],
        'from': 'the date of the norm', 'note': 'state norms of the record'})
    a = ch('albania', 'c09')
    panels.append({'c': 'albania', 'gazette': 'Official Journal', 'series': [
        {'k': 'Decisions of the Council of Ministers', 'main': True, 'pts': [[r['y'], r['med'], r['n']] for r in a if r['n'] >= min_n]},
        {'k': 'Laws', 'pts': [[r['y'], r['lmed'], r['ln']] for r in a if (r.get('ln') or 0) >= min_n and r.get('lmed') is not None]}],
        'from': 'the date of adoption', 'note': 'acts held in the repository; for laws the time includes promulgation'})
    b = ch('belgium', 'c09')['rows']
    panels.append({'c': 'belgium', 'gazette': 'Moniteur belge', 'series': [
        {'k': 'Laws changing the codes', 'main': True, 'pts': [[r['y'], r['med'], r['n']] for r in b if r['n'] >= min_n]}],
        'from': 'the date of the law', 'note': 'laws that changed the codes and laws of the repository'})
    al = {}
    for r in ch('algeria', 'c03'):
        if r['d'] >= 0:
            al.setdefault(r['y'], []).append(r['d'])
    panels.append({'c': 'algeria', 'gazette': 'Journal officiel', 'series': [
        {'k': 'Laws, organic laws and ordinances', 'main': True, 'pts': [[y, median(v), len(v)] for y, v in sorted(al.items()) if len(v) >= min_n]}],
        'from': 'the date of signature', 'note': 'texts in the repository; law n° 02-01, dated before its signature, left out',
        'all_median': median([d for v in al.values() for d in v]), 'since2020': median([d for y, v in al.items() if y >= 2020 for d in v])})
    return {'min_n': min_n, 'panels': panels}


# ------------------------------------------------------------------ the government's acts with the force of law, next to Parliament's laws
def executive():
    out = []
    s = ch('spain', 'c08')
    out.append({'c': 'spain', 'parl': 'Laws and organic laws', 'gov': 'Royal decree-laws',
                'rows': [[y, s['max']['Ley'][i] + s['max']['Ley Orgánica'][i], s['max']['Real Decreto-ley'][i]] for i, y in enumerate(s['years'])],
                'note': 'the highest number of each year, so at least that many; before 1983 for laws and 2004 for decree-laws the record names fewer than half of each year’s'})
    f = ch('france', 'c16')
    out.append({'c': 'france', 'parl': 'Laws and organic laws', 'gov': 'Ordinances (art. 38 of the Constitution)',
                'rows': [[y, f['loi'][i] + f['lo'][i], f['ord'][i]] for i, y in enumerate(f['years'])],
                'note': 'by year of signature; only texts that wrote at least one article version in LEGI'})
    na = {}
    for r in ch('albania', 'c06')['acts']:
        na[int(r['d'][:4])] = na.get(int(r['d'][:4]), 0) + 1
    out.append({'c': 'albania', 'parl': 'Laws', 'gov': 'Normative acts with the force of law (art. 101)',
                'rows': [[r['y'], r['n'], na.get(r['y'], 0)] for r in ch('albania', 'c01')['laws']],
                'note': 'laws by the numbers they were given; normative acts by their date'})
    bh = ch('bosnia-and-herzegovina', 'c08')
    out.append({'c': 'bosnia-and-herzegovina', 'parl': 'Laws of the Parliamentary Assembly', 'gov': 'Laws and amendments enacted by the High Representative',
                'rows': [[r['y'], sum(r.get(k, 0) for k in ('new', 'amend', 'budget', 'adopt')), r.get('hr', 0)] for r in bh],
                'note': 'by year of publication in the Official Gazette'})
    hl = {y: sum(ms) for y, ms in ch('croatia', 'c04')}
    hd = {}
    for d in ch('croatia', 'c05')['decrees']:
        hd[int(d[0][:4])] = hd.get(int(d[0][:4]), 0) + 1
    out.append({'c': 'croatia', 'parl': 'Laws', 'gov': 'Government decrees amending a law (art. 88)',
                'rows': [[y, hl.get(y, 0), hd.get(y, 0)] for y in sorted(set(hl) | set(hd))],
                'note': 'by year of publication in Narodne novine'})
    for o in out:
        o['peak'] = max(o['rows'], key=lambda r: r[2])
        o['tot'] = [sum(r[1] for r in o['rows']), sum(r[2] for r in o['rows'])]
    return out


# ------------------------------------------------------------------ what kind of law: amending, treaty, budget, other (by title)
def law_kinds():
    out = []
    S = ch('serbia', 'c01')
    t = lambda k: sum(r[k] for r in S['rows'])
    out.append({'c': 'serbia', 'span': f"{S['years'][0]}–{S['years'][-1]}", 'what': 'laws passed',
                'amend': t('amend'), 'treaty': t('treaty') + t('loan') + t('guarantee'), 'budget': t('budget'), 'other': t('new') + t('interp')})
    B = ch('bulgaria', 'c01')['rows']
    t = lambda k: sum(r['types'].get(k, 0) for r in B)
    out.append({'c': 'bulgaria', 'span': '2003–2026', 'what': 'laws of the State Gazette',
                'amend': t('amend'), 'treaty': t('treaty'), 'budget': t('budget'), 'other': t('new')})
    Z = ch('croatia', 'c02')['zakon']
    out.append({'c': 'croatia', 'span': '1990–2026', 'what': 'laws (treaties are ratified in a separate part of Narodne novine)',
                'amend': sum(r[2] for r in Z), 'treaty': 0, 'budget': 0, 'other': sum(r[1] - r[2] for r in Z)})
    A = ch('andorra', 'c01')['years']
    t = lambda k: sum(v[k] for v in A.values())
    out.append({'c': 'andorra', 'span': '1989–2026', 'what': 'laws',
                'amend': t('amend'), 'treaty': 0, 'budget': t('budget') + t('credit'), 'other': t('new') + t('consol')})
    M = ch('montenegro', 'c07')
    am = sum(M['areas'][k][p][1] for k in M['areas'] for p in M['periods'])
    al = sum(M['areas'][k][p][0] for k in M['areas'] for p in M['periods'])
    out.append({'c': 'montenegro', 'span': '1992–2026', 'what': 'laws in force (treaties are separate acts)',
                'amend': am, 'treaty': 0, 'budget': 0, 'other': al - am})
    T = ch('turkey', 'c02')
    t = lambda k: sum(r.get(k, 0) for r in T)
    out.append({'c': 'turkey', 'span': '1920–2026', 'what': 'laws published in the Resmî Gazete',
                'amend': t('amend') + t('omnibus'), 'treaty': t('treaty'), 'budget': t('budget'), 'other': t('new') + t('special') + t('khk')})
    H = ch('bosnia-and-herzegovina', 'c08')
    t = lambda k: sum(r.get(k, 0) for r in H)
    out.append({'c': 'bosnia-and-herzegovina', 'span': '1997–2026', 'what': 'laws of the Parliamentary Assembly',
                'amend': t('amend'), 'treaty': 0, 'budget': t('budget'), 'other': t('new') + t('adopt')})
    for o in out:
        o['n'] = o['amend'] + o['treaty'] + o['budget'] + o['other']
    return out


# ------------------------------------------------------------------ one act, many laws
def omnibus():
    """The two acts that changed the most other acts, as each page counts them (English names as the pages give them)."""
    out = []
    reach = sorted(ch('turkey', 'c03')['reach'], key=lambda r: -r['acts'])
    nm = {('KHK', 703): 'Decree-law 703 of 2 July 2018', ('Kanun', 5728): 'Law 5728 of 2008'}
    out.append({'c': 'turkey', 'unit': 'laws and decree-laws changed', 'acts': [[nm.get((r['k'], r['no']), f"{'Decree-law' if r['k'] == 'KHK' else 'Law'} {r['no']}"), r['acts'], r['d'][:4]] for r in reach[:2]]})
    pts = sorted(ch('czechia', 'c13')['pts'], key=lambda p: -p[1])
    cz = {'281/2009 Sb.': 'Act 281/2009, accompanying the Tax Procedure Code', '320/2002 Sb.': 'Act 320/2002, abolishing the district offices'}
    out.append({'c': 'czechia', 'unit': 'acts changed', 'acts': [[cz[p[2]], p[1], str(p[0])] for p in pts[:2]]})
    sp = sorted(ch('spain', 'c06')['rows'], key=lambda r: -r['n'])
    es = {'Ley 62/2003, de 30 de diciembre': 'Law 62/2003, fiscal, administrative and social measures', 'Ley 6/2018, de 3 de julio': 'Law 6/2018, the budget for 2018'}
    out.append({'c': 'spain', 'unit': 'norms changed', 'acts': [[es[r['name']], r['n'], r['days'][0][:4]] for r in sp[:2]]})
    bg = sorted(ch('bulgaria', 'c06')['top'], key=lambda r: -r['n'])
    bgn = ['Act amending the Investment Promotion Act (2026)', 'Anti-Corruption Act (2023)']
    out.append({'c': 'bulgaria', 'unit': 'laws amended', 'acts': [[bgn[i], r['n'], str(r['y'])] for i, r in enumerate(bg[:2])]})
    fr = sorted(ch('france', 'c10')['rows'], key=lambda r: -len(r['codes']))
    frn = {'loi:92-1336': 'Law 92-1336 on the entry into force of the new Criminal Code', 'loi:2013-403': 'Law 2013-403 on the election of departmental councillors'}
    out.append({'c': 'france', 'unit': 'codes changed', 'acts': [[frn[r['k']], len(r['codes']), r['k'][4:8] if r['k'][4:6] == '20' else '19' + r['k'][4:6]] for r in fr[:2]]})
    vn = sorted(ch('vietnam', 'c06')['laws'], key=lambda r: -r[4])
    vnn = {'116/2025/QH15': 'Cybersecurity Law (2025)', '35/2018/QH14': 'Law amending 37 laws on planning (2018)'}
    out.append({'c': 'vietnam', 'unit': 'acts of the record changed', 'acts': [[vnn[r[0]], r[4], r[1][:4]] for r in vn[:2]]})
    jp = sorted(ch('japan', 'c06')['rows'], key=lambda r: -r['n'])
    out.append({'c': 'japan', 'unit': 'laws in force that keep its supplementary provisions', 'separate': True,
                'acts': [[f"Act No. {r['no']} of {r['year']}", r['n'], str(r['year'])] for r in jp[:2]]})
    return out


# ------------------------------------------------------------------ the most-amended act of each record
def most_amended():
    """One card per page: the act its most-amended chart puts first, the count and what the count counts."""
    C = []
    add = lambda c, act, n, unit, span, grp: C.append({'c': c, 'act': act, 'n': n, 'unit': unit, 'span': span, 'grp': grp})
    top = lambda rows: max(rows, key=lambda r: r['n'])
    be = top(ch('belgium', 'c11')['rows']); assert be['k'] == 'code-judiciaire'
    add('belgium', 'Judicial Code', be['n'], 'new versions', f"since {be['start'][:4]}", 'versions')
    cz = top(ch('czechia', 'c11')); assert cz['cit'] == '634/2004 Sb.'
    add('czechia', 'Administrative Fees Act', cz['n'], 'new versions', f"since {cz['days'][0][:4]}", 'versions')
    al = top(ch('albania', 'c16')); assert al['a'] == 'vendim/2020/307'
    add('albania', 'Decision on the reconstruction fund (infrastructure in new zones)', al['n'], 'new versions', f"since {min(al['by'])}", 'versions')
    add('algeria', 'Penal Code', pf('algeria')['cp_versions'], 'versions', 'since its 2005 edition', 'versions')
    vn = [r for r in ch('vietnam', 'c12') if r['versions'] == max(x['versions'] for x in ch('vietnam', 'c12'))]; assert len(vn) == 2
    add('vietnam', 'Civil Procedure Code and Criminal Procedure Code', vn[0]['versions'], 'versions each', 'since they took effect', 'versions')
    jp = top(ch('japan', 'c07')['rows']); assert jp['t'] == '地方税法'
    add('japan', 'Local Tax Act', jp['n'], 'amending laws whose supplementary provisions it keeps', f"Act of {jp['year']}", 'amenders')
    bg = top(ch('bulgaria', 'c07'))
    add('bulgaria', 'Social Insurance Code', bg['n'], 'State Gazette issues that amended it', '2004–2026', 'amenders')
    es = top(ch('spain', 'c05')['rows']); assert es['id'] == 'BOE-A-1994-14960'
    add('spain', 'General Social Security Act of 1994', es['n'], 'norms that changed it', 'in 21 years, until it was replaced', 'amenders')
    rs = top(ch('serbia', 'c09')['top'])
    add('serbia', 'Tax Procedure and Tax Administration Act', rs['n'], 'Official Gazette issues that published or changed it', f"since {rs['first']}", 'amenders')
    ad = max(ch('andorra', 'c14')['top'], key=lambda r: r[3]); assert ad[0] == 'lleis/2005-009'
    add('andorra', 'Criminal Code of 2005 (and the Social Security Act of 2008)', ad[3], 'later laws that state changes to each', 'since 2005', 'amenders')
    hr = top(ch('croatia', 'c09')); assert hr['name'] == 'Zakon o porezu na dodanu vrijednost'
    add('croatia', 'Value Added Tax Act', hr['n'], 'amending laws', f"since {min(hr['by'])}", 'amenders')
    el = next(r for r in ch('bosnia-and-herzegovina', 'c07') if r['k'] == 'izborni')
    add('bosnia-and-herzegovina', 'Election Law', el['n'], f"amendments, {sum(1 for i in el['items'] if i[2] == 'hr')} of them by the High Representative",
        f"since {el['items'][0][0]}", 'amenders')
    me = max(ch('montenegro', 'c08')['rows'], key=lambda r: len(r['years']))
    add('montenegro', 'Social and Child Protection Act', len(me['years']), 'amending laws in force', f"since {min(me['years'])}", 'amenders')
    tr = top(ch('turkey', 'c09')); assert tr['title'] == 'İCRA VE İFLAS KANUNU'
    add('turkey', 'Enforcement and Bankruptcy Act', tr['n'], 'amendment notes printed in its text', f"Act of {tr['d'][:4]}", 'notes')
    fr = ch('france', 'c13')['rows'][0]; assert fr['k'] == 'code-de-la-sante-publique'
    add('france', 'Public Health Code', sum(fr['v']), 'article versions', 'since 1990', 'article versions')
    return C


# ------------------------------------------------------------------ constitutions: their life in each record
def constitutions():
    R = []
    def add(c, title, start, events, unit, note, art=None):
        R.append({'c': c, 'title': title, 'start': start, 'events': events, 'unit': unit, 'note': note, 'art': art})
    add('japan', 'Constitution of 1947', '1947-05-03', [], 'articles', 'a single version in e-Gov’s record, never amended', [103, 0])
    sp = ch('spain', 'c17')
    ev = sorted({(d, 1) for a in sp['arts'] for d in a[2]})
    add('spain', 'Constitution of 1978', '1978-12-29', [[d, n] for d, n in ev], 'articles', 'four amendments, each to one article', [169, sum(1 for a in sp['arts'] if a[2])])
    # France, as its page counts: one revision per revising text (2008's took effect in steps); unattributed ones by day
    revs = {}
    for r in ch('france', 'c19'):
        if r['by'].startswith('Constitution') or r['by'] == 'Lexifina':
            continue
        k = 'dila:' + r['day'] if r['by'].startswith('Légifrance') else r['by']
        o = revs.setdefault(k, {'day': r['day'], 'A': set(), 'M': set(), 'D': set()})
        o['day'] = min(o['day'], r['day'])
        for s in 'AMD':
            o[s].update(r[s])
    fr_ev = sorted([o['day'], len(o['A']) + len(o['M'] - o['A']) + len(o['D'] - o['A'] - o['M'])] for o in revs.values())
    add('france', 'Constitution of 1958', '1958-10-05', fr_ev, 'articles created, amended or removed',
        f'{len(fr_ev)} revisions; two (1963, 1976) linked by LEGI to no text', None)
    tr = ch('turkey', 'c10')
    add('turkey', 'Constitution of 1982', '1982-11-09', sorted([tr['act_dates'][a], n] for a, n in tr['acts']), 'amendment notes left in the text',
        'notes only for the latest change of each provision', [177, sum(1 for a in tr['arts'] if not a['tmp'] and a['notes'])])
    hr = ch('croatia', 'c13')
    add('croatia', 'Constitution of 1990', hr[0]['date'], [[r['date'], r['add'] + r['del']] for r in hr[1:]], 'words added and deleted', 'consolidated texts', None)
    bg = ch('bulgaria', 'c11')['chapters']
    add('bulgaria', 'Constitution of 1991', '1991-07-13', [['2015-12-18', sum(c['v2015'] for c in bg)], ['2023-12-22', sum(c['v2023'] for c in bg)], ['2024-07-26', sum(c['v2024'] for c in bg)]],
        'provisions', 'the record holds the 2008 text and three later versions', None)
    R[-1]['held_from'] = '2008-01-01'
    add('andorra', 'Constitution of 1993', '1993-05-03', [], 'articles', 'a single text; no law states a change to it', [107, 0])
    bl = ch('belgium', 'c17')['revs']
    bd = {}
    for r in bl:
        bd[r['inf']] = bd.get(r['inf'], 0) + len(r['arts'])
    add('belgium', 'Constitution coordinated in 1994', '1994-02-17', sorted([d, n] for d, n in bd.items()), 'provisions changed or inserted',
        f"{len({r['law'] for r in bl})} revisions", None)
    md = ch('moldova', 'c05')['acts']
    add('moldova', 'Constitution of 1994', '1994-08-27', sorted([a['enacted'], None] for a in md), 'acts', f'{len(md)} amending acts the repository’s sources name; three versions held (2006, 2016, 2024)', None)
    add('bosnia-and-herzegovina', 'Constitution (Annex 4, 1995)', '1995-12-14', [], 'articles', 'only the English text of 1995, without Amendment I', None)
    al = ch('albania', 'c17')
    add('albania', 'Constitution of 1998', '1998-11-28', [[r['d'], r['n']] for r in al], 'provisions added, changed or repealed', f'{len(al)} amending laws', None)
    me = ch('montenegro', 'c13')
    md2 = {}
    for a in me['amend']:
        md2[a['d']] = md2.get(a['d'], 0) + 1
    add('montenegro', 'Constitution of 2007', '2007-10-22', sorted([d, n] for d, n in md2.items()), 'amendments', '21 amendments changed 17 provisions',
        [len(me['prov']), sum(1 for p in me['prov'] if p['am'])])
    gr = ch('greece', 'c01')
    add('greece', 'Constitution of 1975 (held from 2001)', '2001-04-17', [['2008-06-02', sum(1 for a in gr['arts'] if a['r2008'])], ['2019-11-28', sum(1 for a in gr['arts'] if a['r2019'])]],
        'articles', 'the 1975 text and the 1986 revision are not held', [len(gr['arts']), sum(1 for a in gr['arts'] if a['r2008'] or a['r2019'])])
    R[-1]['held_from'] = '2001-04-17'
    R[-1]['start'] = '1975-06-11'
    add('vietnam', 'Constitution of 2013', '2014-01-01', [['2025-06-16', 5]], 'articles', 'Resolution 203/2025/QH15', [120, 5])
    add('algeria', 'Constitution as revised in 2020', '2020-12-30', [['2026-03-26', 13]], 'articles changed or added', 'law n° 26-04', [226, 13])
    return R


# ------------------------------------------------------------------ still as first written: constitutions and codes
def as_written():
    rows = []
    for o in constitutions():
        if o['art']:
            total, changed = o['art']
            rows.append({'c': o['c'], 'grp': 'Constitutions', 'text': o['title'], 'unit': 'provisions' if o['c'] == 'montenegro' else 'articles',
                         'total': total, 'kept': total - changed, 'empty': 0,
                         'since': 'its 2001 text' if o['c'] == 'greece' else None,
                         'how': 'carry no amendment note' if o['c'] == 'turkey' else None})
    fr = ch('france', 'c05')['rows']
    rows.append({'c': 'france', 'grp': 'Codes', 'text': 'Civil Code of 1804', 'unit': 'articles', 'total': len(fr),
                 'kept': sum(1 for r in fr if r[1] <= '1804-12-31'), 'empty': 0, 'since': None, 'how': 'keep their 1803–1804 wording'})
    es = ch('spain', 'c18')['rows']
    rows.append({'c': 'spain', 'grp': 'Codes', 'text': 'Civil Code of 1889', 'unit': 'articles', 'total': len(es),
                 'kept': sum(1 for r in es if r[4] == 0 and not r[5] and r[2] == '1889-08-16'), 'empty': sum(1 for r in es if r[5]), 'since': None,
                 'how': 'keep their 1889 wording'})
    cp = ch('spain', 'c19')
    rows.append({'c': 'spain', 'grp': 'Codes', 'text': 'Criminal Code of 1995', 'unit': 'articles', 'total': cp['arts'],
                 'kept': cp['never'] if isinstance(cp['never'], int) else len(cp['never']),
                 'empty': cp['emptied'] if isinstance(cp['emptied'], int) else len(cp['emptied']), 'since': None, 'how': 'keep their 1995 text'})
    vc = next(r for r in ch('vietnam', 'c12') if r['i'] == 55)
    assert vc['laws'] == 0 and vc['versions'] == 1
    rows.append({'c': 'vietnam', 'grp': 'Codes', 'text': 'Civil Code of 2015', 'unit': 'articles', 'total': vc['arts'], 'kept': vc['arts'], 'empty': 0,
                 'since': None, 'how': 'never amended'})
    return rows


# ------------------------------------------------------------------ how old the law in force is
ERAS = [('before 1900', None, 1899), ('1900–1944', 1900, 1944), ('1945–1989', 1945, 1989), ('1990–1999', 1990, 1999),
        ('2000–2009', 2000, 2009), ('2010–2019', 2010, 2019), ('2020–2026', 2020, 2026)]


def _era_counts(by_year):
    out = [0] * len(ERAS)
    for y, n in by_year.items():
        y = int(y)
        for i, (_, a, b) in enumerate(ERAS):
            if (a is None or y >= a) and y <= b:
                out[i] += n
                break
    return out


def old_law():
    rows = []
    sp = ch('spain', 'c02')
    rows.append({'c': 'spain', 'what': 'state norms in force, by the year of their date', 'eras': _era_counts({y: sum(v.values()) for y, v in sp['years'].items()}),
                 'oldest': 'a Royal Order of 30 October 1835', 'oldest_y': 1835})
    jp = ch('japan', 'c02')
    rows.append({'c': 'japan', 'what': 'laws in force, by the year of their number', 'eras': _era_counts({y: sum(v.values()) for y, v in jp['years'].items()}),
                 'oldest': 'the Calendar Reform Proclamation of 1872', 'oldest_y': 1872})
    tr = ch('turkey', 'c12')['rows']
    rows.append({'c': 'turkey', 'what': 'laws in force, by the decade they were published', 'eras': _era_counts({r['d']: r.get('inforce', 0) for r in tr}),
                 'oldest': 'laws of the 1920s', 'oldest_y': 1920, 'decades': True})
    cz = ch('czechia', 'c09')['rows']
    e = lambda k: sum(r.get(k, 0) for r in cz)
    # Czech periods: 1918-1938, 1945-1947, 1948-1989, 1990-1992, since 1993; the last cannot be split by decade
    rows.append({'c': 'czechia', 'what': 'consolidated acts in force, by the period they were promulgated in', 'eras': None,
                 'segments': [['1918–1938', e('e1') + e('e2')], ['1945–1989', e('e3') + e('e4')], ['1990–1992', e('e5')], ['since 1993', e('e6')]],
                 'oldest': 'acts of 1918–1938', 'oldest_y': 1918})
    sr = ch('serbia', 'c07')
    rows.append({'c': 'serbia', 'what': 'acts in force in the register, by the year of publication', 'eras': None,
                 'segments': [['before 1992', sr['pre1992']], ['1992 or later', readme_records('serbia', 'Register acts') - sr['pre1992']]],
                 'oldest': 'a rulebook of 1947', 'oldest_y': 1947})
    me = ch('montenegro', 'c01')['rows']
    rows.append({'c': 'montenegro', 'what': 'acts in force, by the year of publication', 'eras': _era_counts({r['y']: sum(v for k, v in r.items() if k != 'y') for r in me}),
                 'oldest': 'acts of 1992, the first year the register holds', 'oldest_y': 1992})
    for r in rows:
        r['n'] = sum(r['eras']) if r['eras'] else sum(s[1] for s in r['segments'])
    return {'eras': [e[0] for e in ERAS], 'rows': rows}


# ------------------------------------------------------------------ budget laws against 1 January
def _days(a, b):
    from datetime import date
    return (date.fromisoformat(b) - date.fromisoformat(a)).days


def budgets():
    out = []
    sp = ch('spain', 'c12')
    out.append({'c': 'spain', 'what': 'General State Budget Law, published in the BOE',
                'years': {int(y): _days(f'{y}-01-01', r['pub']) for y, r in sp['rows'].items()}, 'missing': [int(y) for y in sp['missing']]})
    bh = [r for r in ch('bosnia-and-herzegovina', 'c11') if r['y'] >= 1998]  # as its page: the Gazette's lists start on 29 October 1997
    out.append({'c': 'bosnia-and-herzegovina', 'what': 'budget law of the institutions of BiH (until 2006 the law on budget execution), published in the Official Gazette',
                'years': {r['y']: _days(f"{r['y']}-01-01", r['pub']) for r in bh if r.get('pub')},
                'missing': [r['y'] for r in bh if not r.get('pub')]})
    an = ch('andorra', 'c17')
    out.append({'c': 'andorra', 'what': 'budget law, published in the BOPA',
                'years': {int(y): _days(f'{y}-01-01', r['pub']) for y, r in an['budgets'].items()},
                'approved': {int(y): r['days'] for y, r in an['budgets'].items()}, 'missing': [int(y) for y in an['missing']]})
    bg = ch('bulgaria', 'c04')
    out.append({'c': 'bulgaria', 'what': 'State Budget Act, published in the State Gazette',
                'years': {r['y']: _days(f"{r['y']}-01-01", r['pub']) for r in bg if r.get('pub')},
                'in_force': {r['y']: _days(f"{r['y']}-01-01", r['inf']) for r in bg if r.get('inf')}, 'missing': []})
    for o in out:
        ys = o['years']
        o['late'] = sum(1 for d in ys.values() if d > 0)
        o['n'] = len(ys)
        o['span'] = [min(list(ys) + o['missing']), max(list(ys) + o['missing'])]
    return out


# ------------------------------------------------------------------ money in the law
def money():
    hr = ch('croatia', 'c18')['mw']
    al = ch('albania', 'c14')['wage']
    cz = ch('czechia', 'c20')['wage']
    wages = [
        {'c': 'czechia', 'cur': 'CZK', 'pts': [[r[0], r[2], r[3]] for r in cz], 'note': 'Kčs until 1992'},
        {'c': 'croatia', 'cur': 'EUR', 'pts': [[r[0], r[3], r[2], r[1]] for r in hr], 'note': 'converted at the rates the acts give (1,000 dinars to one kuna, 7.53450 kunas to the euro)'},
        {'c': 'albania', 'cur': 'ALL', 'pts': [[r['d'], r['v'], 'lek'] for r in al if r.get('v')], 'note': 'from the decisions whose text the repository holds'},
    ]
    me = ch('montenegro', 'c16')['rows']
    an = ch('andorra', 'c19')['years']
    bg = ch('bulgaria', 'c20')
    currencies = [
        {'c': 'montenegro', 'what': 'acts in force that give a sum of money, by its currency', 'keys': ['din', 'dem', 'eur'],
         'names': ['dinars', 'German marks', 'euros'], 'rows': [[r['y']] + [r.get(k, 0) for k in ('din', 'dem', 'eur')] for r in me]},
        {'c': 'andorra', 'what': 'laws that mention each currency (share of the year’s laws)', 'keys': ['pta', 'frf', 'eur'],
         'names': ['pesetas', 'French francs', 'euros'], 'rows': [[int(y), v['pta'], v['frf'], v['eur'], v['n']] for y, v in an.items()], 'share_of_laws': True},
        {'c': 'bulgaria', 'what': 'money amounts in the year’s laws, by currency', 'keys': ['lev', 'eur'],
         'names': ['leva', 'euros'], 'rows': [[r['y'], r['lev'], r['eur']] for r in bg]},
    ]
    return {'wages': wages, 'currencies': currencies}


# ------------------------------------------------------------------ the death penalty
# English names of the Vietnamese Penal Code's crimes, as the Vietnamese page gives them (by article)
VN_CRIMES = {108: 'High treason', 109: 'Activities aimed at overthrowing the people’s government', 110: 'Espionage', 112: 'Rebellion',
             113: 'Terrorism against the people’s government', 114: 'Sabotage of the material and technical facilities of the State', 123: 'Murder',
             142: 'Rape of a person under 16', 194: 'Making or trading fake medicines', 248: 'Illegal production of narcotics',
             250: 'Illegal transport of narcotics', 251: 'Illegal trading in narcotics', 299: 'Terrorism', 353: 'Embezzlement', 354: 'Taking bribes',
             421: 'Undermining peace, waging a war of aggression', 422: 'Crimes against humanity', 423: 'War crimes'}


def death_penalty():
    vn = ch('vietnam', 'c14')
    al = ch('algeria', 'c11')
    return {
        'vietnam': {'before': len(vn['crimes']), 'after': sum(1 for c in vn['crimes'] if c[3]), 'day': vn['day'], 'law': vn['law'],
                    'crimes': [[c[0], VN_CRIMES[c[0]], bool(c[3])] for c in vn['crimes']],
                    'life_before': vn['life_before'], 'life_now': vn['life_now'], 'n_crimes': vn['n_crimes'], 'from': '2018-01-01'},
        'algeria': [{'d': r['d'], 'law': r['law'], 'death': r['n'], 'life': r['life']} for r in al],
    }


# ------------------------------------------------------------------ European Union law in the text
def eu():
    out = []
    bg = ch('bulgaria', 'c18')['years']
    out.append({'c': 'bulgaria', 'what': 'laws (treaty ratifications aside) that name an EU directive or regulation',
                'rows': [[r['y'], r.get('mention', 0) + r.get('trans', 0), r.get('mention', 0) + r.get('trans', 0) + r.get('none', 0)] for r in bg]})
    hr = ch('croatia', 'c16')
    out.append({'c': 'croatia', 'what': 'laws whose first three articles name the EU directives or regulations they transpose or implement',
                'rows': [[r[0], r[2], r[1]] for r in hr]})
    me = ch('montenegro', 'c09')['rows']['zakon']
    out.append({'c': 'montenegro', 'what': 'laws in force whose text cites an EU directive, regulation or other act, by year of publication',
                'rows': [[r[0], r[2], r[1]] for r in me]})
    an = ch('andorra', 'c20')
    out.append({'c': 'andorra', 'what': 'laws that mention the European Union, by five-year period', 'periods': True,
                'rows': [[p[0], an['cells']['eu'][i], an['ptot'][i], p[1]] for i, p in enumerate(an['periods'])]})
    cz = ch('czechia', 'c17')
    out.append({'c': 'czechia', 'what': 'government bills the Chamber marks as related to EU law, by term', 'terms': True,
                'rows': [[int(r['t']), r['eu'], r['gov'], r['span']] for r in cz]})
    return out


# ------------------------------------------------------------------ treaty partners
ISO2_N = {'AF': '004', 'AL': '008', 'DZ': '012', 'AD': '020', 'AO': '024', 'AR': '032', 'AM': '051', 'AU': '036', 'AT': '040', 'AZ': '031', 'BH': '048',
          'BD': '050', 'BY': '112', 'BE': '056', 'BA': '070', 'BR': '076', 'BG': '100', 'CA': '124', 'CL': '152', 'CN': '156', 'CO': '170', 'HR': '191',
          'CU': '192', 'CY': '196', 'CZ': '203', 'DK': '208', 'EG': '818', 'EE': '233', 'FI': '246', 'FR': '250', 'GE': '268', 'DE': '276', 'GR': '300',
          'HU': '348', 'IS': '352', 'IN': '356', 'ID': '360', 'IR': '364', 'IQ': '368', 'IE': '372', 'IL': '376', 'IT': '380', 'JP': '392', 'JO': '400',
          'KZ': '398', 'KR': '410', 'KW': '414', 'KG': '417', 'LV': '428', 'LB': '422', 'LY': '434', 'LT': '440', 'LU': '442', 'MY': '458', 'MT': '470',
          'MX': '484', 'MD': '498', 'MN': '496', 'ME': '499', 'MA': '504', 'NL': '528', 'NZ': '554', 'NO': '578', 'MK': '807', 'PK': '586', 'PL': '616',
          'PT': '620', 'QA': '634', 'RO': '642', 'RU': '643', 'SA': '682', 'RS': '688', 'SG': '702', 'SK': '703', 'SI': '705', 'ZA': '710', 'ES': '724',
          'SE': '752', 'CH': '756', 'SY': '760', 'TJ': '762', 'TH': '764', 'TN': '788', 'TR': '792', 'TM': '795', 'UA': '804', 'AE': '784', 'GB': '826',
          'US': '840', 'UY': '858', 'UZ': '860', 'VE': '862', 'VN': '704', 'XK': None, 'PE': '604', 'PH': '608', 'SN': '686', 'NG': '566', 'KE': '404',
          'ET': '231', 'TW': '158', 'LI': '438', 'SM': '674', 'MC': '492', 'VA': '336', 'CR': '188', 'PA': '591', 'EC': '218', 'BO': '068', 'PY': '600',
          'DO': '214', 'GT': '320', 'HN': '340', 'NI': '558', 'SV': '222', 'CV': '132', 'MR': '478', 'OM': '512', 'BN': '096', 'LK': '144', 'NP': '524'}
SERBIA_ISO2 = {'Montenegro': 'ME', 'North Macedonia': 'MK', 'Turkey': 'TR', 'Russia': 'RU', 'Bosnia and Herzegovina': 'BA', 'Hungary': 'HU',
               'Azerbaijan': 'AZ', 'China': 'CN', 'France': 'FR', 'United Arab Emirates': 'AE', 'Romania': 'RO', 'Albania': 'AL', 'Slovenia': 'SI',
               'Belarus': 'BY', 'Greece': 'GR', 'Italy': 'IT', 'Germany': 'DE', 'Austria': 'AT', 'Croatia': 'HR', 'Bulgaria': 'BG', 'Slovakia': 'SK',
               'Czechia': 'CZ', 'Czech Republic': 'CZ', 'Cyprus': 'CY', 'Kazakhstan': 'KZ', 'Egypt': 'EG', 'Switzerland': 'CH', 'Israel': 'IL',
               'Spain': 'ES', 'United Kingdom': 'GB', 'United States': 'US', 'Ukraine': 'UA', 'Poland': 'PL', 'Moldova': 'MD', 'Georgia': 'GE',
               'Armenia': 'AM', 'Uzbekistan': 'UZ', 'Indonesia': 'ID', 'India': 'IN', 'Japan': 'JP', 'Qatar': 'QA', 'Kuwait': 'KW', 'Morocco': 'MA',
               'Tunisia': 'TN', 'Norway': 'NO', 'Sweden': 'SE', 'Netherlands': 'NL', 'Belgium': 'BE', 'Portugal': 'PT', 'Denmark': 'DK',
               'Finland': 'FI', 'Iran': 'IR', 'Malta': 'MT', 'Lithuania': 'LT', 'Latvia': 'LV', 'Estonia': 'EE', 'Saudi Arabia': 'SA',
               'Kyrgyzstan': 'KG', 'Mongolia': 'MN', 'Brazil': 'BR', 'Argentina': 'AR', 'Cuba': 'CU', 'Singapore': 'SG', 'South Korea': 'KR',
               'Korea': 'KR', 'Luxembourg': 'LU', 'Ireland': 'IE', 'Iraq': 'IQ', 'Turkmenistan': 'TM', 'Tajikistan': 'TJ', 'Libya': 'LY', 'Algeria': 'DZ',
               'Kosovo': 'XK', 'Bahrain': 'BH', 'Jordan': 'JO', 'Lebanon': 'LB', 'Syria': 'SY', 'Venezuela': 'VE', 'Mexico': 'MX', 'Canada': 'CA',
               'Australia': 'AU', 'Vietnam': 'VN', 'Thailand': 'TH', 'Malaysia': 'MY', 'Pakistan': 'PK', 'Chile': 'CL', 'Oman': 'OM', 'Angola': 'AO',
               'San Marino': 'SM', 'Liechtenstein': 'LI', 'Holy See': 'VA', 'Monaco': 'MC'}


def treaties(top=10):
    recs = []
    def add(c, what, pairs):
        pairs = sorted([(k, n) for k, n in pairs if k and len(k) == 2], key=lambda p: -p[1])
        recs.append({'c': c, 'what': what, 'partners': pairs, 'top': [p[0] for p in pairs[:top]], 'n_states': len(pairs)})
    add('czechia', 'notices on bilateral treaties since 1990', [(r['k'], r['n']) for r in ch('czechia', 'c18')['rows'] if r['k'] != 'multi'])
    add('turkey', 'laws approving an agreement since 1921', [(r['k'], r['n']) for r in ch('turkey', 'c16')['rows'] if r['k'] != 'multi'])
    add('albania', 'laws of ratification and accession since 2000', [(r['k'], r['n']) for r in ch('albania', 'c19')['rows']])
    add('bulgaria', 'ratification laws since 2003', [(r['k'], r['n']) for r in ch('bulgaria', 'c19')['rows'] if r['k'] != 'multi'])
    add('croatia', 'treaty acts since 1992', [(r['k'], r['n']) for r in ch('croatia', 'c17')['rows'] if r['k'] not in ('org', 'multi')])
    es = {}
    for r in ch('spain', 'c03')['rows']:
        if len(r[3]) == 1:
            es[r[3][0]] = es.get(r[3][0], 0) + 1
    add('spain', 'bilateral agreements the BOE consolidates', es.items())
    add('serbia', 'ratification laws (loans excluded) since 2011', [(SERBIA_ISO2.get(p['name']), p['n']) for p in ch('serbia', 'c05')['partners'] if p['g'] != 'multi'])
    count = {}
    for r in recs:
        for k in r['top']:
            count[k] = count.get(k, 0) + 1
    states = sorted(count.items(), key=lambda kv: -kv[1])
    missing = [k for k in count if k not in PARTNER_NAME]
    assert not missing, missing
    return {'top': top, 'records': recs, 'in_top': [[k, n, ISO2_N.get(k)] for k, n in states], 'names': {k: PARTNER_NAME[k] for k in count},
            'albania_kfw': ch('albania', 'c19')['de_kfw']}


PARTNER_NAME = {'AD': 'Andorra', 'AE': 'United Arab Emirates', 'AL': 'Albania', 'AR': 'Argentina', 'AT': 'Austria', 'AZ': 'Azerbaijan',
                'BA': 'Bosnia and Herzegovina', 'BG': 'Bulgaria', 'CA': 'Canada', 'CH': 'Switzerland', 'CL': 'Chile', 'CN': 'China', 'CO': 'Colombia',
                'DE': 'Germany', 'EC': 'Ecuador', 'FR': 'France', 'GB': 'United Kingdom', 'GR': 'Greece', 'HU': 'Hungary', 'IT': 'Italy', 'MA': 'Morocco',
                'ME': 'Montenegro', 'MK': 'North Macedonia', 'NO': 'Norway', 'PE': 'Peru', 'PL': 'Poland', 'PT': 'Portugal', 'RO': 'Romania', 'RS': 'Serbia',
                'RU': 'Russia', 'SI': 'Slovenia', 'SK': 'Slovakia', 'SY': 'Syria', 'TR': 'Türkiye', 'UA': 'Ukraine', 'US': 'United States', 'VA': 'Holy See',
                'XK': 'Kosovo'}


# ------------------------------------------------------------------ what each page could chart (from its charts and its README's limits)
# 2 = charted from the repository; 1 = charted in part (a selection, some years, or as the source records it); 0 = not charted
QUESTIONS = [
    ('versions', 'Every version of the law in force'),
    ('effect', 'The day each act took effect'),
    ('dates', 'Dates of adoption or signature, and of publication'),
    ('bills', 'Bills and votes'),
    ('const', 'Changes to the constitution'),
    ('courts', 'Court decisions'),
    ('treaties', 'Treaties by partner'),
    ('eu', 'EU law named in the text'),
    ('local', 'Local law'),
    ('money', 'Budgets and amounts of money'),
]
MATRIX = {
    'serbia': {'versions': (1, 'the register has text for many acts only from the mid-2010s'), 'effect': (2, 'vacatio legis; the legal year'), 'dates': (2, 'days from bill to law'),
               'bills': (1, 'bills filed and passed; no votes'), 'const': (0, ''), 'courts': (1, 'the Constitutional Court’s database is a selection'),
               'treaties': (2, 'ratification laws by party'), 'eu': (0, ''), 'local': (1, 'Belgrade’s Official Gazette, 2002–2014'), 'money': (1, 'loans by lender')},
    'czechia': {'versions': (2, 'as complete as e-Sbírka’s consolidation'), 'effect': (2, '1 January and 1 July'), 'dates': (2, 'from filing to the Collection'),
                'bills': (2, 'prints, votes and 16.7 million individual votes'), 'const': (0, ''), 'courts': (1, 'only findings that changed the text of an act'),
                'treaties': (2, 'treaty notices by party'), 'eu': (2, 'EU-related government bills'), 'local': (2, 'ordinances of municipalities and regions'),
                'money': (2, 'minimum wage and default interest')},
    'turkey': {'versions': (1, 'amendment notes printed in the current text'), 'effect': (2, 'in-force tables'), 'dates': (1, 'publication dates of laws'),
               'bills': (1, 'plenary sittings and vetoes; no votes'), 'const': (2, 'amendment notes of the 1982 Constitution'), 'courts': (2, 'individual applications'),
               'treaties': (2, 'approval laws by state'), 'eu': (0, ''), 'local': (1, 'three metropolitan councils'), 'money': (0, '')},
    'bulgaria': {'versions': (1, 'laws held as enacted; amendments from citations'), 'effect': (2, 'entry into force against publication'), 'dates': (2, 'adoption and publication'),
                 'bills': (0, ''), 'const': (2, 'four versions, 2008–2024'), 'courts': (1, 'Constitutional Court decisions listed in citations'),
                 'treaties': (2, 'ratification laws by state'), 'eu': (2, 'laws naming EU acts'), 'local': (0, ''), 'money': (2, 'State Budget Acts; amounts in euro and leva')},
    'albania': {'versions': (1, 'as QBZ consolidated them; codes before 2000 only today’s text'), 'effect': (1, 'decisions take effect on publication'),
                'dates': (2, 'adoption to publication'), 'bills': (0, ''), 'const': (2, 'seven amending laws'), 'courts': (1, '1992–2010 and 2025–2026 only'),
                'treaties': (2, 'ratification laws by state'), 'eu': (0, ''), 'local': (0, 'municipal decisions held, not charted'), 'money': (2, 'minimum wage')},
    'belgium': {'versions': (2, 'from the oldest text in Justel’s archive'), 'effect': (2, 'the tenth day; retroactive changes'), 'dates': (2, 'signature to the Moniteur'),
                'bills': (0, ''), 'const': (2, 'revisions since 1994'), 'courts': (1, 'a selection'), 'treaties': (1, 'acts of assent of 2025'),
                'eu': (1, 'directives transposed by the acts of 2025'), 'local': (0, ''), 'money': (0, '')},
    'france': {'versions': (2, '1,528,182 article versions, fullest from the 1990s'), 'effect': (2, 'the calendar of entry into force'), 'dates': (2, 'signature to the Journal officiel'),
               'bills': (0, 'only the title of each law'), 'const': (2, '25 revisions'), 'courts': (1, 'decisions that rewrote or repealed articles'),
               'treaties': (0, ''), 'eu': (0, ''), 'local': (0, ''), 'money': (1, 'finance laws as authors of the tax codes')},
    'japan': {'versions': (1, 'e-Gov’s record from 2016–2017; earlier amendments as supplementary provisions'), 'effect': (2, '1 April'), 'dates': (2, 'promulgation to entry into force'),
              'bills': (1, 'Cabinet or members’ bill, from the law ID'), 'const': (2, 'one version since 1947'), 'courts': (0, ''), 'treaties': (0, ''),
              'eu': (0, 'not an EU country'), 'local': (0, ''), 'money': (1, 'the annual tax Acts')},
    'spain': {'versions': (2, 'from each norm’s first consolidated text'), 'effect': (2, 'the calendar; the Civil Code’s twenty days'), 'dates': (2, 'a norm’s date to the BOE'),
              'bills': (1, 'the Congreso’s votes on decree-laws'), 'const': (2, 'four amendments'), 'courts': (1, 'judgments credited with a change of text'),
              'treaties': (2, 'bilateral agreements by state'), 'eu': (0, ''), 'local': (0, 'regional law is in other repositories'), 'money': (2, 'budget laws')},
    'vietnam': {'versions': (2, '513 versions, 2000–2026'), 'effect': (2, '1 January and 1 July'), 'dates': (2, 'adoption to entry into force'), 'bills': (0, ''),
                'const': (2, 'the 2025 amendment'), 'courts': (0, ''), 'treaties': (0, ''), 'eu': (0, 'not an EU country'), 'local': (0, ''), 'money': (0, '')},
    'moldova': {'versions': (1, 'three versions of the Constitution'), 'effect': (0, ''), 'dates': (1, 'adoption to publication of constitutional amendments'),
                'bills': (0, ''), 'const': (2, 'the 2024 edition'), 'courts': (2, 'Supreme Court of Justice 2003–2017; two days of judgments'),
                'treaties': (0, ''), 'eu': (1, 'the European Union in the Constitution'), 'local': (0, ''), 'money': (0, '')},
    'bosnia-and-herzegovina': {'versions': (1, 'amendments listed in later acts; 21 official consolidated texts'), 'effect': (2, 'acts with text, from 2010'),
                               'dates': (2, 'the two houses; budget laws'), 'bills': (1, 'bills not adopted, 2004–2015'), 'const': (1, 'the English text of 1995 only'),
                               'courts': (2, 'Constitutional Court; Court of BiH'), 'treaties': (0, ''), 'eu': (0, ''), 'local': (0, ''), 'money': (2, 'budget laws; cigarette excise')},
    'greece': {'versions': (1, '88 laws followed through every amendment; five versions of the Constitution'), 'effect': (0, ''),
               'dates': (1, 'directive to Gazette; issue to posting on Diavgeia'), 'bills': (0, ''), 'const': (2, 'the 2008 and 2019 revisions'),
               'courts': (2, 'Areios Pagos, 2007–2019'), 'treaties': (0, ''), 'eu': (1, '36 acts that name a dated directive'),
               'local': (1, 'posting records of municipalities and regions'), 'money': (0, '')},
    'croatia': {'versions': (1, 'each act as first printed; links between acts'), 'effect': (2, 'the eighth day'), 'dates': (2, 'publication and entry into force'),
                'bills': (0, 'election results, not votes on bills'), 'const': (2, 'seven versions'), 'courts': (1, 'Constitutional Court repeals printed in Narodne novine'),
                'treaties': (2, 'treaty acts by party'), 'eu': (2, 'laws naming EU acts'), 'local': (1, 'municipal income tax decisions'), 'money': (2, 'minimum wage')},
    'algeria': {'versions': (1, '17 amendments applied to 7 of 155 texts'), 'effect': (1, 'the day of the Journal officiel issue'), 'dates': (2, 'signature to the Journal officiel'),
                'bills': (0, ''), 'const': (2, 'the 2026 revision'), 'courts': (0, ''), 'treaties': (0, ''), 'eu': (0, 'not an EU country'), 'local': (0, ''),
                'money': (1, 'fines in the Penal Code')},
    'andorra': {'versions': (1, 'laws as enacted; changes stated by later laws'), 'effect': (2, 'same day or next'), 'dates': (2, 'approval to the BOPA'), 'bills': (0, ''),
                'const': (2, 'a single text since 1993'), 'courts': (0, ''), 'treaties': (0, ''), 'eu': (2, 'mentions of the EU and directives'), 'local': (0, ''),
                'money': (2, 'budgets and currencies')},
    'montenegro': {'versions': (1, 'acts as published; only the Constitution consolidated'), 'effect': (2, 'the eighth day'), 'dates': (2, 'voted, published, in force'),
                   'bills': (1, 'convocations, sessions and laws voted twice'), 'const': (2, 'amendments of 2013 and 2026'), 'courts': (0, ''), 'treaties': (0, ''),
                   'eu': (2, 'EU acts cited in the text'), 'local': (2, 'municipal acts in force'), 'money': (2, 'currencies; pension adjustments')},
}


# ------------------------------------------------------------------ how far back each record reaches, and from when it follows versions
# Years as each page's README states them; 'held' says how the record keeps its acts.
DEPTH = {
    'france': {'from': 1539, 'versions': 1990, 'held': 'every article version', 'note': 'from 25 August 1539; LEGI’s history is fullest from the 1990s'},
    'spain': {'from': 1835, 'versions': 1979, 'held': 'every change since each norm’s first consolidated text', 'note': 'the oldest norm in force is of 1835; the changes charted run from 1979'},
    'japan': {'from': 1872, 'versions': 2017, 'held': 'laws in force; versions from e-Gov’s record', 'note': 'the oldest law in force is of 1872; the revision record starts in 2016–2017 for most laws'},
    'czechia': {'from': 1918, 'versions': 1990, 'held': 'every version e-Sbírka consolidates', 'note': 'the Collection from 1945, 1918–1938 in part; versions charted from 1990'},
    'turkey': {'from': 1920, 'versions': None, 'held': 'laws in force with the amendment notes of their current text', 'note': 'the law index from 1921 and plenary minutes from 1920', 'short': 'laws in force, with notes'},
    'serbia': {'from': 1947, 'versions': 2015, 'held': 'acts in force', 'note': 'the oldest act in force is of 1947; text for many acts only from the mid-2010s'},
    'bulgaria': {'from': 2003, 'versions': None, 'held': 'acts as enacted, 2003–2026', 'note': 'amendments read from the citations in the laws, back to 1950', 'short': 'acts as enacted'},
    'croatia': {'from': 1990, 'versions': None, 'held': 'acts as first printed, 1990–2026', 'note': 'later changes are separate acts; only the Constitution has consolidated versions', 'short': 'acts as first printed'},
    'albania': {'from': 1991, 'versions': 2000, 'held': 'acts in force or repealed later, with QBZ’s versions', 'note': 'laws from 1991, mostly since 2000'},
    'montenegro': {'from': 1992, 'versions': None, 'held': 'acts in force, as published', 'note': 'acts the PIS marks in force, published 1992–2026', 'short': 'acts in force, as published'},
    'moldova': {'from': 1994, 'versions': None, 'held': 'the Constitution in three versions; court decisions', 'note': 'Supreme Court of Justice decisions of 2003–2017', 'short': 'three versions of the Constitution'},
    'belgium': {'from': 1981, 'versions': 1981, 'held': 'codes and laws from the oldest text in Justel’s archive', 'note': 'the Judicial Code from 1985, the Criminal Code from 1990'},
    'bosnia-and-herzegovina': {'from': 1997, 'versions': None, 'held': 'the Gazette’s issue lists; texts from 2010', 'note': 'from 29 October 1997', 'short': 'issue lists; texts from 2010'},
    'andorra': {'from': 1989, 'versions': None, 'held': 'every law as enacted', 'note': 'the BOPA publishes no consolidated versions', 'short': 'laws as enacted'},
    'vietnam': {'from': 2000, 'versions': 2000, 'held': 'acts in force and their versions', 'note': 'versions from 1 April 2000 to 1 October 2026'},
    'greece': {'from': 2001, 'versions': None, 'held': 'a selection of laws and decrees; Diavgeia records; Areios Pagos decisions', 'note': 'the Constitution from its 2001 text', 'short': 'selections and records of acts'},
    'algeria': {'from': 2002, 'versions': 2002, 'held': 'a selection of texts, 148 of 155 as enacted', 'note': 'May 2002 to October 2026; the Penal Code from its 2005 edition'},
}


# ------------------------------------------------------------------ what the pages found wrong in the data, as their READMEs and notes record it
FINDINGS = [
    ('algeria', 'A law dated before it was signed', 'Law n° 02-01 (electricity and gas) is dated 27 April 1991 in the register; it was signed in 2002.', 'README, Limits; chart 3'),
    ('algeria', 'An amendment applied to the wrong text', 'Law n° 08-12, which amends ordinance n° 03-03 on competition, is applied to law n° 03-03 on tourist expansion zones: since 2008, 24 of its articles carry the competition text.', 'README, Limits; chart 17'),
    ('algeria', 'Texts that run on into the next law', 'Laws n° 04-06 and 04-09 carry on with the articles of the laws printed after them in the Journal officiel (201 files).', 'README, Limits'),
    ('algeria', 'A law missing from the register', 'Organic law n° 26-05, applied in the history, is missing from data/laws.csv.', 'data profile; chart 2'),
    ('algeria', 'Repealed articles still in the text', '25 articles that other laws in the repository repeal are still in its Penal Code.', 'chart 11'),
    ('vietnam', 'Two laws holding another document’s text', 'The files of the Law on Children and the Law on Militia and Self-defence Forces hold part of another document’s text.', 'README, Limits'),
    ('japan', 'A placeholder date', '34 versions promulgated but not yet in force are recorded for 31 December 2117, which stands for no day.', 'chart 13'),
    ('spain', 'A missing decree-law', 'The record does not hold Royal Decree-law 4/2020.', 'chart 11'),
    ('croatia', 'Links that stop short', 'The list of acts with links (registry/data/acts.json) predates 3,466 acts, which have no links yet.', 'README, Limits'),
    ('croatia', 'A misprinted coordinate', 'One act fixing the maritime domain (cadastral municipality Split, 2003) gives coordinates in the open sea: a misprinted zone digit.', 'chart 20'),
    ('bosnia-and-herzegovina', 'The wrong issuer', 'For 18 entries the Gazette’s issue lists name the High Representative as the issuer of other institutions’ acts.', 'README, Limits'),
    ('bosnia-and-herzegovina', 'Titles cut short', 'Some titles in the issue lists are cut short, those of issue 3/03 among them.', 'data profile; chart 7'),
    ('andorra', 'Dates that disagree with the bulletin', 'Two laws of 1993 are dated a day after the bulletin that publishes them; the preamble and signature of Law 2/2025 of 23 January say “2024”.', 'README, Limits'),
]
GAPS = [
    ('montenegro', 41636, 'acts in force held back, each with a reason (data/held.json)'),
    ('croatia', 9706, 'acts held back: a number and a title, no text (data/held.json)'),
    ('albania', 3935, 'acts held back, known by number, date and title (data/held.json)'),
    ('bulgaria', 3279, 'acts held back because they do not read cleanly (data/held.json)'),
]


# ------------------------------------------------------------------ the pages, the map and the top-level numbers
def pages():
    out = []
    for c, name, iso, langs in COUNTRIES:
        p = pf(c)
        title_native = readme(c, native=True).split('\n', 1)[0].lstrip('# ').strip()
        title_en = readme(c).split('\n', 1)[0].lstrip('# ').strip()
        out.append({'c': c, 'name': name, 'iso': iso, 'langs': langs, 'lang_names': [LANG_NAME[x] for x in langs], 'file': page_file(c),
                    'title': title_native, 'title_en': title_en, 'repo': f'{c}-law', 'head': (p.get('head') or '')[:10], 'built': p.get('built')})
    return out


def tiles(rec):
    langs = sorted({l for _, _, _, ls in COUNTRIES for l in ls if l != 'en'})
    years = [d['from'] for d in DEPTH.values()]
    last = max(pf(c).get('last_in_force') or pf(c).get('record_to') or pf(c).get('built') for c, *_ in COUNTRIES)
    return {'countries': len(COUNTRIES), 'charts': 20 * len(COUNTRIES), 'languages': len(langs), 'language_codes': langs,
            'records': rec['total'], 'by_kind': rec['by_kind'], 'first_year': min(years), 'first_record': pf('france')['first_in_force'],
            'last_record': last}


def main():
    rec = records()
    out = {
        'built': max(pf(c).get('built') or '' for c, *_ in COUNTRIES),
        'pages': pages(),
        'tiles': tiles(rec),
        'records': rec,
        'calendars': calendars(),
        'default_day': default_day(),
        'weekdays': weekdays(),
        'months': months(),
        'to_gazette': to_gazette(),
        'executive': executive(),
        'law_kinds': law_kinds(),
        'omnibus': omnibus(),
        'most_amended': most_amended(),
        'constitutions': constitutions(),
        'as_written': as_written(),
        'old_law': old_law(),
        'budgets': budgets(),
        'money': money(),
        'death_penalty': death_penalty(),
        'eu': eu(),
        'treaties': treaties(),
        'questions': QUESTIONS,
        'matrix': MATRIX,
        'depth': DEPTH,
        'findings': FINDINGS,
        'gaps': GAPS,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')), encoding='utf-8', newline='\n')
    print(f'{OUT.name}: {OUT.stat().st_size:,} bytes; {rec["total"]:,} records')


if __name__ == '__main__':
    main()


