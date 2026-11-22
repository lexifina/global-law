import NpGlobal.Pit

/-!
# Nepal 2025: value added tax (5111); excise duty not modelled

Source: Value Added Tax Act, 2052 (1996), English text on nepallaws.com (secondary host; per-section pages and
Schedule 1 "List of VAT exempt goods and services", read 2026-11-21; `np/law/np_vat_*_nepallaws.txt`, sha256 in
`SHA256SUMS`). The Finance Acts 2081 and 2082 that set the rate and amend Schedule 1 were not read (ird.gov.np pages are
script-driven; the IRD PDF of the Act answers 404): grade B.
* **s. 7 (1)**: the tax is levied "in a single rate as prescribed in the Financial Act made for that fiscal year":
  13 % (rate in the Finance Acts 2081/2082, not read). **s. 7 (2)**: Schedule 2 zero-rated (exports).
* **s. 9**: small vendors under "a prescribed annual taxable transaction threshold" are exempt from registration; the
  threshold is in the VAT Rules (not read): not applied.
* **Schedule 1** (s. 5 (3)): Group 1 basic agricultural products (rice, cereals, flours, vegetables, fruit; not when
  supplied by hotels or restaurants); Group 2 goods of basic needs (salt, kerosene 2710.19.10, electrical energy
  2716.00.00, fuel wood, tap water); Group 3 live animals and animal products; Group 5 medicines (Chapter 30) and
  health services; Group 6 education by schools and universities; Group 7 books and newspapers; Group 9 air transport
  and public transportation; Group 11 (B) 4 financial services and life, accident, medical and agricultural insurance;
  Group 12 purchase, sale and rental of buildings and land (not hotels, guesthouses, apartments).
-/

namespace NpGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Value added tax", standard := 1300,
    classOf := fun gd => match gd with
      | .food | .electricity | .water | .heatingOil | .medicines | .health | .education | .books | .newspapers | .transport | .financial | .rent => .exempt
      | _ => .standard }

def vatStatute : String := "VAT Act 2052 s. 7 (13 % by the Finance Act), Schedule 1 Groups 1-3, 5-7, 9, 11, 12"

def families : List Family :=
  [{ name := "5111 Value added tax", covers := [.vat],
     run := fun _ g _ =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else []) }]

def absent : List Absent :=
  []

def notes : List String := ["NP 5111: VAT Act 2052 (nepallaws.com English text, Schedule 1); 13 % from the Finance Act (not read); grade B"]

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .food) then ["basic food (Schedule 1 Groups 1 and 3: cereals, flours, vegetables, fruit, meat, fish, milk) is exempt; processed food is taxable at 13 %: food modelled as exempt"] else [])
  ++ (if g.consumption.any (fun s => s.good == .insurance) then ["only life, accident, medical and agricultural insurance are exempt (Schedule 1 Group 11 (B) 4); insurance is modelled as taxable"] else [])
  ++ (if g.consumption.any (fun s => s.good == .transport) then ["air transport and public transportation are exempt (Schedule 1 Group 9); applied to the whole class"] else [])
  ++ (if true then ["registration threshold (VAT Act s. 9, amount in the VAT Rules) not applied"] else [])
  ++ (if g.consumption.any (fun s => s.good == .spirits || s.good == .wine || s.good == .beer || s.good == .cigarettes || s.good == .tobaccoOther || s.good == .petrol || s.good == .diesel) then ["excise duty (Excise Duty Act 2058 and the Finance Act schedule) not modelled"] else [])

#guard vat.embedded { good := .clothing, amount := 1130 } == 130
#guard vat.embedded { good := .rent, amount := 1130 } == 0
#guard vat.embedded { good := .hotels, amount := 1130 } == 130

end NpGlobal.Consumption
