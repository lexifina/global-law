import TaxKernel.Global
import R5Common

/-!
# Palestine 2025: value added tax (5111)

Decree-Law No 26 of 2024 on Value Added Tax (قرار بقانون رقم (26) لسنة 2024م بشأن ضريبة القيمة المضافة), Official
Gazette (الوقائع الفلسطينية) special issue 30 of 31/12/2024 p. 29; PDF from Maqam (`law/ps_vat_dl26_2024.pdf`, text layer):
* art. 2(1): "تفرض الضريبة بنسبة (%16) على كافة الصفقات التي تعقد في الدولة وعلى استيراد البضائع"; (2) the Council of
  Ministers may lower it or set different rates (not above 16 %).
* art. 3: financial institutions pay the tax on their profits and wages (no VAT on their supplies to consumers).
* art. 32 (zero rate): exports, services to non-residents, foreign tourists' hotel stays, travel tickets abroad,
  unprocessed plant products (para. 8), …
* art. 33 (exempt): real-estate lease for housing or business (except hotel and recreational stays); students' fees of
  kindergartens, private schools, universities and institutes; a doctor's consultation in a private clinic within the
  official tariff; sale of apartments and shops; raw stone; diamonds and precious stones.
* art. 124: in force six months after publication, i.e. from 30/6/2025; art. 123 repeals the Law of fees on local
  products 16/1963 (the former VAT basis). Decree-Law 11/2026 (OG 239 of 25/06/2026) is administrative and later.
Basket classes: rent, education, financial, insurance exempt; every other good 16 % (food: only unprocessed plant
products are zero-rated; health: only clinic consultations exempt).
**Grade B**: the 16 % and the classes are DL 26/2024's (A for 30/6-31/12/2025); for 1/1-29/6/2025 the former regime
applied, taken at the same 16 % (its rate decision not read).
-/

namespace PsGlobal
open TaxKernel TaxKernel.Global R5Common

def vat : Vat :=
  { name := "ضريبة القيمة المضافة", standard := 1600,
    classOf := fun g => match g with
      | .rent | .education | .financial | .insurance => .exempt
      | _ => .standard }

def consumption : Family :=
  { name := "5111 ضريبة القيمة المضافة", covers := [.vat],
    run := fun _ g _ =>
      (if g.consumption.isEmpty then [] else
        [vat.basketCharge g.consumption "Decree-Law 26/2024 art. 2(1) (16 %), art. 3, 32, 33 (in force 30/6/2025; same rate taken before)"])
      ++ (if g.entity == .company && !g.company.sales.isEmpty then
        [vat.businessCharge g.company "Decree-Law 26/2024 art. 2(1) (16 %); input tax deduction art. 36"] else []) }

def consumptionUnsupported (g : CanonGlobal) : List String :=
  ["VAT 1/1-29/6/2025: the former regime (Law 16/1963 as amended) taken at the same 16 % with DL 26/2024's exemptions"]
  ++ (if g.consumption.any (·.good == .food) then
    ["VAT: food taken at 16 %; unprocessed plant products are zero-rated (DL 26/2024 art. 32(8))"] else [])
  ++ (if g.consumption.any (·.good == .health) then
    ["VAT: health taken at 16 %; a doctor's consultation in a private clinic within the official tariff is exempt (art. 33(8))"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .tobaccoOther
        || s.good == .beer || s.good == .wine || s.good == .spirits) then
    ["purchase tax and fuel excise (Paris Protocol, Israeli rates) not modelled"] else [])

#guard vat.embedded { good := .clothing, amount := 11600 } == 1600
#guard vat.embedded { good := .rent, amount := 5000 } == 0

end PsGlobal
