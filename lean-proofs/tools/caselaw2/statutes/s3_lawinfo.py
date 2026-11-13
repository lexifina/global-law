"""Step 3: per law, what the record and the law's own text say about dates, and where in the law each US Code section is
amended. Writes statutes/lawinfo.jsonl (one object per law) and statutes/commits.tsv (commit -> how the record dated it).

Per law:
  enacted      approval day (law text "Approved ...", else the record's Enacted: trailer)
  secs         [{i, num, div, usc: ["42:2000e-5", ...], eff: [passage ids]}]  law sections in order
  eff          [{id, sec_i, scope, text, kind, day, retro, retro_day}] effective-date / applicability passages
  cites        normalised reporter cites in the law; names: (left, right, offset)
Effective-date rules (regex, 'rx'):
  as if enacted on D               -> day D; retro if D < enacted
  as if included in <law>          -> that law's enactment day; retro (technical correction)
  take effect on D / on the date of enactment / N days|months|years after enactment
  apply to taxable years beginning after D -> D + 1 day
  apply to ... pending ...         -> retro_day 1 (all conduct in pending matters) unless a date is given
  apply to conduct/offenses ... occurring (on or) after D -> prospective from D
"""
import collections, datetime, json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
import common as C

# --- the record: how each commit was dated, enactment days
log = subprocess.run(['git', '--git-dir', f'{C.W}/usc-full.git', 'log', 'main', '--format=@@@%H%n%B'], capture_output=True).stdout.decode('utf-8', 'replace')
ckind, enacted_rec = {}, {}
for blk in log.split('@@@')[1:]:
    h, _, body = blk.partition('\n')
    b1 = re.sub(r'\s+', ' ', body)
    m = re.search(r'In force [A-Z][a-z]+ \d+, \d{4}[.:] (.{0,80})', b1)
    k = 'unknown'
    if m:
        s = m.group(1)
        if s.startswith('Dated the day it was enacted'): k = 'enacted'
        elif s.startswith('Neither the law'): k = 'none'
        elif s.startswith('The amending provision sets its own date') or s.startswith('Set by'): k = 'own'
        elif s.startswith('Enacted'): k = 'edition' if 'but the' in s else 'enacted'
        else: k = 'other'
    lm = re.search(r'^Law: (.+)$', body, re.M); em = re.search(r'^Enacted: (\d{4}-\d\d-\d\d)', body, re.M)
    if lm and em: enacted_rec[lm.group(1).strip()] = C.day(em.group(1))
    ckind[h] = k
C.wtsv(f'{C.S}/commits.tsv', sorted(ckind.items()))

WORDNUM = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
           'eleven': 11, 'twelve': 12, 'fifteen': 15, 'eighteen': 18, 'twenty': 20, 'thirty': 30, 'forty-five': 45,
           'sixty': 60, 'ninety': 90, 'one hundred and twenty': 120, 'one hundred eighty': 180, '180': 180}
MON = r'(?:January|February|March|April|May|June|July|August|September|October|November|December)'
DATE = MON + r' \d{1,2}, \d{4}'
def add(d, n, unit):
    x = datetime.date(d // 10000, d // 100 % 100, d % 100)
    if unit.startswith('day'): x += datetime.timedelta(days=n)
    else:
        months = n * (12 if unit.startswith('year') else 1)
        y, mo = divmod(x.month - 1 + months, 12)
        import calendar
        dd = min(x.day, calendar.monthrange(x.year + y, mo + 1)[1])
        x = datetime.date(x.year + y, mo + 1, dd)
    return int(x.strftime('%Y%m%d'))
def nxt(d):
    x = datetime.date(d // 10000, d // 100 % 100, d % 100) + datetime.timedelta(days=1)
    return int(x.strftime('%Y%m%d'))

USC_A = re.compile(r'\((\d+) U\.S\.C\. ?(\d+[\dA-Za-z]*(?:[\-–]\d+[A-Za-z]*)?)')
USC_C = re.compile(r'[Ss]ections? (\d+[A-Za-z]*)(?:\([^)]{1,6}\))* of the Internal Revenue Code of (?:1986|1954)')
USC_B = re.compile(r'[Ss]ections? (\d+[\dA-Za-z]*(?:[\-–]\d+[A-Za-z]*)?)(?:\([^)]{1,6}\))* of title (\d+), United States Code')
SEC = re.compile(r'^\s*SEC(?:TION)?\. (\d+[A-Za-z]?(?:-\d+)?)\.\s*(.*)$', re.M)
DIV = re.compile(r'^\s*(DIVISION [A-Z]+)\b', re.M)
HEAD = re.compile(r'^\s*\(([a-z]{1,2}|\d+)\) ([A-Z][^\n]{0,120}?)\.--', re.M)
EFFH = re.compile(r'[Ee]ffective [Dd]ate|[Aa]pplicab|[Aa]pplication of [Aa]mend|[Tt]ransition|[Ss]avings|[Rr]etroactiv|[Pp]ending', )
SENTK = re.compile(r'take effect|become effective|be effective|shall apply|shall not apply|apply to|applies to|as if included|as if enacted')
SENT = re.compile(r'[^.;]*?(?:take effect|become effective|be effective|shall apply|shall not apply|apply to|applies to|as if included|as if enacted)[^.]*\.', re.S)

def parse_passage(p, enacted, lawdays):
    """kind, day, retro (0/1), retro_day for one passage."""
    q = re.sub(r'\s+', ' ', p)
    out = dict(kind='', day=0, retro=0, retro_day=0)
    m = re.search(r'as if (?:it had been )?enacted (?:on|as of) (' + DATE + ')', q)
    if m:
        d = C.day(m.group(1)); out.update(kind='asIfEnacted', day=d)
        if enacted and d < enacted: out.update(retro=1, retro_day=d)
    m2 = re.search(r'as if included in (?:the enactment of )?(?:(?:section|title|subtitle|part)[^,]{0,60} of )?(?:the )?([^,.;]{3,160}?)(?:\)|,|;|\.| to which)', q)
    if not out['kind'] and m2:
        ref = m2.group(1)
        pm = re.search(r'Public Law (\d+)[\-–](\d+)', q[m2.start():m2.start() + 300])
        d = lawdays.get(f'Pub. L. {pm.group(1)}-{pm.group(2)}', 0) if pm else 0
        out.update(kind='asIfIncluded', day=d, retro=1 if d and enacted and d < enacted else 0, retro_day=d if d and enacted and d < enacted else 0)
        if not d: out['ref'] = ref[:120]
    if not out['kind']:
        m = re.search(r'(?:take effect|become effective|be effective|effective) (?:on|as of|beginning on) (' + DATE + ')', q)
        if m: out.update(kind='onDate', day=C.day(m.group(1)))
    if not out['kind']:
        m = re.search(r'(?:take effect|become effective|be effective|effective) (?:on|upon) (?:the date of (?:the )?enactment|enactment)', q)
        if m: out.update(kind='onEnactment', day=enacted)
    if not out['kind']:
        m = re.search(r'(?:take effect|apply)[^.]{0,80}?(?:on|beginning) the (?:date|day) that is (\d+|[a-z\- ]+?) (days?|months?|years?) after the date of (?:the )?enactment', q) or \
            re.search(r'(?:take effect|become effective|be effective) (\d+|[a-z\- ]+?) (days?|months?|years?) after (?:the date of )?(?:the )?enactment', q) or             re.search(r'(?:take effect|become effective|be effective|apply)[^.]{0,40}?(?:upon|on|at) the (?:expiration|end) of the (\d+|[a-z\-]+)[\- ](days?|months?|years?) period beginning on the date of (?:the )?enactment', q)
        if m and enacted:
            n = int(m.group(1)) if m.group(1).isdigit() else WORDNUM.get(m.group(1).strip(), 0)
            if n: out.update(kind='afterEnactment', day=add(enacted, n, m.group(2)))
    if not out['kind']:
        m = re.search(r'taxable years beginning after (' + DATE + ')', q)
        if m: out.update(kind='taxableYears', day=nxt(C.day(m.group(1))))
    if not out['kind']:
        m = re.search(r'(?:conduct|offenses?|violations?|acts?|transactions?|services?|discharges?|deaths?|injur(?:y|ies)|claims?|events?)[^.]{0,80}?(?:occurring|committed|arising|made|furnished|incurred|accruing)(?: on or)? after (' + DATE + r'|the date of (?:the )?enactment)', q)
        if m:
            d = enacted if 'enactment' in m.group(1) else C.day(m.group(1))
            out.update(kind='conductAfter', day=d)
    if not out['kind']:
        m = re.search(r'(?:cases?|actions?|proceedings?|petitions?|applications?|appeals?|complaints?|suits?)[^.]{0,60}?(?:filed|commenced|brought|initiated|instituted)(?: on or)? after (' + DATE + r'|the date of (?:the )?enactment)', q)
        if m:
            d = enacted if 'enactment' in m.group(1) else C.day(m.group(1))
            out.update(kind='filedAfter', day=d)
    if re.search(r'(?:apply|applies) to (?:all |any )?(?:claims?|cases?|actions?|civil actions?|proceedings?|appeals?|petitions?|matters?)[^.]{0,450}?pending', q) and \
            not re.search(r'shall not apply to (?:any )?(?:claims?|cases?|actions?|proceedings?)[^.]{0,80}pending', q):
        out['retro'] = 1
        if not out['retro_day']: out['retro_day'] = out['day'] if out['day'] and enacted and out['day'] < enacted else 1
        out['kind'] = (out['kind'] + '+' if out['kind'] else '') + 'pending'
    if re.search(r'(?:conduct|offenses?|violations?|acts?|claims?)[^.]{0,60}?(?:occurring|committed|arising) before', q) and re.search(r'shall apply|applies', q) \
            and not re.search(r'shall not apply[^.]{0,80}before', q):
        if not out['retro']:
            out.update(retro=1, retro_day=out['retro_day'] or 1)
            out['kind'] = (out['kind'] + '+' if out['kind'] else '') + 'priorConduct'
    return out

def scope_of(p, sec_num):
    q = re.sub(r'\s+', ' ', p)
    m = re.search(r'(?:amendments?|repeals?)(?: and repeals?)? made by (sections?|subsections?|paragraphs?|this section|this subsection|this paragraph|this title|this subtitle|this part|this Act|this division|such section|such subsection)([^.;]{0,120})', q)
    if not m:
        # "this Act" as the subject of the timing rule, not "the date of enactment of this Act"
        if re.search(r'\b[Tt]his Act,? (?:\(?and the amendments made by this Act\)?,? )?(?:shall|takes?|appl(?:y|ies)|becomes?|is effective)', q): return 'act'
        if re.search(r'\b[Tt]his (?:title|subtitle|division),? (?:\(?and the amendments made by this (?:title|subtitle|division)\)?,? )?(?:shall|takes?|appl(?:y|ies)|becomes?)', q): return 'title'
        return f'sec:{sec_num}'
    w = m.group(1)
    if w in ('this Act',): return 'act'
    if w in ('this title', 'this subtitle', 'this part', 'this division'): return 'title'
    if w.startswith('section') and not w.startswith('this'):
        nums = re.findall(r'(?<![(\w])(\d+[A-Za-z]?)(?![\w)])', m.group(2).split(' of ')[0])
        return 'secs:' + ','.join(nums) if nums else f'sec:{sec_num}'
    return f'sec:{sec_num}'

def law_info(lab, lawdays):
    L = C.lines(lab)
    if L is None: return None
    t = C.clean(L)
    m = re.search(r'Approved (' + DATE + ')', t)
    enacted = C.day(m.group(1)) if m else enacted_rec.get(lab, 0)
    # sections, with divisions and titles
    secs = []
    marks = sorted([(mm.start(), 'sec', mm) for mm in SEC.finditer(L)] + [(mm.start(), 'div', mm) for mm in DIV.finditer(L)] +
                   [(mm.start(), 'title', mm) for mm in re.finditer(r'^\s*(TITLE [IVXLC]+)--', L, re.M)], key=lambda x: x[0])
    div = title = ''
    starts = []
    for pos, k, mm in marks:
        if k == 'div': div = mm.group(1)
        elif k == 'title': title = mm.group(1)
        else: starts.append((pos, mm.group(1), mm.group(2)[:120], div, title))
    if not starts: starts = [(0, '1', '', '', '')]
    for i, (pos, num, head, dv, ti) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else len(L)
        body = L[pos:end]
        bodyc = re.sub(r'\s+', ' ', body)
        usc = []
        for mm in USC_A.finditer(bodyc): usc.append(f'{mm.group(1)}:{mm.group(2).replace("–", "-")}')
        for mm in USC_B.finditer(bodyc): usc.append(f'{mm.group(2)}:{mm.group(1).replace("–", "-")}')
        for mm in USC_C.finditer(bodyc): usc.append(f'26:{mm.group(1)}')
        secs.append(dict(i=i, num=num, head=head, div=dv, title=ti, usc=sorted(set(usc)), start=pos, end=end))
    # effective-date passages
    eff = []
    for s in secs:
        body = L[s['start']:s['end']]
        whole = bool(EFFH.search(s['head'])) and len(body) < 12000
        cands = []
        if whole:
            cands.append(body)
        else:
            hs = list(HEAD.finditer(body))
            for j, h in enumerate(hs):
                if EFFH.search(h.group(2)):
                    e = hs[j + 1].start() if j + 1 < len(hs) else len(body)
                    cands.append(body[h.start():min(e, h.start() + 4000)])
            covered = ' '.join(cands)
            for x in re.split(r'(?<=[.;])\s+', re.sub(r'\s+', ' ', body)):
                x = x.strip()
                if not SENTK.search(x): continue
                if len(x) > 30 and x[:60] not in covered and re.search(r'amendment|this Act|this section|this title', x):
                    cands.append(x)
        for p in cands:
            pc = re.sub(r'\s+', ' ', p).strip()
            r = parse_passage(pc, enacted, lawdays)
            eff.append(dict(id=len(eff), sec_i=s['i'], sec=s['num'], div=s['div'], title=s['title'], scope=scope_of(pc, s['num']),
                            text=pc[:3000], **r))
    for s in secs: del s['start'], s['end']
    return dict(law=lab, enacted=enacted, enacted_rec=enacted_rec.get(lab, 0), secs=secs, eff=eff,
                cites=sorted({c for c, _ in C.LT.cites(t)}), reports=[list(x) for x in C.LT.reports(t)])

if __name__ == '__main__':
    laws = sorted({l.split('\t')[0] for l in open(f'{C.S}/blockchanges.tsv', encoding='utf-8')} |
                  {l.split('\t')[3] for l in open(f'{C.W}/usc/versions.tsv', encoding='utf-8') if l.split('\t')[2] == 'law'})
    lawdays = dict(enacted_rec)
    n = ne = 0
    with open(f'{C.S}/lawinfo.jsonl', 'w', encoding='utf-8', newline='\n') as fo:
        for lab in laws:
            x = law_info(lab, lawdays)
            if x is None:
                x = dict(law=lab, enacted=enacted_rec.get(lab, 0), enacted_rec=enacted_rec.get(lab, 0), secs=[], eff=[], cites=[], reports=[], notext=1)
            else:
                n += 1; ne += bool(x['eff'])
            fo.write(json.dumps(x, ensure_ascii=False) + '\n')
    print('laws', len(laws), 'with text', n, 'with effective-date passages', ne)
