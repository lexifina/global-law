"""Independent statute reference (exact decimals) for a full-time private-sector employee, 2025, one period (month or year).
Sources: CSS D242-4 (vieillesse 6,90 % / 0,40 %); ANI AGIRC-ARRCO 17 Nov 2017 (3,15 %/8,64 %; CEG 0,86 %/1,08 %; CET 0,14 %
when pay > PASS, on T1+T2); APEC 0,024 % to 4 PASS (cadres); CSS L136-1-1, L136-2 I (abattement 1,75 % below 4 PASS),
L136-8 I 1° (CSG 9,2 %, 6,8 deductible, CGI 154 quinquies); ord. 96-50 art. 14, 19 (CRDS 0,5 %); ANI prévoyance des cadres
17 Nov 2017 (1,50 % T1, employer); CGI art. 83, 1° quater (prévoyance deductible within 5 % PASS + 2 % pay, at most 2 % of
8 PASS, employer health contributions excluded from that rule)."""
from decimal import Decimal as D
def law(g, per, cadre, sante=D(0), taux_empl=D('0.5'), prev_cadres=True):
    g = D(str(g)); P = D(3925) if per == 'mois' else D(47100)
    t1 = min(g, P); t2 = max(D(0), min(g, 8 * P) - P)
    r = {}
    r['vplaf'] = D('0.069') * t1; r['vdeplaf'] = D('0.004') * g
    r['rc'] = D('0.0315') * t1 + D('0.0864') * t2; r['ceg'] = D('0.0086') * t1 + D('0.0108') * t2
    r['cet'] = D('0.0014') * (t1 + t2) if g > P else D(0)
    r['apec'] = D('0.00024') * min(g, 4 * P) if cadre else D(0)
    r['prevCadres'] = D('0.015') * t1 if (cadre and prev_cadres) else D(0)
    sante_e = sante * taux_empl; sante_s = sante - sante_e
    r['prevEmpl'] = sante_e + r['prevCadres']
    r['baseAbattue'] = D('0.9825') * min(g, 4 * P) + max(D(0), g - 4 * P)
    r['csgBase'] = r['baseAbattue'] + r['prevEmpl']
    r['csgDed'] = D('0.068') * r['csgBase']; r['csgNd'] = D('0.024') * r['csgBase']; r['crds'] = D('0.005') * r['csgBase']
    ssc = r['vplaf'] + r['vdeplaf'] + r['rc'] + r['ceg'] + r['cet'] + r['apec']
    r['salarie'] = ssc + sante_s + r['csgDed'] + r['csgNd'] + r['crds']
    r['net'] = g - r['salarie']
    # CGI art. 83, 1° quater: the compulsory prévoyance contributions (employee's, and the employer's other than health)
    # are deductible within the limit; the employer's health contribution is taxable pay.
    limit = min(D('0.05') * P + D('0.02') * g, D('0.02') * 8 * P)
    pool = sante_s + r['prevCadres']
    r['netImposable'] = g + sante_e + r['prevCadres'] - ssc - r['csgDed'] - min(pool, limit)
    return r
