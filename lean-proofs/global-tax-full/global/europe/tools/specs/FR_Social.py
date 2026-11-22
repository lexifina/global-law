S = {'cc': 'FR', 'fam': 'Social', 'doc': "# FR 2025: employer social contributions (2200) and payroll taxes (3000)\n\nSource: CLEISS (the French public liaison body for social security), its table of the social-security and unemployment contribution rates at 1 January 2025, cleiss.fr as captured by the Internet Archive on 2025-09-29 (`fr/law/cleiss_taux_wb20250929.html`); facts only, in our words. SMIC at 31.12.2023 from vie-publique.fr (Internet Archive 2024-02-06, `fr/law/vie_publique_smic_2024.html`; facts only).\n* Maladie, maternité, invalidité, décès, employer share: 13 % of the whole pay; 7 % for an employee paid at most 2,25 times the SMIC (the table's note 1 takes the SMIC at 31.12.2023; for 2025, D. 241-1-2 takes the SMIC of 1.1.2025: see the FT review below)\n* Allocations familiales, employer share: 5,25 % of the whole pay; 3,45 % when the employer is within the réduction générale and the year's pay is at most 3,3 times the SMIC (note 4, same SMIC date; D. 241-3-2 for 2025)\n* CSA: 0,3 %. Capped old-age insurance: 8,55 % up to the monthly ceiling (3 925 €). Uncapped old-age insurance: 2,02 % of the whole pay\n* Unemployment insurance: 4,05 %, lowered to 4 % from 1 May 2025 (note 6); AGS: 0,25 %; both up to four monthly ceilings (15 700 €)\n* Agirc-Arrco, employer shares: tranche 1 (up to 3 925 €) 4,72 % plus CEG 1,29 %; tranche 2 (3 925 € to 31 400 €) 12,95 % plus CEG 1,62 %; CET 0,21 % for every employee, cadre or not, whose pay exceeds the ceiling\n* vie-publique.fr (2024): the gross hourly SMIC became 11,65 € on 1.1.2024, 1 766,92 € a month, 19,72 € a month more than before: so 1 747,20 € a month at 31.12.2023\n", 'lean': '/-- Plafond annuel de la sécurité sociale 2025: the monthly ceiling for 2025 is 3 925 € (CLEISS 2025 table, facts);\n12 × 3 925 = 47 100, as `Compare.Fr.pass`. -/\ndef pss : Int := 47100\n/-- SMIC en vigueur au 31 décembre 2023, a year: 1 747,20 € a month (vie-publique.fr: 1 766,92 € a month from 1.1.2024,\n19,72 € more), × 12 = 20 966,40 €. Thresholds of the reduced rates (CLEISS 2025, notes 1 and 4):\nmaladie 7 % for pay not exceeding 2,25 SMIC = 47 174,40 €; famille 3,45 % for pay not exceeding 3,3 SMIC = 69 189,12 €.\nThe reduced rate applies to the WHOLE pay when the year\'s pay is at or below the threshold, and the full rate to the\nwhole pay above it: a cliff on the pay, not a marginal band (the kernel `Schedule` is marginal; written by hand). -/\ndef maladieCliff : Int := 47174\ndef familleCliff : Int := 69189\ndef frMaladie (w : Int) : Int := w * (if w ≤ maladieCliff then 700 else 1300) / 10000\ndef frFamille (w : Int) : Int := w * (if w ≤ familleCliff then 345 else 525) / 10000\ndef frCsa (w : Int) : Int := w * 30 / 10000\ndef frViePlaf (w : Int) : Int := min w pss * 855 / 10000\ndef frVieDeplaf (w : Int) : Int := w * 202 / 10000\n/-- 4,05 % to 30 April, 4 % from 1 May 2025 (4 and 8 months of evenly paid pay), limit 4 plafonds. -/\ndef frChomage (w : Int) : Int := min w (4 * pss) * (4 * 405 + 8 * 400) / 120000\ndef frAgs (w : Int) : Int := min w (4 * pss) * 25 / 10000\ndef frT1 (w : Int) : Int := min w pss * 601 / 10000\ndef frT2 (w : Int) : Int := if w > pss then (min w (8 * pss) - pss) * 1457 / 10000 else 0\ndef frCet (w : Int) : Int := if w > pss then min w (8 * pss) * 21 / 10000 else 0\n\ndef contribs : List (String × (Int → Int) × Oecd × String) :=\n  [("Assurance maladie, maternité, invalidité, décès (part patronale)", frMaladie, .sscEmployer, "CSS art. L. 241-2, L. 241-2-1: 13 %, 7 % where the year\'s pay does not exceed 2,25 SMIC (at 31.12.2023) for employers within the réduction générale (CLEISS 2025)"),\n   ("Allocations familiales (part patronale)", frFamille, .sscEmployer, "CSS art. L. 241-6, L. 241-6-1: 5,25 %, 3,45 % where the year\'s pay does not exceed 3,3 SMIC (at 31.12.2023) (CLEISS 2025)"),\n   ("Contribution solidarité autonomie", frCsa, .sscEmployer, "CASF art. L. 14-10-4: 0,3 % (CLEISS 2025)"),\n   ("Assurance vieillesse plafonnée (part patronale)", frViePlaf, .sscEmployer, "CSS art. D. 242-4: 8,55 % dans la limite du plafond (3 925 EUR a month in 2025) (CLEISS 2025)"),\n   ("Assurance vieillesse déplafonnée (part patronale)", frVieDeplaf, .sscEmployer, "CSS art. D. 242-4: 2,02 % sur la totalité du salaire (CLEISS 2025)"),\n   ("Assurance chômage", frChomage, .sscEmployer, "Convention d\'assurance chômage: 4,05 %, 4 % from 1 May 2025, limit 4 plafonds (CLEISS 2025)"),\n   ("AGS (garantie des salaires)", frAgs, .sscEmployer, "Code du travail art. L. 3253-18: 0,25 %, limit 4 plafonds (CLEISS 2025)"),\n   ("Retraite complémentaire Agirc-Arrco tranche 1 + CEG (part patronale)", frT1, .sscEmployer, "ANI Agirc-Arrco: 4,72 % + CEG 1,29 % to one plafond (CLEISS 2025)"),\n   ("Retraite complémentaire Agirc-Arrco tranche 2 + CEG (part patronale)", frT2, .sscEmployer, "ANI Agirc-Arrco: 12,95 % + CEG 1,62 % from one to eight plafonds (CLEISS 2025)"),\n   ("Contribution d\'équilibre technique (part patronale)", frCet, .sscEmployer, "ANI Agirc-Arrco: CET 0,21 % where the pay exceeds the plafond, to eight plafonds (CLEISS 2025)")]\n\n/-- On the household\'s wages: each adult, each contribution (borne by the employer). -/\ndef householdCharges (g : CanonGlobal) : List Charge :=\n  if g.entity == .company then [] else\n  (g.household.adults.zipIdx.filter (fun (a, _) => 0 < a.wages)).flatMap fun (a, i) =>\n    contribs.map fun (nm, f, o, st) =>\n      charge o nm a.wages id (fun x => f x) (event := s!"adult {i + 1}") (level := .social)\n        (bearer := .employer) (statute := st)\n\n/-- On a company\'s payroll, spread evenly over its employees. -/\ndef companyCharges (g : CanonGlobal) : List Charge :=\n  if g.entity != .company || g.company.payroll ≤ 0 then [] else\n  let n : Int := max 1 (g.company.employees : Int)\n  let avg := g.company.payroll / n\n  contribs.map fun (nm, f, o, st) =>\n    charge o nm g.company.payroll id (fun _ => n * f avg) (event := "payroll") (level := .social)\n      (statute := st)\n', 'families': [('2200/3000 employer contributions', ['.sscEmployer'], 'householdCharges g ++ companyCharges g')], 'notes': ['FR 2200/3000: CLEISS table au 1er janvier 2025 (with the 1 May 2025 chômage change)'], 'unsupported': [('g.household.adults.any (fun a => 0 < a.wages)', "accidents du travail (rate by the firm's size and risk), FNAL (0,10 % / 0,50 %), versement mobilité, formation professionnelle and taxe d'apprentissage, APEC and prévoyance cadres not modelled; the réduction générale des cotisations patronales (up to 1,6 SMIC) not applied, which overstates the employer cost of low pay; the thresholds are read on the year's pay, evenly paid"), ('g.entity == .company && g.company.payroll > 0', 'company payroll spread evenly over its employees')], 'guards': ['frMaladie 30000 == 2100', 'frMaladie 47174 == 3302', 'frMaladie 47175 == 6132', 'frMaladie 69190 == 8994', 'frMaladie 200000 == 26000', 'frFamille 30000 == 1035', 'frFamille 47174 == 1627', 'frFamille 47175 == 1627', 'frFamille 69190 == 3632', 'frFamille 200000 == 10500', 'frCsa 30000 == 90', 'frCsa 47174 == 141', 'frCsa 47175 == 141', 'frCsa 69190 == 207', 'frCsa 200000 == 600', 'frViePlaf 30000 == 2565', 'frViePlaf 47174 == 4027', 'frViePlaf 47175 == 4027', 'frViePlaf 69190 == 4027', 'frViePlaf 200000 == 4027', 'frVieDeplaf 30000 == 606', 'frVieDeplaf 47174 == 952', 'frVieDeplaf 47175 == 952', 'frVieDeplaf 69190 == 1397', 'frVieDeplaf 200000 == 4040', 'frChomage 30000 == 1205', 'frChomage 47174 == 1894', 'frChomage 47175 == 1894', 'frChomage 69190 == 2779', 'frChomage 200000 == 7567', 'frAgs 30000 == 75', 'frAgs 47174 == 117', 'frAgs 47175 == 117', 'frAgs 69190 == 172', 'frAgs 200000 == 471', 'frT1 30000 == 1803', 'frT1 47174 == 2830', 'frT1 47175 == 2830', 'frT1 69190 == 2830', 'frT1 200000 == 2830', 'frT2 30000 == 0', 'frT2 47174 == 10', 'frT2 47175 == 10', 'frT2 69190 == 3218', 'frT2 200000 == 22277', 'frCet 30000 == 0', 'frCet 47174 == 99', 'frCet 47175 == 99', 'frCet 69190 == 145', 'frCet 200000 == 420'], 'taxes': [{'oecd': '2200', 'tax': 'Assurance maladie, maternité, invalidité, décès (part patronale)', 'statute': "CSS art. L. 241-2, L. 241-2-1: 13 %, 7 % where the year's pay does not exceed 2,25 SMIC (at 31.12.2023) for employers within the réduction générale (CLEISS 2025)", 'dated': 'CLEISS table au 1er janvier 2025 (with the 1 May 2025 chômage change)', 'grade': 'B', 'kernel_parts': ['charge (hand-written schedule)'], 'unsupported': []}, {'oecd': '2200', 'tax': 'Allocations familiales (part patronale)', 'statute': "CSS art. L. 241-6, L. 241-6-1: 5,25 %, 3,45 % where the year's pay does not exceed 3,3 SMIC (at 31.12.2023) (CLEISS 2025)", 'dated': 'CLEISS table au 1er janvier 2025 (with the 1 May 2025 chômage change)', 'grade': 'B', 'kernel_parts': ['charge (hand-written schedule)'], 'unsupported': []}, {'oecd': '2200', 'tax': 'Contribution solidarité autonomie', 'statute': 'CASF art. L. 14-10-4: 0,3 % (CLEISS 2025)', 'dated': 'CLEISS table au 1er janvier 2025 (with the 1 May 2025 chômage change)', 'grade': 'B', 'kernel_parts': ['charge (hand-written schedule)'], 'unsupported': []}, {'oecd': '2200', 'tax': 'Assurance vieillesse plafonnée (part patronale)', 'statute': 'CSS art. D. 242-4: 8,55 % dans la limite du plafond (3 925 EUR a month in 2025) (CLEISS 2025)', 'dated': 'CLEISS table au 1er janvier 2025 (with the 1 May 2025 chômage change)', 'grade': 'B', 'kernel_parts': ['charge (hand-written schedule)'], 'unsupported': []}, {'oecd': '2200', 'tax': 'Assurance vieillesse déplafonnée (part patronale)', 'statute': 'CSS art. D. 242-4: 2,02 % sur la totalité du salaire (CLEISS 2025)', 'dated': 'CLEISS table au 1er janvier 2025 (with the 1 May 2025 chômage change)', 'grade': 'B', 'kernel_parts': ['charge (hand-written schedule)'], 'unsupported': []}, {'oecd': '2200', 'tax': 'Assurance chômage', 'statute': "Convention d'assurance chômage: 4,05 %, 4 % from 1 May 2025, limit 4 plafonds (CLEISS 2025)", 'dated': 'CLEISS table au 1er janvier 2025 (with the 1 May 2025 chômage change)', 'grade': 'B', 'kernel_parts': ['charge (hand-written schedule)'], 'unsupported': []}, {'oecd': '2200', 'tax': 'AGS (garantie des salaires)', 'statute': 'Code du travail art. L. 3253-18: 0,25 %, limit 4 plafonds (CLEISS 2025)', 'dated': 'CLEISS table au 1er janvier 2025 (with the 1 May 2025 chômage change)', 'grade': 'B', 'kernel_parts': ['charge (hand-written schedule)'], 'unsupported': []}, {'oecd': '2200', 'tax': 'Retraite complémentaire Agirc-Arrco tranche 1 + CEG (part patronale)', 'statute': 'ANI Agirc-Arrco: 4,72 % + CEG 1,29 % to one plafond (CLEISS 2025)', 'dated': 'CLEISS table au 1er janvier 2025 (with the 1 May 2025 chômage change)', 'grade': 'B', 'kernel_parts': ['charge (hand-written schedule)'], 'unsupported': []}, {'oecd': '2200', 'tax': 'Retraite complémentaire Agirc-Arrco tranche 2 + CEG (part patronale)', 'statute': 'ANI Agirc-Arrco: 12,95 % + CEG 1,62 % from one to eight plafonds (CLEISS 2025)', 'dated': 'CLEISS table au 1er janvier 2025 (with the 1 May 2025 chômage change)', 'grade': 'B', 'kernel_parts': ['charge (hand-written schedule)'], 'unsupported': []}, {'oecd': '2200', 'tax': "Contribution d'équilibre technique (part patronale)", 'statute': 'ANI Agirc-Arrco: CET 0,21 % where the pay exceeds the plafond, to eight plafonds (CLEISS 2025)', 'dated': 'CLEISS table au 1er janvier 2025 (with the 1 May 2025 chômage change)', 'grade': 'B', 'kernel_parts': ['charge (hand-written schedule)'], 'unsupported': []}]}


# ---- FT review (2026-11-21, fourth pass): FNAL, AT/MP, dialogue social, réduction générale; CFP and taxe d'apprentissage (fr_ft_employer_urssaf_grid dev; IMPROVE_FT Dataset round 2 R2-4, row 991) ----
S["doc"] += r'''
## FT review (2026-11-21, fourth pass): the other employer contributions, the réduction générale and the payroll taxes
Texts (Légifrance through the Internet Archive; `fr/law/*_wb.*`, sha256 in SHA256SUMS):
* **CSS art. D. 241-7** (version en vigueur depuis le 31 décembre 2023, décret n° 2023-1329; capture 2024-04-09, no later
  version found), I: "Coefficient = (T/0,6) × (1,6 × SMIC calculé pour un an/ rémunération annuelle brute-1)"; T "est fixée à
  0,3194" for employers under CCH L. 813-5 1° and "à 0,3234" under 2°; "arrondi à quatre décimales"; a
  coefficient above T is taken at T. II: SMIC for a
  year = 1 820 × the hourly SMIC. Pay is the entity's year's pay, read as full-time pay (no hours: the SMIC is not prorated).
* **Décret n° 2025-318 du 4 avril 2025** (JORFTEXT000051430146, capture 2025-04-06), art. 1: 1° D. 241-1-2: the L. 241-2-1
  amount is "2,25 fois" the SMIC "applicable au 1er janvier 2025" (computed as in D. 241-7 II-IV); 3° D. 241-3-2:
  "3,3 fois" for L. 241-6-1;
  4° D. 241-6: the réduction's limit "1,6 fois ... applicable au 1er janvier 2025"; 5° a) in D. 241-7 I "0,3194" and "0,3234"
  become "0,3193" and "0,3233"; art. 5: 1° to 4° apply from 1 January 2025, **5° a) from 1 May 2025**. So T is 0,3194 for
  January to April and 0,3193 from May (pay evenly spread: 4/12 and 8/12 of the year's réduction), and the reduced maladie (7 %)
  and famille (3,45 %) rates run to 2,25 and 3,3 × 21 621,60 € = 48 648,60 € and 71 351,28 € (the model had them on the SMIC
  at 31.12.2023, as the CLEISS note printed: corrected here).
* **Décret n° 2024-951** art. 1, 1°: the SMIC "est porté à 11,88 euros l'heure" from 1.11.2024 (no other 2025 change read):
  SMIC calculé pour un an 21 621,60 €.
* **CCH art. L. 813-5** (FNAL, en vigueur depuis le 1.1.2020): "1° ... 0,1 % ... dans la limite du plafond ... pour les
  employeurs occupant moins de cinquante salariés"; "2° Pour les autres employeurs ... 0,5 %" on the whole pay.
* **AT/MP: declared convention.** The rate is fixed per establishment (CSS L. 242-5); the entity names none. The model uses the
  **taux net moyen national**, arrêté du 29 avril 2025 relatif à la tarification AT/MP pour 2025, art. 2: national average net rate
  2,12 %, which is URSSAF's published default when the establishment's rate is unknown
  (modele-social `établissement . taux ATMP`, default `taux collectif` -> `taux moyen`). A real employer's rate differs.
* **Code du travail D. 2135-34**: the L. 2135-10 II contribution is "0,016 %".
* **Code du travail L. 6331-1**: employer of fewer than eleven: "0,55 %"; **L. 6331-3**: of at least eleven: "1 %" (3000).
* **Code du travail L. 6241-1** (employers liable to corporation tax or taxed on BIC), **L. 6241-1-1 II**: taxe
  d'apprentissage "0,68 %" (L. 6241-2: part principale 0,59 % + solde 0,09 %); Alsace-Moselle 0,44 % not applied (3000).
* **Employer of a household's wages: declared convention.** The entity says nothing about the employer: the model takes a private
  employer of fewer than eleven employees (T 0,3194, FNAL 0,1 %, CFP 0,55 %), liable to the taxe d'apprentissage and to VAT on
  its turnover (so not to the taxe sur les salaires, CGI art. 231-1). A company entity uses its own headcount.
'''
_L = S["lean"]
import re as _re
_i0 = _L.index("/-- SMIC en vigueur au 31 décembre 2023")
_i1 = _L.index("def frFamille (w : Int) : Int := w * (if w ≤ familleCliff then 345 else 525) / 10000")
_i1 = _L.index("\n", _i1) + 1
_L = _L[:_i0] + '''/-- CSS D. 241-7 II: SMIC calculé pour un an = 1 820 × 11,88 € (décret n° 2024-951; "applicable au 1er janvier 2025",
décret n° 2025-318 art. 1 5° b), in cents. -/
def smicAnCents : Int := 1820 * 1188
/-- D. 241-1-2 and D. 241-3-2 (décret n° 2025-318 art. 1 1°, 3°, from 1.1.2025): the reduced rates apply where the year's pay
does not exceed 2,25 (maladie) and 3,3 (famille) times the SMIC applicable au 1er janvier 2025 (48 648,60 € and 71 351,28 €),
in cents. The reduced rate applies to the WHOLE pay at or below the threshold and the full rate to the whole pay above it: a
cliff on the pay, not a marginal band (written by hand). -/
def maladieCliffCents : Int := 225 * smicAnCents / 100
def familleCliffCents : Int := 330 * smicAnCents / 100
def frMaladie (w : Int) : Int := w * (if w * 100 ≤ maladieCliffCents then 700 else 1300) / 10000
def frFamille (w : Int) : Int := w * (if w * 100 ≤ familleCliffCents then 345 else 525) / 10000
''' + _L[_i1:]
for _a, _b in [("13 %, 7 % where the year\\'s pay does not exceed 2,25 SMIC (at 31.12.2023)", "13 %, 7 % where the year\\'s pay does not exceed 2,25 SMIC (applicable au 1.1.2025, D. 241-1-2)"),
               ("5,25 %, 3,45 % where the year\\'s pay does not exceed 3,3 SMIC (at 31.12.2023)", "5,25 %, 3,45 % where the year\\'s pay does not exceed 3,3 SMIC (applicable au 1.1.2025, D. 241-3-2)")]:
    _a2, _b2 = _a.replace("\\'", "'"), _b.replace("\\'", "'")
    assert _L.count(_a2) == 1, _a2
    _L = _L.replace(_a2, _b2)
for _t in S["taxes"]:
    _t["statute"] = _t["statute"].replace("2,25 SMIC (at 31.12.2023)", "2,25 SMIC (applicable au 1.1.2025, D. 241-1-2)").replace("3,3 SMIC (at 31.12.2023)", "3,3 SMIC (applicable au 1.1.2025, D. 241-3-2)")
S["guards"] = [{"frMaladie 47175 == 6132": "frMaladie 47175 == 3302", "frFamille 69190 == 3632": "frFamille 69190 == 2387"}.get(g, g) for g in S["guards"]]
_anchor ="def contribs : List (String × (Int → Int) × Oecd × String) :="
assert _L.count(_anchor) == 1, "FR contribs"
_L = _L.replace(_anchor, '''/-- CCH L. 813-5: FNAL 0,1 % within the plafond (employer of fewer than 50), 0,5 % on the whole pay (others). -/
def frFnal (big : Bool) (w : Int) : Int := if big then w * 50 / 10000 else min w pss * 10 / 10000
/-- AT/MP at the taux net moyen national (arrêté du 29 avril 2025, art. 2: 2,12 %): declared convention, the
establishment's own rate being unknown. -/
def frAtmp (w : Int) : Int := w * 212 / 10000
/-- Code du travail D. 2135-34: contribution au dialogue social 0,016 %. -/
def frDialogue (w : Int) : Int := w * 16 / 100000
/-- CSS D. 241-7 I: (T/0,6) × (1,6 × SMIC an / pay − 1), in ten-thousandths (T = tBp / 10 000), rounded to the nearest,
at most T, nil from 1,6 SMIC. -/
def rgCoef (tBp w : Int) : Int :=
  if w ≤ 0 then 0 else
  let num := tBp * (16 * smicAnCents - 1000 * w)
  let den := 6 * (100 * w)
  if num ≤ 0 then 0 else min tBp ((2 * num + den) / (2 * den))
/-- CSS L. 241-13 III: the réduction = the coefficient × the year's gross pay (to the nearest euro); T (tBp) for January to
April, T − 0,0001 from 1 May 2025 (décret n° 2025-318 art. 1 5° a, art. 5), the pay evenly spread over the year. -/
def frReduction (tBp w : Int) : Int := (4 * rgCoef tBp w * w + 8 * rgCoef (tBp - 1) w * w + 60000) / 120000
/-- Code du travail L. 6331-1 (fewer than eleven: 0,55 %), L. 6331-3 (at least eleven: 1 %). -/
def frCfp (big : Bool) (w : Int) : Int := w * (if big then 100 else 55) / 10000
/-- Code du travail L. 6241-1-1 II: taxe d'apprentissage 0,68 %. -/
def frTa (w : Int) : Int := w * 68 / 10000

/-- The contributions and taxes that depend on the employer's headcount `n` (FT review, fourth pass). -/
def sized (n : Int) : List (String × (Int → Int) × Oecd × String) :=
  [("FNAL (contribution au Fonds national d'aide au logement)", frFnal (50 ≤ n), .sscEmployer, "CCH art. L. 813-5: 0,1 % within the plafond (fewer than 50 employees), 0,5 % on the whole pay (others)"),
   ("Accidents du travail et maladies professionnelles", frAtmp, .sscEmployer, "CSS L. 242-5; declared convention: taux net moyen national 2,12 % (arrêté du 29 avril 2025, art. 2), the establishment's rate being unknown"),
   ("Contribution au dialogue social", frDialogue, .sscEmployer, "Code du travail L. 2135-10 II, D. 2135-34: 0,016 %"),
   ("Réduction générale des cotisations patronales", (fun w => - frReduction (if 50 ≤ n then 3234 else 3194) w), .sscEmployer, "CSS L. 241-13; D. 241-7 I: (T/0,6) × (1,6 × SMIC an / pay − 1), 4 decimals, T 0,3194 to April and 0,3193 from May 2025 (0,3234 / 0,3233 from 50 employees; décret n° 2025-318 art. 1 5° a, art. 5); II: SMIC an 1 820 × 11,88 € (décret n° 2024-951)"),
   ("Contribution à la formation professionnelle", frCfp (11 ≤ n), .payroll, "Code du travail L. 6331-1: 0,55 % (fewer than eleven employees); L. 6331-3: 1 %"),
   ("Taxe d'apprentissage", frTa, .payroll, "Code du travail L. 6241-1, L. 6241-1-1 II: 0,68 % (L. 6241-2: 0,59 % + solde 0,09 %)")]

''' + _anchor, 1)
_old_h = '''    contribs.map fun (nm, f, o, st) =>
      charge o nm a.wages id (fun x => f x) (event := s!"adult {i + 1}") (level := .social)'''
assert _L.count(_old_h) == 1, "FR household"
_L = _L.replace(_old_h, '''    (contribs ++ sized 1).map fun (nm, f, o, st) =>
      charge o nm a.wages id (fun x => f x) (event := s!"adult {i + 1}") (level := .social)''')
_old_c = '''  contribs.map fun (nm, f, o, st) =>
    charge o nm g.company.payroll id (fun _ => n * f avg) (event := "payroll") (level := .social)'''
assert _L.count(_old_c) == 1, "FR company"
_L = _L.replace(_old_c, '''  (contribs ++ sized n).map fun (nm, f, o, st) =>
    charge o nm g.company.payroll id (fun _ => n * f avg) (event := "payroll") (level := .social)''')
S["lean"] = _L
S["families"] = [(nm, ['.payroll', '.sscEmployer'] if c == ['.sscEmployer'] else c, e) for nm, c, e in S["families"]]
assert S["families"][0][1] == ['.payroll', '.sscEmployer']
S["notes"] = S["notes"] + ["FR 2200/3000 (FT review, fourth pass): FNAL, AT/MP, dialogue social, réduction générale (D. 241-7), CFP, taxe d'apprentissage; household wages: an employer of fewer than eleven, AT/MP at the taux net moyen national (declared conventions)"]
_u0 = S["unsupported"][0]
assert _u0[1].startswith("accidents du travail"), "FR unsupported"
S["unsupported"][0] = (_u0[0], "household wages read as paid by a private employer of fewer than eleven employees, liable to the taxe d'apprentissage and to VAT (no taxe sur les salaires), outside Alsace-Moselle (declared convention); AT/MP at the taux net moyen national 2,12 % (declared convention); versement mobilité (11 or more, by locality), PEEC (50 or more), contribution supplémentaire à l'apprentissage (250 or more), APEC and prévoyance cadres not modelled; pay read as full-time pay (the réduction générale's SMIC is not prorated); the thresholds are read on the year's pay, evenly paid")
S["unsupported"] = S["unsupported"] + [("g.entity == .company && g.company.payroll > 0 && g.company.sales.any (fun s => s.good == .financial || s.good == .insurance || s.good == .health || s.good == .education || s.good == .medicines)", "taxe sur les salaires (CGI art. 231: employers not liable to VAT on at least 90 % of their turnover) not computed for a company with VAT-exempt sales; versement mobilité, PEEC and the contribution supplémentaire à l'apprentissage not modelled")]
S["guards"] = S["guards"] + [
  "rgCoef 3194 21374 == 3194", "rgCoef 3194 22029 == 3036", "rgCoef 3194 34594 == 0", "rgCoef 3194 30000 == 815",
  "frReduction 3194 22029 == 6688", "frReduction 3194 21374 == 6825", "frReduction 3194 40000 == 0",
  "frFnal false 113275 == 47", "frFnal true 113275 == 566", "frAtmp 113275 == 2401", "frDialogue 113275 == 18",
  "frCfp false 113275 == 623", "frCfp true 113275 == 1132", "frTa 113275 == 770"]
S["taxes"] = S["taxes"] + [
 {"oecd": "2200", "tax": "FNAL, accidents du travail, contribution au dialogue social, réduction générale des cotisations patronales", "statute": "CCH L. 813-5; CSS L. 242-5 + arrêté du 29 avril 2025 art. 2 (convention); Code du travail D. 2135-34; CSS L. 241-13, D. 241-7; décret n° 2024-951", "dated": "Légifrance (Internet Archive), versions in force in 2025", "grade": "A", "kernel_parts": ["charge (hand-written schedule)"], "unsupported": ["AT/MP: establishment's rate (convention: national average)", "employer size of a household's wages (convention: fewer than eleven)"]},
 {"oecd": "3000", "tax": "Contribution à la formation professionnelle, taxe d'apprentissage", "statute": "Code du travail L. 6331-1, L. 6331-3; L. 6241-1, L. 6241-1-1 II", "dated": "Légifrance (Internet Archive), versions in force in 2024-2025", "grade": "A", "kernel_parts": ["charge (hand-written schedule)"], "unsupported": ["versement mobilité", "PEEC", "contribution supplémentaire à l'apprentissage", "taxe sur les salaires (VAT-exempt employers)"]}]
