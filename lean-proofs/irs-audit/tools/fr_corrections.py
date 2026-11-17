"""Federal Register correction notices for the IRS (federalregister.gov API). Index -> src/fr/corrections.json;
raw text of each -> src/fr/text/<document_number>.txt. Sequential, 0.5 s apart, resumable."""
import os, json, time, requests
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit')); D = H + '/src/fr'; os.makedirs(D + '/text', exist_ok=True)
s = requests.Session(); s.headers['User-Agent'] = 'Mozilla/5.0 (compatible; tax-guidance-audit/1.0; research use)'
F = ['document_number', 'title', 'type', 'publication_date', 'citation', 'raw_text_url', 'html_url', 'correction_of', 'cfr_references', 'docket_ids', 'action']
idx = D + '/corrections.json'
if not os.path.exists(idx):
    out = []; page = 1
    while True:
        r = s.get('https://www.federalregister.gov/api/v1/documents.json', params=[('conditions[agencies][]', 'internal-revenue-service'), ('conditions[correction]', '1'), ('per_page', '1000'), ('page', str(page)), ('order', 'oldest')] + [('fields[]', f) for f in F], timeout=120)
        r.raise_for_status(); j = r.json(); out += j.get('results', [])
        print('page', page, len(out), j.get('count'), flush=True)
        if not j.get('next_page_url'): break
        page += 1; time.sleep(1)
    json.dump(out, open(idx, 'w'), indent=0)
out = json.load(open(idx))
n = 0
for d in out:
    f = D + '/text/%s.txt' % d['document_number']
    if os.path.exists(f) or not d.get('raw_text_url'): continue
    r = s.get(d['raw_text_url'], timeout=120)
    if r.status_code in (403, 429, 503): print('STOP', r.status_code); break
    if r.status_code == 200: open(f, 'w').write(r.text); n += 1
    time.sleep(0.5)
print('FR DONE', len(out), 'index,', n, 'new texts', flush=True)
