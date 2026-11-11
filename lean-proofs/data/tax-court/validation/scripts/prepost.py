"""Compare item-level checks of the ORIGINAL encodings under the pre-case framework (commit 2e1e6ecae8d, built in an
isolated export) and the current framework. Items whose key did not exist before the cases were seen are 'post-hoc rules'."""
import json,collections
b=json.load(open('prepost_base.json',encoding='utf-8')); c=json.load(open('prepost_current.json',encoding='utf-8'))
def items(r):
    out={}
    if 'error' in r: return None
    for k,o in enumerate(r['outcomes']):
        for ch in o['checks']: out[(k,ch['item'])]=ch
    return out,[e for o in r['outcomes'] for e in o['errors']]
rows=[];tot=collections.Counter()
for cid in sorted(c):
    ci=items(c[cid]); bi=items(b[cid])
    if ci is None: continue
    for key,ch in ci[0].items():
        bch=None if bi is None else bi[0].get(key)
        if bi is None: bstate='base-parse-error'
        elif bi[1] and any('outside' in e for e in bi[1]): bstate='base-year-unsupported'
        elif bch is None: bstate='base-no-item'
        elif bch['computed']=='(not computed)': bstate='base-not-computed'
        else: bstate='base-ok' if bch['ok'] else 'base-differs'
        rows.append({'case':cid,'item':key[1],'variant':key[0],'current_ok':ch['ok'],'base':bstate,
                     'expected':ch['expected'],'current':ch['computed'],'base_computed':None if bch is None else bch['computed']})
        tot[(ch['ok'],bstate)]+=1
cur_ok=sum(r['current_ok'] for r in rows)
summ={'items':len(rows),'current_match':cur_ok,
 'by_current_and_base':{f"current_{'match' if k[0] else 'differs'}|{k[1]}":v for k,v in sorted(tot.items())},
 'base_errors':{cid:b[cid].get('error','')[:200] for cid in b if 'error' in b[cid]}}
json.dump({'summary':summ,'rows':rows},open('prepost_items.json','w',encoding='utf-8'),indent=1)
print(json.dumps(summ,indent=1))
