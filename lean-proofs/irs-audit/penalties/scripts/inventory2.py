#!/usr/bin/env python3
"""Deduplicate docket entries to opinions (consolidated cases share one opinion), pick one entry per opinion."""
import json, os, re, collections
D = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/penalties')
E = json.load(open(D + '/cache/inventory_entries.json'))
def cite(t):
    t = re.sub(r'\s+', ' ', t)
    m = re.search(r'T\.\s?C\.\s?Memo\.?\s?(\d{4})\s?-\s?(\d+)', t)
    if m: return 'TCM %s-%s' % (m.group(1), int(m.group(2)))
    m = re.search(r'Summ(?:ary)?\.?\s?Op(?:inion)?\.?\s?(\d{4})\s?-\s?(\d+)', t)
    if m: return 'TCS %s-%s' % (m.group(1), int(m.group(2)))
    m = re.search(r'(\d{2,3})\s?T\.\s?C\.\s?(?:No\.?\s?)?(\d+)', t)
    if m: return 'TC %s-%s' % (m.group(1), int(m.group(2)))
    return None
ops = collections.OrderedDict()
for e in sorted(E, key=lambda e: (e['filingDate'], e['docketNumber'])):
    c = cite(e['documentTitle'])
    k = c or 'X|%s|%s|%s|%s|%s' % (e['eventCode'], e.get('judge'), e['filingDate'][:10], e.get('numberOfPages'), e['documentTitle'])
    o = ops.setdefault(k, {'key': k, 'cite': c, 'year': int(e['filingDate'][:4]), 'type': e['eventCode'], 'entries': [], 'keywords': set()})
    o['entries'].append({'docketNumber': e['docketNumber'], 'docketEntryId': e['docketEntryId'], 'caption': e['caseCaption'], 'title': e['documentTitle'], 'pages': e.get('numberOfPages'), 'filingDate': e['filingDate'], 'judge': e.get('judge')})
    o['keywords'] |= set(e['keywords'])
for o in ops.values():
    o['keywords'] = sorted(o['keywords'])
    have = [x for x in o['entries'] if os.path.exists('%s/cache/pdf/%s.pdf' % (D, x['docketEntryId']))]
    o['pick'] = (have or o['entries'])[0]['docketEntryId']
    o['cached_before'] = bool(have)
json.dump(list(ops.values()), open(D + '/data2/inventory.json', 'w'))
by = collections.Counter((o['year'], o['type']) for o in ops.values())
print('entries', len(E), 'opinions', len(ops), 'already cached', sum(o['cached_before'] for o in ops.values()))
print('by type', collections.Counter(o['type'] for o in ops.values()))
