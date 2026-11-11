import json,glob,os,re,collections
base='..'
def norm(s): return re.sub(r'[\s\-­]+','',s).lower().replace('’',"'").replace('“','"').replace('”','"')
idx=[];bad=[];tags=collections.Counter()
for f in sorted(glob.glob(f'{base}/cases/*.json')):
    d=json.load(open(f,encoding='utf-8')); i=d['id']
    t=norm(open(f'{base}/cases/text/{i}.txt',encoding='utf-8').read())
    miss=[x['fact_id'] for x in d.get('findings_of_fact',[]) if norm(x.get('snippet','')) not in t]
    if miss: bad.append((i,miss))
    iss=[dict(issue_id=x['issue_id'],tags=x['tags'],computable=x['computable'],prevailing_party=x.get('prevailing_party')) for x in d['issues']]
    if d.get('suitable',True):
        for x in d['issues']:
            for g in x['tags']: tags[g]+=1
    idx.append(dict(id=i,citation=d['citation'],case_name=d['case_name'],date=d['date'],opinion_type=d['opinion_type'],tax_years=d['tax_years'],
        suitable=d.get('suitable',True),n_findings=len(d.get('findings_of_fact',[])),any_computable=any(x['computable'] for x in d['issues']),
        issues=iss,decision=d['decision'].get('summary') or d['decision'].get('text'),json=f'cases/{i}.json',text=f'cases/text/{i}.txt',snippets_unverified=dict(bad).get(i,[])))
json.dump(dict(generated='2026-11-11',source='US Tax Court DAWSON public API (opinion PDFs)',count=len(idx),
    suitable_count=sum(x['suitable'] for x in idx),issue_tag_counts=dict(tags.most_common()),cases=idx),open(f'{base}/index.json','w',encoding='utf-8'),indent=1)
print(len(idx),'cases;',sum(x['suitable'] for x in idx),'suitable'); print(dict(tags.most_common()))
for b in bad: print('snippet mismatch',b)
