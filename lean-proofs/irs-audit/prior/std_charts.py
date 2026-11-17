"""Prior-year Pubs 501 and 17 (irs-prior, 1995-2025): the standard deduction charts against s63 and the year's Rev. Proc.
amounts (indexing/published.json): 'Most People' chart (single/MFS, MFJ/QW, HoH) and the aged/blind chart (basic amount
+ n x the s63(f) additional amount: unmarried amount for single and HoH, married amount for MFJ and MFS)."""
import os, re, json, subprocess
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit')); P = json.load(open(H + '/indexing/published.json'))
STD21 = {'std_mfj': [25100], 'std_single': [12550], 'std_hoh': [25100, 18800]}
def amt(s): return int(s.replace('$', '').replace(',', '').replace(' ', ''))
res = {'docs': 0, 'cells': 0, 'off': [], 'skipped': []}
for name in ('p501', 'p17'):
    for y in range(1995, 2026):
        f = H + '/cache/www.irs.gov/pub/irs-prior/%s--%d.pdf' % (name, y)
        if not os.path.exists(f): continue
        d = dict(P.get(str(y), {})); 
        if y == 2021: d.update({k: {'v': v} for k, v in STD21.items()})
        if y == 2025: d.update({'std_single': {'v': [15750]}, 'std_mfj': {'v': [31500]}, 'std_hoh': {'v': [23625]}})   # s63(c)(7) as amended by Pub. L. 119-21 sec. 70102 (after Rev. Proc. 2024-40)
        if not all(k in d for k in ('std_single', 'std_mfj', 'std_hoh', 'aged_blind')): res['skipped'].append((name, y)); continue
        S, J, Hh = d['std_single']['v'][0], d['std_mfj']['v'][0], d['std_hoh']['v'][-1]; mar, unm = d['aged_blind']['v'][0], d['aged_blind']['v'][1]
        t = subprocess.run(['pdftotext', '-layout', f, '-'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True).stdout
        i = t.find('Standard Deduction Chart for Most People'); res['docs'] += 1
        if i >= 0:
            nums = [amt(x) for x in re.findall(r'\$?\s?(\d{1,2},\d{3})', t[i: i + 900])][:3]
            for lab, g, w in zip(('single', 'mfj', 'hoh'), nums, (S, J, Hh)):
                res['cells'] += 1
                if g != w: res['off'].append((name, y, 'most ' + lab, g, w))
        j = t.find('Standard Deduction Chart for People Born Before')
        if j >= 0:
            seg = t[j: j + 2500]
            rows = [(int(a), amt(b)) for a, b in re.findall(r'^\s+([1-4])\s+\$?\s?(\d{1,2},\d{3})\s*$', seg, re.M)]
            exp = [(n, S + n * unm) for n in (1, 2)] + [(n, J + n * mar) for n in (1, 2, 3, 4)] + [(n, S + n * mar) for n in (1, 2, 3, 4)] + [(n, Hh + n * unm) for n in (1, 2)]
            if len(rows) >= 12:
                for (n, g), (n2, w) in zip(rows[:12], exp):
                    res['cells'] += 1
                    if n != n2 or g != w: res['off'].append((name, y, 'aged/blind %d' % n2, g, w))
            else: res['skipped'].append((name, y, 'aged chart rows %d' % len(rows)))
print(res['docs'], 'docs', res['cells'], 'cells', len(res['off']), 'off'); print(res['off'][:20]); print('skipped', res['skipped'][:20])
json.dump(res, open(H + '/prior/std_charts.json', 'w'), indent=0)
