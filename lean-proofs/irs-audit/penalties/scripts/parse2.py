#!/usr/bin/env python3
"""Extract the IRS's determination (deficiency and penalties/additions per tax year) from the opening of each sampled
Tax Court opinion. Tables and prose; anything ambiguous is left unparsed (counted, not guessed)."""
import os, re, json, glob, collections
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/penalties')
AMT = r'\$\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?|\$\s?\d+(?:\.\d{2})?'
SEC = r'(66(?:51|53|54|55|59|61|62|63|64|73)A?(?:\s?\([a-zA-Z0-9]{1,3}\))*)'
NULL = re.compile(r'^(?:[-–—]+|[-–—]0[-–—]|N/?A|none|0|\$?0\.00)$', re.I)


def amt(s):
    s = s.replace('$', '').replace(',', '').strip()
    try:
        return round(float(s), 2)
    except ValueError:
        return None


def normsec(s):
    return re.sub(r'\s', '', s)


def clean(t):
    return re.sub(r'\n\s*-\s*\d+\s*-\s*\n', '\n', t)


def section_list(s):
    return [normsec(x) for x in re.findall(SEC, s)]


def parse_table(W):
    lines = W.split('\n'); recs = []; secs = []; started = False; hdr = []
    for ln in lines:
        is_row = re.match(r'^\s*(?:.*?\s{2,})?(?:TYE\s*|FYE\s*|\d{1,2}/\d{1,2}/)?((?:19|20)\d\d)\s{2,}(\$?[\d,]+|[-–—])', ln)
        if not is_row and (re.search(r'Deficienc', ln, re.I) or re.search(SEC, ln)):
            if started and re.search(r'Deficienc', ln, re.I):
                secs = []; hdr = []; started = False
            hdr.append(ln); secs += section_list(ln); continue
        m = re.match(r'^\s*(?:.*?\s{2,})?(?:TYE\s*|FYE\s*|\d{1,2}/\d{1,2}/)?((?:19|20)\d\d)\b(.*)$', ln)
        if m and hdr:
            rest = m.group(2)
            toks = [x for x in re.split(r'\s{2,}|\s(?=\$)', rest.strip()) if x.strip()]
            vals = []
            for x in toks:
                x = x.strip().rstrip('*').strip()
                if re.match(r'^\$?[\d,]+(?:\.\d\d)?\s\d$', x):
                    x = x[:-2]
                if NULL.match(x):
                    vals.append(None)
                elif re.match(r'^\$?\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?$|^\$?\d+(?:\.\d{1,2})?$', x):
                    vals.append(amt(x))
                elif re.match(r'^\(?[a-z0-9]\)?$', x):
                    continue
                else:
                    vals = 'bad'; break
            if vals == 'bad' or not vals:
                continue
            started = True
            if not secs:
                continue
            y = int(m.group(1))
            if len(vals) == 1 + len(secs):
                recs.append(dict(year=y, deficiency=vals[0], pen={s: v for s, v in zip(secs, vals[1:]) if v is not None}, src='table'))
            elif len(vals) == 1:
                recs.append(dict(year=y, deficiency=vals[0], pen={}, src='table', note='no penalty values'))
            else:
                recs.append(dict(year=y, deficiency=vals[0], pen=None, src='table', note='column mismatch %d vs %d' % (len(vals), 1 + len(secs))))
        elif started and ln.strip() and not re.search(r'\d', ln) and len(ln.strip()) > 60:
            break
    return recs


LIST = r'((?:%s)(?:\s*(?:,|,?\s*and)\s*(?:%s))*)' % (AMT, AMT)


def amts(s):
    return [amt(x) for x in re.findall(AMT, s)]


def years(s):
    r = re.search(r'((?:19|20)\d\d)\s*(?:through|to)\s*((?:19|20)\d\d)', s)
    if r:
        a, b = r.groups(); return list(range(int(a), int(b) + 1))
    ys = [int(y) for y in re.findall(r'(?<![\d$,.])((?:19|20)\d\d)(?!\d)(?!,\d)', s)]
    return [y for y in dict.fromkeys(ys) if 1950 < y < 2030]


def prep(W):
    W = re.sub(r'\s+', ' ', W)
    W = re.sub(r' ([.,;:)])', r'\1', W)               # OCR: "$1,341,246 .80", "2000 ."
    W = re.sub(r'\bsectio n\b', 'section', W)
    W = re.sub(r'(\d) \.(\d\d)\b', r'\1.\2', W)
    W = re.sub(r' - \d+ - ', ' ', W)
    stop = re.search(r'issues? (?:for|to be|remaining for) (?:decision|decided)|After concessions|FINDINGS OF FACT|Background|we must decide|The parties|Unless otherwise|The sole issue|The issue|At the time of trial|Subsequently|[Ii]n (?:an|his|its) amend\w* (?:to )?(?:the )?answer|amended answer|asserted an increased|amendment to (?:the )?answer|increasing (?:the|its|his|her|petitioner)|Respondent now|respondent has since|Thereafter', W)
    S = W[:stop.start()] if stop else W[:1500]
    S = re.sub(r'(section\s+66\d\d(?:\([a-z0-9]+\))*)\d\b', r'\1', S)
    S = re.sub(r'\b(sec|secs|Sec)\. ', r'section ', S)
    S = re.sub(r'(accuracy-related penalt(?:y|ies))(?! (?:under|pursuant to) section)', r'\1 under section 6662(a)', S)
    S = re.sub(r'(fraud penalt(?:y|ies))(?! (?:under|pursuant to) section)', r'\1 under section 6663', S)
    return S


def parse_respective(S):
    """'... determined a deficiency in, an addition under section X to, and a penalty under section Y on ... tax for
    that year in the respective amounts of $A, $B, and $C' (one year per sentence)."""
    recs = []
    for sent in re.split(r'(?<=[a-z0-9)])\. (?=[A-Z])', S):
        m = re.search(r'deficienc(.{0,400}?)respective amounts of ' + LIST, sent, re.I)
        ys = years(re.sub(AMT, '', sent))
        if not m or len(ys) != 1:
            continue
        secs = section_list(m.group(1)); vals = amts(m.group(2))
        if len(vals) == 1 + len(secs):
            recs.append(dict(year=ys[0], deficiency=vals[0], pen=dict(zip(secs, vals[1:])), src='prose-respective'))
    return recs


def parse_prose(W, depth=0):
    S = prep(W) if depth == 0 else W
    r = parse_respective(S)
    if r:
        return r, 'ok'
    if depth == 0:
        sents = [s for s in re.split(r'(?<=[a-z0-9)])\. (?=[A-Z])', S) if re.search(r'deficienc', s, re.I) and re.search(r'determin', s) and re.search(AMT, s)]
        if len(sents) >= 2 and all(len(years(re.sub(AMT, '', s))) == 1 for s in sents):
            acc = []
            for s in sents:
                rr, why = parse_prose(s, 1)
                if why == 'ok':
                    acc += rr
            if acc and len({x['year'] for x in acc}) == len(acc) == len(sents):
                return acc, 'ok'
    allyears = [y for y in years(re.sub(AMT, '', S)) if 1950 < y < 2030]
    if not allyears:
        return [], 'no years'
    m = re.search(r'deficienc(?:y|ies)[^$]{0,160}?' + LIST, S, re.I)
    m2 = re.search(r'(%s)\s+(?:income tax |Federal income tax |gift tax |estate tax )?deficiency' % AMT, S, re.I)
    if m2 and (not m or m2.start() < m.start()):
        D = amts(m2.group(1)); after = S[m2.end():m2.end() + 120]
    elif m:
        D = amts(m.group(1)); after = S[m.end():m.end() + 120]
    else:
        return [], 'no deficiency'
    dy = years(after.split('$')[0]) if after else []
    if len(dy) != len(D):
        dy = allyears if len(allyears) == len(D) else []
    if len(D) == 1 and len(dy) != 1:
        fy = re.search(r'(?:for|For|taxable year|tax year|year)\s+(?:the\s+)?(?:taxable\s+)?(?:\(calendar\)\s+)?(?:year\s+)?((?:19|20)\d\d)\b(?!,\d)', S)
        if fy:
            dy = [int(fy.group(1))]
    if len(dy) != len(D) and depth == 0:
        # one year per sentence ("As to 1994, respondent determined ... For 1995, ...")
        acc = []
        for sent in re.split(r'(?<=[a-z0-9)])\. (?=[A-Z])', S):
            if len(years(re.sub(AMT, '', sent))) == 1 and re.search(r'deficienc', sent, re.I):
                r, why = parse_prose(sent, 1)
                if why == 'ok':
                    acc += r
        if acc and len({r['year'] for r in acc}) == len(acc):
            return acc, 'ok'
    if len(dy) != len(D):
        return [], 'years/deficiency mismatch'
    recs = {y: dict(year=y, deficiency=d, pen={}, src='prose') for y, d in zip(dy, D)}
    Dset = set(D)
    for pm in re.finditer(r'(?:section|sec\.|sections)\s+' + SEC, S):
        sec = normsec(pm.group(1)); tail = S[pm.end():pm.end() + 220]
        lm = re.match(r'[^$]{0,110}?' + LIST, tail)
        nxt = re.search(r'(?:section|sec\.)\s+66\d\d', tail)
        if lm and re.search(r'\. [A-Z]', tail[:lm.start(1)]):
            lm = None
        if lm and (not nxt or nxt.start() > lm.start(1)):
            P = amts(lm.group(1)); py = years(tail[lm.end():lm.end() + 90].split('$')[0])
            if not py:
                py = years(tail[:lm.start(1)])
        else:
            pre = S[max(0, pm.start() - 160):pm.start()]
            pa = re.findall(AMT, pre)
            if not pa:
                continue
            gap = pre.split(pa[-1])[-1]
            if re.search(r'section|sec\.|deficienc', gap, re.I) or len(gap) > 90 or re.search(r'[a-z0-9)]\.\s+[A-Z]', gap):
                continue
            P = [amt(pa[-1])]; py = []
        if len(py) != len(P):
            py = dy if len(dy) == len(P) else []
        if len(py) != len(P):
            return list(recs.values()), 'penalty years mismatch'
        for y, p in zip(py, P):
            if y in recs and p is not None and p not in Dset:
                recs[y]['pen'][sec] = p
    return list(recs.values()), 'ok'


def body(t):
    m = re.search(r'(?:Judge|JUDGE)\s*:', t)
    return t[m.end():] if m else t



# ---------------------------------------------------------------- v2 additions (run 2)
from multiprocessing import Pool
INV = {o['pick']: o for o in json.load(open(H + '/data2/inventory.json'))}
SECT = '§'


def padsub(pat, fn, s, flags=0):
    """Regex substitution that keeps the line length (pads with spaces) so table columns stay aligned."""
    def r(m):
        new = fn(m); old = m.group(0)
        return new + ' ' * max(0, len(old) - len(new))
    return re.sub(pat, r, s, flags=flags)


def norm_line(ln):
    ln = padsub(r'((?:[Ss]ec(?:tion)?s?|SEC(?:TION)?S?|I\.?R\.?C\.?)\s?\.?\s*§?\s*|§\s*)6\s?6\s?(\d)\s?(\d)(?!\d)',
                lambda m: m.group(1).replace(' ', '') + ' 66' + m.group(2) + m.group(3), ln)
    ln = padsub(r'(66\d\d)\s+\(', lambda m: m.group(1) + '(', ln)
    ln = padsub(r'\(\s+([a-zA-Z0-9]{1,3})\s*\)|\(([a-zA-Z0-9]{1,3})\s+\)', lambda m: '(' + (m.group(1) or m.group(2)) + ')', ln)
    ln = padsub(r'\$\s+(?=\d)', lambda m: '$', ln)
    ln = padsub(r'(\d) \.(\d\d)\b', lambda m: m.group(1) + '.' + m.group(2), ln)
    ln = padsub(r'(\d) ,(\d{3})', lambda m: m.group(1) + ',' + m.group(2), ln)
    ln = padsub(r'(\d{1,3},\d{2}) (\d)\b(?![,.]\d)', lambda m: m.group(1) + m.group(2), ln)
    ln = padsub(r'(\d{1,3},) (\d{3})\b', lambda m: m.group(1) + m.group(2), ln)
    return ln


JUNK = re.compile(r'^\s*(?:SERVED\b.*|-+\s*\d+\s*-+|\[\*\d+\]|\*?\d{1,3}\s*|Docket No\..*Filed.*)$')


def clean_lines(t, bench):
    out = []
    for ln in t.split('\n'):
        if bench:
            ln = re.sub(r'^\s{0,8}\d{1,2}(?=\s|$)', lambda m: ' ' * len(m.group(0)), ln)
        ln = re.sub(r'^(\s*)\[\*\d+\]\s?', lambda m: m.group(1), ln)
        ln = re.sub(r'SERVED\s+[A-Z][A-Za-z]{2}\s*-?\s*[\d ]{1,4}\s*\d{4}', '', ln)
        if JUNK.match(ln):
            continue
        out.append(norm_line(ln))
    return out


SECX = r'(?:[Ss]ec(?:tion)?s?\.?\s*|§\s*|I\.?R\.?C\.?\s*§?\s*)?(66(?:51|53|54|55|59|61|62|63|64|73)A?(?:\([a-zA-Z0-9]{1,3}\))*)'
VAL = re.compile(r'(?<![\w.,$])(?:\$?\d{1,3}(?:,\d{3})+(?:\.\d{1,2})?|\$?\d+\.\d{1,2}|\$?\d+|-0-|[-–—]{1,6}|None|N/A)(?![\w,])')
ROW = re.compile(r'^\s*(?:TYE\s*|FYE\s*|\d{1,2}/\d{1,2}/)?((?:19|20)\d\d)\b')


def anchors(hdr, gen=None):
    """Column anchors from header lines: [(center, key)], key = 'D' for deficiency or a section.
    Prose lines (6+ single-spaced words, or ending in ':') are not headers. A bare 'Penalty'/'Addition' column takes
    `gen` (the one penalty type the determination sentence names) or 'GEN' (unknown)."""
    hdr = [ln for ln in hdr if not re.search(r"(?:[A-Za-z,'’().-]+ ){6,}", ln.strip()) and not ln.rstrip().endswith(':')]
    A = []
    for ln in hdr:
        for m in re.finditer(r'Deficienc\w*', ln, re.I):
            A.append(((m.start() + m.end()) / 2, 'D'))
        for m in re.finditer(SECX, ln):
            A.append(((m.start(1) + m.end(1)) / 2, normsec(m.group(1))))
    words = []
    for ln in hdr:
        for m in re.finditer(r'Accuracy|Fraud|Negligence', ln, re.I):
            c = (m.start() + m.end()) / 2
            if all(abs(c - a) > 10 for a, _ in A):
                words.append((c, {'a': '6662(a)', 'f': '6663', 'n': '6662(a)'}[m.group(0)[0].lower()]))
    for ln in hdr:
        for m in re.finditer(r'Penalt\w*|Additions?(?: to [Tt]ax)?', ln):
            c = (m.start() + m.end()) / 2
            if all(abs(c - a) > 10 for a, _ in A + words):
                words.append((c, gen or 'GEN'))
    A = sorted(A + words)
    out = []
    for c, k in A:
        if out and abs(out[-1][0] - c) < 4 and out[-1][1] == k:
            continue
        out.append((c, k))
    return out


def gen_of(Wflat):
    """The single penalty type named in the determination sentence(s), for a bare 'Penalty' column."""
    s = Wflat[:500]
    kinds = set()
    if re.search(r'accuracy|6662\(a\)|negligence', s, re.I): kinds.add('6662(a)')
    if re.search(r'fraud penalt|6663', s, re.I): kinds.add('6663')
    if re.search(r'6662\(h\)', s): kinds.add('6662(h)')
    if re.search(r'6651|addition', s, re.I): kinds.add('6651')
    if re.search(r'6654', s): kinds.add('6654')
    return kinds.pop() if len(kinds) == 1 and '6651' not in kinds else None


def parse_table_pos(lines, gen=None):
    recs = []; i = 0; n = len(lines)
    while i < n:
        m = ROW.match(lines[i])
        if not m:
            i += 1; continue
        hdr = []; j = i - 1
        while j >= 0 and len(hdr) < 6:
            if lines[j].strip():
                rj = ROW.match(lines[j])
                if rj and VAL.search(lines[j], rj.end()):
                    break
                hdr.insert(0, lines[j])
            j -= 1
        A = anchors(hdr, gen)
        if not any(k == 'D' for _, k in A) or not any(k != 'D' for _, k in A):
            i += 1; continue
        k = i
        while k < n:
            ln = lines[k]
            rm = ROW.match(ln)
            if not rm:
                if not ln.strip():
                    k += 1; continue
                if re.search(r'Deficienc', ln, re.I) or len(ln.strip()) > 55 or not re.search(r'\d', ln):
                    break
                k += 1; continue
            rest = ln[rm.end():]
            if re.search(r'[A-Za-z]{2,}', re.sub(r'None|N/A|TYE|FYE', '', rest)) or not re.search(r'\d', rest):
                if len(ln.strip()) > 40: break
                k += 1; continue
            y = int(rm.group(1)); toks = []
            if re.search(r'\d,\s+\d{1,2}\b(?![,.]\d)|\d,\d{1,2}\b(?![,.]\d)', rest):
                recs.append(dict(year=y, deficiency=None, pen=None, src='table-pos', note='OCR-damaged amount'))
                k += 1; continue
            for v in VAL.finditer(ln, rm.end()):
                s = v.group(0)
                if re.fullmatch(r'\d', s):
                    continue  # footnote marker
                toks.append(((v.start() + v.end()) / 2, s))
            if not toks:
                k += 1; continue
            cols = {}; ok = True
            for c, s in toks:
                best = min(A, key=lambda a: abs(a[0] - c))
                if abs(best[0] - c) > 30 or best[1] in cols:
                    ok = False; break
                cols[best[1]] = s
            if not ok:
                vs = [s for _, s in toks]
                if len(vs) == len(A):
                    cols = {a[1]: s for a, s in zip(A, vs)}
                else:
                    recs.append(dict(year=y, deficiency=None, pen=None, src='table-pos', note='cell alignment failed'))
                    k += 1; continue
            d = cols.get('D')
            dv = None if (d is None or NULL.match(d.strip())) else amt(d)
            pen = {}
            if any(kk == 'GEN' and not NULL.match(s.strip()) for kk, s in cols.items()):
                recs.append(dict(year=y, deficiency=dv, pen=None, src='table-pos', note='unlabelled penalty column'))
                k += 1; continue
            for kk, s in cols.items():
                if kk == 'D' or kk == 'GEN' or NULL.match(s.strip()):
                    continue
                v = amt(s)
                if v is not None:
                    pen[kk] = v
            recs.append(dict(year=y, deficiency=dv, pen=pen, src='table-pos'))
            k += 1
        i = k + 1
    return recs


STAMP = re.compile(r'(?:Filed|FILED|Entered|ENTERED)\s+[A-Z][a-z]+\.?\s+\d{1,2},?\s+\d{4}|SERVED\s+[A-Z][A-Za-z]{2}\s*-?\s*[\d ]{1,4}\s*\d{4}')
DET = re.compile(r'(?:Respondent|respondent|Commissioner|IRS|Internal Revenue Service|notice|Notice)[^.]{0,160}?(?:determined|determining|asserted|determines)[^.]{0,220}?(?:deficienc|\$)|(?:determined|determining) (?:the following |a |an |deficienc)')


LSTOP = re.compile(r'issues? (?:for|to be|remaining for) (?:decision|decided)|After concessions|FINDINGS OF FACT|we must decide|The sole issue|At the time of (?:trial|filing)|amended answer|[Ii]n (?:an|his|its) amend\w* (?:to )?(?:the )?answer|asserted an increased|Respondent now|respondent has since|Thereafter|conceded|concedes|parties (?:have )?(?:agree|stipulat|settled)|petition(?:er|ers)? resided')


MONTHS = r'(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan\.|Feb\.|Mar\.|Apr\.|Aug\.|Sept?\.|Oct\.|Nov\.|Dec\.)'


def label_key(lab):
    if re.search(r'deficienc', lab, re.I) and not re.search(r'penalt|addition', lab.split('eficienc')[-1], re.I):
        return 'D'
    secs = re.findall(SEC, lab)
    if secs:
        return normsec(secs[-1])
    if re.search(r'accuracy', lab, re.I): return '6662(a)'
    if re.search(r'fraud penalt', lab, re.I): return '6663'
    return None


SENT_END = re.compile(r'(?<!No)(?<!sec)(?<!secs)(?<!Sec)(?<! v)(?<!Co)(?<!Inc)(?<! U\.S)\.[\d¹²³⁰-⁹]*\s+(?:\d{1,2}\s+)?(?=[A-Z(])')
POST = re.compile(r"\s*(?:(?:Federal|federal|income|tax|estate|gift|section|sec\.|66\d\d(?:\([a-z0-9]+\))*|IRC|I\.R\.C\.|§|accuracy-related|fraud|civil|late-filing|addition|additions|to)\s+){0,6}(deficienc|penalt|addition)", re.I)


def resp_sentence(s):
    """One sentence: lists of amounts with their labels (label before the list, or right after it)."""
    lists = list(re.finditer(LIST, s))
    if not lists:
        return None
    ys = years(re.sub(AMT, ' ', s))
    if not ys:
        return None
    cols = []; prev = 0
    post_style = bool(POST.match(s[lists[0].end():lists[0].end() + 80])) and not re.search(r'deficienc', s[:lists[0].start()].split('notice of deficiency')[-1], re.I)
    for i, lm in enumerate(lists):
        if post_style:
            nxt = s[lm.end():lists[i + 1].start() if i + 1 < len(lists) else lm.end() + 120]
            pm = POST.match(nxt)
            if not pm:
                return None
            lab = nxt[:pm.end() + 60]
            k = 'D' if pm.group(1).lower().startswith('deficienc') else None
            if k is None:
                sm = re.search(SEC, lab)
                k = normsec(sm.group(1)) if sm else ('6662(a)' if re.search(r'accuracy', lab, re.I) else '6663' if re.search(r'fraud', lab, re.I) else None)
        else:
            lab = s[prev:lm.start()]
            nxt = s[lm.end():lm.end() + 40]
            sm = re.match(r'\s*(?:accuracy-related |fraud )?(?:penalt\w*|additions? to tax)?\s*(?:under|pursuant to)\s+section\s+' + SEC, nxt)
            k = normsec(sm.group(1)) if sm else label_key(lab)
        if k is None:
            return None
        cols.append((k, amts(lm.group(1)))); prev = lm.end()
    if cols[0][0] != 'D' or [k for k, _ in cols].count('D') != 1:
        return None
    return ys, cols


def parse_resp2(flat, start):
    """Determination sentence(s) with amount lists: 'deficiencies of $A and $B and section 6663 penalties of $C and $D
    for 2012 and 2013, respectively', or 'a $X deficiency and a $Y accuracy-related penalty ... 2003'. Dates, page
    stamps and footnote markers removed first. Consecutive sentences (consolidated petitioners) each give records;
    stops at the first sentence without amounts after one with amounts, or at an amended answer."""
    s = flat[start:start + 2500]
    s = STAMP.sub(' ', s); s = re.sub(r'-\s?\d+\s?-|\[\*\d+\]', ' ', s)
    s = re.sub(MONTHS + r'\s+\d{1,2},?\s+\d{4}', ' DATE ', s)
    s = re.sub(r'\s+', ' ', s); s = re.sub(r' ([.,;:)])', r'\1', s); s = re.sub(r'(\d) \.(\d\d)\b', r'\1.\2', s)
    s = re.sub(r'(section\s+66\d\d(?:\([a-z0-9]+\))*)\d\b', r'\1', s)
    recs = []; pos = 0; seen_amounts = False
    for _ in range(6):
        e = SENT_END.search(s, pos)
        sent = s[pos:e.start() + 1] if e else s[pos:pos + 700]
        if re.search(r'amend\w* (?:to )?(?:the |its |his )?answer|increas(?:ed|ing)|After concessions|issues? for decision', sent, re.I):
            break
        if re.search(AMT, sent):
            r = resp_sentence(sent)
            if r is None:
                if not recs: return []
                break
            seen_amounts = True
            ys, cols = r; n = len(ys); each = re.search(r'for each of', sent)
            for i, y in enumerate(ys):
                row = {}
                for k, v in cols:
                    if len(v) == n: row[k] = v[i]
                    elif len(v) == 1 and (n == 1 or each): row[k] = v[0]
                    else: return []
                d = row.pop('D')
                recs.append(dict(year=y, deficiency=d, pen=row, src='prose-resp'))
        elif seen_amounts:
            break
        if not e: break
        pos = e.end()
    return recs


def _unused():
    if True:
        return []
    n = len(ys)
    each = re.search(r'for each of', s)
    recs = []
    for i, y in enumerate(ys):
        row = {}
        for k, v in cols:
            if len(v) == n: row[k] = v[i]
            elif len(v) == 1 and (n == 1 or each): row[k] = v[0]
            else: return []
        d = row.pop('D')
        recs.append(dict(year=y, deficiency=d, pen=row, src='prose-resp'))
    return recs


def single_sentence(S):
    """One determination sentence, one deficiency, one year (stamps removed)."""
    sents = re.split(r'(?<=[a-z0-9)])\. (?=[A-Z])', S)
    for s in sents[:3]:
        if not re.search(r'determin|assert', s) or not re.search(AMT, s):
            continue
        ys = years(re.sub(AMT, '', s))
        dm = re.search(r'deficienc(?:y|ies)[^$]{0,80}?(%s)|(%s)\s+(?:\w+\s+){0,3}deficiency' % (AMT, AMT), s, re.I)
        if len(ys) != 1 or not dm:
            continue
        d = amt(dm.group(1) or dm.group(2)); pen = {}
        for pm in re.finditer(r'(?:section|sections)\s+' + SEC + r'[^$]{0,60}?(' + AMT + ')', s):
            v = amt(pm.group(2))
            if v is not None and v != d:
                pen[normsec(pm.group(1))] = v
        for pm in re.finditer('(' + AMT + r')\s+(?:\w+[- ]){0,4}?(?:penalty|addition to tax)\s+(?:under|pursuant to)\s+section\s+' + SEC, s):
            v = amt(pm.group(1))
            if v is not None and v != d:
                pen.setdefault(normsec(pm.group(2)), v)
        return [dict(year=ys[0], deficiency=d, pen=pen, src='prose-single')]
    return []


def cite_of(o, t):
    c = o.get('cite')
    if c:
        k, n = c.split(' ', 1)
        if k == 'TC':
            v, no = n.split('-'); return '%s T.C. No. %s' % (v, no)
        return {'TCM': 'T.C. Memo. ', 'TCS': 'T.C. Summary Opinion '}[k] + n
    m = re.search(r'(T\.C\. Memo\. \d{4}-\d+|T\.C\. Summary Opinion \d{4}-\d+|\d+ T\.C\. No\. \d+)', t[:800])
    return m.group(1) if m else None


def decision(title):
    t = (title or '').lower()
    if 'rule 155' in t: return 'Rule 155'
    if 'for respondent' in t and 'for petitioner' in t: return 'mixed'
    if 'for respondent' in t: return 'for respondent'
    if 'for petitioner' in t: return 'for petitioner'
    if 'dismiss' in t: return 'dismissal'
    if 'appropriate' in t or 'will be entered' in t: return 'other order/decision'
    return 'unstated'


def one(did):
    o = INV[did]; e = [x for x in o['entries'] if x['docketEntryId'] == did][0]
    fn = H + '/data2/lay/%s.txt' % did
    base = dict(id=did, key=o['key'], docket=e['docketNumber'], dockets=[x['docketNumber'] for x in o['entries']], title=e['title'],
                filed=e['filingDate'][:10], year_filed=o['year'], type=o['type'], caption=e['caption'], judge=e.get('judge'),
                keywords=o['keywords'], decision=decision(e['title']), cite=o.get('cite'))
    if not os.path.exists(fn):
        return dict(base, status='not fetched', recs=[])
    raw = open(fn, errors='ignore').read()
    base['cite'] = cite_of(o, raw)
    lines = clean_lines(clean(raw), o['type'] == 'OST')
    t = '\n'.join(lines); b = body(t) if o['type'] != 'OST' else t
    flat = re.sub(r'\s+', ' ', b)
    m = DET.search(flat)
    if not m:
        return dict(base, status='no determination passage', recs=[])
    st = max(0, m.start() - 160); pre = flat[st:m.start()]
    cut = max(pre.rfind('. '), pre.rfind(':'))
    Wflat = flat[st + cut + 1 if cut >= 0 else st:m.start() + 4000]
    # locate the window in line space
    words = [w for w in re.sub(r'\s+', ' ', m.group(0)).split(' ') if w][:4]
    li = 0; blines = b.split('\n')
    for idx, ln in enumerate(blines):
        joined = re.sub(r'\s+', ' ', ' '.join(blines[idx:idx + 3]))
        if words and words[0] in ln and ' '.join(words) in joined:
            li = idx; break
    Wl = blines[max(0, li - 2):li + 70]
    for idx in range(3, len(Wl)):
        if not re.match(r'\s*\d+\s', Wl[idx]) and LSTOP.search(Wl[idx]):
            Wl = Wl[:idx]; break
    S = STAMP.sub(' ', Wflat)
    cands = [(parse_table_pos(Wl, gen_of(S)), 'table-pos', 3), (parse_table('\n'.join(Wl)), 'table', 2)]
    pr, why = parse_prose(S); cands.append((pr if why == 'ok' else [], 'prose:' + why, 1))
    cands.append((single_sentence(prep(S)), 'prose-single', 0))
    cands.append((parse_resp2(flat, m.start()), 'prose-resp', 1.5))
    def score(c):
        rs = c[0]
        full = sum(1 for r in rs if r.get('pen') and r.get('deficiency') is not None)
        bad = sum(1 for r in rs if r.get('pen') is None or r.get('deficiency') is None)
        some = sum(1 for r in rs if r.get('pen') is not None and r.get('deficiency') is not None)
        return (full, some - bad, c[2])
    # rank: table-pos > prose-resp > table > prose > prose-single; a lower-ranked table wins only with strictly more
    # complete records
    RANK = {'table-pos': 5, 'prose-resp': 4, 'table': 3, 'prose': 2, 'prose-single': 1}
    full = [c for c in cands if score(c)[0] > 0 and score(c)[1] >= 0]
    if full:
        top = max(full, key=lambda c: RANK[c[1].split(':')[0]])
        for c in full:
            if c[1] in ('table', 'table-pos') and score(c)[0] > score(top)[0]:
                top = c
        best = top
    else:
        best = max(cands, key=score)
    recs, mode = best[0], best[1]
    if not recs and pr:
        recs, mode = pr, 'prose:' + why
    if not recs:
        mode = 'prose:' + why
    if not recs and re.search(r'estate tax|gift tax', Wflat[:600], re.I):
        dm = re.search(r'(%s)\s+(?:Federal\s+)?(?:estate|gift) tax deficiency|deficiency in (?:the )?(?:Federal )?(?:estate|gift) tax[^$.]{0,80}?(%s)' % (AMT, AMT), Wflat[:800], re.I)
        if dm:
            d = amt(dm.group(1) or dm.group(2)); pen = {}
            for pm in re.finditer('(' + AMT + r')\s+(?:\w+[- ]){0,3}?penalty\s+(?:under|pursuant to)\s+section\s+' + SEC, Wflat[:800]):
                pen[normsec(pm.group(2))] = amt(pm.group(1))
            recs = [dict(year=o['year'], deficiency=d, pen=pen, src='estate/gift', note='no tax year stated: opinion year used')]; mode = 'estate/gift'
    usable = [r for r in recs if r.get('pen') is not None and r.get('deficiency') is not None]
    if recs and usable and all(not r['pen'] for r in usable):
        if re.search(r'penalt|addition', Wflat[:900], re.I):
            return dict(base, status='penalty amount not stated', mode=mode, recs=recs)
        return dict(base, status='no penalty in determination', mode=mode, recs=recs)
    status = 'parsed' if usable else 'unparsed'
    if not usable:
        lead = STAMP.sub(' ', Wflat)[:700]
        if not re.search(AMT, lead):
            status = 'no amounts stated in determination'
        elif re.search(r'collection due process|section 6330|section 6320|section 6015|innocent spouse|levy|lien|whistleblower|section 7623', flat[:6000], re.I) and not re.search(r'deficienc[^.$]{0,60}\$', lead):
            status = 'not a deficiency case (CDP, 6015, whistleblower)'
    return dict(base, status=status, mode=mode, recs=recs)


if __name__ == '__main__':
    import sys
    ids = list(INV) if len(sys.argv) < 2 else sys.argv[1:]
    with Pool(8) as p:
        out = p.map(one, ids, chunksize=25)
    if len(sys.argv) >= 2:
        for o in out:
            print(json.dumps(o)[:3000])
        raise SystemExit
    seen = {}
    for o in out:
        c = o.get('cite')
        if c and o['status'] != 'not fetched':
            if c in seen:
                o['status'] = 'duplicate (consolidated, same citation)'; o['dup_of'] = seen[c]
            else:
                seen[c] = o['id']
    json.dump(out, open(H + '/data2/parsed.json', 'w'))
    st = collections.Counter(o['status'] for o in out)
    print(st.most_common())
    print(collections.Counter(o.get('mode', '').split(':')[0] for o in out if o['status'] == 'parsed').most_common())
    print(collections.Counter(o.get('mode') for o in out if o['status'] == 'unparsed').most_common())
    print('year-records with penalties', sum(1 for o in out for r in o.get('recs', []) if r.get('pen')))
