#!/usr/bin/env python3
"""soc_hand_p5.py [CC ...]: pass-5 employer contributions that a flat rate with a ceiling cannot express (written by
hand in Lean; quicksoc.py's household/company shape otherwise): DK (ATP: a fixed annual amount), IE (PRSI: the whole
week's pay at one rate chosen by the week's pay, two rate periods in 2025), BE (ONSS: wage moderation on the pay plus
the basic employer contributions), FR (taux réduits maladie / famille: the whole pay at one rate chosen by the pay).
Each row: contributions [(name, lean function name, oecd '2200'|'3000', statute, python twin)], `lean` definitions of
the functions, guards recomputed with the python twins."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))

# ---------- DK
def dk_atp(x): return 2376 if x > 0 else 0
# ---------- IE
def ie_prsi(x):
    if x <= 0: return 0
    low = x <= 52 * 527
    w1 = x * 39 // 52; w2 = x - w1
    return (w1 * (790 if low else 1015) + w2 * (800 if low else 1025)) // 10000
# ---------- BE
def be_base(x): return x * 1988 // 10000
def be_mod(x): return x * 11988 * 427 // 100000000

# ---------- FR (CLEISS table au 1er janvier 2025; SMIC au 31.12.2023: 1 747,20 EUR a month = 20 966,40 a year)
PSS = 47100
def fr_mal(x): return x * (700 if x <= 47174 else 1300) // 10000
def fr_fam(x): return x * (345 if x <= 69189 else 525) // 10000
def fr_csa(x): return x * 30 // 10000
def fr_vp(x): return min(x, PSS) * 855 // 10000
def fr_vd(x): return x * 202 // 10000
def fr_cho(x): return min(x, 4 * PSS) * (4 * 405 + 8 * 400) // 120000
def fr_ags(x): return min(x, 4 * PSS) * 25 // 10000
def fr_t1(x): return min(x, PSS) * 601 // 10000
def fr_t2(x): return (min(x, 8 * PSS) - PSS) * 1457 // 10000 if x > PSS else 0
def fr_cet(x): return min(x, 8 * PSS) * 21 // 10000 if x > PSS else 0

ROWS = [
 dict(cc="DK",
      cs=[("ATP-bidrag (arbejdsgiverandel)", "atpEmployer", "2200", "ATP-loven § 15, stk. 6 (arbejdsgiveren betaler 2/3); BEK nr 1621 af 12/12/2023 § 2, stk. 1 (A-satsen 3.564 kr. årligt): 2.376 kr.", dk_atp)],
      lean='''/-- ATP, full-time (A-sats): BEK nr 1621 af 12/12/2023 § 2, stk. 1 "Det almindelige årsbidrag udgør 3.564 kr.
(A-satsen)" (in force 1.1.2024, unchanged for 2025); ATP-loven § 15, stk. 6 "Arbejdsgiveren betaler 2/3 af bidraget":
2.376 kr. a year, a fixed amount per full-time employee, not a share of the pay. -/
def atpEmployer (wages : Int) : Int := if 0 < wages then 2376 else 0''',
      src="the dated statute quotes carried by the 1.x model's parameters (`lean/DKTax/Params.lean`, rounds 15: BEK nr 1621 af 12/12/2023 read from retsinformation.dk, `cmp20/nordic/dk/refs/web/atp_bek_2023_1621.xml`)",
      quotes=["BEK nr 1621 af 12/12/2023 § 2, stk. 1: \"Det almindelige årsbidrag udgør 3.564 kr. (A-satsen)\"; Bilag 1, månedslønnede \"Mindst 117 (fuldtid) 99 198 297\"; § 13: \"træder i kraft den 1. januar 2024\"",
              "ATP-loven § 15, stk. 6: \"Arbejdsgiveren betaler 2/3 af bidraget og medlemmet 1/3\" (1.x `atpEmployer := 2376` for 2025)"],
      grade="A", dated="BEK nr 1621 af 12/12/2023 (A-sats for 2024, still in force in 2025)", testWages=[0, 50000, 500000],
      uns=[("g.household.adults.any (fun a => 0 < a.wages)", "every wage earner taken as full-time monthly paid (A-sats); hours are not in the input. AUB, AES, Barsel.dk, the finansieringsbidrag and the lønsumsafgift (exempt sectors) not modelled")]),
 dict(cc="IE",
      cs=[("Employer PRSI (Class A)", "prsiEmployer", "2200", "Social Welfare Consolidation Act 2005 s. 13 (2) (d) (i)-(ii), as amended by SW(MP)A 2024 s. 3 and Table cols. (4)-(5): 7.9 % / 10.15 % to 30.9.2025, 8 % / 10.25 % from 1.10.2025, the whole week's pay at one rate; weekly threshold €527 (Social Welfare Act 2024)", ie_prsi)],
      lean='''/-- Employer PRSI, SWCA 2005 s. 13 (2) (d): a contribution "at the rate of [x] per cent of the amount of the reckonable
earnings in that week ... where those reckonable earnings do not exceed €527" and at the higher rate "where those
reckonable earnings exceed €527": the whole week's pay at one rate (a cliff, not a band). Rates for 2025 from the
Social Welfare (Miscellaneous Provisions) Act 2024 s. 3 and Table: 7.9 % / 10.15 % on and from 1 October 2024 (col. (4)),
8 % / 10.25 % on and from 1 October 2025 (col. (5)). Threshold €527 from 1 January 2025 (Social Welfare Act 2024 s. 2 (1), in operation 1.1.2025 by s. 2 (2):
"€527" for "€496"). Year convention of the 1.x model (IeTax.Params `payWeeksAt41 = 39`): 52 equal weekly payments, the
first 39 at the January-September rate. Annual pay `w` (euros): weekly pay w / 52 exceeds €527 iff w > 52 × 527. -/
def prsiThresholdYear : Int := 52 * 527
def prsiEmployer (w : Int) : Int :=
  if w ≤ 0 then 0 else
  let low := decide (w ≤ prsiThresholdYear)
  let w1 := w * 39 / 52
  let w2 := w - w1
  (w1 * (if low then 790 else 1015) + w2 * (if low then 800 else 1025)) / 10000''',
      src="Social Welfare Consolidation Act 2005, revised act (Law Reform Commission, updated to 21 January 2026, `cmp20/anglo/ie/refs/swca_rev.pdf`), Social Welfare (Miscellaneous Provisions) Act 2024 (`swmp2024.txt`) and Social Welfare Act 2024 (`swa2024.txt`), irishstatutebook.ie, kept by the 1.x model",
      quotes=["SWCA s. 13 (2) (d) (revised): \"a contribution shall be payable by the employed contributor's employer— (i) at the rate of [..] per cent of the amount of the reckonable earnings in that week to which that payment relates where those reckonable earnings do not exceed €527 ... and (ii) at the rate of [..] per cent ... where those reckonable earnings exceed €527\"",
              "SW(MP)A 2024 s. 3 (1): provisions amended \"on and from 1 October 2024\" by column (4); (2): \"on and from 1 October 2025\" by column (5); Table amendments 2-3 (s. 13 (2) (d) (i), (ii)): \"7.8 per cent\" -> \"7.9 per cent\" -> \"8 per cent\"; \"10.05 per cent\" -> \"10.15 per cent\" -> \"10.25 per cent\"",
              "Social Welfare Act 2024: \"by the substitution, in subparagraph (i), of '€527' for '€496', and (b) ... in subparagraph (ii), of '€527' for '€496'\""],
      grade="A", dated="2025: SW(MP)A 2024 cols. (4)-(5); Social Welfare Act 2024 threshold", testWages=[20000, 27404, 27405, 60000],
      uns=[("g.household.adults.any (fun a => 0 < a.wages)", "National Training Fund levy (1 %, collected with employer PRSI; NTF Act 2000 s. 2 not read) and the 2025 weekly pay pattern (evenly paid, 39 weeks at the January-September rate) taken by convention")]),
 dict(cc="BE",
      cs=[("Cotisation patronale de base (secteur privé, catégorie 1)", "onssBase", "2200", "ONSS instructions 2025/1: cotisation patronale de base 19,88 % (catégories 1 et 3 de la réduction structurelle, from 2018: loi 26.12.2015, loi 16.5.2016)", be_base),
          ("Cotisation de modération salariale", "onssModeration", "2200", "ONSS instructions 2025/1: 4,27 % de la rémunération augmentée de 4,27 % des cotisations patronales dues (catégorie 1)", be_mod)],
      lean='''/-- ONSS, private sector, structural-reduction category 1 (employés, 100 % pay): basic employer contribution 19,88 %
of the gross pay; wage moderation "5,67 % de la rémunération du travailleur, augmentée de 5,67 % des cotisations
patronales dues", lowered to 4,27 % for categories 1 and 3 from 2018: 4,27 % × (pay + 19,88 % of pay). -/
def onssBase (w : Int) : Int := w * 1988 / 10000
def onssModeration (w : Int) : Int := w * 11988 * 427 / 100000000''',
      src="ONSS (Office national de sécurité sociale), instructions administratives DmfA 2025/1, \"Les cotisations ordinaires\" (official administrative instructions, socialsecurity.be, `be/law/onss_ordinarycontributions_2025-1.html`)",
      quotes=["\"Le pourcentage de cotisation applicable est diminué pour ces travailleurs de 22,65 % à 19,88 % à partir du 1 er trimestre 2018.\" (catégories 1 et 3 de la réduction structurelle)",
              "\"La cotisation de modération salariale ... s'élève à 5,67 % de la rémunération du travailleur, augmentée de 5,67 % des cotisations patronales dues.\"; \"Le pourcentage de modération salariale applicable pour ces travailleurs est diminué de 5,67 % à 4,27 % à partir du 1 er trimestre 2018.\""],
      grade="B", dated="ONSS instructions, quarter 2025/1", testWages=[50000, 200000],
      uns=[("g.household.adults.any (fun a => 0 < a.wages)", "employés (pay at 100 %) taken: manual workers' 108 % base and holiday-pay contributions (5,57 % + 10,27 %), the réduction structurelle on low pay, the fonds amiante (0,01 %), accidents du travail (0,02 %), Fonds de fermeture and the 1,60 % sector contributions not modelled")]),

 dict(cc="FR",
      cs=[("Assurance maladie, maternité, invalidité, décès (part patronale)", "frMaladie", "2200", "CSS art. L. 241-2, L. 241-2-1: 13 %, 7 % where the year's pay does not exceed 2,25 SMIC (at 31.12.2023) for employers within the réduction générale (CLEISS 2025)", fr_mal),
          ("Allocations familiales (part patronale)", "frFamille", "2200", "CSS art. L. 241-6, L. 241-6-1: 5,25 %, 3,45 % where the year's pay does not exceed 3,3 SMIC (at 31.12.2023) (CLEISS 2025)", fr_fam),
          ("Contribution solidarité autonomie", "frCsa", "2200", "CASF art. L. 14-10-4: 0,3 % (CLEISS 2025)", fr_csa),
          ("Assurance vieillesse plafonnée (part patronale)", "frViePlaf", "2200", "CSS art. D. 242-4: 8,55 % dans la limite du plafond (3 925 EUR a month in 2025) (CLEISS 2025)", fr_vp),
          ("Assurance vieillesse déplafonnée (part patronale)", "frVieDeplaf", "2200", "CSS art. D. 242-4: 2,02 % sur la totalité du salaire (CLEISS 2025)", fr_vd),
          ("Assurance chômage", "frChomage", "2200", "Convention d'assurance chômage: 4,05 %, 4 % from 1 May 2025, limit 4 plafonds (CLEISS 2025)", fr_cho),
          ("AGS (garantie des salaires)", "frAgs", "2200", "Code du travail art. L. 3253-18: 0,25 %, limit 4 plafonds (CLEISS 2025)", fr_ags),
          ("Retraite complémentaire Agirc-Arrco tranche 1 + CEG (part patronale)", "frT1", "2200", "ANI Agirc-Arrco: 4,72 % + CEG 1,29 % to one plafond (CLEISS 2025)", fr_t1),
          ("Retraite complémentaire Agirc-Arrco tranche 2 + CEG (part patronale)", "frT2", "2200", "ANI Agirc-Arrco: 12,95 % + CEG 1,62 % from one to eight plafonds (CLEISS 2025)", fr_t2),
          ("Contribution d'équilibre technique (part patronale)", "frCet", "2200", "ANI Agirc-Arrco: CET 0,21 % where the pay exceeds the plafond, to eight plafonds (CLEISS 2025)", fr_cet)],
      lean='''/-- Plafond annuel de la sécurité sociale 2025: the monthly ceiling for 2025 is 3 925 € (CLEISS 2025 table, facts);
12 × 3 925 = 47 100, as `Compare.Fr.pass`. -/
def pss : Int := 47100
/-- SMIC en vigueur au 31 décembre 2023, a year: 1 747,20 € a month (vie-publique.fr: 1 766,92 € a month from 1.1.2024,
19,72 € more), × 12 = 20 966,40 €. Thresholds of the reduced rates (CLEISS 2025, notes 1 and 4):
maladie 7 % for pay not exceeding 2,25 SMIC = 47 174,40 €; famille 3,45 % for pay not exceeding 3,3 SMIC = 69 189,12 €.
The reduced rate applies to the WHOLE pay when the year's pay is at or below the threshold, and the full rate to the
whole pay above it: a cliff on the pay, not a marginal band (the kernel `Schedule` is marginal; written by hand). -/
def maladieCliff : Int := 47174
def familleCliff : Int := 69189
def frMaladie (w : Int) : Int := w * (if w ≤ maladieCliff then 700 else 1300) / 10000
def frFamille (w : Int) : Int := w * (if w ≤ familleCliff then 345 else 525) / 10000
def frCsa (w : Int) : Int := w * 30 / 10000
def frViePlaf (w : Int) : Int := min w pss * 855 / 10000
def frVieDeplaf (w : Int) : Int := w * 202 / 10000
/-- 4,05 % to 30 April, 4 % from 1 May 2025 (4 and 8 months of evenly paid pay), limit 4 plafonds. -/
def frChomage (w : Int) : Int := min w (4 * pss) * (4 * 405 + 8 * 400) / 120000
def frAgs (w : Int) : Int := min w (4 * pss) * 25 / 10000
def frT1 (w : Int) : Int := min w pss * 601 / 10000
def frT2 (w : Int) : Int := if w > pss then (min w (8 * pss) - pss) * 1457 / 10000 else 0
def frCet (w : Int) : Int := if w > pss then min w (8 * pss) * 21 / 10000 else 0''',
      src="CLEISS (the French public liaison body for social security), its table of the social-security and unemployment contribution rates at 1 January 2025, cleiss.fr as captured by the Internet Archive on 2025-09-29 (`fr/law/cleiss_taux_wb20250929.html`); facts only, in our words. SMIC at 31.12.2023 from vie-publique.fr (Internet Archive 2024-02-06, `fr/law/vie_publique_smic_2024.html`; facts only)",
      quotes=["Maladie, maternité, invalidité, décès, employer share: 13 % of the whole pay; 7 % for an employee paid at most 2,25 times the SMIC (the table's note 1 takes the SMIC at 31.12.2023; for 2025, D. 241-1-2 takes the SMIC of 1.1.2025: see the FT review below)",
              "Allocations familiales, employer share: 5,25 % of the whole pay; 3,45 % when the employer is within the réduction générale and the year's pay is at most 3,3 times the SMIC (note 4, same SMIC date; D. 241-3-2 for 2025)",
              "CSA: 0,3 %. Capped old-age insurance: 8,55 % up to the monthly ceiling (3 925 €). Uncapped old-age insurance: 2,02 % of the whole pay",
              "Unemployment insurance: 4,05 %, lowered to 4 % from 1 May 2025 (note 6); AGS: 0,25 %; both up to four monthly ceilings (15 700 €)",
              "Agirc-Arrco, employer shares: tranche 1 (up to 3 925 €) 4,72 % plus CEG 1,29 %; tranche 2 (3 925 € to 31 400 €) 12,95 % plus CEG 1,62 %; CET 0,21 % for every employee, cadre or not, whose pay exceeds the ceiling",
              "vie-publique.fr (2024): the gross hourly SMIC became 11,65 € on 1.1.2024, 1 766,92 € a month, 19,72 € a month more than before: so 1 747,20 € a month at 31.12.2023"],
      grade="B", dated="CLEISS table au 1er janvier 2025 (with the 1 May 2025 chômage change)", testWages=[30000, 47174, 47175, 69190, 200000],
      uns=[("g.household.adults.any (fun a => 0 < a.wages)", "accidents du travail (rate by the firm's size and risk), FNAL (0,10 % / 0,50 %), versement mobilité, formation professionnelle and taxe d'apprentissage, APEC and prévoyance cadres not modelled; the réduction générale des cotisations patronales (up to 1,6 SMIC) not applied, which overstates the employer cost of low pay; the thresholds are read on the year's pay, evenly paid")]),
]


def build(r):
    cc = r["cc"]
    items = []
    for name, fn, oecd, st, _ in r["cs"]:
        o = ".sscEmployer" if oecd == "2200" else ".payroll"
        items.append(f"({json.dumps(name, ensure_ascii=False)}, {fn}, {o}, {json.dumps(st, ensure_ascii=False)})")
    lean = r["lean"] + "\n\ndef contribs : List (String × (Int → Int) × Oecd × String) :=\n  [" + ",\n   ".join(items) + "]\n" + """
/-- On the household's wages: each adult, each contribution (borne by the employer). -/
def householdCharges (g : CanonGlobal) : List Charge :=
  if g.entity == .company then [] else
  (g.household.adults.zipIdx.filter (fun (a, _) => 0 < a.wages)).flatMap fun (a, i) =>
    contribs.map fun (nm, f, o, st) =>
      charge o nm a.wages id (fun x => f x) (event := s!"adult {i + 1}") (level := .social)
        (bearer := .employer) (statute := st)

/-- On a company's payroll, spread evenly over its employees. -/
def companyCharges (g : CanonGlobal) : List Charge :=
  if g.entity != .company || g.company.payroll ≤ 0 then [] else
  let n : Int := max 1 (g.company.employees : Int)
  let avg := g.company.payroll / n
  contribs.map fun (nm, f, o, st) =>
    charge o nm g.company.payroll id (fun _ => n * f avg) (event := "payroll") (level := .social)
      (statute := st)
"""
    g = [f"{fn} {w} == {py(w)}" for _, fn, _, _, py in r["cs"] for w in r.get("testWages", [50000, 200000])]
    covers = sorted({".sscEmployer" if c[2] == "2200" else ".payroll" for c in r["cs"]})
    taxes = [{"oecd": oecd, "tax": name, "statute": st, "dated": r["dated"], "grade": r["grade"],
              "kernel_parts": ["charge (hand-written schedule)"], "unsupported": []} for name, fn, oecd, st, _ in r["cs"]]
    taxes += r.get("taxes_extra", [])
    doc = (f"# {cc} 2025: employer social contributions (2200) and payroll taxes (3000)\n\nSource: {r['src']}.\n"
           + "".join(f"* {q}\n" for q in r["quotes"]))
    S = dict(cc=cc, fam="Social", doc=doc, lean=lean,
             families=[("2200/3000 employer contributions", covers, "householdCharges g ++ companyCharges g")],
             notes=[f"{cc} 2200/3000: {r['dated']}"],
             unsupported=r.get("uns", []) + [("g.entity == .company && g.company.payroll > 0", "company payroll spread evenly over its employees")],
             guards=g, taxes=taxes)
    open(os.path.join(HERE, "specs", f"{cc}_Social.py"), "w", encoding="utf-8").write("S = " + repr(S) + "\n")
    print(cc, "Social spec (hand):", len(g), "guards")


if __name__ == "__main__":
    for r in ROWS:
        if len(sys.argv) == 1 or r["cc"] in sys.argv[1:]:
            build(r)
