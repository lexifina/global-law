import KiGlobal.Pit

/-!
# Kiribati 2025: value added tax (5111); excise not modelled

Source: Value Added Tax Act 2013 (Kiribati sessional legislation, PacLII; Wayback capture 20250130161400 of
`paclii.org/ki/legis/num_act/vata2013132/`; `ki/law/ki_vat2013_paclii.html`, sha256 in `SHA256SUMS`).
* **s. 7 (3)**: "The rate of VAT is — (a) in the case of a taxable supply that is a zero-rated supply, zero percent; or
  (b) in any other case, 12.5%."
* **s. 8 (2)**: "The registration threshold is $100,000." (registration when taxable supplies in a 12 month period exceed
  it).
* **Second Schedule cl. 1** exempt: (a) financial services; (d), (e) sale or lease of residential premises (other than new
  premises and leases under 2 months); (h) education services; (i) medical, dental or nursing services by a person
  registered under the Medical Services Act 1996; (j) "a supply of medicine".
* Third Schedule: zero-rating of exports and international transport only (no basket good).
The Act as enacted (sessional text) is the latest reached; the rate is taken as in force in 2025 (grade B).
-/

namespace KiGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Value added tax", standard := 1250, threshold := 100000,
    classOf := fun gd => match gd with
      | .financial | .rent | .education | .health | .medicines => .exempt
      | _ => .standard }

def vatStatute : String := "Value Added Tax Act 2013 s. 7 (3) (12.5 %), s. 8 (2) ($100,000), Second Schedule cl. 1 (a), (d), (e), (h), (i), (j)"

def families : List Family :=
  [{ name := "5111 Value Added Tax", covers := [.vat],
     run := fun _ g _ =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else []) }]

def absent : List Absent :=
  []

def notes : List String := ["KI 5111: VAT Act 2013 ss. 7-8, Second Schedule (PacLII sessional text)"]

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .spirits || s.good == .wine || s.good == .beer || s.good == .cigarettes || s.good == .tobaccoOther || s.good == .petrol || s.good == .diesel || s.good == .nonAlcoholic) then ["excise (Excise Tax Act) not modelled: its 2025 schedule was not reached"] else [])
  ++ (if g.consumption.any (fun s => s.good == .insurance) then ["insurance modelled as taxable (the Second Schedule definition of financial services was not read in full)"] else [])

#guard vat.embedded { good := .clothing, amount := 1125 } == 125
#guard vat.embedded { good := .medicines, amount := 1125 } == 0
#guard vat.net { turnover := 100000, sales := [{ good := .other, net := 100000 }] } == 0

end KiGlobal.Consumption
