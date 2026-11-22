import R4Common

/-!
# Sao Tome and Principe 2025: corporate income tax (1200) and withholding (generated from `R4/specs/st.json`)

Pass 10: Direcção dos Impostos legislation downloads (`impostos.financas.gov.st/index.php/legislacao/leg-tributaria/category/<cat>?download=<id>:<slug>`, ids 173 IRC, 172 CMT, 180 IVA, 179 IEC) and the OGE 2024 law (`financas.gov.st/phocadownload/Orcamento/oge/A-2024/OGE2024-APROVADO/…`), via Wayback, in `R4/fetch/st10/` (SHA256SUMS; the CMT decree OCRed). The IEC decree (Decreto-Lei n.º 27/2021) is held but its Anexo I rate table pages are blank in the published copy.

CIRC "Artigo 81.º Taxas 1. A taxa geral do IRC é de 25%. 2. São tributados em 20% os rendimentos sujeitos à retenção na fonte nos termos do artigo 86.º." Decreto-Lei n.º 6/2016 art. 1.º: subject to the minimum contribution are "os sujeitos passivos de IRC cujo imposto anual liquidado ... seja inferior ao valor mínimo fixado no artigo 3.º". OGE 2024 law art. 8: "10. É alterado o n.º 2 do artigo 3.º do Decreto-Lei n.º 6/2016, de 31 de Outubro, que passa a ter a seguinte redacção: «O valor mínimo fixado para o IRC é de Dbs: 2.544,00». ... 14. Todas as alterações constantes na presente Lei manter-se-ão em vigor até aprovação e publicação da Lei do Orçamento Geral do Estado do ano seguinte."

CIRC art. 86.º "1. O IRC é objecto de retenção na fonte relativamente aos seguintes rendimentos obtidos em território são-tomense ...: a) Rendimentos provenientes da propriedade intelectual ou industrial ...; c) Rendimentos de aplicação de capitais tal como são definidos para efeitos de IRS; ... g) Rendimentos provenientes da realização de trabalhos ou serviços para um cliente no território são-tomense ... 3. As retenções na fonte têm a natureza de imposto por conta, excepto quando o titular dos rendimentos seja entidade não residente que não tenha estabelecimento estável ..., caso em que a retenção na fonte tem carácter definitivo. 4. As retenções na fonte ... são efectuadas à taxa prevista no n.º 2 do artigo 81.º" (20 %).
-/

namespace StGlobal
open TaxKernel TaxKernel.Global

def citR : CorpRegime :=
  { name := "Imposto sobre o Rendimento das Pessoas Colectivas (IRC)", sched := Schedule.flat 2500, lossFull := -1, lossExcessBp := 10000 }

def minT : R4.MinTax := { bp := 0, fixed := 2544, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citR minT { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1 == 2500249
#guard R4.corpTax citR minT { profit := 0, turnover := 1000000000, lossesForward := 0 } 1 == 2544
#guard R4.corpTax citR minT { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1 == 2544
#guard R4.corpTax citR minT { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1 == 250000
def whtR : Wht :=
  { name := "IRC withholding on non-residents (final)",
    rules := [{ kind := .royalty, rateBp := 2000, statute := "CIRC art. 86.º n.º 1 a), art. 81.º n.º 2: 20 %" },
              { kind := .dividend, rateBp := 2000, statute := "CIRC art. 86.º n.º 1 c), art. 81.º n.º 2: 20 %" },
              { kind := .interest, rateBp := 2000, statute := "CIRC art. 86.º n.º 1 c), art. 81.º n.º 2: 20 %" },
              { kind := .services, rateBp := 2000, statute := "CIRC art. 86.º n.º 1 g), art. 81.º n.º 2: 20 %" }] }
#guard whtR.amount { kind := .royalty, amount := 1000000 } == 200000
#guard whtR.amount { kind := .dividend, amount := 1000000 } == 200000
#guard whtR.amount { kind := .interest, amount := 1000000 } == 200000
#guard whtR.amount { kind := .services, amount := 1000000 } == 200000
def corporate : Family :=
  { name := "1200 Imposto sobre o Rendimento das Pessoas Colectivas (IRC)", covers := [.cit],
    run := fun _ g _ => if g.entity != .company then [] else [R4.citCharge citR minT g.company "Código do IRC (Lei n.º 10/2009) art. 81.º n.º 1 (taxa geral 25 %); contribuição mínima, Decreto-Lei n.º 6/2016 art. 1.º and 3.º n.º 2 as amended by the OGE 2024 law art. 8 n.º 10 (Dbs 2.544,00)" (step := 1)] ++ whtR.charges g.company }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["the OGE 2024 changes are applied to 2025 (they stay in force until the next OGE law; the OGE 2025 law is not held)", "the 'selo de conhecimento e cobrança' added to the minimum (Dbs 72.000 old dobras in 2016) is not modelled", "the 2009 code text is used; amendments other than the OGE 2024 law were not read (flagged)"]

end StGlobal
