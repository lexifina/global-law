import R4Common

/-!
# Guinea-Bissau 2025: corporate income tax (1200) and withholding (generated from `R4/specs/gw.json`)

No usable 2025 text for these headings: only budget documents (OGE 2023-2026 proposals) and a 2021 DGCI instruction are held; the IGV, contribuição industrial and excise texts are not. Pass 10 (IVA): customs-service uploads `alfandegas.mef.gw/wp-content/uploads/2025/03/…` listed by Wayback CDX (`url=mef.gw&matchType=domain&filter=mimetype:application/pdf`): IVA-E-LEI-GERAL-TRIBUTARIA.pdf (the Wayback copy is truncated at 5 MB; the live file, 33 MB, 59 pages, is complete), Codigo-IGV-2014.pdf, RGIT-e-IEC-1.pdf (IEC code; its rate table annex is not in the text layer), Lei-2-2018 (OGE 2018), Lei-no-1-OGE-2022 (scanned), in `R4/fetch/gw10/`. MEF Despacho 44/2020 (new IGV return from 1 Jan 2021) read by OCR.




-/

namespace GwGlobal
open TaxKernel TaxKernel.Global



def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["CIT not modelled: only budget documents (OGE 2023-2026 proposals) and a 2021 DGCI instruction are held; the IGV, contribuição industrial and excise texts are not", "withholding on payments abroad not modelled: Código do Imposto de Capitais (Decreto 8/84) art. 1 c) as amended by Lei 2/2018 art. 11 taxes dividends and repatriated profits, but the code's rates are not held; no withholding text for interest, royalties or services"]

end GwGlobal
