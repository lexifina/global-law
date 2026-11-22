import TaxKernel.Global
import R5Common

/-!
# Azerbaijan 2025: state duty (dövlət rüsumu) on the transfer of immovable property (4400)

Law "Dövlət rüsumu haqqında" No. 223-IIQ of 04/12/2001 (e-qanun framework 2860), consolidated text read from the
Wayback capture of 02/12/2024 of `e-qanun.az/frameworks/2/f_2860.html` (meta charset windows-1251; extract
`law/eqanun_2860_art3_10_26.txt`):
* art. 3.1: the payers are the citizens, foreigners and legal persons for whom the acts are performed, the services
  rendered and the rights acquired.
* art. 10.1: certification of contracts alienating immovable property (land, buildings, structures; or a share in an
  enterprise owning immovable property): 10.1.1 to a spouse, child, parent, grandparent, grandchild, brother or sister
  **25 manat**; 10.1.2 to other persons **280 manat** (Law 415-VIQD of 03/12/2021: 250 -> 280).
* art. 26.1.1: issue of the extract on the state registration of ownership of immovable property (including rights
  acquired by inheritance) **50 manat** (Law 415-VIQD: 30 -> 50).
Model: a purchase is a contract with another person (10.1.2) and its registration; both duties are charged to the buyer,
the person acquiring the registered right (art. 3.1); the law does not split the notarial duty between the parties,
which may agree otherwise. Fixed amounts, independent of the price. **Grade A** (statute text read; amendments after
02/12/2024 not checked).
Gap-closing pass (2026-11-21): **re-cited for 2025, grade A.** The team's git history of the e-qanun texts
(lexifina/azerbaijan-law, act 2860; official source e-qanun.az/framework/2860; extract `law/az_gitlaw_2860_2025.txt`):
art. 3 and art. 10 are the same blob in the versions in force from 1/1/2025 and from 29/12/2025; the footnotes of
art. 10 name 415-VIQD (2021) as the last change to 10.1.1 and 10.1.2. Every act changing the law in force during 2025
(121, 77, 124, 161, 172, 177, 179, 192, 240, 297 and 313-VIIQD) was read in the same repository: none touches art. 3,
10.1 or 26. Art. 26 itself is not a file in the repository (its parser lost it); its 2025 wording is the capture of
02/12/2024, and Law 329-VIIQD of 30/12/2025 (in force 9/1/2026) still refers to the services of art. 26.
-/

namespace AzGlobal
open TaxKernel TaxKernel.Global R5Common

def notarialDuty : Int := 280
def extractDuty : Int := 50

def transfers : Family :=
  { name := "4400 Dövlət rüsumu (daşınmaz əmlak)", covers := [.transactions],
    run := fun _ g _ =>
      (g.purchases.zipIdx.filter fun (p, _) => p.kind.isRealEstate).flatMap fun (p, i) =>
        [charge .transactions "Dövlət rüsumu: özgəninkiləşdirmə müqaviləsinin təsdiqi" p.price pos (fun _ => notarialDuty)
           (event := s!"purchase {i + 1}") (statute := "Dövlət rüsumu haqqında Qanun art. 10.1.2 (280 manat), art. 3.1"),
         charge .transactions "Dövlət rüsumu: mülkiyyət hüququnun qeydiyyatı barədə çıxarış" p.price pos (fun _ => extractDuty)
           (event := s!"purchase {i + 1}") (statute := "Dövlət rüsumu haqqında Qanun art. 26.1.1 (50 manat), art. 3.1")] }

def transfersUnsupported (g : CanonGlobal) : List String :=
  if g.purchases.any (fun p => p.kind.isRealEstate) then
    ["state duty: purchases taken as contracts with other persons (art. 10.1.2, 280 manat; 25 manat between close relatives) and charged in full to the buyer (the law does not split the notarial duty)"] else []

#guard notarialDuty + extractDuty == 330



end AzGlobal
