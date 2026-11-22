# DE findings

- **DE FTR-1 (5121 Energiesteuer on heating oil, model fix, FT review 2).** EnergieStG § 2 (3) Nr. 1 b) 61,35 EUR / 1 000 l for marked gas oil (≤ 50 mg/kg sulphur) added to `Basic.lean` `energie` (1 guard). Dev oil bulletin: DE 2 -> 3 / 3. Note: TEDB's DE electricity 0 % is the § 12 (3) photovoltaic row (dataset mapping), model right at 19 %.

## FT review, third pass (2026-11-21; dev cases only; IMPROVE_FT.md "Third pass")
- **DE FTR-2 (2200, Minijob).** SGB IV § 8 (1) Nr. 1, (1a) with MiLoV4 § 1 Nr. 2 (556 € a month); SGB VI § 168 (1) Nr. 1b / § 172 (3) 15 %; SGB V § 249b 13 %. `de_ft_employer_minijob_grid` dev ratio 0,669 -> 0,952 (0 -> 4 exact); the rest is the Umlagen U1/U2 and Insolvenzgeldumlage, not modelled for any employee (open).

## FT review, fifth pass (2026-11-21; dev only)
- **DE FTR-1 (2200, model fix).** Insolvenzgeldumlage added: SGB III § 358 (1) (monthly Umlage of the employers; public
  bodies and private households not included), (2) (on the RV Arbeitsentgelt, so to 96 600 €), § 360 ("Der Umlagesatz
  beträgt 0,15 Prozent"; § 361 Verordnungen exist for 2022-2024 only). Texts `law/sgb3_358.html`, `sgb3_360.html`
  (gesetze-im-internet.de, 2026-11-21). Also on Minijobs. 3 guards; PIT unchanged; only 2200 changed.
- **DE FTS-1 (GETTSIM)**: no Insolvenzgeldumlage. What is left at the KV ceiling on bruttonetto / gettsim (≈ 827 €) is the
  employer's half of the average Zusatzbeitrag 2,5 % (SGB V § 242a; kassenindividuell, flagged); U1 / U2: Satzung rates.
