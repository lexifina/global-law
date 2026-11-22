S = {'cc': 'VU', 'doc': '# Vanuatu 2025: no corporate income tax (1200)\n\nVanuatu has no income tax act (the 1.x model is in B15-no-pit); companies pay business licence fees (P7).', 'taxes': [{'oecd': '1200', 'tax': 'No corporate income tax (cited absence)', 'statute': 'no income tax act in the laws of Vanuatu (1.x B15-no-pit)', 'dated': '2025', 'grade': 'B', 'kernel_parts': ['Absent'], 'unsupported': []}], 'absent': [['cit', 'Vanuatu levies no income tax on companies or individuals (no income tax act; 1.x model B15-no-pit); grade B']], 'guards': ['absent.length == 1']}

# --- R3 session 5 (2026-11-21): withholding under kernel 2.3.0 ---
def _s5_wht_entry(**kw):
    for t in S['taxes']:
        if t['oecd'] == '1200/1100':
            t.update(kw); return
    S['taxes'].append(dict({'oecd': '1200/1100', 'kernel_parts': ['Wht'], 'unsupported': []}, **kw))

S['wht'] = [dict(kind=k, rate=0, statute='Vanuatu levies no income tax (no income tax act; cited absence of the CIT, grade B): nothing is withheld from payments abroad') for k in ('dividend', 'interest', 'royalty', 'services')]
S['whtName'] = 'No withholding on payments abroad (no income tax)'
_s5_wht_entry(tax='No withholding tax on payments abroad (no income tax; cited)', statute='no income tax act in the laws of Vanuatu (1.x B15-no-pit)', dated='2025',
    grade='B', kernel_parts=['Wht', 'Absent'], unsupported=[])
