import R4Common

/-!
# Sao Tome and Principe 2025: VAT (5111) and excises (5121) (generated from `R4/specs/st.json` by `R4/tools/gen_country.py`)

Pass 10: Direcção dos Impostos legislation downloads (`impostos.financas.gov.st/index.php/legislacao/leg-tributaria/category/<cat>?download=<id>:<slug>`, ids 173 IRC, 172 CMT, 180 IVA, 179 IEC) and the OGE 2024 law (`financas.gov.st/phocadownload/Orcamento/oge/A-2024/OGE2024-APROVADO/…`), via Wayback, in `R4/fetch/st10/` (SHA256SUMS; the CMT decree OCRed). The IEC decree (Decreto-Lei n.º 27/2021) is held but its Anexo I rate table pages are blank in the published copy.

Lei n.º 13/2019, "Artigo 16.º Taxa 1. A taxa do imposto é de 15%. 2. Os produtos constantes do anexo I, quando vendidos no mercado nacional, ficam sujeitos ao regime especial de aplicação do IVA, sendo que a taxa do IVA em vigor incidi sobre 50% do valor total da factura." "Artigo 17.º Isenções nas operações internas. Estão isentas do imposto: a) A prestação de seguros e resseguros de vida; b) As operações de intermediação financeira, incluindo aquelas listadas no Anexo II, mas exceptuando aquelas em que uma taxa, ou contraprestação, específica é cobrada pelo serviço; c) A transmissão de ouro para investimento; d) A transmissão do direito de propriedade de bens imóveis, à exclusão da primeira transmissão, destinados a fins residenciais ...; e) A locação de bens imóveis destinados a fins residenciais ...".


-/

namespace StGlobal
open TaxKernel TaxKernel.Global

def vatX : Vat :=
  { name := "Imposto sobre o Valor Acrescentado (IVA)", standard := 1500, reduced := 0, reduced2 := 0,
    threshold := 0,
    classOf := fun gd => match gd with
      | .financial | .insurance | .rent => .exempt
      | _ => .standard }

def vat : Family := R4.vatFamily vatX "Lei n.º 13/2019 (Código do IVA) art. 16.º n.º 1 (taxa 15 %) and art. 17.º (isenções nas operações internas: seguros e resseguros de vida, intermediação financeira, locação de imóveis para fins residenciais)"

-- the standard rate as printed: 15 % inside a tax-inclusive 11500
#guard vatX.embedded { good := .other, amount := 11500 } == 1500
#guard vatX.embedded { good := .financial, amount := 10000 } == 0
#guard vatX.embedded { good := .insurance, amount := 10000 } == 0
#guard vatX.embedded { good := .rent, amount := 10000 } == 0

def consumptionNotes (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty then [] else
  ["health and education are not in the art. 17.º exemption list and are taxed at 15 %", "the Anexo I products taxed on 50 % of the invoice (an effective 7.5 %) were not identified (the annex was not read): no basket line is moved to it", "only life insurance is exempt; amendments after 2019 other than the OGE 2024 law were not read (OGE 2025 not held)", "excises not modelled: the rates are in Anexo I of Decreto-Lei n.º 27/2021 (art. on 'Taxas aplicáveis': 'As taxas ... correspondem às constantes da tabela anexa'), and the annex pages (D.R. n.º 87 of 11 Nov 2021, pp. 1299-1300) are blank in the published PDF"]

end StGlobal
