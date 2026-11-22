S = {'cc': 'CN-HK', 'doc': '# Hong Kong 2025/26: profits tax on corporations and the royalty charge on non-residents (1200)\n\nInland Revenue Ordinance (Cap. 112): text not fetched (elegislation.gov.hk is script-driven); rates from IRD tables (B).\n* **s. 14, Sch. 8 Part 1**: two-tiered rates for corporations, 8.25 % on the first HK$2 m of assessable profits, 16.5 %\n  above (from 2018/19; one entity per connected group).\n* **s. 15 (1) (a)-(b), s. 21A**: royalties to non-residents deemed 30 % profit, so 4.95 % of the gross. No withholding\n  on dividends or interest.', 'regimeName': 'Profits tax (corporations)', 'unsupported': [['company', 'global minimum tax (Cap. 112 Part 4AA, from 2025) not modelled']], 'taxes': [{'oecd': '1200', 'tax': 'Profits tax (corporations)', 'statute': 'IRO Cap. 112 s. 14 (1), Sch. 8 Part 1', 'dated': '2025/26 (two-tier since 2018/19)', 'grade': 'B', 'kernel_parts': ['CorpRegime'], 'unsupported': []}, {'oecd': '1200/1100', 'tax': 'Withholding tax on payments to non-residents', 'statute': 'IRO s. 15, s. 21A', 'dated': '2025/26 (two-tier since 2018/19)', 'grade': 'B', 'kernel_parts': ['Wht'], 'unsupported': []}], 'sched': [(0, 825), (2000000, 1650)], 'citStatute': 'IRO Cap. 112 s. 14 (1), Sch. 8 Part 1', 'wht': [{'kind': 'royalty', 'rate': 495, 'statute': 'IRO s. 15 (1) (b), s. 21A (30 % deemed × 16.5 %)', 'toCompany': True}], 'whtName': 'Withholding tax on payments to non-residents', 'guards': ['cit.citTax { profit := 3000000 } == 330000']}

# --- R3 session 7 (2026-11-21): withholding pass 7 ---
def _s7_wht_entry(add_unsupported=(), drop_unsupported=(), **kw):
    for t in S['taxes']:
        if t['oecd'] == '1200/1100':
            t.update(kw)
            t['unsupported'] = [u for u in t.get('unsupported', []) if not any(d in u for d in drop_unsupported)] + list(add_unsupported)
            return
    S['taxes'].append(dict({'oecd': '1200/1100', 'kernel_parts': ['Wht'], 'unsupported': list(add_unsupported)}, **kw))

S['wht'] = [w for w in S['wht'] if w['kind'] != 'royalty'] + [
    dict(kind='dividend', rate=0, statute='IRO (Cap. 112) s. 26 (a): a dividend from a corporation chargeable to profits tax is not included in any other person\'s profits; no other charge on dividends'),
    dict(kind='interest', rate=0, statute='IRO s. 14 (1) (profits tax only on persons carrying on business in Hong Kong), s. 15 (1) (f), (g), (i) (interest deemed a receipt only for persons carrying on business in Hong Kong): none on a non-resident lender'),
    dict(kind='services', rate=0, statute='IRO s. 14 (1): profits tax only on profits arising in or derived from Hong Kong from a business carried on in Hong Kong; s. 20B (1) (b) covers only entertainers and sportsmen performing in Hong Kong')]
S['extra_lean'] = (S.get('extra_lean') or '') + """
/-- IRO (Cap. 112, HKLII version of 25 Jul 2025) s. 15 (1) (b), s. 20B (charged in the payer's name, deducted from the
payment), s. 21A (1) (assessable profits 30 % of the sum; 100 % from an associate), Sch. 8A s. 2 (persons other than
corporations: 7.5 % to $2,000,000, 15 % above), Sch. 8B s. 2 (a) (corporations: 8.25 % / 16.5 %). -/
def sch8A : Schedule := Schedule.ofList [(0, 750), (2000000, 1500)]
def sch8B : Schedule := Schedule.ofList [(0, 825), (2000000, 1650)]
def royaltyProfit (p : Payment) : Int := if p.stakeBp > 5000 then pos p.amount else pos p.amount * 3 / 10
def royaltyTax (p : Payment) : Int := (if p.toCompany then sch8B else sch8A).tax {} (royaltyProfit p)

def royaltyCharges (co : Company) : List Charge :=
  co.paymentsAbroad.zipIdx.filterMap fun (p, i) =>
    if p.kind == .royalty then
      some (charge (if p.toCompany then .cit else .pit) "Profits tax on royalties of non-residents (charged in the payer's name)" p.amount
        (fun _ => royaltyProfit p) (fun b => (if p.toCompany then sch8B else sch8A).tax {} b)
        (event := s!"payment {i + 1} ({p.kind.name})") (bearer := .withheld)
        (statute := "IRO (Cap. 112) s. 15 (1) (b), s. 20B, s. 21A (1) (30 %; 100 % from an associate), Sch. 8A / 8B two-tiered rates"))
    else none
"""
S['extra_run'] = (S.get('extra_run') or []) + ['royaltyCharges g.company']
_s7_wht_entry(statute='IRO (Cap. 112) ss. 14, 15 (1), 20B, 21A, 26, Sch. 8A, 8B', grade='A',
    dated='HKLII consolidation version of 25 Jul 2025 (hklii.hk api getcapversiontoc id 51521; cn-hk/law/hk_cap112_hklii_v51521_20250725.json): year of assessment 2025/26',
    add_unsupported=['royalties: an associate (s. 21A (3)) is read as a recipient holding more than 50 % of the payer; the two-tiered rates are applied to the payment alone (s. 14AAC connected entities and the recipient\'s other Hong Kong profits not known)', 'interest and services: cited zeros assume the recipient carries on no business in Hong Kong'])
S['guards'] = S['guards'] + ['royaltyTax { kind := .royalty, amount := 1000000 } == 24750', 'royaltyTax { kind := .royalty, amount := 1000000, toCompany := false } == 22500', 'royaltyTax { kind := .royalty, amount := 10000000 } == 330000', 'wht.amount { kind := .dividend, amount := 1000 } == 0']

# --- R3 session 7 (2026-11-21): CIT B -> A (IRO read via the HKLII API, version of 25 Jul 2025) ---
S['citStatute'] = 'IRO (Cap. 112) s. 14 (1), (3) (b); Sch. 8B s. 2 (a): 8.25 % on assessable profits up to $2,000,000, 16.5 % above'
for _t in S['taxes']:
    if _t['oecd'] == '1200':
        _t.update(statute='IRO (Cap. 112) s. 14 (1), (3) (b), s. 14AAC, Sch. 8B s. 2 (a)', grade='A',
                  dated='HKLII consolidation version of 25 Jul 2025 (hklii.hk api getcapversiontoc id 51521; cn-hk/law/hk_cap112_hklii_v51521_20250725.json): year of assessment 2025/26')
        _t['unsupported'] = list(_t.get('unsupported', [])) + ['s. 14AAC: of connected entities only the one nominated gets the two-tiered rates (taken as nominated); offshore (non-Hong Kong-sourced) profits and the global minimum tax not modelled']
