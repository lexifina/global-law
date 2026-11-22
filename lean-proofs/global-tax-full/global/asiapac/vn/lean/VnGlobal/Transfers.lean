import VnGlobal.Pit

/-!
# Viet Nam 2025: no separate inheritance, estate or gift tax (4300, cited)

Luật Thuế thu nhập cá nhân 04/2007/QH12, văn bản hợp nhất 28/VBHN-VPQH (Công báo 18 Mar 2025) and 103/VBHN-VPQH (Sep 2025)
(`cmp20/world/B03-asia-east-se/vn/law/`): inheritances and gifts of securities, capital, real estate and registered assets
are personal income (art. 3 (10)), taxed at 10 % on the part above VND 10 m (arts. 16, 23 (2); non-residents art. 31): this is
the PIT, modelled under 1100 in `Capital.lean` (giftF). No other law levies a tax on estates, inheritances or gifts.
-/

namespace VnGlobal.Transfers
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .estate, why := "Viet Nam has no separate inheritance, estate or gift tax: inheritances and gifts are personal income (PIT Law 04/2007 arts. 3 (10), 16, 23 (2); consolidated 28/VBHN-VPQH 2025), modelled under 1100" }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard absent.length == 1

end VnGlobal.Transfers
