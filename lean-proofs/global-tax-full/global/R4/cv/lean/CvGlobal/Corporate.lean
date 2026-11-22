import R4Common

/-!
# Cabo Verde 2025: corporate income tax (1200) and withholding (generated from `R4/specs/cv.json`)

No usable 2025 text for these headings: the 2025 State Budget law and the 2020-2021 tax laws are held; IVA and IRPC rates were not located in the extraction. Pass 10 (IRPC/retenções): Lei n.º 86/IX/2020 republications (`world/B07-west-africa-fr-pt/cv/src/Lei-86-IX-2020.flow.txt`: CIRPC art. 84-89 from line ~10150, CIRPS art. 14, 48-52 from line ~11352) and OE 2025 (`OE-2025.flow.txt` art. 25-26, 73).

CIRPC (republicação, Lei n.º 86/IX/2020) "Artigo 84º Taxa geral de imposto 1. A taxa de IRPC é de 22% (vinte e dois por cento) para os sujeitos passivos enquadrados no regime de contabilidade organizada. 2. Os sujeitos passivos enquadrados no regime simplificado para micro e pequenas empresas estão sujeitos a uma taxa de 4% (quatro por cento) incidente sobre o volume de negócios, nos termos previstos no artigo 96.º." OE 2025 art. 25: "É alterado o artigo 68.º, da Lei n.º 82/VIII/2015 ... na redação que lhe foi dada pela Lei n.º 16/X/2022, de 30 de dezembro e pela Lei n.º 35/X/2023, de 31 de dezembro".

CIRPC "Artigo 89º ... 1. Os rendimentos obtidos em território nacional, nos termos do artigo 7.º, por não residentes que não sejam imputáveis a estabelecimento estável nele situado, são tributados nos seguintes termos: a) Através da aplicação das taxas de retenção na fonte referidas no Código do IRPS, com carácter liberatório, e sem opção de englobamento". CIRPS "Artigo 50º Taxa de retenção da categoria D: Os rendimentos da categoria D estão sujeitos a taxa de retenção na fonte de 20% (vinte porcentos), excepto os das alíneas f), e j) do artigo 14º cuja taxa é de 10% (dez porcentos), todos com carácter liberatório"; art. 14.º n.º 2: "a) Os juros ... de contratos de mútuo ...; j) ... os dividendos e quaisquer participações nos lucros das sociedades ...; k) Os rendimentos provenientes de contratos que tenham por objecto a cessão ou utilização temporária de direitos de propriedade intelectual ou industrial ..."; "Artigo 48º ... 1. Os rendimentos da categoria B estão sujeitos a taxa de retenção na fonte de 15%".
-/

namespace CvGlobal
open TaxKernel TaxKernel.Global

def citR : CorpRegime :=
  { name := "Imposto sobre o Rendimento das Pessoas Coletivas (IRPC)", sched := Schedule.flat 2200, lossFull := -1, lossExcessBp := 10000 }

def minT : R4.MinTax := { bp := 0, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citR minT { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1 == 2200219
#guard R4.corpTax citR minT { profit := 0, turnover := 1000000000, lossesForward := 0 } 1 == 0
#guard R4.corpTax citR minT { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1 == 0
#guard R4.corpTax citR minT { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1 == 220000
def whtR : Wht :=
  { name := "Retenção na fonte sobre não residentes sem estabelecimento estável",
    rules := [{ kind := .dividend, rateBp := 1000, statute := "CIRPS art. 50.º with art. 14.º n.º 2 j): dividends 10 %" },
              { kind := .interest, rateBp := 2000, statute := "CIRPS art. 50.º with art. 14.º n.º 2 a): loan interest 20 %" },
              { kind := .royalty, rateBp := 2000, statute := "CIRPS art. 50.º with art. 14.º n.º 2 k): royalties 20 %" },
              { kind := .services, rateBp := 1500, statute := "CIRPS art. 48.º n.º 1 (category B) via CIRPC art. 89.º: 15 %" }] }
#guard whtR.amount { kind := .dividend, amount := 1000000 } == 100000
#guard whtR.amount { kind := .interest, amount := 1000000 } == 200000
#guard whtR.amount { kind := .royalty, amount := 1000000 } == 200000
#guard whtR.amount { kind := .services, amount := 1000000 } == 150000
def corporate : Family :=
  { name := "1200 Imposto sobre o Rendimento das Pessoas Coletivas (IRPC)", covers := [.cit],
    run := fun _ g _ => if g.entity != .company then [] else [R4.citCharge citR minT g.company "Código do IRPC art. 84.º n.º 1 (republished by Lei n.º 86/IX/2020): 22 % for taxpayers under organised accounting; OE 2025 art. 25 amends art. 68.º only [text version: the codes as republished by Lei n.º 86/IX/2020 (B.O. I Série n.º 53, 28 April 2020); Lei n.º 16/X/2022 and Lei n.º 35/X/2023 not held (flag)]" (step := 1)] ++ whtR.charges g.company }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["the CIRPC was amended by Lei n.º 16/X/2022 and Lei n.º 35/X/2023 (budget laws for 2023 and 2024), not held: art. 84.º is taken as unchanged (flagged)", "the micro and small enterprise regime (4 % of turnover) is not modelled", "services paid to a non-resident company are taken as category B income at the 15 % rate (final under CIRPC art. 89.º); bond and deposit interest (art. 14.º n.º 2 f), 10 %) is not the modelled loan-interest line", "the 2022 and 2023 amending laws were not read (flagged)"]

end CvGlobal
