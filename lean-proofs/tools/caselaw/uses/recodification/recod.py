"""Shared helpers for the recodification checks: the record (git), section keys, and the disposition-table grammar."""
import os, re, subprocess, collections

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.normpath(os.path.join(HERE, '..'))
DATA = os.path.join(BASE, 'data')
GIT = os.path.normpath(os.path.join(BASE, '..', '..', 'usc-full.git'))

# title restated, law, in-force day, first record commit holding the new title when the restatement day is not in it
RESTATEMENTS = [
    (36, 'Pub. L. 105-225', 19980812),
    (40, 'Pub. L. 107-217', 20020821),
    (46, 'Pub. L. 109-304', 20061006),
    (51, 'Pub. L. 111-314', 20101218),
    (41, 'Pub. L. 111-350', 20110104),
    (54, 'Pub. L. 113-287', 20141219),
]


def git(*a):
    return subprocess.run(['git', '--git-dir', GIT] + list(a), capture_output=True, text=True, encoding='utf-8').stdout


_log = {}


def title_log(t):
    """Commits touching title-t in first-parent order: (sha, day, author, subject). Per title, days are monotonic."""
    if t not in _log:
        out = git('log', '--first-parent', '--reverse', '--format=%H\t%ad\t%an\t%s', '--date=format:%Y%m%d',
                  'main', '--', f'title-{t}')
        _log[t] = [tuple(l.split('\t', 3)[:2]) + tuple(l.split('\t', 3)[2:]) for l in out.splitlines() if l]
        _log[t] = [(s, int(d), a, sub) for s, d, a, sub in _log[t]]
    return _log[t]


def commit_on(t, day):
    """The record's commit holding title t as in force on `day` (last commit touching it dated on or before)."""
    best = None
    for s, d, a, sub in title_log(t):
        if d <= day:
            best = s
        else:
            break
    return best


_tree = {}


def sections(t, commit):
    """{section id: blob sha} for title t at commit."""
    k = (t, commit)
    if k not in _tree:
        out = git('ls-tree', commit, f'title-{t}/') if commit else ''
        m = {}
        for l in out.splitlines():
            meta, path = l.split('\t')
            sec = path.split('/', 1)[1][:-3]
            m[sec] = meta.split()[2]
        _tree[k] = m
    return _tree[k]


class Blobs:
    def __init__(self):
        self.p = subprocess.Popen(['git', '--git-dir', GIT, 'cat-file', '--batch'], stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE)
        self.cache = {}

    def get(self, sha):
        if sha in self.cache:
            return self.cache[sha]
        self.p.stdin.write((sha + '\n').encode())
        self.p.stdin.flush()
        hdr = self.p.stdout.readline().split()
        n = int(hdr[2])
        body = self.p.stdout.read(n)
        self.p.stdout.read(1)
        s = body.decode('utf-8')
        self.cache[sha] = s
        return s


# ---- section keys -------------------------------------------------------------------------------------------------
TOK = re.compile(r'\d+|[A-Za-z]+')


def skey(s):
    return tuple((0, int(x)) if x.isdigit() else (1, x.lower()) for x in TOK.findall(s))


def in_range(s, a, b):
    ks, ka, kb = skey(s), skey(a), skey(b)
    return ka <= ks and (ks <= kb or ks[:len(kb)] == kb)


SEC = r'\d+[A-Za-z]*(?:-\d+[A-Za-z]*)*'


def depth0(s):
    out, d = [], 0
    for ch in s:
        if ch == '(':
            d += 1
        elif ch == ')':
            d = max(0, d - 1)
        elif d == 0:
            out.append(ch)
    return ''.join(out)


def parse_left(left, title, known):
    """A former-section cell -> (source title, kind, [('one', s) | ('range', a, b)]). kind 'sec' or 'note'.
    `known(src, s)` says whether section id s exists at the old location in the record (resolves '1a-1' vs '8-13')."""
    src = str(title)
    txt = left.strip()
    m = re.match(r'^(\d+) U\.S\.C\. (.*)$', txt)
    if m:
        src, txt = m.group(1), m.group(2)
    m = re.match(r'^T\. (\d+) App\. §+\s*(.*)$', txt)
    if m:
        src, txt = m.group(1) + 'A', m.group(2)
    m = re.match(r'^T\. (\d+) §+\s*(.*)$', txt)
    if m:
        src, txt = m.group(1), m.group(2)
    txt = re.sub(r'\)\s*(?:-|to|through)\s*\(', '),(', txt)
    t0 = depth0(txt)
    items = []
    for piece in re.split(r',|\band\b', t0):
        piece = piece.strip().rstrip('.')
        if not piece or re.search(r'\bnotes?\b', piece):
            continue
        m = re.match(rf'^({SEC})\s+(?:to|through)\s+({SEC})$', piece)
        if m:
            items.append(('range', m.group(1), m.group(2)))
            continue
        m = re.match(rf'^({SEC})$', piece)
        if not m:
            continue
        s = m.group(1)
        if '-' in s and not known(src, s):
            parts = s.split('-')
            # a range a-b, or a hyphenated section id: a range when the right part starts at or after the left
            a, b = '-'.join(parts[:-1]), parts[-1]
            if len(parts) == 2 and skey(b)[:1] >= skey(a)[:1] and skey(b) > skey(a):
                items.append(('range', a, b))
                continue
        items.append(('one', s))
    kind = 'sec' if items else 'note'
    if kind == 'note':  # a note-only row: keep the section the note sits under, for the record
        m = re.match(rf'^\s*({SEC})', t0)
        items = [('one', m.group(1))] if m else []
    return src, kind, items


REASONS = [
    (r'previously repealed', 'previously repealed'),
    (r'previously transferred', 'previously transferred'),
    (r'not repealed but omitted', 'omitted, not repealed'),
    (r'outside (the )?scope', 'outside the scope of the codification'),
    (r'as obsolete', 'repealed as obsolete'),
    (r'as unnecessary', 'repealed as unnecessary'),
    (r'^rep\b|^repealed', 'repealed'),
    (r'^elim', 'eliminated'),
    (r'omitted', 'omitted'),
    (r'expired', 'expired'),
    (r'executed', 'executed'),
    (r'superseded', 'superseded'),
]


def parse_right(right, title):
    """A disposition cell -> ('map', [(title, sec or ('range', a, b), is_note)]) | ('omit', reason)
    | ('see_former', s) | ('act', text) | ('unknown', text)."""
    r = right.strip()
    low = r.lower().strip('() ')
    if not low or set(low) <= set('. '):
        return ('unknown', r)
    low = re.sub(rf'^\(?see {title}:', '(see former ', low)  # "(See 36:1101)": the former section 1101
    m = re.match(rf'^\(?see former ({SEC})\)?$', low)
    if m:
        return ('see_former', m.group(1))
    if re.search(r'see §\s*\S+ of bill', low) or re.match(r'^sec\. \S+ of pub\. l\.', low):
        return ('act', r)
    for pat, reason in REASONS:
        if re.search(pat, low):
            return ('omit', reason)
    if 'transfer' in low:
        pass
    low2 = re.sub(r'^\(?see\s+', '', low).rstrip(')').strip()
    low2 = re.sub(r'^transfer to\s+', '', low2)
    low2 = low2.replace('d.c. official code', 'DC')
    if 'DC' in low2:
        return ('omit', 'moved to the D.C. Official Code')
    targets = []
    cur_t = title
    # split on ';' and ',' but keep "T. N §" / "N U.S.C." prefixes as the running title
    for piece in re.split(r'[;,]', low2):
        p = piece.strip()
        if not p:
            continue
        m = re.match(r'^t\. (\d+) §+\s*(.*)$', p)
        if m:
            cur_t, p = int(m.group(1)), m.group(2)
        m = re.match(r'^(\d+)\s*:\s*(.*)$', p)
        if m:
            cur_t, p = int(m.group(1)), m.group(2)
        m = re.match(r'^(\d+) u\.s\.c\. (.*)$', p)
        if m:
            cur_t, p = int(m.group(1)), m.group(2)
        p = p.strip().rstrip('.')
        note = bool(re.search(r'notes?\b', p))
        p = re.sub(r'notes?\b.*$', '', p).replace('prec.', '').strip()
        p = depth0(p).strip()
        m = re.match(rf'^({SEC})\s+(?:to|through)\s+({SEC})$', p)
        if m:
            targets.append((cur_t, ('range', m.group(1), m.group(2)), note))
            continue
        m = re.match(rf'^({SEC})', p)
        if m:
            targets.append((cur_t, m.group(1), note))
        elif note and targets == [] and p == '':
            targets.append((cur_t, '', True))
    if targets:
        return ('map', targets)
    return ('unknown', r)


STOP = set("""the and for any that such this with from shall may under each not have has been are was were which
who whom their its his her other than such into upon all also any but only out over such then there these those
under where whether while within without being made make makes any said same section sections subsection
paragraph subparagraph clause title chapter subchapter part act law laws united states code provided provision
provisions apply applies applied following described referred term terms means mean including include includes""".split())
NUMW = {w: i for i, w in enumerate("zero one two three four five six seven eight nine ten eleven twelve thirteen "
                                   "fourteen fifteen sixteen seventeen eighteen nineteen twenty".split())}
NUMW.update({'thirty': 30, 'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90,
             'hundred': 100, 'thousand': 1000})
MONTHS = 'january february march april may june july august september october november december'.split()
FOLD = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"', "—": "-", "–": "-", " ": " "})


def body(md):
    """Statute words of a record file: drop the heading line and list bullets."""
    lines = md.translate(FOLD).split('\n')
    if lines and lines[0].startswith('#'):
        lines = lines[1:]
    return '\n'.join(re.sub(r'^\s*-\s+', '', l) for l in lines)


def words(text):
    out = set()
    for w in re.findall(r"[A-Za-z][A-Za-z'-]+", text):
        w = w.lower().strip("'-")
        if len(w) < 3 or w in STOP or w in NUMW:
            continue
        if w.endswith('ies') and len(w) > 5:
            w = w[:-3] + 'y'
        elif w.endswith('s') and not w.endswith('ss') and len(w) > 4:
            w = w[:-1]
        out.add(w)
    return out


REFCTX = re.compile(r"(section|sections|§+|title|titles|chapter|chapters|subchapter|subchapters|part|parts|subtitle|"
                    r"subtitles|stat\.?|pub\.?|l\.|u\.s\.c\.?|note|notes|paragraph|paragraphs|subsection|subsections|"
                    r"clause|clauses|no\.?|division|article|articles|act|reorganization|plan|ch\.?|sec\.?|app\.?|"
                    r"and|or|to|through|of|e\.o\.|order|executive|public|law|item|items|annex)$", re.I)


def number_words(text):
    """Number words to digits: 'twenty-five' -> 25, 'thirty' -> 30 (simple cases only)."""
    def rep(m):
        a = m.group(1).lower()
        b = (m.group(2) or '').lower()
        if a in NUMW and (not b or b in NUMW):
            return str(NUMW[a] + (NUMW[b] if b else 0))
        return m.group(0)
    return re.sub(r"\b([A-Za-z]+)(?:-([A-Za-z]+))?\b", rep, text)


def numbers(text):
    """Substantive numbers: amounts ($), percents, dates/years, counts and periods. Skips numbers used as references
    to other provisions or laws (after 'section', 'title', 'Stat.', 'Pub. L.', 'U.S.C.', inside '(15 U.S.C. 631)')."""
    t = text.translate(FOLD)
    # drop citations in parentheses that name the Code or Stat
    t = re.sub(r'\([^()]*(U\.S\.C\.|Stat\.|Pub\. ?L\.|note)[^()]*\)', ' ', t)
    t = number_words(t)
    out = collections.Counter()
    toks = re.findall(r"\$?\d[\d,]*(?:\.\d+)?%?|[A-Za-z§.]+|\S", t)
    prev = []
    for i, tok in enumerate(toks):
        if re.match(r"\$?\d", tok):
            raw = tok.rstrip(',')
            # a run of references: "sections 101, 102, and 103"
            back = [p for p in prev[-3:]]
            is_ref = any(REFCTX.match(p) for p in back[-1:]) or (len(back) >= 2 and REFCTX.match(back[-2]) and back[-1] in (',', '(', 'and'))
            if raw.startswith('$'):
                is_ref = False
            nxt = toks[i + 1] if i + 1 < len(toks) else ''
            if nxt in ('U.S.C.', 'Stat.', 'U.S.C', 'Stat'):
                is_ref = True
            if prev and prev[-1] == '(' and nxt == ')':
                is_ref = True  # a designation such as "(10)", not a quantity
            if not is_ref:
                v = raw.replace(',', '')
                cls = 'amount' if raw.startswith('$') else 'percent' if raw.endswith('%') or nxt.lower() in (
                    'percent', 'per') else 'year' if re.fullmatch(r'1[6-9]\d\d|20\d\d', v) and not any(
                    p.lower() in ('section', 'sections', '§') for p in back) else 'number'
                if prev and prev[-1].lower() in MONTHS:
                    cls = 'date'
                out[(cls, v.lstrip('$').rstrip('%'))] += 1
            prev.append('N')
        else:
            prev.append(tok)
    return out


def name_tokens(text):
    """Capitalized words not at a sentence start (named entities: people, places, bodies)."""
    out = set()
    for m in re.finditer(r"(?<![.:;]\s)(?<!^)\b([A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,})*)", text, re.M):
        for w in m.group(1).split():
            lw = w.lower()
            if lw in STOP or lw in MONTHS or lw in ('secretary', 'administrator', 'congress', 'president', 'federal',
                                                   'government', 'state', 'states', 'united', 'board', 'commission',
                                                   'director', 'attorney', 'general'):
                continue
            out.add(lw)
    return out


PLACEHOLDER = re.compile(r'^#[^\n]*?§+\s*\S+?\.?\s+\[?(Repealed|Transferred|Omitted|Renumbered|Reserved|Expired|Terminated)\b')
_blobs = None


def blob_text(sha):
    global _blobs
    if _blobs is None:
        _blobs = Blobs()
    return _blobs.get(sha)


def in_force(t, commit):
    """{section: blob} for title t at commit, leaving out status placeholders ('Repealed.', 'Transferred', ...)."""
    return {s: b for s, b in sections(t, commit).items() if not PLACEHOLDER.match(blob_text(b))}
