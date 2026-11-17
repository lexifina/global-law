#!/usr/bin/env python3
"""Extract the IRS's determination (deficiency and penalties/additions per tax year) from the opening of each sampled
Tax Court opinion. Tables and prose; anything ambiguous is left unparsed (counted, not guessed)."""
import os, re, json, glob, collections
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/penalties')
SAMPLE = {r['docketEntryId']: r for r in json.load(open(H + '/cache/sample.json'))}
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
    stop = re.search(r'issues? (?:for|to be|remaining for) (?:decision|decided)|After concessions|FINDINGS OF FACT|Background|we must decide|The parties|Unless otherwise|The sole issue|The issue|At the time of trial|Subsequently|[Ii]n (?:an|his|its) amend\w* (?:to )?(?:the )?answer|amended answer|asserted an increased|Respondent now|respondent has since|Thereafter', W)
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
            if re.search(r'section|sec\.|deficienc', gap, re.I):
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


def cite(title, t):
    m = re.search(r'(T\.\s?C\.\s?Memo\.?\s?\d{4}-\d+|T\.\s?C\.\s?Summary Opinion\s?\d{4}-\d+|\d+ T\.\s?C\.\s?No\.\s?\d+|T\.\s?C\.\s?\d{4}-\d+)', title or '')
    if not m:
        m = re.search(r'(T\.C\. Memo\. \d{4}-\d+|T\.C\. Summary Opinion \d{4}-\d+|\d+ T\.C\. No\. \d+)', t[:600])
    return re.sub(r'\s+', ' ', m.group(1)).replace('Memo ', 'Memo. ') if m else None


out = []; stats = collections.Counter(); seen = set()
for f in sorted(glob.glob(H + '/data/lay/*.txt')):
    did = os.path.basename(f)[:-4]; meta = SAMPLE.get(did, {})
    raw = open(f, errors='ignore').read()
    c = cite(meta.get('documentTitle'), raw)
    key = c or re.sub(r'\W', '', raw[:3000])
    if key in seen:
        stats['duplicate opinion (consolidated dockets)'] += 1; continue
    seen.add(key)
    t = clean(open(f, errors='ignore').read()); b = body(t)
    base = dict(id=did, cite=c, docket=meta.get('docketNumber'), title=meta.get('documentTitle'), filed=meta.get('filingDate', '')[:10],
                type=meta.get('eventCode'), caption=meta.get('caseCaption'), sampled_by=meta.get('sampled_by'))
    m = re.search(r'(?:Respondent|respondent|Commissioner|IRS|notice|Notice)[^.]{0,140}?determined[^.]{0,200}?(?:deficienc|\$)|determined (?:the following |a |an |deficienc)', b)
    if not m:
        stats['no determination passage'] += 1; out.append(dict(base, status='no determination passage', recs=[])); continue
    st = max(0, m.start() - 120)
    pre = b[st:m.start()]
    cut = max(pre.rfind('. '), pre.rfind(':'))
    W = b[st + cut + 1 if cut >= 0 else st:m.start() + 4000]
    recs = parse_table(W); mode = 'table'
    if not recs or all(r.get('pen') is None for r in recs):
        recs2, why = parse_prose(W); mode = 'prose:' + why
        if recs2:
            recs = recs2
    status = 'parsed' if recs else 'unparsed'
    stats[status + ':' + mode.split(':')[0]] += 1
    out.append(dict(base, status=status, mode=mode, recs=recs))
json.dump(out, open(H + '/data/parsed.json', 'w'), indent=0)
print(stats.most_common())
print('year-records with penalties', sum(1 for o in out for r in o.get('recs', []) if r.get('pen')))
