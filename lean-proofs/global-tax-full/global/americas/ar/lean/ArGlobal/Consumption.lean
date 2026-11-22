import ArGlobal.Pit
import TaxKernel.Global2

/-!
# Argentina 2025: IVA (5111); impuestos internos (5121); fuel taxes unsupported

Source: Ley de Impuesto al Valor Agregado, t.o. 1997 (Ley 23.349 and amendments), Infoleg texto actualizado
(`ar/law/iva_23349_texact.htm`, fetched 2026-11-21; its latest amendment notes are Ley 27.743, B.O. 2024: the 2025
wording).
* **art. 28**: "La alícuota del impuesto será del veintiuno por ciento (21%)"; 27 % for gas, electricity and water
  supplied outside homes (not the household basket); "Estarán alcanzados por una alícuota equivalente al cincuenta por
  ciento (50%)": a) live animals, meat, fresh fruit and vegetables, flour, bread (the basket's food line read as these:
  10,5 %, flagged).
* **art. 7** exemptions: a) "Libros, folletos e impresos similares"; f) "El agua ordinaria natural, la leche fluida";
  h) 4) education services; 6), 7) health services by obras sociales and sanitary assistance; 16) financial
  placements and listed interest; 22) "La locación de inmuebles destinados" to housing.
* Impuestos internos (Ley 24.674) and the fuel taxes (Ley 23.966 Título III, amounts updated by decree) were not read
  in a dated text: unsupported.

Pass 6: **Impuesto sobre los Ingresos Brutos, Ciudad Autónoma de Buenos Aires** (5112, level state), Ley Tarifaria para
el año 2025, **Ley 6806** (B.O.C.B.A., promulgated 23 Dec 2024), Anexo Título I (`ar/law/ley6806_tarifaria_2025_anexo.pdf`,
ARCHIVE_INDEX.tsv), rates by activity and by the taxpayer's gross income of the previous year: art. 3 electricity, gas,
water 3,00 % (3,75 % above $1.670.000.000); art. 5 commerce, repairs and other services 3,00 % (5,00 % above
$303.200.000); art. 6 restaurants and hotels 3,00 % (4,50 %); art. 7 transport 2,00 %; art. 8 communications 3,00 %
(4,00 %); art. 9 real estate and rental services 3,00 % (5,00 %); art. 10 social and health services 3,00 % (4,75 %);
art. 11 education, community and personal services 3,00 % (5,00 %); art. 1 primary production 0 %. Grade A.
Model: a company's supplies (net amounts; exports out) at the rate of the activity read from each supply's good, the
band chosen by the year's turnover (the law reads the previous year's); financial and insurance services (arts. 12-14:
5,5-9 %) and manufacturing (art. 2: 1 % on sales to businesses) are not distinguished (taxed as commerce). Households:
the tax is inside consumer prices and is not added to the basket (no statutory incidence on the buyer).

**Pass 10 (2026-11-21): impuestos internos (Ley 24.674, InfoLEG texto actualizado id 38621, fetched 2026-11-21; `ar/law/ley24674_texact.*`).** Art. 15 (as substituted by Ley 27.742 art. 230, B.O. 8 Jul 2024, in force the next day): cigarettes "tributarán sobre el precio de venta al consumidor, inclusive impuestos, excepto el impuesto al valor agregado, un gravamen del setenta y tres por ciento (73%)". Art. 4: other rates on the precio neto de venta, which deducts the IVA débito fiscal (c) but "en ningún caso … el impuesto de esta ley". Art. 16: cigars 20 % (minimum per cigar, IPC-indexed: not applied). Art. 18: smoking tobacco 25 %. Art. 23 (Ley 27.430): whisky, brandy, gin, vodka, rum etc. 26 %; others by strength: 10°-29° and fraction 20 %, 30° and more 26 %; wines excluded. Art. 25: beer 14 % (SME craft 8 %), exempt up to 1,2° GL. Art. 26: non-alcoholic drinks 8 %. Ley 27.802 (B.O. 6 Mar 2026) repeals only the insurance, mobile, luxury and vehicle headings, from 2026. Grade A.
-/

namespace ArGlobal.Consumption
open TaxKernel TaxKernel.Global AmerCommon ArGlobal

def vat : Vat :=
  { name := "Impuesto al Valor Agregado", standard := 2100, reduced := 1050,
    classOf := fun gd => match gd with
      | .food => .reduced
      | .books | .newspapers | .water | .education | .health | .financial | .rent => .exempt
      | _ => .standard }

def vatStatute : String := "Ley de IVA (t.o. 1997) art. 28 (21 %, 10,5 %), art. 7 a), f), h) 4), 6), 7), 16), 22)"

def vatF : Family := vatFamily "Impuesto al Valor Agregado" vat vatStatute .vat .central

/-- CABA Ley Tarifaria 2025 (Ley 6806) Anexo arts. 3-11: rate in bp for a supply of a good, by turnover band. -/
def iibbRate (big : Bool) (bigCommerce : Bool) (gd : Good) : Int :=
  match gd with
  | .restaurants | .hotels => if big then 450 else 300
  | .transport => 200
  | .communication => if big then 400 else 300
  | .rent => if big then 500 else 300
  | .health => if big then 475 else 300
  | .education | .recreation => if big then 500 else 300
  | .electricity | .gas | .water => if big then 375 else 300
  | _ => if bigCommerce then 500 else 300

def iibb (co : Company) : Int :=
  let big := decide (co.turnover > 1670000000)
  let bigC := decide (co.turnover > 303200000)
  isum ((co.sales.filter (fun s => !s.exported)).map fun s => divR .down (iibbRate big bigC s.good * pos s.net) BP)

def iibbF : Family :=
  { name := "5112 impuesto sobre los ingresos brutos (CABA)", covers := [.salesTax],
    run := fun _ g _ =>
      if g.entity != .company || g.company.sales.isEmpty then [] else
      [charge .salesTax "Impuesto sobre los Ingresos Brutos (CABA)" (isum (g.company.sales.map (·.net))) id (fun _ => iibb g.company)
        (event := "sales") (level := .state)
        (statute := "Ley 6806 (Ley Tarifaria CABA 2025) Anexo arts. 3, 5-11: 3 % / 2 % transport / higher rates above $303.200.000 (commerce) or $1.670.000.000")] }

/-! Pass 10: impuestos internos (Ley 24.674). Art. 15: cigarettes 73 % of the consumer price including taxes but
excluding IVA; art. 4: the other rates on the net sale price, which excludes the IVA (c) but never the internal tax
itself: both are a rate on the price net of IVA (`valueBase := .netOfVat`). -/
def intRule (good : Good) (name : String) (bp : Int) (lit : String) (sub : String := "") (lo : Int := -1) (hi : Int := 100000) : ExciseRule :=
  { good, name, sub, adValoremBp := bp, valueBase := .netOfVat, vatBp := 2100, minAbvBp := lo, maxAbvBp := hi,
    statute := "Ley 24.674 (Ley de Impuestos Internos, InfoLEG texto actualizado id 38621) " ++ lit }

def internos : List ExciseRule :=
  [intRule .cigarettes "Impuestos internos (cigarrillos)" 7300 "art. 15 (73 %, Ley 27.742 art. 230, from 9 Jul 2024)",
   intRule .tobaccoOther "Impuestos internos (cigarros y cigarritos)" 2000 "art. 16 (20 %)" (sub := "cigar"),
   intRule .tobaccoOther "Impuestos internos (tabacos para fumar)" 2500 "art. 18 (25 %)",
   intRule .beer "Impuestos internos (cervezas, exentas hasta 1,2° GL)" 0 "art. 25 third para. (exempt up to 1,2° GL)" (lo := 0) (hi := 120),
   intRule .beer "Impuestos internos (cervezas)" 1400 "art. 25 (14 %)",
   intRule .spirits "Impuestos internos (bebidas alcohólicas 1a clase)" 2000 "art. 23 c) (i) (20 %, 10° to 29° GL and fraction)" (lo := 999) (hi := 2999),
   intRule .spirits "Impuestos internos (bebidas alcohólicas)" 2600 "art. 23 a), b), c) (ii) (26 %)",
   intRule .nonAlcoholic "Impuestos internos (bebidas analcohólicas)" 800 "art. 26 (8 %)"]

def internosF : Family := exciseRuleFamily "impuestos internos (Ley 24.674)" internos (firstOnly := true)

def families : List Family := [vatF, iibbF, internosF]

def absent : List Absent :=
  []

def notes : List String := ["Wine pays no impuestos internos: art. 23 classifies drinks of 10° GL or more as alcoholic drinks 'excluidos los vinos', art. 26 excludes wines (Ley 24.674, InfoLEG texto actualizado)."]

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.consumption.any fun s => s.good == .medicines || s.good == .transport || s.good == .insurance) "medicines, passenger transport and insurance: the exemptions / 10,5 % cases for them were not read item by item: taxed at 21 %"
  ++ when (!g.consumption.isEmpty) "food read as the fresh foods, flour and bread of art. 28 a) (10,5 %); other food is at 21 %; IIBB (provincial gross receipts tax) inside prices is not modelled here"
  ++ when (g.entity == .company && !g.company.sales.isEmpty) "ingresos brutos (CABA): activity read from each supply's good (financial 5.5-9 % and manufacturing 1 % not distinguished); band by the year's turnover (the law uses the previous year's); other provinces not modelled"
  ++ when (g.consumption.any fun s => s.good == .petrol || s.good == .diesel) "impuesto a los combustibles líquidos y al dióxido de carbono (Ley 23.966 Título III): 2025 amounts set by decree (deferred updates) not read: not charged"
  ++ when (g.consumption.any fun s => s.good == .cigarettes || s.good == .tobaccoOther || s.good == .beer || s.good == .spirits || s.good == .nonAlcoholic) "impuestos internos: the statutory base is the manufacturer's or importer's net sale (art. 4), read from the consumer price net of IVA (includes the retail margin: upper bound; art. 15 cigarettes are on the consumer price, exact); tobaccoOther is cigars (art. 16, 20 %) only when sub = cigar, otherwise smoking tobacco (art. 18, 25 %); the minimum taxes of art. 16 (cigars, IPC-indexed) and the art. s/n after art. 14 executive rate changes are not applied; craft beer of SMEs (8 %), fruit-juice drinks (4 %/5 %), mineral waters (4 %) and caffeine/taurine drinks (10 %) are not distinguished; spirits without a strength are taxed at 26 %"

#guard vat.embedded { good := .clothing, amount := 1210 } == 210
#guard vat.embedded { good := .food, amount := 1105 } == 105
#guard vat.embedded { good := .books, amount := 1210 } == 0
#guard iibb { turnover := 1000, sales := [{ good := .clothing, net := 1000 }] } == 30
#guard iibb { turnover := 400000000, sales := [{ good := .clothing, net := 400000000 }] } == 20000000
-- a pack at 1.210: 73 % of the 1.000 net of IVA
#guard (internos.head!.dutyOn { good := .cigarettes, amount := 1210, quantity := 20000 } {}) == 730
-- rules selected for beer 12.100 at 5 % vol: only 14 %; at 1 % vol the exemption first (firstOnly charges it alone)
#guard (internos.filter (·.appliesTo 2025 { good := .beer, amount := 12100, abvBp := 500 } {})).map (·.dutyOn { good := .beer, amount := 12100, abvBp := 500 } {}) == [1400]
#guard (internos.filter (·.appliesTo 2025 { good := .beer, amount := 12100, abvBp := 100 } {})).map (·.dutyOn { good := .beer, amount := 12100, abvBp := 100 } {}) == [0, 1400]
-- spirits 12.100: 20 % first at 25 % vol, only 26 % at 40 % vol
#guard (internos.filter (·.appliesTo 2025 { good := .spirits, amount := 12100, abvBp := 2500 } {})).map (·.dutyOn { good := .spirits, amount := 12100, abvBp := 2500 } {}) == [2000, 2600]
#guard (internos.filter (·.appliesTo 2025 { good := .spirits, amount := 12100, abvBp := 4000 } {})).map (·.dutyOn { good := .spirits, amount := 12100, abvBp := 4000 } {}) == [2600]

end ArGlobal.Consumption
