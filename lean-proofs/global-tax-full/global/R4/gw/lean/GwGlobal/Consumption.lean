import R4Common

/-!
# Guinea-Bissau 2025: VAT (5111) and excises (5121) (generated from `R4/specs/gw.json` by `R4/tools/gen_country.py`)

No usable 2025 text for these headings: only budget documents (OGE 2023-2026 proposals) and a 2021 DGCI instruction are held; the IGV, contribuição industrial and excise texts are not. Pass 10 (IVA): customs-service uploads `alfandegas.mef.gw/wp-content/uploads/2025/03/…` listed by Wayback CDX (`url=mef.gw&matchType=domain&filter=mimetype:application/pdf`): IVA-E-LEI-GERAL-TRIBUTARIA.pdf (the Wayback copy is truncated at 5 MB; the live file, 33 MB, 59 pages, is complete), Codigo-IGV-2014.pdf, RGIT-e-IEC-1.pdf (IEC code; its rate table annex is not in the text layer), Lei-2-2018 (OGE 2018), Lei-no-1-OGE-2022 (scanned), in `R4/fetch/gw10/`. MEF Despacho 44/2020 (new IGV return from 1 Jan 2021) read by OCR.

Código do IVA "ARTIGO 18.º Taxas 1. As taxas do imposto são as seguintes: a) Para as importações, transmissões de bens e prestações de serviços constantes do Anexo I ao presente código, a taxa 10%; b) Para as restantes importações, transmissões de bens e prestações de serviços, a taxa de 19%; c) Para as exportações, a taxa 0%." Art. 15.º n.º 1: "Estão isentas de Imposto sobre o Valor Acrescentado as seguintes operações: a) A transmissão dos medicamentos, produtos farmacêuticos e produtos para atividades médicas constantes do Anexo II ...; b) A prestação de cuidados médicos, realizadas por hospitais, centros de saúde, clínicas ...; c) As prestações de serviços efetuadas no exercício de profissões médicas e paramédicas ...; d) As prestações de serviços realizadas no domínio do ensino escolar ou universitário ...; e) O gás para uso doméstico; f) As operações financeiras e as operações de seguro e de resseguro que não sejam remuneradas por uma comissão ou contraprestação explícita; g) As operações imobiliárias relativas a imóveis com fins de habitação, com exceção das prestações de serviços de alojamento efetuadas no âmbito da atividade hoteleira". Lei n.º 4/2022 "ARTIGO 7.º Revogações São revogadas as seguintes disposições legais: a) O Código do Imposto Geral sobre Vendas e Serviços, aprovado pela Lei n.º 16/97, de 31 de março".


-/

namespace GwGlobal
open TaxKernel TaxKernel.Global

def vatX : Vat :=
  { name := "Imposto sobre o Valor Acrescentado (IVA)", standard := 1900, reduced := 1000, reduced2 := 0,
    threshold := 0,
    classOf := fun gd => match gd with
      | .medicines | .health | .education | .gas | .financial | .insurance | .rent => .exempt
      | _ => .standard }

def vat : Family := R4.vatFamily vatX "Código do IVA (Lei n.º 4/2022) art. 18.º n.º 1 (taxas: 10 % for the Anexo I goods and services, 19 % otherwise, 0 % exports) and art. 15.º n.º 1 (isenções); Lei n.º 4/2022 art. 7.º repeals the Código do IGV"

-- the standard rate as printed: 19 % inside a tax-inclusive 11900
#guard vatX.embedded { good := .other, amount := 11900 } == 1900
#guard vatX.embedded { good := .medicines, amount := 10000 } == 0
#guard vatX.embedded { good := .health, amount := 10000 } == 0
#guard vatX.embedded { good := .education, amount := 10000 } == 0

def consumptionNotes (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty then [] else
  ["the IVA replaces the IGV (17 %, Código do IGV 2014 art. 15.º); the texts held do not state from which date the IVA is applied (no commencement date found in Lei n.º 4/2022; the OGE laws 2023-2025 were not read): flagged — if the IGV were still applied in 2025 the rate would be 17 %", "the Anexo I goods at 10 % were not read: no basket line is moved to the reduced rate; financial and insurance services are exempt only without an explicit fee", "only businesses above the FCFA 40 million threshold charge IVA (not modelled)", "excises not modelled: only budget documents (OGE 2023-2026 proposals) and a 2021 DGCI instruction are held; the IGV, contribuição industrial and excise texts are not"]

end GwGlobal
