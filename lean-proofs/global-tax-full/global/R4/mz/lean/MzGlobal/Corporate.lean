import R4Common
import TaxKernel.Global2

/-!
# Mozambique 2025: corporate income tax (1200) and withholding (generated from `R4/specs/mz.json`)

No usable 2025 text for these headings: the IRPC law 19/2013 (registry fetch) and AT page dumps are held; the 2025 IRPC/IVA rates were not located. Lei 22/2022 and Lei 19/2022 (Boletim da República, 28-29 Dec 2022) fetched from www.at.gov.mz (`/api/documents?root=LEGISLAÇÃO` lists the library; files via `/api/webdav?path=...`), saved in `cmp20/global/R4/fetch/mz8/` with SHA256SUMS. Pass 9 (IRPC): Lei n.º 34/2007 (Código do IRPC, BR I Série n.º 52) from the AT site's former download (Wayback 2014-2018 captures of www.at.gov.mz/por/content/download/2131/16310, `R4/fetch/mz9/at_lei34_2007_cirpc.pdf`), Lei n.º 4/2012 (Wayback of www.at.gov.mz/eng/content/download/1319/10270, page 5 read on the image), Lei n.º 19/2013 (`registry/afm_data/fetch/MZ/mz_irpc_lei19_2013.pdf`), the Comissão do Plano e Orçamento opinion n.º 09/2022 on the bill that became Lei n.º 20/2022 (parlamento.mz upload via Wayback: amends only art. 61-62 for agriculture, aquaculture and urban transport to 31 Dec 2025), and BR I Série n.º 248 suplemento of 29 Dec 2025 (AT library: Lei n.º 12/2025 lists the amending laws 20/2009, 4/2012, 19/2013, 20/2022 and applies from 1 Jan 2026). SHA256SUMS in `R4/fetch/mz9/`.

Lei n.º 34/2007, art. 61 (Taxa geral): "1. A taxa do IRPC é de 32%, excepto nos casos previstos nos números seguintes." Lei n.º 4/2012 art. 1 restates art. 61 with n.º 1 "..." and n.º 2 "As actividades agrícola e pecuária beneficiam, até 31 de Dezembro de 2015, de uma taxa reduzida de 10%." CPO opinion n.º 09/2022 on the bill that became Lei n.º 20/2022: "A redução da taxa geral de 32% para 10%, para a agricultura, aquacultura e transportes urbanos, a vigorar até 31 de Dezembro de 2025".

Lei n.º 4/2012, art. 62 (Taxa de retenção na fonte): "2. Tratando-se de rendimentos de entidades que não tenham sede nem direcção efectiva em território moçambicano e não possuam estabelecimento estável em Moçambique ao qual os mesmos sejam imputáveis, são tributados por uma taxa liberatória de 20%. 3. São tributados à taxa liberatória de 10% os rendimentos das entidades referidas no número anterior, desde que derivados de: a) prestação de serviços de telecomunicações e transportes internacionais ... 4. Estão também sujeitos a uma taxa liberatória de 10% os títulos cotados na Bolsa de Valores de Moçambique." (Lei 19/2013 keeps n.º 1-2 and recasts n.º 3-4.)
-/

namespace MzGlobal
open TaxKernel TaxKernel.Global

def citR : CorpRegime :=
  { name := "Imposto sobre o Rendimento das Pessoas Colectivas (IRPC)", sched := Schedule.flat 3200, lossFull := -1, lossExcessBp := 10000 }

def minT : R4.MinTax := { bp := 0, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citR minT { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1 == 3200319
#guard R4.corpTax citR minT { profit := 0, turnover := 1000000000, lossesForward := 0 } 1 == 0
#guard R4.corpTax citR minT { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1 == 0
#guard R4.corpTax citR minT { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1 == 320000
def citS0 : CorpRegime :=
  { name := "Imposto sobre o Rendimento das Pessoas Colectivas (IRPC)", sched := Schedule.flat 1000, lossFull := -1, lossExcessBp := 10000 }

def minS0 : R4.MinTax := { bp := 0, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citS0 minS0 { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1 == 1000099
#guard R4.corpTax citS0 minS0 { profit := 0, turnover := 1000000000, lossesForward := 0 } 1 == 0
#guard R4.corpTax citS0 minS0 { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1 == 0
#guard R4.corpTax citS0 minS0 { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1 == 100000
/-- CIT by `company.sector` (kernel 2.5.0 `SectorCorp`): a company whose sector is given and in none of the rules is under the
general rule; an absent sector: `general` (declared here). -/
def citSec : SectorCorp :=
  { general := { regime := citR }, statute := "Código do IRPC (Lei n.º 34/2007 de 31 de Dezembro) art. 61 n.º 1 (32 %); not amended by Lei n.º 4/2012 or 19/2013 (n.º 1 '...'); Lei n.º 20/2022 adds 10 % for agriculture, aquaculture and urban transport to 31 Dec 2025", ifAbsent := .general,
    bySector := [{ sectors := ["agriculture", "aquaculture", "urbanTransport"], rule := { regime := citS0 }, statute := "CIRPC art. 61 as amended by Lei n.º 20/2022 (agriculture, aquaculture and urban transport 10 % to 31 Dec 2025; enacted text not held: CPO opinion n.º 09/2022 on the bill and Lei n.º 12/2025's list of amending laws, B)" }] }

/-- The minimum tax that goes with the rule `citSec.pick` chose (the rules are told apart by their provision). -/
def citMinFor (st : String) : R4.MinTax :=
  if st == "CIRPC art. 61 as amended by Lei n.º 20/2022 (agriculture, aquaculture and urban transport 10 % to 31 Dec 2025; enacted text not held: CPO opinion n.º 09/2022 on the bill and Lei n.º 12/2025's list of amending laws, B)" then minS0 else minT

def citSecCharges (g : CanonGlobal) : List Charge :=
  match citSec.pick g with
  | some (r, st) => [R4.citCharge r.regime (citMinFor st) g.company st (step := 1)]
  | none => []
def citSecT0 : CanonGlobal :=
  match Lean.Json.parse "{\"id\": \"s18-mz-agr\", \"schema\": \"global/2.0\", \"entity\": \"company\", \"company\": {\"turnover\": 10000000, \"profit\": 1000000, \"lossesForward\": 0, \"sector\": \"agriculture\"}}" with
  | .ok j => (match parseGlobal j with | .ok g => g | .error _ => default)
  | .error _ => default
#guard ((citSecCharges citSecT0).map (·.due)) == [100000]
def citSecT1 : CanonGlobal :=
  match Lean.Json.parse "{\"id\": \"s18-mz-none\", \"schema\": \"global/2.0\", \"entity\": \"company\", \"company\": {\"turnover\": 10000000, \"profit\": 1000000, \"lossesForward\": 0}}" with
  | .ok j => (match parseGlobal j with | .ok g => g | .error _ => default)
  | .error _ => default
#guard ((citSecCharges citSecT1).map (·.due)) == [320000]
def whtR : Wht :=
  { name := "Retenção na fonte de IRPC sobre rendimentos de não residentes",
    rules := [{ kind := .services, rateBp := 2000, statute := "CIRPC art. 62 n.º 2 (20 % liberatory)" },
              { kind := .royalty, rateBp := 2000, statute := "CIRPC art. 62 n.º 2 (20 % liberatory)" },
              { kind := .interest, rateBp := 2000, statute := "CIRPC art. 62 n.º 2 (20 % liberatory)" },
              { kind := .dividend, rateBp := 2000, statute := "CIRPC art. 62 n.º 2 (20 % liberatory)" }] }
#guard whtR.amount { kind := .services, amount := 1000000 } == 200000
#guard whtR.amount { kind := .royalty, amount := 1000000 } == 200000
#guard whtR.amount { kind := .interest, amount := 1000000 } == 200000
#guard whtR.amount { kind := .dividend, amount := 1000000 } == 200000
def corporate : Family :=
  { name := "1200 Imposto sobre o Rendimento das Pessoas Colectivas (IRPC)", covers := [.cit],
    run := fun _ g _ => if g.entity != .company then [] else citSecCharges g ++ whtR.charges g.company }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["by company.sector: 'agriculture', 'aquaculture', 'urbanTransport' 10 % (Lei n.º 20/2022, in force to 31 Dec 2025; this rule is B: the enacted text is not held); another sector or none given: 32 % (declared)", "the 35 % autonomous taxation of undocumented charges (art. 61 n.º 4) is not modelled; the pagamento especial por conta is a payment on account (credited), not a minimum tax", "the 10 % rates (telecoms, international transport, rural electrification, vessel charters, listed securities) and the Lei 20/2022 measures to 31 Dec 2025 (10 % on services to agricultural companies, no withholding on foreign loans to agricultural projects) are not modelled"] ++ citSec.notes "Imposto sobre o Rendimento das Pessoas Colectivas (IRPC)" g ++ citSec.unknown "Imposto sobre o Rendimento das Pessoas Colectivas (IRPC)" g

end MzGlobal
