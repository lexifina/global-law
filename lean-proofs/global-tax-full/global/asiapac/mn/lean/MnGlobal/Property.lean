import MnGlobal.Pit
import TaxKernel.Global2

/-!
# Mongolia 2025: immovable property tax (4100)

Source: Үл хөдлөх эд хөрөнгийн албан татварын тухай хууль, consolidated text on legalinfo.mn (`/mn/detail/39`, read
2026-11-21; last amendment noted: law of 2024-06-05; `mn/law/mn_immovable_property_tax_law39.html`).
* **art. 4.1**: payers are the owners (companies 4.1.1, citizens 4.1.4).
* **art. 5.1**: base = the value in the immovable property register (else insured value, else book value); art. 8.1: value
  as at 15 January.
* **art. 6.1** (amended 2021-07-07, 2024-06-05): rate 0.6-2.0 % of the art. 5 value, set by the aimag / capital Citizens'
  Representative Khural. Ulaanbaatar: Khural resolution No. 123 of 5 December 2023 (registered ЗХХАЭ №37, 2023-12-28; in
  force 1 January 2024): its annex of rates is not in the registry copy (the attached docx holds the resolution only):
  **rates not read**.
* **art. 7.1.2** (amended 2021-07-07, 2024-06-05): exempt "иргэн, хуулийн этгээдийн өмчилж байгаа ... нийслэл, нийслэлийн
  харьяа хот дахь хоёр орон сууц": two dwellings in the capital (one in other cities) are exempt. The model's household
  lives in Ulaanbaatar: its first two homes are booked at a cited 0; any other immovable property, and every company's,
  is listed grade C (UB rate annex not read).

Gap-closing session:
* **4100, kernel 2.8.0 `LocalTax`**: property other than the two exempt dwellings (real estate other than homes, land) is
  charged at the Citizens' Representative Khural's rate given in the entity's `localRates.propertyTax` (in %, inside the
  art. 6.1 range 0.6-2.0 %; outside it: grade C, never clamped); no default is declared (the Ulaanbaatar annex was not
  read), so without the input the line stays grade C with the range. Homes beyond the first two stay listed.
* **4400**: Улсын тэмдэгтийн хураамжийн тухай хууль (2010; legalinfo.mn lawId=515, read in lexifina/mongolia-law law/2010/515, consolidated text with amendment notes) art. 9.1.2: state stamp duty for notarising a real estate contract, 0.05 % of the contract value
  (0.03 % between spouses, children and parents); no amendment note on 9.1.2 (the text in force in 2025). Booked on the
  purchase price of homes, real estate and land (the buyer; the law fixes no payer). Art. 38.1.2-38.1.21 (registration
  fees by value) were repealed by the law of 9 June 2011. A fee proportional to the value, not to the cost of the service,
  is a tax on the transfer (OECD Interpretative Guide §13-14, 4400).
-/

namespace MnGlobal.Property
open TaxKernel TaxKernel.Global

def duty0 : TransferDuty :=
  { name := "State stamp duty on notarised real estate contracts (0.05 %)", sched := Schedule.flat 5, kinds := [.home, .realEstate, .land] }

def fam0 : Family :=
  { name := "4400 transfer duties on property", covers := [.transactions],
    run := fun _ g _ => 
      duty0.charges g.purchases "Улсын тэмдэгтийн хураамжийн тухай хууль (2010; legalinfo.mn lawId=515, read in lexifina/mongolia-law law/2010/515, consolidated text with amendment notes) art. 9.1.2 (0.05 %)" (level := .central) }

/-- Art. 7.1.2: two dwellings in the capital exempt (cited 0); everything else needs the UB rate annex (not read). -/
def mnHomeExempt (g : CanonGlobal) : List Charge :=
  ((g.assets.zipIdx.filter fun (a, _) => a.kind == .home).take 2).map fun (a, i) =>
    charge .propertyRecurrent "Үл хөдлөх эд хөрөнгийн албан татвар (орон сууц, чөлөөлөгдсөн)" a.statutoryValue id (fun _ => 0)
      (event := s!"asset {i + 1}") (level := .local)
      (statute := "Үл хөдлөх эд хөрөнгийн албан татварын тухай хууль 7.1.2: нийслэл дэх хоёр орон сууц чөлөөлөгдөнө (exempt)")
def mnPropF : Family :=
  { name := "4100 үл хөдлөх эд хөрөнгийн албан татвар", covers := [.propertyRecurrent],
    run := fun _ g _ => mnHomeExempt g }
def mnPropUnread (g : CanonGlobal) : Nat :=
  (g.assets.filter (fun a => a.kind == .realEstate || a.kind == .land)).length + ((g.assets.filter (·.kind == .home)).length - 2)
/-- Immovable property tax law art. 6.1: the Khural's rate, 0.6-2.0 % of the art. 5.1 value; kernel 2.8.0 `LocalTax`
(rate from `localRates.propertyTax`, no declared default). -/
def mnLocalProp : LocalTax :=
  { key := "propertyTax", name := "Үл хөдлөх эд хөрөнгийн албан татвар (Khural rate)", base := .assets [.realEstate, .land],
    unit := .percent, minNum := 6, minDen := 10, maxNum := 2, maxDen := 1,
    statute := "Үл хөдлөх эд хөрөнгийн албан татварын тухай хууль arts. 5.1, 6.1 (0.6-2.0 %, set by the Khural)" }
def mnHomesBeyondTwo (g : CanonGlobal) : Nat := (g.assets.filter (·.kind == .home)).length - 2

def families : List Family := [fam0, mnPropF, mnLocalProp.family]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.assets.any (fun a => a.kind == .home) && g.entity == .company then ["a company's dwellings are exempt only within art. 7.1.2's two in the capital; rate on the rest not read (grade C)"] else [])
  ++ (if mnHomesBeyondTwo g > 0 then ["immovable property tax on a third or later dwelling (art. 6.1 rate, art. 7.1.2 exempts two in the capital): homes are not in the LocalTax base: grade C"] else [])
  ++ (if false then [] else mnLocalProp.unknown g) ++ (if false then [""] else [])
  ++ (if g.purchases.any (fun p => [AssetKind.home, .realEstate, .land].contains p.kind) then ["4400 stamp duty: 0.03 % between spouses, children and parents (art. 9.1.2) not distinguished: 0.05 % booked"] else [])

#guard (mnPropF.run [] { id := "t", household := { id := "t" }, assets := [{ kind := .home, value := 300000000 }] } []).map (·.due) == [0]
#guard mnPropUnread { id := "t", household := { id := "t" }, assets := [{ kind := .home, value := 1 }, { kind := .home, value := 1 }, { kind := .home, value := 1 }] } == 1
#guard duty0.amount { kind := .home, price := 200000000 } == 100000
#guard (mnLocalProp.charges { id := "t", household := { id := "t" }, assets := [{ kind := .land, value := 100000000 }], raw := (Lean.Json.parse "{\"localRates\": {\"propertyTax\": 1.0}}").toOption.getD Lean.Json.null }).map (·.due) == [1000000]
#guard (mnLocalProp.charges { id := "t", household := { id := "t" }, assets := [{ kind := .land, value := 100000000 }], raw := (Lean.Json.parse "{\"localRates\": {\"propertyTax\": 2.5}}").toOption.getD Lean.Json.null }).length == 0
#guard (mnLocalProp.charges { id := "t", household := { id := "t" }, assets := [{ kind := .land, value := 100000000 }] }).length == 0

end MnGlobal.Property
