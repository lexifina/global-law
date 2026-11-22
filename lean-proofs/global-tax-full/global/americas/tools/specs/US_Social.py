S = dict(cc="US", fam="Social",
doc=r'''# United States 2025: employer FICA and FUTA (2200)

Source: 26 U.S.C. (Cornell LII, current Code; `us/law/usc26_31*.txt`, `usc26_33*.txt`).
* **§ 3111 (a)** "an excise tax … equal to 6.2 percent of the wages (as defined in section 3121 (a))": wages up to the
  contribution and benefit base, $176,100 for 2025 (the 1.x model's `Compare.Us.wageBase`, from 89 FR 85276);
  **§ 3111 (b)** "1.45 percent of the wages".
* **§ 3301** "equal to 6 percent of the total wages (as defined in section 3306 (b))"; **§ 3306 (b) (1)** wages above
  "$7,000" are excluded; **§ 3302 (b)** the credit for state contributions "shall not exceed 90 percent of the tax":
  0.6 % net when the state contributions are paid (California's 2025 credit reduction, § 3302 (c) (2), not modelled).
* State payroll contributions (California UI, ETT; SDI is employee-paid) not read: unsupported.''',
lean=r'''
def oasdi : Contribution := Contribution.flatCapped "OASDI (employer)" 620 Compare.Us.wageBase
def hi : Contribution := { name := "Hospital insurance (employer)", sched := Schedule.flat 145 }
def futa : Contribution := Contribution.flatCapped "FUTA (net of the § 3302 credit)" 60 7000

def sscF : Family := employerFamily "2200 employer FICA and FUTA" [oasdi, hi, futa]
  "26 U.S.C. § 3111 (a) 6.2 % to $176,100, (b) 1.45 %; § 3301 6 % on $7,000 (§ 3306 (b) (1)) less the § 3302 credit (90 %)"
''',
families="[sscF]",
unsupported=[["g.household.adults.any (·.wages > 0) || g.company.payroll > 0", "California employer UI and ETT contributions, and the 2025 FUTA credit reduction for California (§ 3302 (c) (2)), not modelled; one employer per adult"]],
guards=["oasdi.amount 73520 == 4558", "oasdi.amount 300000 == 10918", "hi.amount 73520 == 1066", "futa.amount 73520 == 42"],
taxes=[dict(oecd="2200", tax="FICA employer (OASDI, HI)", statute="26 U.S.C. § 3111", dated="current Code; 2025 wage base $176,100 (89 FR 85276)", grade="A", package="P4", kernel_parts=["employerFamily","Contribution"]),
 dict(oecd="2200", tax="FUTA", statute="26 U.S.C. §§ 3301, 3302, 3306", dated="current Code", grade="A", package="P4", kernel_parts=["Contribution"], unsupported=["California credit reduction"]),
 dict(oecd="2200", tax="California UI and ETT (employer)", statute="California Unemployment Insurance Code", grade="C", status="unsupported", package="P4", unsupported=["would unlock: the EDD 2025 rates and the Code sections"])])

# ---- P7 triage pass (2026-11-21): 3000 California Employment Training Tax ----
S['doc'] += """

**P7 triage pass (2026-11-21): 3000 California Employment Training Tax**, re-filed from the P4 C entry "California UI and
ETT" (OECD Guide §40: a levy on payroll that confers no entitlement to benefit is 3000, not 2000; §47). Cal. Unemployment
Insurance Code (lexifina/united-states-california-law, Legislative Counsel database snapshot 2016-11-27, commit 3e9e994dd132):
* **§ 976.6**: "every employer, except an employer defined by Section 676, 684, or 685, and except an employer that has
  elected an alternate method of financing ... shall pay into the Employment Training Fund contributions at the rate of
  0.1 percent of wages specified in Section 930" (as amended by Stats. 2001, Ch. 111).
* **§ 930**: "'Wages' does not include remuneration in excess of seven thousand dollars ($7,000) paid to an individual by
  an employer during any calendar year".
At most $7 per employee and year. Grade B: the text read is a 2016 snapshot (sections last amended 2001 and 1984); its
2025 wording was not read from a 2025 text. California UI contributions stay in the P4 C entry."""
S['lean'] += """
/-- Cal. UIC § 976.6: 0.1 % of wages as defined in § 930 (the first $7,000 per employee and year). -/
def ett : Contribution := Contribution.flatCapped "Employment Training Tax (California)" 10 7000

def ettF : Family := employerFamily "3000 California Employment Training Tax" [ett]
  "Cal. Unemployment Insurance Code § 976.6 (0.1 %), § 930 (first $7,000 per employee)" (oecd := .payroll) (level := .state)
"""
S['families'] = S['families'].rstrip(']') + ', ettF]'
S['unsupported'][0][1] = S['unsupported'][0][1].replace('California employer UI and ETT contributions', 'California employer UI contributions; ETT charged at 0.1 % of the first $7,000 (employer types of UIC §§ 676, 684, 685 and reimbursable employers not inputs)')
S['guards'] += ["ett.amount 73520 == 7", "ett.amount 5000 == 5"]
for t in S['taxes']:
    if t['tax'] == 'California UI and ETT (employer)':
        t['tax'] = 'California UI (employer)'
        t['refiled_note'] = 'ETT moved to its own 3000 entry in the P7 triage pass 2026-11-21 (Guide §40, §47)'
S['taxes'].append(dict(oecd="3000", tax="Employment Training Tax (California)",
    statute="Cal. Unemployment Insurance Code § 976.6 (Stats. 2001, Ch. 111), § 930",
    dated="lexifina/united-states-california-law snapshot 2016-11-27 (3e9e994dd132); no 2025 text read",
    grade="B", package="P7", kernel_parts=["employerFamily", "Contribution"],
    unsupported=["employers of UIC §§ 676, 684, 685 and reimbursable-method employers not inputs", "2025 wording not read from a 2025 text"],
    p7_triage="(a)+(b) re-filed from the P4 2200 C entry and modelled in the P7 triage pass 2026-11-21"))
