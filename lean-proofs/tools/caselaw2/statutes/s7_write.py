"""Step 7: the contract files data/lawchanges.tsv and data/supersessions.tsv.

lawchanges.tsv: id, law, usc_block, enacted, effective, retroactive_to, src
  effective: the LLM reading of the law's effective-date provisions (s6, for the top candidates), else the regex reading
  (s3, rx:<kind>), else the record's in-force day (record:<how the record dated the commit>).
  retroactive_to: 0 none; a day = the earliest conduct/claim day the change reaches, before enactment;
  1 = the law applies to matters pending on its effective date whatever the conduct date, with no earlier bound stated.
supersessions.tsv: id, target_node, issue_key, lawchange_id, evidence, score, explicit, src
  one row per (decision, law change, evidence type); laterCourtSays:<treatment id> rows from data/treatments.tsv
  (kind supersededByEnactment) when that file exists; issue_key from data/holdings.tsv + issues.tsv when they exist.
"""
import collections, csv, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
import common as C
csv.field_size_limit(10 ** 9)

def norm_block(b):
    """'18:2256(8)' / '42:2000e-5(e)' / '42:1983' -> (title, section, sub)"""
    m = re.match(r'(\w+):([^(]+)(?:\(([^)]*)\))?', b)
    return (m.group(1), m.group(2), m.group(3) or '') if m else None
def bstr(t, s, sub): return f'{t}:{s}' + (f'({sub})' if sub else '')

def main():
    LI = {}
    for l in open(f'{C.S}/lawinfo.jsonl', encoding='utf-8'):
        x = json.loads(l); LI[x['law']] = x
    ckind = dict(l.rstrip('\n').split('\t') for l in open(f'{C.S}/commits.tsv', encoding='utf-8'))
    vcommit = {}   # (law, title, section) -> [(day, commit)]
    for l in open(f'{C.W}/usc/versions.tsv', encoding='utf-8'):
        f = l.rstrip('\n').split('\t')
        if f[2] != 'law': continue
        m = re.match(r'title-(\w+)/(.+)\.md$', f[0])
        vcommit.setdefault((f[3], m.group(1), m.group(2)), []).append((int(f[4]), f[1]))
    llm = {}
    if os.path.exists(f'{C.S}/llm/retro.jsonl'):
        for l in open(f'{C.S}/llm/retro.jsonl', encoding='utf-8'):
            x = json.loads(l)
            if 'err' not in x: llm[(x['law'], x['usc'])] = x
    # the 60 blind hand reads (validation samples) replace the LLM reading for their items
    import glob
    for fn in glob.glob(f'{C.S}/audit/retro*_out_*.json'):
        for h in json.load(open(fn, encoding='utf-8')):
            law, usc = h['key'].split('|')
            if (law, usc) in llm and h.get('effective_date'):
                llm[(law, usc)].update(effective_date=h['effective_date'], retro_class=h['retro_class'],
                                       retroactive_to=h.get('retroactive_to') or '', confidence='high', correction='handRead')
    # hand corrections after review of the LLM reading (statutes/llm/hand_corrections.jsonl)
    if os.path.exists(f'{C.S}/llm/hand_corrections.jsonl'):
        for l in open(f'{C.S}/llm/hand_corrections.jsonl', encoding='utf-8'):
            c = json.loads(l)
            if (c['law'], c['usc']) in llm: llm[(c['law'], c['usc'])].update(c)
    # law changes: blockchanges + blocks named by evidence rows
    lc = {}
    for l in open(f'{C.S}/blockchanges.tsv', encoding='utf-8'):
        law, t, s, sub, day, rem, first, nb, k = l.rstrip('\n').split('\t')
        key = (law, t, s, sub)
        if key not in lc or int(day) < lc[key]: lc[key] = int(day)
    ev = list(csv.DictReader(open(f'{C.S}/evidence.tsv', encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE))
    for e in ev:
        for b in e['blocks'].split(';'):
            nb_ = norm_block(b)
            if not nb_: continue
            key = (e['law'],) + nb_
            if key not in lc:
                vs = vcommit.get((e['law'], nb_[0], nb_[1]))
                lc[key] = min(d for d, _ in vs) if vs else int(e['law_day'] or 0)
    def eff_for(law, t, s, sub, inforce, use_llm=True):
        x = LI.get(law, {})
        enacted = x.get('enacted') or x.get('enacted_rec') or inforce
        # 1. LLM
        r = (llm.get((law, f'{t}:{s}')) or llm.get((law, bstr(t, s, sub)))) if use_llm else None
        if r and r.get('confidence') != 'low' and r.get('effective_date'):
            effd = C.day(r['effective_date']) or enacted
            rt = C.day(r['retroactive_to']) if r.get('retroactive_to') else 0
            if r['retro_class'] in ('prospectiveOnly', 'noProvision'): rt = 0
            elif not rt or (rt != 1 and rt >= enacted):
                # a retroactive class without an earlier date: reaches earlier conduct in pending matters, no bound stated
                rt = 1
            return enacted, effd, rt, f"llm:{r['retro_class']}:{r['effective_basis']}" + (':' + r['correction'] if r.get('correction') else '')
        # 2. regex over the law's effective-date passages, most specific first
        amend = [sc for sc in x.get('secs', []) if f'{t}:{s}' in sc['usc']]
        ams = {sc['i'] for sc in amend}; nums = {sc['num'] for sc in amend}; titles = {sc['title'] for sc in amend}
        best = None
        for e in x.get('eff', []):
            if not e['kind']: continue
            if e['sec_i'] in ams: rk = 0
            elif e['scope'].startswith('secs:') and nums & set(e['scope'][5:].split(',')): rk = 1
            elif e['scope'] == 'title' and e['title'] in titles and amend: rk = 2
            elif e['scope'] == 'act': rk = 3
            else: continue
            if best is None or rk < best[0]: best = (rk, e)
        if best:
            e = best[1]
            effd = e['day'] or enacted
            rt = e['retro_day'] if e['retro'] else 0
            if rt and rt != 1 and rt >= enacted: rt = 0
            return enacted, effd, rt, f"rx:{e['kind']}:sec{e['sec']}:rank{best[0]}"
        # 3. the record
        vs = vcommit.get((law, t, s), [])
        ck = next((ckind.get(c, 'unknown') for d, c in vs if d == inforce), 'unknown')
        return enacted, inforce, 0, f'record:{ck}' + ('' if x.get('secs') else ':notext')
    ids = {}
    rows = []; rx_rows = []
    for i, (key, inforce) in enumerate(sorted(lc.items(), key=lambda kv: (kv[1], kv[0]))):
        law, t, s, sub = key
        enacted, effd, rt, src = eff_for(law, t, s, sub, inforce)
        ids[key] = i + 1
        rows.append([i + 1, law, bstr(t, s, sub), enacted, effd, rt, src])
        if src.startswith('llm'):
            rx_rows.append([i + 1, law, bstr(t, s, sub)] + list(eff_for(law, t, s, sub, inforce, use_llm=False)))
    C.wtsv(f'{C.D}/lawchanges.tsv', rows)
    C.wtsv(f'{C.S}/lawchanges_rx_for_llm_rows.tsv', rx_rows)
    # issue keys
    issue_of = collections.defaultdict(list)    # (node, title, section) -> [issue_key]
    if os.path.exists(f'{C.D}/holdings.tsv') and os.path.exists(f'{C.D}/issues.tsv'):
        usc = {}
        for l in open(f'{C.D}/issues.tsv', encoding='utf-8'):
            f = l.rstrip('\n').split('\t')
            if len(f) > 3 and f[3] != '-':
                m = re.match(r'(\w+):([^(\s]+)', f[3])
                if m: usc[f[0]] = (m.group(1), m.group(2), f[3])
        for l in open(f'{C.D}/holdings.tsv', encoding='utf-8'):
            f = l.rstrip('\n').split('\t')
            if len(f) > 2 and f[2] in usc:
                issue_of[(f[1], usc[f[2]][0], usc[f[2]][1])].append((f[2], usc[f[2]][2]))
    def issue(nid, t, s, sub):
        c = issue_of.get((nid, t, s), [])
        if not c: return '-'
        exact = [k for k, u in c if sub and f'({sub})' in u]
        return (exact or [k for k, _ in c])[0]
    sup = []
    for e in ev:
        for b in e['blocks'].split(';'):
            nb_ = norm_block(b)
            if not nb_: continue
            lid = ids.get((e['law'],) + nb_)
            if not lid: continue
            sup.append([e['nid'], issue(e['nid'], *nb_), lid, e['evidence'], e['score'], e['explicit'],
                        f"{e['score_from']};{e['stratum']};{e['src']}"])
    # later courts (reader's treatments)
    nlc = 0
    tpath = f'{C.D}/treatments.tsv'
    if os.path.exists(tpath):
        by_target = collections.defaultdict(set)   # target -> lawchange ids already proposed
        for r in sup: by_target[r[0]].add(r[2])
        lc_by_block = collections.defaultdict(list)
        for (law, t, s, sub), i in ids.items(): lc_by_block[(t, s, sub)].append((lc[(law, t, s, sub)], i, law))
        cited = collections.defaultdict(set); ddate = {}
        for r in open(f'{C.W}/usc/enc/rows.tsv', encoding='utf-8'):
            rid, nid, d, t, s, sub, nm = r.rstrip('\n').split('\t'); cited[nid].add((t, s, sub)); ddate[nid] = int(d)
        cal = json.load(open(f'{C.S}/calibration.json', encoding='utf-8'))
        court_p = cal.get('laterCourtSays|court', {}).get('smoothed', 0.8)
        for l in open(tpath, encoding='utf-8'):
            f = l.rstrip('\n').split('\t')
            if len(f) < 6 or f[4] != 'supersededByEnactment': continue
            tid, by, tgt, dd = f[0], f[1], f[2], int(f[3] or 0)
            explicit = f[7] if len(f) > 7 else '0'
            quote = f[11] if len(f) > 11 else ''
            # candidate law changes: proposed already for the target, else rewrites of its cited blocks between the two decisions
            cands = sorted(by_target.get(tgt, ()))
            how = 'proposed'
            if not cands:
                cands = sorted({i for b in cited.get(tgt, ()) for day, i, law in lc_by_block.get(b, ()) if ddate.get(tgt, 0) <= day <= (dd or 99999999)})
                how = 'blocksBetween'
            pm = re.search(r'Pub(?:lic|\.) ?L(?:aw|\.) ?(?:No\. )?(\d+)[\-–](\d+)', quote)
            if pm:
                lab = f'Pub. L. {pm.group(1)}-{pm.group(2)}'
                named = [i for i in cands if rows[i - 1][1] == lab]
                if named: cands, how = named, 'quoteNamesLaw'
            if not cands: cands, how = [0], 'lawUnknown'
            for i in cands[:3]:
                sup.append([tgt, issue(tgt, *norm_block(rows[i - 1][2])) if i else '-', i, f'laterCourtSays:{tid}', f'{court_p:.3f}', explicit,
                            f'treatments.tsv;{how};by:{by}'])
                nlc += 1
    sup = [[n + 1] + r for n, r in enumerate(sup)]
    C.wtsv(f'{C.D}/supersessions.tsv', sup)
    S = dict(lawchanges=len(rows), lawchange_src=dict(collections.Counter(r[6].split(':')[0] for r in rows)),
             retro=sum(1 for r in rows if r[5]), supersessions=len(sup),
             by_evidence=dict(collections.Counter(r[4].split(':')[0] for r in sup)), explicit=sum(1 for r in sup if str(r[6]) == '1'),
             targets=len({r[1] for r in sup}), laterCourtSays=nlc, with_issue=sum(1 for r in sup if r[2] != '-'))
    json.dump(S, open(f'{C.S}/write_summary.json', 'w'), indent=1)
    print(json.dumps(S, indent=1))

if __name__ == '__main__':
    main()
