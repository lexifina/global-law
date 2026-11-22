import VuGlobal.Pit

/-!
# Vanuatu 2025: Value Added Tax (5111); excise not modelled

Source: Value Added Tax Act [CAP 247], consolidated edition 2020 (Department of Customs and Inland Revenue,
vanuatucustoms.gov.vu; `cmp20/global/registry/ap_work/law/vu_vat_cap247_consol2020.txt`, sha256 in `law/SOURCES.tsv`).
The later amending Act No. 13 of 2021 was not read; no 2025 rate change was found (a 2025 Statute Law
(Miscellaneous Provisions) Bill changes record keeping only).
* **s. 11 (1)**: "The rate of value added tax will be 15 % of – (a) except in the case of importation, the value of
  the supply".
* **s. 12 (1) (a)**: registration when supplies in the year have "exceeded four million vatu".
* **Schedule 1** exempt supplies: 1. financial services; 3. "the supply of accommodation in a residential dwelling by
  way of hire"; 6. education by an educational institution.
-/

namespace VuGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Value Added Tax", standard := 1500, threshold := 4000000,
    classOf := fun gd => match gd with
      | .financial | .rent | .education => .exempt
      | _ => .standard }

def vatStatute : String := "VAT Act Cap 247 s. 11 (1) (15 %), s. 12 (1) (a) (VT 4 000 000), Sch. 1 items 1, 3, 6"

def families : List Family :=
  [{ name := "5111 VAT", covers := [.vat],
     run := fun _ g _ =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else []) }]

def absent : List Absent :=
  []

def notes : List String := ["VU 5111: VAT Act Cap 247 (consolidation 2020)"]

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .spirits || s.good == .wine || s.good == .beer || s.good == .cigarettes || s.good == .tobaccoOther || s.good == .petrol || s.good == .diesel) then ["excise (Excise Act [CAP 91] and its schedule): not on the build server, not modelled"] else [])
  ++ (if g.consumption.any (fun s => s.good == .insurance) then ["insurance: whether it is a Schedule 1 financial service was not read (standard rate)"] else [])

#guard vat.embedded { good := .food, amount := 11500 } == 1500
#guard vat.embedded { good := .rent, amount := 11500 } == 0
#guard vat.net { turnover := 4000000, sales := [{ good := .other, net := 4000000 }] } == 0
#guard vat.net { turnover := 4000001, sales := [{ good := .other, net := 4000001 }] } == 600000

end VuGlobal.Consumption
