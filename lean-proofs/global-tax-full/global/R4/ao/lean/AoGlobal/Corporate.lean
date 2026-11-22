import R4Common
import TaxKernel.Global2

/-!
# Angola 2025: corporate income tax (1200) and withholding (generated from `R4/specs/ao.json`)

No usable 2025 text for these headings: OCR excerpts (pages 1-30) of budget laws and a tax-code page are held; the IVA, Imposto Industrial and IEC codes are not. Pass 9: Diário da República scans from files.lex.ao (Lei 7/19, 17/19, 14/23, 16/21, 19/14, 26/20, 27/22) and the IAC code from ucm.minfin.gov.ao (minfin052583.pdf, AGT attachment list), OCR (tesseract por, `R4/tools/ocr9.sh`) in `R4/fetch/ao9/` (SHA256SUMS; IEC Anexo I read on the page image). Amendments checked: the lex.ao list of Assembleia Nacional laws 2021-2025 (`world/B09-southern-africa/ao/law/rescue2/an_desc.tsv`: only Lei 16/21 touches the IEC, only Lei 32/21 and 14/23 the IVA code, only Lei 27/22 the CII) and the OGE laws 2022-2025 (first 30 pages); OGE 2026 (Lei 14/25) changes the IAC from 2026 only.

Lei n.º 26/20, art. 64.º (Taxas): "1. A taxa geral do Imposto Industrial é de 25%. 2. Tratando-se de rendimentos provenientes de actividades exclusivamente de explorações agrícolas, aquícolas, apícolas, avícolas, pecuárias, piscatórias e silvícolas, excepto a exploração da madeira, aplica-se a taxa única de 10%. 3. Tratando-se de rendimentos provenientes de actividades do sector bancário e de seguros, operadoras de telecomunicações e de empresas petrolíferas angolanas ... aplica-se a taxa única de 35%." Lei n.º 27/22 amends only art. 73 (simplified regime); OGE 2025 (Lei 18/24) art. 21 changes the base (revaluations), not the rate.

Lei n.º 26/20, art. 64.º n.º 6: "A taxa de tributação liberatória incidente sobre serviços acidentais prestados por entidades sem sede, domicílio, estabelecimento estável ou local de direcção efectiva em Angola é de 15%." DLP n.º 2/14, art. 27.º (Taxas do imposto): "1. A taxa de imposto para os rendimentos previstos no n.º 1 do artigo 3.º é de 15%. 2. A taxa de imposto para os rendimentos previstos no n.º 1 do artigo 9.º é de 10%, salvo quando se trate dos rendimentos a que se referem as alíneas e), o) e p), casos em que a taxa é de 15%. 3. A taxa de imposto é de 5%: ... b) No caso de rendimentos referidos na alínea a) do n.º 1 do artigo 9.º, quando as participações sociais ... se encontrem admitidas à negociação em mercado regulamentado"; art. 3 n.º 1 a): "Os juros dos capitais mutuados"; art. 9 n.º 1 a) "Os lucros ... atribuídos aos sócios ou accionistas", i) "Royalties".
-/

namespace AoGlobal
open TaxKernel TaxKernel.Global

def citR : CorpRegime :=
  { name := "Imposto Industrial", sched := Schedule.flat 2500, lossFull := -1, lossExcessBp := 10000 }

def minT : R4.MinTax := { bp := 0, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citR minT { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1 == 2500249
#guard R4.corpTax citR minT { profit := 0, turnover := 1000000000, lossesForward := 0 } 1 == 0
#guard R4.corpTax citR minT { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1 == 0
#guard R4.corpTax citR minT { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1 == 250000
def citS0 : CorpRegime :=
  { name := "Imposto Industrial", sched := Schedule.flat 3500, lossFull := -1, lossExcessBp := 10000 }

def minS0 : R4.MinTax := { bp := 0, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citS0 minS0 { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1 == 3500349
#guard R4.corpTax citS0 minS0 { profit := 0, turnover := 1000000000, lossesForward := 0 } 1 == 0
#guard R4.corpTax citS0 minS0 { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1 == 0
#guard R4.corpTax citS0 minS0 { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1 == 350000
def citS1 : CorpRegime :=
  { name := "Imposto Industrial", sched := Schedule.flat 1000, lossFull := -1, lossExcessBp := 10000 }

def minS1 : R4.MinTax := { bp := 0, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citS1 minS1 { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1 == 1000099
#guard R4.corpTax citS1 minS1 { profit := 0, turnover := 1000000000, lossesForward := 0 } 1 == 0
#guard R4.corpTax citS1 minS1 { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1 == 0
#guard R4.corpTax citS1 minS1 { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1 == 100000
/-- CIT by `company.sector` (kernel 2.5.0 `SectorCorp`): a company whose sector is given and in none of the rules is under the
general rule; an absent sector: `general` (declared here). -/
def citSec : SectorCorp :=
  { general := { regime := citR }, statute := "Código do Imposto Industrial (Lei n.º 19/14) art. 64 n.º 1 as amended by Lei n.º 26/20 de 20 de Julho (25 %); n.º 2 farming 10 %, n.º 3 banking, insurance, telecoms and Angolan oil companies 35 %", ifAbsent := .general,
    bySector := [{ sectors := ["bank", "insurer", "telecom", "petroleum"], rule := { regime := citS0 }, statute := "CII art. 64 n.º 3 (Lei n.º 26/20): banking and insurance, telecoms operators and Angolan oil companies 35 %" },
      { sectors := ["agriculture", "aquaculture", "fishing", "forestry"], rule := { regime := citS1 }, statute := "CII art. 64 n.º 2 (Lei n.º 26/20): income exclusively from farming, aquaculture, beekeeping, poultry, livestock, fishing and forestry (not timber) 10 %" }] }

/-- The minimum tax that goes with the rule `citSec.pick` chose (the rules are told apart by their provision). -/
def citMinFor (st : String) : R4.MinTax :=
  if st == "CII art. 64 n.º 3 (Lei n.º 26/20): banking and insurance, telecoms operators and Angolan oil companies 35 %" then minS0 else if st == "CII art. 64 n.º 2 (Lei n.º 26/20): income exclusively from farming, aquaculture, beekeeping, poultry, livestock, fishing and forestry (not timber) 10 %" then minS1 else minT

def citSecCharges (g : CanonGlobal) : List Charge :=
  match citSec.pick g with
  | some (r, st) => [R4.citCharge r.regime (citMinFor st) g.company st (step := 1)]
  | none => []
def citSecT0 : CanonGlobal :=
  match Lean.Json.parse "{\"id\": \"s18-ao-bank\", \"schema\": \"global/2.0\", \"entity\": \"company\", \"company\": {\"turnover\": 10000000, \"profit\": 1000000, \"lossesForward\": 0, \"sector\": \"bank\"}}" with
  | .ok j => (match parseGlobal j with | .ok g => g | .error _ => default)
  | .error _ => default
#guard ((citSecCharges citSecT0).map (·.due)) == [350000]
def citSecT1 : CanonGlobal :=
  match Lean.Json.parse "{\"id\": \"s18-ao-agri\", \"schema\": \"global/2.0\", \"entity\": \"company\", \"company\": {\"turnover\": 10000000, \"profit\": 1000000, \"lossesForward\": 0, \"sector\": \"agriculture\"}}" with
  | .ok j => (match parseGlobal j with | .ok g => g | .error _ => default)
  | .error _ => default
#guard ((citSecCharges citSecT1).map (·.due)) == [100000]
def citSecT2 : CanonGlobal :=
  match Lean.Json.parse "{\"id\": \"s18-ao-mfg\", \"schema\": \"global/2.0\", \"entity\": \"company\", \"company\": {\"turnover\": 10000000, \"profit\": 1000000, \"lossesForward\": 0, \"sector\": \"manufacturing\"}}" with
  | .ok j => (match parseGlobal j with | .ok g => g | .error _ => default)
  | .error _ => default
#guard ((citSecCharges citSecT2).map (·.due)) == [250000]
def citSecT3 : CanonGlobal :=
  match Lean.Json.parse "{\"id\": \"s18-ao-none\", \"schema\": \"global/2.0\", \"entity\": \"company\", \"company\": {\"turnover\": 10000000, \"profit\": 1000000, \"lossesForward\": 0}}" with
  | .ok j => (match parseGlobal j with | .ok g => g | .error _ => default)
  | .error _ => default
#guard ((citSecCharges citSecT3).map (·.due)) == [250000]
def whtR : Wht :=
  { name := "Retenções sobre pagamentos a não residentes (Imposto Industrial e IAC)",
    rules := [{ kind := .services, rateBp := 1500, statute := "CII art. 64 n.º 6 (Lei 26/20): 15 % liberatory" },
              { kind := .dividend, rateBp := 1000, statute := "IAC art. 27 n.º 2, art. 9 n.º 1 a) (10 %)" },
              { kind := .royalty, rateBp := 1000, statute := "IAC art. 27 n.º 2, art. 9 n.º 1 i) (10 %)" },
              { kind := .interest, rateBp := 1500, statute := "IAC art. 27 n.º 1, art. 3 n.º 1 a) loan interest (15 %)" }] }
#guard whtR.amount { kind := .services, amount := 1000000 } == 150000
#guard whtR.amount { kind := .dividend, amount := 1000000 } == 100000
#guard whtR.amount { kind := .royalty, amount := 1000000 } == 100000
#guard whtR.amount { kind := .interest, amount := 1000000 } == 150000
def corporate : Family :=
  { name := "1200 Imposto Industrial", covers := [.cit],
    run := fun _ g _ => if g.entity != .company then [] else citSecCharges g ++ whtR.charges g.company }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["the 6,5 % provisional withholding on services (art. 67, credited against the final tax) is not modelled", "rates by company.sector (art. 64 n.º 2-3): 'agriculture' (also 'aquaculture', 'fishing', 'forestry'; income exclusively from those activities, not timber) 10 %; 'bank', 'insurer', 'telecom', 'petroleum' 35 %; another sector 25 %; no sector given: 25 % (declared by the model; the charge says so)", "deposit interest (art. 9 n.º 1 j) is taxed at 10 % and listed-share dividends at 5 % (art. 27 n.º 3); the payments-abroad line is taken as loan interest and unlisted dividends", "OGE 2026 (Lei 14/25) revokes art. 27 n.º 3 and sets a 10 % rate from 2026 (not in force in 2025)"] ++ citSec.notes "Imposto Industrial" g ++ citSec.unknown "Imposto Industrial" g

end AoGlobal
