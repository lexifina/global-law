# Germany (VZ 2025): how to run `detax`

Build once: `cd lean && lake build` (Lean 4.35 through elan).
Run: `lean/.lake/build/bin/detax [FILE] [--kist=800|900] [--separate]` — reads canonical households
(CONTRACT.md, one JSON object per line) from FILE or stdin, writes one JSON result per line in the same order.

* `--kist=900` (or 800 in Bavaria/Baden-Württemberg): Kirchensteuer for church members (default: none).
* `--separate`: married couples assessed individually (§ 26a) instead of jointly (§ 26b, splitting) — default joint.

## Output fields
* `incomeTax`: Einkommensteuer by the tariff (§ 32a, splitting for married couples) after the Kindergeld /
  Kinderfreibetrag Günstigerprüfung (§ 31), **plus** the Abgeltungsteuer on capital income (§ 32d (1), 25 %) — or,
  when § 32d (6) puts capital income into the tariff because that is cheaper including surtaxes, the tariff only.
  The Kindergeld that § 2 (6) adds back to the tax when the Freibeträge win is *not* in `incomeTax`; instead that
  Kindergeld is left out of `benefits`. So net = gross − incomeTax − Soli − KiSt − employeeSocial + benefits.
* `surtaxes`: `Soli` (SolZG 1995: 5,5 %, Freigrenze 19 950 / 39 900 €, Milderungszone 11,9 %; full 5,5 % on the
  Abgeltungsteuer) and `Kirchensteuer` (0 unless `--kist`).
* `employeeSocial`: employee RV, AV, KV (+ average Zusatzbeitrag 2,5 %), PV (childless surcharge / child reductions)
  2025 at statutory rates and ceilings; Minijob (≤ 556 €/month) none, Übergangsbereich (≤ 2 000 €/month) reduced;
  pensioners' KV/PV on the pension; main-activity self-employed: voluntary GKV + PV. See `lean/DeTax/Social.lean`.
  `detail.employeeSocialOnPensions` and `detail.employeeSocialOnSelfEmployment` give those two parts separately, for
  a comparison that counts only contributions on wages.
* `benefits`: Kindergeld (255 €/month per child under 25) the household keeps after the Günstigerprüfung.
* `detail`: per assessment unit (one for a married couple, one per adult otherwise): Einkünfte chain of § 2, zvE,
  tariff tax, children with Freibetrag, Abgeltungsteuer, Soli base, contributions per adult; for married couples
  `splittingAdvantage_vs_26a` (tax saved by joint assessment against individual assessment, in euros).
* Amounts in euros; cents appear where the law counts cents (Soli, KiSt, Abgeltungsteuer, contributions).

## Validation (details in RESULTS.md)
OECD Taxing Wages 2026 (year 2025), Germany: 7 of 8 households identical to the cent (the 8th differs by 54 € because
the OECD compares all children at once; FINDINGS O1). BMF Datensammlung 2026 tables for 2025 (marginal/average rates,
start of taxation, Kinderfreibetrag thresholds) all reproduced. The OECD's 2025 country
tables for all OECD countries come from its SDMX service (not copied here):
https://sdmx.oecd.org/public/rest/data/OECD.CTP.TPS,DSD_TAX_WAGES_COU@DF_TW_COU,2.1/all?startPeriod=2025&endPeriod=2025&dimensionAtObservation=AllDimensions&format=csvfilewithlabels.

## Main assumptions (details in lean/DeTax/Assess.lean, Social.lean)
Household-level amounts split equally between two adults; married = jointly assessed; children < 18, and 18–24 taken
as in education, count; a single adult gets the full child allowances (other parent absent) and § 24b; two unmarried
adults are both parents (half allowances, half Kindergeld each); wages ≤ 6 672 €/year are a Minijob taxed flat by the
employer (outside the assessment); `pension` = statutory pension begun at 65 (taxable share by start year, § 22);
`pensionContributions` = Basisrente (§ 10 (1) Nr. 2 b); `selfEmployment` = freelance profit (§ 18, no Gewerbesteuer);
`rentalIncome` = net rental Einkünfte (§ 21); capital income = long-held listed shares, interest: Sparer-Pauschbetrag
1 000/2 000 €, then 25 % or tariff, whichever is cheaper including surtaxes.

## Example 1 (single, 50 000 € wages)
Input:
```
{"id": "s1", "year": 2025, "adults": [{"age": 40, "wages": 50000, "selfEmployment": 0, "pension": 0}], "married": false, "children": [], "interest": 0, "dividends": 0, "capitalGains": 0, "rentalIncome": 0, "charitable": 0, "pensionContributions": 0}
```
Output:
```
{"benefits":0,"country":"DE","currency":"EUR","detail":{"employeeSocialOnPensions":0,"employeeSocialOnSelfEmployment":0,"incomeTaxIs":"ESt by tariff after the § 31 Günstigerprüfung (Kindergeld add-back excluded) + Abgeltungsteuer § 32d (1)","kindergeldPaid":0,"units":[{"abgeltungsteuer_32d":0,"altersentlastungsbetrag_24a":0,"capitalInTariff_32d6":false,"einkommen":38780,"entlastungsbetragAlleinerziehende_24b":0,"festzusetzendeEinkommensteuer":6933,"gesamtbetragDerEinkuenfte":48770,"joint":false,"kidsCounted":0,"kidsWithFreibetrag":0,"kindergeldAddedBack_2_6":0,"kirchensteuer":0,"members":[{"AV":650,"KV":4275,"PV":1200,"RV":4650,"age":40,"employerRV":4650,"onPension":0,"onSelfEmployment":0,"status":"employee"}],"soli":0,"soliBase_SolZG3_2":6933,"sonderausgabenOther_10b_10c":36,"summeDerEinkuenfte":48770,"tariffTax_32a":6933,"vorsorgeaufwendungen_10":9954,"zvE":38780}]},"employeeSocial":10775,"id":"s1","incomeTax":6933,"localIncomeTax":0,"surtaxes":{"Kirchensteuer":0,"Soli":0},"unsupported":["Kirchensteuer not applied (pass --kist=800|900)","Kirchensteuer as Sonderausgabe (§ 10 (1) Nr. 4) not modelled"]}
```

## Example 2 (married, 60 000 + 20 000 € wages, two children, 3 500 € capital income, 300 € donations)
Input:
```
{"id": "m2", "year": 2025, "adults": [{"age": 40, "wages": 60000, "selfEmployment": 0, "pension": 0}, {"age": 38, "wages": 20000, "selfEmployment": 0, "pension": 0}], "married": true, "children": [{"age": 7}, {"age": 4}], "interest": 1500, "dividends": 2000, "capitalGains": 0, "rentalIncome": 0, "charitable": 300, "pensionContributions": 0}
```
Output:
```
{"benefits":6120,"country":"DE","currency":"EUR","detail":{"employeeSocialOnPensions":0,"employeeSocialOnSelfEmployment":0,"incomeTaxIs":"ESt by tariff after the § 31 Günstigerprüfung (Kindergeld add-back excluded) + Abgeltungsteuer § 32d (1)","kindergeldPaid":6120,"splittingAdvantage_vs_26a":797.19,"units":[{"abgeltungsteuer_32d":375,"altersentlastungsbetrag_24a":0,"capitalInTariff_32d6":false,"einkommen":62287.12,"entlastungsbetragAlleinerziehende_24b":0,"festzusetzendeEinkommensteuer":9635,"gesamtbetragDerEinkuenfte":77540,"joint":true,"kidsCounted":2,"kidsWithFreibetrag":0,"kindergeldAddedBack_2_6":0,"kirchensteuer":0,"members":[{"AV":780,"KV":5130,"PV":930,"RV":5580,"age":40,"employerRV":5580,"onPension":0,"onSelfEmployment":0,"status":"employee"},{"AV":239.98,"KV":1578.32,"PV":286.13,"RV":1716.76,"age":38,"employerRV":1908.21,"onPension":0,"onSelfEmployment":0,"status":"uebergangsbereich"}],"soli":20.62,"soliBase_SolZG3_2":4054,"sonderausgabenOther_10b_10c":300,"summeDerEinkuenfte":77540,"tariffTax_32a":9260,"vorsorgeaufwendungen_10":14952.88,"zvE":62287}]},"employeeSocial":16241.19,"id":"m2","incomeTax":9635,"localIncomeTax":0,"surtaxes":{"Kirchensteuer":0,"Soli":20.62},"unsupported":["Kirchensteuer not applied (pass --kist=800|900)","Kirchensteuer as Sonderausgabe (§ 10 (1) Nr. 4) not modelled"]}
```
