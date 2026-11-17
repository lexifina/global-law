"""Sample the IRS written determinations (irs.gov/pub/irs-wd/YYWWNNNNN.pdf): probe sequence numbers per sampled week
until 4 consecutive misses. Waits for the IRM harvest to finish so that requests stay sequential."""
import os, sys, time, subprocess, json
sys.path.insert(0, os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/tools'))
while subprocess.run(['pgrep', '-f', 'irm/harvest.py'], capture_output=True).stdout.strip():
    time.sleep(60)
import fetch
weeks = [(y, w) for y in (2000, 2010, 2020, 2025) for w in (5, 18, 31, 44)]
out = {}
for y, w in weeks:
    found = []; miss = 0; n = 0
    while miss < 4 and n < 120:
        n += 1
        num = '%02d%02d%03d' % (y % 100, w, n) if y < 2000 or False else '%d%02d%03d' % (y, w, n)
        url = 'https://www.irs.gov/pub/irs-wd/%s.pdf' % num
        f, code = fetch.get(url)
        if f: found.append(num); miss = 0
        else: miss += 1
        if code in ('403', '429'): print('STOP', code, url, flush=True); json.dump(out, open(os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/wd/probe.json'), 'w')); sys.exit()
    out['%d-%02d' % (y, w)] = found
    print(y, w, len(found), flush=True)
json.dump(out, open(os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/wd/probe.json'), 'w'), indent=1)
print('DONE', flush=True)
