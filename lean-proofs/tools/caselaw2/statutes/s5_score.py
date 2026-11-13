"""Step 5: evidence rows per candidate, scored by audit precision (calibrated per evidence type and stratum).

    python s5_score.py   -> statutes/evidence.tsv, statutes/calibration.json, statutes/top_pairs.tsv

Evidence types (schema): lawNamesDecision, reportNamesDecision, quotedWordsStruck, laterCourtSays:<treatment id>.
Strata (for calibration):
  lawNames/reportNames: 'first10y' (the overrides census/sample: first rewrite of the cited block, within 10 years),
                        'later' (another rewrite, or 10-15 years; new here), 'cite' (a reporter cite in the law or report
                        resolved to the decision, linked by section; new here)
  quoted: 'SA' (Supreme Court, appeals), 'FT' (other courts)
Score of a row = the audit verdict when that (decision, law) was read (override 0.97 / not 0.03), else the stratum's
precision (Laplace-smoothed, (k+1)/(n+2)). Audits: uses/overrides/audit (N census, R and Q samples) and
statutes/audit (blind reads of the new strata).
"""
import collections, csv, glob, json, math, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
import common as C
csv.field_size_limit(10 ** 9)
OVL = ('override_express', 'override_implicit')
EXPL = re.compile(r'overrul|overturn|supersed|abrogat|revers(?:e|es|ed|ing) the|in response to|respond(?:s|ed|ing)? to|reject(?:s|ed|ing)? the|'
                  r'contrary to (?:the )?(?:intent of Congress|congressional intent|the intent)|narrowly (?:interpreted|construed)|misinterpret|'
                  r'restor(?:e|es|ing) the|clarif(?:y|ies|ying) that|legislatively|correct(?:s|ing)? the|wrongly decided|erroneous', re.I)

def load_audits():
    """(nid, law) -> (label, tags, name_check, express) from both audit sets."""
    lab = {}
    for base in (f'{C.OV}/audit', f'{C.S}/audit'):
        for kf in glob.glob(f'{base}/key_*.json'):
            mode = kf.split('key_')[1][:-5]
            key = json.load(open(kf, encoding='utf-8'))
            for of in glob.glob(f'{base}/out_{mode}_*.json'):
                for v in json.load(open(of, encoding='utf-8')):
                    if v['id'] not in key: continue
                    t, nid, law = key[v['id']].split('|')[:3]
                    old = lab.get((nid, law))
                    tags = (old[1] if old else set()) | {('ov:' if base.endswith('overrides/audit') else 'st:') + t}
                    lab[(nid, law)] = (v['label'], tags, v.get('name_check', ''), v)
    return lab

def stratum(p, ev):
    if ev in ('lawNamesDecision', 'reportNamesDecision'):
        if p['src'].startswith('cite'): return 'cite'
        return 'first10y' if p['first'] == '1' and months(int(p['decided']), int(p['law_day'])) <= 120 else 'later'
    if ev == 'quotedWordsStruck':
        return 'SA' if p['tier'] in ('S', 'A') else 'FT'
    return 'court'
def months(d0, d1): return (d1 // 10000 - d0 // 10000) * 12 + (d1 // 100 % 100 - d0 // 100 % 100)

def main():
    pairs = list(csv.DictReader(open(f'{C.S}/pairs2.tsv', encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE))
    lab = load_audits()
    # evidence rows
    rows = []
    for p in pairs:
        evs = []
        if p['law_match']: evs.append(('lawNamesDecision', p['law_snip']))
        if p['report_match']: evs.append(('reportNamesDecision', p['report_snip']))
        if p['ov_kind'] == 'quoted words struck': evs.append(('quotedWordsStruck', p['quote']))
        for ev, sn in evs:
            rows.append(dict(p=p, ev=ev, st=stratum(p, ev), snip=sn))
    # laterCourtSays rows come from s7 (treatments); calibration of 'court' from statutes/audit tag L
    # calibration: which audits estimate which stratum
    # overrides census N -> lawNames first10y; R sample -> reportNames first10y; Q sample -> quoted SA/FT;
    # statutes audit tags: X<later>, Y<cite>, L<court>  (new blind reads)
    TAGS = {('lawNamesDecision', 'first10y'): {'ov:N'}, ('reportNamesDecision', 'first10y'): {'ov:R'},
            ('quotedWordsStruck', 'SA'): {'ov:Q'}, ('quotedWordsStruck', 'FT'): {'ov:Q'},
            ('lawNamesDecision', 'later'): {'st:X'}, ('reportNamesDecision', 'later'): {'st:X'},
            ('lawNamesDecision', 'cite'): {'st:Y'}, ('reportNamesDecision', 'cite'): {'st:Y'}}
    cal = {}
    for (ev, st), tg in TAGS.items():
        items = [r for r in rows if r['ev'] == ev and r['st'] == st and (r['p']['nid'], r['p']['law']) in lab
                 and lab[(r['p']['nid'], r['p']['law'])][1] & tg]
        seen = set(); k = n = ex = 0
        for r in items:
            kk = (r['p']['nid'], r['p']['law'])
            if kk in seen: continue
            seen.add(kk); n += 1
            k += lab[kk][0] in OVL; ex += lab[kk][0] == 'override_express'
        size = len({(r['p']['nid'], r['p']['law']) for r in rows if r['ev'] == ev and r['st'] == st})
        cal[f'{ev}|{st}'] = dict(n=n, override=k, express=ex, pairs=size, precision=round(k / n, 3) if n else None,
                                 smoothed=round((k + 1) / (n + 2), 3), wilson=wilson(k, n))
    # pooled fallbacks for a stratum with no audit: the evidence type's pooled precision
    for ev in ('lawNamesDecision', 'reportNamesDecision'):
        for st in ('later', 'cite'):
            c = cal[f'{ev}|{st}']
            if c['n'] == 0:
                o = [cal[f'{e}|{st}'] for e in ('lawNamesDecision', 'reportNamesDecision')]
                k = sum(x['override'] for x in o); n = sum(x['n'] for x in o)
                if n: c['smoothed'] = round((k + 1) / (n + 2), 3); c['pooled'] = 1
    json.dump(cal, open(f'{C.S}/calibration.json', 'w', encoding='utf-8'), indent=1)
    out = []
    for r in rows:
        p = r['p']; kk = (p['nid'], p['law'])
        a = lab.get(kk)
        if a and a[0] in OVL: sc, how = 0.97, 'audit:' + a[0]
        elif a: sc, how = 0.03, 'audit:' + a[0]
        else: sc, how = cal[f"{r['ev']}|{r['st']}"]['smoothed'], 'stratum'
        if a: explicit = int(a[0] == 'override_express' and r['ev'] != 'quotedWordsStruck')
        else: explicit = int(r['ev'] in ('lawNamesDecision', 'reportNamesDecision') and bool(EXPL.search(r['snip'] or '')))
        out.append([p['nid'], p['law'], p['blocks'], r['ev'], r['st'], f'{sc:.3f}', explicit, how, p['src'], p['tier'], p['decided'], p['law_day'],
                    p['name'], p['cite']])
    C.wtsv(f'{C.S}/evidence.tsv', out, ['nid', 'law', 'blocks', 'evidence', 'stratum', 'score', 'explicit', 'score_from', 'src', 'tier',
                                         'decided', 'law_day', 'name', 'cite'])
    # pair ranking: noisy-or of row scores, audited verdict wins
    pr = collections.defaultdict(list)
    for o in out: pr[(o[0], o[1])].append(o)
    ranked = []
    for kk, os_ in pr.items():
        if os_[0][7].startswith('audit'): s = float(os_[0][5])
        else:
            s = 1 - math.prod(1 - float(o[5]) for o in os_)
        ranked.append((s, kk, os_[0]))
    ranked.sort(key=lambda x: -x[0])
    C.wtsv(f'{C.S}/top_pairs.tsv', ([f'{s:.3f}', kk[0], kk[1], o[2], o[9], o[10], o[11], o[12], o[13], ','.join(sorted({x[3] for x in pr[kk]})), o[7]]
                                    for s, kk, o in ranked), ['pair_score', 'nid', 'law', 'blocks', 'tier', 'decided', 'law_day', 'name', 'cite', 'evidence', 'score_from'])
    print(json.dumps(cal, indent=1))
    print('rows', len(out), collections.Counter((o[3], o[4]) for o in out))

def wilson(k, n, z=1.96):
    if n == 0: return (0, 0)
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(c - h, 3), round(c + h, 3))

if __name__ == '__main__':
    main()
