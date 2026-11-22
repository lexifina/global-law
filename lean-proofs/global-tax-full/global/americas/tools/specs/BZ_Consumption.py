S = {'cc': 'BZ', 'fam': 'Consumption', 'doc': '# Belize 2025: General Sales Tax (5111); excise grade C\n\nSource: General Sales Tax Act, Chapter 63, Revised Edition 2011 ("showing the substantive laws as at 31st December,\n2011"), as posted by the Belize Tax Service (`bts.gov.bz/wp-content/uploads/2020/06/Chap-63-General-Sales-Tax-Act.pdf`,\nWayback capture 2026-04-18; `bz/law/gst_act_cap63_rev2020.pdf`, ARCHIVE_INDEX.tsv). Grade B (a 2011 consolidation still\nposted by the administration; Statutory Instruments after 2011 not read; the 2021-2025 Acts held by the 1.x builder do\nnot mention the GST).\n* **s. 9 (1)**: "(a) if the supply or import is zero-rated under the First Schedule, the Second Schedule or the Third\n  Schedule, 0%; or (b) in any other case, 12.5%" (s. 9 (2): variable by Ministerial Order; none read).\n* **Third Schedule (zero rated)**, substituted by S.I. 38 of 2010: I. food itemized (unprocessed: rice, flour, ...;\n  processed: "Bread, Corn and Flour tortilla ..."); "A supply of water (other than water supplied in bottles ...)"; IV.\n  listed medicines (analgesics, cough and cold preparations, insulin, oral rehydration ...); "Petroleum Products, namely:\n  Premium and Regular Gasoline, Illuminating Kerosene, Diesel and Gas oils" (S.I. 21 of 2011).\n* **Fourth Schedule (exempt)**: 1 financial services; 4 "A supply of residential accommodation"; 5 education by an\n  Educational Institution; 7 textbooks; 9 "Medical, dental, hospital, optical and paramedical services"; 10 "The supply\n  of accommodation in a hotel, inn, guesthouse"; 11 "A supply of electricity to consumers who use up to $200.00 of\n  electricity"; 13 "domestic public transport of passengers"; 19 internet services.\n\nPass 6: general sales tax (5112) cited not levied (grade A): General Sales Tax Act Cap. 63 (Rev. Ed. 2020, `bz/law/gst_act_cap63_rev2020.txt`) **s. 98 (1)**: "The Sales Tax Act, Revised Edition 2000, is hereby repealed" (s. 99 repeals the Entertainment Tax Act): the GST of the P1 row replaced the sales tax.', 'vat': {'name': 'General Sales Tax', 'standard': 1250, 'statute': 'GST Act Cap. 63 (Rev. Ed. 2011) s. 9 (1) (12.5 %; 0 % Scheds. 1-3); Third Schedule I, II, IV and petroleum (S.I. 21/2011) (zero); Fourth Schedule items 1, 4, 5, 7, 9, 10, 11, 13 (exempt)', 'classes': {'food': 'zero', 'water': 'zero', 'medicines': 'zero', 'petrol': 'zero', 'diesel': 'zero', 'financial': 'exempt', 'rent': 'exempt', 'education': 'exempt', 'books': 'exempt', 'health': 'exempt', 'hotels': 'exempt', 'electricity': 'exempt', 'transport': 'exempt'}}, 'unsupported': [['g.consumption.any fun s => s.good == .food', 'food: only the itemized Third Schedule foods (rice, flour, bread, tortillas ...) are zero rated; other food is taxed at 12.5 % (lower bound)'], ['g.consumption.any fun s => s.good == .medicines || s.good == .books', 'medicines and books: only the listed medicines and textbooks are relieved (lower bound)'], ['g.consumption.any fun s => s.good == .electricity', 'electricity is exempt only for consumers using up to $200 a month (Fourth Schedule item 11): read as within the cap (lower bound)'], ['g.consumption.any fun s => s.good == .cigarettes || s.good == .tobaccoOther || s.good == .beer || s.good == .wine || s.good == .spirits', 'excise duties on alcohol and tobacco not modelled']], 'guards': ['vat.embedded { good := .clothing, amount := 1125 } == 125', 'vat.embedded { good := .petrol, amount := 1125 } == 0', 'vat.embedded { good := .hotels, amount := 1125 } == 0'], 'taxes': [{'oecd': '5111', 'tax': 'General Sales Tax', 'statute': 'GST Act Cap. 63 s. 9; Third and Fourth Schedules (S.I. 38 of 2010, S.I. 21 of 2011)', 'dated': 'Revised Edition 2011 (laws as at 31 December 2011), posted by the Belize Tax Service in 2020', 'grade': 'B', 'package': 'P1', 'kernel_parts': ['Vat'], 'unsupported': ['post-2011 Statutory Instruments not read', 'food relief limited to itemized foods']}, {'oecd': '5121', 'tax': 'Excise duties', 'statute': 'Excise Duty Act Cap. 52', 'grade': 'C', 'status': 'unsupported', 'package': 'P1', 'kernel_parts': [], 'tried': 'bts.gov.bz uploads (Wayback): GST texts only', 'unsupported': ['would unlock: the Excise Duty Act schedule in force 2025']}, {'oecd': '5112', 'tax': 'General sales / consumption tax', 'statute': 'none: Sales Tax Act (Rev. Ed. 2000) repealed by GST Act Cap. 63 s. 98 (1)', 'dated': 'GST Act Cap. 63 Rev. Ed. 2020', 'grade': 'A', 'status': 'not levied', 'package': 'P1', 'kernel_parts': ['Absent']}], 'absent': [['salesTax', 'the Sales Tax Act (Rev. Ed. 2000) was repealed by the General Sales Tax Act Cap. 63 s. 98 (1)']]}


# ---- gap pass 2 (2026-11-22): 5121 excise duties on alcohol and tobacco (Cap. 48 s. 21, Schedule II); kept apart from the customs block ----
_IG = "454609"  # imperial gallon = 4.54609 litres
S['ex'] = S.get('ex', []) + [
    dict(good='beer', name='Excise duty (beer, Cap. 48 Sched. II)', num=762000, den=454609, vat=1250,
         statute='Customs and Excise Duties Act Cap. 48 s. 21; Schedule II items 7-8 (2203.00.10, 2203.00.20): $7.62 per imperial gallon (4.54609 l)'),
    dict(good='wine', name='Excise duty (wine, Cap. 48 Sched. II)', num=2000000, den=454609, vat=1250,
         statute='Cap. 48 s. 21; Schedule II items 9-13 (22.04, 22.05): $20.00 per imperial gallon'),
    dict(good='spirits', name='Excise duty (spirits, Cap. 48 Sched. II)', num=9000000, den=454609, vat=1250,
         statute='Cap. 48 s. 21; Schedule II items 16-25 (22.08: brandy, whisky, rum, gin, vodka, liqueurs): $90.00 per imperial gallon'),
    dict(good='cigarettes', name='Excise duty (cigarettes, Cap. 48 Sched. II)', num=65, den=1000, vat=1250,
         statute='Cap. 48 s. 21; Schedule II item 27 (2402.20.00): $65.00 per 1,000 cigarettes')]
_old = 'excise duties on alcohol and tobacco not modelled'
assert any(u[1] == _old for u in S['unsupported'])
S['unsupported'] = [u for u in S['unsupported'] if u[1] != _old] + [
    ['g.consumption.any fun s => s.good == .petrol || s.good == .diesel',
     'excise duties on motor spirit and diesel (Cap. 48 Sched. II heading 27.10) not computed: the Minister changed the rates by Order about twice a month in 2025 (S.I. 14, 25, 32, 33, 36, 53, 56, 70, 71, 78, 79, 94, 99, 114, 141, 144, 147, 151 of 2025): dated rates (grade C)'],
    ['g.consumption.any fun s => s.good == .tobaccoOther || s.good == .nonAlcoholic',
     'excise on cigars ($65 per 1,000, item 26), other tobacco products ($3 per pack, item 28) and aerated or sweetened waters ($1.75 per imperial gallon, items 4-6; not juices) not computed: the canonical goods do not separate these products']]
S['guards'] = S.get('guards', []) + [
    '-- beer: 100 l x 7.62 / 4.54609 = 167.62 -> 167',
    '(lines.find? (·.good == .beer)).get!.duty { good := .beer, amount := 1000, quantity := 100000 } == 167',
    '-- wine: 20 l x 20 / 4.54609 = 87.99 -> 87; spirits: 10 l x 90 / 4.54609 = 197.97 -> 197',
    '(lines.find? (·.good == .wine)).get!.duty { good := .wine, amount := 500, quantity := 20000 } == 87',
    '(lines.find? (·.good == .spirits)).get!.duty { good := .spirits, amount := 600, quantity := 10000 } == 197',
    '-- cigarettes: 1,000 sticks x $65 per 1,000 = 65',
    '(lines.find? (·.good == .cigarettes)).get!.duty { good := .cigarettes, amount := 300, quantity := 1000000 } == 65']
for _t in S['taxes']:
    if str(_t.get('oecd')) == '5121' and _t.get('grade') == 'C':
        _t.update(tax='Excise duties (alcohol and tobacco; fuels C)', grade='A', status='modelled', kernel_parts=['ExLine', 'exciseCharges'],
            statute='Customs and Excise Duties Act Cap. 48 s. 21 (1), (2) (payable on goods produced locally or imported), (3) (reduction by Order); Schedule II items 7-13, 16-25, 27',
            dated=('lexifina/belize-law cap/48/21.md and schedule-ii3.md (Revised Edition 2020; Schedule II substituted by Act 8 of 2016, '
                   'amended by S.I. 44 and 47 of 2016, Act 29 of 2017, Act 3 of 2018; official source Laws of Belize, agm.gov.bz/laws); the '
                   'Schedule II Orders of 2021-2026 in the repository (S.I.s under s. 21 (3), about 20 a year) change only heading 27.10 fuel '
                   'rates (one, S.I. 54 of 2025, has no tariff line in its text layer; its neighbours are fuel Orders); 235 scanned S.I.s '
                   'of 2020-2026 are not in the repository'),
            unsupported=['motor spirit and diesel (rates changed by Order about twice a month in 2025)', 'cigars, other tobacco, aerated waters'],
            gap_pass2='2026-11-22 approach 1 (lexifina law repository; MAP americas/bz#2)')
        _t.pop('tried', None)
        break
else:
    raise SystemExit('BZ: no C 5121 row')
S['doc'] += ("\n\n**5121 (gap pass 2, 2026-11-22)**: excise duties of the Customs and Excise Duties Act Cap. 48 s. 21, Schedule II "
             "(on goods produced locally or imported): beer $7.62, wine $20.00, spirits $90.00 per imperial gallon (4.54609 l); "
             "cigarettes $65.00 per 1,000. Fuels (heading 27.10) are left at grade C: their rates changed by Order about twice a month in 2025.")
