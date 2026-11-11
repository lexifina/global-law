"""Blind re-encoding / holdout comparison.
usage: python compare_blind.py blind|holdout
blind:   expected items = the court figures from the ORIGINAL encoding (encoded/<id>.case.json; notice-position variants
         skipped), injected into the blind case with the same tax year; also reports what the original encoding computed
         for the same item (from prepost_current.json).
holdout: expected items = holdout/keys/<id>.key.json (per-year items may carry "year").
Dependent-keyed items (qualifyingChild:<name>...) are mapped to the blind encoding's dependent by name, else by position."""
import json, sys, os, subprocess, tempfile, glob, re

SET = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__)); V = os.path.dirname(HERE)
ROOT = r'C:\Users\alany\Documents\global-law-lean\lean-proofs'
env = dict(os.environ); env['PATH'] = os.path.expanduser('~/.elan/bin') + os.pathsep + env['PATH']


def run(cases):
    t = tempfile.mkdtemp(); i = os.path.join(t, 'in.json'); o = os.path.join(t, 'out.json')
    json.dump(cases, open(i, 'w', encoding='utf-8'))
    p = subprocess.run(['lake', 'env', 'lean', '--run', 'LegalProofs/USTax/TaxCourt/Run.lean', i, o], cwd=ROOT, env=env,
                       capture_output=True, text=True, encoding='utf-8')
    if not os.path.exists(o): return None, p.stdout + p.stderr
    return json.load(open(o, encoding='utf-8')), p.stdout


def norm(n): return re.sub(r'[^a-z0-9]', '', n.lower())


def mapname(item, orig_deps, blind_deps):
    if ':' not in item: return item
    k, n = item.split(':', 1)
    bn = [d.get('name', '') for d in blind_deps]
    for b in bn:
        if norm(b) == norm(n): return k + ':' + b
    on = [d.get('name', '') for d in orig_deps]
    if n in on and on.index(n) < len(bn): return k + ':' + bn[on.index(n)]
    return item


def as_list(x): return x if isinstance(x, list) else [x]


def expstr(e):
    if 'value' in e and e['value'] is not None: return str(e['value'])
    if 'flag' in e and e['flag'] is not None: return 'true' if e['flag'] else 'false'
    return str(e.get('text'))


pre = json.load(open(os.path.join(V, 'prepost_current.json'), encoding='utf-8')) if SET == 'blind' else {}
report = {'set': SET, 'cases': []}
for f in sorted(glob.glob(os.path.join(V, SET, 'encoded', '*.case.json'))):
    cid = os.path.basename(f)[:-10]
    blinds = as_list(json.load(open(f, encoding='utf-8')))
    if SET == 'blind':
        variants = as_list(json.load(open(os.path.join(V, '..', 'encoded', cid + '.case.json'), encoding='utf-8')))
        oc = pre.get(cid, {}).get('outcomes', [])
    else:
        key = json.load(open(os.path.join(V, 'holdout', 'keys', cid + '.key.json'), encoding='utf-8'))
    for blind in blinds:
        year = blind.get('taxYear')
        label = cid if len(blinds) == 1 else f'{cid}#{year}'
        exp, odeps, origcomp = [], [], []
        if SET == 'blind':
            for k, v in enumerate(variants):
                if re.search(r'notice position|not a holding', v.get('citation', ''), re.I): continue
                if len(blinds) > 1 and v.get('taxYear') != year: continue
                odeps = odeps or v.get('facts', {}).get('dependents', [])
                checks = oc[k]['checks'] if k < len(oc) else []
                for e in v.get('expected', []):
                    ch = next((c for c in checks if c['item'] == e['item'] and c['expected'] == expstr(e)), None)
                    exp.append(e); origcomp.append(ch)
        else:
            for e in key['expected']:
                if len(blinds) > 1 and e.get('year') not in (None, year): continue
                exp.append({k: e[k] for k in ('item', 'value', 'flag', 'text', 'note') if k in e}); origcomp.append(None)
        bdeps = blind.get('facts', {}).get('dependents', [])
        inj = [dict(e, item=mapname(e['item'], odeps, bdeps)) for e in exp]
        c2 = {k: v for k, v in blind.items() if k not in ('inferred', 'unencodable')}
        c2['expected'] = inj
        out, log = run([c2])
        if out is None:
            report['cases'].append({'id': label, 'error': log[-300:]}); continue
        o = out[0]; rows = []
        for e, ch, oc_ in zip(inj, o['checks'], origcomp):
            r = {'item': e['item'], 'court': ch['expected'], 'blind': ch['computed'], 'blind_ok': ch['ok']}
            if oc_: r['original'] = oc_['computed']; r['original_ok'] = oc_['ok']
            rows.append(r)
        report['cases'].append({'id': label, 'deficiency_blind': o.get('deficiency'), 'errors': o.get('errors', []),
                                'inferred': blind.get('inferred', []), 'unencodable': blind.get('unencodable', []),
                                'items': rows})

allr = [r for c in report['cases'] for r in c.get('items', [])]
s = {'cases': len({c['id'].split('#')[0] for c in report['cases']}), 'items': len(allr),
     'blind_match': sum(r['blind_ok'] for r in allr),
     'blind_not_computed': sum(r['blind'] == '(not computed)' for r in allr)}
if SET == 'blind':
    s.update(original_match=sum(r.get('original_ok', False) for r in allr),
             both_match=sum(r['blind_ok'] and r.get('original_ok', False) for r in allr),
             original_only=sum((not r['blind_ok']) and r.get('original_ok', False) for r in allr),
             blind_only=sum(r['blind_ok'] and not r.get('original_ok', False) for r in allr),
             blind_equals_original_value=sum(r['blind'] == r.get('original') for r in allr))
report['summary'] = s
json.dump(report, open(os.path.join(V, f'{SET}_comparison.json'), 'w', encoding='utf-8'), indent=1)
print(json.dumps(s, indent=1))
for c in report['cases']:
    if 'error' in c: print('ERROR', c['id'], c['error'])
    for r in c.get('items', []):
        if not r['blind_ok'] or (SET == 'blind' and not r.get('original_ok', False)): print(c['id'], r)
