# Austria 2025: what is most useful to know

## For a taxpayer
1. **File the Arbeitnehmerveranlagung if you earn little.** Withholding never pays out the VAB-Zuschlag, the
   SV-Rückerstattung (55 % of your contributions, up to 1 277 €), the AEAB/AVAB refund or the Kindermehrbetrag. A single
   parent of two on 1 500 € a month has 117 € withheld but is owed 3 083 € back on assessment (BMF calculator vs model,
   `results/bmf_grid.md`; FINDINGS F4, CATALOGUE K21).
2. **Watch the cliffs where one euro costs hundreds:** 551,10 € a month (all contributions start: −606 € a year),
   2 074 / 2 262 / 2 451 € a month (AV steps: −217 to −300 €), a partner's Einkünfte of 7 284 € (AVAB: −813 € with two
   children), family Einkommen 55 000 € with three children (Mehrkindzuschlag: −292,80 €). Proved in Lean
   (`geringfuegig_notch`, `av_notches`, `mkz_notch`) and found blind by the METR scanner.
3. **Couples with low pay and children: the Kindermehrbetrag depends on both partners' tax.** If the partner's tariff
   tax reaches 700 € per child, the other partner's Kindermehrbetrag (up to 1 400 € for two children) is lost entirely
   (NOVEL N1, `kmb_partner_cliff`). Deductions that keep the partner's tax under the line are worth up to that amount.

## For an adviser
1. **Familienbonus Plus allocation matters**: it cannot exceed each partner's tariff tax; putting it where it can be
   used saved 1 050 € for a 63 054 € + 25 000 € couple (K8). The model's optimiser reproduces this.
2. **GmbH owner-managers**: at a profit of 2 AW the best mix is a salary of about 34 000 € plus dividends (7 955 € a year
   better than all salary) if dividends are free of GSVG, but only 1 594 € better if the SVS includes them (GSVG § 25
   Abs. 1 last sentence) — the GSVG treatment of dividends decides the plan (F15, `results/recreate.md`).
3. The 13th/14th salary at 6 % is worth 2 631 € at the average wage (K1); pay above one sixth of the regular pay loses it.

## For the government
1. **§ 33 Abs. 7 EStG** says "unter 700 Euro" but is administered as 700 € per child (F7); write "700 Euro je Kind".
   The lit. b partner condition creates an all-or-nothing cliff of up to 700 € per child (N1); a taper (withdraw the
   amount by which the partner's tax exceeds the limit) would remove it.
2. **Frozen amounts:** the Mehrkindzuschlag limit has been 55 000 € since it stopped tracking the Höchstbeitragsgrundlage
   (twelve times it would be 77 400 € today) while the benefit itself is indexed (F12); the Werbungskostenpauschale is
   still 132 € (F13).
3. **BMF Brutto-Netto-Rechner** charges 6 % KV on the April 2025 pension Sonderzahlung; the law gave 5,1 % until May
   (F5). Its employee results are otherwise exact to the cent on 90 of 90 test cases (F4). The BMF's Kindermehrbetrag
   income limits for one and two children are 5 € low (F6).
4. **OECD Taxing Wages** for Austria books the 6-year-old child at the 10+ Familienbeihilfe rate (+285,60 €, F2).
