import json, yaml, glob, os, datetime
base = glob.glob(os.path.expanduser('~/venvs/pe/lib/python3*/site-packages/policyengine_us/parameters/gov/states'))[0]
out = {}
for pat in ['*/tax/income/credits/eitc/match.yaml','*/tax/income/credits/eitc/rate.yaml','*/tax/income/credits/eitc_fraction.yaml',
            '*/tax/income/credits/eitc/fraction.yaml','*/tax/income/credits/earned_income/eitc_fraction.yaml',
            '*/tax/income/credits/eitc/with_children/match.yaml','*/tax/income/credits/eitc/match/has_young_child.yaml',
            '*/tax/income/credits/eitc/match/refundable.yaml','*/tax/income/credits/eitc/refundable/married_or_has_child/match.yaml',
            '*/tax/income/credits/eitc/rate/with_qualifying_child.yaml',
            '*/tax/income/credits/cdcc/match.yaml','*/tax/income/credits/cdcc/rate.yaml','*/tax/income/credits/cdcc/refundable/match.yaml',
            '*/tax/income/credits/dependent_care_service/match.yaml','*/tax/income/credits/cdcc/non_refundable/match.yaml']:
    for f in glob.glob(os.path.join(base, pat)):
        st = os.path.relpath(f, base).split('/')[0]
        d = yaml.safe_load(open(f))
        vals = d.get('values')
        v25 = None
        if isinstance(vals, dict):
            ks = sorted(k for k in vals if str(k) <= '2025-12-31')
            if ks: v25 = vals[ks[-1]]
        kind = 'eitc' if 'eitc' in f or 'earned' in f else 'cdcc'
        refs = [r.get('href') for r in (d.get('metadata', {}).get('reference') or []) if isinstance(r, dict)][:2]
        out.setdefault(st, {}).setdefault(kind, []).append(dict(file=os.path.relpath(f, base), value_2025=v25, refs=refs))
json.dump(out, open('credit_matches_pe.json','w'), indent=1, default=str)
for st in sorted(out):
    print(st, {k: [x['value_2025'] for x in v] for k, v in out[st].items()})
