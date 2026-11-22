# AT findings

## FT review, third pass (2026-11-21; dev cases only; IMPROVE_FT.md "Third pass")
- **AT FTR-1 (5121, heating oil).** No `heatingOil` rule (in an unsupported line, not in the scorer's grade-C form): scored 0. MinStG § 3 (1) Z 5 lit. a: gekennzeichnetes Gasöl ≤ 10 mg/kg S 98 € / 1 000 l (lit. b 128 € listed). Oil bulletin dev 0 -> 98 exact. PIT unchanged; 5121 on 1 of 15,497 AT dev lines.
- **AT FTR-2 (2200, 3000).** UV 1,1 % (ASVG § 51 (1) Z 2; none from 60, (6)), AV 2,95 % (AMPFG § 2), IESG-Zuschlag 0,1 %, WBF 0,5 % on 12/14 of pay (WBFBG § 3), Kommunalsteuer 3 % (KommStG 1993 § 9, fetched), geringfügig (≤ 14 x 551,10 €): UV only (§ 53a (1)). BMF Brutto-Netto-Rechner 3000 grid 0 -> 687 / 690 w1%; its 2200 grid 0 -> 582 / 687 w1% (105 left: UV charged by the calculator for employees aged 60+); EUROMOD 0 -> 645 / 716 and 623 / 716 w1%.

- **AT FTR-3 (5200 motorbezogene Versicherungssteuer, electric cars from 1 April 2025; FT review 6).** VersStG § 12 (1) Z 35:
  § 4 (3), § 5, § 6 as worded by BGBl. I Nr. 7/2025 apply to insurance periods after 31 March 2025; the Fassung vom 31.03.2025
  (RIS, `ftreview/rv6/fetch/at/versstg_2025-03-31.html`) exempts cars with 0 g CO2 (§ 4 (3) Z 6). Combustion-car rates are the
  same in both Fassungen. EVs now pay 9/12 of the annual lit. a amount for 2025. Block appended to `tools/specs/AT_Other.py`.
- **AT FTC-1 (BMF NoVA-Rechner, `at_ft_vehicle_bmfnova_grid`).** The calculator prices the annual mVSt at its Tatbestand date
  (1.7.2025) for 12 months; for calendar 2025 an EV owes 9 months (AT FTR-3). The 92 EV dev cases are now 25 % below:
  referee convention, recorded. NoVA: NoVAG § 6 (7) "Die jährliche Absenkung des CO2-Abzugsbetrages gemäß Abs. 2 [und 3]
  wird ab 1. Jänner 2025 mit dem Wert 3 fortgesetzt" (Fassungen 1.1., 30.6. and 1.7.2025): 97 - 3 = **94** g/km for 2025
  (the europe builder's pass-12 change); with it every NoVA dev case is within 1 % (the "92" of R4-8 was inferred from three
  printed rates that 94 also gives); 40 cases differ by 1-14 EUR (whole euros vs cents).
