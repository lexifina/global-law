S = {'cc': 'CN-MO', 'doc': '# Macao 2025: complementary tax on income (1200): not reached\n\nRegulamento do Imposto Complementar de Rendimentos (Lei n.º 21/78/M) and the 2025 budget law (12 % above MOP 600,000) were not fetched (bo.io.gov.mo not tried in this pass).', 'taxes': [{'oecd': '1200', 'tax': 'Imposto complementar de rendimentos', 'statute': 'Lei n.º 21/78/M, tabela; Lei do Orçamento 2025 (exemption to MOP 600,000)', 'dated': 'not reached', 'grade': 'C', 'kernel_parts': [], 'unsupported': ['text not fetched: bo.io.gov.mo would unlock']}], 'absent': [], 'guards': ['absent.length == 0']}

# --- R3 session 7 (2026-11-21): withholding pass 7 ---
def _s7_wht_entry(add_unsupported=(), drop_unsupported=(), **kw):
    for t in S['taxes']:
        if t['oecd'] == '1200/1100':
            t.update(kw)
            t['unsupported'] = [u for u in t.get('unsupported', []) if not any(d in u for d in drop_unsupported)] + list(add_unsupported)
            return
    S['taxes'].append(dict({'oecd': '1200/1100', 'kernel_parts': ['Wht'], 'unsupported': list(add_unsupported)}, **kw))

_s7_wht_entry(tax='Withholding on payments to non-residents', statute='Regulamento do Imposto Complementar de Rendimentos (Lei n.º 21/78/M) as amended; Regulamento do Imposto Profissional', dated='not reached', grade='C', kernel_parts=[], drop_unsupported=[], add_unsupported=['session 7: bo.io.gov.mo and images.io.gov.mo give no answer from a second machine; Wayback holds the Boletim Oficial 1978 n.º 36 as published (lei21.asp, 2025-10-15), not a consolidation: grade C'])
