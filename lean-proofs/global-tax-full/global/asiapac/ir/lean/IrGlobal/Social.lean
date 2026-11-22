import IrGlobal.Pit

/-!
# Iran 2025 (1403 and 1404): employer social security (2200)
(B.) قانون تأمین اجتماعی مصوب ۱۳۵۴ art. 28 (1) and تبصره ۱: "از اول سال ۱۳۵۵ حق‌بیمه سهم کارفرما بیست درصد مزد یا حقوق
بیمه‌شده خواهد بود" (employer 20 %; consolidated text on ekhtebar.ir, a private publisher's transcription, last amendment
shown 1394; `cmp20/world/B06-mena/ir/law/w5/ir_ekhtebar_sso1354.html`): no change in 1403 or 1404, so the rate is the
same either side of 21 March 2025 (no split). Unemployment insurance (employer 3 %, Unemployment Insurance Act): registry
(not read). The maximum insurable wage (set each year, 1403 and 1404 differ) is not applied (flagged).
-/

namespace IrGlobal.Social
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "2200 employer social contributions", covers := [.sscEmployer],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "تأمین اجتماعی (employer 23 %)" a.wages pos (fun b => divR .down (2300 * b) BP) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "Social Security Act 1354 art. 28; Unemployment Insurance Act")) }

def families : List Family := [fam0]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard (fam0.run [] { id := "t", household := { id := "t", adults := [{ wages := 1000000 }] } } []).map (·.due) == [230000]

end IrGlobal.Social
