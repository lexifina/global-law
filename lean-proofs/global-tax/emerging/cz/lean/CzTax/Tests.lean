import CzTax.Theorems

/-!
# Official worked figures, kernel-checked (`decide`)

Source A: Finanční správa, "Informace k institutu paušální daně pro rok 2025 a 2026"
(https://financnisprava.gov.cz/cs/dane/dane/dan-z-prijmu/pausalni-dan/informace-k-institutu-pausalni-dane-pro-rok-2025,
fetched 2026-11-19, copy `refs/fs_pausal_2025.txt`): table "Výše měsíční zálohy na paušální daň pro rok 2025" —
I. pásmo 8 716 = 100 + 5 473 + 3 143; II. pásmo 16 745 = 4 963 + 8 191 + 3 591; III. pásmo 27 139 = 9 320 + 12 527 +
5 292; and the "Příklady": a craftsman (80 %) with 1 900 000 Kč "může se tedy přihlásit do I. pásma"; a doctor (40 %)
with 1 200 000 Kč may enter the II. pásmo but "nemůže však vstoupit do I. pásma"; a craftsman with 1 400 000 Kč meets
"podmínku pro účast v I. pásmu".

Source B: OECD Taxing Wages 2025 (CZE), statutory reading: the OECD's CGITLETC 87 712 for S100 is 15 % of the unrounded
584 744; § 16 odst. 2 taxes the base rounded down to 584 700 (87 705).
-/

namespace CzTax

-- Source A: the twelve components of the 2025 paušální zálohy
example : pausalTax 1 = 100 ∧ bpCeil (pausalSocialBase 1) seSocialRate = 5473 ∧
    bpCeil (pausalHealthYear 1 / 12) healthRate = 3143 := by decide
example : pausalTax 2 = 4963 ∧ bpCeil (pausalSocialBase 2) seSocialRate = 8191 ∧
    bpCeil (pausalHealthYear 2 / 12) healthRate = 3591 := by decide
example : pausalTax 3 = 9320 ∧ bpCeil (pausalSocialBase 3) seSocialRate = 12527 ∧
    bpCeil (pausalHealthYear 3 / 12) healthRate = 5292 := by decide
-- Source A: the band examples
example : pausalBandFor 1900000 80 = 1 := by decide
example : pausalBandFor 1200000 40 = 2 := by decide
example : pausalBandFor 1400000 80 = 1 := by decide
-- the ČSSZ/VZP 2025 minimum monthly advances implied by the bases (29,2 % / 13,5 %, rounded up)
example : bpCeil seMinBaseMain seSocialRate = 4759 ∧ bpCeil seMinBaseSide seSocialRate = 1496 ∧
    bpCeil seHealthMinMonthly healthRate = 3143 := by decide
-- Source B
example : tax16 (roundBase 584744) = 87705 := by decide
example : tax16 (roundBase 391778) = 58755 := by decide
example : (computeTax { wages := 584744 }).finalTax = 56865 := by decide
example : (computeTax { wages := 391778, childCredits := 15204 + 22320 }).finalTax = -9609 := by decide

end CzTax
