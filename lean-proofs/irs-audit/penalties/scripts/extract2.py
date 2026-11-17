#!/usr/bin/env python3
"""pdftotext (layout + plain) for every fetched opinion; 8 processes; incremental. Records chars per page;
pages with no text layer are counted (OCR only if few)."""
import json, os, subprocess, sys
from multiprocessing import Pool
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/penalties')
def one(did):
    pdf = '%s/cache/pdf/%s.pdf' % (H, did); lay = '%s/data2/lay/%s.txt' % (H, did); txt = '%s/data2/txt/%s.txt' % (H, did)
    if not os.path.exists(pdf): return did, None
    if not os.path.exists(lay):
        subprocess.run(['pdftotext', '-layout', pdf, lay + '.tmp'], capture_output=True, timeout=300); os.replace(lay + '.tmp', lay) if os.path.exists(lay + '.tmp') else None
    if not os.path.exists(txt):
        subprocess.run(['pdftotext', pdf, txt + '.tmp'], capture_output=True, timeout=300); os.replace(txt + '.tmp', txt) if os.path.exists(txt + '.tmp') else None
    return did, os.path.getsize(txt) if os.path.exists(txt) else 0
if __name__ == '__main__':
    inv = json.load(open(H + '/data2/inventory.json'))
    with Pool(int(sys.argv[1]) if len(sys.argv) > 1 else 8) as p:
        res = dict(p.map(one, [o['pick'] for o in inv], chunksize=20))
    have = {k: v for k, v in res.items() if v is not None}
    print('pdf present', len(have), 'empty text (<500 bytes)', sum(1 for v in have.values() if v < 500))
    json.dump(res, open(H + '/data2/extract_sizes.json', 'w'))
