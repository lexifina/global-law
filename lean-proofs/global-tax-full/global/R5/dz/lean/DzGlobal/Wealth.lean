import TaxKernel.Global2
import R5Common

/-!
# Algeria 2025: impôt sur la fortune (4200) and droits de donation et de succession (4300)

Sources: the DGI codes in their 2025 Arabic editions (`law/dgi_cidta_2025_ar.pdf`, `law/dgi_cenr_2025_ar.pdf`, already
the sources of DZ 4100/4400; read by Arabic OCR checked on the page images, `law/dz_cidta25_ar_p80_82_ocr.txt`,
`law/dz_cenr25_ar_ocr.txt`) with the 2023 French editions for the wording (`dgi_cidta_2023_fr.pdf`,
`dgi_cenr_2023_fr.pdf`). Amendment footnotes of the 2025 editions run to LF 2025.

**Impôt sur la fortune** (CIDTA art. 274-281 bis 14; title renamed by LFC 2020):
* art. 274: natural persons domiciled in Algeria (all their property) or not (their Algerian property); art. 275: the
  net value on 1 January of the taxable property; a married woman is taxed separately;
* art. 276: the elements to be declared: built and unbuilt immovable property and real rights, and listed movables
  (cars above 2 000 cm³ petrol or 2 200 cm³ diesel, motorcycles above 250 cm³, yachts, aircraft, racehorses, art above
  500 000 DA);
* art. 278 bis: outside the base: estates in liquidation, **the main home when its value is at most 450 000 000 DA**,
  **rented property**; art. 280: professional property and shares in companies (art. 281: not those of companies
  managing their own property); art. 281 bis: immovables at market value by the administration's reference prices;
  art. 281 bis 4-6: debts deductible (loans for the immovables);
* art. 281 bis 8 (last changed by LFC 2020): marginal scale: below 100 000 000 DA 0 %; 100-150 m 0,15 %; 150-250 m
  0,25 %; 250-350 m 0,35 %; 350-450 m 0,5 %; above 450 m 1 % (the bands start at x 000 001: taken at x 000 000).
Model: per person (asset `person`), the immovables (home, realEstate, land) except the first home when it is worth at
most 450 m and anything with an `annualValue` (rented), at their statutory value, less their debts. Movables of art.
276 are not in the record with the facts they need (engine size, kind): not counted, listed.

**Donations** (CENR art. 231, as changed by LF 2024 art. 30 and LF 2025 art. 37): **5 %**; exempt between ascendants
and descendants of the first degree, between spouses, and between kafil and makfoul child; gifts of shares or company
interests at the rate of art. 218 (not read: not charged, listed).
**Successions** (CENR art. 236): **5 %** of each heir's net share, **3 %** for ascendants, descendants and spouses; these
heirs pay nothing on the individual home the deceased occupied; art. 37: the estate's assets after an allowance of
**50 000 DA** (applied to each inheritance record); art. 238: 10 % less per dependent child of the heir (not applied).
Grade A (2025 code text read).
-/

namespace DzGlobal
open TaxKernel TaxKernel.Global R5Common

def ifScale : Schedule :=
  Schedule.ofList [(0, 0), (100000000, 15), (150000000, 25), (250000000, 35), (350000000, 50), (450000000, 100)]

def impotFortune : WealthTax := { name := "الضريبة على الثروة (impôt sur la fortune)", sched := ifScale }

/-- the immovables counted for one person (art. 276, 278 bis) -/
def ifAssets (g : CanonGlobal) (p : Nat) : List Asset :=
  let mine := g.assets.filter (·.person == p)
  let firstHome := mine.findIdx? (·.kind == .home)
  (mine.zipIdx.filter fun (a, i) =>
    a.kind.isRealEstate && a.annualValue ≤ 0 &&
      !(a.kind == .home && firstHome == some i && a.statutoryValue ≤ 450000000)).map (·.1)

def ifPersons (g : CanonGlobal) : List Nat := (g.assets.map (·.person)).eraseDups

def ifCharges (g : CanonGlobal) : List Charge :=
  if g.entity == .company then [] else
  (ifPersons g).filterMap fun p =>
    let as := ifAssets g p
    if as.isEmpty then none else
    some (charge .wealth impotFortune.name (impotFortune.netWealth as) (fun _ => impotFortune.base as)
      (fun _ => impotFortune.gross as) (event := s!"1 January 2025, person {p}")
      (statute := "CIDTA art. 274-276, 278 bis (main home up to 450 000 000 DA and rented property outside), 280, 281 bis, 281 bis 4-6, 281 bis 8 (0 % to 1 %)"))

/-- first-degree line and spouse (gift exemption, art. 231) -/
def firstDegree (r : Relation) : Bool := r == .spouse || r == .child || r == .parent
/-- ascendants, descendants and spouse (3 %, art. 236) -/
def directLine (r : Relation) : Bool := r == .spouse || r == .child || r == .grandchild || r == .parent

def isShares (x : TransferX) : Bool := x.assetKind == some .listedShares || x.assetKind == some .unlistedShares

def giftRate (r : Relation) : Int := if firstDegree r || r == .charity then 0 else 500
def inheritanceRate (r : Relation) : Int := if r == .charity then 0 else if directLine r then 300 else 500

def inheritanceBase (t : Transfer) : Int :=
  pos (pos t.statutoryValue - (if directLine t.relation then pos t.homeValue else 0) - 50000)

def estateCharges (g : CanonGlobal) : List Charge :=
  (transfersX g).zipIdx.filterMap fun ((t, x), i) =>
    if t.kind == .gift then
      if isShares x || giftRate t.relation == 0 then none else
      some (charge .estate "رسم التسجيل على الهبات (droit de donation)" t.statutoryValue pos
        (fun b => b * giftRate t.relation / 10000) (event := s!"gift {i + 1}")
        (statute := "CENR art. 231 (5 %; first-degree line, spouses, kafala exempt; LF 2024 art. 30, LF 2025 art. 37)"))
    else
      let r := inheritanceRate t.relation
      if r == 0 then none else
      some (charge .estate "حق نقل الملكية بسبب الوفاة (droit de mutation par décès)" t.statutoryValue
        (fun _ => inheritanceBase t) (fun b => b * r / 10000) (event := s!"inheritance {i + 1}")
        (statute := "CENR art. 236 (5 %; 3 % ascendants, descendants, spouse; the deceased's home exempt for them), art. 37 (50 000 DA)"))

def wealth : Family :=
  { name := "4200-4300 الضريبة على الثروة، رسوم الهبة والتركة", covers := [.wealth, .estate],
    run := fun _ g _ => ifCharges g ++ estateCharges g }

def wealthUnsupported (g : CanonGlobal) : List String :=
  (if g.entity != .company && g.assets.any (fun a => !a.kind.isRealEstate && a.kind != .business &&
      a.kind != .listedShares && a.kind != .unlistedShares && a.kind != .pensionFund) then
    ["impôt sur la fortune: movables of art. 276 (cars above 2 000/2 200 cm³, yachts, aircraft, racehorses, art above 500 000 DA) cannot be told from the record: only immovables counted; deposits and securities are not elements of art. 276 (shares are professional property, art. 280)"] else []) ++
  (if g.assets.any (·.kind == .home) then
    ["impôt sur la fortune: the first home of each person taken as the main home (art. 278 bis); an asset with annualValue is taken as rented and left out"] else []) ++
  ((transfersX g).zipIdx.filterMap fun ((t, x), i) =>
    if t.kind == .gift && isShares x && giftRate t.relation != 0 then
      some s!"droit de donation: gift {i + 1} is shares: rate of CENR art. 218 not read, not charged (grade C)" else none) ++
  (if g.transfers.any (·.kind == .inheritance) then
    ["droit de succession: the 50 000 DA allowance of art. 37 (per estate) applied to each inheritance record; 10 % less per dependent child (art. 238) and the CNEP savings exemption (art. 236 bis) not applied; the deceased's home exempt only through the record's homeValue"] else [])

#guard ifScale.tax {} 200000000 == 200000
#guard giftRate .child == 0 && giftRate .grandchild == 500 && inheritanceRate .child == 300

end DzGlobal
