import TjGlobal.Pit

/-!
# Tajikistan 2025: VAT (5111); excises (5121) not modelled (rates set by the Government)

Source: Tax Code of the Republic of Tajikistan (2021) as amended to 14.05.2025, official English and Tajik texts on
the build server (`cmp20/world/B05-former-ussr/tj/law/tc_en_20250514.txt`, `tc_tj_20250514.txt`; sha256 in `law/SOURCES.tsv`).
* **art. 264 (1)**: "1) standard rate - 15 percent; 2) reduced rate … construction works, hotel services and catering
  services - 7 percent and sale of agricultural products of domestic production …, training services and … medical
  services in sanatoriums and resorts … - 5 percent; 3) zero rate".
* **art. 245 (1)**: a VAT payer is "a person whose total income for a period not exceeding 12 full consecutive
  calendar months exceeds 1.0 million somoni".
* **art. 397 (4)** (transitional provisions): "Rates of value added tax established by paragraph 1) of part 1 of
  Article 264 of this Code for taxable operations and taxable importation shall be established from January 1, 2024 to
  December 31, 2026 - 14 percent and from January 1, 2027 - 13 percent": the 2025 standard rate is 14 % (FT review
  2026-11-21; the model had 15 %).
* **art. 251 (2)** exempt: 1) the sale or lease of real property (newly built dwellings, hotels and business premises
  excepted: residential rent is exempt); 2) financial services; 5) medical services of state institutions; 6)
  education by budget-financed institutions.
* **art. 285 (1)**: excise rates "shall be established by the Government"; (4) electric communication 7 % (not
  modelled: the base excludes VAT).
-/

namespace TjGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Андози арзиши иловашуда (НДС)", standard := 1400, reduced := 700, reduced2 := 500,
    threshold := 1000000,
    classOf := fun gd => match gd with
      | .restaurants | .hotels => .reduced
      | .rent | .financial | .health | .education => .exempt
      | _ => .standard }

def vatStatute : String := "Tax Code art. 264 (1), art. 397 (4) (14 % in 2024-2026; 7 % hotels and catering), art. 245 (1) (1.0 million somoni), art. 251 (2) 1), 2), 5), 6)"

def families : List Family :=
  [{ name := "5111 VAT", covers := [.vat],
     run := fun _ g _ =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else []) }]

def absent : List Absent := []
def notes : List String := ["TJ 5111: Tax Code as amended to 14.05.2025"]

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .spirits || s.good == .wine || s.good == .beer || s.good == .cigarettes
      || s.good == .tobaccoOther || s.good == .petrol || s.good == .diesel || s.good == .communication) then
    ["excise (art. 285): rates are set by Government resolution, not read; telecom excise 7 % not modelled"] else [])
  ++ (if g.consumption.any (fun s => s.good == .health || s.good == .education) then
    ["art. 251 (2) 5)-6): health and education taken as supplied by state/budget institutions (exempt)"] else [])

-- art. 397 (4): 14 % from 2024-01-01 to 2026-12-31
#guard vat.embedded { good := .food, amount := 11400 } == 1400
#guard vat.embedded { good := .restaurants, amount := 10700 } == 700
#guard vat.net { turnover := 1000000, sales := [{ good := .other, net := 1000000 }] } == 0
#guard vat.net { turnover := 1000001, sales := [{ good := .other, net := 1000001 }] } == 140000

end TjGlobal.Consumption
