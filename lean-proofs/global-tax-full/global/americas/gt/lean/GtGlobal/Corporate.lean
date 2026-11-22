import GtGlobal.Pit

/-!
# Guatemala 2025: ISR régimen sobre las utilidades (1200)

Source: Decreto 10-2012, Ley de Actualización Tributaria (`world/.../gt/src/d10_2012.txt`): grade B (amendments not
checked).
* **art. 36**: "a la base imponible determinada el tipo impositivo del veinticinco por ciento (25%)". The optional
  simplified regime on gross income (art. 44: 5 % / 7 %) and the non-resident withholdings (Título V) not read.

**Pass 8 (2026-11-21), withholding on payments abroad:** Ley de Actualización Tributaria (Decreto 10-2012) Libro I Título V, Rentas de no residentes: art. 103 the base is the amount paid or credited; art. 104: 5 % on dividends and profit distributions (num. 1 e.), 10 % on interest (num. 2 a.), 15 % on royalties, fees and scientific, economic, technical or financial advice (num. 3 c.-e.), 25 % on other income (num. 4); art. 105: whoever pays withholds, final. Grade A (text with the Decreto 19-2013 changes; later Decretos not checked).
-/

namespace GtGlobal.Corporate
open TaxKernel TaxKernel.Global AmerCommon GtGlobal

def regime : CorpRegime :=
  { name := "Impuesto sobre la renta (régimen sobre las utilidades)", sched := Schedule.flat 2500 }

def citStatute : String := "Decreto 10-2012 art. 36 (25 %)"

def wht : Wht :=
  { name := "Withholding tax (non-residents)", rules := [{ kind := .dividend, rateBp := 500, statute := "Decreto 10-2012 Libro I Título V art. 104 num. 1 e.: dividendos, reparto de utilidades 5 %" }, { kind := .interest, rateBp := 1000, statute := "Decreto 10-2012 Libro I Título V art. 104 num. 2 a.: intereses pagados o acreditados a no residentes 10 %" }, { kind := .royalty, rateBp := 1500, statute := "Decreto 10-2012 Libro I Título V art. 104 num. 3 c.: regalías 15 %" }, { kind := .services, rateBp := 1500, statute := "Decreto 10-2012 Libro I Título V art. 104 num. 3 d., e.: honorarios; asesoramiento científico, económico, técnico o financiero 15 %" }] }

def citF : Family := corpFamily "1200 Impuesto sobre la renta (régimen sobre las utilidades)" (fun _ => regime) (fun _ => citStatute) wht (fun _ => [])

def families : List Family := [citF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.entity == .company) "losses brought forward, interest limitation and participation exemptions not modelled: taxable profit = profit + add-backs − exempt income"
  ++ when (g.entity == .company) "régimen opcional simplificado (art. 44, % of gross income) not modelled"
  ++ when (g.entity == .company && strField g.raw "regime" != "") "1200 cit: the elected regime named in the entity (\"regime\") is not modelled (grade C for that regime): the model computes the general regime only"
  ++ when (g.entity == .company && !g.company.paymentsAbroad.isEmpty) "Decreto 10-2012 art. 104: the num. 2 a. exception for loans from regulated foreign banks, 3 % for news and films, 5 % for transport, insurance and telecoms, and 25 % on other unspecified income (num. 4) not modelled; services are taken as fees or technical advice (15 %)"

#guard regime.citTax { profit := 1000000 } == 250000
#guard wht.amount { kind := .dividend, amount := 1000000 } == 50000
#guard wht.amount { kind := .interest, amount := 1000000 } == 100000
#guard wht.amount { kind := .royalty, amount := 1000000 } == 150000
#guard wht.amount { kind := .services, amount := 1000000 } == 150000

end GtGlobal.Corporate
