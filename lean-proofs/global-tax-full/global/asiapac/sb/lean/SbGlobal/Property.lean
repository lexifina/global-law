import SbGlobal.Pit

/-!
# Solomon Islands 2025: stamp duty on transfers (4400)

Source: Stamp Duties Act (Cap. 126), official **reprint "As in force at: 5 February 2024"** (authorised by the Attorney
General under the Legislation Act 2023), published on the Inland Revenue Division's legislation page
(`ird.gov.sb/wp-content/uploads/2025/10/STAMP-DUTY-ACT-CAP-126.pdf`, listed as the current Act in October 2025;
`sb/law/sb_stamp_duties_cap126_reprint20240205.pdf`). The PacLII 1996 Revised Edition (1.75 / 2.75 / 3.75 %, LN 38/1990) is
superseded.
* **s. 3 (1)**: duties on the documents in the Schedule.
* **Schedule item 11** (liable: "The transferee"): transfer of any property or interest, on the consideration (or the value
  where there is none): (i) above $10,000 to $25,000: **2 %**; (ii) above $25,000 to $50,000: **3 %**; (iii) above $50,000:
  **4 %** of the whole consideration (a rate by bracket, not marginal); $10,000 or less: no duty under item 11. Shares: the
  threshold is $100 (not modelled).
-/

namespace SbGlobal.Property
open TaxKernel TaxKernel.Global

/-- Stamp Duties Act (Cap. 126) Schedule item 11 (reprint as in force 5 Feb 2024): rate by bracket on the whole consideration. -/
def sbTransferRateBp (v : Int) : Int := if v ≤ 10000 then 0 else if v ≤ 25000 then 200 else if v ≤ 50000 then 300 else 400
def sbDuty (p : Purchase) : Int := divR .down (sbTransferRateBp p.price * p.price) BP
def sbDutyF : Family :=
  { name := "4400 stamp duty on transfers", covers := [.transactions],
    run := fun _ g _ => (g.purchases.zipIdx.filter fun (p, _) => p.kind == .home || p.kind == .realEstate || p.kind == .land).map fun (p, i) =>
      charge .transactions "Stamp duty on transfers (Schedule item 11, the transferee)" p.price id (fun _ => sbDuty p) (event := s!"purchase {i + 1}")
        (statute := "Stamp Duties Act (Cap. 126) s. 3 (1), Schedule item 11 (reprint as in force 5 February 2024): 2 % / 3 % / 4 % above $10,000 / $25,000 / $50,000") }

def families : List Family := [sbDutyF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if !g.purchases.isEmpty then ["stamp duty on transfers booked on the purchaser (item 11: the transferee); share transfers ($100 threshold), leases (item 8) and other instruments not modelled"] else [])

#guard sbDuty { kind := .home, price := 60000 } == 2400
#guard sbDuty { kind := .land, price := 20000 } == 400
#guard sbDuty { kind := .home, price := 10000 } == 0
#guard sbDuty { kind := .home, price := 50000 } == 1500

end SbGlobal.Property
