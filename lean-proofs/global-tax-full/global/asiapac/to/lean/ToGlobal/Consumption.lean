import ToGlobal.Pit

/-!
# Tonga 2025: consumption tax (5111); excise not modelled

Source: Consumption Tax Act 2003 (Act 29 of 2003), bilingual text published by the Ministry of Revenue and Customs
(`revenue.gov.to/sites/default/files/inline-files/ConsumptionTaxAct2003.pdf`, fetched 2026-11-21;
`to/law/to_consumption_tax_act2003.pdf`, sha256 in `SHA256SUMS`).
* **s. 5 (3) (a)**: "The rate of Consumption Tax shall be 15% provided that Chief Commissioner with the consent of Privy
  Council may by Order direct what shall be an exempt import, exempt supply or a zero rated supply".
* **s. 6 (1)**: registration where taxable supplies in a 12 month period "will be $100,000 or more" / "is $100,000 or
  more" (liable from 100 000 pa'anga: kernel threshold 99 999, "at or below which a business is not liable").
* The Ministry's page "Consumption Tax Overview" (fetched 2026-11-21): CT "at the rate of 15% with effect from 1st April
  2005".
Exempt and zero-rated supplies are fixed by Orders under s. 5 (3) (a), which were not read: every basket good is taxed at
15 % (flagged). Grade B: the Act text is not a dated 2025 consolidation.
-/

namespace ToGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Consumption Tax", standard := 1500, threshold := 99999,
    classOf := fun gd => match gd with
      | _ => .standard }

def vatStatute : String := "Consumption Tax Act 2003 s. 5 (3) (a) (15 %), s. 6 (1) ($100,000 or more)"

def families : List Family :=
  [{ name := "5111 Consumption Tax", covers := [.vat],
     run := fun _ g _ =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else []) }]

def absent : List Absent :=
  []

def notes : List String := ["TO 5111: Consumption Tax Act 2003 s. 5 (3) (a), s. 6 (1)"]

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if !g.consumption.isEmpty then ["Consumption Tax exempt and zero-rated supplies are set by Orders under s. 5 (3) (a) (not read): every good taxed at 15 %"] else [])
  ++ (if g.consumption.any (fun s => s.good == .spirits || s.good == .wine || s.good == .beer || s.good == .cigarettes || s.good == .tobaccoOther || s.good == .petrol || s.good == .diesel) then ["excise (Excise Tax Act 2008 and amendment orders to 2017) not modelled: later orders not reached"] else [])

#guard vat.embedded { good := .food, amount := 1150 } == 150
#guard vat.net { turnover := 99999, sales := [{ good := .other, net := 99999 }] } == 0
#guard vat.net { turnover := 100000, sales := [{ good := .other, net := 100000 }] } == 15000

end ToGlobal.Consumption
