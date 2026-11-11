"""Label every holdout key item that the blind encoding did not match (hand diagnosis, 2026-11-11) and total them."""
import json,collections
d=json.load(open('holdout_comparison.json',encoding='utf-8'))
L={}
def lab(case,item,cls,note): L[(case,item)]=(cls,note)
for c in ['tcmemo-2020-85#2015','tcmemo-2026-116','tcmemo-2026-25','tcsumm-2020-28#2015','tcsumm-2020-28#2016','tcsumm-2021-7','tcsumm-2023-11']:
    lab(c,'accuracyPenaltyApplies','excluded-concession','Penalty conceded by respondent; encoders do not encode conceded issues, so nothing to compute.')
for c in ['tcmemo-2025-7','tcmemo-2026-93','tcsumm-2019-13','tcsumm-2020-6']:
    lab(c,'rolloverIncludible','excluded-key-item-misuse','Key used rolloverIncludible for an ordinary includible distribution; that item only measures failed rollover claims. The blind encodings did include the distribution in income.')
for c in ['tcmemo-2020-85#2015','tcmemo-2020-96','tcmemo-2026-116']:
    lab(c,'deficiency','facts-not-stated','Opinion states no income/return figures, so no deficiency can be computed.')
for i in ['deficiency','accuracyPenalty','failureToFile','failureToFileApplies']:
    lab('tcsumm-2019-28',i,'facts-not-stated','Main (Afghanistan) wages, withholding and filing status not in the opinion; blind result (-228) meaningless.')
for i in ['deficiency','accuracyPenalty','accuracyPenaltyApplies']:
    lab('tcsumm-2022-7',i,'facts-not-stated','No income figures in the opinion; alimony disallowance itself matched.')
lab('tcsumm-2019-13','substantialUnderstatement','facts-not-stated','Schedule C base income not stated; no understatement computed.')
lab('tcsumm-2025-8','gamblingLossDeduction','redaction-removed-fact','Allowed losses ($16,140, a substantiation finding) were redacted as a key figure.')
lab('tcsumm-2025-8','deficiency','redaction-removed-fact','Follows from the redacted losses and an unstated Schedule C base.')
lab('tcsumm-2025-8','substantialUnderstatement','redaction-removed-fact','Follows from the deficiency.')
lab('tcsumm-2021-13','deficiency','redaction-removed-fact','Notice deficiency = 1,275 excess APTC (blind: 1,275, exact) + 327 net PTC claimed on the return, which was redacted.')
lab('tcsumm-2021-13','premiumTaxCredit','model-gap','Court computes the credit month by month with a partial September; the model computes it annually (7,620 vs 6,405).')
lab('tcsumm-2022-19','agi','court-figure-inconsistent','Key note: the court\'s stipulated AGI omits the $4,000 tuition deduction the IRS allowed; blind 115,821 = court\'s own figure less 4,000 (court computes 119,821 elsewhere).')
lab('tcsumm-2022-19','householdIncome','court-figure-inconsistent','Same 4,000 tuition-deduction difference as AGI.')
lab('tcsumm-2022-19','deficiency','model-gap','Model caps the capital loss on the as-filed return too, so the as-filed tax (a math-error-corrected return) differs; 16,652 vs 17,288.')
lab('tcmemo-2026-25','taxableSocialSecurity','facts-not-stated','Filing status not stated; blind assumed single (3,195). The IRS figure is 85% of benefits, which is what a married-filing-separately base of $0 gives; status is not in the opinion.')
lab('tcmemo-2026-25','deficiency','facts-not-stated','Follows from taxable Social Security / filing status.')
lab('tcmemo-2025-7','deficiency','rounding','83,374 vs 83,373 ($1).')
lab('tcmemo-2025-7','estimatedTaxAddition','near-miss','1,067 vs 1,071 ($4); 2017 tax (prior-year safe harbor) not stated, computation date differs.')
lab('tcmemo-2025-7','failureToPay','encoding-assumption','Blind computed the addition to the opinion date (9,518); the notice/court figure (7,424) is as of an earlier date.')
lab('tcmemo-2026-93','totalTax','rounding','100,421 vs 100,420 ($1).')
lab('tcmemo-2026-93','deficiency','facts-not-stated','Notice includes an uncontested child tax credit adjustment with no facts; spouse wages back-solved from the stated reported tax. 79,893 vs 80,292.')
lab('tcmemo-2026-93','accuracyPenalty','facts-not-stated','20% of the deficiency above.')
lab('tcsumm-2020-6','deficiency','facts-not-stated','Filing status, other income and the §72(t) base not stated; blind assumed single and 10% on all 86,400.')
lab('tcsumm-2020-6','accuracyPenalty','facts-not-stated','20% of the deficiency above.')
for nm in ['N.K.','C.K.']:
    for k in ['dependent','qualifyingChild','ctcChild']:
        lab('tcmemo-2020-96',f'{k}:{nm}','encoder-legal-error','Blind encoder set releasedUnder152e = true from a Form 8332 signed in 2017 but never attached to the 2014 return; the court held no valid release. (qualifyingChild is also expected false by residence; the model returned true because the release flag was set.)')
rows=[];cnt=collections.Counter()
for c in d['cases']:
    for r in c.get('items',[]):
        k=(c['id'],r['item'])
        if r['blind_ok']: cls,note='match',''
        else: cls,note=L.get(k,('UNLABELLED',''))
        r['class']=cls; r['class_note']=note; cnt[cls]+=1
d['summary']['classes']=dict(cnt)
excluded=cnt['excluded-concession']+cnt['excluded-key-item-misuse']
scorable=d['summary']['items']-excluded
nofacts=cnt['facts-not-stated']+cnt['redaction-removed-fact']
s=d['summary']
s['scorable_items']=scorable
s['match_rate_scorable']=f"{cnt['match']}/{scorable}"
s['match_or_within_5_dollars']=f"{cnt['match']+cnt['rounding']+cnt['near-miss']}/{scorable}"
facts_ok=scorable-nofacts
s['items_where_needed_facts_are_in_the_opinion']=facts_ok
s['match_rate_where_facts_stated']=f"{cnt['match']}/{facts_ok}"
s['match_or_within_5_where_facts_stated']=f"{cnt['match']+cnt['rounding']+cnt['near-miss']}/{facts_ok}"
json.dump(d,open('holdout_comparison.json','w',encoding='utf-8'),indent=1,ensure_ascii=False)
print(json.dumps(s,indent=1))
