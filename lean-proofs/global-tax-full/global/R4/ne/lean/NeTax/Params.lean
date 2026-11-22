import TaxKernel.World

/-!
# Niger 2025: parameters, each with its dated source (whole francs CFA)

Sources (copies in `../src/`; impots.gouv.ne does not answer from our hosts, so both are archived official copies):
* Code général des impôts (Loi n° 2012-37 du 20 juin 2012), DGI edition "CGI 2013 MAJ LF 2022"
  (`impots.gouv.ne/media/telech/CGI 2013 MAJ LF  2022.pdf`, Wayback 20230727151430): arts. 52-68 (ITS), 69-99 (IRCM).
* Ordonnance n° 2024-59 portant loi de finances 2025 (`impots.gouv.ne/media/loi/ORDONNANCE N 2024-59 LOI DE FINANCES
  2025..pdf`, Wayback 20250709034954): art. 11 replaces CGI art. 52 (what is taxable) and art. 12 replaces arts. 73-75
  (IRVM) "A compter du 1er janvier 2025"; no other ITS article is amended.
* The lois de finances 2023 and 2024 were NOT reached: arts. 60-66 are taken in their LF 2022 wording (access B).
-/

namespace NeTax
open TaxKernel

/-- Art. 66: "L'impôt sur les traitements, salaires et revenus assimilés est un impôt progressif calculé par tranches
mensuelles": 0 à 25 000: 1 %; 25 001 à 50 000: 2 %; 50 001 à 100 000: 6 %; 100 001 à 150 000: 13 %; 150 001 à 300 000:
25 %; 300 001 à 400 000: 30 %; 400 001 à 700 000: 32 %; 700 001 à 1 000 000: 34 %; au-delà de 1 000 000: 35 %. -/
def monthly : Schedule :=
  Schedule.ofList [(0, 100), (25000, 200), (50000, 600), (100000, 1300), (150000, 2500), (300000, 3000),
    (400000, 3200), (700000, 3400), (1000000, 3500)]

/-- Art. 61: "calculé sur la base d'un revenu net mensuel arrondi au millier de francs inférieur". -/
def rounding : Int := 1000

/-- Art. 60: deductions "dans l'ordre suivant": 1) pension retentions "limités à 6 % du montant de la rémunération
principale brute"; 2) 17 % for expatriates with a dépaysement allowance (not in the contract); 3) insurance premiums
up to 20 000 F; 4) "d'un abattement de 13%, pour frais professionnels, sur le salaire imposable". -/
def pensionDedCap : Int := 600
def proAbat : Int := 1300

/-- Art. 65: "Les charges de famille ... donnent droit aux abattements suivants": 0: 0 %; 1: 5 %; 2: 10 %; 3: 12 %;
4: 13 %; 5: 14 %; 6: 15 %; 7: 30 %. Art. 64: at most seven dependants per household, children at most six. -/
def familyAbat (n : Int) : Int :=
  match min n 7 with
  | 1 => 500 | 2 => 1000 | 3 => 1200 | 4 => 1300 | 5 => 1400 | 6 => 1500 | 7 => 3000 | _ => 0

/-- Art. 64 1): children "mineurs célibataires âgés de 21 ans au plus" (or up to 25 if students), "dans la limite de
six (6)"; 2): "un conjoint ne disposant pas de revenu". Children counted: age ≤ 21. -/
def childMaxAge : Nat := 21
def maxChildren : Int := 6

/-- LF 2025 art. 12, CGI art. 74 (nouveau): "10% pour les dividendes" (7 % for listed companies). -/
def dividendRate : Int := 1000
/-- Art. 80: IRC 20 %, "Toutefois, il est de 10% pour les intérêts ... des comptes de dépôts ... d'une banque";
art. 97 exempts savings-book interest. Reading: the household's interest is bank-deposit interest (10 %). -/
def bankInterestRate : Int := 1000

end NeTax
