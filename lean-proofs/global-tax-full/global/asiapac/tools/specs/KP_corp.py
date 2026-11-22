S = {'cc': 'KP', 'doc': '# DPRK 2025: tax on foreign-invested businesses (1200): not reached\n\nThe DPRK levies no tax on its citizens; the Law on Taxation of Foreign-invested Businesses and Foreign Individuals (1993, amended) charges enterprise income tax (25 %, Rason 14 %) on foreign-invested businesses only. No official text reached.', 'taxes': [{'oecd': '1200', 'tax': 'Enterprise income tax (foreign-invested businesses only)', 'statute': 'Law on Taxation of Foreign-invested Businesses and Foreign Individuals (1993, amended)', 'dated': 'not reached', 'grade': 'C', 'kernel_parts': [], 'unsupported': ['no official text available']}], 'absent': [], 'guards': ['absent.length == 0']}

# --- R3 session 7 (2026-11-21): withholding pass 7 ---
def _s7_wht_entry(add_unsupported=(), drop_unsupported=(), **kw):
    for t in S['taxes']:
        if t['oecd'] == '1200/1100':
            t.update(kw)
            t['unsupported'] = [u for u in t.get('unsupported', []) if not any(d in u for d in drop_unsupported)] + list(add_unsupported)
            return
    S['taxes'].append(dict({'oecd': '1200/1100', 'kernel_parts': ['Wht'], 'unsupported': list(add_unsupported)}, **kw))

_s7_wht_entry(tax='Tax on foreign-invested businesses and foreign individuals (payments abroad)', statute='Law of the DPRK on Taxation of Foreign-Invested Businesses and Foreign Individuals', dated='not reached', grade='C', kernel_parts=[], drop_unsupported=[], add_unsupported=['session 7: no official or reliable text of the DPRK foreign-investment tax law reached (no national legislation portal; secondary English compilations not located): grade C'])
