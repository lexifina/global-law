"""Load monthly C-CPI-U (SUUR0000SA0) and CPI-U (CUUR0000SA0) values.

Sources (saved under ~/docs/data/cpi):
  ccpiu_v<date>.csv : ALFRED vintage of SUUR0000SA0 as of <date> (BLS release date of the August index)
  bls_<year>.json   : BLS public API v2, current (latest) values, retrieved 2026-11-16
All values are kept as integer thousandths of an index point (the published 3-decimal values).
"""
import csv, json, glob, os
D = os.path.expanduser('~/docs/data/cpi')
VINTAGE = {2022: '2022-09-13', 2023: '2023-09-13', 2024: '2024-09-11', 2025: '2025-09-11', 2026: '2026-09-30'}

def _milli(s):
    a, b = s.split('.')
    return int(a) * 1000 + int((b + '000')[:3])

def vintage(year):
    """C-CPI-U monthly values as of the release of August `year` (the §1(f)(6)(A) vintage for tax year year+1)."""
    out = {}
    with open(f'{D}/ccpiu_v{VINTAGE[year]}.csv') as f:
        r = csv.reader(f); next(r)
        for d, v in r:
            if v and v != '.':
                y, m, _ = d.split('-'); out[(int(y), int(m))] = _milli(v)
    return out

def bls(series):
    out = {}
    for fn in glob.glob(f'{D}/bls_*.json'):
        for s in json.load(open(fn))['Results']['series']:
            if s['seriesID'] != series: continue
            for row in s['data']:
                if row['period'].startswith('M') and row['period'] != 'M13' and row['value'] not in ('-', ''):
                    out[(int(row['year']), int(row['period'][1:]))] = _milli(row['value'])
    return out

def months(year):
    """The 12 months Sep(year-1)..Aug(year) (§1(f)(4), (f)(6)(B))."""
    return [(year - 1, m) for m in range(9, 13)] + [(year, m) for m in range(1, 9)]

def ysum(series, year):
    return sum(series[k] for k in months(year))

MARCH_VINTAGE = {2024: '2024-04-10', 2025: '2025-04-10'}

def march_vintage(year):
    """C-CPI-U as of the release of the March `year` index (for §223(g), which uses 12 months ending March 31)."""
    out = {}
    with open(f'{D}/ccpiu_v{MARCH_VINTAGE[year]}.csv') as f:
        r = csv.reader(f); next(r)
        for d, v in r:
            if v and v != '.':
                y, m, _ = d.split('-'); out[(int(y), int(m))] = _milli(v)
    return out

def months_mar(year):
    """The 12 months April (year-1) .. March year (§1(f)(4) as modified by §223(g)(1))."""
    return [(year - 1, m) for m in range(4, 13)] + [(year, m) for m in range(1, 4)]

MED_VINTAGE = {2024: '2024-09-11', 2025: '2025-09-11'}

def med_vintage(year):
    """Medical care component of the C-CPI-U (SUUR0000SAM) as of the release of August `year`."""
    out = {}
    with open(f'{D}/ccpiu_med_v{MED_VINTAGE[year]}.csv') as f:
        r = csv.reader(f); next(r)
        for d, v in r:
            if v and v != '.':
                y, m, _ = d.split('-'); out[(int(y), int(m))] = _milli(v)
    return out
