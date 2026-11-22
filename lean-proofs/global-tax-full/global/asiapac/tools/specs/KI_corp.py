S = {'cc': 'KI', 'doc': '# Kiribati 2025: corporate tax (1200): not reached\n\nIncome Tax Act 1990 (PacLII ki_ita116): text on the build server not read for rates in this pass.', 'taxes': [{'oecd': '1200', 'tax': 'Income tax on companies', 'statute': 'Income Tax Act 1990 (PacLII ki_ita116)', 'dated': 'not reached', 'grade': 'C', 'kernel_parts': [], 'unsupported': ['rates not located']}, {'oecd': '1200/1100', 'tax': 'Withholding tax on payments to non-residents', 'statute': 'Income Tax Act 1990 (PacLII ki_ita116)', 'dated': 'not reached', 'grade': 'C', 'kernel_parts': [], 'unsupported': ['rates not located']}], 'absent': [], 'guards': ['absent.length == 0']}

# --- R3 session 7 (2026-11-21): withholding pass 7 ---
def _s7_wht_entry(add_unsupported=(), drop_unsupported=(), **kw):
    for t in S['taxes']:
        if t['oecd'] == '1200/1100':
            t.update(kw)
            t['unsupported'] = [u for u in t.get('unsupported', []) if not any(d in u for d in drop_unsupported)] + list(add_unsupported)
            return
    S['taxes'].append(dict({'oecd': '1200/1100', 'kernel_parts': ['Wht'], 'unsupported': list(add_unsupported)}, **kw))

_K = "Income Tax Act 1990 (Kiribati)"
S['wht'] = [dict(kind=k, rate=3000, statute=_K + ' s. 90 (1) (a), (2) (a) (final), s. 9 (standard rate 30 %)' + x) for k, x in
            [('dividend', ''), ('interest', ''), ('royalty', ''), ('services', '; services taken as a "management charge" (s. 3: any payment for any management or administrative service)')]]
S['whtName'] = 'Withholding tax on international transactions (ITA 1990 s. 90)'
_s7_wht_entry(tax='Withholding tax on international transactions (dividends, interest, royalties, management charges: standard rate 30 %)',
    statute=_K + ' ss. 3, 9, 90, 117, 121', dated='Act as enacted (PacLII num_act ita1990116, Wayback 20230628072620) with the amending Acts 1993-2009 checked for ss. 9 and 90; MFED fact sheet (June 2025, mfed.gov.ki node/115) states the 30 % rate', grade='A', kernel_parts=['Wht'],
    drop_unsupported=['rates not located'],
    add_unsupported=['services other than management or administrative services not distinguished; natural resource payments not a payment kind'])
S['guards'] = S.get('guards', []) + ['wht.amount { kind := .dividend, amount := 1000 } == 300', 'wht.amount { kind := .services, amount := 1000, toCompany := false } == 300']


# --- R3 session 11 (2026-11-21): year-in-force audit: downgraded to C (old content kept in S['_pre11']) ---
_N11 = 'session 11 year-in-force audit: Income Tax Act 1990 as enacted with amending Acts to 2009 checked; nothing later, and no 2025 version or official 2025 source reached: grade C'
S['_pre11'] = {k: S.get(k) for k in ('sched', 'wht', 'guards', 'extra_lean', 'extra_run', 'extra_covers', 'taxes', 'unsupported')}
for _k in ['wht']:
    S[_k] = [] if _k != 'extra_lean' else ''
S['guards'] = [g for g in S.get('guards', []) if g.startswith('absent')]
S['unsupported'] = [u for u in S.get('unsupported', []) if not True] + [['company', _N11]]
for _t in S['taxes']:
    if _t['oecd'] in ['1200/1100']:
        _t.update(grade='C', dated='not modelled (' + _N11 + ')', kernel_parts=[], unsupported=[_N11])
