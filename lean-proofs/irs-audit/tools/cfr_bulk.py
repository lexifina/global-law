"""26 CFR annual editions 1997-2016 (GovInfo bulk XML; title 26 is absent from the 1996 bulk folder).
Waits until govinfo_cb.py has finished (one GovInfo stream at a time), then fetches CFR-<year>-title-26.zip, 4 at a time,
and unzips into src/cfr_annual/<year>/."""
import os, sys, time, json, subprocess, zipfile, concurrent.futures as cf
sys.path.insert(0, os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/tools')); import cfetch, requests
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit'))
while subprocess.run(['pgrep', '-f', 'govinfo_cb.py'], capture_output=True).stdout.strip(): time.sleep(30)
cfetch.host('www.govinfo.gov', 4)
def one(y):
    u = 'https://www.govinfo.gov/bulkdata/CFR/%d/title-26/CFR-%d-title-26.zip' % (y, y)
    f, c = cfetch.get(u, head_first=False, timeout=1800)
    if f:
        d = H + '/src/cfr_annual/%d' % y
        if not os.path.isdir(d):
            os.makedirs(d + '.tmp', exist_ok=True); zipfile.ZipFile(f).extractall(d + '.tmp'); os.replace(d + '.tmp', d)
    print('CFR', y, c, flush=True); return c
with cf.ThreadPoolExecutor(4) as ex: r = list(ex.map(one, range(1997, 2017)))
print('CFR DONE', r, flush=True)
