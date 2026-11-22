import R4Common

/-!
# Burundi 2025: corporate income tax (1200) and withholding (generated from `R4/specs/bi.json`)

No usable 2025 text for these headings: the income tax laws (2013, 2020) and the LF 2025-26 OCR are held; the VAT law is not; the company rate was not mapped in this pass. Second pass: Loi n°1/14 du 24 décembre 2020 (impôts sur les revenus) with the LF 2025/2026 derogations; LF 2021-2025 not held. Pass 10 (TVA, taxe de consommation): Loi n°1/10 du 16 novembre 2020 portant modification de la Loi n°1/12 du 29 juillet 2013 (TVA), scanned PDF from obr.bi (`www.obr.bi/images/LOI_N1_10_DU_16_NOVEMBRE_2020_…TVA_.pdf`, the Wayback copy is truncated; the live file is complete), OCR (tesseract fra) in `R4/fetch/bi10/` (SHA256SUMS); LF 2025/2026 OCR already held (`world/B08-central-africa-fr/bi/law/lf2025_26.ocr1-70.txt`). The LF 2023/24 PDFs held are corrupt (no xref).

art. 103: "Le montant des revenus imposables est arrondi en millier de francs burundais le plus proche et imposé au taux de trente pour cent (30%), à l'exception des revenus locatifs imposables au taux prévu à l'article 21" (OCR prints "(50%)" after the words "trente pour cent": the words govern). The 2020 law is the latest IR text held; the LF 2025/2026 derogations read do not change the rate: grade B.

art. 122: "Une retenue de quinze pour cent (15%) est pratiquée sur les paiements ci-après effectués par les personnes résidentes ... 1° les dividendes ... 2° les paiements d'intérêts de toute nature ... 3° les redevances à l'exception de celles payées à l'État ; 4° les rémunérations de prestations fournies par des personnes non-résidentes au Burundi"; art. 102: for non-residents without a permanent establishment the withholdings "ont un caractère libératoire".
-/

namespace BiGlobal
open TaxKernel TaxKernel.Global

def citR : CorpRegime :=
  { name := "Impôt sur les revenus des sociétés", sched := Schedule.flat 3000, lossFull := -1, lossExcessBp := 10000 }

def minT : R4.MinTax := { bp := 0, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citR minT { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1 == 3000299
#guard R4.corpTax citR minT { profit := 0, turnover := 1000000000, lossesForward := 0 } 1 == 0
#guard R4.corpTax citR minT { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1 == 0
#guard R4.corpTax citR minT { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1 == 300000
def whtR : Wht :=
  { name := "Retenue à la source (art. 122)",
    rules := [{ kind := .dividend, rateBp := 1500, statute := "Loi IR 2020 art. 122 1° (15 %)" },
              { kind := .interest, rateBp := 1500, statute := "Loi IR 2020 art. 122 2° (15 %)" },
              { kind := .royalty, rateBp := 1500, statute := "Loi IR 2020 art. 122 3° (15 %)" },
              { kind := .services, rateBp := 1500, statute := "Loi IR 2020 art. 122 4° (15 %)" }] }
#guard whtR.amount { kind := .dividend, amount := 1000000 } == 150000
#guard whtR.amount { kind := .interest, amount := 1000000 } == 150000
#guard whtR.amount { kind := .royalty, amount := 1000000 } == 150000
#guard whtR.amount { kind := .services, amount := 1000000 } == 150000
def corporate : Family :=
  { name := "1200 Impôt sur les revenus des sociétés", covers := [.cit],
    run := fun _ g _ => if g.entity != .company then [] else [R4.citCharge citR minT g.company "Loi n°1/14 du 24/12/2020 art. 103 (30 %)" (step := 1)] ++ whtR.charges g.company }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["Loi IR 2020 art. 103: 30 %; rounding to the nearest 1 000 FBu not applied"]

end BiGlobal
