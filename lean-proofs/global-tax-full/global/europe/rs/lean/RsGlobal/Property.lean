import RsGlobal.Pit

/-!
# RS 2025: Property family not reached (grade C)

* 4400 Real-estate transfer and stamp duties (Zakon o porezima na imovinu (porez na prenos apsolutnih prava 2,5 %)): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)
* 4100 Recurrent property tax (porez na imovinu (Beograd)): tried not read in the P5 pass; would unlock: the act and the reference municipality's 2025 rate (registry choice)

* **4100 Recurrent property tax (pass 6 note, grade C)**: porez na imovinu (Beograd): porez na imovinu: rates set by each local government within the Zakon o porezima na imovinu ranges; Beograd decision not read (pass 6 note (PwC WWTS 2025 captures on disk))


## 4400 Porez na prenos apsolutnih prava (pass 6)
Source: Zakon o porezima na imovinu (Sl. glasnik RS 26/2001 ... 94/2024), consolidated text, paragraf.rs, fetched 2026-11-21 (`rs/law/zpi.txt`).
* čl. 25 st. 1: "Obveznik poreza na prenos apsolutnih prava je prodavac, odnosno prenosilac prava"
* čl. 27 st. 1: "Osnovica poreza na prenos apsolutnih prava je ugovorena cena u trenutku nastanka poreske obaveze, ukoliko nije niža od tržišne vrednosti"
* čl. 30: "Stopa poreza na prenos apsolutnih prava iznosi 2,5%."
-/

namespace RsGlobal.Property
open TaxKernel TaxKernel.Global

/-- Zakon o porezima na imovinu čl. 25 st. 1 (the seller pays), čl. 27 (contract price, not below market value), čl. 30 (2,5 %) -/
def p7prenos (d : Disposal) : Int := if d.kind.isRealEstate then divR .down (250 * pos d.proceeds) 10000 else 0
def p7prenosCharges (ds : List Disposal) : List Charge :=
  (ds.zipIdx.filter fun (d, _) => d.kind.isRealEstate).map fun (d, i) =>
    charge .transactions "Porez na prenos apsolutnih prava" d.proceeds (fun v => v) (fun _ => p7prenos d)
      (event := s!"disposal {i + 1}") (statute := "Zakon o porezima na imovinu čl. 25 st. 1 (the seller pays), čl. 27 (contract price, not below market value), čl. 30 (2,5 %)")

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4400 Porez na prenos apsolutnih prava (seller)", covers := [.transactions],
     run := fun args g prev =>
       p7prenosCharges g.disposals }]

def absent : List Absent :=
  []

def notes : List String := ["RS 4400: Zakon o porezima na imovinu čl. 25, 27, 30, consolidated to Sl. glasnik 94/2024 (A)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.purchases.isEmpty || g.assets.any (·.kind.isRealEstate) then ["4100 Recurrent property tax: not modelled (grade C: not read in the P5 pass)"] else [])
  ++ (if g.disposals.any (·.kind.isRealEstate) then ["4400 prenos: the base is the contract price unless below market value (čl. 27: proceeds stand in); exemptions of čl. 31 (contribution to capital, life-maintenance contracts) and the first-home buyer refund not modelled"] else [])
  ++ (if !g.purchases.isEmpty then ["4400 prenos: the buyer pays nothing (čl. 25 st. 1: the seller is the taxpayer, charged on the household's disposals); used motor vehicles (čl. 23 st. 1 tač. 4a, buyer) not modelled"] else [])

#guard p7prenos { kind := .realEstate, proceeds := 200000, cost := 0 } == 5000
#guard p7prenos { kind := .home, proceeds := 1000000, cost := 900000 } == 25000
#guard p7prenos { kind := .listedShares, proceeds := 200000, cost := 0 } == 0

end RsGlobal.Property
