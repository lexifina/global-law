import R4Common

/-!
# Mozambique 2025: VAT (5111) and excises (5121) (generated from `R4/specs/mz.json` by `R4/tools/gen_country.py`)

No usable 2025 text for these headings: the IRPC law 19/2013 (registry fetch) and AT page dumps are held; the 2025 IRPC/IVA rates were not located. Lei 22/2022 and Lei 19/2022 (Boletim da República, 28-29 Dec 2022) fetched from www.at.gov.mz (`/api/documents?root=LEGISLAÇÃO` lists the library; files via `/api/webdav?path=...`), saved in `cmp20/global/R4/fetch/mz8/` with SHA256SUMS. Pass 9 (IRPC): Lei n.º 34/2007 (Código do IRPC, BR I Série n.º 52) from the AT site's former download (Wayback 2014-2018 captures of www.at.gov.mz/por/content/download/2131/16310, `R4/fetch/mz9/at_lei34_2007_cirpc.pdf`), Lei n.º 4/2012 (Wayback of www.at.gov.mz/eng/content/download/1319/10270, page 5 read on the image), Lei n.º 19/2013 (`registry/afm_data/fetch/MZ/mz_irpc_lei19_2013.pdf`), the Comissão do Plano e Orçamento opinion n.º 09/2022 on the bill that became Lei n.º 20/2022 (parlamento.mz upload via Wayback: amends only art. 61-62 for agriculture, aquaculture and urban transport to 31 Dec 2025), and BR I Série n.º 248 suplemento of 29 Dec 2025 (AT library: Lei n.º 12/2025 lists the amending laws 20/2009, 4/2012, 19/2013, 20/2022 and applies from 1 Jan 2026). SHA256SUMS in `R4/fetch/mz9/`.

Lei n.º 22/2022 (BR I série n.º 250, 28 Dec 2022) 'Altera os artigos 9, 10, 12, 15, 17, 20 e 21 do Código do Imposto sobre o Valor Acrescentado': "Artigo 17 (Taxa do imposto) 1. A taxa do imposto é de 16%." No later amendment of art. 17 is listed in the AT library.

art. 27: "2. O grau de teor alcoólico é expresso por litro de álcool puro a 100% ... 3. O valor do Imposto sobre Consumos Específicos é obtido através da multiplicação da taxa pela quantidade do bem ... na unidade de tributação prevista em litros, pela quantidade de álcool expressa em volume (ex: 5%=0,05, 42%=0,42)". Tabela de taxas (columns Taxa 2023 / 2024 / 2025, MT): "2203.00.10 - De malte ... 465/Litro Alc. 470/Litro Alc. 475/Litro Alc."; "2204.21.00 -- Em recipientes de capacidade não sup. a 2 litros ... 610/Litro Alc. 614/Litro Alc. 619/Litro Alc."; "2208.30.00 - Uísques ... 455/Litro Alc. 457/Litro Alc. 460/Litro Alc."; "2402.20.00 - Cigarros contendo tabaco ... 500/mil Unid 520/mil Unid 540/mil Unid".
-/

namespace MzGlobal
open TaxKernel TaxKernel.Global

def vatX : Vat :=
  { name := "Imposto sobre o Valor Acrescentado", standard := 1600, reduced := 0, reduced2 := 0,
    threshold := 0,
    classOf := fun gd => match gd with
      | _ => .standard }

def vat : Family := R4.vatFamily vatX "Código do IVA (Lei n.º 32/2007, republicado pela Lei n.º 13/2016) art. 17 (1) as amended by Lei n.º 22/2022: 16 %"

-- the standard rate as printed: 16 % inside a tax-inclusive 11600
#guard vatX.embedded { good := .other, amount := 11600 } == 1600
def accises : List R4.Exc :=
  [ { good := .beer, name := "ICE cervejas de malte", perUnitNum := 475000, perUnitDen := 1000, vatBp := 1600, onPureAlcohol := true, statute := "Código do ICE tabela 2203.00.10 (475 MT/l alc., 2025)" },
    { good := .wine, name := "ICE vinhos", perUnitNum := 619000, perUnitDen := 1000, vatBp := 1600, onPureAlcohol := true, statute := "Código do ICE tabela 2204.21.00 (619 MT/l alc., 2025)" },
    { good := .spirits, name := "ICE bebidas espirituosas", perUnitNum := 460000, perUnitDen := 1000, vatBp := 1600, onPureAlcohol := true, statute := "Código do ICE tabela 2208 (460 MT/l alc., 2025)" },
    { good := .cigarettes, name := "ICE cigarros", perUnitNum := 540, perUnitDen := 1000, vatBp := 1600, statute := "Código do ICE tabela 2402.20.00 (540 MT por mil, 2025)" } ]
def excise : Family := R4.exciseFamily "Imposto sobre Consumos Específicos" accises
-- Código do ICE tabela 2203.00.10 (475 MT/l alc., 2025): 10000 paid for 1 unit(s) at 5 % vol → 23
#guard (R4.exciseCharges [{ good := .beer, name := "ICE cervejas de malte", perUnitNum := 475000, perUnitDen := 1000, vatBp := 1600, onPureAlcohol := true, statute := "Código do ICE tabela 2203.00.10 (475 MT/l alc., 2025)" }] [{ good := .beer, amount := 10000, quantity := 1000, abvBp := 500 }] []).map (·.due) == [23]
-- Código do ICE tabela 2204.21.00 (619 MT/l alc., 2025): 10000 paid for 1 unit(s) at 12 % vol → 74
#guard (R4.exciseCharges [{ good := .wine, name := "ICE vinhos", perUnitNum := 619000, perUnitDen := 1000, vatBp := 1600, onPureAlcohol := true, statute := "Código do ICE tabela 2204.21.00 (619 MT/l alc., 2025)" }] [{ good := .wine, amount := 10000, quantity := 1000, abvBp := 1200 }] []).map (·.due) == [74]
-- Código do ICE tabela 2208 (460 MT/l alc., 2025): 10000 paid for 1 unit(s) at 40 % vol → 184
#guard (R4.exciseCharges [{ good := .spirits, name := "ICE bebidas espirituosas", perUnitNum := 460000, perUnitDen := 1000, vatBp := 1600, onPureAlcohol := true, statute := "Código do ICE tabela 2208 (460 MT/l alc., 2025)" }] [{ good := .spirits, amount := 10000, quantity := 1000, abvBp := 4000 }] []).map (·.due) == [184]
-- Código do ICE tabela 2402.20.00 (540 MT por mil, 2025): 10000 paid for 1 unit(s) at 0 % vol → 0
#guard (R4.exciseCharges [{ good := .cigarettes, name := "ICE cigarros", perUnitNum := 540, perUnitDen := 1000, vatBp := 1600, statute := "Código do ICE tabela 2402.20.00 (540 MT por mil, 2025)" }] [{ good := .cigarettes, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [0]

def consumptionNotes (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty then [] else
  ["art. 9 exemptions (health services, education, financial services, basic foods, ...) and art. 10 reduced regimes are not applied: only the amended paragraphs were read", "soft drinks are taxed per gram of added sugar per 100 ml (2202.99.10: 0,0147 MT in 2025): the basket carries no sugar content, not applied", "local cereal beers (2203.00.50) and opaque beer (5,50 MT/l) not separable; fuel ICE not modelled"]

end MzGlobal
