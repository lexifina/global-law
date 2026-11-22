import TaxKernel.Global2
import R5Common

/-!
# Morocco 2025: droits d'enregistrement on gifts (4300)

CGI 2025 (`law/cgi2025fr.txt`). A gift between living persons is a "mutation entre vifs, à titre gratuit" that must be
registered when it bears on the goods of art. 127-I-A-1°: a) immovables and real rights in them, b) businesses
(fonds de commerce) and clienteles, c) shares in unlisted companies. The rates are those of art. 133-I:
* C-4° (1,5 %): gifts of the goods of art. 127-I-A-1°, 2°, 3° and B-3° in the direct line, between spouses, between
  brothers and sisters (and between a kafil and the child in kafala, not a relation in the record);
* outside that circle the ordinary rates of the acquisition: G-1° 5 % for land, acquired "à titre onéreux ou gratuit";
  F-1° 4 % for built premises (the paragraph taxes "l'acquisition" without limiting it to purchases; reading: a gift
  is an acquisition of art. 127-I-A-1°-a); A-1° 6 % for businesses (art. 127-I-A-1-b deeds, for consideration or not);
* art. 129-IV-25°: transfers, for consideration or free of charge, of shares in companies other than real-estate
  companies (art. 3-3°, 61-II) are exempt: unlisted shares are not charged (real-estate companies are not told apart).
Gifts of movables outside art. 127 (cash, listed securities, vehicles) are not registered deeds: no duty. Inheritance
is not taxed by the CGI. The record gives what a gift is through `"assetKind"` (kernel 2.1.1 `TransferX`); a gift
without it is listed as not charged, never assumed. Base: the gift's statutory value. Grade A (CGI 2025 text read).
-/

namespace MaGlobal
open TaxKernel TaxKernel.Global R5Common

/-- The value of a gift by what it is: `pick k` says whether its kind is charged (`none`: kind not given). -/
def partBy (pick : AssetKind → Bool) (t : Transfer) (x : TransferX) : Option Int :=
  match x.assetKind with
  | some k => some (if pick k then pos t.statutoryValue else 0)
  | none => none

def isBuilt (k : AssetKind) : Bool := k == .home || k == .realEstate
def isLand (k : AssetKind) : Bool := k == .land
def isBusiness (k : AssetKind) : Bool := k == .business
def isArt127 (k : AssetKind) : Bool := isBuilt k || isLand k || isBusiness k

def familyRel : List Relation := [.spouse, .child, .grandchild, .parent, .sibling]
def otherRel : List Relation := [.nieceNephew, .otherRelative, .unrelated]

def giftFamily : PartDuty :=
  { name := "Droits d'enregistrement (donation, famille)", rates := familyRel.map (·, 150), part := partBy isArt127,
    statute := "CGI art. 133-I-C-4° (1,5 %), art. 127-I-A-1°; unlisted shares exempt (art. 129-IV-25°)" }
def giftBuilt : PartDuty :=
  { name := "Droits d'enregistrement (donation, locaux construits)", rates := otherRel.map (·, 400),
    part := partBy isBuilt, statute := "CGI art. 133-I-F-1° (4 %), art. 127-I-A-1°-a" }
def giftLand : PartDuty :=
  { name := "Droits d'enregistrement (donation, terrains)", rates := otherRel.map (·, 500),
    part := partBy isLand, statute := "CGI art. 133-I-G-1° (5 %, à titre onéreux ou gratuit)" }
def giftBusiness : PartDuty :=
  { name := "Droits d'enregistrement (donation, fonds de commerce)", rates := otherRel.map (·, 600),
    part := partBy isBusiness, statute := "CGI art. 133-I-A-1° (6 %), art. 127-I-A-1°-b" }

def giftDuties : List PartDuty := [giftFamily, giftBuilt, giftLand, giftBusiness]

def wealth : Family :=
  { name := "4300 droits d'enregistrement (donations)", covers := [.estate],
    run := fun _ g _ => giftDuties.flatMap (·.charges g) }

def wealthUnsupported (g : CanonGlobal) : List String :=
  (giftFamily.unknown g ++ giftBuilt.unknown g).eraseDups ++
  (if (transfersX g).any (fun (t, x) => t.kind == .gift && x.assetKind == some .unlistedShares) then
    ["gift of unlisted shares: exempt (CGI art. 129-IV-25°) unless the company is a real-estate company (art. 3-3°, 61-II), which the record does not say"] else []) ++
  (if g.transfers.any (fun t => t.kind == .gift && t.relation == .charity) then
    ["gift to a charity: exemptions for public-utility bodies (art. 129) not modelled; not charged"] else [])

#guard giftFamily.amount 150 1000000 == 15000
#guard giftLand.amount 500 500000 == 25000
#guard giftBuilt.amount 400 1000000 == 40000
#guard partBy isArt127 { kind := .gift, value := 300000, relation := .child } { assetKind := some .listedShares } == some 0
#guard partBy isArt127 { kind := .gift, value := 300000, relation := .child } {} == none

end MaGlobal
