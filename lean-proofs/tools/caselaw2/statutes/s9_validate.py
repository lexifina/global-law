"""Step 9: validation -> data/STATUTES.md (+ statutes/validation.json).

Recall on the Christiansen-Eskridge (+ Hasen) gold, 1995-2011 Supreme Court decisions overridden by laws of 2011 or
earlier: any evidence vs explicit. Precision per evidence type (calibration.json). Retroactivity extraction accuracy on
the hand-read sample (statutes/audit/retro_hand_*.json vs llm/retro.jsonl). Two-date examples.
"""
import collections, csv, glob, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
import common as C
csv.field_size_limit(10 ** 9)

def load(path, cols):
    return [dict(zip(cols, l.rstrip('\n').split('\t'))) for l in open(path, encoding='utf-8') if l.strip()]
LC = {r['id']: r for r in load(f'{C.D}/lawchanges.tsv', ['id', 'law', 'usc_block', 'enacted', 'effective', 'retroactive_to', 'src'])}
SU = load(f'{C.D}/supersessions.tsv', ['id', 'target_node', 'issue_key', 'lawchange_id', 'evidence', 'score', 'explicit', 'src'])
cal = json.load(open(f'{C.S}/calibration.json', encoding='utf-8'))
V = {}
# ---- recall
gold = list(csv.DictReader(open(f'{C.OV}/gold/gold.tsv', encoding='utf-8'), delimiter='\t'))
idx = {}
want = {C.norm_cite_key(g['us_cite']) for g in gold}
for l in open(f'{C.W}/graph/cite_index.tsv', encoding='utf-8'):
    k, v = l.rstrip('\n').split('\t')
    if k in want: idx[k] = v
by_t = collections.defaultdict(list)
for s in SU: by_t[s['target_node']].append(s)
rec = []
for g in gold:
    nid = idx.get(C.norm_cite_key(g['us_cite']))
    rows = [s for s in by_t.get(nid, []) if s['lawchange_id'] != '0' and LC[s['lawchange_id']]['law'] == g['overriding_law']]
    anyl = by_t.get(nid, [])
    rec.append(dict(decision=g['decision'], cite=g['us_cite'], law=g['overriding_law'], nid=nid or '',
                    found=int(bool(rows)), explicit=int(any(s['explicit'] == '1' for s in rows)),
                    evidence=','.join(sorted({s['evidence'].split(':')[0] for s in rows})),
                    best=max((float(s['score']) for s in rows), default=0), other_laws=len({LC[s['lawchange_id']]['law'] for s in anyl if s['lawchange_id'] != '0'})))
V['recall'] = dict(gold=len(rec), found=sum(r['found'] for r in rec), explicit=sum(r['explicit'] for r in rec),
                   found_score_ge_0_5=sum(1 for r in rec if r['found'] and r['best'] >= 0.5), previous_found=20)
C.wtsv(f'{C.S}/recall2.tsv', ([r[k] for k in rec[0]] for r in rec), list(rec[0]))
# ---- retro accuracy
def loadj(fn):
    d = {}
    if os.path.exists(fn):
        for l in open(fn, encoding='utf-8'):
            x = json.loads(l); d[x['key']] = x
    return d
llm = loadj(f'{C.S}/llm/retro.jsonl'); llm1 = loadj(f'{C.S}/llm/retro_v1.jsonl')
def hands(pat):
    h = []
    for f in sorted(glob.glob(f'{C.S}/audit/{pat}')): h += json.load(open(f, encoding='utf-8'))
    return h
def retro_yes(c): return c in ('appliesToPendingCases', 'retroactiveToDate', 'asIfIncluded')
def evaluate(hand, model):
    acc = collections.Counter(); conf = collections.Counter(); diffs = []
    for h in hand:
        x = model.get(h['key'])
        if not x or 'err' in x: continue
        acc['n'] += 1
        acc['class'] += x['retro_class'] == h['retro_class']
        acc['retro_yes_no'] += retro_yes(x['retro_class']) == retro_yes(h['retro_class'])
        acc['effective'] += (x.get('effective_date') or '') == (h.get('effective_date') or '')
        acc['retroactive_to'] += (x.get('retroactive_to') or '') == (h.get('retroactive_to') or '')
        conf[f"{h['retro_class']} -> {x['retro_class']}"] += 1
        if x['retro_class'] != h['retro_class'] or (x.get('effective_date') or '') != (h.get('effective_date') or ''):
            diffs.append((h['key'], h['retro_class'], x['retro_class'], h.get('effective_date'), x.get('effective_date'), h.get('why', '')[:200]))
    return dict(acc), dict(conf), diffs
H1, H2 = hands('retro_out_*.json'), hands('retro2_out_*.json')
V['retro_v1_sample1'], V['conf_v1_sample1'], _ = evaluate(H1, llm1)
V['retro_v2_sample2'], V['conf_v2_sample2'], diffs = evaluate(H2, llm)
V['retro_v2_sample1'], V['conf_v2_sample1'], _ = evaluate(H1, llm)
hand = H2
# regex/record reading of the same items (the fallback used for rows the LLM did not read)
rx = {}
if os.path.exists(f'{C.S}/lawchanges_rx_for_llm_rows.tsv'):
    for l in open(f'{C.S}/lawchanges_rx_for_llm_rows.tsv', encoding='utf-8'):
        f = l.rstrip('\n').split('\t')
        k = f[1] + '|' + re.sub(r'\(.*$', '', f[2])
        rx.setdefault(k, f)
def dd(s): return f'{s[:4]}-{s[4:6]}-{s[6:]}' if s and len(s) == 8 else ''
racc = collections.Counter()
for h in H1 + H2:
    f = rx.get(h['key'])
    if not f: continue
    racc['n'] += 1
    racc['retro_yes_no'] += (f[5] != '0') == retro_yes(h['retro_class'])
    racc['effective'] += dd(f[4]) == (h.get('effective_date') or '')
V['retro_rx'] = dict(racc)
V['llm'] = dict(calls=len(llm), errors=sum(1 for x in llm.values() if 'err' in x),
                classes=dict(collections.Counter(x.get('retro_class', 'err') for x in llm.values())))
tok = [l.split('\t') for l in open(f'{C.S}/llm/usage.tsv', encoding='utf-8')] if os.path.exists(f'{C.S}/llm/usage.tsv') else []
V['llm']['tokens'] = sum(int(t[2]) for t in tok)
json.dump(V, open(f'{C.S}/validation.json', 'w', encoding='utf-8'), indent=1)
W_ = json.load(open(f'{C.S}/write_summary.json', encoding='utf-8'))
# ---- report
def pct(a, b): return f'{a}/{b} ({100 * a / b:.0f}%)' if b else f'{a}/0'
L = []
L.append('# Statutes: law changes and supersession of holdings by enactment (caselaw-lean-2)\n')
L.append('Agent: statutes. Files: `lawchanges.tsv`, `supersessions.tsv` (schema in SCHEMA.md). Scripts: '
         '`global-law-lean/lean-proofs/tools/caselaw2/statutes/` (s1_blocks, s2_fetch, s3_lawinfo, s4_pairs, s5_score, s6_retro_llm, '
         's7_write, s8_audit, s9_validate). Work files and caches: `caselaw-lean-2/statutes/`.\n')
L.append('## Counts\n')
L.append(f"- lawchanges.tsv: {W_['lawchanges']:,} (law, US Code block) rewrites, each after at least one decision citing the block "
         f"(1,931,153 citations, 1995 on). Dates from: {', '.join(f'{k} {v:,}' for k, v in sorted(W_['lawchange_src'].items()))}. "
         f"Rows with retroactive_to set: {W_['retro']:,}.")
L.append(f"- supersessions.tsv: {W_['supersessions']:,} rows over {W_['targets']:,} decisions; by evidence: "
         f"{', '.join(f'{k} {v:,}' for k, v in sorted(W_['by_evidence'].items()))}; explicit = 1: {W_['explicit']:,}; "
         f"issue_key attached: {W_['with_issue']:,}; laterCourtSays rows: {W_['laterCourtSays']:,}.")
L.append('- `retroactive_to`: 0 none; a yyyymmdd day = the earliest conduct/claim day the change reaches (before enactment); '
         '1 = applies to matters pending on its effective date whatever the conduct date, no earlier bound stated. '
         '`effective` is the law\'s own effective date where it states one (src `llm:` or `rx:`), else the record\'s in-force day '
         '(src `record:<how the record dated it>`; `record:enacted` = dated on enactment because the record does not read effective dates).\n')
L.append('## Recall: Christiansen & Eskridge (+ Hasen), 1995-2011 Supreme Court decisions overridden by 2011\n')
r = V['recall']
L.append(f"- Any evidence linking the decision to the overriding law: {pct(r['found'], r['gold'])} (overrides work: 20/36). "
         f"Explicit (law, report or court states it): {pct(r['explicit'], r['gold'])}. Score >= 0.5: {pct(r['found_score_ge_0_5'], r['gold'])}.")
L.append('- Per item: `statutes/recall2.tsv`.\n')
L.append('## Precision per evidence type (blind audits; override = express or implicit)\n')
L.append('| evidence | stratum | pairs | audited | override | express | precision | Wilson 95% | score used |')
L.append('|---|---|---|---|---|---|---|---|---|')
for k, c in cal.items():
    ev, st = k.split('|')
    L.append(f"| {ev} | {st} | {c['pairs']:,} | {c['n']} | {c['override']} | {c['express']} | {c['precision'] if c['precision'] is not None else '-'} | "
             f"{c['wilson'][0]}-{c['wilson'][1]} | {c['smoothed']} |")
L.append('\nStrata: first10y = first rewrite of the cited block within 10 years (overrides census/samples); later = another '
         'rewrite or 10-15 years (new, blind reads here); cite = reporter cite in the law/report resolved to the decision, '
         'linked by section (new, blind reads here); SA/FT = Supreme Court + appeals / other courts. Audited pairs carry their '
         'verdict (0.97 / 0.03) as score; others the smoothed stratum precision (k+1)/(n+2).\n')
L.append('## Retroactivity extraction (gpt-5.4-mini, effective-date provisions)\n')
lm = V['llm']
L.append(f"- Calls: {lm['calls']} (law x amended section, for the 34 confirmed overrides and the top 300 candidates), errors {lm['errors']}, "
         f"tokens {lm['tokens']:,}. Classes: {', '.join(f'{k} {v}' for k, v in sorted(lm['classes'].items()))}.")
def line(name, a):
    if not a.get('n'): return
    L.append(f"- {name} ({a['n']}): class {pct(a['class'], a['n'])}; retroactive yes/no {pct(a['retro_yes_no'], a['n'])}; "
             f"effective date {pct(a['effective'], a['n'])}; retroactive_to {pct(a['retroactive_to'], a['n'])}.")
L.append('- Hand reads: subagents read the law text blind (no model output) and classified each item; RETRO_INSTRUCTIONS.md.')
line('Final prompt/packet (v2) on a fresh hand-read sample [headline]', V['retro_v2_sample2'])
line('First run (v1) on the first hand-read sample (blind)', V['retro_v1_sample1'])
line('v2 on the first sample (used to diagnose v1, so optimistic)', V['retro_v2_sample1'])
L.append('- v1 -> v2: v1 packets missed the amending section when a tax law names "section N of the Internal Revenue Code" (no '
         'U.S.C. cite) and dropped passages that name the section by number; v1 also called a delayed effective date "noProvision".')
ra = V.get('retro_rx', {})
if ra.get('n'):
    L.append(f"- The regex/record reading (used for every row the LLM did not read) on both samples: retroactive yes/no "
             f"{pct(ra['retro_yes_no'], ra['n'])}; effective date {pct(ra['effective'], ra['n'])}.")
L.append('- Confusion, fresh sample (hand -> v2): ' + '; '.join(f'{k} {v}' for k, v in sorted(V['conf_v2_sample2'].items())))
L.append('- Disagreements on the fresh sample (hand class -> LLM class; hand date / LLM date):')
for d in diffs: L.append(f'  - {d[0]}: {d[1]} -> {d[2]}; {d[3]} / {d[4]}. {d[5]}')
L.append('')
# two dates: the confirmed overrides with their law change's effective date and reach
L.append('## Two dates: confirmed overrides (question date vs conduct date)\n')
L.append('For a question asked on or after `effective`, the holding still governs conduct before `effective` unless '
         '`retroactive_to` reaches it (rule AB1, doctrine.md 7). One row per confirmed (decision, law), its first linked block.\n')
L.append('| decision | decided | law | block | enacted | effective | retroactive_to | holding still governs conduct | src |')
L.append('|---|---|---|---|---|---|---|---|---|')
names = {}
for l in open(f'{C.S}/evidence.tsv', encoding='utf-8'):
    f = l.rstrip('\n').split('\t'); names[(f[0], f[1])] = (f[12], f[10])
seen = set()
for s in SU:
    if not s['src'].startswith('audit:override') or s['lawchange_id'] == '0': continue
    lc = LC[s['lawchange_id']]
    k = (s['target_node'], lc['law'])
    if k in seen: continue
    seen.add(k)
    nm, dd_ = names.get(k, ('?', '?'))
    rt = lc['retroactive_to']
    gov = (f"before {lc['effective']}" if rt == '0' else ('none (pending matters reached)' if rt == '1' else f'before {rt}'))
    L.append(f"| {nm} | {dd_} | {lc['law']} | {lc['usc_block']} | {lc['enacted']} | {lc['effective']} | {rt} | {gov} | {lc['src']} |")
L.append('')
L.append('## Gaps\n')
L.append('- Citations are read only from 1995 on, so block-level links start in 1995; earlier decisions enter only through a '
         'reporter cite in a law or report (`cite` stratum, linked by section).')
L.append('- Block rewrites the record credits to an edition rather than a law (174,795 first rewrites in the overrides work) '
         'have no law, so no row here.')
L.append('- Law texts: govinfo PLAW starts with the 104th Congress; earlier laws (Civil Rights Act of 1991, etc.) have no text '
         '(`record:...:notext`), so no effective-date reading and no naming evidence.')
L.append('- Effective dates for rows the LLM did not read come from regex rules over the law\'s effective-date passages '
         '(src `rx:<kind>:sec<n>:rank<r>`; rank 0 = in the amending section, 1 = names it, 2 = its title, 3 = Act-wide), '
         'or the record\'s in-force day. See the regex accuracy line above.')
L.append('- quotedWordsStruck covers only the first rewrite of a cited block (decision-text features were not recomputed for later rewrites).')
L.append('- Committee reports: only those listed in the law\'s legislative-history note, part 1 of multi-part reports.')
L.append('- `explicit` for unaudited rows: the naming passage contains override language (overrul, supersed, in response to, '
         'reject the, restore, clarify that, ...); the audits show naming alone often means codification (see the codifies counts).')
L.append('- laterCourtSays and issue_key depend on the reader\'s treatments.tsv and the holdings agent\'s holdings.tsv/issues.tsv; '
         'rows are added by rerunning s7_write.py and s9_validate.py when those files exist.')
L.append('')
open(f'{C.D}/STATUTES.md', 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')
print(json.dumps(V, indent=1)[:3000])
