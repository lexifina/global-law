"""Fetch now (one sequential stream, 0.5 s apart) the irs-prior withholding guides needed for the table check:
p15t--2020..2025, p15--1995..2025, n1036--1995..2026. Same cache as everything else."""
import os, sys, time
sys.path.insert(0, os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/tools'))
import cfetch
cfetch.host('www.irs.gov', 1)
U = ['https://www.irs.gov/pub/irs-prior/p15t--%d.pdf' % y for y in range(2020, 2026)] + ['https://www.irs.gov/pub/irs-prior/p15--%d.pdf' % y for y in range(1995, 2026)] + ['https://www.irs.gov/pub/irs-prior/n1036--%d.pdf' % y for y in range(1995, 2027)]
for u in U:
    f, c = cfetch.get(u); print(c, u, flush=True); time.sleep(0.5)
