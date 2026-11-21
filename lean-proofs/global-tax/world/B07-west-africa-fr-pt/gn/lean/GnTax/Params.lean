import TaxKernel.World

/-!
# Guinea 2025: parameters, each with its dated source (whole Guinean francs)

Sources (copies in `../src/`), from the Journal officiel of the Secrétariat général du Gouvernement
(https://journal-officiel.sgg.gov.gn, search "Droit fiscal", fetched 2026-11-20):
* Code général des impôts, Loi ordinaire L/2021/032/AN, "Promulguée par Décret D/2021/236/PRG/SGG du 21 Juillet 2021",
  "Code applicable à partir du 1er Janvier 2022" (`textes-officiels/lois/2021/Guinee-Loi-2021-32.pdf`).
* Loi L/2024/023/CNT portant loi de finances pour l'année 2025 (`.../lois/2024/Guinee-Loi-2024-23.pdf`, scanned, OCR):
  22 pages of budget articles, no amendment of the CGI.
* The lois de finances 2022-2024 were NOT read for CGI amendments: arts. 57-69 and 189-191 are taken in their 2021
  wording (access B).
-/

namespace GnTax
open TaxKernel

/-- CGI art. 63: "Le montant de la retenue est calculé par application au revenu mensuel imposable les taux
suivants": 0 à 1 000 000: 0 %; 1 000 001 à 3 000 000: 5 %; 3 000 001 à 5 000 000: 8 %; 5 000 001 à 10 000 000: 10 %;
10 000 001 à 20 000 000: 15 %; supérieure à 20 000 000: 20 %. Art. 64: "La retenue prévue à l'article 61 est
libératoire." Art. 68: pensions and life annuities at the same rates (art. 69: final). -/
def monthly : Schedule :=
  Schedule.ofList [(0, 0), (1000000, 500), (3000000, 800), (5000000, 1000), (10000000, 1500), (20000000, 2000)]

/-- Art. 189 II: dividends "La retenue au taux de quinze pourcent (15%)"; art. 190 III: interest 15 %, but II "ne
s'applique pas aux intérêts provenant de comptes d'épargne ou de comptes de dépôt à terme de plus de trois (3) mois";
art. 191: "Les retenues à la source prévues aux articles 189 et 190 sont libératoires." -/
def dividendRate : Int := 1500
def interestRate : Int := 1500

end GnTax
