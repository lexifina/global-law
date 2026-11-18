"""Recreate German (VZ 2025) Steuerspartipps with the DeTax exe; (b) items use statute-faithful post-steps or proxies.
Proxy P1: deductions the exe has no input for (Werbungskosten above the Pauschbetrag, Sonderausgaben, agB, Pauschbetraege)
enter as negative rentalIncome: same zvE effect (EStG 2 (3)-(5)); tax burdens compared, never 'gross'."""
import json, math, de
from de import A, H, run1, burden, net, est, split, soli, pap
R = []
def B(h, *f): return burden(run1(h, *f))
def add(i, name, cite, cls, scen, wo, w, saving, note=''):
    R.append(dict(id=i, name=name, cite=cite, cls=cls, scenario=scen, without=round(wo, 2), with_=round(w, 2),
                  saving=round(saving, 2), note=note))
S = lambda w, **k: H([A(wages=w)], **k)

# L01 splitting
h = H([A(wages=80000), A()], married=True); wo, w = B(h, '--separate'), B(h)
add('L01', 'Ehegattensplitting (joint vs individual)', 'EStG §§ 26, 26b, 32a (5)', 'a', 'married, one earner 80 000 €', wo, w, wo - w)
# L02 Steuerklassen (withholding only)
iv = sum(sum(pap(m, 4, pvz=1)) for m in (5000, 2000)) * 12
iii = (sum(pap(5000, 3, pvz=1)) + sum(pap(2000, 5, pvz=1))) * 12
r = run1(H([A(wages=60000), A(wages=24000)], married=True)); fin = r['incomeTax'] + r['surtaxes']['Soli']
add('L02', 'Steuerklassen III/V vs IV/IV', 'EStG §§ 38b, 39b; § 46 (2) Nr. 3a', 'a', '5 000 + 2 000 €/month; LSt+Soli withheld per year',
    iv, iii, iv - iii, f'withholding only: assessed tax {fin:.2f} € either way (Pflichtveranlagung § 46 (2) Nr. 3a)')
# L04 Heirat im Dezember; L05 Trennungsjahr; L06 Witwensplitting
for i, nm, cite, a1, a2 in [('L04', 'Marry by 31 December (whole-year splitting)', 'EStG § 26 (1) Satz 1', 90000, 0),
                           ('L05', 'Separation year: stay jointly assessed', 'EStG § 26 (1): not permanently separated at any time in the VZ', 70000, 15000)]:
    wo, w = B(H([A(wages=a1), A(wages=a2)])), B(H([A(wages=a1), A(wages=a2)], married=True))
    add(i, nm, cite, 'a', f'{a1} + {a2} € wages, unmarried vs married', wo, w, wo - w)
wo, w = B(S(70000)), B(H([A(wages=70000), A()], married=True))
add('L06', 'Witwensplitting (year after the death)', 'EStG § 32a (6) Nr. 1', 'a', 'widow(er) 70 000 € wages; proxy: joint with a 0-income spouse', wo, w, wo - w)
# L08 Minijob for spouse
b0 = B(H([A(wages=70000), A(wages=6672)], married=True)); b1 = B(H([A(wages=70000), A(wages=6673)], married=True))
add('L08', 'Minijob for the second earner', 'EStG § 40a (2); SGB IV § 8 (1a); SGB VI § 6 (1b)', 'a', 'primary 70 000 €, spouse 6 672 vs 6 673 €',
    b1 - 1, b0, b1 - b0 - 1, 'employer pays the 2 % flat tax (133 €); the known Minijob cliff (the comparison's cliffs)')
# L09 Ehegatten-Arbeitsverhaeltnis (Minijob in the spouse's practice)
cost = round(6672 * 1.3147)  # employer: 15 % RV, 13 % KV, 2 % Pauschsteuer, U1 1.1 %, U2 0.22 %, Insolvenzgeld 0.15 %
hwo, hw = H([A(se=90000), A()], married=True), H([A(se=90000 - cost), A(wages=6672)], married=True)
nwo, nw = net(hwo, run1(hwo)), net(hw, run1(hw))
add('L09', 'Employ the spouse (Minijob) in own practice', 'EStG § 4 (4), § 40a (2); R 4.8 EStR; BFH X R 31/12', 'a',
    f'freelancer 90 000 € profit; spouse Minijob 6 672 € (employer cost {cost} €)', nwo, nw, nw - nwo,
    "household net income; needs a real, arm's-length job")
# L10 Midijob
r = run1(H([A(age=30, wages=14400)])); full = 14400 * 0.2155
add('L10', 'Midijob (Uebergangsbereich)', 'SGB IV § 20 (2); SGB VI § 163 (10)', 'a', '1 200 €/month, childless, 30', full, r['employeeSocial'],
    full - r['employeeSocial'], 'pension points on the full wage (SGB VI § 70 (1a))')
# L11 child-by-child Guenstigerpruefung
h = H([A(wages=66700), A(wages=44689)], married=True, kids=(8, 5))
wo, w = B(h, '--all-children-together'), B(h)
add('L11', 'Guenstigerpruefung child by child', 'EStG § 31 Satz 4; WD 4-3000-065/24', 'a', 'OECD couple 100 % + 67 % AW, 2 children', wo, w, wo - w, 'automatic; = FINDINGS O1')
# L12 § 24b
h = H([A(wages=40000)], kids=(8,)); wo, w = B(dict(h, rentalIncome=4260)), B(h)
add('L12', 'Entlastungsbetrag Alleinerziehende (no other adult at home)', 'EStG § 24b', 'a', 'single parent 40 000 €, 1 child', wo, w, wo - w,
    'without = same parent sharing a home with another adult (proxy: § 24b removed)')
# L13 capital to child
wo = B(S(90000, dividends=7400)); w = B(S(90000)) + B(H([A(age=10)], dividends=7400))
add('L13', 'Give capital to a child (own Grundfreibetrag + Sparer-Pauschbetrag)', 'EStG §§ 20 (9), 32a, 32d (6); SGB V § 10 (1) Nr. 5', 'a',
    'parent 90 000 €, 7 400 € dividends', wo, w, wo - w, 'kept <= 7 420 € so the child stays family-insured (535 €/month); gift-tax Freibetrag 400 000 €')
# L14 annual use of Sparer-Pauschbetrag
wo = B(S(60000, capitalGains=2000)) + B(S(60000)); w = 2 * B(S(60000, capitalGains=1000))
add('L14', 'Realise gains yearly to use the Sparer-Pauschbetrag', 'EStG § 20 (9)', 'a', '60 000 € wages, 2 000 € gains over 2 years', wo, w, wo - w)
# L15 § 32d (6)
h = H([A(age=70, pension=22000)], dividends=10000); wo, w = B(h, '--no-32d6'), B(h)
add('L15', 'Guenstigerpruefung § 32d (6)', 'EStG § 32d (6)', 'a', 'pensioner 70, 22 000 € pension, 10 000 € dividends', wo, w, wo - w)
# L16 Teilfreistellung
wo, w = B(S(60000, capitalGains=10000)), B(S(60000, capitalGains=7000))
add('L16', 'Equity fund instead of bond fund (Teilfreistellung 30 %)', 'InvStG § 20 (1)', 'b', '10 000 € fund gain; proxy: 70 % taxable', wo, w, wo - w)
# L17 Realsplitting
wo = B(S(80000)) + B(S(15000)); w = B(S(80000, rentalIncome=-13805)) + B(S(15000, rentalIncome=13805 - 102))
add('L17', 'Realsplitting for maintenance to an ex-spouse', 'EStG § 10 (1a) Nr. 1, § 22 Nr. 1a, § 9a Nr. 3', 'b',
    'payer 80 000 €, recipient 15 000 € wages, 13 805 € maintenance', wo, w, wo - w, "both returns; payer compensates the recipient's extra tax")
# L18 Kinderbetreuungskosten
h = H([A(wages=70000), A(wages=20000)], married=True, kids=(3, 5)); wo, w = B(h), B(dict(h, rentalIncome=-9600))
add('L18', 'Claim childcare costs', 'EStG § 10 (1) Nr. 5 (80 %, <= 4 800 €/child)', 'b', 'couple 70 000 + 20 000 €, 2 children, 6 000 €/child', wo, w, wo - w)
# L19 Kita-Zuschuss
hwo = H([A(wages=76000), A(wages=20000)], married=True, kids=(3, 9), rentalIncome=-4800)
hw = H([A(wages=70000), A(wages=20000)], married=True, kids=(3, 9))
cwo = 96000 - B(hwo) - 6000; cw = 90000 - B(hw)
add('L19', 'Employer Kita subsidy instead of a raise', 'EStG § 3 Nr. 33; SvEV § 1 (1) Nr. 1', 'a', '6 000 € Kita fees: raise (fees deducted 80 %) vs subsidy', cwo, cw, cw - cwo, 'cash after fees')
# L20-L22 Werbungskosten
b = B(S(60000))
def wk(x): return b - B(S(60000, rentalIncome=-x))
add('L20', 'Bunch Werbungskosten into one year', 'EStG § 9a Nr. 1 a (1 230 €)', 'b', '1 000 €/yr vs 2 000 € in one year', 2 * b, 2 * b - wk(770), wk(770))
add('L21', 'Homeoffice-Tagespauschale + commuting', 'EStG § 4 (5) Nr. 6c, § 9 (1) Nr. 4', 'b', '138 HO days + 92 days x 25 km = 1 555 €', b, b - wk(325), wk(325))
add('L22', 'Entfernungspauschale (any means of transport)', 'EStG § 9 (1) Nr. 4, (2) (2025: 0,30/0,38 €/km)', 'b', '40 km, 220 days = 2 992 €', b, b - wk(1762), wk(1762))
# L23 bAV
n0, n1 = net(S(60000), run1(S(60000))), net(S(56136), run1(S(56136)))
add('L23', 'bAV Entgeltumwandlung (4 % BBG + 15 % employer)', 'EStG § 3 Nr. 63; SvEV § 1 (1) Nr. 9; BetrAVG § 1a (1a)', 'a',
    '60 000 €, converts 3 864 €; contract receives 4 444 €', n0 - n1, 4444, 4444 - (n0 - n1), 'deferral: payouts taxed (§ 22 Nr. 5) and KV/PV-liable; lower state pension')
# L24 Sachbezug; L25 Uebungsleiter; L26 SFN
g600 = net(S(60600), run1(S(60600))) - n0
add('L24', 'Sachbezug 50 €/month instead of a raise', 'EStG § 8 (2) Satz 11; SvEV § 3', 'a', '600 € a year', g600, 600, 600 - g600)
wo = B(H([A(wages=50000, se=3000)])); w = B(S(50000))
add('L25', 'Uebungsleiterpauschale', 'EStG § 3 Nr. 26 (3 000 €); Nr. 26a (840 €)', 'a', '50 000 € wages + 3 000 € coaching', wo, w, wo - w)
wo, w = B(S(51000)), B(S(45000))
add('L26', 'Tax-free night/Sunday supplements', 'EStG § 3b; SvEV § 1 (1) Nr. 1', 'a', '45 000 € + 6 000 € supplements', wo, w, wo - w)
# L27 Fuenftelregelung + timing
r = run1(S(70000)); z = r['detail']['units'][0]['zvE']; Ab = 100000
t0 = est(z + Ab); t1 = est(z) + 5 * (est(z + Ab // 5) - est(z)); t2 = 5 * est((Ab - 36) // 5)
tot0 = t0 + soli(t0); tot1 = t1 + soli(t1); tot2 = est(z) + soli(est(z)) + t2 + soli(t2)
add('L27a', 'Fuenftelregelung for a severance payment', 'EStG § 34 (1), (2) Nr. 2, § 24 Nr. 1', 'b', '70 000 € wages + 100 000 € Abfindung, same year', tot0, tot1, tot0 - tot1)
add('L27b', 'Severance paid in a year without other income', 'EStG § 34 (1) Satz 3, § 11', 'b', 'same, Abfindung paid next January (no other income)', tot1, tot2, tot1 - tot2,
    'Abfindung SV-free (BSG 21.2.1990, 12 RK 20/88); health cover in year 2 not costed')
# L28 Elterngeld via Steuerklasse
def eg(stkl, g=3000):
    lst, so = pap(g, stkl); e = g - 1230 / 12 - lst - so - 0.21 * g
    rate = max(65, 67 - 0.1 * math.floor(max(0, e - 1200) / 2))
    return min(1800, rate / 100 * e)
add('L28', 'Switch the mother to Steuerklasse III before Elterngeld', 'BEEG §§ 2, 2c (3), 2e (3), 2f; BSG 25.6.2009 B 10 EG 3/08 R', 'b',
    'mother 3 000 €/month, 12 months Basiselterngeld', 12 * eg(5), 12 * eg(3), 12 * (eg(3) - eg(5)), 'partner in V withholds more, refunded at assessment')
# L29 Progressionsvorbehalt: separate vs joint
rows = []
for wa, ega, wb in [(12000, 14400, 90000), (0, 21600, 60000), (20000, 10800, 40000), (6000, 18000, 30000), (30000, 9000, 30000), (14000, 21600, 14000)]:
    h = H([A(wages=wb), A(wages=wa)], married=True)
    z = run1(h)['detail']['units'][0]['zvE']; ej = max(0, z * split(z + ega) // max(1, z + ega)); tj = ej + soli(ej, True)
    us = run1(h, '--separate')['detail']['units']; zb, za = us[0]['zvE'], us[1]['zvE']
    ta = max(0, za * est(za + ega) // max(1, za + ega)) if za > 0 else 0; tb = est(zb)
    ts = ta + soli(ta) + tb + soli(tb)
    rows.append((round(tj - ts, 2), wa, ega, wb, tj, ts))
best = max(rows)
add('L29', 'Progressionsvorbehalt: Einzelveranlagung test', 'EStG § 32b (1) Nr. 1 j, (2); § 26a', 'b',
    f'best of {len(rows)}: spouse {best[1]} € wages + {best[2]} € Elterngeld, other {best[3]} €', best[4], best[5], best[0],
    'all: ' + '; '.join(f'{x[1]}+{x[2]}|{x[3]}: {x[0]}' for x in rows))
# L30 Riester
for i, h, zl, d in [('L30a', S(80000), 175, 'single 80 000 €'), ('L30b', H([A(wages=50000)], kids=(8, 10)), 775, 'single parent 50 000 €, 2 children')]:
    s = B(h) - B(dict(h, rentalIncome=-2100))
    add(i, 'Riester: Sonderausgabe on top of the Zulage', 'EStG § 10a (1), (2); §§ 84, 85', 'b', d, zl, s, max(0, s - zl), 'extra over the Zulage (Guenstigerpruefung § 10a (2))')
# L31 Ruerup
wo, w = B(S(80000)), B(S(80000, pensionContributions=10000))
add('L31', 'Basisrente (Ruerup) contribution', 'EStG § 10 (1) Nr. 2 b, (3)', 'a', 'single 80 000 €, 10 000 € paid', wo, w, wo - w, 'deferral: the pension is taxed later')
# L32 § 24a
wo = B(H([A(age=66, pension=20000), A(age=60, wages=15000)], married=True)); w = B(H([A(age=66, pension=20000, wages=15000), A(age=60)], married=True))
add('L32', 'Put side earnings on the spouse past 64', 'EStG § 24a (Satz 4: each spouse)', 'a', '15 000 € wages; older spouse 66 with pension', wo, w, wo - w)
# L33 work past the Regelaltersgrenze
def sv(h):
    r = run1(h); return r['employeeSocial'] - r['detail']['employeeSocialOnPensions']
wo, w = sv(H([A(age=66, wages=40000, pension=18000)])), sv(H([A(age=68, wages=40000, pension=18000)]))
add('L33', 'Work past the Regelaltersgrenze with full pension (no RV/AV share)', 'SGB VI § 5 (4) Nr. 1; SGB III § 28 (1) Nr. 1', 'a', '40 000 € wages, age 66 vs 68', wo, w, wo - w, 'opt-in to RV possible (§ 5 (4) Satz 2)')
# L34 Spenden
wo, w = B(S(80000)), B(S(80000, charitable=1000))
add('L34', 'Donation', 'EStG § 10b (1)', 'a', 'single 80 000 €, 1 000 € donated', wo, w, wo - w)
# L35 § 34g
r = run1(S(60000)); t = r['detail']['units'][0]['tariffTax_32a']; t2 = max(0, t - 825)
alt = B(S(60000)) - B(S(60000, charitable=1650))
add('L35', 'Party donation credit', 'EStG § 34g (50 %, <= 825 €)', 'b', 'single 60 000 €, 1 650 € to a party', t + soli(t), t2 + soli(t2), t + soli(t) - t2 - soli(t2), f'vs § 10b deduction of 1 650 €: {alt:.2f}')
# L36 § 35a
r = run1(S(60000)); t = r['detail']['units'][0]['tariffTax_32a']
add('L36', 'Split craftsman invoices over two years', 'EStG § 35a (3) (20 %, <= 1 200 €/yr)', 'b', '12 000 € labour: one year vs Dec/Jan', 1200, 2400, 1200)
r = run1(H([A(age=72, pension=19000)])); t = r['detail']['units'][0]['tariffTax_32a']
add('L36b', '§ 35a credit is not refundable (low-income pensioner)', 'EStG § 35a', 'b', 'pensioner 19 000 €, 4 000 € credit due', 4000, min(4000, t), min(4000, t) - 4000, f'tax only {t} €: the rest is lost')
# L37 agB bunching
h = H([A(wages=70000), A()], married=True, kids=(6, 9)); g = run1(h)['detail']['units'][0]['gesamtbetragDerEinkuenfte']
zb = 15340 * .02 + (51130 - 15340) * .03 + max(0, g - 51130) * .04
d = max(0, 4000 - zb); wo, w = 2 * B(h), B(h) + B(dict(h, rentalIncome=-round(d)))
add('L37', 'Bunch medical costs into one year', 'EStG § 33 (3); BFH VI R 75/14 (stepwise)', 'b', f'2 000 €/yr vs 4 000 € once (zumutbar {zb:.0f} €)', wo, w, wo - w)
# L38 Kirchenaustritt
h = S(60000); k = 0
for _ in range(3):
    r = run1(dict(h, charitable=k), '--kist=900'); k = round(r['surtaxes']['Kirchensteuer'])
wo, w = burden(r), B(h)
add('L38', 'Leave the church (Kirchensteuer 9 %)', 'KiStG der Laender; EStG § 51a; § 10 (1) Nr. 4', 'a', 'single 60 000 €', wo, w, wo - w, 'KiSt deducted as Sonderausgabe in the member case')
# L39 smoothing
wo = B(S(60000)) + B(S(100000)); w = 2 * B(S(80000))
add('L39', 'Time a bonus to smooth income (tariff + Soli zone)', 'EStG § 11, § 38a (1) Satz 3; SolZG § 4', 'a', '60k + 100k vs 80k + 80k', wo, w, wo - w)
# L40 loss timing
wo = B(S(120000)) + B(S(30000, rentalIncome=-20000)); w = B(S(120000, rentalIncome=-20000)) + B(S(30000))
add('L40', 'Book a rental repair in the high-income year', 'EStG §§ 11 (2), 21, 2 (3)', 'a', '20 000 € repair; incomes 120k / 30k', wo, w, wo - w)
# L41 § 23
wo, w = B(S(60000, rentalIncome=5000)), B(S(60000))
add('L41', 'Hold crypto/gold more than one year', 'EStG § 23 (1) Nr. 2, (3) Satz 5', 'b', '60 000 € wages, 5 000 € gain', wo, w, wo - w)
# L42 § 33b
wo, w = B(S(45000)), B(S(45000, rentalIncome=-1140))
add('L42', 'Claim the Behinderten-Pauschbetrag (GdB 50)', 'EStG § 33b (3)', 'b', '45 000 € wages', wo, w, wo - w)
json.dump(R, open('runs/recreate.json', 'w'), ensure_ascii=False, indent=1)
for x in R:
    print(f"{x['id']:5} {x['saving']:>10.2f}  {x['without']:>10.2f} {x['with_']:>10.2f}  {x['name'][:50]} | {x['note'][:90]}")
