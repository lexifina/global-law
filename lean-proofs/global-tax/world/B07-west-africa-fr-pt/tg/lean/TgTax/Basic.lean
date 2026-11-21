import TaxKernel.World

/-!
# Togo: impôt sur le revenu des personnes physiques (IRPP), 2025

Access tier B (rescue pass 2). Statute text: the Code général des impôts (CGI, Loi n° 2018-024 as amended by the
finance laws) as consolidated by the tax administration: "Code Général des Impôts & Livre des Procédures Fiscales
2025, mis à jour par la Direction de la Législation Fiscale et du Contentieux" (Office Togolais des Recettes, otr.tg
document 600; archived copy
`web.archive.org/web/20251211205452id_/https://www.otr.tg/index.php/fr/impots/reglementations-fiscales/code-general-des-impots/600-code-general-des-impots-livre-des-procedures-fiscales-mis-a-jour-2025/file.html`,
361 pages with a text layer; `tg/law/rescue2/otr_cgi_lpf_2025.pdf`, sha256 7d0df3af…).
Why B and not A: the art. 74 barème in this edition carries a footnote to the LF 2023 although its wording is the one
the projet de loi de finances 2024 put forward (art. 16, page 17 of `tg/src/PLF-2024.pdf`; both page images compared);
the enacted LF 2024 was not reached, so the date of the barème rests on the administration's consolidation. The PLF 2025
(art. 17) and the LF 2026 (art. 21) list the CGI articles they amend: none of arts. 5, 6, 23, 26, 27, 72-80.

* art. 5: the spouses choose, by a declaration to the employer, which of them has the children "à charge" (default:
  the husband). art. 6: a spouse with own income is taxed separately, as single, without the child reductions unless
  shown to support them; the same child never counts for two spouses.
* art. 23-3: pensions and life annuities are exempt when their annual total "n'excède pas deux millions quatre cent
  mille (2 400 000) francs CFA". art. 27: the net pension retained is "25% lorsque le montant annuel est compris entre
  deux millions quatre cent mille (2 400 000) et trois millions six cent mille (3 600 000) francs CFA" and "50%
  lorsque le montant annuel excède trois millions six cent mille (3 600 000) francs CFA".
* art. 26: net employment income = gross less (1) compulsory pension deductions (at most 6 %), (2) employee social
  contributions, (3)-(9) itemised items; then "une déduction calculée forfaitairement ... fixée à 28 % sur la fraction
  du revenu n'excédant pas dix millions (10 000 000) de francs CFA".
* art. 72: dependants are "le (ou les) conjoint(s) ne disposant pas de ressource", children under 21 (25 if studying),
  and others; "le nombre de personnes à charge ... est limité à six (06)". The reduction exists "exclusivement en
  matière de revenus d'emplois". art. 73: "dix mille (10 000) francs CFA par personne à charge et par mois".
* art. 74: "le revenu net annuel imposable arrondi au millier de francs inférieur" and the barème (Tableau 1, read on
  the page image, p. 40): 0-900 000 exonéré; 900 001-3 000 000 3 %; 3 000 001-6 000 000 10 %; 6 000 001-9 000 000
  15 %; 9 000 001-12 000 000 20 %; 12 000 001-15 000 000 25 %; 15 000 001-20 000 000 30 %; plus de 20 000 000 35 %.
  "Le produit obtenu par application du barème ci-dessus est arrondi à la dizaine de francs inférieure." The article
  ends with a stray paragraph "Abrogé." (also in the PLF 2024 wording).
* arts. 75-77: the art. 74 barème applies "également" to managers' pay, pensions and rental income. art. 78: business
  income (revenus d'affaires) "par application du taux de 30%". arts. 79-80: for natural persons 13 % withholding on
  distributed income and on fixed-income products, "libératoires de l'impôt sur le revenu".

Household mapping: `wages` = gross employment income (art. 25); `pension`; `selfEmployment` = net business income of a
taxpayer outside the impôt synthétique (art. 78); `dividends` / `interest` = gross distributions / fixed-income
products (unlisted shares). Reading: each category is taxed by its own application of the barème (arts. 74-77 apply
it category by category and the family reduction exists only for employment income). Children under 21 are
dependants; a spouse with no earnings and no pension is "sans ressource".
W5 pattern A (2026-11-20; files in `tg/law/w5/`, served by cnss.tg):
* CNSS (Code de sécurité sociale 2011 art. 13: rates by decree; the rate decree itself was not reached). The CNSS's
  page "Cotisations sociales" (official secondary): "Le taux de cotisation sociale est de 21,5% ... Les 4% à la charge
  du travailleur salarié appelés cotisations ouvrières participent au financement de la branche des pensions de
  vieillesse"; "calculées sur l'ensemble des rémunérations du travailleur salarié" (no ceiling stated). Arrêté
  d'application art. 36: the split is the rate decree's.
* AMU: Décret n° 2023-096/PR fixant les taux ... des cotisations ... au titre de l'assurance maladie universelle (loi
  2021-022), page images OCR'd: art. 12 "fixé à 10 % des rémunérations mensuelles soumises à cotisation"; art. 29
  "réparties à raison de 5 % ... à la charge de l'employeur et 5 % à la charge du travailleur salarié"; art. 10 the base
  "ne peut être inférieur ... au montant du salaire minimum interprofessionnel garanti (SMIG)" (the SMIG floor is not
  applied: its 2025 amount was not read).
* Both are "cotisations sociales" deducted under CGI art. 26 (2) (CNSS pension also art. 26 (1), capped at 6 %: 4 % is
  below it). Reading: the 28 % forfait applies to the income after the art. 26 (1)-(9) deductions.
Input `"w5Contrib": false` drops both and their deduction. Rounding of the 28 % deduction and of the flat 30 % / 13 % amounts: not printed; whole francs
down.
-/

namespace TgTax
open TaxKernel

/-- CGI art. 74, Tableau 1 (annual FCFA; each rate applies above the lower bound). -/
def bareme : Schedule := Schedule.ofList
  [(0, 0), (900000, 300), (3000000, 1000), (6000000, 1500), (9000000, 2000), (12000000, 2500),
   (15000000, 3000), (20000000, 3500)]

/-- art. 26 last paragraph: 28 % flat deduction on the fraction not exceeding 10,000,000. -/
def abatRate : Int := 2800
def abatCap : Int := 10000000
def abattement (gross : Int) : Int := (min (pos gross) abatCap) * abatRate / BP

/-- art. 73: 10,000 FCFA per dependant per month; art. 72: at most six dependants. -/
def perDependantMonthly : Int := 10000
def maxDependants : Int := 6
def familyReduction (n : Int) : Int := 12 * perDependantMonthly * min (pos n) maxDependants

/-- art. 74: base rounded down to the thousand, tax rounded down to the ten. -/
def taxOnBase (base : Int) : Int := bareme.tax (Rule.downTo 10) ((Rule.downTo 1000).apply (pos base))

/-- Employee CNSS 4 % (CNSS page) + AMU 5 % (Décret 2023-096 art. 29) of gross remuneration. -/
def cnssEmployee (gross : Int) : Int := pos gross * 400 / BP
def amuEmployee (gross : Int) : Int := pos gross * 500 / BP
def contributions (on : Bool) (gross : Int) : Int := if on then cnssEmployee gross + amuEmployee gross else 0

#guard cnssEmployee 1000000 = 40000 ∧ amuEmployee 1000000 = 50000

/-- Employment income with `n` dependants (arts. 26, 72-74); `on` = W5 contributions deducted (art. 26 (1)-(2)). -/
def wageBaseW (on : Bool) (n gross : Int) : Int :=
  let net := pos gross - contributions on gross
  pos (net - abattement net - familyReduction n)
def wageBase (n gross : Int) : Int := wageBaseW true n gross
def wageTaxW (on : Bool) (n gross : Int) : Int := if gross ≤ 0 then 0 else taxOnBase (wageBaseW on n gross)
def wageTax (n gross : Int) : Int := wageTaxW true n gross

/-- arts. 23-3, 27, 76: pensions. -/
def pensionTaxable (p : Int) : Int :=
  if p ≤ 2400000 then 0 else if p ≤ 3600000 then p * 25 / 100 else p * 50 / 100
def pensionTax (p : Int) : Int := taxOnBase (pensionTaxable p)

/-- art. 78: business income at 30 %; arts. 79-80: 13 % final withholding for natural persons. -/
def businessTax (x : Int) : Int := pos x * 30 / 100
def rcmTax (x : Int) : Int := pos x * 13 / 100

-- The statute's own figures: at the top edge the barème is the sum of each band width times its rate.
#guard bareme.tax (Rule.downTo 10) 20000000 =
  2100000 * 3 / 100 + 3000000 * 10 / 100 + 3000000 * 15 / 100 + 3000000 * 20 / 100 + 3000000 * 25 / 100 + 5000000 * 30 / 100
#guard taxOnBase 900000 = 0
#guard taxOnBase 900999 = 0
#guard abattement 10000000 = 2800000 ∧ abattement 20000000 = 2800000
#guard familyReduction 6 = 720000 ∧ familyReduction 9 = 720000
-- art. 27 notch: one franc above 3,600,000 doubles the retained pension (900,000 -> 1,800,000): 27,000 FCFA more tax.
#guard pensionTax 3600000 = 0 ∧ pensionTax 3600001 = 27000
-- art. 23-3 / 27: 2,400,001 is retained at 25 % = 600,000, inside the exempt band: no tax.
#guard pensionTax 2400001 = 0
-- art. 72: a spouse's first franc of income ends the 120,000 FCFA reduction (earner at 6,000,000 gross, no children).
#guard wageTaxW false 1 6000000 = 183000 ∧ wageTaxW false 0 6000000 = 195000

def nKids (c : Canon) : Int := (c.children.filter (fun k => k.age < 21)).length

def noResource (a : Adult) : Bool := a.wages ≤ 0 && a.selfEmployment ≤ 0 && a.pension ≤ 0

structure Res where
  wage : Int
  pension : Int
  business : Int
  dependantsA : Int
  dependantsB : Int

def household (c : Canon) : Res :=
  let on := (c.bool? "w5Contrib").getD true
  let wageTax := wageTaxW on
  let k := nKids c
  let pen := sumInts (c.adults.map fun a => pensionTax a.pension)
  let bus := sumInts (c.adults.map fun a => businessTax a.selfEmployment)
  match c.adults with
  | [a] => ⟨wageTax k a.wages, pen, bus, min k maxDependants, 0⟩
  | [a, b] =>
    let spA : Int := if c.married && noResource b then 1 else 0
    let spB : Int := if c.married && noResource a then 1 else 0
    -- art. 5: the spouses choose which of them has the children (one only, art. 6): the cheaper choice
    let o1 := wageTax (spA + k) a.wages + wageTax spB b.wages
    let o2 := wageTax spA a.wages + wageTax (spB + k) b.wages
    if o1 ≤ o2 then ⟨o1, pen, bus, min (spA + k) maxDependants, spB⟩
    else ⟨o2, pen, bus, spA, min (spB + k) maxDependants⟩
  | _ => ⟨sumInts (c.adults.map fun a => wageTax 0 a.wages), pen, bus, 0, 0⟩

def out (c : Canon) : Out :=
  let r := household c
  let rcm := rcmTax c.dividends + rcmTax c.interest
  let on := (c.bool? "w5Contrib").getD true
  let cn := if on then sumInts (c.adults.map fun a => cnssEmployee a.wages) else 0
  let am := if on then sumInts (c.adults.map fun a => amuEmployee a.wages) else 0
  Out.make c "TG" "XOF" (r.wage + r.pension + r.business + rcm)
    (employeeSocial := cn + am)
    (detail := [Out.d "irppEmploi" r.wage, Out.d "irppPensions" r.pension, Out.d "irppRevenusAffaires" r.business,
      Out.d "retenueLiberatoireRCM" rcm, Out.d "cnssEmployee" cn, Out.d "amuEmployee" am, Out.d "dependantsAdult1" r.dependantsA, Out.d "dependantsAdult2" r.dependantsB,
      Out.dStr "note" "CGI 2025 (OTR/DLFC consolidation) arts. 5-6, 23, 26-27, 72-80; barème per category; CNSS 4 % + AMU 5 % deducted (art. 26)"])
    (unsupported := ["CNSS rate from the CNSS page (rate decree not reached); AMU base floor at the SMIG (Décret 2023-096 art. 10) not applied"] ++
      (if c.rentalIncome ≠ 0 then ["rental income (revenus fonciers, arts. 14-16, 77): not modelled"] else []) ++
      (if c.capitalGains ≠ 0 then ["capital gains (taxe sur les plus-values, CGI ch. II): not modelled"] else []) ++
      (if c.children.any (fun k => k.age ≥ 21) then ["children aged 21-24 count as dependants only while studying (art. 72): not counted"] else []))

def country : Country := { code := "TG", name := "Togo", currency := "XOF", year := "2025", compute := out }

theorem bareme_progressive : bareme.progressive = true := by decide

end TgTax
