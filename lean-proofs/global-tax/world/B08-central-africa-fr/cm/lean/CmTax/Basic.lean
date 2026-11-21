import TaxKernel.World

/-!
# Cameroon: IRPP on wages (Code général des impôts), centimes additionnels communaux, taxe de développement local,
contribution au Crédit Foncier, redevance audiovisuelle and the CNPS pension contribution, tax year 2025

Sources (files in `cm/law/`, sha256 in `SHA256SUMS`):
* CGI édition 2024 (impots.cm, Internet Archive copy 2024-02-17, `cgi2024.pdf`) and CGI édition 2026 (impots.cm,
  fetched 2026-11-20, `cgi2026.pdf`): arts. 29, 34, 69, 70 (1), 71 read identically in both editions; the LF 2025
  circular (impots.cm, archived 2025-02-28, scanned, OCR `circ_lf2025.ocr.txt`) changes no wage provision and adds the
  10 % IRCM rate for dividends of companies with turnover <= 3 bn (from 1 January 2025; CGI 2026 art. 70 (2)).
  * art. 29: "après abattement d'un montant forfaitaire de 500 000 F CFA en ce qui concerne les traitements et salaires"
  * art. 34: "les frais professionnels calculés forfaitairement au taux de 30 %, ainsi que les cotisations versées ...
    (CNPS) au titre de la retraite obligatoire ... plafonné à FCFA quatre millions huit cent mille (4 800 000) par an"
  * art. 69 (1): "De 0 à 2 000 000 ... 10 % / De 2 000 001 à 3 000 000 .. 15 % / De 3 000 001 à 5 000 000 .. 25 % /
    Plus de 5 000 000 ... 35 %"
  * art. 70 (1): revenus des capitaux mobiliers "taux libératoire de 15 %"; (2) "10 % pour les dividendes
    régulièrement distribués par les entreprises dont le chiffre d'affaires est inférieur ou égal à trois (3) milliards"
  * art. 71: "L'impôt calculé ... prévus aux articles 69 et 70 ... sont majorés de 10 % au titre des centimes
    additionnels communaux"
* Loi 77-10 du 13 juillet 1977 (CGI annex): art. 6 (1) "1 % pour les salariés", (2) "La base de prélèvement est
  arrondie au millier de F CFA inférieur"; art. 5: pensions not subject.
* Ordonnance 89/004 du 12 décembre 1989 (CGI annex) art. 3 (5) as modified by LF 2003/017: monthly flat amounts by
  monthly gross salary (0 up to 50 000; 750 ... 13 000 above 1 000 000); art. 6: pensions exempt.
* Taxe de développement local: CGI 2024 art. C 58 ("Les taux maxima ... salaire de base mensuel compris entre 62 000 et
  75 000 F CFA : 3 000 F CFA/an ... supérieur à 500 000 F CFA : 30 000 F CFA/an"); the same scale is CGI 2026 art. C 86.
* CNPS: Décret n° 2016/072 du 15 février 2016 (CNPS Recueil des textes de base, Nov. 2022, archived): art. 3 pension
  "4,2 % à la charge du travailleur"; art. 4 "plafond des rémunérations de sept cent cinquante mille (750.000) francs par
  mois, soit neuf millions (9.000.000) de francs par an". Still listed as the contribution decree on cnps.cm "Textes
  réglementaires" (archived 2025-10-13).
-/

namespace CmTax
open TaxKernel

def pct (bp x : Int) : Int := divR .halfUp (x * bp) 10000

/-- art. 69 (1). -/
def sched : Schedule := Schedule.ofList [(0, 1000), (2000000, 1500), (3000000, 2500), (5000000, 3500)]
def abattement : Int := 500000        -- art. 29
def fraisRate : Int := 3000           -- art. 34
def fraisCap : Int := 4800000         -- art. 34
def cacRate : Int := 1000             -- art. 71 (10 % of the tax)
def rcmRate : Int := 1500             -- art. 70 (1)
def rcmSmeDivRate : Int := 1000       -- art. 70 (2), from 2025
def cfcRate : Int := 100              -- Loi 77-10 art. 6 (1)
def cnpsRate : Int := 420             -- Décret 2016/072 art. 3
def cnpsCapMonth : Int := 750000      -- Décret 2016/072 art. 4

/-- Ordonnance 89/004 art. 3 (5): monthly redevance audiovisuelle by monthly gross salary. -/
def ravTable : Table :=
  [ {lo := 0, hi := 50000, value := 0}, {lo := 50001, hi := 100000, value := 750},
    {lo := 100001, hi := 200000, value := 1950}, {lo := 200001, hi := 300000, value := 3250},
    {lo := 300001, hi := 400000, value := 4550}, {lo := 400001, hi := 500000, value := 5850},
    {lo := 500001, hi := 600000, value := 7150}, {lo := 600001, hi := 700000, value := 8450},
    {lo := 700001, hi := 800000, value := 9750}, {lo := 800001, hi := 900000, value := 11050},
    {lo := 900001, hi := 1000000, value := 12350} ]
def rav (m : Int) : Int := if m ≤ 0 then 0 else Table.lookup ravTable m 13000

/-- CGI 2024 art. C 58 (= CGI 2026 art. C 86): annual TDL by monthly base salary (maximum rates; the commune's own
rate is not modelled). -/
def tdlTable : Table :=
  [ {lo := 62000, hi := 75000, value := 3000}, {lo := 75001, hi := 100000, value := 6000},
    {lo := 100001, hi := 125000, value := 9000}, {lo := 125001, hi := 150000, value := 12000},
    {lo := 150001, hi := 200000, value := 15000}, {lo := 200001, hi := 250000, value := 18000},
    {lo := 250001, hi := 300000, value := 24000}, {lo := 300001, hi := 500000, value := 27000} ]
def tdl (m : Int) : Int := if m < 62000 then 0 else Table.lookup tdlTable m 30000

structure Person where
  gross : Int
  cnps : Int
  frais : Int
  taxable : Int
  irpp : Int
  cfc : Int
  rav : Int
  tdl : Int
  deriving Repr

/-- One person's wages (and pension, same category, art. 30) for the year, paid evenly over 12 months. -/
def person (w pension : Int) : Person :=
  let w := pos w
  let p := pos pension
  let cnps := perPeriod 12 (fun m => pct cnpsRate (min m cnpsCapMonth)) w
  let g := w + p
  let frais := min (pct fraisRate g) fraisCap
  let net := pos (g - frais - cnps)
  let taxable := pos (net - (if w > 0 then abattement else 0))
  let irpp := sched.tax Rule.unitHalfUp taxable
  let cfc := perPeriod 12 (fun m => pct cfcRate (toMultiple .down 1000 m)) w
  let rv := perPeriod 12 rav w
  let td := if w > 0 then tdl (divR .halfUp w 12) else 0
  { gross := g, cnps := cnps, frais := frais, taxable := taxable, irpp := irpp, cfc := cfc, rav := rv, tdl := td }

/-- DGI withholding convention (`--dgi-bareme`, rule 8: the authority's own published method). CGI édition officielle 2026,
annexe "NOTE EXPLICATIVE SUR L'UTILISATION DU BAREME DE L'IRPP (Nouvelle version)" (signed by the Directeur Général des
Impôts; `cgi2026.txt`), "Formule de calcul ... servira notamment ... à la rédaction des programmes informatiques de
retenues de l'IRPP sur les salaires", Sbm = monthly gross salary: up to 62 000: 0; 62 001-310 000: "(Sbm * 70 % - Sbm *
2,8 % - 41,667) * 10 %"; 310 001-429 000: "16 693 + (Sbm - 310 000) * 70 % * 15 %"; 429 001-667 000: "29 188 + (Sbm -
429 000) * 70 % * 25 %"; 667 001 and more: "70 830 + (Sbm - 667 000) * 70 % * 35 %". The method departs from the
statute: CNPS at 2,8 % on at most 300 000 a month (the note: "taux de 2,8 % sur le salaire mensuel brut plafonné à
300 000"; the decree in force is 4,2 % up to 750 000) and no 4 800 000 cap on the 30 % frais (art. 34). Monthly tax in
francs (half-up), x 12. Round D6. -/
def dgiMonthly (sbm : Int) : Int :=
  let r (x : Int) (num : Int) := divR .halfUp (x * num) 1000000
  if sbm ≤ 62000 then 0
  else if sbm ≤ 310000 then pos (divR .halfUp ((sbm * 7000 - min sbm 300000 * 280 - 416670000) * 1000) 100000000)
  else if sbm ≤ 429000 then 16693 + r (sbm - 310000) 105000
  else if sbm ≤ 667000 then 29188 + r (sbm - 429000) 175000
  else 70830 + r (sbm - 667000) 245000

/- The note's fixed amounts are its first-band formula at the band top with the CNPS term capped at 300 000 (its text:
"2,8 % sur le salaire mensuel brut plafonné à 300 000"): (217 000 - 8 400 - 41 667) x 10 % = 16 693,3 -> 16 693;
then 16 693 + 119 000 x 70 % x 15 % = 29 188; 29 188 + 238 000 x 70 % x 25 % = 70 838 (the note prints 70 830);
at 3 000 000: 70 830 + 2 333 000 x 70 % x 35 % = 642 415. -/
#guard dgiMonthly 310000 = 16693 ∧ dgiMonthly 429000 = 29188 ∧ dgiMonthly 667000 = 70838
#guard dgiMonthly 62000 = 0 ∧ dgiMonthly 3000000 = 642415

def out (args : List String) (c : Canon) : Out :=
  let dgi := args.contains "--dgi-bareme"
  let ps := c.adults.map fun a => person a.wages a.pension
  let irpp := if dgi then sumInts (c.adults.map fun a => 12 * dgiMonthly (divR .halfUp (pos a.wages) 12)) else sumInts (ps.map (·.irpp))
  let smeDiv := (c.bool? "dividendsSmallCompany").getD false
  let rcm := pct rcmRate (pos c.interest) + pct (if smeDiv then rcmSmeDivRate else rcmRate) (pos c.dividends)
  let cac := pct cacRate irpp + pct cacRate rcm
  let cfc := sumInts (ps.map (·.cfc))
  let rv := sumInts (ps.map (·.rav))
  let td := sumInts (ps.map (·.tdl))
  let cnps := sumInts (ps.map (·.cnps))
  let unsup :=
    (if (c.adults.map (·.selfEmployment)).any (· ≠ 0) then ["self-employment (BIC/BNC: art. 17 rate with the 2 % turnover minimum, art. 69 (2)) not modelled"] else []) ++
    (if c.rentalIncome ≠ 0 then ["rental income (revenus fonciers: art. 69 (2)) not modelled"] else []) ++
    (if c.capitalGains ≠ 0 then ["capital gains not modelled"] else [])
  Out.make c "CM" "XAF" (irpp + rcm) (surtaxes := [("creditFoncier", cfc), ("redevanceAudiovisuelle", rv)])
    (localIncomeTax := cac + td) (employeeSocial := cnps)
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (·.taxable))), Out.d "irppWages" irpp, Out.d "ircm" rcm,
      Out.d "centimesAdditionnels" cac, Out.d "taxeDeveloppementLocal" td, Out.d "fraisProfessionnels" (sumInts (ps.map (·.frais))),
      Out.dStr "note" "IRPP on wages: (gross - 30 % frais capped 4.8 M - CNPS pension) - 500 000, art. 69 bands 10/15/25/35 %; CAC 10 % of IRPP and IRCM (art. 71); TDL at the CGI's maximum rates; CFC 1 %; RAV monthly table; CNPS pension 4.2 % capped 750 000 a month"])
    (unsupported := unsup ++ ["individual taxation: no family quotient or child relief in the CGI (art. 67)",
      "wages paid evenly over 12 months; TDL base taken as the monthly wage (the CGI uses the monthly base salary) at the maximum communal rates"])

def country : Country :=
  { code := "CM", name := "Cameroon (IRPP + CAC + TDL + CFC + RAV)", currency := "XAF", year := "2025", compute := out [], computeWith := out }

theorem sched_progressive : sched.progressive = true := by decide

/- Hand-computed statutory cases (the statute prints no worked example):
   gross 3 600 000: CNPS 4.2 % = 151 200; frais 30 % = 1 080 000; net 2 368 800; taxable 1 868 800;
   IRPP 10 % = 186 880; CAC 18 688. -/
#guard (person 3600000 0).irpp = 186880
#guard (out [] { id := "c", adults := [{ wages := 3600000 }] }).localIncomeTax = 18688 + 24000
/- 20 M gross: frais capped at 4.8 M; CNPS 4.2 % of 9 M = 378 000; net 14 822 000; taxable 14 322 000;
   IRPP 200 000 + 150 000 + 500 000 + 35 % x 9 322 000 = 4 112 700. -/
#guard (person 20000000 0).irpp = 4112700
/- 62 000 a month is the art. 81 withholding threshold: the annual tax is zero there. -/
#guard (person 744000 0).irpp = 0
#guard rav 50000 = 0 ∧ rav 50001 = 750 ∧ rav 1000001 = 13000
#guard tdl 61999 = 0 ∧ tdl 62000 = 3000 ∧ tdl 500001 = 30000

end CmTax
