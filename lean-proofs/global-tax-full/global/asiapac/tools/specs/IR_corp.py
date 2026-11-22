S = {'cc': 'IR', 'doc': '# Iran 2025 (1404): corporate income tax: not reached\n\nDirect Taxes Act art. 105 (25 %) and the withholding articles: no official text reached from the build server (rc.majlis.ir / the 1.x rescue folders).', 'taxes': [{'oecd': '1200', 'tax': 'Income tax on legal persons', 'statute': 'Direct Taxes Act art. 105', 'dated': 'not reached', 'grade': 'C', 'kernel_parts': [], 'unsupported': ['text not reached']}, {'oecd': '1200/1100', 'tax': 'Withholding tax on payments to non-residents', 'statute': 'Direct Taxes Act arts. 107-109', 'dated': 'not reached', 'grade': 'C', 'kernel_parts': [], 'unsupported': ['text not reached']}], 'absent': [], 'guards': ['absent.length == 0']}

# --- R3 session 7 (2026-11-21): withholding pass 7 ---
def _s7_wht_entry(add_unsupported=(), drop_unsupported=(), **kw):
    for t in S['taxes']:
        if t['oecd'] == '1200/1100':
            t.update(kw)
            t['unsupported'] = [u for u in t.get('unsupported', []) if not any(d in u for d in drop_unsupported)] + list(add_unsupported)
            return
    S['taxes'].append(dict({'oecd': '1200/1100', 'kernel_parts': ['Wht'], 'unsupported': list(add_unsupported)}, **kw))

_s7_wht_entry(tax='Withholding tax on payments to non-residents', statute='Direct Taxes Act arts. 107-109', dated='not reached', grade='C', kernel_parts=[], drop_unsupported=['text not reached'], add_unsupported=['session 7: not retried: qavanin.ir bot check (not bypassed), dotic.ir 403, rc.majlis.ir / intamedia.ir no answer in sessions 4-6: grade C'])
