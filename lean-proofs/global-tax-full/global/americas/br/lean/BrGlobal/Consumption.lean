import BrGlobal.Pit

/-!
# Brazil 2025 (São Paulo state and city): ICMS, PIS/COFINS (5111), ISS (5112) at model level; IPI, fuel ICMS (5121) unsupported

Sources (`br/law/`, ARCHIVE_INDEX.tsv): **Lei SP 6.374/1989** (ICMS), Assembleia Legislativa consolidation with every
amendment note (latest seen Lei 17.784 of 02/10/2023); **Lei 10.637/2002** (PIS) and **Lei 10.833/2003** (COFINS),
Planalto pages archived 2025-07-02; **Lei municipal SP 13.701/2003** (ISS), Prefeitura consolidation.
* ICMS art. 34 I: "18% (dezoito por cento), nas operações ou prestações internas" (Lei 13.230/2008); § 1° 1 and § 5°:
  25 % for "bebidas alcoólicas classificadas nas posições 22.04, 22.05 e 22.08" (wine, spirits; not beer, 22.03);
  § 5° 2 (tobacco) "Revogado"; § 1° 2: 12 % "nas prestações de serviços de transporte"; the 25 % on residential
  electricity above 200 kWh and on communication was "Declarada inconstitucional … pelo Supremo Tribunal Federal": 18 %.
  ICMS is inside its own base: the ICMS in a consumer amount is the rate × the amount.
* PIS 1,65 % (Lei 10.637 art. 2°) and COFINS 7,6 % (Lei 10.833 art. 2°) on revenue (the non-cumulative regime), the
  base net of ICMS (STF, RE 574.706): 9,25 % × (amount − ICMS).
* ISS SP art. 16: 2 % for health (list items 4, 5) and education (8.01, except higher education); 5 % otherwise.
* Not modelled (unsupported): ICMS on fuels (monophasic ad rem amounts of LC 192/2022 and the ICMS agreements), the
  RICMS reductions for food (decree), PIS/COFINS zero rates (Lei 10.925 basic foods, books, medicines' single-phase
  regime) beyond books, IPI (TIPI decree), and the 2026 CBS/IBS transition (not in force in 2025).

**Pass 10 (2026-11-21), 5121:** IPI on cigarettes: Decreto 12.127/2024 (Planalto, Wayback capture 2026-01-10, `br/law/d12127_wb.*`) amends RIPI art. 212-B § 1: from 1/11/2024 ad valorem 66,70 % and R$ 2,25 per maço and per box; Decreto 7.555/2011 (Wayback 2025-12-22, `br/law/d7555_wb.*`) art. 4 § 1: valor tributável = 15 % of the retail price, art. 5 § 1 I: the special regime's ad valorem part uses that base. CIDE-combustíveis: Decreto 5.060/2004 (Wayback 2025-12-21, `br/law/d5060_wb.*`) art. 1 I R$ 100,00 per m³ of gasolines (Decreto 8.395/2015), parágrafo único VII diesel at zero (Decreto 9.391/2018). Grade A. IPI on drinks (TIPI) stays C.

## Pass 11 (2026-11-21): IPI on drinks and other tobacco (TIPI)

RFB consolidated TIPI (Decreto 11.158/2022 and updates to ADE RFB 5/2026; `br/law/tipi_rfb.txt`): chapter 22 rows
2202 2,6 %, 2203 cerveja 3,9 %, 2204 vinhos 6,5 %, 2208 destilados 19,5 % (cachaça 16,25 %); chapter 24 cigars,
smoking tobacco, heated tobacco 30 %. No update note in chapters 22 and 24 after 2022, so these are the 2025 rates.
Grade B (official consolidated table, not the decree text). The IPI is levied on the producer's valor da operação
(not an input): the price paid is read as that value plus the IPI, an upper bound.
-/

namespace BrGlobal.Consumption
open TaxKernel TaxKernel.Global AmerCommon BrGlobal

/-- ICMS-SP rate in the consumer price, bp (0: not an ICMS good or not modelled). -/
def icmsRate (g : Good) : Int :=
  match g with
  | .wine | .spirits => 2500
  | .transport => 1200
  | .petrol | .diesel | .gas | .heatingOil => 0
  | .education | .health | .hotels | .recreation | .financial | .insurance | .rent | .water => 0
  | _ => 1800

/-- ISS-SP rate, bp (services of the municipal list). -/
def issRate (g : Good) : Int :=
  match g with
  | .health | .education => 200
  | .hotels | .recreation => 500
  | _ => 0

/-- PIS/COFINS apply (non-cumulative 9,25 %) except where the model has no rule or a zero rate is read. -/
def pisCofinsApplies (g : Good) : Bool :=
  match g with
  | .books | .newspapers | .rent | .financial | .insurance | .medicines | .petrol | .diesel | .gas => false
  | _ => true

def icms (s : Spend) : Int := divR .down (icmsRate s.good * pos s.amount) BP
def iss (s : Spend) : Int := divR .down (issRate s.good * pos s.amount) BP
def pisCofins (s : Spend) : Int := if pisCofinsApplies s.good then divR .down (925 * pos (s.amount - icms s)) BP else 0

def basketTotal (f : Spend → Int) (sp : List Spend) : Int := isum (sp.map f)

def fams : Family :=
  { name := "5111/5112 ICMS, PIS/COFINS, ISS", covers := [.vat, .salesTax],
    run := fun _ g _ =>
      if g.consumption.isEmpty then [] else
      let tot := isum (g.consumption.map (·.amount))
      [charge .vat "ICMS (São Paulo)" tot id (fun _ => basketTotal icms g.consumption) (event := "basket") (level := .state)
         (bearer := .consumer) (statute := "Lei SP 6.374/1989 art. 34 I (18 %), § 1° 1-2, § 5° (25 %, 12 %)"),
       charge .vat "PIS/COFINS (não cumulativo)" tot id (fun _ => basketTotal pisCofins g.consumption) (event := "basket")
         (bearer := .consumer) (statute := "Lei 10.637/2002 art. 2° (1,65 %), Lei 10.833/2003 art. 2° (7,6 %); base net of ICMS"),
       charge .salesTax "ISS (São Paulo)" tot id (fun _ => basketTotal iss g.consumption) (event := "basket") (level := .local)
         (bearer := .consumer) (statute := "Lei municipal SP 13.701/2003 art. 16 (2 %, 5 %)")] }

/-! Pass 10: IPI on cigarettes (special regime) and CIDE-combustíveis. -/
/-- RIPI art. 212-B (Decreto 12.127/2024): 66,70 % of the valor tributável (15 % of the retail price, Decreto 7.555 art. 4 § 1)
plus R$ 2,25 per pack of 20 (R$ 0,1125 per stick): (q × 22.500 + 20.010.000 × price) / 200.000.000, q in thousandths of a stick. -/
def ipiCigarros (s : Spend) : Int := divR .down (s.quantity * 22500 + 20010000 * pos s.amount) 200000000

/-- Decreto 5.060/2004 art. 1: R$ 100 per m³ of gasoline (q thousandths of a litre: q × 100 / 10⁶); diesel reduced to zero. -/
def cide (s : Spend) : Int := if s.good == .petrol then divR .down (s.quantity * 100) 1000000 else 0

/-- TIPI rate (bp) of a drink or other tobacco product. -/
def ipiRate (g : Good) : Int :=
  match g with
  | .nonAlcoholic => 260 | .beer => 390 | .wine => 650 | .spirits => 1950 | .tobaccoOther => 3000 | _ => 0

/-- IPI is charged on top of the valor da operação (RIPI art. 189): the price paid is read as that value plus the IPI,
so the IPI is `amount × r / (1 + r)` (an upper bound: ICMS, PIS/COFINS and the distribution margin inside the
retail price are not removed). -/
def ipiDrink (s : Spend) : Int := divR .down (pos s.amount * ipiRate s.good) (10000 + ipiRate s.good)

def exciseF : Family :=
  { name := "5121 IPI (cigarros, bebidas, demais tabacos), CIDE-combustíveis", covers := [.excise],
    run := fun _ g _ => g.consumption.filterMap fun s =>
      if s.good == .cigarettes then
        some (charge .excise "IPI (cigarros, regime especial)" s.amount id (fun _ => ipiCigarros s) (event := s.good.name)
          (bearer := .consumer) (statute := "IPI cigarros, regime especial: Decreto 7.212/2010 (RIPI) art. 212-B § 1 as amended by Decreto 12.127/2024 (from 1 Nov 2024: 66,70 % + R$ 2,25 per maço or box); Decreto 7.555/2011 arts. 4 § 1 and 5 § 1 I: the ad valorem rate applies to 15 % of the retail price"))
      else if ipiRate s.good != 0 then
        some (charge .excise "IPI (bebidas, demais produtos do tabaco: TIPI)" s.amount id (fun _ => ipiDrink s) (event := s.good.name)
          (bearer := .consumer) (statute := "TIPI (Decreto 11.158/2022), RFB consolidated table updated to ADE RFB 5/2026 (no chapter 22 or 24 change noted after 2022): 2202.10.00 / 2202.99.00 2,6 %; 2203.00.00 cervejas de malte 3,9 %; 2204 vinhos 6,5 % (2205 vermutes 9,75 %); 2208.20-2208.90 aguardentes, uísques, gim, vodca, licores 19,5 % (2208.40.00 cachaça 16,25 %); 2402.10, 2403.19, 2404.11 30 %"))
      else if s.good == .petrol || s.good == .diesel then
        some (charge .excise "CIDE-combustíveis" s.quantity id (fun _ => cide s) (event := s.good.name)
          (bearer := .consumer) (statute := "CIDE-combustíveis: Lei 10.336/2001 art. 5; Decreto 5.060/2004 art. 1 I (R$ 100,00 per m³ of gasoline, Decreto 8.395/2015) and parágrafo único VII (diesel reduced to zero, Decreto 9.391/2018)"))
      else none }

def families : List Family := [fams, exciseF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.consumption.any fun s => s.good == .food || s.good == .medicines || s.good == .restaurants) "ICMS reductions for food and meals (RICMS, decree) and PIS/COFINS zero rates for basic foods (Lei 10.925) not read: food at 18 % ICMS and 9,25 % PIS/COFINS"
  ++ when (g.entity == .company) "company supplies: ICMS/IPI/PIS/COFINS/ISS on a company's sales not modelled"
  ++ when (g.consumption.any fun s => s.good == .petrol || s.good == .diesel || s.good == .gas) "fuels: ICMS monophasic ad rem (LC 192/2022, ICMS agreements) and PIS/COFINS per litre not read: not charged; CIDE charged (gasoline R$ 100/m³, diesel zero)"
  ++ when (g.consumption.any fun s => s.good == .cigarettes) "IPI on cigarettes: the special regime (art. 212-B) is taken as chosen (the general regime is 300 % of 15 % of the retail price); the price paid is taken as the retail price of the pack; a line without quantity pays no specific part"
  ++ when (g.consumption.any fun s => s.good == .beer || s.good == .wine || s.good == .spirits || s.good == .nonAlcoholic || s.good == .tobaccoOther) "IPI on drinks and other tobacco: the TIPI rate on the price paid net of the IPI (upper bound: the valor da operação is the producer's price); spirits at 19,5 % (cachaça 2208.40.00: 16,25 %), wine 6,5 % (vermouth 9,75 %), non-alcoholic drinks 2,6 % (non-alcoholic beer 3,9 %; soy and nectar drinks 0); mineral water NT"

#guard icms { good := .clothing, amount := 1000 } == 180
#guard icms { good := .spirits, amount := 1000 } == 250
#guard pisCofins { good := .clothing, amount := 1000 } == 75
#guard iss { good := .education, amount := 1000 } == 20
-- 1.000 packs at R$ 10: 2.250 specific + 66,70 % × 15 % × 10.000 = 1.000,5
#guard ipiCigarros { good := .cigarettes, amount := 10000, quantity := 20000000 } == 3250
-- 1.000 litres of gasoline: R$ 100; diesel: zero
#guard cide { good := .petrol, amount := 6000, quantity := 1000000 } == 100
#guard cide { good := .diesel, amount := 6000, quantity := 1000000 } == 0
-- TIPI: R$ 10,39 of beer = 10,00 + 3,9 % IPI; 119,50 of spirits = 100 + 19,5 %; 13,00 of cigars = 10 + 30 %
#guard ipiDrink { good := .beer, amount := 1039 } == 39
#guard ipiDrink { good := .spirits, amount := 11950 } == 1950
#guard ipiDrink { good := .tobaccoOther, amount := 1300 } == 300
#guard ipiDrink { good := .wine, amount := 1065 } == 65
#guard ipiDrink { good := .nonAlcoholic, amount := 1026 } == 26
#guard ipiDrink { good := .food, amount := 1000 } == 0

end BrGlobal.Consumption
