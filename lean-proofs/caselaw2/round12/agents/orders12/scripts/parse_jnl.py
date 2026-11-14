"""Parse Journal of the Supreme Court texts (PyMuPDF output, page breaks = form-feed lines) into docket entries.

Usage: python -I parse_jnl.py <out_dir> <journal.txt> [...]
Writes <out_dir>/entries.tsv (every entry: journal, line span, date, section, dockets, class, caption, court below,
disposition) and <out_dir>/entries.jsonl (same plus caption lines and body), and heading_misses.tsv (heading-like lines
outside entries that were not recognised, for review). Class: gvr / vacated / reversed / affirmed / cert_denied /
dismissed / other / opinion (entries printed under an Opinion(s) / Per Curiam heading = opinions announced).
"""
import sys, os, re, json, collections

DAYS = 'MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY|SUNDAY'
MONTHS = ['JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', 'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER',
          'NOVEMBER', 'DECEMBER']
DATE_RE = re.compile(r'^(%s), (%s) (\d{1,2}), (\d{4})$' % (DAYS, '|'.join(MONTHS)))
DASH = '[—–-]'
HEAD_RE = re.compile(
    r'^(?:'
    r'Certiorari (?:Denied|Granted|Dismissed)'
    r'|Certiorari ?%(d)s ?Summary Dispositions?'
    r'|Appeals? ?%(d)s ?(?:Summary Dispositions?|Jurisdiction (?:Noted|Postponed))'
    r'|Jurisdiction (?:Noted|Postponed)'
    r'|Summary Dispositions?'
    r'|Orders? [Ii]n Pending Cases?'
    r'|Oral Arguments?'
    r'|Rehearings? (?:Denied|Granted)'
    r'|Petitions? for Rehearing'
    r'|Habeas Corpus (?:Denied|Dismissed)'
    r'|(?:Mandamus|Prohibition)(?: Denied| Dismissed)?'
    r'|Opinions?(?: Per Curiam)?'
    r'|Per Curiam'
    r'|Attorney Discipline'
    r'|Admissions? to the Bar on (?:Oral|Written) Motions?'
    r'|Orders?|Motions? Denied'
    r')$' % {'d': DASH})
HEADLIKE_RE = re.compile(r'^[A-Z][a-z]+(?:[ —–-]+(?:[A-Z][a-z]+|in|on|of|the|for|to|and))*$')
STOP_RE = re.compile(r'^(?:Adjourned|Present:|The Chief Justice said|SUPREME COURT OF THE UNITED STATES|\(JOURNAL\))')
PAGENO_RE = re.compile(r'^(?:\d{1,4}|[IVXLC]{1,6})$')
CONT_RE = re.compile(r'%s\s*Continued$' % DASH)
DOCKET = r'(?:\d{2}[–—‑-]\s?\d{1,5}|\d{2}A\d{1,4}|\d{2}M\d{1,4}|\d{1,3},? Orig(?:inal)?|D[–-]\d{1,5})'
START_RE = re.compile(r'^No\. (%s)(?: \((%s)\))?\.(?:\s|$)' % (DOCKET, DOCKET))
DOCK_IN_CAP_RE = re.compile(r'(?:^|\s)No\. (%s)(?: \((%s)\))?\.' % (DOCKET, DOCKET))
NO_PREFIX = r'^No\. %s(?: \(%s\))?\.\s*' % (DOCKET, DOCKET)
LIGS = {'ﬀ': 'ff', 'ﬁ': 'fi', 'ﬂ': 'fl', 'ﬃ': 'ffi', 'ﬄ': 'ffl'}
STARTERS = (r'On (?:[Pp]etitions?|[Ww]rits?|[Aa]ppeals?|[Aa]pplications?|[Mm]otions?|[Cc]ertificate)\b|Petitions? for\b'
            r'|Motions? (?:of|for|to)\b|Appeals? from\b|Applications? (?:for|to|of)\b|Because\b|Judgments?\b|Writs? of\b'
            r'|Certiorari\b|The (?:petition|motion|application|judgment|case|order)s?\b|Upon\b|Joint motion\b'
            r'|The (?:Acting )?Solicitor General\b'
            r'|Argued\b|Reargued\b|Treating\b|Questions? (?:presented|certified)|Leave to\b|Response\b')
CAP_SPLIT_RE = re.compile(r'(?<!\bv)\.\s+(?=(?:%s))' % STARTERS)
VERB_RE = re.compile(r'\b(?:granted|denied|vacated|reversed|affirmed|dismissed|remanded|Argued|deferred|allowed|'
                     r'appointed|referred|noted|postponed|extended|ordered)\b')


def norm(s):
    for k, v in LIGS.items():
        s = s.replace(k, v)
    return s.replace('\t', ' ')


def join_lines(lines):
    out = ''
    for ln in lines:
        ln = norm(ln.strip())
        if not ln:
            continue
        if not out:
            out = ln
        elif out.endswith('­'):
            out = out[:-1] + ln
        elif re.search(r'[a-z]-$', out) and re.match(r'[a-z]', ln):
            # older Journals hyphenate words at line ends with a plain hyphen ("Judg-" / "ment")
            out = out[:-1] + ln
        elif re.search(r'[A-Za-z0-9][-–]$', out) and re.match(r'[A-Z0-9]', ln):
            # a hyphenated name or a docket split at its hyphen ("Alejo-" / "Agramon", "No. 20-" / "1531")
            out = out + ln
        else:
            out = out + ' ' + ln
    out = out.replace('­', '')
    return re.sub(r' {2,}', ' ', out).strip()


def ascii_docket(d):
    d = re.sub(r'[–—‑]', '-', d)
    return re.sub(r'\s+', '', d)


JDG = r'\b[Jj]udgments?\b(?:[^.]|\bNos?\.|\bU\. S\.){0,200}?\s(?:is |are )?(?:hereby )?'
VAC_RE = re.compile(JDG + r'vacated')
REV_RE = re.compile(JDG + r'reversed')
# later Journals drop the fi ligature in extraction ("affrmed")
AFF_RE = re.compile(JDG + r'af+i?rmed')
GRANT_RE = re.compile(r'certiorari[^.]{0,80}?\bgranted|certiorari (?:is |are )?granted', re.I)
DENY_RE = re.compile(r'certiorari[^.]{0,300}?\bdenied', re.I)
DISMISS_RE = re.compile(r'\bdismissed\b')
COURT_RE = re.compile(r'(?:On (?:petitions? for (?:a )?writs? of certiorari|writs? of certiorari|appeals?) (?:to|from)'
                      r'|[Pp]etitions? for (?:a )?writs? of certiorari to|Appeals? from) (?:the )?(.+?)(?: denied)?\.(?=\s|$)')


REMAND_TO_RE = re.compile(r'remanded to (?:the )?(.+?)(?:,? for (?:further|proceedings)|,? with instructions|\.(?=\s|$))')


COND_RE = re.compile(r'\b(?:Should|should|In the event|in the event|If|if|unless|Unless)\b|terminate')


def find_disp(rx, body):
    """first match of rx whose sentence is not conditional (stay orders: 'In the event ... judgment affirmed, this order
    shall terminate')."""
    for m in rx.finditer(body):
        a = body.rfind('. ', 0, m.start())
        b = body.find('. ', m.end())
        sent = body[a + 1 if a >= 0 else 0: b if b >= 0 else len(body)]
        if not COND_RE.search(sent):
            return m
    return None


ORDVAC_RE = re.compile(r'\b(?:order|orders|injunction|stay|stays)\b(?:[^.]|\bNos?\.){0,300}?\b(?:is |are )?vacated\b')
LOWER_RE = re.compile(r'\b(?:District Court|Court of Appeals|Court of Appeal|Supreme Court of|Circuit|Superior Court|'
                      r'Court of Criminal Appeals|district court|court of appeals)\b')


class _M:
    def __init__(self, a):
        self.a = a

    def start(self):
        return self.a


def find_order_vac(body):
    """a lower court's order / injunction / stay vacated (not the Court's or a Justice's own order)."""
    for m in ORDVAC_RE.finditer(body):
        a = body.rfind('. ', 0, m.start())
        b = body.find('. ', m.end())
        sent = body[a + 1 if a >= 0 else 0: b if b >= 0 else len(body)]
        if COND_RE.search(sent) or re.search(r'heretofore|entered by (?:The |the )?(?:Chief )?Justice', sent):
            continue
        if LOWER_RE.search(sent):
            return _M(a + 2 if a >= 0 else 0)
    return None


def classify(body, section):
    if section and re.match(r'(?:Opinions?|Per Curiam)', section):
        return 'opinion'
    vac, rev, aff = find_disp(VAC_RE, body), find_disp(REV_RE, body), find_disp(AFF_RE, body)
    if vac and GRANT_RE.search(body) and 'remanded' in body[vac.start():]:
        return 'gvr'
    if vac:
        return 'vacated'
    if rev:
        return 'reversed'
    if aff:
        return 'affirmed'
    if find_order_vac(body):
        return 'order_vacated'
    gm = GRANT_RE.search(body)
    if gm and re.search(r'\b(?:case|cases|matter)s? (?:is |are )?remanded\b', body[gm.start():]):
        return 'granted_remanded'
    if DENY_RE.search(body):
        return 'cert_denied'
    if DISMISS_RE.search(body):
        return 'dismissed'
    return 'other'


SENT_END_RE = re.compile(r'(?<![A-Z])(?<!\bv)(?<!\bet al)(?<!\bInc)(?<!\bCo)(?<!\bJr)(?<!\bNo)(?<!\bAssn)\.(?=\s+[A-Z][a-z]|$)')


def disposition_words(body, cls):
    m = {'gvr': VAC_RE, 'vacated': VAC_RE, 'reversed': REV_RE, 'affirmed': AFF_RE,
         'granted_remanded': GRANT_RE}.get(cls)
    mm = find_disp(m, body) if m is not None else None
    if cls == 'order_vacated':
        mm = find_order_vac(body)
    if mm is None:
        return '-'
    s = body[mm.start():]
    e = SENT_END_RE.search(s)
    s = s[:e.end()] if e else s
    if len(s) > 400:
        s = s[:397] + '...'
    return s


def split_caption(text):
    """text = one printed docket entry joined; returns (caption incl. 'No. x.' prefix, rest)."""
    m = START_RE.match(text)
    pos = m.end() if m else 0
    sm = CAP_SPLIT_RE.search(text, pos)
    if not sm:
        return text, ''
    return text[:sm.start() + 1], text[sm.end():]


class Entry:
    def __init__(self, first, date, datehead, section):
        self.lines = []
        self.first = first
        self.last = first
        self.date = date
        self.datehead = datehead
        self.section = section


def parse(path):
    raw = open(path, encoding='utf-8').read().split('\n')
    date = None
    datehead = None
    section = None
    started = False
    page_top = True
    entries = []
    cur = None
    misses = collections.Counter()

    def close():
        nonlocal cur
        if cur is not None and cur.lines:
            entries.append(cur)
        cur = None

    for i, line in enumerate(raw, 1):
        s = line.strip()
        if line == '\f' or s == '\f':
            page_top = True
            continue
        if not s:
            continue
        if page_top:
            if PAGENO_RE.match(s) or CONT_RE.search(s) or s == '(JOURNAL)':
                continue
            dm = DATE_RE.match(s)
            if dm:
                date = '%s%02d%02d' % (dm.group(4), MONTHS.index(dm.group(2)) + 1, int(dm.group(3)))
                datehead = s
                continue
            page_top = False
        dm = DATE_RE.match(s)
        if dm:
            close()
            nd = '%s%02d%02d' % (dm.group(4), MONTHS.index(dm.group(2)) + 1, int(dm.group(3)))
            if nd != date:
                section = None
            date, datehead = nd, s
            continue
        if STOP_RE.match(s):
            close()
            if s.startswith('SUPREME COURT OF THE UNITED STATES') or s.startswith('(JOURNAL)'):
                started = True
                section = None
            continue
        if not started:
            continue
        if HEAD_RE.match(s):
            close()
            section = s
            continue
        if START_RE.match(s):
            close()
            cur = Entry(i, date, datehead, section)
            cur.lines.append(s)
            continue
        if cur is not None:
            cur.lines.append(s)
            cur.last = i
        elif HEADLIKE_RE.match(s) and len(s) < 60:
            misses[s] += 1
    close()
    return entries, misses


def build_rows(jname, ents):
    rows = []
    groups, pend = [], []
    for e in ents:
        txt = join_lines(e.lines)
        if pend and (pend[-1][0].date, pend[-1][0].section) != (e.date, e.section):
            groups.extend([x] for x in pend)
            pend = []
        pend.append((e, txt))
        # a caption-only entry ending '; and' (printed group) joins the next entry
        if not VERB_RE.search(txt) and len(txt) < 600 and re.search(r'(?:;|; and\.?|, and)$', txt):
            continue
        groups.append(pend)
        pend = []
    groups.extend([x] for x in pend)
    for gg in groups:
        e0, el = gg[0][0], gg[-1][0]
        caps = [t for _, t in gg[:-1]]
        cap, body = split_caption(gg[-1][1])
        caps.append(cap)
        dockets = []
        for c in caps:
            for pair in DOCK_IN_CAP_RE.findall(' ' + c):
                for d in pair:
                    d = ascii_docket(d)
                    if d and d not in dockets:
                        dockets.append(d)
        basis = body if body else gg[-1][1]
        cls = classify(basis, el.section)
        cm = COURT_RE.search(gg[-1][1])
        if not cm:
            cm = REMAND_TO_RE.search(basis)
        court = cm.group(1) if cm else '-'
        caption_plain = ' '.join(re.sub(NO_PREFIX, '', c) for c in caps).strip()
        caption_plain = re.sub(r'\.$', '', caption_plain)
        rows.append({
            'journal': jname, 'first': e0.first, 'last': max(el.last, el.first), 'date': el.date,
            'datehead': el.datehead, 'section': el.section or '-', 'dockets': dockets, 'cls': cls,
            'caption': caption_plain or '-', 'court': court, 'disp': disposition_words(basis, cls),
            'caplines': caps, 'body': body,
        })
    return rows


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    rows = []
    misses_all = collections.Counter()
    for path in sys.argv[2:]:
        jname = os.path.splitext(os.path.basename(path))[0]
        ents, misses = parse(path)
        misses_all.update(misses)
        rows.extend(build_rows(jname, ents))
    with open(os.path.join(out, 'entries.jsonl'), 'w', encoding='utf-8', newline='\n') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    with open(os.path.join(out, 'entries.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('journal\tline_span\tdate\tsection\tdockets\tclass\tcaption\tcourt\tdisposition\n')
        for r in rows:
            f.write('\t'.join([r['journal'], '%d-%d' % (r['first'], r['last']), r['date'] or '-', r['section'],
                               ';'.join(r['dockets']) or '-', r['cls'], r['caption'], r['court'], r['disp']]) + '\n')
    with open(os.path.join(out, 'heading_misses.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        for k, v in misses_all.most_common():
            f.write('%d\t%s\n' % (v, k))
    c = collections.Counter((r['date'][:4] if r['date'] else '-', r['cls']) for r in rows)
    for k in sorted(c):
        print(k[0], k[1], c[k])


if __name__ == '__main__':
    main()
