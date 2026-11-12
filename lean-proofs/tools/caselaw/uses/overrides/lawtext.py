"""Law texts: plain text of each cached PLAW htm, the cases it names, its citations to reports, override language."""
import html, os, re
O = os.path.expanduser('~/Documents/us-caselaw-lean-work/uses/overrides')
def plaw_path(lab):
    m = re.fullmatch(r'Pub\. L\. (\d+)-(\d+)', lab)
    return f'{O}/cache/plaw/PLAW-{m.group(1)}publ{m.group(2)}.htm' if m else None
def text(lab):
    p = plaw_path(lab)
    if not p or not os.path.exists(p): return None
    s = open(p, encoding='utf-8', errors='replace').read()
    s = html.unescape(re.sub(r'<[^>]+>', ' ', s))
    s = re.sub(r'\[\[Page [^\]]*\]\]', ' ', s)
    s = re.sub(r'<<NOTE:[^>]*>>', ' ', s)
    s = s.replace('``', '"').replace("''", '"')
    s = re.sub(r'-\s*\n\s*', '-', s)  # hyphen breaks at line ends keep the hyphen
    return re.sub(r'\s+', ' ', s)
CONN = {'of', 'the', 'and', '&', 'for', 'de', 'ex', 'rel.', 'rel', 'du', 'la', 'in', 'on', 'to'}
TOK = re.compile(r"[A-Z][\w'’.\-]*,?|&|of|the|and|for|ex|rel\.|de|du|la|in|on|to")
def _left(words):
    out = []
    for w in reversed(words):
        if TOK.fullmatch(w) and not w.endswith(',') or (w.endswith(',') and out == [] and False):
            out.append(w)
        elif w.endswith(',') and re.fullmatch(r"[A-Z][\w'’.\-]*,", w):
            out.append(w)
        else:
            break
        if len(out) >= 8: break
    while out and out[-1].lower() in CONN: out.pop()
    return list(reversed(out))
def _right(words):
    out = []
    for w in words:
        if TOK.fullmatch(w): out.append(w)
        else: break
        if len(out) >= 10: break
    while out and out[-1].lower().rstrip(',') in CONN: out.pop()
    return out
CITE = re.compile(r'\b(\d{1,4}) (U\.S\.|S\. ?Ct\.|F\.(?: ?[234]d| ?4th)?|F\. ?Supp\.(?: ?[23]d)?|B\.R\.|T\.C\.|Fed\. ?Cl\.|M\.J\.|Vet\. ?App\.) (\d{1,5})\b')
def named_cases(t):
    """[(left party, right party, offset)] for every 'X v. Y' in the text."""
    out = []
    for m in re.finditer(r' v\. ', t):
        L = _left(t[max(0, m.start() - 160):m.start()].split())
        R = _right(t[m.end():m.end() + 200].split())
        if L and R:
            out.append((' '.join(L), ' '.join(R), m.start()))
    return out
def cites(t):
    return [(f'{a} {re.sub(" ", "", b)} {c}', m.start()) for m in CITE.finditer(t) for a, b, c in [m.groups()]]
OVR = re.compile(r"Supreme Court|the [Cc]ourt (?:in|held|of Appeals)|[Cc]ourt decisions?|decision of the|decision in|holding (?:of|in)|"
                 r"overrul|overturn|supersed|abrogat|in response to|to reverse|reject(?:s|ed)? the|"
                 r"restor(?:e|es|ing) the|clarif(?:y|ies|ying)|notwithstanding (?:any|the) (?:decision|holding|ruling)|"
                 r"interpretation (?:of|by) the|narrowly interpreted|misinterpret|contrary to the intent of Congress|intent of Congress")
STRONG = re.compile(r"Supreme Court|the [Cc]ourt in |decision (?:of|in) |holding (?:of|in) |overrul|overturn|supersed|abrogat|"
                    r"contrary to the intent of Congress|narrowly interpreted|misinterpret|reject(?:s|ed)? the (?:reasoning|holding|interpretation)")
REPORTS = re.compile(r'(HOUSE|SENATE) REPORTS?: ((?:Nos?\. )?[\d\-, and]+(?:\s*\(|\s|$))')
def reports(raw_text):
    """Report numbers listed in the law's LEGISLATIVE HISTORY note: [('h', '110', '237'), ...]"""
    out = []
    i = raw_text.find('LEGISLATIVE HISTORY')
    if i < 0: return out
    seg = raw_text[i:i + 3000]
    for m in re.finditer(r'(HOUSE|SENATE) REPORTS?:(.*?)(?=(?:HOUSE|SENATE) REPORTS?:|CONGRESSIONAL RECORD|SENATE|HOUSE|$)', seg):
        for c, n in re.findall(r'(\d{3})-(\d+)', m.group(2)):
            out.append(('h' if m.group(1) == 'HOUSE' else 's', c, n))
    return out
