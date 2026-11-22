import R4Common

/-!
# Chad 2025: corporate income tax (1200) and withholding (generated from `R4/specs/td.json`)

Sources: CGI 2016 (`world/B08-central-africa-fr/td/law/cgi2016.raw.txt`), LF 2023 OCR (`lf2023.ocr.txt`), DGI circular on LF 2024 (`circ_lf2024.raw.txt`; the LF 2024 PDF itself is unreadable), LF 2025 OCR (`lf2025.ocr.txt`).

DGI circular on LF 2024, para. 6: "Les dispositions nouvelles de l'article 143 du CGI consacrent la baisse de taux de l'Impôt sur les Sociétés (IS) de 35 % à 30 %. Le taux de 30 % s'applique à toutes les personnes physiques et morales quelle que soit l'activité à l'exception des entreprises pétrolières et minières ... des entreprises industrielles de transformation des produits locaux ... du secteur de l'énergie"; para. 8-9: "modifient le taux de l'Impôt Minimum Forfaitaire (IMF) en le portant de 1,5 % à 2 % ... Le taux de l'IMF de 2 % s'applique sur le chiffre d'affaires mensuel hors taxes". CGI 2016 art. 151 II: "un plancher de un million (1.000.000) de Francs CFA par an". The LF 2024 text itself is not readable here (grade B); LF 2025 does not amend art. 143 or 151.

LF 2025 art. 19 quotes art. 26 as in force before 1 Jan 2025: "Les frais d'études, de siège, d'assistance technique, financière, comptable ... versées aux sociétés non-résidentes ... sont soumis à un prélèvement libératoire retenu à la source, au taux de 18 %" (the 25 % paragraph is the LF 2024 struck wording: the DGI circular, para. 25, says LF 2024 brought it 'de 25 % à 18 %' for contracts from 1 Jan 2024; the art. 26 (nouveau) of LF 2025 restates the deduction limits and leaves this paragraph unchanged). LF 2025 art. 23, art. 82 (nouveau): "Les revenus des capitaux mobiliers entrant dans les provisions des articles 74 à 78 donnent lieu à l'application d'une retenue à la source au taux est de 18 %". Circular para. 23: art. 84 interest to persons without a professional establishment 'de 25 % à 18 %'. Twelfth pass (kernel 2.3.0 grade-C withholding): royalty 25 %: CGI 2016 art. 59, 857 I (retenue 25 % on sums paid to persons without a professional installation in Chad); the LF 2024 cut to 18 % (art. 857) lists services, studies, head-office and assistance fees, medical services and interconnection charges only (DGI circular LF 2024 para 25): royalties kept at 25 % (flag)
-/

namespace TdGlobal
open TaxKernel TaxKernel.Global

def citR : CorpRegime :=
  { name := "Impôt sur les sociétés", sched := Schedule.flat 3000, lossFull := -1, lossExcessBp := 10000 }

def minT : R4.MinTax := { bp := 200, fixed := 0, floor := 1000000, cap := -1, onAssets := false }
#guard R4.corpTax citR minT { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1 == 3000299
#guard R4.corpTax citR minT { profit := 0, turnover := 1000000000, lossesForward := 0 } 1 == 20000000
#guard R4.corpTax citR minT { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1 == 1000000
#guard R4.corpTax citR minT { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1 == 8000000
def whtR : Wht :=
  { name := "Retenues à la source (non-résidents)",
    rules := [{ kind := .services, rateBp := 1800, statute := "CGI art. 26 (18 %, LF 2024)" },
              { kind := .dividend, rateBp := 1800, statute := "CGI art. 82 (nouveau), LF 2025 art. 23 (18 %)" },
              { kind := .interest, rateBp := 1800, statute := "CGI art. 84 (18 %, LF 2024 per the DGI circular)" },
              { kind := .royalty, rateBp := 2500, statute := "CGI 2016 art. 59, 857 I (retenue 25 % on sums paid to persons without a professional installation in Chad); the LF 2024 cut to 18 % (art. 857) lists services, studies, head-office and assistance fees, medical services and interconnection charges only (DGI circular LF 2024 para 25): royalties kept at 25 % (flag)" }] }
#guard whtR.amount { kind := .services, amount := 1000000 } == 180000
#guard whtR.amount { kind := .dividend, amount := 1000000 } == 180000
#guard whtR.amount { kind := .interest, amount := 1000000 } == 180000
#guard whtR.amount { kind := .royalty, amount := 1000000 } == 250000
def corporate : Family :=
  { name := "1200 Impôt sur les sociétés", covers := [.cit],
    run := fun _ g _ => if g.entity != .company then [] else [R4.citCharge citR minT g.company "CGI art. 143 as amended by LF 2024 (30 %, per the DGI circular); art. 151 (IMF 2 % of turnover from 1 Jan 2024, per the circular; floor 1 000 000 F, CGI 2016 art. 151 II)" (step := 1)] ++ whtR.charges g.company }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["CGI art. 143-151: IS 30 % and IMF 2 % from the DGI circular on LF 2024 (the act's text not read); the 1 000 000 F floor is the CGI 2016 wording; the CGI 2016 rounding (fractions under 20 000 F) is not applied since art. 143 was rewritten", "the 25 % vs 18 % pair in LF 2025's quotation of the old art. 26 is the LF 2024 amendment (25 % struck, 18 % in force from 1 Jan 2024): 18 % applied"]

end TdGlobal
