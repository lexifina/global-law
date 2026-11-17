"""Written determinations before 2011 are numbered YYWWNNN (7 digits): probe the same sample weeks for 2000 and 2010."""
import os, sys, time, subprocess, json
sys.path.insert(0, os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/tools'))
while subprocess.run(['pgrep', '-f', 'wd/probe.py|final_fetch.sh'], capture_output=True).stdout.strip():
    time.sleep(30)
import fetch
P = json.load(open(os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/wd/probe.json')))
for y in (2000, 2010):
    for w in (5, 18, 31, 44):
        found = []; miss = 0; n = 0
        while miss < 4 and n < 120:
            n += 1
            num = '%02d%02d%03d' % (y % 100, w, n)
            f, code = fetch.get('https://www.irs.gov/pub/irs-wd/%s.pdf' % num)
            if f: found.append(num); miss = 0
            else: miss += 1
            if code in ('403', '429'): print('STOP', code, flush=True); sys.exit()
        P['%d-%02d' % (y, w)] = found
        print(y, w, len(found), flush=True)
json.dump(P, open(os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/wd/probe.json'), 'w'), indent=1)
print('DONE2', flush=True)
