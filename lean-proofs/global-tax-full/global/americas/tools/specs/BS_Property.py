S = {'cc': 'BS', 'fam': 'Property', 'doc': '# BS 2025: Property family — no dated statute text reached (grade C)\n\n* Inheritance, gift and wealth taxes (registry: none levied (not cited from a text)): tried no statute read; would unlock: a text showing the abolition or absence.', 'families': '[]', 'taxes': [{'oecd': '4300', 'tax': 'Inheritance, gift and wealth taxes', 'statute': 'registry: none levied (not cited from a text)', 'grade': 'C', 'status': 'unsupported', 'package': 'P6', 'kernel_parts': [], 'tried': 'no statute read', 'unsupported': ['would unlock: a text showing the abolition or absence']}, {'oecd': '4200', 'tax': 'Net wealth tax', 'statute': 'Department of Inland Revenue (inlandrevenue.finance.gov.bs): list of taxes administered', 'dated': 'Wayback copy dated 2025; pass 13, 2026-11-21', 'grade': 'B', 'status': 'not levied', 'package': 'P6', 'kernel_parts': ['Absent'], 'why': "Not levied (convention R2-P13-CARIB (no tax-legality clause in the constitution: revenue authority's list of the taxes it administers + consolidated index of revenue Acts), pass 13): the Department of Inland Revenue (inlandrevenue.finance.gov.bs) list of the taxes it administers, `bs/law/dir_home_2025-02-06.*` (Wayback 2025-02-06), names: Value Added Tax, Business Licence, Real Property Tax, stamp duty (DMTT), Condo-Hotel Tax; consolidated index of revenue Acts not held; none of them is a recurrent tax on net wealth."}], 'unsupported': [['true', 'Inheritance, gift and wealth taxes: statute not reached in a dated form (grade C): not computed']], 'absent': [['wealth', "Not levied (convention R2-P13-CARIB (no tax-legality clause in the constitution: revenue authority's list of the taxes it administers + consolidated index of revenue Acts), pass 13): the Department of Inland Revenue (inlandrevenue.finance.gov.bs) list of the taxes it administers, `bs/law/dir_home_2025-02-06.*` (Wayback 2025-02-06), names: Value Added Tax, Business Licence, Real Property Tax, stamp duty (DMTT), Condo-Hotel Tax; consolidated index of revenue Acts not held; none of them is a recurrent tax on net wealth."]]}

# ---- gap pass 2 (2026-11-22): 4300 not levied (OECD Revenue Statistics, Guide §52) ----
_why43 = 'Not levied (grade B, gap pass 2, 2026-11-22): the OECD Revenue Statistics detailed table for The Bahamas (DSD_REV_LAC@DF_REVBHS v2.1, sdmx.oecd.org, fetched 2026-11-21 with a plain research user-agent, copy americas/p7t/oecd/BHS.csv): general government heading 4300 (estate, inheritance and gift taxes) = 0.0 in 2021, 2022, 2023 and 2024, no 4310 or 4320 line; Interpretative Guide §52 (4300 = taxes on estates, inheritances and gifts). No estate, inheritance or gift tax is known in the national law. 2025 revenue statistics not yet published.'
for _t in S['taxes']:
    if str(_t.get('oecd')) == '4300' and _t.get('grade') == 'C':
        _t.update(status='not levied', grade='B', kernel_parts=['Absent'], why=_why43,
                  statute='none: no estate, inheritance or gift tax (OECD Revenue Statistics table, heading 4300 = 0 in 2021-2024)',
                  dated='OECD Revenue Statistics detailed table for The Bahamas (DSD_REV_LAC@DF_REVBHS v2.1, sdmx.oecd.org, fetched 2026-11-21 with a plain research user-agent, copy americas/p7t/oecd/BHS.csv): general government heading 4300 (estate, inheritance and gift taxes) = 0.0 in 2021, 2022, 2023 and 2024, no 4310 or 4320 line' + '; 2025 not yet published',
                  evidence=['OECD Revenue Statistics detailed table for The Bahamas (DSD_REV_LAC@DF_REVBHS v2.1, sdmx.oecd.org, fetched 2026-11-21 with a plain research user-agent, copy americas/p7t/oecd/BHS.csv): general government heading 4300 (estate, inheritance and gift taxes) = 0.0 in 2021, 2022, 2023 and 2024, no 4310 or 4320 line'], gap_pass2='2026-11-22 approach 2 (OECD Revenue Statistics: absence, grade B)')
        _t.pop('tried', None); _t.pop('unsupported', None)
        break
else:
    raise SystemExit('BS: no C 4300 row')
S.setdefault('absent', []).append(['estate', _why43])
_u43 = 'Inheritance, gift and wealth taxes: statute not reached in a dated form (grade C): not computed'
if 'unsupported_expr' in S:
    _f1 = '(if true then ["' + _u43 + '"] else []) ++ '; _f2 = '["' + _u43 + '"] ++ '
    _ue = S['unsupported_expr']; assert _f1 in _ue or _f2 in _ue
    S['unsupported_expr'] = _ue.replace(_f1, '', 1) if _f1 in _ue else _ue.replace(_f2, '', 1)
else:
    _n = len(S['unsupported']); S['unsupported'] = [u for u in S['unsupported'] if u[1] != _u43]
    assert len(S['unsupported']) == _n - 1
S['doc'] += "\n\n**4300 (gap pass 2, 2026-11-22)**: not levied (grade B): " + _why43
