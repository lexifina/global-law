import json, re
from collections import Counter

H = r'C:\Users\alany\Documents\tax-formalization-data\taxcourt\validation\holdout'
res = json.load(open(H + r'\search_results.json'))
draw = json.load(open(H + r'\draw.json'))
sel = json.load(open(H + r'\selected.json'))
seldock = {v['docket']: k for k, v in sel.items()}
drawn = {d for v in draw['drawn'].values() for d in v}
elig = {d: k for k, v in draw['strata'].items() for d in v}

# text-screened candidates: docket -> (tax_years, issues, exclusion reason or None if eligible)
S = {
    '10031-17': ('2014', 'dependency exemption, HOH, CTC/ACTC, EIC', None),
    '10104-18': ('2015-2016', 'dependency exemption, HOH, CTC/ACTC, EIC, education credit expenses, 6662 penalty', None),
    '10198-17': ('2014', 'dependency exemption, CTC, HOH', None),
    '10406-17': ('2014', 'dependency exemption, CTC', None),
    '12807-15': ('2012', 'dependency, HOH, CTC, EIC', None),
    '23461-17': ('2015', 'dependency, CTC, EIC, HOH', None),
    '6448-24': ('2022', 'HOH, CTC (two qualifying children), EIC; penalty conceded', None),
    '24305-18S': ('2015-2016', 'filing status (single vs MFS); unreimbursed employee expenses', None),
    '1044-25': ('2022', 'taxable Social Security (summary judgment); penalty conceded', None),
    '11390-25': ('2022', 'taxable Social Security', None),
    '3621-22S': ('2019', 'Social Security payments includible', None),
    '24551-18S': ('2017', 'PTC/excess APTC; lump-sum Social Security back payments in MAGI', None),
    '1468-20S': ('2018', 'excess APTC repayment', None),
    '8380-22S': ('2019', 'excess APTC deficiency; installment-agreement preclusion argument', None),
    '20268-19S': ('2017', 'capital loss limitation 1211(b); PTC and excess APTC', None),
    '2090-18S': ('2015', '401(k) distribution includible; 72(t) additional tax', None),
    '5367-18S': ('2015', 'Roth IRA withdrawal; 72(t); 6662 penalty', None),
    '22664-18S': ('2016', 'pension distribution; 72(t); 6662 penalty (summary judgment)', None),
    '16983-24': ('2021', 'IRA distributions includible; 72(t); 6662 penalty', None),
    '4464-21': ('2017', 'IRA distribution constructively received; 6651(a)(1)/(a)(2) (summary judgment)', None),
    '7871-23': ('2019', 'wages and retirement distribution taxable (frivolous); additions; 6673', None),
    '11872-22': ('2018', 'NOL and capital loss carryforwards; 72(t); 6651(a)(1)/(a)(2); 6654', None),
    '10750-20S': ('2017', 'alimony deduction 215; 6662 penalty', None),
    '8755-18S': ('2015', 'alimony deduction 215', None),
    '13323-18S': ('2014', '911 foreign earned income exclusion (tax home); 6662; 6651(a)(1)', None),
    '6561-23S': ('2020', 'sales tax deduction; gambling losses 165(d); gambling winnings amount; 6662', None),
    '10416-20S': ('2017', '6662 penalty only (deficiency conceded); reasonable cause', None),
    '4398-24': ('2021', 'unreported wages; credit for estimated tax payment; penalty conceded', None),
    '24311-18S': ('2016', 'unreimbursed employee expenses; American opportunity credit; 6662', None),
    '10398-16S': ('2012-2013', 'charitable deductions, Schedule C (foster care), dependency, education credits, 6662', 'excluded: principal decided issues are Schedule A/Schedule C substantiation'),
    '10691-14S': ('2009-2010', 'IRA distribution, 72(t), 6651, 6662', 'excluded: tax years before 2012'),
    '10807-25S': ('2023', 'Schedule C deductions; 6662', 'excluded: Schedule C substantiation only'),
    '11047-22': ('2017-2018', 'section 6015 relief', 'excluded: innocent spouse'),
    '11171-24S': ('n/a', 'section 6015 relief', 'excluded: innocent spouse'),
    '11350-19': ('2010-2017', 'multi-year SFR/business adjustments, CTC/EIC/HOH, 6651, 6662', 'excluded: most years before 2012 and principal issues are business income adjustments'),
    '11462-15S': ('2012', 'gain on sale of Canadian home; section 988 loss', 'excluded: issues outside coverage (home sale gain, foreign currency loss)'),
    '11844-24S': ('multi', 'deduction substantiation; civil fraud penalty', 'excluded: substantiation + fraud penalty, outside coverage'),
    '12958-17S': ('2013', 'travel expense deductions (timberland activity)', 'excluded: business expense substantiation'),
    '13863-22': ('2019', 'section 6015(f) relief', 'excluded: innocent spouse'),
    '13919-19S': ('2016', 'notice validity/presumption, burden, abatement; education credits conceded-if', 'excluded: decided issues are procedural; in-coverage items not decided on the merits'),
    '15563-19S': ('2013-2014', 'section 6015 relief', 'excluded: innocent spouse'),
    '15597-23': ('2020', 'rebate vs nonrebate erroneous refund', 'excluded: procedural refund characterization, outside coverage'),
    '16116-17S': ('2014-2015', 'Schedule C deductions; 6662', 'excluded: Schedule C substantiation'),
    '1690-15S': ('2010', 'employee expenses, Schedule C, COI, moving, ACTC, 6651, 6662', 'excluded: tax year before 2012'),
    '20248-18S': ('2015', 'Schedule C deductions; 6662', 'excluded: Schedule C substantiation only'),
    '20779-16S': ('2003-2006', 'payment/collection history', 'excluded: tax years before 2012 and collection-type issues'),
    '24875-16S': ('2013', 'employee expenses, Schedule C car/home office', 'excluded: principal decided issues are Schedule A/C substantiation'),
    '25309-18S': ('2015', 'Schedule C expenses', 'excluded: Schedule C substantiation only'),
    '25645-22': ('2020-2021', 'Schedule C expenses; IRA distributions; 6662', 'excluded: principal issue Schedule C substantiation'),
    '29638-14': ('2012', 'IRA distributions, taxable SS, partnership income, 6662, section 6015 claim', 'excluded: includes a decided section 6015 (innocent spouse) claim'),
    '3404-19S': ('2016', 'retirement income $479, payments in lieu of dividends, foreign tax credit', 'excluded: principal issue is foreign tax credit (outside coverage)'),
    '4975-23': ('2019', 'section 104(a)(2) settlement exclusion', 'excluded: outside coverage'),
    '5687-16S': ('2012-2013', 'Schedule A/C/E deductions; unreported income; 6662', 'excluded: substantiation of Schedules A/C/E'),
    '7214-20': ('2015-2017', 'unreported gross receipts, SFR, 6651, 6654', 'excluded: business gross-receipts case'),
    '7381-18S': ('2015', 'deemed distribution from plan loan (72(p)); 72(t) conceded-if', 'excluded: decisive issue is section 72(p) loan rules, outside coverage'),
    '8540-20S': ('2017', 'section 105 disability payment exclusion; 6662', 'excluded: outside coverage'),
    '9320-18S': ('2013', 'Schedule C deductions; 72(t); 6651; 6662', 'excluded: principal issue Schedule C substantiation'),
    '940-24': ('2015-2019', 'unreported income, business deductions, capital loss, NOL, additions, 6662', 'excluded: principal issues business deductions/NOL'),
}

log, seen = [], set()
for x in res:
    d = x['docketNumberWithSuffix']
    if d in seen:
        continue
    seen.add(d)
    base = dict(caseCaption=x['caseCaption'], docket=d, filingDate=x['filingDate'][:10], opinionType=x['eventCode'],
                documentTitle=x['documentTitle'][:200], search_topics=sorted(set(x['hits'])))
    if d in S:
        ty, iss, why = S[d]
        base.update(stage='text-screened', tax_years=ty, issues=iss)
        if why:
            base.update(included=False, reason=why)
        elif d in drawn:
            base.update(included=True, id=seldock.get(d), stratum=elig[d],
                        reason='eligible (decided issues in coverage, tax years 2012-2024, no excluded issue type); drawn in seeded stratified sample (draw.json)')
        else:
            base.update(included=False, stratum=elig.get(d),
                        reason='eligible but not drawn in seeded stratified sample (4 per stratum, seed 20261111); reserve')
    else:
        broad = set(x['hits']) <= {'6651', '6654', 'se'}
        suf = re.sub(r'^\d+-\d+', '', d)
        if suf in ('L', 'SL', 'P', 'W', 'R', 'D', 'X'):
            r = f"not opened: docket suffix {suf} (CDP/whistleblower/declaratory/passport etc.)"
        elif x['caseCaption'].startswith('Estate'):
            r = 'not opened: estate petitioner'
        elif broad:
            r = 'not opened: matched only broad keywords (6651/6654/self-employment tax), mostly business/SFR cases'
        else:
            r = 'not opened: title/keyword-level screen, lower apparent issue fit than the opened pool (manual choice; see note)'
        base.update(stage='title-screened', included=False, reason=r)
    log.append(base)

note = ("Search: DAWSON opinion-search, 19 keywords x SOP/MOP. The API ignored startDate (returned 2001+ opinions), so filingDate 2019-2026 "
        "was filtered locally; isStricken skipped. Exclusion: dockets/docketEntryIds found in index.json and work/meta.json. "
        "58 candidates were opened and read (chosen manually from the keyword-hit listing, preferring multi-topic in-coverage hits and "
        "summary opinions, skipping L/SL/P suffixes and estates) - this manual step is the main place selection bias could enter. "
        "Eligibility rule on the text: at least one decided issue in current coverage, tax years 2012-2024, no decided issue of an excluded type "
        "(Schedule C substantiation as principal issue, CDP, innocent spouse, partnership, whistleblower, estate/gift), not decided on purely procedural grounds. "
        "29 eligible -> 4 issue strata -> 4 drawn per stratum by seeded random sample (draw.json), independent of how easy a case looks.")
counts = dict(search_unique=len(log),
              text_screened=sum(1 for l in log if l['stage'] == 'text-screened'),
              eligible=sum(1 for l in log if l.get('stratum')),
              included=sum(1 for l in log if l['included']),
              excluded_by_reason=Counter(l['reason'] for l in log if not l['included']))
json.dump({'note': note, 'counts': counts, 'candidates': log}, open(H + r'\selection_log.json', 'w'), indent=1)
print(json.dumps(counts, indent=1))
