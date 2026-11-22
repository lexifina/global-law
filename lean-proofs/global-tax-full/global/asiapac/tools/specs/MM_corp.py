S = {'cc': 'MM', 'doc': '# Myanmar 2025-26: income tax on companies (1200)\n\nUnion Tax Law 2025 and the Income Tax Law 1974: not on the build server (B from the IRD tables).\n* Companies 22 %. Withholding on non-residents (MOPF notification): not reached (C).', 'regimeName': 'Income tax on companies', 'unsupported': [], 'taxes': [{'oecd': '1200', 'tax': 'Income tax on companies', 'statute': 'Income Tax Law 1974 s. 14; Union Tax Law 2025', 'dated': '2025-26', 'grade': 'B', 'kernel_parts': ['CorpRegime'], 'unsupported': []}, {'oecd': '1200/1100', 'tax': 'Withholding on non-residents', 'statute': 'Income Tax Law s. 15; MOPF notification', 'dated': 'not reached', 'grade': 'C', 'kernel_parts': [], 'unsupported': ['notification not reached']}], 'sched': [(0, 2200)], 'citStatute': 'Income Tax Law 1974 s. 14; Union Tax Law 2025', 'guards': ['cit.citTax { profit := 1000000 } == 220000']}

# --- R3 session 7 (2026-11-21): withholding pass 7 ---
def _s7_wht_entry(add_unsupported=(), drop_unsupported=(), **kw):
    for t in S['taxes']:
        if t['oecd'] == '1200/1100':
            t.update(kw)
            t['unsupported'] = [u for u in t.get('unsupported', []) if not any(d in u for d in drop_unsupported)] + list(add_unsupported)
            return
    S['taxes'].append(dict({'oecd': '1200/1100', 'kernel_parts': ['Wht'], 'unsupported': list(add_unsupported)}, **kw))

_s7_wht_entry(tax='Withholding on non-residents', statute='Income Tax Law s. 15; MOPF notification (No. 47/2017 as amended)', dated='not reached', grade='C', kernel_parts=[], drop_unsupported=['notification not reached'], add_unsupported=['session 7: ird.gov.mm/policies/notification lists notifications from 2021 to 2026 only (pages 1-6, Burmese titles by number); the 2021 PDFs read (3, 36, 38, 57, 389, 510 of 2021) are in legacy Burmese font encodings (pdftotext unreadable, not OCRed); the UTL 2025 (mm/law/mm_utl2025.pdf) sets income tax rates but no withholding on payments abroad: grade C'])
