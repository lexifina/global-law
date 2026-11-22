S = {'cc': 'PA', 'fam': 'Property', 'doc': "# PA 2025: Property family — no dated statute text reached (grade C)\n\n* Inheritance, gift and wealth taxes (none read): tried not read in this pass; would unlock: the act's 2025 text.", 'families': '[]', 'taxes': [{'oecd': '4300', 'tax': 'Inheritance, gift and wealth taxes', 'statute': 'none read', 'grade': 'C', 'status': 'unsupported', 'package': 'P6', 'kernel_parts': [], 'tried': 'not read in this pass', 'unsupported': ["would unlock: the act's 2025 text"]}], 'unsupported': [['true', 'Inheritance, gift and wealth taxes: statute not reached in a dated form (grade C): not computed']]}

# ---- gap pass 2 (2026-11-22): 4300 not levied (OECD Revenue Statistics, Guide §52) ----
_why43 = 'Not levied (grade B, gap pass 2, 2026-11-22): the OECD Revenue Statistics detailed table for Panama (DSD_REV_LAC@DF_REVPAN v2.1, sdmx.oecd.org, fetched 2026-11-21 with a plain research user-agent, copy americas/p7t/oecd/PAN.csv): general government heading 4300 (estate, inheritance and gift taxes) = 0.0 in 2021, 2022, 2023 and 2024, no 4310 or 4320 line; Interpretative Guide §52 (4300 = taxes on estates, inheritances and gifts). No estate, inheritance or gift tax is known in the national law. 2025 revenue statistics not yet published.'
for _t in S['taxes']:
    if str(_t.get('oecd')) == '4300' and _t.get('grade') == 'C':
        _t.update(status='not levied', grade='B', kernel_parts=['Absent'], why=_why43,
                  statute='none: no estate, inheritance or gift tax (OECD Revenue Statistics table, heading 4300 = 0 in 2021-2024)',
                  dated='OECD Revenue Statistics detailed table for Panama (DSD_REV_LAC@DF_REVPAN v2.1, sdmx.oecd.org, fetched 2026-11-21 with a plain research user-agent, copy americas/p7t/oecd/PAN.csv): general government heading 4300 (estate, inheritance and gift taxes) = 0.0 in 2021, 2022, 2023 and 2024, no 4310 or 4320 line' + '; 2025 not yet published',
                  evidence=['OECD Revenue Statistics detailed table for Panama (DSD_REV_LAC@DF_REVPAN v2.1, sdmx.oecd.org, fetched 2026-11-21 with a plain research user-agent, copy americas/p7t/oecd/PAN.csv): general government heading 4300 (estate, inheritance and gift taxes) = 0.0 in 2021, 2022, 2023 and 2024, no 4310 or 4320 line'], gap_pass2='2026-11-22 approach 2 (OECD Revenue Statistics: absence, grade B)')
        _t.pop('tried', None); _t.pop('unsupported', None)
        break
else:
    raise SystemExit('PA: no C 4300 row')
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
