"""Dump the numeric constants of IRS-Public fact dictionaries (TWE, EITC Assistant, Direct File): path, values -> public/facts_<repo>.tsv"""
import os, re, glob, sys
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit')); S = H + '/src/irs-public'
for repo, pat in (('twe', 'tax-withholding-estimator/src/main/resources/twe/facts/*.xml'), ('eitc', 'eitc-assistant/src/main/resources/credit-assistant/facts/*.xml'),
                  ('df', 'direct-file/direct-file/backend/src/main/resources/tax/*.xml')):
    out = open(H + '/public/facts_%s.tsv' % repo, 'w'); n = 0
    for f in sorted(glob.glob(S + '/' + pat)):
        t = open(f, errors='replace').read()
        for m in re.finditer(r'<Fact path="([^"]+)"(.*?)</Fact>', t, re.S):
            body = m.group(2)
            vals = re.findall(r'<(Dollar|Rational|Int|Decimal)>([^<]+)</\1>', body)
            if not vals: continue
            desc = re.search(r'<Description>(.*?)</Description>', body, re.S)
            out.write('%s\t%s\t%s\t%s\n' % (os.path.basename(f), m.group(1), ' '.join('%s:%s' % v for v in vals), (desc.group(1).strip()[:150].replace('\n', ' ') if desc else '')))
            n += 1
    print(repo, n)
