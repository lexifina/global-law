import json, glob, os, re
H = r'~\Documents\tax-formalization-data\taxcourt\validation\holdout'
ALLOWED = set('deficiency accuracyPenalty accuracyPenaltyApplies substantialUnderstatement failureToFile failureToPay failureToFileApplies failureToPayApplies estimatedTaxAddition estimatedTaxApplies eic ctcNonrefundable refundableCtc educationCredits aotcRefundable educationNonrefundable taxableSocialSecurity earlyDistributionTax rolloverIncludible iraDeduction hsaIncludible hsaAdditionalTax gamblingLossDeduction alimonyDeduction alimonyIncluded foreignEarnedIncomeExclusion premiumTaxCredit excessAdvancePtc householdIncome seTax agi taxableIncome totalTax filingStatus headOfHousehold'.split())
PREFIX = ('qualifyingChild:', 'qualifyingRelative:', 'dependent:', 'eicChild:', 'ctcChild:', 'hohQualifyingPerson:')
sel = json.load(open(H + r'\selected.json'))
for i in sorted(sel):
    kf = os.path.join(H, 'keys', i + '.key.json')
    rf = os.path.join(H, 'redacted', i + '.txt')
    jf = os.path.join(H, 'redacted', i + '.redactions.json')
    probs = []
    for f in (kf, rf, jf):
        if not os.path.exists(f): probs.append('missing ' + os.path.basename(f))
    if probs: print(i, probs); continue
    k = json.load(open(kf, encoding='utf-8')); json.load(open(jf, encoding='utf-8'))
    red = open(rf, encoding='utf-8').read()
    raw = re.sub(r'\s+', ' ', open(os.path.join(H, 'raw', i + '.txt'), encoding='utf-8').read())
    for e in k['expected']:
        it = e['item']
        if it not in ALLOWED and not it.startswith(PREFIX): probs.append('bad item ' + it)
        if len(e.get('snippet', '').split()) > 25: probs.append('long snippet ' + it)
        v = e.get('value')
        if isinstance(v, int) and v >= 100:
            for form in {str(v), f'{v:,}'}:
                if re.search(r'(?<![\d,.])' + re.escape(form) + r'(?![\d,])', red): probs.append(f'LEAK {it}={form}')
    for ph in ['we hold', 'We hold', 'Decision will be entered', 'decision will be entered']:
        if ph in red: probs.append('phrase ' + ph)
    print(i, len(k['expected']), 'items', sorted({e['item'].split(':')[0] for e in k['expected']}), probs or 'ok')
