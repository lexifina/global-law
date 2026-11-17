#!/usr/bin/env python3
"""Parse fetched decision documents (court-entered decisions) into final per-year figures; compare with the notice's
figures from the opinion; write Lean rows for the final figures (data2/rows_final.tsv) and data2/final.json."""
import json, os, re, subprocess, collections, sys
sys.path.insert(0, os.path.dirname(__file__))
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/penalties')
import parse2 as p2
AMT = p2.AMT; SEC = r'(66(?:51|53|54|55|59|61|62|63|64|73)A?(?:\s?\([a-zA-Z0-9]{1,3}\))*)'


def text(did):
    pdf = '%s/cache/dec/%s.pdf' % (H, did); lay = '%s/data2/dec/%s.txt' % (H, did)
    os.makedirs(H + '/data2/dec', exist_ok=True)
    if not os.path.exists(lay):
        subprocess.run(['pdftotext', '-layout', pdf, lay], capture_output=True)
    return open(lay, errors='ignore').read() if os.path.exists(lay) else ''


def parse_decision(t):
    """-> {year: {'D': amount, section: amount}} from the ORDERED AND DECIDED clauses (or a table)."""
    out = collections.defaultdict(dict)
    t = t.replace('ﬁ', 'fi').replace('ﬂ', 'fl')
    m = re.search(r'ORDERED\s+AND\s+DECIDED', t, re.I) or re.search(r'DECIDED', t)
    body = t[m.end():] if m else t
    e = re.search(r'\(Signed\)|\bJudge\s*\.?\s*(?:\n|Entered|ENTERED)|\bEntered\s*:|ENTERED\s*:|SERVED\b|The parties stipulate|Special Trial Judge\s*\n', body)
    if e:
        body = body[:e.start()]
    lines = p2.clean_lines(body, False)
    tab = p2.parse_table_pos(lines)
    for r in tab:
        if r.get('pen') is not None and r.get('deficiency') is not None:
            out[r['year']]['D'] = r['deficiency']
            for k, v in r['pen'].items():
                out[r['year']][k] = v
    flat = re.sub(r'\s+', ' ', '\n'.join(lines))
    flat = re.sub(r'(?:Entered|ENTERED|Served|SERVED)[^.;]{0,30}\d{2}/\d{2}/\d{2,4}', ' ', flat)
    flat = re.sub(r'\$\s+(?=\d)', '$', flat)
    flat = re.sub(r'\$(\d{1,3})\s*,\s*(\d)\s?(\d)\s?(\d)\b', r'$\1,\2\3\4', flat)
    flat = re.sub(r'(\$[\d,]+)\s*\.\s*(\d)\s?(\d)\b', r'\1.\2\3', flat)
    for cl in re.split(r';|,?\s+and\s+that\b|,\s+that\b|\bthat\b|,\s+and\s+(?=there (?:is|are)\b)', flat, flags=re.I):
        if re.search(r'overpayment|interest', cl, re.I) and not re.search(r'deficienc|penalt|addition', cl, re.I):
            continue
        if re.search(r'(?:percent|%)\s+of\b', cl, re.I):
            continue  # an (a)(2)/(a)(3) or 6654 formula: the amount is a base, not the addition
        ys = [y for y in p2.years(re.sub(AMT, ' ', cl)) if 1980 < y < 2030]
        if not ys:
            continue
        am = [p2.amt(x) for x in re.findall(AMT, cl)]
        none = re.search(r'\bno\s+(?:deficienc|penalt|addition|liabilit)|\bnot liable\b|\bis no\b|\bare no\b', cl, re.I)
        if re.search(r'deficienc', cl, re.I) and not re.search(r'penalt|addition', cl, re.I):
            key = 'D'
        else:
            sm = re.findall(SEC, cl)
            if not sm:
                continue
            key = re.sub(r'\s', '', sm[0])
            key = p2.normsec(key)
            if not re.search(r'penalt|addition', cl, re.I):
                continue
        if none and not am:
            for y in ys: out[y].setdefault(key, 0.0)
        elif len(am) == len(ys):
            for y, a in zip(ys, am): out[y].setdefault(key, a)
        elif len(am) == 1 and re.search(r'each of', cl):
            for y in ys: out[y].setdefault(key, am[0])
    return {y: v for y, v in out.items() if v}


if __name__ == '__main__':
    R = json.load(open(H + '/data2/decisions_index.json'))
    P = {o['docket']: o for o in json.load(open(H + '/data2/parsed.json')) if o['status'] == 'parsed'}
    final = {}; rows = []
    NORM = {'6663(a)': '6663', '6662': '6662(a)', '6654(a)': '6654'}
    for r in R:
        o = P.get(r['docket'])
        if not o:
            continue
        fetched = [d for d in r['decisions'] if d['result'] == 'fetched']
        res = dict(docket=r['docket'], id=o['id'], cite=o.get('cite'), decision=o['decision'], docket_status=r['status'],
                   outcomes=[d['eventCode'] + ':' + d['result'] for d in r['decisions']])
        if fetched:
            d = fetched[-1]
            fig = parse_decision(text(d['docketEntryId']))
            res['final'] = {str(y): {NORM.get(k, k): v for k, v in v.items()} for y, v in fig.items()}
            res['decision_entry'] = d['docketEntryId']; res['decision_event'] = d['eventCode']; res['decision_date'] = d['filingDate']
            for y, v in fig.items():
                if v.get('D') is None:
                    continue
                pens = {NORM.get(k, k): x for k, x in v.items() if k != 'D' and x}
                if pens:
                    rows.append('%s#F%s\t%d\t%d\t%s' % (o['id'], y, y, round(v['D'] * 100), ';'.join('%s=%d' % (k, round(x * 100)) for k, x in pens.items())))
        final[o['id']] = res
    json.dump(final, open(H + '/data2/final.json', 'w'))
    open(H + '/data2/rows_final.tsv', 'w').write('\n'.join(rows) + '\n')
    env = dict(os.environ, PATH=os.path.expanduser('~/.elan/bin:') + os.environ['PATH'])
    print(subprocess.run([H + '/lean/.lake/build/bin/run', H + '/data2/rows_final.tsv', H + '/data2/classified_final.tsv'], cwd=H + '/lean', env=env, capture_output=True, text=True).stdout)
    c = collections.Counter()
    for v in final.values():
        c['with fetched decision' if 'final' in v else 'no public decision'] += 1
        if 'final' in v and v['final']: c['decision figures parsed'] += 1
    print(dict(c))
    print(collections.Counter(l.split('\t')[3] for l in open(H + '/data2/classified_final.tsv')).most_common())
