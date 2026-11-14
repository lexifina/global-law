"""Validate parse_jnl.py against the corpus's S. Ct. memorandum orders for one month (no key read).

Usage: python -I validate.py <entries.jsonl> <yyyymm> <out_dir>
Corpus side: round6 cache supreme-court.*.meta.tsv.gz rows (court 2906) dated <yyyymm> (node, docket, title), texts from
git via round6/history/r6lib.py fetch_texts. Journal side: parse_jnl entries dated <yyyymm>.
Reports: docket match counts, same-date share, caption agreement (party-name token overlap), disposition agreement
(journal class vs. words in the corpus text).
"""
import sys, os, re, json, gzip, glob, collections

C2 = os.path.expanduser('~/Documents/us-caselaw-lean-work/caselaw-lean-2')
sys.path.insert(0, os.path.join(C2, 'round6', 'history'))
import r6lib as L  # noqa: E402


def dk(s):
    s = re.sub(r'[–—‑]', '-', s or '')
    return re.findall(r'\b\d{2}-\d{1,5}\b|\b\d{2}[AM]\d{1,4}\b|\b\d{1,3} Orig|\bD-\d{1,5}\b', s)


STOP = set('v the of and et al in his her official capacity as petitioner petitioners respondent respondents appellant '
           'appellants appellee appellees inc co corp llc united states state warden secretary director a an for on to '
           'department county city individually aka'.split())


def toks(s):
    return set(t for t in re.findall(r'[a-z]{3,}', (s or '').lower()) if t not in STOP)


def corpus_class(t):
    t = re.sub(r'\s+', ' ', t)
    if re.search(r'vacated', t) and re.search(r'remanded', t) and re.search(r'granted', t, re.I):
        return 'gvr'
    if re.search(r'judgments? (?:is |are )?vacated|\bvacated\b', t, re.I):
        return 'vacated'
    if re.search(r'af+i?rmed', t):
        return 'affirmed'
    if re.search(r'reversed', t):
        return 'reversed'
    if re.search(r'denied', t, re.I):
        return 'cert_denied'
    if re.search(r'dismissed', t, re.I):
        return 'dismissed'
    return 'other'


def main():
    ent_path, month, out = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(out, exist_ok=True)
    corp = {}
    for p in sorted(glob.glob(os.path.join(C2, 'round6', 'history', 'cache', 'supreme-court.*.meta.tsv.gz'))):
        for r in L.meta_rows(p):
            if r[4] == '2906' and r[3].startswith(month):
                corp[int(r[0])] = r
    texts = L.fetch_texts(list(corp))
    by_dk = collections.defaultdict(list)
    for n, r in corp.items():
        for d in dk(r[5]):
            by_dk[d].append(n)
    jr = [json.loads(l) for l in open(ent_path, encoding='utf-8')]
    jr = [r for r in jr if r['date'] and r['date'].startswith(month)]
    stats = collections.Counter()
    conf = collections.Counter()
    matched_nodes = set()
    rows = []
    for r in jr:
        stats['journal_entries'] += 1
        stats['journal_dockets'] += len(r['dockets'])
        hits = []
        for d in r['dockets']:
            hits += by_dk.get(d, [])
        if not hits:
            stats['journal_entries_no_corpus_node'] += 1
            rows.append([r['date'], ';'.join(r['dockets']), r['cls'], '-', '-', '-', '-', r['caption'][:120]])
            continue
        stats['journal_entries_matched'] += 1
        same = [n for n in hits if corp[n][3] == r['date']]
        if same:
            stats['matched_same_date'] += 1
        n = (same or hits)[0]
        matched_nodes.update(hits)
        jt, ct = toks(r['caption']), toks(corp[n][8] + ' ' + corp[n][7])
        ov = len(jt & ct) / max(1, len(jt))
        stats['caption_overlap_ge_0.5' if ov >= 0.5 else 'caption_overlap_lt_0.5'] += 1
        cc = corpus_class(texts.get(n, ('', ''))[1])
        jc = r['cls'] if r['cls'] != 'granted_remanded' else 'gvr'
        conf[(jc, cc)] += 1
        rows.append([r['date'], ';'.join(r['dockets']), r['cls'], str(n), corp[n][3], cc, '%.2f' % ov,
                     r['caption'][:120] + ' || ' + corp[n][8][:120]])
    stats['corpus_nodes'] = len(corp)
    stats['corpus_nodes_matched'] = len(matched_nodes)
    unmatched = [n for n in corp if n not in matched_nodes]
    with open(os.path.join(out, 'validation_%s.tsv' % month), 'w', encoding='utf-8', newline='\n') as f:
        f.write('date\tdockets\tjournal_class\tnode\tnode_date\tcorpus_class\tcaption_overlap\tcaptions\n')
        for x in rows:
            f.write('\t'.join(L.norm(v) for v in x) + '\n')
    with open(os.path.join(out, 'unmatched_corpus_%s.tsv' % month), 'w', encoding='utf-8', newline='\n') as f:
        for n in unmatched:
            r = corp[n]
            t = texts.get(n, ('', ''))[1]
            f.write('\t'.join([str(n), r[3], r[5], L.norm(r[7])[:100], corpus_class(t), L.norm(t[:200])]) + '\n')
    for k in sorted(stats):
        print(k, stats[k])
    print('class agreement (journal, corpus):')
    agree = sum(v for (a, b), v in conf.items() if a == b)
    print('  agree', agree, 'of', sum(conf.values()))
    for k, v in conf.most_common():
        print(' ', k, v)


if __name__ == '__main__':
    main()
