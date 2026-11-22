import R4Common

/-!
# Angola 2025: VAT (5111) and excises (5121) (generated from `R4/specs/ao.json` by `R4/tools/gen_country.py`)

No usable 2025 text for these headings: OCR excerpts (pages 1-30) of budget laws and a tax-code page are held; the IVA, Imposto Industrial and IEC codes are not. Pass 9: Diário da República scans from files.lex.ao (Lei 7/19, 17/19, 14/23, 16/21, 19/14, 26/20, 27/22) and the IAC code from ucm.minfin.gov.ao (minfin052583.pdf, AGT attachment list), OCR (tesseract por, `R4/tools/ocr9.sh`) in `R4/fetch/ao9/` (SHA256SUMS; IEC Anexo I read on the page image). Amendments checked: the lex.ao list of Assembleia Nacional laws 2021-2025 (`world/B09-southern-africa/ao/law/rescue2/an_desc.tsv`: only Lei 16/21 touches the IEC, only Lei 32/21 and 14/23 the IVA code, only Lei 27/22 the CII) and the OGE laws 2022-2025 (first 30 pages); OGE 2026 (Lei 14/25) changes the IAC from 2026 only.

Código do IVA (republicação, Lei n.º 14/23) art. 19 (Taxas do imposto): "1. As taxas do imposto são as seguintes: a) 14%, como taxa geral, para as importações, transmissões de bens e prestações de serviços; b) 7% para o regime simplificado; c) 7% para as prestações de serviços de hotelaria e restauração; d) 5% para as importações e transmissões de bens alimentares de amplo consumo e insumos agrícolas constantes dos Anexos I e II do presente Código; e) 1%, para ... a Província de Cabinda"; art. 12 n.º 1: "Estão isentos do imposto: ... b) As transmissões de medicamentos destinados exclusivamente a fins terapêuticos e profiláticos; ... d) A transmissão de livros ... e) A locação de bens imóveis, com excepção das prestações de serviços de alojamento ... h) O serviço de transporte colectivo de passageiros; i) As operações de intermediação financeira ... k) As transmissões de produtos petrolíferos, conforme Anexo IV ... l) A prestação de serviços de ensino ... m) A prestação de serviço médico sanitário". The petroleum annex lists "Óleos de petróleo ou de minerais betuminosos, excepto óleos brutos".

art. 7 (Base de cálculo do Imposto): "1. O valor tributável sujeito a Imposto Especial de Consumo é: a) Para os bens produzidos no País, o valor da transacção; b) Para os bens importados, o valor aduaneiro; ... e) Para os derivados do petróleo, o Imposto incide sobre o custo de produção." art. 11: "As taxas do Imposto Especial de Consumo correspondem às constantes das tabelas dos Anexos I e II da presente Lei." Anexo I (Tabela de Taxas ... Aplicáveis aos Produtos de Produção Nacional e Importados, IEC %): 2202.10.00 águas adicionadas de açúcar 3; 2202.91.00 cerveja sem álcool 4; 2202.99.00 outras 4; 2203.00.00 cervejas de malte 4; 2204 vinhos 8; 2205 vermutes 8; 2206 outras bebidas fermentadas 8; 2208.20-2208.90 aguardentes, uísques, rum, gin, vodca, licores 8; 2402.20.00 cigarros 25.
-/

namespace AoGlobal
open TaxKernel TaxKernel.Global

def vatX : Vat :=
  { name := "Imposto sobre o Valor Acrescentado", standard := 1400, reduced := 700, reduced2 := 0,
    threshold := 0,
    classOf := fun gd => match gd with
      | .medicines | .books | .rent | .transport | .financial | .education | .health | .petrol | .diesel => .exempt
      | .restaurants | .hotels => .reduced
      | _ => .standard }

def vat : Family := R4.vatFamily vatX "Código do IVA (Lei n.º 7/19, republished by Lei n.º 14/23 de 28 de Dezembro) art. 19 n.º 1 (14 % general; 7 % simplified regime and hotel/restaurant services; 5 % Anexo I basic foods and Anexo II farm inputs; 1 % Cabinda special regime) and art. 12 n.º 1 (exemptions)"

-- the standard rate as printed: 14 % inside a tax-inclusive 11400
#guard vatX.embedded { good := .other, amount := 11400 } == 1400
#guard vatX.embedded { good := .medicines, amount := 10000 } == 0
#guard vatX.embedded { good := .books, amount := 10000 } == 0
#guard vatX.embedded { good := .rent, amount := 10000 } == 0
def accises : List R4.Exc :=
  [ { good := .nonAlcoholic, name := "IEC águas adicionadas de açúcar (2202.10)", advBp := 300, vatBp := 1400, statute := "Lei 16/21 Anexo I 2202.10.00 (3 %)" },
    { good := .beer, name := "IEC cervejas de malte (2203)", advBp := 400, vatBp := 1400, statute := "Lei 16/21 Anexo I 2203.00.00 (4 %)" },
    { good := .wine, name := "IEC vinhos (22.04)", advBp := 800, vatBp := 1400, statute := "Lei 16/21 Anexo I 22.04 (8 %)" },
    { good := .spirits, name := "IEC bebidas espirituosas (22.08)", advBp := 800, vatBp := 1400, statute := "Lei 16/21 Anexo I 22.08 (8 %)" },
    { good := .cigarettes, name := "IEC cigarros (2402.20)", advBp := 2500, vatBp := 1400, statute := "Lei 16/21 Anexo I 2402.20.00 (25 %)" } ]
def excise : Family := R4.exciseFamily "Imposto Especial de Consumo" accises
-- Lei 16/21 Anexo I 2202.10.00 (3 %): 10000 paid for 1 unit(s) at 0 % vol → 255
#guard (R4.exciseCharges [{ good := .nonAlcoholic, name := "IEC águas adicionadas de açúcar (2202.10)", advBp := 300, vatBp := 1400, statute := "Lei 16/21 Anexo I 2202.10.00 (3 %)" }] [{ good := .nonAlcoholic, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [255]
-- Lei 16/21 Anexo I 2203.00.00 (4 %): 10000 paid for 1 unit(s) at 5 % vol → 337
#guard (R4.exciseCharges [{ good := .beer, name := "IEC cervejas de malte (2203)", advBp := 400, vatBp := 1400, statute := "Lei 16/21 Anexo I 2203.00.00 (4 %)" }] [{ good := .beer, amount := 10000, quantity := 1000, abvBp := 500 }] []).map (·.due) == [337]
-- Lei 16/21 Anexo I 22.04 (8 %): 10000 paid for 1 unit(s) at 12 % vol → 649
#guard (R4.exciseCharges [{ good := .wine, name := "IEC vinhos (22.04)", advBp := 800, vatBp := 1400, statute := "Lei 16/21 Anexo I 22.04 (8 %)" }] [{ good := .wine, amount := 10000, quantity := 1000, abvBp := 1200 }] []).map (·.due) == [649]
-- Lei 16/21 Anexo I 22.08 (8 %): 10000 paid for 1 unit(s) at 40 % vol → 649
#guard (R4.exciseCharges [{ good := .spirits, name := "IEC bebidas espirituosas (22.08)", advBp := 800, vatBp := 1400, statute := "Lei 16/21 Anexo I 22.08 (8 %)" }] [{ good := .spirits, amount := 10000, quantity := 1000, abvBp := 4000 }] []).map (·.due) == [649]
-- Lei 16/21 Anexo I 2402.20.00 (25 %): 10000 paid for 1 unit(s) at 0 % vol → 1754
#guard (R4.exciseCharges [{ good := .cigarettes, name := "IEC cigarros (2402.20)", advBp := 2500, vatBp := 1400, statute := "Lei 16/21 Anexo I 2402.20.00 (25 %)" }] [{ good := .cigarettes, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [1754]

def consumptionNotes (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty then [] else
  ["the 5 % rate for Anexo I basic foods is not applied to the processed-food basket line (region convention)", "the 7 % hotel/restaurant rate requires the art. 19 n.º 2 compliance conditions (assumed met); the simplified regime (7 %), the Cabinda 1 % regime and the OGE 2025 art. 22 5 % rate on industrial equipment are not modelled; health insurance and life insurance (art. 12 j) are exempt but the insurance line is taken as other insurance", "the non-alcoholic basket line is charged at the 2202.10 sweetened-water rate (3 %); other 2202.99 drinks are 4 %, plain water and juices of 20.09 are outside the table", "Anexo II (petroleum products) taxes the cost of production (art. 7 n.º 1 e), which the input does not carry: petrol and diesel are not charged"]

end AoGlobal
