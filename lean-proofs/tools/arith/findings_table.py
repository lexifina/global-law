"""Write the item-by-item table TaxCode/Indexing/ITEMS.tsv from out/index.json (run after index.py)."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
R = json.load(open(os.path.join(HERE, 'out', 'index.json')))
YEAR = {'rp-22-38': 2023, 'rp-23-34': 2024, 'rp-24-40': 2025, 'rp-25-32': 2026}

def money(v, unit):
    if v is None: return '—'
    if unit == 'c': return f'${v // 100}.{v % 100:02d}'
    if unit == 'm': return f'{v / 10:.1f}¢'
    return f'${v:,}'

def rnd(r):
    k = r[0]
    return {'inc_down': lambda: f'increase ↓ {r[1]}', 'inc_near': lambda: f'increase ≈ {r[1]}', 'amt_down': lambda: f'amount ↓ {r[1]}',
            'amt_near': lambda: f'amount ≈ {r[1]}', 'pen': lambda: f'amount ↓ {r[2]} (≥{r[1]:,}) else ↓ {r[3]}',
            'none': lambda: 'none stated', 'fixed': lambda: 'not indexed this year'}[k]()

def index_of(r):
    if r['by'] == 'med': return 'medical C-CPI-U (Aug) vs medical CPI-U Aug 1996 × C/P(2016)'
    if r['by'] is None: return '—'
    return f"C-CPI-U, COLA for {r['cy']} (Sep–Aug {r['cy'] - 2}/{r['cy'] - 1}, vintage of Aug {r['cy'] - 1} release)"

def verdict(r):
    st = r['status']
    if r['id'].startswith('p6') and r.get('comp_prev') == r['pub'] and st != 'match':
        return 'matches IRS reading (COLA of year before filing year); literal: ' + ('not computable' if r['comp'] is None else money(r['comp'], r['unit']))
    return {'match': 'yes', 'rounding': 'yes up to non-statutory rounding', 'mismatch': '**NO**', 'intermediate': '(intermediate)',
            'not computable': 'not computable'}[st]

def main():
    hdr = ['rev_proc', 'tax_year', 'section', 'id', 'provision', 'base', 'base_year', 'rounding', 'published', 'computed', 'match']
    TAB, NL = chr(9), chr(10)
    rows = [TAB.join(hdr)]
    for r in R:
        base = r['base'] if not isinstance(r['base'], list) else ' + '.join(f'{b:,} ({y})' for b, y in r['base'])
        base = money(base, r['unit']) if isinstance(base, int) else base
        rows.append(TAB.join(str(x) for x in (r['doc'], YEAR[r['doc']], r['sec'], r['id'], r['cite'], base, r['by'] if r['by'] else '-',
                    rnd(r['rnd']), money(r['pub'], r['unit']), money(r['comp'], r['unit']), verdict(r).replace('**', ''))))
    open(os.path.join(ROOT, 'TaxCode', 'Indexing', 'ITEMS.tsv'), 'w', encoding='utf-8', newline=NL).write(NL.join(rows) + NL)

if __name__ == '__main__':
    main()
