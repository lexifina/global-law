S = {'cc': 'DE', 'fam': 'Social', 'doc': '# DE 2025: employer social contributions (2200) and payroll taxes (3000)\n\nSource: gesetze-im-internet.de (official, BMJ/juris): SGB V §§ 241, 242a, 249, SGB XI § 58, SGB VI §§ 158, 168, 287, SGB III §§ 341, 346 as captured by the Internet Archive between 2025-02-15 and 2025-11-18 (`de/law/ssc_sgb_*`); SGB XI § 55, PBAV 2025 and SVBezGrV 2025 live (`ssc_sgb_11___55`, `ssc_pbav_2025`, `ssc_svbezgrv_2025`).\n* SGB V § 241: "Der allgemeine Beitragssatz beträgt 14,6 Prozent der beitragspflichtigen Einnahmen der Mitglieder."; § 249 (1): Beschäftigte "und ihre Arbeitgeber tragen die nach dem Arbeitsentgelt zu bemessenden Beiträge jeweils zur Hälfte"\n* SGB VI § 287 (1): "Der Beitragssatz in der allgemeinen Rentenversicherung ist bis zum Jahr 2025 abweichend von § 158 auf mindestens 18,6 Prozent festzusetzen"\n* PBAV 2025 § 1 (1): "Der Beitragssatz nach § 55 Absatz 1 Satz 1 des Elften Buches Sozialgesetzbuch wird zum 1. Januar 2025 auf 3,6 Prozent ... festgesetzt"; SGB XI § 58 (1): "jeweils zur Hälfte"\n* SGB III § 341 (2): "Der Beitragssatz beträgt 2,6 Prozent." (4): Beitragsbemessungsgrenze der allgemeinen Rentenversicherung; § 346 (1): "je zur Hälfte"\n* SVBezGrV 2025 § 2 (2): Jahresarbeitsentgeltgrenze nach § 6 Absatz 7 SGB V "für das Jahr 2025 auf 66 150 Euro"; § 4 (1) Nr. 1: "in der allgemeinen Rentenversicherung auf 96 600 Euro jährlich"\n', 'lean': 'def c0 : Contribution := { name := "Rentenversicherung (Arbeitgeberanteil)", sched := Schedule.flat 930, ceiling := 96600 }\ndef c1 : Contribution := { name := "Krankenversicherung (Arbeitgeberanteil, allgemeiner Beitragssatz)", sched := Schedule.flat 730, ceiling := 66150 }\ndef c2 : Contribution := { name := "Pflegeversicherung (Arbeitgeberanteil)", sched := Schedule.flat 180, ceiling := 66150 }\ndef c3 : Contribution := { name := "Arbeitslosenversicherung (Arbeitgeberanteil)", sched := Schedule.flat 130, ceiling := 96600 }\n\ndef contribs : List (Contribution × Oecd × String) :=\n  [(c0, .sscEmployer, "SGB VI § 287 (1) Satz 2 (mindestens 18,6 Prozent bis 2025), § 168 (1) Nr. 1 (je zur Hälfte); SVBezGrV 2025 § 4 (1) Nr. 1: 96 600 Euro"),\n   (c1, .sscEmployer, "SGB V § 241 (14,6 Prozent), § 249 (1) (jeweils zur Hälfte); SVBezGrV 2025 § 2 (2): 66 150 Euro (§ 223 (3))"),\n   (c2, .sscEmployer, "SGB XI § 55 (1), (2); PBAV 2025 § 1 (1): 3,6 Prozent ab 1.1.2025; § 58 (1) (jeweils zur Hälfte)"),\n   (c3, .sscEmployer, "SGB III § 341 (2) 2,6 Prozent, (4); § 346 (1) (je zur Hälfte)")]\n\n/-- On the household\'s wages: each adult, each contribution (borne by the employer). -/\ndef householdCharges (g : CanonGlobal) : List Charge :=\n  if g.entity == .company then [] else\n  (g.household.adults.zipIdx.filter (fun (a, _) => 0 < a.wages)).flatMap fun (a, i) =>\n    contribs.map fun (c, o, st) =>\n      charge o c.name a.wages id (fun x => c.amount x) (event := s!"adult {i + 1}") (level := .social)\n        (bearer := .employer) (statute := st)\n\n/-- On a company\'s payroll, spread evenly over its employees (ceilings per employee). -/\ndef companyCharges (g : CanonGlobal) : List Charge :=\n  if g.entity != .company || g.company.payroll ≤ 0 then [] else\n  let n : Int := max 1 (g.company.employees : Int)\n  let avg := g.company.payroll / n\n  contribs.map fun (c, o, st) =>\n    charge o c.name g.company.payroll id (fun _ => n * c.amount avg) (event := "payroll") (level := .social)\n      (statute := st)\n', 'families': [('2200/3000 employer contributions', ['.sscEmployer'], 'householdCharges g ++ companyCharges g')], 'notes': ['DE 2200/3000: 2025 (SVBezGrV 2025, PBAV 2025; SGB texts captured 2025)'], 'unsupported': [('g.household.adults.any (fun a => 0 < a.wages)', "kassenindividueller Zusatzbeitrag (half borne by the employer; the BMG's 2025 average under SGB V § 242a (2) not read), Umlagen U1/U2, Insolvenzgeldumlage, Unfallversicherung (Berufsgenossenschaft) and the Sachsen PV split (§ 58 (3)) not modelled"), ('g.entity == .company && g.company.payroll > 0', 'company payroll spread evenly over its employees (per-employee ceilings applied to the average wage)')], 'guards': ['c0.amount 50000 == 4650', 'c0.amount 200000 == 8983', 'c1.amount 50000 == 3650', 'c1.amount 200000 == 4828', 'c2.amount 50000 == 900', 'c2.amount 200000 == 1190', 'c3.amount 50000 == 650', 'c3.amount 200000 == 1255'], 'taxes': [{'oecd': '2200', 'tax': 'Rentenversicherung (Arbeitgeberanteil)', 'statute': 'SGB VI § 287 (1) Satz 2 (mindestens 18,6 Prozent bis 2025), § 168 (1) Nr. 1 (je zur Hälfte); SVBezGrV 2025 § 4 (1) Nr. 1: 96 600 Euro', 'dated': '2025 (SVBezGrV 2025, PBAV 2025; SGB texts captured 2025)', 'grade': 'A', 'kernel_parts': ['Contribution'], 'unsupported': []}, {'oecd': '2200', 'tax': 'Krankenversicherung (Arbeitgeberanteil, allgemeiner Beitragssatz)', 'statute': 'SGB V § 241 (14,6 Prozent), § 249 (1) (jeweils zur Hälfte); SVBezGrV 2025 § 2 (2): 66 150 Euro (§ 223 (3))', 'dated': '2025 (SVBezGrV 2025, PBAV 2025; SGB texts captured 2025)', 'grade': 'A', 'kernel_parts': ['Contribution'], 'unsupported': []}, {'oecd': '2200', 'tax': 'Pflegeversicherung (Arbeitgeberanteil)', 'statute': 'SGB XI § 55 (1), (2); PBAV 2025 § 1 (1): 3,6 Prozent ab 1.1.2025; § 58 (1) (jeweils zur Hälfte)', 'dated': '2025 (SVBezGrV 2025, PBAV 2025; SGB texts captured 2025)', 'grade': 'A', 'kernel_parts': ['Contribution'], 'unsupported': []}, {'oecd': '2200', 'tax': 'Arbeitslosenversicherung (Arbeitgeberanteil)', 'statute': 'SGB III § 341 (2) 2,6 Prozent, (4); § 346 (1) (je zur Hälfte)', 'dated': '2025 (SVBezGrV 2025, PBAV 2025; SGB texts captured 2025)', 'grade': 'A', 'kernel_parts': ['Contribution'], 'unsupported': []}]}


# ---- FT review (2026-11-21, third pass): geringfügige Beschäftigung (Minijob) employer flat rates (de_ft_employer_minijob_grid dev; IMPROVE_FT late-3) ----
S["doc"] += r'''
## FT review (2026-11-21, third pass): Minijob employer contributions
gesetze-im-internet.de, fetched 2026-11-21 (`de/law/sgb_6___172.html`, `sgb_5___249b.html`, `sgb_4___8.html`,
`milov4___1.html`; `ssc_sgb_6___168.txt` already held):
* **SGB IV § 8 (1) Nr. 1**: a geringfügige Beschäftigung where "das Arbeitsentgelt aus dieser Beschäftigung regelmäßig
  die Geringfügigkeitsgrenze nicht übersteigt"; **(1a)**: the limit "wird berechnet, indem der Mindestlohn mit 130
  vervielfacht, durch drei geteilt und auf volle Euro aufgerundet wird". **MiLoV4 § 1 Nr. 2**: "ab 1. Januar 2025 12,82
  Euro brutto je Zeitstunde": 12,82 x 130 / 3 = 555,53, rounded up 556 euro a month, 6 672 euro a year.
* **SGB VI § 168 (1) Nr. 1b**: for "Personen, die gegen Arbeitsentgelt geringfügig versicherungspflichtig beschäftigt
  werden, von den Arbeitgebern in Höhe des Betrages, der 15 vom Hundert des der Beschäftigung zugrunde liegenden
  Arbeitsentgelts entspricht"; **§ 172 (3)**: the same 15 % where the employee is exempted (§ 6 (1b)) or versicherungsfrei
  (§ 5 (4)).
* **SGB V § 249b Satz 1**: "Der Arbeitgeber einer Beschäftigung nach § 8 Abs. 1 Nr. 1 des Vierten Buches hat für
  Versicherte, die in dieser Beschäftigung versicherungsfrei oder nicht versicherungspflichtig sind, einen Beitrag in
  Höhe von 13 vom Hundert des Arbeitsentgelts dieser Beschäftigung zu tragen."
* No Pflege- or Arbeitslosenversicherung (SGB XI § 20 / SGB III § 27 (2): geringfügig Beschäftigte not insured).
An adult whose annual wages are at most 6 672 euro is read as holding one regular Minijob (wages spread evenly).
'''
_old = '''  (g.household.adults.zipIdx.filter (fun (a, _) => 0 < a.wages)).flatMap fun (a, i) =>
    contribs.map fun (c, o, st) =>'''
_new = '''  (g.household.adults.zipIdx.filter (fun (a, _) => 0 < a.wages)).flatMap fun (a, i) =>
    if a.wages ≤ minijobAnnual then
      minijob.map fun (c, st) =>
        charge .sscEmployer c.name a.wages id (fun x => c.amount x) (event := s!"adult {i + 1}") (level := .social)
          (bearer := .employer) (statute := st)
    else
    contribs.map fun (c, o, st) =>'''
assert S["lean"].count(_old) == 1
S["lean"] = S["lean"].replace("/-- On the household's wages", r'''/-- SGB IV § 8 (1a) with MiLoV4 § 1 Nr. 2 (12,82 euro x 130 / 3, rounded up): 556 euro a month in 2025 -/
def minijobAnnual : Int := 12 * 556
def m0 : Contribution := { name := "Rentenversicherung (Arbeitgeber, geringfügige Beschäftigung)", sched := Schedule.flat 1500 }
def m1 : Contribution := { name := "Krankenversicherung (Arbeitgeber, geringfügige Beschäftigung)", sched := Schedule.flat 1300 }
def minijob : List (Contribution × String) :=
  [(m0, "SGB VI § 168 (1) Nr. 1b, § 172 (3): 15 vom Hundert des Arbeitsentgelts (Minijob, SGB IV § 8 (1) Nr. 1; 556 Euro monatlich 2025)"),
   (m1, "SGB V § 249b Satz 1: 13 vom Hundert des Arbeitsentgelts (Minijob, SGB IV § 8 (1) Nr. 1)")]

/-- On the household's wages''', 1).replace(_old, _new)
S["unsupported"] = S["unsupported"] + [
  ("g.household.adults.any (fun a => 0 < a.wages && a.wages ≤ 12 * 556)", "annual wages up to 6 672 euro read as one regular Minijob (SGB IV § 8 (1) Nr. 1): employer 15 % RV + 13 % KV; private-household Minijobs (§ 8a: 5 % + 5 %), privately insured employees (no § 249b), the Umlagen U1/U2 and Insolvenzgeldumlage and the 2 % Pauschsteuer (EStG § 40a (2), not 2200) not modelled")]
S["guards"] = S["guards"] + ["m0.amount 6000 == 900", "m1.amount 6000 == 780", "minijobAnnual == 6672"]
S["taxes"] = S["taxes"] + [
  {"oecd": "2200", "tax": "Minijob: Renten- und Krankenversicherung (Arbeitgeber, Pauschalbeiträge)", "statute": "SGB IV § 8 (1) Nr. 1, (1a); MiLoV4 § 1 Nr. 2; SGB VI § 168 (1) Nr. 1b, § 172 (3); SGB V § 249b", "dated": "gesetze-im-internet.de fetched 2026-11-21", "grade": "A", "kernel_parts": ["Contribution"], "unsupported": ["§ 8a Privathaushalt rates", "Umlagen U1/U2, Insolvenzgeldumlage"]}]

# ---- FT review 5 (2026-11-21): Insolvenzgeldumlage (SGB III §§ 358-360), 0,15 % on the RV Arbeitsentgelt ----
S["doc"] = S["doc"] + '''
FT review 5 (2026-11-21): **Insolvenzgeldumlage** (gesetze-im-internet.de, fetched 2026-11-21, `de/law/sgb3_358.html`,
`sgb3_360.html`): SGB III § 358 (1) "Die Mittel für die Zahlung des Insolvenzgeldes werden durch eine monatliche Umlage
von den Arbeitgebern aufgebracht" (the Bund, Länder, Gemeinden, insolvency-proof public bodies "und private Haushalte
werden nicht in die Umlage einbezogen"); (2) on the Arbeitsentgelt "nach dem die Beiträge zur gesetzlichen
Rentenversicherung ... bemessen werden" (so up to the RV ceiling, 96 600 euro); § 360 "Der Umlagesatz beträgt 0,15
Prozent" (the footnote lists InsoGeldFestV for 2022, 2023 and 2024 only: no § 361 Verordnung for 2025, so 0,15 %).
Paid with the Gesamtsozialversicherungsbeitrag to the Bundesagentur (§ 359), it finances the Insolvenzgeld: OECD 2200
(Interpretative Guide §40-41). The employer of a household's wages is read as a private business (not a private
household, not a public body), as for the Minijob reading of SGB IV § 8 (1) Nr. 1.'''
S["lean"] = S["lean"].replace(
  'def c3 : Contribution := { name := "Arbeitslosenversicherung (Arbeitgeberanteil)", sched := Schedule.flat 130, ceiling := 96600 }',
  'def c3 : Contribution := { name := "Arbeitslosenversicherung (Arbeitgeberanteil)", sched := Schedule.flat 130, ceiling := 96600 }\n'
  '/-- SGB III § 358 (2), § 360: 0,15 % of the RV Arbeitsentgelt (no InsoGeldFestV for 2025). -/\n'
  'def c4 : Contribution := { name := "Insolvenzgeldumlage", sched := Schedule.flat 15, ceiling := 96600 }')
S["lean"] = S["lean"].replace(
  '''(c3, .sscEmployer, "SGB III § 341 (2) 2,6 Prozent, (4); § 346 (1) (je zur Hälfte)")]''',
  '''(c3, .sscEmployer, "SGB III § 341 (2) 2,6 Prozent, (4); § 346 (1) (je zur Hälfte)"),
   (c4, .sscEmployer, "SGB III § 358 (1), (2) (Arbeitsentgelt der Rentenversicherung), § 360: Umlagesatz 0,15 Prozent (no InsoGeldFestV for 2025)")]''')
S["lean"] = S["lean"].replace(
  '''(m1, "SGB V § 249b Satz 1: 13 vom Hundert des Arbeitsentgelts (Minijob, SGB IV § 8 (1) Nr. 1)")]''',
  '''(m1, "SGB V § 249b Satz 1: 13 vom Hundert des Arbeitsentgelts (Minijob, SGB IV § 8 (1) Nr. 1)"),
   (c4, "SGB III § 358 (1), (2), § 360: Insolvenzgeldumlage 0,15 Prozent (Minijob: the RV Arbeitsentgelt, SGB VI § 168 (1) Nr. 1b)")]''')
assert "def c4" in S["lean"] and S["lean"].count("(c4,") == 2
S["unsupported"] = [(c, t.replace("Umlagen U1/U2, Insolvenzgeldumlage,", "Umlagen U1/U2 (each Krankenkasse's Satzung, AAG §§ 7, 9),")
                         .replace("the Umlagen U1/U2 and Insolvenzgeldumlage and", "the Umlagen U1/U2 and"))
                    for (c, t) in S["unsupported"]]
assert not any("Insolvenzgeldumlage" in t for (_, t) in S["unsupported"])
S["unsupported"] = S["unsupported"] + [("g.household.adults.any (fun a => 0 < a.wages)",
  "Insolvenzgeldumlage: the employer read as a private business (SGB III § 358 (1) exempts public bodies and private households)")]
S["guards"] = S["guards"] + ["c4.amount 50000 == 75", "c4.amount 200000 == 144", "c4.amount 6000 == 9"]
S["taxes"] = S["taxes"] + [{"oecd": "2200", "tax": "Insolvenzgeldumlage",
  "statute": "SGB III §§ 358, 359, 360 (Umlagesatz 0,15 Prozent; § 361 InsoGeldFestV for 2022-2024 only)",
  "dated": "gesetze-im-internet.de fetched 2026-11-21", "grade": "A", "kernel_parts": ["Contribution"],
  "unsupported": ["employer type (public bodies, private households exempt)"]}]

# ---- pass 16 (R1 Europe, 2026-11-21): year-in-force audit (tools/p16_rows.py, tools/yif16_rows.json) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p8_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p9_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p10_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p11_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p12_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p13_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p14_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p15_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p16_rows.py")).read())
p16_rows(S)
p6_finish(S)
