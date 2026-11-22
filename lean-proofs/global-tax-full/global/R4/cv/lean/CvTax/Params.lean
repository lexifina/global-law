import TaxKernel.World

/-!
# Cabo Verde 2025: parameters, each with its dated source (whole escudos)

Sources: DNRE (Ministério das Finanças) legislation library, https://www.mf.gov.cv/web/dnre/legislacao (fetched
2026-11-20; copies in `../src/`):
* Código do IRPS, Lei n.º 78/VIII/2014 (B.O. I Série n.º 81, 31 de dezembro de 2014), and its republication by
  Lei n.º 116/IX/2021 de 2 de fevereiro ("Alterações Códigos Tributários", B.O. I Série n.º 10), which is the wording
  used here (articles cited by that numbering).
* Orçamento do Estado 2025 (B.O. I Série n.º 125 Sup., 30 de dezembro de 2024): it contains fiscal incentives but no
  amendment of the IRPS articles used here. The budgets for 2022-2024 were not read for IRPS amendments (access B).
* NOT reached: the category A progressive withholding tables ("legislação específica", art. 70-71; Decreto-Lei 6/2015
  and later portarias), so the model computes the annual tax by englobamento (art. 45), which the taxpayer may always
  elect (art. 28 1.).
-/

namespace CvTax
open TaxKernel

/-- Art. 46.º 1.: "a) 16,5% para rendimentos até 960.000$00 ... anuais; b) 23,1% para rendimentos superiores a
960.000$00 ... e até 1.800.000$00 ... anuais; c) 27,5% para rendimentos superiores a 1.800.000$00". Reading A
(default): band rates on each slice. -/
def sched : Schedule := Schedule.ofList [(0, 1650), (960000, 2310), (1800000, 2750)]

/-- Art. 46.º 2.: "Por cada sujeito passivo que engloba o rendimento é fixado 220.000$00 ... a título de mínimo de
existência" (deducted from the collectable income, art. 45.º 1. b)). -/
def minimoExistencia : Int := 220000

/-- Art. 54.º: "À colecta do imposto é deduzido o valor de 5.000$00 ... por cada uma das seguintes pessoas, com o
máximo de 25.000$00": dependants who are not taxpayers, disabled dependants, ascendants. -/
def perDependant : Int := 5000
def dependantCap : Int := 25000

/-- Art. 19.º 3. a): dependants are "Os filhos, adoptados, enteados, menores não emancipados" (b): up to 24 if in
11th/12th year or higher education). Reading: under 18. -/
def childAgeLimit : Nat := 18

/-- Art. 50.º: category D (capital income) "taxa de retenção na fonte de 20% ... excepto os das alíneas f), e j) do
artigo 14º cuja taxa é de 10% ..., todos com caráter liberatório, sem opção de englobamento". Reading: the household's
interest and dividends at 20 % (art. 14 f) and j) not read). -/
def capitalRate : Int := 2000
/-- Art. 49.º: category C "taxa de retenção na fonte de 10% ... com caracter liberatório, ... sem prejuízo da opção de
englobamento". Reading: category C = property (rental) income. -/
def rentalRate : Int := 1000

end CvTax
